"""Verify the signed artifacts the Technical Specifications carry.

Reads the pages rather than the build output, so it checks what a reader
gets: the verifier certificate chain and its revocation list, the Use
Statements, the Authority Statement answers, the Accreditation Credentials,
the subject key identifier the trusted list names, and the subset rule that
binds a reader's certificate to the uses its entity registered. Past that
it sweeps every compact JWS in ``docs/``, replays the ``did:webvh`` log and
its witness proof, checks the Publisher request body, the status lists in
both forms, the credentials, the presentations, the Data Integrity proofs,
the issuer X.509 branch and the VICAL, the trusted list, the issuance
exchanges of TS-1-01, and that every identifier two pages share is one value.

DID Documents other than the log TS-5-02 prints come from
``build/artifacts/webvh.json``; keys that sign a statement come from the
keystore. Nothing here touches the network or runs a generator.

Run: ``.venv/bin/python scripts/verify_artifacts.py``
"""

from __future__ import annotations

import base64
import datetime as dt
import functools
import gzip
import hashlib
import json
import re
import sys
import zlib
from pathlib import Path

import cbor2
from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, utils as asym_utils
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "artifacts"))
import ldp  # noqa: E402  (its document loader reads only scripts/artifacts/contexts/)
import presentations  # noqa: E402  (for the diagnostic-notation parser)
import webvh  # noqa: E402

DOCS = ROOT / "docs"
TS = DOCS / "technical-specifications"
ART = ROOT / "build" / "artifacts"

TS_01 = TS / "finding-a-signers-key-from-its-did.md"
TS_4_01 = TS / "witnessing-a-log-entry-and-serving-its-copy.md"
TS_5_02 = TS / "publishing-and-resolving-a-did-webvh-identifier.md"
TS_5_03 = TS / "deriving-a-did-key-and-a-device-identifier.md"
TS_5_08 = TS / "issuing-and-reading-a-key-attestation.md"
TS_2_01 = TS / "enrolling-a-wallet-installation-and-attesting-its-key.md"
TS_5_09 = TS / "publishing-and-reading-a-status-list.md"
TS_5_10 = TS / "issuing-a-credential-in-sd-jwt-vc-mdoc-and-ldp-vc.md"
TS_5_11 = TS / "building-and-verifying-a-presentation.md"
TS_5_01 = TS / "publishing-and-reading-the-trusted-list.md"
TS_02 = TS / "publishing-and-reading-the-governance-profile.md"
TS_5_04 = TS / "issuing-and-validating-the-x509-certificates-and-the-vical.md"
TS_5_05 = TS / "answering-with-an-authority-statement.md"
TS_5_06 = TS / "registering-and-carrying-a-use-statement.md"
TS_5_07 = TS / "issuing-and-carrying-an-accreditation-credential.md"

READER_AUTH_ROLE = x509.ObjectIdentifier("1.3.6.1.4.1.32473.1.1")

failures: list[str] = []
checks = 0


def check(passed: bool, label: str, detail: str = "") -> None:
    global checks
    checks += 1
    if passed:
        print(f"{label:<58} OK")
    else:
        print(f"{label:<58} FAILED")
        if detail:
            print(f"    {detail}")
        failures.append(label)


@functools.cache
def blocks(path: Path) -> dict[str, list[str]]:
    """Every fenced block of ``path``, by the title on its opening line."""
    found: dict[str, list[str]] = {}
    title = None
    body: list[str] = []
    for line in path.read_text().split("\n"):
        if title is None and line.startswith("```") and len(line) > 3:
            match = re.search(r'title="([^"]*)"', line)
            title = match.group(1) if match else ""
            body = []
        elif title is not None and line.strip() == "```":
            found.setdefault(title, []).append("\n".join(body))
            title = None
        elif title is not None:
            body.append(line)
    return found


def certificates(path: Path) -> dict[str, x509.Certificate]:
    out = {}
    for title, bodies in blocks(path).items():
        filename = title.split(",")[0]
        if filename.endswith(".pem") and "BEGIN CERTIFICATE" in bodies[0]:
            out[filename] = x509.load_pem_x509_certificate(bodies[0].encode())
    return out


def verify_chain(child, parent) -> bool:
    try:
        parent.public_key().verify(
            child.signature, child.tbs_certificate_bytes, ec.ECDSA(hashes.SHA256())
        )
        return True
    except InvalidSignature:
        return False


def b64u_decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def jws_parts(token: str) -> tuple[dict, dict, bytes, bytes]:
    header, payload, signature = token.split(".")
    raw = b64u_decode(payload)
    return (
        json.loads(b64u_decode(header)),
        json.loads(raw) if raw else {},  # a read at Trust Authority's entity endpoint signs nothing
        b64u_decode(signature),
        f"{header}.{payload}".encode(),
    )


def verify_raw(public_key, signature: bytes, data: bytes) -> bool:
    """ES256 (``r`` then ``s``) or EdDSA, whichever the key is."""
    try:
        if isinstance(public_key, Ed25519PublicKey):
            public_key.verify(signature, data)
        else:
            if len(signature) != 64:
                return False
            r = int.from_bytes(signature[:32], "big")
            s = int.from_bytes(signature[32:], "big")
            public_key.verify(asym_utils.encode_dss_signature(r, s), data, ec.ECDSA(hashes.SHA256()))
        return True
    except InvalidSignature:
        return False


def verify_jws(token: str, public_key) -> bool:
    _, _, signature, signing_input = jws_parts(token)
    return verify_raw(public_key, signature, signing_input)


def keystore_key(name: str):
    sys.path.insert(0, str(ROOT / "scripts" / "artifacts"))
    from keystore import keystore_dir  # noqa: PLC0415

    path = keystore_dir() / f"{name}.pem"
    if not path.exists():
        return None
    return serialization.load_pem_private_key(path.read_bytes(), password=None).public_key()


def tlv(raw: bytes) -> list[tuple[int, bytes]]:
    """The tag and the contents of every element in one DER sequence body."""
    out = []
    index = 0
    while index < len(raw):
        tag = raw[index]
        length = raw[index + 1]
        if length & 0x80:
            count = length & 0x7F
            length = int.from_bytes(raw[index + 2 : index + 2 + count], "big")
            index += count
        start = index + 2
        out.append((tag, raw[start : start + length]))
        index = start + length
    return out


def reader_auth_role(certificate: x509.Certificate) -> dict[str, set[str]]:
    """The document types and data elements the extension carries."""
    raw = certificate.extensions.get_extension_for_oid(READER_AUTH_ROLE).value.value
    entries = tlv(tlv(raw)[0][1]) if tlv(raw)[0][0] == 0x30 else []
    out: dict[str, set[str]] = {}
    for tag, body in entries:
        if tag != 0x30:
            continue
        members = tlv(body)
        doc_type = members[0][1].decode()
        out[doc_type] = {value.decode() for _, value in tlv(members[1][1])}
    return out


def check_reader_branch() -> None:
    # The two reader-side chains.
    certs = certificates(TS_5_04)
    root = certs["verifier-root-ca.pem"]
    issuing = certs["verifier-issuing-ca.pem"]
    device = certs["verifier-device.pem"]
    check(verify_chain(root, root), "Verifier Root CA self-signature")
    check(verify_chain(issuing, root), "Verifier Issuing CA <- Verifier Root CA")
    check(verify_chain(device, issuing), "Verifier Device Certificate <- Issuing CA")

    crl_body = blocks(TS_5_04)[
        "verifier-issuing-ca.crl, served at "
        "https://terminal-nusantara.co.id/crl/verifier-issuing-ca"
    ][0]
    crl = x509.load_pem_x509_crl(crl_body.encode())
    check(crl.is_signature_valid(issuing.public_key()), "Verifier Issuing CA revocation list")

    # The identifier the trusted list names for that intermediate.
    issuing_ski = (
        issuing.extensions.get_extension_for_class(x509.SubjectKeyIdentifier)
        .value.digest.hex()
        .upper()
    )
    trusted_list = TS_5_01.read_text()
    check(
        f'"X509SKIs": ["{issuing_ski}"]' in trusted_list,
        "Trusted list names the Issuing CA subject key identifier",
    )
    issuing_b64 = base64.b64encode(issuing.public_bytes(serialization.Encoding.DER)).decode()
    check(issuing_b64 in trusted_list, "Trusted list carries the Issuing CA certificate")

    # The two blocks that repeat an artifact in another encoding.
    role_hex = "".join(
        blocks(TS_5_04)["The ReaderAuthRole of verifier-device.pem, as DER"][0]
        .split("\n\n")[-1]
        .split()
    )
    extension = device.extensions.get_extension_for_oid(READER_AUTH_ROLE).value.value
    check(role_hex.lower() == extension.hex(), "ReaderAuthRole hex matches the certificate")

    items_hex = "".join(blocks(TS_5_06)["The same ItemsRequest, as CBOR"][0].split())
    items_request = cbor2.loads(bytes.fromhex(items_hex))
    carried = items_request["requestInfo"]["idUseStatement"].decode()
    check(
        carried == blocks(TS_5_06)["The same statement, as the verifier carries it"][0].strip(),
        "ItemsRequest carries the business category statement",
    )
    mdl_hex = "".join(
        blocks(TS_5_06)["The same mobile driving license ItemsRequest, as CBOR"][0].split()
    )
    mdl_request = cbor2.loads(bytes.fromhex(mdl_hex))
    check(
        mdl_request["requestInfo"]["idUseStatement"].decode() == carried,
        "mobile driving license ItemsRequest carries the same statement",
    )
    check(
        mdl_request["docType"] == "org.iso.18013.5.1.mDL"
        and "org.iso.18013.5.1.mDL.1#age_over_18"
        in json.loads(base64.urlsafe_b64decode(carried.split(".")[1] + "=="))["claims"],
        "mobile driving license ItemsRequest maps to a claims entry through its Rulebook",
    )

    # The statements, each against the key that signed it.
    use_key = keystore_key("ta-use-statement")
    authority_key = keystore_key("ta-authority-statement")
    accreditation_key = keystore_key("ta-accreditation-credential")
    if use_key is None:
        print("keystore absent, signature checks on the statements skipped")
    else:
        statements = blocks(TS_5_06)["The same statement, as the verifier carries it"]
        for number, token in enumerate(statements, start=1):
            check(verify_jws(token.strip(), use_key), f"Use Statement {number} signature")

        answers = [
            json.loads(body)
            for title, bodies in blocks(TS_5_05).items()
            if title.startswith("The answer to")
            for body in bodies
        ]
        for answer in answers:
            check(
                verify_jws(answer["statement"], authority_key),
                f"Authority Statement answer over {answer['resource']}",
            )

        for number, body in enumerate(
            [
                b
                for title, bodies in blocks(TS_5_07).items()
                if title.startswith("The credential of")
                for b in bodies
            ],
            start=1,
        ):
            check(
                verify_jws(body.strip().rstrip("~"), accreditation_key),
                f"Accreditation Credential {number} signature",
            )

    # The subset rule the reader branch rests on.
    role = reader_auth_role(device)
    # ReaderAuthRole names a docType as ISO/IEC 18013-5 writes it; a Use
    # Statement, an answer and a scope name the Rulebook id, with its version.
    # Each docType is read as the id of the Rulebook whose mdoc format names it.
    # A Rulebook that names no mdoc representation is named by its id.
    doc_type_ids: dict[str, str] = {}
    no_mdoc_ids: set[str] = set()
    for path in (DOCS / "credential-rulebook" / "example").glob("*/rulebook.json"):
        rulebook = json.loads(path.read_text())
        doc_type = rulebook.get("formats", {}).get("mdoc", {}).get("docType")
        if doc_type:
            doc_type_ids[doc_type] = rulebook["id"]
        else:
            no_mdoc_ids.add(rulebook["id"])
    role_pairs = {
        f"{doc_type_ids.get(doc, doc)}#{element}" for doc, elements in role.items() for element in elements
    }
    check(
        set(role) <= set(doc_type_ids) | no_mdoc_ids,
        "Every ReaderAuthRole entry names an mdoc docType or the id of a Rulebook with no mdoc representation",
    )
    check(
        not no_mdoc_ids & set(doc_type_ids),
        "No Rulebook id without an mdoc representation equals another Rulebook's mdoc docType",
    )
    statements = blocks(TS_5_06)["The same statement, as the verifier carries it"]
    registered: set[str] = set()
    for token in statements:
        _, payload, _, _ = jws_parts(token.strip())
        if payload["sub"].endswith("terminal-nusantara.co.id"):
            registered |= set(payload["claims"])
    check(role_pairs <= registered, "ReaderAuthRole within the registered uses")

    permissions = set()
    for title, bodies in blocks(TS_5_05).items():
        if not title.startswith("The answer to"):
            continue
        for body in bodies:
            answer = json.loads(body)
            if answer["authorized"]:
                permissions.add(answer["resource"])
    accreditation_scope: set[str] = set()
    for title, bodies in blocks(TS_5_07).items():
        if not title.startswith("The credential of"):
            continue
        for body in bodies:
            _, payload, _, _ = jws_parts(body.strip().rstrip("~"))
            if payload["sub"].endswith("terminal-nusantara.co.id"):
                accreditation_scope |= {entry["resource"] for entry in payload["scope"]}
    # TS-5-05 shows only some answers; a permission the Relying Party's
    # accreditation scope lists is one Trust Registry answers true for.
    check(
        role_pairs <= permissions | accreditation_scope,
        "What the reader may ask for is permitted by an answer or by the accreditation scope",
    )
    # Every attribute a use names is covered by a permission the credential in
    # force lists, REQ-TS-5-06-026 and REQ-TS-5-07-031; a permission over a
    # type covers each of its attributes, REQ-TS-5-06-028.
    check(
        bool(registered)
        and all(
            claim in accreditation_scope or claim.split("#")[0] in accreditation_scope
            for claim in registered
        ),
        "Every registered use is in the accreditation scope",
    )

    # A permission in a credential's scope was held when it was issued,
    # REQ-TS-5-07-031, so the date the answer reports cannot be later.
    issuance: dict[str, tuple[int, set[str]]] = {}
    for title, bodies in blocks(TS_5_07).items():
        if not title.startswith("The credential of"):
            continue
        for body in bodies:
            _, payload, _, _ = jws_parts(body.strip().rstrip("~"))
            issuance[payload["sub"]] = (
                payload["iat"],
                {entry["resource"] for entry in payload["scope"]},
            )
    import datetime as dt  # noqa: PLC0415

    for title, bodies in blocks(TS_5_05).items():
        if not title.startswith("The answer to"):
            continue
        for body in bodies:
            answer = json.loads(body)
            granted = re.match(r"Granted (\S+)\.", answer.get("message", ""))
            held = issuance.get(answer["entity_id"])
            if not granted or not held or answer["resource"] not in held[1]:
                continue
            when = dt.datetime.fromisoformat(granted.group(1).replace("Z", "+00:00"))
            check(
                when.timestamp() <= held[0],
                f"Permission over {answer['resource']} granted by issuance",
            )

# --------------------------------------------------------------------------
# Helpers for what follows
# --------------------------------------------------------------------------


