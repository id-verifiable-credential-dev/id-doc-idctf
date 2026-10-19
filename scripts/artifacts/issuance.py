"""Build the exchanges TS-1-01 shows between Mobile Wallet and Issuer Core.

Two issuances run end to end. The Kartu ASN comes from BKN through the
Pre-Authorized Code flow with anonymous access, a ``jwt`` proof carrying the
Key Attestation, and the SD-JWT VC TS-5-10 shows. The KTP Digital comes from
Dukcapil through the Authorization Code flow with a pushed authorization
request, an ``attestation`` proof, a deferred answer, and the mdoc TS-5-10
shows. A third answer carries the Kartu Nikah ``ldp_vc`` of Kemenag, so that
every form of ``credential`` appears once.

What another page already shows is read from that page, never rebuilt: the
key proof and its Key Attestation from TS-5-08, the three credentials from
TS-5-10, the Type Metadata from the Credential Rulebook examples. What is new
is signed under keys the keystore keeps: the signed issuer metadata, with
each issuer's ``issuance-jose`` key; the DPoP proofs, with a DPoP key per
issuer; and the second Key Attestation, with the Wallet Provider's key. ECDSA
is randomized, so a stored token is kept while it still verifies and says the
same thing; ``--rebuild`` signs it anew.

Run after ``logs.py``, ``statuslists.py``, ``credentials.py`` and ``ldp.py``
have been injected: ``.venv/bin/python scripts/artifacts/issuance.py [--rebuild]``
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
import sys
import urllib.parse
from pathlib import Path

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

ROOT = webvh.REPO_ROOT
ART = ROOT / "build" / "artifacts"
OUT = ART / "issuance.json"
TS = webvh.TS_DIR
TS_5_08 = TS / "issuing-and-reading-a-key-attestation.md"
TS_5_10 = TS / "issuing-a-credential-in-sd-jwt-vc-mdoc-and-ldp-vc.md"
EXAMPLES = ROOT / "docs" / "credential-rulebook" / "example"

CLIENT_ID = "id.wallet"
REDIRECT_URI = "https://dompet.co.id/wallet/cb"

BKN = "https://issuer.bkn.go.id"
DUKCAPIL = "https://issuer.dukcapil.go.id"
KEMENAG = "https://issuer.kemenag.go.id"

ASN_SD = "id.idctf.kartu-asn.1:sd-jwt-vc"
ASN_MDOC = "id.idctf.kartu-asn.1:mdoc"
KTP_MDOC = "id.idctf.ktp.1:mdoc"
NIKAH_LDP = "id.idctf.kartu-nikah.1:ldp_vc"

METADATA_IAT = 1792195200  # 17 October 2026 00:00 UTC

# The BKN issuance. The c_nonce and the times of the attestation and the
# proof are the ones TS-5-08 already shows.
BKN_C_NONCE = "kQ8vZ2mH7rT1"
BKN_TOKEN_TRY = 1792216790
BKN_TOKEN = 1792216791
BKN_CREDENTIAL = 1792216806
BKN_NOTIFY = 1792216812
RENEWAL = 1884319200  # 17 September 2029 06:00 UTC

# The Dukcapil issuance, which ends before the mdoc's signing time of 06:00:10.
DUK_PAR = 1792216680
DUK_TOKEN = 1792216740
DUK_ATTEST = 1792216750
DUK_CREDENTIAL = 1792216755
DUK_DEFERRED = 1792216815

ACCESS_LIFETIME = 300
INTERVAL = 30


# --------------------------------------------------------------------------
# Encoding
# --------------------------------------------------------------------------


def b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def unb64u(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def seeded(label: str, size: int = 24) -> str:
    """A fixed value standing for one drawn at random."""
    return b64u(hashlib.sha256(f"idctf-example-{label}".encode()).digest()[:size])


def compact(obj) -> bytes:
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode()


def pretty(obj) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False)


def es256(key, data: bytes) -> bytes:
    r, s = decode_dss_signature(key.sign(data, ec.ECDSA(hashes.SHA256())))
    return r.to_bytes(32, "big") + s.to_bytes(32, "big")


def es256_ok(public_key, signature: bytes, data: bytes) -> bool:
    der = encode_dss_signature(int.from_bytes(signature[:32], "big"), int.from_bytes(signature[32:], "big"))
    try:
        public_key.verify(der, data, ec.ECDSA(hashes.SHA256()))
        return True
    except InvalidSignature:
        return False


def parts(token: str) -> tuple[dict, dict, bytes, bytes]:
    head, body, sig = token.split(".")
    return json.loads(unb64u(head)), json.loads(unb64u(body)), unb64u(sig), f"{head}.{body}".encode()


def jwk_of(public_key) -> dict:
    numbers = public_key.public_numbers()
    return {"kty": "EC", "crv": "P-256",
            "x": b64u(numbers.x.to_bytes(32, "big")), "y": b64u(numbers.y.to_bytes(32, "big"))}


def key_of_jwk(jwk: dict):
    return ec.EllipticCurvePublicNumbers(
        int.from_bytes(unb64u(jwk["x"]), "big"), int.from_bytes(unb64u(jwk["y"]), "big"), ec.SECP256R1()
    ).public_key()


class Signer:
    """Signs a token, or hands back the stored one while it still holds."""

    def __init__(self, stored: dict, rebuild: bool):
        self.stored = stored
        self.rebuild = rebuild
        self.made: dict[str, str] = {}

    def sign(self, label: str, key, header: dict, payload: dict) -> str:
        old = self.stored.get(label)
        if old and not self.rebuild:
            h, p, sig, signing_input = parts(old)
            if h == header and p == payload and es256_ok(key.public_key(), sig, signing_input):
                self.made[label] = old
                return old
        signing_input = b64u(compact(header)) + "." + b64u(compact(payload))
        token = signing_input + "." + b64u(es256(key, signing_input.encode()))
        self.made[label] = token
        return token


# --------------------------------------------------------------------------
# What other pages already show
# --------------------------------------------------------------------------


def page_block(page: Path, title: str) -> str:
    text = page.read_text()
    match = re.search(r'title="' + re.escape(title) + r'"[^\n]*\n(.*?)\n```', text, re.S)
    if not match:
        raise SystemExit(f"no block {title!r} in {page.name}")
    return match.group(1)


def joined(body: str) -> str:
    return "".join(body.split())


def webvh_db() -> dict:
    return json.loads((ART / "webvh.json").read_text())


# --------------------------------------------------------------------------
# HTTP
# --------------------------------------------------------------------------


def http_request(method: str, host: str, path: str, headers: list[str], body: str | None = None) -> str:
    lines = [f"{method} {path} HTTP/1.1", f"Host: {host}", *headers]
    return "\n".join(lines) + ("\n\n" + body if body is not None else "")


def http_answer(status: str, headers: list[str], body: str | None = None) -> str:
    lines = [f"HTTP/1.1 {status}", *headers]
    return "\n".join(lines) + ("\n\n" + body if body is not None else "")


def form(pairs: list[tuple[str, str]]) -> str:
    return "&".join(f"{k}={urllib.parse.quote(v, safe='')}" for k, v in pairs)


def ath(access_token: str) -> str:
    return b64u(hashlib.sha256(access_token.encode()).digest())


# --------------------------------------------------------------------------
# Issuer metadata
# --------------------------------------------------------------------------


def type_metadata(slug: str) -> dict:
    return json.loads((EXAMPLES / slug / "type-metadata.json").read_text())


def display_of(meta: dict) -> list[dict]:
    """``credential_metadata.display``, copied from the Type Metadata (REQ-TS-1-01-019)."""
    out = []
    for entry in meta["display"]:
        simple = entry["rendering"]["simple"]
        out.append({
            "name": entry["name"],
            "locale": entry["locale"],
            "description": entry["description"],
            "logo": {"uri": simple["logo"]["uri"], "alt_text": simple["logo"]["alt_text"]},
            "background_color": simple["background_color"],
            "text_color": simple["text_color"],
        })
    return out


def claims_of(meta: dict, namespace: str | None = None) -> list[dict]:
    """``credential_metadata.claims``; an mdoc path takes the namespace in front (REQ-TS-1-01-143)."""
    out = []
    for claim in meta["claims"]:
        path = claim["path"]
        if namespace and path[0] != namespace:
            path = [namespace, *path]
        entry = {"path": path}
        if "mandatory" in claim:
            entry["mandatory"] = claim["mandatory"]
        entry["display"] = [{"name": d["label"], "locale": d["locale"]} for d in claim["display"]]
        out.append(entry)
    return out


SUBSTANTIAL = {
    "key_storage": ["iso_18045_moderate", "iso_18045_high"],
    "user_authentication": ["iso_18045_moderate", "iso_18045_high"],
}
HIGH = {
    "key_storage": ["iso_18045_high"],
    "user_authentication": ["iso_18045_moderate", "iso_18045_high"],
}


def proof_types(required: dict, attestation_only: bool) -> dict:
    out = {}
    if not attestation_only:
        out["jwt"] = {"proof_signing_alg_values_supported": ["ES256"], "key_attestations_required": required}
    out["attestation"] = {"proof_signing_alg_values_supported": ["ES256"], "key_attestations_required": required}
    return out


def endpoints(base: str) -> dict:
    return {
        "credential_issuer": base,
        "credential_endpoint": f"{base}/credential",
        "nonce_endpoint": f"{base}/nonce",
        "deferred_credential_endpoint": f"{base}/deferred_credential",
        "notification_endpoint": f"{base}/notification",
    }


def bkn_metadata() -> dict:
    meta = type_metadata("kartu-asn")
    display = display_of(meta)
    return {
        **endpoints(BKN),
        "credential_configurations_supported": {
            ASN_SD: {
                "format": "dc+sd-jwt",
                "vct": "id.idctf.kartu-asn.1",
                "cryptographic_binding_methods_supported": ["jwk"],
                "credential_signing_alg_values_supported": ["ES256"],
                "proof_types_supported": proof_types(SUBSTANTIAL, False),
                "credential_metadata": {"display": display, "claims": claims_of(meta)},
            },
            ASN_MDOC: {
                "format": "mso_mdoc",
                "doctype": "id.idctf.kartu-asn.1",
                "cryptographic_binding_methods_supported": ["cose_key"],
                "credential_signing_alg_values_supported": [-7],
                "proof_types_supported": proof_types(SUBSTANTIAL, False),
                "credential_metadata": {"display": display, "claims": claims_of(meta, "id.idctf.kartu-asn.1")},
            },
        },
    }


def dukcapil_metadata() -> dict:
    meta = type_metadata("ktp-digital")
    return {
        **endpoints(DUKCAPIL),
        "credential_configurations_supported": {
            KTP_MDOC: {
                "format": "mso_mdoc",
                "doctype": "id.idctf.ktp.1",
                "cryptographic_binding_methods_supported": ["cose_key"],
                "credential_signing_alg_values_supported": [-7],
                "proof_types_supported": proof_types(HIGH, True),
                "credential_metadata": {"display": display_of(meta), "claims": claims_of(meta, "id.idctf.ktp.1")},
            },
        },
    }


def kemenag_configuration(credential: dict) -> dict:
    meta = type_metadata("kartu-nikah")
    return {
        NIKAH_LDP: {
            "format": "ldp_vc",
            "credential_definition": {"@context": credential["@context"], "type": credential["type"]},
            "cryptographic_binding_methods_supported": ["did:key"],
            "credential_signing_alg_values_supported": ["ecdsa-rdfc-2019"],
            "proof_types_supported": proof_types(SUBSTANTIAL, False),
            "credential_metadata": {"display": display_of(meta), "claims": claims_of(meta)},
        }
    }


def as_metadata(base: str) -> dict:
    return {
        "issuer": base,
        "authorization_endpoint": f"{base}/authorize",
        "token_endpoint": f"{base}/token",
        "pushed_authorization_request_endpoint": f"{base}/par",
        "require_pushed_authorization_requests": True,
        "response_types_supported": ["code"],
        "grant_types_supported": [
            "authorization_code",
            "urn:ietf:params:oauth:grant-type:pre-authorized_code",
            "refresh_token",
        ],
        "code_challenge_methods_supported": ["S256"],
        "token_endpoint_auth_methods_supported": ["none"],
        "authorization_details_types_supported": ["openid_credential"],
        "authorization_response_iss_parameter_supported": True,
        "dpop_signing_alg_values_supported": ["ES256"],
        "pre-authorized_grant_anonymous_access_supported": True,
    }


# --------------------------------------------------------------------------
# The exchanges
# --------------------------------------------------------------------------


def dpop(signer: Signer, label: str, key, method: str, url: str, iat: int,
         nonce: str | None = None, token: str | None = None) -> str:
    claims = {"jti": seeded(f"dpop-jti-{label}", 16), "htm": method, "htu": url, "iat": iat}
    if nonce:
        claims["nonce"] = nonce
    if token:
        claims["ath"] = ath(token)
    header = {"typ": "dpop+jwt", "alg": "ES256", "jwk": jwk_of(key.public_key())}
    return signer.sign(label, key, header, claims)


def decoded(token: str) -> str:
    header, payload, _, _ = parts(token)
    return pretty({"header": header, "payload": payload})


def build(rebuild: bool) -> dict:
    stored = {}
    if OUT.exists():
        stored = json.loads(OUT.read_text()).get("_tokens", {})
    signer = Signer(stored, rebuild)
    db = webvh_db()
    bkn_did = db["entities"]["bkn"]["did"]
    duk_did = db["entities"]["dukcapil"]["did"]
    blocks: dict[str, str] = {}

    no_store = "Cache-Control: no-store"
    json_type = "Content-Type: application/json"

    # ---- What TS-5-08 and TS-5-10 already show -------------------------------
    key_proof = joined(page_block(TS_5_08, "A key proof carrying the attestation in its header"))
    asn_sd_jwt = joined(page_block(TS_5_10, "A Kartu ASN in SD-JWT VC, as issued"))
    ktp_mdoc = bytes.fromhex(joined(page_block(TS_5_10, "The mdoc IssuerSigned, as issued")))
    nikah = json.loads(page_block(TS_5_10, "A Kartu Nikah in ldp_vc, as issued"))

    # ---- BKN, the Kartu ASN, Pre-Authorized Code flow ----------------------
    bkn_dpop = keystore.load_or_create("holder-dpop-bkn-1")
    pre_code = seeded("bkn-pre-authorized-code", 18)
    offer = {
        "credential_issuer": BKN,
        "credential_configuration_ids": [ASN_SD, ASN_MDOC],
        "grants": {
            "urn:ietf:params:oauth:grant-type:pre-authorized_code": {
                "pre-authorized_code": pre_code,
                "tx_code": {"input_mode": "numeric", "length": 6,
                            "description": "Kode enam angka yang dikirim BKN lewat SMS"},
            }
        },
    }
    blocks["A credential offer with a pre-authorized code, as the QR code carries it"] = (
        "openid-credential-offer://?credential_offer=" + urllib.parse.quote(compact(offer).decode(), safe="")
    )
    blocks["The same credential offer, decoded"] = pretty(offer)

    bkn_meta = bkn_metadata()
    bkn_meta_claims = {"iss": bkn_did, "sub": BKN, "iat": METADATA_IAT, **bkn_meta}
    bkn_meta_jwt = signer.sign(
        "bkn-metadata", keystore.load_or_create("bkn-issuance-jose-1"),
        {"typ": "openidvci-issuer-metadata+jwt", "alg": "ES256", "kid": f"{bkn_did}#issuance-jose-1"},
        bkn_meta_claims,
    )
    blocks["GET /.well-known/openid-credential-issuer, asking for the signed form"] = http_request(
        "GET", "issuer.bkn.go.id", "/.well-known/openid-credential-issuer", ["Accept: application/jwt"])
    blocks["200, the signed issuer metadata"] = http_answer(
        "200 OK", ["Content-Type: application/jwt"], bkn_meta_jwt)
    blocks["Signed issuer metadata header"] = pretty(parts(bkn_meta_jwt)[0])
    blocks["Signed issuer metadata claims"] = pretty(parts(bkn_meta_jwt)[1])

    blocks["GET /.well-known/oauth-authorization-server"] = http_request(
        "GET", "issuer.bkn.go.id", "/.well-known/oauth-authorization-server", ["Accept: application/json"])
    blocks["200, the authorization server metadata"] = http_answer(
        "200 OK", [json_type], pretty(as_metadata(BKN)))

    tx_code = "493817"
    details_request = [
        {"type": "openid_credential", "credential_configuration_id": ASN_SD},
        {"type": "openid_credential", "credential_configuration_id": ASN_MDOC},
    ]
    token_form = form([
        ("grant_type", "urn:ietf:params:oauth:grant-type:pre-authorized_code"),
        ("pre-authorized_code", pre_code),
        ("tx_code", tx_code),
        ("authorization_details", compact(details_request).decode()),
    ])
    token_url = f"{BKN}/token"
    try_proof = dpop(signer, "bkn-token-try", bkn_dpop, "POST", token_url, BKN_TOKEN_TRY)
    blocks["POST /token, a first attempt with no DPoP nonce"] = http_request(
        "POST", "issuer.bkn.go.id", "/token",
        ["Content-Type: application/x-www-form-urlencoded", f"DPoP: {try_proof}"], token_form)
    dpop_nonce_1 = seeded("bkn-dpop-nonce-1", 18)
    blocks["400, asking for a DPoP nonce"] = http_answer(
        "400 Bad Request", [f"DPoP-Nonce: {dpop_nonce_1}", no_store, json_type],
        pretty({"error": "use_dpop_nonce",
                "error_description": "Authorization server requires nonce in DPoP proof"}))

    token_proof = dpop(signer, "bkn-token", bkn_dpop, "POST", token_url, BKN_TOKEN, nonce=dpop_nonce_1)
    blocks["POST /token, the pre-authorized code"] = http_request(
        "POST", "issuer.bkn.go.id", "/token",
        ["Content-Type: application/x-www-form-urlencoded", f"DPoP: {token_proof}"], token_form)
    blocks["The DPoP proof of the token request, decoded"] = decoded(token_proof)

    access_bkn = seeded("bkn-access-token", 32)
    refresh_bkn = seeded("bkn-refresh-token", 32)
    asn_sd_id = "asn-" + seeded("bkn-credential-identifier-sd", 9)
    asn_mdoc_id = "asn-" + seeded("bkn-credential-identifier-mdoc", 9)
    dpop_nonce_2 = seeded("bkn-dpop-nonce-2", 18)
    blocks["200, the access token and the credential identifiers"] = http_answer(
        "200 OK", [f"DPoP-Nonce: {dpop_nonce_2}", no_store, json_type],
        pretty({
            "access_token": access_bkn,
            "token_type": "DPoP",
            "expires_in": ACCESS_LIFETIME,
            "refresh_token": refresh_bkn,
            "authorization_details": [
                {"type": "openid_credential", "credential_configuration_id": ASN_SD,
                 "credential_identifiers": [asn_sd_id]},
                {"type": "openid_credential", "credential_configuration_id": ASN_MDOC,
                 "credential_identifiers": [asn_mdoc_id]},
            ],
        }))

    blocks["POST /nonce"] = http_request("POST", "issuer.bkn.go.id", "/nonce", ["Content-Length: 0"])
    dpop_nonce_3 = seeded("bkn-dpop-nonce-3", 18)
    blocks["200, a fresh c_nonce"] = http_answer(
        "200 OK", [f"DPoP-Nonce: {dpop_nonce_3}", no_store, json_type], pretty({"c_nonce": BKN_C_NONCE}))

    credential_url = f"{BKN}/credential"
    credential_proof = dpop(signer, "bkn-credential", bkn_dpop, "POST", credential_url, BKN_CREDENTIAL,
                            nonce=dpop_nonce_3, token=access_bkn)
    blocks["POST /credential, the Kartu ASN as SD-JWT VC"] = http_request(
        "POST", "issuer.bkn.go.id", "/credential",
        [json_type, f"Authorization: DPoP {access_bkn}", f"DPoP: {credential_proof}"],
        pretty({"credential_identifier": asn_sd_id, "proofs": {"jwt": [key_proof]}}))
    blocks["The DPoP proof of the credential request, decoded"] = decoded(credential_proof)
    notification_bkn = seeded("bkn-notification-id", 12)
    dpop_nonce_4 = seeded("bkn-dpop-nonce-4", 18)
    blocks["200, the Kartu ASN as SD-JWT VC"] = http_answer(
        "200 OK", [f"DPoP-Nonce: {dpop_nonce_4}", no_store, json_type],
        pretty({"credentials": [{"credential": asn_sd_jwt}], "notification_id": notification_bkn}))

    notify_url = f"{BKN}/notification"
    notify_proof = dpop(signer, "bkn-notification", bkn_dpop, "POST", notify_url, BKN_NOTIFY,
                        nonce=dpop_nonce_4, token=access_bkn)
    blocks["POST /notification, the credential stored"] = http_request(
        "POST", "issuer.bkn.go.id", "/notification",
        [json_type, f"Authorization: DPoP {access_bkn}", f"DPoP: {notify_proof}"],
        pretty({"notification_id": notification_bkn, "event": "credential_accepted"}))
    blocks["204, the notification taken"] = http_answer(
        "204 No Content", [f"DPoP-Nonce: {seeded('bkn-dpop-nonce-5', 18)}", no_store])

    # ---- Renewal --------------------------------------------------------------
    renewal_nonce = seeded("bkn-dpop-nonce-renewal", 18)
    blocks["400, the refresh token request asked for a DPoP nonce"] = http_answer(
        "400 Bad Request", [f"DPoP-Nonce: {renewal_nonce}", no_store, json_type],
        pretty({"error": "use_dpop_nonce",
                "error_description": "Authorization server requires nonce in DPoP proof"}))
    renewal_proof = dpop(signer, "bkn-renewal", bkn_dpop, "POST", token_url, RENEWAL, nonce=renewal_nonce)
    blocks["POST /token, the refresh token"] = http_request(
        "POST", "issuer.bkn.go.id", "/token",
        ["Content-Type: application/x-www-form-urlencoded", f"DPoP: {renewal_proof}"],
        form([("grant_type", "refresh_token"), ("refresh_token", refresh_bkn)]))
    access_renewal = seeded("bkn-access-token-renewal", 32)
    blocks["200, a new access token for renewal"] = http_answer(
        "200 OK", [f"DPoP-Nonce: {seeded('bkn-dpop-nonce-renewal-2', 18)}", no_store, json_type],
        pretty({
            "access_token": access_renewal,
            "token_type": "DPoP",
            "expires_in": ACCESS_LIFETIME,
            "authorization_details": [
                {"type": "openid_credential", "credential_configuration_id": ASN_SD,
                 "credential_identifiers": [asn_sd_id]},
                {"type": "openid_credential", "credential_configuration_id": ASN_MDOC,
                 "credential_identifiers": [asn_mdoc_id]},
            ],
        }))

    # ---- Dukcapil, the KTP Digital, Authorization Code flow ----------------
    duk_dpop = keystore.load_or_create("holder-dpop-dukcapil-1")
    issuer_state = seeded("dukcapil-issuer-state", 18)
    offer_uri = f"{DUKCAPIL}/offer/{seeded('dukcapil-offer-id', 12)}"
    duk_offer = {
        "credential_issuer": DUKCAPIL,
        "credential_configuration_ids": [KTP_MDOC],
        "grants": {"authorization_code": {"issuer_state": issuer_state}},
    }
    blocks["A credential offer by reference, as the QR code carries it"] = (
        "openid-credential-offer://?credential_offer_uri=" + urllib.parse.quote(offer_uri, safe="")
    )
    blocks["GET the credential offer"] = http_request(
        "GET", "issuer.dukcapil.go.id", urllib.parse.urlparse(offer_uri).path, ["Accept: application/json"])
    blocks["200, the credential offer"] = http_answer("200 OK", [no_store, json_type], pretty(duk_offer))

    duk_meta = dukcapil_metadata()
    duk_meta_jwt = signer.sign(
        "dukcapil-metadata", keystore.load_or_create("dukcapil-issuance-jose-2"),
        {"typ": "openidvci-issuer-metadata+jwt", "alg": "ES256", "kid": f"{duk_did}#issuance-jose-2"},
        {"iss": duk_did, "sub": DUKCAPIL, "iat": METADATA_IAT, **duk_meta},
    )
    blocks["200, Dukcapil's signed issuer metadata"] = http_answer(
        "200 OK", ["Content-Type: application/jwt"], duk_meta_jwt)
    blocks["Dukcapil's issuer metadata claims"] = pretty(parts(duk_meta_jwt)[1])

    verifier = seeded("dukcapil-pkce-verifier", 32)
    challenge = b64u(hashlib.sha256(verifier.encode()).digest())
    state = seeded("dukcapil-state", 12)
    duk_details = [{"type": "openid_credential", "credential_configuration_id": KTP_MDOC}]
    par_url = f"{DUKCAPIL}/par"
    duk_nonce_par = seeded("dukcapil-dpop-nonce-1", 18)
    blocks["400, the pushed authorization request asked for a DPoP nonce"] = http_answer(
        "400 Bad Request", [f"DPoP-Nonce: {duk_nonce_par}", no_store, json_type],
        pretty({"error": "use_dpop_nonce",
                "error_description": "Authorization server requires nonce in DPoP proof"}))
    par_proof = dpop(signer, "dukcapil-par", duk_dpop, "POST", par_url, DUK_PAR, nonce=duk_nonce_par)
    blocks["POST /par, the pushed authorization request"] = http_request(
        "POST", "issuer.dukcapil.go.id", "/par",
        ["Content-Type: application/x-www-form-urlencoded", f"DPoP: {par_proof}"],
        form([
            ("response_type", "code"),
            ("client_id", CLIENT_ID),
            ("redirect_uri", REDIRECT_URI),
            ("state", state),
            ("code_challenge", challenge),
            ("code_challenge_method", "S256"),
            ("authorization_details", compact(duk_details).decode()),
            ("issuer_state", issuer_state),
        ]))
    blocks["The DPoP proof of the pushed authorization request, decoded"] = decoded(par_proof)
    request_uri = "urn:ietf:params:oauth:request_uri:" + seeded("dukcapil-request-uri", 18)
    duk_nonce_2 = seeded("dukcapil-dpop-nonce-2", 18)
    blocks["201, the request URI"] = http_answer(
        "201 Created", [f"DPoP-Nonce: {duk_nonce_2}", no_store, json_type],
        pretty({"request_uri": request_uri, "expires_in": 60}))

    blocks["The authorization request the wallet opens"] = (
        f"{DUKCAPIL}/authorize?" + form([("client_id", CLIENT_ID), ("request_uri", request_uri)])
    )
    code = seeded("dukcapil-authorization-code", 18)
    blocks["303, back to the wallet with the code"] = http_answer(
        "303 See Other",
        [f"Location: {REDIRECT_URI}?" + form([("code", code), ("state", state), ("iss", DUKCAPIL)]),
         no_store])

    duk_token_url = f"{DUKCAPIL}/token"
    duk_token_proof = dpop(signer, "dukcapil-token", duk_dpop, "POST", duk_token_url, DUK_TOKEN, nonce=duk_nonce_2)
    blocks["POST /token, the authorization code"] = http_request(
        "POST", "issuer.dukcapil.go.id", "/token",
        ["Content-Type: application/x-www-form-urlencoded", f"DPoP: {duk_token_proof}"],
        form([
            ("grant_type", "authorization_code"),
            ("code", code),
            ("code_verifier", verifier),
            ("redirect_uri", REDIRECT_URI),
            ("client_id", CLIENT_ID),
        ]))
    access_duk = seeded("dukcapil-access-token", 32)
    ktp_id = "ktp-" + seeded("dukcapil-credential-identifier", 9)
    duk_nonce_3 = seeded("dukcapil-dpop-nonce-3", 18)
    blocks["200, the access token after an authorization code"] = http_answer(
        "200 OK", [f"DPoP-Nonce: {duk_nonce_3}", no_store, json_type],
        pretty({
            "access_token": access_duk,
            "token_type": "DPoP",
            "expires_in": ACCESS_LIFETIME,
            "refresh_token": seeded("dukcapil-refresh-token", 32),
            "authorization_details": [
                {"type": "openid_credential", "credential_configuration_id": KTP_MDOC,
                 "credential_identifiers": [ktp_id]},
            ],
        }))

    # The second Key Attestation, bound to Dukcapil's c_nonce.
    duk_c_nonce = seeded("dukcapil-c-nonce", 9)
    attestation_claims = json.loads(page_block(TS_5_08, "Key Attestation claims"))
    attestation_header = json.loads(page_block(TS_5_08, "Key Attestation header"))
    attestation_claims.update({"nonce": duk_c_nonce, "iat": DUK_ATTEST, "exp": DUK_ATTEST + 86400})
    attestation = signer.sign(
        "dukcapil-key-attestation", keystore.load_or_create("dompet-key-attestation-1"),
        attestation_header, attestation_claims)
    blocks["The Key Attestation for Dukcapil's nonce, decoded"] = pretty(attestation_claims)

    duk_nonce_4 = seeded("dukcapil-dpop-nonce-4", 18)
    blocks["200, Dukcapil's c_nonce"] = http_answer(
        "200 OK", [f"DPoP-Nonce: {duk_nonce_4}", no_store, json_type], pretty({"c_nonce": duk_c_nonce}))

    duk_credential_url = f"{DUKCAPIL}/credential"
    duk_credential_proof = dpop(signer, "dukcapil-credential", duk_dpop, "POST", duk_credential_url,
                                DUK_CREDENTIAL, nonce=duk_nonce_4, token=access_duk)
    blocks["POST /credential, the KTP Digital with an attestation proof"] = http_request(
        "POST", "issuer.dukcapil.go.id", "/credential",
        [json_type, f"Authorization: DPoP {access_duk}", f"DPoP: {duk_credential_proof}"],
        pretty({"credential_identifier": ktp_id, "proofs": {"attestation": [attestation]}}))
    transaction = seeded("dukcapil-transaction-id", 15)
    duk_nonce_5 = seeded("dukcapil-dpop-nonce-5", 18)
    blocks["202, the KTP Digital deferred"] = http_answer(
        "202 Accepted", [f"DPoP-Nonce: {duk_nonce_5}", no_store, json_type],
        pretty({"transaction_id": transaction, "interval": INTERVAL}))

    deferred_url = f"{DUKCAPIL}/deferred_credential"
    deferred_proof = dpop(signer, "dukcapil-deferred", duk_dpop, "POST", deferred_url, DUK_DEFERRED,
                          nonce=duk_nonce_5, token=access_duk)
    blocks["POST /deferred_credential"] = http_request(
        "POST", "issuer.dukcapil.go.id", "/deferred_credential",
        [json_type, f"Authorization: DPoP {access_duk}", f"DPoP: {deferred_proof}"],
        pretty({"transaction_id": transaction}))
    blocks["200, the KTP Digital as mdoc"] = http_answer(
        "200 OK", [f"DPoP-Nonce: {seeded('dukcapil-dpop-nonce-6', 18)}", no_store, json_type],
        pretty({"credentials": [{"credential": b64u(ktp_mdoc)}],
                "notification_id": seeded("dukcapil-notification-id", 12)}))

    # ---- Kemenag, the form of an ldp_vc answer ---------------------------------
    blocks["The ldp_vc configuration in Kemenag's issuer metadata"] = pretty(
        {"credential_configurations_supported": kemenag_configuration(nikah)})
    blocks["200, the Kartu Nikah as ldp_vc"] = http_answer(
        "200 OK", [f"DPoP-Nonce: {seeded('kemenag-dpop-nonce', 18)}", no_store, json_type],
        pretty({"credentials": [{"credential": nikah}],
                "notification_id": seeded("kemenag-notification-id", 12)}))

    # ---- Errors ---------------------------------------------------------------
    blocks["400, a credential request whose nonce was used"] = http_answer(
        "400 Bad Request", [f"DPoP-Nonce: {seeded('bkn-dpop-nonce-error', 18)}", no_store, json_type],
        pretty({"error": "invalid_nonce"}))
    blocks["400, a credential request the source system refuses"] = http_answer(
        "400 Bad Request", [f"DPoP-Nonce: {seeded('bkn-dpop-nonce-denied', 18)}", no_store, json_type],
        pretty({"error": "credential_request_denied",
                "error_description": "No record of this citizen in the source system"}))

    return {
        "issuers": {"bkn": BKN, "dukcapil": DUKCAPIL, "kemenag": KEMENAG},
        "client_id": CLIENT_ID,
        "values": {
            "bkn_access_token": access_bkn,
            "dukcapil_access_token": access_duk,
            "pkce_verifier": verifier,
            "pkce_challenge": challenge,
            "dukcapil_c_nonce": duk_c_nonce,
            "attestation": attestation,
            "bkn_metadata": bkn_meta_jwt,
            "dukcapil_metadata": duk_meta_jwt,
        },
        "blocks": blocks,
        "_tokens": signer.made,
    }


# --------------------------------------------------------------------------
# Verification
# --------------------------------------------------------------------------


def verify(out: dict) -> bool:
    ok_all = True

    def check(label: str, ok: bool) -> None:
        nonlocal ok_all
        ok_all &= ok
        print(f"{'OK' if ok else 'FAIL'}  {label}")

    db = webvh_db()
    blocks = out["blocks"]
    values = out["values"]

    def method_key(kid: str):
        did = kid.split("#")[0]
        for entity in db["entities"].values():
            if entity["did"] != did:
                continue
            for entry in entity["entries"]:
                for method in entry["state"]["verificationMethod"]:
                    if method["id"] == kid and kid in entry["state"].get("assertionMethod", []):
                        return webvh.public_key_from_multikey(method["publicKeyMultibase"])
        raise KeyError(kid)

    for name, base in (("bkn_metadata", BKN), ("dukcapil_metadata", DUKCAPIL)):
        header, payload, sig, signing_input = parts(values[name])
        check(f"{name}: signature under {header['kid'].split('#')[1]}",
              es256_ok(method_key(header["kid"]), sig, signing_input))
        check(f"{name}: sub and credential_issuer are the issuer identifier, iss is the kid's DID",
              payload["sub"] == base == payload["credential_issuer"] and header["kid"].startswith(payload["iss"] + "#"))

    for title, body in blocks.items():
        for line in body.split("\n"):
            if not line.startswith("DPoP: "):
                continue
            token = line.removeprefix("DPoP: ")
            header, claims, sig, signing_input = parts(token)
            request_line = body.split("\n")[0].split()
            host = body.split("\n")[1].removeprefix("Host: ")
            check(f"{title}: DPoP signature, htm, htu",
                  es256_ok(key_of_jwk(header["jwk"]), sig, signing_input)
                  and claims["htm"] == request_line[0] and claims["htu"] == f"https://{host}{request_line[1]}")
            auth = [l for l in body.split("\n") if l.startswith("Authorization: DPoP ")]
            if auth:
                check(f"{title}: ath is the hash of the access token",
                      claims.get("ath") == ath(auth[0].removeprefix("Authorization: DPoP ")))

    proof = json.loads(blocks["POST /credential, the Kartu ASN as SD-JWT VC"].split("\n\n", 1)[1])["proofs"]["jwt"][0]
    _, proof_claims, _, _ = parts(proof)
    check("key proof aud is the BKN credential issuer, nonce the c_nonce served",
          proof_claims["aud"] == BKN and proof_claims["nonce"] == BKN_C_NONCE
          and json.loads(blocks["200, a fresh c_nonce"].split("\n\n", 1)[1])["c_nonce"] == BKN_C_NONCE)

    att_header, att_claims, att_sig, att_input = parts(values["attestation"])
    check("Dukcapil attestation: signature, nonce",
          es256_ok(method_key(att_header["kid"]), att_sig, att_input) and att_claims["nonce"] == values["dukcapil_c_nonce"])

    check("PKCE challenge is S256 of the verifier",
          b64u(hashlib.sha256(values["pkce_verifier"].encode()).digest()) == values["pkce_challenge"])

    sd_jwt = json.loads(blocks["200, the Kartu ASN as SD-JWT VC"].split("\n\n", 1)[1])["credentials"][0]["credential"]
    _, sd_claims, _, _ = parts(sd_jwt.split("~")[0])
    bkn_claims = parts(values["bkn_metadata"])[1]
    check("the SD-JWT VC iss is the DID the signed metadata names", sd_claims["iss"] == bkn_claims["iss"])
    check("the SD-JWT VC is bound to the key the attestation covers",
          sd_claims["cnf"]["jwk"] == parts(proof)[0]["jwk"])
    mdoc_claims = bkn_claims["credential_configurations_supported"][ASN_MDOC]["credential_metadata"]["claims"]
    check("every mso_mdoc claim path starts with the namespace (REQ-TS-1-01-143)",
          all(c["path"][0] == "id.idctf.kartu-asn.1" and len(c["path"]) == 2 for c in mdoc_claims))
    return ok_all


def main() -> int:
    out = build("--rebuild" in sys.argv)
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0 if verify(json.loads(OUT.read_text())) else 1


if __name__ == "__main__":
    sys.exit(main())
