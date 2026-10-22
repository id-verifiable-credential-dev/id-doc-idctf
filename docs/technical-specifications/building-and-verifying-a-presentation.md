---
title: "[TS-5-11] Building and verifying a presentation"
description: What a wallet sends when a verifier asks, in each of the three representations, how that answer is bound to the one request that asked for it, and what the verifier checks before it believes any of it.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §4.5, §4.7 (Kep. 2, 19, 28), §5.3, §7.3, §7.5; JWT di OpenID4VCI dan OpenID4VP §0, §2, §3; Peta Alur Penerbitan dan Presentasi §1, §3.1, §4.1, §6; Panduan mdoc §3, §5, §9; tracks/0092, tracks/0211, tracks/0220 -->

<p class="ekdn-docid">TS-5-11</p>

# Building and verifying a presentation {#ts-5-11-building-and-verifying-a-presentation}

<p class="ekdn-lead" markdown="span">
A presentation is a citizen's answer to one request: the claims that request
asked for, proof that the wallet holds the key the credential is bound to, and
a binding to that request and no other. This specification fixes what travels
in each of the three representations and what the verifier checks.
</p>

Every sentence on this page binds Mobile Wallet, which builds a presentation,
and Verifier Core and Mobile Verifier, which verify one, and an Assessment Body
tests them against it in the version the Governance Profile puts in force. The
key words and the identifier `REQ-TS-5-11-nnn` follow
[Common provisions](common-provisions.md).

## Who runs this and what it needs {#ts-5-11-who-runs-this-and-what-it-needs}

This specification fixes the presentation itself: which claims of a credential
travel, the proof that the presenter holds the credential key, the values that
bind that proof to the request that asked for it, and the checks a verifier runs
before it accepts the answer. It covers the three representations
[Issuing a credential in SD-JWT VC, mdoc, and `ldp_vc`](issuing-a-credential-in-sd-jwt-vc-mdoc-and-ldp-vc.md)
issues, in the mode each is presented in: an
[SD-JWT-based Verifiable Credential (SD-JWT VC)][ref-i-d-ietf-oauth-sd-jwt-vc]
draft -13 and an `ldp_vc` online over [OpenID4VP][ref-openid4vp] 1.0, an
[ISO mdoc][ref-iso-18013-5] in proximity under ISO/IEC 18013-5:2021.

Its conformance targets are Mobile Wallet, Verifier Core, and Mobile Verifier.
Mobile Verifier verifies in both modes: an mdoc in proximity, and an SD-JWT VC
or an `ldp_vc` online. The online check runs through the relay at the
RP Intermediary's Verifier Core, as
[Mobile Verifier to Verifier Core][mobile-verifier-to-verifier-core] sets out. A
Relying Party's own application built on Reader SDK verifies a proximity
presentation through that library, and the requirements addressed to
Mobile Verifier bind the application as well, except where a requirement names
the application itself.

It leaves to other documents:

- The request a presentation answers, with its `client_id`, its Digital
  Credentials Query Language (DCQL) query, and its response encryption, which
  [Verifying a credential online via OpenID4VP](verifying-a-credential-online-via-openid4vp.md)
  holds.
- The proximity exchange that carries one, from device engagement to the
  encrypted session, which
  [Verifying a credential in proximity via ISO/IEC 18013-5](verifying-a-credential-in-proximity-via-iso-iec-18013-5.md)
  holds.
- The Use Statement that bounds what a verifier may ask for, which
  [Registering and carrying a Use Statement](registering-and-carrying-a-use-statement.md)
  holds.
- The `ReaderAuthRole` that bounds what a verifier may ask for in proximity,
  which
  [Issuing and validating the X.509 certificates and the VICAL](issuing-and-validating-the-x509-certificates-and-the-vical.md)
  holds.
- The credential being presented, and the checks that reach the credential
  itself, which
  [Issuing a credential in SD-JWT VC, mdoc, and `ldp_vc`](issuing-a-credential-in-sd-jwt-vc-mdoc-and-ldp-vc.md)
  holds.
- Whether the verifier may be trusted at all, which is the trusted list that
  [Publishing and reading the trusted list](publishing-and-reading-the-trusted-list.md)
  holds.

