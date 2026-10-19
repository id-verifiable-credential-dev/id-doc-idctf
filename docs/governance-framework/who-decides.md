---
title: Who decides
description: Which institution decides what, at which approval tier, how the Governance Profile, a Technical Specification version and this Framework are amended, and the limits the Governance Profile's values must keep.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §0, §2.2; tracks/0018, tracks/0111, tracks/0135, tracks/0159, tracks/0181, tracks/0288, tracks/0305, tracks/0368, tracks/0397, tracks/0410; debt/0048, debt/0081, debt/0083, debt/0176, debt/0194 -->

# Who decides {#gf-who-decides}

<p class="ekdn-lead" markdown="span">
This page names the institution that decides, and what it decides. The Root
Authority decides every registration, accreditation and authorization, and it
alone changes the Governance Profile, a Technical Specification version in
force, and this Framework.
</p>

!!! info "Normative page"

    The rules on this page bind. A participant holding the role a rule names
    is compliant only when it meets it, and an Assessment Body tests it
    against them. The capitalized key words carry the meaning given in
    [RFC 2119][ref-rfc2119] and [RFC 8174][ref-rfc8174]. Each requirement
    carries an identifier, `REQ-GF-nnn`, numbered across the document. A
    number is never reused, and a withdrawn requirement keeps its number,
    marked withdrawn.

## Legal basis {#gf-legal-basis}

This Framework operates inside Indonesian law and adds to it. Every entity
that runs Issuer Core, Verifier Core or Wallet Backend Service operates an
electronic system under [UU No. 11 Tahun 2008 tentang Informasi dan Transaksi Elektronik][ref-uu-11-2008]
and [PP No. 71 Tahun 2019][ref-pp-71-2019]. Each issuer and Relying Party
handles personal data under
[UU No. 27 Tahun 2022 tentang Pelindungan Data Pribadi][ref-uu-27-2022].
The Identity Issuer's role rests on [UU No. 24 Tahun 2013][ref-uu-24-2013]
and [Permendagri No. 72 Tahun 2022][ref-permendagri-72-2022], and the
accessibility duty on [UU No. 8 Tahun 2016][ref-uu-8-2016]. Each page that
applies one of these laws says so where it applies it. None of them
designates the Root Authority.

Where a law sets a stricter obligation or a shorter deadline than a rule in
this Framework, the law prevails.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-001 }**REQ-GF-001** Every participant MUST meet the obligations Indonesian law places on it, and nothing in this Framework relieves it of one.

</div>

## The Root Authority {#gf-the-root-authority}

The Root Authority is the state institution that the regulation establishing
IDCTF designates. That regulation has not been issued and no institution has
been designated, and this Framework does not name a candidate. Until one is
designated, the Framework names the role and binds it, and every rule
addressed to the Root Authority binds whichever institution is designated.
[Who the Root Authority is][root-authority] stays open, as the Architecture
Framework states it.

The Root Authority decides, Trust Authority records and carries out what it
decides, and Trust Registry publishes the result. A decision
is never Trust Authority's own. Trust Authority acts for the Root Authority
and has no discretion over a request.

The Root Authority holds the two roots of trust, the Issuer Root CA and the
Verifier Root CA, in separate offline hardware. It operates them itself,
unless the regulation that designates it names another state institution as
operator. That operator signs only what the Root Authority has decided.

An Assessment Body tests and reports, and the Root Authority decides on the
report. A Root Authority that were also an Assessment Body would decide on its
own findings, so the two roles never meet in one institution.

