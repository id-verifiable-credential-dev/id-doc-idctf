---
title: "RP Intermediary and merchant"
description: How an accredited Relying Party registers merchants that are too small to be accredited, what it may ask for, and what it answers for.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §2.2, §2.5, §2.6, §5.5 (sertifikat berumur pendek sebagai mekanisme pencabutan), §7.4 (Use Statement di jalur luring), Kep. 29, 30, 31; Peta Alur Penerbitan dan Presentasi, §1, §3.2, §4.1, §5.1 (batas cakupan merchant); Rincian Module dan Operasi, §2.4, §7 (registrasi per kategori, relay tanpa retensi); tracks/0078, tracks/0080, tracks/0081 -->

# RP Intermediary and merchant {#rp-intermediary-and-merchant}

Most of the parties that will eventually want to verify a credential are too
small to be assessed one by one. A corner shop cannot be audited against the
Governance Profile, and neither can a village clinic. Leaving them out would
limit the ecosystem to large institutions; letting them in individually would
mean accrediting millions of businesses.

This is an arrangement, not a new role. An accredited
Relying Party may be granted, on the accreditation it already holds, the
standing to serve merchants: it may register them, and it may hold the
authority that issues them certificates. Granted that standing, it is an
**RP Intermediary**, Relying Party Intermediary written in full, and it runs
verifying infrastructure for those merchants as well as for itself. The
RP Intermediary is assessed, the merchant is not, and the RP Intermediary answers for
what its merchants do.

Neither is a role of its own. Relying Party is the only role on the verifying
side, and these two are its subtypes: an RP Intermediary is a Relying Party with
a further grant, and a merchant is a Relying Party that somebody else answers
for.

A merchant fails the role test on [Role map](role-map.md) on every count: the
Root Authority never accredits it, never registers it directly, and never
recognizes it as a participant of its own, because the RP Intermediary
registers it. What still separates the three is who runs the infrastructure
and who answers for the result. They are described together on this page for
that reason, rather than one by one in [Primary roles][primary-roles].

The word intermediary suggests a party that receives an answer and passes it
on. Here it cannot read the answer at all: the response is encrypted
to a key the merchant's own device drew for that request. For a merchant's online checks, it holds that answer only long
enough to pass it back, then deletes it and never logs it; the request side is
what it may record. The
party accountable for a merchant is deliberately not the party able to watch
it.

The relay is the
RP Intermediary's own service, so it necessarily observes that one of its
merchants ran a check and when, and the request it holds is signed rather than
encrypted. That much lets an RP Intermediary notice a merchant asking for
more than its category allows, which is the thing it answers for. The Technical
Specifications fix what it keeps of a relayed request, refused requests
included, and the Governance Profile fixes for how long; the architecture
settles only that the request side is readable to it and the response side is
not.

This arrangement exists on the verifying side only. Every Identity Issuer and
every Attribute Issuer runs its own issuing infrastructure, signs with its own
key, and appears in the trusted list; nobody issues through somebody else's.
See [Accreditation][accreditation].

## What the RP Intermediary takes on {#what-the-intermediary-takes-on}

An RP Intermediary verifies a merchant's identity as a business before
registering it, and grants it authority that is a subset of its own, never
wider. It registers a use for each business category it serves, such as an age
check on restricted goods or confirming an address at delivery, rather than a
use for each merchant, and binds a merchant's device to one or more of those
categories. It revokes a merchant that abuses the arrangement,
[within the deadline the Governance Framework sets][gf-withdrawing-a-merchant].
It keeps an inventory of its active merchants so the Root Authority can see who
is acting under its name at any time. And it carries the consequences when a
merchant breaks the rules.

The ecosystem does not need to assess a corner shop, because it has already
assessed the party that vouched for it and will answer for it.

The cap falls on the merchant, not on the RP Intermediary. An RP Intermediary
is accredited on exactly the terms an ordinary Relying Party is. If its work
needs restricted attributes, it reaches them through the same Approval Tier C
review. Serving merchants adds the power to register them and withdraws
nothing, so an institution that was already a Relying Party keeps every
attribute it could ask for before.

A merchant's scope may never carry the
`restricted` class of attribute, whatever the RP Intermediary itself was
accredited for, because that class should not reach a party nobody has assessed.
The rule has two homes, and each does a different job. The Governance Framework
[carries it as an obligation of the RP Intermediary][gf-merchant-scope]: setting
a merchant's scope without `restricted` is one of the things an RP Intermediary
answers for. The architecture carries it as a bound written into the certificate
the merchant is given, so a wallet enforces it on sight rather than looking
anything up.

The Governance Profile sets something narrower, the numbers around that
certificate, covered in
[what the three steps produce][what-the-three-steps-produce]. The
three classes, `open`, `normal`, and `restricted`, are set per attribute in the
Credential Rulebook, described in
[The Credential Rulebook][the-credential-rulebook], and the review each one
triggers is in [Authorization][authorization].

