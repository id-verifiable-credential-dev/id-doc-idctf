---
title: "[TS-02] Publishing and reading the Governance Profile"
description: The signed file every other specification takes its numbers and algorithms from, what it carries, how Trust Authority signs it, where Trust Registry serves it, and how a reader checks and caches its copy.
---

<!-- Sumber: tracks/0305, tracks/0368, tracks/0436; debt/0177, debt/0194; Glosarium dan Konvensi IDCTF §D.1 (Governance Profile), §F; data-model-and-protocols/index.md; keys-who-creates-who-signs.md; publishing-and-reading-the-trusted-list.md -->

<p class="ekdn-docid">TS-02</p>

# Publishing and reading the Governance Profile {#ts-02-publishing-and-reading-the-governance-profile}

<p class="ekdn-lead" markdown="span">
The one file every Module reads before anything else. It names the version
of each specification in force and every number and algorithm the ecosystem
may change without changing an interface. This specification fixes its
form, its signature, its address, and how long a copy counts.
</p>

Every sentence on this page binds Trust Authority, Trust Registry, and every
Module that reads the Governance Profile, and an Assessment Body tests them
against it in the version the Governance Profile puts in force. The key words
and the identifier `REQ-TS-02-nnn` follow
[Common provisions](common-provisions.md).

## Who runs this and what it needs {#ts-02-who-runs-this-and-what-it-needs}

