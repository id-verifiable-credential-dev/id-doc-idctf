"""Generate the issuer X.509 branch and the VICAL of TS-5-04.

Builds, under keys the keystore keeps, the Issuer Root CA certificate, the
Document Signer certificate request and certificate, the VICAL signer
certificate, the Issuer Root CA certificate revocation list, a recognized
foreign root (the second VICAL entry), and the VICAL itself as a payload and
as a signed ``COSE_Sign1``. The verifier branch is ``build.py``'s; this module
only reads its three certificates to state the ten checks the page lists.

Keystore keys: ``issuer-root-ca``, ``issuer-document-signer-1`` (the
``issuance-cose`` key; the mdoc worker signs with it),
``issuer-document-signer-korlantas-1`` (the SIM issuer's), ``issuer-vical-signer``,
``vical-foreign-my-root``, and the ``status-list`` keys ``dukcapil-status-list-1``
and ``bkn-status-list-1`` that the status list signer certificates certify,
all P-256.

Writes ``build/artifacts/x509.json``, which holds:

``certificates``   one object per certificate (``issuer-root-ca``,
                   ``document-signer``, ``vical-signer``, ``foreign-my-root``)
                   with ``pem``, ``der_b64``, ``der_size``, ``ski`` (hex,
                   upper case), ``aki``, ``serial_hex``, ``subject``,
                   ``issuer``, ``not_before``, ``not_after`` and ``key`` (the
                   keystore name of the key it certifies).
``csr``            ``pem``, ``der_size``, ``key``.
``crl``            ``pem``, ``der_size``, ``crl_number``, ``aki``, ``key``.
``vical``          ``payload_diag`` (the page's block), ``payload_hex``,
                   ``payload_size``, ``cose_sign1_base64`` (the page's
                   block), ``cose_sign1_hex``, ``cose_sign1_size``, the
                   ``vical_issue_id`` and both entries' ``doc_type``.
``blocks``         block title -> exact text to put in the fence, for
                   ``inject.py``.
``keys``           role -> keystore name.

Signing is randomized for ECDSA, so a re-run would rewrite every signature
other pages embed (the Document Signer Certificate sits in the mdocs). When
``x509.json`` exists and its certificates still certify the keystore's keys,
the run reuses them and only re-verifies; ``--rebuild`` signs everything anew.

Run: ``.venv/bin/python scripts/artifacts/x509ca.py [--rebuild]``
"""

from __future__ import annotations

import base64
import datetime as dt
import json
import sys

import cbor2
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, utils as asym_utils
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID, ObjectIdentifier

from keystore import REPO_ROOT, load_or_create

OUT = REPO_ROOT / "build" / "artifacts"

MDOC_DOCUMENT_SIGNING = ObjectIdentifier("1.0.18013.5.1.2")
MDOC_VICAL_SIGNING = ObjectIdentifier("1.0.18013.5.1.8")
MDL_IACA_PROFILE = "1.0.18013.5.1.7"

TA_ORG = "Trust Authority Republik Indonesia"
ROOT_CRL_URL = "https://registry.trust.go.id/crl/issuer-root-ca"
TA_URL = "https://trust.go.id"

KEYS = {
    "issuer_root_ca": "issuer-root-ca",
    "document_signer": "issuer-document-signer-1",
    "vical_signer": "issuer-vical-signer",
    "foreign_my_root": "vical-foreign-my-root",
    "document_signer_retired": "issuer-document-signer-retired",
    "document_signer_korlantas": "issuer-document-signer-korlantas-1",
    "status_list_signer_dukcapil": "dukcapil-status-list-1",
    "status_list_signer_bkn": "bkn-status-list-1",
}

# The status list signer certificates of TS-5-04, one per issuer that issues
# in mdoc and publishes the CWT form of its list (TS-5-09): record name ->
# (KEYS role, organizationName, commonName, serial).
STATUS_LIST_SIGNERS = {
    "status-list-signer-dukcapil": (
        "status_list_signer_dukcapil",
        "Direktorat Jenderal Kependudukan dan Pencatatan Sipil",
        "Dukcapil Status List Signer 2026-A",
        0x393F3B03452AAC04524969A3,
    ),
    "status-list-signer-bkn": (
        "status_list_signer_bkn",
        "Badan Kepegawaian Negara",
        "BKN Status List Signer 2026-A",
        0x24E85E631BAF6F0F571315A0,
    ),
}

# The Document Signer Certificate the root CRL revokes (2026-09-15).
RETIRED_SERIAL = 0xF9218BDD107B1B04FC1F16E5


def utc(y: int, m: int, d: int, hh: int = 0, mm: int = 0) -> dt.datetime:
    return dt.datetime(y, m, d, hh, mm, tzinfo=dt.timezone.utc)


def name(country: str, org: str, common: str) -> x509.Name:
    return x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, country),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, org),
            x509.NameAttribute(NameOID.COMMON_NAME, common),
        ]
    )


def key_usage(**on: bool) -> x509.KeyUsage:
    fields = dict(
        digital_signature=False,
        content_commitment=False,
        key_encipherment=False,
        data_encipherment=False,
        key_agreement=False,
        key_cert_sign=False,
        crl_sign=False,
        encipher_only=False,
        decipher_only=False,
    )
    fields.update(on)
    return x509.KeyUsage(**fields)


def crl_dp(url: str) -> x509.CRLDistributionPoints:
    return x509.CRLDistributionPoints(
        [
            x509.DistributionPoint(
                full_name=[x509.UniformResourceIdentifier(url)],
                relative_name=None,
                reasons=None,
                crl_issuer=None,
            )
        ]
    )


