---
title: Three stages of authority
description: What authority means in this ecosystem, and the three stages an entity passes through before it holds any.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §2.2 (syarat registrasi, model peserta), §2.4, §2.5, §4.4 (kelas atribut menentukan jalur persetujuan), §7.1, §7.3; Peta Alur Penerbitan dan Presentasi, §1 -->

# 2. Three stages of authority

Authority here means permission to act: to issue a particular credential, or to
ask for a particular attribute. Nobody holds it by virtue of being large, or
official, or looking legitimate. It is held because a decision was recorded
about that party, and it reaches exactly as far as the decision says.

That authority is never granted in one act. Being known, being judged capable,
and being allowed to do a specific thing are three different findings, and the
ecosystem keeps them apart on purpose. Each is a separate question, asked in
order, and each produces something the next one needs. A party that has
answered only the first can do nothing at all.

Keeping them apart is what makes the arrangement workable over time. An entity
is examined once, at the middle stage, and can then be given or refused
individual permissions for years afterwards without being examined again.
Adding a credential type is a small decision. Judging whether an institution
can be trusted to run the software at all is a large one, and it should not
have to be repeated every time the small decision comes up.

All three stages are decided by the Root Authority, with nothing between it and
the entity, and all three run outside any citizen's transaction. Nothing
described on this page happens while somebody is waiting to be served.

The three stages in brief, before each gets a section of its own.

| Stage | Question | What it means |
|---|---|---|
| **Registration** | Who are you? | The party becomes known and its file is opened, but it may still do nothing. Everyone passes through this stage, merchants included |
| **Accreditation** | Are you fit? | The party is judged capable of taking part, and becomes visible to everyone else as a participant worth trusting. Only parties that run their own infrastructure reach it |
| **Authorization** | What may you do? | The party is granted specific permissions, one at a time. Only accredited parties, and it repeats for as long as they take part |

The three stages line up with the three layers of the participant model in
[Section 1, Role map](role-map.md): registration is about the institution,
accreditation produces the entity, and authorization grants the roles that
entity holds.

## 2.1 Registration

Registration answers who a party is. The applicant approaches the Root
Authority with the documents that establish it as a legal body, and names the
person answerable for it. It also attaches whatever license the body that
already regulates its sector has issued. That license is evidence and never
authority: it is read as part of the file, not treated as a decision the Root
Authority has to honor. This is also why an institution in a sector with no regulator
still has a way in, since nothing in the process depends on a license existing.

What registration produces is a file and an entry that is pending. The party is
known and can be found, and it can do nothing. No keys exist yet, and nothing
about it has been published for anyone else to check. In the participant model
this is the institution layer, the one that changes on a merger or a change of
the person answerable.

**One role never goes further.** A merchant is registered by an RP
Intermediary, not by the Root Authority, and stops here permanently. It is
never judged fit, never published, and never appears in the trusted list. What
stands in for all of that is the intermediary: the intermediary is accredited,
the intermediary is published, and the intermediary carries the legal
consequences of what its merchants do. The arrangement is set out in
[Section 3, RP Intermediary and merchant](rp-intermediary-and-merchant.md).

The practical effect is that nobody ever has to look a merchant up. A wallet
approached by one follows the certificate it was given back to the intermediary
that issued it, and the intermediary is the party the ecosystem knows. Millions
of small businesses can take part without a single one of them being added to a
national list.

On the issuing side there is no equivalent and none is offered. Every issuer is
accredited in its own name, runs its own infrastructure, and signs with its own
key. Nobody issues credentials through somebody else's arrangement.

## 2.2 Accreditation

Accreditation answers whether a party is fit to take part. It is the stage that
costs the most and happens the least: once, before anything else, and not again
unless the accreditation is withdrawn.

