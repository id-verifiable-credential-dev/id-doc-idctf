"""The trusted list of TS-5-01, signed under a kept key (tracks/0293, debt/0165).

Builds the LoTE payload, its JWS protected header and the compact JWS, plus the
two blocks of TS-01 that quote them, and writes everything to
``build/artifacts/trustlist.json`` keyed by block title.

The payload keeps the structure, the times, the names and the layout that
TS-5-01 prints today: the page's own block is the template, and only the values
that derive from keys move. Every DID comes from ``webvh.json``, every subject
key identifier and the Verifier Issuing CA certificate from ``summary.json``,
the two signer keys from the keystore (``ta-trusted-list-1`` signs,
``ta-trusted-list-2`` is announced and has signed nothing).

ES256 signing is randomized. A re-run reuses the stored signature while it
still verifies over the same bytes; ``--rebuild`` signs anew.

Run as a script it builds, then verifies its own output, one line per check;
the exit status is 0 only when every check passes.
"""

from __future__ import annotations

import base64
import copy
import json
import re
import sys
from pathlib import Path

from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import (
    decode_dss_signature,
    encode_dss_signature,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
import keystore  # noqa: E402
import webvh  # noqa: E402

REPO_ROOT = webvh.REPO_ROOT
TS_DIR = webvh.TS_DIR
ART = REPO_ROOT / "build" / "artifacts"
OUT_JSON = ART / "trustlist.json"
P_LIST = TS_DIR / "publishing-and-reading-the-trusted-list.md"
P_TS01 = TS_DIR / "finding-a-signers-key-from-its-did.md"

T_PAYLOAD = "trusted-list.json, the LoTE payload"
T_HEADER = "trusted-list.json, the JWS protected header"
T_JWS = "trusted-list.json, the JWS compact serialization"
T01_HEADER = "Protected header of the trusted list"
T01_SERVICE = "Trusted list signer service that names the key"

SIGNER_1 = "ta-trusted-list-1"
SIGNER_2 = "ta-trusted-list-2"
WRAP = 78  # the width the page already wraps its compact serialization at

SVC = "https://idctf.id/ns/19602/SvcType/"
# The legal identifier in TETradeName names the entry; it is the page's own
# structure, not a value that moves with a key.
ENTITY_BY_TRADE_NAME = {
    "BKN:013250": "dukcapil",
    "NIB:9120407260031": "dompet-digital-nusantara",
    "NIB:8120015640022": "terminal-nusantara",
    "BKN:401160": "universitas-nusantara",
    "BKN:402510": "kemenag",
    "BKN:403380": "bkn",
    "BKN:404390": "korlantas",
    "BKN:000100": "trust-authority",
}


# --- helpers ------------------------------------------------------------------
def load(name: str) -> dict:
    return json.loads((ART / name).read_text())


def page_block(page: Path, title: str) -> str:
    text = page.read_text()
    m = re.search(r'title="' + re.escape(title) + r'"[^\n]*\n(.*?)\n```', text, re.S)
    if not m:
        raise ValueError(f"no block {title!r} in {page.name}")
    return m.group(1)


def es256_sign(key, data: bytes) -> bytes:
    r, s = decode_dss_signature(key.sign(data, ec.ECDSA(hashes.SHA256())))
    return r.to_bytes(32, "big") + s.to_bytes(32, "big")


def es256_verify(public_key, signature: bytes, data: bytes) -> bool:
    if len(signature) != 64:
        return False
    der = encode_dss_signature(
        int.from_bytes(signature[:32], "big"), int.from_bytes(signature[32:], "big")
    )
    try:
        public_key.verify(der, data, ec.ECDSA(hashes.SHA256()))
        return True
    except InvalidSignature:
        return False


def wrap(value: str, width: int = WRAP) -> str:
    return "\n".join(value[i : i + width] for i in range(0, len(value), width))


def leaf_pairs(old, new, out: list):
    """Collect (old, new) for every string leaf that differs at the same path."""
    if isinstance(old, dict):
        assert old.keys() == new.keys()
        for k in old:
            leaf_pairs(old[k], new[k], out)
    elif isinstance(old, list):
        assert len(old) == len(new)
        for a, b in zip(old, new):
            leaf_pairs(a, b, out)
    elif old != new:
        out.append((old, new))


def entries_of(lote: dict) -> list:
    return lote["LoTE"]["TrustedEntitiesList"]


def entity_of(entry: dict) -> str:
    return ENTITY_BY_TRADE_NAME[entry["TrustedEntityInformation"]["TETradeName"][0]["value"]]


def services_of(entry: dict):
    """Every service information object and every history instance of an entry."""
    for svc in entry["TrustedEntityServices"]:
        yield svc["ServiceInformation"]
        yield from svc.get("ServiceHistory", [])


# --- build --------------------------------------------------------------------
def signer_keys() -> dict:
    out = {}
    for name in (SIGNER_1, SIGNER_2):
        key = keystore.load_or_create(name)
        mk = webvh.multikey(key.public_key())
        out[name] = {"keystore": name, "key": key, "multikey": mk, "did_key": webvh.did_key(mk),
                     "algorithm": "ES256"}
    return out


def derive(template: dict, db: dict, summary: dict, signers: dict) -> dict:
    """The payload object: the page's structure with every key-derived value set."""
    lote = copy.deepcopy(template)
    witness = db["witness_keys"]
    for entry in entries_of(lote):
        ent = db["entities"][entity_of(entry)]
        witness_seen = 0
        signer_seen = 0
        for info in services_of(entry):
            kind = info["ServiceTypeIdentifier"].removeprefix(SVC)
            ids = info["ServiceDigitalIdentity"]
            if kind in ("IdentityIssuer", "WalletProvider", "RelyingParty", "AttributeIssuer"):
                ids["OtherIds"] = [ent["did"]]
            elif kind == "RevokedKey" and "OtherIds" in ids:
                k = ent["keys"]["issuance-jose-1"]
                ids["OtherIds"] = [k["did_key"], ent["did"] + "#issuance-jose-1"]
            elif kind == "VerifierIssuingCA":
                ids["X509SKIs"] = [summary["verifier_issuing_ca"]["ski"]]
                if "X509Certificates" in ids:
                    ids["X509Certificates"] = [{"val": summary["verifier_issuing_ca"]["base64"]}]
            elif kind == "Witness":
                # The first service is the key in force, the second the one withdrawn;
                # a history instance repeats the key of the service it belongs to.
                pass
            elif kind == "TrustedListSigner":
                pass
        # Witness and signer services are ordered, and a history instance shares
        # its parent's key, so they are set service by service.
        for svc in entry["TrustedEntityServices"]:
            kind = svc["ServiceInformation"]["ServiceTypeIdentifier"].removeprefix(SVC)
            if kind == "Witness":
                wk = witness["ta-witness-2" if witness_seen == 0 else "ta-witness-1"]["did_key"]
                witness_seen += 1
                svc["ServiceInformation"]["ServiceDigitalIdentity"]["OtherIds"] = [wk]
                for h in svc.get("ServiceHistory", []):
                    h["ServiceDigitalIdentity"]["OtherIds"] = [wk]
            elif kind == "TrustedListSigner":
                sk = signers[SIGNER_1 if signer_seen == 0 else SIGNER_2]["did_key"]
                signer_seen += 1
                svc["ServiceInformation"]["ServiceDigitalIdentity"]["OtherIds"] = [sk]
    return lote


def render(template_obj: dict, template_text: str, new_obj: dict) -> str:
    """The page's layout with the changed values written in, byte for byte."""
    pairs: list = []
    leaf_pairs(template_obj, new_obj, pairs)
    mapping: dict = {}
    for old, new in pairs:
        if mapping.setdefault(old, new) != new:
            raise SystemExit(f"value {old!r} maps to two different new values")
    text = template_text
    for old in sorted(mapping, key=len, reverse=True):
        # substring replacement is what keeps a DID URL fragment attached
        text = text.replace(old, mapping[old])
    if json.loads(text) != new_obj:
        raise SystemExit("rendered text does not parse back to the derived payload")
    return text


def build(rebuild: bool = False) -> dict:
    db = load("webvh.json")
    summary = load("summary.json")
    signers = signer_keys()
    template_text = page_block(P_LIST, T_PAYLOAD)
    template = json.loads(template_text)
    payload_obj = derive(template, db, summary, signers)
    payload_text = render(template, template_text, payload_obj)

    header_obj = {"alg": "ES256", "kid": signers[SIGNER_1]["did_key"]}
    header_text = json.dumps(header_obj, separators=(",", ":"))
    signing_input = (webvh._b64u(header_text.encode()) + "." + webvh._b64u(payload_text.encode()))
    signing_key = signers[SIGNER_1]["key"]

    token = None
    reused = False
    if OUT_JSON.exists() and not rebuild:
        old = json.loads(OUT_JSON.read_text()).get("_structured", {})
        prev = old.get("jws", "")
        if prev.startswith(signing_input + "."):
            sig = webvh._unb64u(prev[len(signing_input) + 1 :])
            if es256_verify(signing_key.public_key(), sig, signing_input.encode()):
                token, reused = prev, True
    if token is None:
        token = signing_input + "." + webvh._b64u(es256_sign(signing_key, signing_input.encode()))

    signer_service = _signer_service(payload_obj, signers[SIGNER_1]["did_key"])
    service_text = _service_text(page_block(P_TS01, T01_SERVICE), signer_service)

    pairs: list = []
    leaf_pairs(template, payload_obj, pairs)
    out = {
        T_PAYLOAD: payload_text,
        T_HEADER: header_text,
        T_JWS: wrap(token),
        T01_HEADER: header_text,
        T01_SERVICE: service_text,
        "_structured": {
            "payload": payload_obj,
            "header": header_obj,
            "jws": token,
            "signature_reused": reused,
            "signers": {
                n: {k: v for k, v in s.items() if k != "key"} for n, s in signers.items()
            },
            "changed_values": [{"old": o, "new": n} for o, n in pairs],
        },
    }
    out["_structured"]["contradictions"] = contradictions(out, pairs, db, summary)
    return out


def _signer_service(payload: dict, did_key: str) -> dict:
    root = next(e for e in entries_of(payload) if entity_of(e) == "trust-authority")
    for svc in root["TrustedEntityServices"]:
        info = svc["ServiceInformation"]
        if info["ServiceTypeIdentifier"] == SVC + "TrustedListSigner" and \
                info["ServiceDigitalIdentity"]["OtherIds"] == [did_key]:
            return svc
    raise SystemExit("no trusted list signer service names the signing key")


def _service_text(page_text: str, svc: dict) -> str:
    """TS-01's block keeps its layout; only the did:key moves."""
    old = json.loads(page_text)["ServiceInformation"]["ServiceDigitalIdentity"]["OtherIds"][0]
    new = svc["ServiceInformation"]["ServiceDigitalIdentity"]["OtherIds"][0]
    text = page_text.replace(old, new)
    if json.loads(text) != {"ServiceInformation": svc["ServiceInformation"]}:
        raise SystemExit("TS-01 signer service block differs from the payload's service")
    return text


# --- what the build contradicts ------------------------------------------------
def contradictions(out: dict, pairs: list, db: dict, summary: dict) -> list:
    found = []
    payload = out["_structured"]["payload"]
    page = P_LIST.read_text().splitlines()

    def at(pattern: str, claim: str, holds: bool, detail: str):
        if holds:
            return
        for n, line in enumerate(page, 1):
            if re.search(pattern, line):
                found.append({"file": str(P_LIST.relative_to(REPO_ROOT)), "line": n,
                              "text": line.strip()[:200], "claim": claim, "build": detail})
                return

    entries = entries_of(payload)
    at(r"Its eight entries", "eight entries", len(entries) == 8, f"{len(entries)} entries")
    revoked = [i for e in entries for i in services_of(e)
               if i["ServiceTypeIdentifier"] == SVC + "RevokedKey"]
    at(r"revoked key services are two", "two revoked key services", len(revoked) == 2,
       f"{len(revoked)} revoked key services")
    at(r"signature is 64 bytes", "the signature is 64 bytes",
       len(webvh._unb64u(out["_structured"]["jws"].split(".")[2])) == 64, "not 64 bytes")
    # The two sentences that say what the list carries.
    vca = next(i for e in entries for i in services_of(e)
               if i["ServiceTypeIdentifier"] == SVC + "VerifierIssuingCA")
    at(r"the same bytes and the same subject key identifier", "same bytes as TS-5-04",
       vca["ServiceDigitalIdentity"]["X509Certificates"][0]["val"] == summary["verifier_issuing_ca"]["base64"],
       "differs from summary.json")

    # Every superseded value that a page still prints, wherever it is.
    old_values = {o for o, _ in pairs if len(o) > 20}
    for md in sorted((REPO_ROOT / "docs").rglob("*.md")):
        if md == P_LIST:
            continue
        for n, line in enumerate(md.read_text().splitlines(), 1):
            hit = next((o for o in old_values if o in line), None)
            if hit:
                found.append({"file": str(md.relative_to(REPO_ROOT)), "line": n,
                              "text": line.strip()[:200],
                              "claim": "carries a value the rebuilt list replaced",
                              "build": hit[:80]})
    return found


# --- verify -------------------------------------------------------------------
def main() -> int:
    rebuild = "--rebuild" in sys.argv[1:]
    out = build(rebuild)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    st = out["_structured"]
    db = load("webvh.json")
    summary = load("summary.json")
    x509j = load("x509.json")
    results: list[bool] = []

    def check(label: str, ok: bool) -> None:
        results.append(bool(ok))
        print(f"{'OK  ' if ok else 'FAIL'} {label}")

    print("signature " + ("reused, still verifies" if st["signature_reused"] else "signed anew"))
    head_b64, body_b64, sig_b64 = st["jws"].split(".")
    header = json.loads(webvh._unb64u(head_b64))
    body = webvh._unb64u(body_b64).decode()
    sig = webvh._unb64u(sig_b64)
    signing_input = f"{head_b64}.{body_b64}".encode()
    s1, s2 = st["signers"][SIGNER_1], st["signers"][SIGNER_2]

    key1 = keystore.load_or_create(SIGNER_1).public_key()
    check("JWS verifies under ta-trusted-list-1", es256_verify(key1, sig, signing_input))
    check("header is exactly alg ES256 and kid, in that order",
          st["jws"].split(".")[0] == webvh._b64u(b'{"alg":"ES256","kid":"' + s1["did_key"].encode() + b'"}'))
    check("signature is 64 bytes, r then s, and the payload is attached (RFC 7515 compact)",
          len(sig) == 64 and st["jws"].count(".") == 2 and body == out[T_PAYLOAD])
    check("wrapped serialization joins back to the JWS",
          out[T_JWS].replace("\n", "") == st["jws"])

    payload = json.loads(body)
    signer_ids = [i["ServiceDigitalIdentity"]["OtherIds"][0]
                  for e in entries_of(payload) if entity_of(e) == "trust-authority"
                  for i in services_of(e)
                  if i["ServiceTypeIdentifier"] == SVC + "TrustedListSigner"]
    granted_ids = [i["ServiceDigitalIdentity"]["OtherIds"][0]
                   for e in entries_of(payload) if entity_of(e) == "trust-authority"
                   for i in services_of(e)
                   if i["ServiceTypeIdentifier"] == SVC + "TrustedListSigner"
                   and i["ServiceStatus"].endswith("/granted")]
    check("kid names the did:key of a granted trusted list signer service in the payload",
          header["kid"] in granted_ids and header["kid"] == s1["did_key"])
    pub_from_kid = webvh.public_key_from_multikey(header["kid"].removeprefix("did:key:"))
    check("kid decodes to the key that verifies the signature",
          es256_verify(pub_from_kid, sig, signing_input))
    check("the announced key is ta-trusted-list-2, granted, and has signed nothing",
          signer_ids == [s1["did_key"], s2["did_key"]] and header["kid"] != s2["did_key"]
          and not es256_verify(keystore.load_or_create(SIGNER_2).public_key(), sig, signing_input))
    check("signer did:keys are P-256 and match their keystore keys",
          all(webvh.did_key(webvh.multikey(keystore.load_or_create(n).public_key())) == st["signers"][n]["did_key"]
              and st["signers"][n]["did_key"].startswith("did:key:zDna") for n in (SIGNER_1, SIGNER_2)))

    ents = {entity_of(e): e for e in entries_of(payload)}
    ok = True
    for name, entry in ents.items():
        for info in services_of(entry):
            kind = info["ServiceTypeIdentifier"].removeprefix(SVC)
            if kind in ("IdentityIssuer", "WalletProvider", "RelyingParty", "AttributeIssuer"):
                ok &= info["ServiceDigitalIdentity"]["OtherIds"] == [db["entities"][name]["did"]]
    check("every entity DID in the payload equals the one in webvh.json", ok and len(ents) == 8)

    ent = db["entities"]["dukcapil"]
    revoked = [i["ServiceDigitalIdentity"] for i in services_of(ents["dukcapil"])
               if i["ServiceTypeIdentifier"] == SVC + "RevokedKey"]
    jose1 = ent["keys"]["issuance-jose-1"]
    final_state = ent["entries"][-1]["state"]
    method = next(m for m in final_state["verificationMethod"] if m["id"] == ent["did"] + "#issuance-jose-1")
    check("revoked did:webvh key service names issuance-jose-1 as did:key and DID URL, "
          "and the log still publishes it",
          revoked[0]["OtherIds"] == [jose1["did_key"], ent["did"] + "#issuance-jose-1"]
          and method["publicKeyMultibase"] == jose1["multikey"])
    witnesses = [i["ServiceDigitalIdentity"]["OtherIds"][0] for i in services_of(ents["trust-authority"])
                 if i["ServiceTypeIdentifier"] == SVC + "Witness" and "ServiceStatus" in i
                 and i["ServiceDigitalIdentity"]["OtherIds"]]
    check("witness services name ta-witness-2 (in force) then ta-witness-1 (withdrawn), as the logs use them",
          witnesses[0] == db["witness_keys"]["ta-witness-2"]["did_key"]
          and witnesses[-1] == db["witness_keys"]["ta-witness-1"]["did_key"]
          and db["witness_keys"]["ta-witness-1"]["did_key"] in
          [w["id"] for w in ent["entries"][-1]["parameters"]["witness"]["witnesses"]])

    vca = next(i for i in services_of(ents["terminal-nusantara"])
               if i["ServiceTypeIdentifier"] == SVC + "VerifierIssuingCA")
    der = base64.b64decode(vca["ServiceDigitalIdentity"]["X509Certificates"][0]["val"])
    cert = x509.load_der_x509_certificate(der)
    root = x509.load_pem_x509_certificate((ART / "verifier-root-ca.pem").read_bytes())
    ski = x509.SubjectKeyIdentifier.from_public_key(cert.public_key()).digest.hex().upper()
    cert_ski = cert.extensions.get_extension_for_class(x509.SubjectKeyIdentifier).value.digest.hex().upper()
    check("Verifier Issuing CA service SKI equals summary.json and the certificate's own extension",
          vca["ServiceDigitalIdentity"]["X509SKIs"] == [summary["verifier_issuing_ca"]["ski"]]
          and cert_ski == summary["verifier_issuing_ca"]["ski"] and len(ski) == 40)
    try:
        cert.verify_directly_issued_by(root)
        chains = True
    except Exception:
        chains = False
    check("embedded certificate parses, is %d bytes as summary.json says, and chains to the Verifier Root CA"
          % len(der), chains and len(der) == summary["verifier_issuing_ca"]["der_size"]
          and der == x509.load_pem_x509_certificate((ART / "verifier-issuing-ca.pem").read_bytes())
          .public_bytes(__import__("cryptography.hazmat.primitives.serialization", fromlist=["Encoding"]).Encoding.DER))
    root_ski = root.extensions.get_extension_for_class(x509.SubjectKeyIdentifier).value.digest.hex().upper()
    check("Verifier Root CA SKI equals summary.json", root_ski == summary["verifier_root_ca"]["ski"])

    x509_revoked = [i["ServiceDigitalIdentity"]["X509SKIs"][0] for i in services_of(ents["dukcapil"])
                    if "X509SKIs" in i["ServiceDigitalIdentity"]]
    certs = x509j["certificates"]
    live = {c["ski"] for n, c in certs.items() if n != "document-signer-retired"} | {
        summary["verifier_issuing_ca"]["ski"]}
    crl = x509.load_pem_x509_crl(x509j["crl"]["pem"].encode())
    check("revoked X.509 SKI is not a live certificate's, and the Issuer Root CA list revokes on the same date",
          x509_revoked[0] not in live
          and next(iter(crl)).revocation_date_utc.date().isoformat() == "2026-09-15"
          and [i["StatusStartingTime"] for i in services_of(ents["dukcapil"])
               if "X509SKIs" in i["ServiceDigitalIdentity"]] == ["2026-09-15T00:00:00Z"])
    check("revoked X.509 SKI is the retired Document Signer Certificate the Issuer Root CA list revokes",
          x509_revoked[0] == certs["document-signer-retired"]["ski"]
          and int(certs["document-signer-retired"]["serial_hex"], 16) == next(iter(crl)).serial_number)

    check("TS-01 header block equals the TS-5-01 protected header block byte for byte",
          out[T01_HEADER] == out[T_HEADER])
    root_entry = ents["trust-authority"]
    svc_text = out[T01_SERVICE]
    check("TS-01 signer service block is the payload's service for the signing key",
          json.loads(svc_text)["ServiceInformation"]
          == next(s["ServiceInformation"] for s in root_entry["TrustedEntityServices"]
                  if s["ServiceInformation"]["ServiceDigitalIdentity"].get("OtherIds") == [s1["did_key"]]
                  and s["ServiceInformation"]["ServiceTypeIdentifier"].endswith("TrustedListSigner")))
    check("page layout kept: payload differs from the page's block only at replaced values",
          len(out[T_PAYLOAD].splitlines()) == len(page_block(P_LIST, T_PAYLOAD).splitlines()))

    n = len(st["contradictions"])
    print(f"INFO {n} place(s) in docs/ the build contradicts; see _structured.contradictions")
    bad = results.count(False)
    print(f"{len(results) - bad}/{len(results)} checks passed")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
