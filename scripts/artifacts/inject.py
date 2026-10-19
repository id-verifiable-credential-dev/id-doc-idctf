"""Write the artifacts ``build.py`` generated into the pages that show them.

Each artifact lands in the fenced block whose ``title=`` names it, and the
values the tables repeat, the subject key identifiers and the DER sizes, are
replaced wherever they appear. Run ``build.py`` first.

Run: ``.venv/bin/python scripts/artifacts/inject.py``
"""

from __future__ import annotations

import base64
import json
import re
from pathlib import Path

import cbor2

from keystore import REPO_ROOT

OUT = REPO_ROOT / "build" / "artifacts"
DOCS = REPO_ROOT / "docs"
TS = DOCS / "technical-specifications"

# The identifiers the pages carried before the rebuild of tracks/0293, each
# with the entity whose new identifier replaces it. A self-certifying
# identifier is a hash of a log entry, so a rebuilt log gives a new one, and
# every page that names the entity moves with it.
OLD_SCIDS = {
    "QmPqCtppckKCt28QvVA3khYg2re3T63rMZ5vLdK5R4Wyvc": "trust-authority",
    "QmVKedV3NnPibhEGcL23QGemXmLyLxcbNVwRpLVDXucyqQ": "dukcapil",
    "QmZckxxGrhPDEJojTXQQGjDF3qEyBvMHvcFwK8w86nzQGh": "bkn",
    "QmW12U9Ph24uxanT1VeXeRtyGW5sfKrDTm4bFhLuQwaBwm": "kemenag",
    "QmcEDLuNdG389YS6Sr18NBwC5dHmt5eAEnzHhXP8jXreDG": "terminal-nusantara",
    "QmeRcpDUtUiFc28aVTBhF8JAL9wjTpSXjUjcrA9YRTrunK": "dompet-digital-nusantara",
    "QmfS4F4RAGFnDpMhhfFfxubGDbY5m9Xc1bttQ7iE1HmYKE": "universitas-nusantara",
}

TS_5_01 = TS / "publishing-and-reading-the-trusted-list.md"
TS_5_04 = TS / "issuing-and-validating-the-x509-certificates-and-the-vical.md"
TS_5_05 = TS / "answering-with-an-authority-statement.md"
TS_5_06 = TS / "registering-and-carrying-a-use-statement.md"
TS_5_07 = TS / "issuing-and-carrying-an-accreditation-credential.md"

# The values the pages carried before this run, so that a table row that
# repeats one is moved with the artifact that holds it.
OLD = {
    "verifier_root_ca_ski": "04BE11ECE4493B07546EE83F707AF410EB2DDC36",
    "verifier_issuing_ca_ski": "4646C7BC7F86A2620DF80B51673757E5C0E2B840",
    "verifier_device_ski": "F5653CC2D5FCDB7F3B980B4E0618FEC4EDF78F58",
}


# A subject key identifier is a hash of a public key, so a rebuilt branch
# moves every one of them, in the certificate and in every table that
# repeats it.
OLD_SKIS = {
    "70B452A7CAAAF21F92139F4AB49515F5E35B4E47": "issuer-root-ca",
    "BFEE3BDBB507A2E549DA412C5E28C299DC73FA50": "document-signer",
    "D9B8BB28349B10226330CB2160706799BD2C8F60": "vical-signer",
    "E5905EA39A99A4D59C2819F8C21D78FE795F4DD9": "foreign-my-root",
    "44D6E11DA9C57DA66A8CAFEB1F3946094F573B59": "document-signer-retired",
}

OLD_SIGNER_KEYS = {
    "zDnaec3EgK8Pxu9RqJWWNARNmNmFdiE2cWTAjEXyJfWCXQ22B": "ta-trusted-list-1",
    "zDnaej78VUfDkh5wzzjKtM3nPHQYTWwb6ADPt4D36h1ByDGgg": "ta-trusted-list-2",
}

OLD_MULTIKEYS = {
    "z6MkvmYnxpmRVof97p7pLzjdaqK4X9zhA7BWAdE9tpe1Rm9k": ("witness", "ta-witness-1"),
    "z6MkeVA1AGRbdW7QMWWELuVBo75xwHzMjBENGG7zc1Y44KGP": ("witness", "ta-witness-2"),
    "zDnaewZQY1BzgCoWTXYB8w6uUSAkv52XRU6snCLRLHnhbGk65": ("holder", "holder-credential-1"),
    "zDnaewCz6BDY9K6QHRWthxrLjYV3rc2C3xhFhfsLEpyJgmtaj": ("dukcapil", "issuance-jose-1"),
    "zDnaevW5VQ2i1dfoveW8KFRNttLoQTcnefxnYJJUwdmZ54Bde": ("dukcapil", "status-list-1"),
    "zDnaezMqUP3fFPyz6qn6FCUUhVjy4jjPkfBW3UxT6s7iYLiHd": ("dukcapil", "issuance-jose-2"),
}


