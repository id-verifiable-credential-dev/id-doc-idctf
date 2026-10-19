---
title: Credential Rulebook Catalog
description: "IDCTF-CR: the rules for each credential type, one Rulebook per type, each owned by the institution responsible for it."
---

<!-- Sumber: IDCTF-AF — Architecture Framework, §0; Glosarium dan Konvensi IDCTF, D.2, D.4; Rincian Module dan Operasi, §2.1; tracks/0214 -->

# Credential Rulebook Catalog {#credential-rulebook-catalog}

<p class="ekdn-lead" markdown="span">
<code>IDCTF-CR</code>. One Rulebook per credential type: its attributes, the
formats it may take, and the assurance it demands. Each Rulebook is changed by
the owner of that credential type, not by the architects.
</p>

A Credential Rulebook holds the rules for one credential type. This catalog is
the list of every Rulebook the Root Authority has approved, together with the
rules every Rulebook has to follow: the fields it carries, and the path a
proposal takes before it is published. Where a Rulebook sits beside the
Governance Profile and the Governance Framework is in
[The Credential Rulebook][the-credential-rulebook].

Trust Registry publishes the catalog on the central content delivery network
(CDN), as a list of types and one file per Rulebook version. Issuers, wallets
and Relying Parties read it from cache. A participant is compliant with this
document when it meets the Rulebook of every credential type it issues or asks
for.

Credential types are named in the `id.idctf.<type>.<N>` namespace, or, for a
private party, under a domain it owns as `<reverse-domain>.<type>.<N>`; a type
another body already named keeps that name with its version appended, as
`org.iso.18013.5.1.mDL.1`.

## Registered Rulebooks {#registered-rulebooks}

No Rulebook has been approved yet. Each approved version is added here as one
row. The five rows below are illustrations worked through in
[Examples](example/index.md), and none is registered. `id.idctf.ktp.1` is also
the identifier the Architecture Framework uses in its examples.

<figure markdown="1" class="ekdn-table">

| Identifier | Credential type | Credential Rulebook Provider | Formats | Status | Details |
|---|---|---|---|---|---|
| `id.idctf.ktp.1` | KTP Digital, the resident identity card the civil registry issues | Kementerian Dalam Negeri | [mdoc][ref-iso-18013-5] | Example, not approved | [KTP Digital](example/rulebook-ktp-digital.md) |
| `id.idctf.kartu-indonesia-sehat.1` | Kartu Indonesia Sehat, the membership card of the national health insurance | Badan Penyelenggara Jaminan Sosial (BPJS) Kesehatan | [SD-JWT VC][ref-i-d-ietf-oauth-sd-jwt-vc] | Example, not approved | [Kartu Indonesia Sehat](example/rulebook-kartu-indonesia-sehat.md) |
| `id.idctf.kartu-asn.1` | Kartu ASN, the card every civil servant (ASN or PNS) in Indonesia holds | Badan Kepegawaian Negara (BKN) | [SD-JWT VC][ref-i-d-ietf-oauth-sd-jwt-vc], [mdoc][ref-iso-18013-5] | Example, not approved | [Kartu ASN](example/rulebook-kartu-asn.md) |
| `id.idctf.kartu-nikah.1` | Kartu Nikah, the marriage card of a couple married in Indonesia | Kementerian Agama Republik Indonesia | [W3C VCDM 2.0][ref-vc-data-2-0] | Example, not approved | [Kartu Nikah](example/rulebook-kartu-nikah.md) |
| `org.iso.18013.5.1.mDL.1` | SIM, the driving license in the form ISO/IEC 18013-5 defines | Korps Lalu Lintas Polri | [mdoc][ref-iso-18013-5] | Example, not approved | [SIM](example/rulebook-sim.md) |

</figure>

## Contents {#cr-contents}

1. [Rulebook structure](rulebook-structure.md)
2. [Admission and versions](admission-and-versions.md)
3. [Examples](example/index.md)
