"""Generate the example artifacts of the reader branch and the statements.

Covers what the Use Statement over a mobile driving license changed: the
verifier X.509 branch of TS-5-04, its certificate revocation list, the Use
Statements of TS-5-06, the Authority Statement answers of TS-5-05, and the
Accreditation Credentials of TS-5-07. Everything it writes lands in
``build/artifacts`` and is injected into ``docs/`` by ``inject.py``.

Run: ``.venv/bin/python scripts/artifacts/build.py``
"""

from __future__ import annotations

import base64
import datetime as dt
import json
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, utils as asym_utils
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID, ObjectIdentifier

from keystore import load_or_create, REPO_ROOT

OUT = REPO_ROOT / "build" / "artifacts"

MDOC_READER_AUTH = ObjectIdentifier("1.0.18013.5.1.6")
READER_AUTH_ROLE = ObjectIdentifier("1.3.6.1.4.1.32473.1.1")

def entity_dids() -> dict[str, str]:
    """The identifier of each entity, from the logs ``logs.py`` generated."""
    path = OUT / "webvh.json"
    if not path.exists():
        raise SystemExit(f"{path} is missing: run scripts/artifacts/logs.py first")
    entities = json.loads(path.read_text())["entities"]
    return {slug: entity["did"] for slug, entity in entities.items()}


DIDS = entity_dids()
TRUST_AUTHORITY = DIDS["trust-authority"]
TERMINAL_NUSANTARA = DIDS["terminal-nusantara"]
DUKCAPIL = DIDS["dukcapil"]
DOMPET = DIDS["dompet-digital-nusantara"]
BKN = DIDS["bkn"]
KORLANTAS = DIDS["korlantas"]
KEMENAG = DIDS["kemenag"]


def utc(year: int, month: int, day: int, hour: int = 0, minute: int = 0) -> dt.datetime:
    return dt.datetime(year, month, day, hour, minute, tzinfo=dt.timezone.utc)


def name(country: str, org: str, common: str) -> x509.Name:
    return x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, country),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, org),
            x509.NameAttribute(NameOID.COMMON_NAME, common),
        ]
    )


def ski_hex(certificate: x509.Certificate) -> str:
    digest = certificate.extensions.get_extension_for_class(
        x509.SubjectKeyIdentifier
    ).value.digest
    return digest.hex().upper()


# ---------------------------------------------------------------- DER helpers