def renames() -> dict[str, str]:
    """Every identifier the rebuild replaces, old value to new value.

    A bare Multikey is renamed as well as the ``did:key`` around it, because
    the trusted list and a verification method carry the key without it.
    """
    webvh = json.loads((OUT / "webvh.json").read_text())
    table = {
        old: webvh["entities"][slug]["scid"] for old, slug in OLD_SCIDS.items()
    }
    x509 = json.loads((OUT / "x509.json").read_text())
    for old, label in OLD_SKIS.items():
        table[old] = x509["certificates"][label]["ski"]
    signer = json.loads((OUT / "trustlist.json").read_text())["_structured"]["signers"]
    for old, name in OLD_SIGNER_KEYS.items():
        table[old] = signer[name]["multikey"]
    holder = json.loads((OUT / "statuslists.json").read_text())["holder"]
    for old, (owner, name) in OLD_MULTIKEYS.items():
        if owner == "witness":
            table[old] = webvh["witness_keys"][name]["multikey"]
        elif owner == "holder":
            table[old] = holder["multikey"]
        else:
            table[old] = webvh["entities"][owner]["keys"][name]["multikey"]
    return table


def rename_identifiers(table: dict[str, str]) -> dict[str, int]:
    """Replace every old identifier in ``docs/``, reporting what moved."""
    moved: dict[str, int] = {}
    for path in sorted(DOCS.rglob("*.md")) + sorted(DOCS.rglob("*.json")):
        text = path.read_text()
        edited = text
        for old, new in table.items():
            if old in edited:
                moved[old] = moved.get(old, 0) + edited.count(old)
                edited = edited.replace(old, new)
        if edited != text:
            path.write_text(edited)
    return moved


def check_renamed(table: dict[str, str]) -> list[str]:
    """Every old identifier still in ``docs/``, which is a page left behind."""
    left = []
    for path in sorted(DOCS.rglob("*.md")) + sorted(DOCS.rglob("*.json")):
        text = path.read_text()
        for old in table:
            if old in text:
                left.append(f"{path.relative_to(REPO_ROOT)}: {old}")
    return left


def read_blocks(path: Path) -> list[tuple[int, int, str]]:
    """Every fenced block in ``path``: its opening line, closing line, title."""
    lines = path.read_text().split("\n")
    blocks = []
    opening = None
    title = ""
    for number, line in enumerate(lines):
        if opening is None and line.startswith("```") and len(line) > 3:
            opening = number
            match = re.search(r'title="([^"]*)"', line)
            title = match.group(1) if match else ""
        elif opening is not None and line.strip() == "```":
            blocks.append((opening, number, title))
            opening = None
    return blocks


def replace_block(path: Path, title: str, body: str, occurrence: int = 0) -> None:
    lines = path.read_text().split("\n")
    matches = [b for b in read_blocks(path) if b[2] == title]
    if len(matches) <= occurrence:
        raise SystemExit(f"{path.name}: no block {occurrence} titled {title!r}")
    start, end, _ = matches[occurrence]
    lines[start + 1 : end] = body.split("\n")
    path.write_text("\n".join(lines))


FAMILIES = {
    "statuslists.json": None,
    "credentials.json": "blocks",
    "x509.json": "blocks",
    "ldp.json": "blocks",
    "trustlist.json": None,
    "trqp.json": "blocks",
    "presentations.json": "blocks",
    "entities.json": "blocks",
    "enrollment.json": None,
    "issuance.json": "blocks",
    "proximity.json": "blocks",
    "openid4vp.json": "blocks",
    "governance.json": "blocks",
}


def locate(title: str) -> list[tuple[Path, int]]:
    """Every page holding a block with ``title``, with how many it holds."""
    found = []
    for path in sorted(TS.glob("*.md")):
        count = len([b for b in read_blocks(path) if b[2] == title])
        if count:
            found.append((path, count))
    return found


def inject_family(name: str, container: str | None) -> int:
    """Write each block a generator produced into the page that shows it.

    A title names one block on one page, so an ambiguous or missing title is
    an error rather than a guess: the generator and the page have drifted.
    """
    path = OUT / name
    if not path.exists():
        raise SystemExit(f"{path} is missing: run its generator first")
    payload = json.loads(path.read_text())
    blocks = payload if container is None else payload[container]
    written = 0
    for title, body in blocks.items():
        if not isinstance(body, str):
            continue
        found = locate(title)
        if len(found) != 1 or found[0][1] != 1:
            raise SystemExit(f"{name}: {title!r} matches {found}, expected one block")
        replace_block(found[0][0], title, body.rstrip("\n"))
        written += 1
    return written


