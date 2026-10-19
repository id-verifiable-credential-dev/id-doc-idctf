"""The enrollment of a wallet installation and the request for its Key Attestation.

Builds the artifacts of TS-2-01: the record Wallet Backend Service holds for
an Android installation, the two binding strings and their hashes, the
platform evidence as Wallet Backend Service reads it once decoded, the
device key's signature over a Key Attestation request on Android, and the
App Attest assertion that carries the same request on iOS. Writes them to
``build/artifacts/enrollment.json`` keyed by block title.

The Android installation's credential key is the one the Key Attestation of
TS-5-08 attests, and its request carries that attestation's nonce, so the two
pages show one installation. The platform's own chains are not built: they
are signed by Google and Apple roots, and an illustration does not imitate
either. The evidence is shown decoded, every field exact.

Signing is randomized: a stored signature is kept while what it covers stays
the same. Run as a script it builds, verifies its own output, and prints one
line per check; the exit status is 0 only when every check passes.
"""

from __future__ import annotations

import base64
import hashlib
import json
import sys
from pathlib import Path

import cbor2
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

sys.path.insert(0, str(Path(__file__).resolve().parent))
import keystore  # noqa: E402
import webvh  # noqa: E402

REPO_ROOT = webvh.REPO_ROOT
STATUSLISTS_JSON = REPO_ROOT / "build" / "artifacts" / "statuslists.json"
OUT_JSON = REPO_ROOT / "build" / "artifacts" / "enrollment.json"

# --- values the page fixes, kept by hand ------------------------------------
PACKAGE = "id.co.dompet.wallet"
APP_ID = "D7K2M9Q4XW.id.co.dompet.wallet"  # Team ID and bundle identifier
SIGNING_CERT_DIGEST = hashlib.sha256(
    b"Dompet Digital Nusantara release signing certificate, illustration"
).digest()
VERSION_CODE = "42"

IDP_ISS = "https://login.akunnusantara.co.id"
IDP_SUB = "5f0c9a1e-7b3d-4c2e-9a61-2d8e4b7f3c10"
WBS_CLIENT_ID = "dompet-wallet"

ANDROID_CHALLENGE = "Yb3xQ0nR7vLp2sKd9WfH1g"
IOS_CHALLENGE = "tK7vN2qZ8mR4xW1cL5pD0s"
ENROLLED_AT = 1792215002  # 17 October 2026 05:30:02 UTC, after the verdict
PREVIOUS_ENROLLED_AT = 1760000000
VERIFIED_BOOT_KEY = hashlib.sha256(b"Nusa Teknologi verified boot key, illustration").digest()
VERIFIED_BOOT_HASH = hashlib.sha256(b"Nusa Phone 8 Pro boot image, illustration").digest()
IOS_ENROLLED_AT = 1792215600
KEY_STORAGE = ["iso_18045_high"]
USER_AUTH = ["iso_18045_moderate"]
CERTIFICATION = "https://dompet.co.id/certification/se-2026-a"
DEVICE_MODEL = "Nusa Phone 8 Pro"
DEVICE_BRAND = "nusa"
DEVICE_MANUFACTURER = "Nusa Teknologi"
IOS_MODEL = "iPhone17,1"
IOS_SUB = "a3e17c52-08d4-4f9b-b6c2-71d0e95a4b28"
IOS_KEY_VALUE = ["iso_18045_enhanced-basic"]

REQUEST_MILLIS = 1792216798000  # two seconds before the attestation's iat
ASSERTION_COUNTER = 1

ANDROID_DEVICE_KEY = "wallet-device-android-1"
IOS_DEVICE_KEY = "wallet-device-ios-1"
IOS_CREDENTIAL_KEY = "holder-credential-ios-1"
PREVIOUS_DEVICE_KEY = "wallet-device-android-0"
PREVIOUS_CREDENTIAL_KEY = "holder-credential-0"
PREVIOUS_MODEL = "Nusa Phone 5"


# --- helpers ----------------------------------------------------------------
def b64u(data: bytes) -> str:
    return webvh._b64u(data)


def jwk_of(public_key) -> dict:
    n = public_key.public_numbers()
    return {
        "kty": "EC",
        "crv": "P-256",
        "x": b64u(n.x.to_bytes(32, "big")),
        "y": b64u(n.y.to_bytes(32, "big")),
    }


