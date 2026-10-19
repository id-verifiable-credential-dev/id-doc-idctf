"""Build and verify the proximity session of TS-3-02.

The session is the one TS-5-11 shows the DeviceResponse of: the same
DeviceEngagement, the same reader ephemeral key, the same SessionTranscript.
This script adds what travels around that response: the QR code, the
DeviceRequest whose ReaderAuth the Warung Bu Ani device signs over the
SessionTranscript and the ItemsRequest TS-5-06 publishes, the session keys,
the SessionEstablishment and the two SessionData messages. It also builds a
second engagement, over NFC with Static Handover, to show the other form the
Handover of a SessionTranscript takes.

Inputs, read at run time: ``build/artifacts/presentations.json`` (the
DeviceResponse and the SessionTranscript), the TS-5-06 page (the ItemsRequest
as sent), ``build/artifacts/verifier-device.pem`` and
``verifier-issuing-ca.pem``, and the keystore (the two ephemeral keys of each
engagement and the device key). ReaderAuth is RFC 6979 ES256 and the session
encryption is AES-256-GCM under a counter, so a re-run writes the same bytes.

Output ``build/artifacts/proximity.json``::

    {"blocks": {<block title>: <text of the fenced block>, ...},
     "documents": {"qr", "device_engagement_hex", "device_request_hex",
                   "session_establishment_hex", "session_data_hex",
                   "termination_hex", "sk_reader", "sk_device", "z_ab",
                   "nfc_handover_select_hex", "nfc_session_transcript_hex"}}

Run as ``.venv/bin/python scripts/artifacts/proximity.py`` after
``presentations.py``.
"""

from __future__ import annotations

import base64
import hashlib
import json
import sys
from pathlib import Path

import cbor2
from cbor2 import CBORTag
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

sys.path.insert(0, str(Path(__file__).resolve().parent))

import credentials as cr  # noqa: E402
import keystore  # noqa: E402
import presentations as pr  # noqa: E402
import webvh  # noqa: E402

ROOT = webvh.REPO_ROOT
ART = ROOT / "build" / "artifacts"
OUT = ART / "proximity.json"
TS_5_06 = ROOT / "docs" / "technical-specifications" / "registering-and-carrying-a-use-statement.md"

DEVICE_KEY = "verifier-device-warung-bu-ani"
NFC_EDEVICE_KEY = "proximity-edevice-nfc-1"
NFC_EREADER_KEY = "proximity-ereader-nfc-1"
# The UUID of the NFC engagement, for mdoc central client mode (RFC 4122 order).
NFC_UUID = bytes.fromhex("8d2b4a1fc63e4e0b9a7d51e2f0c4b693")
# The two UUIDs of an engagement offering both BLE modes (RFC 4122 order).
BOTH_UUIDS = {
    10: bytes.fromhex("c3a6e1f0b2d94f7e8a51d07e6b4f2c19"),
    11: bytes.fromhex("5f0e9b72a4c84d3a9e17b2c6d8f40a85"),
}

# ---- block titles
T_QR = "The QR code of the engagement"
T_ENG = "The DeviceEngagement, in CBOR diagnostic notation"
T_KEYS = "The session keys of that session"
T_REQ = "The DeviceRequest, in CBOR diagnostic notation"
T_EST_HEX = "The SessionEstablishment, as sent"
T_EST = "The SessionEstablishment, in CBOR diagnostic notation"
T_DATA_HEX = "The SessionData carrying the DeviceResponse, as sent"
T_END = "The SessionData that ends the session, as sent"
T_END_DIAG = "The SessionData that ends the session, in CBOR diagnostic notation"
T_ERR = "The SessionData of the two error statuses, as sent"
T_BOTH = "The BleOptions of an engagement offering both BLE modes, in CBOR diagnostic notation"
T_HS_HEX = "The Handover Select message of an NFC engagement, as the tag holds it"
T_HS = "The same Handover Select message, record by record"
T_NFC_ST = "The SessionTranscript of the NFC engagement"

READER_ID = bytes(8)
DEVICE_ID = bytes(7) + b"\x01"