The Root Authority decides it, and decides it directly. There is no sectoral
body in between with the power to admit entities in its own field. What the
Root Authority reads is the report of an Assessment Body, which tests the
party's implementation against the Governance Profile and audits its security
without deciding anything itself. That separation is deliberate, and is
described in
[Section 1.1.2, Assessment Body](role-map.md#112-assessment-body).

What accreditation produces is the thing everyone else actually checks. The
party's status becomes granted, it receives a credential of its own attesting
that it was accredited, and it is added to the trusted list that issuers,
wallets and verifiers all carry a copy of. Until this point the party existed
only in a file at the Root Authority. After it, the party exists in a published
record that any participant can verify without asking anyone. In the
participant model this is the entity layer.

Five roles reach this stage: the two issuers, the Wallet Provider, the Relying
Party, and the RP Intermediary. What they have in common is that each runs
infrastructure of its own and is answerable for it.

**The two sides are judged on different questions.** On the issuing side, what
matters is what a party issues. Both issuer roles run their own issuing
infrastructure and hold their own signing key. What tells them apart is what
they are permitted to put their name to: the Identity Issuer to basic identity
and nothing else, through Approval Tier C, and an Attribute Issuer to the
credential types it was specifically granted. Neither is measured by size.

On the verifying side, what matters is who runs the infrastructure. A Relying
Party runs a verifier for itself. An RP Intermediary runs the same thing for
itself and for the merchants it registers, and is accredited on the same terms:
serving merchants adds the power to register them and takes nothing away. A
merchant runs a reader on a phone and is accredited for nothing at all.

The two questions are unrelated, and they are not meant to line up. A party can
be an issuer and a verifier at once, accredited once, listed once, and granted
on both sides separately.

**No participant carries a tier.** What separates one Relying Party from
another is the scope it was granted, not a class it belongs to. The approval
tiers in [Section 2.3, Authorization](#23-authorization) grade a single request
and attach to nobody. A bank may be permitted to ask for a national identity
number and a shop only to ask whether someone is old enough. Both are
accredited participants in good standing, differing in what they may request
and in nothing else. How deeply any particular request is reviewed is settled
in the next stage rather than by the party's standing.

One detail is worth separating from the rest, because the words look alike. The
assurance recorded against an issuer grades that issuer's own signing key. It
is a different scale from the assurance demanded of the key on a citizen's
device, which is set per credential type. The two are compared in
[Two assurance levels](../trust-model/two-assurance-levels.md).

## 2.3 Authorization

Authorization answers what an accredited party may actually do. It is the only
stage that repeats, and it is where nearly all the ongoing work of governance
happens.

The Root Authority records each permission separately in an **Authority
Statement**, naming what the party may do and what it may do it to. The
statement is not handed to the party and not published as a file. It is
answered over TRQP when a participant asks, so any participant can check it at
the moment it matters. A
wallet asked for an attribute does not take the request on trust because the
asker is accredited; it checks that this particular request falls inside what
that party was granted. In the participant model this
is the role layer, the one that changes most often. How a participant queries
those records is covered in
[Section 3.1, Protocols per interaction](../data-model-and-protocols/protocols-and-modes.md#31-protocols-per-interaction).

Because accreditation is already done, adding a permission is cheap. A party
that has been taking part for years can be granted a new credential type or a
new attribute without being reassessed, and can have one withdrawn the same
way, leaving the rest of its standing untouched.

**How deeply a request is reviewed depends on what is being asked for, not on
who is asking.** Every attribute carries a sensitivity class set in its
Credential Rulebook, described in
[Section 1.6, The Credential Rulebook](../data-model-and-protocols/credential-formats.md#16-the-credential-rulebook).
The three classes are `open`, `normal` and `restricted`, and the class decides
which of three approval tiers the request takes.

!!! note "Tiers grade requests, not parties"

    The three depths of review an authorization request can receive are called
    **Approval Tier A**, **B** and **C**. A tier grades one request and not the
    party that made it. Nobody is a tier A or a tier C participant, and what a
    participant may ask for is set by its accreditation scope alone.

**Approval Tier A is automatic.** An already accredited verifier asking only
for `open` attributes receives them immediately, with nobody reviewing
anything, because the data involved is not sensitive enough to justify the
delay.

**Approval Tier B is a single reviewer, working within days.** It covers
`normal` attributes, and it also covers a party that is already accredited
asking to change the scope it holds. There is a person in the loop, but only
one, because the question is narrow.

**Approval Tier C is a committee, working over weeks,** and it requires an
Assessment Body's report alongside the application. It covers `restricted`
attributes, and it also covers two situations that have nothing to do with
sensitivity: a party applying for the first time, and a credential type nobody
has issued before. Both are cases where there is no track record to lean on, so
the ecosystem looks harder.

A party can therefore hold permissions granted through different tiers at
different times, which is the point. The effort matches the risk of each
request rather than being fixed once at the party's accreditation.
