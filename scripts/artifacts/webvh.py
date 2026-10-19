"""did:webvh v1.0 primitives for the example artifacts.

Implements the log arithmetic of did:webvh v1.0 (SCID, entry hash, pre-rotation,
Read) and the ``eddsa-jcs-2022`` Data Integrity proofs a log entry and a
witness proof carry, plus the proof of possession fixed in ``tracks/0293``.
Run as a script it replays the logs published in ``docs/`` and prints one line
per check.
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import base58
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.asymmetric.utils import (
    decode_dss_signature,
    encode_dss_signature,
)
from cryptography.hazmat.primitives import hashes

REPO_ROOT = Path(__file__).resolve().parents[2]
TS_DIR = REPO_ROOT / "docs" / "technical-specifications"

ED25519_PREFIX = b"\xed\x01"
P256_PREFIX = b"\x80\x24"
POP_TYP = "vnd.id.idctf.key-pop+jwt"


def jcs(obj) -> bytes:
    """Canonical JSON of RFC 8785, for the string and integer values used here."""
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()


def _sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def multihash_b58(data: bytes) -> str:
    """SHA-256 multihash of ``data``, base58btc, the ``Qm`` form."""
    return base58.b58encode(b"\x12\x20" + _sha256(data)).decode()


def multikey(public_key) -> str:
    """Multikey string of an Ed25519 (``z6Mk``) or P-256 (``zDna``) public key."""
    if isinstance(public_key, Ed25519PublicKey):
        raw = public_key.public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw
        )
        prefix = ED25519_PREFIX
    elif isinstance(public_key, ec.EllipticCurvePublicKey):
        raw = public_key.public_bytes(
            serialization.Encoding.X962, serialization.PublicFormat.CompressedPoint
        )
        prefix = P256_PREFIX
    else:
        raise ValueError("unsupported key type")
    return "z" + base58.b58encode(prefix + raw).decode()


def public_key_from_multikey(value: str):
    """Public key object a Multikey string encodes."""
    if not value.startswith("z"):
        raise ValueError("Multikey is not base58btc")
    data = base58.b58decode(value[1:])
    prefix, raw = data[:2], data[2:]
    if prefix == ED25519_PREFIX and len(raw) == 32:
        return Ed25519PublicKey.from_public_bytes(raw)
    if prefix == P256_PREFIX and len(raw) == 33:
        return ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), raw)
    raise ValueError("unsupported Multikey prefix or length")


def did_key(multikey_string: str) -> str:
    return f"did:key:{multikey_string}"


def scid_of(first_entry: dict) -> str:
    """SCID of a log, from its first entry (``{SCID}`` placeholders in place or not)."""
    entry = {k: v for k, v in first_entry.items() if k != "proof"}
    scid = entry["parameters"]["scid"]
    text = jcs(entry).decode().replace(scid, "{SCID}")
    entry = json.loads(text)
    entry["versionId"] = "{SCID}"
    return multihash_b58(jcs(entry))


def entry_hash(entry: dict, previous_version_id: str) -> str:
    """Hash half of an entry's ``versionId``, given the previous ``versionId``."""
    body = {k: v for k, v in entry.items() if k != "proof"}
    body["versionId"] = previous_version_id
    return multihash_b58(jcs(body))


def next_key_hash(multikey_string: str) -> str:
    """Pre-rotation hash a ``nextKeyHashes`` member holds."""
    return multihash_b58(multikey_string.encode())


def _sign_di(document, private_key: Ed25519PrivateKey, verification_method: str) -> dict:
    config = {
        "type": "DataIntegrityProof",
        "cryptosuite": "eddsa-jcs-2022",
        "verificationMethod": verification_method,
        "proofPurpose": "assertionMethod",
    }
    signature = private_key.sign(_sha256(jcs(config)) + _sha256(jcs(document)))
    return {**config, "proofValue": "z" + base58.b58encode(signature).decode()}


