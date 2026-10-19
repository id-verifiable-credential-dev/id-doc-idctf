"""The Governance Profile of TS-02, signed under a kept key (tracks/0368).

Builds the Profile payload, its JWS protected header and the compact JWS, and
writes them to ``build/artifacts/governance.json`` keyed by block title, for
``inject.py`` to place in TS-02.

Every value is dummy data, but every value another example already shows is
taken from that example: the addresses the TS pages use, the credential types
the catalog registers, the key storage root certificate the entity endpoint
example chains to, and the lifetimes the example tokens carry. Three
signer keys come from the keystore: ``ta-governance-profile-1`` is withdrawn,
``ta-governance-profile-2`` signs, ``ta-governance-profile-3`` is announced and
has signed nothing.

ES256 signing is randomized. A re-run reuses the stored signature while it
still verifies over the same bytes; ``--rebuild`` signs anew.

Run as a script it builds, then verifies its own output, one line per check;
the exit status is 0 only when every check passes. Run it after
``entities.py``, ``trqp.py`` and ``trustlist.py``.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import keystore  # noqa: E402
import webvh  # noqa: E402
from trustlist import es256_sign, es256_verify, wrap  # noqa: E402

REPO_ROOT = webvh.REPO_ROOT
ART = REPO_ROOT / "build" / "artifacts"
OUT_JSON = ART / "governance.json"

T_PAYLOAD = "governance-profile.json, the Profile payload"
T_HEADER = "governance-profile.json, the JWS protected header"
T_JWS = "governance-profile.json, the JWS compact serialization"

SIGNERS = ("ta-governance-profile-1", "ta-governance-profile-2", "ta-governance-profile-3")
SIGNING = "ta-governance-profile-2"

CEILINGS = {
    "id.idctf.ktp.1": "P90D",
    "org.iso.18013.5.1.mDL.1": "P90D",
    "id.idctf.kartu-indonesia-sehat.1": "P1Y",
    "id.idctf.kartu-asn.1": "P1Y",
    "id.idctf.kartu-nikah.1": "P1Y",
}

# RFC 3339 Appendix A without the week form, as TS-02 admits; the ABNF has no fractions.
DURATION = re.compile(
    r"^P(?!$)(\d+Y)?(\d+M)?(\d+D)?(T(?=\d)(\d+H)?(\d+M)?(\d+S)?)?$"
)


def load(name: str) -> dict:
    return json.loads((ART / name).read_text())


def signer_keys() -> dict:
    out = {}
    for name in SIGNERS:
        key = keystore.load_or_create(name)
        out[name] = {"key": key, "did_key": webvh.did_key(webvh.multikey(key.public_key()))}
    return out


def payload(signers: dict) -> dict:
    entities = load("entities.json")
    trust_list = load("trustlist.json")["_structured"]["payload"]
    catalog = load("trqp.json")["catalog_payload"]

    trusted_list = trust_list["LoTE"]["ListAndSchemeInformation"]["DistributionPoints"]
    types = [r["id"] for r in catalog["rulebooks"]]

    algorithms_jose = ["ES256"]
    return {
        "profile_version": 1,
        "sequence_number": 3,
        "issued_at": "2026-10-01T00:00:00Z",
        "next_update": "2026-12-30T00:00:00Z",
        "signers": [
            {"key": signers["ta-governance-profile-3"]["did_key"], "status": "granted",
             "since": "2026-10-01T00:00:00Z"},
            {"key": signers["ta-governance-profile-2"]["did_key"], "status": "granted",
             "since": "2026-04-01T00:00:00Z"},
            {"key": signers["ta-governance-profile-1"]["did_key"], "status": "withdrawn",
             "since": "2026-07-01T00:00:00Z"},
        ],
        "specifications": [
            {"id": sid, "versions": ["1.0"]}
            for sid in ("TS-00", "TS-01", "TS-02", "TS-1-01", "TS-2-01", "TS-3-01", "TS-3-02",
                        "TS-4-01", "TS-4-02", "TS-4-03")
        ] + [
            {"id": "TS-5-01", "versions": ["1.0", "2.0"],
             "transition_ends": "2027-03-31T00:00:00Z"},
        ] + [
            {"id": sid, "versions": ["1.0"]}
            for sid in ("TS-5-02", "TS-5-03", "TS-5-04", "TS-5-05", "TS-5-06", "TS-5-07",
                        "TS-5-08", "TS-5-09", "TS-5-10", "TS-5-11")
        ],
        "standards": {
            "DID-Key": "0.9",
            "DID-WebVH": "1.0",
            "ETSI.TS.119602": "V1.1.1",
            "I-D.ietf-oauth-sd-jwt-vc": "13",
            "I-D.ietf-oauth-status-list": "14",
            "ISO.18013-5": "2021",
            "OpenID4VCI": "1.0",
            "OpenID4VP": "1.0",
            "TRQP": "2.0",
        },
        "addresses": {
            "trust_registry": "https://query.trust.go.id",
            "catalog": "https://catalog.trust.go.id",
            "trusted_list": trusted_list,
            "status_list_host": "https://registry.trust.go.id",
            "did_resolver": "https://did.trust.go.id",
            "entity_endpoint": entities["endpoint"],
            "portal": "https://portal.trust.go.id",
        },
        "algorithms": {
            "trusted_list": algorithms_jose,
            "recognition_answer": algorithms_jose,
            "catalog": algorithms_jose,
            "authority_statement": algorithms_jose,
            "use_statement": algorithms_jose,
            "accreditation_credential": algorithms_jose,
            "key_attestation": algorithms_jose,
            "status_list": algorithms_jose,
            "issuance": {
                "dc+sd-jwt": algorithms_jose,
                "mso_mdoc": [-7],
                "ldp_vc": ["ecdsa-rdfc-2019"],
            },
            "credential_key": algorithms_jose,
            "dpop": algorithms_jose,
            "request_object": algorithms_jose,
        },
        "lifetimes": {
            "authority_statement": "PT12H",
            "recognition_answer": "PT12H",
            "catalog": "P1D",
            "status_list_ttl": {
                "credential": "PT12H",
                "use_statement": "PT12H",
                "accreditation": "PT12H",
            },
            "credential_suspension": "P30D",
            "use_statement": "P1Y",
            "trusted_list_horizon": "P7D",
            "verifier_device_certificate": "P730D",
            "verifier_issuing_ca": "P5Y",
            "accreditation_period": "P2Y",
            "entity_endpoint_nonce": "PT5M",
            "registration_code": "P14D",
            "enrollment_challenge": "PT5M",
            "pre_authorized_code": "PT10M",
            "par_request_uri": "PT1M",
            "authorization_code": "PT1M",
            "access_token": "PT5M",
            "refresh_token_inactivity": "P90D",
            "dpop_nonce": "PT5M",
            "c_nonce": "PT5M",
            "deferred_request": "P1D",
            "request_object": "PT5M",
            "relayed_response": "PT10M",
            "relay_record": "P90D",
            "consent_receipt": "P1Y",
            "presentation_history": "P1Y",
            "dispute_period": "P5Y",
            "registration_suspension": "P90D",
        },
        "roots": {
            "issuer_root_ca": {"longest_certificate": "P10Y", "signing_period": "P3Y",
                               "lead_time": "P2Y"},
            "verifier_root_ca": {"longest_certificate": "P5Y", "signing_period": "P8Y",
                                 "lead_time": "P2Y"},
        },
        "credential_types": {
            t: {"validity_ceiling": CEILINGS[t]} for t in types
        },
        "tolerances": {
            "recognition_answer": "P1D",
            "catalog": "P7D",
            "authority_statement": "P1D",
            "did_webvh_log": "P7D",
            "status_list": "P3D",
            "use_statement_status_list": "P3D",
            "crl": "P7D",
            "vical": "P7D",
        },
        "intervals": {
            "trust_cache_sync": {"every": "PT6H", "jitter": "PT30M"},
            "status_list_republication": "PT12H",
            "status_list_change": "PT1H",
            "accreditation_status_change": "PT1H",
            "crl_publication": "P1D",
            "vical_publication": "P1D",
            "dsc_expiry_warning": "P90D",
            "credential_renewal_lead": "P30D",
            "accreditation_renewal_lead": "P90D",
            "merchant_withdrawal": "P1D",
            "registration_change_notice": "P7D",
            "loss_report_action": "PT24H",
            "license_change_report": "P14D",
            "correction_period": "P30D",
            "incident_report": "PT24H",
            "post_mortem": "P30D",
            "amendment_notice": "P90D",
        },
        "rotation": {
            "issuance-jose": {"interval": "P1Y", "overlap": "P60D"},
            "issuance-cose": {"interval": "P1Y", "overlap": "P60D"},
            "request-object": {"interval": "P1Y", "overlap": "P60D"},
            "verifier-issuing-ca": {"interval": "P3Y", "overlap": "P90D"},
            "key-attestation": {"interval": "P1Y", "overlap": "P60D"},
            "update": {"interval": "P2Y"},
            "retired_private_key": "destroy",
            "trust_authority": {
                **{name: {"interval": "P2Y", "lead_time": "P90D"}
                   for name in ("trusted-list", "vical", "governance-profile")},
                **{name: {"interval": "P2Y"}
                   for name in ("accreditation-credential", "accreditation-status-list",
                                "use-statement", "use-statement-status-list",
                                "authority-statement", "recognition-statement", "catalog",
                                "update", "witness")},
            },
        },
        "limits": {
            "query_rate": {"requests": 600, "per": "PT1M"},
            "entity_endpoint_rate": {"requests": 60, "per": "PT1M"},
            "portal_rate": {"requests": 120, "per": "PT1M"},
            "portal_failed_sign_ins": 10,
            "use_statement_cut_off": "2026-10-01T00:00:00Z",
            "key_attestation_clock_skew": "PT1M",
            "transaction_code_attempts": 3,
            "did_service_availability": {"share": 0.995, "window": "P90D"},
            "did_service_recovery": "PT4H",
            "integrity_verdict_window": "PT5M",
        },
        "lists": {
            "authorization_actions": ["issue", "request"],
            "recognition_actions": ["issue"],
            "key_storage_roots": {"hsm": [entities["maker_root"]], "cloudkms": []},
            "portal_second_factors": ["webauthn", "totp"],
            "recognized_evaluation_schemes": ["eucc", "sogis", "id-bssn"],
            "android_device_recognition_verdict": [
                {"from_version": 13, "requires": "MEETS_STRONG_INTEGRITY"},
                {"from_version": 10, "requires": "MEETS_DEVICE_INTEGRITY"},
            ],
            "attestation_root_refusal": [
                {"root": "CEDB1CB6DC896AE5EC797348BCE9286753C2B38EE71CE0FBE34A9A1248800DFC",
                 "from": "2036-01-01T00:00:00Z"},
            ],
        },
        "mappings": {
            "min_assurance": {
                "high": {"key_storage": ["iso_18045_high"],
                         "user_authentication": ["iso_18045_moderate", "iso_18045_high"],
                         "proof_types": ["attestation"]},
                "substantial": {"key_storage": ["iso_18045_moderate", "iso_18045_high"],
                                "user_authentication": ["iso_18045_moderate", "iso_18045_high"],
                                "proof_types": ["attestation", "jwt"]},
                "low": {"key_storage": ["iso_18045_enhanced-basic", "iso_18045_moderate",
                                        "iso_18045_high"],
                        "user_authentication": ["iso_18045_enhanced-basic", "iso_18045_moderate",
                                                "iso_18045_high"],
                        "proof_types": ["attestation", "jwt"]},
            },
            "issuer_assurance": {"software": "low", "cloudkms": "substantial", "hsm": "high"},
        },
        "key_storage": {"verifier-issuing-ca": ["cloudkms", "hsm"]},
        "permissions": {"dsc_per_group_of_types": False},
    }


def build(rebuild: bool = False) -> dict:
    signers = signer_keys()
    body = payload(signers)
    payload_text = json.dumps(body, indent=2, ensure_ascii=False)
    header = {"alg": "ES256", "kid": signers[SIGNING]["did_key"]}
    header_text = json.dumps(header, separators=(",", ":"))
    signing_input = webvh._b64u(header_text.encode()) + "." + webvh._b64u(payload_text.encode())
    key = signers[SIGNING]["key"]

    token, reused = None, False
    if OUT_JSON.exists() and not rebuild:
        prev = json.loads(OUT_JSON.read_text()).get("_structured", {}).get("jws", "")
        if prev.startswith(signing_input + "."):
            if es256_verify(key.public_key(), webvh._unb64u(prev[len(signing_input) + 1:]),
                            signing_input.encode()):
                token, reused = prev, True
    if token is None:
        token = signing_input + "." + webvh._b64u(es256_sign(key, signing_input.encode()))

    return {
        "blocks": {T_PAYLOAD: payload_text, T_HEADER: header_text, T_JWS: wrap(token)},
        "_structured": {
            "payload": body,
            "header": header,
            "jws": token,
            "signature_reused": reused,
            "signers": {n: s["did_key"] for n, s in signers.items()},
        },
    }


def durations(obj, path=""):
    """Every string a duration member holds, with its path."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from durations(v, f"{path}/{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from durations(v, f"{path}[{i}]")
    elif isinstance(obj, str) and obj.startswith("P"):
        yield path, obj


def main() -> int:
    out = build("--rebuild" in sys.argv[1:])
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    st = out["_structured"]
    results: list[bool] = []

    def check(label: str, ok: bool) -> None:
        results.append(bool(ok))
        print(f"{'OK  ' if ok else 'FAIL'} {label}")

    print("signature " + ("reused, still verifies" if st["signature_reused"] else "signed anew"))
    head_b64, body_b64, sig_b64 = st["jws"].split(".")
    header = json.loads(webvh._unb64u(head_b64))
    body = json.loads(webvh._unb64u(body_b64))
    sig = webvh._unb64u(sig_b64)
    signing_input = f"{head_b64}.{body_b64}".encode()

    pub = webvh.public_key_from_multikey(header["kid"].removeprefix("did:key:"))
    check("JWS verifies under the key its kid decodes to", es256_verify(pub, sig, signing_input))
    check("kid is ta-governance-profile-2 and the header is exactly alg ES256 and kid",
          header == {"alg": "ES256", "kid": st["signers"][SIGNING]}
          and list(header) == ["alg", "kid"])
    check("signature is 64 bytes and the payload is the block byte for byte",
          len(sig) == 64 and webvh._unb64u(body_b64).decode() == out["blocks"][T_PAYLOAD])
    check("wrapped serialization joins back to the JWS",
          out["blocks"][T_JWS].replace("\n", "") == st["jws"])
    granted = [s["key"] for s in body["signers"] if s["status"] == "granted"]
    check("kid is a signer the Profile names at granted", header["kid"] in granted)
    check("the withdrawn and the announced keys did not sign",
          not any(es256_verify(keystore.load_or_create(n).public_key(), sig, signing_input)
                  for n in SIGNERS if n != SIGNING))
    check("issued_at is before next_update", body["issued_at"] < body["next_update"])
    bad = [p for p, v in durations(body) if not DURATION.match(v)]
    check("every duration is an RFC 3339 duration without the week form", not bad)

    trust_list = load("trustlist.json")["_structured"]["payload"]
    check("trusted_list equals DistributionPoints of the trusted list",
          body["addresses"]["trusted_list"]
          == trust_list["LoTE"]["ListAndSchemeInformation"]["DistributionPoints"])
    catalog = load("trqp.json")["catalog_payload"]
    check("credential_types are the types the catalog registers",
          list(body["credential_types"]) == [r["id"] for r in catalog["rulebooks"]])
    check("catalog lifetime equals the catalog list's exp minus iat (P1D)",
          catalog["exp"] - catalog["iat"] == 86400 and body["lifetimes"]["catalog"] == "P1D")
    statuses = load("statuslists.json")["_structured"]["lists"]
    ttls = {json.loads(webvh._unb64u(v["token"].split(".")[1])).get("ttl") for v in statuses.values()}
    check("status list TTL equals the ttl every example list carries (43200 s)",
          ttls == {43200} and set(body["lifetimes"]["status_list_ttl"].values()) == {"PT12H"})
    summary = load("summary.json")
    a = summary["answers"][0]["statement"]
    claims = json.loads(webvh._unb64u(a.split(".")[1]))
    check("Authority Statement lifetime equals exp minus iat of the example answers (PT12H)",
          claims["exp"] - claims["iat"] == 43200 and body["lifetimes"]["authority_statement"] == "PT12H")
    lists = [json.loads(webvh._unb64u(v["token"].split(".")[1])) for v in statuses.values()]
    check("every example status list has exp no earlier than iat plus ttl plus the tolerance "
          "(REQ-TS-5-09-084)",
          all(c["exp"] - c["iat"] >= c["ttl"] + 3 * 86400 for c in lists)
          and body["tolerances"]["status_list"] == "P3D")
    entities = load("entities.json")
    check("key storage root for hsm is the root certificate the entity endpoint example chains to",
          body["lists"]["key_storage_roots"]["hsm"] == [entities["maker_root"]])
    check("every signer did:key is P-256 and matches its keystore key",
          all(st["signers"][n] == webvh.did_key(webvh.multikey(keystore.load_or_create(n).public_key()))
              and st["signers"][n].startswith("did:key:zDna") for n in SIGNERS))

    bad_count = results.count(False)
    print(f"{len(results) - bad_count}/{len(results)} checks passed")
    return 1 if bad_count else 0


if __name__ == "__main__":
    sys.exit(main())