def block(path: Path, title: str) -> str:
    """The body of the first fenced block of ``path`` whose title starts with ``title``."""
    for found, bodies in blocks(path).items():
        if found.startswith(title):
            return bodies[0]
    raise KeyError(f"no block titled {title!r} in {path.name}")


def joined(body: str) -> str:
    """A hard-wrapped block (hex, base64, a token) as one string."""
    return "".join(body.split())


def lead_in(path: Path, title: str) -> str:
    """The paragraph that introduces the block called ``title``."""
    text = path.read_text()
    at = text.rindex("\n", 0, text.index(f'title="{title}'))
    chunks = [c for c in text[:at].split("\n\n") if c.strip()]
    return " ".join(chunks[-1].split())


def http_body(body: str):
    return json.loads(body.split("\n\n", 1)[1])


def jwk_key(jwk: dict):
    x = int.from_bytes(b64u_decode(jwk["x"]), "big")
    y = int.from_bytes(b64u_decode(jwk["y"]), "big")
    return ec.EllipticCurvePublicNumbers(x, y, ec.SECP256R1()).public_key()


def cose_key(item: dict):
    x = int.from_bytes(item[-2], "big")
    y = int.from_bytes(item[-3], "big")
    return ec.EllipticCurvePublicNumbers(x, y, ec.SECP256R1()).public_key()


def sha256_b64u(data: bytes) -> str:
    return webvh._b64u(hashlib.sha256(data).digest())


@functools.cache
def webvh_db():
    path = ART / "webvh.json"
    return json.loads(path.read_text()) if path.exists() else None


@functools.cache
def did_methods() -> dict[str, tuple[str, bool]]:
    """Every verification method of every DID Document version held.

    Maps its identifier to the Multikey and to whether some version lists it
    under ``assertionMethod``. The log TS-5-02 prints is read from the page;
    the other entities' logs come from ``build/artifacts/webvh.json``.
    """
    logs = []
    db = webvh_db()
    if db:
        logs = [entity["entries"] for entity in db["entities"].values()]
    logs.append(page_log())
    methods: dict[str, tuple[str, bool]] = {}
    for entries in logs:
        for entry in entries:
            state = entry["state"]
            for method in state["verificationMethod"]:
                asserted = method["id"] in state.get("assertionMethod", [])
                known = methods.get(method["id"], (None, False))[1]
                methods[method["id"]] = (method["publicKeyMultibase"], asserted or known)
    return methods


def page_log() -> list[dict]:
    body = block(TS_5_02, "did.jsonl")
    return [json.loads(line) for line in body.split("\n") if line.strip()]


def resolve_key(kid: str):
    """The public key a ``kid`` names, as a reader finds it (TS-01)."""
    if kid.startswith("did:key:"):
        material, _, fragment = kid.removeprefix("did:key:").partition("#")
        if fragment and fragment != material:
            raise ValueError(f"{kid} does not name its own key")
        return webvh.public_key_from_multikey(material)
    methods = did_methods()
    if kid not in methods:
        raise ValueError(f"{kid} names no verification method in any DID Document held")
    multikey, asserted = methods[kid]
    if not asserted:
        raise ValueError(f"{kid} is listed under no assertionMethod")
    return webvh.public_key_from_multikey(multikey)


def key_matches_alg(key, alg: str) -> bool:
    if alg == "ES256":
        return isinstance(key, ec.EllipticCurvePublicKey)
    if alg == "EdDSA":
        return isinstance(key, Ed25519PublicKey)
    return False


# --------------------------------------------------------------------------
# 1. Every JWS in docs/
# --------------------------------------------------------------------------

TOKEN = re.compile(r"eyJ[\w-]+\.[\w-]+\.[\w-]+(?:~[\w.-]*)*")
BARE_TOKEN = re.compile(r"eyJ[\w-]+\.[\w-]+\.[\w-]+")
ABBREVIATED = re.compile(r"eyJ[\w-]*\.\.\.")


def fenced(text: str) -> tuple[str, list[str]]:
    """The prose of ``text`` and the bodies of its fenced blocks, apart."""
    prose, bodies, body = [], [], None
    for line in text.split("\n"):
        if body is None and line.startswith("```") and len(line) > 3:
            body = []
        elif body is not None and line.strip() == "```":
            bodies.append("\n".join(body))
            body = None
        elif body is not None:
            body.append(line)
        else:
            prose.append(line)
    return "\n".join(prose), bodies


def sweep_tokens() -> tuple[list[tuple[Path, str]], list[tuple[Path, str]]]:
    """Every compact serialization in ``docs/``, and every one shown cut short."""
    full, abbreviated = [], []
    for path in sorted(DOCS.rglob("*.md")):
        prose, bodies = fenced(path.read_text())
        units = [prose]
        for body in bodies:
            lines = [line for line in body.split("\n") if line.strip()]
            wrapped = bool(lines) and all(re.fullmatch(r"[\w.~-]+", line) for line in lines)
            units.append(joined(body) if wrapped else body)
        for unit in units:
            full += [(path, m.group(0).rstrip(".")) for m in TOKEN.finditer(unit)]
            abbreviated += [(path, m.group(0)) for m in ABBREVIATED.finditer(unit)]
    return full, abbreviated


def token_problem(token: str, issuer_payload: dict | None = None) -> str | None:
    """Why ``token`` does not verify under the key it names, or ``None``."""
    try:
        header, payload, signature, signing_input = jws_parts(token)
        if "kid" in header:
            key = resolve_key(header["kid"])
        elif "jwk" in header:
            key = jwk_key(header["jwk"])
        elif "x5c" in header:
            # A merchant's Request Object under x509_hash: the key of the leaf,
            # which has to be issued by the next certificate of the chain.
            leaf = x509.load_der_x509_certificate(base64.b64decode(header["x5c"][0]))
            try:
                leaf.verify_directly_issued_by(
                    x509.load_der_x509_certificate(base64.b64decode(header["x5c"][1]))
                )
            except Exception:  # noqa: BLE001
                return "x5c[0] is not issued by x5c[1]"
            key = leaf.public_key()
        elif issuer_payload and "cnf" in issuer_payload:
            key = jwk_key(issuer_payload["cnf"]["jwk"])
        else:
            return "no kid, no jwk and no cnf names a key"
        if not key_matches_alg(key, header.get("alg")):
            return f"alg {header.get('alg')} does not fit the key"
        if not verify_raw(key, signature, signing_input):
            return "signature does not verify"
    except (ValueError, KeyError, TypeError) as error:
        return str(error)
    return None


def nested_tokens(value):
    """Every complete token held in a string inside a decoded header or payload."""
    if isinstance(value, str) and BARE_TOKEN.fullmatch(value):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from nested_tokens(item)
    elif isinstance(value, list):
        for item in value:
            yield from nested_tokens(item)


def check_jws_sweep() -> list[str]:
    """Verify every token; return the ones that verified, for the abbreviation check."""
    full, abbreviated = sweep_tokens()
    verified: list[str] = []
    seen: dict[Path, int] = {}
    for path, text in full:
        seen[path] = seen.get(path, 0) + 1
        parts = text.split("~")
        issuer = parts[0]
        try:
            if json.loads(b64u_decode(issuer.split(".")[0])).get("alg") == "HS256":
                continue  # a registration binding: keyed by its code, checked in check_entity_endpoint
            header, payload, _, _ = jws_parts(issuer)
        except ValueError:
            check(False, f"{path.stem[:26]} token {seen[path]}", "the token does not decode")
            continue
        label = f"JWS {path.stem[:22]} {seen[path]}: {header.get('typ', '?')[-24:]}"
        problem = token_problem(issuer)
        check(problem is None, label, problem or "")
        if problem is None:
            verified.append(issuer)
        for inner in nested_tokens([header, payload]):
            if json.loads(b64u_decode(inner.split(".")[0])).get("alg") == "HS256":
                continue
            problem = token_problem(inner)
            check(problem is None, f"{label} (inside)", problem or "")
            if problem is None:
                verified.append(inner)
        if len(parts) > 1 and parts[-1].count(".") == 2:
            problem = token_problem(parts[-1], payload)
            check(problem is None, f"{label} Key Binding JWT", problem or "")
            if problem is None:
                verified.append(parts[-1])
    for number, (path, text) in enumerate(abbreviated, start=1):
        prefix = text.removesuffix("...")
        check(
            any(token.startswith(prefix) for token in verified),
            f"Abbreviated JWS {number} ({path.stem[:20]}) cut from a token above",
            "no verified token begins with it",
        )
    return verified


# --------------------------------------------------------------------------
# 2. The did:webvh log, its witness proof, and the Publisher request
# --------------------------------------------------------------------------

TA_WITNESS_TITLES = ("did-witness.json, served at", "did-witness.json, the proof")


def trusted_list_payload() -> dict:
    return json.loads(block(TS_5_01, "trusted-list.json, the LoTE payload"))


def lote_services(payload: dict):
    """Every service information object of a trusted list, history instances included."""
    for entry in payload["LoTE"]["TrustedEntitiesList"]:
        for service in entry["TrustedEntityServices"]:
            yield entry, service["ServiceInformation"]
            for old in service.get("ServiceHistory", []):
                yield entry, old


def witness_did_keys(payload: dict) -> set[str]:
    return {
        did
        for _, info in lote_services(payload)
        if info["ServiceTypeIdentifier"].endswith("/Witness")
        for did in info["ServiceDigitalIdentity"].get("OtherIds", [])
    }


def check_webvh_log() -> None:
    entries = page_log()
    try:
        webvh.read_log(entries)
        problem = ""
    except ValueError as error:
        problem = str(error)
    check(not problem, "did.jsonl: Read operation over the whole log", problem)
    scid = entries[0]["parameters"]["scid"]
    check(
        webvh.scid_of(entries[0]) == scid
        and all(e["state"]["id"].startswith(f"did:webvh:{scid}:") for e in entries),
        "did.jsonl: every DID Document names the SCID of the first entry",
    )
    db = webvh_db()
    if db:
        check(
            entries == db["entities"]["dukcapil"]["entries"],
            "did.jsonl is the log webvh.json holds for dukcapil",
        )

    logs = [("did.jsonl", entries)] + ([(name, e["entries"]) for name, e in db["entities"].items()] if db else [])
    reused = [
        f"{name} entry {n}"
        for name, log in logs
        for n, entry in enumerate(log, start=1)
        if any(
            webvh.next_key_hash(key) in entry["parameters"].get("nextKeyHashes", [])
            for key in entry["parameters"].get("updateKeys", [])
        )
    ]
    check(
        not reused,
        "did:webvh logs: no entry commits to the update key it carries",
        "; ".join(reused[:4]),
    )

    witnesses = witness_did_keys(trusted_list_payload())
    published = {}
    for path, title in ((TS_5_02, TA_WITNESS_TITLES[0]), (TS_4_01, TA_WITNESS_TITLES[1])):
        shown = json.loads(block(path, title))
        record = shown[0] if isinstance(shown, list) else shown
        published[path.name] = record
        proof = record["proof"][0]
        key = proof["verificationMethod"].split("#")[0]
        check(
            webvh.verify_witness_proof(record["versionId"], proof),
            f"Witness proof on {path.stem[:30]}",
            "signature does not verify over the versionId",
        )
        check(
            record["versionId"] == entries[-1]["versionId"]
            and key in witnesses
            and key in [w["id"] for w in entries[-1]["parameters"]["witness"]["witnesses"]],
            f"Witness proof on {path.stem[:30]}: its key",
            "versionId is not the last entry's, or the witness is not in the log's parameters "
            "and the trusted list",
        )
    first, second = published.values()
    check(first == second, "Witness proof is the same in TS-5-02 and TS-4-01")


def check_publisher_request() -> None:
    entries = page_log()
    request = http_body(block(TS_4_01, "POST /entries"))
    entry = request["logEntry"]
    check(entry == entries[1], "Publisher request: logEntry is the log's second entry")
    previous = entries[0]
    published_before = set(previous["parameters"]["updateKeys"]) | {
        m["publicKeyMultibase"] for m in previous["state"]["verificationMethod"]
    }
    published_now = set(entry["parameters"]["updateKeys"]) | {
        m["publicKeyMultibase"] for m in entry["state"]["verificationMethod"]
    }
    ta_did = webvh_db()["trust_authority_did"] if webvh_db() else None
    proved = set()
    for number, token in enumerate(request["proofOfPossession"], start=1):
        header, payload, _, _ = jws_parts(token)
        kid = header["kid"]
        method = next((m for m in entry["state"]["verificationMethod"] if m["id"] == kid), None)
        material = method["publicKeyMultibase"] if method else kid.removeprefix("did:key:").split("#")[0]
        proved.add(material)
        check(
            webvh.verify_pop(token, webvh.public_key_from_multikey(material)),
            f"Proof of possession {number}: signature under the key its kid names",
            "signature, typ or alg does not fit",
        )
        check(
            payload["nonce"] == request["nonce"]
            and (ta_did is None or payload["aud"] == ta_did)
            and isinstance(payload["iat"], int)
            and payload["iat"] >= webvh_time(entry["versionTime"]),
            f"Proof of possession {number}: nonce, aud and iat",
            f"payload {payload}",
        )
    check(
        proved == published_now - published_before,
        "Proofs of possession cover exactly the keys first published",
        f"proved {sorted(proved)}, new {sorted(published_now - published_before)}",
    )


def webvh_time(text: str) -> int:
    import datetime as dt  # noqa: PLC0415

    return int(dt.datetime.fromisoformat(text.replace("Z", "+00:00")).timestamp())


# --------------------------------------------------------------------------
# 3. Status lists, in both forms
# --------------------------------------------------------------------------

STATUS_WORDS = {"valid": 0, "invalid": 1, "revoked": 1, "suspended": 2}
JWT_LISTS = (
    "Credential status list",
    "Kartu ASN status list",
    "Use Statement status list",
    "Accreditation status list",
)


def named_entries(prose: str) -> dict[int, int]:
    """The indices a paragraph names as invalid, revoked or suspended, with their values."""
    found = re.findall(r"(\d+)\s+(?:is\s+)?(valid|invalid|revoked|suspended)", prose)
    return {int(n): STATUS_WORDS[word] for n, word in found if STATUS_WORDS[word]}


def set_entries(raw: bytes, bits: int, msb_first: bool = False) -> dict[int, int]:
    """Every non-zero entry of a status array: index to value."""
    per_byte = 8 // bits
    out = {}
    for position, byte in enumerate(raw):
        if not byte:
            continue
        for slot in range(per_byte):
            shift = 8 - bits * (slot + 1) if msb_first else bits * slot
            value = (byte >> shift) & ((1 << bits) - 1)
            if value:
                out[position * per_byte + slot] = value
    return out


def status_list_of(payload: dict) -> bytes:
    return zlib.decompress(b64u_decode(payload["status_list"]["lst"]))