def der_len(length: int) -> bytes:
    if length < 0x80:
        return bytes([length])
    body = length.to_bytes((length.bit_length() + 7) // 8, "big")
    return bytes([0x80 | len(body)]) + body


def der_utf8(value: str) -> bytes:
    raw = value.encode()
    return b"\x0c" + der_len(len(raw)) + raw


def der_seq(*parts: bytes) -> bytes:
    body = b"".join(parts)
    return b"\x30" + der_len(len(body)) + body


def reader_auth_role(entries: list[tuple[str, list[str]]]) -> bytes:
    return der_seq(
        *[
            der_seq(der_utf8(doc_type), der_seq(*[der_utf8(e) for e in elements]))
            for doc_type, elements in entries
        ]
    )


# --------------------------------------------------------------- JOSE helpers


def b64u(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def canonical(obj: dict) -> bytes:
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode()


def jws(header: dict, payload: dict, key: ec.EllipticCurvePrivateKey) -> str:
    signing_input = f"{b64u(canonical(header))}.{b64u(canonical(payload))}".encode()
    der = key.sign(signing_input, ec.ECDSA(hashes.SHA256()))
    r, s = asym_utils.decode_dss_signature(der)
    raw = r.to_bytes(32, "big") + s.to_bytes(32, "big")
    return f"{signing_input.decode()}.{b64u(raw)}"


# ------------------------------------------------------------------- the PKI


# The categories the Warung Bu Ani device is bound to: the tobacco age check
# and the civil servant discount, each read under its mdoc docType.
DEVICE_ROLE = [
    ("id.idctf.ktp.1", ["usia_di_atas_17"]),
    ("org.iso.18013.5.1.mDL", ["age_over_18"]),
    ("id.idctf.kartu-asn.1", ["nama", "instansi"]),
]


def build_verifier_branch() -> dict:
    root_key = load_or_create("verifier-root-ca")
    issuing_key = load_or_create("verifier-issuing-ca")
    device_key = load_or_create("verifier-device-warung-bu-ani")

    root_name = name("ID", "Trust Authority Republik Indonesia", "IDCTF Verifier Root CA")
    issuing_name = name("ID", "Terminal Nusantara", "Terminal Nusantara Verifier Issuing CA")
    device_name = name("ID", "Terminal Nusantara", "Warung Bu Ani")

    root = (
        x509.CertificateBuilder()
        .subject_name(root_name)
        .issuer_name(root_name)
        .public_key(root_key.public_key())
        .serial_number(0x2FD61D5785EF16C777E4CB5F)
        .not_valid_before(utc(2026, 1, 1))
        .not_valid_after(utc(2041, 1, 1))
        .add_extension(x509.BasicConstraints(ca=True, path_length=1), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=False,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=True,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(
            x509.SubjectKeyIdentifier.from_public_key(root_key.public_key()), critical=False
        )
        .add_extension(
            x509.IssuerAlternativeName([x509.UniformResourceIdentifier("https://trust.go.id")]),
            critical=False,
        )
        .add_extension(
            x509.CRLDistributionPoints(
                [
                    x509.DistributionPoint(
                        full_name=[
                            x509.UniformResourceIdentifier(
                                "https://registry.trust.go.id/crl/verifier-root-ca"
                            )
                        ],
                        relative_name=None,
                        reasons=None,
                        crl_issuer=None,
                    )
                ]
            ),
            critical=False,
        )
        .sign(root_key, hashes.SHA256())
    )

    issuing = (
        x509.CertificateBuilder()
        .subject_name(issuing_name)
        .issuer_name(root_name)
        .public_key(issuing_key.public_key())
        .serial_number(0xB589CDF61B889EBF0A9CCE05)
        .not_valid_before(utc(2026, 6, 1))
        .not_valid_after(utc(2031, 6, 1))
        .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=False,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=True,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(x509.ExtendedKeyUsage([MDOC_READER_AUTH]), critical=False)
        .add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(root_key.public_key()),
            critical=False,
        )
        .add_extension(
            x509.SubjectKeyIdentifier.from_public_key(issuing_key.public_key()), critical=False
        )
        .add_extension(
            x509.CRLDistributionPoints(
                [
                    x509.DistributionPoint(
                        full_name=[
                            x509.UniformResourceIdentifier(
                                "https://registry.trust.go.id/crl/verifier-root-ca"
                            )
                        ],
                        relative_name=None,
                        reasons=None,
                        crl_issuer=None,
                    )
                ]
            ),
            critical=False,
        )
        .sign(root_key, hashes.SHA256())
    )

    role = reader_auth_role(DEVICE_ROLE)

    device = (
        x509.CertificateBuilder()
        .subject_name(device_name)
        .issuer_name(issuing_name)
        .public_key(device_key.public_key())
        .serial_number(0x598BDB20342F8D4489AB2C0F)
        .not_valid_before(utc(2026, 9, 20))
        .not_valid_after(utc(2028, 9, 19))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(x509.ExtendedKeyUsage([MDOC_READER_AUTH]), critical=True)
        .add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(issuing_key.public_key()),
            critical=False,
        )
        .add_extension(
            x509.SubjectKeyIdentifier.from_public_key(device_key.public_key()), critical=False
        )
        .add_extension(x509.UnrecognizedExtension(READER_AUTH_ROLE, role), critical=False)
        .add_extension(
            x509.CRLDistributionPoints(
                [
                    x509.DistributionPoint(
                        full_name=[
                            x509.UniformResourceIdentifier(
                                "https://terminal-nusantara.co.id/crl/verifier-issuing-ca"
                            )
                        ],
                        relative_name=None,
                        reasons=None,
                        crl_issuer=None,
                    )
                ]
            ),
            critical=False,
        )
        .sign(issuing_key, hashes.SHA256())
    )

    # The device the list below revokes: the same merchant's earlier terminal,
    # replaced and then revoked. Without it the revoked serial names nothing.
    retired_key = load_or_create("verifier-device-warung-bu-ani-retired")
    retired_role = reader_auth_role(DEVICE_ROLE[:2])
    retired = (
        x509.CertificateBuilder()
        .subject_name(device_name)
        .issuer_name(issuing_name)
        .public_key(retired_key.public_key())
        .serial_number(0x80D376F5BF5FC52A9BC78E9D)
        .not_valid_before(utc(2025, 10, 1))
        .not_valid_after(utc(2027, 9, 30))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(x509.ExtendedKeyUsage([MDOC_READER_AUTH]), critical=True)
        .add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(issuing_key.public_key()),
            critical=False,
        )
        .add_extension(
            x509.SubjectKeyIdentifier.from_public_key(retired_key.public_key()), critical=False
        )
        .add_extension(x509.UnrecognizedExtension(READER_AUTH_ROLE, retired_role), critical=False)
        .add_extension(
            x509.CRLDistributionPoints(
                [
                    x509.DistributionPoint(
                        full_name=[
                            x509.UniformResourceIdentifier(
                                "https://terminal-nusantara.co.id/crl/verifier-issuing-ca"
                            )
                        ],
                        relative_name=None,
                        reasons=None,
                        crl_issuer=None,
                    )
                ]
            ),
            critical=False,
        )
        .sign(issuing_key, hashes.SHA256())
    )

    crl = (
        x509.CertificateRevocationListBuilder()
        .issuer_name(issuing_name)
        .last_update(utc(2026, 10, 15))
        .next_update(utc(2026, 10, 16))
        .add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(issuing_key.public_key()),
            critical=False,
        )
        .add_extension(x509.CRLNumber(31), critical=False)
        .add_revoked_certificate(
            x509.RevokedCertificateBuilder()
            .serial_number(0x80D376F5BF5FC52A9BC78E9D)
            .revocation_date(utc(2026, 10, 12))
            .build()
        )
        .sign(issuing_key, hashes.SHA256())
    )

    return {
        "root": root,
        "issuing": issuing,
        "device": device,
        "retired": retired,
        "crl": crl,
        "reader_auth_role": role,
    }


