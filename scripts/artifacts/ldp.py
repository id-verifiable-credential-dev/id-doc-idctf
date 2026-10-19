"""Data Integrity proofs in ``ecdsa-rdfc-2019`` for the ``ldp_vc`` artifacts.

Builds the Kartu Nikah credential (TS-5-10), the two Bitstring Status List
credentials (TS-5-09) and the ``ldp_vc`` presentation (TS-5-11), signs each with
a key the keystore keeps, and verifies every proof again from the result.

RDF Dataset Canonicalization runs through PyLD with a document loader that
reads only ``scripts/artifacts/contexts/``: the run never touches the network.
PyLD names the algorithm ``URDNA2015``; RDFC-1.0 is the same algorithm under its
W3C Recommendation name.

The content of each artifact (claims, times, status entries, list bits) is read
from the page that shows it. Only identifiers, ``verificationMethod`` and
``proofValue`` are rewritten, from ``build/artifacts/webvh.json`` and the
keystore. Signing is randomized, so a run with an existing, still-verifying
``build/artifacts/ldp.json`` reuses it; pass ``--rebuild`` to sign again.

Run as ``.venv/bin/python scripts/artifacts/ldp.py``.
"""

from __future__ import annotations

import base64
import gzip
import hashlib
import json
import re
import sys
from pathlib import Path

import base58
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.utils import (
    decode_dss_signature,
    encode_dss_signature,
)
from pyld import jsonld

sys.path.insert(0, str(Path(__file__).resolve().parent))
import keystore  # noqa: E402
import webvh  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
TS_DIR = REPO_ROOT / "docs" / "technical-specifications"
CONTEXT_DIR = Path(__file__).resolve().parent / "contexts"
WEBVH_JSON = REPO_ROOT / "build" / "artifacts" / "webvh.json"
OUT = REPO_ROOT / "build" / "artifacts" / "ldp.json"

CONTEXT_FILES = {
    "https://www.w3.org/ns/credentials/v2": "credentials-v2.jsonld",
    "https://catalog.trust.go.id/type-metadata/kartu-nikah-v1/context.jsonld": (
        "kartu-nikah-v1.jsonld"
    ),
}
RULEBOOK_CONTEXT = (
    REPO_ROOT / "docs" / "credential-rulebook" / "example" / "kartu-nikah" / "context.jsonld"
)

HOLDER_KEY_NAME = "holder-credential-1"  # shared with statuslists.py: one wallet key
CRYPTOSUITE = "ecdsa-rdfc-2019"
# The nonce of the Kartu Nikah Request Object of TS-5-06, which presentations.py
# writes from this value; the presentation carries it as challenge.
CHALLENGE = "RuHSu26QAGIX4UP7H-ulTA"

PAGE_ISSUE = TS_DIR / "issuing-a-credential-in-sd-jwt-vc-mdoc-and-ldp-vc.md"
PAGE_STATUS = TS_DIR / "publishing-and-reading-a-status-list.md"
PAGE_PRESENT = TS_DIR / "building-and-verifying-a-presentation.md"

T_CREDENTIAL = "A Kartu Nikah in ldp_vc, as issued"
T_REVOCATION = "Bitstring Status List credential, revocation purpose"
T_SUSPENSION = "Bitstring Status List credential, suspension purpose"
T_ENTRIES = "The credentialStatus entries of an ldp_vc credential"
T_PRESENTATION = "The vp_token of an ldp_vc presentation"

REVOKED_INDEX = 94721
LIST_SIZE = 524288


# ---------------------------------------------------------------- offline loader


def _loader(url, options=None):
    name = CONTEXT_FILES.get(url.split("#")[0])
    if name is None:
        raise jsonld.JsonLdError(
            f"refused to fetch {url}: not cached under scripts/artifacts/contexts/",
            "jsonld.LoadDocumentError",
            code="loading document failed",
        )
    document = json.loads((CONTEXT_DIR / name).read_text())
    return {"contentType": "application/ld+json", "contextUrl": None,
            "documentUrl": url, "document": document}


