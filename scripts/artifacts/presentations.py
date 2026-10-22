"""Build and verify the presentations of TS-5-11, and the two signed Request
Objects of TS-5-06 that the online presentations answer.

Inputs, read at run time: ``build/artifacts/webvh.json`` (identifiers, keys),
``credentials.json`` (the issued Kartu ASN and KTP, the holder key),
``ldp.json`` (shared values only), ``summary.json`` (the Use Statements) and
the keystore. Claim values, nonce, ``aud``, times, the session transcript and
the requested claims are the ones the pages already carry; keys, identifiers,
signatures and what derives from them are new.

Signatures are RFC 6979 ES256, so a re-run writes the same bytes. A signature
already stored in ``build/artifacts/presentations.json`` is reused when it
still verifies over the same input; ``--rebuild`` signs anew.

Output ``build/artifacts/presentations.json``::

    {"blocks": {<block title>: <text of the fenced block>, ...},
     "documents": {"sd_jwt_presentation", "kb_jwt", "sd_hash", "vp_token",
                   "device_response_hex", "device_authentication_hex",
                   "device_signature_payload_hex", "session_transcript_hex",
                   "request_object": {"header", "payload", "jws"},
                   "request_object_ldp": {"header", "payload", "jws"}}}

Run as ``.venv/bin/python scripts/artifacts/presentations.py [--rebuild]``.
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
import sys
from pathlib import Path

import cbor2
from cbor2 import CBORTag
from cryptography import x509

sys.path.insert(0, str(Path(__file__).resolve().parent))

import credentials as cr  # noqa: E402
import keystore  # noqa: E402
import webvh  # noqa: E402

ROOT = webvh.REPO_ROOT
ART = ROOT / "build" / "artifacts"
OUT = ART / "presentations.json"
SUMMARY = ART / "summary.json"
LDP = ART / "ldp.json"

# ---- block titles
T_VPTOKEN = "The vp_token of an SD-JWT VC presentation"
T_PRES = "An SD-JWT VC presentation"
T_DISC = "The disclosures that traveled"
T_KBH = "Key Binding JWT header"
T_KBC = "Key Binding JWT claims"
T_DRHEX = "The DeviceResponse, as sent"
T_DRDIAG = "The DeviceResponse, in CBOR diagnostic notation"
T_ST = "The SessionTranscript of that session"
T_RO = "The Use Statement in a Request Object, online"
T_RO_LDP = "The Use Statement of the Kartu Nikah use in a Request Object, online"
T_LDP_VPTOKEN = "The vp_token of an ldp_vc presentation"

# ---- values the pages fix
KB_IAT = 1792221300
NONCE = "lDBtAJCIkEhdHMvK0Vp6rQ"
TRAVEL = ["nama", "nip", "instansi"]
# The two options of the query's claim_sets, least disclosure first: the
# restricted nip only in the second. The wallet answers the first (REQ-TS-5-11-095).
CLAIM_SETS = [["nama", "instansi"], ["nama", "nip", "instansi"]]
ANSWERED = CLAIM_SETS[0]
QUERY_ID = "kartu-asn"
RELEASED = "usia_di_atas_17"
USE_ID = "tarif-dinas-asn"
RESPONSE_URI = "https://terminal-nusantara.co.id/presentation/response"
# TS-3-01: every Request Object carries state, iat, exp and the formats the
# verifier accepts. The lifetime is the Governance Profile's; 300 seconds is an
# illustration.
STATE = "LMvHXBmP9koh5LKQbQcv6A"
LDP_STATE = "407uibewmpIt7GXwpP4eHA"
RO_IAT = KB_IAT - 60
LDP_RO_IAT = 1792221250
RO_LIFETIME = 300
VP_FORMATS = {
    "dc+sd-jwt": {"sd-jwt_alg_values": ["ES256"], "kb-jwt_alg_values": ["ES256"]},
    "ldp_vc": {
        "proof_type_values": ["DataIntegrityProof"],
        "cryptosuite_values": ["ecdsa-rdfc-2019"],
    },
}
# TS-3-01 (tracks/0362): each Request Object names a key pair drawn for it
# alone; the keystore keeps the illustration keys so the examples reproduce.
ENC_KEYS = {
    "request_object": "openid4vp-response-key-asn",
    "request_object_ldp": "openid4vp-response-key-nikah",
}
LDP_QUERY_ID = "kartu-nikah"
LDP_USE_ID = "pencatatan-ahli-waris"
# The types of the Kartu Nikah, expanded against its @context (OpenID4VP 1.0 B.1.1).
LDP_TYPES = [
    "https://www.w3.org/2018/credentials#VerifiableCredential",
    "https://catalog.trust.go.id/vocab/id.idctf.kartu-nikah#KartuNikah",
]
LDP_ATTRIBUTES = [
    "nama_suami", "nama_istri", "tanggal_akad", "nomor_akta_nikah", "kua",
    "kabupaten_kota", "provinsi",
]

# SessionTranscript elements of the proximity session. The two ephemeral keys
# live in the keystore, so the session TS-3-02 shows can be encrypted and
# decrypted again (tracks/0348, tracks/0349).
EDEVICE_KEY = "proximity-edevice-1"
EREADER_KEY = "proximity-ereader-1"
ENG_VERSION = "1.0"
ENG_RETRIEVAL = {0: False, 1: True, 11: bytes.fromhex("45efef742b2c4837a9a3b0e1d05a6917")}


def cose_key(name: str) -> dict:
    """The P-256 public key of keystore key ``name`` as a COSE_Key, x and y only."""
    numbers = keystore.load_or_create(name).public_key().public_numbers()
    return {
        1: 2,
        -1: 1,
        -2: numbers.x.to_bytes(32, "big"),
        -3: numbers.y.to_bytes(32, "big"),
    }


ENG_EPHEMERAL = cose_key(EDEVICE_KEY)
READER_KEY = cose_key(EREADER_KEY)

b64u, unb64u, compact, wrap = cr.b64u, cr.unb64u, cr.compact, cr.wrap
Embedded = cr.Embedded


# ------------------------------------------------ diagnostic notation (null)


def diag(value, indent: int = 0) -> str:
    """``credentials.diag`` plus ``null`` (the handover of a SessionTranscript)."""
    if value is None:
        return "null"
    pad = " " * indent
    if isinstance(value, dict):
        ordered = sorted(
            value.items(), key=lambda kv: (len(cbor2.dumps(kv[0])), cbor2.dumps(kv[0]))
        )
        rows = [f"{pad}  {diag(k)}: {diag(v, indent + 2)}" for k, v in ordered]
        return "{\n" + ",\n".join(rows) + f"\n{pad}}}"
    if isinstance(value, list):
        rows = [f"{pad}  {diag(v, indent + 2)}" for v in value]
        return "[\n" + ",\n".join(rows) + f"\n{pad}]"
    if isinstance(value, CBORTag):
        if isinstance(value.value, Embedded):
            return f"{value.tag}(<< {diag(value.value.value, indent)} >>)"
        return f"{value.tag}({diag(value.value, indent)})"
    return cr.diag(value, indent)


def parse_diag(text: str):
    """Parse ``diag`` output back to values; ``null`` is added to ``cr.parse_diag``."""
    marker = CBORTag(60000, 0)
    # protect the literal null so the shared parser sees a tagged integer
    masked = re.sub(r"(?<![\w\"'])null(?![\w\"'])", "60000(0)", text)
    out = cr.parse_diag(masked)

    def unmask(v):
        if isinstance(v, CBORTag) and v.tag == marker.tag:
            return None
        if isinstance(v, dict):
            return {k: unmask(x) for k, x in v.items()}
        if isinstance(v, list):
            return [unmask(x) for x in v]
        if isinstance(v, CBORTag):
            return CBORTag(v.tag, unmask(v.value))
        return v

    return unmask(out)


def enc(value) -> bytes:
    return cbor2.dumps(value, canonical=True)


def tag24(value) -> CBORTag:
    return CBORTag(24, enc(value))


# ------------------------------------------------------------------ inputs


def load_inputs() -> dict:
    web = json.loads((ART / "webvh.json").read_text())
    cred = json.loads((ART / "credentials.json").read_text())
    ldp = json.loads(LDP.read_text())
    summary = json.loads(SUMMARY.read_text())
    return {"web": web, "cred": cred, "ldp": ldp, "summary": summary}


def stored() -> dict:
    if "--rebuild" in sys.argv or not OUT.exists():
        return {}
    try:
        return json.loads(OUT.read_text()).get("documents", {})
    except ValueError:
        return {}


def sign_es256(key, data: bytes, previous_sig: bytes | None) -> bytes:
    """Reuse ``previous_sig`` when it still verifies over ``data``."""
    if previous_sig and cr.es256_check(key.public_key(), previous_sig, data):
        return previous_sig
    return cr.es256_raw(key, data)


# ---------------------------------------------------------- SD-JWT VC online


def build_sd_jwt(inp: dict, prev: dict) -> dict:
    cred, web = inp["cred"], inp["web"]
    sd = cred["sd_jwt"]
    holder = cr.holder()
    client_id = "decentralized_identifier:" + web["entities"]["terminal-nusantara"]["did"]
    by_name = {d["array"][1]: d for d in sd["disclosures"]}
    travelling = [by_name[n] for n in ANSWERED]
    body = sd["jwt"] + "~" + "".join(d["disclosure"] + "~" for d in travelling)
    sd_hash = b64u(hashlib.sha256(body.encode("ascii")).digest())
    header = {"typ": "kb+jwt", "alg": "ES256"}
    claims = {"iat": KB_IAT, "aud": client_id, "nonce": NONCE, "sd_hash": sd_hash}
    signing_input = b64u(compact(header)) + "." + b64u(compact(claims))
    old = prev.get("kb_jwt", "")
    old_sig = unb64u(old.split(".")[2]) if old.count(".") == 2 and old.startswith(signing_input + ".") else None
    sig = sign_es256(holder["key"], signing_input.encode(), old_sig)
    kb = signing_input + "." + b64u(sig)
    presentation = body + kb
    vp_token = {QUERY_ID: [presentation]}
    disc_text = "\n".join(
        f"~{d['disclosure']}\n  "
        + json.dumps(d["array"], separators=(",", ":"), ensure_ascii=False)
        for d in travelling
    )
    return {
        "client_id": client_id,
        "travelling": travelling,
        "body": body,
        "sd_hash": sd_hash,
        "header": header,
        "claims": claims,
        "kb_jwt": kb,
        "presentation": presentation,
        "vp_token": vp_token,
        "blocks": {
            T_VPTOKEN: json.dumps(vp_token, indent=2, ensure_ascii=False),
            T_PRES: wrap(presentation),
            T_DISC: disc_text,
            T_KBH: json.dumps(header, indent=2),
            T_KBC: json.dumps(claims, indent=2),
        },
    }


# ---------------------------------------------------------------- mdoc


def build_mdoc(inp: dict, prev: dict) -> dict:
    md = inp["cred"]["mdoc"]
    holder = cr.holder()
    doc_type = md["doc_type"]
    full_bytes = bytes.fromhex(md["issuer_signed_hex"])
    full = cbor2.loads(full_bytes)
    issuer_auth = full["issuerAuth"]
    item = next(i for i in md["items"] if i["identifier"] == RELEASED)
    tagged = bytes.fromhex(item["tagged_hex"])
    released_tag = cbor2.loads(tagged)  # CBORTag(24, bytes)
    released_struct = cbor2.loads(released_tag.value)

    # session transcript
    engagement = {
        0: ENG_VERSION,
        1: [1, tag24(ENG_EPHEMERAL)],
        2: [[2, 1, ENG_RETRIEVAL]],
    }
    transcript = [tag24(engagement), tag24(READER_KEY), None]
    transcript_bytes = enc(transcript)

    # DeviceAuthentication and the detached payload
    device_ns = tag24({})
    device_auth = ["DeviceAuthentication", transcript, doc_type, device_ns]
    device_auth_bytes = enc(device_auth)
    payload = enc(CBORTag(24, device_auth_bytes))
    protected = enc({1: -7})
    sig_structure = enc(["Signature1", protected, b"", payload])
    old = prev.get("device_signature_hex")
    sig = sign_es256(holder["key"], sig_structure, bytes.fromhex(old) if old else None)

    issuer_signed = {
        "issuerAuth": issuer_auth,
        "nameSpaces": {doc_type: [released_tag]},
    }
    response = {
        "version": "1.0",
        "documents": [
            {
                "docType": doc_type,
                "issuerSigned": issuer_signed,
                "deviceSigned": {
                    "nameSpaces": device_ns,
                    "deviceAuth": {"deviceSignature": [protected, {}, None, sig]},
                },
            }
        ],
        "status": 0,
    }
    response_bytes = enc(response)

    # the diagnostic tree: same data, items and embedded structures shown decoded
    d_issuer_auth = [issuer_auth[0], issuer_auth[1], issuer_auth[2], issuer_auth[3]]
    diag_tree = {
        "version": "1.0",
        "documents": [
            {
                "docType": doc_type,
                "issuerSigned": {
                    "issuerAuth": d_issuer_auth,
                    "nameSpaces": {doc_type: [CBORTag(24, Embedded(released_struct))]},
                },
                "deviceSigned": {
                    "nameSpaces": CBORTag(24, Embedded({})),
                    "deviceAuth": {"deviceSignature": [protected, {}, None, sig]},
                },
            }
        ],
        "status": 0,
    }
    transcript_diag = [
        CBORTag(24, Embedded(engagement_diag(engagement))),
        CBORTag(24, Embedded(READER_KEY)),
        None,
    ]
    return {
        "doc_type": doc_type,
        "full": full,
        "full_bytes": full_bytes,
        "issuer_auth": issuer_auth,
        "released_tag": released_tag,
        "protected": protected,
        "sig": sig,
        "sig_structure": sig_structure,
        "payload": payload,
        "device_auth_bytes": device_auth_bytes,
        "transcript": transcript,
        "transcript_bytes": transcript_bytes,
        "response": response,
        "response_bytes": response_bytes,
        "diag_tree": diag_tree,
        "blocks": {
            T_DRHEX: wrap(response_bytes.hex()),
            T_DRDIAG: diag(diag_tree),
            T_ST: diag(transcript_diag),
        },
    }


def engagement_diag(engagement: dict) -> dict:
    out = dict(engagement)
    out[1] = [1, CBORTag(24, Embedded(ENG_EPHEMERAL))]
    return out


# --------------------------------------------------------- Request Object


def request_query_text(query: dict) -> str:
    """One credential query of ``dcql_query``, laid out as the pages show it."""
    meta = query["meta"]
    if "vct_values" in meta:
        meta_text = f'        "meta": {{ "vct_values": {json.dumps(meta["vct_values"])} }},'
    else:
        types = ",\n".join(f"              {json.dumps(t)}" for t in meta["type_values"][0])
        meta_text = (
            '        "meta": {\n'
            '          "type_values": [\n'
            "            [\n"
            f"{types}\n"
            "            ]\n"
            "          ]\n"
            "        },"
        )
    claims = ",\n".join(
        "          { "
        + (f'"id": {json.dumps(c["id"])}, ' if "id" in c else "")
        + "\"path\": [" + ", ".join(json.dumps(n) for n in c["path"]) + "] }"
        for c in query["claims"]
    )
    claim_sets = ""
    if "claim_sets" in query:
        options = ",\n".join(
            "          [" + ", ".join(json.dumps(i) for i in option) + "]"
            for option in query["claim_sets"]
        )
        claim_sets = ',\n        "claim_sets": [\n' f"{options}\n" "        ]"
    return (
        "      {\n"
        f'        "id": {json.dumps(query["id"])},\n'
        f'        "format": {json.dumps(query["format"])},\n'
        f"{meta_text}\n"
        '        "claims": [\n'
        f"{claims}\n"
        f"        ]{claim_sets}\n"
        "      }"
    )


def build_request_object(
    inp: dict, prev: dict, *, use_id: str, nonce: str, state: str, iat: int, query: dict,
    title: str, stored_as: str
) -> dict:
    """A signed Request Object carrying the Use Statement of ``use_id``."""
    web, summary = inp["web"], inp["summary"]
    terminal = web["entities"]["terminal-nusantara"]
    ro_key = terminal["keys"]["request-object-1"]
    key = keystore.load_or_create(ro_key["keystore"])
    enc_key = keystore.load_or_create(ENC_KEYS[stored_as])
    x, y = cr.xy(enc_key.public_key())
    jwk = {"kty": "EC", "crv": "P-256", "x": b64u(x), "y": b64u(y)}
    thumb = b64u(
        hashlib.sha256(
            json.dumps({k: jwk[k] for k in ("crv", "kty", "x", "y")}, separators=(",", ":")).encode()
        ).digest()
    )
    enc_jwk = {**jwk, "use": "enc", "alg": "ECDH-ES", "kid": thumb}

    statement = None
    for token in summary["use_statements"]:
        if json.loads(unb64u(token.split(".")[1]))["use_id"] == use_id:
            statement = token
    if statement is None:
        raise SystemExit(f"no Use Statement with use_id {use_id} in summary.json")

    client_id = "decentralized_identifier:" + terminal["did"]
    payload = {
        "client_id": client_id,
        "aud": "https://self-issued.me/v2",
        "response_type": "vp_token",
        "response_mode": "direct_post.jwt",
        "response_uri": RESPONSE_URI,
        "client_metadata": {"jwks": {"keys": [enc_jwk]}, "vp_formats_supported": VP_FORMATS},
        "nonce": nonce,
        "state": state,
        "dcql_query": {"credentials": [query]},
        "verifier_info": [{"format": "vnd.id.idctf.use-statement+jwt", "data": statement}],
        "iat": iat,
        "exp": iat + RO_LIFETIME,
    }
    header = {"typ": "oauth-authz-req+jwt", "alg": "ES256", "kid": ro_key["kid"]}
    signing_input = b64u(compact(header)) + "." + b64u(compact(payload))
    old = prev.get(stored_as, {}).get("jws", "")
    old_sig = unb64u(old.split(".")[2]) if old.startswith(signing_input + ".") else None
    sig = sign_es256(key, signing_input.encode(), old_sig)
    jws = signing_input + "." + b64u(sig)

    block = f"""{{
  "client_id": {json.dumps(client_id)},
  "aud": "https://self-issued.me/v2",
  "response_type": "vp_token",
  "response_mode": "direct_post.jwt",
  "response_uri": {json.dumps(RESPONSE_URI)},
  "client_metadata": {{
    "jwks": {{
      "keys": [
        {{
          "kty": "EC",
          "crv": "P-256",
          "x": {json.dumps(enc_jwk["x"])},
          "y": {json.dumps(enc_jwk["y"])},
          "use": "enc",
          "alg": "ECDH-ES",
          "kid": {json.dumps(thumb)}
        }}
      ]
    }},
    "vp_formats_supported": {{
      "dc+sd-jwt": {{
        "sd-jwt_alg_values": ["ES256"],
        "kb-jwt_alg_values": ["ES256"]
      }},
      "ldp_vc": {{
        "proof_type_values": ["DataIntegrityProof"],
        "cryptosuite_values": ["ecdsa-rdfc-2019"]
      }}
    }}
  }},
  "nonce": {json.dumps(nonce)},
  "state": {json.dumps(state)},
  "dcql_query": {{
    "credentials": [
{request_query_text(query)}
    ]
  }},
  "verifier_info": [
    {{
      "format": "vnd.id.idctf.use-statement+jwt",
      "data": {json.dumps(statement)}
    }}
  ],
  "iat": {iat},
  "exp": {iat + RO_LIFETIME}
}}"""
    return {
        "header": header,
        "payload": payload,
        "jws": jws,
        "statement": statement,
        "enc_jwk": enc_jwk,
        "blocks": {title: block},
    }


def build_request_objects(inp: dict, prev: dict) -> tuple[dict, dict]:
    """The Kartu ASN request the SD-JWT VC answers, and the Kartu Nikah one the
    ``ldp_vc`` presentation answers, whose ``nonce`` is that presentation's
    ``challenge`` (fixed in ``ldp.py``)."""
    asn = build_request_object(
        inp, prev, use_id=USE_ID, nonce=NONCE, state=STATE, iat=RO_IAT, title=T_RO,
        stored_as="request_object",
        query={
            "id": QUERY_ID,
            "format": "dc+sd-jwt",
            "meta": {"vct_values": ["id.idctf.kartu-asn.1"]},
            "claims": [{"id": n, "path": [n]} for n in TRAVEL],
            "claim_sets": CLAIM_SETS,
        },
    )
    vp = json.loads(inp["ldp"]["blocks"][T_LDP_VPTOKEN])[LDP_QUERY_ID][0]
    nikah = build_request_object(
        inp, prev, use_id=LDP_USE_ID, nonce=vp["proof"]["challenge"], state=LDP_STATE,
        iat=LDP_RO_IAT, title=T_RO_LDP,
        stored_as="request_object_ldp",
        query={
            "id": LDP_QUERY_ID,
            "format": "ldp_vc",
            "meta": {"type_values": [LDP_TYPES]},
            "claims": [{"path": ["credentialSubject", n]} for n in LDP_ATTRIBUTES],
        },
    )
    return asn, nikah


# ------------------------------------------------------------------ build


def build() -> dict:
    inp = load_inputs()
    prev = stored()
    sd = build_sd_jwt(inp, prev)
    md = build_mdoc(inp, prev)
    ro, ro_ldp = build_request_objects(inp, prev)
    return {"inp": inp, "sd": sd, "md": md, "ro": ro, "ro_ldp": ro_ldp}


def to_json(b: dict) -> dict:
    sd, md, ro, ro_ldp = b["sd"], b["md"], b["ro"], b["ro_ldp"]
    return {
        "blocks": {**sd["blocks"], **md["blocks"], **ro["blocks"], **ro_ldp["blocks"]},
        "documents": {
            "sd_jwt_presentation": sd["presentation"],
            "sd_jwt_body": sd["body"],
            "disclosures": [d["disclosure"] for d in sd["travelling"]],
            "kb_jwt": sd["kb_jwt"],
            "kb_header": sd["header"],
            "kb_claims": sd["claims"],
            "sd_hash": sd["sd_hash"],
            "vp_token": sd["vp_token"],
            "device_response_hex": md["response_bytes"].hex(),
            "device_signature_hex": md["sig"].hex(),
            "device_authentication_hex": md["device_auth_bytes"].hex(),
            "device_signature_payload_hex": md["payload"].hex(),
            "session_transcript_hex": md["transcript_bytes"].hex(),
            "request_object": {
                "header": ro["header"],
                "payload": ro["payload"],
                "jws": ro["jws"],
            },
            "request_object_ldp": {
                "header": ro_ldp["header"],
                "payload": ro_ldp["payload"],
                "jws": ro_ldp["jws"],
            },
        },
    }


# ----------------------------------------------------------------- verify


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

    inp, sd, md, ro = b["inp"], b["sd"], b["md"], b["ro"]
    web, cred = inp["web"], inp["cred"]
    holder = cr.holder()
    pub = holder["key"].public_key()
    issued = cred["sd_jwt"]

    # --- SD-JWT VC presentation
    h_b, c_b, s_b = sd["kb_jwt"].split(".")
    report(
        cr.es256_check(pub, unb64u(s_b), f"{h_b}.{c_b}".encode())
        and json.loads(unb64u(h_b)) == {"typ": "kb+jwt", "alg": "ES256"},
        "Key Binding JWT verifies under the holder key (header typ kb+jwt, alg only)",
    )
    cnf = issued["payload"]["cnf"]["jwk"]
    report(
        cnf == holder["jwk"] and (cnf["x"], cnf["y"]) == (b64u(holder["x"]), b64u(holder["y"])),
        "the credential's cnf names the holder key the Key Binding JWT verifies under",
    )
    prefix, _, kb = sd["presentation"].rpartition("~")
    recomputed = b64u(hashlib.sha256((prefix + "~").encode("ascii")).digest())
    report(
        kb == sd["kb_jwt"] and json.loads(unb64u(c_b))["sd_hash"] == recomputed,
        f"sd_hash recomputes over the presentation up to the KB-JWT ({recomputed})",
    )
    report(
        list(json.loads(unb64u(c_b))) == ["iat", "aud", "nonce", "sd_hash"]
        and json.loads(unb64u(c_b))["nonce"] == NONCE
        and json.loads(unb64u(c_b))["aud"] == ro["payload"]["client_id"]
        and json.loads(unb64u(c_b))["aud"].endswith(web["entities"]["terminal-nusantara"]["did"]),
        "Key Binding JWT nonce and aud are the Request Object's nonce and client_id",
    )
    parts = sd["presentation"].split("~")
    report(
        parts[0] == issued["jwt"] and len(parts) == len(ANSWERED) + 2,
        "presentation is the issued JWT, the travelling disclosures, then the KB-JWT",
    )
    issued_set = {d["disclosure"] for d in issued["disclosures"]}
    sd_claim = set(issued["payload"]["_sd"])
    ok = True
    for d in parts[1:-1]:
        digest = b64u(hashlib.sha256(d.encode("ascii")).digest())
        ok = ok and d in issued_set and digest in sd_claim
    report(
        ok and [json.loads(unb64u(d))[1] for d in parts[1:-1]] == ANSWERED,
        f"{len(ANSWERED)} travelling disclosures are issued ones and their digests sit in the issued _sd",
    )
    ent = web["entities"]["bkn"]
    ipub = webvh.public_key_from_multikey(ent["keys"]["issuance-jose-1"]["multikey"])
    ih, ic, isg = issued["jwt"].split(".")
    report(
        cr.es256_check(ipub, unb64u(isg), f"{ih}.{ic}".encode()),
        "issued SD-JWT VC verifies under the BKN issuance-jose-1 key",
    )
    report(
        sd["blocks"][T_VPTOKEN] and json.loads(sd["blocks"][T_VPTOKEN]) == {QUERY_ID: [sd["presentation"]]}
        and sd["blocks"][T_PRES].replace("\n", "") == sd["presentation"]
        and json.loads(sd["blocks"][T_KBH]) == json.loads(unb64u(h_b))
        and json.loads(sd["blocks"][T_KBC]) == json.loads(unb64u(c_b)),
        "vp_token, presentation, header and claims blocks decode to the signed token",
    )

    # --- mdoc DeviceResponse
    # DeviceAuthentication rebuilt from the transcript, docType and namespaces
    rebuilt_transcript = cbor2.loads(md["transcript_bytes"])
    da = ["DeviceAuthentication", rebuilt_transcript, md["doc_type"], tag24({})]
    payload = enc(CBORTag(24, enc(da)))
    sig_structure = enc(["Signature1", md["protected"], b"", payload])
    report(
        payload == md["payload"] and cr.es256_check(pub, md["sig"], sig_structure),
        "deviceSignature verifies under the holder key over DeviceAuthentication "
        "(SessionTranscript, docType, device namespaces)",
    )
    mso = cbor2.loads(cbor2.loads(md["issuer_auth"][2]).value)
    dk = mso["deviceKeyInfo"]["deviceKey"]
    report(
        (dk[-2], dk[-3]) == (holder["x"], holder["y"]),
        "the Mobile Security Object's deviceKey is the key deviceSignature verifies under",
    )
    resp = cbor2.loads(md["response_bytes"])
    doc = resp["documents"][0]
    got_auth = doc["issuerSigned"]["issuerAuth"]
    orig = cbor2.loads(bytes.fromhex(cred["mdoc"]["issuer_signed_hex"]))
    report(
        enc(got_auth) == enc(orig["issuerAuth"])
        and got_auth[0] == orig["issuerAuth"][0]
        and got_auth[2] == orig["issuerAuth"][2]
        and got_auth[3] == orig["issuerAuth"][3],
        "issuerAuth in the DeviceResponse is byte-identical to the one in credentials.json",
    )
    ns = doc["issuerSigned"]["nameSpaces"][md["doc_type"]]
    orig_items = [enc(t) for t in orig["nameSpaces"][md["doc_type"]]]
    restored = {"issuerAuth": orig["issuerAuth"],
                "nameSpaces": {md["doc_type"]: orig["nameSpaces"][md["doc_type"]]}}
    report(
        len(ns) == 1 and enc(ns[0]) in orig_items
        and enc(restored) == bytes.fromhex(cred["mdoc"]["issuer_signed_hex"]),
        "the one disclosed item is byte-identical to the issued item; the issued IssuerSigned "
        "re-encodes byte for byte",
    )
    digest = hashlib.sha256(enc(ns[0])).digest()
    report(
        mso["valueDigests"][md["doc_type"]][cbor2.loads(ns[0].value)["digestID"]] == digest,
        "the disclosed item's digest is the one in the Mobile Security Object",
    )
    cert = x509.load_der_x509_certificate(orig["issuerAuth"][1][33])
    sig_s = enc(["Signature1", orig["issuerAuth"][0], b"", orig["issuerAuth"][2]])
    report(
        cr.es256_check(cert.public_key(), orig["issuerAuth"][3], sig_s),
        "issuerAuth verifies under the Document Signer Certificate in x5chain",
    )
    report(
        doc["deviceSigned"]["nameSpaces"] == tag24({})
        and doc["deviceSigned"]["deviceAuth"]["deviceSignature"][1] == {}
        and "deviceMac" not in doc["deviceSigned"]["deviceAuth"],
        "deviceSigned.nameSpaces is an empty map in tag 24; no deviceMac; empty unprotected header",
    )
    report(
        md["blocks"][T_DRHEX].replace("\n", "") == md["response_bytes"].hex()
        and enc(parse_diag(md["blocks"][T_DRDIAG])) == md["response_bytes"],
        "the diagnostic notation of the DeviceResponse parses back to the same bytes as the hex",
    )
    report(
        enc(parse_diag(md["blocks"][T_ST])) == md["transcript_bytes"],
        "the diagnostic notation of the SessionTranscript parses back to the same bytes",
    )

    # --- Request Object and its Use Statement
    jh, jc, js = ro["jws"].split(".")
    rk = web["entities"]["terminal-nusantara"]["keys"]["request-object-1"]
    rpub = webvh.public_key_from_multikey(rk["multikey"])
    report(
        cr.es256_check(rpub, unb64u(js), f"{jh}.{jc}".encode())
        and json.loads(unb64u(jh))["kid"] == rk["kid"],
        f"Request Object verifies under {rk['kid']}",
    )
    report(
        json.loads(ro["blocks"][T_RO]) == json.loads(unb64u(jc)) == ro["payload"],
        "the Request Object block decodes to the signed payload",
    )
    data = ro["payload"]["verifier_info"][0]["data"]
    ta = web["entities"]["trust-authority"]["keys"]["use-statement-1"]
    upub = keystore.load_or_create(ta["keystore"]).public_key()
    uh, uc, us = data.split(".")
    use = json.loads(unb64u(uc))
    report(
        data in inp["summary"]["use_statements"]
        and inp["summary"]["use_statements"].index(data) == 2 and use["use_id"] == USE_ID,
        f"embedded Use Statement is summary.json's, byte for byte (use_id {use['use_id']})",
    )
    report(
        cr.es256_check(upub, unb64u(us), f"{uh}.{uc}".encode()),
        f"embedded Use Statement verifies under the keystore key {ta['keystore']}",
    )
    asn_query = ro["payload"]["dcql_query"]["credentials"][0]
    report(
        use["claims"] == [f"id.idctf.kartu-asn.1#{n}" for n in TRAVEL]
        and [c["path"][0] for c in asn_query["claims"]] == TRAVEL,
        "the statement names the three attributes the query's claims point at",
    )
    ids = [c["id"] for c in asn_query["claims"]]
    report(
        len(set(ids)) == len(ids)
        and asn_query["claim_sets"] == CLAIM_SETS
        and all(set(option) <= set(ids) for option in asn_query["claim_sets"])
        and ANSWERED == asn_query["claim_sets"][0],
        "every claim_sets option names claims of the query by id, and the presentation answers the first",
    )
    expected_sub = web["entities"]["terminal-nusantara"]["did"]
    report(
        use["sub"] == expected_sub,
        f"statement sub is the request's DID ({expected_sub}); summary.json holds {use['sub']} "
        "and needs rebuilding by build.py",
        warn=True,
    )
    report(
        use["iss"] == ta["kid"].split("#")[0]
        and json.loads(unb64u(uh))["kid"] == ta["kid"],
        "statement iss and kid are Trust Authority's current DID",
        warn=True,
    )

    # --- the Kartu Nikah Request Object the ldp_vc presentation answers
    ro_ldp = b["ro_ldp"]
    jh, jc, js = ro_ldp["jws"].split(".")
    report(
        cr.es256_check(rpub, unb64u(js), f"{jh}.{jc}".encode())
        and json.loads(unb64u(jh))["kid"] == rk["kid"]
        and json.loads(ro_ldp["blocks"][T_RO_LDP]) == json.loads(unb64u(jc)) == ro_ldp["payload"],
        f"Kartu Nikah Request Object verifies under {rk['kid']} and its block decodes to the payload",
    )
    nikah = json.loads(unb64u(ro_ldp["payload"]["verifier_info"][0]["data"].split(".")[1]))
    query = ro_ldp["payload"]["dcql_query"]["credentials"][0]
    report(
        nikah["use_id"] == LDP_USE_ID
        and nikah["claims"] == [f"id.idctf.kartu-nikah.1#{n}" for n in LDP_ATTRIBUTES]
        and [c["path"] for c in query["claims"]] == [["credentialSubject", n] for n in LDP_ATTRIBUTES],
        "the Kartu Nikah statement and query name the same attributes",
    )
    vp = json.loads(inp["ldp"]["blocks"][T_LDP_VPTOKEN])[LDP_QUERY_ID][0]
    report(
        vp["proof"]["challenge"] == ro_ldp["payload"]["nonce"]
        and vp["proof"]["domain"] == ro_ldp["payload"]["client_id"]
        and vp["type"] == ["VerifiablePresentation"]
        and vp["verifiableCredential"][0]["type"] == ["VerifiableCredential", "KartuNikah"],
        "ldp_vc presentation challenge and domain are the Kartu Nikah request's nonce and client_id",
    )
    return failures


def main() -> int:
    b = build()
    OUT.write_text(json.dumps(to_json(b), indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    failures = verify(b)
    print("all checks passed" if not failures else f"{failures} check(s) FAILED")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