def thumbprint(jwk: dict) -> str:
    """RFC 7638: the required members in lexicographic order, no whitespace."""
    members = {k: jwk[k] for k in ("crv", "kty", "x", "y")}
    canonical = json.dumps(members, separators=(",", ":"), sort_keys=True)
    return b64u(hashlib.sha256(canonical.encode()).digest())


def thumbprint_input(jwk: dict) -> str:
    """The canonical JSON RFC 7638 hashes: required members, sorted, no whitespace."""
    members = {k: jwk[k] for k in ("crv", "kty", "x", "y")}
    return json.dumps(members, separators=(",", ":"), sort_keys=True)


def binding(first: str, credential_thumbprint: str) -> tuple[str, bytes]:
    """The binding string and its SHA-256 hash."""
    text = f"{first}.{credential_thumbprint}"
    return text, hashlib.sha256(text.encode()).digest()


def uncompressed(public_key) -> bytes:
    return public_key.public_bytes(
        serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint
    )


def es256_raw(key, data: bytes) -> bytes:
    from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature

    r, s = decode_dss_signature(key.sign(data, ec.ECDSA(hashes.SHA256())))
    return r.to_bytes(32, "big") + s.to_bytes(32, "big")


def es256_raw_ok(public_key, signature: bytes, data: bytes) -> bool:
    from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature

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


def pretty(obj) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False)


def load_stored() -> dict:
    if not OUT_JSON.exists():
        return {}
    return json.loads(OUT_JSON.read_text()).get("_structured", {})


