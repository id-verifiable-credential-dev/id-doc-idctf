"""Status lists and the Key Attestation family, signed under kept keys.

Builds the artifacts of TS-5-09 (the four Status List Tokens, the two CWT
forms), TS-01 (the same Dukcapil list, decomposed) and TS-5-08 (the Key
Attestation, the key proof that carries it, and the attestation proof type),
and writes them to ``build/artifacts/statuslists.json`` keyed by block title.

Every identifier and every ``kid`` comes from ``build/artifacts/webvh.json``,
every key from the keystore. Signing is randomized for ES256: a re-run
rewrites every signature, so run it when an artifact has to change.

Run as a script it builds, then verifies its own output and prints one line
per check; the exit status is 0 only when every check passes.
"""

from __future__ import annotations

import base64
import json
import re
import sys
import zlib
from pathlib import Path

import cbor2
from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.x509.oid import NameOID
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
WEBVH_JSON = REPO_ROOT / "build" / "artifacts" / "webvh.json"
X509_JSON = REPO_ROOT / "build" / "artifacts" / "x509.json"
OUT_JSON = REPO_ROOT / "build" / "artifacts" / "statuslists.json"

P_STATUS = TS_DIR / "publishing-and-reading-a-status-list.md"
P_TS01 = TS_DIR / "finding-a-signers-key-from-its-did.md"
P_ATTEST = TS_DIR / "issuing-and-reading-a-key-attestation.md"

# --- values the pages fix, kept by hand ------------------------------------
IAT = 1792216800  # 17 October 2026 06:00 UTC
EXP = 1794808800
TTL = 43200
# (entity, key id in webvh.json, sub, bits, entries, {index: value}, title prefix)
LISTS = {
    "Credential status list": dict(
        entity="dukcapil", key="status-list-1", sub="https://dukcapil.go.id/status/ktp-7",
        bits=2, entries=524288, set={481920: 0, 481921: 1, 481922: 2}),
    "Kartu ASN status list": dict(
        entity="bkn", key="status-list-1", sub="https://bkn.go.id/status/kartu-asn-1",
        bits=2, entries=524288, set={}),
    "Use Statement status list": dict(
        entity="trust-authority", key="use-statement-status-list-1",
        sub="https://registry.trust.go.id/status/use-statements-1",
        bits=1, entries=131072, set={2077: 1}),
    "Accreditation status list": dict(
        entity="trust-authority", key="accreditation-status-list-1",
        sub="https://registry.trust.go.id/status/accreditations-1",
        bits=2, entries=131072, set={23: 1, 31: 2}),
}
# Indices the pages name as valid, which must decode to 0.
VALID_INDICES = {"Credential status list": [481920], "Kartu ASN status list": [481920]}
CWT_FORMS = ["Credential status list", "Kartu ASN status list"]
# The status list signer certificate of TS-5-04 each CWT form carries in x5chain.
CWT_SIGNER_CERT = {
    "Credential status list": "status-list-signer-dukcapil",
    "Kartu ASN status list": "status-list-signer-bkn",
}

ATTEST_ENTITY = "dompet-digital-nusantara"
ATTEST_KEY = "key-attestation-1"
ATTEST_NONCE = "kQ8vZ2mH7rT1"
ATTEST_IAT = 1792216800
ATTEST_EXP = 1792303200
ATTEST_CERT = "https://dompet.co.id/certification/se-2026-a"
ATTEST_KEY_STORAGE = ["iso_18045_high"]
ATTEST_USER_AUTH = ["iso_18045_moderate"]
PROOF_AUD = "https://issuer.bkn.go.id"
PROOF_IAT = 1792216805
ABBREV_HEADER_CHARS = 40  # "key_attestation" in the abbreviated key proof header
ABBREV_PROOF_CHARS = 60   # the attestation proof type, abbreviated
HOLDER_KEY = "holder-credential-1"  # the wallet installation's credential key


# --- helpers ----------------------------------------------------------------
def load_webvh() -> dict:
    return json.loads(WEBVH_JSON.read_text())


def signer_cert_der(title: str) -> bytes:
    """DER of the status list signer certificate x509ca.py issued for a CWT form."""
    pem = json.loads(X509_JSON.read_text())["certificates"][CWT_SIGNER_CERT[title]]["pem"]
    body = "".join(l for l in pem.splitlines() if not l.startswith("-----"))
    return base64.b64decode(body)