# ------------------------------------------------------------- the statements

USE_STATEMENT_KID = f"{TRUST_AUTHORITY}#use-statement-1"
AUTHORITY_KID = f"{TRUST_AUTHORITY}#authority-statement-1"
ACCREDITATION_KID = f"{TRUST_AUTHORITY}#accreditation-credential-1"

USE_STATEMENTS = [
    {
        "iss": TRUST_AUTHORITY,
        "sub": TERMINAL_NUSANTARA,
        "use_id": "kategori-tembakau",
        "purpose": {
            "id": "Verifikasi usia pembeli produk tembakau",
            "en": "Age verification for the purchase of tobacco products",
        },
        "legal_basis": "PP 109/2012 Pasal 25 huruf b",
        "claims": [
            "id.idctf.ktp.1#usia_di_atas_17",
            "org.iso.18013.5.1.mDL.1#age_over_18",
        ],
        "status": {
            "status_list": {
                "idx": 812,
                "uri": "https://registry.trust.go.id/status/use-statements-1",
            }
        },
        "iat": 1776470400,
        "exp": 1808006400,
    },
    {
        "iss": TRUST_AUTHORITY,
        "sub": TERMINAL_NUSANTARA,
        "use_id": "penukaran-valas",
        "purpose": {
            "id": "Verifikasi identitas penukaran valuta asing",
            "en": "Identity verification for a foreign exchange transaction",
        },
        "legal_basis": "Ketentuan APU PPT sektor jasa keuangan",
        "claims": ["id.idctf.ktp.1#nik", "id.idctf.ktp.1#nama"],
        "status": {
            "status_list": {
                "idx": 4219,
                "uri": "https://registry.trust.go.id/status/use-statements-1",
            }
        },
        "iat": 1777852800,
        "exp": 1809388800,
    },
    {
        "iss": TRUST_AUTHORITY,
        "sub": TERMINAL_NUSANTARA,
        "use_id": "tarif-dinas-asn",
        "purpose": {
            "id": "Verifikasi status ASN untuk tarif perjalanan dinas",
            "en": "Civil servant status check for the official travel fare",
        },
        "legal_basis": "Perjanjian kerja sama tarif perjalanan dinas dengan instansi pemerintah",
        "claims": [
            "id.idctf.kartu-asn.1#nama",
            "id.idctf.kartu-asn.1#nip",
            "id.idctf.kartu-asn.1#instansi",
        ],
        "status": {
            "status_list": {
                "idx": 6350,
                "uri": "https://registry.trust.go.id/status/use-statements-1",
            }
        },
        "iat": 1780272000,
        "exp": 1811808000,
    },
    {
        "iss": TRUST_AUTHORITY,
        "sub": TERMINAL_NUSANTARA,
        "use_id": "pencatatan-ahli-waris",
        "purpose": {
            "id": "Verifikasi status perkawinan untuk pencatatan ahli waris",
            "en": "Verification of marital status for recording a beneficiary",
        },
        "legal_basis": "Perjanjian layanan dengan pengguna untuk pencatatan ahli waris",
        "claims": [
            "id.idctf.kartu-nikah.1#nama_suami",
            "id.idctf.kartu-nikah.1#nama_istri",
            "id.idctf.kartu-nikah.1#tanggal_akad",
            "id.idctf.kartu-nikah.1#nomor_akta_nikah",
            "id.idctf.kartu-nikah.1#kua",
            "id.idctf.kartu-nikah.1#kabupaten_kota",
            "id.idctf.kartu-nikah.1#provinsi",
        ],
        "status": {
            "status_list": {
                "idx": 7408,
                "uri": "https://registry.trust.go.id/status/use-statements-1",
            }
        },
        "iat": 1782864000,
        "exp": 1814400000,
    },
    {
        "iss": TRUST_AUTHORITY,
        "sub": TERMINAL_NUSANTARA,
        "use_id": "kategori-diskon-asn",
        "purpose": {
            "id": "Verifikasi status ASN untuk potongan harga",
            "en": "Civil servant status check for a discount",
        },
        "legal_basis": "Perjanjian kerja sama program potongan harga ASN dengan pedagang mitra",
        "claims": [
            "id.idctf.kartu-asn.1#nama",
            "id.idctf.kartu-asn.1#instansi",
        ],
        "status": {
            "status_list": {
                "idx": 9031,
                "uri": "https://registry.trust.go.id/status/use-statements-1",
            }
        },
        "iat": 1792022400,
        "exp": 1823558400,
    },
]