jsonld.set_document_loader(_loader)


def canonical(document: dict) -> bytes:
    """Canonical N-Quads of ``document`` (RDFC-1.0, PyLD's ``URDNA2015``)."""
    return jsonld.normalize(
        document, {"algorithm": "URDNA2015", "format": "application/n-quads"}
    ).encode()


# ------------------------------------------------------------- Data Integrity


def _hash_data(proof_config: dict, document: dict) -> bytes:
    return (
        hashlib.sha256(canonical(proof_config)).digest()
        + hashlib.sha256(canonical(document)).digest()
    )


def _proof_config(document: dict, proof: dict) -> dict:
    config = {k: v for k, v in proof.items() if k != "proofValue"}
    return {"@context": document["@context"], **config}


def sign(document: dict, private_key, proof_options: dict) -> dict:
    """``document`` with a Data Integrity proof under ``proof_options`` added."""
    bare = {k: v for k, v in document.items() if k != "proof"}
    r, s = decode_dss_signature(
        private_key.sign(
            _hash_data(_proof_config(bare, proof_options), bare), _ecdsa()
        )
    )
    proof = dict(proof_options)
    proof["proofValue"] = "z" + base58.b58encode(
        r.to_bytes(32, "big") + s.to_bytes(32, "big")
    ).decode()
    return {**bare, "proof": proof}


def _ecdsa():
    from cryptography.hazmat.primitives.asymmetric import ec

    return ec.ECDSA(hashes.SHA256())


def verify(document: dict, public_key) -> bool:
    try:
        proof = document["proof"]
        if (
            proof["type"] != "DataIntegrityProof"
            or proof["cryptosuite"] != CRYPTOSUITE
            or not proof["proofValue"].startswith("z")
        ):
            return False
        raw = base58.b58decode(proof["proofValue"][1:])
        if len(raw) != 64:
            return False
        bare = {k: v for k, v in document.items() if k != "proof"}
        public_key.verify(
            encode_dss_signature(
                int.from_bytes(raw[:32], "big"), int.from_bytes(raw[32:], "big")
            ),
            _hash_data(_proof_config(bare, proof), bare),
            _ecdsa(),
        )
        return True
    except (InvalidSignature, KeyError, ValueError, TypeError):
        return False


# ------------------------------------------------------------------ the pages


def block(page: Path, title: str) -> str:
    text = page.read_text()
    match = re.search(
        r"^``` \{[^}\n]*title=\"" + re.escape(title) + r"\"[^}\n]*\}\n(.*?)^```$",
        text,
        re.S | re.M,
    )
    if not match:
        raise SystemExit(f"no block titled {title!r} in {page.name}")
    return match.group(1)


def page_json(page: Path, title: str):
    return json.loads(block(page, title))


def dump(obj) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False)


def _topology():
    data = json.loads(WEBVH_JSON.read_text())
    kemenag = data["entities"]["kemenag"]
    terminal = data["entities"]["terminal-nusantara"]
    return data, kemenag, terminal


def _all_keys(data: dict) -> dict:
    """Every key ``webvh.json`` records, by ``kid``."""
    keys = {}
    for entity in data["entities"].values():
        for key in entity["keys"].values():
            keys[key["kid"]] = key
    return keys


def _public_key_for(vm: str, keys: dict):
    """Public key a ``verificationMethod`` names: a DID URL in webvh.json or a did:key."""
    if vm in keys:
        return webvh.public_key_from_multikey(keys[vm]["multikey"])
    if vm.startswith("did:key:"):
        material, _, fragment = vm.removeprefix("did:key:").partition("#")
        if fragment != material:
            raise ValueError(f"did:key URL {vm} does not name its own key")
        return webvh.public_key_from_multikey(material)
    raise ValueError(f"{vm} is not in webvh.json")


# ----------------------------------------------------------------------- build