enc, tag24, diag = pr.enc, pr.tag24, pr.diag
Embedded = cr.Embedded


# ------------------------------------------------------------------ crypto


def session_keys(reader_priv, device_pub, transcript_bytes: bytes) -> dict:
    """SKReader and SKDevice of ISO/IEC 18013-5 9.1.1.5."""
    z_ab = reader_priv.exchange(ec.ECDH(), device_pub)
    salt = hashlib.sha256(transcript_bytes).digest()

    def derive(info: str) -> bytes:
        return HKDF(hashes.SHA256(), 32, salt, info.encode()).derive(z_ab)

    return {"z_ab": z_ab, "salt": salt, "sk_reader": derive("SKReader"), "sk_device": derive("SKDevice")}


def seal(key: bytes, identifier: bytes, counter: int, plaintext: bytes) -> bytes:
    return AESGCM(key).encrypt(identifier + counter.to_bytes(4, "big"), plaintext, b"")


def open_(key: bytes, identifier: bytes, counter: int, ciphertext: bytes) -> bytes:
    return AESGCM(key).decrypt(identifier + counter.to_bytes(4, "big"), ciphertext, b"")


def public_of(cose: dict):
    return ec.EllipticCurvePublicNumbers(
        int.from_bytes(cose[-2], "big"), int.from_bytes(cose[-3], "big"), ec.SECP256R1()
    ).public_key()


# --------------------------------------------------------------------- NFC


def ndef_record(tnf: int, rtype: bytes, payload: bytes, rid: bytes = b"", mb=False, me=False) -> bytes:
    """One short NDEF record (NFC Forum NDEF 1.0)."""
    assert len(payload) < 256
    flags = tnf | 0x10 | (0x80 if mb else 0) | (0x40 if me else 0) | (0x08 if rid else 0)
    out = bytes([flags, len(rtype), len(payload)])
    if rid:
        out += bytes([len(rid)])
    return out + rtype + rid + payload


def handover_select(device_engagement: bytes) -> tuple[bytes, list[tuple[str, bytes]]]:
    """A Static Handover Select message offering BLE in mdoc central client mode."""
    ac = bytes([0x01, 0x01]) + b"0" + bytes([0x01, 0x04]) + b"mdoc"
    hs_payload = bytes([0x15]) + ndef_record(0x01, b"ac", ac, mb=True, me=True)
    oob = bytes([0x02, 0x1C, 0x01]) + bytes([0x11, 0x07]) + NFC_UUID[::-1]
    records = [
        ("Handover Select record", ndef_record(0x01, b"Hs", hs_payload, mb=True)),
        (
            "BLE carrier configuration record",
            ndef_record(0x02, b"application/vnd.bluetooth.le.oob", oob, rid=b"0"),
        ),
        (
            "DeviceEngagement record",
            ndef_record(0x04, b"iso.org:18013:deviceengagement", device_engagement, rid=b"mdoc", me=True),
        ),
    ]
    return b"".join(r for _, r in records), records


# ------------------------------------------------------------------- build


def items_request_bytes() -> bytes:
    """The ItemsRequest TS-5-06 publishes, byte for byte as the page carries it."""
    text = TS_5_06.read_text()
    marker = '``` { .text title="The same ItemsRequest, as CBOR"'
    body = text[text.index(marker) :].split("\n", 1)[1].split("```", 1)[0]
    return bytes.fromhex("".join(body.split()))


def jwt_diag(tree_text: str, jwt: str) -> str:
    """Show the statement as the TS-5-06 diagnostic does, a quoted text byte string."""
    return tree_text.replace("h'" + jwt.encode().hex() + "'", "'" + jwt + "'")