ANSWERS = [
    {
        "authority_id": TRUST_AUTHORITY,
        "entity_id": DUKCAPIL,
        "action": "issue",
        "resource": "id.idctf.ktp.1",
        "authorized": True,
        "time_evaluated": "2026-10-17T03:11:20Z",
        "message": "Granted 2026-02-01T00:00:00Z.",
        "periods": [{"valid_from": "2026-02-01T00:00:00Z"}],
    },
    {
        "authority_id": TRUST_AUTHORITY,
        "entity_id": TERMINAL_NUSANTARA,
        "action": "request",
        "resource": "id.idctf.ktp.1#usia_di_atas_17",
        "authorized": True,
        "time_requested": "2026-09-01T00:00:00Z",
        "time_evaluated": "2026-10-17T03:11:20Z",
        "context": {"time": "2026-09-01T00:00:00Z"},
        "message": "Granted 2026-03-01T00:00:00Z.",
        "periods": [
            {"valid_from": "2026-04-10T00:00:00Z"},
            {"valid_from": "2026-03-01T00:00:00Z", "valid_until": "2026-04-01T00:00:00Z"},
        ],
    },
    {
        "authority_id": TRUST_AUTHORITY,
        "entity_id": TERMINAL_NUSANTARA,
        "action": "request",
        "resource": "org.iso.18013.5.1.mDL.1#age_over_18",
        "authorized": True,
        "time_evaluated": "2026-10-17T03:11:20Z",
        "message": "Granted 2026-03-01T00:00:00Z.",
        "periods": [{"valid_from": "2026-03-01T00:00:00Z"}],
    },
    {
        "authority_id": TRUST_AUTHORITY,
        "entity_id": KORLANTAS,
        "action": "issue",
        "resource": "org.iso.18013.5.1.mDL.1",
        "authorized": True,
        "time_evaluated": "2026-10-17T03:11:20Z",
        "message": "Granted 2026-03-01T00:00:00Z.",
        "periods": [{"valid_from": "2026-03-01T00:00:00Z"}],
    },
    {
        "authority_id": TRUST_AUTHORITY,
        "entity_id": BKN,
        "action": "issue",
        "resource": "id.idctf.kartu-asn.1",
        "authorized": True,
        "time_evaluated": "2026-10-17T03:11:20Z",
        "message": "Granted 2026-03-01T00:00:00Z.",
        "periods": [{"valid_from": "2026-03-01T00:00:00Z"}],
    },
    {
        "authority_id": TRUST_AUTHORITY,
        "entity_id": KEMENAG,
        "action": "issue",
        "resource": "id.idctf.kartu-nikah.1",
        "authorized": True,
        "time_evaluated": "2026-10-17T03:11:20Z",
        "message": "Granted 2026-03-01T00:00:00Z.",
        "periods": [{"valid_from": "2026-03-01T00:00:00Z"}],
    },
    {
        "authority_id": TRUST_AUTHORITY,
        "entity_id": BKN,
        "action": "issue",
        "resource": "id.idctf.kartu-nikah.1",
        "authorized": False,
        "time_evaluated": "2026-10-17T03:11:20Z",
        "message": "Not granted.",
        "periods": [],
    },
]