Before it builds a presentation, Mobile Wallet holds the credential, every
disclosure that came with it, the credential key in its secure storage, and a
verified request: signature checked, verifier found on the trusted list,
Use Statement read, and the citizen's consent taken. Before it verifies one,
Verifier Core or Mobile Verifier holds the nonce it issued, the trusted list,
the issuer's Decentralized Identifier (DID) Document or the Issuer Root CA, and
the status lists, all from its own cache.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-11-001 }**REQ-TS-5-11-001** Mobile Wallet MUST meet every requirement this specification addresses to it before it sends a presentation.
- [](){ #req-ts-5-11-002 }**REQ-TS-5-11-002** Verifier Core and Mobile Verifier MUST meet every requirement in [Verifying a presentation][ts-5-11-verifying-a-presentation].
- [](){ #req-ts-5-11-003 }**REQ-TS-5-11-003** Mobile Wallet MUST NOT build a presentation before the citizen has consented to it.

</div>

## What a presentation is {#ts-5-11-what-a-presentation-is}

A credential proves who said what. A presentation proves that the party holding
it now is the party it was issued to, and that the answer was produced for this
request rather than captured from an earlier one. Those are the two halves of
the transaction chain a verifier evaluates, T3 and T4 of
[entity chain and transaction chain][entity-chain-and-transaction-chain]. Without
the first, a credential copied off a device is as good as the original. Without
the second, an answer recorded once can be replayed later.

Each representation proves both halves with its own mechanism, and
[the table of three presentations][tbl-ts-5-11-three-presentations] gives them
side by side.

[](){ #tbl-ts-5-11-three-presentations }

<figure markdown="1" class="ekdn-table">

| | SD-JWT VC | `ldp_vc` | mdoc |
|---|---|---|---|
| Mode | Online | Online | Proximity |
| Protocol | OpenID4VP 1.0 | OpenID4VP 1.0 | ISO/IEC 18013-5:2021 |
| What carries the claims | The selected disclosures | The whole credential | The disclosed `IssuerSignedItem` structures |
| Proof of the key | A Key Binding JWT | A Data Integrity proof over the presentation | A `deviceSignature` in `DeviceAuth` |
| Bound to the request by | `nonce` and `aud` | `challenge` and `domain` | `SessionTranscript` |
| Selective disclosure | Per claim | None, so a request is for the whole credential | Per data element |

</figure>

Which representation is presented is not a choice the wallet makes in the
moment. An SD-JWT VC has no proximity profile and an mdoc is not presented
online, so the mode decides the representation, as
[online and offline][online-and-offline] sets out.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-11-004 }**REQ-TS-5-11-004** Mobile Wallet MUST present an SD-JWT VC and an `ldp_vc` online over OpenID4VP.
- [](){ #req-ts-5-11-005 }**REQ-TS-5-11-005** Mobile Wallet MUST NOT present an SD-JWT VC or an `ldp_vc` in proximity.
- [](){ #req-ts-5-11-006 }**REQ-TS-5-11-006** Mobile Wallet MUST present an mdoc in proximity over [ISO/IEC 18013-5][ref-iso-18013-5].
- [](){ #req-ts-5-11-007 }**REQ-TS-5-11-007** Mobile Wallet MUST NOT present an mdoc online.
- [](){ #req-ts-5-11-008 }**REQ-TS-5-11-008** Verifier Core and Mobile Verifier MUST refuse a presentation in a representation they did not ask for.

</div>

## The presentations as exchanged {#ts-5-11-the-presentations-as-exchanged}

The three presentations below are an illustration: the citizen, the verifier,
the session, and the keys are invented, and no transaction has taken place. Every
field is exact. Each was signed with the credential key the credential it
presents is bound to, each signature verifies, and each digest recomputes, so an
implementation can parse these artifacts and find what the clauses below
require.

The presentations agree with the other examples on four points:

- All three present the credentials
  [the credentials as issued][ts-5-10-the-credentials-as-issued] publishes.
- All three present them to the Relying Party
  [the trusted list][ts-5-01-trusted-list-payload] carries.
- The SD-JWT VC one answers the first Request Object
  [carrying it online][ts-5-06-carrying-it-online] publishes and carries its
  `nonce`; the `ldp_vc` one answers the second, under a second registered use,
  and carries that request's `nonce` as `challenge`.
- The proximity one answers the `ItemsRequest` of the age check
  [carrying it in proximity][ts-5-06-carrying-it-in-proximity] publishes and
  carries no nonce at all, because its binding is the session.

What each discloses is what the Use Statements
[Registering and carrying a Use Statement](registering-and-carrying-a-use-statement.md)
register:

- `nama` and `instansi` for the official travel use, the first of the two
  options its request offers.
- `usia_di_atas_17` alone for the tobacco use.
- All nine attributes of the type for the Kartu Nikah, because an `ldp_vc`
  presentation cannot withhold one.

### An SD-JWT VC presentation {#ts-5-11-an-sd-jwt-vc-presentation}

The `vp_token` of the response, keyed by the identifier the credential query
carried:

``` { .json title="The vp_token of an SD-JWT VC presentation" data-format="JSON" }
{
  "kartu-asn": [
    "eyJ0eXAiOiJkYytzZC1qd3QiLCJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDp3ZWJ2aDpRbWU4UnJpR25LeDVqMlFqb2FZMVNnUlNweFRIZGpxMTFMMkV4Z3kxelYyeHNKOmJrbi5nby5pZCNpc3N1YW5jZS1qb3NlLTEifQ.eyJpc3MiOiJkaWQ6d2Vidmg6UW1lOFJyaUduS3g1ajJRam9hWTFTZ1JTcHhUSGRqcTExTDJFeGd5MXpWMnhzSjpia24uZ28uaWQiLCJ2Y3QiOiJpZC5pZGN0Zi5rYXJ0dS1hc24uMSIsImNuZiI6eyJqd2siOnsia3R5IjoiRUMiLCJjcnYiOiJQLTI1NiIsIngiOiIzQ09oeE9lT3hwQk9qVUpncVdTQVUwUUFBWWFZZ3VnUFZKXzJYMnFHZGtjIiwieSI6IjJrOTg4NTRwQjc3dWRkUnZlOE80a2c1bklQVDdFakVncGJlS3FXTHVNRUUifX0sIl9zZF9hbGciOiJzaGEtMjU2IiwiX3NkIjpbIjF6QTdMcXNPdGJoTFZRaG9fUlNlMFRHcVJyZmctUzU4SlpHV1NmZzZabU0iLCJDZnVRdi1jS3JnemYwdXpIeHUtVEJFQkp2dFo0UEE3U0RhVjloOFQ5TF9RIiwiRVQ5QmlsbFV3VmRoYkhjNnRmXy0xWEFDRWdWUDRiX2lVUHhIQ2FYQlNiYyIsIkhMeVU4aHRZWno0TmkyZlJkN3BTWWRpQ2JCLXF0NDhwQlM5aDJCR013VFEiLCJlNlVoQk44QXk1emRVUGdDX2htbnBXbGR3QnhpWDhGN2tPVzRuUklwNXdNIiwiZkFoREt6VjNVMzlqQzZiN0dMaEdGRGw3NnVnVy1tN0R6N1hxcUJuamxkYyIsImhLTUpsakZJTlQtd0ljUDhFUnJhWURrSExyMjZPWUJTQUlHS0ItMG5ORzgiLCJ3N0MxZXJCNno4OG1oRVZzTm5hUVlEZ2JacUNIakxsM2NieDFFemllUnFzIl0sInN0YXR1cyI6eyJzdGF0dXNfbGlzdCI6eyJpZHgiOjQ4MTkyMCwidXJpIjoiaHR0cHM6Ly9ia24uZ28uaWQvc3RhdHVzL2thcnR1LWFzbi0xIn19LCJuYmYiOjE3OTIyMTY4MTAsImlhdCI6MTc5MjIxNjgxMCwiZXhwIjoxODIzNzUyODEwfQ.Rtt14iNH1COHmkwCwvzkYcg2RftZdls7V1WghZc1xZC3GmENzivjroJTPBu2C83Qy4pbdbNsX0lorDW26kbPLg~WyJ3SXVNc2VoQTM1UEp0RU1yUzRub0NRIiwibmFtYSIsIkJ1ZGkgU2FudG9zbyBXaWNha3Nvbm8iXQ~WyJSb1o4SHRpMk9JVkJ4NHlNd3Q0UkZRIiwiaW5zdGFuc2kiLCJCYWRhbiBLZXBlZ2F3YWlhbiBOZWdhcmEiXQ~eyJ0eXAiOiJrYitqd3QiLCJhbGciOiJFUzI1NiJ9.eyJpYXQiOjE3OTIyMjEzMDAsImF1ZCI6ImRlY2VudHJhbGl6ZWRfaWRlbnRpZmllcjpkaWQ6d2Vidmg6UW1VQVRDNWp5ZjV5Vnk3MkdZQXA4blN2dXdzaHpEeTZ3WVg3V21OWTVVSnRYVDp0ZXJtaW5hbC1udXNhbnRhcmEuY28uaWQiLCJub25jZSI6ImxEQnRBSkNJa0VoZEhNdkswVnA2clEiLCJzZF9oYXNoIjoiNEtCeEdNWUwwVk5rMjk2bDVBYW03TW8yN3czd2VzZk45LW5JVUNCZEh6ZyJ9.VX1bqErPuXtjNRRHFLYG3Si5LTdc4xUfeYgvq_WnpfGx8SnHio0C9pxEfDhhGEJ_603yMcH9Ygm8J4EK0ooBKw"
  ]
}
```

Its one value is the presentation: the credential as issued, then the two
disclosures of the first option the request offers, then the Key Binding JWT.
The other six disclosures, `nip` among them, are absent, and nothing in what
travels says which they were.

``` { .text title="An SD-JWT VC presentation" data-format="SD-JWT VC" }
eyJ0eXAiOiJkYytzZC1qd3QiLCJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDp3ZWJ2aDpRbWU4UnJp
R25LeDVqMlFqb2FZMVNnUlNweFRIZGpxMTFMMkV4Z3kxelYyeHNKOmJrbi5nby5pZCNpc3N1YW5j
ZS1qb3NlLTEifQ.eyJpc3MiOiJkaWQ6d2Vidmg6UW1lOFJyaUduS3g1ajJRam9hWTFTZ1JTcHhUS
GRqcTExTDJFeGd5MXpWMnhzSjpia24uZ28uaWQiLCJ2Y3QiOiJpZC5pZGN0Zi5rYXJ0dS1hc24uM
SIsImNuZiI6eyJqd2siOnsia3R5IjoiRUMiLCJjcnYiOiJQLTI1NiIsIngiOiIzQ09oeE9lT3hwQ
k9qVUpncVdTQVUwUUFBWWFZZ3VnUFZKXzJYMnFHZGtjIiwieSI6IjJrOTg4NTRwQjc3dWRkUnZlO
E80a2c1bklQVDdFakVncGJlS3FXTHVNRUUifX0sIl9zZF9hbGciOiJzaGEtMjU2IiwiX3NkIjpbI
jF6QTdMcXNPdGJoTFZRaG9fUlNlMFRHcVJyZmctUzU4SlpHV1NmZzZabU0iLCJDZnVRdi1jS3Jne
mYwdXpIeHUtVEJFQkp2dFo0UEE3U0RhVjloOFQ5TF9RIiwiRVQ5QmlsbFV3VmRoYkhjNnRmXy0xW
EFDRWdWUDRiX2lVUHhIQ2FYQlNiYyIsIkhMeVU4aHRZWno0TmkyZlJkN3BTWWRpQ2JCLXF0NDhwQ
lM5aDJCR013VFEiLCJlNlVoQk44QXk1emRVUGdDX2htbnBXbGR3QnhpWDhGN2tPVzRuUklwNXdNI
iwiZkFoREt6VjNVMzlqQzZiN0dMaEdGRGw3NnVnVy1tN0R6N1hxcUJuamxkYyIsImhLTUpsakZJT
lQtd0ljUDhFUnJhWURrSExyMjZPWUJTQUlHS0ItMG5ORzgiLCJ3N0MxZXJCNno4OG1oRVZzTm5hU
VlEZ2JacUNIakxsM2NieDFFemllUnFzIl0sInN0YXR1cyI6eyJzdGF0dXNfbGlzdCI6eyJpZHgiO
jQ4MTkyMCwidXJpIjoiaHR0cHM6Ly9ia24uZ28uaWQvc3RhdHVzL2thcnR1LWFzbi0xIn19LCJuY
mYiOjE3OTIyMTY4MTAsImlhdCI6MTc5MjIxNjgxMCwiZXhwIjoxODIzNzUyODEwfQ.Rtt14iNH1C
OHmkwCwvzkYcg2RftZdls7V1WghZc1xZC3GmENzivjroJTPBu2C83Qy4pbdbNsX0lorDW26kbPLg
~WyJ3SXVNc2VoQTM1UEp0RU1yUzRub0NRIiwibmFtYSIsIkJ1ZGkgU2FudG9zbyBXaWNha3Nvbm8
iXQ~WyJSb1o4SHRpMk9JVkJ4NHlNd3Q0UkZRIiwiaW5zdGFuc2kiLCJCYWRhbiBLZXBlZ2F3YWlh
biBOZWdhcmEiXQ~eyJ0eXAiOiJrYitqd3QiLCJhbGciOiJFUzI1NiJ9.eyJpYXQiOjE3OTIyMjEz
MDAsImF1ZCI6ImRlY2VudHJhbGl6ZWRfaWRlbnRpZmllcjpkaWQ6d2Vidmg6UW1VQVRDNWp5ZjV5
Vnk3MkdZQXA4blN2dXdzaHpEeTZ3WVg3V21OWTVVSnRYVDp0ZXJtaW5hbC1udXNhbnRhcmEuY28u
aWQiLCJub25jZSI6ImxEQnRBSkNJa0VoZEhNdkswVnA2clEiLCJzZF9oYXNoIjoiNEtCeEdNWUww
Vk5rMjk2bDVBYW03TW8yN3czd2VzZk45LW5JVUNCZEh6ZyJ9.VX1bqErPuXtjNRRHFLYG3Si5LTd
c4xUfeYgvq_WnpfGx8SnHio0C9pxEfDhhGEJ_603yMcH9Ygm8J4EK0ooBKw
```

The two disclosures that traveled, with the arrays they decode to:

``` { .text title="The disclosures that traveled" data-format="SD-JWT VC" }
~WyJ3SXVNc2VoQTM1UEp0RU1yUzRub0NRIiwibmFtYSIsIkJ1ZGkgU2FudG9zbyBXaWNha3Nvbm8iXQ
  ["wIuMsehA35PJtEMrS4noCQ","nama","Budi Santoso Wicaksono"]
~WyJSb1o4SHRpMk9JVkJ4NHlNd3Q0UkZRIiwiaW5zdGFuc2kiLCJCYWRhbiBLZXBlZ2F3YWlhbiBOZWdhcmEiXQ
  ["RoZ8Hti2OIVBx4yMwt4RFQ","instansi","Badan Kepegawaian Negara"]
```

The Key Binding JWT at the end of it, decoded:

``` { .json title="Key Binding JWT header" data-format="JSON" }
{
  "typ": "kb+jwt",
  "alg": "ES256"
}
```

``` { .json title="Key Binding JWT claims" data-format="JSON" }
{
  "iat": 1792221300,
  "aud": "decentralized_identifier:did:webvh:QmUATC5jyf5yVy72GYAp8nSvuwshzDy6wYX7WmNY5UJtXT:terminal-nusantara.co.id",
  "nonce": "lDBtAJCIkEhdHMvK0Vp6rQ",
  "sd_hash": "4KBxGMYL0VNk296l5Aam7Mo27w3wesfN9-nIUCBdHzg"
}
```

### An `ldp_vc` presentation {#ts-5-11-an-ldp-vc-presentation}

The same wallet answering a request for the Kartu Nikah, under the
`pencatatan-ahli-waris` use. The credential travels whole, because nothing in
it can be withheld. That registered use therefore names all nine of the
type's attributes. The proof of the key is a second Data Integrity proof over
the presentation that wraps the credential, carrying this request's `nonce` as
`challenge`. The `vp_token` is keyed by the credential query's `id`, as it is
for an SD-JWT VC:

``` { .json title="The vp_token of an ldp_vc presentation" data-format="JSON-LD" }
{
  "kartu-nikah": [
    {
      "@context": [
        "https://www.w3.org/ns/credentials/v2",
        "https://catalog.trust.go.id/type-metadata/kartu-nikah-v1/context.jsonld"
      ],
      "type": [
        "VerifiablePresentation"
      ],
      "holder": "did:key:zDnaexUcd7ETfUxHRrCKpKq7tYbfJCH1AWNN5WDppWYj2RS7Q",
      "verifiableCredential": [
        {
          "@context": [
            "https://www.w3.org/ns/credentials/v2",
            "https://catalog.trust.go.id/type-metadata/kartu-nikah-v1/context.jsonld"
          ],
          "type": [
            "VerifiableCredential",
            "KartuNikah"
          ],
          "issuer": "did:webvh:QmbAb7u9RMjqsZ9L98pe47szJZdnKQLh9KizqNW2WwKac1:kemenag.go.id",
          "validFrom": "2026-10-17T06:00:10Z",
          "validUntil": "2027-10-17T06:00:10Z",
          "credentialSubject": {
            "id": "did:key:zDnaexUcd7ETfUxHRrCKpKq7tYbfJCH1AWNN5WDppWYj2RS7Q",
            "nama_suami": "Arif Setiawan Nugroho",
            "nama_istri": "Nurul Aini Safitri",
            "tanggal_akad": "2025-05-17",
            "nomor_akta_nikah": "0123/0007/V/2025",
            "kua": "KUA Kec. Cibinong",
            "kabupaten_kota": "Kabupaten Bogor",
            "provinsi": "Jawa Barat"
          },
          "credentialStatus": [
            {
              "id": "https://kemenag.go.id/status/kartu-nikah-1-revocation#481920",
              "type": "BitstringStatusListEntry",
              "statusPurpose": "revocation",
              "statusListIndex": "481920",
              "statusListCredential": "https://kemenag.go.id/status/kartu-nikah-1-revocation"
            },
            {
              "id": "https://kemenag.go.id/status/kartu-nikah-1-suspension#481920",
              "type": "BitstringStatusListEntry",
              "statusPurpose": "suspension",
              "statusListIndex": "481920",
              "statusListCredential": "https://kemenag.go.id/status/kartu-nikah-1-suspension"
            }
          ],
          "credentialSchema": {
            "id": "https://catalog.trust.go.id/type-metadata/kartu-nikah-v1/credential-schema.json",
            "type": "JsonSchema",
            "digestSRI": "sha384-ZgGlm2JwrvKbb05pUITOcjghTRr1ImjyhgXstLXKDA/j2LzIwpgUSZwbk7ABXxpn"
          },
          "proof": {
            "type": "DataIntegrityProof",
            "cryptosuite": "ecdsa-rdfc-2019",
            "created": "2026-10-17T06:00:10Z",
            "verificationMethod": "did:webvh:QmbAb7u9RMjqsZ9L98pe47szJZdnKQLh9KizqNW2WwKac1:kemenag.go.id#issuance-jose-1",
            "proofPurpose": "assertionMethod",
            "proofValue": "z3JTvebTQCkzF6G4dX57mTnykwTtDGWD1gBCfBjzpWmkx2PdTocdowomBTR7Qzaef1L34erTcPA16ArhQhiNxS5UW"
          }
        }
      ],
      "proof": {
        "type": "DataIntegrityProof",
        "cryptosuite": "ecdsa-rdfc-2019",
        "created": "2026-10-17T07:15:00Z",
        "verificationMethod": "did:key:zDnaexUcd7ETfUxHRrCKpKq7tYbfJCH1AWNN5WDppWYj2RS7Q#zDnaexUcd7ETfUxHRrCKpKq7tYbfJCH1AWNN5WDppWYj2RS7Q",
        "proofPurpose": "authentication",
        "challenge": "RuHSu26QAGIX4UP7H-ulTA",
        "domain": "decentralized_identifier:did:webvh:QmUATC5jyf5yVy72GYAp8nSvuwshzDy6wYX7WmNY5UJtXT:terminal-nusantara.co.id",
        "proofValue": "z4LeoqAxQA3HaH4VjaNg9FmPYDdoEUYUQXYx1sob1MiWyy5sgjedFZUDA9AUPHJzZjafAc3Duvywfhp8vsarv1nP5"
      }
    }
  ]
}
```

### An mdoc presentation in proximity {#ts-5-11-an-mdoc-presentation-in-proximity}

The `DeviceResponse` the wallet sends over the session, carrying one data
element of one document:

``` { .text title="The DeviceResponse, as sent" data-format="CBOR" }
a366737461747573006776657273696f6e63312e3069646f63756d656e747381a367646f6354
7970656e69642e69646374662e6b74702e316c6465766963655369676e6564a26a6465766963
6541757468a16f6465766963655369676e61747572658443a10126a0f65840477338544fb353
f924e8f0994d657d503ac7638c878f151b1226882bb72d0c22d7c24b4a1988eb3476e83ca206
2b8cfe274a32007731d575fedcbbde5210afdf6a6e616d65537061636573d81841a06c697373
7565725369676e6564a26a697373756572417574688443a10126a118215902ae308202aa3082
0250a003020102020c16a98534626a68b21d10c09b300a06082a8648ce3d0403023059310b30
09060355040613024944312b3029060355040a0c22547275737420417574686f726974792052
657075626c696b20496e646f6e65736961311d301b06035504030c1449444354462049737375
657220526f6f74204341301e170d3236303930313030303030305a170d323731313031303030
3030305a307c310b3009060355040613024944313e303c060355040a0c35446972656b746f72
6174204a656e646572616c204b6570656e647564756b616e2064616e2050656e636174617461
6e20536970696c312d302b06035504030c2444756b636170696c206d646f6320446f63756d65
6e74205369676e657220323032362d413059301306072a8648ce3d020106082a8648ce3d0301
0703420004d186cc636737d34188257ae33074ea8b1f40a38e31276be9bf54e81a26345ca304
c7d8adf082ebb7b050041778ec0ce19f143e4076197c026a331f532fa78364a381da3081d730
0c0603551d130101ff04023000300e0603551d0f0101ff04040302078030150603551d250101
ff040b3009060728818c5d050102301f0603551d23041830168014fbf0d56ab0bfda804a32ed
dd33ccc9ddd283799a301d0603551d0e04160414eeadd07e695e6a68950188f2cf92e6c566c9
a8dd301e0603551d1204173015861368747470733a2f2f74727573742e676f2e696430400603
551d1f043930373035a033a031862f68747470733a2f2f72656769737472792e74727573742e
676f2e69642f63726c2f6973737565722d726f6f742d6361300a06082a8648ce3d0403020348
00304502201edae3b5dac8d94c01debc4e8d305f3c7e3a90701d8722fc55aa28a9be90ca6902
2100e1f31e36a6b297303e3a8bcbe00d397d45ab75f6f97b22a0ecc5d353dd2bd8ef590482d8
1859047da766737461747573a16b7374617475735f6c697374a2636964781a00075a80637572
69782368747470733a2f2f64756b636170696c2e676f2e69642f7374617475732f6b74702d37
67646f63547970656e69642e69646374662e6b74702e316776657273696f6e63312e306c7661
6c6964697479496e666fa3667369676e6564c074323032362d31302d31375430363a30303a31
305a6976616c696446726f6dc074323032362d31302d31375430363a30303a31305a6a76616c
6964556e74696cc074323032372d30312d31355430363a30303a31305a6c76616c7565446967
65737473a16e69642e69646374662e6b74702e31b41a1eae7aca5820969d6b9f8caa888adeb8
511704351b467c4b15f1a8d0bf742d7c4b81c41c52d51a2a153b8f5820d3d5963f3eaaabcd99
34287091b698d0191d4560b272706c65bcac4187fdf5bd1a305148c5582033f032060e3078ab
96b4a75966d14a8a11163607158b61b5e0907c28ffe31ec41a3df00192582071234abfed33da
cc47a2404b3a27ed46d3fa3e95628195c0aa7597346a3432031a3f3e48cb58207232a83d154a
2985fd0edad4b60ad4af1a12a3ff9e3aee98433753a0ca6f0ff71a4282129c5820ad9c266608
d711d800a1cca8f38ec66af1291b33ba999902bd0923731b1c62a01a4a29657d5820b98635a8
c8af79dcbd2643bd1ab02ae6936b510a4f06ec167fb697ff4a6a5adb1a5a29effe5820956884
2eaae203290039cc507e59b5f1d6c6fb34a26662d2c4c7218762c5c6ce1a5bc6a7d35820fb44
1e9a38cf10d9185e5bcefdd8299f3185a582dc25a2228e6752849332ae391a6512f379582045
9eb92c0576083efdf079bc2cdcaa8ca73b17a403ff80d74eb094d5982d71a81a69eae2365820
b88abb8ed9ba4fcbc2f9ad23372a7d14a696edf9f26c6523428a26f427b71dc41a6a5c174b58
20a3f6dbb37157efdbb00010f95ce5e61af30520017eb7e8ae26930242b5ca4cac1a6d4bbc00
5820d0de7fa5c7c5645872f3e4d1333226cb9efe9398ed4399437dd525305b9be8691a6e4a87
475820909e6f33c99a5057c507e626fa93db18aa966eaf79b27117ef6040e4528acd8a1a7174
245c5820e0421c7acb5c6ce84a4d9d8fac575cec4cba3d934b5560c75df632a187e18ecd1a71
864e715820aeb439baaa64f3dc57bc818ee92c7b8cc10e6d0abe1f7bd7a5847b00ed51cfa41a
736348c95820d0d95bc8a974e5ea4df2c46dcffd259fbe46cdea94f3a07f1c54d8d447c29f21
1a79bc264d5820c280534630b1a8c1632d1f9c4480e7841a35135eb363f2b8bf6d41531ebb17
7f1a7b134d3b5820a075f55adbf32598926cf59efb120270a9d4f5e199dbd42e88547a950afe
5f061a7e81a8d658200a641643c3d05b4092912a6b5b16db84f200731a5dda44d1731b2469c0
cd96036d6465766963654b6579496e666fa1696465766963654b6579a401022001215820dc23
a1c4e78ec6904e8d4260a9648053440001869882e80f549ff65f6a867647225820da4f7cf39e
2907beee75d46f7bc3b8920e6720f4fb123120a5b78aa962ee30416f646967657374416c676f
726974686d675348412d323536584034f75e1ce8f1d897d0f7044679bcfcdfebc870c8cb17c8
e431bd210b93db75073fe12adaba811ad5641fe245092a77d77f731967cc431b4d301c0d9ea1
b72d146a6e616d65537061636573a16e69642e69646374662e6b74702e3181d8185857a46672
616e646f6d50e22dfff74e8aa035175b4e2a29e897896864696765737449441a71864e716c65
6c656d656e7456616c7565f571656c656d656e744964656e7469666965726f757369615f6469
5f617461735f3137
```

The same bytes in Concise Binary Object Representation (CBOR) diagnostic
notation. `issuerAuth` is the one the issuer signed, unchanged, and only the
disclosed item travels beside it:

``` { .text title="The DeviceResponse, in CBOR diagnostic notation" data-format="CBOR diag" }
{
  "status": 0,
  "version": "1.0",
  "documents": [
    {
      "docType": "id.idctf.ktp.1",
      "deviceSigned": {
        "deviceAuth": {
          "deviceSignature": [
            h'a10126',
            {

            },
            null,
            h'477338544fb353f924e8f0994d657d503ac7638c878f151b1226882bb72d0c22d7c24b4a1988eb3476e83ca2062b8cfe274a32007731d575fedcbbde5210afdf'
          ]
        },
        "nameSpaces": 24(<< {

        } >>)
      },
      "issuerSigned": {
        "issuerAuth": [
          h'a10126',
          {
            33: h'308202aa30820250a003020102020c16a98534626a68b21d10c09b300a06082a8648ce3d0403023059310b3009060355040613024944312b3029060355040a0c22547275737420417574686f726974792052657075626c696b20496e646f6e65736961311d301b06035504030c1449444354462049737375657220526f6f74204341301e170d3236303930313030303030305a170d3237313130313030303030305a307c310b3009060355040613024944313e303c060355040a0c35446972656b746f726174204a656e646572616c204b6570656e647564756b616e2064616e2050656e6361746174616e20536970696c312d302b06035504030c2444756b636170696c206d646f6320446f63756d656e74205369676e657220323032362d413059301306072a8648ce3d020106082a8648ce3d03010703420004d186cc636737d34188257ae33074ea8b1f40a38e31276be9bf54e81a26345ca304c7d8adf082ebb7b050041778ec0ce19f143e4076197c026a331f532fa78364a381da3081d7300c0603551d130101ff04023000300e0603551d0f0101ff04040302078030150603551d250101ff040b3009060728818c5d050102301f0603551d23041830168014fbf0d56ab0bfda804a32eddd33ccc9ddd283799a301d0603551d0e04160414eeadd07e695e6a68950188f2cf92e6c566c9a8dd301e0603551d1204173015861368747470733a2f2f74727573742e676f2e696430400603551d1f043930373035a033a031862f68747470733a2f2f72656769737472792e74727573742e676f2e69642f63726c2f6973737565722d726f6f742d6361300a06082a8648ce3d040302034800304502201edae3b5dac8d94c01debc4e8d305f3c7e3a90701d8722fc55aa28a9be90ca69022100e1f31e36a6b297303e3a8bcbe00d397d45ab75f6f97b22a0ecc5d353dd2bd8ef'
          },
          h'd81859047da766737461747573a16b7374617475735f6c697374a2636964781a00075a8063757269782368747470733a2f2f64756b636170696c2e676f2e69642f7374617475732f6b74702d3767646f63547970656e69642e69646374662e6b74702e316776657273696f6e63312e306c76616c6964697479496e666fa3667369676e6564c074323032362d31302d31375430363a30303a31305a6976616c696446726f6dc074323032362d31302d31375430363a30303a31305a6a76616c6964556e74696cc074323032372d30312d31355430363a30303a31305a6c76616c756544696765737473a16e69642e69646374662e6b74702e31b41a1eae7aca5820969d6b9f8caa888adeb8511704351b467c4b15f1a8d0bf742d7c4b81c41c52d51a2a153b8f5820d3d5963f3eaaabcd9934287091b698d0191d4560b272706c65bcac4187fdf5bd1a305148c5582033f032060e3078ab96b4a75966d14a8a11163607158b61b5e0907c28ffe31ec41a3df00192582071234abfed33dacc47a2404b3a27ed46d3fa3e95628195c0aa7597346a3432031a3f3e48cb58207232a83d154a2985fd0edad4b60ad4af1a12a3ff9e3aee98433753a0ca6f0ff71a4282129c5820ad9c266608d711d800a1cca8f38ec66af1291b33ba999902bd0923731b1c62a01a4a29657d5820b98635a8c8af79dcbd2643bd1ab02ae6936b510a4f06ec167fb697ff4a6a5adb1a5a29effe58209568842eaae203290039cc507e59b5f1d6c6fb34a26662d2c4c7218762c5c6ce1a5bc6a7d35820fb441e9a38cf10d9185e5bcefdd8299f3185a582dc25a2228e6752849332ae391a6512f3795820459eb92c0576083efdf079bc2cdcaa8ca73b17a403ff80d74eb094d5982d71a81a69eae2365820b88abb8ed9ba4fcbc2f9ad23372a7d14a696edf9f26c6523428a26f427b71dc41a6a5c174b5820a3f6dbb37157efdbb00010f95ce5e61af30520017eb7e8ae26930242b5ca4cac1a6d4bbc005820d0de7fa5c7c5645872f3e4d1333226cb9efe9398ed4399437dd525305b9be8691a6e4a87475820909e6f33c99a5057c507e626fa93db18aa966eaf79b27117ef6040e4528acd8a1a7174245c5820e0421c7acb5c6ce84a4d9d8fac575cec4cba3d934b5560c75df632a187e18ecd1a71864e715820aeb439baaa64f3dc57bc818ee92c7b8cc10e6d0abe1f7bd7a5847b00ed51cfa41a736348c95820d0d95bc8a974e5ea4df2c46dcffd259fbe46cdea94f3a07f1c54d8d447c29f211a79bc264d5820c280534630b1a8c1632d1f9c4480e7841a35135eb363f2b8bf6d41531ebb177f1a7b134d3b5820a075f55adbf32598926cf59efb120270a9d4f5e199dbd42e88547a950afe5f061a7e81a8d658200a641643c3d05b4092912a6b5b16db84f200731a5dda44d1731b2469c0cd96036d6465766963654b6579496e666fa1696465766963654b6579a401022001215820dc23a1c4e78ec6904e8d4260a9648053440001869882e80f549ff65f6a867647225820da4f7cf39e2907beee75d46f7bc3b8920e6720f4fb123120a5b78aa962ee30416f646967657374416c676f726974686d675348412d323536',
          h'34f75e1ce8f1d897d0f7044679bcfcdfebc870c8cb17c8e431bd210b93db75073fe12adaba811ad5641fe245092a77d77f731967cc431b4d301c0d9ea1b72d14'
        ],
        "nameSpaces": {
          "id.idctf.ktp.1": [
            24(<< {
              "random": h'e22dfff74e8aa035175b4e2a29e89789',
              "digestID": 1904627313,
              "elementValue": true,
              "elementIdentifier": "usia_di_atas_17"
            } >>)
          ]
        }
      }
    }
  ]
}
```

The `SessionTranscript` both sides built independently, the bytes the
`deviceSignature` is taken over. It is not transmitted:

``` { .text title="The SessionTranscript of that session" data-format="CBOR diag" }
[
  24(<< {
    0: "1.0",
    1: [
      1,
      24(<< {
        1: 2,
        -1: 1,
        -2: h'a3255df40a9b0c3c960015d5bd3027a07ccf7992db5a5dd49015d124ab850750',
        -3: h'2064870aa041a7809de901d7d912d6de5217122492aeadc3973d02cc38355d2e'
      } >>)
    ],
    2: [
      [
        2,
        1,
        {
          0: false,
          1: true,
          11: h'45efef742b2c4837a9a3b0e1d05a6917'
        }
      ]
    ]
  } >>),
  24(<< {
    1: 2,
    -1: 1,
    -2: h'60ed1de1facf2443f8f4d2e3692ee956e4956034f712238ffaa5a6017534a279',
    -3: h'd0d3ab6943faa692262db0f90c2218a8fa4cce2c521fae0a54c56b8b1b7a928a'
  } >>),
  null
]
```

## Choosing what to disclose {#ts-5-11-choosing-what-to-disclose}

A presentation carries what the request asked for and nothing beside it. Four
bounds narrow the answer. The wallet applies the request, the Use Statement, and
the certificate before it shows the citizen anything; what the citizen releases
is the fourth.

1. **What the request asks for.** The claims of the credential query online,
   or, where it carries `claim_sets`, those of the first option the other
   bounds leave whole; the data elements of the `ItemsRequest` in
   proximity.
2. **What the Use Statement allows.** The wallet refuses the difference before
   the citizen is asked, which [REQ-TS-5-06-067][req-ts-5-06-067] fixes.
3. **What the certificate allows**, in proximity, where `ReaderAuthRole` is a
   second bound alongside the Use Statement, which
   [REQ-TS-5-04-101][req-ts-5-04-101] fixes.
4. **What the citizen consents to.** The citizen approves every claim the
   first three leave, or refuses, and the wallet sends no part of an answer
   the citizen did not approve whole. [OpenID4VP][ref-openid4vp] returns a
   credential only with every claim its query asks for, and a verifier that
   receives part of what it needs cannot serve the citizen yet still holds
   their data.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-11-009 }**REQ-TS-5-11-009** In an SD-JWT VC and in an mdoc, Mobile Wallet MUST NOT disclose a claim the request did not ask for.
- [](){ #req-ts-5-11-010 }**REQ-TS-5-11-010** In an `ldp_vc`, Mobile Wallet MUST present the credential whole, because its proof covers every claim and withholding one breaks it.
- [](){ #req-ts-5-11-011 }**REQ-TS-5-11-011** In an SD-JWT VC and in an mdoc, Mobile Wallet MUST disclose only the claims the citizen released for this request.
- [](){ #req-ts-5-11-012 }**REQ-TS-5-11-012** Mobile Wallet MUST NOT send an `ldp_vc` presentation where the citizen released fewer than every claim of the credential.
- [](){ #req-ts-5-11-094 }**REQ-TS-5-11-094** In an SD-JWT VC and in an mdoc, Mobile Wallet MUST NOT present a credential where the citizen released fewer than every claim of it that the request, the Use Statement, and the certificate leave, which under `claim_sets` are the claims of the option it answers.
- [](){ #req-ts-5-11-095 }**REQ-TS-5-11-095** Mobile Wallet MUST answer a credential query that carries `claim_sets` with the first of its options that includes no attribute refused under [REQ-TS-5-06-067][req-ts-5-06-067].
- [](){ #req-ts-5-11-013 }**REQ-TS-5-11-013** Mobile Wallet MUST build a presentation for one request only.
- [](){ #req-ts-5-11-014 }**REQ-TS-5-11-014** Mobile Wallet MUST NOT reuse a presentation it built for an earlier request.
- [](){ #req-ts-5-11-015 }**REQ-TS-5-11-015** Mobile Wallet MUST present one credential per credential query.
- [](){ #req-ts-5-11-016 }**REQ-TS-5-11-016** Mobile Wallet MUST NOT present a second credential of the same type in one answer.
- [](){ #req-ts-5-11-017 }**REQ-TS-5-11-017** Mobile Wallet MUST refuse a request for a credential whose representation the request's mode does not carry.

</div>

## The SD-JWT VC presentation {#ts-5-11-the-sd-jwt-vc-presentation}

A presented SD-JWT VC is the issuer-signed JSON Web Token (JWT) as issued, then
the disclosures
that travel, then a Key Binding JWT.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-11-018 }**REQ-TS-5-11-018** Mobile Wallet MUST send the issuer-signed JWT byte for byte as the issuer signed it.
- [](){ #req-ts-5-11-019 }**REQ-TS-5-11-019** Mobile Wallet MUST send each disclosure byte for byte as the issuer built it.
- [](){ #req-ts-5-11-020 }**REQ-TS-5-11-020** Mobile Wallet MUST serialize a presentation as the issuer-signed JWT, then every disclosed disclosure each preceded by `~`, then `~`, then the Key Binding JWT.
- [](){ #req-ts-5-11-021 }**REQ-TS-5-11-021** Mobile Wallet MUST place the presentation in `vp_token` under the `id` of the credential query it answers.
- [](){ #req-ts-5-11-022 }**REQ-TS-5-11-022** The value under that `id` MUST be an array holding exactly one presentation.

</div>

### The Key Binding JWT {#ts-5-11-the-key-binding-jwt}

`sd_hash`
covers the credential and the disclosures that travel with it, so a disclosure
added or removed in transit invalidates the whole answer.

[](){ #tbl-ts-5-11-kb-jwt }

<figure markdown="1" class="ekdn-table">

| Claim | Type | Presence | What it carries |
|---|---|---|---|
| `iat` | number | Present | The moment the wallet signed |
| `aud` | string | Present | The `client_id` of the request, with its prefix |
| `nonce` | string | Present | The `nonce` of the request |
| `sd_hash` | string | Present | The digest of everything before the Key Binding JWT |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-11-023 }**REQ-TS-5-11-023** A Key Binding JWT MUST be a JSON Web Signature in compact serialization, as [RFC 7515][ref-rfc7515] defines it.
- [](){ #req-ts-5-11-024 }**REQ-TS-5-11-024** The `typ` header parameter MUST be `kb+jwt`.
- [](){ #req-ts-5-11-025 }**REQ-TS-5-11-025** The `alg` header parameter MUST name a digital signature algorithm the Governance Profile allows for a credential key.
- [](){ #req-ts-5-11-026 }**REQ-TS-5-11-026** The header MUST carry `typ` and `alg` and no other parameter, because the key is found in the credential's `cnf` and not from the token.
- [](){ #req-ts-5-11-027 }**REQ-TS-5-11-027** Mobile Wallet MUST sign the Key Binding JWT with the credential key that the credential's `cnf` claim names.
- [](){ #req-ts-5-11-028 }**REQ-TS-5-11-028** Mobile Wallet MUST include every claim [the table of a Key Binding JWT][tbl-ts-5-11-kb-jwt] lists and no other claim.
- [](){ #req-ts-5-11-029 }**REQ-TS-5-11-029** `aud` MUST be the `client_id` of the request as the request wrote it, including its Client Identifier Prefix.
- [](){ #req-ts-5-11-030 }**REQ-TS-5-11-030** `nonce` MUST be the `nonce` of the request, byte for byte.
- [](){ #req-ts-5-11-031 }**REQ-TS-5-11-031** `sd_hash` MUST be the digest, under the algorithm the credential's `_sd_alg` claim names, of the ASCII bytes of the presentation up to and including the tilde that precedes the Key Binding JWT.
- [](){ #req-ts-5-11-032 }**REQ-TS-5-11-032** Mobile Wallet MUST build a Key Binding JWT for one presentation only.

</div>

## The `ldp_vc` presentation {#ts-5-11-the-ldp-vc-presentation}

An `ldp_vc` presentation is a
[W3C Verifiable Credentials Data Model (VCDM) 2.0][ref-vc-data-2-0]
`VerifiablePresentation` holding the
credential whole, secured with a second Data Integrity proof in the
[`ecdsa-rdfc-2019`][ref-vc-di-ecdsa] cryptosuite. That proof plays
the part the Key Binding JWT plays for an SD-JWT VC: it is made with the
credential key, and it carries the request's values as `challenge` and `domain`.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-11-033 }**REQ-TS-5-11-033** An `ldp_vc` presentation MUST be a `VerifiablePresentation` whose `@context` is the one the credential carries.
- [](){ #req-ts-5-11-034 }**REQ-TS-5-11-034** `verifiableCredential` MUST hold the credential as the issuer signed it, with its own proof unchanged.
- [](){ #req-ts-5-11-035 }**REQ-TS-5-11-035** `holder` MUST be the holder identifier of the credential key.
- [](){ #req-ts-5-11-036 }**REQ-TS-5-11-036** `holder` MUST equal the `credentialSubject.id` of the credential it carries.
- [](){ #req-ts-5-11-037 }**REQ-TS-5-11-037** The presentation's proof MUST be a Data Integrity proof with `cryptosuite` `ecdsa-rdfc-2019`.
- [](){ #req-ts-5-11-038 }**REQ-TS-5-11-038** `proofPurpose` MUST be `authentication`, so that a presentation proof is never mistaken for an issuer's assertion.
- [](){ #req-ts-5-11-039 }**REQ-TS-5-11-039** `challenge` MUST be the `nonce` of the request, byte for byte.
- [](){ #req-ts-5-11-040 }**REQ-TS-5-11-040** `domain` MUST be the `client_id` of the request as the request wrote it, including its Client Identifier Prefix.
- [](){ #req-ts-5-11-041 }**REQ-TS-5-11-041** `verificationMethod` MUST be the `did:key` of the credential key as a DID URL, whose fragment repeats its body, as [REQ-TS-5-03-006][req-ts-5-03-006] requires.
- [](){ #req-ts-5-11-042 }**REQ-TS-5-11-042** Mobile Wallet MUST sign the presentation with the credential key.
- [](){ #req-ts-5-11-043 }**REQ-TS-5-11-043** Mobile Wallet MUST NOT fetch a context while it builds a presentation.
- [](){ #req-ts-5-11-044 }**REQ-TS-5-11-044** Mobile Wallet MUST place the presentation in `vp_token` under the `id` of the credential query it answers, as an array holding exactly one presentation.

</div>

## The mdoc presentation {#ts-5-11-the-mdoc-presentation}

A proximity presentation is a `DeviceResponse`. It carries the issuer's own
`issuerAuth` unchanged, the items the citizen released, and a `DeviceAuth` made
with the credential key over the transcript of the session both sides saw.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-11-045 }**REQ-TS-5-11-045** A `DeviceResponse` MUST carry `version`, `documents`, and `status`.
- [](){ #req-ts-5-11-046 }**REQ-TS-5-11-046** `version` MUST be `1.0`.
- [](){ #req-ts-5-11-047 }**REQ-TS-5-11-047** Each entry of `documents` MUST carry `docType`, `issuerSigned`, and `deviceSigned`.
- [](){ #req-ts-5-11-048 }**REQ-TS-5-11-048** `issuerAuth` MUST be the one the issuer signed, byte for byte.
- [](){ #req-ts-5-11-049 }**REQ-TS-5-11-049** `issuerSigned.nameSpaces` MUST carry only the items the citizen released, each wrapped in CBOR tag 24 exactly as the issuer built it.
- [](){ #req-ts-5-11-050 }**REQ-TS-5-11-050** Mobile Wallet MUST NOT alter `digestID`, `random`, `elementIdentifier`, or `elementValue` of an item it discloses.
- [](){ #req-ts-5-11-051 }**REQ-TS-5-11-051** `deviceSigned.nameSpaces` MUST be an empty map wrapped in CBOR tag 24, because no data element of IDCTF is signed by the device rather than by the issuer.
- [](){ #req-ts-5-11-052 }**REQ-TS-5-11-052** Mobile Wallet MUST encode every CBOR structure it builds for a `DeviceResponse` with the deterministic encoding [ISO/IEC 18013-5][ref-iso-18013-5] requires, which orders the keys of a map by length and then by value.
- [](){ #req-ts-5-11-053 }**REQ-TS-5-11-053** Mobile Wallet MUST forward a structure the issuer signed without re-encoding it, because a re-encoded structure is a different sequence of bytes and the signature is over the bytes.

</div>

### DeviceAuth and the SessionTranscript {#ts-5-11-deviceauth-and-the-sessiontranscript}

`DeviceAuth` carries a `deviceSignature` and never a `deviceMac`, as
[the two columns compared][tbl-online-versus-offline] records. The signature is taken over
`DeviceAuthentication`, which names the session, the document type, and the
device-signed namespaces. A mismatch between the transcripts each side builds
means the two were not in the same session.

1. **Build the transcript.** `SessionTranscript` is the `DeviceEngagement` the
   reader read, the reader's ephemeral public key, and the handover, each of the
   first two wrapped in CBOR tag 24. The handover is `null` after a QR code
   and the NFC handover after a tap, as
   [Session establishment and encryption][ts-3-02-session-establishment-and-encryption]
   fixes.
2. **Build `DeviceAuthentication`.** The fixed string
   `DeviceAuthentication`, the transcript, the `docType`, and the device-signed
   namespaces.
3. **Wrap and sign.** The structure is encoded, wrapped in CBOR tag 24, and that
   is the detached payload of the `COSE_Sign1`.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-11-054 }**REQ-TS-5-11-054** `deviceAuth` MUST carry `deviceSignature`.
- [](){ #req-ts-5-11-055 }**REQ-TS-5-11-055** `deviceAuth` MUST NOT carry `deviceMac`.
- [](){ #req-ts-5-11-056 }**REQ-TS-5-11-056** `deviceSignature` MUST be a `COSE_Sign1` as [RFC 9052][ref-rfc9052] defines it, with the payload detached.
- [](){ #req-ts-5-11-057 }**REQ-TS-5-11-057** Its protected header MUST carry label 1 and no other label.
- [](){ #req-ts-5-11-058 }**REQ-TS-5-11-058** Label 1 MUST name an algorithm the Governance Profile allows for a credential key.
- [](){ #req-ts-5-11-059 }**REQ-TS-5-11-059** Its unprotected header MUST be empty, because the key is found in the Mobile Security Object and not from the message.
- [](){ #req-ts-5-11-060 }**REQ-TS-5-11-060** Mobile Wallet MUST sign with the credential key the Mobile Security Object's `deviceKey` names.
- [](){ #req-ts-5-11-061 }**REQ-TS-5-11-061** The detached payload MUST be the `DeviceAuthentication` structure wrapped in CBOR tag 24 over its encoded form.
- [](){ #req-ts-5-11-062 }**REQ-TS-5-11-062** `DeviceAuthentication` MUST be an array of the string `DeviceAuthentication`, the `SessionTranscript`, the `docType`, and the device-signed namespaces.
- [](){ #req-ts-5-11-063 }**REQ-TS-5-11-063** `SessionTranscript` MUST be an array of the `DeviceEngagement` wrapped in CBOR tag 24, the reader's ephemeral public key wrapped in CBOR tag 24, and the handover the engagement produced.
- [](){ #req-ts-5-11-064 }**REQ-TS-5-11-064** Mobile Wallet and Mobile Verifier MUST each build the `SessionTranscript` from the values they observed.
- [](){ #req-ts-5-11-065 }**REQ-TS-5-11-065** Mobile Wallet and Mobile Verifier MUST NOT take a member of the `SessionTranscript` from a message the other side sent after engagement.
- [](){ #req-ts-5-11-066 }**REQ-TS-5-11-066** Mobile Wallet MUST NOT transmit the `SessionTranscript`.
- [](){ #req-ts-5-11-067 }**REQ-TS-5-11-067** The external additional authenticated data of the signature MUST be empty.

</div>

## Binding to the request {#ts-5-11-binding-to-the-request}

Every representation binds the answer to the request that asked for it, and
[the table of request binding][tbl-ts-5-11-binding] says which field carries
which value. A presentation that carries the right claims under the wrong binding answers a
different request from the one that was sent.

[](){ #tbl-ts-5-11-binding }

<figure markdown="1" class="ekdn-table">

| Representation | The verifier's freshness value | The verifier's identity | Covered by |
|---|---|---|---|
| SD-JWT VC | `nonce` of the Key Binding JWT | `aud` of the Key Binding JWT | The credential key's signature |
| `ldp_vc` | `challenge` of the presentation proof | `domain` of the presentation proof | The credential key's signature |
| mdoc | The reader's ephemeral key in the `SessionTranscript` | The reader's certificate, through `ReaderAuth` over the same transcript | The credential key's signature |

</figure>

Proximity carries no `client_id`, so the reader's identity enters the binding
through the session rather than through a field the wallet copies. `ReaderAuth`
and `DeviceAuth` are taken over the same `SessionTranscript`, and a captured
`DeviceResponse` replayed in another session fails against the transcript that
session built.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-11-068 }**REQ-TS-5-11-068** Mobile Wallet MUST bind a presentation to the request with the fields [the table of request binding][tbl-ts-5-11-binding] names for its representation.
- [](){ #req-ts-5-11-069 }**REQ-TS-5-11-069** Mobile Wallet MUST NOT send a presentation whose binding values it did not take from the request it is answering.
- [](){ #req-ts-5-11-070 }**REQ-TS-5-11-070** Verifier Core and Mobile Verifier MUST issue a fresh `nonce` for every OpenID4VP request, drawn from a cryptographically secure random number generator and carrying at least 128 bits of entropy.
- [](){ #req-ts-5-11-071 }**REQ-TS-5-11-071** Verifier Core and Mobile Verifier MUST accept a `nonce` once.
- [](){ #req-ts-5-11-072 }**REQ-TS-5-11-072** Verifier Core and Mobile Verifier MUST refuse a presentation carrying a `nonce` they have already accepted.

</div>

## Verifying a presentation {#ts-5-11-verifying-a-presentation}

The verifier runs the credential checks of
[Reading a credential][ts-5-10-reading-a-credential] first, then the three below,
which reach the presentation rather than the credential. Each is a reason to
refuse on its own.

1. **The presenter holds the key.** Verify the Key Binding JWT against `cnf`,
   the presentation proof against `credentialSubject.id`, or the
   `deviceSignature` against `deviceKey`.
2. **The answer is for this request.** The freshness value and the identity
   value are the ones the verifier sent, [REQ-TS-5-11-080][req-ts-5-11-080] and
   [REQ-TS-5-11-081][req-ts-5-11-081], and for an mdoc the signature verifies
   against the transcript the verifier built,
   [REQ-TS-5-11-084][req-ts-5-11-084].
3. **The answer is what was asked.** A claim the request did not ask
   for is a reason to refuse the presentation rather than to ignore the claim,
   because a wallet that sends more than it was asked for has a defect the
   verifier cannot see the extent of. A claim the request asked for and the
   presentation omits is a reason to refuse it too, because a citizen
   approves a request whole or refuses it.

A verifier asks the issuer nothing while it verifies, and tells the presenting
party nothing about which check failed. Both are fixed for the credential in
[REQ-TS-5-10-120][req-ts-5-10-120] and
[REQ-TS-5-10-121][req-ts-5-10-121], and they hold for the presentation too.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-11-073 }**REQ-TS-5-11-073** Verifier Core and Mobile Verifier MUST verify the proof of the credential key before they read any claim of a presentation.
- [](){ #req-ts-5-11-074 }**REQ-TS-5-11-074** Verifier Core and Mobile Verifier MUST refuse a presentation whose proof of the credential key does not verify.
- [](){ #req-ts-5-11-075 }**REQ-TS-5-11-075** Verifier Core and Mobile Verifier MUST verify a Key Binding JWT with the key in the credential's `cnf`.
- [](){ #req-ts-5-11-076 }**REQ-TS-5-11-076** Verifier Core and Mobile Verifier MUST NOT take that key from the Key Binding JWT itself.
- [](){ #req-ts-5-11-077 }**REQ-TS-5-11-077** Verifier Core and Mobile Verifier MUST refuse a presentation whose Key Binding JWT `typ` is not `kb+jwt`.
- [](){ #req-ts-5-11-078 }**REQ-TS-5-11-078** Verifier Core and Mobile Verifier MUST recompute `sd_hash` over the presentation up to the Key Binding JWT.
- [](){ #req-ts-5-11-079 }**REQ-TS-5-11-079** Verifier Core and Mobile Verifier MUST refuse the presentation if the recomputed `sd_hash` differs from the one it carries.
- [](){ #req-ts-5-11-080 }**REQ-TS-5-11-080** Verifier Core and Mobile Verifier MUST refuse a presentation whose `nonce` or `challenge` is not the one they issued for this request.
- [](){ #req-ts-5-11-081 }**REQ-TS-5-11-081** Verifier Core and Mobile Verifier MUST refuse a presentation whose `aud` or `domain` is not its own `client_id`.
- [](){ #req-ts-5-11-082 }**REQ-TS-5-11-082** Verifier Core and Mobile Verifier MUST refuse an `ldp_vc` presentation whose `proofPurpose` is not `authentication`.
- [](){ #req-ts-5-11-083 }**REQ-TS-5-11-083** Verifier Core and Mobile Verifier MUST refuse an `ldp_vc` presentation whose `holder` does not equal the `credentialSubject.id` of the credential it carries.
- [](){ #req-ts-5-11-084 }**REQ-TS-5-11-084** Mobile Verifier MUST verify `deviceSignature` against the `SessionTranscript` it built itself.
- [](){ #req-ts-5-11-085 }**REQ-TS-5-11-085** Mobile Verifier MUST refuse a `DeviceResponse` whose `deviceSigned.nameSpaces` is not an empty map.
- [](){ #req-ts-5-11-086 }**REQ-TS-5-11-086** Mobile Verifier MUST refuse a `DeviceResponse` whose `docType` differs from the `docType` of the `ItemsRequest` it answers.
- [](){ #req-ts-5-11-087 }**REQ-TS-5-11-087** Verifier Core and Mobile Verifier MUST refuse a presentation carrying a claim they did not ask for.
- [](){ #req-ts-5-11-088 }**REQ-TS-5-11-088** Verifier Core and Mobile Verifier MUST refuse a presentation that omits a claim the request asked for; under a credential query that carries `claim_sets`, the claims asked for are those of any one of its options.

</div>

## What the verifier keeps {#ts-5-11-what-the-verifier-keeps}

A verified presentation leaves a record, and the record is deliberately not the
answer. What a verifier needs later is evidence that a transaction happened and what it
was allowed to be, which is T6 of
[entity chain and transaction chain][entity-chain-and-transaction-chain]. The
attribute values themselves are the citizen's, and the verifier has already used
them by the time the record is written.

A proximity record keeps less. With every `IntentToRetain` at `false`,
[ISO/IEC 18013-5][ref-iso-18013-5] clause 8.3.2.1.2.1 forbids the reader to keep
anything it received from the wallet or derived from it, digests and signatures
included. No consent receipt is produced in proximity: Mobile Verifier
records what it produced itself and nothing the wallet sent, keeping only
what [REQ-TS-5-11-096][req-ts-5-11-096] lists, and the consent is recorded on
the wallet's side.

A Relying Party's own application is the one reader that keeps a value, and
it marks each element its business system keeps with `IntentToRetain` `true`
under [REQ-TS-3-02-075][req-ts-3-02-075], as clause 8.3.2.1.2.1 asks of a
reader that keeps one. The record of the transaction still carries none.

The citizen's consent receipt that [REQ-TS-5-11-089][req-ts-5-11-089] names is
one record of six fields, modeled on [ISO/IEC TS 27560:2023][ref-iso-27560], which
IDCTF borrows from and does not claim conformance to. The verifier signs
nothing new for it.

[](){ #tbl-ts-5-11-consent-receipt }

<figure markdown="1" class="ekdn-table">

| Field | What it holds | Where the verifier takes it from |
|---|---|---|
| Controller | The verifier that asked | The `client_id` of the Request Object: a DID or, for a merchant, `x509_hash` and the digest of the Verifier Device Certificate in `x5c[0]` |
| Purpose | The registered use | The `use_id` of the Use Statement in `verifier_info`, where the Request Object carries one |
| Notice | What the citizen was shown | The SHA-256 digest of the signed Request Object, as the compact JWS the verifier served; it pairs the receipt with the record the wallet keeps of the same transaction |
| Data consented to | What the citizen agreed to release | For each credential presented, its type (`vct`, `doctype`, or `type`) and the `path` of each claim released, never a value; the claims are those of the request, or of the `claim_sets` option answered, as [REQ-TS-5-11-087][req-ts-5-11-087] and [REQ-TS-5-11-088][req-ts-5-11-088] fix them |
| Consent | Whether the citizen agreed | `given` where the wallet answered with `vp_token`, `not given` where it answered `access_denied`, which does not say whether the citizen declined or the wallet had nothing to present, as [when the wallet does not answer][ts-3-01-when-the-wallet-does-not-answer] describes |
| Time | When the answer arrived | The moment the verifier received the response |

</figure>

The receipt carries no holder identifier, no `cnf` key, no claim value, and no
disclosure. A response that carries `invalid_request`, and a request that got no
response, leave no consent receipt, because the citizen was never asked.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-11-089 }**REQ-TS-5-11-089** For an OpenID4VP presentation, Verifier Core and Mobile Verifier MUST record the transaction identifier, the `use_id` of the Use Statement they ran under, the citizen's consent receipt, the version of the trusted list they read, and the moment of the transaction.
- [](){ #req-ts-5-11-090 }**REQ-TS-5-11-090** For an OpenID4VP presentation, Verifier Core and Mobile Verifier MUST record the digest of the presentation.
- [](){ #req-ts-5-11-096 }**REQ-TS-5-11-096** For a proximity presentation, Mobile Verifier MUST record the `use_id` of the Use Statement it ran under, the version of the trusted list it read, the moment of the transaction, and whether it accepted the presentation, and nothing it received from the wallet or derived from it.
- [](){ #req-ts-5-11-091 }**REQ-TS-5-11-091** Verifier Core and Mobile Verifier MUST NOT record the presentation itself.
- [](){ #req-ts-5-11-092 }**REQ-TS-5-11-092** Verifier Core and Mobile Verifier MUST NOT record the value of a disclosed claim.
- [](){ #req-ts-5-11-093 }**REQ-TS-5-11-093** Verifier Core and Mobile Verifier MUST NOT record a disclosure or an `IssuerSignedItem`, because either one carries the value and its salt.
- [](){ #req-ts-5-11-097 }**REQ-TS-5-11-097** Verifier Core and Mobile Verifier MUST write the consent receipt with the fields of [the table of consent receipt fields][tbl-ts-5-11-consent-receipt] for every OpenID4VP response that carries `vp_token` or `access_denied`.
- [](){ #req-ts-5-11-098 }**REQ-TS-5-11-098** Verifier Core and Mobile Verifier MUST NOT keep in the consent receipt any value that [the table of consent receipt fields][tbl-ts-5-11-consent-receipt] does not list.
- [](){ #req-ts-5-11-099 }**REQ-TS-5-11-099** Verifier Core and Mobile Verifier MUST delete a record of [REQ-TS-5-11-089][req-ts-5-11-089] and [REQ-TS-5-11-090][req-ts-5-11-090], and its consent receipt, once the time the Governance Profile sets for keeping it has passed, unless a law binding the party the verifier acts for requires the record to be kept longer.
- [](){ #req-ts-5-11-104 }**REQ-TS-5-11-104** Where a law binding the party the verifier acts for requires a record of [REQ-TS-5-11-089][req-ts-5-11-089] and [REQ-TS-5-11-090][req-ts-5-11-090], or its consent receipt, to be kept beyond the time the Governance Profile sets, Verifier Core and Mobile Verifier MUST delete that record when that duty ends.

</div>

## What the wallet keeps {#ts-5-11-what-the-wallet-keeps}

Mobile Wallet keeps a record of each request it shows the citizen, and the
record is made of what the verifier already signed. Mobile Wallet signs nothing
new for it, and it holds no attribute value. The record lives in the encrypted
Credential Store and travels in the encrypted client-side backup, so the citizen
chooses on a new device whether to restore it, as
[device migration and reissuance][device-migration-and-reissuance] describes.

[](){ #tbl-ts-5-11-presentation-history }

<figure markdown="1" class="ekdn-table">

| Field | What it holds | Where Mobile Wallet takes it from |
|---|---|---|
| Request | What was asked, signed by the party that asked | Online, the signed Request Object as the compact JWS Mobile Wallet received. In proximity, the DocRequest as received, with its `ItemsRequest` and its `readerAuth`. The Use Statement travels inside it (`verifier_info` online, `requestInfo` in proximity), so it is kept as part of the request and not copied separately |
| Outcome | What became of the request | `presented` where Mobile Wallet presented; `refused` where it answered `access_denied` online, or ended the session without presenting in proximity; `failed` where the exchange broke off after the citizen was shown the request and no answer reached the verifier |
| Time | When the exchange ended | The moment Mobile Wallet sent its answer or the exchange ended |

</figure>

Online, the SHA-256 digest of the stored Request Object equals the Notice field
of the verifier's consent receipt in [the table of consent receipt
fields][tbl-ts-5-11-consent-receipt], so the two records of one transaction
can be read against each other. In proximity there is no verifier receipt, and
the wallet's record is the only one. A request that fails a check is never shown
to the citizen and is not recorded, since an unverified request is attributable to
nobody.

The period the Governance Profile sets is the longest a record stays. The
citizen, whose device and whose record it is, may delete it sooner, as
[UU No. 27 Tahun 2022][ref-uu-27-2022] gives a data subject the right to erase
personal data about them.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-11-100 }**REQ-TS-5-11-100** Mobile Wallet MUST write a record with the fields of [the table of presentation history fields][tbl-ts-5-11-presentation-history] for every request it shows the citizen, online and in proximity.
- [](){ #req-ts-5-11-101 }**REQ-TS-5-11-101** Mobile Wallet MUST NOT keep in the record any value that [the table of presentation history fields][tbl-ts-5-11-presentation-history] does not list, in particular no attribute value, no disclosure, no `IssuerSignedItem`, and no presentation.
- [](){ #req-ts-5-11-102 }**REQ-TS-5-11-102** Mobile Wallet MUST delete a record once the time the Governance Profile sets for keeping it has passed.
- [](){ #req-ts-5-11-103 }**REQ-TS-5-11-103** Mobile Wallet MUST let the citizen delete any record, or the whole history, at any time.

</div>

## Security considerations {#ts-5-11-security-considerations}

- **A transcript built from the other side's message binds nothing.** The
  whole value of `SessionTranscript` is that each side built it from what it
  saw. A reader that takes the `DeviceEngagement` out of the wallet's own
  message verifies a signature over a transcript the wallet chose, which a
  captured response can satisfy as easily as a live one.
  [REQ-TS-5-11-064][req-ts-5-11-064] and [REQ-TS-5-11-084][req-ts-5-11-084]
  state the rule for both sides.
- **A nonce the verifier does not remember is no protection.**
  [REQ-TS-5-11-070][req-ts-5-11-070] and [REQ-TS-5-11-071][req-ts-5-11-071]
  fix where the freshness value comes from and that it is spent once.
- **A presentation is good for one audience.** Without `aud` and `domain`, a
  verifier that receives a presentation could forward it to a second
  verifier and be believed as the citizen. The audience value stops
  that: [REQ-TS-5-11-081][req-ts-5-11-081] compares it against
  the verifier's own `client_id`.
- **`sd_hash` is what makes the parts one answer.** The credential, the
  disclosures, and the Key Binding JWT travel as separate strings, and only
  `sd_hash` ties them together. A verifier that checks the Key Binding JWT's
  signature without recomputing `sd_hash` accepts a presentation whose
  disclosures were swapped in transit for other valid disclosures of the
  same credential, as [REQ-TS-5-11-078][req-ts-5-11-078] prevents.
- **An unverified presentation is untrusted input.** Everything in a
  presentation arrives from a device the verifier does not control,
  including the lengths and the nesting a parser walks. A verifier parses
  before it can verify, so the parse is the first thing an attacker reaches,
  and [REQ-TS-5-10-121][req-ts-5-10-121] keeps what it learns from a failure
  to a single bit.

## Privacy considerations {#ts-5-11-privacy-considerations}

- **The verifier learns what it asked for.** The six disclosures that
  stayed on the device leave no trace of what they said: the digests in
  `_sd` were already in the credential, and their order says nothing, as
  [REQ-TS-5-10-035][req-ts-5-10-035] arranges. Their number is not hidden: the
  Credential Rulebook publishes how many claims the type has. The same holds for an mdoc, where `valueDigests`
  carries one digest per item whether or not the item travels.
- **`ldp_vc` has no such property.** A presentation of an `ldp_vc`
  credential carries every claim in it, so a verifier that asks for the type
  asks for all of them, [REQ-TS-3-01-115][req-ts-3-01-115], and its use
  names all of them, [REQ-TS-5-06-119][req-ts-5-06-119]. The bound that
  holds is the one on the format: a Credential Rulebook that names `ldp_vc` carries no restricted
  attribute, as [REQ-CR-017][req-cr-017] requires.
- **One credential key means every verifier sees one identifier.** The same
  key signs every presentation a wallet makes, so two verifiers comparing
  notes can match the holder, as [the holder
  identifier][holder-one-didkey-per-wallet-installation] sets out. In an
  `ldp_vc` presentation that identifier is written out in full, as `holder`
  and as `verificationMethod`. The exposure is one IDCTF accepts, and this
  specification does not widen it.
- **The record is bounded by what it omits.** [REQ-TS-5-11-090][req-ts-5-11-090]
  to [REQ-TS-5-11-093][req-ts-5-11-093] keep attribute values out of the
  verifier's own log, so a later breach of that log yields transactions rather
  than identities. Nothing stops the verifier's business system from storing
  what it was given, which is why the Governance Framework rather than this
  specification
  [governs what happens after the result is handed over][gf-relying-parties].
- **A presentation is non-repudiable.** Because `DeviceAuth` is a signature
  rather than a message authentication code, a verifier can prove to a third
  party that the citizen presented. The ecosystem accepts that for dispute
  resolution, and [the two columns compared][tbl-online-versus-offline]
  records the choice.

## Changelog {#ts-5-11-changelog}

<figure markdown="1" class="ekdn-table">

| Version | Date | Change |
|---|---|---|
| 1.0 draft | 21 October 2026 | First draft |

</figure>
