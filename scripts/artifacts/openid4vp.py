"""Build and verify the OpenID4VP exchanges of TS-3-01.

Two exchanges. The first is the Kartu ASN request TS-5-06 publishes, as it
travels: the authorization request in the QR code, the fetch of the request
URI, the signed Request Object, the encrypted response carrying the
presentation TS-5-11 publishes, and Verifier Core's answer. The second is a
merchant's online check: the Warung Bu Ani device signs a Request Object
under ``x509_hash`` with its Verifier Device Certificate in ``x5c``, the
request carries the category Use Statement of the Kartu ASN discount, and the
wallet answers with a Kartu ASN presentation encrypted to a key the device drew for the request,
through the relay at Terminal Nusantara's Verifier Core.

Inputs, read at run time: ``build/artifacts/presentations.json`` (the signed
Request Objects and the SD-JWT VC presentation), ``credentials.json`` (the
issued Kartu ASN), ``summary.json`` (the category Use Statement),
``verifier-device.pem`` and ``verifier-issuing-ca.pem``, and the keystore.

The Request Object and the Key Binding JWT are RFC 6979 ES256. Each JWE is
ECDH-ES with A128GCM, to the key each Request Object names, under an ephemeral key the keystore keeps and an IV
derived from its label, so a re-run writes the same bytes.

Output ``build/artifacts/openid4vp.json``::

    {"blocks": {<block title>: <text of the fenced block>, ...},
     "documents": {...}}

Run as ``.venv/bin/python scripts/artifacts/openid4vp.py`` after
``presentations.py``.
"""

from __future__ import annotations

import base64
import hashlib
import json
import sys
from pathlib import Path
from urllib.parse import quote, urlencode

from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

sys.path.insert(0, str(Path(__file__).resolve().parent))

import credentials as cr  # noqa: E402
import keystore  # noqa: E402
import webvh  # noqa: E402

ROOT = webvh.REPO_ROOT
ART = ROOT / "build" / "artifacts"
OUT = ART / "openid4vp.json"

b64u, unb64u, compact, wrap = cr.b64u, cr.unb64u, cr.compact, cr.wrap

# ---- block titles
T_QR = "The authorization request in the QR code"
T_GET = "GET of the request URI"
T_RO_200 = "200, the signed Request Object"
T_RO_H = "Protected header of the Request Object"
T_POST = "POST of the encrypted response"
T_JWE_H = "Protected header of the encrypted response"
T_JWE_P = "The response, decrypted"
T_POST_200 = "200, the response received"
T_POST_200_SD = "200, the response received on the same device"
T_REFUSE = "The response of a citizen who refuses, decrypted"
T_M_QR = "The authorization request in the merchant's QR code"
T_M_RO_H = "Protected header of the merchant's Request Object"
T_M_RO_P = "Claims of the merchant's Request Object"
T_M_RO = "The merchant's Request Object, as the relay serves it"
T_M_POST = "POST of the merchant's encrypted response to the relay"
T_M_JWE_H = "Protected header of the merchant's encrypted response"
T_M_JWE_P = "The merchant's response, decrypted on the device"

# ---- values the pages fix
HOST = "terminal-nusantara.co.id"
ASN_REQUEST_ID = "9vbqGNHdLrd781dSqQvJtQ"
RESPONSE_CODE = "l6vA73NPFTCvmWg6kTQLPA"
M_REQUEST_ID = "BmLpWLcn9GF1Tw2O8Jb5Uw"
M_NONCE = "wtlE9Lk7abdHqh2ZTbDJmA"
M_STATE = "BHXa1KFvGuDdKvabMuUNzw"
M_IAT = 1792224000
M_EXP = M_IAT + 300
M_KB_IAT = M_IAT + 40
M_USE_ID = "kategori-diskon-asn"
M_CLAIMS = ["nama", "instansi"]
ENC_KEY = "openid4vp-response-key-asn"
DEVICE_KEY = "verifier-device-warung-bu-ani"
# The key the merchant's device draws for its request (tracks/0362).
M_ENC_KEY = "openid4vp-response-key-merchant"
VP_FORMATS = {
    "dc+sd-jwt": {"sd-jwt_alg_values": ["ES256"], "kb-jwt_alg_values": ["ES256"]},
    "ldp_vc": {
        "proof_type_values": ["DataIntegrityProof"],
        "cryptosuite_values": ["ecdsa-rdfc-2019"],
    },
}


