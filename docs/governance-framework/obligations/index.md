---
title: Obligations of every participant
description: What every registered participant owes the Root Authority, its peers and the people it serves, whatever its role, from keeping a registration true to retention and accessibility.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §2.2, §2.4, §10; tracks/0008, tracks/0135, tracks/0159, tracks/0161, tracks/0288, tracks/0305, tracks/0367, tracks/0384, tracks/0387, tracks/0389; debt/0067, debt/0088, debt/0098, debt/0194 -->

# Obligations of every participant {#gf-obligations-of-every-participant}

<p class="ekdn-lead" markdown="span">
Some duties do not depend on the role. Every participant keeps its
registration true, holds its keys where it said it would, claims no more
standing than it was granted, lets the Assessment Body in, protects personal
data, keeps records for a set time, and builds software people with
disabilities can use.
</p>

!!! info "Normative page"

    The rules on this page bind. A participant holding the role a rule names
    is compliant only when it meets it, and an Assessment Body tests it
    against them. The capitalized key words carry the meaning given in
    [RFC 2119][ref-rfc2119] and [RFC 8174][ref-rfc8174]. Each requirement
    carries an identifier, `REQ-GF-nnn`, numbered across the document. A
    number is never reused, and a withdrawn requirement keeps its number,
    marked withdrawn.

## Keeping the registration true {#gf-keeping-the-registration-true}

The trusted list publishes the legal name and legal identifier of every entity
it lists, and the Root Authority approved the registration on the strength of
those items and of the person answerable. A registration that no longer
describes the entity misleads every party that reads the list. The rule is
therefore that an entity tells the Root Authority when an item changes, and
that it does so before the change takes effect when it can. A person answerable
who leaves, or a merger announced after the fact, cannot be foreseen, so the
Governance Profile sets a notice period for that case in
[Intervals][ts-02-intervals]. How the registration is first made is in
[registration][registration] and in
[registering an entity][ts-4-03-registration].

