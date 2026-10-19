---
title: Rulebook structure
description: The fields every Credential Rulebook carries, and the rule each field has to meet before Trust Registry publishes it.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §4.4, Kep. 3, Kep. 13; tracks/0165, tracks/0176, tracks/0183, tracks/0208, tracks/0209, tracks/0211, tracks/0214, tracks/0219, tracks/0220, tracks/0222, tracks/0223, tracks/0225, tracks/0226, tracks/0227, tracks/0253, tracks/0319, tracks/0322, tracks/0323, tracks/0326, tracks/0327 -->

# Rulebook structure {#rulebook-structure}

<p class="ekdn-lead" markdown="span">
A Rulebook is one JSON file per credential type and version. Issuer Core
builds the credential from it, Verifier Core reads what it may ask for, and an
issuer's metadata is generated from it.
</p>

!!! info "Normative page"

    The rules on this page bind. A participant that issues or asks for a
    credential type is compliant only when it meets them, and an Assessment
    Body tests it against them. The capitalized key words carry the meaning
    given in [RFC 2119][ref-rfc2119] and
    [RFC 8174][ref-rfc8174]. Each requirement
    carries an identifier, `REQ-CR-nnn`, numbered across the catalog. A
    number is never reused, and a withdrawn requirement keeps its number,
    marked withdrawn.

Worked examples are in [Examples](example/index.md). Every Rulebook carries
the fields in [the table of Rulebook fields][tbl-rulebook-fields].