def request_uri(request_id: str, relay: bool) -> str:
    path = "relay" if relay else "presentation/request"
    return f"https://{HOST}/{path}/{request_id}" + ("/request" if relay else "")


def qr(client_id: str, uri: str) -> str:
    return "openid4vp://?" + urlencode({"client_id": client_id, "request_uri": uri}, quote_via=quote, safe="")


def thumbprint(jwk: dict) -> str:
    members = {k: jwk[k] for k in ("crv", "kty", "x", "y")}
    return b64u(hashlib.sha256(json.dumps(members, separators=(",", ":")).encode()).digest())


def enc_jwk(public_key) -> dict:
    x, y = cr.xy(public_key)
    jwk = {"kty": "EC", "crv": "P-256", "x": b64u(x), "y": b64u(y)}
    return {**jwk, "use": "enc", "alg": "ECDH-ES", "kid": thumbprint(jwk)}


# ---------------------------------------------------------------- JWE


def concat_kdf(z: bytes, enc: str, bits: int = 128) -> bytes:
    """RFC 7518 section 4.6.2, with empty apu and apv, for ECDH-ES direct."""
    def part(data: bytes) -> bytes:
        return len(data).to_bytes(4, "big") + data

    other = part(enc.encode()) + part(b"") + part(b"") + bits.to_bytes(4, "big")
    return hashlib.sha256((1).to_bytes(4, "big") + z + other).digest()[: bits // 8]


def jwe_encrypt(recipient_public, kid: str, payload: dict, label: str) -> tuple[str, dict]:
    eph = keystore.load_or_create(label)
    ex, ey = cr.xy(eph.public_key())
    header = {
        "alg": "ECDH-ES",
        "enc": "A128GCM",
        "kid": kid,
        "epk": {"kty": "EC", "crv": "P-256", "x": b64u(ex), "y": b64u(ey)},
    }
    protected = b64u(compact(header))
    cek = concat_kdf(eph.exchange(ec.ECDH(), recipient_public), "A128GCM")
    iv = hashlib.sha256(label.encode()).digest()[:12]
    sealed = AESGCM(cek).encrypt(iv, compact(payload), protected.encode("ascii"))
    ciphertext, tag = sealed[:-16], sealed[-16:]
    return f"{protected}..{b64u(iv)}.{b64u(ciphertext)}.{b64u(tag)}", header


def jwe_decrypt(private_key, token: str) -> tuple[dict, dict]:
    protected, key, iv, ciphertext, tag = token.split(".")
    header = json.loads(unb64u(protected))
    epk = header["epk"]
    eph = ec.EllipticCurvePublicNumbers(
        int.from_bytes(unb64u(epk["x"]), "big"), int.from_bytes(unb64u(epk["y"]), "big"), ec.SECP256R1()
    ).public_key()
    cek = concat_kdf(private_key.exchange(ec.ECDH(), eph), header["enc"])
    plain = AESGCM(cek).decrypt(unb64u(iv), unb64u(ciphertext) + unb64u(tag), protected.encode("ascii"))
    return header, json.loads(plain)


# ------------------------------------------------------------ the blocks


def http_get(uri: str) -> str:
    path = uri.split(HOST, 1)[1]
    return f"GET {path} HTTP/1.1\nHost: {HOST}\nAccept: application/oauth-authz-req+jwt"


def http_ro(jws: str) -> str:
    return (
        "HTTP/1.1 200 OK\nContent-Type: application/oauth-authz-req+jwt\n"
        f"Cache-Control: no-store\n\n{jws}"
    )


def http_post(uri: str, jwe: str) -> str:
    path = uri.split(HOST, 1)[1]
    return (
        f"POST {path} HTTP/1.1\nHost: {HOST}\n"
        f"Content-Type: application/x-www-form-urlencoded\n\nresponse={jwe}"
    )


def http_200(body: dict) -> str:
    return (
        "HTTP/1.1 200 OK\nContent-Type: application/json\nCache-Control: no-store\n\n"
        + json.dumps(body, indent=2)
    )


def merchant_payload(summary: dict, device_cert: x509.Certificate) -> tuple[dict, str]:
    der = device_cert.public_bytes(serialization.Encoding.DER)
    client_id = "x509_hash:" + b64u(hashlib.sha256(der).digest())
    statement = None
    for token in summary["use_statements"]:
        if json.loads(unb64u(token.split(".")[1]))["use_id"] == M_USE_ID:
            statement = token
    if statement is None:
        raise SystemExit(f"no Use Statement with use_id {M_USE_ID} in summary.json: run build.py")
    uri = request_uri(M_REQUEST_ID, relay=True)
    payload = {
        "client_id": client_id,
        "aud": "https://self-issued.me/v2",
        "response_type": "vp_token",
        "response_mode": "direct_post.jwt",
        "response_uri": uri.replace("/request", "/response"),
        "client_metadata": {
            "jwks": {"keys": [enc_jwk(keystore.load_or_create(M_ENC_KEY).public_key())]},
            "vp_formats_supported": VP_FORMATS,
        },
        "nonce": M_NONCE,
        "state": M_STATE,
        "dcql_query": {
            "credentials": [
                {
                    "id": "kartu-asn",
                    "format": "dc+sd-jwt",
                    "meta": {"vct_values": ["id.idctf.kartu-asn.1"]},
                    "claims": [{"path": [n]} for n in M_CLAIMS],
                }
            ]
        },
        "verifier_info": [{"format": "vnd.id.idctf.use-statement+jwt", "data": statement}],
        "iat": M_IAT,
        "exp": M_EXP,
    }
    return payload, client_id


def merchant_presentation(cred: dict, client_id: str) -> str:
    sd = cred["sd_jwt"]
    by_name = {d["array"][1]: d for d in sd["disclosures"]}
    body = sd["jwt"] + "~" + "".join(by_name[n]["disclosure"] + "~" for n in M_CLAIMS)
    sd_hash = b64u(hashlib.sha256(body.encode("ascii")).digest())
    header = {"typ": "kb+jwt", "alg": "ES256"}
    claims = {"iat": M_KB_IAT, "aud": client_id, "nonce": M_NONCE, "sd_hash": sd_hash}
    signing_input = b64u(compact(header)) + "." + b64u(compact(claims))
    sig = cr.es256_raw(cr.holder()["key"], signing_input.encode())
    return body + signing_input + "." + b64u(sig)


def build() -> dict:
    pres = json.loads((ART / "presentations.json").read_text())["documents"]
    cred = json.loads((ART / "credentials.json").read_text())
    summary = json.loads((ART / "summary.json").read_text())
    device_cert = x509.load_pem_x509_certificate((ART / "verifier-device.pem").read_bytes())
    issuing_cert = x509.load_pem_x509_certificate((ART / "verifier-issuing-ca.pem").read_bytes())

    # --- the first exchange, the Kartu ASN request of TS-5-06
    ro = pres["request_object"]
    asn_uri = request_uri(ASN_REQUEST_ID, relay=False)
    client_id = ro["payload"]["client_id"]
    response_uri = ro["payload"]["response_uri"]
    enc = ro["payload"]["client_metadata"]["jwks"]["keys"][0]
    enc_public = keystore.load_or_create(ENC_KEY).public_key()
    response = {"vp_token": pres["vp_token"], "state": ro["payload"]["state"]}
    jwe, jwe_header = jwe_encrypt(enc_public, enc["kid"], response, "openid4vp-jwe-ephemeral-asn")

    ro_ldp = pres["request_object_ldp"]["payload"]
    refusal = {"error": "access_denied", "state": ro_ldp["state"]}

    # --- the second exchange, the merchant's check through the relay
    m_payload, m_client_id = merchant_payload(summary, device_cert)
    der = serialization.Encoding.DER
    m_header = {
        "typ": "oauth-authz-req+jwt",
        "alg": "ES256",
        "x5c": [
            base64.b64encode(device_cert.public_bytes(der)).decode(),
            base64.b64encode(issuing_cert.public_bytes(der)).decode(),
        ],
    }
    signing_input = b64u(compact(m_header)) + "." + b64u(compact(m_payload))
    m_jws = signing_input + "." + b64u(cr.es256_raw(keystore.load_or_create(DEVICE_KEY), signing_input.encode()))
    m_uri = request_uri(M_REQUEST_ID, relay=True)
    m_presentation = merchant_presentation(cred, m_client_id)
    m_response = {"vp_token": {"kartu-asn": [m_presentation]}, "state": M_STATE}
    m_jwe, m_jwe_header = jwe_encrypt(
        keystore.load_or_create(M_ENC_KEY).public_key(), m_payload["client_metadata"]["jwks"]["keys"][0]["kid"],
        m_response, "openid4vp-jwe-ephemeral-merchant",
    )

    blocks = {
        T_QR: qr(client_id, asn_uri),
        T_GET: http_get(asn_uri),
        T_RO_200: http_ro(ro["jws"]),
        T_RO_H: json.dumps(ro["header"], indent=2),
        T_POST: http_post(response_uri, jwe),
        T_JWE_H: json.dumps(jwe_header, indent=2),
        T_JWE_P: json.dumps(response, indent=2),
        T_POST_200: http_200({}),
        T_POST_200_SD: http_200(
            {"redirect_uri": f"https://{HOST}/presentation/done#response_code={RESPONSE_CODE}"}
        ),
        T_REFUSE: json.dumps(refusal, indent=2),
        T_M_QR: qr(m_client_id, m_uri),
        T_M_RO_H: json.dumps(m_header, indent=2),
        T_M_RO_P: json.dumps(m_payload, indent=2, ensure_ascii=False),
        T_M_RO: wrap(m_jws),
        T_M_POST: http_post(m_payload["response_uri"], m_jwe),
        T_M_JWE_H: json.dumps(m_jwe_header, indent=2),
        T_M_JWE_P: json.dumps(m_response, indent=2),
    }
    return {
        "blocks": blocks,
        "documents": {
            "asn": {"request_uri": asn_uri, "jwe": jwe, "response": response},
            "refusal": refusal,
            "merchant": {
                "client_id": m_client_id,
                "request_uri": m_uri,
                "header": m_header,
                "payload": m_payload,
                "jws": m_jws,
                "presentation": m_presentation,
                "jwe": m_jwe,
                "response": m_response,
            },
        },
        "_pres": pres,
        "_cred": cred,
        "_device": device_cert,
        "_issuing": issuing_cert,
    }


# ----------------------------------------------------------------- verify


def reader_auth_role(certificate: x509.Certificate) -> dict[str, list[str]]:
    import importlib

    sys.path.insert(0, str(ROOT / "scripts"))
    va = importlib.import_module("verify_artifacts")
    return va.reader_auth_role(certificate)


def verify(b: dict) -> int:
    failures = 0

    def report(ok: bool, text: str) -> None:
        nonlocal failures
        print(("OK   " if ok else "FAIL ") + text)
        failures += 0 if ok else 1

    pres, cred = b["_pres"], b["_cred"]
    web = json.loads((ART / "webvh.json").read_text())
    ro = pres["request_object"]
    payload = ro["payload"]

    # Request Object of the first exchange
    rk = web["entities"]["terminal-nusantara"]["keys"]["request-object-1"]
    h, c, s = ro["jws"].split(".")
    report(
        cr.es256_check(webvh.public_key_from_multikey(rk["multikey"]), unb64u(s), f"{h}.{c}".encode())
        and json.loads(unb64u(h)) == {"typ": "oauth-authz-req+jwt", "alg": "ES256", "kid": rk["kid"]},
        "Kartu ASN Request Object verifies under request-object-1, header typ, alg and kid only",
    )
    for name, p in (("Kartu ASN", payload), ("Kartu Nikah", pres["request_object_ldp"]["payload"])):
        report(
            p["client_metadata"].get("vp_formats_supported") == VP_FORMATS
            and isinstance(p.get("iat"), int) and p["exp"] - p["iat"] == 300
            and len(unb64u(p["state"])) == 16 and len(unb64u(p["nonce"])) == 16
            and p["aud"] == "https://self-issued.me/v2",
            f"{name} Request Object carries vp_formats_supported, iat, exp, a 128-bit state and nonce",
        )
    report(
        payload["iat"] < pres["kb_claims"]["iat"] < payload["exp"],
        "the Key Binding JWT was signed inside the Request Object's lifetime",
    )
    qr_text = b["blocks"][T_QR]
    report(
        qr_text.startswith("openid4vp://?client_id=decentralized_identifier%3Adid%3Awebvh%3A")
        and quote(b["documents"]["asn"]["request_uri"], safe="") in qr_text,
        "the QR code carries client_id and request_uri, both percent-encoded, and nothing else",
    )
    # JWE of the first exchange
    header, plain = jwe_decrypt(keystore.load_or_create(ENC_KEY), b["documents"]["asn"]["jwe"])
    report(
        plain == {"vp_token": pres["vp_token"], "state": payload["state"]}
        and header["kid"] == payload["client_metadata"]["jwks"]["keys"][0]["kid"]
        and header["alg"] == "ECDH-ES" and header["enc"] == "A128GCM",
        "the response decrypts under the response encryption key to the TS-5-11 vp_token and the state",
    )
    report(
        payload["client_metadata"]["jwks"]["keys"][0]["kid"]
        == thumbprint(payload["client_metadata"]["jwks"]["keys"][0]),
        "the encryption key's kid is its RFC 7638 thumbprint",
    )

    # merchant Request Object
    m = b["documents"]["merchant"]
    device, issuing = b["_device"], b["_issuing"]
    der = device.public_bytes(serialization.Encoding.DER)
    report(
        m["client_id"] == "x509_hash:" + b64u(hashlib.sha256(der).digest())
        and base64.b64decode(m["header"]["x5c"][0]) == der,
        "x509_hash is the base64url SHA-256 of the DER of x5c[0], the Verifier Device Certificate",
    )
    h, c, s = m["jws"].split(".")
    report(
        cr.es256_check(device.public_key(), unb64u(s), f"{h}.{c}".encode())
        and json.loads(unb64u(c)) == m["payload"],
        "the merchant Request Object verifies under the key of x5c[0]",
    )
    try:
        device.verify_directly_issued_by(issuing)
        chained = True
    except Exception:  # noqa: BLE001
        chained = False
    report(
        chained and len(m["header"]["x5c"]) == 2,
        "x5c[0] is issued by x5c[1], the Verifier Issuing CA; the root is not carried",
    )
    statement = json.loads(unb64u(m["payload"]["verifier_info"][0]["data"].split(".")[1]))
    asked = [f"id.idctf.kartu-asn.1#{c['path'][0]}" for c in m["payload"]["dcql_query"]["credentials"][0]["claims"]]
    role = reader_auth_role(device)
    report(
        statement["use_id"] == M_USE_ID and set(asked) <= set(statement["claims"])
        and statement["sub"] == web["entities"]["terminal-nusantara"]["did"],
        "the category statement covers every attribute asked and names the holder of the Verifier Issuing CA",
    )
    report(
        set(M_CLAIMS) <= set(role.get("id.idctf.kartu-asn.1", set())),
        "the device's ReaderAuthRole covers every attribute asked",
    )
    report(
        m["payload"]["client_metadata"]["jwks"]["keys"][0]["x"] != b64u(cr.xy(device.public_key())[0])
        and m["payload"]["client_metadata"]["jwks"]["keys"][0]["x"]
        != payload["client_metadata"]["jwks"]["keys"][0]["x"]
        != pres["request_object_ldp"]["payload"]["client_metadata"]["jwks"]["keys"][0]["x"],
        "each Request Object names a key of its own, and the merchant's is not the device key",
    )
    # merchant presentation and its JWE
    pres_str = m["presentation"]
    prefix, _, kb = pres_str.rpartition("~")
    kh, kc, ks = kb.split(".")
    claims = json.loads(unb64u(kc))
    report(
        cr.es256_check(cr.holder()["key"].public_key(), unb64u(ks), f"{kh}.{kc}".encode())
        and claims["aud"] == m["client_id"] and claims["nonce"] == M_NONCE
        and claims["sd_hash"] == b64u(hashlib.sha256((prefix + "~").encode("ascii")).digest())
        and m["payload"]["iat"] < claims["iat"] < m["payload"]["exp"],
        "merchant Key Binding JWT verifies, aud is the x509_hash client_id, nonce and sd_hash match",
    )
    report(
        [json.loads(unb64u(d))[1] for d in pres_str.split("~")[1:-1]] == M_CLAIMS
        and pres_str.split("~")[0] == cred["sd_jwt"]["jwt"],
        "the merchant presentation is the issued Kartu ASN with the nama and instansi disclosures",
    )
    header, plain = jwe_decrypt(keystore.load_or_create(M_ENC_KEY), m["jwe"])
    report(
        plain == m["response"] and header["kid"] == m["payload"]["client_metadata"]["jwks"]["keys"][0]["kid"],
        "the merchant response decrypts under the key the device drew for the request",
    )
    report(
        b["blocks"][T_M_RO].replace("\n", "") == m["jws"]
        and json.loads(b["blocks"][T_M_RO_P]) == m["payload"]
        and json.loads(b["blocks"][T_M_RO_H]) == m["header"],
        "the merchant blocks decode to the signed token",
    )
    return failures


def main() -> int:
    b = build()
    OUT.write_text(
        json.dumps({"blocks": b["blocks"], "documents": b["documents"]}, indent=2, ensure_ascii=False) + "\n"
    )
    print(f"wrote {OUT.relative_to(ROOT)}")
    failures = verify(b)
    print("all checks passed" if not failures else f"{failures} check(s) FAILED")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
