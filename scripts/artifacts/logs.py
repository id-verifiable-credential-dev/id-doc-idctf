"""Build the did:webvh log of every entity the documentation names.

Every private key comes from the keystore (``keystore.py``); every hash, proof
and Multikey comes from ``webvh.py``. The result is written to
``build/artifacts/webvh.json``, the one file later generators read, and the
output is verified before the script exits.

Run as ``.venv/bin/python scripts/artifacts/logs.py``.
"""

from __future__ import annotations

import base64
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import keystore  # noqa: E402
import webvh  # noqa: E402

OUT = webvh.REPO_ROOT / "build" / "artifacts" / "webvh.json"
WATCHER = "https://did.trust.go.id"
CONTEXT = ["https://www.w3.org/ns/did/v1", "https://w3id.org/security/multikey/v1"]

# Fixed so a re-run does not change the request body. The value stands for one
# Trust Authority issued: 24 random bytes, base64url.
NONCE = base64.urlsafe_b64encode(
    hashlib.sha256(b"idctf-example-publisher-nonce-1").digest()[:24]
).decode().rstrip("=")
# A minute after the entry was made: the nonce is fetched once the entry exists (TS-4-03).
POP_IAT = int(datetime.fromisoformat("2026-09-15T09:01:00+00:00").timestamp())

# prefix, domain, role, first versionTime, DID Document purposes (keystore order)
ENTITIES = {
    "trust-authority": ("ta", "trust.go.id", "Trust Authority", "2026-01-01T00:00:00Z",
                        ["accreditation-credential", "authority-statement", "use-statement",
                         "use-statement-status-list", "accreditation-status-list"]),
    "dukcapil": ("dukcapil", "dukcapil.go.id", "Identity Issuer", "2026-02-01T00:00:00Z",
                 ["issuance-jose", "status-list"]),
    "bkn": ("bkn", "bkn.go.id", "Attribute Issuer", "2026-03-01T00:00:00Z",
            ["issuance-jose", "status-list"]),
    "kemenag": ("kemenag", "kemenag.go.id", "Attribute Issuer", "2026-03-01T00:00:00Z",
                ["issuance-jose", "status-list"]),
    "terminal-nusantara": ("terminal", "terminal-nusantara.co.id", "Relying Party",
                           "2026-03-01T00:00:00Z", ["request-object"]),
    "dompet-digital-nusantara": ("dompet", "dompet.co.id", "Wallet Provider",
                                 "2026-03-01T00:00:00Z", ["key-attestation"]),
    "universitas-nusantara": ("unn", "ijazah.unn.ac.id", "Attribute Issuer",
                              "2026-02-01T00:00:00Z", ["issuance-jose", "status-list"]),
    # Issues the SIM in mdoc alone, so it signs with its Document Signer Certificate
    # and its DID Document carries only the status list key.
    "korlantas": ("korlantas", "korlantas.polri.go.id", "Attribute Issuer",
                  "2026-03-01T00:00:00Z", ["status-list"]),
}
# Keys the keystore already held and that already sign; the DID Document publishes them.
EXISTING_KEYS = {
    ("trust-authority", "use-statement"): "ta-use-statement",
    ("trust-authority", "authority-statement"): "ta-authority-statement",
    ("trust-authority", "accreditation-credential"): "ta-accreditation-credential",
}
# Keys added to Trust Authority's DID Document by its second entry; both already in the keystore.
TA_ADDED = {
    "recognition-statement": "ta-recognition-statement",
    "catalog": "ta-catalog",
}
# Before ta-witness-1 is withdrawn (1 October 2026), so a reader still accepts its proof
# (REQ-TS-5-01-077), and after ta-witness-2 is granted (1 September 2026).
TA_SECOND_TIME = "2026-09-30T09:00:00Z"
EXPECTED_TA_SCID = "QmZjy1t9oFiaFjhX2e38uMuR7mgtdLjHPMGfjEfvrsmaiq"
DUKCAPIL_SECOND_TIME = "2026-09-15T09:00:00Z"


