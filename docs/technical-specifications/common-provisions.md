---
title: "[TS-00] Common provisions"
description: What every Technical Specification shares, the key words, the requirement identifiers, what conformance means and who is tested, and how a specification is versioned.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §0; Glosarium dan Konvensi IDCTF §D.2, §D.3, §D.4, §D.5; tracks/0236, tracks/0237, tracks/0241, tracks/0242, tracks/0269, tracks/0368 -->

<p class="ekdn-docid">TS-00</p>

# Common provisions {#common-provisions}

<p class="ekdn-lead" markdown="span">
The rules every Technical Specification is read by, and that every
implementation claiming conformance to one is tested against.
</p>

Every sentence on this page binds. Its key words are those of
[Requirements notation][requirements-notation] below, and its requirements
carry `REQ-TS-00-nnn`.

## Scope {#ts-00-scope}

This specification applies to every Technical Specification of IDCTF and to
every implementation that claims conformance to one. It sets the
requirements notation, the identifier scheme, the meaning of conformance, and
the versioning rule. It binds no interface of its own.

A Technical Specification holds the requirements on an implementation. It
leaves to other documents:

- The numbers and algorithms the ecosystem may change without changing an
  interface, which the Governance Profile holds.
- [The obligations of a role as an organization][gf-obligations-of-every-participant],
  which the Governance Framework holds.
- The rules of one credential type, which its Credential Rulebook holds.
- The reasons behind a rule, which the
  [Architecture Framework](../architecture-framework/index.md) holds.

Where a specification names one of these, it names the document and takes the
value from it.

Each Technical Specification covers one family of artifacts or one
interface, so that a test can be written for it on its own. An artifact
family is a format together with its signature, its lifecycle, how it is
published, and how a reader checks it. An interface is a protocol between two
Modules, or between a Module and a system outside the ecosystem.

## Requirements notation {#requirements-notation}

The key words MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY in a Technical
Specification are to be interpreted as described in [RFC 2119][ref-rfc2119] and
[RFC 8174][ref-rfc8174] when, and only when, they appear in capitals. The
same word in lower case carries its ordinary meaning: a lower-case "must"
marks a constraint that an outside standard or a law imposes, not a
requirement of IDCTF.

A requirement is one sentence, holds one key word, and names the Module or
party it binds as its subject. A sentence with two obligations is two
requirements.

Every other sentence of a Technical Specification binds as well: a sentence
without a key word states a fact about the ecosystem that an implementation
may rely on, and no section, note, or example of a Technical Specification
is informative.

What a specification shows of its artifact or message is dummy data whose
every field is exact. The names, the organizations, the domains, and the
keys in it are invented, and everything around them is generated against the
profile the page fixes, signed, and verified, so that an implementation can
parse what it shows and find what the clauses require. Where a field admits
several forms, it shows every one of them.

