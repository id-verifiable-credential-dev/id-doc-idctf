---
title: Assessment and supervision
description: Which bodies may assess an entity and how one is recognized, who asks for a conformance test and what follows from skipping it, and what the Root Authority watches after an entity is accredited.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §2.2, §2.4; Rincian Module dan Operasi, §2.4; tracks/0135, tracks/0136, tracks/0152, tracks/0159, tracks/0175, tracks/0178, tracks/0288, tracks/0302, tracks/0305, tracks/0367, tracks/0389, tracks/0415; debt/0031, debt/0089, debt/0193 -->

# Assessment and supervision {#gf-assessment-and-supervision}

<p class="ekdn-lead" markdown="span">
An Assessment Body measures an entity against the Technical Specifications and
reports to the Root Authority, which decides. This page says which bodies the
Root Authority recognizes, who asks for a test and pays for it, and what the
Root Authority watches once an entity is accredited.
</p>

!!! info "Normative page"

    The rules on this page bind. A participant holding the role a rule names
    is compliant only when it meets it, and an Assessment Body tests it
    against them. The capitalized key words carry the meaning given in
    [RFC 2119][ref-rfc2119] and [RFC 8174][ref-rfc8174]. Each requirement
    carries an identifier, `REQ-GF-nnn`, numbered across the document. A
    number is never reused, and a withdrawn requirement keeps its number,
    marked withdrawn.

## Assessment Bodies {#gf-assessment-bodies}

[An Assessment Body][assessment-body] tests and audits, hands a report to the
Root Authority and decides nothing. It holds no key and runs nothing inside
IDCTF, so it holds no Accreditation Credential either: the Root Authority
recognizes it, and its standing is its place on the list this section keeps.
The list lives here and not in the Governance Profile, because nothing reads
it by machine and a signed list would need a specification for no reader.

### Recognition criteria {#gf-assessment-body-recognition-criteria}