Grading the RP Intermediary instead of the merchant would have contradicted the
rule that scope bounds a request, rather than the class of the party making it.
See [Accreditation][accreditation].

## Three parties, side by side {#three-parties-side-by-side}

The merchant is the only one of the three trusted through somebody else, and
[a row-by-row comparison][tbl-three-verifier-parties] shows what follows from
that.

[](){ #tbl-three-verifier-parties }

<figure markdown="1" class="ekdn-table">

|  | Relying Party | RP Intermediary | Merchant |
|---|---|---|---|
| Verifying infrastructure | Its own | Its own, for itself and its merchants | None of its own; verifying software on the device it holds |
| [Relying Party Instance][relying-party-instance] | Remote, plus one on a device where it reads face to face | Remote, serving many merchants, plus one on a device where it reads face to face | On a device only; its online check is carried through its RP Intermediary's infrastructure |
| Accreditation | Yes | Yes | No; registered by an RP Intermediary |
| Trusted list | Listed, plus the authority it certifies its own counter devices from, where it reads face to face | Listed, together with the authority it issues merchant certificates from | Never listed |
| Authority | Its accreditation scope, up to `restricted` | The same, up to `restricted` | A subset of the RP Intermediary's, never `restricted`, written into the certificate it is given |
| How a wallet identifies it | By its own entry in the trusted list | By its own entry in the trusted list | By the certificate its RP Intermediary issued, traced back to that RP Intermediary |
| Keys | Held by the party itself, plus the authority it certifies its own counter devices from, where it reads face to face | Held by the party itself, plus the authority that signs merchant certificates | Held on the merchant's own phone, and never leaving it |
| Legal responsibility | Its own | Its own and every merchant's | Sits with the RP Intermediary |
| Citizen data | In its own infrastructure | On the merchant's device; the RP Intermediary cannot read the response | On its own device |

</figure>

The technical detail behind
[the table of the three verifier parties][tbl-three-verifier-parties],
including how a wallet follows a merchant's certificate back to the
RP Intermediary that issued it, is in
[Two trust anchor paths][two-trust-anchor-paths].

## Provisioning a merchant {#provisioning-a-merchant}

A merchant reaches the point of verifying anything through three steps, and
each answers a different question. Registration asks whether the business is
real. Device activation asks whether the phone in its hands can be trusted to
hold a key. Renewal asks whether both are still true. All three run outside any
citizen's transaction, so nothing described here happens while somebody is
standing at a counter waiting.

Three properties hold across all three steps. A merchant is registered
rather than assessed. It is given a certificate that carries its own scope
inside it, so the limit travels with the device instead of being looked up. And
it is removed through a published withdrawal list rather than through a daily
re-approval. Together they let an RP Intermediary carry many merchants
without the ecosystem having to look at any of them.

### Registration {#merchant-registration}

Registration establishes that there is a real business and a real person
answerable for it. The merchant applies to the RP Intermediary, not to the
Root Authority, and hands over its business identity and its registration as a
company. No device and no key is involved at this stage, and nothing has
happened yet beyond opening a file.

The RP Intermediary checks both, and produces an entry for that merchant in its
own records, carrying the attribute scope the merchant is being granted.
That scope is set here, once, and it must be a subset of the RP Intermediary's own
accreditation scope with restricted attributes left out. This is the stage where
both rules are applied.

A third bound applies at the same time. A merchant has no registered use of its
own; it is bound instead to one or more of its RP Intermediary's categories, such
as an age check or an address confirmation, and the scope set here has to fall
inside that category's [Use Statement][use-statement]. The statement is handed
to the device along with its certificate, and the wallet later checks both: the
attributes asked for against the certificate, and the certificate's attributes
against the statement.

If the check fails, no entry is created and the merchant never starts. There is
nothing to revoke, because nothing was issued.

### Device activation {#device-activation}

Activation binds the registration entry to one physical device. The merchant
installs the verifying application, and the application generates a key on
that device that never leaves it. The device then presents its public
half to the RP Intermediary, together with evidence from the platform about the
state it is in.

The RP Intermediary makes three checks, all of them about the device rather
than the business:

- it follows the evidence back to the manufacturer, which shows the key is
  held in hardware;
- it confirms that the application asking is the official build rather than a
  modified copy;
- it confirms that the device has not been tampered with to remove the
  protections the rest of this depends on.

The evidence comes from the device platform, an external system the ecosystem
depends on and does not govern, described in
[External systems][external-systems].

What comes out is the merchant's first certificate. From this point the
merchant can verify credentials, within the scope written into that
certificate and no wider.

If the check fails, no first certificate is issued. The registration survives,
so the merchant may try again with a device that passes, but until then it can
do nothing.

### Periodic renewal {#periodic-renewal}

Renewal is the only stage that repeats. A merchant's certificate runs for the
period the Governance Profile sets, so staying active means passing this stage
again.

The RP Intermediary checks three things each time:

- the device still holds the same key it was activated with, which catches a
  certificate moved to another device;
- its integrity evidence is current rather than the one presented months ago,
  which catches a device compromised since;
- the merchant's registration still stands, which catches a merchant the
  RP Intermediary has already decided to remove.

What comes out is a new certificate, valid for another such period, or a
refusal.

A refusal is how a merchant is removed, and withdrawal is how the removal takes
effect. The RP Intermediary withdraws the certificate and announces it on its
withdrawal list, so that a wallet that was offline at the time still learns of
it, and the Governance Framework asks for that on every ground on which a
merchant is removed. Letting the certificate run out is the backstop rather
than the path, because a wallet that checks the date rejects it on its own
once it expires. Why an attestation's lifetime is made to do the work of
revocation where it can is set out in
[Short-lived attestations][short-lived-attestations].

### What the three steps produce {#what-the-three-steps-produce}

One certificate comes out of all this, and it serves both channels, online and
face to face, so a merchant is provisioned once rather than twice. The scope
set at registration travels inside it, so a wallet enforces the limit itself
at the moment it reads the certificate, with nobody to consult and
no list to fetch. The RP Intermediary's Use Statement travels with it in both
channels alike: the device attaches it to every request, signed along with the
rest of that request. The wallet runs the same check either way. The sequence a merchant runs at the counter is in
[verification by a merchant][verification-by-a-merchant].

The numbers are the Governance Profile's: how long a merchant certificate lives, how
often the withdrawal list is published, and how stale that list may be before
a wallet with no network stops trusting it. The Profile may loosen them once the
operation has proved itself.

## How the intermediated group works {#how-the-intermediated-group-works}

A terminal provider accredited as an RP Intermediary registers three merchants
whose needs have nothing in common.

- A shop selling age-restricted goods needs one answer: whether the person in
  front of it is old enough. It never needs a name.
- A small practice needs to confirm that a visiting practitioner holds a
  current professional license.
- A delivery depot needs to confirm an address before handing a parcel over.

The RP Intermediary registers a use per category it serves, not per merchant. It
holds one registered use for the age check, one for the professional license
check, and one for confirming an address, and none at all naming the shop, the
practice, or the depot.

The shop's device is bound to the age-check category,
the practice's to the license-check category, the depot's to the
address-confirmation category, and the person at the counter picks the category
the transaction falls under; the request that goes out carries only that
category's registered purpose.

Registering by category rather than by merchant keeps the Root Authority from
having to review a registered use for every merchant the RP Intermediary ever
takes on, potentially millions of them.

What the citizen sees at the counter comes from the merchant, not the
RP Intermediary. The wallet shows the shop's own name, taken from the certificate
the RP Intermediary issued it, and the purpose of the category the cashier picked. The
RP Intermediary's name never reaches that screen; it appears only afterward, in the
transaction history.

Each merchant gets its own scope, and none of them gets the RP Intermediary's.
The shop is granted the age check alone, so the wallet refuses a request for a
name from that device before the person is ever asked. The depot is
granted the address and not the license.

None of the three appears in the trusted list. A wallet approached by the
shop does not look the shop up, because there is nothing to look up. It reads
the certificate the RP Intermediary issued to that device and follows it back
to the RP Intermediary, which is listed. The RP Intermediary is the party the ecosystem
knows.

The RP Intermediary cannot read any of the three responses. The answer the shop
receives is encrypted to a key on the shop's own phone. Online, the
RP Intermediary's own infrastructure carries the shop's signed request and that
encrypted answer between the wallet and the shop. Face to face it carries
nothing at all.

If one of the three misbehaves, only that one stops. Suppose the depot
starts asking for more than an address. The RP Intermediary withdraws that
merchant's certificate, the shop and the practice are untouched, and the
RP Intermediary answers to the Root Authority for having let it happen. Nothing about
the incident reaches the other two, and no citizen has to be told to distrust a
list.

The shop's counter makes the point again with no network at all. If it loses
signal, the device still holds the one certificate it was given, still carries
its category's registered use, and checks a presentation entirely from what it
already has; nothing about the transaction has to reach the RP Intermediary or the
Root Authority for the check to run. Provisioning happened once, and the
counter does not depend on being online at the moment somebody is being served.

The RP Intermediary's own scope may be wider than all three merchant scopes
together, and it may reach restricted attributes if it was accredited for
them. None of the three merchants reaches that class, whatever the RP Intermediary
holds, for the reason given in
[what the RP Intermediary takes on][what-the-intermediary-takes-on].