def kept_key(name: str, expected_multikey: str):
    """Load a keystore key that must already exist and must match webvh.json."""
    path = keystore.keystore_dir() / f"{name}.pem"
    if not path.exists():
        raise SystemExit(f"keystore has no key {name!r}")
    key = keystore.load_or_create(name)
    if webvh.multikey(key.public_key()) != expected_multikey:
        raise SystemExit(f"keystore key {name!r} does not match webvh.json")
    return key


def entity_key(db: dict, entity: str, key_id: str):
    info = db["entities"][entity]["keys"][key_id]
    return kept_key(info["keystore"], info["multikey"]), info


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


def compact(obj) -> bytes:
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode()


def jws(key, header: dict, payload: dict) -> str:
    signing_input = webvh._b64u(compact(header)) + "." + webvh._b64u(compact(payload))
    for token in STORED["tokens"]:
        if token.startswith(signing_input + "."):
            return token
    return signing_input + "." + webvh._b64u(es256_sign(key, signing_input.encode()))


def cose_sign1(key, protected: bytes, kid: str, payload: bytes) -> bytes:
    """A COSE_Sign1 signature, the stored one while protected, kid and payload stay."""
    for cwt in STORED["cwt"]:
        if (cwt["protected"] == protected.hex() and cwt["unprotected_kid"] == kid
                and cwt["payload"] == payload.hex()):
            return bytes.fromhex(cwt["signature"])
    return es256_sign(key, cbor2.dumps(["Signature1", protected, b"", payload]))


def load_stored() -> dict:
    """Tokens and COSE signatures of the previous run.

    Signing is randomized, so re-signing an unchanged payload would rewrite a
    page for nothing. A token is signed again only when what it says changes.
    """
    if not OUT_JSON.exists():
        return {"tokens": [], "cwt": []}
    prev = json.loads(OUT_JSON.read_text())
    tokens = [v for v in prev.values() if isinstance(v, str) and v.count(".") == 2]
    st = prev.get("_structured", {})
    tokens += [st.get("attestation", {}).get("proof", "")]
    cwt = [item["cwt"] for item in st.get("lists", {}).values() if "cwt" in item]
    return {"tokens": [t for t in tokens if t], "cwt": cwt}


STORED: dict = {"tokens": [], "cwt": []}


def pretty(obj) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False)