def build() -> dict:
    data, kemenag, terminal = _topology()
    issuer_did = kemenag["did"]
    issuance = kemenag["keys"][kemenag["current"]["issuance-jose"]]
    status = kemenag["keys"][kemenag["current"]["status-list"]]
    issuance_key = keystore.load_or_create(issuance["keystore"])
    status_key = keystore.load_or_create(status["keystore"])

    holder_key = keystore.load_or_create(HOLDER_KEY_NAME)
    holder_multikey = webvh.multikey(holder_key.public_key())
    holder_did = webvh.did_key(holder_multikey)
    holder_vm = f"{holder_did}#{holder_multikey}"

    # The Kartu Nikah credential: same content, new identifiers, new proof.
    old = page_json(PAGE_ISSUE, T_CREDENTIAL)
    old_proof = old.pop("proof")
    credential = dict(old)
    credential["issuer"] = issuer_did
    # One year, the ceiling of id.idctf.kartu-nikah.1 (tracks/0421), from validFrom.
    credential["validUntil"] = "2027-10-17T06:00:10Z"
    credential["credentialSubject"] = {**old["credentialSubject"], "id": holder_did}
    credential = sign(
        credential,
        issuance_key,
        {
            "type": "DataIntegrityProof",
            "cryptosuite": CRYPTOSUITE,
            "created": old_proof["created"],
            "verificationMethod": issuance["kid"],
            "proofPurpose": "assertionMethod",
        },
    )

    # The two status list credentials.
    lists = {}
    for title in (T_REVOCATION, T_SUSPENSION):
        doc = page_json(PAGE_STATUS, title)
        doc_proof = doc.pop("proof")
        doc["issuer"] = issuer_did
        lists[title] = sign(
            doc,
            status_key,
            {
                "type": "DataIntegrityProof",
                "cryptosuite": CRYPTOSUITE,
                "created": doc_proof["created"],
                "verificationMethod": status["kid"],
                "proofPurpose": "assertionMethod",
            },
        )

    entries = page_json(PAGE_STATUS, T_ENTRIES)

    # The presentation: the credential above, wrapped and signed by the holder.
    old_vp = page_json(PAGE_PRESENT, T_PRESENTATION)["kartu-nikah"][0]
    old_vp_proof = old_vp["proof"]
    presentation = {k: v for k, v in old_vp.items() if k != "proof"}
    presentation["holder"] = holder_did
    presentation["verifiableCredential"] = [credential]
    presentation = sign(
        presentation,
        holder_key,
        {
            "type": "DataIntegrityProof",
            "cryptosuite": CRYPTOSUITE,
            "created": old_vp_proof["created"],
            "verificationMethod": holder_vm,
            "proofPurpose": "authentication",
            "challenge": CHALLENGE,
            "domain": "decentralized_identifier:" + terminal["did"],
        },
    )
    vp_token = {"kartu-nikah": [presentation]}

    return {
        "cryptosuite": CRYPTOSUITE,
        "canonicalization": "RDFC-1.0 (PyLD URDNA2015), offline contexts",
        "holder": {
            "keystore": HOLDER_KEY_NAME,
            "multikey": holder_multikey,
            "did_key": holder_did,
            "kid": holder_vm,
            "algorithm": "ES256",
        },
        "blocks": {
            T_CREDENTIAL: dump(credential),
            T_REVOCATION: dump(lists[T_REVOCATION]),
            T_SUSPENSION: dump(lists[T_SUSPENSION]),
            T_ENTRIES: dump(entries),
            T_PRESENTATION: dump(vp_token),
        },
        "documents": {
            "credential": credential,
            "revocation_list": lists[T_REVOCATION],
            "suspension_list": lists[T_SUSPENSION],
            "credential_status": entries,
            "presentation": presentation,
            "vp_token": vp_token,
        },
    }


# ---------------------------------------------------------------------- verify


class Checks:
    def __init__(self):
        self.failed = 0

    def ok(self, label: str, passed: bool, detail: str = ""):
        print(("OK   " if passed else "FAIL ") + label + (f" ({detail})" if detail else ""))
        if not passed:
            self.failed += 1