[](){ #tbl-rulebook-fields }

<figure markdown="1" class="ekdn-table">

| Field | Holds | Details |
|---|---|---|
| `id` | The credential type identifier, with its version | [See Details][rulebook-id-field] |
| `authority` | The Decentralized Identifier (DID) of the institution whose rules the credential type rests on | [See Details][rulebook-authority-and-legal-basis] |
| `legal_basis` | The regulation or rule the credential type rests on | [See Details][rulebook-authority-and-legal-basis] |
| `formats` | The formats the type is issued in, with the per-format values | [See Details][rulebook-formats-field] |
| `schema` | The address of the JSON Schema for the type's claims, one for every format | [See Details][rulebook-schema-field] |
| `display` | The address of the type's display metadata, as SD-JWT VC Type Metadata | [See Details][rulebook-display-field] |
| `attributes` | Every attribute, with its minimization class | [See Details][rulebook-attributes-field] |
| `min_assurance` | The assurance level demanded of the credential key | [See Details][rulebook-assurance-fields] |
| `issuer_assurance` | The assurance level demanded of the issuer's signing key | [See Details][rulebook-assurance-fields] |

</figure>

## Identifier {#rulebook-id-field}

`id` names the credential type and its version. Who owns the type decides the
root it sits under. A type another body already named, such as the [ISO/IEC 18013-5:2021 mobile
driving license][ref-iso-18013-5], keeps the names that body gave it, so it can be read by
software built to that body's standard.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-cr-001 }**REQ-CR-001** `id` MUST be the credential type identifier as [Identifier](../architecture-framework/data-model-and-protocols/identifier.md) defines it, including its version number.
- [](){ #req-cr-002 }**REQ-CR-002** A Rulebook owned by the Root Authority MUST use the `id.idctf` root.
- [](){ #req-cr-003 }**REQ-CR-003** A Rulebook owned by a private party MUST use the reverse of a domain that party declares it owns.
- [](){ #req-cr-004 }**REQ-CR-004** A private party's `id` MUST NOT begin with `id.idctf.`.
- [](){ #req-cr-005 }**REQ-CR-005** A type another body already named, such as `org.iso.18013.5.1.mDL`, MUST keep that body's name as its `vct` or `docType`.
- [](){ #req-cr-069 }**REQ-CR-069** The `id` of such a type MUST be that name followed by the version number, such as `org.iso.18013.5.1.mDL.1`.

</div>

## Authority and legal basis {#rulebook-authority-and-legal-basis}

`authority` names neither the Credential Rulebook Provider nor an issuer.
Which issuers may issue the type is set by the Root Authority in an
[Authority Statement][authorization], never by the Rulebook. The
`legal_basis` citation is also the source of the credential's administrative
validity period, which mirrors the underlying document, as
[Credential lifecycle](../architecture-framework/data-model-and-protocols/credential-lifecycle.md)
sets out.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-cr-006 }**REQ-CR-006** `authority` MUST name the institution whose law or rule the credential type rests on: for the identity card, the ministry whose regulation defines it.
- [](){ #req-cr-007 }**REQ-CR-007** `legal_basis` MUST cite the regulation or rule the credential type rests on.

</div>

## Formats {#rulebook-formats-field}

`formats` names the representations a credential type is issued in. [SD-JWT-based Verifiable Credential (SD-JWT VC)][ref-i-d-ietf-oauth-sd-jwt-vc] draft -13
and mdoc may be two representations of one credential. An `ldp_vc` credential
stands alone for now.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-cr-008 }**REQ-CR-008** `formats` MUST list at least one of three keys, and only these:
    - **`sd-jwt-vc`**: an [SD-JWT VC][ref-i-d-ietf-oauth-sd-jwt-vc], with its `vct`.
    - **`mdoc`**: an [ISO mdoc][ref-iso-18013-5], with its `docType`, and its `namespace` where [REQ-CR-061][req-cr-061] demands one.
    - **`ldp_vc`**: a [W3C Verifiable Credentials Data Model (VCDM) 2.0][ref-vc-data-2-0] credential, with its [JSON-LD 1.1][ref-json-ld] `context`, the `context_digest` of that context, its `type`, its `cryptosuite`, and its `credential_schema`.
- [](){ #req-cr-009 }**REQ-CR-009** `vct` and `docType` MUST equal `id`, so the two representations of one credential carry the same name, except for a type [REQ-CR-005][req-cr-005] covers.
- [](){ #req-cr-061 }**REQ-CR-061** An `mdoc` entry for a type [REQ-CR-005][req-cr-005] covers MUST carry `namespace`, the namespace that body defines for the type's data elements.
- [](){ #req-cr-080 }**REQ-CR-080** An `mdoc` entry for any other type MUST NOT carry `namespace`, so that the type's data elements sit in the namespace that equals `id`.
- [](){ #req-cr-055 }**REQ-CR-055** A Rulebook that lists `ldp_vc` MUST NOT list another format.
- [](){ #req-cr-017 }**REQ-CR-017** A Rulebook MUST NOT list `ldp_vc` if any attribute is `restricted`, because [`ecdsa-rdfc-2019`][ref-vc-di-ecdsa] signs the whole document and cannot hide one attribute.
- [](){ #req-cr-018 }**REQ-CR-018** A credential type that has to be verifiable with no network reaching the verifier MUST list `mdoc`, because [SD-JWT VC][ref-i-d-ietf-oauth-sd-jwt-vc] has no offline path.

</div>

### The `ldp_vc` entry {#rulebook-ldp-vc-entry}

`ecdsa-rdfc-2019` signs what the contexts make of the document, so the
context is pinned and read from cache. The VCDM 2.0 context ships with the
verifier's build. The Rulebook is also the vocabulary of its terms, so no
separate vocabulary document exists. Leaving the version out of a term's Internationalized Resource Identifier (IRI)
keeps one IRI per term across versions, and keeping the whole `id` keeps two
private types with the same last segment apart.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-cr-010 }**REQ-CR-010** An `ldp_vc` entry MUST state its `cryptosuite` explicitly, as [`ecdsa-rdfc-2019`][ref-vc-di-ecdsa], so that a later move to another cryptosuite changes one field.
- [](){ #req-cr-062 }**REQ-CR-062** An `ldp_vc` entry MUST carry `type`, the term of its `context` that names the credential type, so that the issuer's metadata can declare the credential's `type` and a verifier can ask for it.
- [](){ #req-cr-011 }**REQ-CR-011** The `context` of an `ldp_vc` entry MUST define the type and every attribute in `attributes`, so that no term is left undefined, which JSON-LD expansion would drop from the data the proof signs.
- [](){ #req-cr-056 }**REQ-CR-056** Every term the `context` defines MUST expand to an IRI of the form `<catalog>/vocab/<type>#<term>`, where `<catalog>` is the address of the Trust Registry catalog and `<type>` is `id` without its version number.
- [](){ #req-cr-057 }**REQ-CR-057** Trust Registry MUST answer each such IRI with the catalog page of the credential type, which shows each term's schema type and its labels from `display`.
- [](){ #req-cr-014 }**REQ-CR-014** `context_digest` MUST be the [Subresource Integrity (SRI)][ref-sri] digest of the context document, in `sha384`, the form [`credentialSchema`][ref-vc-json-schema] already carries in `digestSRI`.
- [](){ #req-cr-012 }**REQ-CR-012** *Withdrawn: moved to [REQ-TS-5-10-119][req-ts-5-10-119].*
- [](){ #req-cr-013 }**REQ-CR-013** *Withdrawn: moved to [REQ-TS-5-10-120][req-ts-5-10-120].*
- [](){ #req-cr-015 }**REQ-CR-015** *Withdrawn: moved to [REQ-TS-5-10-131][req-ts-5-10-131].*
- [](){ #req-cr-016 }**REQ-CR-016** *Withdrawn: moved to [REQ-TS-5-10-132][req-ts-5-10-132].*
- [](){ #req-cr-063 }**REQ-CR-063** *Withdrawn: moved to [REQ-TS-5-10-071][req-ts-5-10-071].*

</div>

The same cache rule holds for `credential_schema`: a verifier that validates
against it reads it from cache, checks it against the credential's
`digestSRI`, and never fetches it while it verifies.

## Schema {#rulebook-schema-field}

`schema` describes the type's claims and nothing else, in no format's
encoding, so one schema serves every format the Rulebook lists. [JSON Schema][ref-json-schema]
2020-12 treats `format` and `contentEncoding` as annotations unless a
validator is told otherwise, so a date in the wrong form or a broken [base64][ref-rfc4648]
value passes a default validation. Whether a
verifier validates a received credential against a schema is its own choice.
A passed schema check proves the claims have the declared shape, never that
the credential is genuine.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-cr-019 }**REQ-CR-019** `schema` MUST point at a [JSON Schema][ref-json-schema] document, draft 2020-12, that declares its `$schema`.
- [](){ #req-cr-020 }**REQ-CR-020** The `properties` of `schema` MUST name exactly the attributes in `attributes`.
- [](){ #req-cr-021 }**REQ-CR-021** `schema` MUST NOT set [`additionalProperties`][ref-json-schema] or `unevaluatedProperties` to `false`, because the `ldp_vc` schema below extends it with the subject's `id`.
- [](){ #req-cr-022 }**REQ-CR-022** *Withdrawn: moved to [REQ-TS-5-10-128][req-ts-5-10-128].*
- [](){ #req-cr-064 }**REQ-CR-064** *Withdrawn: moved to [REQ-TS-5-10-129][req-ts-5-10-129].*
- [](){ #req-cr-065 }**REQ-CR-065** *Withdrawn: moved to [REQ-TS-5-10-130][req-ts-5-10-130].*

</div>

### The schema in each format {#schema-in-each-format}

Each format carries the schema its own way, and Trust Registry derives every
format-specific artifact from the one schema when it publishes the Rulebook.
SD-JWT VC carries no schema, because SD-JWT VC Type Metadata no longer
defines one; its attributes are listed in the Type Metadata instead. mdoc
carries no schema either: every attribute is a data element of the same name,
in the namespace that equals `id`, or in the `namespace` the `mdoc` entry
names, and its [Concise Binary Object
Representation (CBOR)][ref-rfc8949] type follows from the schema as
[the table of mdoc encodings][tbl-mdoc-encodings] sets out. `ldp_vc` names its
schema in `credential_schema`. `sd` binds the SD-JWT VC only; mdoc discloses
each data element on its own, and `ldp_vc` discloses the whole credential.
SD-JWT VC recommends a data URI for binary data such as an image, so a value
the schema marks as base64 travels in SD-JWT VC with its media type in front
of it, while mdoc carries the decoded bytes.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-cr-023 }**REQ-CR-023** For `sd-jwt-vc`, every attribute MUST appear in the [Type Metadata][ref-i-d-ietf-oauth-sd-jwt-vc] `claims`, with `mandatory` set to `true` when the schema lists it in `required` and to `false` otherwise.
- [](){ #req-cr-024 }**REQ-CR-024** For `sd-jwt-vc`, every attribute in the [Type Metadata][ref-i-d-ietf-oauth-sd-jwt-vc] `claims` MUST also carry `sd`.
- [](){ #req-cr-025 }**REQ-CR-025** For `sd-jwt-vc`, every attribute, whatever its minimization class, MUST have `sd` set to `always` in the [Type Metadata][ref-i-d-ietf-oauth-sd-jwt-vc] `claims`, so a holder can disclose it alone and a Relying Party receives only the attributes it asked for, because its approval is granted per attribute and an attribute sent in the clear reaches every verifier.
- [](){ #req-cr-026 }**REQ-CR-026** *Withdrawn: [REQ-CR-025][req-cr-025] covers it.*
- [](){ #req-cr-070 }**REQ-CR-070** For `sd-jwt-vc`, a value whose schema sets [`contentEncoding: base64`][ref-json-schema] MUST be sent as a [data URI][ref-rfc2397], `data:<contentMediaType>;base64,<value>`.
- [](){ #req-cr-027 }**REQ-CR-027** A Rulebook MUST NOT list `mdoc` if an attribute has a type [the table of mdoc encodings][tbl-mdoc-encodings] does not name.
- [](){ #req-cr-077 }**REQ-CR-077** A Rulebook that lists `mdoc` MUST list every attribute in the `required` array of its `schema`, and, for an attribute its source record may hold no value for, MUST name the value Issuer Core writes in that case, because an mdoc carries one digest per data element and [ISO/IEC 18013-5:2021][ref-iso-18013-5] defines no decoy, so a varying set of attributes would tell a verifier which ones a holder has.
- [](){ #req-cr-028 }**REQ-CR-028** For `ldp_vc`, `credential_schema` MUST point at a second [JSON Schema][ref-json-schema], draft 2020-12, over the whole credential document, whose `credentialSubject` holds the subject's `id`, the claims of `schema` by `$ref`, and `unevaluatedProperties: false`.
- [](){ #req-cr-029 }**REQ-CR-029** *Withdrawn: moved to [REQ-TS-5-10-135][req-ts-5-10-135].*

</div>

[](){ #tbl-mdoc-encodings }

<figure markdown="1" class="ekdn-table">

| Schema type | mdoc data element |
|---|---|
| `string` | `tstr` |
| `string` with `format: date` | `full-date`, [CBOR tag 1004][ref-rfc8943] |
| `string` with `format: date-time` | `tdate` |
| `string` with `contentEncoding: base64` | `bstr`, holding the decoded bytes |
| `integer` | `int`, or `uint` when `minimum` is `0` or more |
| `boolean` | `bool` |

</figure>

## Display {#rulebook-display-field}

Trust Registry publishes the display document with the Rulebook, and a wallet
draws the credential from it, whatever format the credential arrived in. An
mdoc carries no display metadata of its own, so one design serves every
representation of the type. A wallet outside IDCTF that receives an `ldp_vc`
credential has no way to find this document, because a VCDM credential
carries no `vct`. [OpenID4VCI 1.0][ref-openid4vci] gives such a wallet a fallback in the
issuer's metadata, `credential_metadata`, so the issuer copies the type's
name, logo, colors and labels there from this document. That wallet then
shows the name, the logo and the labels, but not the [Scalable Vector Graphics (SVG) 2][ref-svg2] template, which
OpenID4VCI has no place for. A logo an issuer supplies about itself is
checked by no one, so the issuer adds nothing of its own, and one issuer's
credential looks like every other issuer's credential of the same type.
SD-JWT VC lets a template place a claim only in text,
never in an attribute, so no claim image can be drawn on the card; the
working group declined to change that, because a card that looks like a
physical identity document invites acceptance on sight. A logo or other fixed
image inside a template is not a claim and is allowed. A document type another
body named is issued by authorities in several countries, so the card design
and the name belong to the issuer whose root the Root Authority publishes, and
a credential of that type admitted through the Verified Issuer Certificate Authority List (VICAL) is drawn plainly, from
what the credential itself carries. A wallet shows the
holder's photo from the claim itself, outside the card. The wallet names the issuer from its entry in the
trusted list, which carries the legal body behind it, and shows that name
beside the card. A rendered card proves nothing.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-cr-030 }**REQ-CR-030** `display` MUST point at an [SD-JWT VC Type Metadata][ref-i-d-ietf-oauth-sd-jwt-vc] document whose `vct` is the Rulebook's `id`.
- [](){ #req-cr-031 }**REQ-CR-031** The [Type Metadata][ref-i-d-ietf-oauth-sd-jwt-vc] document that `display` points at MUST carry:
    - **A name for the type** in `display`, one entry per locale.
    - **A label for every attribute** in `claims[].display`, one entry per locale.
    - **The simple rendering** in `rendering.simple` of each `display` entry: the logo, the background color, and the text color, with alternative text for the logo.
- [](){ #req-cr-032 }**REQ-CR-032** Every name and label MUST be given at least in the `id` and `en` locales.
- [](){ #req-cr-033 }**REQ-CR-033** That [Type Metadata][ref-i-d-ietf-oauth-sd-jwt-vc] document MAY also carry `rendering.svg_templates` in each `display` entry, a full card design with the attribute values filled in by the wallet.
- [](){ #req-cr-034 }**REQ-CR-034** A [Type Metadata][ref-i-d-ietf-oauth-sd-jwt-vc] document that carries `display[].rendering.svg_templates` SHOULD offer a light and a dark variant.
- [](){ #req-cr-078 }**REQ-CR-078** *Withdrawn: moved to [REQ-TS-5-10-134][req-ts-5-10-134].*
- [](){ #req-cr-079 }**REQ-CR-079** *Withdrawn: moved to [REQ-TS-5-10-136][req-ts-5-10-136] and [REQ-TS-5-10-137][req-ts-5-10-137].*
- [](){ #req-cr-071 }**REQ-CR-071** An [SVG][ref-svg2] template MUST NOT carry a placeholder for an image attribute; where the card has room for a photo, the template draws a fixed figure there.
- [](){ #req-cr-035 }**REQ-CR-035** *Withdrawn: moved to [REQ-TS-1-01-009][req-ts-1-01-009].*
- [](){ #req-cr-072 }**REQ-CR-072** *Withdrawn: moved to [REQ-TS-1-01-019][req-ts-1-01-019].*
- [](){ #req-cr-073 }**REQ-CR-073** For `ldp_vc`, every claim `path` in the [Type Metadata][ref-i-d-ietf-oauth-sd-jwt-vc] MUST begin with `credentialSubject`, the way [OpenID4VCI][ref-openid4vci] writes claim paths for a [W3C credential][ref-vc-data-2-0].
- [](){ #req-cr-074 }**REQ-CR-074** For a Rulebook that lists `mdoc` and not `sd-jwt-vc`, every claim `path` in the [Type Metadata][ref-i-d-ietf-oauth-sd-jwt-vc] MUST be the namespace followed by the attribute's name, the claims path pointer [OpenID4VCI][ref-openid4vci] defines for an mdoc.
- [](){ #req-cr-075 }**REQ-CR-075** For a Rulebook that lists both `sd-jwt-vc` and `mdoc`, every claim `path` in the [Type Metadata][ref-i-d-ietf-oauth-sd-jwt-vc] MUST be the attribute's path in the SD-JWT VC, because that draft treats a path that selects nothing in the SD-JWT VC as an error.
- [](){ #req-cr-076 }**REQ-CR-076** *Withdrawn: moved to [REQ-TS-1-01-143][req-ts-1-01-143].*
- [](){ #req-cr-036 }**REQ-CR-036** *Withdrawn: [Reading a credential][ts-5-10-reading-a-credential] covers it.*

</div>

## Attributes {#rulebook-attributes-field}

The minimization class decides which approval tier a Relying Party's request
for an attribute takes, as [Authorization][authorization] sets out: `open` is
granted automatically, `normal` needs one reviewer, and `restricted` needs a
committee. `expiry_date` and `issuance_date` are ordinary attributes with a
minimization class of their own.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-cr-037 }**REQ-CR-037** Each entry in `attributes` MUST carry a `name` and a `minimization` class, `open`, `normal`, or `restricted`.
- [](){ #req-cr-038 }**REQ-CR-038** An attribute computed by the issuer rather than read from its source system MUST carry `derived_from`, naming another attribute in the same Rulebook.
- [](){ #req-cr-039 }**REQ-CR-039** A Rulebook SHOULD offer a derived attribute wherever a Relying Party would otherwise ask for the fact underneath it, such as an over-17 flag in place of a birth date.
- [](){ #req-cr-040 }**REQ-CR-040** A credential type that has an administrative validity period MUST list an `expiry_date` attribute, whose value mirrors the expiry of the underlying document.
- [](){ #req-cr-041 }**REQ-CR-041** A credential type MAY list an `issuance_date` attribute, whose value mirrors the issuance date of the underlying document, whether or not the type has an administrative validity period.

</div>

## Assurance {#rulebook-assurance-fields}

The two levels answer different questions and are set independently, as
[Two assurance levels](../architecture-framework/trust-model/two-assurance-levels.md)
explains. `min_assurance` sets which key storage the
[Key Attestation][key-attestation] demanded at every issuance has to report.
Issuer Core announces it in `key_attestations_required`, through the mapping
the Governance Profile sets. `issuer_assurance` sets the lowest grade an
issuer's signing key may have. The Root Authority authorizes an issuer for
the type only where the issuer's grade meets it.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-cr-042 }**REQ-CR-042** `min_assurance` and `issuer_assurance` MUST each be [`low`, `substantial`, or `high`][ref-eu-2015-1502].

</div>

## What a Rulebook does not carry {#what-a-rulebook-does-not-carry}

How long one signed copy verifies is chosen by the issuer within a ceiling the
Governance Profile sets. A Rulebook carries no revocation field either. Every
credential of every type carries a status list entry, as
[Credential lifecycle](../architecture-framework/data-model-and-protocols/credential-lifecycle.md)
sets out.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-cr-043 }**REQ-CR-043** A Rulebook MUST NOT carry a technical validity period.

</div>
