---
title: KTP Digital
description: An illustrative Rulebook for the resident identity card in ISO mdoc, with its SD-JWT VC Type Metadata and a light and a dark card template.
---

<!-- Sumber: card design supplied by the user, 17 October 2026; Panduan mdoc, Lampiran A; tracks/0199, tracks/0204, tracks/0226, tracks/0253, tracks/0319 -->

# KTP Digital {#ktp-digital}

<p class="ekdn-lead" markdown="span">
One credential type worked through from its Rulebook to the card a wallet
draws: the Kartu Tanda Penduduk (KTP) Digital, the resident identity card of the Ministry of Home
Affairs, issued as an [ISO/IEC 18013-5:2021 mdoc][ref-iso-18013-5].
</p>

!!! note "Informative page"

    This Rulebook is an illustration and is not registered. Its values show
    how the fields of [Rulebook structure](../rulebook-structure.md) fit
    together, and the Root Authority has approved none of them. The addresses
    under `catalog.trust.go.id` do not exist yet, so this page shows the files
    they name.

## The Rulebook {#ktp-digital-rulebook}

The Rulebook for `id.idctf.ktp.1` carries every field
[Rulebook structure](../rulebook-structure.md) lists. It lists `mdoc` alone,
because a KTP Digital has to verify with no network reaching the verifier, as
[REQ-CR-018][req-cr-018] requires. It covers the card of an Indonesian citizen
alone, so `kewarganegaraan` is always `WNI`. It lists no `expiry_date`, because
that card is valid for life under its legal basis and so has no administrative
validity period. A foreign resident's card expires with the residence permit,
and a type covering it would need an `expiry_date`. `usia_di_atas_17` is derived
from `tanggal_lahir`, so a Relying Party that needs only the holder's age never
receives the birth date.

``` { .json title="rulebook.json" data-format="JSON" }
--8<-- "docs/credential-rulebook/example/ktp-digital/rulebook.json"
```

## Schema {#ktp-digital-schema}

This is the [JSON Schema 2020-12][ref-json-schema] that
[the schema field][rulebook-schema-field] points at. Issuer Core checks the
twenty type claims against it before it signs. The schema requires every claim,
so every KTP Digital carries the same number of digests, as
[REQ-CR-077][req-cr-077] requires of a type issued in mdoc. `golongan_darah` is
the one claim the source record may hold no value for, so it carries
`absent_value` `-`. Issuer Core writes that value in its place, as the printed
KTP-el does. Each claim becomes a data element of the same name in the namespace
`id.idctf.ktp.1`, encoded as [the table of mdoc encodings][tbl-mdoc-encodings]
sets out.

``` { .json title="schema.json" data-format="JSON" }
--8<-- "docs/credential-rulebook/example/ktp-digital/schema.json"
```

## Display {#ktp-digital-display}

A wallet draws the card, light and dark, from the
[SD-JWT-based Verifiable Credential (SD-JWT VC) draft -13 Type Metadata][ref-i-d-ietf-oauth-sd-jwt-vc]
that [the display field][rulebook-display-field] points at. The Type Metadata
carries both templates and the logo. Each claim `path` names the namespace and
then the data element, as [REQ-CR-074][req-cr-074] requires of a Rulebook that
lists `mdoc` alone.