This specification binds the Governance Profile as an artifact: its format,
the name and type of every member it carries, its signature, its
publication, and the rules a reader applies to the copy it holds. It sits
beside Common provisions and
[Finding a signer's key from its DID](finding-a-signers-key-from-its-did.md)
outside the groups, because every other specification takes a value from
it.

Its conformance targets are Trust Authority, which signs the Profile; Trust
Registry, which publishes it; and every reader. A reader is every Module that
applies a value the Profile holds: Issuer Core, Mobile Wallet, Wallet
Backend Service, Verifier Core, Mobile Verifier, Trust Authority, Trust
Registry, Decentralized Identifier (DID) Service, and a Relying Party's own application built on
Reader SDK. Issuer Console and Verifier Console apply no value of their own
and read nothing. A reader meets its requirements through Trust SDK where it
embeds the library, and otherwise by its own means.

It leaves to other documents: the values themselves, which the Governance
Profile as published holds and the Root Authority approves; [who may amend the Profile and through which approval, which the Governance Framework holds][gf-amending-the-governance-profile]; and
the rule each value feeds, which the specification named beside each member
holds. A value the Profile carries never changes an interface: an algorithm
it allows still has to be one the interface's specification admits, and a
lifetime it sets still has to fit the ceiling that specification fixes.

Before the first exchange, each target holds what the rules below assume:

- **Trust Authority** holds the Governance Profile key in its hardware
  security module (HSM), as [Trust Authority's own keys][trust-authoritys-own-keys]
  describes, and the values the Root Authority approved.
- **Trust Registry** reaches that key through Trust Authority and holds no
  private key of its own.
- **A reader** carries the Governance Profile key from build time, and the
  address of [Publication][ts-02-publication].

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-02-001 }**REQ-TS-02-001** Trust Authority MUST meet every requirement in [Signature][ts-02-signature] that names Trust Authority.
- [](){ #req-ts-02-002 }**REQ-TS-02-002** Trust Registry MUST meet every requirement in [Format][ts-02-format], [Edition information][ts-02-edition-information], [Signers][ts-02-signers], [Parameters][ts-02-parameters], and [Publication][ts-02-publication].
- [](){ #req-ts-02-003 }**REQ-TS-02-003** Every reader MUST meet every requirement in [Reading the copy][ts-02-reading-the-copy].

</div>

## What the Profile answers {#ts-02-overview}

A specification states what an implementation does, and leaves out the
numbers and algorithms the ecosystem may want to change on a different
cadence: how long a nonce lives, which algorithm signs an Authority
Statement, at which address the trusted list is served. Each of those
sentences ends in "the Governance Profile sets", and the Profile is where
the value is. [Data Model and Protocols](../architecture-framework/data-model-and-protocols/index.md)
places the Profile between the Credential Rulebook and the Governance
Framework.

The Profile is a file, not a document of IDCTF. The Root Authority approves
what it says, Trust Authority signs it, and Trust Registry publishes it.
Every edition is complete, carries a sequence number, and says when the next
one is due, in the shape [the trusted list](publishing-and-reading-the-trusted-list.md)
already has, so a reader that can check one can check the other.

The Profile carries every address but its own. A reader is built with one
address and one key, and finds everything else in the copy it verified:
the trusted list, the catalog, the query endpoint, the status lists, and the
doors of Trust Authority. The Profile cannot bound how stale its own copy may
be, or name the algorithm it is verified with, so this specification fixes
both.

## Governance Profile payload {#ts-02-governance-profile-payload}

The payload of an edition as Trust Registry publishes it, before
[Signature][ts-02-signature] wraps it in the JWS. It shows every member this
specification defines and every form a member admits: the three signer
states, a specification in force at two versions during a transition, the
three algorithm forms of an issuance key, a credential type map, and a key
storage value with no accepted root.

The Profile is an illustration: the addresses and the keys are invented, and
no Root Authority has approved an edition. Most values are the ones IDCTF sets
for the pilot, and the rest are invented.
Every field is exact. Where another example on these pages shows a value the Profile sets,
the Profile carries the same one: the trusted list address is the one the
[trusted list payload][ts-5-01-trusted-list-payload] repeats, the credential
types are the ones the catalog registers, the key storage root is the one
the entity endpoint's evidence chains to, and each lifetime is the interval
the example tokens carry. Version 2.0 of TS-5-01 does not exist; it stands
in for the transition a major version opens. The Profile was signed with the
key its own `signers` names at `granted`, and the signature verifies.

``` { .json title="governance-profile.json, the Profile payload" data-format="JSON" }
{
  "profile_version": 1,
  "sequence_number": 3,
  "issued_at": "2026-10-01T00:00:00Z",
  "next_update": "2026-12-30T00:00:00Z",
  "signers": [
    {
      "key": "did:key:zDnaeSid6fjPchzuU9t8VtWC6FsGf5yLGrFzFnTi9v2yVXCxa",
      "status": "granted",
      "since": "2026-10-01T00:00:00Z"
    },
    {
      "key": "did:key:zDnaeycT26AUYZiH8MKR7y8quFjayVbNJn9CCK4YoAhfJd9Ax",
      "status": "granted",
      "since": "2026-04-01T00:00:00Z"
    },
    {
      "key": "did:key:zDnaejUEW335Xfo4VbYNQoaZP9fBzLxubxjCBChVrihNkeB4w",
      "status": "withdrawn",
      "since": "2026-07-01T00:00:00Z"
    }
  ],
  "specifications": [
    {
      "id": "TS-00",
      "versions": [
        "1.0"
      ]
    },
    {
      "id": "TS-01",
      "versions": [
        "1.0"
      ]
    },
    {
      "id": "TS-02",
      "versions": [
        "1.0"
      ]
    },
    {
      "id": "TS-1-01",
      "versions": [
        "1.0"
      ]
    },
    {
      "id": "TS-2-01",
      "versions": [
        "1.0"
      ]
    },
    {
      "id": "TS-3-01",
      "versions": [
        "1.0"
      ]
    },
    {
      "id": "TS-3-02",
      "versions": [
        "1.0"
      ]
    },
    {
      "id": "TS-4-01",
      "versions": [
        "1.0"
      ]
    },
    {
      "id": "TS-4-02",
      "versions": [
        "1.0"
      ]
    },
    {
      "id": "TS-4-03",
      "versions": [
        "1.0"
      ]
    },
    {
      "id": "TS-5-01",
      "versions": [
        "1.0",
        "2.0"
      ],
      "transition_ends": "2027-03-31T00:00:00Z"
    },
    {
      "id": "TS-5-02",
      "versions": [
        "1.0"
      ]
    },
    {
      "id": "TS-5-03",
      "versions": [
        "1.0"
      ]
    },
    {
      "id": "TS-5-04",
      "versions": [
        "1.0"
      ]
    },
    {
      "id": "TS-5-05",
      "versions": [
        "1.0"
      ]
    },
    {
      "id": "TS-5-06",
      "versions": [
        "1.0"
      ]
    },
    {
      "id": "TS-5-07",
      "versions": [
        "1.0"
      ]
    },
    {
      "id": "TS-5-08",
      "versions": [
        "1.0"
      ]
    },
    {
      "id": "TS-5-09",
      "versions": [
        "1.0"
      ]
    },
    {
      "id": "TS-5-10",
      "versions": [
        "1.0"
      ]
    },
    {
      "id": "TS-5-11",
      "versions": [
        "1.0"
      ]
    }
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
    "TRQP": "2.0"
  },
  "addresses": {
    "trust_registry": "https://query.trust.go.id",
    "catalog": "https://catalog.trust.go.id",
    "trusted_list": [
      "https://registry.trust.go.id/trusted-list.json"
    ],
    "status_list_host": "https://registry.trust.go.id",
    "did_resolver": "https://did.trust.go.id",
    "entity_endpoint": "https://entities.trust.go.id",
    "portal": "https://portal.trust.go.id"
  },
  "algorithms": {
    "trusted_list": [
      "ES256"
    ],
    "recognition_answer": [
      "ES256"
    ],
    "catalog": [
      "ES256"
    ],
    "authority_statement": [
      "ES256"
    ],
    "use_statement": [
      "ES256"
    ],
    "accreditation_credential": [
      "ES256"
    ],
    "key_attestation": [
      "ES256"
    ],
    "status_list": [
      "ES256"
    ],
    "issuance": {
      "dc+sd-jwt": [
        "ES256"
      ],
      "mso_mdoc": [
        -7
      ],
      "ldp_vc": [
        "ecdsa-rdfc-2019"
      ]
    },
    "credential_key": [
      "ES256"
    ],
    "dpop": [
      "ES256"
    ],
    "request_object": [
      "ES256"
    ]
  },
  "lifetimes": {
    "authority_statement": "PT12H",
    "recognition_answer": "PT12H",
    "catalog": "P1D",
    "status_list_ttl": {
      "credential": "PT12H",
      "use_statement": "PT12H",
      "accreditation": "PT12H"
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
    "registration_suspension": "P90D"
  },
  "roots": {
    "issuer_root_ca": {
      "longest_certificate": "P10Y",
      "signing_period": "P3Y",
      "lead_time": "P2Y"
    },
    "verifier_root_ca": {
      "longest_certificate": "P5Y",
      "signing_period": "P8Y",
      "lead_time": "P2Y"
    }
  },
  "credential_types": {
    "id.idctf.ktp.1": {
      "validity_ceiling": "P90D"
    },
    "id.idctf.kartu-indonesia-sehat.1": {
      "validity_ceiling": "P1Y"
    },
    "id.idctf.kartu-asn.1": {
      "validity_ceiling": "P1Y"
    },
    "id.idctf.kartu-nikah.1": {
      "validity_ceiling": "P1Y"
    },
    "org.iso.18013.5.1.mDL.1": {
      "validity_ceiling": "P90D"
    }
  },
  "tolerances": {
    "recognition_answer": "P1D",
    "catalog": "P7D",
    "authority_statement": "P1D",
    "did_webvh_log": "P7D",
    "status_list": "P3D",
    "use_statement_status_list": "P3D",
    "crl": "P7D",
    "vical": "P7D"
  },
  "intervals": {
    "trust_cache_sync": {
      "every": "PT6H",
      "jitter": "PT30M"
    },
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
    "amendment_notice": "P90D"
  },
  "rotation": {
    "issuance-jose": {
      "interval": "P1Y",
      "overlap": "P60D"
    },
    "issuance-cose": {
      "interval": "P1Y",
      "overlap": "P60D"
    },
    "request-object": {
      "interval": "P1Y",
      "overlap": "P60D"
    },
    "verifier-issuing-ca": {
      "interval": "P3Y",
      "overlap": "P90D"
    },
    "key-attestation": {
      "interval": "P1Y",
      "overlap": "P60D"
    },
    "update": {
      "interval": "P2Y"
    },
    "retired_private_key": "destroy",
    "trust_authority": {
      "trusted-list": {
        "interval": "P2Y",
        "lead_time": "P90D"
      },
      "vical": {
        "interval": "P2Y",
        "lead_time": "P90D"
      },
      "governance-profile": {
        "interval": "P2Y",
        "lead_time": "P90D"
      },
      "accreditation-credential": {
        "interval": "P2Y"
      },
      "accreditation-status-list": {
        "interval": "P2Y"
      },
      "use-statement": {
        "interval": "P2Y"
      },
      "use-statement-status-list": {
        "interval": "P2Y"
      },
      "authority-statement": {
        "interval": "P2Y"
      },
      "recognition-statement": {
        "interval": "P2Y"
      },
      "catalog": {
        "interval": "P2Y"
      },
      "update": {
        "interval": "P2Y"
      },
      "witness": {
        "interval": "P2Y"
      }
    }
  },
  "limits": {
    "query_rate": {
      "requests": 600,
      "per": "PT1M"
    },
    "entity_endpoint_rate": {
      "requests": 60,
      "per": "PT1M"
    },
    "portal_rate": {
      "requests": 120,
      "per": "PT1M"
    },
    "portal_failed_sign_ins": 10,
    "use_statement_cut_off": "2026-10-01T00:00:00Z",
    "key_attestation_clock_skew": "PT1M",
    "transaction_code_attempts": 3,
    "did_service_availability": {
      "share": 0.995,
      "window": "P90D"
    },
    "did_service_recovery": "PT4H",
    "integrity_verdict_window": "PT5M"
  },
  "lists": {
    "authorization_actions": [
      "issue",
      "request"
    ],
    "recognition_actions": [
      "issue"
    ],
    "key_storage_roots": {
      "hsm": [
        "MIIB1jCCAXugAwIBAgIESx0AATAKBggqhkjOPQQDAjBPMQswCQYDVQQGEwJJRDEjMCEGA1UECgwaUFQgQ29udG9oIFBlcmFuZ2thdCBLcmlwdG8xGzAZBgNVBAMMEkNvbnRvaCBIU00gUm9vdCBDQTAeFw0yNDAxMDEwMDAwMDBaFw00NDAxMDEwMDAwMDBaME8xCzAJBgNVBAYTAklEMSMwIQYDVQQKDBpQVCBDb250b2ggUGVyYW5na2F0IEtyaXB0bzEbMBkGA1UEAwwSQ29udG9oIEhTTSBSb290IENBMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAERj-9cvrN1iS_N0FgXkCb2JAWyUioa7LBZiBJr7I9SaHWylp5oPKwL03Pekn2PRRaOCZTqlA9m8WaXCtd1jP5p6NFMEMwEgYDVR0TAQH_BAgwBgEB_wIBADAOBgNVHQ8BAf8EBAMCAgQwHQYDVR0OBBYEFKc7FiFUzk9-74EH7FvsRLLGiuhhMAoGCCqGSM49BAMCA0kAMEYCIQDJ87wCSxTqCuERQO_HhBAAoRkdh66dAoW6eFNLYRSzQgIhAO5tmKcuwZ_xH5isT2LUTVknP1J8gEf5Jv3-LYKh6KyF"
      ],
      "cloudkms": []
    },
    "portal_second_factors": [
      "webauthn",
      "totp"
    ],
    "recognized_evaluation_schemes": [
      "eucc",
      "sogis",
      "id-bssn"
    ],
    "android_device_recognition_verdict": [
      {
        "from_version": 13,
        "requires": "MEETS_STRONG_INTEGRITY"
      },
      {
        "from_version": 10,
        "requires": "MEETS_DEVICE_INTEGRITY"
      }
    ],
    "attestation_root_refusal": [
      {
        "root": "CEDB1CB6DC896AE5EC797348BCE9286753C2B38EE71CE0FBE34A9A1248800DFC",
        "from": "2036-01-01T00:00:00Z"
      }
    ]
  },
  "mappings": {
    "min_assurance": {
      "high": {
        "key_storage": [
          "iso_18045_high"
        ],
        "user_authentication": [
          "iso_18045_moderate",
          "iso_18045_high"
        ],
        "proof_types": [
          "attestation"
        ]
      },
      "substantial": {
        "key_storage": [
          "iso_18045_moderate",
          "iso_18045_high"
        ],
        "user_authentication": [
          "iso_18045_moderate",
          "iso_18045_high"
        ],
        "proof_types": [
          "attestation",
          "jwt"
        ]
      },
      "low": {
        "key_storage": [
          "iso_18045_enhanced-basic",
          "iso_18045_moderate",
          "iso_18045_high"
        ],
        "user_authentication": [
          "iso_18045_enhanced-basic",
          "iso_18045_moderate",
          "iso_18045_high"
        ],
        "proof_types": [
          "attestation",
          "jwt"
        ]
      }
    },
    "issuer_assurance": {
      "software": "low",
      "cloudkms": "substantial",
      "hsm": "high"
    }
  },
  "key_storage": {
    "verifier-issuing-ca": [
      "cloudkms",
      "hsm"
    ]
  },
  "permissions": {
    "dsc_per_group_of_types": false
  }
}
```

## Format {#ts-02-format}

The Profile is one JSON object in UTF-8. Its members are the edition
information, the signers, and the parameters, each defined below with its
type. The types are these: `integer` and `number` as JSON gives them; a
`string`; a `date-time` in Coordinated Universal Time (UTC) as the
`date-time` of [RFC 3339][ref-rfc3339] with no fraction of a second and the
`Z` designator, as [ETSI TS 119 602 V1.1.1][ref-etsi-ts-119602] asks of the trusted list; a `duration` as
the `duration` of [RFC 3339][ref-rfc3339] Appendix A, without the week
form; and a `URL`, an absolute Uniform Resource Locator (URL) with the
`https` scheme, no query and no fragment.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-02-004 }**REQ-TS-02-004** The Profile MUST be a JSON object encoded in UTF-8.
- [](){ #req-ts-02-005 }**REQ-TS-02-005** The Profile MUST carry every member this specification defines, with the type it gives.
- [](){ #req-ts-02-006 }**REQ-TS-02-006** The Profile MUST NOT carry a member with a null value.
- [](){ #req-ts-02-007 }**REQ-TS-02-007** Every `date-time` MUST follow the `date-time` production of [RFC 3339][ref-rfc3339] in UTC, with no fraction of a second and the `Z` designator.
- [](){ #req-ts-02-008 }**REQ-TS-02-008** Every `duration` MUST follow the `duration` production of [RFC 3339][ref-rfc3339] Appendix A, without the week form.
- [](){ #req-ts-02-009 }**REQ-TS-02-009** Every `URL` MUST be an absolute `https` URL with no query and no fragment.

</div>

A member is added to this specification as a minor version, when another
specification defers a new value to the Profile, and an older reader ignores
it; a member is never removed or retyped except in a major version.

## Edition information {#ts-02-edition-information}

[](){ #tbl-ts-02-edition-information }

<figure markdown="1" class="ekdn-table">

| Member | Type | Requirement |
|---|---|---|
| `profile_version` | integer | `1`, the major version of this specification the edition is written to |
| `sequence_number` | integer | `1` for the first edition ever published, then one more for every edition after it |
| `issued_at` | date-time | The time the edition was issued |
| `next_update` | date-time | The time by which the next edition is published |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-02-010 }**REQ-TS-02-010** Trust Registry MUST set every member of [the table of edition information][tbl-ts-02-edition-information] as it requires.
- [](){ #req-ts-02-011 }**REQ-TS-02-011** Trust Registry MUST increase `sequence_number` by exactly one on every edition it publishes.
- [](){ #req-ts-02-012 }**REQ-TS-02-012** Trust Registry MUST set `next_update` later than `issued_at`.
- [](){ #req-ts-02-013 }**REQ-TS-02-013** Trust Registry MUST NOT set `next_update` later than six months after `issued_at`.

</div>

An edition is a complete Profile, never a change to the one before. The
six-month ceiling is the one the trusted list keeps,
[REQ-TS-5-01-012][req-ts-5-01-012].

## Signers {#ts-02-signers}

`signers` names every key that may sign an edition, and every key that did
and may no longer. A key is announced in an edition before it signs one, and
withdrawn in an edition when it stops, as
[how Trust Authority's keys are replaced][how-trust-authoritys-keys-are-replaced]
describes for the lists. Each entry is an object.

[](){ #tbl-ts-02-signers }

<figure markdown="1" class="ekdn-table">

| Member | Type | Requirement |
|---|---|---|
| `key` | string | The public key as a `did:key`, encoded as [Encoding][ts-5-03-encoding] requires |
| `status` | string | `granted` or `withdrawn` |
| `since` | date-time | The time the status took effect |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-02-014 }**REQ-TS-02-014** `signers` MUST name the key that signed the edition, at `granted`.
- [](){ #req-ts-02-015 }**REQ-TS-02-015** `signers` MUST name every key that may sign the next edition, at `granted`.
- [](){ #req-ts-02-016 }**REQ-TS-02-016** A key that stops being accepted MUST be set to `withdrawn`, with `since` the time from which an edition it signs is refused.
- [](){ #req-ts-02-017 }**REQ-TS-02-017** Trust Registry MUST NOT remove a withdrawn key from `signers`.

</div>

## Parameters {#ts-02-parameters}

Every value another specification defers to the Profile is one member below,
grouped as the values are. Each table gives the member, its type, and the
requirement that applies it; a member whose table names no requirement is
applied where the specification names the Profile in prose. The values
themselves are the Root Authority's.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-02-018 }**REQ-TS-02-018** A Module MUST take every value another specification defers to the Governance Profile from the member this section names for it, in the copy [Reading the copy][ts-02-reading-the-copy] lets it use.

</div>

### Specifications and standards in force {#ts-02-specifications-and-standards-in-force}

`specifications` is an array with one entry for every Technical
Specification, each an object with `id`, the identifier as `TS-5-01`;
`versions`, the array of versions in force as `1.0`; and, when `versions`
holds two, `transition_ends`, the `date-time` the older one stops counting.
`standards` is an object whose names are the labels of
[References](../references/index.md) and whose values are the version of that
standard in force, as the entry writes it.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-02-019 }**REQ-TS-02-019** `specifications` MUST name every Technical Specification once.
- [](){ #req-ts-02-020 }**REQ-TS-02-020** An entry MUST hold two versions only during the transition period of a major change, and MUST then carry `transition_ends`.
- [](){ #req-ts-02-021 }**REQ-TS-02-021** A Module MUST conform to a version `specifications` holds for each specification that binds it, as [REQ-TS-00-004][req-ts-00-004] to [REQ-TS-00-006][req-ts-00-006] require.
- [](){ #req-ts-02-022 }**REQ-TS-02-022** A Module MUST NOT run a standard that `standards` names at a version other than the one it gives.

</div>

### Addresses {#ts-02-addresses}

[](){ #tbl-ts-02-addresses }

<figure markdown="1" class="ekdn-table">

| Member | Type | Applied by |
|---|---|---|
| `trust_registry` | URL | `<endpoint>` of the query endpoint, [REQ-TS-4-02-005][req-ts-4-02-005] |
| `catalog` | URL | `<catalog>` of [The catalog][ts-4-02-the-catalog] |
| `trusted_list` | array of URL | Every distribution point of the trusted list, which its `DistributionPoints` repeats |
| `status_list_host` | URL | The host of the Use Statement and accreditation status lists, [Publishing and reading a status list](publishing-and-reading-a-status-list.md) |
| `did_resolver` | URL | DID Service's Resolver endpoint, [Witnessing a log entry and serving its copy](witnessing-a-log-entry-and-serving-its-copy.md) |
| `entity_endpoint` | URL | `<endpoint>` of Trust Authority's entity endpoint, [REQ-TS-4-03-050][req-ts-4-03-050] |
| `portal` | URL | Trust Authority's portal, [REQ-TS-4-03-003][req-ts-4-03-003] |

</figure>

### Algorithms {#ts-02-algorithms}

`algorithms` holds, for each key, the array of algorithms a signature with
it may use, as the `alg` names of [RFC 7518][ref-rfc7518]. `issuance` is an
object instead, because one key signs three formats: `dc+sd-jwt` holds `alg`
names, `mso_mdoc` the algorithm numbers of [RFC 9053][ref-rfc9053], and
`ldp_vc` cryptosuite names, as [REQ-TS-1-01-014][req-ts-1-01-014] writes them.
Where a credential key signs a `COSE_Sign1`, as a `deviceSignature` does, an
entry of `credential_key` stands for the number [RFC 9053][ref-rfc9053] gives
the same algorithm: `ES256` is `-7` under
[REQ-TS-5-11-058][req-ts-5-11-058].

<figure markdown="1" class="ekdn-table">

| Member | Applied by |
|---|---|
| `trusted_list` | [REQ-TS-5-01-053][req-ts-5-01-053] |
| `recognition_answer` | [REQ-TS-4-02-039][req-ts-4-02-039] |
| `catalog` | [REQ-TS-4-02-063][req-ts-4-02-063] |
| `authority_statement` | [REQ-TS-5-05-023][req-ts-5-05-023] |
| `use_statement` | [REQ-TS-5-06-029][req-ts-5-06-029] |
| `accreditation_credential` | [REQ-TS-5-07-006][req-ts-5-07-006] |
| `key_attestation` | [REQ-TS-5-08-006][req-ts-5-08-006], [REQ-TS-1-01-017][req-ts-1-01-017], [REQ-TS-1-01-018][req-ts-1-01-018] |
| `status_list` | [REQ-TS-5-09-012][req-ts-5-09-012] |
| `issuance` | [REQ-TS-5-10-013][req-ts-5-10-013], [REQ-TS-5-10-063][req-ts-5-10-063], [REQ-TS-1-01-014][req-ts-1-01-014], [REQ-TS-1-01-022][req-ts-1-01-022], [REQ-TS-3-01-041][req-ts-3-01-041] |
| `credential_key` | [REQ-TS-5-11-025][req-ts-5-11-025], [REQ-TS-5-11-058][req-ts-5-11-058], [REQ-TS-1-01-018][req-ts-1-01-018], [REQ-TS-3-01-041][req-ts-3-01-041] |
| `dpop` | [REQ-TS-1-01-079][req-ts-1-01-079], [REQ-TS-1-01-037][req-ts-1-01-037] |
| `request_object` | [REQ-TS-3-01-027][req-ts-3-01-027] |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-02-023 }**REQ-TS-02-023** An algorithm in `algorithms` MUST be one the specification of the artifact it signs admits.

</div>

### Lifetimes {#ts-02-lifetimes}

Every member of `lifetimes` is a `duration`, except `status_list_ttl`, an
object of three durations named `credential`, `use_statement` and
`accreditation`, one for each kind of status list.

<figure markdown="1" class="ekdn-table">

| Member | What it bounds | Applied by |
|---|---|---|
| `authority_statement` | From `iat` to `exp` of an Authority Statement | [REQ-TS-5-05-032][req-ts-5-05-032] |
| `recognition_answer` | From `iat` to `exp` of a recognition answer | [REQ-TS-4-02-042][req-ts-4-02-042] |
| `catalog` | From `iat` to `exp` of the catalog list | [REQ-TS-4-02-067][req-ts-4-02-067] |
| `status_list_ttl` | `ttl` of each kind of status list | [REQ-TS-5-09-052][req-ts-5-09-052] |
| `credential_suspension` | The longest a credential's entry stays suspended | [REQ-TS-5-09-124][req-ts-5-09-124] |
| `use_statement` | From `iat` to `exp` of a registered use | [REQ-TS-5-06-036][req-ts-5-06-036] |
| `trusted_list_horizon` | From `ListIssueDateTime` to `NextUpdate` | [REQ-TS-5-01-011][req-ts-5-01-011] |
| `verifier_device_certificate` | Validity of a Verifier Device Certificate | [Issuing and validating the X.509 certificates and the VICAL](issuing-and-validating-the-x509-certificates-and-the-vical.md) |
| `verifier_issuing_ca` | Validity of a Verifier Issuing CA certificate, never past its root | [Issuing and validating the X.509 certificates and the VICAL](issuing-and-validating-the-x509-certificates-and-the-vical.md) |
| `accreditation_period` | An accreditation period | [REQ-TS-5-07-050][req-ts-5-07-050] |
| `entity_endpoint_nonce` | A nonce at the entity endpoint | [REQ-TS-4-03-057][req-ts-4-03-057] |
| `registration_code` | A registration code | [REQ-TS-4-03-021][req-ts-4-03-021] |
| `enrollment_challenge` | An enrollment challenge | [REQ-TS-2-01-005][req-ts-2-01-005], [REQ-TS-5-04-139][req-ts-5-04-139] |
| `pre_authorized_code` | A pre-authorized code | [REQ-TS-1-01-046][req-ts-1-01-046] |
| `par_request_uri` | A request URI at the pushed authorization request endpoint | [REQ-TS-1-01-059][req-ts-1-01-059] |
| `authorization_code` | An authorization code | [REQ-TS-1-01-069][req-ts-1-01-069] |
| `access_token` | An access token at Issuer Core | [REQ-TS-1-01-075][req-ts-1-01-075] |
| `refresh_token_inactivity` | How long past the end of the technical validity period of its latest credential a refresh token still works | [REQ-TS-1-01-148][req-ts-1-01-148] |
| `dpop_nonce` | A DPoP nonce | [REQ-TS-1-01-086][req-ts-1-01-086] |
| `c_nonce` | A `c_nonce` | [REQ-TS-1-01-094][req-ts-1-01-094] |
| `deferred_request` | A deferred issuance request | [REQ-TS-1-01-119][req-ts-1-01-119] |
| `request_object` | A Request Object | [REQ-TS-3-01-035][req-ts-3-01-035] |
| `relayed_response` | The time the relay holds a response its device has not collected | [REQ-TS-3-01-095][req-ts-3-01-095] |
| `relay_record` | How long the relay keeps the record of a relayed transaction | [REQ-TS-3-01-113][req-ts-3-01-113] |
| `consent_receipt` | How long a verifier keeps the record of an OpenID4VP presentation and its consent receipt, where no law binding the Relying Party requires longer | [REQ-TS-5-11-099][req-ts-5-11-099] |
| `presentation_history` | The longest Mobile Wallet keeps the record of a presentation | [REQ-TS-5-11-102][req-ts-5-11-102] |
| `dispute_period` | How long an entity keeps the records a dispute may call for | [Retention][gf-retention] |
| `registration_suspension` | The longest a registration stays suspended before the Root Authority restores or withdraws it | [Grounds for suspension][gf-grounds-for-suspension] |

</figure>

### Roots {#ts-02-roots}

`roots` holds `issuer_root_ca` and `verifier_root_ca`, each an object of
three durations whose sum is the root's validity, as
[REQ-TS-5-04-026][req-ts-5-04-026] requires: `longest_certificate`, the
longest validity of a certificate the root signs; `signing_period`, the
period in which it signs them; and `lead_time`, the time to distribute it.

### Credential types {#ts-02-credential-types}

`credential_types` is an object with one member for every credential type
the catalog registers, named by its identifier, as `id.idctf.ktp.1`. Each is
an object with `validity_ceiling`, the `duration` an issuer's technical
validity period never exceeds, which
[REQ-TS-5-10-097][req-ts-5-10-097] applies.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-02-024 }**REQ-TS-02-024** `credential_types` MUST carry a member for every credential type the catalog registers.
- [](){ #req-ts-02-025 }**REQ-TS-02-025** Issuer Core MUST NOT issue a credential of a type that `credential_types` does not name.

</div>

### Tolerances {#ts-02-tolerances}

Every member of `tolerances` is a `duration`: how long past its own expiry a
reader may still use a cached copy, as
[the three rules for reading the copy][three-rules-for-reading-the-copy]
set out. One value applies to every reader of the copy, online or
not: no reader fetches during a transaction, so a reader that reaches the
network refreshes on the [trust cache sync][trust-cache-sync] and seldom
nears the limit, and one that cannot stops at the same limit.

<figure markdown="1" class="ekdn-table">

| Member | Copy | Applied by |
|---|---|---|
| `recognition_answer` | A recognition answer | [REQ-TS-4-02-047][req-ts-4-02-047] |
| `catalog` | The catalog list | [REQ-TS-4-02-096][req-ts-4-02-096], [REQ-TS-4-02-097][req-ts-4-02-097] |
| `authority_statement` | An Authority Statement | [REQ-TS-5-05-034][req-ts-5-05-034] |
| `did_webvh_log` | A cached `did:webvh` log | [REQ-TS-5-02-061][req-ts-5-02-061] |
| `status_list` | An issuer's status list | [REQ-TS-5-09-074][req-ts-5-09-074], [REQ-TS-5-09-084][req-ts-5-09-084] |
| `use_statement_status_list` | The Use Statement status list | [REQ-TS-5-06-043][req-ts-5-06-043] |
| `crl` | A certificate revocation list (CRL), reader side | [REQ-TS-5-04-158][req-ts-5-04-158], [REQ-TS-5-04-159][req-ts-5-04-159] |
| `vical` | The Verified Issuer Certificate Authority List (VICAL), reader side | [REQ-TS-5-04-160][req-ts-5-04-160], [REQ-TS-5-04-161][req-ts-5-04-161] |

</figure>

### Intervals {#ts-02-intervals}

<figure markdown="1" class="ekdn-table">

| Member | Type | What it times | Applied by |
|---|---|---|---|
| `trust_cache_sync` | object | `every`, the duration between two syncs, and `jitter`, the largest random delay added to each | [REQ-TS-5-01-091][req-ts-5-01-091] |
| `status_list_republication` | duration | Republication of a status list whether or not an entry changed | [REQ-TS-5-09-048][req-ts-5-09-048] |
| `status_list_change` | duration | Republication after an entry changes | [REQ-TS-5-09-049][req-ts-5-09-049] |
| `accreditation_status_change` | duration | Setting an accreditation status entry after the Root Authority changes it | [REQ-TS-5-07-065][req-ts-5-07-065] |
| `crl_publication` | duration | Publication of every CRL, Trust Authority's and each Verifier Issuing CA's, and the longest time from its `thisUpdate` to its `nextUpdate` | [REQ-TS-5-04-069][req-ts-5-04-069], [REQ-TS-5-04-166][req-ts-5-04-166] |
| `vical_publication` | duration | The longest time from a VICAL's `date` to its `nextUpdate` | [REQ-TS-5-04-167][req-ts-5-04-167] |
| `dsc_expiry_warning` | duration | How long before a Document Signer Certificate expires its issuer is warned | [REQ-TS-5-04-162][req-ts-5-04-162] |
| `credential_renewal_lead` | duration | The longest time before `exp` a wallet starts renewal | [REQ-TS-1-01-127][req-ts-1-01-127], [REQ-TS-1-01-149][req-ts-1-01-149] |
| `accreditation_renewal_lead` | duration | How long before `exp` an accreditation renewal is prepared | [REQ-TS-5-07-051][req-ts-5-07-051] |
| `merchant_withdrawal` | duration | Withdrawing a merchant from the Relying Party that vouches for it | [Withdrawing a merchant][gf-withdrawing-a-merchant] |
| `registration_change_notice` | duration | Telling Trust Authority of a change to what an entity registered | [Keeping the registration true][gf-keeping-the-registration-true] |
| `loss_report_action` | duration | Acting on a report that a credential or device is lost | [Loss reports][gf-loss-reports] |
| `license_change_report` | duration | Reporting a change to a sector license | [Sector license][gf-sector-license] |
| `correction_period` | duration | The time an entity has to correct the grounds for a warning | [Grounds for a warning][gf-grounds-for-a-warning] |
| `incident_report` | duration | Reporting an incident after it is found | [Reporting an incident][gf-reporting-an-incident] |
| `post_mortem` | duration | Delivering the post-mortem of an incident | [Post-mortem][gf-post-mortem] |
| `amendment_notice` | duration | Notice given before an amendment takes effect | [Notice of an amendment][gf-notice-of-an-amendment] |

</figure>

### Rotation {#ts-02-rotation}

`rotation` holds one member per entity key purpose, `issuance-jose`,
`issuance-cose`, `request-object`, `verifier-issuing-ca`, `key-attestation`
and `update`, each an object of two durations: `interval`, the time between
two scheduled rotations, and `overlap`, the time in which the old and the new
key are both accepted. `update` carries `interval` alone, because under
pre-rotation the old update key signs nothing after the entry that commits to
its successor ([REQ-TS-5-02-036][req-ts-5-02-036],
[REQ-TS-5-02-038][req-ts-5-02-038]). The `status-list` key has no member of
its own and rotates on the calendar of `issuance-jose`. `retired_private_key` is `destroy` or `retain`: what a
Key Manager does with a private key once it is retired. `trust_authority`
holds one member for each of Trust Authority's twelve keys other than the
two roots, each an object with `interval`, the time between two scheduled
replacements; the trusted list key, the VICAL key and the Governance Profile
key, which are replaced by announcement, also carry `lead_time`, how long
before its first signature a new key is announced.
[How an entity rotates a key][how-an-entity-rotates-a-key] and
[how Trust Authority's keys are replaced][how-trust-authoritys-keys-are-replaced]
apply them. The `interval` of `verifier-issuing-ca` bounds the time the key
signs; the certificate that carries it stays valid for
`lifetimes.verifier_issuing_ca`, past the end of that interval, so that a
Verifier Device Certificate it signed never outlasts it
([REQ-TS-5-04-051][req-ts-5-04-051]).

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-02-026 }**REQ-TS-02-026** The `interval` of `issuance-cose` MUST NOT exceed the shortest validity period a Document Signer Certificate may have under [Issuing and validating the X.509 certificates and the VICAL](issuing-and-validating-the-x509-certificates-and-the-vical.md) for the credential types its issuer signs.

</div>

### Limits {#ts-02-limits}

<figure markdown="1" class="ekdn-table">

| Member | Type | What it limits | Applied by |
|---|---|---|---|
| `query_rate` | object | `requests` per `per` from one network address at the query endpoint | [REQ-TS-4-02-013][req-ts-4-02-013] |
| `entity_endpoint_rate` | object | The same at the entity endpoint | [REQ-TS-4-03-053][req-ts-4-03-053] |
| `portal_rate` | object | The same at the portal | [REQ-TS-4-03-010][req-ts-4-03-010] |
| `portal_failed_sign_ins` | integer | Consecutive failed sign-ins after which a portal account is locked | [REQ-TS-4-03-122][req-ts-4-03-122] |
| `use_statement_cut_off` | date-time | The time after which a request carrying no Use Statement is refused | [REQ-TS-5-06-075][req-ts-5-06-075], [REQ-TS-5-06-102][req-ts-5-06-102], [REQ-TS-02-059][req-ts-02-059] |
| `key_attestation_clock_skew` | duration | How far a Key Attestation's `iat` may lie in the future | [REQ-TS-5-08-038][req-ts-5-08-038] |
| `transaction_code_attempts` | integer | Wrong transaction codes after which a pre-authorized code is invalidated | [REQ-TS-1-01-072][req-ts-1-01-072] |
| `did_service_availability` | object | `share`, a number between 0 and 1, of the rolling `window` DID Service is available | [REQ-TS-4-01-014][req-ts-4-01-014] |
| `did_service_recovery` | duration | The time DID Service is back within after an outage | [REQ-TS-4-01-015][req-ts-4-01-015] |
| `integrity_verdict_window` | duration | How far an integrity verdict's `timestampMillis` may lie from the moment it is read | [REQ-TS-2-01-034][req-ts-2-01-034], [REQ-TS-5-04-145][req-ts-5-04-145] |

</figure>

Every edition carries `use_statement_cut_off`, so the edition that sets the
date or brings it forward is the notice of it, and Mobile Wallet reads it at
its next sync. The 90 days below are a constant of this specification and not
a member of the Profile, because an edition that set its own notice could
shorten it in the edition that uses it, the same reason
[REQ-TS-02-056][req-ts-02-056] fixes its seven days here. Postponing the date,
or keeping it, needs no notice. Who tells the staff of a Relying Party, and
what notice a law requires, [is the Governance Framework's][gf-amendment].


<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-02-059 }**REQ-TS-02-059** Trust Registry MUST NOT publish an edition, other than the first, whose `use_statement_cut_off` is earlier than that of the previous edition and earlier than 90 days after its own `issued_at`.

</div>

### Closed lists {#ts-02-closed-lists}

<figure markdown="1" class="ekdn-table">

| Member | Type | What it lists | Applied by |
|---|---|---|---|
| `authorization_actions` | array of string | The `action` values admitted for authorization | [REQ-TS-5-05-013][req-ts-5-05-013], [REQ-TS-5-05-014][req-ts-5-05-014], [REQ-TS-5-07-029][req-ts-5-07-029] |
| `recognition_actions` | array of string | The `action` values admitted for recognition | [REQ-TS-4-02-025][req-ts-4-02-025], [REQ-TS-4-02-033][req-ts-4-02-033] |
| `key_storage_roots` | object | For `hsm` and `cloudkms`, the array of root certificates accepted as key storage evidence, each DER in base64url without padding, as the `certs` of the evidence carry the rest of the chain | [REQ-TS-4-03-083][req-ts-4-03-083] |
| `portal_second_factors` | array of string | The second factors accepted at sign-in to the portal, `webauthn` or `totp` | [REQ-TS-4-03-004][req-ts-4-03-004] |
| `android_device_recognition_verdict` | array of object | `from_version`, an Android major version, and `requires`, the `deviceRecognitionVerdict` value a verdict from that version on has to hold | [REQ-TS-2-01-033][req-ts-2-01-033], [REQ-TS-5-04-145][req-ts-5-04-145] |
| `attestation_root_refusal` | array of object | `root`, the fingerprint of an accepted attestation root, and `from`, the `date-time` from which a chain ending at it is refused | [REQ-TS-2-01-047][req-ts-2-01-047], [REQ-TS-5-04-151][req-ts-5-04-151] |
| `recognized_evaluation_schemes` | array of string | The schemes whose Common Criteria certificates count as an evaluation reaching `iso_18045_high`, each of the codes [the table of evaluation scheme codes][tbl-ts-02-evaluation-scheme-codes] gives | [REQ-TS-5-08-081][req-ts-5-08-081], [REQ-TS-5-08-088][req-ts-5-08-088] |

</figure>

[](){ #tbl-ts-02-evaluation-scheme-codes }

<figure markdown="1" class="ekdn-table">

| Code | Scheme |
|---|---|
| `eucc` | The European Union Common Criteria based cybersecurity certification scheme, Regulation (EU) 2024/482 |
| `sogis` | The Senior Officials Group Information Systems Security (SOG-IS) Mutual Recognition Agreement |
| `id-bssn` | Skema Common Criteria Indonesia (SCCI), run by Badan Siber dan Sandi Negara (BSSN) under Peraturan BSSN Nomor 15 Tahun 2019, with certificates issued by its product certification body (LSPro) |

</figure>

An evaluation counts when a laboratory that the scheme
which issued the certificate licenses or accredits carried it out
([REQ-TS-5-08-089][req-ts-5-08-089]); the Profile holds no list of
laboratories.

The entry of `android_device_recognition_verdict` that applies to a device
is the one with the highest `from_version` that is not above the device's
Android version.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-02-027 }**REQ-TS-02-027** Wallet Backend Service MUST refuse an integrity verdict from an Android version below the lowest `from_version` of `android_device_recognition_verdict`.

</div>

### Mappings {#ts-02-mappings}

`mappings` holds `min_assurance`, an object with one member for each of
`low`, `substantial` and `high`, each holding `key_storage` and
`user_authentication`, the arrays of `iso_18045_*` values an issuer announces
in `key_attestations_required`, and `proof_types`, the proof types it
accepts; and `issuer_assurance`, an object that names the grade each Key
Manager driver, `software`, `cloudkms` and `hsm`, earns.
[`min_assurance`][min-assurance] and [`issuer_assurance`][issuer-assurance]
explain both, and [REQ-TS-1-01-016][req-ts-1-01-016] and
[REQ-TS-4-03-086][req-ts-4-03-086] apply them.

### Key storage and permissions {#ts-02-key-storage-and-permissions}

`key_storage` holds one member per key purpose whose driver is bound, each
the array of drivers that key may live in, as `verifier-issuing-ca` for the
Verifier Issuing CA key, which [a Relying Party's keys][a-relying-partys-keys]
keeps out of the software keystore. `permissions` holds
`dsc_per_group_of_types`, a boolean that says whether an issuer may hold one
Document Signer Certificate for a group of credential types, as
[the issuer side][the-issuer-side] leaves open.

## Signature {#ts-02-signature}

The Profile is signed as a JSON Web Signature (JWS) in the compact
serialization of [RFC 7515][ref-rfc7515], the payload being the Profile. The
signing key is the Governance Profile key that
[Trust Authority's own keys][trust-authoritys-own-keys] names, held in Trust
Authority's HSM. The Profile names its key in `kid` as a `did:key`, as
[Naming the key][ts-01-naming-under-did-key] of TS-01 requires, and the key
is authorized by the Profile a reader already verified rather than by the
trusted list. The algorithm is fixed here, because the Profile cannot name
the algorithm it is verified with; changing it is a major version of this
specification.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-02-028 }**REQ-TS-02-028** The Profile MUST be published as a JWS in the compact serialization of [RFC 7515][ref-rfc7515], whose payload is the Profile.
- [](){ #req-ts-02-029 }**REQ-TS-02-029** Trust Authority MUST sign the Profile with a key that `signers` names at `granted`.
- [](){ #req-ts-02-030 }**REQ-TS-02-030** Trust Authority MUST hold the private key of the Governance Profile key in its HSM.
- [](){ #req-ts-02-031 }**REQ-TS-02-031** Trust Authority MUST NOT sign anything but the Profile with the Governance Profile key.
- [](){ #req-ts-02-032 }**REQ-TS-02-032** Trust Registry MUST NOT hold the private key.
- [](){ #req-ts-02-033 }**REQ-TS-02-033** The protected header MUST be exactly `alg` and `kid`.
- [](){ #req-ts-02-034 }**REQ-TS-02-034** `alg` MUST be `ES256`.
- [](){ #req-ts-02-035 }**REQ-TS-02-035** `kid` MUST name the signing key under `did:key`, as [Naming the key][ts-01-naming-under-did-key] of TS-01 requires and as `signers` names it.
- [](){ #req-ts-02-036 }**REQ-TS-02-036** Before a new key signs any edition, the key MUST have been named at `granted` in an edition signed with a key already accepted.

</div>

The protected header of the Profile above, and the compact serialization it
sits in. The payload is the base64url encoding of the JSON shown in
[Governance Profile payload][ts-02-governance-profile-payload], byte for
byte, and the signature is 64 bytes, the concatenation of `r` and `s`.

``` { .json title="governance-profile.json, the JWS protected header" data-format="JSON" }
{"alg":"ES256","kid":"did:key:zDnaeycT26AUYZiH8MKR7y8quFjayVbNJn9CCK4YoAhfJd9Ax"}
```

``` { .text title="governance-profile.json, the JWS compact serialization" data-format="JWS" }
eyJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDprZXk6ekRuYWV5Y1QyNkFVWVppSDhNS1I3eThxdUZqYX
lWYk5KbjlDQ0s0WW9BaGZKZDlBeCJ9.ewogICJwcm9maWxlX3ZlcnNpb24iOiAxLAogICJzZXF1ZW5
jZV9udW1iZXIiOiAzLAogICJpc3N1ZWRfYXQiOiAiMjAyNi0xMC0wMVQwMDowMDowMFoiLAogICJuZ
Xh0X3VwZGF0ZSI6ICIyMDI2LTEyLTMwVDAwOjAwOjAwWiIsCiAgInNpZ25lcnMiOiBbCiAgICB7CiA
gICAgICJrZXkiOiAiZGlkOmtleTp6RG5hZVNpZDZmalBjaHp1VTl0OFZ0V0M2RnNHZjV5TEdyRnpGb
lRpOXYyeVZYQ3hhIiwKICAgICAgInN0YXR1cyI6ICJncmFudGVkIiwKICAgICAgInNpbmNlIjogIjI
wMjYtMTAtMDFUMDA6MDA6MDBaIgogICAgfSwKICAgIHsKICAgICAgImtleSI6ICJkaWQ6a2V5OnpEb
mFleWNUMjZBVVlaaUg4TUtSN3k4cXVGamF5VmJOSm45Q0NLNFlvQWhmSmQ5QXgiLAogICAgICAic3R
hdHVzIjogImdyYW50ZWQiLAogICAgICAic2luY2UiOiAiMjAyNi0wNC0wMVQwMDowMDowMFoiCiAgI
CB9LAogICAgewogICAgICAia2V5IjogImRpZDprZXk6ekRuYWVqVUVXMzM1WGZvNFZiWU5Rb2FaUDl
mQnpMeHVieGpDQkNoVnJpaE5rZUI0dyIsCiAgICAgICJzdGF0dXMiOiAid2l0aGRyYXduIiwKICAgI
CAgInNpbmNlIjogIjIwMjYtMDctMDFUMDA6MDA6MDBaIgogICAgfQogIF0sCiAgInNwZWNpZmljYXR
pb25zIjogWwogICAgewogICAgICAiaWQiOiAiVFMtMDAiLAogICAgICAidmVyc2lvbnMiOiBbCiAgI
CAgICAgIjEuMCIKICAgICAgXQogICAgfSwKICAgIHsKICAgICAgImlkIjogIlRTLTAxIiwKICAgICA
gInZlcnNpb25zIjogWwogICAgICAgICIxLjAiCiAgICAgIF0KICAgIH0sCiAgICB7CiAgICAgICJpZ
CI6ICJUUy0wMiIsCiAgICAgICJ2ZXJzaW9ucyI6IFsKICAgICAgICAiMS4wIgogICAgICBdCiAgICB
9LAogICAgewogICAgICAiaWQiOiAiVFMtMS0wMSIsCiAgICAgICJ2ZXJzaW9ucyI6IFsKICAgICAgI
CAiMS4wIgogICAgICBdCiAgICB9LAogICAgewogICAgICAiaWQiOiAiVFMtMi0wMSIsCiAgICAgICJ
2ZXJzaW9ucyI6IFsKICAgICAgICAiMS4wIgogICAgICBdCiAgICB9LAogICAgewogICAgICAiaWQiO
iAiVFMtMy0wMSIsCiAgICAgICJ2ZXJzaW9ucyI6IFsKICAgICAgICAiMS4wIgogICAgICBdCiAgICB
9LAogICAgewogICAgICAiaWQiOiAiVFMtMy0wMiIsCiAgICAgICJ2ZXJzaW9ucyI6IFsKICAgICAgI
CAiMS4wIgogICAgICBdCiAgICB9LAogICAgewogICAgICAiaWQiOiAiVFMtNC0wMSIsCiAgICAgICJ
2ZXJzaW9ucyI6IFsKICAgICAgICAiMS4wIgogICAgICBdCiAgICB9LAogICAgewogICAgICAiaWQiO
iAiVFMtNC0wMiIsCiAgICAgICJ2ZXJzaW9ucyI6IFsKICAgICAgICAiMS4wIgogICAgICBdCiAgICB
9LAogICAgewogICAgICAiaWQiOiAiVFMtNC0wMyIsCiAgICAgICJ2ZXJzaW9ucyI6IFsKICAgICAgI
CAiMS4wIgogICAgICBdCiAgICB9LAogICAgewogICAgICAiaWQiOiAiVFMtNS0wMSIsCiAgICAgICJ
2ZXJzaW9ucyI6IFsKICAgICAgICAiMS4wIiwKICAgICAgICAiMi4wIgogICAgICBdLAogICAgICAid
HJhbnNpdGlvbl9lbmRzIjogIjIwMjctMDMtMzFUMDA6MDA6MDBaIgogICAgfSwKICAgIHsKICAgICA
gImlkIjogIlRTLTUtMDIiLAogICAgICAidmVyc2lvbnMiOiBbCiAgICAgICAgIjEuMCIKICAgICAgX
QogICAgfSwKICAgIHsKICAgICAgImlkIjogIlRTLTUtMDMiLAogICAgICAidmVyc2lvbnMiOiBbCiA
gICAgICAgIjEuMCIKICAgICAgXQogICAgfSwKICAgIHsKICAgICAgImlkIjogIlRTLTUtMDQiLAogI
CAgICAidmVyc2lvbnMiOiBbCiAgICAgICAgIjEuMCIKICAgICAgXQogICAgfSwKICAgIHsKICAgICA
gImlkIjogIlRTLTUtMDUiLAogICAgICAidmVyc2lvbnMiOiBbCiAgICAgICAgIjEuMCIKICAgICAgX
QogICAgfSwKICAgIHsKICAgICAgImlkIjogIlRTLTUtMDYiLAogICAgICAidmVyc2lvbnMiOiBbCiA
gICAgICAgIjEuMCIKICAgICAgXQogICAgfSwKICAgIHsKICAgICAgImlkIjogIlRTLTUtMDciLAogI
CAgICAidmVyc2lvbnMiOiBbCiAgICAgICAgIjEuMCIKICAgICAgXQogICAgfSwKICAgIHsKICAgICA
gImlkIjogIlRTLTUtMDgiLAogICAgICAidmVyc2lvbnMiOiBbCiAgICAgICAgIjEuMCIKICAgICAgX
QogICAgfSwKICAgIHsKICAgICAgImlkIjogIlRTLTUtMDkiLAogICAgICAidmVyc2lvbnMiOiBbCiA
gICAgICAgIjEuMCIKICAgICAgXQogICAgfSwKICAgIHsKICAgICAgImlkIjogIlRTLTUtMTAiLAogI
CAgICAidmVyc2lvbnMiOiBbCiAgICAgICAgIjEuMCIKICAgICAgXQogICAgfSwKICAgIHsKICAgICA
gImlkIjogIlRTLTUtMTEiLAogICAgICAidmVyc2lvbnMiOiBbCiAgICAgICAgIjEuMCIKICAgICAgX
QogICAgfQogIF0sCiAgInN0YW5kYXJkcyI6IHsKICAgICJESUQtS2V5IjogIjAuOSIsCiAgICAiREl
ELVdlYlZIIjogIjEuMCIsCiAgICAiRVRTSS5UUy4xMTk2MDIiOiAiVjEuMS4xIiwKICAgICJJLUQua
WV0Zi1vYXV0aC1zZC1qd3QtdmMiOiAiMTMiLAogICAgIkktRC5pZXRmLW9hdXRoLXN0YXR1cy1saXN
0IjogIjE0IiwKICAgICJJU08uMTgwMTMtNSI6ICIyMDIxIiwKICAgICJPcGVuSUQ0VkNJIjogIjEuM
CIsCiAgICAiT3BlbklENFZQIjogIjEuMCIsCiAgICAiVFJRUCI6ICIyLjAiCiAgfSwKICAiYWRkcmV
zc2VzIjogewogICAgInRydXN0X3JlZ2lzdHJ5IjogImh0dHBzOi8vcXVlcnkudHJ1c3QuZ28uaWQiL
AogICAgImNhdGFsb2ciOiAiaHR0cHM6Ly9jYXRhbG9nLnRydXN0LmdvLmlkIiwKICAgICJ0cnVzdGV
kX2xpc3QiOiBbCiAgICAgICJodHRwczovL3JlZ2lzdHJ5LnRydXN0LmdvLmlkL3RydXN0ZWQtbGlzd
C5qc29uIgogICAgXSwKICAgICJzdGF0dXNfbGlzdF9ob3N0IjogImh0dHBzOi8vcmVnaXN0cnkudHJ
1c3QuZ28uaWQiLAogICAgImRpZF9yZXNvbHZlciI6ICJodHRwczovL2RpZC50cnVzdC5nby5pZCIsC
iAgICAiZW50aXR5X2VuZHBvaW50IjogImh0dHBzOi8vZW50aXRpZXMudHJ1c3QuZ28uaWQiLAogICA
gInBvcnRhbCI6ICJodHRwczovL3BvcnRhbC50cnVzdC5nby5pZCIKICB9LAogICJhbGdvcml0aG1zI
jogewogICAgInRydXN0ZWRfbGlzdCI6IFsKICAgICAgIkVTMjU2IgogICAgXSwKICAgICJyZWNvZ25
pdGlvbl9hbnN3ZXIiOiBbCiAgICAgICJFUzI1NiIKICAgIF0sCiAgICAiY2F0YWxvZyI6IFsKICAgI
CAgIkVTMjU2IgogICAgXSwKICAgICJhdXRob3JpdHlfc3RhdGVtZW50IjogWwogICAgICAiRVMyNTY
iCiAgICBdLAogICAgInVzZV9zdGF0ZW1lbnQiOiBbCiAgICAgICJFUzI1NiIKICAgIF0sCiAgICAiY
WNjcmVkaXRhdGlvbl9jcmVkZW50aWFsIjogWwogICAgICAiRVMyNTYiCiAgICBdLAogICAgImtleV9
hdHRlc3RhdGlvbiI6IFsKICAgICAgIkVTMjU2IgogICAgXSwKICAgICJzdGF0dXNfbGlzdCI6IFsKI
CAgICAgIkVTMjU2IgogICAgXSwKICAgICJpc3N1YW5jZSI6IHsKICAgICAgImRjK3NkLWp3dCI6IFs
KICAgICAgICAiRVMyNTYiCiAgICAgIF0sCiAgICAgICJtc29fbWRvYyI6IFsKICAgICAgICAtNwogI
CAgICBdLAogICAgICAibGRwX3ZjIjogWwogICAgICAgICJlY2RzYS1yZGZjLTIwMTkiCiAgICAgIF0
KICAgIH0sCiAgICAiY3JlZGVudGlhbF9rZXkiOiBbCiAgICAgICJFUzI1NiIKICAgIF0sCiAgICAiZ
HBvcCI6IFsKICAgICAgIkVTMjU2IgogICAgXSwKICAgICJyZXF1ZXN0X29iamVjdCI6IFsKICAgICA
gIkVTMjU2IgogICAgXQogIH0sCiAgImxpZmV0aW1lcyI6IHsKICAgICJhdXRob3JpdHlfc3RhdGVtZ
W50IjogIlBUMTJIIiwKICAgICJyZWNvZ25pdGlvbl9hbnN3ZXIiOiAiUFQxMkgiLAogICAgImNhdGF
sb2ciOiAiUDFEIiwKICAgICJzdGF0dXNfbGlzdF90dGwiOiB7CiAgICAgICJjcmVkZW50aWFsIjogI
lBUMTJIIiwKICAgICAgInVzZV9zdGF0ZW1lbnQiOiAiUFQxMkgiLAogICAgICAiYWNjcmVkaXRhdGl
vbiI6ICJQVDEySCIKICAgIH0sCiAgICAiY3JlZGVudGlhbF9zdXNwZW5zaW9uIjogIlAzMEQiLAogI
CAgInVzZV9zdGF0ZW1lbnQiOiAiUDFZIiwKICAgICJ0cnVzdGVkX2xpc3RfaG9yaXpvbiI6ICJQN0Q
iLAogICAgInZlcmlmaWVyX2RldmljZV9jZXJ0aWZpY2F0ZSI6ICJQNzMwRCIsCiAgICAidmVyaWZpZ
XJfaXNzdWluZ19jYSI6ICJQNVkiLAogICAgImFjY3JlZGl0YXRpb25fcGVyaW9kIjogIlAyWSIsCiA
gICAiZW50aXR5X2VuZHBvaW50X25vbmNlIjogIlBUNU0iLAogICAgInJlZ2lzdHJhdGlvbl9jb2RlI
jogIlAxNEQiLAogICAgImVucm9sbG1lbnRfY2hhbGxlbmdlIjogIlBUNU0iLAogICAgInByZV9hdXR
ob3JpemVkX2NvZGUiOiAiUFQxME0iLAogICAgInBhcl9yZXF1ZXN0X3VyaSI6ICJQVDFNIiwKICAgI
CJhdXRob3JpemF0aW9uX2NvZGUiOiAiUFQxTSIsCiAgICAiYWNjZXNzX3Rva2VuIjogIlBUNU0iLAo
gICAgInJlZnJlc2hfdG9rZW5faW5hY3Rpdml0eSI6ICJQOTBEIiwKICAgICJkcG9wX25vbmNlIjogI
lBUNU0iLAogICAgImNfbm9uY2UiOiAiUFQ1TSIsCiAgICAiZGVmZXJyZWRfcmVxdWVzdCI6ICJQMUQ
iLAogICAgInJlcXVlc3Rfb2JqZWN0IjogIlBUNU0iLAogICAgInJlbGF5ZWRfcmVzcG9uc2UiOiAiU
FQxME0iLAogICAgInJlbGF5X3JlY29yZCI6ICJQOTBEIiwKICAgICJjb25zZW50X3JlY2VpcHQiOiA
iUDFZIiwKICAgICJwcmVzZW50YXRpb25faGlzdG9yeSI6ICJQMVkiLAogICAgImRpc3B1dGVfcGVya
W9kIjogIlA1WSIsCiAgICAicmVnaXN0cmF0aW9uX3N1c3BlbnNpb24iOiAiUDkwRCIKICB9LAogICJ
yb290cyI6IHsKICAgICJpc3N1ZXJfcm9vdF9jYSI6IHsKICAgICAgImxvbmdlc3RfY2VydGlmaWNhd
GUiOiAiUDEwWSIsCiAgICAgICJzaWduaW5nX3BlcmlvZCI6ICJQM1kiLAogICAgICAibGVhZF90aW1
lIjogIlAyWSIKICAgIH0sCiAgICAidmVyaWZpZXJfcm9vdF9jYSI6IHsKICAgICAgImxvbmdlc3RfY
2VydGlmaWNhdGUiOiAiUDVZIiwKICAgICAgInNpZ25pbmdfcGVyaW9kIjogIlA4WSIsCiAgICAgICJ
sZWFkX3RpbWUiOiAiUDJZIgogICAgfQogIH0sCiAgImNyZWRlbnRpYWxfdHlwZXMiOiB7CiAgICAia
WQuaWRjdGYua3RwLjEiOiB7CiAgICAgICJ2YWxpZGl0eV9jZWlsaW5nIjogIlA5MEQiCiAgICB9LAo
gICAgImlkLmlkY3RmLmthcnR1LWluZG9uZXNpYS1zZWhhdC4xIjogewogICAgICAidmFsaWRpdHlfY
2VpbGluZyI6ICJQMVkiCiAgICB9LAogICAgImlkLmlkY3RmLmthcnR1LWFzbi4xIjogewogICAgICA
idmFsaWRpdHlfY2VpbGluZyI6ICJQMVkiCiAgICB9LAogICAgImlkLmlkY3RmLmthcnR1LW5pa2FoL
jEiOiB7CiAgICAgICJ2YWxpZGl0eV9jZWlsaW5nIjogIlAxWSIKICAgIH0sCiAgICAib3JnLmlzby4
xODAxMy41LjEubURMLjEiOiB7CiAgICAgICJ2YWxpZGl0eV9jZWlsaW5nIjogIlA5MEQiCiAgICB9C
iAgfSwKICAidG9sZXJhbmNlcyI6IHsKICAgICJyZWNvZ25pdGlvbl9hbnN3ZXIiOiAiUDFEIiwKICA
gICJjYXRhbG9nIjogIlA3RCIsCiAgICAiYXV0aG9yaXR5X3N0YXRlbWVudCI6ICJQMUQiLAogICAgI
mRpZF93ZWJ2aF9sb2ciOiAiUDdEIiwKICAgICJzdGF0dXNfbGlzdCI6ICJQM0QiLAogICAgInVzZV9
zdGF0ZW1lbnRfc3RhdHVzX2xpc3QiOiAiUDNEIiwKICAgICJjcmwiOiAiUDdEIiwKICAgICJ2aWNhb
CI6ICJQN0QiCiAgfSwKICAiaW50ZXJ2YWxzIjogewogICAgInRydXN0X2NhY2hlX3N5bmMiOiB7CiA
gICAgICJldmVyeSI6ICJQVDZIIiwKICAgICAgImppdHRlciI6ICJQVDMwTSIKICAgIH0sCiAgICAic
3RhdHVzX2xpc3RfcmVwdWJsaWNhdGlvbiI6ICJQVDEySCIsCiAgICAic3RhdHVzX2xpc3RfY2hhbmd
lIjogIlBUMUgiLAogICAgImFjY3JlZGl0YXRpb25fc3RhdHVzX2NoYW5nZSI6ICJQVDFIIiwKICAgI
CJjcmxfcHVibGljYXRpb24iOiAiUDFEIiwKICAgICJ2aWNhbF9wdWJsaWNhdGlvbiI6ICJQMUQiLAo
gICAgImRzY19leHBpcnlfd2FybmluZyI6ICJQOTBEIiwKICAgICJjcmVkZW50aWFsX3JlbmV3YWxfb
GVhZCI6ICJQMzBEIiwKICAgICJhY2NyZWRpdGF0aW9uX3JlbmV3YWxfbGVhZCI6ICJQOTBEIiwKICA
gICJtZXJjaGFudF93aXRoZHJhd2FsIjogIlAxRCIsCiAgICAicmVnaXN0cmF0aW9uX2NoYW5nZV9ub
3RpY2UiOiAiUDdEIiwKICAgICJsb3NzX3JlcG9ydF9hY3Rpb24iOiAiUFQyNEgiLAogICAgImxpY2V
uc2VfY2hhbmdlX3JlcG9ydCI6ICJQMTREIiwKICAgICJjb3JyZWN0aW9uX3BlcmlvZCI6ICJQMzBEI
iwKICAgICJpbmNpZGVudF9yZXBvcnQiOiAiUFQyNEgiLAogICAgInBvc3RfbW9ydGVtIjogIlAzMEQ
iLAogICAgImFtZW5kbWVudF9ub3RpY2UiOiAiUDkwRCIKICB9LAogICJyb3RhdGlvbiI6IHsKICAgI
CJpc3N1YW5jZS1qb3NlIjogewogICAgICAiaW50ZXJ2YWwiOiAiUDFZIiwKICAgICAgIm92ZXJsYXA
iOiAiUDYwRCIKICAgIH0sCiAgICAiaXNzdWFuY2UtY29zZSI6IHsKICAgICAgImludGVydmFsIjogI
lAxWSIsCiAgICAgICJvdmVybGFwIjogIlA2MEQiCiAgICB9LAogICAgInJlcXVlc3Qtb2JqZWN0Ijo
gewogICAgICAiaW50ZXJ2YWwiOiAiUDFZIiwKICAgICAgIm92ZXJsYXAiOiAiUDYwRCIKICAgIH0sC
iAgICAidmVyaWZpZXItaXNzdWluZy1jYSI6IHsKICAgICAgImludGVydmFsIjogIlAzWSIsCiAgICA
gICJvdmVybGFwIjogIlA5MEQiCiAgICB9LAogICAgImtleS1hdHRlc3RhdGlvbiI6IHsKICAgICAgI
mludGVydmFsIjogIlAxWSIsCiAgICAgICJvdmVybGFwIjogIlA2MEQiCiAgICB9LAogICAgInVwZGF
0ZSI6IHsKICAgICAgImludGVydmFsIjogIlAyWSIKICAgIH0sCiAgICAicmV0aXJlZF9wcml2YXRlX
2tleSI6ICJkZXN0cm95IiwKICAgICJ0cnVzdF9hdXRob3JpdHkiOiB7CiAgICAgICJ0cnVzdGVkLWx
pc3QiOiB7CiAgICAgICAgImludGVydmFsIjogIlAyWSIsCiAgICAgICAgImxlYWRfdGltZSI6ICJQO
TBEIgogICAgICB9LAogICAgICAidmljYWwiOiB7CiAgICAgICAgImludGVydmFsIjogIlAyWSIsCiA
gICAgICAgImxlYWRfdGltZSI6ICJQOTBEIgogICAgICB9LAogICAgICAiZ292ZXJuYW5jZS1wcm9ma
WxlIjogewogICAgICAgICJpbnRlcnZhbCI6ICJQMlkiLAogICAgICAgICJsZWFkX3RpbWUiOiAiUDk
wRCIKICAgICAgfSwKICAgICAgImFjY3JlZGl0YXRpb24tY3JlZGVudGlhbCI6IHsKICAgICAgICAia
W50ZXJ2YWwiOiAiUDJZIgogICAgICB9LAogICAgICAiYWNjcmVkaXRhdGlvbi1zdGF0dXMtbGlzdCI
6IHsKICAgICAgICAiaW50ZXJ2YWwiOiAiUDJZIgogICAgICB9LAogICAgICAidXNlLXN0YXRlbWVud
CI6IHsKICAgICAgICAiaW50ZXJ2YWwiOiAiUDJZIgogICAgICB9LAogICAgICAidXNlLXN0YXRlbWV
udC1zdGF0dXMtbGlzdCI6IHsKICAgICAgICAiaW50ZXJ2YWwiOiAiUDJZIgogICAgICB9LAogICAgI
CAiYXV0aG9yaXR5LXN0YXRlbWVudCI6IHsKICAgICAgICAiaW50ZXJ2YWwiOiAiUDJZIgogICAgICB
9LAogICAgICAicmVjb2duaXRpb24tc3RhdGVtZW50IjogewogICAgICAgICJpbnRlcnZhbCI6ICJQM
lkiCiAgICAgIH0sCiAgICAgICJjYXRhbG9nIjogewogICAgICAgICJpbnRlcnZhbCI6ICJQMlkiCiA
gICAgIH0sCiAgICAgICJ1cGRhdGUiOiB7CiAgICAgICAgImludGVydmFsIjogIlAyWSIKICAgICAgf
SwKICAgICAgIndpdG5lc3MiOiB7CiAgICAgICAgImludGVydmFsIjogIlAyWSIKICAgICAgfQogICA
gfQogIH0sCiAgImxpbWl0cyI6IHsKICAgICJxdWVyeV9yYXRlIjogewogICAgICAicmVxdWVzdHMiO
iA2MDAsCiAgICAgICJwZXIiOiAiUFQxTSIKICAgIH0sCiAgICAiZW50aXR5X2VuZHBvaW50X3JhdGU
iOiB7CiAgICAgICJyZXF1ZXN0cyI6IDYwLAogICAgICAicGVyIjogIlBUMU0iCiAgICB9LAogICAgI
nBvcnRhbF9yYXRlIjogewogICAgICAicmVxdWVzdHMiOiAxMjAsCiAgICAgICJwZXIiOiAiUFQxTSI
KICAgIH0sCiAgICAicG9ydGFsX2ZhaWxlZF9zaWduX2lucyI6IDEwLAogICAgInVzZV9zdGF0ZW1lb
nRfY3V0X29mZiI6ICIyMDI2LTEwLTAxVDAwOjAwOjAwWiIsCiAgICAia2V5X2F0dGVzdGF0aW9uX2N
sb2NrX3NrZXciOiAiUFQxTSIsCiAgICAidHJhbnNhY3Rpb25fY29kZV9hdHRlbXB0cyI6IDMsCiAgI
CAiZGlkX3NlcnZpY2VfYXZhaWxhYmlsaXR5IjogewogICAgICAic2hhcmUiOiAwLjk5NSwKICAgICA
gIndpbmRvdyI6ICJQOTBEIgogICAgfSwKICAgICJkaWRfc2VydmljZV9yZWNvdmVyeSI6ICJQVDRII
iwKICAgICJpbnRlZ3JpdHlfdmVyZGljdF93aW5kb3ciOiAiUFQ1TSIKICB9LAogICJsaXN0cyI6IHs
KICAgICJhdXRob3JpemF0aW9uX2FjdGlvbnMiOiBbCiAgICAgICJpc3N1ZSIsCiAgICAgICJyZXF1Z
XN0IgogICAgXSwKICAgICJyZWNvZ25pdGlvbl9hY3Rpb25zIjogWwogICAgICAiaXNzdWUiCiAgICB
dLAogICAgImtleV9zdG9yYWdlX3Jvb3RzIjogewogICAgICAiaHNtIjogWwogICAgICAgICJNSUlCM
WpDQ0FYdWdBd0lCQWdJRVN4MEFBVEFLQmdncWhrak9QUVFEQWpCUE1Rc3dDUVlEVlFRR0V3SkpSREV
qTUNFR0ExVUVDZ3dhVUZRZ1EyOXVkRzlvSUZCbGNtRnVaMnRoZENCTGNtbHdkRzh4R3pBWkJnTlZCQ
U1NRWtOdmJuUnZhQ0JJVTAwZ1VtOXZkQ0JEUVRBZUZ3MHlOREF4TURFd01EQXdNREJhRncwME5EQXh
NREV3TURBd01EQmFNRTh4Q3pBSkJnTlZCQVlUQWtsRU1TTXdJUVlEVlFRS0RCcFFWQ0JEYjI1MGIyZ
2dVR1Z5WVc1bmEyRjBJRXR5YVhCMGJ6RWJNQmtHQTFVRUF3d1NRMjl1ZEc5b0lFaFRUU0JTYjI5MEl
FTkJNRmt3RXdZSEtvWkl6ajBDQVFZSUtvWkl6ajBEQVFjRFFnQUVSai05Y3ZyTjFpU19OMEZnWGtDY
jJKQVd5VWlvYTdMQlppQkpyN0k5U2FIV3lscDVvUEt3TDAzUGVrbjJQUlJhT0NaVHFsQTltOFdhWEN
0ZDFqUDVwNk5GTUVNd0VnWURWUjBUQVFIX0JBZ3dCZ0VCX3dJQkFEQU9CZ05WSFE4QkFmOEVCQU1DQ
WdRd0hRWURWUjBPQkJZRUZLYzdGaUZVems5LTc0RUg3RnZzUkxMR2l1aGhNQW9HQ0NxR1NNNDlCQU1
DQTBrQU1FWUNJUURKODd3Q1N4VHFDdUVSUU9fSGhCQUFvUmtkaDY2ZEFvVzZlRk5MWVJTelFnSWhBT
zV0bUtjdXdaX3hINWlzVDJMVVRWa25QMUo4Z0VmNUp2My1MWUtoNkt5RiIKICAgICAgXSwKICAgICA
gImNsb3Vka21zIjogW10KICAgIH0sCiAgICAicG9ydGFsX3NlY29uZF9mYWN0b3JzIjogWwogICAgI
CAid2ViYXV0aG4iLAogICAgICAidG90cCIKICAgIF0sCiAgICAicmVjb2duaXplZF9ldmFsdWF0aW9
uX3NjaGVtZXMiOiBbCiAgICAgICJldWNjIiwKICAgICAgInNvZ2lzIiwKICAgICAgImlkLWJzc24iC
iAgICBdLAogICAgImFuZHJvaWRfZGV2aWNlX3JlY29nbml0aW9uX3ZlcmRpY3QiOiBbCiAgICAgIHs
KICAgICAgICAiZnJvbV92ZXJzaW9uIjogMTMsCiAgICAgICAgInJlcXVpcmVzIjogIk1FRVRTX1NUU
k9OR19JTlRFR1JJVFkiCiAgICAgIH0sCiAgICAgIHsKICAgICAgICAiZnJvbV92ZXJzaW9uIjogMTA
sCiAgICAgICAgInJlcXVpcmVzIjogIk1FRVRTX0RFVklDRV9JTlRFR1JJVFkiCiAgICAgIH0KICAgI
F0sCiAgICAiYXR0ZXN0YXRpb25fcm9vdF9yZWZ1c2FsIjogWwogICAgICB7CiAgICAgICAgInJvb3Q
iOiAiQ0VEQjFDQjZEQzg5NkFFNUVDNzk3MzQ4QkNFOTI4Njc1M0MyQjM4RUU3MUNFMEZCRTM0QTlBM
TI0ODgwMERGQyIsCiAgICAgICAgImZyb20iOiAiMjAzNi0wMS0wMVQwMDowMDowMFoiCiAgICAgIH0
KICAgIF0KICB9LAogICJtYXBwaW5ncyI6IHsKICAgICJtaW5fYXNzdXJhbmNlIjogewogICAgICAia
GlnaCI6IHsKICAgICAgICAia2V5X3N0b3JhZ2UiOiBbCiAgICAgICAgICAiaXNvXzE4MDQ1X2hpZ2g
iCiAgICAgICAgXSwKICAgICAgICAidXNlcl9hdXRoZW50aWNhdGlvbiI6IFsKICAgICAgICAgICJpc
29fMTgwNDVfbW9kZXJhdGUiLAogICAgICAgICAgImlzb18xODA0NV9oaWdoIgogICAgICAgIF0sCiA
gICAgICAgInByb29mX3R5cGVzIjogWwogICAgICAgICAgImF0dGVzdGF0aW9uIgogICAgICAgIF0KI
CAgICAgfSwKICAgICAgInN1YnN0YW50aWFsIjogewogICAgICAgICJrZXlfc3RvcmFnZSI6IFsKICA
gICAgICAgICJpc29fMTgwNDVfbW9kZXJhdGUiLAogICAgICAgICAgImlzb18xODA0NV9oaWdoIgogI
CAgICAgIF0sCiAgICAgICAgInVzZXJfYXV0aGVudGljYXRpb24iOiBbCiAgICAgICAgICAiaXNvXzE
4MDQ1X21vZGVyYXRlIiwKICAgICAgICAgICJpc29fMTgwNDVfaGlnaCIKICAgICAgICBdLAogICAgI
CAgICJwcm9vZl90eXBlcyI6IFsKICAgICAgICAgICJhdHRlc3RhdGlvbiIsCiAgICAgICAgICAiand
0IgogICAgICAgIF0KICAgICAgfSwKICAgICAgImxvdyI6IHsKICAgICAgICAia2V5X3N0b3JhZ2UiO
iBbCiAgICAgICAgICAiaXNvXzE4MDQ1X2VuaGFuY2VkLWJhc2ljIiwKICAgICAgICAgICJpc29fMTg
wNDVfbW9kZXJhdGUiLAogICAgICAgICAgImlzb18xODA0NV9oaWdoIgogICAgICAgIF0sCiAgICAgI
CAgInVzZXJfYXV0aGVudGljYXRpb24iOiBbCiAgICAgICAgICAiaXNvXzE4MDQ1X2VuaGFuY2VkLWJ
hc2ljIiwKICAgICAgICAgICJpc29fMTgwNDVfbW9kZXJhdGUiLAogICAgICAgICAgImlzb18xODA0N
V9oaWdoIgogICAgICAgIF0sCiAgICAgICAgInByb29mX3R5cGVzIjogWwogICAgICAgICAgImF0dGV
zdGF0aW9uIiwKICAgICAgICAgICJqd3QiCiAgICAgICAgXQogICAgICB9CiAgICB9LAogICAgImlzc
3Vlcl9hc3N1cmFuY2UiOiB7CiAgICAgICJzb2Z0d2FyZSI6ICJsb3ciLAogICAgICAiY2xvdWRrbXM
iOiAic3Vic3RhbnRpYWwiLAogICAgICAiaHNtIjogImhpZ2giCiAgICB9CiAgfSwKICAia2V5X3N0b
3JhZ2UiOiB7CiAgICAidmVyaWZpZXItaXNzdWluZy1jYSI6IFsKICAgICAgImNsb3Vka21zIiwKICA
gICAgImhzbSIKICAgIF0KICB9LAogICJwZXJtaXNzaW9ucyI6IHsKICAgICJkc2NfcGVyX2dyb3VwX
29mX3R5cGVzIjogZmFsc2UKICB9Cn0.fzuvq_duxkZ3oJuvsc4zkbCc1ESD39xEX4N0SmYXkNA1u2I
z0HdsZDzhWYkZwrC4fOH-Pc-QN07KvRb61PTi4g
```

## Publication {#ts-02-publication}

An edition reaches a reader in four steps, each on the trust path.

1. Trust Registry builds the edition from the values the Root Authority
   approved.
2. Trust Authority signs it with the Governance Profile key, using its
   Certificate Authority Component, and returns the JWS.
3. Trust Registry serves the JWS at the address below, using its Object
   Storage Provider Component.
4. Every reader fetches it on its next trust cache sync, never on demand.

The address is `https://idctf.id/governance-profile`. It is the one address a
reader is built with, and it lies outside `https://idctf.id/ns/`, because
everything under that root is an identifier no reader fetches, as
[The scheme identifiers][ts-5-01-the-scheme-identifiers] fixes. Moving the
address is a major version of this specification, with the transition period
that version names.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-02-037 }**REQ-TS-02-037** Trust Registry MUST serve the current edition at `https://idctf.id/governance-profile`, over HTTP with Transport Layer Security (TLS), as a static file.
- [](){ #req-ts-02-038 }**REQ-TS-02-038** Trust Registry MUST serve the edition with the media type `application/jose`.
- [](){ #req-ts-02-039 }**REQ-TS-02-039** Trust Registry MUST serve the edition without authentication.
- [](){ #req-ts-02-040 }**REQ-TS-02-040** Trust Registry MUST NOT require any identifier of the reader.
- [](){ #req-ts-02-041 }**REQ-TS-02-041** Trust Registry MUST publish a new edition before the `next_update` of the current one.
- [](){ #req-ts-02-042 }**REQ-TS-02-042** Trust Registry MAY publish a new edition at any time before the `next_update` of the current one.
- [](){ #req-ts-02-043 }**REQ-TS-02-043** Trust Registry MUST keep every edition it published.

</div>

An edition published early is the ordinary edition with the next sequence
number. Nothing marks it, and a reader takes it on its next sync like any
other.

## Reading the copy {#ts-02-reading-the-copy}

A reader works from one copy, filled on the sync and read wherever a
specification defers to the Profile.

1. On the sync, the reader fetches the edition, verifies the JWS, checks
   the sequence number against the copy it holds, and stores the new copy.
2. On a read, it verifies the JWS of the copy again, checks that the copy
   is within its tolerance, and takes the member it needs.
3. It never asks Trust Registry for a single value.

A copy counts until `next_update` plus seven days. The grace is there because
a late edition would otherwise stop every Module in the ecosystem at once;
the values in it change by plan, so a week of an old edition costs little,
while a reader with no edition can check nothing.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-02-044 }**REQ-TS-02-044** A reader MUST fetch the Profile only from `https://idctf.id/governance-profile`.
- [](){ #req-ts-02-045 }**REQ-TS-02-045** A reader MUST refresh its copy outside any transaction, through the trust cache sync.
- [](){ #req-ts-02-046 }**REQ-TS-02-046** A reader MUST NOT fetch the Profile during a transaction.
- [](){ #req-ts-02-047 }**REQ-TS-02-047** A reader MUST verify the JWS of its copy every time it reads the copy, not only when it fetched it.
- [](){ #req-ts-02-048 }**REQ-TS-02-048** *Withdrawn: [REQ-TS-01-024][req-ts-01-024] covers it.*
- [](){ #req-ts-02-049 }**REQ-TS-02-049** A reader MUST accept a signature only from the Governance Profile key it carries from build time, or from a key that an edition it already verified named in `signers` at `granted`.
- [](){ #req-ts-02-050 }**REQ-TS-02-050** A reader MUST refuse an edition signed with a key that an edition it already verified names at `withdrawn`, when the edition was issued at or after that key's `since`.
- [](){ #req-ts-02-051 }**REQ-TS-02-051** A reader MUST refuse an edition whose `alg` is not `ES256`.
- [](){ #req-ts-02-052 }**REQ-TS-02-052** A reader MUST refuse an edition whose `profile_version` is not a major version of this specification it implements.
- [](){ #req-ts-02-053 }**REQ-TS-02-053** A reader MUST refuse an edition whose `sequence_number` is lower than that of the copy it holds.
- [](){ #req-ts-02-054 }**REQ-TS-02-054** A reader MUST refuse an edition that lacks a member this specification defines, or carries one with another type.
- [](){ #req-ts-02-055 }**REQ-TS-02-055** A reader MUST ignore a member it does not know.
- [](){ #req-ts-02-056 }**REQ-TS-02-056** A reader MUST stop using its copy once `next_update` plus seven days has passed.
- [](){ #req-ts-02-057 }**REQ-TS-02-057** A reader that holds no copy it may use MUST refuse every exchange that depends on a value the Profile holds.
- [](){ #req-ts-02-058 }**REQ-TS-02-058** A reader MUST NOT send any identifier of a holder, a device, or a transaction when it fetches the Profile.

</div>

A reader that holds no copy it may use refuses rather than guesses, because
every check it runs rests on a value it would have to invent: an algorithm,
an address, a lifetime.

## Security considerations {#ts-02-security-considerations}

Each threat below is answered by the requirement named with it.

- **A forged Profile that sends readers elsewhere.** An edition is accepted
  only under a key the reader was built with or a verified edition
  announced, [REQ-TS-02-049][req-ts-02-049], so whoever holds the domain or
  the wire can withhold an edition but cannot write one.
- **Substitution of an old edition.** The sequence number,
  [REQ-TS-02-053][req-ts-02-053], refuses an edition older than the copy,
  and the tolerance, [REQ-TS-02-056][req-ts-02-056], bounds how long a
  withheld update keeps a reader on an old one.
- **A stolen signing key.** The key signs nothing else,
  [REQ-TS-02-031][req-ts-02-031], so a stolen key of another kind cannot
  forge a Profile; containment is to withdraw the key in the next edition,
  [REQ-TS-02-016][req-ts-02-016], after which a reader refuses what it signs,
  [REQ-TS-02-050][req-ts-02-050].
- **A poisoned cache.** The signature is checked at every read,
  [REQ-TS-02-047][req-ts-02-047].
- **A weakened algorithm list.** An algorithm the Profile allows still has
  to be one the artifact's specification admits,
  [REQ-TS-02-023][req-ts-02-023], so an edition can narrow what a
  specification admits and never widen it.

## Privacy considerations {#ts-02-privacy-considerations}

The Profile carries no citizen data. It is fetched whole, without
authentication and without any identifier of the reader,
[REQ-TS-02-039][req-ts-02-039], [REQ-TS-02-040][req-ts-02-040] and
[REQ-TS-02-058][req-ts-02-058], on the sync rather than during a
transaction, [REQ-TS-02-045][req-ts-02-045] and
[REQ-TS-02-046][req-ts-02-046], so that its fetch reveals nothing about which
citizen dealt with which party.

## Changelog {#ts-02-changelog}

<figure markdown="1" class="ekdn-table">

| Version | Date | Change |
|---|---|---|
| 1.0 draft | 19 October 2026 | First draft |

</figure>
