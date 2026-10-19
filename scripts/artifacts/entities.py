"""Build the exchanges TS-4-03 shows at Trust Authority's entity endpoint.

Every request after a registration is a compact JWS signed with the update
key of the registration's latest witnessed log entry, carrying the nonce and
the URL in its protected header, after the pattern of RFC 8555. The first
entry is bound to its registration by an HS256 JWS under the one-time code
Trust Authority delivered. Everything the exchanges carry that another page
also shows is read from the build output, never rebuilt: the log entries and
the rotation's proofs of possession from ``webvh.json``, the certificate
signing request and the certificates from ``x509.json``, the Accreditation
Credential and the Use Statements from ``summary.json``.

What is new here is signed under keys the keystore keeps: the request
signatures and the first entry's binding (EdDSA and HS256, deterministic),
the proofs of possession of the first entry and the status list certificate
request (ES256, randomized), and the key storage evidence, a device
certificate per key issued by an invented HSM. A randomized value is kept
while it still verifies and says the same thing; ``--rebuild`` signs it anew.

Run after ``logs.py``, ``x509ca.py`` and ``build.py``:
``.venv/bin/python scripts/artifacts/entities.py [--rebuild]``
"""

from __future__ import annotations

import base64
import datetime as dt
import hashlib
import hmac
import json
import sys
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID

sys.path.insert(0, str(Path(__file__).resolve().parent))

import keystore  # noqa: E402
import webvh  # noqa: E402

ART = webvh.REPO_ROOT / "build" / "artifacts"
OUT = ART / "entities.json"
HOST = "entities.trust.go.id"
ENDPOINT = f"https://{HOST}"
REGISTRATION = "R2026-000117"


def b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def unb64u(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def seeded(label: str, size: int = 24) -> str:
    """A fixed value standing for one Trust Authority drew at random."""
    return b64u(hashlib.sha256(f"idctf-example-{label}".encode()).digest()[:size])


def utc(y: int, m: int, d: int, hh: int = 0, mm: int = 0) -> dt.datetime:
    return dt.datetime(y, m, d, hh, mm, tzinfo=dt.timezone.utc)


def epoch(text: str) -> int:
    return int(dt.datetime.fromisoformat(text.replace("Z", "+00:00")).timestamp())


def compact(obj) -> bytes:
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode()


def sign_eddsa(private_key, protected: dict, payload: bytes) -> str:
    signing_input = b64u(compact(protected)) + "." + b64u(payload)
    return signing_input + "." + b64u(private_key.sign(signing_input.encode()))


def sign_hs256(secret: bytes, protected: dict, payload: bytes) -> str:
    signing_input = b64u(compact(protected)) + "." + b64u(payload)
    mac = hmac.new(secret, signing_input.encode(), hashlib.sha256).digest()
    return signing_input + "." + b64u(mac)


def request(private_key, kid: str, nonce: str, path: str, payload) -> str:
    """One submission at the entity endpoint."""
    protected = {"alg": "EdDSA", "kid": kid, "nonce": nonce, "url": f"{ENDPOINT}{path}"}
    body = compact(payload)
    return sign_eddsa(private_key, protected, body)


def decoded(token: str) -> str:
    header, payload, _ = token.split(".")
    shown = {"protected": json.loads(unb64u(header))}
    raw = unb64u(payload)
    shown["payload"] = json.loads(raw)
    return json.dumps(shown, indent=2, ensure_ascii=False)


def http_request(path: str, body: str, media: str = "application/jose") -> str:
    return f"POST {path} HTTP/1.1\nHost: {HOST}\nContent-Type: {media}\n\n{body}"


def http_answer(status: str, nonce: str, body=None, media: str = "application/json") -> str:
    lines = [f"HTTP/1.1 {status}", f"Replay-Nonce: {nonce}", "Cache-Control: no-store"]
    if body is None:
        return "\n".join(lines)
    lines.append(f"Content-Type: {media}")
    return "\n".join(lines) + "\n\n" + json.dumps(body, indent=2, ensure_ascii=False)


# --------------------------------------------------------------------------
# Key storage evidence: a certificate over each key, issued by the
# device the key lives in, under its manufacturer's root.
# --------------------------------------------------------------------------

MAKER = "PT Contoh Perangkat Kripto"


def name(common: str) -> x509.Name:
    return x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "ID"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, MAKER),
        x509.NameAttribute(NameOID.COMMON_NAME, common),
    ])