def replace_everywhere(paths: list[Path], old: str, new: str) -> int:
    hits = 0
    for path in paths:
        text = path.read_text()
        if old in text:
            hits += text.count(old)
            path.write_text(text.replace(old, new))
    return hits


def wrap(value: str, width: int = 64) -> str:
    return "\n".join(value[i : i + width] for i in range(0, len(value), width))


def reader_auth_role_text(entries: list[tuple[str, list[str]]], der: bytes) -> str:
    """The extension as the page shows it: the structure, then its hex."""

    def length(payload: int) -> str:
        return f"{payload:02X}"

    lines = []
    outer = len(der) - 2
    lines.append(f"30 {length(outer)}")
    for doc_type, elements in entries:
        elements_der = b"".join(
            b"\x0c" + bytes([len(e.encode())]) + e.encode() for e in elements
        )
        entry_body = (
            b"\x0c" + bytes([len(doc_type.encode())]) + doc_type.encode()
            + b"\x30" + bytes([len(elements_der)]) + elements_der
        )
        lines.append(f"   30 {length(len(entry_body))}")
        lines.append(f'      0C {length(len(doc_type.encode()))} "{doc_type}"')
        lines.append(f"      30 {length(len(elements_der))}")
        for element in elements:
            lines.append(f'         0C {length(len(element.encode()))} "{element}"')
    lines.append("")
    lines.append(wrap(der.hex().upper()))
    return "\n".join(lines)


def inject_log() -> int:
    """The log, the witness file, and the request that carried the entry.

    The log is the one artifact a page shows whole, so it is written from
    ``webvh.json`` rather than renamed in place: an entry's hash covers the
    keys inside it, and a key replaced by hand would leave a log nothing can
    replay.
    """
    webvh = json.loads((OUT / "webvh.json").read_text())
    dukcapil = webvh["entities"]["dukcapil"]
    ts_5_02 = TS / "publishing-and-resolving-a-did-webvh-identifier.md"
    ts_4_01 = TS / "witnessing-a-log-entry-and-serving-its-copy.md"

    replace_block(
        ts_5_02,
        "did.jsonl, served at https://dukcapil.go.id/.well-known/did.jsonl",
        "\n".join(
            json.dumps(entry, separators=(", ", ": "), ensure_ascii=False)
            for entry in dukcapil["entries"]
        ),
    )
    witness_file = json.dumps(dukcapil["witness_file"], indent=2, ensure_ascii=False)
    replace_block(
        ts_5_02,
        "did-witness.json, served at "
        "https://dukcapil.go.id/.well-known/did-witness.json",
        witness_file,
    )
    replace_block(
        ts_4_01,
        "did-witness.json, the proof DID Service returns",
        json.dumps(dukcapil["witness_file"][0], indent=2, ensure_ascii=False),
    )

    request = webvh["publisher_request"]
    body = json.dumps(request, indent=2, ensure_ascii=False)
    replace_block(
        ts_4_01,
        "POST /entries, DID Service Publisher endpoint",
        "POST /entries HTTP/1.1\n"
        "Host: did-publisher.trust.internal\n"
        "Content-Type: application/json\n"
        "\n" + body,
    )
    return 4


def patch_numbers() -> list[str]:
    """The sizes a page repeats in prose and in a table, from the artifacts.

    A rebuilt certificate is a few bytes longer or shorter than the one it
    replaces, and the page states the length in places no block covers.
    """
    x509 = json.loads((OUT / "x509.json").read_text())
    certificates = x509["certificates"]
    pairs = [
        (TS_5_04, "| DER size | 601 bytes |",
         f"| DER size | {certificates['issuer-root-ca']['der_size']} bytes |"),
        (TS_5_04, "| DER size | 685 bytes |",
         f"| DER size | {certificates['document-signer']['der_size']} bytes |"),
        (TS_5_04, "| DER size | 654 bytes |",
         f"| DER size | {certificates['vical-signer']['der_size']} bytes |"),
        (TS_5_04, "| DER size | 311 bytes |",
         f"| DER size | {x509['crl']['der_size']} bytes |"),
        (TS_5_04, "314 bytes of DER", f"{x509['csr']['der_size']} bytes of DER"),
        (TS_5_04, "The payload is 2328 bytes.",
         f"The payload is {x509['vical']['payload_size']} bytes."),
        (TS_5_04, "The whole list is 3062 bytes",
         f"The whole list is {x509['vical']['cose_sign1_size']} bytes"),
    ]
    missing = []
    for path, old, new in pairs:
        if old == new:
            continue
        text = path.read_text()
        if text.count(old) == 0 and new in text:
            continue
        if text.count(old) != 1:
            missing.append(f"{path.name}: {old!r} appears {text.count(old)} times")
            continue
        path.write_text(text.replace(old, new))
    return missing


