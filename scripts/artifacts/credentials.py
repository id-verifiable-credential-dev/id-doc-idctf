"""Build and verify the credentials of TS-5-10: a Kartu ASN as an SD-JWT VC
(issued by BKN under its ``issuance-jose`` key) and a KTP Digital as an mdoc
(signed by a Document Signer Certificate's key).

Claim values, salts, ``random`` values, ``digestID`` values, times and status
pointers are the ones the page already carries; the keys, the issuer
identifier, the signatures and everything derived from them are new. Every key
comes from the keystore (``keystore.py``) and every identifier from
``build/artifacts/webvh.json``.

The page's mdoc is a KTP Digital, a different credential from the Kartu ASN
(it was never "the same credential as an mdoc"); the page's claim values stand.

Signing is deterministic (RFC 6979 ECDSA), so a re-run writes the same bytes.

Document Signer key: ``build/artifacts/x509.json`` is read when present. The
reader looks for a dict whose keystore name holds ``document-signer`` and that
carries a certificate (``der_hex``, ``der``, ``certificate_der_hex``,
``pem`` or ``certificate``). When the file is absent the key
``issuer-document-signer-1`` signs and ``x5chain`` carries the certificate now
on the page, which does not hold that key (reported as WARN).

Output ``build/artifacts/credentials.json``::

    {
      "blocks": {<block title>: <text of the fenced block>, ...},   # 7 titles
      "holder": {"keystore", "did_key", "multikey",
                 "jwk": {kty, crv, x, y},
                 "cose": {"1": 2, "-1": 1, "-2": <x hex>, "-3": <y hex>}},
      "sd_jwt": {"issuer_did", "kid", "keystore", "header", "payload",
                 "jwt",                       # issuer-signed JWT, no disclosures
                 "disclosures": [{"disclosure", "array", "digest"}, ...],
                 "serialization"},            # jwt~d1~...~d8~  (no KB-JWT)
      "mdoc": {"doc_type", "namespace", "issuer_signed_hex",
               "items": [{"digestID", "random", "identifier", "value",
                          "tagged_hex", "digest"}, ...],   # tag 24 bytes, hex
               "mso_hex",                  # the MSO, plain CBOR
               "mso_tagged_hex",           # tag 24 over it: the COSE payload
               "protected_hex", "x5chain_hex", "signature_hex",
               "signer": {"keystore", "source", "certificate_matches_key"}}
    }

Run as ``.venv/bin/python scripts/artifacts/credentials.py``.
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import cbor2
from cbor2 import CBORTag
from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import (
    decode_dss_signature,
    encode_dss_signature,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))

import keystore  # noqa: E402
import webvh  # noqa: E402

ROOT = webvh.REPO_ROOT
WEBVH = ROOT / "build" / "artifacts" / "webvh.json"
X509 = ROOT / "build" / "artifacts" / "x509.json"
OUT = ROOT / "build" / "artifacts" / "credentials.json"
PAGE = webvh.TS_DIR / "issuing-a-credential-in-sd-jwt-vc-mdoc-and-ldp-vc.md"

HOLDER_KEY = "holder-credential-1"
FALLBACK_SIGNER = "issuer-document-signer-1"

ASN_VCT = "id.idctf.kartu-asn.1"
ASN_STATUS = {"idx": 481920, "uri": "https://bkn.go.id/status/kartu-asn-1"}
ASN_NBF = ASN_IAT = 1792216810
ASN_EXP = 1823752810

KTP_DOCTYPE = "id.idctf.ktp.1"
KTP_STATUS = {"idx": 481920, "uri": "https://dukcapil.go.id/status/ktp-7"}
KTP_SIGNED = KTP_FROM = "2026-10-17T06:00:10Z"
KTP_UNTIL = "2027-01-15T06:00:10Z"

T_ASN = "A Kartu ASN in SD-JWT VC, as issued"
T_HEADER = "SD-JWT VC header"
T_CLAIMS = "SD-JWT VC claims"
T_DISC = "The eight disclosures, with their decoded arrays"
T_MDOC = "The mdoc IssuerSigned, as issued"
T_DIAG = "The mdoc IssuerSigned, in CBOR diagnostic notation"
T_MSO = "The Mobile Security Object"

# (salt, claim name, value) in the order the issuer put them in, which is not the order of _sd.
ASN_CLAIMS = [
    ('wIuMsehA35PJtEMrS4noCQ', 'nama', 'Budi Santoso Wicaksono'),
    ('uo_XY7iQt-ddLfN2MVLdGg', 'nip', '198703152010011002'),
    ('LJ0fbNx7vpOhxRZBV3a50w', 'golongan', 'III/c'),
    ('VNdj_lhSM1MpVNKL9mG14w', 'status_kepegawaian', 'PNS'),
    ('peUbAhAvVbRCavJ1nnf6dA', 'jabatan', 'Analis Kebijakan Ahli Muda'),
    ('M5o5JvrSFixvoR3Kei5U1g', 'unit_kerja', 'Direktorat Jabatan ASN'),
    ('RoZ8Hti2OIVBx4yMwt4RFQ', 'instansi', 'Badan Kepegawaian Negara'),
    ('MkADHOopqIHbolBHHuA6cg', 'foto', 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/wAALCAABAAEBAREA/8QAFAABAAAAAAAAAAAAAAAAAAAACf/EABQQAQAAAAAAAAAAAAAAAAAAAAD/2gAIAQEAAD8AKp//2Q=='),
]

# (digestID, random hex, elementIdentifier, value); ("full-date", text) is tag 1004.
KTP_ITEMS = [
    (1784420171, '81f5f22818a83bdf839e4565ea459056', 'nik', '3174015201950003'),
    (1935886537, '0dbbb070f43fe1dcb3145b8cf582d776', 'nama', 'Rina Kartika Sari'),
    (1833679872, '6f6e11c8610fecb6bb143c3e564907b8', 'tempat_lahir', 'Jakarta'),
    (1512697854, 'e15336da27bfcb551fdeaddd18746969', 'tanggal_lahir', ('full-date', '1995-01-12')),
    (1904627313, 'e22dfff74e8aa035175b4e2a29e89789', 'usia_di_atas_17', True),
    (1539745747, '713ac10c6f40d4b9d249c9ad2c9e1f93', 'jenis_kelamin', 'PEREMPUAN'),
    (1039139218, 'ce252487a3ab5767f7b5d859fd370a3e', 'golongan_darah', 'B'),
    (2042373709, '75e8c8d784a3f81d1e5fb8b96ca4ab1b', 'alamat', 'Jalan Kenanga Nomor 12'),
    (1695740793, '2083912dcc83d1282059af664b9cb8fe', 'rt_rw', '004/007'),
    (514751178, '6a1117b6b2c20a09323b1020e1438baa', 'kelurahan_desa', 'Gondangdia'),
    (1903436892, 'f7951c2e684abe9b11effe558bf7ae8a', 'kecamatan', 'Menteng'),
    (1244226941, 'e49fd723c6cf6e449201a60231f7af9e', 'kabupaten_kota', 'Jakarta Pusat'),
    (706034575, '2f85eb4474086989e829791131c959a8', 'provinsi', 'DKI Jakarta'),
    (1061046475, '99c6154c0c41c3b169d3d9e464537926', 'agama', 'ISLAM'),
    (1115820700, '792870492760192a7a1c40431634d885', 'status_perkawinan', 'BELUM KAWIN'),
    (2122426582, '79138313426355d01a6a1c60752e9cd1', 'pekerjaan', 'KARYAWAN SWASTA'),
    (810633413, 'f9646611eaa18ea5f59423437d261105', 'kewarganegaraan', 'WNI'),
    (1777001014, '32bef7dd836dd6ee3b168b32754dffec', 'tempat_dikeluarkan', 'JAKARTA PUSAT'),
    (1850378055, '8f60d442ca76eb68ecbea4b684624423', 'issuance_date', ('full-date', '2020-01-28')),
    (2064862523, '17dd402ae5505d63635fd23944d9ac4c', 'foto', 'FOTO'),
]

KTP_FOTO = bytes.fromhex(
    'ffd8ffe000104a46494600010101006000600000ffdb00430008060607060508'
    '0707070909080a0c140d0c0b0b0c1912130f141d1a1f1e1d1a1c1c20242e2720'
    '222c231c1c2837292c30313434341f27393d38323c2e333432ffc0000b080001'
    '000101011100ffc40014000100000000000000000000000000000009ffc40014'
    '100100000000000000000000000000000000ffda0008010100003f002a9fffd9'
)


# ---------------------------------------------------------------- helpers


def b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def unb64u(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def compact(obj) -> bytes:
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode()


def wrap(text: str, width: int = 76) -> str:
    return "\n".join(text[i : i + width] for i in range(0, len(text), width))


def es256_raw(key, data: bytes) -> bytes:
    der = key.sign(data, ec.ECDSA(hashes.SHA256(), deterministic_signing=True))
    r, s = decode_dss_signature(der)
    return r.to_bytes(32, "big") + s.to_bytes(32, "big")


def es256_check(public_key, signature: bytes, data: bytes) -> bool:
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


def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def xy(public_key) -> tuple[bytes, bytes]:
    n = public_key.public_numbers()
    return n.x.to_bytes(32, "big"), n.y.to_bytes(32, "big")


# ----------------------------------------------- CBOR diagnostic notation


class Embedded:
    """A structure that travels as a byte string: ``<< ... >>`` in diagnostics."""

    def __init__(self, value):
        self.value = value


def diag(value, indent: int = 0) -> str:
    pad = " " * indent
    if isinstance(value, dict):
        ordered = sorted(value.items(), key=lambda kv: (len(cbor2.dumps(kv[0])), cbor2.dumps(kv[0])))
        rows = [f"{pad}  {diag(k)}: {diag(v, indent + 2)}" for k, v in ordered]
        return "{\n" + ",\n".join(rows) + f"\n{pad}}}"
    if isinstance(value, list):
        rows = [f"{pad}  {diag(v, indent + 2)}" for v in value]
        return "[\n" + ",\n".join(rows) + f"\n{pad}]"
    if isinstance(value, CBORTag):
        if isinstance(value.value, Embedded):
            return f"{value.tag}(<< {diag(value.value.value, indent)} >>)"
        return f"{value.tag}({diag(value.value, indent)})"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, bytes):
        return "h'" + value.hex() + "'"
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, int):
        return str(value)
    raise ValueError(f"no diagnostic form for {type(value)}")


def parse_diag(text: str):
    """Parse the subset of diagnostic notation ``diag`` writes, back to values."""
    pos = 0

    def skip():
        nonlocal pos
        while pos < len(text) and text[pos] in " \n\t":
            pos += 1

    def value():
        nonlocal pos
        skip()
        c = text[pos]
        if text.startswith("<<", pos):
            pos += 2
            inner = value()
            skip()
            assert text.startswith(">>", pos)
            pos += 2
            return cbor2.dumps(inner, canonical=True)
        if c == "{":
            pos += 1
            out = {}
            while True:
                skip()
                if text[pos] == "}":
                    pos += 1
                    return out
                k = value()
                skip()
                assert text[pos] == ":"
                pos += 1
                out[k] = value()
                skip()
                if text[pos] == ",":
                    pos += 1
        if c == "[":
            pos += 1
            out = []
            while True:
                skip()
                if text[pos] == "]":
                    pos += 1
                    return out
                out.append(value())
                skip()
                if text[pos] == ",":
                    pos += 1
        if c == '"':
            end = pos + 1
            while text[end] != '"':
                end += 2 if text[end] == "\\" else 1
            s = json.loads(text[pos : end + 1])
            pos = end + 1
            return s
        if text.startswith("h'", pos):
            end = text.index("'", pos + 2)
            b = bytes.fromhex(text[pos + 2 : end])
            pos = end + 1
            return b
        if text.startswith("true", pos):
            pos += 4
            return True
        if text.startswith("false", pos):
            pos += 5
            return False
        m = re.compile(r"-?\d+").match(text, pos)
        assert m, f"cannot parse at {pos}: {text[pos:pos+20]!r}"
        pos = m.end()
        n = int(m.group())
        if pos < len(text) and text[pos] == "(":
            pos += 1
            inner = value()
            skip()
            assert text[pos] == ")"
            pos += 1
            return CBORTag(n, inner)
        return n

    out = value()
    skip()
    assert pos == len(text), "trailing text in diagnostic notation"
    return out


# ------------------------------------------------------------------ keys


def entity(name: str) -> dict:
    return json.loads(WEBVH.read_text())["entities"][name]


def holder() -> dict:
    key = keystore.load_or_create(HOLDER_KEY)
    x, y = xy(key.public_key())
    mk = webvh.multikey(key.public_key())
    return {
        "key": key,
        "keystore": HOLDER_KEY,
        "multikey": mk,
        "did_key": webvh.did_key(mk),
        "jwk": {"kty": "EC", "crv": "P-256", "x": b64u(x), "y": b64u(y)},
        "cose": {"1": 2, "-1": 1, "-2": x.hex(), "-3": y.hex()},
        "x": x,
        "y": y,
    }


def page_certificate() -> bytes:
    """DER of the certificate now in label 33 on the page (fallback only)."""
    text = PAGE.read_text()
    m = re.search(
        r'title="The mdoc IssuerSigned, as issued"[^\n]*\n(.*?)\n```', text, re.S
    )
    signed = cbor2.loads(bytes.fromhex(m.group(1).replace("\n", "")))
    return signed["issuerAuth"][1][33]


def signer() -> dict:
    if X509.exists():
        data = json.loads(X509.read_text())
        rec = data["certificates"]["document-signer"]
        der = x509.load_pem_x509_certificate(rec["pem"].encode()).public_bytes(
            serialization.Encoding.DER
        )
        out = _signer(data["keys"]["document_signer"], der, "x509.json")
        out["root"] = x509.load_pem_x509_certificate(
            data["certificates"]["issuer-root-ca"]["pem"].encode()
        )
        return out
    return _signer(FALLBACK_SIGNER, page_certificate(), "fallback key; certificate from the page")


def _signer(name: str, der: bytes, source: str) -> dict:
    key = keystore.load_or_create(name)
    cert = x509.load_der_x509_certificate(der)
    pub = lambda k: k.public_bytes(  # noqa: E731
        serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint
    )
    return {
        "key": key,
        "keystore": name,
        "der": der,
        "cert": cert,
        "source": source,
        "matches": pub(cert.public_key()) == pub(key.public_key()),
        "root": None,
    }


# ------------------------------------------------------------------- SD-JWT


def build_sd_jwt(h: dict) -> dict:
    ent = entity("bkn")
    kid = ent["keys"]["issuance-jose-1"]["kid"]
    key = keystore.load_or_create(ent["keys"]["issuance-jose-1"]["keystore"])
    disclosures = []
    for salt, name, value in ASN_CLAIMS:
        array = [salt, name, value]
        disc = b64u(compact(array))
        disclosures.append(
            {
                "disclosure": disc,
                "array": array,
                "digest": b64u(sha256(disc.encode("ascii"))),
            }
        )
    header = {"typ": "dc+sd-jwt", "alg": "ES256", "kid": kid}
    payload = {
        "iss": ent["did"],
        "vct": ASN_VCT,
        "cnf": {"jwk": h["jwk"]},
        "_sd_alg": "sha-256",
        "_sd": sorted(d["digest"] for d in disclosures),
        "status": {"status_list": ASN_STATUS},
        "nbf": ASN_NBF,
        "iat": ASN_IAT,
        "exp": ASN_EXP,
    }
    signing_input = b64u(compact(header)) + "." + b64u(compact(payload))
    jwt = signing_input + "." + b64u(es256_raw(key, signing_input.encode()))
    serialization_ = jwt + "~" + "".join(d["disclosure"] + "~" for d in disclosures)
    return {
        "issuer_did": ent["did"],
        "kid": kid,
        "keystore": ent["keys"]["issuance-jose-1"]["keystore"],
        "header": header,
        "payload": payload,
        "jwt": jwt,
        "disclosures": disclosures,
        "serialization": serialization_,
    }


def sd_jwt_blocks(sd: dict) -> dict:
    disc_text = "\n".join(
        f"~{d['disclosure']}\n  "
        + json.dumps(d["array"], separators=(",", ":"), ensure_ascii=False)
        for d in sd["disclosures"]
    )
    return {
        T_ASN: wrap(sd["serialization"]),
        T_HEADER: json.dumps(sd["header"], indent=2, ensure_ascii=False),
        T_CLAIMS: json.dumps(sd["payload"], indent=2, ensure_ascii=False),
        T_DISC: disc_text,
    }


# --------------------------------------------------------------------- mdoc


def item_struct(spec):
    digest_id, random_hex, ident, value = spec
    if isinstance(value, tuple):
        value = CBORTag(1004, value[1])
    elif value == "FOTO":
        value = KTP_FOTO
    return {
        "random": bytes.fromhex(random_hex),
        "digestID": digest_id,
        "elementValue": value,
        "elementIdentifier": ident,
    }


def build_mdoc(h: dict, sg: dict) -> dict:
    structs = [item_struct(s) for s in KTP_ITEMS]
    tagged = [cbor2.dumps(CBORTag(24, cbor2.dumps(s, canonical=True)), canonical=True)
              for s in structs]
    digests = {s["digestID"]: sha256(t) for s, t in zip(structs, tagged)}
    mso = {
        "version": "1.0",
        "digestAlgorithm": "SHA-256",
        "valueDigests": {KTP_DOCTYPE: digests},
        "deviceKeyInfo": {
            "deviceKey": {1: 2, -1: 1, -2: h["x"], -3: h["y"]}
        },
        "docType": KTP_DOCTYPE,
        "validityInfo": {
            "signed": CBORTag(0, KTP_SIGNED),
            "validFrom": CBORTag(0, KTP_FROM),
            "validUntil": CBORTag(0, KTP_UNTIL),
        },
        "status": {"status_list": KTP_STATUS},
    }
    mso_bytes = cbor2.dumps(mso, canonical=True)
    payload = cbor2.dumps(CBORTag(24, mso_bytes), canonical=True)
    protected = cbor2.dumps({1: -7}, canonical=True)
    sig_structure = cbor2.dumps(["Signature1", protected, b"", payload])
    signature = es256_raw(sg["key"], sig_structure)
    issuer_auth = [protected, {33: sg["der"]}, payload, signature]
    namespaces = {KTP_DOCTYPE: [cbor2.loads(t) for t in tagged]}
    signed_struct = {"issuerAuth": issuer_auth, "nameSpaces": namespaces}
    issuer_signed = cbor2.dumps(signed_struct, canonical=True)

    # The diagnostic trees: same data, with each item shown decoded.
    diag_items = [CBORTag(24, Embedded(s)) for s in structs]
    diag_tree = {
        "issuerAuth": [protected, {33: sg["der"]}, payload, signature],
        "nameSpaces": {KTP_DOCTYPE: diag_items},
    }
    return {
        "mso": mso,
        "mso_bytes": mso_bytes,
        "payload": payload,
        "protected": protected,
        "signature": signature,
        "structs": structs,
        "tagged": tagged,
        "digests": digests,
        "issuer_signed": issuer_signed,
        "diag_tree": diag_tree,
        "signer": sg,
    }


def mdoc_blocks(md: dict) -> dict:
    return {
        T_MDOC: wrap(md["issuer_signed"].hex()),
        T_DIAG: diag(md["diag_tree"]),
        T_MSO: diag(md["mso"]),
    }


# ------------------------------------------------------------------- output


def build() -> dict:
    h = holder()
    sd = build_sd_jwt(h)
    sg = signer()
    md = build_mdoc(h, sg)
    blocks = {**sd_jwt_blocks(sd), **mdoc_blocks(md)}
    return {"h": h, "sd": sd, "md": md, "blocks": blocks}


def to_json(b: dict) -> dict:
    h, sd, md = b["h"], b["sd"], b["md"]
    items = []
    for spec, s, t in zip(KTP_ITEMS, md["structs"], md["tagged"]):
        v = s["elementValue"]
        items.append(
            {
                "digestID": s["digestID"],
                "random": s["random"].hex(),
                "identifier": s["elementIdentifier"],
                "value": v.value if isinstance(v, CBORTag) else
                (v.hex() if isinstance(v, bytes) else v),
                "value_type": "full-date" if isinstance(v, CBORTag) else
                ("bstr" if isinstance(v, bytes) else type(v).__name__),
                "tagged_hex": t.hex(),
                "digest": md["digests"][s["digestID"]].hex(),
            }
        )
    sg = md["signer"]
    return {
        "blocks": b["blocks"],
        "holder": {k: h[k] for k in ("keystore", "did_key", "multikey", "jwk", "cose")},
        "sd_jwt": {k: sd[k] for k in
                   ("issuer_did", "kid", "keystore", "header", "payload", "jwt",
                    "disclosures", "serialization")},
        "mdoc": {
            "doc_type": KTP_DOCTYPE,
            "namespace": KTP_DOCTYPE,
            "issuer_signed_hex": md["issuer_signed"].hex(),
            "items": items,
            "mso_hex": md["mso_bytes"].hex(),
            "mso_tagged_hex": md["payload"].hex(),
            "protected_hex": md["protected"].hex(),
            "x5chain_hex": sg["der"].hex(),
            "signature_hex": md["signature"].hex(),
            "signer": {
                "keystore": sg["keystore"],
                "source": sg["source"],
                "certificate_matches_key": sg["matches"],
            },
        },
    }


# ------------------------------------------------------------------- checks


def verify(b: dict) -> int:
    failures = 0

    def report(ok: bool, text: str, warn: bool = False):
        nonlocal failures
        if ok:
            print(f"OK   {text}")
        elif warn:
            print(f"WARN {text}")
        else:
            print(f"FAIL {text}")
            failures += 1

    h, sd, md = b["h"], b["sd"], b["md"]
    ent = entity("bkn")

    # SD-JWT VC signature under the key the BKN DID Document publishes
    doc = ent["entries"][-1]["state"]
    vm = next(v for v in doc["verificationMethod"] if v["id"] == sd["kid"])
    pub = webvh.public_key_from_multikey(vm["publicKeyMultibase"])
    head_b, body_b, sig_b = sd["jwt"].split(".")
    report(
        es256_check(pub, unb64u(sig_b), f"{head_b}.{body_b}".encode())
        and sd["kid"] in doc["assertionMethod"] and sd["header"]["kid"] == sd["kid"],
        f"SD-JWT VC signature verifies under {sd['kid']}",
    )
    report(
        json.loads(unb64u(head_b)) == sd["header"]
        and list(json.loads(unb64u(head_b))) == ["typ", "alg", "kid"]
        and json.loads(unb64u(body_b)) == sd["payload"]
        and sd["payload"]["iss"] == ent["did"],
        "SD-JWT VC header carries typ, alg, kid only; claims decode to the shown block",
    )
    shown = json.loads(b["blocks"][T_CLAIMS])
    report(shown == json.loads(unb64u(body_b))
           and json.loads(b["blocks"][T_HEADER]) == json.loads(unb64u(head_b)),
           "header and claims blocks equal the decoded token")

    # disclosures
    in_sd = sd["payload"]["_sd"]
    digests = [hashlib.sha256(d["disclosure"].encode("ascii")).digest() for d in sd["disclosures"]]
    report(
        all(b64u(x) in in_sd for x in digests)
        and len(in_sd) == len(set(in_sd)) == len(sd["disclosures"]) == 8
        and in_sd == sorted(in_sd),
        "all 8 disclosure digests are in _sd, which is sorted, unique, with no decoy",
    )
    report(
        all(json.loads(unb64u(d["disclosure"])) == d["array"] and len(d["array"]) == 3
            and len(unb64u(d["array"][0])) >= 16 for d in sd["disclosures"])
        and len({d["array"][0] for d in sd["disclosures"]}) == 8,
        "disclosures decode to [salt, name, value]; salts are 16 bytes and distinct",
    )
    parts = sd["serialization"].split("~")
    report(parts[0] == sd["jwt"] and parts[-1] == ""
           and parts[1:-1] == [d["disclosure"] for d in sd["disclosures"]],
           "serialization is JWT, every disclosure, a final tilde with no Key Binding JWT")
    report(sd["payload"]["cnf"]["jwk"] == h["jwk"] and list(h["jwk"]) == ["kty", "crv", "x", "y"],
           f"cnf.jwk is the keystore key {HOLDER_KEY}")

    # mdoc
    hex_text = b["blocks"][T_MDOC].replace("\n", "")
    raw = bytes.fromhex(hex_text)
    signed = cbor2.loads(raw)
    protected, unprotected, payload, signature = signed["issuerAuth"]
    sg = md["signer"]
    sig_structure = cbor2.dumps(["Signature1", protected, b"", payload])
    report(
        es256_check(sg["key"].public_key(), signature, sig_structure)
        and cbor2.loads(protected) == {1: -7} and list(unprotected) == [33],
        f"mdoc COSE_Sign1 verifies under keystore key {sg['keystore']}; "
        "protected header is alg only, x5chain is label 33 in the unprotected header",
    )
    report(sg["matches"],
           f"x5chain certificate holds exactly the public key that signed the MSO ({sg['source']})", warn=True)
    cert = sg["cert"]
    root = sg["root"]
    if root is not None:
        try:
            root.public_key().verify(
                cert.signature, cert.tbs_certificate_bytes,
                ec.ECDSA(cert.signature_hash_algorithm))
            chained = cert.issuer == root.subject
        except InvalidSignature:
            chained = False
        report(chained, "x5chain certificate chains to the Issuer Root CA in x509.json")
        report(unprotected[33] == sg["der"]
               and cbor2.loads(raw)["issuerAuth"][1][33] == cert.public_bytes(
                   serialization.Encoding.DER),
               "label 33 holds exactly the Document Signer Certificate of x509.json")
    signed_at = datetime.fromisoformat(KTP_SIGNED.replace("Z", "+00:00"))
    report(cert.not_valid_before_utc <= signed_at <= cert.not_valid_after_utc,
           "signed falls inside the Document Signer Certificate validity")

    mso = cbor2.loads(cbor2.loads(payload).value)
    ns_items = signed["nameSpaces"][KTP_DOCTYPE]
    recomputed = {}
    for tagged in ns_items:
        enc = cbor2.dumps(tagged, canonical=True)
        recomputed[cbor2.loads(tagged.value)["digestID"]] = sha256(enc)
    vd = mso["valueDigests"][KTP_DOCTYPE]
    report(recomputed == vd and len(vd) == len(ns_items) == 20,
           "all 20 valueDigests recompute from the tag 24 IssuerSignedItem bytes")
    report(
        list(mso) and set(mso) == {"version", "digestAlgorithm", "valueDigests",
                                   "deviceKeyInfo", "docType", "validityInfo", "status"}
        and mso["digestAlgorithm"] == "SHA-256" and mso["version"] == "1.0"
        and list(mso["deviceKeyInfo"]) == ["deviceKey"]
        and mso["deviceKeyInfo"]["deviceKey"] == {1: 2, -1: 1, -2: h["x"], -3: h["y"]}
        and mso["docType"] == KTP_DOCTYPE,
        f"MSO carries the seven fields, docType, and deviceKey of {HOLDER_KEY}",
    )
    report(cbor2.dumps(signed, canonical=True) == raw,
           "IssuerSigned is deterministically encoded")

    # diagnostic notation parses back to the same bytes
    parsed = parse_diag(b["blocks"][T_DIAG])
    report(cbor2.dumps(parsed, canonical=True) == raw,
           "IssuerSigned diagnostic notation parses back to the hex bytes")
    parsed_mso = parse_diag(b["blocks"][T_MSO])
    report(cbor2.dumps(parsed_mso, canonical=True) == cbor2.loads(payload).value,
           "Mobile Security Object diagnostic notation parses back to the signed MSO bytes")
    return failures


def main() -> int:
    built = build()
    failures = verify(built)
    if failures:
        print(f"{failures} check(s) failed; {OUT.name} not written")
        return 1
    OUT.write_text(json.dumps(to_json(built), indent=1, ensure_ascii=False) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