ACCREDITATIONS = [
    {
        "iss": TRUST_AUTHORITY,
        "vct": "id.idctf.accreditation.1",
        "sub": DUKCAPIL,
        "entity_name": "Direktorat Jenderal Kependudukan dan Pencatatan Sipil",
        "entity_type": ["https://idctf.id/ns/19602/SvcType/IdentityIssuer"],
        "scope": [{"action": "issue", "resource": "id.idctf.ktp.1"}],
        "status": {
            "status_list": {
                "idx": 17,
                "uri": "https://registry.trust.go.id/status/accreditations-1",
            }
        },
        "iat": 1769904000,
        "exp": 1832976000,
    },
    {
        "iss": TRUST_AUTHORITY,
        "vct": "id.idctf.accreditation.1",
        "sub": TERMINAL_NUSANTARA,
        "entity_name": "PT Terminal Nusantara",
        "entity_type": ["https://idctf.id/ns/19602/SvcType/RelyingParty"],
        "scope": [
            {"action": "request", "resource": "id.idctf.ktp.1#usia_di_atas_17"},
            {"action": "request", "resource": "id.idctf.ktp.1#nik"},
            {"action": "request", "resource": "id.idctf.ktp.1#nama"},
            {"action": "request", "resource": "org.iso.18013.5.1.mDL.1#age_over_18"},
            {"action": "request", "resource": "id.idctf.kartu-asn.1#nama"},
            {"action": "request", "resource": "id.idctf.kartu-asn.1#nip"},
            {"action": "request", "resource": "id.idctf.kartu-asn.1#instansi"},
            {"action": "request", "resource": "id.idctf.kartu-nikah.1"},
        ],
        "status": {
            "status_list": {
                "idx": 42,
                "uri": "https://registry.trust.go.id/status/accreditations-1",
            }
        },
        "iat": 1772323200,
        "exp": 1835481600,
    },
    {
        "iss": TRUST_AUTHORITY,
        "vct": "id.idctf.accreditation.1",
        "sub": DOMPET,
        "entity_name": "PT Dompet Digital Nusantara",
        "entity_type": ["https://idctf.id/ns/19602/SvcType/WalletProvider"],
        "scope": [],
        "status": {
            "status_list": {
                "idx": 8,
                "uri": "https://registry.trust.go.id/status/accreditations-1",
            }
        },
        "iat": 1772323200,
        "exp": 1835481600,
    },
]


