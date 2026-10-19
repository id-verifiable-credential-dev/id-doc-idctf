---
title: Kartu ASN
description: An illustrative Rulebook for the civil servant card, with its SD-JWT VC Type Metadata and a light and a dark card template.
---

<!-- Sumber: card design supplied by the user, 16 October 2026; tracks/0198, tracks/0199, tracks/0203, tracks/0204, tracks/0226, tracks/0320, tracks/0321 -->

# Kartu ASN {#kartu-asn}

<p class="ekdn-lead" markdown="span">
One credential type worked through from its Rulebook to the card a wallet
draws: the Kartu ASN, the identity card of an Indonesian civil
servant.
</p>

!!! note "Informative page"

    This Rulebook is an illustration and is not registered. Its values were
    chosen to show how the fields of [Rulebook structure](../rulebook-structure.md)
    fit together, and none of them has been approved by the Root Authority.
    The addresses under `catalog.trust.go.id` do not exist yet; the files they
    name are shown on this page instead.

## The Rulebook {#kartu-asn-rulebook}

The Rulebook for `id.idctf.kartu-asn.1`, carrying every field
[Rulebook structure](../rulebook-structure.md) lists. It lists no
`expiry_date`, because the card it mirrors carries no validity period.

``` { .json title="rulebook.json" data-format="JSON" }
--8<-- "docs/credential-rulebook/example/kartu-asn/rulebook.json"
```

## Schema {#kartu-asn-schema}

The [JSON Schema 2020-12][ref-json-schema] that [the schema field][rulebook-schema-field] points at.
Issuer Core checks the eight type claims against it before it signs.

``` { .json title="schema.json" data-format="JSON" }
--8<-- "docs/credential-rulebook/example/kartu-asn/schema.json"
```

## Display {#kartu-asn-display}

The card a wallet draws, light and dark, and the [SD-JWT-based Verifiable
Credential (SD-JWT VC) draft -13 Type Metadata][ref-i-d-ietf-oauth-sd-jwt-vc] that [the display field][rulebook-display-field]
points at. The Type Metadata carries both templates and the logo.