def build() -> dict:
    pres = json.loads((ART / "presentations.json").read_text())["documents"]
    transcript_bytes_plain = bytes.fromhex(pres["session_transcript_hex"])
    transcript = cbor2.loads(transcript_bytes_plain)
    transcript_bytes = enc(CBORTag(24, transcript_bytes_plain))
    engagement_bytes = transcript[0].value
    response_bytes = bytes.fromhex(pres["device_response_hex"])

    # engagement
    qr = "mdoc:" + base64.urlsafe_b64encode(engagement_bytes).decode().rstrip("=")

    # the request
    items_bytes = items_request_bytes()
    items = cbor2.loads(items_bytes)
    device_key = keystore.load_or_create(DEVICE_KEY)
    device_cert = x509.load_pem_x509_certificate((ART / "verifier-device.pem").read_bytes())
    issuing_cert = x509.load_pem_x509_certificate((ART / "verifier-issuing-ca.pem").read_bytes())
    der = lambda c: c.public_bytes(cr.serialization.Encoding.DER)  # noqa: E731
    protected = enc({1: -7})
    reader_authentication = ["ReaderAuthentication", transcript, CBORTag(24, items_bytes)]
    reader_authentication_bytes = enc(CBORTag(24, enc(reader_authentication)))
    sig_structure = enc(["Signature1", protected, b"", reader_authentication_bytes])
    signature = cr.es256_raw(device_key, sig_structure)
    reader_auth = [protected, {33: [der(device_cert), der(issuing_cert)]}, None, signature]
    device_request = {
        "version": "1.0",
        "docRequests": [{"itemsRequest": CBORTag(24, items_bytes), "readerAuth": reader_auth}],
    }
    device_request_bytes = enc(device_request)

    # the session
    reader_priv = keystore.load_or_create(pr.EREADER_KEY)
    device_pub = public_of(pr.ENG_EPHEMERAL)
    keys = session_keys(reader_priv, device_pub, transcript_bytes)
    establishment = {
        "eReaderKey": transcript[1],
        "data": seal(keys["sk_reader"], READER_ID, 1, device_request_bytes),
    }
    establishment_bytes = enc(establishment)
    session_data = {"data": seal(keys["sk_device"], DEVICE_ID, 1, response_bytes)}
    session_data_bytes = enc(session_data)
    termination = {"status": 20}
    termination_bytes = enc(termination)

    # the NFC engagement: a second session, shown up to its SessionTranscript
    nfc_edevice = pr.cose_key(NFC_EDEVICE_KEY)
    nfc_engagement = {0: "1.0", 1: [1, tag24(nfc_edevice)]}
    nfc_engagement_bytes = enc(nfc_engagement)
    hs_bytes, hs_records = handover_select(nfc_engagement_bytes)
    nfc_transcript = [CBORTag(24, nfc_engagement_bytes), tag24(pr.cose_key(NFC_EREADER_KEY)), [hs_bytes, None]]
    nfc_transcript_bytes = enc(nfc_transcript)

    # diagnostic forms
    jwt = items["requestInfo"]["idUseStatement"].decode()
    request_tree = {
        "version": "1.0",
        "docRequests": [
            {
                "itemsRequest": CBORTag(24, Embedded(items)),
                "readerAuth": [
                    protected,
                    {33: [der(device_cert), der(issuing_cert)]},
                    None,
                    signature,
                ],
            }
        ],
    }
    engagement_tree = cbor2.loads(engagement_bytes)
    engagement_tree[1] = [1, CBORTag(24, Embedded(cbor2.loads(engagement_tree[1][1].value)))]
    establishment_tree = {
        "eReaderKey": CBORTag(24, Embedded(cbor2.loads(transcript[1].value))),
        "data": establishment["data"],
    }
    nfc_transcript_tree = [
        CBORTag(24, Embedded({0: "1.0", 1: [1, CBORTag(24, Embedded(nfc_edevice))]})),
        CBORTag(24, Embedded(pr.cose_key(NFC_EREADER_KEY))),
        [hs_bytes, None],
    ]
    keys_text = "\n".join(
        [
            "ZAB       " + keys["z_ab"].hex(),
            "salt      " + keys["salt"].hex(),
            "SKReader  " + keys["sk_reader"].hex(),
            "SKDevice  " + keys["sk_device"].hex(),
        ]
    )
    hs_text = "\n".join(f"{name}\n{cr.wrap(raw.hex(), 64)}" for name, raw in hs_records)

    return {
        "transcript": transcript,
        "transcript_bytes": transcript_bytes,
        "engagement_bytes": engagement_bytes,
        "qr": qr,
        "items_bytes": items_bytes,
        "items": items,
        "device_cert": device_cert,
        "issuing_cert": issuing_cert,
        "reader_authentication_bytes": reader_authentication_bytes,
        "signature": signature,
        "device_request": device_request,
        "device_request_bytes": device_request_bytes,
        "keys": keys,
        "establishment_bytes": establishment_bytes,
        "session_data_bytes": session_data_bytes,
        "termination_bytes": termination_bytes,
        "response_bytes": response_bytes,
        "nfc_engagement_bytes": nfc_engagement_bytes,
        "hs_bytes": hs_bytes,
        "nfc_transcript_bytes": nfc_transcript_bytes,
        "blocks": {
            T_QR: qr,
            T_ENG: diag(engagement_tree),
            T_KEYS: keys_text,
            T_REQ: jwt_diag(diag(request_tree), jwt),
            T_EST_HEX: cr.wrap(establishment_bytes.hex()),
            T_EST: diag(establishment_tree),
            T_DATA_HEX: cr.wrap(session_data_bytes.hex()),
            T_END: termination_bytes.hex(),
            T_END_DIAG: diag(termination),
            T_ERR: "\n".join(enc({"status": code}).hex() for code in (10, 11)),
            T_BOTH: diag({0: True, 1: True, **BOTH_UUIDS}),
            T_HS_HEX: cr.wrap(hs_bytes.hex()),
            T_HS: hs_text,
            T_NFC_ST: diag(nfc_transcript_tree),
        },
    }