def ian(url: str) -> x509.IssuerAlternativeName:
    return x509.IssuerAlternativeName([x509.UniformResourceIdentifier(url)])


def ski_of(cert: x509.Certificate) -> bytes:
    return cert.extensions.get_extension_for_class(x509.SubjectKeyIdentifier).value.digest


def pem(obj) -> str:
    return obj.public_bytes(serialization.Encoding.PEM).decode().strip()


def der(obj) -> bytes:
    return obj.public_bytes(serialization.Encoding.DER)


def b64_lines(raw: bytes, width: int = 64) -> str:
    text = base64.b64encode(raw).decode()
    return "\n".join(text[i : i + width] for i in range(0, len(text), width))


# ------------------------------------------------------------------ the PKI


# Issued in the exchange that carried Dukcapil's first log entry, 2026-02-01.
RETIRED_FROM = dt.datetime(2026, 2, 1, tzinfo=dt.timezone.utc)


# The Issuer Root CA list lives one crl_publication interval, P1D (tracks/0436).
CRL_THIS_UPDATE = dt.datetime(2026, 10, 1, tzinfo=dt.timezone.utc)
CRL_NEXT_UPDATE = dt.datetime(2026, 10, 2, tzinfo=dt.timezone.utc)


def build_root_crl(root: x509.Certificate, root_key) -> x509.CertificateRevocationList:
    return (
        x509.CertificateRevocationListBuilder()
        .issuer_name(root.subject)
        .last_update(CRL_THIS_UPDATE)
        .next_update(CRL_NEXT_UPDATE)
        .add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(root_key.public_key()),
            critical=False,
        )
        .add_extension(x509.CRLNumber(7), critical=False)
        .add_revoked_certificate(
            x509.RevokedCertificateBuilder()
            .serial_number(0xF9218BDD107B1B04FC1F16E5)
            .revocation_date(utc(2026, 9, 15))
            .build()
        )
        .sign(root_key, hashes.SHA256())
    )


def build_retired(root: x509.Certificate, root_key) -> x509.Certificate:
    """The earlier Dukcapil signer, same profile as the live one, 455 days from
    the issuer's first log entry (TS-4-03), revoked inside its window on 2026-09-15."""
    key = load_or_create(KEYS["document_signer_retired"])
    return (
        x509.CertificateBuilder()
        .subject_name(
            name(
                "ID",
                "Direktorat Jenderal Kependudukan dan Pencatatan Sipil",
                "Dukcapil mdoc Document Signer 2026-0",
            )
        )
        .issuer_name(root.subject)
        .public_key(key.public_key())
        .serial_number(RETIRED_SERIAL)
        .not_valid_before(RETIRED_FROM)
        .not_valid_after(RETIRED_FROM + dt.timedelta(days=455))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(key_usage(digital_signature=True), critical=True)
        .add_extension(x509.ExtendedKeyUsage([MDOC_DOCUMENT_SIGNING]), critical=True)
        .add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(root_key.public_key()),
            critical=False,
        )
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(key.public_key()), critical=False)
        .add_extension(ian(TA_URL), critical=False)
        .add_extension(crl_dp(ROOT_CRL_URL), critical=False)
        .sign(root_key, hashes.SHA256())
    )


def build_pki() -> dict:
    root_key = load_or_create(KEYS["issuer_root_ca"])
    dsc_key = load_or_create(KEYS["document_signer"])
    vical_key = load_or_create(KEYS["vical_signer"])
    my_key = load_or_create(KEYS["foreign_my_root"])

    root_name = name("ID", TA_ORG, "IDCTF Issuer Root CA")
    root_ski = x509.SubjectKeyIdentifier.from_public_key(root_key.public_key())
    root_aki = x509.AuthorityKeyIdentifier.from_issuer_public_key(root_key.public_key())

    root = (
        x509.CertificateBuilder()
        .subject_name(root_name)
        .issuer_name(root_name)
        .public_key(root_key.public_key())
        .serial_number(0x2C799082EE4470F97328DDCD)
        .not_valid_before(utc(2026, 1, 1))
        .not_valid_after(utc(2041, 1, 1))
        .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
        .add_extension(key_usage(key_cert_sign=True, crl_sign=True), critical=True)
        .add_extension(root_ski, critical=False)
        .add_extension(ian(TA_URL), critical=False)
        .add_extension(crl_dp(ROOT_CRL_URL), critical=False)
        .sign(root_key, hashes.SHA256())
    )

    dsc_name = name(
        "ID",
        "Direktorat Jenderal Kependudukan dan Pencatatan Sipil",
        "Dukcapil mdoc Document Signer 2026-A",
    )
    csr = (
        x509.CertificateSigningRequestBuilder()
        .subject_name(dsc_name)
        .sign(dsc_key, hashes.SHA256())
    )

    dsc = (
        x509.CertificateBuilder()
        .subject_name(csr.subject)
        .issuer_name(root_name)
        .public_key(csr.public_key())
        .serial_number(0x16A98534626A68B21D10C09B)
        .not_valid_before(utc(2026, 9, 1))
        .not_valid_after(utc(2027, 11, 1))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(key_usage(digital_signature=True), critical=True)
        .add_extension(x509.ExtendedKeyUsage([MDOC_DOCUMENT_SIGNING]), critical=True)
        .add_extension(root_aki, critical=False)
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(csr.public_key()), critical=False)
        .add_extension(ian(TA_URL), critical=False)
        .add_extension(crl_dp(ROOT_CRL_URL), critical=False)
        .sign(root_key, hashes.SHA256())
    )

    vical_signer = (
        x509.CertificateBuilder()
        .subject_name(name("ID", TA_ORG, "IDCTF VICAL Signer 2026"))
        .issuer_name(root_name)
        .public_key(vical_key.public_key())
        .serial_number(0x309A194F9588B631B53120DF)
        .not_valid_before(utc(2026, 10, 1))
        .not_valid_after(utc(2029, 12, 31))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(key_usage(content_commitment=True), critical=True)
        .add_extension(x509.ExtendedKeyUsage([MDOC_VICAL_SIGNING]), critical=True)
        .add_extension(root_aki, critical=False)
        .add_extension(
            x509.SubjectKeyIdentifier.from_public_key(vical_key.public_key()), critical=False
        )
        .add_extension(ian(TA_URL), critical=False)
        .add_extension(crl_dp(ROOT_CRL_URL), critical=False)
        .sign(root_key, hashes.SHA256())
    )

    my_name = name("MY", "Jabatan Pengangkutan Jalan Malaysia", "MYDL Issuing Authority Root")
    my_root = (
        x509.CertificateBuilder()
        .subject_name(my_name)
        .issuer_name(my_name)
        .public_key(my_key.public_key())
        .serial_number(0x5BBBA9D4E105FF74AE84C5ED)
        .not_valid_before(utc(2025, 3, 1))
        .not_valid_after(utc(2035, 3, 1))
        .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
        .add_extension(key_usage(key_cert_sign=True, crl_sign=True), critical=True)
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(my_key.public_key()), critical=False)
        .add_extension(ian("https://jpj.gov.my"), critical=False)
        .add_extension(crl_dp("https://pki.jpj.gov.my/crl/iaca"), critical=False)
        .sign(my_key, hashes.SHA256())
    )

    crl = build_root_crl(root, root_key)

    return {
        "root": root,
        "csr": csr,
        "dsc": dsc,
        "vical_signer": vical_signer,
        "my_root": my_root,
        "crl": crl,
        "retired": build_retired(root, root_key),
        "korlantas": build_korlantas(root, root_key),
        "status_signers": {
            rec: build_status_signer(root, root_key, rec) for rec in STATUS_LIST_SIGNERS
        },
        "keys": {"root": root_key, "vical": vical_key},
    }