def check_status_lists() -> dict[str, dict]:
    """The JWT and CWT forms of the lists on TS-5-09; returns each list's claims."""
    lists = {}
    for name in JWT_LISTS:
        title = f"{name}, as served"
        token = joined(block(TS_5_09, title))
        header, payload, _, _ = jws_parts(token)
        lists[name] = payload
        problem = token_problem(token)
        check(
            problem is None and header["kid"].startswith(payload["iss"] + "#"),
            f"{name}: JWS signed by a key of its iss",
            problem or "kid is not a key of iss",
        )
        expected = named_entries(lead_in(TS_5_09, title))
        bits = payload["status_list"]["bits"]
        found = set_entries(status_list_of(payload), bits)
        check(
            found == expected,
            f"{name}: entries set are the ones the page names",
            f"page names {expected}, array sets {found}",
        )
        shown = json.loads(block(TS_5_09, f"{name} claims"))
        check(shown == payload, f"{name}: claims block is the token's payload")

    for name in ("Credential status list", "Kartu ASN status list"):
        title = f"{name}, CWT form, in hex"
        tag = cbor2.loads(bytes.fromhex(joined(block(TS_5_09, title))))
        protected, unprotected, payload_raw, signature = tag.value
        kid = unprotected[4].decode()
        claims = cbor2.loads(payload_raw)
        jwt = lists[name]
        try:
            signed = verify_raw(
                resolve_key(kid),
                signature,
                cbor2.dumps(["Signature1", protected, b"", payload_raw]),
            )
            problem = "" if signed else "signature does not verify"
        except ValueError as error:
            problem = str(error)
        check(
            tag.tag == 18 and not problem,
            f"{name} CWT: COSE_Sign1 signature under the key its kid names",
            problem or "not tagged 18",
        )
        header = cbor2.loads(protected)
        page = certificates(TS_5_04)
        signer = x509.load_der_x509_certificate(header.get(33, b"")) if 33 in header else None
        org = lambda c: c.subject.get_attributes_for_oid(x509.NameOID.ORGANIZATION_NAME)[0].value  # noqa: E731
        check(
            signer is not None
            and verify_chain(signer, page["issuer-root-ca.pem"])
            and signer.public_key().public_numbers() == resolve_key(kid).public_numbers()
            and (name != "Credential status list"
                 or (der_bytes(signer) == der_bytes(page["status-list-signer.pem"])
                     and org(signer) == org(page["document-signer.pem"]))),
            f"{name} CWT: x5chain chains to the Issuer Root CA, certifies the key kid names,"
            " and names the organization of the Document Signer Certificate",
            "x5chain absent, off the root, or certifying another key or organization",
        )
        check(
            header == {1: -7, 16: "application/statuslist+cwt", 33: header.get(33)}
            and kid == jws_parts(joined(block(TS_5_09, f"{name}, as served")))[0]["kid"]
            and claims[1] == jwt["iss"]
            and kid.startswith(claims[1] + "#")
            and claims[2] == jwt["sub"]
            and claims[6] == jwt["iat"]
            and claims[4] == jwt["exp"]
            and claims[65534] == jwt["ttl"]
            and claims[65533]["bits"] == jwt["status_list"]["bits"]
            and claims[65533]["lst"] == b64u_decode(jwt["status_list"]["lst"]),
            f"{name} CWT: same iss, kid, claims and array as the JWT form",
        )
        expected = named_entries(lead_in(TS_5_09, f"{name}, as served"))
        found = set_entries(zlib.decompress(claims[65533]["lst"]), claims[65533]["bits"])
        check(
            found == expected,
            f"{name} CWT: entries set are the ones the page names",
            f"page names {expected}, array sets {found}",
        )
    return lists


def check_ts01_status_list() -> None:
    """TS-01 takes the Dukcapil status list of TS-5-09 apart; the parts must be its own."""
    token = joined(block(TS_5_09, "Credential status list, as served"))
    header, payload, _, _ = jws_parts(token)
    method = next(
        (m for e in page_log() for m in e["state"]["verificationMethod"] if m["id"] == header["kid"]),
        None,
    )
    check(
        json.loads(block(TS_01, "Protected header of the credential status list")) == header
        and json.loads(block(TS_01, "Signer named in the claims"))
        == {"iss": payload["iss"], "iat": payload["iat"]},
        "TS-01: header and signer blocks are the TS-5-09 status list token's",
    )
    check(
        method is not None and json.loads(block(TS_01, "Verification method the kid names")) == method
        and method["controller"] == payload["iss"],
        "TS-01: the verification method is the one the published log carries",
        "TS-01 shows a method the log does not publish under that kid",
    )


# --------------------------------------------------------------------------
# 4. The credentials of TS-5-10
# --------------------------------------------------------------------------


def disclosure_pairs(body: str) -> list[tuple[str, list]]:
    """The ``~disclosure`` lines of a block with the array shown under each."""
    lines = body.split("\n")
    return [
        (line.removeprefix("~"), json.loads(lines[number + 1]))
        for number, line in enumerate(lines)
        if line.startswith("~")
    ]


def der_of(value) -> bytes:
    return value if isinstance(value, bytes) else value[0]


def check_credentials() -> dict:
    """The SD-JWT VC and the mdoc of TS-5-10; returns what the presentations rest on."""
    parts = joined(block(TS_5_10, "A Kartu ASN in SD-JWT VC")).split("~")
    jwt, disclosures = parts[0], parts[1:-1]
    header, payload, _, _ = jws_parts(jwt)
    problem = token_problem(jwt)
    check(problem is None, "SD-JWT VC signature under the key its kid names", problem or "")
    digests = [sha256_b64u(d.encode("ascii")) for d in disclosures]
    check(
        payload["_sd_alg"] == "sha-256"
        and sorted(digests) == sorted(payload["_sd"])
        and len(set(digests)) == len(digests),
        f"SD-JWT VC: all {len(disclosures)} disclosure digests are in _sd",
        "a digest is missing from _sd, or _sd carries one no disclosure matches",
    )
    check(parts[-1] == "", "SD-JWT VC ends in the empty Key Binding slot")
    check(
        json.loads(block(TS_5_10, "SD-JWT VC header")) == header
        and json.loads(block(TS_5_10, "SD-JWT VC claims")) == payload,
        "SD-JWT VC: header and claims blocks are the token's",
    )
    pairs = disclosure_pairs(block(TS_5_10, "The eight disclosures"))
    check(
        sorted(d for d, _ in pairs) == sorted(disclosures)
        and all(json.loads(b64u_decode(d)) == shown for d, shown in pairs),
        "SD-JWT VC: the disclosure block shows the arrays the token carries",
    )

    raw = bytes.fromhex(joined(block(TS_5_10, "The mdoc IssuerSigned, as issued")))
    signed = cbor2.loads(raw)
    protected, unprotected, mso_bytes, signature = signed["issuerAuth"]
    signer_der = der_of(unprotected[33])
    signer = x509.load_der_x509_certificate(signer_der)
    check(
        verify_raw(
            signer.public_key(),
            signature,
            cbor2.dumps(["Signature1", protected, b"", mso_bytes]),
        ),
        "mdoc: COSE_Sign1 signature under the x5chain certificate",
    )
    page = certificates(TS_5_04)
    check(
        signer_der == page["document-signer.pem"].public_bytes(serialization.Encoding.DER)
        and verify_chain(signer, page["issuer-root-ca.pem"]),
        "mdoc: x5chain is the Document Signer Certificate, chained to the Root CA",
    )
    mso = cbor2.loads(cbor2.loads(mso_bytes).value)
    signed_at = parse_time(mso["validityInfo"]["signed"])
    check(
        signer.not_valid_before_utc <= signed_at <= signer.not_valid_after_utc,
        "mdoc: signed inside the Document Signer Certificate's validity",
    )
    namespace = mso["docType"]
    items = signed["nameSpaces"][namespace]
    recomputed = {
        cbor2.loads(item.value)["digestID"]: hashlib.sha256(cbor2.dumps(item, canonical=True)).digest()
        for item in items
    }
    check(
        recomputed == mso["valueDigests"][namespace],
        f"mdoc: all {len(items)} valueDigests recompute from the items",
    )
    check(
        presentations.enc(presentations.parse_diag(block(TS_5_10, "The mdoc IssuerSigned, in CBOR")))
        == raw
        and presentations.enc(presentations.parse_diag(block(TS_5_10, "The Mobile Security Object")))
        == cbor2.loads(mso_bytes).value,
        "mdoc: the two diagnostic blocks parse back to the signed bytes",
    )
    return {
        "jwt": jwt,
        "disclosures": disclosures,
        "payload": payload,
        "signed": signed,
        "mso": mso,
        "raw": raw,
    }


def parse_time(value):
    """A tdate the CBOR decoder already turned into a datetime, or its text."""
    import datetime as dt  # noqa: PLC0415

    if isinstance(value, dt.datetime):
        return value
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


# --------------------------------------------------------------------------
# 5. The presentations of TS-5-11
# --------------------------------------------------------------------------


def check_presentations(issued: dict) -> None:
    text = joined(block(TS_5_11, "An SD-JWT VC presentation"))
    parts = text.split("~")
    jwt, travelling, kb = parts[0], parts[1:-1], parts[-1]
    holder = jwk_key(issued["payload"]["cnf"]["jwk"])
    kb_header, kb_claims, _, _ = jws_parts(kb)
    check(
        jwt == issued["jwt"] and verify_jws(kb, holder) and kb_header == {"typ": "kb+jwt", "alg": "ES256"},
        "SD-JWT VC presentation: Key Binding JWT under the cnf key",
        "issued JWT changed, or the Key Binding JWT does not verify under the credential's cnf",
    )
    check(
        kb_claims["sd_hash"] == sha256_b64u(text[: text.rindex("~") + 1].encode("ascii")),
        "SD-JWT VC presentation: sd_hash covers the presentation up to the KB-JWT",
    )
    digests = [sha256_b64u(d.encode("ascii")) for d in travelling]
    check(
        set(travelling) <= set(issued["disclosures"])
        and set(digests) <= set(issued["payload"]["_sd"]),
        f"SD-JWT VC presentation: {len(travelling)} disclosures are a subset of the issued ones",
    )
    check(
        json.loads(block(TS_5_11, "The vp_token of an SD-JWT VC")) == {"kartu-asn": [text]}
        and json.loads(block(TS_5_11, "Key Binding JWT header")) == kb_header
        and json.loads(block(TS_5_11, "Key Binding JWT claims")) == kb_claims
        and sorted(d for d, _ in disclosure_pairs(block(TS_5_11, "The disclosures that travelled")))
        == sorted(travelling),
        "SD-JWT VC presentation: vp_token, header, claims and disclosure blocks agree",
    )
    request = json.loads(block(TS_5_06, "The Use Statement in a Request Object"))
    check(
        kb_claims["nonce"] == request["nonce"] and kb_claims["aud"] == request["client_id"],
        "Key Binding JWT nonce and aud are the Request Object's",
    )
    query = request["dcql_query"]["credentials"][0]
    statement = jws_parts(request["verifier_info"][0]["data"])[1]
    by_id = {c["id"]: c["path"][-1] for c in query["claims"]}
    options = query.get("claim_sets", [list(by_id)])
    sent = [json.loads(b64u_decode(d))[1] for d in travelling]
    check(
        len(by_id) == len(query["claims"])
        and all(set(option) <= set(by_id) for option in options)
        and {f"id.idctf.kartu-asn.1#{n}" for n in by_id.values()} <= set(statement["claims"])
        and sent == [by_id[i] for i in options[0]],
        "Kartu ASN Request Object: every claim_sets option names claims of the query, the statement "
        "covers them all, and the presentation discloses the first option",
        "REQ-TS-5-06-051, REQ-TS-5-11-095",
    )

    response_bytes = bytes.fromhex(joined(block(TS_5_11, "The DeviceResponse, as sent")))
    response = cbor2.loads(response_bytes)
    document = response["documents"][0]
    transcript = presentations.parse_diag(block(TS_5_11, "The SessionTranscript of that session"))
    device = document["deviceSigned"]
    protected, _, _, signature = device["deviceAuth"]["deviceSignature"]
    authentication = ["DeviceAuthentication", transcript, document["docType"], device["nameSpaces"]]
    payload = presentations.enc(cbor2.CBORTag(24, presentations.enc(authentication)))
    device_key = cose_key(issued["mso"]["deviceKeyInfo"]["deviceKey"])
    check(
        verify_raw(
            device_key,
            signature,
            cbor2.dumps(["Signature1", protected, b"", payload]),
        ),
        "DeviceResponse: deviceSignature over DeviceAuthentication, SessionTranscript",
        "the signature does not verify under the MSO's deviceKey",
    )
    issued_items = [presentations.enc(item) for item in issued["signed"]["nameSpaces"][document["docType"]]]
    sent = document["issuerSigned"]
    check(
        presentations.enc(sent["issuerAuth"]) == presentations.enc(issued["signed"]["issuerAuth"])
        and all(presentations.enc(i) in issued_items for i in sent["nameSpaces"][document["docType"]]),
        "DeviceResponse: issuerAuth and disclosed items are the issued ones",
    )
    check(
        presentations.enc(presentations.parse_diag(block(TS_5_11, "The DeviceResponse, in CBOR")))
        == response_bytes,
        "DeviceResponse: the diagnostic block parses back to the hex",
    )
    items = cbor2.loads(bytes.fromhex(joined(block(TS_5_06, "The same ItemsRequest, as CBOR"))))
    disclosed = [cbor2.loads(i.value)["elementIdentifier"] for i in sent["nameSpaces"][document["docType"]]]
    check(
        document["docType"] == items["docType"]
        and set(disclosed) <= set(items["nameSpaces"][items["docType"]]),
        "DeviceResponse: docType and data elements are inside the ItemsRequest of TS-5-06",
        "REQ-TS-5-11-086 and 087",
    )

    nikah = json.loads(block(TS_5_06, "The Use Statement of the Kartu Nikah use in a Request Object"))
    vp = json.loads(block(TS_5_11, "The vp_token of an ldp_vc presentation"))["kartu-nikah"][0]
    query = nikah["dcql_query"]["credentials"][0]
    statement = jws_parts(nikah["verifier_info"][0]["data"])[1]
    check(
        vp["proof"]["challenge"] == nikah["nonce"] and vp["proof"]["domain"] == nikah["client_id"],
        "ldp_vc presentation: challenge and domain are the Kartu Nikah Request Object's nonce and client_id",
        "REQ-TS-5-11-080 and 081",
    )
    check(
        query["format"] == "ldp_vc"
        and [f"id.idctf.kartu-nikah.1#{c['path'][-1]}" for c in query["claims"]] == statement["claims"]
        and statement["use_id"] == "pencatatan-ahli-waris"
        and statement["sub"] == nikah["client_id"].removeprefix("decentralized_identifier:"),
        "Kartu Nikah Request Object: the query asks for what its statement names, under the statement's sub",
    )
    check(
        "claim_sets" not in query,
        "Kartu Nikah Request Object: an ldp_vc query carries no claim_sets",
        "REQ-TS-5-06-114",
    )


# --------------------------------------------------------------------------
# 6. Data Integrity proofs
# --------------------------------------------------------------------------


def multibase_bits(encoded: str) -> bytes:
    return gzip.decompress(b64u_decode(encoded[1:]))