# ------------------------------------------------------------------ verify


def verify(b: dict) -> int:
    failures = 0

    def report(ok: bool, text: str):
        nonlocal failures
        print(("OK   " if ok else "FAIL ") + text)
        failures += 0 if ok else 1

    # engagement
    raw = base64.urlsafe_b64decode(b["qr"][5:] + "=" * (-len(b["qr"][5:]) % 4))
    report(b["qr"].startswith("mdoc:") and raw == b["engagement_bytes"], "QR code is mdoc: and the DeviceEngagement in base64url without padding")
    eng = cbor2.loads(b["engagement_bytes"])
    edevice = cbor2.loads(eng[1][1].value)
    report(
        eng[0] == "1.0" and eng[1][0] == 1 and edevice[-1] == 1 and 3 not in eng and eng[2] == [[2, 1, pr.ENG_RETRIEVAL]],
        "DeviceEngagement: version 1.0, cipher suite 1, P-256, BLE central client mode only, no server retrieval",
    )

    # the wallet side rebuilds the keys from its own private key
    device_priv = keystore.load_or_create(pr.EDEVICE_KEY)
    reader_pub = public_of(cbor2.loads(b["transcript"][1].value))
    z_wallet = device_priv.exchange(ec.ECDH(), reader_pub)
    report(z_wallet == b["keys"]["z_ab"], "ECDH from either side gives the same ZAB")
    report(
        b["keys"]["salt"] == hashlib.sha256(b["transcript_bytes"]).digest()
        and b["transcript_bytes"][:2] == bytes.fromhex("d818"),
        "salt is SHA-256 of the SessionTranscriptBytes, tag 24 over the transcript",
    )
    est = cbor2.loads(b["establishment_bytes"])
    request = open_(b["keys"]["sk_reader"], READER_ID, 1, est["data"])
    report(
        request == b["device_request_bytes"] and est["eReaderKey"] == b["transcript"][1],
        "SessionEstablishment decrypts under SKReader, counter 1, to the DeviceRequest; eReaderKey is the transcript's",
    )
    data = cbor2.loads(b["session_data_bytes"])
    report(
        open_(b["keys"]["sk_device"], DEVICE_ID, 1, data["data"]) == b["response_bytes"] and set(data) == {"data"},
        "SessionData decrypts under SKDevice, counter 1, to the DeviceResponse of TS-5-11",
    )
    report(cbor2.loads(b["termination_bytes"]) == {"status": 20} and b["termination_bytes"].hex() == "a16673746174757314", "the last SessionData carries status 20 and no data")

    # the request
    req = cbor2.loads(request)
    doc = req["docRequests"][0]
    report(req["version"] == "1.0" and len(req["docRequests"]) == 1, "DeviceRequest version 1.0 with one DocRequest")
    report(doc["itemsRequest"].value == b["items_bytes"], "itemsRequest is the TS-5-06 ItemsRequest, byte for byte")
    items = cbor2.loads(doc["itemsRequest"].value)
    report(
        all(v is False for ns in items["nameSpaces"].values() for v in ns.values()),
        "every IntentToRetain is false",
    )
    prot, unprot, payload, sig = doc["readerAuth"]
    chain = [x509.load_der_x509_certificate(c) for c in unprot[33]]
    report(cbor2.loads(prot) == {1: -7} and payload is None and set(unprot) == {33}, "ReaderAuth: alg -7 alone protected, x5chain alone unprotected, payload detached")
    report(
        [c.subject for c in chain] == [b["device_cert"].subject, b["issuing_cert"].subject]
        and chain[0].issuer == chain[1].subject
        and chain[1].issuer != chain[1].subject,
        "x5chain is the Verifier Device Certificate then the Verifier Issuing CA, without the root",
    )
    ra = enc(CBORTag(24, enc(["ReaderAuthentication", b["transcript"], doc["itemsRequest"]])))
    report(
        cr.es256_check(chain[0].public_key(), sig, enc(["Signature1", prot, b"", ra])),
        "ReaderAuth verifies under the device certificate over ReaderAuthentication with the wallet's own transcript",
    )
    report(
        chain[0].public_key().public_numbers() == keystore.load_or_create(DEVICE_KEY).public_key().public_numbers(),
        "the device certificate certifies the Warung Bu Ani device key",
    )

    # NFC
    hs = b["hs_bytes"]
    report(hs[0] == 0x91 and hs[3:5] == b"Hs" and hs[5] == 0x15, "Handover Select record: MB, short, well-known Hs, version 1.5")
    report(b"iso.org:18013:deviceengagement" in hs and b["nfc_engagement_bytes"] in hs, "the DeviceEngagement rides in the Handover Select message")
    nfc_eng = cbor2.loads(b["nfc_engagement_bytes"])
    report(2 not in nfc_eng and 3 not in nfc_eng, "the NFC DeviceEngagement carries no retrieval method")
    oob = bytes([0x02, 0x1C, 0x01, 0x11, 0x07]) + NFC_UUID[::-1]
    report(oob in hs, "the BLE carrier names LE Role central only and the UUID little-endian")
    st = cbor2.loads(b["nfc_transcript_bytes"])
    report(st[2] == [hs, None] and st[0].value == b["nfc_engagement_bytes"], "the NFC SessionTranscript ends in [Handover Select, null]")
    return failures


def to_json(b: dict) -> dict:
    return {
        "blocks": b["blocks"],
        "documents": {
            "qr": b["qr"],
            "device_engagement_hex": b["engagement_bytes"].hex(),
            "device_request_hex": b["device_request_bytes"].hex(),
            "session_establishment_hex": b["establishment_bytes"].hex(),
            "session_data_hex": b["session_data_bytes"].hex(),
            "termination_hex": b["termination_bytes"].hex(),
            "z_ab": b["keys"]["z_ab"].hex(),
            "sk_reader": b["keys"]["sk_reader"].hex(),
            "sk_device": b["keys"]["sk_device"].hex(),
            "nfc_handover_select_hex": b["hs_bytes"].hex(),
            "nfc_session_transcript_hex": b["nfc_transcript_bytes"].hex(),
        },
    }


def main() -> int:
    b = build()
    OUT.write_text(json.dumps(to_json(b), indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    failures = verify(b)
    print("all checks passed" if not failures else f"{failures} check(s) FAILED")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