class Key:
    """A keystore key and everything published about it."""

    def __init__(self, name: str, ed25519: bool):
        self.name = name
        self.private = (
            keystore.load_or_create_ed25519(name) if ed25519 else keystore.load_or_create(name)
        )
        self.multikey = webvh.multikey(self.private.public_key())
        self.algorithm = "EdDSA" if ed25519 else "ES256"
        self.did_key = webvh.did_key(self.multikey)
        self.kid = f"{self.did_key}#{self.multikey}"  # replaced for DID Document keys

    def describe(self) -> dict:
        return {
            "keystore": self.name,
            "multikey": self.multikey,
            "did_key": self.did_key,
            "kid": self.kid,
            "algorithm": self.algorithm,
        }


def _witness(*keys: Key) -> dict:
    return {"threshold": 1, "witnesses": [{"id": k.did_key} for k in keys]}


def _method(did: str, fragment: str, key: Key) -> dict:
    return {"id": f"{did}#{fragment}", "type": "Multikey", "controller": did,
            "publicKeyMultibase": key.multikey}


def _finish(entry: dict, previous_id: str, update: Key) -> dict:
    """Set versionId and proof. ``entry`` carries its final versionId number in it."""
    number = entry["versionId"]
    entry["versionId"] = previous_id
    digest = webvh.entry_hash(entry, previous_id)
    entry["versionId"] = f"{number}-{digest}"
    proof = webvh.sign_entry_proof(entry, update.private, update.kid)
    entry["proof"] = [proof]
    return entry


def build_entity(slug: str, witness1: Key, witness2: Key) -> dict:
    prefix, domain, role, time1, purposes = ENTITIES[slug]
    count = 3 if slug in ("dukcapil", "trust-authority") else 2
    update = [Key(f"{prefix}-update-{n}", True) for n in range(1, count + 1)]
    keys: dict[str, Key] = {}
    purpose_keys: dict[str, Key] = {}
    for purpose in purposes:
        k = Key(EXISTING_KEYS.get((slug, purpose), f"{prefix}-{purpose}-1"), False)
        keys[f"{purpose}-1"] = k
        purpose_keys[purpose] = k
    if slug == "dukcapil":
        k2 = Key("dukcapil-issuance-jose-2", False)
        keys["issuance-jose-2"] = k2
    if slug == "trust-authority":
        for purpose, name in TA_ADDED.items():
            if not (keystore.keystore_dir() / f"{name}.pem").exists():
                raise SystemExit(f"keystore holds no {name}; it must already exist")
            keys[f"{purpose}-1"] = Key(name, False)
    for u in update:
        keys[f"update-{u.name.rsplit('-', 1)[1]}"] = u
    keys["witness-1"] = witness1
    if slug in ("dukcapil", "trust-authority"):
        keys["witness-2"] = witness2

    placeholder = "{SCID}"
    did_ph = f"did:webvh:{placeholder}:{domain}"
    first_state = {
        "@context": CONTEXT,
        "id": did_ph,
        "verificationMethod": [
            _method(did_ph, f"{p}-1", purpose_keys[p]) for p in purposes
        ],
        "assertionMethod": [f"{did_ph}#{p}-1" for p in purposes],
    }
    first = {
        "versionId": placeholder,
        "versionTime": time1,
        "parameters": {
            "method": "did:webvh:1.0",
            "scid": placeholder,
            "updateKeys": [update[0].multikey],
            "nextKeyHashes": [webvh.next_key_hash(update[1].multikey)],
            "witness": _witness(witness1),
            "watchers": [WATCHER],
            "portable": False,
        },
        "state": first_state,
    }
    scid = webvh.scid_of(first)
    first = json.loads(json.dumps(first).replace(placeholder, scid))
    did = f"did:webvh:{scid}:{domain}"
    first["versionId"] = "1"
    update[0].kid = f"{update[0].did_key}#{update[0].multikey}"
    _finish(first, scid, update[0])
    entries = [first]

    pop_request = None
    witness_file = None
    current = {p: f"{p}-1" for p in purposes}
    if slug == "dukcapil":
        state2 = json.loads(json.dumps(first["state"]))
        state2["verificationMethod"].append(_method(did, "issuance-jose-2", keys["issuance-jose-2"]))
        state2["assertionMethod"] = [f"{did}#issuance-jose-2", f"{did}#status-list-1"]
        second = {
            "versionId": "2",
            "versionTime": DUKCAPIL_SECOND_TIME,
            "parameters": {
                "updateKeys": [update[1].multikey],
                "nextKeyHashes": [webvh.next_key_hash(update[2].multikey)],
                "witness": _witness(witness1, witness2),
            },
            "state": state2,
        }
        _finish(second, first["versionId"], update[1])
        entries.append(second)
        current["issuance-jose"] = "issuance-jose-2"
        witness_file = [{
            "versionId": second["versionId"],
            "proof": [webvh.witness_proof(second["versionId"], witness1.private)],
        }]
    if slug == "trust-authority":
        state2 = json.loads(json.dumps(first["state"]))
        for purpose in TA_ADDED:
            state2["verificationMethod"].append(_method(did, f"{purpose}-1", keys[f"{purpose}-1"]))
            state2["assertionMethod"].append(f"{did}#{purpose}-1")
        second = {
            "versionId": "2",
            "versionTime": TA_SECOND_TIME,
            "parameters": {
                "updateKeys": [update[1].multikey],
                "nextKeyHashes": [webvh.next_key_hash(update[2].multikey)],
                "witness": _witness(witness1, witness2),
            },
            "state": state2,
        }
        _finish(second, first["versionId"], update[1])
        entries.append(second)
        for purpose in TA_ADDED:
            current[purpose] = f"{purpose}-1"
        witness_file = [{
            "versionId": second["versionId"],
            "proof": [webvh.witness_proof(second["versionId"], witness1.private)],
        }]
    for name, key in keys.items():
        if name.startswith(("update-", "witness-")):
            continue
        key.kid = f"{did}#{name}"
    return {
        "did": did, "scid": scid, "domain": domain, "role": role,
        "entries": entries, "witness_file": witness_file,
        "keys": keys, "current": current,
        "log_url": f"https://{domain}/.well-known/did.jsonl",
        "witness_url": f"https://{domain}/.well-known/did-witness.json",
    }