def check_data_integrity() -> None:
    credential = json.loads(block(TS_5_10, "A Kartu Nikah in ldp_vc, as issued"))
    revocation = json.loads(block(TS_5_09, "Bitstring Status List credential, revocation"))
    suspension = json.loads(block(TS_5_09, "Bitstring Status List credential, suspension"))
    presentation = json.loads(block(TS_5_11, "The vp_token of an ldp_vc presentation"))["kartu-nikah"][0]
    documents = (
        ("Kartu Nikah credential", credential),
        ("Bitstring Status List, revocation", revocation),
        ("Bitstring Status List, suspension", suspension),
        ("ldp_vc presentation", presentation),
        ("ldp_vc presentation: embedded credential", presentation["verifiableCredential"][0]),
    )
    for label, document in documents:
        proof = document["proof"]
        try:
            ok = ldp.verify(document, resolve_key(proof["verificationMethod"]))
            problem = "signature does not verify"
        except Exception as error:  # noqa: BLE001  (an unresolvable key or context is a failure)
            ok, problem = False, repr(error)[:150]
        check(
            ok and proof["cryptosuite"] == "ecdsa-rdfc-2019",
            f"Data Integrity proof: {label}",
            problem,
        )
    check(
        presentation["verifiableCredential"] == [credential],
        "ldp_vc presentation carries the credential of TS-5-10 unchanged",
    )
    proof = credential["proof"]
    check(
        proof["verificationMethod"].split("#")[0] == credential["issuer"]
        and proof["proofPurpose"] == "assertionMethod"
        and "created" in proof,
        "ldp_vc proof: key of the issuer, assertionMethod, created",
        "REQ-TS-5-10-138 to 140",
    )
    title = "Bitstring Status List credential, revocation purpose"
    size = int(re.search(r"(\d+) entries", lead_in(TS_5_09, title)).group(1))
    for label, status_list, lead in (
        ("revocation", revocation, lead_in(TS_5_09, title)),
        ("suspension", suspension, lead_in(TS_5_09, "Bitstring Status List credential, suspension purpose")),
    ):
        raw = multibase_bits(status_list["credentialSubject"]["encodedList"])
        found = set_entries(raw, 1, msb_first=True)
        expected = {int(n): 1 for n in re.findall(r"index (\d+) is revoked", lead)}
        check(
            len(raw) * 8 == size and found == expected,
            f"Bitstring Status List {label}: {size} entries, the ones the page names are set",
            f"{len(raw) * 8} entries, array sets {found}, page names {expected}",
        )
    entries = json.loads(block(TS_5_09, "The credentialStatus entries"))
    check(entries == credential["credentialStatus"], "credentialStatus entries equal the credential's")


# --------------------------------------------------------------------------
# 7. The issuer X.509 branch and the VICAL
# --------------------------------------------------------------------------


def der_bytes(certificate: x509.Certificate) -> bytes:
    return certificate.public_bytes(serialization.Encoding.DER)


def ski_hex(certificate: x509.Certificate) -> str:
    extension = certificate.extensions.get_extension_for_class(x509.SubjectKeyIdentifier)
    return extension.value.digest.hex().upper()


def stored_certificates() -> list[x509.Certificate]:
    """The certificates ``build/artifacts/x509.json`` holds beyond what the page prints."""
    path = ART / "x509.json"
    if not path.exists():
        return []
    record = json.loads(path.read_text())["certificates"]
    return [x509.load_pem_x509_certificate(item["pem"].encode()) for item in record.values()]


def verifier_crl_signed(certs: dict[str, x509.Certificate]) -> bool:
    """The Verifier Issuing CA list names that CA and verifies under its key.

    The device it revokes is shown nowhere, as the page says ("one withdrawn
    device"), so there is no certificate to hold its serial against.
    """
    crl = x509.load_pem_x509_crl(block(TS_5_04, "verifier-issuing-ca.crl, served at").encode())
    issuing = certs["verifier-issuing-ca.pem"]
    return crl.issuer == issuing.subject and crl.is_signature_valid(issuing.public_key())


def check_mdl_issuer() -> None:
    """The VICAL names org.iso.18013.5.1.mDL for the Issuer Root CA, so an
    issuer under that root holds the permission and a signer certificate."""
    granted = [
        json.loads(body)
        for title, bodies in blocks(TS_5_05).items()
        if title.startswith("The answer to")
        for body in bodies
    ]
    holders = [
        a["entity_id"]
        for a in granted
        if a["action"] == "issue"
        and a["resource"] == "org.iso.18013.5.1.mDL.1"
        and a["authorized"]
    ]
    check(len(holders) == 1, "one Authority Statement answer grants issue over org.iso.18013.5.1.mDL.1")
    if len(holders) != 1:
        return
    lote = json.loads(block(TS_5_01, "trusted-list.json, the LoTE payload"))
    entry = next(
        (
            e
            for e in lote["LoTE"]["TrustedEntitiesList"]
            for svc in e["TrustedEntityServices"]
            if svc["ServiceInformation"]["ServiceDigitalIdentity"].get("OtherIds") == [holders[0]]
            and svc["ServiceInformation"]["ServiceStatus"].endswith("/granted")
        ),
        None,
    )
    check(entry is not None, "the mDL issuer is granted on the trusted list")
    if entry is None:
        return
    names = {n["value"] for n in entry["TrustedEntityInformation"]["TEName"]}
    certs = certificates(TS_5_04)
    signer = certs["document-signer-korlantas.pem"]
    organization = signer.subject.get_attributes_for_oid(x509.NameOID.ORGANIZATION_NAME)[0].value
    check(
        verify_chain(signer, certs["issuer-root-ca.pem"]) and organization in names,
        "the mDL issuer's Document Signer Certificate chains to the Issuer Root CA and names it",
    )


def check_issuer_branch() -> None:
    certs = certificates(TS_5_04)
    root = certs["issuer-root-ca.pem"]
    document_signer = certs["document-signer.pem"]
    vical_signer = certs["vical-signer.pem"]
    check(verify_chain(root, root), "Issuer Root CA self-signature")
    check(verify_chain(document_signer, root), "Document Signer Certificate <- Issuer Root CA")
    check(verify_chain(vical_signer, root), "VICAL signer certificate <- Issuer Root CA")

    csr = x509.load_pem_x509_csr(block(TS_5_04, "document-signer.csr").encode())
    check(
        csr.is_signature_valid
        and csr.public_key().public_numbers() == document_signer.public_key().public_numbers()
        and csr.subject == document_signer.subject,
        "CSR signature, key and subject match the Document Signer",
    )

    crl = x509.load_pem_x509_crl(
        block(TS_5_04, "issuer-root-ca.crl, served at").encode()
    )
    check(
        crl.is_signature_valid(root.public_key()) and crl.issuer == root.subject,
        "Issuer Root CA revocation list",
    )
    held = {c.serial_number: c for c in [*certs.values(), *stored_certificates()]}
    check(
        verifier_crl_signed(certs),
        "Verifier Issuing CA revocation list, issuer and signature",
    )
    for revoked in crl:
        named = held.get(revoked.serial_number)
        check(
            named is not None and verify_chain(named, root),
            "Issuer Root CA list revokes a certificate the page or x509.json holds",
            f"serial {revoked.serial_number:X} names no certificate Trust Authority signed",
        )

    # The verifier list revokes a device certificate that build.py issues, so
    # the serial names a key and not a number nobody can produce.
    verifier_crl = x509.load_pem_x509_crl(
        block(TS_5_04, "verifier-issuing-ca.crl, served at").encode()
    )
    issuing = certs["verifier-issuing-ca.pem"]
    retired_path = ROOT / "build" / "artifacts" / "verifier-device-retired.pem"
    retired = (
        x509.load_pem_x509_certificate(retired_path.read_bytes())
        if retired_path.exists()
        else None
    )
    for revoked in verifier_crl:
        check(
            retired is not None
            and retired.serial_number == revoked.serial_number
            and verify_chain(retired, issuing),
            "Verifier Issuing CA list revokes the device certificate build.py issues",
            f"serial {revoked.serial_number:X} names no device certificate",
        )

    cose = cbor2.loads(base64.b64decode(joined(block(TS_5_04, "GET /vical"))))
    cose = cose.value if isinstance(cose, cbor2.CBORTag) else cose
    protected, unprotected, payload, signature = cose
    signer = x509.load_der_x509_certificate(der_of(unprotected[33]))
    check(
        cbor2.loads(protected) == {1: -7}
        and der_bytes(signer) == der_bytes(vical_signer)
        and verify_raw(
            signer.public_key(),
            signature,
            cbor2.dumps(["Signature1", protected, b"", payload]),
        ),
        "VICAL COSE_Sign1 under the VICAL signer certificate",
    )
    vical = cbor2.loads(payload)
    diagram = block(TS_5_04, "The VICAL payload")
    infos = vical["certificateInfos"]
    parsed = [x509.load_der_x509_certificate(info["certificate"]) for info in infos]
    check(
        all(info["ski"] == c.extensions.get_extension_for_class(x509.SubjectKeyIdentifier).value.digest
            and info["serialNumber"] == c.serial_number
            and info["subject"] == c.subject.public_bytes()
            and f"h'{info['ski'].hex().upper()}'" in diagram
            for info, c in zip(infos, parsed))
        and f'"vicalIssueID": {vical["vicalIssueID"]},' in diagram
        and der_bytes(parsed[0]) == der_bytes(root),
        f"VICAL entries match their certificates and the diagnostic block ({len(infos)})",
    )

    # No list outlives the interval at which it is republished (REQ-GF-045,
    # REQ-TS-5-04-166, REQ-TS-5-04-167, tracks/0436).
    intervals = json.loads(block(TS_02, "governance-profile.json, the Profile payload"))["intervals"]
    crl_limit = profile_duration(intervals["crl_publication"])
    check(
        all(c.next_update_utc - c.last_update_utc <= crl_limit for c in (crl, verifier_crl)),
        "both revocation lists live no longer than intervals.crl_publication",
    )
    date, next_update = (
        v.value if isinstance(v, cbor2.CBORTag) else v for v in (vical["date"], vical["nextUpdate"])
    )
    check(
        next_update - date <= profile_duration(intervals["vical_publication"]),
        "the VICAL lives no longer than intervals.vical_publication",
    )


# --------------------------------------------------------------------------
# 8. The trusted list
# --------------------------------------------------------------------------


def check_trusted_list() -> None:
    header_text = block(TS_5_01, "trusted-list.json, the JWS protected header")
    payload_text = block(TS_5_01, "trusted-list.json, the LoTE payload")
    token = joined(block(TS_5_01, "trusted-list.json, the JWS compact serialization"))
    head_b64, body_b64, _ = token.split(".")
    header = json.loads(b64u_decode(head_b64))
    problem = token_problem(token)
    check(problem is None, "Trusted list: JWS under the key its kid names", problem or "")
    check(
        b64u_decode(head_b64).decode() == header_text
        and b64u_decode(body_b64).decode() == payload_text,
        "Trusted list: header and payload blocks are the JWS's, byte for byte",
    )
    payload = json.loads(payload_text)
    signers = [
        info
        for _, info in lote_services(payload)
        if info["ServiceTypeIdentifier"].endswith("/TrustedListSigner")
        and header["kid"] in info["ServiceDigitalIdentity"].get("OtherIds", [])
    ]
    check(
        header["kid"].startswith("did:key:")
        and any(info["ServiceStatus"].endswith("/granted") for info in signers),
        "Trusted list: its kid is a TrustedListSigner at status granted",
        "no TrustedListSigner service at status granted names the kid",
    )
    check(
        header_text == block(TS_01, "Protected header of the trusted list")
        and [json.loads(block(TS_01, "Trusted list signer service"))["ServiceInformation"]]
        == signers[:1],
        "TS-01 shows the trusted list's header and signer service unchanged",
    )


# --------------------------------------------------------------------------
# The Governance Profile of TS-02
# --------------------------------------------------------------------------


def profile_duration(text: str) -> dt.timedelta:
    """A Governance Profile duration with no year or month part, as a timedelta."""
    m = re.fullmatch(r"P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)?", text)
    if not m:
        raise ValueError(f"not a day-based duration: {text}")
    d, h, mi, se = (int(g or 0) for g in m.groups())
    return dt.timedelta(days=d, hours=h, minutes=mi, seconds=se)


def check_governance_profile() -> None:
    header_text = block(TS_02, "governance-profile.json, the JWS protected header")
    payload_text = block(TS_02, "governance-profile.json, the Profile payload")
    token = joined(block(TS_02, "governance-profile.json, the JWS compact serialization"))
    head_b64, body_b64, signature_b64 = token.split(".")
    header = json.loads(b64u_decode(head_b64))
    problem = token_problem(token)
    check(problem is None, "Governance Profile: JWS under the key its kid names", problem or "")
    check(
        b64u_decode(head_b64).decode() == header_text
        and b64u_decode(body_b64).decode() == payload_text,
        "Governance Profile: header and payload blocks are the JWS's, byte for byte",
    )
    check(
        list(header) == ["alg", "kid"] and header["alg"] == "ES256"
        and header["kid"].startswith("did:key:zDna"),
        "Governance Profile: header is exactly alg ES256 and a P-256 did:key (REQ-TS-02-033 to 035)",
    )
    profile = json.loads(payload_text)
    granted = [s["key"] for s in profile["signers"] if s["status"] == "granted"]
    check(header["kid"] in granted, "Governance Profile: its kid is a signer at granted (REQ-TS-02-029)")
    for name in ("ta-governance-profile-1", "ta-governance-profile-2", "ta-governance-profile-3"):
        public = keystore_key(name)
        if public is None:
            check(False, f"Governance Profile: keystore key {name}", "the keystore is absent")
            continue
        check(
            any(resolve_key(s["key"]).public_numbers() == public.public_numbers()
                for s in profile["signers"]),
            f"Governance Profile: {name} is one of its signers",
        )
    lote = json.loads(block(TS_5_01, "trusted-list.json, the LoTE payload"))
    check(
        profile["addresses"]["trusted_list"]
        == lote["LoTE"]["ListAndSchemeInformation"]["DistributionPoints"],
        "Governance Profile: trusted_list equals the trusted list's DistributionPoints",
    )
    stamp = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
    check(
        all(stamp.match(profile[k]) for k in ("issued_at", "next_update"))
        and profile["issued_at"] < profile["next_update"],
        "Governance Profile: issued_at and next_update are UTC date-times in order",
    )
    ids = re.findall(r"\*\*(REQ-TS-02-\d{3})\*\*", TS_02.read_text())
    check(len(ids) == len(set(ids)), f"TS-02 carries {len(ids)} requirements, each identifier once")
    listed = [s["id"] for s in profile["specifications"]]
    pages = sorted(re.findall(r'^title: "\[(TS-[0-9-]+)\]', p.read_text(), re.M)[0]
                   for p in TS.glob("*.md") if p.name != "index.md")
    check(sorted(listed) == pages, "Governance Profile: specifications names every TS page once")


# --------------------------------------------------------------------------
# 9. The key attestation
# --------------------------------------------------------------------------