def _decode_list(encoded: str) -> bytes:
    raw = base64.urlsafe_b64decode(encoded[1:] + "=" * (-len(encoded[1:]) % 4))
    return gzip.decompress(raw)


def _bit(bits: bytes, index: int) -> int:
    return (bits[index // 8] >> (7 - index % 8)) & 1


def check(result: dict, quiet_build: bool = False) -> int:
    c = Checks()
    data, kemenag, terminal = _topology()
    keys = _all_keys(data)
    docs = result["documents"]

    # contexts and canonicalization
    c.ok(
        "cached Kartu Nikah context equals the Rulebook example's context.jsonld",
        (CONTEXT_DIR / "kartu-nikah-v1.jsonld").read_bytes() == RULEBOOK_CONTEXT.read_bytes(),
    )
    try:
        jsonld.expand({"@context": "https://example.org/not-cached", "id": "x"})
        refused = False
    except jsonld.JsonLdError:
        refused = True
    c.ok("document loader refuses a URL that is not cached", refused)

    credential = docs["credential"]
    for label, doc in (
        ("credential", credential),
        ("revocation list", docs["revocation_list"]),
        ("suspension list", docs["suspension_list"]),
        ("presentation", docs["presentation"]),
    ):
        bare = {k: v for k, v in doc.items() if k != "proof"}
        if label == "presentation":
            # the embedded credential is checked on its own above
            bare = {k: v for k, v in bare.items() if k != "verifiableCredential"}
        round_trip = jsonld.compact(jsonld.expand(bare), bare["@context"])
        round_trip["@context"] = bare["@context"]
        if isinstance(round_trip.get("type"), str):
            round_trip["type"] = [round_trip["type"]]
        c.ok(
            f"{label}: every term is defined by a cached context (expand and compact lose nothing)",
            round_trip == bare,
        )

    # proofs
    def proof_check(label, document, who):
        vm = document["proof"]["verificationMethod"]
        key = _public_key_for(vm, keys)
        c.ok(f"{label}: {CRYPTOSUITE} proof verifies under {who}", verify(document, key), vm)
        c.ok(
            f"{label}: cryptosuite is {CRYPTOSUITE}",
            document["proof"]["cryptosuite"] == CRYPTOSUITE
            and document["proof"]["type"] == "DataIntegrityProof",
        )
        tampered = json.loads(json.dumps(document))
        tampered["holder" if "holder" in tampered else "validFrom"] = "did:key:z6MkTampered"
        c.ok(f"{label}: a changed document breaks the proof", not verify(tampered, key))

    issuer_did = kemenag["did"]
    proof_check("Kartu Nikah credential", credential, "Kemenag issuance-jose")
    c.ok("credential issuer is Kemenag's DID in webvh.json", credential["issuer"] == issuer_did)
    c.ok(
        "credential verificationMethod is the DID Document key issuance-jose",
        credential["proof"]["verificationMethod"]
        == kemenag["keys"][kemenag["current"]["issuance-jose"]]["kid"],
    )
    proof_check("revocation list", docs["revocation_list"], "Kemenag status-list")
    proof_check("suspension list", docs["suspension_list"], "Kemenag status-list")
    for name in ("revocation_list", "suspension_list"):
        c.ok(
            f"{name}: issuer is Kemenag's DID, key is status-list",
            docs[name]["issuer"] == issuer_did
            and docs[name]["proof"]["verificationMethod"]
            == kemenag["keys"][kemenag["current"]["status-list"]]["kid"],
        )

    # list content
    for name, purpose, revoked in (
        ("revocation_list", "revocation", True),
        ("suspension_list", "suspension", False),
    ):
        doc = docs[name]
        bits = _decode_list(doc["credentialSubject"]["encodedList"])
        c.ok(f"{name}: purpose is {purpose}", doc["credentialSubject"]["statusPurpose"] == purpose)
        c.ok(f"{name}: {len(bits) * 8} entries", len(bits) * 8 == LIST_SIZE)
        set_bits = [i for i in range(LIST_SIZE) if _bit(bits, i)]
        c.ok(
            f"{name}: set entries are {[REVOKED_INDEX] if revoked else []}",
            set_bits == ([REVOKED_INDEX] if revoked else []),
        )
    c.ok(
        "credentialStatus entries equal the credential's",
        docs["credential_status"] == credential["credentialStatus"],
    )
    for entry in credential["credentialStatus"]:
        target = (
            docs["revocation_list"]
            if entry["statusPurpose"] == "revocation"
            else docs["suspension_list"]
        )
        index = int(entry["statusListIndex"])
        bits = _decode_list(target["credentialSubject"]["encodedList"])
        c.ok(
            f"entry {entry['statusPurpose']}: points at its list and its bit is clear",
            entry["statusListCredential"] == target["id"] and _bit(bits, index) == 0,
            f"index {index}",
        )

    # presentation
    vp = docs["presentation"]
    holder = result["holder"]
    c.ok("presentation holder is the credential subject", vp["holder"] == credential["credentialSubject"]["id"] == holder["did_key"])
    proof_check("presentation", vp, "the holder credential key")
    c.ok(
        "presentation proofPurpose is authentication",
        vp["proof"]["proofPurpose"] == "authentication",
    )
    c.ok(
        "presentation domain names Terminal Nusantara's DID",
        vp["proof"]["domain"] == "decentralized_identifier:" + terminal["did"],
    )
    c.ok(
        "embedded credential is byte-identical to the issued one",
        vp["verifiableCredential"] == [credential],
    )
    c.ok(
        "embedded credential's proof verifies on its own",
        verify(vp["verifiableCredential"][0], _public_key_for(
            vp["verifiableCredential"][0]["proof"]["verificationMethod"], keys)),
    )
    c.ok(
        "vp_token is keyed by the credential query id",
        list(docs["vp_token"]) == ["kartu-nikah"] and docs["vp_token"]["kartu-nikah"] == [vp],
    )

    # the text that goes into the pages is the same as the documents
    blocks = result["blocks"]
    c.ok("block text of the credential parses to the document", json.loads(blocks[T_CREDENTIAL]) == credential)
    c.ok("block text of the presentation parses to the vp_token", json.loads(blocks[T_PRESENTATION]) == docs["vp_token"])
    c.ok(
        "five blocks produced",
        list(blocks) == [T_CREDENTIAL, T_REVOCATION, T_SUSPENSION, T_ENTRIES, T_PRESENTATION],
    )

    # the claim values the Rulebook example shows
    for path in sorted((REPO_ROOT / "docs" / "credential-rulebook" / "example").rglob("*.md")):
        text = path.read_text()
        if "nomor_akta_nikah" in text and "0123/0007/V/2025" in text:
            subject = credential["credentialSubject"]
            same = all(
                str(subject[k]) in text
                for k in ("nama_suami", "nama_istri", "tanggal_akad", "nomor_akta_nikah", "kua",
                          "kabupaten_kota", "provinsi")
            )
            c.ok(f"claim values appear unchanged in {path.relative_to(REPO_ROOT)}", same)
    return c.failed


def main(argv: list[str]) -> int:
    rebuild = "--rebuild" in argv
    result = None
    if OUT.exists() and not rebuild:
        existing = json.loads(OUT.read_text())
        print("reusing build/artifacts/ldp.json (pass --rebuild to sign again)")
        if check_silent(existing):
            result = existing
        else:
            print("existing ldp.json no longer verifies; rebuilding")
    if result is None:
        result = build()
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
        print(f"wrote {OUT.relative_to(REPO_ROOT)}")
    failed = check(result)
    if failed:
        print(f"{failed} check(s) failed")
        return 1
    print("all checks passed")
    return 0


def check_silent(result: dict) -> bool:
    import contextlib
    import io

    try:
        with contextlib.redirect_stdout(io.StringIO()):
            return check(result) == 0
    except Exception:
        return False


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