def _verify_di(document, proof: dict) -> bool:
    try:
        if (
            proof["type"] != "DataIntegrityProof"
            or proof["cryptosuite"] != "eddsa-jcs-2022"
            or proof["proofPurpose"] != "assertionMethod"
        ):
            return False
        method = proof["verificationMethod"]
        key_part, _, fragment = method.removeprefix("did:key:").partition("#")
        if not method.startswith("did:key:") or fragment != key_part:
            return False
        key = public_key_from_multikey(key_part)
        if not isinstance(key, Ed25519PublicKey):
            return False
        config = {k: v for k, v in proof.items() if k != "proofValue"}
        signature = base58.b58decode(proof["proofValue"][1:])
        key.verify(signature, _sha256(jcs(config)) + _sha256(jcs(document)))
        return True
    except (InvalidSignature, KeyError, ValueError, TypeError):
        return False


def sign_entry_proof(
    entry_without_proof: dict, update_private_key: Ed25519PrivateKey, verification_method: str
) -> dict:
    """Data Integrity proof over a log entry, which carries no ``proof`` yet.

    The signing input is SHA-256 of the canonical proof configuration followed
    by SHA-256 of the canonical entry. The configuration holds ``type``,
    ``cryptosuite``, ``verificationMethod`` and ``proofPurpose``.
    """
    return _sign_di(entry_without_proof, update_private_key, verification_method)


def verify_entry_proof(entry: dict, proof: dict) -> bool:
    """Check ``proof`` against ``entry`` with its ``proof`` member removed."""
    return _verify_di({k: v for k, v in entry.items() if k != "proof"}, proof)


def witness_proof(version_id: str, witness_private_key: Ed25519PrivateKey) -> dict:
    """Witness proof over the document ``{"versionId": version_id}``."""
    key_string = multikey(witness_private_key.public_key())
    method = f"{did_key(key_string)}#{key_string}"
    return _sign_di({"versionId": version_id}, witness_private_key, method)


def verify_witness_proof(version_id: str, proof: dict) -> bool:
    return _verify_di({"versionId": version_id}, proof)