def check_key_attestation() -> None:
    token = block(TS_5_08, "A Key Attestation, in compact").strip()
    proof = block(TS_5_08, "A key proof carrying").strip()
    header, claims, _, _ = jws_parts(token)
    proof_header, proof_claims, _, _ = jws_parts(proof)
    check(
        json.loads(block(TS_5_08, "Key Attestation header")) == header
        and json.loads(block(TS_5_08, "Key Attestation claims")) == claims,
        "Key Attestation: header and claims blocks are the token's",
    )
    problem = token_problem(proof)
    check(
        problem is None
        and proof_header["key_attestation"] == token
        and proof_header["jwk"] == claims["attested_keys"][0]
        and proof_claims["nonce"] == claims["nonce"],
        "Key proof: signed by the attested key, carries the attestation, same nonce",
        problem or "the proof does not carry the attestation shown, or its key",
    )
    shown = json.loads(block(TS_5_08, "Key proof header, with the attestation abbreviated"))
    check(
        shown["jwk"] == proof_header["jwk"]
        and token.startswith(shown["key_attestation"].removesuffix("...")),
        "Key proof: the abbreviated header is cut from the same attestation",
    )
    check(
        json.loads(block(TS_5_08, "Key proof claims")) == proof_claims,
        "Key proof: claims block is the token's",
    )