The Root Authority also publishes a register a person can read. The trusted
list is the one home of the fact that a registration exists, and its readers
are software. A citizen, a journalist or an auditor who wants to know whether
an institution is registered, and in which roles, needs a page. The register
is that page, generated from the trusted list and never maintained beside it,
so the two cannot disagree. It lives on the Root Authority's own official
site, which makes it an act of the institution and changes no Module. A
merchant is not on the trusted list and so not in the register.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-002 }**REQ-GF-002** The Root Authority MUST operate the Issuer Root CA and the Verifier Root CA itself, unless the regulation that designates it names another state institution as their operator.
- [](){ #req-gf-003 }**REQ-GF-003** An operator the designating regulation names MUST act only on the decisions of the Root Authority.
- [](){ #req-gf-004 }**REQ-GF-004** The Root Authority MUST NOT be an Assessment Body.
- [](){ #req-gf-005 }**REQ-GF-005** The Root Authority MUST carry out each of its decisions through Trust Authority.
- [](){ #req-gf-006 }**REQ-GF-006** The Root Authority MUST publish a register that lists every registration on the trusted list with its legal name, operating name, roles and status.
- [](){ #req-gf-007 }**REQ-GF-007** The Root Authority MUST generate the register from the trusted list in force.
- [](){ #req-gf-008 }**REQ-GF-008** The Root Authority MUST NOT edit the register apart from the trusted list.
- [](){ #req-gf-009 }**REQ-GF-009** The Root Authority MUST publish the register on its own official site.

</div>

## Approval tiers {#gf-approval-tiers}

[Three stages of authority](../architecture-framework/roles/three-stages-of-authority.md)
describes [registration][registration], [accreditation][accreditation] and
[authorization][authorization], and the three approval tiers that grade a
request. This section makes the tiers binding. A tier grades a request by the
highest minimization class among the attributes it reaches, and never grades a
party: an accredited party asking for an open attribute is at Approval Tier A
today and at Approval Tier C tomorrow if it asks for a restricted one. A
credential type nobody has issued before is already at Approval Tier C under
[REQ-CR-046][req-cr-046], and this page does not repeat that rule.

The Architecture Framework says a decision takes days at Approval Tier B and
weeks at Approval Tier C. Those are expectations. This Framework sets no
decision deadline, because a deadline is neither a value software reads nor a
value this Framework may hold.

The merchant is outside every tier. An RP Intermediary registers its
merchants, and the Root Authority decides nothing about a merchant directly.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-010 }**REQ-GF-010** The Root Authority MUST decide every registration, accreditation, authorization and [registered use][registered-use] of every institution other than a merchant.
- [](){ #req-gf-011 }**REQ-GF-011** The Root Authority MUST review an authorization request or a request for a registered use at Approval Tier A when the highest minimization class among the attributes it reaches is `open`, at Approval Tier B when it is `normal`, and at Approval Tier C when it is `restricted`.
- [](){ #req-gf-012 }**REQ-GF-012** The Root Authority MUST review a request from an accredited party to change the scope it holds at Approval Tier B or higher.
- [](){ #req-gf-013 }**REQ-GF-013** The Root Authority MUST review the first accreditation of a registration at Approval Tier C, whatever attributes the party asks for.
- [](){ #req-gf-014 }**REQ-GF-014** At Approval Tier A, the Root Authority MUST grant the request without review when the party is accredited and the attributes lie within its accreditation scope.
- [](){ #req-gf-015 }**REQ-GF-015** The Root Authority MUST have one reviewer decide a request at Approval Tier B.
- [](){ #req-gf-016 }**REQ-GF-016** The Root Authority MUST have a committee it constitutes decide a request at Approval Tier C.
- [](){ #req-gf-017 }**REQ-GF-017** The Root Authority MUST NOT decide an Approval Tier C request without the report of a recognized Assessment Body on the implementation that would serve the request, even when the party is already accredited.
- [](){ #req-gf-018 }**REQ-GF-018** The Root Authority MUST NOT assign an approval tier to a party.
- [](){ #req-gf-019 }**REQ-GF-019** The Root Authority MUST review a request that falls under more than one of these rules at the highest tier any of them sets.

</div>

## A grant narrower than the request {#gf-a-grant-narrower-than-the-request}

A grant is often narrower than the request, because a party asks for what it
hopes to use and the Root Authority grants what it can justify. A refusal that
gives no reason leaves the party unable to correct the request or to object,
which is why the reason is recorded.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-020 }**REQ-GF-020** The Root Authority MAY grant less than a party requested.
- [](){ #req-gf-021 }**REQ-GF-021** The Root Authority MUST record the reason for every part of a request it refuses.

</div>

## Amendment {#gf-amendment}

Three things change by decision of the Root Authority: the
[Governance Profile](../technical-specifications/publishing-and-reading-the-governance-profile.md),
the version of a Technical Specification in force, and this Framework. The
Credential Rulebook Catalog changes through its own
[admission cycle](../credential-rulebook/admission-and-versions.md) and is
outside this section. Amendment is not an approval tier. A tier grades one
request by the attributes it reaches, while an edition of the Governance
Profile binds every party and carries no attribute. Applying a committee and an
Assessment Body report to it would ask for a report that has no subject.

### Who may propose {#gf-who-may-propose}

Anyone who carries the rules may ask for them to change. The channel is plain
writing to the Root Authority. The Trust Authority portal gains no function
for it.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-022 }**REQ-GF-022** An accredited entity, a Credential Rulebook Provider and a recognized Assessment Body MAY propose to the Root Authority an amendment to the Governance Profile, a Technical Specification or this Framework.
- [](){ #req-gf-023 }**REQ-GF-023** The Root Authority MUST record every proposal it receives and the decision it reaches on it.

</div>

### Amending the Governance Profile {#gf-amending-the-governance-profile}

Only the Root Authority decides what an edition says, and Trust Registry
publishes the edition ([Publishing and reading the Governance Profile][ts-02-publishing-and-reading-the-governance-profile]
fixes its format). An edition that changes a value is published as a draft
beside the edition in force before it is approved, so the people it binds can
read it. An edition that changes no value, such as one that only renews
`next_update`, announces or withdraws a signer, or adds a `credential_types`
member for a Rulebook the Root Authority already approved, follows from a
decision taken elsewhere and needs no review.

A tightening makes a rule harder to meet: removing an algorithm, shortening a
lifetime or a tolerance, narrowing a closed list, bringing a date forward or
ending a transition. A tightening needs notice, which is the member
`intervals.amendment_notice` in [Intervals][ts-02-intervals]. The period is
read from the edition in force on the day the draft is published. An edition
therefore cannot shorten the notice it is itself subject to, the same reason
TS-02 gives for keeping its own notice constants outside the Profile. A
relaxation, a new option or a postponed date needs no notice beyond its
publication.

A value that has to tighten at once to contain a security incident, such as an
algorithm or an attestation root shown to be broken, cannot wait for review or
notice. The reason is then published as part of the incident's post-mortem.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-024 }**REQ-GF-024** An institution other than the Root Authority MUST NOT decide what an edition of the Governance Profile says.
- [](){ #req-gf-025 }**REQ-GF-025** Before it approves an edition that changes a value, the Root Authority MUST publish the draft edition for review beside the edition in force.
- [](){ #req-gf-026 }**REQ-GF-026** The Root Authority MAY approve an edition that changes no value without a review.
- [](){ #req-gf-027 }**REQ-GF-027** The Root Authority MUST NOT bring an edition that tightens a value into force earlier than the period the Governance Profile sets as `intervals.amendment_notice` in the edition in force when the draft is published.
- [](){ #req-gf-028 }**REQ-GF-028** The Root Authority MAY bring an edition that relaxes a value, adds an option or postpones a date into force on its publication.
- [](){ #req-gf-029 }**REQ-GF-029** The Root Authority MAY approve an edition without review or notice when a value has to tighten at once to contain a security incident.
- [](){ #req-gf-030 }**REQ-GF-030** The Root Authority MUST publish the reason for an edition approved under [REQ-GF-029][req-gf-029] as part of the post-mortem of that incident.

</div>

### Putting a specification version in force {#gf-putting-a-specification-version-in-force}

Drafting a Technical Specification stays with the technical team, and
[Versions][ts-00-versions] already requires a draft of every revision to be
published for review. What this Framework adds is who puts a version in force:
the Root Authority, through the `specifications` member of the Governance
Profile, so that the same edition that names the version carries its notice.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-031 }**REQ-GF-031** The Root Authority MUST put a version of a Technical Specification in force only through an edition of the Governance Profile.
- [](){ #req-gf-032 }**REQ-GF-032** The Root Authority MUST carry a new major version in `specifications` beside the version it replaces, with a `transition_ends` no earlier than the period the Governance Profile sets as `intervals.amendment_notice` after the edition is published.

</div>

### Amending the Governance Framework {#gf-amending-the-governance-framework}

This Framework is amended by the same hand that applies it. A revision is
published as a draft for review, adopted by the Root Authority, and numbered
by the major and minor rule that Technical Specifications follow. A major
version names its own transition period and takes effect no earlier than its
publication, so no participant is bound by a rule it could not yet read.

The list of [recognized Assessment Bodies][gf-recognized-assessment-bodies]
changes by decision of the Root Authority and not by a revision of this
Framework, because a recognition is an act and adding one changes no rule.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-033 }**REQ-GF-033** An institution other than the Root Authority MUST NOT amend this Framework.
- [](){ #req-gf-034 }**REQ-GF-034** The Root Authority MUST give every version of this Framework an identifier of the form `IDCTF-GF-x.y`, where a change that an already conformant participant may fail raises the first number and any other change raises the second.
- [](){ #req-gf-035 }**REQ-GF-035** The Root Authority MUST publish a draft of every revision of this Framework for review before it adopts the revision.
- [](){ #req-gf-036 }**REQ-GF-036** The Root Authority MUST name in each major version of this Framework its transition period.
- [](){ #req-gf-037 }**REQ-GF-037** The Root Authority MUST NOT bring a major version of this Framework into effect before it publishes it.
- [](){ #req-gf-038 }**REQ-GF-038** The Root Authority MAY add a row to the list of recognized Assessment Bodies, or remove one, by decision and without a revision of this Framework.

</div>

### Notice of an amendment {#gf-notice-of-an-amendment}

The published edition is the notice to every Module, and software needs
nothing beyond the sync TS-02 describes. People are another matter. The
person answerable for an entity, the one who answers to the Root Authority for
it, may never read the Governance Profile. The Root Authority therefore tells
that person itself, as its own act and not through Incident Service, which is
for incidents. The entity then tells its own people: a Relying Party tells the
staff who operate a verifier, and an RP Intermediary tells its merchants.

A participant meets a tightened value from the moment its Modules hold the
edition that carries it. The notice is the time the participant has to
prepare, and ends when the edition takes effect.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-039 }**REQ-GF-039** The Root Authority MUST notify the person answerable for each accredited entity of every approved edition that tightens a value, at the time it approves the edition.
- [](){ #req-gf-040 }**REQ-GF-040** The Root Authority MUST send that notice outside Incident Service.
- [](){ #req-gf-041 }**REQ-GF-041** A Relying Party MUST tell its own staff who operate a verifier of any change that alters what they see or do.
- [](){ #req-gf-042 }**REQ-GF-042** An RP Intermediary MUST tell its merchants of any change that alters what they see or do.
- [](){ #req-gf-043 }**REQ-GF-043** Every participant MUST meet a tightened value from the moment its Modules hold the edition that carries it.

</div>

## Constraints on the values of the Governance Profile {#gf-constraints-on-the-governance-profile}

The Architecture Framework states the relation and leaves the number to this
Framework: a device that cannot sync keeps working from its
copy, so a revocation can go unseen for as long as the copy lives. See
[Transaction path and trust path](../architecture-framework/high-level-architecture/transaction-path-and-trust-path.md)
for the paragraph on what the limit bounds. The Governance Profile already
holds the members that make the window: the `lifetimes.trusted_list_horizon`
of [Lifetimes][ts-02-lifetimes], the members of [Tolerances][ts-02-tolerances]
and the publication members of [Intervals][ts-02-intervals]. This Framework
adds no member of its own. It fixes the relation the existing ones keep.

The trusted list horizon is already the staleness accepted from a device with
no network, so every other path is anchored to it. The longest a reader with
no network may accept a revoked key or credential is then the horizon plus the
longest republication interval of a list that carries a revocation. No
tolerance outlasts the horizon, and no list outlives the interval at which it
is republished. The Root Authority accepts that single window for every
credential type before it puts an edition in force. Windows per type would
need tolerances per type, which no reader implements, and the strictest type
is the one the window is judged against.

Past the tolerance a verifier refuses, as the Technical Specifications
already require. Accepting under a stated risk would reopen the grace period that
[the three rules for reading the copy][three-rules-for-reading-the-copy] exclude. A Relying Party whose use carries more risk than the
window allows may stop using a cached copy earlier, which is where the risk
analysis of that use belongs.

A credential's own technical validity is bounded the same way. Key
Attestation expiry, installation revocation and Wallet Provider suspension
reach issuance only, so the technical period is what limits how long a
disowned installation's credentials go on presenting when the citizen never
told the issuer.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-044 }**REQ-GF-044** The Root Authority MUST set the Governance Profile so that no member of [Tolerances][ts-02-tolerances] exceeds `lifetimes.trusted_list_horizon`.
- [](){ #req-gf-045 }**REQ-GF-045** The Root Authority MUST set the Governance Profile so that every list a reader uses to learn of a revocation is republished within an interval a member of the Profile sets, and is valid no longer than that interval.
- [](){ #req-gf-046 }**REQ-GF-046** The Root Authority MUST accept the window that the trusted list horizon and the longest such interval give, for every credential type, before it puts an edition in force.
- [](){ #req-gf-047 }**REQ-GF-047** A Relying Party MUST refuse, at every verifier it runs, a credential once a copy it needs to check the credential is past its tolerance.
- [](){ #req-gf-048 }**REQ-GF-048** A Relying Party MUST NOT accept a credential under a stated risk once a copy it needs is past its tolerance.
- [](){ #req-gf-049 }**REQ-GF-049** A Relying Party MAY stop using a cached copy before its tolerance for a use whose risk calls for it.
- [](){ #req-gf-050 }**REQ-GF-050** The Root Authority MUST set `validity_ceiling` in [Credential types][ts-02-credential-types] for every credential type a Rulebook registers.
- [](){ #req-gf-051 }**REQ-GF-051** The Root Authority MUST NOT set a `validity_ceiling` longer than the administrative validity of a credential type, where its Rulebook names one.

</div>