def load_existing() -> tuple[dict, bytes] | None:
    """The stored branch, if it still matches the keystore; else None."""
    path = OUT / "x509.json"
    if not path.exists():
        return None
    try:
        rec = json.loads(path.read_text())
        certs = rec["certificates"]
        load = lambda k: x509.load_pem_x509_certificate(certs[k]["pem"].encode())  # noqa: E731
        pki = {
            "root": load("issuer-root-ca"),
            "dsc": load("document-signer"),
            "vical_signer": load("vical-signer"),
            "my_root": load("foreign-my-root"),
            "csr": x509.load_pem_x509_csr(rec["csr"]["pem"].encode()),
            "crl": x509.load_pem_x509_crl(rec["crl"]["pem"].encode()),
            "keys": {
                "root": load_or_create(KEYS["issuer_root_ca"]),
                "vical": load_or_create(KEYS["vical_signer"]),
            },
        }
        if (pki["crl"].last_update_utc, pki["crl"].next_update_utc) != (CRL_THIS_UPDATE, CRL_NEXT_UPDATE):
            pki["crl"] = build_root_crl(pki["root"], pki["keys"]["root"])
        if "document-signer-retired" in certs:
            pki["retired"] = load("document-signer-retired")
            mine = load_or_create(KEYS["document_signer_retired"]).public_key().public_numbers()
            if pki["retired"].public_key().public_numbers() != mine:
                return None
            if pki["retired"].not_valid_before_utc != RETIRED_FROM:  # moved by tracks/0355
                pki["retired"] = build_retired(pki["root"], pki["keys"]["root"])
        else:  # added later: sign it, leave everything else as stored
            pki["retired"] = build_retired(pki["root"], pki["keys"]["root"])
        if "document-signer-korlantas" in certs:
            pki["korlantas"] = load("document-signer-korlantas")
            mine = load_or_create(KEYS["document_signer_korlantas"]).public_key().public_numbers()
            if pki["korlantas"].public_key().public_numbers() != mine:
                return None
        else:  # added later: sign it, leave everything else as stored
            pki["korlantas"] = build_korlantas(pki["root"], pki["keys"]["root"])
        pki["status_signers"] = {}
        for rec_name, (role, *_rest) in STATUS_LIST_SIGNERS.items():
            if rec_name in certs:
                pki["status_signers"][rec_name] = load(rec_name)
                mine = load_or_create(KEYS[role]).public_key().public_numbers()
                if pki["status_signers"][rec_name].public_key().public_numbers() != mine:
                    return None
            else:  # added later: sign it, leave everything else as stored
                pki["status_signers"][rec_name] = build_status_signer(
                    pki["root"], pki["keys"]["root"], rec_name)
        for cert_key, name_ in (
            ("root", "issuer_root_ca"), ("dsc", "document_signer"),
            ("vical_signer", "vical_signer"), ("my_root", "foreign_my_root"),
        ):
            mine = load_or_create(KEYS[name_]).public_key().public_numbers()
            if pki[cert_key].public_key().public_numbers() != mine:
                return None
        return pki, bytes.fromhex(rec["vical"]["cose_sign1_hex"])
    except (KeyError, ValueError):
        return None


# -------------------------------------------------------------------- VICAL