Every requirement carries an identifier of the form `REQ-TS-g-nn-nnn`: the
prefix, the specification's number as it stands in `IDCTF-TS-g-nn`, which
is its group digit and its two-digit sequence within the group, and a
three-digit sequence that runs in page order through that specification.
The groups are 1 Issuer Services, 2 Wallet Services, 3 Verifier Services,
4 Trust Infrastructure, and 5 Artifacts. Three specifications stand outside
them: this one as `TS-00`, with `REQ-TS-00-nnn`;
[Finding a signer's key from its DID](finding-a-signers-key-from-its-did.md)
as `TS-01`, with `REQ-TS-01-nnn`; and
[Publishing and reading the Governance Profile](publishing-and-reading-the-governance-profile.md)
as `TS-02`, with `REQ-TS-02-nnn`.

A number is never reused. A requirement that is withdrawn
keeps its number and its place, marked withdrawn, so that a reference to it
from a test report or a sanction still lands. A requirement added later takes
the next free number, wherever it sits on the page. Another page cites a
requirement by its identifier, as `REQ-TS-00-001`.

## Conformance {#ts-00-conformance}

Each specification names its conformance targets in its Scope. A conformance
target is a Module as the Architecture Framework names it, such as Trust
Registry or Mobile Wallet. Where a specification names a Relying Party's own
application built on Reader SDK, that application is a target too, and a
requirement is addressed to the target it binds.

A target that embeds Trust SDK meets a requirement through the library where the
library performs the check. The requirement still binds the Module, because the
Module is what an Assessment Body tests.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-00-001 }**REQ-TS-00-001** An implementation that claims conformance to a Technical Specification MUST meet every requirement that specification addresses to its conformance target.
- [](){ #req-ts-00-002 }**REQ-TS-00-002** An implementation MUST NOT claim conformance to a Technical Specification for a conformance target that specification does not name.
- [](){ #req-ts-00-003 }**REQ-TS-00-003** A participant MUST meet every Technical Specification that covers an interface it runs or an artifact it produces or reads.

</div>

A participant is compliant with IDCTF when it meets the specifications
that [REQ-TS-00-003][req-ts-00-003] names,
[the obligations of its role in the Governance Framework][gf-obligations-of-every-participant], and the
Credential Rulebook of every credential type it issues or asks for. It is
compliant when an Assessment Body has tested it against those specifications as
well. A merchant is registered and
never accredited, so no Assessment Body tests it; the RP Intermediary that
registered it answers for it, as
[what the RP Intermediary takes on][what-the-intermediary-takes-on] sets out.

Conformity to the Software Architecture of the Architecture Framework is not a
condition of compliance: an implementation built with other technology complies
when it meets [the conditions of compliance][ts-00-conformance]. The
[constraints binding implementations][constraints-binding-implementations] are
what a reviewer judges a vendor's work against, not what an Assessment Body
tests.

### Conformance testing {#ts-00-conformance-testing}

An Assessment Body tests a conformance target against the requirements that
the conformance clauses of each specification address to it, in the version
the Governance Profile names. Two applicants for the same target are measured
against the same list, and nothing outside the list is measured.

A target is tested from outside, through the interfaces it runs, with the
test playing the party on the other side. A Mobile Wallet exposes no
endpoint, so it is tested as the build its Wallet Provider releases, driven
against three counterparts:

- a test issuer under
  [Issuing a credential via OpenID4VCI](issuing-a-credential-via-openid4vci.md);
- a test verifier under
  [Verifying a credential online via OpenID4VP](verifying-a-credential-online-via-openid4vp.md);
- a test reader under
  [Verifying a credential in proximity via ISO/IEC 18013-5](verifying-a-credential-in-proximity-via-iso-iec-18013-5.md).

Wallet Backend Service is handed good evidence and bad, as
[Enrolling a wallet installation and attesting its key](enrolling-a-wallet-installation-and-attesting-its-key.md)
describes. The test checks which evidence it records, which keys it attests,
and which it refuses.

After accreditation, Conformance Crawler compares the metadata an issuer
publishes against its approved scope. A Mobile Wallet publishes
nothing, so nothing crawls it, and the check runs at every issuance instead.
Issuer Core refuses a credential request that carries no Key Attestation,
[REQ-TS-5-08-059][req-ts-5-08-059]. It also refuses one signed by a
Wallet Provider whose trusted list entry does not read `granted`,
[REQ-TS-5-08-049][req-ts-5-08-049]. Wallet Backend Service attests only keys
that the official build generated, [REQ-TS-2-01-025][req-ts-2-01-025] and
[REQ-TS-2-01-041][req-ts-2-01-041].

Suspending the Wallet Provider's trusted list entry therefore stops issuance
to every installation of its wallet at each issuer's next
[trust cache sync][trust-cache-sync], and
[revoking an installation][ts-2-01-revoking-an-installation] stops one.

An accredited target is tested again at each renewal of its accreditation,
against the specifications in the versions the Governance Profile in force at
that time names; the Governance Profile
holds [how long an accreditation period runs][ts-5-07-lifetime]. Between
renewals, a Mobile Wallet build is tested again before its release whenever the
release changes how the build runs an interface or handles an artifact that a
specification binds: its issuance and presentation protocols, its keys and
their attestation, and what it discloses. Who asks for the test, and what
follows from skipping it, are set by
[the Governance Framework's rules on conformance testing][gf-conformance-testing].


## Transport {#ts-00-transport}

Each specification says that an interface is served over HTTP with Transport
Layer Security (TLS) and names no version, because the version is fixed once,
here, for every interface at once: [TLS 1.3][ref-rfc8446]. The profiles IDCTF
is written against admit TLS 1.2 as well, and IDCTF does not, because nothing
in the ecosystem predates this series and no participant has a client to keep
working. What runs between the Modules of one entity is behind that entity's
own door, and the
[rules every Module shares](../architecture-framework/software-architecture/constraints-decisions-and-targets.md)
in the Architecture Framework are where it is stated.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-00-007 }**REQ-TS-00-007** A Module MUST serve every interface a Technical Specification binds over TLS 1.3 or a later version of TLS.
- [](){ #req-ts-00-008 }**REQ-TS-00-008** A Module MUST NOT read an artifact or call an interface a Technical Specification binds over a version of TLS earlier than 1.3.

</div>

## Versions {#ts-00-versions}

Every Technical Specification carries its own version, written after its
identifier as `IDCTF-TS-g-nn-x.y`, so `IDCTF-TS-5-01-1.0` is the first version
of the trusted list specification. A major change, the first number, withdraws
or alters a requirement in a way that an implementation already conformant to
the previous version may fail. It is published with a transition period during
which both versions are in force. That period ends at the `transition_ends` the
specification's entry carries in the `specifications` member of the
Governance Profile, which
[Specifications and standards in force][ts-02-specifications-and-standards-in-force]
defines. A minor change, the second number, adds or clarifies without failing
any implementation conformant to the previous version. A draft of a revision is
published for review before it is adopted.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-00-004 }**REQ-TS-00-004** An implementation MUST state the version of each Technical Specification it claims conformance to.
- [](){ #req-ts-00-005 }**REQ-TS-00-005** During the transition period of a major change, an implementation MAY conform to either version.
- [](){ #req-ts-00-006 }**REQ-TS-00-006** After the transition period of a major change, an implementation MUST conform to the new version.

</div>

## How a specification is laid out {#how-a-specification-is-laid-out}

Every Technical Specification follows the same order, so that a reader
knows where a rule sits before opening the page, and sees the wire before
the rule.

1. A title that names the task and the protocol or artifact, as *Verifying
   a credential online via OpenID4VP* or *Publishing and reading the
   trusted list*, after the identifier.
2. **Who runs this and what it needs**: what the specification binds, its
   conformance targets, what it leaves to another document, what each
   target holds before the first exchange, and the conformance
   requirements.
3. **What it does**: what the artifact or interface is, linking the
   Architecture Framework pages that explain it.
4. The artifact or message as published or exchanged: one instance in
   full, showing every option the specification admits, under a heading
   that names the thing shown.
5. The technical clauses. Each opens with the exchange as numbered steps
   where there is one, gives each parameter in a table with its type and
   presence, and states the requirements beside the table. For an
   interface, one clause per message, with its request and its response.
6. **Security considerations** and **Privacy considerations**: the threats,
   each with the requirement that answers it.
7. A changelog.

## Changelog {#ts-00-changelog}

<figure markdown="1" class="ekdn-table">

| Version | Date | Change |
|---|---|---|
| 1.0 draft | 21 October 2026 | First draft |

</figure>