[](){ #fig-ktp-digital-light }
[](){ #fig-ktp-digital-dark }

<div class="ekdn-fig-pair" markdown="1">
<figure markdown="1">
  ![Light KTP Digital card filled with a made-up resident](ktp-digital/preview-light.png){ loading=lazy }
  <figcaption><span class="ekdn-fignum"></span> The KTP Digital, light template.</figcaption>
</figure>
<figure markdown="1">
  ![Dark KTP Digital card filled with a made-up resident](ktp-digital/preview-dark.png){ loading=lazy }
  <figcaption><span class="ekdn-fignum"></span> The KTP Digital, dark template.</figcaption>
</figure>
</div>

The templates are [`card-light.svg`](ktp-digital/card-light.svg) and
[`card-dark.svg`](ktp-digital/card-dark.svg).

``` { .json title="type-metadata.json" data-format="JSON" }
--8<-- "docs/credential-rulebook/example/ktp-digital/type-metadata.json"
```

## Issued credential {#ktp-digital-issued-credential}

This section shows one credential as Issuer Core signs it, and where each of
its parts comes from.

``` { .text title="mdoc IssuerSigned and its Mobile Security Object" data-format="CBOR diag" }
// IssuerSigned
{
  "nameSpaces": {
    "id.idctf.ktp.1": [
      24(<< { "digestID": 88829943, "random": h'8f2a61c0...',
              "elementIdentifier": "nik",
              "elementValue": "3174015201950003" } >>),
      24(<< { "digestID": 650865597, "random": h'4be79d13...',
              "elementIdentifier": "nama",
              "elementValue": "Rina Kartika Sari" } >>),
      24(<< { "digestID": 1847969377, "random": h'c105e7a4...',
              "elementIdentifier": "tanggal_lahir",
              "elementValue": 1004("1995-01-12") } >>),
      24(<< { "digestID": 1081400995, "random": h'd4a09ee2...',
              "elementIdentifier": "usia_di_atas_17",
              "elementValue": true } >>),
      ...
      24(<< { "digestID": 407846542, "random": h'7a3e0b52...',
              "elementIdentifier": "issuance_date",
              "elementValue": 1004("2020-01-28") } >>),
      24(<< { "digestID": 548034289, "random": h'1f6c88d9...',
              "elementIdentifier": "foto",
              "elementValue": h'ffd8ffe000104a464946...' } >>)
    ]
  },
  "issuerAuth": [
    h'a10126',                          // protected: {1: -7}, ES256
    { 33: h'30820278308202...' },       // unprotected: x5chain, the Document Signer Certificate
    24(<< MobileSecurityObject >>),     // payload
    h'dcf748da1ba9a849...'              // signature
  ]
}

// MobileSecurityObject
{
  "version": "1.0",
  "digestAlgorithm": "SHA-256",
  "valueDigests": {
    "id.idctf.ktp.1": {
      88829943: h'2b9e04c1...', 650865597: h'67516f23...',
      1847969377: h'91d0a7e5...',
      ...
      548034289: h'0bfd78aa...'
    }
  },
  "deviceKeyInfo": {
    "deviceKey": { 1: 2, -1: 1, -2: h'e1877f64...', -3: h'fde025ca...' }
  },
  "docType": "id.idctf.ktp.1",
  "validityInfo": {
    "signed": 0("2026-10-17T03:12:00Z"),
    "validFrom": 0("2026-10-17T03:12:00Z"),
    "validUntil": 0("2027-01-15T03:12:00Z")
  },
  "status": {
    "status_list": { "idx": 481920,
                     "uri": "https://dukcapil.go.id/status/ktp-7" }
  }
}
```

<figure markdown="1" class="ekdn-table">

| Part | Comes from |
|---|---|
| `nameSpaces` | One `IssuerSignedItem` per type claim, in the namespace `id.idctf.ktp.1`. Each value is read from the issuer's source system by Issuer Core, using its Claims Provider Component, and checked against `schema.json`; `tanggal_lahir` and `issuance_date` are `full-date`, and `foto` is the decoded JPEG bytes, as [the table of mdoc encodings][tbl-mdoc-encodings] sets out |
| `random` | Issuer Core, sixteen fresh bytes per item, so a verifier cannot guess a value from its digest |
| `usia_di_atas_17` | Issuer Core, computed from `tanggal_lahir` at signing, as the Rulebook's `derived_from` names |
| `x5chain` | The issuer's Document Signer Certificate, chained to the Issuer Root CA, as [Document Signer Certificate][ts-5-04-document-signer-certificate] sets out. The issuer is the one the Root Authority authorized for the type in an [Authority Statement][authority-statement], not the Rulebook |
| `valueDigests` | Issuer Core, the SHA-256 of each tagged item, so the holder can disclose one data element and withhold the rest |
| `deviceKeyInfo` | The credential key reported in `attested_keys` of the [Key Attestation][key-attestation], as a COSE key |
| `docType` | The Rulebook's `formats.mdoc.docType`, which equals `id` |
| `validityInfo` | `signed` and `validFrom` are the moment Issuer Core signs. `validUntil` is set by the issuer, within the ceiling the Governance Profile sets, because [a Rulebook carries no technical validity period][what-a-rulebook-does-not-carry] |
| `status` | The credential's entry in the issuer's [status list][status-list], allocated by Issuer Core, using its Status Manager Component |
| `issuerAuth` signature | Issuer Core, signing the Mobile Security Object with the key of its Document Signer Certificate |

</figure>