def statement_payload(answer: dict) -> dict:
    """The signed payload of an answer: its members, without the two the
    answer adds around the signature, with the periods the permission was in
    force (a claim of the payload alone), and with the lifetime of the answer."""
    payload = {k: v for k, v in answer.items() if k not in ("message", "context")}
    payload["iat"] = 1792206680
    payload["exp"] = 1792249880
    return payload


def previous_summary() -> dict:
    """What the last run wrote, or nothing on the first run."""
    path = OUT / "summary.json"
    return json.loads(path.read_text()) if path.exists() else {}


def reuse_or_sign(
    stored: list[str], header: dict, payload: dict, key: ec.EllipticCurvePrivateKey
) -> str:
    """The stored token for this header and payload, or a new signature.

    Signing is randomized, so re-signing an unchanged payload would rewrite a
    page for nothing, and a copy of the token quoted elsewhere would fall out
    of step with it. A token is signed again only when what it says changes.
    """
    want = f"{b64u(canonical(header))}.{b64u(canonical(payload))}"
    for token in stored:
        if token.startswith(want + "."):
            return token
    return jws(header, payload, key)


def same_certificate(stored: x509.Certificate, built: x509.Certificate) -> bool:
    """Whether a stored certificate is the one just built, bar its signature."""
    pem = serialization.Encoding.PEM
    return (
        stored.subject == built.subject
        and stored.issuer == built.issuer
        and stored.serial_number == built.serial_number
        and stored.not_valid_before_utc == built.not_valid_before_utc
        and [(e.oid, e.critical, e.value) for e in stored.extensions]
        == [(e.oid, e.critical, e.value) for e in built.extensions]
        and stored.public_key().public_bytes(
            pem, serialization.PublicFormat.SubjectPublicKeyInfo
        )
        == built.public_key().public_bytes(
            pem, serialization.PublicFormat.SubjectPublicKeyInfo
        )
    )