def main() -> None:
    summary = json.loads((OUT / "summary.json").read_text())

    print(f"  webvh.json: {inject_log()} blocks")
    for name, container in FAMILIES.items():
        print(f"  {name}: {inject_family(name, container)} blocks")

    # TS-5-04, the verifier branch.
    replace_block(
        TS_5_04,
        "verifier-root-ca.pem, the Verifier Root CA certificate",
        (OUT / "verifier-root-ca.pem").read_text().strip(),
    )
    replace_block(
        TS_5_04,
        "verifier-issuing-ca.pem, the Verifier Issuing CA certificate",
        (OUT / "verifier-issuing-ca.pem").read_text().strip(),
    )
    replace_block(
        TS_5_04,
        "verifier-device.pem, the Verifier Device Certificate",
        (OUT / "verifier-device.pem").read_text().strip(),
    )
    replace_block(
        TS_5_04,
        "verifier-issuing-ca.crl, served at "
        "https://terminal-nusantara.co.id/crl/verifier-issuing-ca",
        (OUT / "verifier-issuing-ca.crl").read_text().strip(),
    )
    replace_block(
        TS_5_04,
        "The ReaderAuthRole of verifier-device.pem, as DER",
        reader_auth_role_text(
            [
                ("id.idctf.ktp.1", ["usia_di_atas_17"]),
                ("org.iso.18013.5.1.mDL", ["age_over_18"]),
                ("id.idctf.kartu-asn.1", ["nama", "instansi"]),
            ],
            bytes.fromhex(summary["verifier_device"]["reader_auth_role_hex"]),
        ),
    )

    # The values the tables and the trusted list repeat.
    pages = [TS_5_01, TS_5_04]
    replace_everywhere(pages, OLD["verifier_root_ca_ski"], summary["verifier_root_ca"]["ski"])
    replace_everywhere(
        pages, OLD["verifier_issuing_ca_ski"], summary["verifier_issuing_ca"]["ski"]
    )
    replace_everywhere(pages, OLD["verifier_device_ski"], summary["verifier_device"]["ski"])

    text = TS_5_04.read_text()
    text = text.replace(
        "| DER size | 607 bytes |", f"| DER size | {summary['verifier_root_ca']['der_size']} bytes |"
    )
    text = text.replace(
        "| DER size | 629 bytes |",
        f"| DER size | {summary['verifier_issuing_ca']['der_size']} bytes |",
    )
    text = text.replace(
        "| DER size | 714 bytes |", f"| DER size | {summary['verifier_device']['der_size']} bytes |"
    )
    text = text.replace(
        "non-critical, 89 bytes of DER",
        f"non-critical, {summary['verifier_device']['reader_auth_role_size']} bytes of DER",
    )
    # The device certificate's ReaderAuthRole and DER size, in its table.
    text = re.sub(
        r"(\| `ReaderAuthRole` \| `1\.3\.6\.1\.4\.1\.32473\.1\.1`, non-critical, )\d+( bytes of DER \|)",
        lambda m: m.group(1) + str(summary["verifier_device"]["reader_auth_role_size"]) + m.group(2),
        text,
    )
    text = re.sub(
        r"(\| CRL distribution points \| `https://terminal-nusantara\.co\.id/crl/verifier-issuing-ca` \|\n\| DER size \| )\d+( bytes \|)",
        lambda m: m.group(1) + str(summary["verifier_device"]["der_size"]) + m.group(2),
        text,
    )
    TS_5_04.write_text(text)

    # TS-5-01, the Verifier Issuing CA certificate the trusted list carries.
    text = TS_5_01.read_text()
    text = re.sub(
        r'("val": ")MIIC[^"]+(")',
        lambda m: m.group(1) + summary["verifier_issuing_ca"]["base64"] + m.group(2),
        text,
    )
    TS_5_01.write_text(text)

    # TS-5-06, the statements and the proximity request that carries one.
    titles = ["The same statement, as the verifier carries it"] * 5
    for index, (title, statement) in enumerate(zip(titles, summary["use_statements"])):
        replace_block(TS_5_06, title, statement, occurrence=index)
    replace_block(
        TS_5_06,
        "The Use Statement of a business category, decoded",
        json.dumps(
            {
                "typ": "vnd.id.idctf.use-statement+jwt",
                "alg": "ES256",
                "kid": json.loads(
                    base64.urlsafe_b64decode(
                        summary["use_statements"][0].split(".")[0] + "=="
                    )
                )["kid"],
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n.\n"
        + json.dumps(summary["use_statement_payloads"][0], indent=2, ensure_ascii=False),
    )

    replace_block(
        TS_5_06,
        "The Use Statement of a second business category, decoded",
        json.dumps(
            json.loads(base64.urlsafe_b64decode(summary["use_statements"][4].split(".")[0] + "==")),
            indent=2,
            ensure_ascii=False,
        )
        + "\n.\n"
        + json.dumps(summary["use_statement_payloads"][4], indent=2, ensure_ascii=False),
    )

    items_request = {
        "docType": "id.idctf.ktp.1",
        "nameSpaces": {"id.idctf.ktp.1": {"usia_di_atas_17": False}},
        "requestInfo": {"idUseStatement": summary["use_statements"][0].encode()},
    }
    diagnostic = (
        "{\n"
        '  "docType": "id.idctf.ktp.1",\n'
        '  "nameSpaces": {\n'
        '    "id.idctf.ktp.1": {\n'
        '      "usia_di_atas_17": false\n'
        "    }\n"
        "  },\n"
        '  "requestInfo": {\n'
        f"    \"idUseStatement\": '{summary['use_statements'][0]}'\n"
        "  }\n"
        "}"
    )
    replace_block(
        TS_5_06,
        "The ItemsRequest of a proximity age check, in CBOR diagnostic notation",
        diagnostic,
    )
    replace_block(
        TS_5_06,
        "The same ItemsRequest, as CBOR",
        wrap(cbor2.dumps(items_request).hex()),
    )

    mdl_request = {
        "docType": "org.iso.18013.5.1.mDL",
        "nameSpaces": {"org.iso.18013.5.1": {"age_over_18": False}},
        "requestInfo": {"idUseStatement": summary["use_statements"][0].encode()},
    }
    mdl_diagnostic = (
        "{\n"
        '  "docType": "org.iso.18013.5.1.mDL",\n'
        '  "nameSpaces": {\n'
        '    "org.iso.18013.5.1": {\n'
        '      "age_over_18": false\n'
        "    }\n"
        "  },\n"
        '  "requestInfo": {\n'
        f"    \"idUseStatement\": '{summary['use_statements'][0]}'\n"
        "  }\n"
        "}"
    )
    replace_block(
        TS_5_06,
        "The ItemsRequest of a proximity age check on a mobile driving license, in CBOR diagnostic notation",
        mdl_diagnostic,
    )
    replace_block(
        TS_5_06,
        "The same mobile driving license ItemsRequest, as CBOR",
        wrap(cbor2.dumps(mdl_request).hex()),
    )

    # TS-5-05, the answers.
    answer_titles = [
        "The answer to an issuing permission that is granted",
        "The answer to a request permission, evaluated at a stated time",
        "The answer to a request permission over a type another body names",
        "The answer to an issuing permission over a type another body names",
        "The answer to an issuing permission over the Kartu ASN",
        "The answer to an issuing permission over the Kartu Nikah",
        "The answer to a permission the entity does not hold",
    ]
    for title, answer in zip(answer_titles, summary["answers"]):
        replace_block(TS_5_05, title, json.dumps(answer, indent=2, ensure_ascii=False))

    # TS-5-07, the Accreditation Credentials.
    credential_titles = [
        "The credential of an accredited Identity Issuer",
        "The credential of an accredited Relying Party",
        "The credential of an accredited Wallet Provider, which holds no permission",
    ]
    for title, credential in zip(credential_titles, summary["accreditations"]):
        replace_block(TS_5_07, title, credential)
    replace_block(
        TS_5_07,
        "The claims of the Identity Issuer's credential",
        json.dumps(summary["accreditation_payloads"][0], indent=2, ensure_ascii=False),
    )

    table = renames()
    moved = rename_identifiers(table)
    for old, count in sorted(moved.items(), key=lambda item: -item[1]):
        print(f"  renamed {count:>3}x  {old[:24]}… -> {table[old][:24]}…")

    for problem in patch_numbers():
        print(f"  number not patched: {problem}")

    left = check_renamed(table)
    for line in left:
        print(f"  left behind: {line}")
    print("injected" if not left else f"injected, {len(left)} old values left")


if __name__ == "__main__":
    main()