VICAL_ENTRIES = [
    # (certificate key in pki, docTypes, issuingAuthority, issuingCountry)
    ("root", ["id.idctf.ktp.1", "org.iso.18013.5.1.mDL"], TA_ORG, "ID"),
    ("my_root", ["org.iso.18013.5.1.mDL"], "Jabatan Pengangkutan Jalan Malaysia", "MY"),
]


def tdate(text: str) -> cbor2.CBORTag:
    return cbor2.CBORTag(0, text)


def iso(value: dt.datetime) -> str:
    return value.strftime("%Y-%m-%dT%H:%M:%SZ")


def serial_bytes(cert: x509.Certificate) -> bytes:
    n = cert.serial_number
    return n.to_bytes((n.bit_length() + 7) // 8, "big")


def vical_payload(pki: dict) -> dict:
    infos = []
    for key, doc_types, authority, country in VICAL_ENTRIES:
        cert = pki[key]
        infos.append(
            {
                "certificate": der(cert),
                "serialNumber": cbor2.CBORTag(2, serial_bytes(cert)),
                "ski": ski_of(cert),
                "docType": doc_types,
                "certificateProfile": [MDL_IACA_PROFILE],
                "issuingAuthority": authority,
                "issuingCountry": country,
                "issuer": cert.issuer.public_bytes(),
                "subject": cert.subject.public_bytes(),
                "notBefore": tdate(iso(cert.not_valid_before_utc)),
                "notAfter": tdate(iso(cert.not_valid_after_utc)),
            }
        )
    return {
        "version": "1.0",
        "vicalProvider": TA_ORG,
        "date": tdate("2026-10-17T06:00:00Z"),
        "vicalIssueID": 4,
        "nextUpdate": tdate("2026-10-18T06:00:00Z"),  # vical_publication, P1D
        "certificateInfos": infos,
    }


def diag_text(payload: dict) -> str:
    """The payload in diagnostic notation, long byte strings elided as the page does."""

    def bstr(raw: bytes, elide: bool) -> str:
        if elide and len(raw) > 40:
            return f"h'{raw[:16].hex().upper()} ... {raw[-16:].hex().upper()}',   / {len(raw)} bytes /"
        return f"h'{raw.hex().upper()}',"

    def tstr(v: str) -> str:
        return json.dumps(v, ensure_ascii=False)

    lines = [
        "{",
        f'  "version": {tstr(payload["version"])},',
        f'  "vicalProvider": {tstr(payload["vicalProvider"])},',
        f'  "date": 0({tstr(payload["date"].value)}),',
        f'  "vicalIssueID": {payload["vicalIssueID"]},',
        f'  "nextUpdate": 0({tstr(payload["nextUpdate"].value)}),',
        '  "certificateInfos": [',
    ]
    infos = payload["certificateInfos"]
    for i, e in enumerate(infos):
        doc = ", ".join(tstr(d) for d in e["docType"])
        prof = ", ".join(tstr(d) for d in e["certificateProfile"])
        lines += [
            "    {",
            f'      "certificate": {bstr(e["certificate"], True)}',
            f'      "serialNumber": 2(h\'{e["serialNumber"].value.hex().upper()}\'),',
            f'      "ski": h\'{e["ski"].hex().upper()}\',',
            f'      "docType": [{doc}],',
            f'      "certificateProfile": [{prof}],',
            f'      "issuingAuthority": {tstr(e["issuingAuthority"])},',
            f'      "issuingCountry": {tstr(e["issuingCountry"])},',
            f'      "issuer": {bstr(e["issuer"], True)}',
            f'      "subject": {bstr(e["subject"], True)}',
            f'      "notBefore": 0({tstr(e["notBefore"].value)}),',
            f'      "notAfter": 0({tstr(e["notAfter"].value)})',
            "    }" + ("," if i < len(infos) - 1 else ""),
        ]
    lines += ["  ]", "}"]
    return "\n".join(lines)


PROTECTED = bytes.fromhex("a10126")


def sig_structure(payload: bytes) -> bytes:
    return cbor2.dumps(["Signature1", PROTECTED, b"", payload])


def sign_cose(payload: bytes, signer_cert: x509.Certificate, key) -> bytes:
    sig_der = key.sign(sig_structure(payload), ec.ECDSA(hashes.SHA256()))
    r, s = asym_utils.decode_dss_signature(sig_der)
    raw = r.to_bytes(32, "big") + s.to_bytes(32, "big")
    return cbor2.dumps([PROTECTED, {33: der(signer_cert)}, payload, raw])


# ------------------------------------------------------------ verification


def verify_ecdsa_raw(pub, raw: bytes, data: bytes) -> None:
    pub.verify(
        asym_utils.encode_dss_signature(
            int.from_bytes(raw[:32], "big"), int.from_bytes(raw[32:], "big")
        ),
        data,
        ec.ECDSA(hashes.SHA256()),
    )


def check(label: str, fn) -> bool:
    try:
        fn()
        print(f"OK    {label}")
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL  {label}: {exc!r}")
        return False


def ext(cert, cls):
    return cert.extensions.get_extension_for_class(cls)


def build_korlantas(root: x509.Certificate, root_key) -> x509.Certificate:
    """The Document Signer Certificate of the issuer of the SIM, the second
    issuer under the root and the one that signs ``org.iso.18013.5.1.mDL``."""
    key = load_or_create(KEYS["document_signer_korlantas"])
    return (
        x509.CertificateBuilder()
        .subject_name(
            name(
                "ID",
                "Korps Lalu Lintas Kepolisian Negara Republik Indonesia",
                "Korlantas mdoc Document Signer 2026-A",
            )
        )
        .issuer_name(root.subject)
        .public_key(key.public_key())
        .serial_number(0x4B1D7E30C95A26F3880E1D52)
        .not_valid_before(utc(2026, 9, 1))
        .not_valid_after(utc(2027, 11, 1))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(key_usage(digital_signature=True), critical=True)
        .add_extension(x509.ExtendedKeyUsage([MDOC_DOCUMENT_SIGNING]), critical=True)
        .add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(root_key.public_key()),
            critical=False,
        )
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(key.public_key()), critical=False)
        .add_extension(ian(TA_URL), critical=False)
        .add_extension(crl_dp(ROOT_CRL_URL), critical=False)
        .sign(root_key, hashes.SHA256())
    )