def check_enrollment() -> None:
    """TS-2-01: the bindings, the evidence that commits to them, and the request signatures."""
    def thumb(jwk: dict) -> str:
        canonical = json.dumps({k: jwk[k] for k in ("crv", "kty", "x", "y")},
                               separators=(",", ":"), sort_keys=True)
        return sha256_b64u(canonical.encode())

    record = json.loads(blocks(TS_2_01)["The installation record"][0])
    ios_record = json.loads(block(TS_2_01, "The installation record on iOS"))
    check(record["platform"] == "android" and ios_record["platform"] == "ios",
          "TS-2-01: one record per platform")
    for rec in (record, ios_record):
        check(rec["installation"] == thumb(rec["device_key"]),
              f"TS-2-01 {rec['platform']}: installation is the device key's RFC 7638 thumbprint")
    shown_jwk, shown_canonical, shown_id = block(
        TS_5_03, "A device key and its device identifier").strip().split("\n\n")
    canonical = json.dumps({k: json.loads(shown_jwk)[k] for k in ("crv", "kty", "x", "y")},
                           separators=(",", ":"), sort_keys=True)
    check(shown_canonical == canonical and shown_id == sha256_b64u(canonical.encode()),
          "TS-5-03: the device identifier is the SHA-256 of the canonical JSON of the shown key")
    check(json.loads(shown_jwk) == record["device_key"] and shown_id == record["installation"],
          "TS-5-03: the shown key and identifier are the Android installation TS-2-01 records")
    previous = json.loads(block(TS_2_01, "The previous installation's record"))
    enroll_verdict = json.loads(block(TS_2_01, "The integrity verdict at enrollment"))
    check(previous["state"] == "revoked" and previous["account"] == record["account"]
          and previous["revoked_at"] == record["enrolled_at"]
          and previous["installation"] == thumb(previous["device_key"])
          and previous["credential_key"] != record["credential_key"]
          and int(enroll_verdict["requestDetails"]["timestampMillis"]) <= record["enrolled_at"] * 1000,
          "TS-2-01 android: the account's previous installation is revoked when the new one is recorded")
    claims = json.loads(block(TS_5_08, "Key Attestation claims"))
    check(record["credential_key"] == claims["attested_keys"][0]
          and record["key_storage"] == claims["key_storage"]
          and record["user_authentication"] == claims["user_authentication"]
          and record["certification"] == claims["certification"],
          "TS-2-01 android: the record's key and values are the ones TS-5-08 attests")

    enroll = block(TS_2_01, "The enrollment binding string").strip()
    request = block(TS_2_01, "The request binding string").strip()
    challenge = enroll.split(".")[0]
    cred_tp = thumb(record["credential_key"])
    check(enroll == f"{challenge}.{cred_tp}" and request == f"{claims['nonce']}.{cred_tp}",
          "TS-2-01 android: bindings are challenge or nonce, then the credential key's thumbprint")
    idt = json.loads(block(TS_2_01, "The identity provider's token claims"))
    check(idt["nonce"] == challenge and [idt["iss"], idt["sub"]]
          == [record["account"]["iss"], record["account"]["sub"]],
          "TS-2-01 android: the ID Token carries the challenge and names the recorded account")
    for title in ("KeyDescription of the credential key", "KeyDescription of the device key"):
        body = block(TS_2_01, title)
        check(f'"{challenge}"' in body and f'"{record["device_model"]}"' in body,
              f"TS-2-01 android: {title} carries the challenge and the recorded model")
    for title, binding in (("The integrity verdict at enrollment", enroll),
                           ("The integrity verdict in the request", request)):
        verdict = json.loads(block(TS_2_01, title))
        check(verdict["requestDetails"]["requestHash"] == sha256_b64u(binding.encode()),
              f"TS-2-01 android: {title} carries the hash of its binding")
    signature = b64u_decode(block(TS_2_01, "The device key's signature").strip())
    check(verify_raw(jwk_key(record["device_key"]), signature, request.encode()),
          "TS-2-01 android: the device key's signature verifies over the request binding")

    shown = json.loads(block(TS_2_01, "The App Attest attestation"))
    att = shown["attestation"]
    ios_enroll = block(TS_2_01, "The iOS enrollment binding string").strip()
    ios_request = block(TS_2_01, "The iOS request binding string").strip()
    ios_tp = thumb(ios_record["credential_key"])
    check(shown["credential_key"] == ios_record["credential_key"]
          and ios_enroll.endswith("." + ios_tp)
          and ios_request == f"{claims['nonce']}.{ios_tp}"
          and att["clientDataHash"] == sha256_b64u(ios_enroll.encode()),
          "TS-2-01 ios: the attestation commits to the enrollment binding of the recorded key")
    point = jwk_key(ios_record["device_key"]).public_bytes(
        serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
    check(base64.b64decode(att["keyId"]) == hashlib.sha256(point).digest()
          == bytes.fromhex(att["authData"]["credentialId"]),
          "TS-2-01 ios: keyId and credentialId are the SHA-256 of the device key")
    assertion = cbor2.loads(bytes.fromhex(joined(block(TS_2_01, "The App Attest assertion"))))
    auth_data = assertion["authenticatorData"]
    message = hashlib.sha256(auth_data + hashlib.sha256(ios_request.encode()).digest()).digest()
    try:
        jwk_key(ios_record["device_key"]).verify(assertion["signature"], message,
                                                 ec.ECDSA(hashes.SHA256()))
        signed = True
    except InvalidSignature:
        signed = False
    check(signed and auth_data[:32].hex() == att["authData"]["rpIdHash"]
          and int.from_bytes(auth_data[33:37], "big") == ios_record["sign_count"] > 0,
          "TS-2-01 ios: the assertion verifies, names the App ID, and its counter is the record's")


# --------------------------------------------------------------------------
# 10. The statements: decoded blocks against their tokens
# --------------------------------------------------------------------------


def check_decoded_blocks() -> None:
    decoded = [
        tuple(json.loads(half) for half in b.split("\n.\n"))
        for t, bs in blocks(TS_5_06).items()
        if t.endswith(", decoded")
        for b in bs
    ]
    carried = blocks(TS_5_06)["The same statement, as the verifier carries it"]
    check(
        len(decoded) == len(carried)
        and all(d == jws_parts(c.strip())[:2] for d, c in zip(decoded, carried)),
        f"Use Statements: {len(carried)} decoded blocks are their tokens' header and payload",
    )
    request = json.loads(block(TS_5_06, "The Use Statement in a Request Object"))
    check(
        request["verifier_info"][0]["data"] in [c.strip() for c in carried],
        "Request Object embeds a Use Statement TS-5-06 carries",
    )
    nikah = json.loads(block(TS_5_06, "The Use Statement of the Kartu Nikah use in a Request Object"))
    check(
        nikah["verifier_info"][0]["data"] in [c.strip() for c in carried],
        "Kartu Nikah Request Object embeds a Use Statement TS-5-06 carries",
    )
    credentials = [
        b for t, bs in blocks(TS_5_07).items() if t.startswith("The credential of") for b in bs
    ]
    claims = json.loads(block(TS_5_07, "The claims of the Identity Issuer"))
    check(
        claims == jws_parts(credentials[0].strip().rstrip("~"))[1],
        "Accreditation Credential: the claims block is the first token's payload",
    )


# --------------------------------------------------------------------------
# 11. Identifiers two pages share are one value
# --------------------------------------------------------------------------

DID_WEBVH = re.compile(r"did:webvh:(Qm[1-9A-HJ-NP-Za-km-z]{44}):([A-Za-z0-9.-]+)(#[\w-]+)?")
DID_KEY = re.compile(r"did:key:(z[1-9A-HJ-NP-Za-km-z]{40,})(#z[1-9A-HJ-NP-Za-km-z]+)?")
SKI = re.compile(r"\b[0-9A-F]{40}\b")


def ts_text() -> dict[Path, str]:
    return {path: path.read_text() for path in sorted(TS.glob("*.md"))}


def known_dids() -> set[str]:
    dids = {entry["state"]["id"] for entry in page_log()}
    if webvh_db():
        dids |= {entity["did"] for entity in webvh_db()["entities"].values()}
    return dids


def check_shared_identifiers(issued: dict) -> None:
    texts = ts_text()
    dids = known_dids()
    unknown, no_method = set(), set()
    for path, text in texts.items():
        for match in DID_WEBVH.finditer(text):
            did = f"did:webvh:{match.group(1)}:{match.group(2).rstrip('.')}"
            if did not in dids:
                unknown.add(f"{did} ({path.stem[:20]})")
            elif match.group(3) and did + match.group(3) not in did_methods():
                no_method.add(f"{did}{match.group(3)} ({path.stem[:20]})")
    check(not unknown, "Every did:webvh in the TS pages is a log's", "; ".join(sorted(unknown)[:4]))
    check(not no_method, "Every did:webvh key identifier names a method", "; ".join(sorted(no_method)[:4]))

    held = set()
    logs = [page_log()] + ([e["entries"] for e in webvh_db()["entities"].values()] if webvh_db() else [])
    for entry in (entry for log in logs for entry in log):
        held |= {f"did:key:{k}" for k in entry["parameters"].get("updateKeys", [])}
        held |= {w["id"] for w in entry["parameters"].get("witness", {}).get("witnesses", [])}
    payload = trusted_list_payload()
    for _, info in lote_services(payload):
        held |= {d for d in info["ServiceDigitalIdentity"].get("OtherIds", []) if d.startswith("did:key:")}
    profile = json.loads(block(TS_02, "governance-profile.json, the Profile payload"))
    held |= {s["key"] for s in profile["signers"]}
    holder = issued["payload"]["cnf"]["jwk"]
    holder_key = jwk_key(holder)
    held.add(webvh.did_key(webvh.multikey(holder_key)))
    stray = set()
    for path, text in texts.items():
        for match in DID_KEY.finditer(text):
            try:
                webvh.public_key_from_multikey(match.group(1))
            except ValueError:
                stray.add(f"{match.group(1)[:16]} cannot be decoded ({path.stem[:20]})")
                continue
            if match.group(2) and match.group(2)[1:] != match.group(1):
                stray.add(f"{match.group(1)[:16]} fragment differs ({path.stem[:20]})")
            if f"did:key:{match.group(1)}" not in held:
                stray.add(f"{match.group(1)[:16]} is held by no artifact ({path.stem[:20]})")
    check(not stray, "Every did:key in the TS pages decodes and a key holds it", "; ".join(sorted(stray)[:4]))

    certs = [*certificates(TS_5_04).values(), *stored_certificates()]
    skis = set()
    for certificate in certs:
        skis.add(ski_hex(certificate))
        try:
            skis.add(
                certificate.extensions.get_extension_for_class(x509.AuthorityKeyIdentifier)
                .value.key_identifier.hex().upper()
            )
        except x509.ExtensionNotFound:
            pass
    cose = cbor2.loads(base64.b64decode(joined(block(TS_5_04, "GET /vical"))))
    cose = cose.value if isinstance(cose, cbor2.CBORTag) else cose
    skis |= {info["ski"].hex().upper() for info in cbor2.loads(cose[2])["certificateInfos"]}
    orphans = {
        f"{ski} ({path.stem[:20]})"
        for path, text in texts.items()
        for ski in SKI.findall(text)
        if ski not in skis
    }
    check(not orphans, "Every subject key identifier is a certificate's", "; ".join(sorted(orphans)[:4]))

    # The wallet's one credential key, wherever a page puts it.
    attested = claims_of(block(TS_5_08, "A Key Attestation, in compact").strip())["attested_keys"][0]
    device = cose_key(issued["mso"]["deviceKeyInfo"]["deviceKey"]).public_numbers()
    credential = json.loads(block(TS_5_10, "A Kartu Nikah in ldp_vc, as issued"))
    subject = webvh.public_key_from_multikey(credential["credentialSubject"]["id"].split(":")[2])
    check(
        holder == attested
        and holder_key.public_numbers() == device == subject.public_numbers(),
        "One wallet key: cnf, attestation, deviceKey and the ldp_vc subject",
    )


def claims_of(token: str) -> dict:
    return jws_parts(token)[1]


def check_statuses(lists: dict[str, dict]) -> None:
    """A status pointer a page shows reads valid in the list it names."""
    by_address = {payload["sub"]: payload for payload in lists.values()}
    pointers = []
    for path in (TS_5_06, TS_5_07):
        for title, bodies in blocks(path).items():
            if title.startswith("The same statement") or title.startswith("The credential of"):
                pointers += [(title, claims_of(b.strip().rstrip("~"))) for b in bodies]
    pointers.append(("Kartu ASN", {"status": jws_parts(joined(block(TS_5_10, "A Kartu ASN in SD-JWT VC")).split("~")[0])[1]["status"]}))
    problems = []
    for title, claims in pointers:
        pointer = claims["status"]["status_list"]
        payload = by_address.get(pointer["uri"])
        if payload is None:
            problems.append(f"{pointer['uri']} is no list TS-5-09 shows")
            continue
        bits = payload["status_list"]["bits"]
        value = set_entries(status_list_of(payload), bits).get(pointer["idx"], 0)
        if value:
            problems.append(f"index {pointer['idx']} of {pointer['uri']} reads {value}")
    check(not problems, f"Status pointers ({len(pointers)}) read valid in the lists TS-5-09 shows", "; ".join(problems[:3]))


def check_authority_identifiers() -> None:
    """One Trust Authority, and the entities it names are the trusted list's."""
    statements = []
    for path in (TS_5_05, TS_5_06, TS_5_07):
        for title, bodies in blocks(path).items():
            if title.startswith(("The same statement", "The credential of")):
                statements += [claims_of(b.strip().rstrip("~")) for b in bodies]
            elif title.startswith("The answer to"):
                statements += [claims_of(json.loads(b)["statement"]) for b in bodies]
    # An Authority Statement names the authority and the entity, not iss and sub.
    issuers = {claims.get("iss", claims.get("authority_id")) for claims in statements}
    request = http_body(block(TS_4_01, "POST /entries"))
    audiences = {jws_parts(t)[1]["aud"] for t in request["proofOfPossession"]}
    check(
        len(issuers) == 1 and audiences == issuers,
        "Trust Authority is one DID in every statement and in the key proofs",
        f"issuers {sorted(issuers)}, audiences {sorted(audiences)}",
    )
    named = {
        did
        for _, info in lote_services(trusted_list_payload())
        for did in info["ServiceDigitalIdentity"].get("OtherIds", [])
        if did.startswith("did:webvh:")
    }
    subjects = {
        claims.get("sub", claims.get("entity_id"))
        for claims in statements
        if claims.get("sub", claims.get("entity_id", "")).startswith("did:webvh:")
    }
    check(subjects <= named, "Every entity a statement names is one the trusted list names",
          "; ".join(sorted(subjects - named)))


TS_4_02 = TS / "answering-a-permission-query-and-serving-the-catalog.md"


def authority_periods() -> dict[tuple[str, str, str], tuple[list[dict], str]]:
    """Each answer of TS-5-05 by (entity_id, action, resource): the `periods`
    its signed payload carries and the message its body carries."""
    found = {}
    for title, bodies in blocks(TS_5_05).items():
        if not title.startswith("The answer to"):
            continue
        for body in bodies:
            answer = json.loads(body)
            _, payload, _, _ = jws_parts(answer["statement"])
            found[(answer["entity_id"], answer["action"], answer["resource"])] = (
                payload["periods"],
                answer.get("message", ""),
            )
    return found


def issued_credentials() -> list[tuple[str, str, str, int, str]]:
    """Every SD-JWT VC and `ldp_vc` example in docs/ that an issuer's permission
    covers: (page, issuer DID, resource, signing time, label). A credential
    Trust Authority issues about an entity is not one."""
    import datetime as dt  # noqa: PLC0415

    contexts: dict[str, str] = {}
    for path in (DOCS / "credential-rulebook" / "example").glob("*/rulebook.json"):
        rulebook = json.loads(path.read_text())
        context = rulebook.get("formats", {}).get("ldp_vc", {}).get("context")
        if context:
            contexts[context] = rulebook["id"]
    found, seen = [], set()
    full, _ = sweep_tokens()
    for path, text in full:
        issuer = text.split("~")[0]
        if issuer in seen:
            continue
        try:
            _, payload, _, _ = jws_parts(issuer)
        except ValueError:
            continue
        if "vct" in payload and "iss" in payload and not payload["vct"].startswith("id.idctf.accreditation."):
            seen.add(issuer)
            found.append((path.stem, payload["iss"], payload["vct"], payload["iat"], f"SD-JWT VC of {payload['vct']}"))
    for path in sorted(DOCS.rglob("*.md")):
        for body in fenced(path.read_text())[1]:
            if '"proof"' not in body or '"VerifiableCredential"' not in body:
                continue
            try:
                document = json.loads(body)
            except ValueError:
                continue
            kinds = document.get("type", [])
            # A Rulebook example page writes the issuer with a placeholder SCID ("QmScid...").
            if "BitstringStatusListCredential" in kinds or not isinstance(document.get("issuer"), str) or "..." in document["issuer"]:
                continue
            created = document["proof"]["created"]
            second = document["@context"][1]
            resource = contexts.get(second, second)
            key = (document["issuer"], resource, created)
            if key in seen:
                continue
            seen.add(key)
            when = int(dt.datetime.fromisoformat(created.replace("Z", "+00:00")).timestamp())
            found.append((path.stem, document["issuer"], resource, when, f"ldp_vc of {resource}"))
    return found


def check_signing_inside_permission() -> None:
    """REQ-TS-5-10-141: the signing time of an example SD-JWT VC or ldp_vc falls
    inside a period of the answer for its issuer, `issue` and its type and version."""
    import datetime as dt  # noqa: PLC0415

    def parse(text: str) -> int:
        return int(dt.datetime.fromisoformat(text.replace("Z", "+00:00")).timestamp())

    answers = authority_periods()
    for (entity, action, resource), (periods, message) in answers.items():
        granted = re.match(r"Granted (\S+)\.", message)
        if granted:
            check(
                bool(periods) and parse(periods[-1]["valid_from"]) == parse(granted.group(1)),
                f"Earliest period of {resource} starts when its message says",
            )
        else:
            check(periods == [], f"No period for {resource}, which the answer does not grant")
        check(
            [parse(p["valid_from"]) for p in periods] == sorted((parse(p["valid_from"]) for p in periods), reverse=True),
            f"Periods of {resource} run newest first",
        )
    for page, issuer, resource, signed, label in issued_credentials():
        periods = answers.get((issuer, "issue", resource), (None, ""))[0]
        if periods is None:
            check(False, f"{label} in {page[:24]}: answer for its issuer", "no answer for this issuer, issue and type")
            continue
        check(
            any(
                parse(p["valid_from"]) <= signed and ("valid_until" not in p or signed < parse(p["valid_until"]))
                for p in periods
            ),
            f"{label} in {page[:24]} signed inside a period of its issuer's answer",
        )


def check_trust_registry() -> None:
    """TS-4-02: the catalog list against the Rulebook files, and each recognition answer against its statement."""
    token = joined(block(TS_4_02, "The catalog list as served"))
    header, payload, _, _ = jws_parts(token)
    check(header.get("typ") == "vnd.id.idctf.catalog+jwt", "Catalog list: typ")
    check(header.get("kid", "").endswith("#catalog-1"), "Catalog list: kid names the catalog key")
    check(payload == json.loads(block(TS_4_02, "Catalog list payload, decoded")),
          "Catalog list: decoded payload is the signed payload")
    rulebooks = {}
    for path in sorted((DOCS / "credential-rulebook" / "example").glob("*/rulebook.json")):
        raw = path.read_bytes()
        rulebooks[json.loads(raw)["id"]] = "sha384-" + base64.b64encode(hashlib.sha384(raw).digest()).decode()
    listed = {entry["id"]: entry for entry in payload["rulebooks"]}
    check(set(listed) == set(rulebooks), "Catalog list names every example Rulebook, no other",
          f"{sorted(set(listed) ^ set(rulebooks))}")
    for type_id, digest in rulebooks.items():
        entry = listed.get(type_id, {})
        check(entry.get("rulebook_digest") == digest, f"Catalog list: digest of {type_id}")
        check(entry.get("rulebook", "").endswith(f"/rulebooks/{type_id}"), f"Catalog list: address of {type_id}")
    for title in ("The answer to a recognition query that is recognized",
                  "The answer to a recognition query that is not recognized"):
        answer = json.loads(block(TS_4_02, title))
        header, claims, _, _ = jws_parts(answer["statement"])
        check(header.get("typ") == "vnd.id.idctf.recognition-statement+jwt"
              and header.get("kid", "").endswith("#recognition-statement-1"),
              f"Recognition answer ({'true' if answer['recognized'] else 'false'}): typ and kid")
        signed = {k: v for k, v in claims.items() if k not in ("iat", "exp")}
        body = {k: v for k, v in answer.items() if k not in ("statement", "message", "context")}
        check(signed == body, f"Recognition answer ({'true' if answer['recognized'] else 'false'}): body equals payload")


# --------------------------------------------------------------------------
# TS-4-03: the entity endpoint of Trust Authority
# --------------------------------------------------------------------------

TS_4_03 = TS / "onboarding-an-entity-and-registering-its-keys.md"


def check_entity_endpoint() -> None:
    import hmac  # noqa: PLC0415

    page = blocks(TS_4_03)
    text = TS_4_03.read_text()

    def token_of(title: str) -> str:
        return block(TS_4_03, title).split("\n\n", 1)[1].strip()

    def answer(title: str) -> dict:
        return http_body(block(TS_4_03, title))

    db = webvh_db()
    ta_did = db["trust_authority_did"] if db else None
    endpoint = "https://" + re.search(r"Host: (\S+)", block(TS_4_03, "GET /nonce")).group(1)
    nonces: list[str] = []
    requests: dict[str, tuple[dict, object]] = {}
    for title in page:
        if not title.startswith("POST /entities/me"):
            continue
        token = token_of(title)
        protected, _, signature, signing_input = (
            json.loads(b64u_decode(token.split(".")[0])), None,
            b64u_decode(token.split(".")[2]), ".".join(token.split(".")[:2]).encode())
        raw = b64u_decode(token.split(".")[1])
        payload = json.loads(raw) if raw else None
        key = resolve_key(protected["kid"])
        path = title.split(",")[0].removeprefix("POST ")
        check(set(protected) == {"alg", "kid", "nonce", "url"} and protected["alg"] == "EdDSA"
              and protected["kid"].startswith("did:key:z6Mk")
              and verify_raw(key, signature, signing_input) and protected["url"] == endpoint + path,
              f"TS-4-03 {title[:44]}: header and signature")
        nonces.append(protected["nonce"])
        requests[title] = (protected, payload)
        decoded_title = {
            "POST /entities/me/keys, the first entry": "The first entry request, decoded",
            "POST /entities/me/keys, a certificate request": "The certificate request, decoded",
            "POST /entities/me/keys, a rotation": "The rotation request, decoded",
            "POST /entities/me/keys, a Verifier Issuing CA request": "The Verifier Issuing CA request, decoded",
        }.get(title)
        shown = json.loads(block(TS_4_03, decoded_title))
        check(shown == {"protected": protected, "payload": payload},
              f"TS-4-03 {decoded_title}: equals the request")
    answers = [t for t in page if re.match(r"\d{3}, ", t)]
    check(all("Replay-Nonce: " in block(TS_4_03, t) and "Cache-Control: no-store" in block(TS_4_03, t)
              for t in answers if not t.startswith("204")) and bool(answers),
          "TS-4-03 every answer carries a nonce and no-store")
    check(len(set(nonces)) == len(nonces), "TS-4-03 every request carries its own nonce")
    for title, (protected, payload) in requests.items():
        if not payload or "countersignature" not in payload:
            continue
        header, claims, _, _ = jws_parts(payload["countersignature"])
        certified = {webvh.multikey(x509.load_der_x509_csr(b64u_decode(r["csr"])).public_key())
                     for r in payload.get("certificationRequests", [])}
        key = resolve_key(header["kid"])
        check("logEntry" not in payload and webvh.verify_pop(payload["countersignature"], key)
              and header["kid"].startswith("did:webvh:") and header["typ"] == "vnd.id.idctf.key-pop+jwt"
              and claims["nonce"] == protected["nonce"] and claims["aud"] == ta_did
              and webvh.multikey(key) not in certified,
              f"TS-4-03 {title[24:60]}: countersignature by a key it does not certify")

    entries = page_log()

    def pops_cover(protected: dict, payload: dict, entry: dict, before: set[str]) -> None:
        published = set(entry["parameters"]["updateKeys"]) | {
            m["publicKeyMultibase"] for m in entry["state"]["verificationMethod"]}
        proved = set()
        for number, pop in enumerate(payload["proofOfPossession"], start=1):
            header, claims, _, _ = jws_parts(pop)
            material = (header["kid"].removeprefix("did:key:").split("#")[0]
                        if header["kid"].startswith("did:key:")
                        else next(m["publicKeyMultibase"] for m in entry["state"]["verificationMethod"]
                                  if m["id"] == header["kid"]))
            proved.add(material)
            check(webvh.verify_pop(pop, webvh.public_key_from_multikey(material))
                  and claims["nonce"] == protected["nonce"] and claims["aud"] == ta_did,
                  f"TS-4-03 proof of possession {material[:12]}: signature, request nonce, aud")
        check(proved == published - before, "TS-4-03 proofs cover exactly the keys first published")

    # The first entry and its binding.
    first_p, first = requests["POST /entities/me/keys, the first entry"]
    check(first["logEntry"] == entries[0], "TS-4-03 first entry is the first line of the TS-5-02 log")
    check(first["logEntry"]["parameters"]["updateKeys"] == [first_p["kid"].removeprefix("did:key:").split("#")[0]],
          "TS-4-03 first entry carries the update key that signs the request")
    pops_cover(first_p, first, entries[0], set())
    code = re.search(r"registration\s+code\s+`([\w-]+)`", text).group(1)
    b_head, b_payload, b_sig = first["registrationBinding"].split(".")
    b_protected = json.loads(b64u_decode(b_head))
    registration = {"registration": re.search(r"registration\s+identifier\s+`([\w-]+)`", text).group(1)}
    mac = hmac.new(b64u_decode(code), f"{b_head}.{b_payload}".encode(), hashlib.sha256).digest()
    check(hmac.compare_digest(mac, b64u_decode(b_sig)) and b_protected == {
              "alg": "HS256", "kid": registration["registration"], "url": first_p["url"]}
          and b64u_decode(b_payload).decode() == first_p["kid"],
          "TS-4-03 registration binding: MAC under the code, kid, url, payload")
    genesis = answer("200, the answer to the first entry")
    w_proof = genesis["witness"]["proof"][0]
    witness_keys = witness_did_keys(trusted_list_payload())
    check(genesis["witness"]["versionId"] == entries[0]["versionId"]
          and webvh.verify_witness_proof(entries[0]["versionId"], w_proof)
          and w_proof["verificationMethod"].split("#")[0] in witness_keys,
          "TS-4-03 first entry witnessed by a witness the trusted list names")
    first_csr = x509.load_der_x509_csr(b64u_decode(first["certificationRequests"][0]["csr"]))
    first_dsc = x509.load_der_x509_certificate(b64u_decode(genesis["certificates"][0]["certificate"]))
    crl = x509.load_pem_x509_crl(block(TS_5_04, "issuer-root-ca.crl").encode())
    first_ski = first_dsc.extensions.get_extension_for_class(x509.SubjectKeyIdentifier).value.digest.hex().upper()
    check(first_csr.is_signature_valid and first_dsc.public_key() == first_csr.public_key()
          and first_dsc.subject == first_csr.subject
          and verify_chain(first_dsc, certificates(TS_5_04)["issuer-root-ca.pem"])
          and crl.get_revoked_certificate_by_serial_number(first_dsc.serial_number) is not None
          and first_ski in TS_5_01.read_text()
          and int(first_dsc.not_valid_before_utc.timestamp()) == webvh_time(entries[0]["versionTime"]),
          "TS-4-03 first entry's DSC: from its request, under the root, the one the CRL and the list revoke")
    credential = genesis["accreditationCredential"]
    check(credential in TS_5_07.read_text(), "TS-4-03 Accreditation Credential is the one TS-5-07 shows")
    check(jws_parts(credential.split("~")[0])[1]["sub"] == entries[0]["state"]["id"]
          and jws_parts(credential.split("~")[0])[1]["iat"] == webvh_time(entries[0]["versionTime"]),
          "TS-4-03 Accreditation Credential names the DID and takes effect at the first entry")

    # Key storage evidence chains to the maker root the build holds.
    maker = json.loads((ART / "entities.json").read_text())["maker_root"] if (ART / "entities.json").exists() else None
    root = x509.load_der_x509_certificate(b64u_decode(maker)) if maker else None
    for title, (_, payload) in requests.items():
        for item in (payload or {}).get("keyStorage", []):
            evidence = item.get("evidence", {})
            check(item["storage"] == "software" or evidence.get("format") in ("x509-chain", "assessment-report"),
                  f"TS-4-03 {item['key'][:14]}: evidence present in a listed format")
            if evidence.get("format") != "x509-chain":
                check(set(evidence) == {"format", "report"}, f"TS-4-03 {item['key'][:14]}: report evidence")
                continue
            leaf, device = (x509.load_der_x509_certificate(b64u_decode(c)) for c in evidence["certs"])
            check(verify_chain(leaf, device) and (root is None or verify_chain(device, root))
                  and webvh.multikey(leaf.public_key()) == item["key"] and item["storage"] in ("cloudkms", "hsm"),
                  f"TS-4-03 evidence for {item['key'][:14]}: chain and key")

    # The certificate request and what it returns.
    _, cert_req = requests["POST /entities/me/keys, a certificate request"]
    certs = certificates(TS_5_04)
    csr_page = x509.load_pem_x509_csr(block(TS_5_04, "document-signer.csr").encode())
    issued = answer("200, the answer to a certificate request")["certificates"]
    expected = {"issuance-cose": certs["document-signer.pem"], "status-list": certs["status-list-signer.pem"]}
    for request_item, issued_item in zip(cert_req["certificationRequests"], issued):
        csr = x509.load_der_x509_csr(b64u_decode(request_item["csr"]))
        cert = x509.load_der_x509_certificate(b64u_decode(issued_item["certificate"]))
        check(request_item["purpose"] == issued_item["purpose"] and csr.is_signature_valid
              and cert == expected[request_item["purpose"]] and cert.subject == csr.subject
              and cert.public_key() == csr.public_key(),
              f"TS-4-03 {request_item['purpose']} request and the TS-5-04 certificate it returns")
    check(x509.load_der_x509_csr(b64u_decode(cert_req["certificationRequests"][0]["csr"])) == csr_page,
          "TS-4-03 Document Signer request is the one TS-5-04 shows")
    check(cert_req["keyStorage"][0]["key"] == webvh.multikey(certs["document-signer.pem"].public_key()),
          "TS-4-03 storage evidence covers the new issuance-cose key")

    # The Verifier Issuing CA request returns the TS-5-04 certificate.
    _, ca_req = requests["POST /entities/me/keys, a Verifier Issuing CA request"]
    ca_csr = x509.load_der_x509_csr(b64u_decode(ca_req["certificationRequests"][0]["csr"]))
    ca_cert = x509.load_der_x509_certificate(b64u_decode(
        answer("200, the answer to a Verifier Issuing CA request")["certificates"][0]["certificate"]))
    check(ca_csr.is_signature_valid and ca_cert == certs["verifier-issuing-ca.pem"]
          and ca_cert.public_key() == ca_csr.public_key() and ca_cert.subject == ca_csr.subject
          and ca_req["keyStorage"][0]["key"] == webvh.multikey(ca_csr.public_key()),
          "TS-4-03 Verifier Issuing CA request and the TS-5-04 certificate it returns")

    # The rotation is the Publisher request TS-4-01 shows.
    rot_p, rotation = requests["POST /entities/me/keys, a rotation"]
    publisher = http_body(block(TS_4_01, "POST /entries"))
    check(rotation["logEntry"] == publisher["logEntry"] == entries[1]
          and rotation["proofOfPossession"] == publisher["proofOfPossession"]
          and rot_p["nonce"] == publisher["nonce"],
          "TS-4-03 rotation carries the entry, proofs and nonce TS-4-01 hands on")
    check(rot_p["kid"].removeprefix("did:key:").split("#")[0] in entries[0]["parameters"]["updateKeys"],
          "TS-4-03 rotation signed with the update key of the latest witnessed entry")
    pops_cover(rot_p, rotation, entries[1], set(entries[0]["parameters"]["updateKeys"]) | {
        m["publicKeyMultibase"] for m in entries[0]["state"]["verificationMethod"]})
    check(answer("200, the answer to a rotation")["witness"]
          == json.loads(block(TS_4_01, "did-witness.json, the proof")),
          "TS-4-03 rotation answer is the witness proof TS-4-01 returns")
    software = json.loads(block(TS_4_03, "A storage item for a key in the software keystore"))
    check(software.get("storage") == "software" and "evidence" not in software
          and any(software["key"] in {m["publicKeyMultibase"] for m in e["entries"][-1]["state"]["verificationMethod"]}
                  for e in (db or {"entities": {}})["entities"].values()),
          "TS-4-03 software storage item: no evidence, a key a log publishes")
    problem = answer("400, the answer to a request whose nonce was used")
    check(problem["type"] == "https://idctf.id/ns/problems/bad-nonce" and problem["status"] == 400
          and "`bad-nonce` | `400` | `Bad nonce`" in text,
          "TS-4-03 problem document is a listed type")


# --------------------------------------------------------------------------
# TS-1-01, the exchanges between Mobile Wallet and Issuer Core
# --------------------------------------------------------------------------

TS_1_01 = TS / "issuing-a-credential-via-openid4vci.md"


def check_issuance() -> None:
    """The bindings between the messages of one issuance, read off the page."""
    pages = blocks(TS_1_01)

    def body(title: str) -> str:
        return block(TS_1_01, title)

    def headers(text: str) -> dict[str, str]:
        head = text.split("\n\n", 1)[0].split("\n")[1:]
        return dict(line.split(": ", 1) for line in head)

    # Every DPoP proof matches its request, and its nonce is one Issuer Core gave.
    given: set[str] = set()
    for title, bodies in pages.items():
        for text in bodies:
            if text.startswith("HTTP/1.1") and "DPoP-Nonce" in headers(text):
                given.add(headers(text)["DPoP-Nonce"])
    for title, bodies in pages.items():
        for text in bodies:
            if not re.match(r"(GET|POST) ", text):
                continue
            head = headers(text)
            if "DPoP" not in head:
                continue
            header, claims, signature, signing_input = jws_parts(head["DPoP"])
            method, path = text.split("\n")[0].split()[:2]
            ok = (header.get("typ") == "dpop+jwt" and verify_raw(jwk_key(header["jwk"]), signature, signing_input)
                  and claims["htm"] == method and claims["htu"] == f"https://{head['Host']}{path}")
            check(ok, f"TS-1-01 {title[:44]}: DPoP signature, htm, htu")
            if "nonce" in claims:
                check(claims["nonce"] in given, f"TS-1-01 {title[:44]}: DPoP nonce was given by the issuer")
            if "Authorization" in head:
                token = head["Authorization"].removeprefix("DPoP ")
                check(claims.get("ath") == sha256_b64u(token.encode()), f"TS-1-01 {title[:44]}: ath hashes the access token")

    # The signed metadata ties the issuer identifier to the DID that signs the credential.
    bkn = jws_parts(body("200, the signed issuer metadata").split("\n\n", 1)[1])[1]
    offer = json.loads(body("The same credential offer, decoded"))
    check(bkn["sub"] == bkn["credential_issuer"] == offer["credential_issuer"],
          "TS-1-01 BKN metadata sub and credential_issuer are the offer's issuer")
    duk = jws_parts(body("200, Dukcapil's signed issuer metadata").split("\n\n", 1)[1])[1]
    check(duk == json.loads(body("Dukcapil's issuer metadata claims")) and duk["sub"] == http_body(body("200, the credential offer"))["credential_issuer"],
          "TS-1-01 Dukcapil metadata is the one decoded and names the offer's issuer")
    check(set(offer["credential_configuration_ids"]) == set(bkn["credential_configurations_supported"]),
          "TS-1-01 the BKN offer names every configuration of the type")
    for name, meta in (("BKN", bkn), ("Dukcapil", duk)):
        for config_id, config in meta["credential_configurations_supported"].items():
            rulebook, _, form = config_id.partition(":")
            namespace_ok = all(c["path"][0] == rulebook for c in config["credential_metadata"]["claims"]) \
                if config["format"] == "mso_mdoc" else True
            check(namespace_ok and (config.get("vct") or config.get("doctype")) == rulebook,
                  f"TS-1-01 {name} {config_id}: type identifier and mdoc claim paths follow the Rulebook")

    # The token response gives one identifier per configuration asked for.
    granted = http_body(body("200, the access token and the credential identifiers"))
    check([d["credential_configuration_id"] for d in granted["authorization_details"]] == offer["credential_configuration_ids"]
          and all(len(d["credential_identifiers"]) == 1 for d in granted["authorization_details"]),
          "TS-1-01 one credential identifier per configuration")

    # The credential request carries the key proof TS-5-08 shows, against the c_nonce served.
    request = http_body(body("POST /credential, the Kartu ASN as SD-JWT VC"))
    proof = request["proofs"]["jwt"][0]
    check(proof == joined(block(TS_5_08, "A key proof carrying the attestation in its header")),
          "TS-1-01 the key proof is the one TS-5-08 shows")
    proof_header, proof_claims, _, _ = jws_parts(proof)
    check(proof_claims["aud"] == offer["credential_issuer"] and proof_claims["nonce"] == http_body(body("200, a fresh c_nonce"))["c_nonce"]
          and "iss" not in proof_claims,
          "TS-1-01 key proof aud, c_nonce, and no iss under anonymous access")
    check(request["credential_identifier"] == granted["authorization_details"][0]["credential_identifiers"][0],
          "TS-1-01 the credential request names an identifier the token response gave")

    # The credentials are the ones TS-5-10 shows.
    sd_jwt = http_body(body("200, the Kartu ASN as SD-JWT VC"))["credentials"][0]["credential"]
    check(sd_jwt == joined(block(TS_5_10, "A Kartu ASN in SD-JWT VC, as issued")), "TS-1-01 the SD-JWT VC is the one TS-5-10 shows")
    sd_claims = jws_parts(sd_jwt.split("~")[0])[1]
    check(sd_claims["iss"] == bkn["iss"] and sd_claims["cnf"]["jwk"] == proof_header["jwk"],
          "TS-1-01 the SD-JWT VC is signed by the metadata's DID and bound to the attested key")
    mdoc = http_body(body("200, the KTP Digital as mdoc"))["credentials"][0]["credential"]
    check(b64u_decode(mdoc) == bytes.fromhex(joined(block(TS_5_10, "The mdoc IssuerSigned, as issued"))),
          "TS-1-01 the mdoc is the IssuerSigned TS-5-10 shows")
    nikah = http_body(body("200, the Kartu Nikah as ldp_vc"))["credentials"][0]["credential"]
    check(nikah == json.loads(block(TS_5_10, "A Kartu Nikah in ldp_vc, as issued")), "TS-1-01 the ldp_vc is the one TS-5-10 shows")

    # The Authorization Code flow: PKCE, state, iss, and the attestation proof.
    par = dict(p.split("=", 1) for p in body("POST /par, the pushed authorization request").split("\n\n", 1)[1].split("&"))
    token = dict(p.split("=", 1) for p in body("POST /token, the authorization code").split("\n\n", 1)[1].split("&"))
    check(sha256_b64u(token["code_verifier"].encode()) == par["code_challenge"] and par["code_challenge_method"] == "S256",
          "TS-1-01 the code verifier hashes to the PAR challenge")
    location = headers(body("303, back to the wallet with the code"))["Location"]
    back = dict(p.split("=", 1) for p in location.split("?", 1)[1].split("&"))
    check(back["state"] == par["state"] and back["code"] == token["code"]
          and back["iss"].replace("%3A", ":").replace("%2F", "/") == duk["credential_issuer"],
          "TS-1-01 the authorization response carries the state, the code and the issuer")
    attestation = http_body(body("POST /credential, the KTP Digital with an attestation proof"))["proofs"]["attestation"][0]
    check(jws_parts(attestation)[1] == json.loads(body("The Key Attestation for Dukcapil's nonce, decoded")),
          "TS-1-01 the attestation proof is the one decoded")
    deferred = http_body(body("202, the KTP Digital deferred"))
    check(http_body(body("POST /deferred_credential")) == {"transaction_id": deferred["transaction_id"]},
          "TS-1-01 the deferred request carries the transaction identifier it was given")


def run(name: str, function, *args):
    """Run one group; a page that cannot be read is a failed check, not a crash."""
    try:
        return function(*args)
    except Exception as error:  # noqa: BLE001
        check(False, f"{name}: the page could not be read", repr(error)[:200])
        return None


# ---------------------------------------------------------------------------
# TS-3-02, the proximity session

TS_3_02 = TS / "verifying-a-credential-in-proximity-via-iso-iec-18013-5.md"


def check_proximity() -> None:
    """The session of TS-3-02 against the transcript and response of TS-5-11."""
    import base64  # noqa: PLC0415

    from cryptography.hazmat.primitives.ciphers.aead import AESGCM  # noqa: PLC0415
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF  # noqa: PLC0415

    enc = presentations.enc
    transcript = presentations.parse_diag(block(TS_5_11, "The SessionTranscript of that session"))
    transcript_bytes = enc(cbor2.CBORTag(24, enc(transcript)))

    qr = block(TS_3_02, "The QR code of the engagement").strip()
    payload = qr[len("mdoc:"):]
    engagement_bytes = base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4))
    check(
        qr.startswith("mdoc:") and "=" not in payload and engagement_bytes == transcript[0].value,
        "TS-3-02 QR code carries the DeviceEngagement of the TS-5-11 SessionTranscript",
    )
    check(
        enc(presentations.parse_diag(block(TS_3_02, "The DeviceEngagement, in CBOR"))) == engagement_bytes,
        "TS-3-02 DeviceEngagement diagnostic notation is the engagement the QR code carries",
    )
    engagement = cbor2.loads(engagement_bytes)
    check(
        engagement[0] == "1.0" and engagement[1][0] == 1 and 3 not in engagement
        and [m[0] for m in engagement[2]] == [2] and engagement[2][0][2][1] is True,
        "TS-3-02 DeviceEngagement: version 1.0, cipher suite 1, BLE in mdoc central client mode, no server retrieval",
    )

    keys = dict(line.split() for line in block(TS_3_02, "The session keys of that session").splitlines() if line.strip())
    z_ab, salt = bytes.fromhex(keys["ZAB"]), bytes.fromhex(keys["salt"])
    sk_reader, sk_device = bytes.fromhex(keys["SKReader"]), bytes.fromhex(keys["SKDevice"])

    def derive(info: str) -> bytes:
        return HKDF(hashes.SHA256(), 32, salt, info.encode()).derive(z_ab)

    check(
        salt == hashlib.sha256(transcript_bytes).digest()
        and derive("SKReader") == sk_reader and derive("SKDevice") == sk_device,
        "TS-3-02 session keys derive by HKDF-SHA-256 from ZAB, salted with the SessionTranscriptBytes",
    )

    establishment = cbor2.loads(bytes.fromhex(joined(block(TS_3_02, "The SessionEstablishment, as sent"))))
    check(
        establishment["eReaderKey"] == transcript[1],
        "TS-3-02 SessionEstablishment carries the eReaderKey of the TS-5-11 SessionTranscript",
    )
    device_priv_path = None
    try:
        sys.path.insert(0, str(ROOT / "scripts" / "artifacts"))
        from keystore import keystore_dir  # noqa: PLC0415

        device_priv_path = keystore_dir() / "proximity-edevice-1.pem"
    except ImportError:
        pass
    if device_priv_path is not None and device_priv_path.exists():
        device_priv = serialization.load_pem_private_key(device_priv_path.read_bytes(), password=None)
        reader_key = cbor2.loads(transcript[1].value)
        reader_pub = ec.EllipticCurvePublicNumbers(
            int.from_bytes(reader_key[-2], "big"), int.from_bytes(reader_key[-3], "big"), ec.SECP256R1()
        ).public_key()
        check(device_priv.exchange(ec.ECDH(), reader_pub) == z_ab, "TS-3-02 ZAB is the ECDH of the wallet's ephemeral key and eReaderKey")
    else:
        check(False, "TS-3-02 ZAB needs the keystore key proximity-edevice-1")

    request_bytes = AESGCM(sk_reader).decrypt(bytes(8) + (1).to_bytes(4, "big"), establishment["data"], b"")
    request = cbor2.loads(request_bytes)
    shown = block(TS_3_02, "The DeviceRequest, in CBOR diagnostic notation")
    jwt = re.search(r"(?<!h)'([A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+)'", shown).group(1)
    shown = shown.replace("'" + jwt + "'", "h'" + jwt.encode().hex() + "'")
    check(
        enc(presentations.parse_diag(shown)) == request_bytes,
        "TS-3-02 SessionEstablishment decrypts under SKReader, counter 1, to the DeviceRequest shown",
    )
    items_bytes = bytes.fromhex(joined(block(TS_5_06, "The same ItemsRequest, as CBOR")))
    doc = request["docRequests"][0]
    check(
        request["version"] == "1.0" and len(request["docRequests"]) == 1 and doc["itemsRequest"].value == items_bytes,
        "TS-3-02 DeviceRequest carries the TS-5-06 ItemsRequest byte for byte in one DocRequest",
    )
    items = cbor2.loads(items_bytes)
    check(
        all(v is False for ns in items["nameSpaces"].values() for v in ns.values())
        and set(items["requestInfo"]) == {"idUseStatement"},
        "TS-3-02 every IntentToRetain is false and requestInfo holds idUseStatement alone",
    )
    protected, unprotected, detached, signature = doc["readerAuth"]
    chain = [x509.load_der_x509_certificate(c) for c in unprotected[33]]
    pages = certificates(TS_5_04)
    device_pem = next(c for t, c in pages.items() if t.startswith("verifier-device.pem"))
    issuing_pem = next(c for t, c in pages.items() if t.startswith("verifier-issuing-ca.pem"))
    check(
        cbor2.loads(protected) == {1: -7} and set(unprotected) == {33} and detached is None
        and [c.fingerprint(hashes.SHA256()) for c in chain]
        == [device_pem.fingerprint(hashes.SHA256()), issuing_pem.fingerprint(hashes.SHA256())],
        "TS-3-02 ReaderAuth: ES256 alone protected; x5chain is the TS-5-04 device then issuing certificate, no root",
    )
    authentication = enc(cbor2.CBORTag(24, enc(["ReaderAuthentication", transcript, doc["itemsRequest"]])))
    check(
        verify_raw(chain[0].public_key(), signature, enc(["Signature1", protected, b"", authentication])),
        "TS-3-02 ReaderAuth verifies under the Verifier Device Certificate over the TS-5-11 SessionTranscript",
    )
    allowed = reader_auth_role(chain[0])
    check(
        all(e in allowed.get(items["docType"], set()) for ns in items["nameSpaces"].values() for e in ns),
        "TS-3-02 every data element asked for sits inside the ReaderAuthRole of the signing certificate",
    )

    data = cbor2.loads(bytes.fromhex(joined(block(TS_3_02, "The SessionData carrying the DeviceResponse, as sent"))))
    response = AESGCM(sk_device).decrypt(bytes(7) + b"\x01" + (1).to_bytes(4, "big"), data["data"], b"")
    check(
        set(data) == {"data"} and response == bytes.fromhex(joined(block(TS_5_11, "The DeviceResponse, as sent"))),
        "TS-3-02 SessionData decrypts under SKDevice, counter 1, to the TS-5-11 DeviceResponse",
    )
    end = block(TS_3_02, "The SessionData that ends the session").split()[0]
    check(cbor2.loads(bytes.fromhex(end)) == {"status": 20}, "TS-3-02 the session ends with status 20 and no data")
    errors = [cbor2.loads(bytes.fromhex(line)) for line in block(TS_3_02, "The SessionData of the two error statuses").split()]
    check(errors == [{"status": 10}, {"status": 11}], "TS-3-02 the two error SessionData carry status 10 and 11 and no data")
    both = presentations.parse_diag(block(TS_3_02, "The BleOptions of an engagement offering both BLE modes"))
    check(
        both[0] is True and both[1] is True and len(both[10]) == 16 and len(both[11]) == 16
        and both[10] != both[11] and 20 not in both and 20 not in engagement[2][0][2],
        "TS-3-02 BleOptions name a UUID per mode offered and no device address",
    )
    ids = re.findall(r"#(req-ts-3-02-\d{3}) ", TS_3_02.read_text())
    check(len(ids) == len(set(ids)), f"TS-3-02 carries {len(ids)} requirements, each identifier once")

    hs = bytes.fromhex(joined(block(TS_3_02, "The Handover Select message of an NFC engagement")))
    records = [line for line in block(TS_3_02, "The same Handover Select message").splitlines() if re.fullmatch(r"[0-9a-f]+", line)]
    nfc = presentations.parse_diag(block(TS_3_02, "The SessionTranscript of the NFC engagement"))
    nfc_engagement = enc(nfc[0].value) if not isinstance(nfc[0].value, bytes) else nfc[0].value
    check(bytes.fromhex("".join(records)) == hs, "TS-3-02 the Handover Select records concatenate to the message")
    check(
        hs[:6] == bytes.fromhex("91020f487315") and b"iso.org:18013:deviceengagement" in hs
        and b"application/vnd.bluetooth.le.oob" in hs and nfc[2] == [hs, None] and nfc_engagement in hs
        and 2 not in cbor2.loads(nfc_engagement),
        "TS-3-02 NFC Static Handover: Hs 1.5, the engagement without retrieval methods, Handover [Hs, null]",
    )