A compromised or lost key follows its own schedule, which
[entity key revocation][entity-key-revocation] fixes. This page sets no second
one.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-091 }**REQ-GF-091** Every participant MUST tell the Root Authority of a change to its legal name, its legal identifier, its control or its person answerable before the change takes effect, or, where it could not know in advance, within the period the Governance Profile sets as `intervals.registration_change_notice`.
- [](){ #req-gf-092 }**REQ-GF-092** Every participant MUST report a compromised or lost key as [reporting an incident][gf-reporting-an-incident] requires.
- [](){ #req-gf-093 }**REQ-GF-093** Every participant MUST file its post-mortem of a key incident through the same portal.

</div>

## Keys and evidence {#gf-keys-and-evidence}

At registration an entity gives evidence of the storage each key lives in, and
the trusted list and the certificates it receives rest on that evidence. A key
moved to weaker storage without a word makes the evidence false while every
signature still verifies. A move is a key change, and
[registering keys][ts-4-03-registering-keys] is the door for it.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-094 }**REQ-GF-094** Every participant MUST hold each key in the storage its registered evidence reports.
- [](){ #req-gf-095 }**REQ-GF-095** Every participant MUST register a move of a key to other storage as a key change before it signs with the key there.

</div>

## Publishing no more than was granted {#gf-publishing-no-more-than-was-granted}

An issuer's metadata, an offer, a statement and a Relying Party's request each
say what the publisher may do. They are controlled by the publisher, so
nothing but a rule stops one from naming a role, permission, credential type
or use it was never granted. The Conformance Crawler reads issuer metadata
against the grant, and [what a finding starts][gf-what-a-finding-starts] says what
follows from a difference.

The same reasoning covers what a participant says about itself. The citizen's
assurance at a counter is the wallet's check of the device certificate, and a
mark with no technical check behind it would be a second, weaker signal that is
easy to copy. IDCTF therefore defines no trust mark for the pilot and instead
forbids a false claim of standing. A merchant is never on the trusted list. It
is known through its RP Intermediary, so its Verifier Device Certificate is
what it may point to, and the RP Intermediary answers for what its merchants
display.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-096 }**REQ-GF-096** A participant MUST NOT publish metadata, an offer, a statement or any other material that names a role, permission, credential type or use it has not been granted.
- [](){ #req-gf-097 }**REQ-GF-097** A participant MUST NOT publish material that is wider than the grant it names.
- [](){ #req-gf-098 }**REQ-GF-098** The Root Authority MUST treat a Conformance Crawler finding of this kind as [what a finding starts][gf-what-a-finding-starts] provides.
- [](){ #req-gf-099 }**REQ-GF-099** The Root Authority MUST NOT designate a trust mark until this Framework is amended to define one.
- [](){ #req-gf-100 }**REQ-GF-100** A participant MUST NOT display a mark, a name or wording that claims an IDCTF accreditation, registration or permission beyond what its trusted list entry carries.
- [](){ #req-gf-101 }**REQ-GF-101** A merchant MUST NOT display a mark, a name or wording that claims an IDCTF registration or permission beyond what its Verifier Device Certificate carries.
- [](){ #req-gf-102 }**REQ-GF-102** An RP Intermediary MUST bind each merchant it registers to [REQ-GF-101][req-gf-101].
- [](){ #req-gf-103 }**REQ-GF-103** An RP Intermediary MUST withdraw a merchant that breaches [REQ-GF-101][req-gf-101], as [withdrawing a merchant][gf-withdrawing-a-merchant] provides.
- [](){ #req-gf-104 }**REQ-GF-104** The Root Authority MUST treat a breach of [REQ-GF-100][req-gf-100] by a participant as a ground for a warning under [grounds for a warning][gf-grounds-for-a-warning].

</div>

## Cooperating with assessment {#gf-cooperating-with-assessment}

An Assessment Body tests and audits and reports, and it can do none of that
without access. Which builds and deployments need testing, and when, is fixed
by [conformance testing][ts-00-conformance-testing] and by
[conformance testing][gf-conformance-testing] in this Framework. The duty
here is the participant's side: open the door and send the build before
release, not after.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-105 }**REQ-GF-105** Every participant MUST give the Assessment Body the access, documents and test systems its assessment needs.
- [](){ #req-gf-106 }**REQ-GF-106** Every participant MUST submit each build or deployment that conformance testing covers to the Assessment Body before it releases it.

</div>

## Personal data {#gf-personal-data}

IDCTF adds no data protection regime of its own. A participant that processes
personal data in IDCTF owes what
[UU No. 27 Tahun 2022 tentang Pelindungan Data Pribadi][ref-uu-27-2022]
requires, including its Pasal 46 notice of a failure of protection. The one
addition is that the Root Authority receives a copy, so it can read a breach
against the registrations it holds. No new deadline is set, and this Framework
does not decide who is the Personal Data Controller in any given exchange.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-107 }**REQ-GF-107** Every participant that processes personal data in IDCTF MUST meet its duties under UU No. 27 Tahun 2022.
- [](){ #req-gf-108 }**REQ-GF-108** Every participant MUST send the Root Authority a copy of each notice of a failure of personal data protection it gives under Pasal 46 of UU No. 27 Tahun 2022.

</div>

## Retention {#gf-retention}

Retention is set here and not left to each institution, because a leaked key
cannot be handled without the records of what it signed, and a dispute years
later needs them too. The Governance Profile sets one dispute period as
`lifetimes.dispute_period` in [Lifetimes][ts-02-lifetimes], and each record
below is kept for it past the point the record stops mattering for the live
system. A participant keeps a record for the period and then deletes it, unless
a law that binds it requires the record to be kept longer.

An issuer keeps each `issuance_record` for the dispute period after the end of
the technical validity period of the credential it records, so a credential
that is renewed keeps its newest record alive. The same period applies to every
copy of a status list after the last credential it covers has expired, which
answers whether a credential was revoked at a given time. A Wallet Provider
keeps the installation record described in
[the installation record][ts-2-01-the-installation-record] while the
installation is `active`, and for the dispute period after `revoked_at`,
because a dispute over whether a key was hardware-backed needs it. A Relying
Party keeps and deletes its verification record and consent receipt as
[Relying Parties][gf-relying-parties] binds it. The relay record and the merchant
inventory carry their own periods in
[the relay record and transport logs][gf-relay-record] and
[the merchant inventory][gf-merchant-inventory].

A session value, a nonce, a code or a token is short-lived, and the
Governance Profile sets each lifetime. Archiving one would turn a short-lived secret into
a long-lived record. The Transparency Log and the history of the trusted list
are never edited or shortened, as [REQ-TS-4-03-121][req-ts-4-03-121] states
for the log. The Root Authority keeps both for as long as IDCTF operates and
provides, in its plan for ending IDCTF, for who keeps them afterward.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-109 }**REQ-GF-109** An issuer MUST keep each `issuance_record` until the period the Governance Profile sets as `lifetimes.dispute_period` has passed after the end of the technical validity period of the credential it records.
- [](){ #req-gf-110 }**REQ-GF-110** An issuer MUST keep every copy of a status list it published until the period the Governance Profile sets as `lifetimes.dispute_period` has passed after the last credential that list covers reached the end of its technical validity period.
- [](){ #req-gf-111 }**REQ-GF-111** A Relying Party MUST keep and delete its verification record and consent receipt as [Relying Parties][gf-relying-parties] requires.
- [](){ #req-gf-112 }**REQ-GF-112** A Wallet Provider MUST keep an installation record while the installation is `active` and until the period the Governance Profile sets as `lifetimes.dispute_period` has passed after its `revoked_at`.
- [](){ #req-gf-113 }**REQ-GF-113** A participant MUST delete a record it keeps under [REQ-GF-109][req-gf-109], [REQ-GF-110][req-gf-110] or [REQ-GF-112][req-gf-112] when its period ends, unless a law that binds the participant requires it to be kept longer.
- [](){ #req-gf-114 }**REQ-GF-114** Every participant MUST delete a session value, nonce, code or token once the lifetime the Governance Profile sets for it has passed.
- [](){ #req-gf-115 }**REQ-GF-115** A participant MUST NOT archive a session value, nonce, code or token.
- [](){ #req-gf-116 }**REQ-GF-116** The Root Authority MUST keep the Transparency Log and the history of the trusted list for as long as IDCTF operates.
- [](){ #req-gf-117 }**REQ-GF-117** The Root Authority MUST name in its plan for ending IDCTF who keeps the Transparency Log and the history of the trusted list afterward.

</div>

## Accessibility {#gf-accessibility}

Every surface a person touches has to be usable by people with disabilities.
[UU No. 8 Tahun 2016 tentang Penyandang Disabilitas][ref-uu-8-2016] and
[PP No. 42 Tahun 2020][ref-pp-42-2020] oblige a public service that uses
technology to make it accessible, and neither names a technical standard.
IDCTF binds
[Web Content Accessibility Guidelines (WCAG) 2.2][ref-wcag-2-2] at Level AA,
the level the web surfaces can be audited against, and the
[architecture's statement of the principle][accessibility] rests on this
section.

The surfaces are Mobile Wallet, Mobile Verifier, Issuer Console, Verifier
Console, the page where an issuer signs a citizen in at its authorization
endpoint, and the Trust Authority portal. Mobile Wallet and Mobile Verifier are
native software, so their success criteria are read as the
[Guidance on Applying WCAG 2 to Non-Web Information and Communications Technologies (WCAG2ICT)][ref-wcag2ict],
the Group Note of 11 December 2025, reads them, and the platform's own assistive
technologies have to work on every screen of the consent and verification
paths. Platform guidelines are not the standard, because they carry no version
or level an Assessment Body could audit against. They are what the assistive
technology clause tests.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-118 }**REQ-GF-118** Each participant MUST make every surface it runs that a person uses meet the Level AA success criteria of WCAG 2.2.
- [](){ #req-gf-119 }**REQ-GF-119** A participant MUST apply those success criteria to native software as WCAG2ICT interprets them.
- [](){ #req-gf-120 }**REQ-GF-120** A participant MUST support the assistive technologies of the platform, including screen reader, text scaling and switch access, on every screen of the consent and verification paths of Mobile Wallet and Mobile Verifier.
- [](){ #req-gf-121 }**REQ-GF-121** The Root Authority MUST make the Trust Authority portal meet [REQ-GF-118][req-gf-118].

</div>

### Assessing accessibility {#gf-assessing-accessibility}

An audit against the success criteria is the evidence, and it travels with the
Assessment Body's report so that one review covers both. The Root Authority is
audited too: the portal is a surface like the others, and the Root Authority
publishes the result rather than keeping it to itself. A failed Level AA
criterion is a finding under [assessment and supervision][gf-assessment-and-supervision],
and the approval tier decides whether it blocks.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-122 }**REQ-GF-122** An applicant for accreditation MUST submit, with the Assessment Body's report, an audit of each surface it runs against Level AA of WCAG 2.2.
- [](){ #req-gf-123 }**REQ-GF-123** An accredited entity MUST repeat that audit at each renewal.
- [](){ #req-gf-124 }**REQ-GF-124** A Wallet Provider MUST repeat that audit for Mobile Wallet on each release that [wallet releases][gf-wallet-releases] requires to be tested.
- [](){ #req-gf-125 }**REQ-GF-125** The Root Authority MUST commission the audit of the Trust Authority portal from an Assessment Body before the portal opens and at each change of its interface.
- [](){ #req-gf-126 }**REQ-GF-126** The Root Authority MUST publish the result of that audit.

</div>

## Chapter contents {#gf-obligations-chapter-contents}

1. [Issuers](issuers.md)
2. [Wallet Providers](wallet-providers.md)
3. [Relying Parties and merchants](relying-parties-and-merchants.md)