def build_status_signer(root: x509.Certificate, root_key, rec_name: str) -> x509.Certificate:
    """A status list signer certificate over an issuer's ``status-list`` key:
    no extended key usage until Token Status List has its OID assigned."""
    role, org, common, serial = STATUS_LIST_SIGNERS[rec_name]
    key = load_or_create(KEYS[role])
    return (
        x509.CertificateBuilder()
        .subject_name(name("ID", org, common))
        .issuer_name(root.subject)
        .public_key(key.public_key())
        .serial_number(serial)
        .not_valid_before(utc(2026, 9, 1))
        .not_valid_after(utc(2029, 9, 1))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(key_usage(digital_signature=True), critical=True)
        .add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(root_key.public_key()),
            critical=False,
        )
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(key.public_key()), critical=False)
        .add_extension(ian(TA_URL), critical=False)
        .add_extension(crl_dp(ROOT_CRL_URL), critical=False)
        .sign(root_key, hashes.SHA256())
    )


def profile_checks(pki: dict) -> list[tuple[str, object]]:
    root, dsc, vs, my = pki["root"], pki["dsc"], pki["vical_signer"], pki["my_root"]
    checks: list[tuple[str, object]] = []

    def req(cond, msg="false"):
        assert cond, msg

    def common(cert: x509.Certificate):
        req(cert.version == x509.Version.v3, "version")
        req(cert.signature_algorithm_oid.dotted_string == "1.2.840.10045.4.3.2", "sig alg")
        pub = cert.public_key()
        req(isinstance(pub, ec.EllipticCurvePublicKey) and pub.curve.name == "secp256r1", "curve")
        req(
            len(pub.public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)) == 65,
            "uncompressed",
        )
        req(2**62 <= cert.serial_number < 2**159, "serial >= 63 bits, <= 20 octets")
        s = ext(cert, x509.SubjectKeyIdentifier)
        req(not s.critical, "SKI critical")
        req(s.value == x509.SubjectKeyIdentifier.from_public_key(pub), "SKI is SHA-1 of key")
        c = cert.subject.get_attributes_for_oid(NameOID.COUNTRY_NAME)
        req(c[0].value == "ID" and c[0]._type.name == "PrintableString", "countryName")
        req(cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME), "commonName")
        forbidden = (
            x509.PolicyConstraints, x509.NameConstraints, x509.InhibitAnyPolicy, x509.FreshestCRL,
        )
        for e in cert.extensions:
            req(not isinstance(e.value, forbidden), "forbidden extension")
            req(e.value.oid.dotted_string != "2.5.29.33", "PolicyMappings")
        known = (
            x509.BasicConstraints, x509.KeyUsage, x509.ExtendedKeyUsage, x509.SubjectKeyIdentifier,
            x509.AuthorityKeyIdentifier, x509.IssuerAlternativeName, x509.CRLDistributionPoints,
        )
        for e in cert.extensions:
            req(not e.critical or isinstance(e.value, known), "unknown critical extension")

    def leaf(cert: x509.Certificate, ku: dict, eku: ObjectIdentifier):
        common(cert)
        bc = ext(cert, x509.BasicConstraints)
        req(bc.critical and not bc.value.ca, "basic constraints")
        k = ext(cert, x509.KeyUsage)
        req(k.critical, "key usage critical")
        for attr in ("digital_signature", "content_commitment", "key_cert_sign", "crl_sign"):
            req(getattr(k.value, attr) == ku.get(attr, False), f"key usage {attr}")
        e = ext(cert, x509.ExtendedKeyUsage)
        req(e.critical and list(e.value) == [eku], "extended key usage")
        a = ext(cert, x509.AuthorityKeyIdentifier)
        req(not a.critical and a.value.key_identifier == ski_of(root), "AKI")
        i = ext(cert, x509.IssuerAlternativeName)
        req(not i.critical and list(i.value) == [x509.UniformResourceIdentifier(TA_URL)], "IAN")
        d = ext(cert, x509.CRLDistributionPoints)
        req(not d.critical and len(d.value) == 1, "CRLDP")
        p = d.value[0]
        req(p.reasons is None and p.crl_issuer is None, "CRLDP reasons/cRLIssuer")
        req(p.full_name == [x509.UniformResourceIdentifier(ROOT_CRL_URL)], "CRLDP url")
        req(cert.issuer == root.subject, "issuer is root subject (binary)")
        req(cert.issuer.public_bytes() == root.subject.public_bytes(), "issuer bytes")
        req(cert.not_valid_after_utc <= root.not_valid_after_utc, "not after within root")

    def root_profile():
        common(root)
        req(root.subject == root.issuer and root.subject.public_bytes() == root.issuer.public_bytes(), "self-issued")
        bc = ext(root, x509.BasicConstraints)
        req(bc.critical and bc.value.ca and bc.value.path_length == 0, "basic constraints")
        k = ext(root, x509.KeyUsage)
        req(k.critical and k.value.key_cert_sign and k.value.crl_sign, "key usage")
        req(not any([k.value.digital_signature, k.value.content_commitment, k.value.key_encipherment,
                     k.value.data_encipherment, k.value.key_agreement]), "key usage only two")
        i = ext(root, x509.IssuerAlternativeName)
        req(not i.critical, "IAN")
        d = ext(root, x509.CRLDistributionPoints)
        req(not d.critical and d.value[0].full_name == [x509.UniformResourceIdentifier(ROOT_CRL_URL)], "CRLDP")
        req(d.value[0].reasons is None and d.value[0].crl_issuer is None, "CRLDP fields")
        try:
            root.extensions.get_extension_for_class(x509.ExtendedKeyUsage)
            raise AssertionError("EKU present")
        except x509.ExtensionNotFound:
            pass
        req((root.not_valid_after_utc - root.not_valid_before_utc).days <= 20 * 366, "<= 20 years")

    def dsc_profile():
        leaf(dsc, {"digital_signature": True}, MDOC_DOCUMENT_SIGNING)
        req((dsc.not_valid_after_utc - dsc.not_valid_before_utc).days == 426, "426 days")
        req((dsc.not_valid_after_utc - dsc.not_valid_before_utc).days <= 457, "457-day ceiling")

    def korlantas_profile():
        k = pki["korlantas"]
        leaf(k, {"digital_signature": True}, MDOC_DOCUMENT_SIGNING)
        req((k.not_valid_after_utc - k.not_valid_before_utc).days <= 457, "457-day ceiling")
        req(ski_of(k) != ski_of(dsc), "a key of its own")

    def status_signer_profile():
        for rec_name, cert in pki["status_signers"].items():
            common(cert)
            bc = ext(cert, x509.BasicConstraints)
            req(bc.critical and not bc.value.ca, "basic constraints")
            k = ext(cert, x509.KeyUsage)
            req(k.critical and k.value.digital_signature, "key usage critical, digitalSignature")
            req(not any([k.value.content_commitment, k.value.key_encipherment, k.value.data_encipherment,
                         k.value.key_agreement, k.value.key_cert_sign, k.value.crl_sign]),
                "key usage digitalSignature only")
            try:
                cert.extensions.get_extension_for_class(x509.ExtendedKeyUsage)
                raise AssertionError("EKU present")
            except x509.ExtensionNotFound:
                pass
            a = ext(cert, x509.AuthorityKeyIdentifier)
            req(not a.critical and a.value.key_identifier == ski_of(root), "AKI")
            i = ext(cert, x509.IssuerAlternativeName)
            req(not i.critical and list(i.value) == [x509.UniformResourceIdentifier(TA_URL)], "IAN")
            d = ext(cert, x509.CRLDistributionPoints)
            req(not d.critical and d.value[0].full_name == [x509.UniformResourceIdentifier(ROOT_CRL_URL)], "CRLDP")
            req(cert.issuer.public_bytes() == root.subject.public_bytes(), "issuer bytes")
            req((cert.not_valid_after_utc - cert.not_valid_before_utc).days <= 1187, "1187-day ceiling")
            req(cert.not_valid_after_utc <= root.not_valid_after_utc, "not after within root")
            req(ski_of(cert) not in (ski_of(dsc), ski_of(pki["korlantas"])), "a key of its own")
        org = lambda c: c.subject.get_attributes_for_oid(NameOID.ORGANIZATION_NAME)[0].value  # noqa: E731
        req(org(pki["status_signers"]["status-list-signer-dukcapil"]) == org(dsc),
            "Dukcapil's names the organization of its Document Signer Certificate")

    def vs_profile():
        leaf(vs, {"content_commitment": True}, MDOC_VICAL_SIGNING)
        req((vs.not_valid_after_utc - vs.not_valid_before_utc).days == 1187, "1187 days")

    def csr_profile():
        c = pki["csr"]
        req(len(list(c.extensions)) == 0, "CSR carries an extension")
        req(c.subject == dsc.subject, "CSR subject = certificate subject")

    def crl_profile():
        crl = pki["crl"]
        req(crl.issuer.public_bytes() == root.subject.public_bytes(), "issuer name")
        names = sorted(type(e.value).__name__ for e in crl.extensions)
        req(names == ["AuthorityKeyIdentifier", "CRLNumber"], f"extensions {names}")
        req(all(not e.critical for e in crl.extensions), "extensions critical")
        req(crl.extensions.get_extension_for_class(x509.AuthorityKeyIdentifier).value.key_identifier == ski_of(root), "AKI")
        req(crl.extensions.get_extension_for_class(x509.CRLNumber).value.crl_number == 7, "CRL number")
        req(len(list(crl)) == 1 and len(list(crl[0].extensions)) == 0, "entry without extension")
        req(crl.signature_algorithm_oid.dotted_string == "1.2.840.10045.4.3.2", "sig alg")
        req(b"\x02\x01\x01" in crl.tbs_certlist_bytes[:12], "version v2")

    checks += [
        ("profile: Issuer Root CA (root profile, IACA)", root_profile),
        ("profile: CSR carries subject and key, no extension", csr_profile),
        ("profile: Document Signer Certificate", dsc_profile),
        ("profile: Korlantas Document Signer Certificate", korlantas_profile),
        ("profile: VICAL signer certificate", vs_profile),
        ("profile: status list signer certificates", status_signer_profile),
        ("profile: certificate revocation list", crl_profile),
    ]
    return checks