# ---------------------------------------------------------------------------
# TS-3-01, the online exchange

TS_3_01 = TS / "verifying-a-credential-online-via-openid4vp.md"


def jwe_open(private_key, token: str) -> tuple[dict, dict]:
    """ECDH-ES direct key agreement with A128GCM, empty apu and apv (RFC 7518 4.6)."""
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM  # noqa: PLC0415

    protected, encrypted_key, iv, ciphertext, tag = token.split(".")
    header = json.loads(b64u_decode(protected))
    z = private_key.exchange(ec.ECDH(), jwk_key(header["epk"]))
    enc = header["enc"].encode()
    other = len(enc).to_bytes(4, "big") + enc + bytes(8) + (128).to_bytes(4, "big")
    cek = hashlib.sha256((1).to_bytes(4, "big") + z + other).digest()[:16]
    plain = AESGCM(cek).decrypt(
        b64u_decode(iv), b64u_decode(ciphertext) + b64u_decode(tag), protected.encode("ascii")
    )
    return header, json.loads(plain)


def check_online() -> None:
    from urllib.parse import parse_qs, urlsplit  # noqa: PLC0415

    page = blocks(TS_3_01)
    one = lambda title: page[title][0]  # noqa: E731
    # The first exchange: the request TS-5-06 shows, as it travels.
    qr = parse_qs(urlsplit(one("The authorization request in the QR code")).query)
    jws = one("200, the signed Request Object").split("\n\n", 1)[1].strip()
    header, payload, _, _ = jws_parts(jws)
    shown = json.loads(block(TS_5_06, "The Use Statement in a Request Object, online"))
    check(payload == shown, "TS-3-01 the served Request Object is the one TS-5-06 shows")
    check(
        json.loads(one("Protected header of the Request Object")) == header
        and set(header) == {"typ", "alg", "kid"} and header["typ"] == "oauth-authz-req+jwt",
        "TS-3-01 Request Object header: typ, alg and kid alone",
    )
    check(
        set(qr) == {"client_id", "request_uri"} and qr["client_id"] == [payload["client_id"]]
        and urlsplit(qr["request_uri"][0]).path
        == one("GET of the request URI").split()[1],
        "TS-3-01 the QR code carries the Request Object's client_id and the URI the wallet fetches",
    )
    for name, request in (
        ("Kartu ASN", payload),
        ("Kartu Nikah", json.loads(block(TS_5_06, "The Use Statement of the Kartu Nikah use in a Request Object"))),
    ):
        check(
            {"state", "iat", "exp", "aud"} <= set(request)
            and "vp_formats_supported" in request["client_metadata"]
            and len(request["client_metadata"]["jwks"]["keys"]) == 1
            and len(b64u_decode(request["state"])) >= 16
            and request["response_mode"] == "direct_post.jwt",
            f"TS-3-01 {name} Request Object carries every claim the table marks present",
        )
    post = one("POST of the encrypted response")
    jwe = post.split("\n\n", 1)[1].removeprefix("response=")
    check(
        json.loads(b64u_decode(jwe.split(".")[0])) == json.loads(one("Protected header of the encrypted response"))
        and jwe.split(".")[1] == "",
        "TS-3-01 the response header block is the JWE's, with no encrypted key",
    )
    decrypted = json.loads(one("The response, decrypted"))
    check(
        decrypted["state"] == payload["state"]
        and decrypted["vp_token"] == json.loads(block(TS_5_11, "The vp_token of an SD-JWT VC presentation")),
        "TS-3-01 the decrypted response carries the TS-5-11 vp_token and the request's state",
    )
    enc_private = keystore_private("openid4vp-response-key-asn")
    if enc_private is not None:
        _, plain = jwe_open(enc_private, jwe)
        check(plain == decrypted, "TS-3-01 the response decrypts under the key the Request Object names")
    refusal = json.loads(one("The response of a citizen who refuses, decrypted"))
    nikah = json.loads(block(TS_5_06, "The Use Statement of the Kartu Nikah use in a Request Object"))
    check(
        refusal == {"error": "access_denied", "state": nikah["state"]},
        "TS-3-01 the refusal carries access_denied and the Kartu Nikah request's state alone",
    )
    # The merchant's exchange through the relay.
    m_jws = joined(one("The merchant's Request Object, as the relay serves it"))
    m_header, m_payload, _, _ = jws_parts(m_jws)
    check(
        m_header == json.loads(one("Protected header of the merchant's Request Object"))
        and m_payload == json.loads(one("Claims of the merchant's Request Object")),
        "TS-3-01 the merchant's header and claims blocks decode from the token",
    )
    certs = certificates(TS_5_04)
    device_der = certs["verifier-device.pem"].public_bytes(serialization.Encoding.DER)
    issuing_der = certs["verifier-issuing-ca.pem"].public_bytes(serialization.Encoding.DER)
    check(
        [base64.b64decode(c) for c in m_header["x5c"]] == [device_der, issuing_der]
        and m_payload["client_id"] == "x509_hash:" + base64.urlsafe_b64encode(
            hashlib.sha256(device_der).digest()).decode().rstrip("="),
        "TS-3-01 x5c is the TS-5-04 device and issuing certificates, and x509_hash is the device's",
    )
    check(
        verify_jws(m_jws, certs["verifier-device.pem"].public_key()),
        "TS-3-01 the merchant's Request Object verifies under the device key",
    )
    statement = m_payload["verifier_info"][0]["data"]
    statements = [s.strip() for s in blocks(TS_5_06)["The same statement, as the verifier carries it"]]
    claims = jws_parts(statement)[1]["claims"]
    asked = {f"id.idctf.kartu-asn.1#{c['path'][0]}" for c in m_payload["dcql_query"]["credentials"][0]["claims"]}
    role = reader_auth_role(certs["verifier-device.pem"])
    check(
        statement in statements and asked <= set(claims)
        and {a.split("#")[1] for a in asked} <= role.get("id.idctf.kartu-asn.1", set()),
        "TS-3-01 the merchant asks inside its category statement and its ReaderAuthRole",
    )
    m_decrypted = json.loads(one("The merchant's response, decrypted on the device"))
    presentation = m_decrypted["vp_token"]["kartu-asn"][0]
    _, kb, _, _ = jws_parts(presentation.rsplit("~", 1)[1])
    check(
        m_decrypted["state"] == m_payload["state"]
        and kb["aud"] == m_payload["client_id"] and kb["nonce"] == m_payload["nonce"],
        "TS-3-01 the merchant's presentation is bound to its x509_hash client_id and nonce",
    )
    device_x = base64.urlsafe_b64encode(
        certs["verifier-device.pem"].public_key().public_numbers().x.to_bytes(32, "big")
    ).decode().rstrip("=")
    keys = [r["client_metadata"]["jwks"]["keys"][0]["x"] for r in (payload, nikah, m_payload)]
    check(
        len(set(keys)) == 3 and device_x not in keys,
        "TS-3-01 every Request Object names an encryption key of its own, never the device key",
    )
    device_private = keystore_private("openid4vp-response-key-merchant")
    if device_private is not None:
        m_jwe = one("POST of the merchant's encrypted response to the relay").split("\n\n", 1)[1].removeprefix("response=")
        _, plain = jwe_open(device_private, m_jwe)
        check(plain == m_decrypted, "TS-3-01 the merchant's response decrypts under the key its Request Object names, not the device key")
    ids = re.findall(r"\*\*(REQ-TS-3-01-\d{3})\*\*", TS_3_01.read_text())
    check(len(ids) == len(set(ids)), f"TS-3-01 carries {len(ids)} requirements, each identifier once")


