---
title: "High-Level Architecture"
description: What the ecosystem is made of, how its parts are kept apart, and the principles that separation serves.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §1 (Kep. 3, 5, 8, 9, 12, 16, 20, 21, 23, 25, 26, 27), §2, §3, §8.7; EUDI Architecture and Reference Framework 3.0.0, §4.2, disesuaikan -->

# High-Level Architecture

<p class="ekdn-lead" markdown="span">
This chapter is the shape of the system. The previous one named who is
answerable for what; this one names what actually runs, where each piece sits,
and which pieces are forbidden to speak to one another.
</p>

Three words carry the chapter, and they nest: Service, Module, and component.
[Section 1, System Models](system-models.md) defines them beside the figure that
shows how they sit inside one another, and describes the four Services and the
eleven Modules that fill them.

The separation that shapes everything else runs between two planes. On the
transaction path, a credential is issued to a citizen's wallet and shown to
someone who needs to check it. On the trust path, the Root Authority decides who
is allowed to do either. The two never meet while a transaction is running. A
third group sits on neither: the consoles and the wallet's backend configure and
vouch for the parties on the transaction path without issuing or verifying
anything themselves.

This chapter specifies nothing. It says that a credential is presented, not what
the message carrying it looks like, and that a cache has a tolerance limit, not
how many hours that limit is. Message formats and protocol choices belong to
[Data Model and Protocols](../data-model-and-protocols/index.md), testable rules
to the [Technical Specifications](../../technical-specifications/index.md), and
anything a participant can be assessed against to the
[Governance Framework](../../governance-framework/index.md).

## Design principles

A principle here is a constraint the architecture already obeys, not an ambition
it works toward. Six of the seven trace back to a numbered decision in the draft
or to a rule the build tests, and each one forbids something specific: a call
that may not be made, a central component whose outage may not stop a
verification, an attribute a verifier may not ask for. The seventh states an
obligation the architecture does not yet meet, and says so.

### 1. The two paths never cross

Two planes run through the ecosystem and they do not meet at runtime. On the
transaction path, an issuer hands a credential to a wallet, and the wallet shows
it to a verifier. On the trust path, Trust Authority drives the registry, the
identifier service, and the key management that stand behind all of them. No
message crosses from one to the other while a credential is being issued or
verified.

What makes that possible is that everything the transaction path needs was
published in advance as a file and copied into a local cache before the
transaction began: the list of accredited entities, the rules for the credential
type, each entity's published keys. Even checking whether a credential has been
revoked is a read of a file the issuer itself publishes, rather than a question
put to the center.