def pack(bits: int, entries: int, values: dict[int, int]) -> bytes:
    """Status List byte array: ``bits`` per entry, least significant bit first."""
    raw = bytearray(entries * bits // 8)
    for index, value in values.items():
        if not 0 <= index < entries or not 0 <= value < (1 << bits):
            raise ValueError(f"entry {index}={value} does not fit")
        raw[index * bits // 8] |= value << (index * bits % 8)
    return bytes(raw)


def unpack(raw: bytes, bits: int, index: int) -> int:
    return (raw[index * bits // 8] >> (index * bits % 8)) & ((1 << bits) - 1)


def deflate(raw: bytes) -> bytes:
    return zlib.compress(raw, 9)


def jwk_of(public_key) -> dict:
    n = public_key.public_numbers()
    return {
        "kty": "EC",
        "crv": "P-256",
        "x": webvh._b64u(n.x.to_bytes(32, "big")),
        "y": webvh._b64u(n.y.to_bytes(32, "big")),
    }


def hex_lines(data: bytes) -> str:
    h = data.hex()
    return "\n".join(h[i : i + 64] for i in range(0, len(h), 64))


# --- build ------------------------------------------------------------------
def build() -> dict:
    STORED.update(load_stored())
    db = load_webvh()
    out: dict = {}
    st: dict = {"lists": {}, "attestation": {}}
    compressed: dict[str, bytes] = {}

    for title, spec in LISTS.items():
        key, info = entity_key(db, spec["entity"], spec["key"])
        did = db["entities"][spec["entity"]]["did"]
        raw = pack(spec["bits"], spec["entries"], spec["set"])
        comp = deflate(raw)
        compressed[title] = comp
        lst = webvh._b64u(comp)
        header = {"typ": "statuslist+jwt", "alg": "ES256", "kid": info["kid"]}
        payload = {
            "iss": did, "sub": spec["sub"], "iat": IAT, "exp": EXP, "ttl": TTL,
            "status_list": {"bits": spec["bits"], "lst": lst},
        }
        token = jws(key, header, payload)
        out[f"{title}, as served"] = token
        out[f"{title} claims"] = pretty(payload)
        st["lists"][title] = {
            "entity": spec["entity"], "kid": info["kid"], "multikey": info["multikey"],
            "header": header, "payload": payload, "token": token,
            "bits": spec["bits"], "entries": spec["entries"], "set": spec["set"],
        }

    for title in CWT_FORMS:
        spec = LISTS[title]
        key, info = entity_key(db, spec["entity"], spec["key"])
        protected = cbor2.dumps(
            {1: -7, 16: "application/statuslist+cwt", 33: signer_cert_der(title)})
        unprotected = {4: info["kid"].encode()}
        payload = cbor2.dumps({
            1: db["entities"][spec["entity"]]["did"],
            2: spec["sub"], 6: IAT, 4: EXP, 65534: TTL,
            65533: {"bits": spec["bits"], "lst": compressed[title]},
        })
        signature = cose_sign1(key, protected, info["kid"], payload)
        message = cbor2.dumps(cbor2.CBORTag(18, [protected, unprotected, payload, signature]))
        out[f"{title}, CWT form, in hex"] = hex_lines(message)
        st["lists"][title]["cwt"] = {
            "hex": message.hex(), "protected": protected.hex(), "unprotected_kid": info["kid"],
            "payload": payload.hex(), "signature": signature.hex(),
        }

    # TS-01: the Dukcapil credential status list, decomposed.
    duk = st["lists"]["Credential status list"]
    out["Protected header of the credential status list"] = pretty(duk["header"])
    out["Signer named in the claims"] = pretty(
        {"iss": duk["payload"]["iss"], "iat": duk["payload"]["iat"]}
    )
    entity = db["entities"]["dukcapil"]
    state = None
    for entry in entity["entries"]:
        if entry["versionTime"] <= "2026-10-17T06:00:00Z":
            state = entry["state"]
    method = next(m for m in state["verificationMethod"] if m["id"] == duk["kid"])
    out["Verification method the kid names"] = pretty(method)
    st["verification_method"] = method

    # TS-5-08: Key Attestation, key proof, attestation proof type.
    akey, ainfo = entity_key(db, ATTEST_ENTITY, ATTEST_KEY)
    adid = db["entities"][ATTEST_ENTITY]["did"]
    holder = keystore.load_or_create(HOLDER_KEY)
    holder_jwk = jwk_of(holder.public_key())
    a_header = {"typ": "key-attestation+jwt", "alg": "ES256", "kid": ainfo["kid"]}
    a_claims = {
        "iss": adid, "attested_keys": [holder_jwk],
        "key_storage": ATTEST_KEY_STORAGE, "user_authentication": ATTEST_USER_AUTH,
        "certification": ATTEST_CERT, "nonce": ATTEST_NONCE,
        "iat": ATTEST_IAT, "exp": ATTEST_EXP,
    }
    attestation = jws(akey, a_header, a_claims)
    out["A Key Attestation, in compact serialization"] = attestation
    out["Key Attestation header"] = pretty(a_header)
    out["Key Attestation claims"] = pretty(a_claims)

    p_header = {"typ": "openid4vci-proof+jwt", "alg": "ES256", "jwk": holder_jwk,
                "key_attestation": attestation}
    p_claims = {"aud": PROOF_AUD, "iat": PROOF_IAT, "nonce": ATTEST_NONCE}
    proof = jws(holder, p_header, p_claims)
    out["A key proof carrying the attestation in its header"] = proof
    out["Key proof header, with the attestation abbreviated"] = pretty(
        {**p_header, "key_attestation": attestation[:ABBREV_HEADER_CHARS] + "..."}
    )
    out["Key proof claims"] = pretty(p_claims)
    out["The attestation as the proof itself, abbreviated"] = pretty(
        {"proofs": {"attestation": [attestation[:ABBREV_PROOF_CHARS] + "..."]}}
    )
    st["attestation"] = {
        "entity": ATTEST_ENTITY, "kid": ainfo["kid"], "multikey": ainfo["multikey"],
        "header": a_header, "claims": a_claims, "token": attestation,
        "holder_keystore": HOLDER_KEY, "holder_jwk": holder_jwk,
        "holder_multikey": webvh.multikey(holder.public_key()),
        "holder_did_key": webvh.did_key(webvh.multikey(holder.public_key())),
        "proof_header": p_header, "proof_claims": p_claims, "proof": proof,
    }
    n = holder.public_key().public_numbers()
    out["holder"] = {
        "keystore": HOLDER_KEY,
        "did_key": st["attestation"]["holder_did_key"],
        "multikey": st["attestation"]["holder_multikey"],
        "jwk": holder_jwk,
        "cose_key": {"1": 2, "-1": 1, "-2": n.x.to_bytes(32, "big").hex(),
                     "-3": n.y.to_bytes(32, "big").hex()},
    }
    out["_structured"] = st
    return out


# --- verify -----------------------------------------------------------------
def read_jws(token: str):
    head, body, sig = token.split(".")
    return (json.loads(webvh._unb64u(head)), json.loads(webvh._unb64u(body)),
            webvh._unb64u(sig), f"{head}.{body}".encode())


def did_document_key(db: dict, entity: str, kid: str, at: str = "2999-01-01T00:00:00Z"):
    """Resolve ``kid`` in the DID Document version in force at ``at``."""
    state = None
    for entry in db["entities"][entity]["entries"]:
        if entry["versionTime"] <= at:
            state = entry["state"]
    method = next(m for m in state["verificationMethod"] if m["id"] == kid)
    return webvh.public_key_from_multikey(method["publicKeyMultibase"])


def page_block(page: Path, title: str) -> str:
    text = page.read_text()
    m = re.search(r'title="' + re.escape(title) + r'"[^\n]*\n(.*?)\n```', text, re.S)
    if not m:
        raise ValueError(f"no block {title!r} in {page.name}")
    return m.group(1)


def main() -> int:
    out = build()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    st = out["_structured"]
    db = load_webvh()
    results: list[bool] = []

    def check(label: str, ok: bool) -> None:
        results.append(bool(ok))
        print(f"{'OK  ' if ok else 'FAIL'} {label}")

    iat_time = "2026-10-17T06:00:00Z"
    for title, spec in LISTS.items():
        item = st["lists"][title]
        header, payload, sig, signing_input = read_jws(item["token"])
        pub = did_document_key(db, spec["entity"], header["kid"], iat_time)
        check(f"{title}: JWS verifies under the key its kid names in the DID Document",
              es256_verify(pub, sig, signing_input))
        check(f"{title}: kid and iss come from webvh.json",
              header["kid"] == db["entities"][spec["entity"]]["keys"][spec["key"]]["kid"]
              and payload["iss"] == db["entities"][spec["entity"]]["did"]
              and header["kid"].startswith(payload["iss"] + "#"))
        check(f"{title}: typ statuslist+jwt, alg ES256, claims iss sub iat exp ttl status_list",
              header["typ"] == "statuslist+jwt" and header["alg"] == "ES256"
              and list(payload) == ["iss", "sub", "iat", "exp", "ttl", "status_list"]
              and payload["iat"] == IAT and payload["exp"] == EXP and payload["ttl"] == TTL
              and payload["exp"] >= payload["iat"] + payload["ttl"])
        sl = payload["status_list"]
        check(f"{title}: status_list is bits and lst, bits={spec['bits']}",
              list(sl) == ["bits", "lst"] and sl["bits"] == spec["bits"] and "=" not in sl["lst"])
        raw = zlib.decompress(webvh._unb64u(sl["lst"]))
        check(f"{title}: lst decodes to {spec['entries']} entries",
              len(raw) * 8 // spec["bits"] == spec["entries"])
        nonzero = {i: unpack(raw, spec["bits"], i)
                   for i in range(spec["entries"]) if unpack(raw, spec["bits"], i)}
        check(f"{title}: nonzero entries are exactly {spec['set'] or 'none'}",
              nonzero == {i: v for i, v in spec["set"].items() if v})
        check(f"{title}: named valid indices decode to 0",
              all(unpack(raw, spec["bits"], i) == 0 for i in VALID_INDICES.get(title, [])))
        check(f"{title}: block text is the claims object",
              json.loads(out[f"{title} claims"]) == payload)
        page_text = P_STATUS.read_text()
        check(f"{title}: sub is the address the page names", f'"sub": "{spec["sub"]}"' in page_text)

    for title in CWT_FORMS:
        spec = LISTS[title]
        item = st["lists"][title]
        data = bytes.fromhex(out[f"{title}, CWT form, in hex"].replace("\n", ""))
        tag = cbor2.loads(data)
        protected_raw, unprotected, payload_raw, signature = tag.value
        protected = cbor2.loads(protected_raw)
        kid = unprotected[4].decode()
        pub = did_document_key(db, spec["entity"], kid, iat_time)
        sig_structure = cbor2.dumps(["Signature1", protected_raw, b"", payload_raw])
        check(f"{title} CWT: COSE_Sign1 tag 18 signature verifies under the key its kid names",
              tag.tag == 18 and es256_verify(pub, signature, sig_structure))
        check(f"{title} CWT: protected header is {{1: -7, 16: application/statuslist+cwt, 33: x5chain}}",
              protected == {1: -7, 16: "application/statuslist+cwt", 33: signer_cert_der(title)})
        cert = x509.load_der_x509_certificate(protected[33])
        root = x509.load_pem_x509_certificate(
            json.loads(X509_JSON.read_text())["certificates"]["issuer-root-ca"]["pem"].encode())
        cert.verify_directly_issued_by(root)
        check(f"{title} CWT: x5chain certificate chains to the Issuer Root CA and certifies the key kid names",
              cert.public_key().public_numbers() == pub.public_numbers()
              and es256_verify(cert.public_key(), signature, sig_structure))
        if title == "Credential status list":
            dsc = x509.load_pem_x509_certificate(
                json.loads(X509_JSON.read_text())["certificates"]["document-signer"]["pem"].encode())
            org = lambda c: c.subject.get_attributes_for_oid(NameOID.ORGANIZATION_NAME)[0].value  # noqa: E731
            check(f"{title} CWT: x5chain names the organization of the Document Signer Certificate",
                  org(cert) == org(dsc))
        claims = cbor2.loads(payload_raw)
        jwt_payload = item["payload"]
        jl = jwt_payload["status_list"]
        check(f"{title} CWT: same sub, iat, exp, ttl, bits and array as the JWT form",
              claims[2] == jwt_payload["sub"] and claims[6] == jwt_payload["iat"]
              and claims[4] == jwt_payload["exp"] and claims[65534] == jwt_payload["ttl"]
              and claims[65533]["bits"] == jl["bits"]
              and isinstance(claims[65533]["lst"], bytes)
              and claims[65533]["lst"] == webvh._unb64u(jl["lst"]))
        check(f"{title} CWT: same kid as the JWT form, signed by the same key",
              kid == item["kid"] == read_jws(item["token"])[0]["kid"])
        check(f"{title} CWT: label 1 is the iss of the JWT form, and the DID part of kid",
              claims[1] == jwt_payload["iss"] and kid.startswith(claims[1] + "#")
              and list(claims) == [1, 2, 6, 4, 65534, 65533])

    # TS-01 cross-page agreement with the TS-5-09 Dukcapil token.
    duk = st["lists"]["Credential status list"]
    header, payload, _, _ = read_jws(duk["token"])
    check("TS-01: protected header block equals the TS-5-09 token header",
          json.loads(out["Protected header of the credential status list"]) == header)
    check("TS-01: signer block holds iss and iat of the TS-5-09 token, byte for byte",
          json.loads(out["Signer named in the claims"]) == {"iss": payload["iss"], "iat": payload["iat"]})
    vm = json.loads(out["Verification method the kid names"])
    check("TS-01: verification method is the one Dukcapil's DID Document publishes under the kid",
          vm["id"] == header["kid"] and vm["controller"] == payload["iss"]
          and vm["type"] == "Multikey"
          and vm["publicKeyMultibase"] == db["entities"]["dukcapil"]["keys"]["status-list-1"]["multikey"])
    check("TS-01: that verification method sits under assertionMethod",
          vm["id"] in next(e for e in reversed(db["entities"]["dukcapil"]["entries"])
                           if e["versionTime"] <= iat_time)["state"]["assertionMethod"])
    ts01 = P_TS01.read_text()
    check("TS-01: page still dates the token 17 October 2026 06:00 UTC and the second log entry",
          "17 October 2026 06:00 UTC" in ts01 and "15 September 2026" in ts01
          and str(IAT) == str(payload["iat"]))

    # TS-5-08.
    att = st["attestation"]
    ah, ac, asig, ain = read_jws(att["token"])
    akey = did_document_key(db, ATTEST_ENTITY, ah["kid"], "2999-01-01T00:00:00Z")
    check("Key Attestation: JWS verifies under the key its kid names in the Wallet Provider DID Document",
          es256_verify(akey, asig, ain))
    check("Key Attestation: typ key-attestation+jwt, alg ES256, header holds no x5c, jwk or trust_chain",
          ah["typ"] == "key-attestation+jwt" and ah["alg"] == "ES256"
          and list(ah) == ["typ", "alg", "kid"])
    check("Key Attestation: kid and iss come from webvh.json, purpose key-attestation",
          ah["kid"] == db["entities"][ATTEST_ENTITY]["keys"][ATTEST_KEY]["kid"]
          and ac["iss"] == db["entities"][ATTEST_ENTITY]["did"]
          and ah["kid"].startswith(ac["iss"] + "#key-attestation-"))
    check("Key Attestation: claims are exactly the eight the table lists, exp within a day of iat",
          list(ac) == ["iss", "attested_keys", "key_storage", "user_authentication",
                       "certification", "nonce", "iat", "exp"]
          and ac["exp"] - ac["iat"] <= 86400)
    check("Key Attestation: attested_keys is one P-256 JWK with kty crv x y alone",
          len(ac["attested_keys"]) == 1 and list(ac["attested_keys"][0]) == ["kty", "crv", "x", "y"]
          and ac["attested_keys"][0]["crv"] == "P-256")
    check("Key Attestation: header and claims blocks decode from the token",
          json.loads(out["Key Attestation header"]) == ah
          and json.loads(out["Key Attestation claims"]) == ac)
    ph, pc, psig, pin = read_jws(att["proof"])
    holder_pub = webvh.public_key_from_multikey(att["holder_multikey"])
    check("Key proof: JWS verifies under the attested credential key",
          es256_verify(holder_pub, psig, pin))
    jwk = ph["jwk"]
    n = holder_pub.public_numbers()
    check("Key proof: header jwk is the attested key, which is the holder key",
          jwk == ac["attested_keys"][0] == jwk_of(holder_pub)
          and int.from_bytes(webvh._unb64u(jwk["x"]), "big") == n.x)
    check("Key proof: key_attestation is the attestation unchanged, and the proof signs no kid",
          ph["key_attestation"] == att["token"] and ph["typ"] == "openid4vci-proof+jwt"
          and "kid" not in ph)
    check("Key proof: nonce is the attestation's nonce, claims are aud iat nonce",
          pc["nonce"] == ac["nonce"] and list(pc) == ["aud", "iat", "nonce"])
    abb_h = json.loads(out["Key proof header, with the attestation abbreviated"])
    abb_p = json.loads(out["The attestation as the proof itself, abbreviated"])
    check("abbreviations are prefixes of the attestation, ending in three dots",
          abb_h["key_attestation"].endswith("...")
          and att["token"].startswith(abb_h["key_attestation"][:-3])
          and att["token"].startswith(abb_p["proofs"]["attestation"][0][:-3])
          and abb_h["jwk"] == jwk)
    attestation_page = P_ATTEST.read_text()
    check("TS-5-08: page still fixes the nonce, aud, certification and times it was written with",
          all(s in attestation_page for s in (
              ATTEST_NONCE, PROOF_AUD, ATTEST_CERT, str(ATTEST_IAT), str(ATTEST_EXP), str(PROOF_IAT))))
    h = out["holder"]
    check("holder member: did:key, JWK and COSE key agree with the keystore key",
          h["did_key"] == att["holder_did_key"] and h["jwk"] == att["holder_jwk"]
          and webvh._unb64u(h["jwk"]["x"]).hex() == h["cose_key"]["-2"]
          and webvh._unb64u(h["jwk"]["y"]).hex() == h["cose_key"]["-3"]
          and h["keystore"] == "holder-credential-1")
    check("holder did:key derives from the keystore key",
          att["holder_did_key"] == "did:key:" + att["holder_multikey"])

    check("every block title the pages carry is a key of statuslists.json",
          all(t in out for t in (
              "Credential status list, as served", "Credential status list claims",
              "Kartu ASN status list, as served", "Kartu ASN status list claims",
              "Use Statement status list, as served", "Use Statement status list claims",
              "Accreditation status list, as served", "Accreditation status list claims",
              "Credential status list, CWT form, in hex", "Kartu ASN status list, CWT form, in hex",
              "Protected header of the credential status list", "Signer named in the claims",
              "Verification method the kid names", "A Key Attestation, in compact serialization",
              "Key Attestation header", "Key Attestation claims",
              "A key proof carrying the attestation in its header",
              "Key proof header, with the attestation abbreviated", "Key proof claims",
              "The attestation as the proof itself, abbreviated"))
          and all(page_block(P_STATUS, t) is not None for t in (
              "Credential status list, as served", "Kartu ASN status list, CWT form, in hex")))

    print(f"wrote {OUT_JSON.relative_to(REPO_ROOT)}")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