def keystore_private(name: str):
    sys.path.insert(0, str(ROOT / "scripts" / "artifacts"))
    from keystore import keystore_dir  # noqa: PLC0415

    path = keystore_dir() / f"{name}.pem"
    if not path.exists():
        return None
    return serialization.load_pem_private_key(path.read_bytes(), password=None)


def main() -> None:
    run("Reader branch", check_reader_branch)
    if webvh_db() is None:
        print("build/artifacts/webvh.json absent: only dukcapil's DID Document and did:key resolve")
    verified = run("JWS sweep", check_jws_sweep)
    check(bool(verified), f"JWS sweep found {len(verified or [])} verifiable tokens")
    run("did:webvh log", check_webvh_log)
    run("Publisher request", check_publisher_request)
    lists = run("Status lists", check_status_lists)
    run("TS-01 status list", check_ts01_status_list)
    issued = run("Credentials", check_credentials)
    if issued:
        run("Presentations", check_presentations, issued)
    else:
        check(False, "Presentations and shared keys need the credentials above")
    run("Data Integrity", check_data_integrity)
    run("Issuer X.509 branch", check_issuer_branch)
    run("mDL issuer", check_mdl_issuer)
    run("Trusted list", check_trusted_list)
    run("Governance Profile", check_governance_profile)
    run("Key attestation", check_key_attestation)
    run("Wallet enrollment", check_enrollment)
    run("Decoded blocks", check_decoded_blocks)
    if issued:
        run("Shared identifiers", check_shared_identifiers, issued)
    if lists:
        run("Status pointers", check_statuses, lists)
    run("Authority identifiers", check_authority_identifiers)
    run("Trust Registry", check_trust_registry)
    run("Signing inside a permission", check_signing_inside_permission)
    run("Entity endpoint", check_entity_endpoint)
    run("Issuance", check_issuance)
    run("Proximity", check_proximity)
    run("Online", check_online)

    print(f"\n{checks - len(failures)}/{checks} checks passed")
    if failures:
        sys.exit(1)

if __name__ == "__main__":
    main()