This is the principle that makes a single national Trust Infrastructure
acceptable. One instance of anything is a single point of failure only if it
sits on the path. Because it does not, its outage costs nothing until the caches
age out. The rule is not left to discipline: four calls are forbidden outright
and the build fails if any of them appears, which
[Section 3.3, Who may call whom](module-map.md#33-who-may-call-whom) sets out.
How the two planes are drawn is
[Section 2, The transaction path and the trust path](transaction-path-and-trust-path.md).

### 2. The center may be down

If the whole of Trust Infrastructure stops, issuance and verification carry on
from cache until the tolerance limit runs out. Verification in person asks more
than that again: it has to succeed with the phone in airplane mode, because two
devices held next to each other reach no network at all.

Three decisions carry this. Revocation data is published and hosted by each
issuer rather than centrally, so it survives a central outage and grows with the
number of issuers instead of concentrating in one place. The lists and rulebooks
everyone reads are static files behind a content delivery network, which fails
more gracefully than an API does. And every Module that consumes them keeps a
cache with a stated tolerance limit, so what ends a verification is the limit
rather than the network.

The measurable targets live in
[Section 7, Quality goals](../software-architecture/quality-targets.md), and how
long a cache may be trusted is set in the
[Governance Framework](../../governance-framework/index.md), not here.

### 3. Finished specifications only

Only final specifications bind implementations in this ecosystem. A draft does
not, however widely it is implemented elsewhere, and a profile published by
another ecosystem is read as a comparison rather than as a requirement.

The rule has already cost the architecture something, which is what makes it a
rule rather than a preference. A draft mechanism for proving that a wallet
installation is genuine would have fitted neatly, and it is not used. The same
job is done with
mechanisms the final issuance specification already defines. Which specification
is fixed for which job is set out in
[Data Model and Protocols, technology map](../data-model-and-protocols/index.md#technology-map).

Interoperability also has to survive two codebases. The Trust SDK exists twice,
once for the server Modules and once for the two applications, and the two are
held together by a shared set of test vectors rather than by shared code. Where
a standard leaves a choice open, the Governance Profile closes it, so that two
independent implementations reach the same answer.

### 4. Minimal disclosure

A verifier receives the attributes it has registered a need for and no others.
That holds because four separate things enforce it at once, not because any one
of them is strong enough alone.

The credential format decides what is possible at all. Two of the three formats
let a holder reveal one attribute without revealing its neighbors. The third
cannot, and the architecture answers by restricting where that format may be
used rather than by accepting the leak. Both the formats and the restriction are
in
[Section 1.2, Three credential formats](../data-model-and-protocols/credential-formats.md#12-three-credential-formats).

The Credential Rulebook classifies every attribute of every credential type, and
that classification is what the restriction above is measured against. On the
verifier's side a registered merchant is bounded twice over: once by what its
intermediary configured for it, and once by a limit written into the certificate
it presents, so its authority over attributes is provable and not merely
configured.

Correlation is attacked separately from disclosure. A holder's identifier is
created fresh for every credential, so two credentials held by the same citizen
carry nothing in common that would let two verifiers, or an issuer and a
verifier, recognize them as one person.
[Section 2, Identifier](../data-model-and-protocols/identifier.md) says which
identifier is used where.

### 5. Security by design

The architecture assumes that a key which can be moved will eventually be moved,
and removes the ability to move it.

The KMS generates, rotates and revokes entity keys, and it has no sign
operation. Nothing can ask it to sign. An entity that needs a signature produces
it locally, from a keystore it holds itself. On a phone, the keys live in
hardware the operating system keeps apart from ordinary storage, and a
merchant's key never leaves the merchant's own device even though the Verifier
Core behind it belongs to an RP Intermediary.

Placement backs this up. The KMS, the hardware module behind it, and both
offline certificate roots sit in a zone that only Trust Authority can reach.
Public endpoints and administrative ones sit on separate doors of the same
application, so one Module is exposed in two different degrees. A Console
reaches its Core through the administrative door and never touches a database.
The layout is
[Section 3.4, Network zones and placement](module-map.md#34-network-zones-and-placement).

The trust anchors are split for the same reason. There are two roots, one for
the issuing side and one for the reading side, kept apart so that a compromise
on one side does not authorize the other. Below that, every protocol option that
could be left loose is fastened down, and the wallet is treated throughout as
software an attacker may take apart, because it is.

### 6. The citizen decides

Before a credential leaves the wallet, the citizen is shown who is asking, what
is being asked for, and on what authority. The wallet's interface exists for
this: it resolves the requester to a named accredited entity, states the
attributes being requested, and shows what is being held. The citizen
authenticates to the wallet before any of it.

The requester cannot stay anonymous, and how it identifies itself depends on
what it is. An accredited Relying Party publishes an identifier and signs its
request with a key the wallet can look up in the trusted list. A merchant
presents the certificate its intermediary issued to it, which carries the
merchant's authority inside it. Either way the wallet has something to show the
citizen that a third party stands behind, rather than a name the requester chose
for itself. The second case is
[Section 3, RP Intermediary and merchant](../roles/rp-intermediary-and-merchant.md).

What was consented to is recorded afterward as a consent receipt, so the
decision is auditable later by someone other than the party that benefited from
it. The record's format is specified in
[TS-12](../../technical-specifications/index.md), and the retention rules belong
to the [Governance Framework](../../governance-framework/index.md).

### 7. Accessibility

Every surface a person touches has to be usable by people with disabilities: the
Mobile Wallet, the Mobile Verifier, both Consoles, and the Trust Authority
portal. In Indonesia this is not a preference. UU No. 8 Tahun 2016 tentang
Penyandang Disabilitas, the 2016 law on persons with disabilities, obliges
state administration and public services to provide accessibility and
reasonable accommodation. A national credential ecosystem is both.

This is the one principle here that the architecture does not currently enforce.
The draft names no accessibility standard, sets no requirement on any
user-facing Module, and defines no test. Nothing elsewhere in this repository
fills the gap either. Six of the seven principles can be checked against
something; this one cannot.

Where it belongs is the Governance Framework rather than this document, for the
same reason the retention rules do: it binds participants and is verified by
assessment, not by architecture. Until it is written there, treat this section as
a statement of the obligation and not as evidence that anything satisfies it.

## Chapter contents

1. [Section 1, System Models](system-models.md), what each Service groups, who
   runs it, and why one of the four is single
2. [Section 2, The transaction path and the trust path](transaction-path-and-trust-path.md),
   which Module sits on which plane, and what passes between them
3. [Section 3, Module Map](module-map.md), the eleven Modules, what each is
   built as and who runs it, who may call whom, and the network zone each is
   placed in
4. [Section 4, Architecture on the device: Mobile Wallet and Mobile Verifier](architecture-on-the-device.md),
   the four parts of an application, and what the Governance Profile fixes
5. [Section 5, Flows per use case](flows-per-use-case.md), eight flows end to
   end, from entity onboarding to a change of device