# --- build ------------------------------------------------------------------
def build() -> dict:
    stored = load_stored()
    attestation = json.loads(STATUSLISTS_JSON.read_text())["_structured"]["attestation"]
    nonce = attestation["claims"]["nonce"]

    # Android: the installation whose credential key TS-5-08 attests.
    cred = keystore.load_or_create(attestation["holder_keystore"])
    cred_jwk = jwk_of(cred.public_key())
    if cred_jwk != attestation["holder_jwk"]:
        raise SystemExit("the credential key is not the key TS-5-08 attests")
    cred_tp = thumbprint(cred_jwk)
    device = keystore.load_or_create(ANDROID_DEVICE_KEY)
    device_jwk = jwk_of(device.public_key())
    device_tp = thumbprint(device_jwk)

    e_text, e_hash = binding(ANDROID_CHALLENGE, cred_tp)
    r_text, r_hash = binding(nonce, cred_tp)

    out: dict = {}
    out["The enrollment binding string"] = e_text
    out["The request binding string"] = r_text

    def key_description(purpose: str, auth: bool) -> str:
        lines = [
            "attestationVersion        300",
            "attestationSecurityLevel  StrongBox",
            "keyMintVersion            300",
            "keyMintSecurityLevel      StrongBox",
            f'attestationChallenge      "{ANDROID_CHALLENGE}"',
            "softwareEnforced {",
            "  attestationApplicationId {",
            "    packageInfos {",
            f'      packageName         "{PACKAGE}"',
            f"      version             {VERSION_CODE}",
            "    }",
            "    signatureDigests {",
            f"      {SIGNING_CERT_DIGEST.hex()}",
            "    }",
            "  }",
            "}",
            "hardwareEnforced {",
            f"  purpose                 [{purpose}]",
            "  algorithm               EC",
            "  ecCurve                 P_256",
        ]
        ids = [
            f'  attestationIdBrand      "{DEVICE_BRAND}"',
            f'  attestationIdManufacturer "{DEVICE_MANUFACTURER}"',
            f'  attestationIdModel      "{DEVICE_MODEL}"',
        ]
        if auth:
            lines += [
                "  userSecureId            7406185221307495937",
                "  userAuthType            FINGERPRINT | PASSWORD",
            ]
        else:
            lines += ["  noAuthRequired"]
        lines += [
            "  origin                  GENERATED",
            "  rootOfTrust {",
            f"    verifiedBootKey       {VERIFIED_BOOT_KEY.hex()}",
            "    deviceLocked          true",
            "    verifiedBootState     Verified",
            f"    verifiedBootHash      {VERIFIED_BOOT_HASH.hex()}",
            "  }",
        ] + ids + ["}"]
        return "\n".join(lines)

    out["KeyDescription of the credential key, decoded"] = key_description("SIGN", True)
    out["KeyDescription of the device key, decoded"] = key_description("SIGN", False)

    def verdict(request_hash: bytes, millis: int) -> dict:
        return {
            "requestDetails": {
                "requestPackageName": PACKAGE,
                "timestampMillis": str(millis),
                "requestHash": b64u(request_hash),
            },
            "appIntegrity": {
                "appRecognitionVerdict": "PLAY_RECOGNIZED",
                "packageName": PACKAGE,
                "certificateSha256Digest": [b64u(SIGNING_CERT_DIGEST)],
                "versionCode": VERSION_CODE,
            },
            "deviceIntegrity": {
                "deviceRecognitionVerdict": [
                    "MEETS_BASIC_INTEGRITY",
                    "MEETS_DEVICE_INTEGRITY",
                    "MEETS_STRONG_INTEGRITY",
                ]
            },
            "accountDetails": {"appLicensingVerdict": "LICENSED"},
        }

    enroll_verdict = verdict(e_hash, (ENROLLED_AT - 1) * 1000)
    request_verdict = verdict(r_hash, REQUEST_MILLIS)
    out["The integrity verdict at enrollment, decoded"] = pretty(enroll_verdict)
    out["The integrity verdict in the request, decoded"] = pretty(request_verdict)

    out["The identity provider's token claims, decoded"] = pretty({
        "iss": IDP_ISS,
        "sub": IDP_SUB,
        "aud": WBS_CLIENT_ID,
        "nonce": ANDROID_CHALLENGE,
        "iat": ENROLLED_AT - 20,
        "exp": ENROLLED_AT + 280,
    })

    record = {
        "installation": device_tp,
        "platform": "android",
        "account": {"iss": IDP_ISS, "sub": IDP_SUB},
        "device_key": device_jwk,
        "credential_key": cred_jwk,
        "device_model": DEVICE_MODEL,
        "key_storage_component": "StrongBox",
        "key_storage": KEY_STORAGE,
        "user_authentication": USER_AUTH,
        "certification": CERTIFICATION,
        "state": "active",
        "enrolled_at": ENROLLED_AT,
    }
    out["The installation record"] = pretty(record)

    # TS-5-03: the same device key, its canonical form, and the identifier.
    out["A device key and its device identifier"] = "\n\n".join([
        pretty(device_jwk), thumbprint_input(device_jwk), device_tp,
    ])

    # The installation the same account held before, revoked when this one enrolled.
    prev_device = keystore.load_or_create(PREVIOUS_DEVICE_KEY)
    prev_cred = keystore.load_or_create(PREVIOUS_CREDENTIAL_KEY)
    out["The previous installation's record, revoked"] = pretty({
        "installation": thumbprint(jwk_of(prev_device.public_key())),
        "platform": "android",
        "account": {"iss": IDP_ISS, "sub": IDP_SUB},
        "device_key": jwk_of(prev_device.public_key()),
        "credential_key": jwk_of(prev_cred.public_key()),
        "device_model": PREVIOUS_MODEL,
        "key_storage_component": "TrustedEnvironment",
        "key_storage": ["iso_18045_enhanced-basic"],
        "user_authentication": ["iso_18045_enhanced-basic"],
        "state": "revoked",
        "enrolled_at": PREVIOUS_ENROLLED_AT,
        "revoked_at": ENROLLED_AT,
    })

    # The device key's signature over the request binding string, on Android.
    prev_sig = stored.get("android_signature", {})
    if prev_sig.get("signed") == r_text and es256_raw_ok(
        device.public_key(), webvh._unb64u(prev_sig["value"]), r_text.encode()
    ):
        signature = prev_sig["value"]
    else:
        signature = b64u(es256_raw(device, r_text.encode()))
    out["The device key's signature over the request binding string"] = signature

    # iOS: the App Attest key is the device key, the credential key a separate
    # Secure Enclave key whose thumbprint the enrollment binding carries.
    ios_device = keystore.load_or_create(IOS_DEVICE_KEY)
    ios_cred = keystore.load_or_create(IOS_CREDENTIAL_KEY)
    ios_cred_jwk = jwk_of(ios_cred.public_key())
    ios_cred_tp = thumbprint(ios_cred_jwk)
    ios_e_text, ios_e_hash = binding(IOS_CHALLENGE, ios_cred_tp)
    ios_r_text, ios_r_hash = binding(nonce, ios_cred_tp)
    rp_id_hash = hashlib.sha256(APP_ID.encode()).digest()
    key_id = hashlib.sha256(uncompressed(ios_device.public_key())).digest()

    out["The iOS enrollment binding string"] = ios_e_text
    out["The App Attest attestation, as Wallet Backend Service checks it"] = pretty({
        "attestation": {
            "fmt": "apple-appattest",
            "keyId": base64.b64encode(key_id).decode(),
            "clientDataHash": b64u(ios_e_hash),
            "authData": {
                "rpIdHash": rp_id_hash.hex(),
                "signCount": 0,
                "aaguid": (b"appattest" + b"\x00" * 7).hex(),
                "credentialId": key_id.hex(),
            },
        },
        "credential_key": ios_cred_jwk,
    })

    auth_data = rp_id_hash + b"\x00" + ASSERTION_COUNTER.to_bytes(4, "big")
    prev_as = stored.get("ios_assertion", {})
    message = hashlib.sha256(auth_data + ios_r_hash).digest()
    if prev_as.get("signed") == ios_r_text and prev_as.get("authenticatorData") == auth_data.hex():
        der = bytes.fromhex(prev_as["signature"])
    else:
        der = ios_device.sign(message, ec.ECDSA(hashes.SHA256()))
    assertion = cbor2.dumps({"signature": der, "authenticatorData": auth_data})
    out["The installation record on iOS"] = pretty({
        "installation": thumbprint(jwk_of(ios_device.public_key())),
        "platform": "ios",
        "account": {"iss": IDP_ISS, "sub": IOS_SUB},
        "device_key": jwk_of(ios_device.public_key()),
        "credential_key": ios_cred_jwk,
        "device_model": IOS_MODEL,
        "key_storage_component": "SecureEnclave",
        "key_storage": IOS_KEY_VALUE,
        "user_authentication": IOS_KEY_VALUE,
        "sign_count": ASSERTION_COUNTER,
        "state": "active",
        "enrolled_at": IOS_ENROLLED_AT,
    })
    out["The iOS request binding string"] = ios_r_text
    out["The App Attest assertion, in hex"] = "\n".join(
        assertion.hex()[i : i + 64] for i in range(0, len(assertion.hex()), 64)
    )

    out["_structured"] = {
        "android": {
            "device_jwk": device_jwk, "device_thumbprint": device_tp,
            "credential_jwk": cred_jwk, "credential_thumbprint": cred_tp,
            "challenge": ANDROID_CHALLENGE, "enrollment_hash": b64u(e_hash),
            "request_hash": b64u(r_hash), "nonce": nonce,
        },
        "android_signature": {"signed": r_text, "value": signature},
        "ios": {
            "device_jwk": jwk_of(ios_device.public_key()),
            "device_thumbprint": thumbprint(jwk_of(ios_device.public_key())),
            "credential_jwk": ios_cred_jwk, "credential_thumbprint": ios_cred_tp,
            "challenge": IOS_CHALLENGE, "key_id": base64.b64encode(key_id).decode(),
            "app_id": APP_ID,
        },
        "ios_assertion": {
            "signed": ios_r_text, "authenticatorData": auth_data.hex(),
            "signature": der.hex(),
        },
    }
    return out