def build() -> dict:
    w1 = Key("ta-witness-1", True)
    w2 = Key("ta-witness-2", True)
    built = {slug: build_entity(slug, w1, w2) for slug in ENTITIES}
    ta_did = built["trust-authority"]["did"]

    duk = built["dukcapil"]
    second = duk["entries"][1]
    # Proof of possession for each key the second entry publishes for the first time.
    new_update = duk["keys"]["update-2"]
    new_jose = duk["keys"]["issuance-jose-2"]
    pops = [
        webvh.pop_jws(new_update.private, new_update.kid, ta_did, NONCE, POP_IAT),
        webvh.pop_jws(new_jose.private, new_jose.kid, ta_did, NONCE, POP_IAT),
    ]
    # ES256 signing is randomized: keep a stored proof while it still verifies and
    # says the same thing, so a re-run does not rewrite the page that quotes it.
    if OUT.exists():
        stored = json.loads(OUT.read_text()).get("publisher_request", {})
        old_pops = stored.get("proofOfPossession", [])
        if stored.get("logEntry") == second and len(old_pops) == len(pops):
            for i, (old, key) in enumerate(zip(old_pops, (new_update, new_jose))):
                same_claims = old.split(".")[:2] == pops[i].split(".")[:2]
                if same_claims and webvh.verify_pop(old, key.private.public_key()):
                    pops[i] = old
    request = {"logEntry": second, "proofOfPossession": pops, "nonce": NONCE}

    out = {"nonce": NONCE, "pop_iat": POP_IAT, "trust_authority_did": ta_did,
           "publisher_request": request,
           "witness_keys": {"ta-witness-1": w1.describe(), "ta-witness-2": w2.describe()},
           "entities": {}}
    for slug, e in built.items():
        out["entities"][slug] = {
            "did": e["did"], "scid": e["scid"], "domain": e["domain"], "role": e["role"],
            "log_url": e["log_url"], "witness_url": e["witness_url"],
            "entries": e["entries"], "witness_file": e["witness_file"],
            "current": e["current"],
            "keys": {n: k.describe() for n, k in e["keys"].items()},
        }
    return out