def certificate(subject: x509.Name, public_key, issuer: x509.Name, signer, serial: int,
                start: dt.datetime, end: dt.datetime, ca: bool) -> x509.Certificate:
    builder = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(public_key)
        .serial_number(serial)
        .not_valid_before(start)
        .not_valid_after(end)
        .add_extension(x509.BasicConstraints(ca=ca, path_length=0 if ca else None), critical=True)
        .add_extension(x509.KeyUsage(
            digital_signature=not ca, content_commitment=False, key_encipherment=False,
            data_encipherment=False, key_agreement=False, key_cert_sign=ca, crl_sign=False,
            encipher_only=False, decipher_only=False), critical=True)
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(public_key), critical=False)
    )
    if issuer != subject:
        builder = builder.add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(signer.public_key()), critical=False)
    return builder.sign(signer, hashes.SHA256())


def same_certificate(stored: str | None, wanted: dict) -> x509.Certificate | None:
    """The stored certificate, if it still says what ``wanted`` says and verifies."""
    if not stored:
        return None
    cert = x509.load_der_x509_certificate(unb64u(stored))
    issuer_key = wanted["issuer_key"]
    try:
        issuer_key.verify(cert.signature, cert.tbs_certificate_bytes, ec.ECDSA(hashes.SHA256()))
    except Exception:  # noqa: BLE001
        return None
    same = (
        cert.subject == wanted["subject"]
        and cert.issuer == wanted["issuer"]
        and cert.serial_number == wanted["serial"]
        and cert.not_valid_before_utc == wanted["start"]
        and cert.not_valid_after_utc == wanted["end"]
        and cert.public_key().public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
        == wanted["public_key"].public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
    )
    return cert if same else None


def make_certificate(stored: dict, label: str, rebuild: bool, **wanted) -> x509.Certificate:
    kept = None if rebuild else same_certificate(stored.get(label), wanted)
    cert = kept or certificate(
        wanted["subject"], wanted["public_key"], wanted["issuer"], wanted["signer"],
        wanted["serial"], wanted["start"], wanted["end"], wanted["ca"])
    stored[label] = b64u(cert.public_bytes(serialization.Encoding.DER))
    return cert


def der(cert: x509.Certificate) -> bytes:
    return cert.public_bytes(serialization.Encoding.DER)


# --------------------------------------------------------------------------
# The exchanges
# --------------------------------------------------------------------------


def keep_pop(stored: list, index: int, fresh: str, public_key) -> str:
    """A stored ES256 proof, when it carries the same claims and still verifies."""
    if index < len(stored):
        old = stored[index]
        if old.split(".")[:2] == fresh.split(".")[:2] and webvh.verify_pop(old, public_key):
            return old
    return fresh


