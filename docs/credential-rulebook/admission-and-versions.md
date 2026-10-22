---
title: Admission and versions
description: How a Credential Rulebook is proposed, reviewed, approved, and published, how a private Rulebook is admitted, and why a published version never changes.
---

<!-- Sumber: Rincian Module dan Operasi, §2.4; Arsitektur Ekosistem Identitas Digital v0.2, §2.2, §4.4; tracks/0135, tracks/0176, tracks/0187, tracks/0211, tracks/0221, tracks/0222, tracks/0223, tracks/0225, tracks/0302, tracks/0322, tracks/0323, tracks/0324 -->

# Admission and versions {#admission-and-versions}

<p class="ekdn-lead" markdown="span">
A Rulebook enters the catalog through one path, whoever owns the credential
type. The Credential Rulebook Provider proposes, the Root Authority decides,
and Trust Registry publishes a version that never changes afterward.
</p>

!!! info "Normative page"

    The rules on this page bind. A participant that issues or asks for a
    credential type is compliant only when it meets them, and an Assessment Body
    tests it against them. The capitalized key words carry the meaning given in
    [RFC 2119][ref-rfc2119] and [RFC 8174][ref-rfc8174]. Each requirement
    carries an identifier, `REQ-CR-nnn`, numbered across the catalog. A number
    is never reused, and a withdrawn requirement keeps its number, marked
    withdrawn.

The rules of this catalog, on this page and in
[Rulebook structure](rulebook-structure.md), are amended by the Root Authority
as [the Governance Framework is amended][gf-amending-the-governance-framework].

## Who proposes {#who-proposes-a-rulebook}

The owner of a credential type is its Credential Rulebook Provider: the
Root Authority for a type it proposes itself, the institution that proposes a
type in the `id.idctf` root, and a private party for a type it names under its
own domain. An entity's own `.well-known` metadata is controlled by the entity,
so taking a Rulebook from that metadata would let an issuer widen its own
scope by editing a file. The
direction runs the other way: an issuer's metadata is generated from the
published Rulebook.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-cr-044 }**REQ-CR-044** Every Rulebook, each later version included, MUST be proposed by the Credential Rulebook Provider of its credential type.
- [](){ #req-cr-045 }**REQ-CR-045** *Withdrawn: moved to [REQ-TS-4-02-087][req-ts-4-02-087].*

</div>

## The admission cycle {#the-admission-cycle}

Every Rulebook, public or private, passes through the same five steps.

1. **Proposal.** The Credential Rulebook Provider submits a draft Rulebook to
   the Credential Rulebook repository in Trust Registry.
2. **Review.** The Root Authority reviews the attribute list, the legal basis,
   the minimization class of each attribute, and `min_assurance`.
3. **Approval.** The Root Authority approves the Rulebook, and Trust Authority
   records the decision. For a type in the `id.idctf` root, the Root Authority
   assigns the identifier. For a private type, it confirms the identifier the
   Credential Rulebook Provider chose.
4. **Publication.** Trust Registry publishes the [JSON Schema 2020-12][ref-json-schema], the display
   metadata, the per-format identifiers, and the [JSON-LD 1.1][ref-json-ld] context of an `ldp_vc`
   type as one Rulebook version, and that version is frozen.
5. **Authorization.** Any institution that wants to issue the type applies
   separately. The Root Authority grants that permission in an
   [Authority Statement][authorization], and an approved Rulebook grants no
   one the right to issue.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-cr-046 }**REQ-CR-046** An authorization request to issue a credential type nobody has issued before MUST be reviewed at [Approval Tier C][authorization].

</div>

## Refused at submission {#refused-at-submission}

Some proposals fail on conditions read from the file itself, which
[REQ-TS-4-02-088][req-ts-4-02-088] lists, so they need no review. Everything
else is for the Root Authority to judge.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-cr-047 }**REQ-CR-047** *Withdrawn: moved to [REQ-TS-4-02-088][req-ts-4-02-088].*

</div>

## Private Rulebooks {#private-rulebooks}

A type that is not in the catalog has no Rulebook anyone can read.
Registration follows [the admission cycle][the-admission-cycle], at the same
review depth as any new type. The party declares that it owns the domain its identifier reads
as, and the declaration is not verified. The ecosystem depends on the name
being unique, and [REQ-TS-4-02-088][req-ts-4-02-088] keeps it unique: a name
already taken is refused at submission, whoever holds the domain.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-cr-048 }**REQ-CR-048** A private party MUST register every credential type it names under its own domain.

</div>

## Versions {#rulebook-versions}

A version, once published, is the fixed set of rules its credentials point
at. A credential already issued keeps pointing at the version it was issued
under, and two parties holding the same version hold the same rules.

Publishing a new version does not end the older one. When the
Credential Rulebook Provider asks for issuance under the older version to end,
the Root Authority decides it, and Trust Authority withdraws the permission to
issue that version from every issuer holding one, each recorded in an
[Authority Statement][authorization]. A permission names the version, so the
permission over the newer version is untouched.

The 90 days an issuer and a wallet get to move are a constant of this document
and not a member of the Governance Profile, because the Root Authority decides
the withdrawal and would otherwise be setting the notice of its own decision.

A published version is never removed from the catalog. Credentials issued
under it keep verifying until they expire or are revoked. A verifier does not
check whether the version still has issuers, so Trust Registry never needs to
know which credentials still point at it.

When a credential was issued means when its issuer signed it, never the
`issuance_date` attribute, which mirrors the underlying document and can be
years older. An
[SD-JWT-based Verifiable Credential (SD-JWT VC) draft -13][ref-i-d-ietf-oauth-sd-jwt-vc]
makes `iat` optional and lets an issuer hide it, and
[VC Data Integrity 1.0][ref-vc-data-integrity] makes a proof's `created`
optional. The signing time is therefore shown only where the issuer is bound
to show it. It is not the start of the credential's validity, which an issuer may set
later.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-cr-049 }**REQ-CR-049** A published version MUST NOT be changed.
- [](){ #req-cr-050 }**REQ-CR-050** Any change, to the schema, an attribute, a minimization class, a format, or an assurance level, MUST be published as a new version, such as `id.idctf.ktp.2` after `id.idctf.ktp.1`.
- [](){ #req-cr-058 }**REQ-CR-058** A term in an `ldp_vc` [context][ref-json-ld] MUST keep its meaning in every version of the credential type, because a term's Internationalized Resource Identifier (IRI) carries no version number.
- [](){ #req-cr-051 }**REQ-CR-051** The withdrawal of the permission to issue a version MUST take effect at least 90 days after the Root Authority's decision to end issuance under it, so issuers and wallets have time to move.
- [](){ #req-cr-052 }**REQ-CR-052** Once its permission to issue a version is withdrawn, an issuer MUST NOT issue a credential under that version.
- [](){ #req-cr-053 }**REQ-CR-053** *Withdrawn.*
- [](){ #req-cr-054 }**REQ-CR-054** *Withdrawn: moved to [REQ-TS-5-10-133][req-ts-5-10-133].*
- [](){ #req-cr-066 }**REQ-CR-066** *Withdrawn: moved to [REQ-TS-5-10-017][req-ts-5-10-017], [REQ-TS-5-10-095][req-ts-5-10-095] and [REQ-TS-5-10-078][req-ts-5-10-078].*
- [](){ #req-cr-067 }**REQ-CR-067** *Withdrawn: moved to [REQ-TS-5-10-017][req-ts-5-10-017].*
- [](){ #req-cr-068 }**REQ-CR-068** *Withdrawn.*

</div>
