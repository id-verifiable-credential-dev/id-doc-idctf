---
title: "[TS-5-01] Publishing and reading the trusted list"
description: The profile of ETSI TS 119 602 the trusted list is published in, what each entry carries, how the list is signed and published, and how a reader checks its cached copy.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, Kep. 7, §2.2, §2.4, §5.4, §5.7, §7.7, §8.7; Rincian Module dan Operasi §2.1, §2.3, §2.5, §7.4; tracks/0158, tracks/0177, tracks/0236 -->

<p class="ekdn-docid">TS-5-01</p>

# Publishing and reading the trusted list {#ts-5-01-publishing-and-reading-the-trusted-list}

<p class="ekdn-lead" markdown="span">
The roll of accredited entities, as a List of Trusted Entities (LoTE) under
ETSI TS 119 602 V1.1.1.
</p>

Every sentence on this page binds Trust Registry and every Module that
reads the trusted list, and an Assessment Body tests them against it in the
version the Governance Profile puts in force. The key words and the
identifier `REQ-TS-5-01-nnn` follow [Common provisions](common-provisions.md).

## Who runs this and what it needs {#ts-5-01-who-runs-this-and-what-it-needs}

This specification is a LoTE profile in the sense of
[ETSI TS 119 602][ref-etsi-ts-119602] clause 4.7: a set of constraints on
the elements of a List of Trusted Entities, fixed by the scheme that
publishes it. It fixes the binding, the value or presence of every scheme
element, what an entry carries for one accredited registration, the
identifiers of the roles and statuses, the signature, the publication, and
the rules a reader applies to its cached copy.

Its conformance targets are:

- Trust Registry, which publishes the list.
- The four Modules that read it: Issuer Core, Verifier Core, Mobile Wallet,
  and Mobile Verifier.
- A Relying Party's own application built on Reader SDK, which reads the
  list on the same terms as Mobile Verifier when it verifies in proximity.

A reader meets its requirements through Trust SDK where the
library performs the check, and otherwise by its own means.

It leaves to other documents:

- [Who is accredited, suspended, or withdrawn and on what grounds][gf-grounds],
  which the Governance Framework holds.
- The longest interval between issue and `NextUpdate`, the sync timer, and
  the signature algorithms allowed, which the Governance Profile holds.
- The Verified Issuer Certificate Authority List (VICAL) and the
  certificates, which
  [Issuing and validating the X.509 certificates and the VICAL](issuing-and-validating-the-x509-certificates-and-the-vical.md)
  holds.
- The Authority Statement, which
  [Answering with an Authority Statement](answering-with-an-authority-statement.md)
  holds.
- The Decentralized Identifier (DID) Document, which
  [Publishing and resolving a did:webvh identifier](publishing-and-resolving-a-did-webvh-identifier.md)
  holds.

One rule of the standard is not followed: the trusted list is signed as a
plain JSON Web Signature (JWS) rather than as the JSON Advanced Electronic
Signature ([JAdES, ETSI TS 119 182-1 V1.2.1][ref-etsi-ts-119182-1]) clause
6.8 asks for, as [Signature][ts-5-01-signature] sets out.

Before the first exchange, each target holds what the rules below assume:

- **Trust Registry** holds the Root Authority's accreditation decisions and
  reaches the trusted list key through Trust Authority, whose Certificate
  Authority Component signs each list; it holds no private key of its own.
- **A reader** carries the trusted list key from build time and performs
  the checks of [Reading the copy][ts-5-01-reading-the-copy], through
  Trust SDK where it embeds the library.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-01-001 }**REQ-TS-5-01-001** Trust Registry MUST meet every requirement in [Format][ts-5-01-format], [Scheme information][ts-5-01-scheme-information], [Entries][ts-5-01-entries], [Signature][ts-5-01-signature], and [Publication][ts-5-01-publication].