def verify(out: dict) -> bool:
    ok_all = True

    def check(label: str, ok: bool) -> None:
        nonlocal ok_all
        ok_all &= ok
        print(f"{'OK' if ok else 'FAIL'}  {label}")

    pubs = {}
    for slug, e in out["entities"].items():
        try:
            webvh.read_log(e["entries"])
            good = True
        except ValueError as error:
            print(error)
            good = False
        check(f"{slug}: read_log over {len(e['entries'])} entr{'y' if len(e['entries']) == 1 else 'ies'}", good)
        check(f"{slug}: scid is the hash of its own first entry, and every id carries it",
              webvh.scid_of(e["entries"][0]) == e["scid"]
              and all(s["state"]["id"] == e["did"] for s in e["entries"]))
        # Every key a DID Document lists is the keystore key it is named for.
        state = e["entries"][-1]["state"]
        listed = {m["id"]: m["publicKeyMultibase"] for m in state["verificationMethod"]}
        match = all(
            k["multikey"] == listed.get(k["kid"])
            for n, k in e["keys"].items() if not n.startswith(("update-", "witness-"))
        ) and len(listed) == sum(1 for n in e["keys"] if not n.startswith(("update-", "witness-")))
        check(f"{slug}: DID Document keys match the keystore", match)
        pubs[slug] = e

    w1 = out["witness_keys"]["ta-witness-1"]
    for slug in ("dukcapil", "trust-authority"):
        ent = out["entities"][slug]
        wf = ent["witness_file"][0]
        wproof = wf["proof"][0]
        check(f"{slug}: witness proof verifies, from ta-witness-1's did:key, on the second entry",
              webvh.verify_witness_proof(wf["versionId"], wproof)
              and wf["versionId"] == ent["entries"][1]["versionId"]
              and wproof["verificationMethod"] == f"{w1['did_key']}#{w1['multikey']}")
    check(f"trust-authority: scid unchanged ({EXPECTED_TA_SCID})",
          out["entities"]["trust-authority"]["scid"] == EXPECTED_TA_SCID)
    duk = out["entities"]["dukcapil"]

    req = out["publisher_request"]
    check("request body: logEntry is the second entry, nonce is the fixed one",
          req["logEntry"] == duk["entries"][1] and req["nonce"] == out["nonce"])
    first_keys = {duk["entries"][0]["parameters"]["updateKeys"][0]} | {
        m["publicKeyMultibase"] for m in duk["entries"][0]["state"]["verificationMethod"]
    }
    new = [duk["keys"]["update-2"], duk["keys"]["issuance-jose-2"]]
    check("request body: the keys needing proof are exactly the ones first published in entry 2",
          {k["multikey"] for k in new} & first_keys == set() and len(req["proofOfPossession"]) == 2)
    for token, k in zip(req["proofOfPossession"], new):
        head = json.loads(base64.urlsafe_b64decode(token.split(".")[0] + "=="))
        body = json.loads(base64.urlsafe_b64decode(token.split(".")[1] + "=="))
        public = webvh.public_key_from_multikey(k["multikey"])
        check(f"proof of possession of {k['keystore']}: signature, kid, aud, nonce",
              webvh.verify_pop(token, public) and head["kid"] == k["kid"]
              and head["alg"] == k["algorithm"] and body["aud"] == out["trust_authority_did"]
              and body["nonce"] == out["nonce"])
    return ok_all


def main() -> int:
    out = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {OUT.relative_to(webvh.REPO_ROOT)}")
    # Verify what was written to disk, not what is in memory.
    ok = verify(json.loads(OUT.read_text()))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