def build(rebuild: bool) -> dict:
    webvh_db = json.loads((ART / "webvh.json").read_text())
    x509_db = json.loads((ART / "x509.json").read_text())
    summary = json.loads((ART / "summary.json").read_text())
    previous = {} if rebuild or not OUT.exists() else json.loads(OUT.read_text()).get("_stored", {})
    stored: dict = {"certificates": dict(previous.get("certificates", {})),
                    "genesis_pops": list(previous.get("genesis_pops", [])),
                    "status_list_csr": previous.get("status_list_csr"),
                    "issuing_ca_csr": previous.get("issuing_ca_csr"),
                    "first_csr": previous.get("first_csr"),
                    "countersignatures": dict(previous.get("countersignatures", {}))}

    ta_did = webvh_db["trust_authority_did"]
    duk = webvh_db["entities"]["dukcapil"]
    term = webvh_db["entities"]["terminal-nusantara"]
    duk_keys = duk["keys"]

    def ed(name: str):
        return keystore.load_or_create_ed25519(name)

    blocks: dict[str, str] = {}

    # The device and its manufacturer, which only the Governance Profile names.
    root_key = keystore.load_or_create("hsm-maker-root")
    device_key = keystore.load_or_create("hsm-device-dukcapil")
    root = make_certificate(
        stored["certificates"], "maker-root", rebuild,
        subject=name("Contoh HSM Root CA"), issuer=name("Contoh HSM Root CA"),
        public_key=root_key.public_key(), signer=root_key, issuer_key=root_key.public_key(),
        serial=0x4B1D0001, start=utc(2024, 1, 1), end=utc(2044, 1, 1), ca=True)
    device = make_certificate(
        stored["certificates"], "device", rebuild,
        subject=name("Contoh HSM 7Q4K-0219"), issuer=root.subject,
        public_key=device_key.public_key(), signer=root_key, issuer_key=root_key.public_key(),
        serial=0x4B1D70219, start=utc(2025, 6, 1), end=utc(2045, 6, 1), ca=True)

    def evidence(label: str, key_name: str, serial: int, start: dt.datetime) -> list[str]:
        public = keystore.load_or_create(key_name).public_key()
        leaf = make_certificate(
            stored["certificates"], label, rebuild,
            subject=name(f"Key {serial:04X}"), issuer=device.subject,
            public_key=public, signer=device_key, issuer_key=device_key.public_key(),
            serial=serial, start=start, end=utc(2045, 6, 1), ca=False)
        return {"format": "x509-chain", "certs": [b64u(der(leaf)), b64u(der(device))]}

    def multikey_of(key_name: str) -> str:
        return webvh.multikey(keystore.load_or_create(key_name).public_key())

    # 1. A nonce.
    nonces = {label: seeded(f"entity-nonce-{label}") for label in
              ("first", "after-first", "certificates", "after-certificates",
               "issuing-ca", "after-issuing-ca", "after-rotation", "after-used")}
    blocks["GET /nonce, Trust Authority entity endpoint"] = f"GET /nonce HTTP/1.1\nHost: {HOST}"
    blocks["204, a fresh nonce"] = (
        f"HTTP/1.1 204 No Content\nReplay-Nonce: {nonces['first']}\nCache-Control: no-store")

    # 2. The first entry, bound to the registration by the one-time code.
    code = seeded("registration-code-dukcapil", 32)
    first = duk["entries"][0]
    update1 = duk_keys["update-1"]
    update1_kid = f"{update1['did_key']}#{update1['multikey']}"
    first_time = first["versionTime"]
    pop_iat = epoch(first_time) + 60
    nonce = nonces["first"]
    pops = [webvh.pop_jws(ed(update1["keystore"]), update1_kid, ta_did, nonce, pop_iat)]
    for i, purpose in enumerate(("issuance-jose-1", "status-list-1")):
        k = duk_keys[purpose]
        fresh = webvh.pop_jws(keystore.load_or_create(k["keystore"]), k["kid"], ta_did, nonce, pop_iat)
        pops.append(keep_pop(stored["genesis_pops"], i, fresh,
                             webvh.public_key_from_multikey(k["multikey"])))
    stored["genesis_pops"] = pops[1:]
    keys_url = "/entities/me/keys"
    binding = sign_hs256(unb64u(code), {"alg": "HS256", "kid": REGISTRATION, "url": f"{ENDPOINT}{keys_url}"},
                         update1_kid.encode())
    first_dsc = x509.load_der_x509_certificate(
        base64.b64decode(x509_db["certificates"]["document-signer-retired"]["der_b64"]))
    first_cose_key = keystore.load_or_create("issuer-document-signer-retired")
    kept = None
    if stored.get("first_csr"):
        old = x509.load_der_x509_csr(unb64u(stored["first_csr"]))
        if old.is_signature_valid and old.subject == first_dsc.subject and old.public_key() == first_cose_key.public_key():
            kept = old
    first_csr = kept or (
        x509.CertificateSigningRequestBuilder().subject_name(first_dsc.subject).sign(first_cose_key, hashes.SHA256()))
    stored["first_csr"] = b64u(first_csr.public_bytes(serialization.Encoding.DER))
    genesis_payload = {
        "logEntry": first,
        "proofOfPossession": pops,
        "keyStorage": [
            {"key": duk_keys["issuance-jose-1"]["multikey"], "storage": "hsm",
             "evidence": evidence("attested-issuance-jose-1", "dukcapil-issuance-jose-1", 0x0041, utc(2026, 1, 30))},
            {"key": duk_keys["status-list-1"]["multikey"], "storage": "hsm",
             "evidence": evidence("attested-status-list-1", "dukcapil-status-list-1", 0x0042, utc(2026, 1, 30))},
            {"key": multikey_of("issuer-document-signer-retired"), "storage": "hsm",
             "evidence": evidence("attested-issuance-cose-first", "issuer-document-signer-retired", 0x0043,
                                  utc(2026, 1, 30))},
        ],
        "certificationRequests": [{"purpose": "issuance-cose", "csr": stored["first_csr"]}],
        "registrationBinding": binding,
    }
    genesis = request(ed(update1["keystore"]), update1_kid, nonce, keys_url, genesis_payload)
    blocks["POST /entities/me/keys, the first entry"] = http_request(keys_url, genesis)
    blocks["The first entry request, decoded"] = decoded(genesis)
    accreditation = next(t for t, p in zip(summary["accreditations"], summary["accreditation_payloads"])
                         if p["sub"] == duk["did"])
    witness1 = ed("ta-witness-1")
    genesis_answer = {
        "witness": {"versionId": first["versionId"],
                    "proof": [webvh.witness_proof(first["versionId"], witness1)]},
        "certificates": [{"purpose": "issuance-cose", "certificate": b64u(der(first_dsc))}],
        "accreditationCredential": accreditation,
    }
    blocks["200, the answer to the first entry"] = http_answer("200 OK", nonces["after-first"], genesis_answer)

    # 3. Two certificates on keys the log does not change.
    csr_der = x509.load_pem_x509_csr(x509_db["csr"]["pem"].encode()).public_bytes(serialization.Encoding.DER)
    status_list_cert = x509_db["certificates"]["status-list-signer-dukcapil"]
    status_key = keystore.load_or_create("dukcapil-status-list-1")
    status_subject = x509.load_pem_x509_certificate(status_list_cert["pem"].encode()).subject
    kept_csr = None
    if stored.get("status_list_csr"):
        old = x509.load_der_x509_csr(unb64u(stored["status_list_csr"]))
        if old.is_signature_valid and old.subject == status_subject and old.public_key() == status_key.public_key():
            kept_csr = old
    status_csr = kept_csr or (
        x509.CertificateSigningRequestBuilder().subject_name(status_subject).sign(status_key, hashes.SHA256()))
    stored["status_list_csr"] = b64u(status_csr.public_bytes(serialization.Encoding.DER))
    def countersign(label: str, key_name: str, kid: str, nonce: str, iat: int) -> str:
        """A proof of possession by a transaction key the registration already holds."""
        private_key = keystore.load_or_create(key_name)
        fresh = webvh.pop_jws(private_key, kid, ta_did, nonce, iat)
        old = stored["countersignatures"].get(label)
        kept = keep_pop([old] if old else [], 0, fresh, private_key.public_key())
        stored["countersignatures"][label] = kept
        return kept

    cert_payload = {
        "countersignature": countersign(
            "certificates", duk_keys["issuance-jose-1"]["keystore"], duk_keys["issuance-jose-1"]["kid"],
            nonces["certificates"], epoch("2026-09-01T00:00:00Z") - 300),
        "keyStorage": [
            {"key": multikey_of("issuer-document-signer-1"), "storage": "hsm",
             "evidence": evidence("attested-issuance-cose-2026", "issuer-document-signer-1", 0x0057, utc(2026, 8, 28))},
        ],
        "certificationRequests": [
            {"purpose": "issuance-cose", "csr": b64u(csr_der)},
            {"purpose": "status-list", "csr": stored["status_list_csr"]},
        ],
    }
    cert_request = request(ed(update1["keystore"]), update1_kid, nonces["certificates"], keys_url, cert_payload)
    blocks["POST /entities/me/keys, a certificate request"] = http_request(keys_url, cert_request)
    blocks["The certificate request, decoded"] = decoded(cert_request)
    dsc_der = base64.b64decode(x509_db["certificates"]["document-signer"]["der_b64"])
    slsc_der = base64.b64decode(status_list_cert["der_b64"])
    issued = [{"purpose": "issuance-cose", "certificate": b64u(dsc_der)},
              {"purpose": "status-list", "certificate": b64u(slsc_der)}]
    blocks["200, the answer to a certificate request"] = http_answer(
        "200 OK", nonces["after-certificates"], {"certificates": issued})

    # 4. A Verifier Issuing CA, for the Relying Party that registers merchants.
    t_update = term["keys"]["update-1"]
    t_kid = f"{t_update['did_key']}#{t_update['multikey']}"
    t_ed = ed(t_update["keystore"])
    issuing_cert = x509.load_pem_x509_certificate((ART / "verifier-issuing-ca.pem").read_bytes())
    issuing_key = keystore.load_or_create("verifier-issuing-ca")
    kept_csr = None
    if stored.get("issuing_ca_csr"):
        old = x509.load_der_x509_csr(unb64u(stored["issuing_ca_csr"]))
        if old.is_signature_valid and old.subject == issuing_cert.subject and old.public_key() == issuing_key.public_key():
            kept_csr = old
    issuing_csr = kept_csr or (
        x509.CertificateSigningRequestBuilder().subject_name(issuing_cert.subject).sign(issuing_key, hashes.SHA256()))
    stored["issuing_ca_csr"] = b64u(issuing_csr.public_bytes(serialization.Encoding.DER))
    request_object = term["keys"]["request-object-1"]
    issuing_payload = {
        "countersignature": countersign(
            "issuing-ca", request_object["keystore"], request_object["kid"],
            nonces["issuing-ca"], epoch("2026-06-01T00:00:00Z") - 300),
        "keyStorage": [{"key": webvh.multikey(issuing_key.public_key()), "storage": "cloudkms",
                        "evidence": {"format": "assessment-report", "report": "AB-2026-0412"}}],
        "certificationRequests": [{"purpose": "verifier-issuing-ca", "csr": stored["issuing_ca_csr"]}],
    }
    issuing_request = request(t_ed, t_kid, nonces["issuing-ca"], keys_url, issuing_payload)
    blocks["POST /entities/me/keys, a Verifier Issuing CA request"] = http_request(keys_url, issuing_request)
    blocks["The Verifier Issuing CA request, decoded"] = decoded(issuing_request)
    blocks["200, the answer to a Verifier Issuing CA request"] = http_answer(
        "200 OK", nonces["after-issuing-ca"],
        {"certificates": [{"purpose": "verifier-issuing-ca", "certificate": b64u(der(issuing_cert))}]})

    # 4c. A storage item for a key held in the software keystore: no evidence.
    blocks["A storage item for a key in the software keystore"] = json.dumps(
        {"key": term["keys"]["request-object-1"]["multikey"], "storage": "software"}, indent=2)

    # 5. The rotation TS-4-01 hands on, as the entity sent it.
    publisher = webvh_db["publisher_request"]
    rotation_payload = {
        "logEntry": publisher["logEntry"],
        "proofOfPossession": publisher["proofOfPossession"],
        "keyStorage": [
            {"key": duk_keys["issuance-jose-2"]["multikey"], "storage": "hsm",
             "evidence": evidence("attested-issuance-jose-2", "dukcapil-issuance-jose-2", 0x0063, utc(2026, 9, 14))},
        ],
    }
    rotation = request(ed(update1["keystore"]), update1_kid, publisher["nonce"], keys_url, rotation_payload)
    blocks["POST /entities/me/keys, a rotation"] = http_request(keys_url, rotation)
    blocks["The rotation request, decoded"] = decoded(rotation)
    blocks["200, the answer to a rotation"] = http_answer(
        "200 OK", nonces["after-rotation"], {"witness": duk["witness_file"][0]})

    # 6. A request that reuses a nonce.
    blocks["400, the answer to a request whose nonce was used"] = http_answer(
        "400 Bad Request", nonces["after-used"],
        {"type": "https://idctf.id/ns/problems/bad-nonce", "title": "Bad nonce", "status": 400},
        media="application/problem+json")

    return {
        "endpoint": ENDPOINT,
        "registration": REGISTRATION,
        "registration_code": code,
        "maker_root": b64u(der(root)),
        "blocks": blocks,
        "_stored": stored,
    }