# --- verify -----------------------------------------------------------------
def main() -> int:
    out = build()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    st = out["_structured"]
    failures = 0

    def check(label: str, ok: bool) -> None:
        nonlocal failures
        print(("ok    " if ok else "FAIL  ") + label)
        failures += 0 if ok else 1

    a = st["android"]
    record = json.loads(out["The installation record"])
    check("Android: the installation is the thumbprint of the device key",
          record["installation"] == thumbprint(record["device_key"]))
    check("Android: the enrollment binding is challenge.credential thumbprint",
          out["The enrollment binding string"] == f"{a['challenge']}.{a['credential_thumbprint']}")
    shown_jwk, shown_canonical, shown_id = out["A device key and its device identifier"].split("\n\n")
    check("Android: the device identifier block shows the installation's key and its thumbprint",
          json.loads(shown_jwk) == record["device_key"] and shown_id == record["installation"]
          and shown_canonical == thumbprint_input(record["device_key"])
          and b64u(hashlib.sha256(shown_canonical.encode()).digest()) == shown_id)
    enroll_v = json.loads(out["The integrity verdict at enrollment, decoded"])
    check("Android: the enrollment verdict carries the hash of that binding",
          enroll_v["requestDetails"]["requestHash"]
          == b64u(hashlib.sha256(out["The enrollment binding string"].encode()).digest()))
    request_v = json.loads(out["The integrity verdict in the request, decoded"])
    check("Android: the request verdict carries the hash of the request binding",
          request_v["requestDetails"]["requestHash"]
          == b64u(hashlib.sha256(out["The request binding string"].encode()).digest()))
    check("Android: the request binding carries the TS-5-08 nonce",
          out["The request binding string"].startswith(a["nonce"] + "."))
    device_pub = webvh.public_key_from_multikey(
        webvh.multikey(keystore.load_or_create(ANDROID_DEVICE_KEY).public_key()))
    check("Android: the device key's signature verifies over the request binding",
          es256_raw_ok(device_pub, webvh._unb64u(
              out["The device key's signature over the request binding string"]),
              out["The request binding string"].encode()))
    check("Android: both KeyDescriptions carry the enrollment challenge",
          all(f'"{a["challenge"]}"' in out[t] for t in (
              "KeyDescription of the credential key, decoded",
              "KeyDescription of the device key, decoded")))
    check("Android: the signing digest agrees between KeyDescription and verdict",
          SIGNING_CERT_DIGEST.hex() in out["KeyDescription of the credential key, decoded"]
          and enroll_v["appIntegrity"]["certificateSha256Digest"] == [b64u(SIGNING_CERT_DIGEST)])
    idt = json.loads(out["The identity provider's token claims, decoded"])
    check("Android: the identity provider's token carries the enrollment challenge",
          idt["nonce"] == a["challenge"] and record["account"]["sub"] == idt["sub"])

    i = st["ios"]
    shown = json.loads(out["The App Attest attestation, as Wallet Backend Service checks it"])
    att = shown["attestation"]
    check("iOS: keyId is the SHA-256 of the device key's uncompressed point",
          att["keyId"] == i["key_id"] and bytes.fromhex(att["authData"]["credentialId"])
          == base64.b64decode(att["keyId"]))
    check("iOS: rpIdHash is the SHA-256 of the App ID",
          att["authData"]["rpIdHash"] == hashlib.sha256(APP_ID.encode()).hexdigest())
    check("iOS: clientDataHash is the hash of the enrollment binding",
          att["clientDataHash"] == b64u(hashlib.sha256(
              out["The iOS enrollment binding string"].encode()).digest())
          and out["The iOS enrollment binding string"]
          == f"{i['challenge']}.{thumbprint(shown['credential_key'])}")
    raw = bytes.fromhex(out["The App Attest assertion, in hex"].replace("\n", ""))
    assertion = cbor2.loads(raw)
    auth_data = assertion["authenticatorData"]
    client_hash = hashlib.sha256(out["The iOS request binding string"].encode()).digest()
    ios_pub = keystore.load_or_create(IOS_DEVICE_KEY).public_key()
    try:
        ios_pub.verify(assertion["signature"], hashlib.sha256(auth_data + client_hash).digest(),
                       ec.ECDSA(hashes.SHA256()))
        signed = True
    except InvalidSignature:
        signed = False
    check("iOS: the assertion verifies over SHA-256(authenticatorData || clientDataHash)", signed)
    check("iOS: the assertion's rpIdHash is the App ID's, its counter above zero",
          auth_data[:32].hex() == att["authData"]["rpIdHash"]
          and int.from_bytes(auth_data[33:37], "big") > 0)

    ios_record = json.loads(out["The installation record on iOS"])
    check("iOS: the record's installation is the thumbprint of the App Attest key, its counter the assertion's",
          ios_record["installation"] == thumbprint(ios_record["device_key"])
          and ios_record["sign_count"] == int.from_bytes(auth_data[33:37], "big")
          and ios_record["credential_key"] == shown["credential_key"])
    check("Android: the record's model is the one the KeyDescription attests",
          f'attestationIdModel      "{record["device_model"]}"' in out["KeyDescription of the credential key, decoded"])
    print(f"wrote {OUT_JSON.relative_to(REPO_ROOT)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