def _b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _unb64u(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def pop_jws(private_key, kid: str, aud: str, nonce: str, iat: int) -> str:
    """Proof of possession of ``tracks/0293``: a compact JWS, EdDSA or ES256."""
    if isinstance(private_key, Ed25519PrivateKey):
        alg = "EdDSA"
    elif isinstance(private_key, ec.EllipticCurvePrivateKey):
        alg = "ES256"
    else:
        raise ValueError("unsupported key type")
    header = {"typ": POP_TYP, "alg": alg, "kid": kid}
    payload = {"aud": aud, "nonce": nonce, "iat": iat}
    signing_input = (
        _b64u(json.dumps(header, separators=(",", ":")).encode())
        + "."
        + _b64u(json.dumps(payload, separators=(",", ":")).encode())
    )
    data = signing_input.encode()
    if alg == "EdDSA":
        signature = private_key.sign(data)
    else:
        r, s = decode_dss_signature(private_key.sign(data, ec.ECDSA(hashes.SHA256())))
        signature = r.to_bytes(32, "big") + s.to_bytes(32, "big")
    return signing_input + "." + _b64u(signature)


def verify_pop(token: str, public_key) -> bool:
    """Check a proof of possession against the key it claims."""
    try:
        head, body, sig = token.split(".")
        header = json.loads(_unb64u(head))
        if header.get("typ") != POP_TYP:
            return False
        signature = _unb64u(sig)
        data = f"{head}.{body}".encode()
        if header.get("alg") == "EdDSA" and isinstance(public_key, Ed25519PublicKey):
            public_key.verify(signature, data)
        elif header.get("alg") == "ES256" and isinstance(
            public_key, ec.EllipticCurvePublicKey
        ):
            if len(signature) != 64:
                return False
            der = encode_dss_signature(
                int.from_bytes(signature[:32], "big"),
                int.from_bytes(signature[32:], "big"),
            )
            public_key.verify(der, data, ec.ECDSA(hashes.SHA256()))
        else:
            return False
        return True
    except (InvalidSignature, ValueError, KeyError, TypeError):
        return False


def read_log(entries: list[dict]) -> dict:
    """Read a whole log. Return the final DID Document state or raise ``ValueError``."""
    if not entries:
        raise ValueError("log is empty")
    scid = entries[0].get("parameters", {}).get("scid")
    if not scid:
        raise ValueError("entry 1: parameters carry no scid")
    if scid_of(entries[0]) != scid:
        raise ValueError("entry 1: scid does not match the first entry")
    update_keys: list[str] = []
    next_hashes: list[str] = []
    previous_id = scid
    previous_time = None
    for n, entry in enumerate(entries, start=1):
        label = f"entry {n}"
        params = entry.get("parameters", {})
        number, _, digest = entry.get("versionId", "").partition("-")
        if number != str(n):
            raise ValueError(f"{label}: version number is not {n}")
        if entry_hash(entry, previous_id) != digest:
            raise ValueError(f"{label}: versionId hash does not match the entry")
        time = entry.get("versionTime", "")
        try:
            parsed = datetime.fromisoformat(time.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError(f"{label}: versionTime is not a timestamp") from None
        if previous_time is not None and parsed < previous_time:
            raise ValueError(f"{label}: versionTime precedes the previous entry")
        previous_time = parsed
        authorized = update_keys
        if "updateKeys" in params:
            new_keys = params["updateKeys"]
            if next_hashes:
                for key in new_keys:
                    if next_key_hash(key) not in next_hashes:
                        raise ValueError(f"{label}: updateKeys not committed by nextKeyHashes")
                authorized = new_keys
            elif n == 1:
                authorized = new_keys
            update_keys = new_keys
        if "nextKeyHashes" in params:
            next_hashes = params["nextKeyHashes"]
        if not authorized:
            raise ValueError(f"{label}: no update key is in force")
        proofs = entry.get("proof", [])
        if not proofs:
            raise ValueError(f"{label}: entry carries no proof")
        for proof in proofs:
            key = proof.get("verificationMethod", "").removeprefix("did:key:").split("#")[0]
            if key not in authorized:
                raise ValueError(f"{label}: proof key is not an authorized update key")
            if not verify_entry_proof(entry, proof):
                raise ValueError(f"{label}: proof does not verify")
        previous_id = entry["versionId"]
    return entries[-1]["state"]


def _block(page: Path, title_start: str) -> str:
    text = page.read_text()
    match = re.search(r"title=\"" + re.escape(title_start) + r"[^\n]*\n(.*?)\n```", text, re.S)
    if not match:
        raise ValueError(f"no block titled {title_start!r} in {page.name}")
    return match.group(1)


def main() -> int:
    page = TS_DIR / "publishing-and-resolving-a-did-webvh-identifier.md"
    witness_page = TS_DIR / "witnessing-a-log-entry-and-serving-its-copy.md"
    entries = [
        json.loads(line)
        for line in _block(page, "did.jsonl").splitlines()
        if line.strip()
    ]
    witness = json.loads(_block(witness_page, "did-witness.json, the proof"))
    checks: list[tuple[str, bool]] = []

    def check(label: str, ok: bool) -> None:
        checks.append((label, ok))
        print(f"{'OK' if ok else 'FAIL'}  {label}")

    try:
        read_log(entries)
        check("read_log: scid, hashes, chain, pre-rotation, times, proofs", True)
    except ValueError as error:
        check(f"read_log: {error}", False)
    for n, entry in enumerate(entries, start=1):
        check(f"entry {n} proof", verify_entry_proof(entry, entry["proof"][0]))
    check(
        "witness proof",
        verify_witness_proof(witness["versionId"], witness["proof"][0])
        and witness["versionId"] == entries[-1]["versionId"],
    )
    return 0 if all(ok for _, ok in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
