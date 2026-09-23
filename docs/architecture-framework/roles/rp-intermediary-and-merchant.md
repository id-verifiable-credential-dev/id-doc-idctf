---
title: "RP Intermediary and merchant"
description: How an accredited relying party registers merchants that are too small to be accredited, what it may ask for, and what it answers for.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §2.6, §5.5 (sertifikat berumur pendek sebagai mekanisme pencabutan); Peta Alur Penerbitan dan Presentasi, §1, §3.2, §5.1 (batas cakupan merchant) -->

# 3. RP Intermediary and merchant

Most of the parties that will eventually want to verify a credential are too
small to be assessed one by one. A corner shop cannot be audited against the
Governance Profile, and neither can a village clinic. Leaving them out would
limit the ecosystem to large institutions; letting them in individually would
mean accrediting millions of businesses.

The answer is a role, not a technology. An accredited Relying Party may take on
the additional role of **RP Intermediary**, called *RP Penyelenggara* in the
draft, and run verifying infrastructure for the merchants it registers as well
as for itself. The intermediary is assessed, the merchant is not, and the
intermediary answers for what its merchants do.

**Both are roles, and both sit in the verifier group.** The verifier group in
[Figure 1.2](role-map.md#figure-1-2) holds three boxes, and each is a primary
role in its own right: Relying Party, RP Intermediary, and Merchant. An RP
Intermediary is not a bigger Relying Party, and a merchant is not a smaller
one. What separates the three is who runs the infrastructure and who answers
for the result, which is why they are described together on this page rather
than one by one in
[Section 1.2, Primary roles](role-map.md#12-primary-roles).

This arrangement exists on the verifying side only. Every Identity Issuer and
every Attribute Issuer runs its own issuing infrastructure, signs with its own
key, and appears in the trusted list; nobody issues through somebody else's.
See [Section 2.2, Accreditation](three-stages-of-authority.md#22-accreditation).

## 3.1 What the intermediary takes on

An RP Intermediary verifies a merchant's identity as a business before
registering it, and grants it authority that is a subset of its own, never
wider. It revokes a merchant that abuses the arrangement, within the deadline
the Governance Framework sets. It keeps an inventory of its active merchants so
the Root Authority can see who is acting under its name at any time. And it
carries the consequences when a merchant breaks the rules.

That last obligation is what makes registration sufficient. The ecosystem does
not need to assess a corner shop, because it has already assessed the party
that vouched for it and will answer for it.

**The cap falls on the merchant, not on the intermediary.** An RP Intermediary
is accredited on exactly the terms an ordinary Relying Party is, and reaches
`restricted` attributes through the same Approval Tier C review if its work
needs them. Serving merchants adds the power to register them and withdraws
nothing, so an institution that was already a Relying Party keeps every
attribute it could ask for before.

What it may hand on is another matter. The Governance Framework bars a
merchant's scope from carrying `restricted` attributes, whatever the
intermediary itself was accredited for, because that class should not reach a
party nobody assessed. The three classes, `open`, `normal` and `restricted`,
are set per attribute in the Credential Rulebook, described in
[Credential Rulebook](../data-model-and-protocols/three-levels-of-rules.md),
and the review each one triggers is in
[Section 2.3, Authorization](three-stages-of-authority.md#23-authorization).

The limit is written into the certificate the merchant is given, so a wallet
enforces it on sight rather than looking anything up. Grading the intermediary
instead would have contradicted the rule that scope, not class of party, is
what bounds a request. See
[Section 2.2, Accreditation](three-stages-of-authority.md#22-accreditation).

So the two roles differ on infrastructure and on nothing else. An intermediary
runs a verifier for parties other than itself, and in what it may ask for it is
a Relying Party.

## 3.2 Three parties, side by side

|  | Relying Party | RP Intermediary | Merchant |
|---|---|---|---|
| Runs Verifier Core | For itself | For itself and its merchants | Runs nothing but the Mobile Verifier |
| Accreditation | Yes | Yes | No; registered by an RP Intermediary |
| Trusted list | Listed | Listed, together with the authority it issues merchant certificates from | Never listed |
| Authority | Its accreditation scope, up to `restricted` | The same, up to `restricted` | A subset of the intermediary's, never `restricted`, written into the certificate it is given |
| How a wallet recognizes it | By its own entry in the trusted list | By its own entry in the trusted list | By the certificate its intermediary issued, traced back to that intermediary |
| Keys | Held by the entity itself | Held by the entity itself, plus the authority that signs merchant certificates | Held on the merchant's own phone, and never leaving it |
| Legal responsibility | Its own | Its own and every merchant's | Sits with the intermediary |
| Citizen data | In its own Verifier Core | On the merchant's device; the intermediary cannot read the response | On its own device |

The privacy consequence is worth stating. A citizen's response is encrypted to
a key held on the merchant's own device, so an RP Intermediary never sees what
its merchants receive, even though it is accountable for them.

The protocol detail behind the last four rows, including how a wallet follows a
merchant's certificate back to the intermediary that issued it, is in
[Two trust anchor paths](../trust-model/two-trust-anchor-paths.md).

## 3.3 Provisioning a merchant

A merchant reaches the point of verifying anything through three stages, and
each answers a different question. Registration asks whether the business is
real. Device activation asks whether the phone in its hands can be trusted to
hold a key. Renewal asks whether both are still true. All three run outside any
citizen's transaction, so nothing described here happens while somebody is
standing at a counter waiting.

Three properties hold across all three stages. A participant is registered
rather than assessed. It is given a certificate that carries its own scope
inside it, so the limit travels with the device instead of being looked up. And
it is removed through a published withdrawal list rather than through a daily
re-approval. Together they are what lets an intermediary carry many merchants
without the ecosystem having to look at any of them.

### 3.3.1 Registration

Registration establishes that there is a real business and a real person
answerable for it. The merchant applies to the intermediary, not to the Root
Authority, and hands over its business identity and its registration as a
company. No device and no key is involved at this stage, and nothing
cryptographic has happened yet.

What the intermediary checks is that the business exists and that a named
person answers for it. What it produces is an entry for that merchant in its
own records, carrying the attribute scope the merchant is being granted.
That scope is set here, once, and it must be a subset of the intermediary's own
accreditation scope with `restricted` attributes left out. An intermediary
cannot grant what it was not granted, and it cannot pass on `restricted`
attributes even when it holds them. This is the stage where both rules are
applied.

If the check fails, no entry is created and the merchant never starts. There is
nothing to revoke, because nothing was issued.

### 3.3.2 Device activation

Activation binds the entry created above to one physical device. The merchant
installs its reader, and the application generates a key that is created on
that device and never leaves it. The device then presents its public
half to the intermediary, together with evidence from the platform about the
state it is in.

What the intermediary checks is threefold and all of it is about the device
rather than the business. That the evidence traces back to the manufacturer, so
the key really is held in hardware. That the application asking is the official
build rather than a modified copy. And that the device has not been tampered
with to remove the protections the rest of this depends on. The evidence comes
from the device platform, which is an external system the ecosystem depends on
and does not govern, described in
[Section 1.3.1, External systems](role-map.md#131-external-systems).

What it produces is the merchant's first certificate. From this point the
merchant can verify credentials, within the scope written into that
certificate and no wider.

If the check fails, no first certificate is issued. The registration survives,
so the merchant may try again with a device that passes, but until then it can
do nothing.

### 3.3.3 Periodic renewal

Renewal is the only stage that repeats, and it repeats for as long as the
merchant operates. A merchant's certificate is deliberately short-lived, so
staying active means passing this stage again and again rather than passing it
once.

What the intermediary checks each time is that the device still holds the same
key it was activated with, that its integrity evidence is current rather than
the one presented months ago, and that the merchant's registration still
stands. The first catches a certificate that has been moved to another device.
The second catches a device that has since been compromised. The third catches
a merchant the intermediary has already decided to remove.

What it produces is a new certificate, valid for another short period, or a
refusal.

A refusal is how a merchant is removed, and there are two ways it plays out.
The quiet one is to stop renewing: the certificate reaches the end of its life
and nothing more needs to be said, because a reader that checks the date will
reject it on its own. The loud one is to withdraw a certificate that has not
yet expired, which is announced on the intermediary's withdrawal list so that a
reader that was offline at the time still learns of it. Why short lifetimes are
made to do the work of revocation is set out in
[Short-lived attestations](../trust-model/short-lived-attestations.md).

### 3.3.4 What the three stages produce

One certificate comes out of all this, and it serves both channels, online and
face to face, so a merchant is provisioned once rather than twice. The scope
set at registration travels inside it, which is what lets a wallet enforce the
limit itself at the moment it reads the certificate, with nobody to consult and
no list to fetch. The sequence a merchant runs at the counter is in
[Section 6.5, Verification by a merchant](../high-level-architecture/flows-per-use-case.md#65-verification-by-a-merchant).

What is left open is the numbers: how long a merchant certificate lives, how
often the withdrawal list is published, and how stale that list may be before
an offline reader stops trusting it. Those belong to the Governance Profile,
which is free to start them short and loosen them once the operation has proved
itself, and they are recorded in
[Open decisions and technical debt](../open-decisions-and-technical-debt.md).

## 3.4 How the verifier group works

One example carries the arrangement better than the rules do. A terminal
provider is accredited as an RP Intermediary and registers three merchants
whose needs have nothing in common.

- A shop selling age-restricted goods needs one answer: whether the person in
  front of it is old enough. It never needs a name.
- A small practice needs to confirm that a visiting practitioner holds a
  current professional licence.
- A delivery depot needs to confirm an address before handing a parcel over.

Four things follow, and together they are the whole arrangement in miniature.

**Each merchant gets its own scope, and none of them gets the intermediary's.**
The shop is granted the age check alone, so a request for a name from that
device is refused by the wallet before the person is ever asked. The depot is
granted the address and not the licence. Each scope is a subset of what the
terminal provider was accredited for, and the provider cannot grant what it
does not hold.

**None of the three appears in the trusted list.** A wallet approached by the
shop does not look the shop up, because there is nothing to look up. It reads
the certificate the terminal provider issued to that device and follows it back
to the provider, which is listed. The provider is the party the ecosystem
knows.

**The provider cannot read any of the three responses.** The answer the shop
receives is encrypted to a key on the shop's own phone. The terminal provider
routes nothing, stores nothing, and sees nothing, which is the point: the party
accountable for a merchant is deliberately not the party able to watch it.

**If one of the three misbehaves, only that one stops.** Suppose the depot
starts asking for more than an address. The terminal provider withdraws that
merchant's certificate, the shop and the practice are untouched, and the
provider answers to the Root Authority for having let it happen. Nothing about
the incident reaches the other two, and no citizen has to be told to distrust a
list.

The terminal provider's own scope may be wider than all three merchant scopes
together, and it may reach `restricted` attributes if it was accredited for
them. None of the three merchants reaches that class, whatever the provider
holds, for the reason given in
[Section 3.1, What the intermediary takes on](#31-what-the-intermediary-takes-on).