def verify(out: dict) -> bool:
    ok_all = True

    def check(label: str, ok: bool) -> None:
        nonlocal ok_all
        ok_all &= ok
        print(f"{'OK' if ok else 'FAIL'}  {label}")

    root = x509.load_der_x509_certificate(unb64u(out["maker_root"]))
    blocks = out["blocks"]
    for title, body in blocks.items():
        if not title.startswith("POST /entities/me"):
            continue
        token = body.split("\n\n", 1)[1]
        head, payload, sig = token.split(".")
        protected = json.loads(unb64u(head))
        key = webvh.public_key_from_multikey(protected["kid"].removeprefix("did:key:").split("#")[0])
        try:
            key.verify(unb64u(sig), f"{head}.{payload}".encode())
            good = True
        except Exception:  # noqa: BLE001
            good = False
        path = title.split(",")[0].removeprefix("POST ")
        check(f"{title}: signature, url", good and protected["url"] == f"{out['endpoint']}{path}")
        raw = unb64u(payload)
        body_json = json.loads(raw)
        if body_json and "countersignature" in body_json:
            claims = json.loads(unb64u(body_json["countersignature"].split(".")[1]))
            check(f"{title}: countersignature over the request nonce", claims["nonce"] == protected["nonce"])
        for item in (body_json or {}).get("keyStorage", []):
            if item.get("evidence", {}).get("format") != "x509-chain":
                continue
            leaf, device = (x509.load_der_x509_certificate(unb64u(c)) for c in item["evidence"]["certs"])
            chain = True
            for child, parent in ((leaf, device), (device, root)):
                try:
                    parent.public_key().verify(child.signature, child.tbs_certificate_bytes, ec.ECDSA(hashes.SHA256()))
                except Exception:  # noqa: BLE001
                    chain = False
            check(f"{title}: evidence for {item['key'][:16]} chains and names the key",
                  chain and webvh.multikey(leaf.public_key()) == item["key"])
        if body_json and "registrationBinding" in body_json:
            b_head, b_payload, b_sig = body_json["registrationBinding"].split(".")
            mac = hmac.new(unb64u(out["registration_code"]), f"{b_head}.{b_payload}".encode(), hashlib.sha256).digest()
            b_protected = json.loads(unb64u(b_head))
            check("registration binding: MAC, kid, url, payload",
                  hmac.compare_digest(mac, unb64u(b_sig)) and b_protected["kid"] == out["registration"]
                  and b_protected["url"] == protected["url"] and unb64u(b_payload).decode() == protected["kid"])
        for pop in (body_json or {}).get("proofOfPossession", []):
            check(f"{title}: proof of possession nonce is the request nonce",
                  json.loads(unb64u(pop.split(".")[1]))["nonce"] == protected["nonce"])
        for item in (body_json or {}).get("certificationRequests", []):
            csr = x509.load_der_x509_csr(unb64u(item["csr"]))
            check(f"{title}: {item['purpose']} request is self-signed", csr.is_signature_valid)
    return ok_all


def main() -> int:
    out = build("--rebuild" in sys.argv)
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {OUT.relative_to(webvh.REPO_ROOT)}")
    return 0 if verify(json.loads(OUT.read_text())) else 1


if __name__ == "__main__":
    sys.exit(main())