- [](){ #req-ts-5-01-002 }**REQ-TS-5-01-002** Issuer Core, Verifier Core, Mobile Wallet, and Mobile Verifier MUST each meet every requirement in [Reading the copy][ts-5-01-reading-the-copy].
- [](){ #req-ts-5-01-090 }**REQ-TS-5-01-090** A Relying Party's own application built on Reader SDK MUST meet every requirement in [Reading the copy][ts-5-01-reading-the-copy].

</div>

## What the list answers {#ts-5-01-overview}

The trusted list answers one question about a counterpart: whether it is
accredited. Which key the counterpart signs with is answered by its
DID Document, and what it may do by its Authority Statement, as
[three questions, three answers][three-questions-three-answers] sets out.

The list is an index rather than a keystore: an entry names a registration by
its DID, its legal name, the legal identifier of the body behind it, its
status, and its role. For a registration that issues reader certificates it
also names the certificate authority (CA) it issues them from, its
Verifier Issuing CA. The
only keys the list names are Trust Authority's own, and any key of an entity
that was revoked early. [The trusted list][trusted-list] records who publishes
it, who reads it, and where it lives.

Every reader works from a bulk download of the whole list, cached outside
any transaction, for the reasons [a bulk download, cached][a-bulk-download-cached]
gives. The [trust cache sync][trust-cache-sync] is the flow that fills the
copy, and this specification turns
[the three rules for reading the copy][three-rules-for-reading-the-copy] into
requirements.

ETSI TS 119 602 models a list as scheme information followed by a sequence
of trusted entities, each holding one or more services; a service has a type,
a digital identity, a status, the time the status started, and a history of
its earlier statuses. In this profile a trusted entity is one accredited
registration, and [Services][ts-5-01-services] gives what a service says about
it. Trust Authority's own keys are an entry of the same shape.

## Trusted list payload {#ts-5-01-trusted-list-payload}

The list is an illustration: the bodies, the legal identifiers, the
addresses, and the keys are invented, and no registration has been
accredited. Every field is exact. The identifiers were generated with the
algorithms this profile names, the list was signed with the key its own
`TrustedListSigner` service carries, and the signature verifies, so an
implementation can parse this list and find what the clauses below require.

The payload, before [Signature][ts-5-01-signature] wraps it in the JWS,
shows every option the profile admits:

- Every service type.
- Both kinds of legal identifier.
- All four statuses.
- Both forms of a revoked key.
- A service history.
- Both languages.
- The Root Authority's entry, with a witness key that was rotated and a
  signing key that is announced but has not signed yet.

Its eight entries are, in order:

- A government Identity Issuer with two revoked keys.
- A private Wallet Provider.
- A private Relying Party that is an RP Intermediary, with its
  Verifier Issuing CA and a suspension in its history.
- A government Attribute Issuer whose accreditation was withdrawn.
- Three government Attribute Issuers in good standing, the issuers of the
  Kartu Nikah, the Kartu ASN, and the SIM.
- The Root Authority.

The list agrees with the other pages on four points:

- Its `VerifierIssuingCA` service carries the same bytes and the same
  subject key identifier as the certificate
  [the Verifier Issuing CA][ts-5-04-verifier-issuing-ca-as-issued]
  publishes.
- Its DIDs are the ones [the log as published][ts-5-02-the-log-as-published]
  resolves.
- Its two revoked key services are two revocations on the two routes, not one
  event written twice: the `did:webvh` key revoked on 16 October 2026, which the
  log still presents in `verificationMethod`, and a Document Signer Certificate
  revoked on 15 September 2026, the entry that
  [the Issuer Root CA list][ts-5-04-the-two-revocation-lists-as-issued] carries.
- The `StatusStartingTime` of each is the `ListIssueDateTime` of the
  emergency list that first carried the service, which
  [REQ-TS-5-01-038][req-ts-5-01-038] requires and which keeps it from
  preceding the list that announces it.

``` { .json title="trusted-list.json, the LoTE payload" data-format="JSON" }
{
  "LoTE": {
    "ListAndSchemeInformation": {
      "LoTEVersionIdentifier": 1,
      "LoTESequenceNumber": 42,
      "LoTEType": "https://idctf.id/ns/19602/LoTEType/IDCTFTrustedList",
      "SchemeOperatorName": [
        { "lang": "id", "value": "Trust Authority Republik Indonesia" },
        { "lang": "en", "value": "Trust Authority Republik Indonesia" }
      ],
      "SchemeOperatorAddress": {
        "SchemeOperatorPostalAddress": [
          {
            "lang": "id",
            "StreetAddress": "Jalan Kepercayaan Digital Nomor 1",
            "Locality": "Jakarta",
            "Country": "ID"
          },
          {
            "lang": "en",
            "StreetAddress": "Jalan Kepercayaan Digital Nomor 1",
            "Locality": "Jakarta",
            "Country": "ID"
          }
        ],
        "SchemeOperatorElectronicAddress": [
          { "lang": "id", "uriValue": "mailto:trust@trust.go.id" },
          { "lang": "en", "uriValue": "mailto:trust@trust.go.id" },
          { "lang": "id", "uriValue": "https://trust.go.id" },
          { "lang": "en", "uriValue": "https://trust.go.id" }
        ]
      },
      "SchemeName": [
        { "lang": "id", "value": "ID:Indonesia Digital Credential Trust Framework" },
        { "lang": "en", "value": "ID:Indonesia Digital Credential Trust Framework" }
      ],
      "SchemeInformationURI": [
        { "lang": "id", "uriValue": "https://trust.go.id/idctf/governance-framework" },
        { "lang": "en", "uriValue": "https://trust.go.id/idctf/governance-framework" }
      ],
      "StatusDeterminationApproach": "https://idctf.id/ns/19602/StatusDetn/IDCTF",
      "SchemeTypeCommunityRules": [
        { "lang": "id", "uriValue": "https://idctf.id/ns/19602/schemerules/IDCTF" },
        { "lang": "en", "uriValue": "https://idctf.id/ns/19602/schemerules/IDCTF" }
      ],
      "SchemeTerritory": "ID",
      "PolicyOrLegalNotice": [
        {
          "LoTEPolicy": { "lang": "id", "uriValue": "https://trust.go.id/idctf/governance-framework/policy" }
        },
        {
          "LoTEPolicy": { "lang": "en", "uriValue": "https://trust.go.id/idctf/governance-framework/policy" }
        }
      ],
      "HistoricalInformationPeriod": 65535,
      "ListIssueDateTime": "2026-10-17T06:00:00Z",
      "NextUpdate": "2026-10-24T06:00:00Z",
      "DistributionPoints": ["https://registry.trust.go.id/trusted-list.json"]
    },
    "TrustedEntitiesList": [
      {
        "TrustedEntityInformation": {
          "TEName": [
            { "lang": "id", "value": "Direktorat Jenderal Kependudukan dan Pencatatan Sipil" },
            { "lang": "en", "value": "Directorate General of Population and Civil Registration" }
          ],
          "TETradeName": [
            { "lang": "id", "value": "BKN:013250" },
            { "lang": "en", "value": "BKN:013250" }
          ],
          "TEAddress": {
            "TEPostalAddress": [
              {
                "lang": "id",
                "StreetAddress": "Jalan Raya Kependudukan Nomor 7",
                "Locality": "Jakarta",
                "Country": "ID"
              },
              {
                "lang": "en",
                "StreetAddress": "Jalan Raya Kependudukan Nomor 7",
                "Locality": "Jakarta",
                "Country": "ID"
              }
            ],
            "TEElectronicAddress": [
              { "lang": "id", "uriValue": "mailto:pki@dukcapil.go.id" },
              { "lang": "en", "uriValue": "mailto:pki@dukcapil.go.id" },
              { "lang": "id", "uriValue": "https://dukcapil.go.id" },
              { "lang": "en", "uriValue": "https://dukcapil.go.id" }
            ]
          },
          "TEInformationURI": [
            { "lang": "id", "uriValue": "https://dukcapil.go.id" },
            { "lang": "en", "uriValue": "https://dukcapil.go.id" }
          ]
        },
        "TrustedEntityServices": [
          {
            "ServiceInformation": {
              "ServiceTypeIdentifier": "https://idctf.id/ns/19602/SvcType/IdentityIssuer",
              "ServiceName": [
                { "lang": "id", "value": "Identity Issuer" },
                { "lang": "en", "value": "Identity Issuer" }
              ],
              "ServiceDigitalIdentity": {
                "OtherIds": ["did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id"]
              },
              "ServiceStatus": "https://idctf.id/ns/19602/SvcStatus/granted",
              "StatusStartingTime": "2026-02-01T00:00:00Z"
            }
          },
          {
            "ServiceInformation": {
              "ServiceTypeIdentifier": "https://idctf.id/ns/19602/SvcType/RevokedKey",
              "ServiceName": [
                { "lang": "id", "value": "Revoked key" },
                { "lang": "en", "value": "Revoked key" }
              ],
              "ServiceDigitalIdentity": {
                "OtherIds": [
                  "did:key:zDnaeWSwJDrKLraHe5w4vA39xFW2TnZaDDNEGGWSyHYSC9Nfp",
                  "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id#issuance-jose-1"
                ]
              },
              "ServiceStatus": "https://idctf.id/ns/19602/SvcStatus/revoked",
              "StatusStartingTime": "2026-10-16T14:05:00Z"
            }
          },
          {
            "ServiceInformation": {
              "ServiceTypeIdentifier": "https://idctf.id/ns/19602/SvcType/RevokedKey",
              "ServiceName": [
                { "lang": "id", "value": "Revoked key" },
                { "lang": "en", "value": "Revoked key" }
              ],
              "ServiceDigitalIdentity": {
                "X509SKIs": ["D50CAA65B460E10402D3972F73B830DB8B03DA28"]
              },
              "ServiceStatus": "https://idctf.id/ns/19602/SvcStatus/revoked",
              "StatusStartingTime": "2026-09-15T00:00:00Z"
            }
          }
        ]
      },
      {
        "TrustedEntityInformation": {
          "TEName": [
            { "lang": "id", "value": "PT Dompet Digital Nusantara" },
            { "lang": "en", "value": "PT Dompet Digital Nusantara" }
          ],
          "TETradeName": [
            { "lang": "id", "value": "NIB:9120407260031" },
            { "lang": "en", "value": "NIB:9120407260031" }
          ],
          "TEAddress": {
            "TEPostalAddress": [
              {
                "lang": "id",
                "StreetAddress": "Jalan Gatot Subroto Kavling 18",
                "Locality": "Jakarta",
                "Country": "ID"
              },
              {
                "lang": "en",
                "StreetAddress": "Jalan Gatot Subroto Kavling 18",
                "Locality": "Jakarta",
                "Country": "ID"
              }
            ],
            "TEElectronicAddress": [
              { "lang": "id", "uriValue": "mailto:pki@dompet.co.id" },
              { "lang": "en", "uriValue": "mailto:pki@dompet.co.id" },
              { "lang": "id", "uriValue": "https://dompet.co.id" },
              { "lang": "en", "uriValue": "https://dompet.co.id" }
            ]
          },
          "TEInformationURI": [
            { "lang": "id", "uriValue": "https://dompet.co.id" },
            { "lang": "en", "uriValue": "https://dompet.co.id" }
          ]
        },
        "TrustedEntityServices": [
          {
            "ServiceInformation": {
              "ServiceTypeIdentifier": "https://idctf.id/ns/19602/SvcType/WalletProvider",
              "ServiceName": [
                { "lang": "id", "value": "Wallet Provider" },
                { "lang": "en", "value": "Wallet Provider" }
              ],
              "ServiceDigitalIdentity": {
                "OtherIds": ["did:webvh:QmeTW134qjUC6EKXU6JL3dVRgd3fYmUpMbooEDokSpFEAH:dompet.co.id"]
              },
              "ServiceStatus": "https://idctf.id/ns/19602/SvcStatus/granted",
              "StatusStartingTime": "2026-03-01T00:00:00Z"
            }
          }
        ]
      },
      {
        "TrustedEntityInformation": {
          "TEName": [
            { "lang": "id", "value": "PT Terminal Nusantara" },
            { "lang": "en", "value": "PT Terminal Nusantara" }
          ],
          "TETradeName": [
            { "lang": "id", "value": "NIB:8120015640022" },
            { "lang": "en", "value": "NIB:8120015640022" }
          ],
          "TEAddress": {
            "TEPostalAddress": [
              { "lang": "id", "StreetAddress": "Jalan Asia Afrika Nomor 112", "Locality": "Bandung", "Country": "ID" },
              { "lang": "en", "StreetAddress": "Jalan Asia Afrika Nomor 112", "Locality": "Bandung", "Country": "ID" }
            ],
            "TEElectronicAddress": [
              { "lang": "id", "uriValue": "mailto:pki@terminal-nusantara.co.id" },
              { "lang": "en", "uriValue": "mailto:pki@terminal-nusantara.co.id" },
              { "lang": "id", "uriValue": "https://terminal-nusantara.co.id" },
              { "lang": "en", "uriValue": "https://terminal-nusantara.co.id" }
            ]
          },
          "TEInformationURI": [
            { "lang": "id", "uriValue": "https://terminal-nusantara.co.id" },
            { "lang": "en", "uriValue": "https://terminal-nusantara.co.id" }
          ]
        },
        "TrustedEntityServices": [
          {
            "ServiceInformation": {
              "ServiceTypeIdentifier": "https://idctf.id/ns/19602/SvcType/RelyingParty",
              "ServiceName": [
                { "lang": "id", "value": "Relying Party" },
                { "lang": "en", "value": "Relying Party" }
              ],
              "ServiceDigitalIdentity": {
                "OtherIds": ["did:webvh:QmUATC5jyf5yVy72GYAp8nSvuwshzDy6wYX7WmNY5UJtXT:terminal-nusantara.co.id"]
              },
              "ServiceStatus": "https://idctf.id/ns/19602/SvcStatus/granted",
              "StatusStartingTime": "2026-09-01T00:00:00Z"
            },
            "ServiceHistory": [
              {
                "ServiceName": [
                  { "lang": "id", "value": "Relying Party" },
                  { "lang": "en", "value": "Relying Party" }
                ],
                "ServiceDigitalIdentity": {
                  "OtherIds": ["did:webvh:QmUATC5jyf5yVy72GYAp8nSvuwshzDy6wYX7WmNY5UJtXT:terminal-nusantara.co.id"]
                },
                "ServiceStatus": "https://idctf.id/ns/19602/SvcStatus/suspended",
                "StatusStartingTime": "2026-08-20T09:30:00Z",
                "ServiceTypeIdentifier": "https://idctf.id/ns/19602/SvcType/RelyingParty"
              },
              {
                "ServiceName": [
                  { "lang": "id", "value": "Relying Party" },
                  { "lang": "en", "value": "Relying Party" }
                ],
                "ServiceDigitalIdentity": {
                  "OtherIds": ["did:webvh:QmUATC5jyf5yVy72GYAp8nSvuwshzDy6wYX7WmNY5UJtXT:terminal-nusantara.co.id"]
                },
                "ServiceStatus": "https://idctf.id/ns/19602/SvcStatus/granted",
                "StatusStartingTime": "2026-03-01T00:00:00Z",
                "ServiceTypeIdentifier": "https://idctf.id/ns/19602/SvcType/RelyingParty"
              }
            ]
          },
          {
            "ServiceInformation": {
              "ServiceTypeIdentifier": "https://idctf.id/ns/19602/SvcType/VerifierIssuingCA",
              "ServiceName": [
                { "lang": "id", "value": "Verifier Issuing CA" },
                { "lang": "en", "value": "Verifier Issuing CA" }
              ],
              "ServiceDigitalIdentity": {
                "X509SKIs": ["2EA3B6F5A1D3E7F7F920605EFFE880A059817933"],
                "X509Certificates": [
                  {
                    "val": "MIICcDCCAhegAwIBAgINALWJzfYbiJ6/CpzOBTAKBggqhkjOPQQDAjBbMQswCQYDVQQGEwJJRDErMCkGA1UECgwiVHJ1c3QgQXV0aG9yaXR5IFJlcHVibGlrIEluZG9uZXNpYTEfMB0GA1UEAwwWSURDVEYgVmVyaWZpZXIgUm9vdCBDQTAeFw0yNjA2MDEwMDAwMDBaFw0zMTA2MDEwMDAwMDBaMFsxCzAJBgNVBAYTAklEMRswGQYDVQQKDBJUZXJtaW5hbCBOdXNhbnRhcmExLzAtBgNVBAMMJlRlcm1pbmFsIE51c2FudGFyYSBWZXJpZmllciBJc3N1aW5nIENBMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAElUF1hsWuBgIrtSf93F93N9xc01IYQG7Nsz+8A+EV7IrxgWYzM0GPaTYMC+z60sBWjVvugNB0but2v89nRQ9/faOBvzCBvDASBgNVHRMBAf8ECDAGAQH/AgEAMA4GA1UdDwEB/wQEAwIBBjASBgNVHSUECzAJBgcogYxdBQEGMB8GA1UdIwQYMBaAFFnF8EN4aHfG4uKhJUSkMD1K7gTzMB0GA1UdDgQWBBQuo7b1odPn9/kgYF7/6ICgWYF5MzBCBgNVHR8EOzA5MDegNaAzhjFodHRwczovL3JlZ2lzdHJ5LnRydXN0LmdvLmlkL2NybC92ZXJpZmllci1yb290LWNhMAoGCCqGSM49BAMCA0cAMEQCICG2iSLIuvM1F8n0ZjzNVRBhsY/aWRe6s9BMBmhN7PNGAiASz3+SCPOvuVg4P8+qIfaeGtkuO4Mv13sfZgKZz6rlrQ=="
                  }
                ]
              },
              "ServiceStatus": "https://idctf.id/ns/19602/SvcStatus/granted",
              "StatusStartingTime": "2026-09-01T00:00:00Z"
            },
            "ServiceHistory": [
              {
                "ServiceName": [
                  { "lang": "id", "value": "Verifier Issuing CA" },
                  { "lang": "en", "value": "Verifier Issuing CA" }
                ],
                "ServiceDigitalIdentity": {
                  "X509SKIs": ["2EA3B6F5A1D3E7F7F920605EFFE880A059817933"],
                  "X509Certificates": [
                    {
                      "val": "MIICcDCCAhegAwIBAgINALWJzfYbiJ6/CpzOBTAKBggqhkjOPQQDAjBbMQswCQYDVQQGEwJJRDErMCkGA1UECgwiVHJ1c3QgQXV0aG9yaXR5IFJlcHVibGlrIEluZG9uZXNpYTEfMB0GA1UEAwwWSURDVEYgVmVyaWZpZXIgUm9vdCBDQTAeFw0yNjA2MDEwMDAwMDBaFw0zMTA2MDEwMDAwMDBaMFsxCzAJBgNVBAYTAklEMRswGQYDVQQKDBJUZXJtaW5hbCBOdXNhbnRhcmExLzAtBgNVBAMMJlRlcm1pbmFsIE51c2FudGFyYSBWZXJpZmllciBJc3N1aW5nIENBMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAElUF1hsWuBgIrtSf93F93N9xc01IYQG7Nsz+8A+EV7IrxgWYzM0GPaTYMC+z60sBWjVvugNB0but2v89nRQ9/faOBvzCBvDASBgNVHRMBAf8ECDAGAQH/AgEAMA4GA1UdDwEB/wQEAwIBBjASBgNVHSUECzAJBgcogYxdBQEGMB8GA1UdIwQYMBaAFFnF8EN4aHfG4uKhJUSkMD1K7gTzMB0GA1UdDgQWBBQuo7b1odPn9/kgYF7/6ICgWYF5MzBCBgNVHR8EOzA5MDegNaAzhjFodHRwczovL3JlZ2lzdHJ5LnRydXN0LmdvLmlkL2NybC92ZXJpZmllci1yb290LWNhMAoGCCqGSM49BAMCA0cAMEQCICG2iSLIuvM1F8n0ZjzNVRBhsY/aWRe6s9BMBmhN7PNGAiASz3+SCPOvuVg4P8+qIfaeGtkuO4Mv13sfZgKZz6rlrQ=="
                    }
                  ]
                },
                "ServiceStatus": "https://idctf.id/ns/19602/SvcStatus/suspended",
                "StatusStartingTime": "2026-08-20T09:30:00Z",
                "ServiceTypeIdentifier": "https://idctf.id/ns/19602/SvcType/VerifierIssuingCA"
              },
              {
                "ServiceName": [
                  { "lang": "id", "value": "Verifier Issuing CA" },
                  { "lang": "en", "value": "Verifier Issuing CA" }
                ],
                "ServiceDigitalIdentity": {
                  "X509SKIs": ["2EA3B6F5A1D3E7F7F920605EFFE880A059817933"],
                  "X509Certificates": [
                    {
                      "val": "MIICcDCCAhegAwIBAgINALWJzfYbiJ6/CpzOBTAKBggqhkjOPQQDAjBbMQswCQYDVQQGEwJJRDErMCkGA1UECgwiVHJ1c3QgQXV0aG9yaXR5IFJlcHVibGlrIEluZG9uZXNpYTEfMB0GA1UEAwwWSURDVEYgVmVyaWZpZXIgUm9vdCBDQTAeFw0yNjA2MDEwMDAwMDBaFw0zMTA2MDEwMDAwMDBaMFsxCzAJBgNVBAYTAklEMRswGQYDVQQKDBJUZXJtaW5hbCBOdXNhbnRhcmExLzAtBgNVBAMMJlRlcm1pbmFsIE51c2FudGFyYSBWZXJpZmllciBJc3N1aW5nIENBMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAElUF1hsWuBgIrtSf93F93N9xc01IYQG7Nsz+8A+EV7IrxgWYzM0GPaTYMC+z60sBWjVvugNB0but2v89nRQ9/faOBvzCBvDASBgNVHRMBAf8ECDAGAQH/AgEAMA4GA1UdDwEB/wQEAwIBBjASBgNVHSUECzAJBgcogYxdBQEGMB8GA1UdIwQYMBaAFFnF8EN4aHfG4uKhJUSkMD1K7gTzMB0GA1UdDgQWBBQuo7b1odPn9/kgYF7/6ICgWYF5MzBCBgNVHR8EOzA5MDegNaAzhjFodHRwczovL3JlZ2lzdHJ5LnRydXN0LmdvLmlkL2NybC92ZXJpZmllci1yb290LWNhMAoGCCqGSM49BAMCA0cAMEQCICG2iSLIuvM1F8n0ZjzNVRBhsY/aWRe6s9BMBmhN7PNGAiASz3+SCPOvuVg4P8+qIfaeGtkuO4Mv13sfZgKZz6rlrQ=="
                    }
                  ]
                },
                "ServiceStatus": "https://idctf.id/ns/19602/SvcStatus/granted",
                "StatusStartingTime": "2026-06-01T00:00:00Z",
                "ServiceTypeIdentifier": "https://idctf.id/ns/19602/SvcType/VerifierIssuingCA"
              }
            ]
          }
        ]
      },
      {
        "TrustedEntityInformation": {
          "TEName": [
            { "lang": "id", "value": "Universitas Negeri Nusantara" },
            { "lang": "en", "value": "Universitas Negeri Nusantara" }
          ],
          "TETradeName": [
            { "lang": "id", "value": "BKN:401160" },
            { "lang": "en", "value": "BKN:401160" }
          ],
          "TEAddress": {
            "TEPostalAddress": [
              { "lang": "id", "StreetAddress": "Jalan Pendidikan Nomor 45", "Locality": "Jakarta", "Country": "ID" },
              { "lang": "en", "StreetAddress": "Jalan Pendidikan Nomor 45", "Locality": "Jakarta", "Country": "ID" }
            ],
            "TEElectronicAddress": [
              { "lang": "id", "uriValue": "mailto:pki@unn.ac.id" },
              { "lang": "en", "uriValue": "mailto:pki@unn.ac.id" },
              { "lang": "id", "uriValue": "https://ijazah.unn.ac.id" },
              { "lang": "en", "uriValue": "https://ijazah.unn.ac.id" }
            ]
          },
          "TEInformationURI": [
            { "lang": "id", "uriValue": "https://ijazah.unn.ac.id" },
            { "lang": "en", "uriValue": "https://ijazah.unn.ac.id" }
          ]
        },
        "TrustedEntityServices": [
          {
            "ServiceInformation": {
              "ServiceTypeIdentifier": "https://idctf.id/ns/19602/SvcType/AttributeIssuer",
              "ServiceName": [
                { "lang": "id", "value": "Attribute Issuer" },
                { "lang": "en", "value": "Attribute Issuer" }
              ],
              "ServiceDigitalIdentity": {
                "OtherIds": ["did:webvh:QmYkJiocF5XVJH9xjKceVciKGvHpv9zf7wZcRy6y3uzFq1:ijazah.unn.ac.id"]
              },
              "ServiceStatus": "https://idctf.id/ns/19602/SvcStatus/withdrawn",
              "StatusStartingTime": "2026-10-01T00:00:00Z"
            },
            "ServiceHistory": [
              {
                "ServiceName": [
                  { "lang": "id", "value": "Attribute Issuer" },
                  { "lang": "en", "value": "Attribute Issuer" }
                ],
                "ServiceDigitalIdentity": {
                  "OtherIds": ["did:webvh:QmYkJiocF5XVJH9xjKceVciKGvHpv9zf7wZcRy6y3uzFq1:ijazah.unn.ac.id"]
                },
                "ServiceStatus": "https://idctf.id/ns/19602/SvcStatus/granted",
                "StatusStartingTime": "2026-02-01T00:00:00Z",
                "ServiceTypeIdentifier": "https://idctf.id/ns/19602/SvcType/AttributeIssuer"
              }
            ]
          }
        ]
      },
      {
        "TrustedEntityInformation": {
          "TEName": [
            { "lang": "id", "value": "Kementerian Agama" },
            { "lang": "en", "value": "Ministry of Religious Affairs" }
          ],
          "TETradeName": [
            { "lang": "id", "value": "BKN:402510" },
            { "lang": "en", "value": "BKN:402510" }
          ],
          "TEAddress": {
            "TEPostalAddress": [
              { "lang": "id", "StreetAddress": "Jalan Kerukunan Nomor 12", "Locality": "Jakarta", "Country": "ID" },
              { "lang": "en", "StreetAddress": "Jalan Kerukunan Nomor 12", "Locality": "Jakarta", "Country": "ID" }
            ],
            "TEElectronicAddress": [
              { "lang": "id", "uriValue": "mailto:pki@kemenag.go.id" },
              { "lang": "en", "uriValue": "mailto:pki@kemenag.go.id" },
              { "lang": "id", "uriValue": "https://kemenag.go.id" },
              { "lang": "en", "uriValue": "https://kemenag.go.id" }
            ]
          },
          "TEInformationURI": [
            { "lang": "id", "uriValue": "https://kemenag.go.id" },
            { "lang": "en", "uriValue": "https://kemenag.go.id" }
          ]
        },
        "TrustedEntityServices": [
          {
            "ServiceInformation": {
              "ServiceTypeIdentifier": "https://idctf.id/ns/19602/SvcType/AttributeIssuer",
              "ServiceName": [
                { "lang": "id", "value": "Attribute Issuer" },
                { "lang": "en", "value": "Attribute Issuer" }
              ],
              "ServiceDigitalIdentity": {
                "OtherIds": ["did:webvh:QmbAb7u9RMjqsZ9L98pe47szJZdnKQLh9KizqNW2WwKac1:kemenag.go.id"]
              },
              "ServiceStatus": "https://idctf.id/ns/19602/SvcStatus/granted",
              "StatusStartingTime": "2026-03-01T00:00:00Z"
            }
          }
        ]
      },
      {
        "TrustedEntityInformation": {
          "TEName": [
            { "lang": "id", "value": "Badan Kepegawaian Negara" },
            { "lang": "en", "value": "National Civil Service Agency" }
          ],
          "TETradeName": [
            { "lang": "id", "value": "BKN:403380" },
            { "lang": "en", "value": "BKN:403380" }
          ],
          "TEAddress": {
            "TEPostalAddress": [
              { "lang": "id", "StreetAddress": "Jalan Kepegawaian Nomor 9", "Locality": "Jakarta", "Country": "ID" },
              { "lang": "en", "StreetAddress": "Jalan Kepegawaian Nomor 9", "Locality": "Jakarta", "Country": "ID" }
            ],
            "TEElectronicAddress": [
              { "lang": "id", "uriValue": "mailto:pki@bkn.go.id" },
              { "lang": "en", "uriValue": "mailto:pki@bkn.go.id" },
              { "lang": "id", "uriValue": "https://bkn.go.id" },
              { "lang": "en", "uriValue": "https://bkn.go.id" }
            ]
          },
          "TEInformationURI": [
            { "lang": "id", "uriValue": "https://bkn.go.id" },
            { "lang": "en", "uriValue": "https://bkn.go.id" }
          ]
        },
        "TrustedEntityServices": [
          {
            "ServiceInformation": {
              "ServiceTypeIdentifier": "https://idctf.id/ns/19602/SvcType/AttributeIssuer",
              "ServiceName": [
                { "lang": "id", "value": "Attribute Issuer" },
                { "lang": "en", "value": "Attribute Issuer" }
              ],
              "ServiceDigitalIdentity": {
                "OtherIds": ["did:webvh:Qme8RriGnKx5j2QjoaY1SgRSpxTHdjq11L2Exgy1zV2xsJ:bkn.go.id"]
              },
              "ServiceStatus": "https://idctf.id/ns/19602/SvcStatus/granted",
              "StatusStartingTime": "2026-03-01T00:00:00Z"
            }
          }
        ]
      },
      {
        "TrustedEntityInformation": {
          "TEName": [
            { "lang": "id", "value": "Korps Lalu Lintas Kepolisian Negara Republik Indonesia" },
            { "lang": "en", "value": "Traffic Corps of the Indonesian National Police" }
          ],
          "TETradeName": [
            { "lang": "id", "value": "BKN:404390" },
            { "lang": "en", "value": "BKN:404390" }
          ],
          "TEAddress": {
            "TEPostalAddress": [
              { "lang": "id", "StreetAddress": "Jalan Lalu Lintas Nomor 7", "Locality": "Jakarta", "Country": "ID" },
              { "lang": "en", "StreetAddress": "Jalan Lalu Lintas Nomor 7", "Locality": "Jakarta", "Country": "ID" }
            ],
            "TEElectronicAddress": [
              { "lang": "id", "uriValue": "mailto:pki@korlantas.polri.go.id" },
              { "lang": "en", "uriValue": "mailto:pki@korlantas.polri.go.id" },
              { "lang": "id", "uriValue": "https://korlantas.polri.go.id" },
              { "lang": "en", "uriValue": "https://korlantas.polri.go.id" }
            ]
          },
          "TEInformationURI": [
            { "lang": "id", "uriValue": "https://korlantas.polri.go.id" },
            { "lang": "en", "uriValue": "https://korlantas.polri.go.id" }
          ]
        },
        "TrustedEntityServices": [
          {
            "ServiceInformation": {
              "ServiceTypeIdentifier": "https://idctf.id/ns/19602/SvcType/AttributeIssuer",
              "ServiceName": [
                { "lang": "id", "value": "Attribute Issuer" },
                { "lang": "en", "value": "Attribute Issuer" }
              ],
              "ServiceDigitalIdentity": {
                "OtherIds": ["did:webvh:QmZQeFgp3SBDLmidt4TiZhix8u5b2oPSqvQFhuSF8BoN6F:korlantas.polri.go.id"]
              },
              "ServiceStatus": "https://idctf.id/ns/19602/SvcStatus/granted",
              "StatusStartingTime": "2026-03-01T00:00:00Z"
            }
          }
        ]
      },
      {
        "TrustedEntityInformation": {
          "TEName": [
            { "lang": "id", "value": "Trust Authority Republik Indonesia" },
            { "lang": "en", "value": "Trust Authority Republik Indonesia" }
          ],
          "TETradeName": [
            { "lang": "id", "value": "BKN:000100" },
            { "lang": "en", "value": "BKN:000100" }
          ],
          "TEAddress": {
            "TEPostalAddress": [
              {
                "lang": "id",
                "StreetAddress": "Jalan Kepercayaan Digital Nomor 1",
                "Locality": "Jakarta",
                "Country": "ID"
              },
              {
                "lang": "en",
                "StreetAddress": "Jalan Kepercayaan Digital Nomor 1",
                "Locality": "Jakarta",
                "Country": "ID"
              }
            ],
            "TEElectronicAddress": [
              { "lang": "id", "uriValue": "mailto:trust@trust.go.id" },
              { "lang": "en", "uriValue": "mailto:trust@trust.go.id" },
              { "lang": "id", "uriValue": "https://trust.go.id" },
              { "lang": "en", "uriValue": "https://trust.go.id" }
            ]
          },
          "TEInformationURI": [
            { "lang": "id", "uriValue": "https://trust.go.id" },
            { "lang": "en", "uriValue": "https://trust.go.id" }
          ]
        },
        "TrustedEntityServices": [
          {
            "ServiceInformation": {
              "ServiceTypeIdentifier": "https://idctf.id/ns/19602/SvcType/Witness",
              "ServiceName": [
                { "lang": "id", "value": "Witness" },
                { "lang": "en", "value": "Witness" }
              ],
              "ServiceDigitalIdentity": {
                "OtherIds": ["did:key:z6MktqjEVK1P1HgMSJYGpPYjuLjEa13u26WEhf7dvCWPYZj1"]
              },
              "ServiceStatus": "https://idctf.id/ns/19602/SvcStatus/granted",
              "StatusStartingTime": "2026-09-01T00:00:00Z"
            }
          },
          {
            "ServiceInformation": {
              "ServiceTypeIdentifier": "https://idctf.id/ns/19602/SvcType/Witness",
              "ServiceName": [
                { "lang": "id", "value": "Witness" },
                { "lang": "en", "value": "Witness" }
              ],
              "ServiceDigitalIdentity": {
                "OtherIds": ["did:key:z6MkrGRs1p2FjsQsxJtKwmaUotzGtjmjcvM7uKcnXU7ffLKe"]
              },
              "ServiceStatus": "https://idctf.id/ns/19602/SvcStatus/withdrawn",
              "StatusStartingTime": "2026-10-01T00:00:00Z"
            },
            "ServiceHistory": [
              {
                "ServiceName": [
                  { "lang": "id", "value": "Witness" },
                  { "lang": "en", "value": "Witness" }
                ],
                "ServiceDigitalIdentity": {
                  "OtherIds": ["did:key:z6MkrGRs1p2FjsQsxJtKwmaUotzGtjmjcvM7uKcnXU7ffLKe"]
                },
                "ServiceStatus": "https://idctf.id/ns/19602/SvcStatus/granted",
                "StatusStartingTime": "2026-01-01T00:00:00Z",
                "ServiceTypeIdentifier": "https://idctf.id/ns/19602/SvcType/Witness"
              }
            ]
          },
          {
            "ServiceInformation": {
              "ServiceTypeIdentifier": "https://idctf.id/ns/19602/SvcType/TrustedListSigner",
              "ServiceName": [
                { "lang": "id", "value": "Trusted list signer" },
                { "lang": "en", "value": "Trusted list signer" }
              ],
              "ServiceDigitalIdentity": {
                "OtherIds": ["did:key:zDnaeSCzChDqLTnobz1iquKetDC1piuwydzo3jkpiEHNwtX7q"]
              },
              "ServiceStatus": "https://idctf.id/ns/19602/SvcStatus/granted",
              "StatusStartingTime": "2026-01-01T00:00:00Z"
            }
          },
          {
            "ServiceInformation": {
              "ServiceTypeIdentifier": "https://idctf.id/ns/19602/SvcType/TrustedListSigner",
              "ServiceName": [
                { "lang": "id", "value": "Trusted list signer" },
                { "lang": "en", "value": "Trusted list signer" }
              ],
              "ServiceDigitalIdentity": {
                "OtherIds": ["did:key:zDnaeboX93RcUPs8Npc68EQD5RgbVeVWTr8sKyYM8vrCeWrki"]
              },
              "ServiceStatus": "https://idctf.id/ns/19602/SvcStatus/granted",
              "StatusStartingTime": "2026-10-17T06:00:00Z"
            }
          }
        ]
      }
    ]
  }
}
```

The second signing key is listed at `granted` from the issue time of this
list and has signed nothing yet; it may sign the next list because this
one, signed with the first key, announced it. The first witness key is
`withdrawn` from 1 October 2026 and still vouches for every log entry
published before that date.

## Format {#ts-5-01-format}

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-01-003 }**REQ-TS-5-01-003** The trusted list MUST be a List of Trusted Entities in the JSON binding of [ETSI TS 119 602][ref-etsi-ts-119602] Annex A.1, valid against the JSON schema ETSI publishes for that binding.
- [](){ #req-ts-5-01-004 }**REQ-TS-5-01-004** The list MUST carry explicit scheme information, with every element that Table 1 of [ETSI TS 119 602][ref-etsi-ts-119602] marks mandatory for explicit scheme information present.
- [](){ #req-ts-5-01-005 }**REQ-TS-5-01-005** Every date-time value MUST follow clause 6.1.3 of [ETSI TS 119 602][ref-etsi-ts-119602]: Coordinated Universal Time (UTC), seconds without a fraction, and the `Z` designator.
- [](){ #req-ts-5-01-006 }**REQ-TS-5-01-006** Every multilingual string and every multilingual pointer MUST be given in Indonesian, tagged `id`, and in English, tagged `en`.
- [](){ #req-ts-5-01-007 }**REQ-TS-5-01-007** The list MUST NOT contain a `SchemeExtensions`, `TEInformationExtensions`, or `ServiceInformationExtensions` element.

</div>

Extensions are forbidden because the published schema gives them no
structure, and nothing this profile needs lacks a place in the model.

## The scheme identifiers {#ts-5-01-the-scheme-identifiers}

The list type, the status determination approach, the scheme rules, every
service type, and every status are written as Uniform Resource Identifiers (URIs) under
`https://idctf.id/ns/19602/`, the pattern ETSI TS 119 602 follows and the
one the credential type namespace `id.idctf` already uses. Each is an
identifier and nothing else: it names a value this profile defines, it is
compared as a string, and no reader ever fetches it.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-01-080 }**REQ-TS-5-01-080** A reader MUST compare an identifier under `https://idctf.id/ns/19602/` with the value this specification gives byte for byte, after no transformation of any kind.
- [](){ #req-ts-5-01-081 }**REQ-TS-5-01-081** A reader MUST NOT dereference such an identifier.
- [](){ #req-ts-5-01-087 }**REQ-TS-5-01-087** A reader MUST NOT make any network request derived from such an identifier.
- [](){ #req-ts-5-01-082 }**REQ-TS-5-01-082** A reader MUST treat a service whose `ServiceTypeIdentifier` is not one of [the table of service types][tbl-ts-5-01-service-types], or a status that is not one of [the table of statuses][tbl-ts-5-01-statuses], as carrying no statement about the registration.
- [](){ #req-ts-5-01-083 }**REQ-TS-5-01-083** Trust Registry MUST NOT make the meaning of such an identifier depend on anything served at its address.

</div>

Fetching an identifier is the one way the name could matter, and it is
refused twice over, by [REQ-TS-5-01-081][req-ts-5-01-081] and by a reader
working from a cached copy and nothing else. A reader that fetched one
would hand whoever holds the name that day a say in whether a registration
is trusted, and would tell them who was reading the list.

Moving the identifiers to another root is a major change under
[Common provisions](common-provisions.md).

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-01-084 }**REQ-TS-5-01-084** Trust Registry MUST write every identifier under the root named by the version of this specification it conforms to.
- [](){ #req-ts-5-01-088 }**REQ-TS-5-01-088** Trust Registry MUST NOT write two roots in one list.
- [](){ #req-ts-5-01-085 }**REQ-TS-5-01-085** During the transition period of a major version that moves the root, a reader MUST accept an identifier under either root.
- [](){ #req-ts-5-01-089 }**REQ-TS-5-01-089** During the transition period of a major version that moves the root, a reader MUST treat an identifier under the superseded root and the matching identifier under the new root as the same value.
- [](){ #req-ts-5-01-086 }**REQ-TS-5-01-086** After that transition period, a reader MUST treat an identifier under the superseded root as one it does not recognize.

</div>

## Scheme information {#ts-5-01-scheme-information}

The `ListAndSchemeInformation` component describes the list and the scheme
it is issued under. [The table of scheme information][tbl-ts-5-01-scheme-information]
gives the value or the presence of each element, in the order of
ETSI TS 119 602 clause 6.3; a row that says no additional requirement leaves
the element as the standard defines it.

[](){ #tbl-ts-5-01-scheme-information }

<figure markdown="1" class="ekdn-table">

| Element | Type | Presence | Requirement |
|---|---|---|---|
| `LoTEVersionIdentifier` | integer | Present | `1` |
| `LoTESequenceNumber` | integer | Present | `1` for the first list ever published, then one more for every list published after it, an emergency list included |
| `LoTEType` | URI | Present | `https://idctf.id/ns/19602/LoTEType/IDCTFTrustedList` |
| `SchemeOperatorName` | multilingual string | Present | The formal legal name of the body that holds the Root Authority role |
| `SchemeOperatorAddress` | object | Present | Present: the postal address, the e-mail address, and the website of that body |
| `SchemeName` | multilingual string | Present | `ID:` followed by the name of the scheme, in each language |
| `SchemeInformationURI` | multilingual pointer | Present | The address at which the Governance Framework is published |
| `StatusDeterminationApproach` | URI | Present | `https://idctf.id/ns/19602/StatusDetn/IDCTF` |
| `SchemeTypeCommunityRules` | multilingual pointer | Present | `https://idctf.id/ns/19602/schemerules/IDCTF`, the identifier of the Governance Framework |
| `SchemeTerritory` | string | Present | `ID` |
| `PolicyOrLegalNotice` | object | Present | Present, as `LoTEPolicy` pointers to the Governance Framework |
| `HistoricalInformationPeriod` | integer | Present | `65535`: history is never removed |
| `PointersToOtherLoTE` | array | Absent | Absent |
| `ListIssueDateTime` | date-time | Present | The time the list was issued |
| `NextUpdate` | date-time | Present | Present and not null; no later than the horizon the Governance Profile sets after `ListIssueDateTime` |
| `DistributionPoints` | array of URI | Present | Present: every address from which the latest list is served |
| `SchemeExtensions` | array | Absent | Absent |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-01-008 }**REQ-TS-5-01-008** Trust Registry MUST set every element of `ListAndSchemeInformation` as [the table of scheme information][tbl-ts-5-01-scheme-information] requires.
- [](){ #req-ts-5-01-009 }**REQ-TS-5-01-009** Trust Registry MUST increase `LoTESequenceNumber` by exactly one on every list it publishes.
- [](){ #req-ts-5-01-010 }**REQ-TS-5-01-010** Trust Registry MUST NOT publish a list whose `LoTESequenceNumber` is lower than or equal to that of a list already published.
- [](){ #req-ts-5-01-011 }**REQ-TS-5-01-011** Trust Registry MUST set `NextUpdate` no later than `ListIssueDateTime` plus the horizon the Governance Profile sets.
- [](){ #req-ts-5-01-012 }**REQ-TS-5-01-012** Trust Registry MUST NOT set `NextUpdate` later than six months after `ListIssueDateTime`, whatever the horizon.
- [](){ #req-ts-5-01-013 }**REQ-TS-5-01-013** Trust Registry MUST NOT set `NextUpdate` to null while the scheme operates.

</div>

The horizon behind `NextUpdate` is the staleness Trust Registry accepts from a
device with no network, as
[the three rules for reading the copy][three-rules-for-reading-the-copy]
explain; the list is reissued on the sync schedule regardless, well inside it.
The six-month ceiling is the one [ETSI TS 119 602][ref-etsi-ts-119602] clause
6.3.15 asks a profile to set, and the value every Annex profile of that standard
sets.

The list points at no other list: whether a foreign authority is
recognized is answered on request over the `recognition` query of
[Answering a permission query and serving the catalog](answering-a-permission-query-and-serving-the-catalog.md),
as [chain of trust](../architecture-framework/trust-model/chain-of-trust.md)
sets out.

## Entries {#ts-5-01-entries}

### One entry per registration {#ts-5-01-one-entry-per-registration}

A `TrustedEntity` is one registration the Root Authority accredited. One
legal body may hold several registrations, each with its own DID, as
[three stages of authority](../architecture-framework/roles/three-stages-of-authority.md)
sets out; each is an entry of its own, and the legal identifier shows they
belong to one body.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-01-014 }**REQ-TS-5-01-014** `TrustedEntitiesList` MUST contain exactly one `TrustedEntity` for every registration whose accreditation the Root Authority has granted, suspended, or withdrawn.
- [](){ #req-ts-5-01-015 }**REQ-TS-5-01-015** `TrustedEntitiesList` MUST NOT contain an entry for a registration that is pending or was rejected.
- [](){ #req-ts-5-01-016 }**REQ-TS-5-01-016** An entry whose accreditation was withdrawn MUST stay in the list, with its services at status `withdrawn`, for as long as the list is published.
- [](){ #req-ts-5-01-017 }**REQ-TS-5-01-017** `TrustedEntitiesList` MUST contain exactly one `TrustedEntity` for the body that holds the Root Authority role, carrying Trust Authority's own keys as [Trust Authority's own keys][ts-5-01-trust-authoritys-own-keys] sets out.

</div>

### Trusted entity information {#ts-5-01-trusted-entity-information}

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-01-018 }**REQ-TS-5-01-018** `TEName` MUST be the legal name of the body behind the registration, as used in its formal legal registration, identical across every registration of that body.
- [](){ #req-ts-5-01-019 }**REQ-TS-5-01-019** `TETradeName` MUST carry, in each language, one string holding the legal identifier of the body: `BKN:` followed by its institution code from the Badan Kepegawaian Negara (BKN) for a government body, or `NIB:` followed by its Nomor Induk Berusaha (NIB) for a private one.
- [](){ #req-ts-5-01-020 }**REQ-TS-5-01-020** The legal identifier in `TETradeName` MUST be identical across every registration of one body.
- [](){ #req-ts-5-01-021 }**REQ-TS-5-01-021** `TETradeName` MAY carry, after the legal identifier, a name under which the body operates the registered services.
- [](){ #req-ts-5-01-022 }**REQ-TS-5-01-022** `TEAddress` MUST carry the postal address, the e-mail address, and the website of the body, at which it answers inquiries about the registration.
- [](){ #req-ts-5-01-023 }**REQ-TS-5-01-023** `TEInformationURI` MUST carry the address of the domain the registration's `did:webvh` resolves at, as `https://` followed by that domain.

</div>

A reader tells a BKN code from an NIB by the prefix; the two
kinds never share a value space because the prefix is part of the string.
A registration's `did:webvh` names the domain it resolves at, as
[entities: did:webvh][entities-didwebvh] sets out, which makes
`TEInformationURI` always available.

### Services {#ts-5-01-services}

An entry's `TrustedEntityServices` says what the list says about the
registration: each role it holds, each certificate authority it runs, and
each key of its that was revoked early. Each is one `TrustedEntityService`, and its
`ServiceTypeIdentifier` says which, from
[the table of service types][tbl-ts-5-01-service-types].

[](){ #tbl-ts-5-01-service-types }

<figure markdown="1" class="ekdn-table">

| Service type | `ServiceTypeIdentifier` | `ServiceDigitalIdentity` |
|---|---|---|
| Identity Issuer | `https://idctf.id/ns/19602/SvcType/IdentityIssuer` | The registration's `did:webvh`, in `OtherIds` |
| Attribute Issuer | `https://idctf.id/ns/19602/SvcType/AttributeIssuer` | The registration's `did:webvh`, in `OtherIds` |
| Wallet Provider | `https://idctf.id/ns/19602/SvcType/WalletProvider` | The registration's `did:webvh`, in `OtherIds` |
| Relying Party | `https://idctf.id/ns/19602/SvcType/RelyingParty` | The registration's `did:webvh`, in `OtherIds` |
| Verifier Issuing CA | `https://idctf.id/ns/19602/SvcType/VerifierIssuingCA` | The subject key identifier of the CA certificate, in `X509SKIs` |
| Revoked key | `https://idctf.id/ns/19602/SvcType/RevokedKey` | The key itself, as [Revoked keys][ts-5-01-revoked-keys] sets out |
| Witness | `https://idctf.id/ns/19602/SvcType/Witness` | The witness key as a `did:key`, in `OtherIds` |
| Trusted list signer | `https://idctf.id/ns/19602/SvcType/TrustedListSigner` | The signing key as a `did:key`, in `OtherIds` |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-01-024 }**REQ-TS-5-01-024** An entry MUST carry one service for each role its registration was accredited for, with the `ServiceTypeIdentifier` of that role from [the table of service types][tbl-ts-5-01-service-types].
- [](){ #req-ts-5-01-025 }**REQ-TS-5-01-025** The `ServiceDigitalIdentity` of a role service MUST consist of the registration's `did:webvh` in `OtherIds` and nothing else.
- [](){ #req-ts-5-01-026 }**REQ-TS-5-01-026** Every service MUST carry `ServiceTypeIdentifier`, `ServiceStatus`, and `StatusStartingTime`.
- [](){ #req-ts-5-01-027 }**REQ-TS-5-01-027** `ServiceName` MUST be the name of the service type in each language.
- [](){ #req-ts-5-01-028 }**REQ-TS-5-01-028** An entry whose registration issues Verifier Device Certificates MUST carry one Verifier Issuing CA service per Verifier Issuing CA it issues them from, with the subject key identifier of that CA's certificate in `X509SKIs`.
- [](){ #req-ts-5-01-029 }**REQ-TS-5-01-029** A Verifier Issuing CA service MAY carry the CA certificate in `X509Certificates` in addition.
- [](){ #req-ts-5-01-030 }**REQ-TS-5-01-030** An entry MUST NOT carry a Document Signer Certificate, a DID Document key in good standing, or any other key of the registration that is not revoked.

</div>

The role is carried and the scope is not: what a registration may issue or
request is the Authority Statement's to answer, as
[Authorization][authorization] explains. An RP Intermediary is accredited as
a Relying Party and carries that role; serving merchants is a standing the
Root Authority grants, not a role of its own, as
[RP Intermediary and merchant][rp-intermediary-and-merchant] sets out, and
the Verifier Issuing CA service is how the list shows it.

That CA is listed by its key identifier rather than its certificate because
a wallet builds the certificate chain of the reading device from the
certificates the request carries. It needs the list only to confirm that the
CA belongs to a granted registration, and
[the reader side][the-reader-side] sets out the chain.

A Document Signer Certificate is never in the list: an mdoc verifier learns
the signing key from the certificate the credential carries and checks it
against the Issuer Root CA, as [the issuer side][the-issuer-side] sets
out.

### Status {#ts-5-01-status}

The status of a service is one of the four in
[the table of statuses][tbl-ts-5-01-statuses]. The three that apply to a
registration follow the [entity lifecycle of the Governance Framework][gf-incidents-and-sanctions]; the
fourth applies to a key.

[](){ #tbl-ts-5-01-statuses }

<figure markdown="1" class="ekdn-table">

| `ServiceStatus` | Means |
|---|---|
| `https://idctf.id/ns/19602/SvcStatus/granted` | The Root Authority has accredited the registration for this role, or accepts this CA or this key, from `StatusStartingTime` |
| `https://idctf.id/ns/19602/SvcStatus/suspended` | The Root Authority has suspended the registration from `StatusStartingTime`; a reader treats it as not accredited until a later status says otherwise |
| `https://idctf.id/ns/19602/SvcStatus/withdrawn` | The accreditation ended at `StatusStartingTime`, or the key stopped being accepted then; the entry stays as history |
| `https://idctf.id/ns/19602/SvcStatus/revoked` | The key this service names may not be trusted for any signature, whatever date the signature claims; `StatusStartingTime` records when the revocation took effect |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-01-031 }**REQ-TS-5-01-031** `ServiceStatus` MUST be one of the four values in [the table of statuses][tbl-ts-5-01-statuses].
- [](){ #req-ts-5-01-032 }**REQ-TS-5-01-032** A role service and a Verifier Issuing CA service MUST carry `granted`, `suspended`, or `withdrawn`.
- [](){ #req-ts-5-01-033 }**REQ-TS-5-01-033** A revoked key service MUST carry `revoked`.
- [](){ #req-ts-5-01-034 }**REQ-TS-5-01-034** A witness service and a trusted list signer service MUST carry `granted` or `withdrawn`.
- [](){ #req-ts-5-01-035 }**REQ-TS-5-01-035** When the Root Authority suspends or withdraws a registration, Trust Registry MUST set every role service and every Verifier Issuing CA service of that entry to the new status, with one `StatusStartingTime`.
- [](){ #req-ts-5-01-036 }**REQ-TS-5-01-036** When the Root Authority extends a suspension to every registration of one legal body, Trust Registry MUST set the services of every entry carrying that legal identifier to `suspended`.
- [](){ #req-ts-5-01-037 }**REQ-TS-5-01-037** `StatusStartingTime` MUST NOT be earlier than the `ListIssueDateTime` of the first list in which that status appears.

</div>

[REQ-TS-5-01-037][req-ts-5-01-037] is clause 6.6.5 of the standard: a status
that starts before the list announcing it was issued would change the outcome
of validations already made. A suspension stops at the one registration unless the Root Authority
extends it, which [the trusted list and cache][trusted-list-and-cache]
describes.

### Revoked keys {#ts-5-01-revoked-keys}

A key of a registration that is revoked before its DID Document or its
certificate stops presenting it is named in the entry, so that a reader can
refuse a signature made with it. The refusal does not depend on the date the
signature claims, because a thief can backdate one, as
[what happens to the old key][what-happens-to-the-old-key] sets out.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-01-038 }**REQ-TS-5-01-038** When the Root Authority revokes a key of a registration, Trust Registry MUST add to that entry one revoked key service naming the key, with `StatusStartingTime` the `ListIssueDateTime` of the first list that carries the service.
- [](){ #req-ts-5-01-039 }**REQ-TS-5-01-039** For a key published in a DID Document, the `ServiceDigitalIdentity` of a revoked key service MUST carry in `OtherIds` the public key as a `did:key` and the DID URL of its verification method.
- [](){ #req-ts-5-01-040 }**REQ-TS-5-01-040** For a key published in an X.509 certificate, the `ServiceDigitalIdentity` of a revoked key service MUST carry the subject key identifier of that certificate in `X509SKIs`.
- [](){ #req-ts-5-01-041 }**REQ-TS-5-01-041** A revoked key service MUST stay in the entry for as long as the list is published.

</div>

A reader matches a key it resolved from a DID Document against the entry by
encoding the public key as a `did:key` and comparing the two strings. The match
then does not depend on how either side serialized the key, and `did:key`
encodes any key type the DID Document may carry.

An X.509 key revoked early is also added to the certificate revocation list
(CRL) of [RFC 5280][ref-rfc5280] its issuer publishes, which an offline mdoc
reader checks. An online verifier refuses the key once its cached trusted list
names it, as [entity key revocation][entity-key-revocation] sets out.

### Trust Authority's own keys {#ts-5-01-trust-authoritys-own-keys}

Two of Trust Authority's keys are read from the trusted list: the witness
key every `did:webvh` log entry is countersigned with, and the key the list
itself is signed with. Both are services of the Root Authority's entry. A
witness key is published beside the old one during a rotation and struck
when stolen, as [the witness key][the-witness-key] describes; a signing key
is announced in a list before it signs one, as
[how Trust Authority's keys are replaced][how-trust-authoritys-keys-are-replaced]
describes. A key that leaves the list in the Architecture Framework's words is
a service set to `withdrawn` here, kept so that the time it stopped counting
stays readable.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-01-042 }**REQ-TS-5-01-042** The Root Authority's entry MUST carry one witness service for each `did:key` whose witness proofs readers accept, at status `granted`.
- [](){ #req-ts-5-01-043 }**REQ-TS-5-01-043** The Root Authority's entry MUST carry one trusted list signer service for each key that may sign the list, at status `granted`, with the public key as a `did:key` in `OtherIds`.
- [](){ #req-ts-5-01-044 }**REQ-TS-5-01-044** A key that stops being accepted as a witness or as a signer MUST be set to `withdrawn`, with `StatusStartingTime` the `ListIssueDateTime` of the first list that carries the status.
- [](){ #req-ts-5-01-045 }**REQ-TS-5-01-045** The Root Authority's entry MUST NOT carry a role service.

</div>

### History {#ts-5-01-history}

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-01-046 }**REQ-TS-5-01-046** Every change of a service's status MUST be recorded as a `ServiceHistoryInstance` in that service's `ServiceHistory`, in descending order of `StatusStartingTime`, as clause 6.4.4 of [ETSI TS 119 602][ref-etsi-ts-119602] requires.
- [](){ #req-ts-5-01-047 }**REQ-TS-5-01-047** A `ServiceHistoryInstance` MUST carry the `ServiceDigitalIdentity` that applied while that status was in force.
- [](){ #req-ts-5-01-048 }**REQ-TS-5-01-048** Trust Registry MUST NOT remove a history instance.

</div>

The history answers the question an incident asks: what the status
of a registration or a key was at a given time, rather than what it is now.

## Signature {#ts-5-01-signature}

The signing key is the trusted list key that
[Trust Authority's own keys][trust-authoritys-own-keys] names, held in
Trust Authority's hardware security module (HSM); Trust Registry publishes
what Trust Authority signed.

This is where the profile departs from clause 6.8 of the standard, which asks
for an Advanced Electronic Signature (AdES) at baseline level B, JAdES on the
JSON binding as the profile annexes name it. A JAdES signature carries a
signing certificate and a critical signing-time parameter that a plain JWS
verifier does not know, and three of the five readers are mobile applications
with plain JWS libraries. A reader verifies the list as a JWS and nothing
more.

The cost falls on a wallet from another ecosystem that validates the list as
clause 6.8 asks: it finds no JAdES signature, so it has to be told to verify
the list as a JWS, along with the pointer to the list it is handed under
recognition, as [the reader side][the-reader-side] sets out. The terms of
recognition say how it is told in
[what IDCTF hands over][gf-what-idctf-hands-over].

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-01-049 }**REQ-TS-5-01-049** The trusted list MUST be published as a JWS in the compact serialization of [RFC 7515][ref-rfc7515], whose payload is the LoTE JSON document.
- [](){ #req-ts-5-01-050 }**REQ-TS-5-01-050** The JWS MUST be signed with a key the Root Authority's entry names in a trusted list signer service at status `granted`.
- [](){ #req-ts-5-01-051 }**REQ-TS-5-01-051** The private key MUST be held in Trust Authority's HSM.
- [](){ #req-ts-5-01-052 }**REQ-TS-5-01-052** Trust Registry MUST NOT hold the private key.
- [](){ #req-ts-5-01-053 }**REQ-TS-5-01-053** The `alg` header parameter MUST be one the Governance Profile allows for the trusted list.
- [](){ #req-ts-5-01-054 }**REQ-TS-5-01-054** *Withdrawn: [REQ-TS-01-034][req-ts-01-034] covers it.*
- [](){ #req-ts-5-01-055 }**REQ-TS-5-01-055** The `kid` header parameter MUST name the signing key under `did:key`, as [Naming the key][ts-01-naming-the-key] of TS-01 requires and as the trusted list signer service names it.
- [](){ #req-ts-5-01-056 }**REQ-TS-5-01-056** Before a new signing key signs any list, the key MUST have been published as a trusted list signer service at status `granted` in a list signed with a key already accepted.

</div>

[REQ-TS-5-01-056][req-ts-5-01-056] lets the key rotate without asking
every reader to trust a new key on sight: a reader accepts a list under a new key only when
a list it already verified announced that key.

The protected header of the list shown in
[Trusted list payload][ts-5-01-trusted-list-payload], and the compact
serialization it sits in. The payload is the base64url encoding of that
JSON, byte for byte, and the signature is 64 bytes, the concatenation of `r` and `s`.

``` { .json title="trusted-list.json, the JWS protected header" data-format="JSON" }
{"alg":"ES256","kid":"did:key:zDnaeSCzChDqLTnobz1iquKetDC1piuwydzo3jkpiEHNwtX7q"}
```

``` { .text title="trusted-list.json, the JWS compact serialization" data-format="JWS" }
eyJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDprZXk6ekRuYWVTQ3pDaERxTFRub2J6MWlxdUtldERDMX
BpdXd5ZHpvM2prcGlFSE53dFg3cSJ9.ewogICJMb1RFIjogewogICAgIkxpc3RBbmRTY2hlbWVJbmZ
vcm1hdGlvbiI6IHsKICAgICAgIkxvVEVWZXJzaW9uSWRlbnRpZmllciI6IDEsCiAgICAgICJMb1RFU
2VxdWVuY2VOdW1iZXIiOiA0MiwKICAgICAgIkxvVEVUeXBlIjogImh0dHBzOi8vaWRjdGYuaWQvbnM
vMTk2MDIvTG9URVR5cGUvSURDVEZUcnVzdGVkTGlzdCIsCiAgICAgICJTY2hlbWVPcGVyYXRvck5hb
WUiOiBbCiAgICAgICAgeyAibGFuZyI6ICJpZCIsICJ2YWx1ZSI6ICJUcnVzdCBBdXRob3JpdHkgUmV
wdWJsaWsgSW5kb25lc2lhIiB9LAogICAgICAgIHsgImxhbmciOiAiZW4iLCAidmFsdWUiOiAiVHJ1c
3QgQXV0aG9yaXR5IFJlcHVibGlrIEluZG9uZXNpYSIgfQogICAgICBdLAogICAgICAiU2NoZW1lT3B
lcmF0b3JBZGRyZXNzIjogewogICAgICAgICJTY2hlbWVPcGVyYXRvclBvc3RhbEFkZHJlc3MiOiBbC
iAgICAgICAgICB7CiAgICAgICAgICAgICJsYW5nIjogImlkIiwKICAgICAgICAgICAgIlN0cmVldEF
kZHJlc3MiOiAiSmFsYW4gS2VwZXJjYXlhYW4gRGlnaXRhbCBOb21vciAxIiwKICAgICAgICAgICAgI
kxvY2FsaXR5IjogIkpha2FydGEiLAogICAgICAgICAgICAiQ291bnRyeSI6ICJJRCIKICAgICAgICA
gIH0sCiAgICAgICAgICB7CiAgICAgICAgICAgICJsYW5nIjogImVuIiwKICAgICAgICAgICAgIlN0c
mVldEFkZHJlc3MiOiAiSmFsYW4gS2VwZXJjYXlhYW4gRGlnaXRhbCBOb21vciAxIiwKICAgICAgICA
gICAgIkxvY2FsaXR5IjogIkpha2FydGEiLAogICAgICAgICAgICAiQ291bnRyeSI6ICJJRCIKICAgI
CAgICAgIH0KICAgICAgICBdLAogICAgICAgICJTY2hlbWVPcGVyYXRvckVsZWN0cm9uaWNBZGRyZXN
zIjogWwogICAgICAgICAgeyAibGFuZyI6ICJpZCIsICJ1cmlWYWx1ZSI6ICJtYWlsdG86dHJ1c3RAd
HJ1c3QuZ28uaWQiIH0sCiAgICAgICAgICB7ICJsYW5nIjogImVuIiwgInVyaVZhbHVlIjogIm1haWx
0bzp0cnVzdEB0cnVzdC5nby5pZCIgfSwKICAgICAgICAgIHsgImxhbmciOiAiaWQiLCAidXJpVmFsd
WUiOiAiaHR0cHM6Ly90cnVzdC5nby5pZCIgfSwKICAgICAgICAgIHsgImxhbmciOiAiZW4iLCAidXJ
pVmFsdWUiOiAiaHR0cHM6Ly90cnVzdC5nby5pZCIgfQogICAgICAgIF0KICAgICAgfSwKICAgICAgI
lNjaGVtZU5hbWUiOiBbCiAgICAgICAgeyAibGFuZyI6ICJpZCIsICJ2YWx1ZSI6ICJJRDpJbmRvbmV
zaWEgRGlnaXRhbCBDcmVkZW50aWFsIFRydXN0IEZyYW1ld29yayIgfSwKICAgICAgICB7ICJsYW5nI
jogImVuIiwgInZhbHVlIjogIklEOkluZG9uZXNpYSBEaWdpdGFsIENyZWRlbnRpYWwgVHJ1c3QgRnJ
hbWV3b3JrIiB9CiAgICAgIF0sCiAgICAgICJTY2hlbWVJbmZvcm1hdGlvblVSSSI6IFsKICAgICAgI
CB7ICJsYW5nIjogImlkIiwgInVyaVZhbHVlIjogImh0dHBzOi8vdHJ1c3QuZ28uaWQvaWRjdGYvZ29
2ZXJuYW5jZS1mcmFtZXdvcmsiIH0sCiAgICAgICAgeyAibGFuZyI6ICJlbiIsICJ1cmlWYWx1ZSI6I
CJodHRwczovL3RydXN0LmdvLmlkL2lkY3RmL2dvdmVybmFuY2UtZnJhbWV3b3JrIiB9CiAgICAgIF0
sCiAgICAgICJTdGF0dXNEZXRlcm1pbmF0aW9uQXBwcm9hY2giOiAiaHR0cHM6Ly9pZGN0Zi5pZC9uc
y8xOTYwMi9TdGF0dXNEZXRuL0lEQ1RGIiwKICAgICAgIlNjaGVtZVR5cGVDb21tdW5pdHlSdWxlcyI
6IFsKICAgICAgICB7ICJsYW5nIjogImlkIiwgInVyaVZhbHVlIjogImh0dHBzOi8vaWRjdGYuaWQvb
nMvMTk2MDIvc2NoZW1lcnVsZXMvSURDVEYiIH0sCiAgICAgICAgeyAibGFuZyI6ICJlbiIsICJ1cml
WYWx1ZSI6ICJodHRwczovL2lkY3RmLmlkL25zLzE5NjAyL3NjaGVtZXJ1bGVzL0lEQ1RGIiB9CiAgI
CAgIF0sCiAgICAgICJTY2hlbWVUZXJyaXRvcnkiOiAiSUQiLAogICAgICAiUG9saWN5T3JMZWdhbE5
vdGljZSI6IFsKICAgICAgICB7CiAgICAgICAgICAiTG9URVBvbGljeSI6IHsgImxhbmciOiAiaWQiL
CAidXJpVmFsdWUiOiAiaHR0cHM6Ly90cnVzdC5nby5pZC9pZGN0Zi9nb3Zlcm5hbmNlLWZyYW1ld29
yay9wb2xpY3kiIH0KICAgICAgICB9LAogICAgICAgIHsKICAgICAgICAgICJMb1RFUG9saWN5Ijoge
yAibGFuZyI6ICJlbiIsICJ1cmlWYWx1ZSI6ICJodHRwczovL3RydXN0LmdvLmlkL2lkY3RmL2dvdmV
ybmFuY2UtZnJhbWV3b3JrL3BvbGljeSIgfQogICAgICAgIH0KICAgICAgXSwKICAgICAgIkhpc3Rvc
mljYWxJbmZvcm1hdGlvblBlcmlvZCI6IDY1NTM1LAogICAgICAiTGlzdElzc3VlRGF0ZVRpbWUiOiA
iMjAyNi0xMC0xN1QwNjowMDowMFoiLAogICAgICAiTmV4dFVwZGF0ZSI6ICIyMDI2LTEwLTI0VDA2O
jAwOjAwWiIsCiAgICAgICJEaXN0cmlidXRpb25Qb2ludHMiOiBbImh0dHBzOi8vcmVnaXN0cnkudHJ
1c3QuZ28uaWQvdHJ1c3RlZC1saXN0Lmpzb24iXQogICAgfSwKICAgICJUcnVzdGVkRW50aXRpZXNMa
XN0IjogWwogICAgICB7CiAgICAgICAgIlRydXN0ZWRFbnRpdHlJbmZvcm1hdGlvbiI6IHsKICAgICA
gICAgICJURU5hbWUiOiBbCiAgICAgICAgICAgIHsgImxhbmciOiAiaWQiLCAidmFsdWUiOiAiRGlyZ
Wt0b3JhdCBKZW5kZXJhbCBLZXBlbmR1ZHVrYW4gZGFuIFBlbmNhdGF0YW4gU2lwaWwiIH0sCiAgICA
gICAgICAgIHsgImxhbmciOiAiZW4iLCAidmFsdWUiOiAiRGlyZWN0b3JhdGUgR2VuZXJhbCBvZiBQb
3B1bGF0aW9uIGFuZCBDaXZpbCBSZWdpc3RyYXRpb24iIH0KICAgICAgICAgIF0sCiAgICAgICAgICA
iVEVUcmFkZU5hbWUiOiBbCiAgICAgICAgICAgIHsgImxhbmciOiAiaWQiLCAidmFsdWUiOiAiQktOO
jAxMzI1MCIgfSwKICAgICAgICAgICAgeyAibGFuZyI6ICJlbiIsICJ2YWx1ZSI6ICJCS046MDEzMjU
wIiB9CiAgICAgICAgICBdLAogICAgICAgICAgIlRFQWRkcmVzcyI6IHsKICAgICAgICAgICAgIlRFU
G9zdGFsQWRkcmVzcyI6IFsKICAgICAgICAgICAgICB7CiAgICAgICAgICAgICAgICAibGFuZyI6ICJ
pZCIsCiAgICAgICAgICAgICAgICAiU3RyZWV0QWRkcmVzcyI6ICJKYWxhbiBSYXlhIEtlcGVuZHVkd
WthbiBOb21vciA3IiwKICAgICAgICAgICAgICAgICJMb2NhbGl0eSI6ICJKYWthcnRhIiwKICAgICA
gICAgICAgICAgICJDb3VudHJ5IjogIklEIgogICAgICAgICAgICAgIH0sCiAgICAgICAgICAgICAge
wogICAgICAgICAgICAgICAgImxhbmciOiAiZW4iLAogICAgICAgICAgICAgICAgIlN0cmVldEFkZHJ
lc3MiOiAiSmFsYW4gUmF5YSBLZXBlbmR1ZHVrYW4gTm9tb3IgNyIsCiAgICAgICAgICAgICAgICAiT
G9jYWxpdHkiOiAiSmFrYXJ0YSIsCiAgICAgICAgICAgICAgICAiQ291bnRyeSI6ICJJRCIKICAgICA
gICAgICAgICB9CiAgICAgICAgICAgIF0sCiAgICAgICAgICAgICJURUVsZWN0cm9uaWNBZGRyZXNzI
jogWwogICAgICAgICAgICAgIHsgImxhbmciOiAiaWQiLCAidXJpVmFsdWUiOiAibWFpbHRvOnBraUB
kdWtjYXBpbC5nby5pZCIgfSwKICAgICAgICAgICAgICB7ICJsYW5nIjogImVuIiwgInVyaVZhbHVlI
jogIm1haWx0bzpwa2lAZHVrY2FwaWwuZ28uaWQiIH0sCiAgICAgICAgICAgICAgeyAibGFuZyI6ICJ
pZCIsICJ1cmlWYWx1ZSI6ICJodHRwczovL2R1a2NhcGlsLmdvLmlkIiB9LAogICAgICAgICAgICAgI
HsgImxhbmciOiAiZW4iLCAidXJpVmFsdWUiOiAiaHR0cHM6Ly9kdWtjYXBpbC5nby5pZCIgfQogICA
gICAgICAgICBdCiAgICAgICAgICB9LAogICAgICAgICAgIlRFSW5mb3JtYXRpb25VUkkiOiBbCiAgI
CAgICAgICAgIHsgImxhbmciOiAiaWQiLCAidXJpVmFsdWUiOiAiaHR0cHM6Ly9kdWtjYXBpbC5nby5
pZCIgfSwKICAgICAgICAgICAgeyAibGFuZyI6ICJlbiIsICJ1cmlWYWx1ZSI6ICJodHRwczovL2R1a
2NhcGlsLmdvLmlkIiB9CiAgICAgICAgICBdCiAgICAgICAgfSwKICAgICAgICAiVHJ1c3RlZEVudGl
0eVNlcnZpY2VzIjogWwogICAgICAgICAgewogICAgICAgICAgICAiU2VydmljZUluZm9ybWF0aW9uI
jogewogICAgICAgICAgICAgICJTZXJ2aWNlVHlwZUlkZW50aWZpZXIiOiAiaHR0cHM6Ly9pZGN0Zi5
pZC9ucy8xOTYwMi9TdmNUeXBlL0lkZW50aXR5SXNzdWVyIiwKICAgICAgICAgICAgICAiU2VydmljZ
U5hbWUiOiBbCiAgICAgICAgICAgICAgICB7ICJsYW5nIjogImlkIiwgInZhbHVlIjogIklkZW50aXR
5IElzc3VlciIgfSwKICAgICAgICAgICAgICAgIHsgImxhbmciOiAiZW4iLCAidmFsdWUiOiAiSWRlb
nRpdHkgSXNzdWVyIiB9CiAgICAgICAgICAgICAgXSwKICAgICAgICAgICAgICAiU2VydmljZURpZ2l
0YWxJZGVudGl0eSI6IHsKICAgICAgICAgICAgICAgICJPdGhlcklkcyI6IFsiZGlkOndlYnZoOlFtY
0VWVDJpSlNyc3M1aGd3aU1Gc01VeEtrUm96Z0ZGNDU4UmNnZ1Q0TUYyTDQ6ZHVrY2FwaWwuZ28uaWQ
iXQogICAgICAgICAgICAgIH0sCiAgICAgICAgICAgICAgIlNlcnZpY2VTdGF0dXMiOiAiaHR0cHM6L
y9pZGN0Zi5pZC9ucy8xOTYwMi9TdmNTdGF0dXMvZ3JhbnRlZCIsCiAgICAgICAgICAgICAgIlN0YXR
1c1N0YXJ0aW5nVGltZSI6ICIyMDI2LTAyLTAxVDAwOjAwOjAwWiIKICAgICAgICAgICAgfQogICAgI
CAgICAgfSwKICAgICAgICAgIHsKICAgICAgICAgICAgIlNlcnZpY2VJbmZvcm1hdGlvbiI6IHsKICA
gICAgICAgICAgICAiU2VydmljZVR5cGVJZGVudGlmaWVyIjogImh0dHBzOi8vaWRjdGYuaWQvbnMvM
Tk2MDIvU3ZjVHlwZS9SZXZva2VkS2V5IiwKICAgICAgICAgICAgICAiU2VydmljZU5hbWUiOiBbCiA
gICAgICAgICAgICAgICB7ICJsYW5nIjogImlkIiwgInZhbHVlIjogIlJldm9rZWQga2V5IiB9LAogI
CAgICAgICAgICAgICAgeyAibGFuZyI6ICJlbiIsICJ2YWx1ZSI6ICJSZXZva2VkIGtleSIgfQogICA
gICAgICAgICAgIF0sCiAgICAgICAgICAgICAgIlNlcnZpY2VEaWdpdGFsSWRlbnRpdHkiOiB7CiAgI
CAgICAgICAgICAgICAiT3RoZXJJZHMiOiBbCiAgICAgICAgICAgICAgICAgICJkaWQ6a2V5OnpEbmF
lV1N3SkRyS0xyYUhlNXc0dkEzOXhGVzJUblphRERORUdHV1N5SFlTQzlOZnAiLAogICAgICAgICAgI
CAgICAgICAiZGlkOndlYnZoOlFtY0VWVDJpSlNyc3M1aGd3aU1Gc01VeEtrUm96Z0ZGNDU4UmNnZ1Q
0TUYyTDQ6ZHVrY2FwaWwuZ28uaWQjaXNzdWFuY2Utam9zZS0xIgogICAgICAgICAgICAgICAgXQogI
CAgICAgICAgICAgIH0sCiAgICAgICAgICAgICAgIlNlcnZpY2VTdGF0dXMiOiAiaHR0cHM6Ly9pZGN
0Zi5pZC9ucy8xOTYwMi9TdmNTdGF0dXMvcmV2b2tlZCIsCiAgICAgICAgICAgICAgIlN0YXR1c1N0Y
XJ0aW5nVGltZSI6ICIyMDI2LTEwLTE2VDE0OjA1OjAwWiIKICAgICAgICAgICAgfQogICAgICAgICA
gfSwKICAgICAgICAgIHsKICAgICAgICAgICAgIlNlcnZpY2VJbmZvcm1hdGlvbiI6IHsKICAgICAgI
CAgICAgICAiU2VydmljZVR5cGVJZGVudGlmaWVyIjogImh0dHBzOi8vaWRjdGYuaWQvbnMvMTk2MDI
vU3ZjVHlwZS9SZXZva2VkS2V5IiwKICAgICAgICAgICAgICAiU2VydmljZU5hbWUiOiBbCiAgICAgI
CAgICAgICAgICB7ICJsYW5nIjogImlkIiwgInZhbHVlIjogIlJldm9rZWQga2V5IiB9LAogICAgICA
gICAgICAgICAgeyAibGFuZyI6ICJlbiIsICJ2YWx1ZSI6ICJSZXZva2VkIGtleSIgfQogICAgICAgI
CAgICAgIF0sCiAgICAgICAgICAgICAgIlNlcnZpY2VEaWdpdGFsSWRlbnRpdHkiOiB7CiAgICAgICA
gICAgICAgICAiWDUwOVNLSXMiOiBbIkQ1MENBQTY1QjQ2MEUxMDQwMkQzOTcyRjczQjgzMERCOEIwM
0RBMjgiXQogICAgICAgICAgICAgIH0sCiAgICAgICAgICAgICAgIlNlcnZpY2VTdGF0dXMiOiAiaHR
0cHM6Ly9pZGN0Zi5pZC9ucy8xOTYwMi9TdmNTdGF0dXMvcmV2b2tlZCIsCiAgICAgICAgICAgICAgI
lN0YXR1c1N0YXJ0aW5nVGltZSI6ICIyMDI2LTA5LTE1VDAwOjAwOjAwWiIKICAgICAgICAgICAgfQo
gICAgICAgICAgfQogICAgICAgIF0KICAgICAgfSwKICAgICAgewogICAgICAgICJUcnVzdGVkRW50a
XR5SW5mb3JtYXRpb24iOiB7CiAgICAgICAgICAiVEVOYW1lIjogWwogICAgICAgICAgICB7ICJsYW5
nIjogImlkIiwgInZhbHVlIjogIlBUIERvbXBldCBEaWdpdGFsIE51c2FudGFyYSIgfSwKICAgICAgI
CAgICAgeyAibGFuZyI6ICJlbiIsICJ2YWx1ZSI6ICJQVCBEb21wZXQgRGlnaXRhbCBOdXNhbnRhcmE
iIH0KICAgICAgICAgIF0sCiAgICAgICAgICAiVEVUcmFkZU5hbWUiOiBbCiAgICAgICAgICAgIHsgI
mxhbmciOiAiaWQiLCAidmFsdWUiOiAiTklCOjkxMjA0MDcyNjAwMzEiIH0sCiAgICAgICAgICAgIHs
gImxhbmciOiAiZW4iLCAidmFsdWUiOiAiTklCOjkxMjA0MDcyNjAwMzEiIH0KICAgICAgICAgIF0sC
iAgICAgICAgICAiVEVBZGRyZXNzIjogewogICAgICAgICAgICAiVEVQb3N0YWxBZGRyZXNzIjogWwo
gICAgICAgICAgICAgIHsKICAgICAgICAgICAgICAgICJsYW5nIjogImlkIiwKICAgICAgICAgICAgI
CAgICJTdHJlZXRBZGRyZXNzIjogIkphbGFuIEdhdG90IFN1YnJvdG8gS2F2bGluZyAxOCIsCiAgICA
gICAgICAgICAgICAiTG9jYWxpdHkiOiAiSmFrYXJ0YSIsCiAgICAgICAgICAgICAgICAiQ291bnRye
SI6ICJJRCIKICAgICAgICAgICAgICB9LAogICAgICAgICAgICAgIHsKICAgICAgICAgICAgICAgICJ
sYW5nIjogImVuIiwKICAgICAgICAgICAgICAgICJTdHJlZXRBZGRyZXNzIjogIkphbGFuIEdhdG90I
FN1YnJvdG8gS2F2bGluZyAxOCIsCiAgICAgICAgICAgICAgICAiTG9jYWxpdHkiOiAiSmFrYXJ0YSI
sCiAgICAgICAgICAgICAgICAiQ291bnRyeSI6ICJJRCIKICAgICAgICAgICAgICB9CiAgICAgICAgI
CAgIF0sCiAgICAgICAgICAgICJURUVsZWN0cm9uaWNBZGRyZXNzIjogWwogICAgICAgICAgICAgIHs
gImxhbmciOiAiaWQiLCAidXJpVmFsdWUiOiAibWFpbHRvOnBraUBkb21wZXQuY28uaWQiIH0sCiAgI
CAgICAgICAgICAgeyAibGFuZyI6ICJlbiIsICJ1cmlWYWx1ZSI6ICJtYWlsdG86cGtpQGRvbXBldC5
jby5pZCIgfSwKICAgICAgICAgICAgICB7ICJsYW5nIjogImlkIiwgInVyaVZhbHVlIjogImh0dHBzO
i8vZG9tcGV0LmNvLmlkIiB9LAogICAgICAgICAgICAgIHsgImxhbmciOiAiZW4iLCAidXJpVmFsdWU
iOiAiaHR0cHM6Ly9kb21wZXQuY28uaWQiIH0KICAgICAgICAgICAgXQogICAgICAgICAgfSwKICAgI
CAgICAgICJURUluZm9ybWF0aW9uVVJJIjogWwogICAgICAgICAgICB7ICJsYW5nIjogImlkIiwgInV
yaVZhbHVlIjogImh0dHBzOi8vZG9tcGV0LmNvLmlkIiB9LAogICAgICAgICAgICB7ICJsYW5nIjogI
mVuIiwgInVyaVZhbHVlIjogImh0dHBzOi8vZG9tcGV0LmNvLmlkIiB9CiAgICAgICAgICBdCiAgICA
gICAgfSwKICAgICAgICAiVHJ1c3RlZEVudGl0eVNlcnZpY2VzIjogWwogICAgICAgICAgewogICAgI
CAgICAgICAiU2VydmljZUluZm9ybWF0aW9uIjogewogICAgICAgICAgICAgICJTZXJ2aWNlVHlwZUl
kZW50aWZpZXIiOiAiaHR0cHM6Ly9pZGN0Zi5pZC9ucy8xOTYwMi9TdmNUeXBlL1dhbGxldFByb3ZpZ
GVyIiwKICAgICAgICAgICAgICAiU2VydmljZU5hbWUiOiBbCiAgICAgICAgICAgICAgICB7ICJsYW5
nIjogImlkIiwgInZhbHVlIjogIldhbGxldCBQcm92aWRlciIgfSwKICAgICAgICAgICAgICAgIHsgI
mxhbmciOiAiZW4iLCAidmFsdWUiOiAiV2FsbGV0IFByb3ZpZGVyIiB9CiAgICAgICAgICAgICAgXSw
KICAgICAgICAgICAgICAiU2VydmljZURpZ2l0YWxJZGVudGl0eSI6IHsKICAgICAgICAgICAgICAgI
CJPdGhlcklkcyI6IFsiZGlkOndlYnZoOlFtZVRXMTM0cWpVQzZFS1hVNkpMM2RWUmdkM2ZZbVVwTWJ
vb0VEb2tTcEZFQUg6ZG9tcGV0LmNvLmlkIl0KICAgICAgICAgICAgICB9LAogICAgICAgICAgICAgI
CJTZXJ2aWNlU3RhdHVzIjogImh0dHBzOi8vaWRjdGYuaWQvbnMvMTk2MDIvU3ZjU3RhdHVzL2dyYW5
0ZWQiLAogICAgICAgICAgICAgICJTdGF0dXNTdGFydGluZ1RpbWUiOiAiMjAyNi0wMy0wMVQwMDowM
DowMFoiCiAgICAgICAgICAgIH0KICAgICAgICAgIH0KICAgICAgICBdCiAgICAgIH0sCiAgICAgIHs
KICAgICAgICAiVHJ1c3RlZEVudGl0eUluZm9ybWF0aW9uIjogewogICAgICAgICAgIlRFTmFtZSI6I
FsKICAgICAgICAgICAgeyAibGFuZyI6ICJpZCIsICJ2YWx1ZSI6ICJQVCBUZXJtaW5hbCBOdXNhbnR
hcmEiIH0sCiAgICAgICAgICAgIHsgImxhbmciOiAiZW4iLCAidmFsdWUiOiAiUFQgVGVybWluYWwgT
nVzYW50YXJhIiB9CiAgICAgICAgICBdLAogICAgICAgICAgIlRFVHJhZGVOYW1lIjogWwogICAgICA
gICAgICB7ICJsYW5nIjogImlkIiwgInZhbHVlIjogIk5JQjo4MTIwMDE1NjQwMDIyIiB9LAogICAgI
CAgICAgICB7ICJsYW5nIjogImVuIiwgInZhbHVlIjogIk5JQjo4MTIwMDE1NjQwMDIyIiB9CiAgICA
gICAgICBdLAogICAgICAgICAgIlRFQWRkcmVzcyI6IHsKICAgICAgICAgICAgIlRFUG9zdGFsQWRkc
mVzcyI6IFsKICAgICAgICAgICAgICB7ICJsYW5nIjogImlkIiwgIlN0cmVldEFkZHJlc3MiOiAiSmF
sYW4gQXNpYSBBZnJpa2EgTm9tb3IgMTEyIiwgIkxvY2FsaXR5IjogIkJhbmR1bmciLCAiQ291bnRye
SI6ICJJRCIgfSwKICAgICAgICAgICAgICB7ICJsYW5nIjogImVuIiwgIlN0cmVldEFkZHJlc3MiOiA
iSmFsYW4gQXNpYSBBZnJpa2EgTm9tb3IgMTEyIiwgIkxvY2FsaXR5IjogIkJhbmR1bmciLCAiQ291b
nRyeSI6ICJJRCIgfQogICAgICAgICAgICBdLAogICAgICAgICAgICAiVEVFbGVjdHJvbmljQWRkcmV
zcyI6IFsKICAgICAgICAgICAgICB7ICJsYW5nIjogImlkIiwgInVyaVZhbHVlIjogIm1haWx0bzpwa
2lAdGVybWluYWwtbnVzYW50YXJhLmNvLmlkIiB9LAogICAgICAgICAgICAgIHsgImxhbmciOiAiZW4
iLCAidXJpVmFsdWUiOiAibWFpbHRvOnBraUB0ZXJtaW5hbC1udXNhbnRhcmEuY28uaWQiIH0sCiAgI
CAgICAgICAgICAgeyAibGFuZyI6ICJpZCIsICJ1cmlWYWx1ZSI6ICJodHRwczovL3Rlcm1pbmFsLW5
1c2FudGFyYS5jby5pZCIgfSwKICAgICAgICAgICAgICB7ICJsYW5nIjogImVuIiwgInVyaVZhbHVlI
jogImh0dHBzOi8vdGVybWluYWwtbnVzYW50YXJhLmNvLmlkIiB9CiAgICAgICAgICAgIF0KICAgICA
gICAgIH0sCiAgICAgICAgICAiVEVJbmZvcm1hdGlvblVSSSI6IFsKICAgICAgICAgICAgeyAibGFuZ
yI6ICJpZCIsICJ1cmlWYWx1ZSI6ICJodHRwczovL3Rlcm1pbmFsLW51c2FudGFyYS5jby5pZCIgfSw
KICAgICAgICAgICAgeyAibGFuZyI6ICJlbiIsICJ1cmlWYWx1ZSI6ICJodHRwczovL3Rlcm1pbmFsL
W51c2FudGFyYS5jby5pZCIgfQogICAgICAgICAgXQogICAgICAgIH0sCiAgICAgICAgIlRydXN0ZWR
FbnRpdHlTZXJ2aWNlcyI6IFsKICAgICAgICAgIHsKICAgICAgICAgICAgIlNlcnZpY2VJbmZvcm1hd
GlvbiI6IHsKICAgICAgICAgICAgICAiU2VydmljZVR5cGVJZGVudGlmaWVyIjogImh0dHBzOi8vaWR
jdGYuaWQvbnMvMTk2MDIvU3ZjVHlwZS9SZWx5aW5nUGFydHkiLAogICAgICAgICAgICAgICJTZXJ2a
WNlTmFtZSI6IFsKICAgICAgICAgICAgICAgIHsgImxhbmciOiAiaWQiLCAidmFsdWUiOiAiUmVseWl
uZyBQYXJ0eSIgfSwKICAgICAgICAgICAgICAgIHsgImxhbmciOiAiZW4iLCAidmFsdWUiOiAiUmVse
WluZyBQYXJ0eSIgfQogICAgICAgICAgICAgIF0sCiAgICAgICAgICAgICAgIlNlcnZpY2VEaWdpdGF
sSWRlbnRpdHkiOiB7CiAgICAgICAgICAgICAgICAiT3RoZXJJZHMiOiBbImRpZDp3ZWJ2aDpRbVVBV
EM1anlmNXlWeTcyR1lBcDhuU3Z1d3NoekR5NndZWDdXbU5ZNVVKdFhUOnRlcm1pbmFsLW51c2FudGF
yYS5jby5pZCJdCiAgICAgICAgICAgICAgfSwKICAgICAgICAgICAgICAiU2VydmljZVN0YXR1cyI6I
CJodHRwczovL2lkY3RmLmlkL25zLzE5NjAyL1N2Y1N0YXR1cy9ncmFudGVkIiwKICAgICAgICAgICA
gICAiU3RhdHVzU3RhcnRpbmdUaW1lIjogIjIwMjYtMDktMDFUMDA6MDA6MDBaIgogICAgICAgICAgI
CB9LAogICAgICAgICAgICAiU2VydmljZUhpc3RvcnkiOiBbCiAgICAgICAgICAgICAgewogICAgICA
gICAgICAgICAgIlNlcnZpY2VOYW1lIjogWwogICAgICAgICAgICAgICAgICB7ICJsYW5nIjogImlkI
iwgInZhbHVlIjogIlJlbHlpbmcgUGFydHkiIH0sCiAgICAgICAgICAgICAgICAgIHsgImxhbmciOiA
iZW4iLCAidmFsdWUiOiAiUmVseWluZyBQYXJ0eSIgfQogICAgICAgICAgICAgICAgXSwKICAgICAgI
CAgICAgICAgICJTZXJ2aWNlRGlnaXRhbElkZW50aXR5IjogewogICAgICAgICAgICAgICAgICAiT3R
oZXJJZHMiOiBbImRpZDp3ZWJ2aDpRbVVBVEM1anlmNXlWeTcyR1lBcDhuU3Z1d3NoekR5NndZWDdXb
U5ZNVVKdFhUOnRlcm1pbmFsLW51c2FudGFyYS5jby5pZCJdCiAgICAgICAgICAgICAgICB9LAogICA
gICAgICAgICAgICAgIlNlcnZpY2VTdGF0dXMiOiAiaHR0cHM6Ly9pZGN0Zi5pZC9ucy8xOTYwMi9Td
mNTdGF0dXMvc3VzcGVuZGVkIiwKICAgICAgICAgICAgICAgICJTdGF0dXNTdGFydGluZ1RpbWUiOiA
iMjAyNi0wOC0yMFQwOTozMDowMFoiLAogICAgICAgICAgICAgICAgIlNlcnZpY2VUeXBlSWRlbnRpZ
mllciI6ICJodHRwczovL2lkY3RmLmlkL25zLzE5NjAyL1N2Y1R5cGUvUmVseWluZ1BhcnR5IgogICA
gICAgICAgICAgIH0sCiAgICAgICAgICAgICAgewogICAgICAgICAgICAgICAgIlNlcnZpY2VOYW1lI
jogWwogICAgICAgICAgICAgICAgICB7ICJsYW5nIjogImlkIiwgInZhbHVlIjogIlJlbHlpbmcgUGF
ydHkiIH0sCiAgICAgICAgICAgICAgICAgIHsgImxhbmciOiAiZW4iLCAidmFsdWUiOiAiUmVseWluZ
yBQYXJ0eSIgfQogICAgICAgICAgICAgICAgXSwKICAgICAgICAgICAgICAgICJTZXJ2aWNlRGlnaXR
hbElkZW50aXR5IjogewogICAgICAgICAgICAgICAgICAiT3RoZXJJZHMiOiBbImRpZDp3ZWJ2aDpRb
VVBVEM1anlmNXlWeTcyR1lBcDhuU3Z1d3NoekR5NndZWDdXbU5ZNVVKdFhUOnRlcm1pbmFsLW51c2F
udGFyYS5jby5pZCJdCiAgICAgICAgICAgICAgICB9LAogICAgICAgICAgICAgICAgIlNlcnZpY2VTd
GF0dXMiOiAiaHR0cHM6Ly9pZGN0Zi5pZC9ucy8xOTYwMi9TdmNTdGF0dXMvZ3JhbnRlZCIsCiAgICA
gICAgICAgICAgICAiU3RhdHVzU3RhcnRpbmdUaW1lIjogIjIwMjYtMDMtMDFUMDA6MDA6MDBaIiwKI
CAgICAgICAgICAgICAgICJTZXJ2aWNlVHlwZUlkZW50aWZpZXIiOiAiaHR0cHM6Ly9pZGN0Zi5pZC9
ucy8xOTYwMi9TdmNUeXBlL1JlbHlpbmdQYXJ0eSIKICAgICAgICAgICAgICB9CiAgICAgICAgICAgI
F0KICAgICAgICAgIH0sCiAgICAgICAgICB7CiAgICAgICAgICAgICJTZXJ2aWNlSW5mb3JtYXRpb24
iOiB7CiAgICAgICAgICAgICAgIlNlcnZpY2VUeXBlSWRlbnRpZmllciI6ICJodHRwczovL2lkY3RmL
mlkL25zLzE5NjAyL1N2Y1R5cGUvVmVyaWZpZXJJc3N1aW5nQ0EiLAogICAgICAgICAgICAgICJTZXJ
2aWNlTmFtZSI6IFsKICAgICAgICAgICAgICAgIHsgImxhbmciOiAiaWQiLCAidmFsdWUiOiAiVmVya
WZpZXIgSXNzdWluZyBDQSIgfSwKICAgICAgICAgICAgICAgIHsgImxhbmciOiAiZW4iLCAidmFsdWU
iOiAiVmVyaWZpZXIgSXNzdWluZyBDQSIgfQogICAgICAgICAgICAgIF0sCiAgICAgICAgICAgICAgI
lNlcnZpY2VEaWdpdGFsSWRlbnRpdHkiOiB7CiAgICAgICAgICAgICAgICAiWDUwOVNLSXMiOiBbIjJ
FQTNCNkY1QTFEM0U3RjdGOTIwNjA1RUZGRTg4MEEwNTk4MTc5MzMiXSwKICAgICAgICAgICAgICAgI
CJYNTA5Q2VydGlmaWNhdGVzIjogWwogICAgICAgICAgICAgICAgICB7CiAgICAgICAgICAgICAgICA
gICAgInZhbCI6ICJNSUlDY0RDQ0FoZWdBd0lCQWdJTkFMV0p6ZlliaUo2L0Nwek9CVEFLQmdncWhra
k9QUVFEQWpCYk1Rc3dDUVlEVlFRR0V3SkpSREVyTUNrR0ExVUVDZ3dpVkhKMWMzUWdRWFYwYUc5eWF
YUjVJRkpsY0hWaWJHbHJJRWx1Wkc5dVpYTnBZVEVmTUIwR0ExVUVBd3dXU1VSRFZFWWdWbVZ5YVdac
FpYSWdVbTl2ZENCRFFUQWVGdzB5TmpBMk1ERXdNREF3TURCYUZ3MHpNVEEyTURFd01EQXdNREJhTUZ
zeEN6QUpCZ05WQkFZVEFrbEVNUnN3R1FZRFZRUUtEQkpVWlhKdGFXNWhiQ0JPZFhOaGJuUmhjbUV4T
HpBdEJnTlZCQU1NSmxSbGNtMXBibUZzSUU1MWMyRnVkR0Z5WVNCV1pYSnBabWxsY2lCSmMzTjFhVzV
uSUVOQk1Ga3dFd1lIS29aSXpqMENBUVlJS29aSXpqMERBUWNEUWdBRWxVRjFoc1d1QmdJcnRTZjkzR
jkzTjl4YzAxSVlRRzdOc3orOEErRVY3SXJ4Z1dZek0wR1BhVFlNQyt6NjBzQldqVnZ1Z05CMGJ1dDJ
2ODluUlE5L2ZhT0J2ekNCdkRBU0JnTlZIUk1CQWY4RUNEQUdBUUgvQWdFQU1BNEdBMVVkRHdFQi93U
UVBd0lCQmpBU0JnTlZIU1VFQ3pBSkJnY29nWXhkQlFFR01COEdBMVVkSXdRWU1CYUFGRm5GOEVONGF
IZkc0dUtoSlVTa01EMUs3Z1R6TUIwR0ExVWREZ1FXQkJRdW83YjFvZFBuOS9rZ1lGNy82SUNnV1lGN
U16QkNCZ05WSFI4RU96QTVNRGVnTmFBemhqRm9kSFJ3Y3pvdkwzSmxaMmx6ZEhKNUxuUnlkWE4wTG1
kdkxtbGtMMk55YkM5MlpYSnBabWxsY2kxeWIyOTBMV05oTUFvR0NDcUdTTTQ5QkFNQ0EwY0FNRVFDS
UNHMmlTTEl1dk0xRjhuMFpqek5WUkJoc1kvYVdSZTZzOUJNQm1oTjdQTkdBaUFTejMrU0NQT3Z1Vmc
0UDgrcUlmYWVHdGt1TzRNdjEzc2ZaZ0taejZybHJRPT0iCiAgICAgICAgICAgICAgICAgIH0KICAgI
CAgICAgICAgICAgIF0KICAgICAgICAgICAgICB9LAogICAgICAgICAgICAgICJTZXJ2aWNlU3RhdHV
zIjogImh0dHBzOi8vaWRjdGYuaWQvbnMvMTk2MDIvU3ZjU3RhdHVzL2dyYW50ZWQiLAogICAgICAgI
CAgICAgICJTdGF0dXNTdGFydGluZ1RpbWUiOiAiMjAyNi0wOS0wMVQwMDowMDowMFoiCiAgICAgICA
gICAgIH0sCiAgICAgICAgICAgICJTZXJ2aWNlSGlzdG9yeSI6IFsKICAgICAgICAgICAgICB7CiAgI
CAgICAgICAgICAgICAiU2VydmljZU5hbWUiOiBbCiAgICAgICAgICAgICAgICAgIHsgImxhbmciOiA
iaWQiLCAidmFsdWUiOiAiVmVyaWZpZXIgSXNzdWluZyBDQSIgfSwKICAgICAgICAgICAgICAgICAge
yAibGFuZyI6ICJlbiIsICJ2YWx1ZSI6ICJWZXJpZmllciBJc3N1aW5nIENBIiB9CiAgICAgICAgICA
gICAgICBdLAogICAgICAgICAgICAgICAgIlNlcnZpY2VEaWdpdGFsSWRlbnRpdHkiOiB7CiAgICAgI
CAgICAgICAgICAgICJYNTA5U0tJcyI6IFsiMkVBM0I2RjVBMUQzRTdGN0Y5MjA2MDVFRkZFODgwQTA
1OTgxNzkzMyJdLAogICAgICAgICAgICAgICAgICAiWDUwOUNlcnRpZmljYXRlcyI6IFsKICAgICAgI
CAgICAgICAgICAgICB7CiAgICAgICAgICAgICAgICAgICAgICAidmFsIjogIk1JSUNjRENDQWhlZ0F
3SUJBZ0lOQUxXSnpmWWJpSjYvQ3B6T0JUQUtCZ2dxaGtqT1BRUURBakJiTVFzd0NRWURWUVFHRXdKS
lJERXJNQ2tHQTFVRUNnd2lWSEoxYzNRZ1FYVjBhRzl5YVhSNUlGSmxjSFZpYkdscklFbHVaRzl1Wlh
OcFlURWZNQjBHQTFVRUF3d1dTVVJEVkVZZ1ZtVnlhV1pwWlhJZ1VtOXZkQ0JEUVRBZUZ3MHlOakEyT
URFd01EQXdNREJhRncwek1UQTJNREV3TURBd01EQmFNRnN4Q3pBSkJnTlZCQVlUQWtsRU1Sc3dHUVl
EVlFRS0RCSlVaWEp0YVc1aGJDQk9kWE5oYm5SaGNtRXhMekF0QmdOVkJBTU1KbFJsY20xcGJtRnNJR
TUxYzJGdWRHRnlZU0JXWlhKcFptbGxjaUJKYzNOMWFXNW5JRU5CTUZrd0V3WUhLb1pJemowQ0FRWUl
Lb1pJemowREFRY0RRZ0FFbFVGMWhzV3VCZ0lydFNmOTNGOTNOOXhjMDFJWVFHN05zeis4QStFVjdJc
nhnV1l6TTBHUGFUWU1DK3o2MHNCV2pWdnVnTkIwYnV0MnY4OW5SUTkvZmFPQnZ6Q0J2REFTQmdOVkh
STUJBZjhFQ0RBR0FRSC9BZ0VBTUE0R0ExVWREd0VCL3dRRUF3SUJCakFTQmdOVkhTVUVDekFKQmdjb
2dZeGRCUUVHTUI4R0ExVWRJd1FZTUJhQUZGbkY4RU40YUhmRzR1S2hKVVNrTUQxSzdnVHpNQjBHQTF
VZERnUVdCQlF1bzdiMW9kUG45L2tnWUY3LzZJQ2dXWUY1TXpCQ0JnTlZIUjhFT3pBNU1EZWdOYUF6a
GpGb2RIUndjem92TDNKbFoybHpkSEo1TG5SeWRYTjBMbWR2TG1sa0wyTnliQzkyWlhKcFptbGxjaTF
5YjI5MExXTmhNQW9HQ0NxR1NNNDlCQU1DQTBjQU1FUUNJQ0cyaVNMSXV2TTFGOG4wWmp6TlZSQmhzW
S9hV1JlNnM5Qk1CbWhON1BOR0FpQVN6MytTQ1BPdnVWZzRQOCtxSWZhZUd0a3VPNE12MTNzZlpnS1p
6NnJsclE9PSIKICAgICAgICAgICAgICAgICAgICB9CiAgICAgICAgICAgICAgICAgIF0KICAgICAgI
CAgICAgICAgIH0sCiAgICAgICAgICAgICAgICAiU2VydmljZVN0YXR1cyI6ICJodHRwczovL2lkY3R
mLmlkL25zLzE5NjAyL1N2Y1N0YXR1cy9zdXNwZW5kZWQiLAogICAgICAgICAgICAgICAgIlN0YXR1c
1N0YXJ0aW5nVGltZSI6ICIyMDI2LTA4LTIwVDA5OjMwOjAwWiIsCiAgICAgICAgICAgICAgICAiU2V
ydmljZVR5cGVJZGVudGlmaWVyIjogImh0dHBzOi8vaWRjdGYuaWQvbnMvMTk2MDIvU3ZjVHlwZS9WZ
XJpZmllcklzc3VpbmdDQSIKICAgICAgICAgICAgICB9LAogICAgICAgICAgICAgIHsKICAgICAgICA
gICAgICAgICJTZXJ2aWNlTmFtZSI6IFsKICAgICAgICAgICAgICAgICAgeyAibGFuZyI6ICJpZCIsI
CJ2YWx1ZSI6ICJWZXJpZmllciBJc3N1aW5nIENBIiB9LAogICAgICAgICAgICAgICAgICB7ICJsYW5
nIjogImVuIiwgInZhbHVlIjogIlZlcmlmaWVyIElzc3VpbmcgQ0EiIH0KICAgICAgICAgICAgICAgI
F0sCiAgICAgICAgICAgICAgICAiU2VydmljZURpZ2l0YWxJZGVudGl0eSI6IHsKICAgICAgICAgICA
gICAgICAgIlg1MDlTS0lzIjogWyIyRUEzQjZGNUExRDNFN0Y3RjkyMDYwNUVGRkU4ODBBMDU5ODE3O
TMzIl0sCiAgICAgICAgICAgICAgICAgICJYNTA5Q2VydGlmaWNhdGVzIjogWwogICAgICAgICAgICA
gICAgICAgIHsKICAgICAgICAgICAgICAgICAgICAgICJ2YWwiOiAiTUlJQ2NEQ0NBaGVnQXdJQkFnS
U5BTFdKemZZYmlKNi9DcHpPQlRBS0JnZ3Foa2pPUFFRREFqQmJNUXN3Q1FZRFZRUUdFd0pKUkRFck1
Da0dBMVVFQ2d3aVZISjFjM1FnUVhWMGFHOXlhWFI1SUZKbGNIVmliR2xySUVsdVpHOXVaWE5wWVRFZ
k1CMEdBMVVFQXd3V1NVUkRWRVlnVm1WeWFXWnBaWElnVW05dmRDQkRRVEFlRncweU5qQTJNREV3TUR
Bd01EQmFGdzB6TVRBMk1ERXdNREF3TURCYU1Gc3hDekFKQmdOVkJBWVRBa2xFTVJzd0dRWURWUVFLR
EJKVVpYSnRhVzVoYkNCT2RYTmhiblJoY21FeEx6QXRCZ05WQkFNTUpsUmxjbTFwYm1Gc0lFNTFjMkZ
1ZEdGeVlTQldaWEpwWm1sbGNpQkpjM04xYVc1bklFTkJNRmt3RXdZSEtvWkl6ajBDQVFZSUtvWkl6a
jBEQVFjRFFnQUVsVUYxaHNXdUJnSXJ0U2Y5M0Y5M045eGMwMUlZUUc3TnN6KzhBK0VWN0lyeGdXWXp
NMEdQYVRZTUMrejYwc0JXalZ2dWdOQjBidXQydjg5blJROS9mYU9CdnpDQnZEQVNCZ05WSFJNQkFmO
EVDREFHQVFIL0FnRUFNQTRHQTFVZER3RUIvd1FFQXdJQkJqQVNCZ05WSFNVRUN6QUpCZ2NvZ1l4ZEJ
RRUdNQjhHQTFVZEl3UVlNQmFBRkZuRjhFTjRhSGZHNHVLaEpVU2tNRDFLN2dUek1CMEdBMVVkRGdRV
0JCUXVvN2Ixb2RQbjkva2dZRjcvNklDZ1dZRjVNekJDQmdOVkhSOEVPekE1TURlZ05hQXpoakZvZEh
Sd2N6b3ZMM0psWjJsemRISjVMblJ5ZFhOMExtZHZMbWxrTDJOeWJDOTJaWEpwWm1sbGNpMXliMjkwT
FdOaE1Bb0dDQ3FHU000OUJBTUNBMGNBTUVRQ0lDRzJpU0xJdXZNMUY4bjBaanpOVlJCaHNZL2FXUmU
2czlCTUJtaE43UE5HQWlBU3ozK1NDUE92dVZnNFA4K3FJZmFlR3RrdU80TXYxM3NmWmdLWno2cmxyU
T09IgogICAgICAgICAgICAgICAgICAgIH0KICAgICAgICAgICAgICAgICAgXQogICAgICAgICAgICA
gICAgfSwKICAgICAgICAgICAgICAgICJTZXJ2aWNlU3RhdHVzIjogImh0dHBzOi8vaWRjdGYuaWQvb
nMvMTk2MDIvU3ZjU3RhdHVzL2dyYW50ZWQiLAogICAgICAgICAgICAgICAgIlN0YXR1c1N0YXJ0aW5
nVGltZSI6ICIyMDI2LTA2LTAxVDAwOjAwOjAwWiIsCiAgICAgICAgICAgICAgICAiU2VydmljZVR5c
GVJZGVudGlmaWVyIjogImh0dHBzOi8vaWRjdGYuaWQvbnMvMTk2MDIvU3ZjVHlwZS9WZXJpZmllckl
zc3VpbmdDQSIKICAgICAgICAgICAgICB9CiAgICAgICAgICAgIF0KICAgICAgICAgIH0KICAgICAgI
CBdCiAgICAgIH0sCiAgICAgIHsKICAgICAgICAiVHJ1c3RlZEVudGl0eUluZm9ybWF0aW9uIjogewo
gICAgICAgICAgIlRFTmFtZSI6IFsKICAgICAgICAgICAgeyAibGFuZyI6ICJpZCIsICJ2YWx1ZSI6I
CJVbml2ZXJzaXRhcyBOZWdlcmkgTnVzYW50YXJhIiB9LAogICAgICAgICAgICB7ICJsYW5nIjogImV
uIiwgInZhbHVlIjogIlVuaXZlcnNpdGFzIE5lZ2VyaSBOdXNhbnRhcmEiIH0KICAgICAgICAgIF0sC
iAgICAgICAgICAiVEVUcmFkZU5hbWUiOiBbCiAgICAgICAgICAgIHsgImxhbmciOiAiaWQiLCAidmF
sdWUiOiAiQktOOjQwMTE2MCIgfSwKICAgICAgICAgICAgeyAibGFuZyI6ICJlbiIsICJ2YWx1ZSI6I
CJCS046NDAxMTYwIiB9CiAgICAgICAgICBdLAogICAgICAgICAgIlRFQWRkcmVzcyI6IHsKICAgICA
gICAgICAgIlRFUG9zdGFsQWRkcmVzcyI6IFsKICAgICAgICAgICAgICB7ICJsYW5nIjogImlkIiwgI
lN0cmVldEFkZHJlc3MiOiAiSmFsYW4gUGVuZGlkaWthbiBOb21vciA0NSIsICJMb2NhbGl0eSI6ICJ
KYWthcnRhIiwgIkNvdW50cnkiOiAiSUQiIH0sCiAgICAgICAgICAgICAgeyAibGFuZyI6ICJlbiIsI
CJTdHJlZXRBZGRyZXNzIjogIkphbGFuIFBlbmRpZGlrYW4gTm9tb3IgNDUiLCAiTG9jYWxpdHkiOiA
iSmFrYXJ0YSIsICJDb3VudHJ5IjogIklEIiB9CiAgICAgICAgICAgIF0sCiAgICAgICAgICAgICJUR
UVsZWN0cm9uaWNBZGRyZXNzIjogWwogICAgICAgICAgICAgIHsgImxhbmciOiAiaWQiLCAidXJpVmF
sdWUiOiAibWFpbHRvOnBraUB1bm4uYWMuaWQiIH0sCiAgICAgICAgICAgICAgeyAibGFuZyI6ICJlb
iIsICJ1cmlWYWx1ZSI6ICJtYWlsdG86cGtpQHVubi5hYy5pZCIgfSwKICAgICAgICAgICAgICB7ICJ
sYW5nIjogImlkIiwgInVyaVZhbHVlIjogImh0dHBzOi8vaWphemFoLnVubi5hYy5pZCIgfSwKICAgI
CAgICAgICAgICB7ICJsYW5nIjogImVuIiwgInVyaVZhbHVlIjogImh0dHBzOi8vaWphemFoLnVubi5
hYy5pZCIgfQogICAgICAgICAgICBdCiAgICAgICAgICB9LAogICAgICAgICAgIlRFSW5mb3JtYXRpb
25VUkkiOiBbCiAgICAgICAgICAgIHsgImxhbmciOiAiaWQiLCAidXJpVmFsdWUiOiAiaHR0cHM6Ly9
pamF6YWgudW5uLmFjLmlkIiB9LAogICAgICAgICAgICB7ICJsYW5nIjogImVuIiwgInVyaVZhbHVlI
jogImh0dHBzOi8vaWphemFoLnVubi5hYy5pZCIgfQogICAgICAgICAgXQogICAgICAgIH0sCiAgICA
gICAgIlRydXN0ZWRFbnRpdHlTZXJ2aWNlcyI6IFsKICAgICAgICAgIHsKICAgICAgICAgICAgIlNlc
nZpY2VJbmZvcm1hdGlvbiI6IHsKICAgICAgICAgICAgICAiU2VydmljZVR5cGVJZGVudGlmaWVyIjo
gImh0dHBzOi8vaWRjdGYuaWQvbnMvMTk2MDIvU3ZjVHlwZS9BdHRyaWJ1dGVJc3N1ZXIiLAogICAgI
CAgICAgICAgICJTZXJ2aWNlTmFtZSI6IFsKICAgICAgICAgICAgICAgIHsgImxhbmciOiAiaWQiLCA
idmFsdWUiOiAiQXR0cmlidXRlIElzc3VlciIgfSwKICAgICAgICAgICAgICAgIHsgImxhbmciOiAiZ
W4iLCAidmFsdWUiOiAiQXR0cmlidXRlIElzc3VlciIgfQogICAgICAgICAgICAgIF0sCiAgICAgICA
gICAgICAgIlNlcnZpY2VEaWdpdGFsSWRlbnRpdHkiOiB7CiAgICAgICAgICAgICAgICAiT3RoZXJJZ
HMiOiBbImRpZDp3ZWJ2aDpRbVlrSmlvY0Y1WFZKSDl4aktjZVZjaUtHdkhwdjl6Zjd3WmNSeTZ5M3V
6RnExOmlqYXphaC51bm4uYWMuaWQiXQogICAgICAgICAgICAgIH0sCiAgICAgICAgICAgICAgIlNlc
nZpY2VTdGF0dXMiOiAiaHR0cHM6Ly9pZGN0Zi5pZC9ucy8xOTYwMi9TdmNTdGF0dXMvd2l0aGRyYXd
uIiwKICAgICAgICAgICAgICAiU3RhdHVzU3RhcnRpbmdUaW1lIjogIjIwMjYtMTAtMDFUMDA6MDA6M
DBaIgogICAgICAgICAgICB9LAogICAgICAgICAgICAiU2VydmljZUhpc3RvcnkiOiBbCiAgICAgICA
gICAgICAgewogICAgICAgICAgICAgICAgIlNlcnZpY2VOYW1lIjogWwogICAgICAgICAgICAgICAgI
CB7ICJsYW5nIjogImlkIiwgInZhbHVlIjogIkF0dHJpYnV0ZSBJc3N1ZXIiIH0sCiAgICAgICAgICA
gICAgICAgIHsgImxhbmciOiAiZW4iLCAidmFsdWUiOiAiQXR0cmlidXRlIElzc3VlciIgfQogICAgI
CAgICAgICAgICAgXSwKICAgICAgICAgICAgICAgICJTZXJ2aWNlRGlnaXRhbElkZW50aXR5Ijogewo
gICAgICAgICAgICAgICAgICAiT3RoZXJJZHMiOiBbImRpZDp3ZWJ2aDpRbVlrSmlvY0Y1WFZKSDl4a
ktjZVZjaUtHdkhwdjl6Zjd3WmNSeTZ5M3V6RnExOmlqYXphaC51bm4uYWMuaWQiXQogICAgICAgICA
gICAgICAgfSwKICAgICAgICAgICAgICAgICJTZXJ2aWNlU3RhdHVzIjogImh0dHBzOi8vaWRjdGYua
WQvbnMvMTk2MDIvU3ZjU3RhdHVzL2dyYW50ZWQiLAogICAgICAgICAgICAgICAgIlN0YXR1c1N0YXJ
0aW5nVGltZSI6ICIyMDI2LTAyLTAxVDAwOjAwOjAwWiIsCiAgICAgICAgICAgICAgICAiU2VydmljZ
VR5cGVJZGVudGlmaWVyIjogImh0dHBzOi8vaWRjdGYuaWQvbnMvMTk2MDIvU3ZjVHlwZS9BdHRyaWJ
1dGVJc3N1ZXIiCiAgICAgICAgICAgICAgfQogICAgICAgICAgICBdCiAgICAgICAgICB9CiAgICAgI
CAgXQogICAgICB9LAogICAgICB7CiAgICAgICAgIlRydXN0ZWRFbnRpdHlJbmZvcm1hdGlvbiI6IHs
KICAgICAgICAgICJURU5hbWUiOiBbCiAgICAgICAgICAgIHsgImxhbmciOiAiaWQiLCAidmFsdWUiO
iAiS2VtZW50ZXJpYW4gQWdhbWEiIH0sCiAgICAgICAgICAgIHsgImxhbmciOiAiZW4iLCAidmFsdWU
iOiAiTWluaXN0cnkgb2YgUmVsaWdpb3VzIEFmZmFpcnMiIH0KICAgICAgICAgIF0sCiAgICAgICAgI
CAiVEVUcmFkZU5hbWUiOiBbCiAgICAgICAgICAgIHsgImxhbmciOiAiaWQiLCAidmFsdWUiOiAiQkt
OOjQwMjUxMCIgfSwKICAgICAgICAgICAgeyAibGFuZyI6ICJlbiIsICJ2YWx1ZSI6ICJCS046NDAyN
TEwIiB9CiAgICAgICAgICBdLAogICAgICAgICAgIlRFQWRkcmVzcyI6IHsKICAgICAgICAgICAgIlR
FUG9zdGFsQWRkcmVzcyI6IFsKICAgICAgICAgICAgICB7ICJsYW5nIjogImlkIiwgIlN0cmVldEFkZ
HJlc3MiOiAiSmFsYW4gS2VydWt1bmFuIE5vbW9yIDEyIiwgIkxvY2FsaXR5IjogIkpha2FydGEiLCA
iQ291bnRyeSI6ICJJRCIgfSwKICAgICAgICAgICAgICB7ICJsYW5nIjogImVuIiwgIlN0cmVldEFkZ
HJlc3MiOiAiSmFsYW4gS2VydWt1bmFuIE5vbW9yIDEyIiwgIkxvY2FsaXR5IjogIkpha2FydGEiLCA
iQ291bnRyeSI6ICJJRCIgfQogICAgICAgICAgICBdLAogICAgICAgICAgICAiVEVFbGVjdHJvbmljQ
WRkcmVzcyI6IFsKICAgICAgICAgICAgICB7ICJsYW5nIjogImlkIiwgInVyaVZhbHVlIjogIm1haWx
0bzpwa2lAa2VtZW5hZy5nby5pZCIgfSwKICAgICAgICAgICAgICB7ICJsYW5nIjogImVuIiwgInVya
VZhbHVlIjogIm1haWx0bzpwa2lAa2VtZW5hZy5nby5pZCIgfSwKICAgICAgICAgICAgICB7ICJsYW5
nIjogImlkIiwgInVyaVZhbHVlIjogImh0dHBzOi8va2VtZW5hZy5nby5pZCIgfSwKICAgICAgICAgI
CAgICB7ICJsYW5nIjogImVuIiwgInVyaVZhbHVlIjogImh0dHBzOi8va2VtZW5hZy5nby5pZCIgfQo
gICAgICAgICAgICBdCiAgICAgICAgICB9LAogICAgICAgICAgIlRFSW5mb3JtYXRpb25VUkkiOiBbC
iAgICAgICAgICAgIHsgImxhbmciOiAiaWQiLCAidXJpVmFsdWUiOiAiaHR0cHM6Ly9rZW1lbmFnLmd
vLmlkIiB9LAogICAgICAgICAgICB7ICJsYW5nIjogImVuIiwgInVyaVZhbHVlIjogImh0dHBzOi8va
2VtZW5hZy5nby5pZCIgfQogICAgICAgICAgXQogICAgICAgIH0sCiAgICAgICAgIlRydXN0ZWRFbnR
pdHlTZXJ2aWNlcyI6IFsKICAgICAgICAgIHsKICAgICAgICAgICAgIlNlcnZpY2VJbmZvcm1hdGlvb
iI6IHsKICAgICAgICAgICAgICAiU2VydmljZVR5cGVJZGVudGlmaWVyIjogImh0dHBzOi8vaWRjdGY
uaWQvbnMvMTk2MDIvU3ZjVHlwZS9BdHRyaWJ1dGVJc3N1ZXIiLAogICAgICAgICAgICAgICJTZXJ2a
WNlTmFtZSI6IFsKICAgICAgICAgICAgICAgIHsgImxhbmciOiAiaWQiLCAidmFsdWUiOiAiQXR0cml
idXRlIElzc3VlciIgfSwKICAgICAgICAgICAgICAgIHsgImxhbmciOiAiZW4iLCAidmFsdWUiOiAiQ
XR0cmlidXRlIElzc3VlciIgfQogICAgICAgICAgICAgIF0sCiAgICAgICAgICAgICAgIlNlcnZpY2V
EaWdpdGFsSWRlbnRpdHkiOiB7CiAgICAgICAgICAgICAgICAiT3RoZXJJZHMiOiBbImRpZDp3ZWJ2a
DpRbWJBYjd1OVJNanFzWjlMOThwZTQ3c3pKWmRuS1FMaDlLaXpxTlcyV3dLYWMxOmtlbWVuYWcuZ28
uaWQiXQogICAgICAgICAgICAgIH0sCiAgICAgICAgICAgICAgIlNlcnZpY2VTdGF0dXMiOiAiaHR0c
HM6Ly9pZGN0Zi5pZC9ucy8xOTYwMi9TdmNTdGF0dXMvZ3JhbnRlZCIsCiAgICAgICAgICAgICAgIlN
0YXR1c1N0YXJ0aW5nVGltZSI6ICIyMDI2LTAzLTAxVDAwOjAwOjAwWiIKICAgICAgICAgICAgfQogI
CAgICAgICAgfQogICAgICAgIF0KICAgICAgfSwKICAgICAgewogICAgICAgICJUcnVzdGVkRW50aXR
5SW5mb3JtYXRpb24iOiB7CiAgICAgICAgICAiVEVOYW1lIjogWwogICAgICAgICAgICB7ICJsYW5nI
jogImlkIiwgInZhbHVlIjogIkJhZGFuIEtlcGVnYXdhaWFuIE5lZ2FyYSIgfSwKICAgICAgICAgICA
geyAibGFuZyI6ICJlbiIsICJ2YWx1ZSI6ICJOYXRpb25hbCBDaXZpbCBTZXJ2aWNlIEFnZW5jeSIgf
QogICAgICAgICAgXSwKICAgICAgICAgICJURVRyYWRlTmFtZSI6IFsKICAgICAgICAgICAgeyAibGF
uZyI6ICJpZCIsICJ2YWx1ZSI6ICJCS046NDAzMzgwIiB9LAogICAgICAgICAgICB7ICJsYW5nIjogI
mVuIiwgInZhbHVlIjogIkJLTjo0MDMzODAiIH0KICAgICAgICAgIF0sCiAgICAgICAgICAiVEVBZGR
yZXNzIjogewogICAgICAgICAgICAiVEVQb3N0YWxBZGRyZXNzIjogWwogICAgICAgICAgICAgIHsgI
mxhbmciOiAiaWQiLCAiU3RyZWV0QWRkcmVzcyI6ICJKYWxhbiBLZXBlZ2F3YWlhbiBOb21vciA5Iiw
gIkxvY2FsaXR5IjogIkpha2FydGEiLCAiQ291bnRyeSI6ICJJRCIgfSwKICAgICAgICAgICAgICB7I
CJsYW5nIjogImVuIiwgIlN0cmVldEFkZHJlc3MiOiAiSmFsYW4gS2VwZWdhd2FpYW4gTm9tb3IgOSI
sICJMb2NhbGl0eSI6ICJKYWthcnRhIiwgIkNvdW50cnkiOiAiSUQiIH0KICAgICAgICAgICAgXSwKI
CAgICAgICAgICAgIlRFRWxlY3Ryb25pY0FkZHJlc3MiOiBbCiAgICAgICAgICAgICAgeyAibGFuZyI
6ICJpZCIsICJ1cmlWYWx1ZSI6ICJtYWlsdG86cGtpQGJrbi5nby5pZCIgfSwKICAgICAgICAgICAgI
CB7ICJsYW5nIjogImVuIiwgInVyaVZhbHVlIjogIm1haWx0bzpwa2lAYmtuLmdvLmlkIiB9LAogICA
gICAgICAgICAgIHsgImxhbmciOiAiaWQiLCAidXJpVmFsdWUiOiAiaHR0cHM6Ly9ia24uZ28uaWQiI
H0sCiAgICAgICAgICAgICAgeyAibGFuZyI6ICJlbiIsICJ1cmlWYWx1ZSI6ICJodHRwczovL2Jrbi5
nby5pZCIgfQogICAgICAgICAgICBdCiAgICAgICAgICB9LAogICAgICAgICAgIlRFSW5mb3JtYXRpb
25VUkkiOiBbCiAgICAgICAgICAgIHsgImxhbmciOiAiaWQiLCAidXJpVmFsdWUiOiAiaHR0cHM6Ly9
ia24uZ28uaWQiIH0sCiAgICAgICAgICAgIHsgImxhbmciOiAiZW4iLCAidXJpVmFsdWUiOiAiaHR0c
HM6Ly9ia24uZ28uaWQiIH0KICAgICAgICAgIF0KICAgICAgICB9LAogICAgICAgICJUcnVzdGVkRW5
0aXR5U2VydmljZXMiOiBbCiAgICAgICAgICB7CiAgICAgICAgICAgICJTZXJ2aWNlSW5mb3JtYXRpb
24iOiB7CiAgICAgICAgICAgICAgIlNlcnZpY2VUeXBlSWRlbnRpZmllciI6ICJodHRwczovL2lkY3R
mLmlkL25zLzE5NjAyL1N2Y1R5cGUvQXR0cmlidXRlSXNzdWVyIiwKICAgICAgICAgICAgICAiU2Vyd
mljZU5hbWUiOiBbCiAgICAgICAgICAgICAgICB7ICJsYW5nIjogImlkIiwgInZhbHVlIjogIkF0dHJ
pYnV0ZSBJc3N1ZXIiIH0sCiAgICAgICAgICAgICAgICB7ICJsYW5nIjogImVuIiwgInZhbHVlIjogI
kF0dHJpYnV0ZSBJc3N1ZXIiIH0KICAgICAgICAgICAgICBdLAogICAgICAgICAgICAgICJTZXJ2aWN
lRGlnaXRhbElkZW50aXR5IjogewogICAgICAgICAgICAgICAgIk90aGVySWRzIjogWyJkaWQ6d2Vid
mg6UW1lOFJyaUduS3g1ajJRam9hWTFTZ1JTcHhUSGRqcTExTDJFeGd5MXpWMnhzSjpia24uZ28uaWQ
iXQogICAgICAgICAgICAgIH0sCiAgICAgICAgICAgICAgIlNlcnZpY2VTdGF0dXMiOiAiaHR0cHM6L
y9pZGN0Zi5pZC9ucy8xOTYwMi9TdmNTdGF0dXMvZ3JhbnRlZCIsCiAgICAgICAgICAgICAgIlN0YXR
1c1N0YXJ0aW5nVGltZSI6ICIyMDI2LTAzLTAxVDAwOjAwOjAwWiIKICAgICAgICAgICAgfQogICAgI
CAgICAgfQogICAgICAgIF0KICAgICAgfSwKICAgICAgewogICAgICAgICJUcnVzdGVkRW50aXR5SW5
mb3JtYXRpb24iOiB7CiAgICAgICAgICAiVEVOYW1lIjogWwogICAgICAgICAgICB7ICJsYW5nIjogI
mlkIiwgInZhbHVlIjogIktvcnBzIExhbHUgTGludGFzIEtlcG9saXNpYW4gTmVnYXJhIFJlcHVibGl
rIEluZG9uZXNpYSIgfSwKICAgICAgICAgICAgeyAibGFuZyI6ICJlbiIsICJ2YWx1ZSI6ICJUcmFmZ
mljIENvcnBzIG9mIHRoZSBJbmRvbmVzaWFuIE5hdGlvbmFsIFBvbGljZSIgfQogICAgICAgICAgXSw
KICAgICAgICAgICJURVRyYWRlTmFtZSI6IFsKICAgICAgICAgICAgeyAibGFuZyI6ICJpZCIsICJ2Y
Wx1ZSI6ICJCS046NDA0MzkwIiB9LAogICAgICAgICAgICB7ICJsYW5nIjogImVuIiwgInZhbHVlIjo
gIkJLTjo0MDQzOTAiIH0KICAgICAgICAgIF0sCiAgICAgICAgICAiVEVBZGRyZXNzIjogewogICAgI
CAgICAgICAiVEVQb3N0YWxBZGRyZXNzIjogWwogICAgICAgICAgICAgIHsgImxhbmciOiAiaWQiLCA
iU3RyZWV0QWRkcmVzcyI6ICJKYWxhbiBMYWx1IExpbnRhcyBOb21vciA3IiwgIkxvY2FsaXR5IjogI
kpha2FydGEiLCAiQ291bnRyeSI6ICJJRCIgfSwKICAgICAgICAgICAgICB7ICJsYW5nIjogImVuIiw
gIlN0cmVldEFkZHJlc3MiOiAiSmFsYW4gTGFsdSBMaW50YXMgTm9tb3IgNyIsICJMb2NhbGl0eSI6I
CJKYWthcnRhIiwgIkNvdW50cnkiOiAiSUQiIH0KICAgICAgICAgICAgXSwKICAgICAgICAgICAgIlR
FRWxlY3Ryb25pY0FkZHJlc3MiOiBbCiAgICAgICAgICAgICAgeyAibGFuZyI6ICJpZCIsICJ1cmlWY
Wx1ZSI6ICJtYWlsdG86cGtpQGtvcmxhbnRhcy5wb2xyaS5nby5pZCIgfSwKICAgICAgICAgICAgICB
7ICJsYW5nIjogImVuIiwgInVyaVZhbHVlIjogIm1haWx0bzpwa2lAa29ybGFudGFzLnBvbHJpLmdvL
mlkIiB9LAogICAgICAgICAgICAgIHsgImxhbmciOiAiaWQiLCAidXJpVmFsdWUiOiAiaHR0cHM6Ly9
rb3JsYW50YXMucG9scmkuZ28uaWQiIH0sCiAgICAgICAgICAgICAgeyAibGFuZyI6ICJlbiIsICJ1c
mlWYWx1ZSI6ICJodHRwczovL2tvcmxhbnRhcy5wb2xyaS5nby5pZCIgfQogICAgICAgICAgICBdCiA
gICAgICAgICB9LAogICAgICAgICAgIlRFSW5mb3JtYXRpb25VUkkiOiBbCiAgICAgICAgICAgIHsgI
mxhbmciOiAiaWQiLCAidXJpVmFsdWUiOiAiaHR0cHM6Ly9rb3JsYW50YXMucG9scmkuZ28uaWQiIH0
sCiAgICAgICAgICAgIHsgImxhbmciOiAiZW4iLCAidXJpVmFsdWUiOiAiaHR0cHM6Ly9rb3JsYW50Y
XMucG9scmkuZ28uaWQiIH0KICAgICAgICAgIF0KICAgICAgICB9LAogICAgICAgICJUcnVzdGVkRW5
0aXR5U2VydmljZXMiOiBbCiAgICAgICAgICB7CiAgICAgICAgICAgICJTZXJ2aWNlSW5mb3JtYXRpb
24iOiB7CiAgICAgICAgICAgICAgIlNlcnZpY2VUeXBlSWRlbnRpZmllciI6ICJodHRwczovL2lkY3R
mLmlkL25zLzE5NjAyL1N2Y1R5cGUvQXR0cmlidXRlSXNzdWVyIiwKICAgICAgICAgICAgICAiU2Vyd
mljZU5hbWUiOiBbCiAgICAgICAgICAgICAgICB7ICJsYW5nIjogImlkIiwgInZhbHVlIjogIkF0dHJ
pYnV0ZSBJc3N1ZXIiIH0sCiAgICAgICAgICAgICAgICB7ICJsYW5nIjogImVuIiwgInZhbHVlIjogI
kF0dHJpYnV0ZSBJc3N1ZXIiIH0KICAgICAgICAgICAgICBdLAogICAgICAgICAgICAgICJTZXJ2aWN
lRGlnaXRhbElkZW50aXR5IjogewogICAgICAgICAgICAgICAgIk90aGVySWRzIjogWyJkaWQ6d2Vid
mg6UW1aUWVGZ3AzU0JETG1pZHQ0VGlaaGl4OHU1YjJvUFNxdlFGaHVTRjhCb042Rjprb3JsYW50YXM
ucG9scmkuZ28uaWQiXQogICAgICAgICAgICAgIH0sCiAgICAgICAgICAgICAgIlNlcnZpY2VTdGF0d
XMiOiAiaHR0cHM6Ly9pZGN0Zi5pZC9ucy8xOTYwMi9TdmNTdGF0dXMvZ3JhbnRlZCIsCiAgICAgICA
gICAgICAgIlN0YXR1c1N0YXJ0aW5nVGltZSI6ICIyMDI2LTAzLTAxVDAwOjAwOjAwWiIKICAgICAgI
CAgICAgfQogICAgICAgICAgfQogICAgICAgIF0KICAgICAgfSwKICAgICAgewogICAgICAgICJUcnV
zdGVkRW50aXR5SW5mb3JtYXRpb24iOiB7CiAgICAgICAgICAiVEVOYW1lIjogWwogICAgICAgICAgI
CB7ICJsYW5nIjogImlkIiwgInZhbHVlIjogIlRydXN0IEF1dGhvcml0eSBSZXB1YmxpayBJbmRvbmV
zaWEiIH0sCiAgICAgICAgICAgIHsgImxhbmciOiAiZW4iLCAidmFsdWUiOiAiVHJ1c3QgQXV0aG9ya
XR5IFJlcHVibGlrIEluZG9uZXNpYSIgfQogICAgICAgICAgXSwKICAgICAgICAgICJURVRyYWRlTmF
tZSI6IFsKICAgICAgICAgICAgeyAibGFuZyI6ICJpZCIsICJ2YWx1ZSI6ICJCS046MDAwMTAwIiB9L
AogICAgICAgICAgICB7ICJsYW5nIjogImVuIiwgInZhbHVlIjogIkJLTjowMDAxMDAiIH0KICAgICA
gICAgIF0sCiAgICAgICAgICAiVEVBZGRyZXNzIjogewogICAgICAgICAgICAiVEVQb3N0YWxBZGRyZ
XNzIjogWwogICAgICAgICAgICAgIHsKICAgICAgICAgICAgICAgICJsYW5nIjogImlkIiwKICAgICA
gICAgICAgICAgICJTdHJlZXRBZGRyZXNzIjogIkphbGFuIEtlcGVyY2F5YWFuIERpZ2l0YWwgTm9tb
3IgMSIsCiAgICAgICAgICAgICAgICAiTG9jYWxpdHkiOiAiSmFrYXJ0YSIsCiAgICAgICAgICAgICA
gICAiQ291bnRyeSI6ICJJRCIKICAgICAgICAgICAgICB9LAogICAgICAgICAgICAgIHsKICAgICAgI
CAgICAgICAgICJsYW5nIjogImVuIiwKICAgICAgICAgICAgICAgICJTdHJlZXRBZGRyZXNzIjogIkp
hbGFuIEtlcGVyY2F5YWFuIERpZ2l0YWwgTm9tb3IgMSIsCiAgICAgICAgICAgICAgICAiTG9jYWxpd
HkiOiAiSmFrYXJ0YSIsCiAgICAgICAgICAgICAgICAiQ291bnRyeSI6ICJJRCIKICAgICAgICAgICA
gICB9CiAgICAgICAgICAgIF0sCiAgICAgICAgICAgICJURUVsZWN0cm9uaWNBZGRyZXNzIjogWwogI
CAgICAgICAgICAgIHsgImxhbmciOiAiaWQiLCAidXJpVmFsdWUiOiAibWFpbHRvOnRydXN0QHRydXN
0LmdvLmlkIiB9LAogICAgICAgICAgICAgIHsgImxhbmciOiAiZW4iLCAidXJpVmFsdWUiOiAibWFpb
HRvOnRydXN0QHRydXN0LmdvLmlkIiB9LAogICAgICAgICAgICAgIHsgImxhbmciOiAiaWQiLCAidXJ
pVmFsdWUiOiAiaHR0cHM6Ly90cnVzdC5nby5pZCIgfSwKICAgICAgICAgICAgICB7ICJsYW5nIjogI
mVuIiwgInVyaVZhbHVlIjogImh0dHBzOi8vdHJ1c3QuZ28uaWQiIH0KICAgICAgICAgICAgXQogICA
gICAgICAgfSwKICAgICAgICAgICJURUluZm9ybWF0aW9uVVJJIjogWwogICAgICAgICAgICB7ICJsY
W5nIjogImlkIiwgInVyaVZhbHVlIjogImh0dHBzOi8vdHJ1c3QuZ28uaWQiIH0sCiAgICAgICAgICA
gIHsgImxhbmciOiAiZW4iLCAidXJpVmFsdWUiOiAiaHR0cHM6Ly90cnVzdC5nby5pZCIgfQogICAgI
CAgICAgXQogICAgICAgIH0sCiAgICAgICAgIlRydXN0ZWRFbnRpdHlTZXJ2aWNlcyI6IFsKICAgICA
gICAgIHsKICAgICAgICAgICAgIlNlcnZpY2VJbmZvcm1hdGlvbiI6IHsKICAgICAgICAgICAgICAiU
2VydmljZVR5cGVJZGVudGlmaWVyIjogImh0dHBzOi8vaWRjdGYuaWQvbnMvMTk2MDIvU3ZjVHlwZS9
XaXRuZXNzIiwKICAgICAgICAgICAgICAiU2VydmljZU5hbWUiOiBbCiAgICAgICAgICAgICAgICB7I
CJsYW5nIjogImlkIiwgInZhbHVlIjogIldpdG5lc3MiIH0sCiAgICAgICAgICAgICAgICB7ICJsYW5
nIjogImVuIiwgInZhbHVlIjogIldpdG5lc3MiIH0KICAgICAgICAgICAgICBdLAogICAgICAgICAgI
CAgICJTZXJ2aWNlRGlnaXRhbElkZW50aXR5IjogewogICAgICAgICAgICAgICAgIk90aGVySWRzIjo
gWyJkaWQ6a2V5Ono2TWt0cWpFVksxUDFIZ01TSllHcFBZanVMakVhMTN1MjZXRWhmN2R2Q1dQWVpqM
SJdCiAgICAgICAgICAgICAgfSwKICAgICAgICAgICAgICAiU2VydmljZVN0YXR1cyI6ICJodHRwczo
vL2lkY3RmLmlkL25zLzE5NjAyL1N2Y1N0YXR1cy9ncmFudGVkIiwKICAgICAgICAgICAgICAiU3Rhd
HVzU3RhcnRpbmdUaW1lIjogIjIwMjYtMDktMDFUMDA6MDA6MDBaIgogICAgICAgICAgICB9CiAgICA
gICAgICB9LAogICAgICAgICAgewogICAgICAgICAgICAiU2VydmljZUluZm9ybWF0aW9uIjogewogI
CAgICAgICAgICAgICJTZXJ2aWNlVHlwZUlkZW50aWZpZXIiOiAiaHR0cHM6Ly9pZGN0Zi5pZC9ucy8
xOTYwMi9TdmNUeXBlL1dpdG5lc3MiLAogICAgICAgICAgICAgICJTZXJ2aWNlTmFtZSI6IFsKICAgI
CAgICAgICAgICAgIHsgImxhbmciOiAiaWQiLCAidmFsdWUiOiAiV2l0bmVzcyIgfSwKICAgICAgICA
gICAgICAgIHsgImxhbmciOiAiZW4iLCAidmFsdWUiOiAiV2l0bmVzcyIgfQogICAgICAgICAgICAgI
F0sCiAgICAgICAgICAgICAgIlNlcnZpY2VEaWdpdGFsSWRlbnRpdHkiOiB7CiAgICAgICAgICAgICA
gICAiT3RoZXJJZHMiOiBbImRpZDprZXk6ejZNa3JHUnMxcDJGanNRc3hKdEt3bWFVb3R6R3RqbWpjd
k03dUtjblhVN2ZmTEtlIl0KICAgICAgICAgICAgICB9LAogICAgICAgICAgICAgICJTZXJ2aWNlU3R
hdHVzIjogImh0dHBzOi8vaWRjdGYuaWQvbnMvMTk2MDIvU3ZjU3RhdHVzL3dpdGhkcmF3biIsCiAgI
CAgICAgICAgICAgIlN0YXR1c1N0YXJ0aW5nVGltZSI6ICIyMDI2LTEwLTAxVDAwOjAwOjAwWiIKICA
gICAgICAgICAgfSwKICAgICAgICAgICAgIlNlcnZpY2VIaXN0b3J5IjogWwogICAgICAgICAgICAgI
HsKICAgICAgICAgICAgICAgICJTZXJ2aWNlTmFtZSI6IFsKICAgICAgICAgICAgICAgICAgeyAibGF
uZyI6ICJpZCIsICJ2YWx1ZSI6ICJXaXRuZXNzIiB9LAogICAgICAgICAgICAgICAgICB7ICJsYW5nI
jogImVuIiwgInZhbHVlIjogIldpdG5lc3MiIH0KICAgICAgICAgICAgICAgIF0sCiAgICAgICAgICA
gICAgICAiU2VydmljZURpZ2l0YWxJZGVudGl0eSI6IHsKICAgICAgICAgICAgICAgICAgIk90aGVyS
WRzIjogWyJkaWQ6a2V5Ono2TWtyR1JzMXAyRmpzUXN4SnRLd21hVW90ekd0am1qY3ZNN3VLY25YVTd
mZkxLZSJdCiAgICAgICAgICAgICAgICB9LAogICAgICAgICAgICAgICAgIlNlcnZpY2VTdGF0dXMiO
iAiaHR0cHM6Ly9pZGN0Zi5pZC9ucy8xOTYwMi9TdmNTdGF0dXMvZ3JhbnRlZCIsCiAgICAgICAgICA
gICAgICAiU3RhdHVzU3RhcnRpbmdUaW1lIjogIjIwMjYtMDEtMDFUMDA6MDA6MDBaIiwKICAgICAgI
CAgICAgICAgICJTZXJ2aWNlVHlwZUlkZW50aWZpZXIiOiAiaHR0cHM6Ly9pZGN0Zi5pZC9ucy8xOTY
wMi9TdmNUeXBlL1dpdG5lc3MiCiAgICAgICAgICAgICAgfQogICAgICAgICAgICBdCiAgICAgICAgI
CB9LAogICAgICAgICAgewogICAgICAgICAgICAiU2VydmljZUluZm9ybWF0aW9uIjogewogICAgICA
gICAgICAgICJTZXJ2aWNlVHlwZUlkZW50aWZpZXIiOiAiaHR0cHM6Ly9pZGN0Zi5pZC9ucy8xOTYwM
i9TdmNUeXBlL1RydXN0ZWRMaXN0U2lnbmVyIiwKICAgICAgICAgICAgICAiU2VydmljZU5hbWUiOiB
bCiAgICAgICAgICAgICAgICB7ICJsYW5nIjogImlkIiwgInZhbHVlIjogIlRydXN0ZWQgbGlzdCBza
WduZXIiIH0sCiAgICAgICAgICAgICAgICB7ICJsYW5nIjogImVuIiwgInZhbHVlIjogIlRydXN0ZWQ
gbGlzdCBzaWduZXIiIH0KICAgICAgICAgICAgICBdLAogICAgICAgICAgICAgICJTZXJ2aWNlRGlna
XRhbElkZW50aXR5IjogewogICAgICAgICAgICAgICAgIk90aGVySWRzIjogWyJkaWQ6a2V5OnpEbmF
lU0N6Q2hEcUxUbm9iejFpcXVLZXREQzFwaXV3eWR6bzNqa3BpRUhOd3RYN3EiXQogICAgICAgICAgI
CAgIH0sCiAgICAgICAgICAgICAgIlNlcnZpY2VTdGF0dXMiOiAiaHR0cHM6Ly9pZGN0Zi5pZC9ucy8
xOTYwMi9TdmNTdGF0dXMvZ3JhbnRlZCIsCiAgICAgICAgICAgICAgIlN0YXR1c1N0YXJ0aW5nVGltZ
SI6ICIyMDI2LTAxLTAxVDAwOjAwOjAwWiIKICAgICAgICAgICAgfQogICAgICAgICAgfSwKICAgICA
gICAgIHsKICAgICAgICAgICAgIlNlcnZpY2VJbmZvcm1hdGlvbiI6IHsKICAgICAgICAgICAgICAiU
2VydmljZVR5cGVJZGVudGlmaWVyIjogImh0dHBzOi8vaWRjdGYuaWQvbnMvMTk2MDIvU3ZjVHlwZS9
UcnVzdGVkTGlzdFNpZ25lciIsCiAgICAgICAgICAgICAgIlNlcnZpY2VOYW1lIjogWwogICAgICAgI
CAgICAgICAgeyAibGFuZyI6ICJpZCIsICJ2YWx1ZSI6ICJUcnVzdGVkIGxpc3Qgc2lnbmVyIiB9LAo
gICAgICAgICAgICAgICAgeyAibGFuZyI6ICJlbiIsICJ2YWx1ZSI6ICJUcnVzdGVkIGxpc3Qgc2lnb
mVyIiB9CiAgICAgICAgICAgICAgXSwKICAgICAgICAgICAgICAiU2VydmljZURpZ2l0YWxJZGVudGl
0eSI6IHsKICAgICAgICAgICAgICAgICJPdGhlcklkcyI6IFsiZGlkOmtleTp6RG5hZWJvWDkzUmNVU
HM4TnBjNjhFUUQ1UmdiVmVWV1RyOHNLeVlNOHZyQ2VXcmtpIl0KICAgICAgICAgICAgICB9LAogICA
gICAgICAgICAgICJTZXJ2aWNlU3RhdHVzIjogImh0dHBzOi8vaWRjdGYuaWQvbnMvMTk2MDIvU3ZjU
3RhdHVzL2dyYW50ZWQiLAogICAgICAgICAgICAgICJTdGF0dXNTdGFydGluZ1RpbWUiOiAiMjAyNi0
xMC0xN1QwNjowMDowMFoiCiAgICAgICAgICAgIH0KICAgICAgICAgIH0KICAgICAgICBdCiAgICAgI
H0KICAgIF0KICB9Cn0.en9jCztnCN639l_jUTb8Dl0RZL7LmwRwwuMZhRCvunFTMZvne591K4Zzhne
6RssD7wc6kX4zgBOedfcVECmy4A
```

## Publication {#ts-5-01-publication}

A list reaches a reader in four steps, each on the trust path and none on
the transaction path.

1. Trust Registry builds the list from the Root Authority's decisions,
   using its List Publisher Component.
2. Trust Authority signs it with the trusted list key, using its Certificate
   Authority Component, and returns the JWS.
3. Trust Registry pushes the JWS to every distribution point, using its
   Object Storage Provider Component.
4. Every reader fetches it on its next trust cache sync, never on demand.

The hour an emergency list is published within is a constant of this
specification and not a member of the Governance Profile. An edition is how
the ecosystem tunes a value, and the answer to a confirmed compromise is the
one value an edition cannot slow.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-01-057 }**REQ-TS-5-01-057** Trust Registry MUST serve the current list at every address in `DistributionPoints`, over HTTP with Transport Layer Security (TLS), as a static file.
- [](){ #req-ts-5-01-058 }**REQ-TS-5-01-058** Every distribution point MUST serve the same bytes.
- [](){ #req-ts-5-01-059 }**REQ-TS-5-01-059** Trust Registry MUST serve the list without authentication.
- [](){ #req-ts-5-01-060 }**REQ-TS-5-01-060** Trust Registry MUST NOT require any identifier of the reader.
- [](){ #req-ts-5-01-061 }**REQ-TS-5-01-061** Trust Registry MUST publish a new list before the `NextUpdate` of the current one.
- [](){ #req-ts-5-01-062 }**REQ-TS-5-01-062** Trust Registry MUST publish an emergency trusted list within one hour of the compromise or the misconduct behind it being confirmed.
- [](){ #req-ts-5-01-063 }**REQ-TS-5-01-063** An emergency trusted list MUST be a complete list of the same form as every other, with the next sequence number.
- [](){ #req-ts-5-01-064 }**REQ-TS-5-01-064** Trust Registry MUST keep every list it published.
- [](){ #req-ts-5-01-065 }**REQ-TS-5-01-065** Trust Registry MAY link archived versions from `SchemeInformationURI`.

</div>

The address of the list is a distribution point the Governance Profile
publishes to participants and the list itself repeats, so that a reader
configured once can follow a move. An emergency list is the ordinary list
reissued early, when a key is revoked or a registration suspended, as
[entity key revocation][entity-key-revocation] sets out. Trust Authority's
order and the list's publication both come inside the hour that flow counts
from the compromise being confirmed.

## Reading the copy {#ts-5-01-reading-the-copy}

A reader works in two moments: the sync, outside any transaction, and the
read, inside one.

1. On the sync, the reader fetches the list from a distribution point,
   verifies the JWS, checks the sequence number against the copy it holds,
   and stores the new copy.
2. On a read, it verifies the JWS of the copy again, checks that
   `NextUpdate` has not passed, finds the counterpart's entry, and takes
   the status of the service it needs.
3. It never asks Trust Registry anything in between.

A reader in this section is any of the five that hold a cached copy of the
list: Issuer Core, Verifier Core, Mobile Wallet, Mobile Verifier, and a
Relying Party's own application built on Reader SDK.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-01-066 }**REQ-TS-5-01-066** A reader MUST verify the JWS of its copy every time it reads the copy, not only when it fetched it.
- [](){ #req-ts-5-01-067 }**REQ-TS-5-01-067** A reader MUST accept a signature only from the trusted list key it carries from build time, or from a key that a list it already verified named in a trusted list signer service at status `granted`.
- [](){ #req-ts-5-01-094 }**REQ-TS-5-01-094** A reader MUST NOT accept a signature from a key that the newest list it verified names at status `withdrawn`, the build-time key included, from the `StatusStartingTime` of that status.
- [](){ #req-ts-5-01-093 }**REQ-TS-5-01-093** A reader MUST keep the trusted list signer services of the newest list it verified, each with its status and `StatusStartingTime`, and that list's `LoTESequenceNumber`, after it discards the copy under [REQ-TS-5-01-069][req-ts-5-01-069], until a later list it verifies replaces them.
- [](){ #req-ts-5-01-068 }**REQ-TS-5-01-068** A reader MUST reject a list whose `LoTESequenceNumber` is lower than that of the copy it holds.
- [](){ #req-ts-5-01-069 }**REQ-TS-5-01-069** A reader MUST discard its copy once the `NextUpdate` it carries has passed, with no grace period.
- [](){ #req-ts-5-01-070 }**REQ-TS-5-01-070** A reader MUST refresh its copy outside any transaction, through the trust cache sync.
- [](){ #req-ts-5-01-091 }**REQ-TS-5-01-091** A reader MUST attempt the trust cache sync at least once in every `every` of the Governance Profile's `trust_cache_sync`, after a delay it draws at random for each attempt, between zero and that member's `jitter`.
- [](){ #req-ts-5-01-071 }**REQ-TS-5-01-071** A reader MUST NOT fetch the list during a transaction.
- [](){ #req-ts-5-01-072 }**REQ-TS-5-01-072** A reader MUST NOT ask Trust Registry for the trusted list entry of a single registration.
- [](){ #req-ts-5-01-073 }**REQ-TS-5-01-073** A reader MUST treat a registration as accredited for a role only when its entry carries a service of that role at status `granted`, except as [REQ-TS-5-01-092][req-ts-5-01-092] sets for the issuer of a credential.
- [](){ #req-ts-5-01-092 }**REQ-TS-5-01-092** A reader MUST treat the issuer of a credential as accredited for its role only when that role service, read with its `ServiceHistory`, was at status `granted` at the signing time the credential carries, and is not at status `suspended` in its copy.
- [](){ #req-ts-5-01-074 }**REQ-TS-5-01-074** A reader MUST refuse a counterpart that introduces itself by a DID whose registration is absent from its copy, however its DID Document resolves.
- [](){ #req-ts-5-01-075 }**REQ-TS-5-01-075** A reader MUST refuse a signature made with a key that a revoked key service names, whatever date the signature claims.
- [](){ #req-ts-5-01-076 }**REQ-TS-5-01-076** A reader MUST accept a Verifier Issuing CA only when a Verifier Issuing CA service names its subject key identifier at status `granted`, in an entry whose role service is at status `granted` and none of whose revoked key services names that subject key identifier.
- [](){ #req-ts-5-01-077 }**REQ-TS-5-01-077** A reader MUST accept a witness proof on a log entry only from a `did:key` that a witness service names at status `granted`, or at status `withdrawn` when the entry was published before that service's `StatusStartingTime`.
- [](){ #req-ts-5-01-078 }**REQ-TS-5-01-078** A reader MUST NOT send any identifier of a holder, a device, or a transaction when it fetches the list.
- [](){ #req-ts-5-01-079 }**REQ-TS-5-01-079** A reader MUST NOT key its cache of the list by a citizen or a transaction.

</div>

Which role a reader checks for depends on what it is doing. Issuer Core
checks that the signer of a Key Attestation is a Wallet Provider.
Verifier Core and Mobile Verifier check that the issuer of a credential is an
Identity Issuer or an Attribute Issuer. Mobile Wallet checks that the issuer
making an offer is one of the two, and that the party asking for a
presentation is a Relying Party.

An mdoc carries no DID, so Mobile Verifier and Verifier Core establish the
issuer through the X.509 chain and the VICAL instead, as
[the issuer side][the-issuer-side] sets out, and find its entry by the
`organizationName` of the Document Signer Certificate, which
[REQ-TS-5-04-168][req-ts-5-04-168] makes the entry's `TEName`. The flows in
[Flows per use case](../architecture-framework/high-level-architecture/flows-per-use-case.md)
place each check.

A merchant's device is not in the list and is checked through the
Verifier Issuing CA of the RP Intermediary behind it, as
[the reader side][the-reader-side] sets out.

A withdrawal revokes no key, as
[Withdrawing the registration][ts-4-03-withdrawing-the-registration] sets
out. What an issuer signed while granted still verifies after its
accreditation is withdrawn; what it signed after the withdrawal, or while it
was suspended, does not.

## Security considerations {#ts-5-01-security-considerations}

- **Substitution of an old list.** `NextUpdate` with no grace period,
  [REQ-TS-5-01-069][req-ts-5-01-069], and the sequence number,
  [REQ-TS-5-01-068][req-ts-5-01-068], together refuse a list that was valid
  once; the standard asks for the first and this profile adds the second.
- **A poisoned cache.** The signature is checked at every read,
  [REQ-TS-5-01-066][req-ts-5-01-066], so a copy altered on disk after it was
  fetched is caught at the next read.
- **A stolen signing key.** A key that appears unannounced is refused,
  [REQ-TS-5-01-067][req-ts-5-01-067], so a stolen key cannot publish a list of
  its own. An announced key that is stolen is struck,
  [REQ-TS-5-01-044][req-ts-5-01-044], by the next list signed with an
  accepted key. A reader that verified that list refuses the struck key from
  then on, the build-time key included, because it keeps the signer services
  and the sequence number after it discards the copy,
  [REQ-TS-5-01-093][req-ts-5-01-093]. A reader that never verified the
  striking list, a fresh installation whose build-time key is the stolen
  one among them, is contained only by a new reader release.
- **A stolen witness key.** Setting the `did:key` to `withdrawn` stops every
  reader counting its proofs on any later entry,
  [REQ-TS-5-01-077][req-ts-5-01-077], as [the witness key][the-witness-key]
  sets out.
- **A key compromised inside a certificate's life.** The revoked key
  service reaches every reader that holds the list,
  [REQ-TS-5-01-075][req-ts-5-01-075], whichever format the credential took, and
  the CRL reaches the offline mdoc reader.
- **A withdrawn issuer that backdates.** A withdrawal leaves the issuer its
  keys, [REQ-TS-4-03-043][req-ts-4-03-043], and the signing time is the
  issuer's own claim, so a withdrawn issuer could date a new credential
  before its withdrawal and pass [REQ-TS-5-01-092][req-ts-5-01-092]. The
  containment is the Root Authority revoking that issuer's keys, which
  [REQ-TS-5-01-075][req-ts-5-01-075] applies whatever date the signature
  claims. The same containment answers credentials signed before a
  suspension that a later withdrawal would let verify again.

## Privacy considerations {#ts-5-01-privacy-considerations}

The list carries no citizen data. It is fetched whole, without
authentication and without any identifier of the reader,
[REQ-TS-5-01-059][req-ts-5-01-059], [REQ-TS-5-01-060][req-ts-5-01-060], and
[REQ-TS-5-01-078][req-ts-5-01-078], on a schedule the citizen's transactions do
not drive, [REQ-TS-5-01-070][req-ts-5-01-070]. Trust Registry therefore learns
nothing about which citizen dealt with which party, and a reader makes no lookup
per transaction,
[REQ-TS-5-01-071][req-ts-5-01-071] and [REQ-TS-5-01-072][req-ts-5-01-072]. A
reader's cache holds only the public artifact and is never keyed by the
citizen, [REQ-TS-5-01-079][req-ts-5-01-079], because a cache keyed by the
citizen is a record of the citizen's behavior.

## Changelog {#ts-5-01-changelog}

<figure markdown="1" class="ekdn-table">

| Version | Date | Change |
|---|---|---|
| 1.0 draft | 21 October 2026 | First draft |

</figure>