def verifier_branch_lines() -> list[tuple[str, bool]]:
    """The four verifier checks of the page's block, read from build.py's output."""
    paths = {k: OUT / f"verifier-{k}.pem" for k in ("root-ca", "issuing-ca", "device")}
    crl_path = OUT / "verifier-issuing-ca.crl"
    if not all(p.exists() for p in [*paths.values(), crl_path]):
        return []
    load = lambda p: x509.load_pem_x509_certificate(p.read_bytes())  # noqa: E731
    vroot, vica, vdev = (load(paths[k]) for k in ("root-ca", "issuing-ca", "device"))
    vcrl = x509.load_pem_x509_crl(crl_path.read_bytes())

    def ok(fn):
        try:
            fn()
            return True
        except Exception:  # noqa: BLE001
            return False

    return [
        ("Verifier Root CA self-signature", ok(lambda: vroot.verify_directly_issued_by(vroot))),
        ("Verifier Issuing CA <- Verifier Root CA", ok(lambda: vica.verify_directly_issued_by(vroot))),
        ("Verifier Device Certificate <- Issuing CA", ok(lambda: vdev.verify_directly_issued_by(vica))),
        ("Verifier Issuing CA revocation list", vcrl.is_signature_valid(vica.public_key())),
    ]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    existing = None if "--rebuild" in sys.argv else load_existing()
    if existing:
        pki, stored_cose = existing
        print("-- reusing the stored branch of build/artifacts/x509.json (--rebuild signs anew)")
    else:
        pki, stored_cose = build_pki(), None
    root, csr, dsc, vs, my, crl = (pki[k] for k in ("root", "csr", "dsc", "vical_signer", "my_root", "crl"))

    payload = vical_payload(pki)
    payload_bytes = cbor2.dumps(payload)
    if stored_cose and cbor2.loads(stored_cose)[2] != payload_bytes:
        stored_cose = None  # the payload changed: sign it again
    cose = stored_cose or sign_cose(payload_bytes, vs, pki["keys"]["vical"])
    cose_b64 = b64_lines(cose)

    def cert_record(cert: x509.Certificate, key_name: str, issuer_cert=None) -> dict:
        try:
            aki = ext(cert, x509.AuthorityKeyIdentifier).value.key_identifier.hex().upper()
        except x509.ExtensionNotFound:
            aki = None
        return {
            "pem": pem(cert),
            "der_b64": base64.b64encode(der(cert)).decode(),
            "der_size": len(der(cert)),
            "ski": ski_of(cert).hex().upper(),
            "aki": aki,
            "serial_hex": f"{cert.serial_number:X}",
            "subject": cert.subject.rfc4514_string(),
            "issuer": cert.issuer.rfc4514_string(),
            "not_before": iso(cert.not_valid_before_utc),
            "not_after": iso(cert.not_valid_after_utc),
            "key": key_name,
        }

    diag = diag_text(payload)
    verifier_lines = verifier_branch_lines()
    v = dict(verifier_lines)
    own = [
        ("Issuer Root CA self-signature", lambda: root.verify_directly_issued_by(root)),
        ("CSR self-signature", lambda: None if csr.is_signature_valid else (_ for _ in ()).throw(ValueError("bad"))),
        ("Document Signer Certificate <- root", lambda: dsc.verify_directly_issued_by(root)),
        ("Korlantas Document Signer <- root", lambda: pki["korlantas"].verify_directly_issued_by(root)),
        ("VICAL signer certificate <- root", lambda: vs.verify_directly_issued_by(root)),
        ("Status list signer certificates <- root",
         lambda: [c.verify_directly_issued_by(root) for c in pki["status_signers"].values()]),
    ]

    # The checks block is written after verification; state the truth only.
    results: dict[str, bool] = {}
    print("-- verification")
    for label, fn in own:
        results[label] = check(label, fn)
    results["CSR public key = Document Signer Certificate key"] = check(
        "CSR public key = Document Signer Certificate key",
        lambda: (_ for _ in ()).throw(ValueError("differ"))
        if csr.public_key().public_numbers() != dsc.public_key().public_numbers()
        or csr.public_key().public_numbers() != load_or_create(KEYS["document_signer"]).public_key().public_numbers()
        else None,
    )
    results["Issuer Root CA certificate revocation list"] = check(
        "Issuer Root CA certificate revocation list (verifies under the root key)",
        lambda: None if crl.is_signature_valid(root.public_key()) else (_ for _ in ()).throw(ValueError("bad")),
    )

    def cose_check():
        arr = cbor2.loads(cose)
        assert len(arr) == 4 and arr[0] == PROTECTED and not hasattr(arr, "tag")
        assert cbor2.loads(arr[0]) == {1: -7}
        assert set(arr[1]) == {33}
        signer = x509.load_der_x509_certificate(arr[1][33])
        signer.verify_directly_issued_by(root)
        assert len(arr[3]) == 64
        verify_ecdsa_raw(signer.public_key(), arr[3], sig_structure(arr[2]))
        decoded = cbor2.loads(arr[2])
        assert decoded["vicalIssueID"] == 4 and len(decoded["certificateInfos"]) == 2
        for e in decoded["certificateInfos"]:
            c = x509.load_der_x509_certificate(e["certificate"])
            assert e["ski"] == ski_of(c) and e["serialNumber"] == c.serial_number
            assert e["issuer"] == c.issuer.public_bytes() and e["subject"] == c.subject.public_bytes()
            c.verify_directly_issued_by(c)

    results["VICAL COSE_Sign1 signature"] = check(
        "VICAL COSE_Sign1 verifies under the VICAL signer certificate; x5chain chains to the root; entries match their certificates",
        cose_check,
    )
    ret = pki["retired"]

    def retired_check():
        ret.verify_directly_issued_by(root)
        assert ret.serial_number == RETIRED_SERIAL
        assert RETIRED_SERIAL == list(crl)[0].serial_number, "serial is the one the CRL revokes"
        assert ret.not_valid_before_utc < dsc.not_valid_before_utc
        assert ret.not_valid_before_utc <= list(crl)[0].revocation_date_utc <= ret.not_valid_after_utc
        assert (ret.not_valid_after_utc - ret.not_valid_before_utc).days <= 457
        assert ski_of(ret) == x509.SubjectKeyIdentifier.from_public_key(
            load_or_create(KEYS["document_signer_retired"]).public_key()).digest
        assert ret.issuer.public_bytes() == root.subject.public_bytes()
        assert ext(ret, x509.ExtendedKeyUsage).critical and list(ext(ret, x509.ExtendedKeyUsage).value) == [MDOC_DOCUMENT_SIGNING]
        assert ext(ret, x509.KeyUsage).value.digital_signature and not ext(ret, x509.BasicConstraints).value.ca
        assert ext(ret, x509.AuthorityKeyIdentifier).value.key_identifier == ski_of(root)

    results["retired Document Signer Certificate"] = check(
        "retired Document Signer Certificate: chains to root, serial is the CRL's, validity brackets the revocation, SKI as recorded",
        retired_check,
    )
    for label, fn in profile_checks(pki):
        results[label] = check(label, fn)

    sig_lines = [
        ("Issuer Root CA self-signature", results["Issuer Root CA self-signature"]),
        ("CSR self-signature", results["CSR self-signature"]),
        ("Document Signer Certificate <- root", results["Document Signer Certificate <- root"]),
        ("Korlantas Document Signer <- root", results["Korlantas Document Signer <- root"]),
        ("VICAL signer certificate <- root", results["VICAL signer certificate <- root"]),
        ("Status list signer certificates <- root", results["Status list signer certificates <- root"]),
        *verifier_lines[:3],
        ("Issuer Root CA certificate revocation list", results["Issuer Root CA certificate revocation list"]),
        *verifier_lines[3:],
        ("VICAL COSE_Sign1 signature", results["VICAL COSE_Sign1 signature"]),
    ]
    sig_block = "\n".join(f"{label:<42} {'OK' if ok else 'FAIL'}" for label, ok in sig_lines)

    blocks = {
        "issuer-root-ca.pem, the Issuer Root CA certificate": pem(root),
        "document-signer.csr, the certificate signing request": pem(csr),
        "document-signer.pem, the Document Signer Certificate": pem(dsc),
        "document-signer-korlantas.pem, the Document Signer Certificate of the SIM issuer": pem(pki["korlantas"]),
        "vical-signer.pem, the VICAL signer certificate": pem(vs),
        "status-list-signer.pem, the status list signer certificate":
            pem(pki["status_signers"]["status-list-signer-dukcapil"]),
        "issuer-root-ca.crl, served at https://registry.trust.go.id/crl/issuer-root-ca": pem(crl),
        "The VICAL payload, in CBOR diagnostic notation": diag,
        "GET /vical, the signed COSE_Sign1 in base64": cose_b64,
        "Signature checks over every artifact below": sig_block,
    }
    record = {
        "certificates": {
            "issuer-root-ca": cert_record(root, KEYS["issuer_root_ca"]),
            "document-signer": cert_record(dsc, KEYS["document_signer"]),
            "vical-signer": cert_record(vs, KEYS["vical_signer"]),
            "foreign-my-root": cert_record(my, KEYS["foreign_my_root"]),
            "document-signer-retired": cert_record(pki["retired"], KEYS["document_signer_retired"]),
            "document-signer-korlantas": cert_record(pki["korlantas"], KEYS["document_signer_korlantas"]),
            **{rec_name: cert_record(cert, KEYS[STATUS_LIST_SIGNERS[rec_name][0]])
               for rec_name, cert in pki["status_signers"].items()},
        },
        "csr": {"pem": pem(csr), "der_size": len(der(csr)), "key": KEYS["document_signer"]},
        "crl": {
            "pem": pem(crl),
            "der_size": len(der(crl)),
            "crl_number": 7,
            "aki": ski_of(root).hex().upper(),
            "key": KEYS["issuer_root_ca"],
        },
        "vical": {
            "payload_diag": diag,
            "payload_hex": payload_bytes.hex(),
            "payload_size": len(payload_bytes),
            "cose_sign1_base64": cose_b64,
            "cose_sign1_hex": cose.hex(),
            "cose_sign1_size": len(cose),
            "vical_issue_id": 4,
            "entries": [
                {"ski": ski_of(pki[k]).hex().upper(), "doc_type": d, "issuing_authority": a}
                for k, d, a, _ in VICAL_ENTRIES
            ],
        },
        "blocks": blocks,
        "keys": KEYS,
    }
    (OUT / "x509.json").write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    print(f"-- wrote {OUT / 'x509.json'}")

    failed = [k for k, ok in results.items() if not ok] + [k for k, ok in verifier_lines if not ok]
    if not verifier_lines:
        print("NOTE  verifier-branch files absent: block lists only what could be checked")
    for k, c in record["certificates"].items():
        print(f"      {k}: SKI {c['ski']}  DER {c['der_size']} bytes  serial {c['serial_hex']}")
    print(f"      csr DER {record['csr']['der_size']}  crl DER {record['crl']['der_size']}  "
          f"payload {len(payload_bytes)}  COSE_Sign1 {len(cose)}")
    if failed:
        print("FAILED:", failed)
        return 1
    print("ALL OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