IDCTF does not judge a laboratory's competence itself. It asks for the
accreditation Indonesia already issues, from the Komite Akreditasi Nasional
(KAN) under [UU No. 20 Tahun 2014 tentang Standardisasi dan Penilaian Kesesuaian][ref-uu-20-2014].
The matching scheme for a body that reports and does not decide is testing,
[ISO/IEC 17025:2017][ref-iso-17025], adopted as Standar Nasional Indonesia
(SNI) ISO/IEC 17025. A certification scheme would give the body the
conformity decision that the Root Authority keeps. For the security audit,
no scheme fits exactly, so the criterion accepts either testing for
information security or a body accredited to [ISO/IEC 17021-1:2015][ref-iso-17021-1]
that certifies information security management systems. Both are accreditations in a
related field, because no accreditation names the IDCTF suite. A body from
outside Indonesia is not recognized in the pilot.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-052 }**REQ-GF-052** The Root Authority MUST recognize as an Assessment Body only a legal body established in Indonesia.
- [](){ #req-gf-053 }**REQ-GF-053** The Root Authority MUST recognize a body for conformance testing only while KAN accredits it to SNI ISO/IEC 17025 for testing software or information security.
- [](){ #req-gf-054 }**REQ-GF-054** The Root Authority MUST recognize a body for security audit only while KAN accredits it to SNI ISO/IEC 17025 for information security testing, or to ISO/IEC 17021-1 for certifying information security management systems.
- [](){ #req-gf-055 }**REQ-GF-055** The Root Authority MUST name the scope of each recognition as conformance testing, security audit, or both.
- [](){ #req-gf-056 }**REQ-GF-056** The Root Authority MUST NOT read a report outside the scope of the body that filed it.
- [](){ #req-gf-057 }**REQ-GF-057** An Assessment Body MUST test against the requirements and versions the Governance Profile in force names, and against nothing else.
- [](){ #req-gf-058 }**REQ-GF-058** An Assessment Body MUST hand every report to the Root Authority, naming the target, the build or deployment tested, the version of each specification, the `sequence_number` of the Governance Profile edition tested against, and each finding.
- [](){ #req-gf-059 }**REQ-GF-059** An Assessment Body MUST NOT state in a report whether a party should be admitted, what scope it should receive, or whether a defect is tolerable.

</div>

### Independence {#gf-assessment-body-independence}

A report is worth reading only when the body that wrote it had no stake in the
result. The rules below close the three usual ways a stake arises: shared
ownership or shared ministry with the entity, having built what is tested, and
holding a registration of its own.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-060 }**REQ-GF-060** An Assessment Body MUST NOT assess a registration of a legal body it belongs to, of a legal body in the same group of companies, or of a body under the same ministry or agency.
- [](){ #req-gf-061 }**REQ-GF-061** An Assessment Body MUST NOT assess an implementation it designed, built, operated or advised on.
- [](){ #req-gf-062 }**REQ-GF-062** An Assessment Body MUST NOT hold a registration in IDCTF in any primary role.
- [](){ #req-gf-063 }**REQ-GF-063** The Root Authority MUST NOT act as an Assessment Body, as [the Root Authority][gf-the-root-authority] requires.

</div>

### Adding and withdrawing a recognition {#gf-adding-and-withdrawing-a-recognition}

Adding a body is a decision of the Root Authority, recorded as a row in the
table below, and does not revise this Framework. A report filed before a
withdrawal stays good, except where the withdrawal was for a false report or a
broken independence rule: then every decision that rested on the report is
open again.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-064 }**REQ-GF-064** A body that asks to be recognized MUST apply to the Root Authority with its KAN certificate and scope, its legal documents and a declaration of independence.
- [](){ #req-gf-065 }**REQ-GF-065** The Root Authority MUST record each recognition, with its scope and date, in [the list of recognized Assessment Bodies][gf-recognized-assessment-bodies].
- [](){ #req-gf-066 }**REQ-GF-066** The Root Authority MUST withdraw a recognition when the body's KAN accreditation for that scope ends or is suspended, when the body breaks an independence rule, or when a report it filed is shown to be false.
- [](){ #req-gf-067 }**REQ-GF-067** The Root Authority MUST review every decision that rested on a report from a body whose recognition it withdrew for a false report or an independence breach.

</div>

### Recognized Assessment Bodies {#gf-recognized-assessment-bodies}

No Assessment Body has been recognized yet.

[](){ #tbl-gf-recognized-assessment-bodies }

<figure markdown="1" class="ekdn-table">

| Assessment Body | Legal identifier | Scope | Accreditation | Recognized since | Status |
|---|---|---|---|---|---|

</figure>

## Conformance testing {#gf-conformance-testing}

[Conformance testing][ts-00-conformance-testing] says what is measured and
against which versions. This section settles who asks for the test, who pays,
and what follows from skipping it. The entity engages a recognized Assessment
Body of its choice and pays for it. Trust Authority schedules nothing and
invites nobody, because every judgement belongs to the Root Authority
([the Root Authority][gf-the-root-authority]).

### At accreditation and renewal {#gf-testing-at-accreditation-and-renewal}

A renewal is a new credential, prepared ahead of the end of the period so that
Trust Authority can issue the replacement before the old one expires. The
report therefore has to be in hand before that lead begins. "Current" means the
versions the Governance Profile names at the moment of the decision, so no age
limit on a report is needed.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-068 }**REQ-GF-068** An entity MUST engage and pay a recognized Assessment Body for every test this Framework requires.
- [](){ #req-gf-069 }**REQ-GF-069** An accredited entity that wants its accreditation renewed MUST file its renewal application with a report of a test against the specification versions the Governance Profile in force names, before the lead the Governance Profile sets as `intervals.accreditation_renewal_lead` begins ([Intervals][ts-02-intervals]).
- [](){ #req-gf-070 }**REQ-GF-070** The Root Authority MUST renew an accreditation only on a report that tested the specification versions the Governance Profile names at the time of the renewal decision.
- [](){ #req-gf-071 }**REQ-GF-071** The Root Authority MAY require a retest of any accredited target at any time, on a finding, an incident or a complaint.
- [](){ #req-gf-072 }**REQ-GF-072** An entity MUST pay for a retest the Root Authority required where the retest finds a defect.

</div>

### Wallet releases {#gf-wallet-releases}

A Mobile Wallet exposes no endpoint, so it is tested as the build its Wallet
Provider releases. A release that changes how the wallet runs an issuance or
presentation protocol, keeps or attests its keys, or discloses what it holds is
a new thing to test. Each such release is declared before it ships and held
back until the report is accepted. The Root Authority does not approve every
release, only the ones that change what a specification binds. A Mobile
Verifier build is observed and not decided here.

The rule for a skipped test needs a way to notice one. The Assessment Body that
tests the renewal reads the store release history against what the Wallet
Provider declared and what was filed.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-073 }**REQ-GF-073** A Wallet Provider MUST have an Assessment Body test its Mobile Wallet build and its Wallet Backend Service against the requirements the Technical Specifications address to them, in the versions the Governance Profile names, before its accreditation and at each renewal.
- [](){ #req-gf-074 }**REQ-GF-074** A Wallet Provider MUST declare every Mobile Wallet release to the Root Authority before it publishes the release, stating the build version and whether the release changes how the wallet runs an interface or handles an artifact a specification binds.
- [](){ #req-gf-075 }**REQ-GF-075** A Wallet Provider MUST NOT publish a release that changes such code until an Assessment Body has tested the build and the Root Authority has accepted the report.
- [](){ #req-gf-076 }**REQ-GF-076** An Assessment Body testing a renewal MUST report each release in the Wallet Provider's published release history that has neither a declaration nor a filed report.
- [](){ #req-gf-077 }**REQ-GF-077** The Root Authority MUST treat a release that changes such code without a test, or a release declared as not changing it when it does, as a ground under [grounds for a warning][gf-grounds-for-a-warning].

</div>

### When an accreditation period lapses {#gf-when-a-period-lapses}

An accreditation that runs out without renewal ends, and that is a lapse, not a
sanction. Suspension is for misconduct ([entity key revocation][entity-key-revocation]), and letting a period
end is not misconduct. The registration stays open, the entity's services go to
`withdrawn` on the trusted list, and its Use Statements fall under
[REQ-TS-5-06-118][req-ts-5-06-118]. The track record that lets
[the lighter approval tiers][authorization] decide quickly has broken, so a
lapsed entity starts again at the top.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-078 }**REQ-GF-078** The Root Authority, through Trust Authority, MUST set the role services of a registration to `withdrawn` when its accreditation period ends without renewal.
- [](){ #req-gf-079 }**REQ-GF-079** The Root Authority MUST NOT treat a lapse as a sanction.
- [](){ #req-gf-080 }**REQ-GF-080** The Root Authority MUST review at Approval Tier C an application for [accreditation][accreditation] from an entity whose accreditation lapsed.

</div>

## Supervision {#gf-supervision}

After accreditation the Root Authority watches what an entity publishes about
itself, through Conformance Crawler, a component of
[Trust Registry][hla-trust-registry]. No party relies on the crawl for security,
because every reader already refuses what the crawl would catch. The crawl
exists so that a discrepancy reaches a person who can act on it.

### What is watched {#gf-what-is-watched}

Two things are read. The first is the `.well-known` metadata of each
accredited issuer, set against the permissions its Authority Statements grant:
metadata that still offers a configuration the issuer no
longer holds is a scope finding. The fetch of that metadata is also the check
that an issuer keeps its Issuer Core endpoint reachable, the obligation of
[reachability][gf-issuer-reachability]. The second is the `did:webvh` log of
every registration, read for an entry without a witness proof from DID Service.
A verifier's metadata is not crawled, because it travels inside each request
and is never published at an address.

Nothing that identifies a holder or a transaction is ever fetched, so
supervision stays off the transaction path.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-081 }**REQ-GF-081** The Root Authority, through Conformance Crawler, MUST compare the `.well-known` credential issuer metadata of every accredited issuer against the permissions its Authority Statements grant.
- [](){ #req-gf-082 }**REQ-GF-082** The Root Authority, through Conformance Crawler, MUST check the `did:webvh` log of every registration for an entry without a witness proof from DID Service.
- [](){ #req-gf-083 }**REQ-GF-083** The Root Authority MUST NOT supervise by fetching anything that identifies a holder or a transaction.

</div>

### How often {#gf-how-often}

A finding that ends in a suspension reaches readers in the next trusted list
edition. One pass per edition horizon means every edition reflects a crawl no
older than itself. No separate crawl interval is added to the Governance
Profile, because nothing depends on its exact value.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-084 }**REQ-GF-084** The Root Authority MUST complete one crawl pass over every registration within each period the Governance Profile sets as `lifetimes.trusted_list_horizon` ([Lifetimes][ts-02-lifetimes]).

</div>

### What a finding starts {#gf-what-a-finding-starts}

A finding opens a procedure and does not decide an outcome. The three cases
differ. A scope finding is a discrepancy the entity can correct, so it leads to
a warning. An unwitnessed log entry means someone other than the entity's
witnessed process wrote to its log, which points at a stolen update key. A
compromised key revokes the key, not the entity ([entity key revocation][entity-key-revocation]), so the entity
stays accredited unless its account of the entry shows misconduct. Two failed
fetches in a row of the same address mean the issuer is not reachable. One
failed fetch is a network fault, and a single miss opens nothing.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-085 }**REQ-GF-085** The Root Authority MUST treat issuer metadata that offers a credential configuration outside the entity's permissions as a ground under [grounds for a warning][gf-grounds-for-a-warning].
- [](){ #req-gf-086 }**REQ-GF-086** The Root Authority MUST handle a log entry without a witness proof as a suspected compromise of the registration's update key, under [the response to a compromised key][gf-response-to-a-compromised-key].
- [](){ #req-gf-087 }**REQ-GF-087** The Root Authority MUST require the entity to account for an entry without a witness proof.
- [](){ #req-gf-088 }**REQ-GF-088** The Root Authority MUST NOT suspend or withdraw an entity for an entry without a witness proof unless the entity's account shows misconduct.
- [](){ #req-gf-089 }**REQ-GF-089** The Root Authority MUST open an incident under [reporting an incident][gf-reporting-an-incident] when two consecutive crawl fetches of the same issuer address fail.
- [](){ #req-gf-090 }**REQ-GF-090** The Root Authority MUST record every finding and its outcome in the Transparency Log, entity events only and nothing about a citizen.

</div>