def reuse_verifier_branch(pki: dict) -> dict:
    """Keep the certificates already built, so a re-run changes no page.

    ECDSA signing is randomized, so signing the same certificate twice gives
    two different files. The trusted list carries one of these certificates,
    so a gratuitous re-signature would ripple into another page. A stored
    certificate is reused whenever it is the one this run would have built.
    """
    for label, key in (
        ("verifier-root-ca", "root"),
        ("verifier-issuing-ca", "issuing"),
        ("verifier-device", "device"),
        ("verifier-device-retired", "retired"),
    ):
        path = OUT / f"{label}.pem"
        if not path.exists():
            continue
        stored = x509.load_pem_x509_certificate(path.read_bytes())
        if same_certificate(stored, pki[key]):
            pki[key] = stored
    crl_path = OUT / "verifier-issuing-ca.crl"
    if crl_path.exists():
        stored_crl = x509.load_pem_x509_crl(crl_path.read_bytes())
        if (
            stored_crl.issuer == pki["crl"].issuer
            and stored_crl.last_update_utc == pki["crl"].last_update_utc
            and stored_crl.next_update_utc == pki["crl"].next_update_utc
            and stored_crl.is_signature_valid(pki["issuing"].public_key())
        ):
            pki["crl"] = stored_crl
    return pki


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    pki = reuse_verifier_branch(build_verifier_branch())

    pem = serialization.Encoding.PEM
    der = serialization.Encoding.DER
    for label, certificate in (
        ("verifier-root-ca", pki["root"]),
        ("verifier-issuing-ca", pki["issuing"]),
        ("verifier-device", pki["device"]),
        ("verifier-device-retired", pki["retired"]),
    ):
        (OUT / f"{label}.pem").write_bytes(certificate.public_bytes(pem))
    (OUT / "verifier-issuing-ca.crl").write_bytes(pki["crl"].public_bytes(pem))

    use_key = load_or_create("ta-use-statement")
    authority_key = load_or_create("ta-authority-statement")
    accreditation_key = load_or_create("ta-accreditation-credential")
    stored = previous_summary()

    use_statements = [
        reuse_or_sign(
            stored.get("use_statements", []),
            {
                "typ": "vnd.id.idctf.use-statement+jwt",
                "alg": "ES256",
                "kid": USE_STATEMENT_KID,
            },
            payload,
            use_key,
        )
        for payload in USE_STATEMENTS
    ]

    answers = []
    for index, answer in enumerate(ANSWERS):
        signed = {k: v for k, v in answer.items() if k != "periods"}
        previous = [a["statement"] for a in stored.get("answers", []) if "statement" in a]
        signed["statement"] = reuse_or_sign(
            previous,
            {
                "typ": "vnd.id.idctf.authority-statement+jwt",
                "alg": "ES256",
                "kid": AUTHORITY_KID,
            },
            statement_payload(answer),
            authority_key,
        )
        answers.append(signed)

    accreditations = [
        reuse_or_sign(
            [a.rstrip("~") for a in stored.get("accreditations", [])],
            {"typ": "dc+sd-jwt", "alg": "ES256", "kid": ACCREDITATION_KID},
            payload,
            accreditation_key,
        )
        + "~"
        for payload in ACCREDITATIONS
    ]

    summary = {
        "verifier_root_ca": {
            "ski": ski_hex(pki["root"]),
            "der_size": len(pki["root"].public_bytes(der)),
        },
        "verifier_issuing_ca": {
            "ski": ski_hex(pki["issuing"]),
            "der_size": len(pki["issuing"].public_bytes(der)),
            "base64": base64.b64encode(pki["issuing"].public_bytes(der)).decode(),
        },
        "verifier_device": {
            "ski": ski_hex(pki["device"]),
            "der_size": len(pki["device"].public_bytes(der)),
            "reader_auth_role_hex": pki["reader_auth_role"].hex().upper(),
            "reader_auth_role_size": len(pki["reader_auth_role"]),
        },
        "verifier_device_retired": {
            "ski": ski_hex(pki["retired"]),
            "der_size": len(pki["retired"].public_bytes(der)),
            "serial_hex": f"{pki['retired'].serial_number:024X}",
        },
        "verifier_issuing_ca_crl": {"der_size": len(pki["crl"].public_bytes(der))},
        "use_statements": use_statements,
        "use_statement_payloads": USE_STATEMENTS,
        "answers": answers,
        "accreditations": accreditations,
        "accreditation_payloads": ACCREDITATIONS,
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {OUT}")
    for key, value in summary.items():
        if isinstance(value, dict):
            print(f"  {key}: {', '.join(f'{k}={v}' for k, v in value.items() if k != 'base64')}")


if __name__ == "__main__":
    main()
