"""Generate the signed examples of TS-4-02.

Two artifacts the Trust Registry interface carries and no other page does:
the answers to a recognition query, signed with Trust Authority's
Recognition Statement key, and the catalog list, signed with its catalog
key. The authorization answers TS-4-02 shows are the ones TS-5-05 already
carries, so they are not signed here.

Everything lands in ``build/artifacts/trqp.json``. The script verifies what
it wrote before it exits, and ``verify_artifacts.py`` checks the copies
pasted into ``docs/``.

Run: ``.venv/bin/python scripts/artifacts/trqp.py``
"""

from __future__ import annotations

import base64
import hashlib
import json

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, utils as asym_utils

from build import OUT, TRUST_AUTHORITY, b64u, jws
from keystore import REPO_ROOT, load_or_create

RECOGNITION_KID = f"{TRUST_AUTHORITY}#recognition-statement-1"
CATALOG_KID = f"{TRUST_AUTHORITY}#catalog-1"
RECOGNITION_TYP = "vnd.id.idctf.recognition-statement+jwt"
CATALOG_TYP = "vnd.id.idctf.catalog+jwt"

# 2026-10-17T03:11:20Z, the time_evaluated every TS-5-05 answer carries.
IAT = 1792206680
ANSWER_TTL = 43200
CATALOG_TTL = 86400

CATALOG = "https://catalog.trust.go.id"
EXAMPLES = REPO_ROOT / "docs" / "credential-rulebook" / "example"

# The five illustrative Rulebooks, in the order the catalog index lists them.
RULEBOOKS = [
    ("id.idctf.ktp.1", "ktp-digital"),
    ("id.idctf.kartu-indonesia-sehat.1", "kartu-indonesia-sehat"),
    ("id.idctf.kartu-asn.1", "kartu-asn"),
    ("id.idctf.kartu-nikah.1", "kartu-nikah"),
    ("org.iso.18013.5.1.mDL.1", "sim"),
]

RECOGNITIONS = [
    {
        "authority_id": TRUST_AUTHORITY,
        "entity_id": "did:web:trust-registry.partner.example",
        "action": "issue",
        "resource": "org.iso.18013.5.1.mDL.1",
        "recognized": True,
        "time_evaluated": "2026-10-17T03:11:20Z",
        "message": "Recognized 2026-03-01T00:00:00Z.",
    },
    {
        "authority_id": TRUST_AUTHORITY,
        "entity_id": "did:web:registry.other-ecosystem.example",
        "action": "issue",
        "resource": "org.iso.18013.5.1.mDL.1",
        "recognized": False,
        "time_requested": "2026-09-01T00:00:00Z",
        "time_evaluated": "2026-10-17T03:11:20Z",
        "context": {"time": "2026-09-01T00:00:00Z"},
    },
]

SIGNED_MEMBERS = (
    "authority_id", "entity_id", "action", "resource",
    "recognized", "time_requested", "time_evaluated",
)


def sri_sha384(data: bytes) -> str:
    return "sha384-" + base64.b64encode(hashlib.sha384(data).digest()).decode()


def statement_payload(answer: dict) -> dict:
    payload = {k: answer[k] for k in SIGNED_MEMBERS if k in answer}
    payload["iat"] = IAT
    payload["exp"] = IAT + ANSWER_TTL
    return payload


def catalog_payload() -> dict:
    entries = []
    for type_id, folder in RULEBOOKS:
        raw = (EXAMPLES / folder / "rulebook.json").read_bytes()
        if json.loads(raw)["id"] != type_id:
            raise SystemExit(f"{folder}/rulebook.json does not carry id {type_id}")
        entries.append(
            {
                "id": type_id,
                "rulebook": f"{CATALOG}/rulebooks/{type_id}",
                "rulebook_digest": sri_sha384(raw),
            }
        )
    return {
        "iss": TRUST_AUTHORITY,
        "iat": IAT,
        "exp": IAT + CATALOG_TTL,
        "rulebooks": entries,
    }


def verify_jws(token: str, key: ec.EllipticCurvePublicKey, typ: str, kid: str) -> dict:
    header_b64, payload_b64, sig_b64 = token.split(".")
    pad = lambda s: s + "=" * (-len(s) % 4)  # noqa: E731
    header = json.loads(base64.urlsafe_b64decode(pad(header_b64)))
    if header != {"typ": typ, "alg": "ES256", "kid": kid}:
        raise SystemExit(f"unexpected header {header}")
    raw = base64.urlsafe_b64decode(pad(sig_b64))
    der = asym_utils.encode_dss_signature(
        int.from_bytes(raw[:32], "big"), int.from_bytes(raw[32:], "big")
    )
    key.verify(der, f"{header_b64}.{payload_b64}".encode(), ec.ECDSA(hashes.SHA256()))
    return json.loads(base64.urlsafe_b64decode(pad(payload_b64)))


def main() -> None:
    recognition_key = load_or_create("ta-recognition-statement")
    catalog_key = load_or_create("ta-catalog")

    # Signing is randomized, so a signature already written is kept while it
    # still verifies over the same payload; the pasted bytes then never move.
    path = OUT / "trqp.json"
    previous = json.loads(path.read_text()) if path.exists() else {}

    def reuse(token: str | None, key, typ: str, kid: str, payload: dict) -> str | None:
        if not token:
            return None
        try:
            return token if verify_jws(token, key.public_key(), typ, kid) == payload else None
        except Exception:  # noqa: BLE001
            return None

    answers = []
    stored = previous.get("recognitions", [])
    for i, answer in enumerate(RECOGNITIONS):
        header = {"typ": RECOGNITION_TYP, "alg": "ES256", "kid": RECOGNITION_KID}
        signed = dict(answer)
        old = stored[i]["statement"] if i < len(stored) else None
        signed["statement"] = reuse(
            old, recognition_key, RECOGNITION_TYP, RECOGNITION_KID, statement_payload(answer)
        ) or jws(header, statement_payload(answer), recognition_key)
        answers.append(signed)

    catalog = reuse(
        previous.get("catalog"), catalog_key, CATALOG_TYP, CATALOG_KID, catalog_payload()
    ) or jws(
        {"typ": CATALOG_TYP, "alg": "ES256", "kid": CATALOG_KID},
        catalog_payload(),
        catalog_key,
    )

    for answer in answers:
        payload = verify_jws(
            answer["statement"], recognition_key.public_key(), RECOGNITION_TYP, RECOGNITION_KID
        )
        if payload != statement_payload({k: v for k, v in answer.items() if k != "statement"}):
            raise SystemExit("recognition payload does not repeat the answer")
    if verify_jws(catalog, catalog_key.public_key(), CATALOG_TYP, CATALOG_KID) != catalog_payload():
        raise SystemExit("catalog payload mismatch")

    blocks = {
        "The answer to a recognition query that is recognized": json.dumps(answers[0], indent=2),
        "The answer to a recognition query that is not recognized": json.dumps(answers[1], indent=2),
        "The catalog list as served": catalog,
        "Catalog list payload, decoded": json.dumps(catalog_payload(), indent=2),
    }
    out = {
        "recognitions": answers,
        "catalog": catalog,
        "catalog_payload": catalog_payload(),
        "blocks": blocks,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "trqp.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {OUT / 'trqp.json'}: {len(answers)} recognition answers, 1 catalog list, all verified")


if __name__ == "__main__":
    main()