[](){ #fig-kartu-asn-light }
[](){ #fig-kartu-asn-dark }

<div class="ekdn-fig-pair" markdown="1">
<figure markdown="1">
  ![Light Kartu ASN card filled with a made-up civil servant](kartu-asn/preview-light.png){ loading=lazy }
  <figcaption><span class="ekdn-fignum"></span> The Kartu ASN, light template.</figcaption>
</figure>
<figure markdown="1">
  ![Dark Kartu ASN card filled with a made-up civil servant](kartu-asn/preview-dark.png){ loading=lazy }
  <figcaption><span class="ekdn-fignum"></span> The Kartu ASN, dark template.</figcaption>
</figure>
</div>

Templates: [`card-light.svg`](kartu-asn/card-light.svg) and
[`card-dark.svg`](kartu-asn/card-dark.svg).

``` { .json title="type-metadata.json" data-format="JSON" }
--8<-- "docs/credential-rulebook/example/kartu-asn/type-metadata.json"
```

## Issued credential {#kartu-asn-issued-credential}

One credential as Issuer Core signs it, in both representations the Rulebook
lists, and where each of its parts comes from.

``` { .json title="SD-JWT VC header, payload and disclosure" data-format="SD-JWT VC" }
// header
{ "typ": "dc+sd-jwt", "alg": "ES256", "kid": "did:webvh:QmScid...:bkn.go.id#issuance-jose-1" }

// payload
{
  "iss": "did:webvh:QmScid...:bkn.go.id",
  "vct": "id.idctf.kartu-asn.1",
  "cnf": { "jwk": { "kty": "EC", "crv": "P-256",
                    "x": "9Hs2Kf...Bn4", "y": "6Wc8Lp...Vm1" } },
  "_sd": [ "X8vK2p...", "Lm4Qr9...", "Tz7Wn3...", "Pq2Hd8...",
           "Ra5Ys1...", "Mk9Bv6...", "Cw3Nf7...", "Jt6Ge4..." ],
  "_sd_alg": "sha-256",
  "status": { "status_list": { "idx": 481920,
                 "uri": "https://bkn.go.id/status/kartu-asn-1" } },
  "iat": 1789901520, "exp": 1852973520
}

// disclosure for nama, sent beside the credential
~WyJzYWx0NDU2IiwibmFtYSIsIkJ1ZGkgU2FudG9zbyBXaWNha3Nvbm8iXQ
// decodes to ["salt456", "nama", "Budi Santoso Wicaksono"]
```

<figure markdown="1" class="ekdn-table">

| Claim | Comes from |
|---|---|
| `iss` | The issuer the Root Authority authorized for the type in an [Authority Statement][authority-statement], not the Rulebook |
| `vct` | The Rulebook's `id`, the only claim taken from the Rulebook |
| `cnf` | The credential key reported in `attested_keys` of the [Key Attestation][key-attestation] |
| `_sd`, `_sd_alg` | Issuer Core, which hides each of the eight type claims behind a digest |
| `status` | The credential's entry in the issuer's [status list][status-list], allocated by Issuer Core, using its Status Manager Component |
| `iat` | The moment Issuer Core signs |
| `exp` | The issuer, within the ceiling the Governance Profile sets, because [a Rulebook carries no technical validity period][what-a-rulebook-does-not-carry] |
| `nama` to `foto` | Disclosures, read from the issuer's source system by Issuer Core, using its Claims Provider Component, and checked against `schema.json`; `foto` is sent as a `data:image/jpeg;base64,` URI, as [REQ-CR-070][req-cr-070] requires |

</figure>

The same credential as an mdoc, the representation a verifier reads in
proximity. It carries the same claim values, the same credential key, the same
status entry and the same validity period as the SD-JWT VC above, as
[one credential, two representations][one-credential-two-representations]
requires.

``` { .text title="mdoc IssuerSigned and its Mobile Security Object" data-format="CBOR diag" }
// IssuerSigned
{
  "nameSpaces": {
    "id.idctf.kartu-asn.1": [
      24(<< { "digestID": 1530772984, "random": h'5d0c93ae...',
              "elementIdentifier": "nama",
              "elementValue": "Budi Santoso Wicaksono" } >>),
      24(<< { "digestID": 271946035, "random": h'a8e14f07...',
              "elementIdentifier": "nip",
              "elementValue": "198703152010011002" } >>),
      24(<< { "digestID": 904418726, "random": h'3b72d6c1...',
              "elementIdentifier": "golongan",
              "elementValue": "III/c" } >>),
      ...
      24(<< { "digestID": 1766205319, "random": h'e09a5b38...',
              "elementIdentifier": "foto",
              "elementValue": h'ffd8ffe000104a464946...' } >>)
    ]
  },
  "issuerAuth": [
    h'a10126',                          // protected: {1: -7}, ES256
    { 33: h'30820281308202...' },       // unprotected: x5chain, the Document Signer Certificate
    24(<< MobileSecurityObject >>),     // payload
    h'4f19c2e7a05d8b13...'              // signature
  ]
}

// MobileSecurityObject
{
  "version": "1.0",
  "digestAlgorithm": "SHA-256",
  "valueDigests": {
    "id.idctf.kartu-asn.1": {
      1530772984: h'c47e2a90...', 271946035: h'0e9b5d17...',
      904418726: h'7a31f8c4...',
      ...
      1766205319: h'b2d06e53...'
    }
  },
  "deviceKeyInfo": {
    "deviceKey": { 1: 2, -1: 1, -2: h'f47b36d8...', -3: h'e9673cf0...' }
  },
  "docType": "id.idctf.kartu-asn.1",
  "validityInfo": {
    "signed": 0("2026-09-20T10:52:00Z"),
    "validFrom": 0("2026-09-20T10:52:00Z"),
    "validUntil": 0("2028-09-19T10:52:00Z")
  },
  "status": {
    "status_list": { "idx": 481920,
                     "uri": "https://bkn.go.id/status/kartu-asn-1" }
  }
}
```

<figure markdown="1" class="ekdn-table">

| Part | Comes from |
|---|---|
| `nameSpaces` | One `IssuerSignedItem` for each of the eight type claims, with the values of the disclosures above, in the namespace `id.idctf.kartu-asn.1`, because the Rulebook's `mdoc` entry names no other and [REQ-CR-080][req-cr-080] makes the namespace the `id`. `foto` is the decoded JPEG bytes, where the SD-JWT VC carries a data URI, as [the table of mdoc encodings][tbl-mdoc-encodings] sets out |
| `random` | Issuer Core, sixteen fresh bytes per item, so a verifier cannot guess a value from its digest |
| `x5chain` | BKN's Document Signer Certificate, chained to the Issuer Root CA, as [Document Signer Certificate][ts-5-04-document-signer-certificate] sets out. The SD-JWT VC names the same issuer by its `did:webvh` |
| `valueDigests` | Issuer Core, the SHA-256 of each tagged item, so the holder can disclose one data element and withhold the rest |
| `deviceKeyInfo` | The credential key in `cnf.jwk` of the SD-JWT VC, written as a COSE key |
| `docType` | The Rulebook's `formats.mdoc.docType`, which equals `id` |
| `validityInfo` | `signed` and `validFrom` are the `iat` of the SD-JWT VC, and `validUntil` is its `exp` |
| `status` | The same entry in BKN's [status list][status-list] as the SD-JWT VC, so revoking the credential revokes both representations |
| `issuerAuth` signature | Issuer Core, signing the Mobile Security Object with the key of its Document Signer Certificate |

</figure>
