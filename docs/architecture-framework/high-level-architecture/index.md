---
title: "High-Level Architecture"
description: What the ecosystem is made of, how its parts are kept apart, and the principles that separation serves.
---

# High-Level Architecture {#high-level-architecture}

<p class="ekdn-lead" markdown="span">
This chapter is the shape of the system. The previous one named who is
answerable for what; this one names what actually runs, where each piece sits,
and which pieces are forbidden to speak to one another.
</p>

Three words carry the chapter, and they nest: System Model, Module, and component.
[System Models](system-models.md) defines them beside the figure that
shows how they sit inside one another, and describes the four System Models and the
ten Modules that fill them.

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

## Design principles {#design-principles}

A principle here is a constraint the architecture already obeys, not an ambition
it works toward.

### The two paths never cross {#the-two-paths-never-cross}

Two planes run through the ecosystem and they do not meet at runtime. On the
transaction path, an issuer hands a credential to a wallet, and the wallet shows
it to a verifier. On the trust path, Trust Authority drives the registry and
the identifier service that stand behind all of them. No message crosses from
one to the other while a credential is being issued or verified.

What makes that possible is that everything the transaction path needs was
published in advance as a file and copied into a local cache before the
transaction began: the list of accredited entities, the rules for the credential
type, each entity's published keys. Even checking whether a credential has been
revoked is a read of a file the issuer itself publishes, rather than a question
put to the center.

This is the principle that makes a single national Trust Infrastructure
acceptable: a single instance is a point of failure only if it sits on the
path, and [the trust path][the-trust-path] sets out why this one does not. How
the two planes are drawn is
[The transaction path and the trust path](transaction-path-and-trust-path.md).

### The center may be down {#the-center-may-be-down}

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
[Quality goals](../software-architecture/quality-targets.md), and how
long a cache may be trusted belongs to the
[Governance Framework](../../governance-framework/index.md), not here. Nothing
has set it there yet, which [the trust path][the-trust-path] states in full.

### Finished specifications only {#finished-specifications-only}

Only final specifications bind implementations in this ecosystem. A draft does
not, however widely it is implemented elsewhere. Two drafts are the exception,
and this section names them. A profile published by another ecosystem is read
as a comparison rather than as a requirement.

The rule has already cost the architecture something, which is what makes it a
rule rather than a preference. A draft mechanism for proving that a wallet
installation is genuine would have fitted neatly, and it is not used. The same
job is done with
mechanisms the final issuance specification already defines. Which specification
is fixed for which job is set out in
[Data Model and Protocols, technology map](../data-model-and-protocols/index.md#technology-map).

Two drafts are admitted, because the credential formats cannot work without
them. [SD-JWT VC][credential-formats-and-their-signatures] defines the credential that [OpenID4VCI 1.0][exchange-protocols] and [OpenID4VP 1.0][exchange-protocols]
carry as `dc+sd-jwt`. Those two specifications fix the format identifier and
how it is requested, and they leave the contents of the credential to the
SD-JWT VC draft. The salted-hash mechanism underneath is already final as
[RFC 9901][credential-formats-and-their-signatures]. [IETF Token Status List][trust-lists-and-credential-status] is the revocation mechanism for SD-JWT VC and
mdoc, and it is waiting in the RFC Editor queue. Each of the two is pinned to
one revision and moves to the RFC once it is published. Which revisions are
pinned is still open. No other draft is admitted on the same grounds.

Interoperability also has to survive two codebases. The Trust SDK exists twice,
once for the server Modules and once for the two applications, and the two are
held together by a shared set of test vectors rather than by shared code. Where
a standard leaves a choice open, the Governance Profile closes it, so that two
independent implementations reach the same answer.

### Minimal disclosure {#minimal-disclosure}

A verifier receives the attributes it has registered a need for and no others.
That holds because five separate things enforce it at once, not because any one
of them is strong enough alone.

The credential format decides what is possible at all. Two of the three formats
let a holder reveal one attribute without revealing its neighbors. The third
cannot, and the architecture answers by restricting where that format may be
used rather than by accepting the leak. Both the formats and the restriction are
in
[Three credential formats][three-credential-formats].

The Credential Rulebook classifies every attribute of every credential type, and
that classification is what the restriction above is measured against. On the
verifier's side a Relying Party is bounded twice over: by its Authority Statement
(per entity, which sets its accreditation scope), and by its Use Statement (per
registered use, which sets the purpose and approved attribute subset for that
transaction). A merchant is bounded three times over, because its Verifier Device
Certificate adds a third boundary through ReaderAuthRole.

Registration is literal rather than a figure of speech. A verifier states each
use it intends before it runs it, naming the purpose and the attributes that
purpose needs, and what the Root Authority approves comes back as a Use
Statement, signed by Trust Authority, that the verifier carries in every
request. The wallet holds the request
against it and refuses anything outside, so the limit on one transaction is the
one that was approved for that use rather than the whole of the verifier's
scope. It is set out in [Registered use][registered-use].

Correlation is the one exposure this phase accepts knowingly. A holder has one
credential key per wallet installation, and so one identifier, for every
credential it holds, which means two verifiers comparing notes can recognize
the same holder. The decision is marked temporary, and each stored credential
records which key binds it, so moving later to a key per credential changes no
credential format.
[Identifier](../data-model-and-protocols/identifier.md) says which
identifier is used where.

### Security by design {#security-by-design}

The architecture assumes that a key which can be moved will eventually be moved,
and removes the ability to move it.

An entity's keys are generated and kept on the entity's own side, by its Key
Manager, and Trust Authority never holds one of them. What Trust Authority
receives is a public key, proof that the entity holds the matching private key,
and a certificate request where one is needed. Every key change goes into the
entity's `did:webvh` log, and an entry without DID Service's witness is
rejected by every resolver, so no key can be swapped quietly. On a phone, the keys live in
hardware the operating system keeps apart from ordinary storage, and a
merchant's key never leaves the merchant's own device even though the Verifier
Core behind it belongs to an RP Intermediary.

Placement backs this up. Trust Authority's HSM, which holds both offline
certificate roots and, in a separate partition, the did:webvh witness key, sits in
the secure zone. Only Trust Authority and, for that witness key partition alone,
the Log Service of DID Service may reach it.
Public endpoints and administrative ones sit on separate doors of the same
application, so one Module is exposed in two different degrees. A Console
reaches its Core through the administrative door and never touches a database.
The layout is
[network zones and placement][network-zones-and-placement].

The trust anchors are split for the same reason. There are two roots, one for
the issuing side and one for the reading side, kept apart so that a compromise
on one side does not authorize the other. Below that, every protocol option that
could be left loose is fastened down, and the wallet is treated throughout as
software an attacker may take apart, because it is.

### The citizen decides {#the-citizen-decides}

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
[RP Intermediary and merchant](../roles/rp-intermediary-and-merchant.md).

The purpose is held to the same standard as the name. It is read from the Use
Statement Trust Authority signed for that use, not from the request the
verifier composed, so a verifier cannot describe its own reason for asking in
whatever terms suit it. Where a request carries none, during the transition
period, the wallet says so on the consent screen rather than passing the
verifier's own wording off as approved.

What was consented to is recorded afterward as a consent receipt, so the
decision is auditable later by someone other than the party that benefited from
it. The record's format is specified in the
[Technical Specifications](../../technical-specifications/index.md), and the
retention rules belong to the
[Governance Framework](../../governance-framework/index.md).

The citizen keeps a record too, and it is made of what the verifier already
signed. Every request arrives signed, under the verifier's own key or under a
merchant's device certificate, and carries the Use Statement Trust Authority
signed for that use. The wallet holds both before anyone is asked to decide, so
it keeps them afterward alongside the outcome and the time. Nothing is signed
anew for this, and no attribute value is ever written down: what the wallet
stores is the asking, never the answering. Format and retention sit where the
verifier's receipt puts them.

### Accessibility {#accessibility}

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

## Chapter contents {#hla-chapter-contents}

1. [System Models](system-models.md), what each System Model groups, who
   runs it, and why one of the four is single
2. [The transaction path and the trust path](transaction-path-and-trust-path.md),
   which Module sits on which plane, and what passes between them
3. [Module Map](module-map.md), the ten Modules, what each is
   built as and who runs it, who may call whom, and the network zone each is
   placed in
4. [Flows per use case](flows-per-use-case.md), the thirteen flows, from
   entity onboarding and incident key revocation through issuance,
   verification, and the lifetime of a wallet on one citizen's phone
5. [Architecture on the device: Mobile Wallet and Mobile Verifier](architecture-on-the-device.md),
   the four parts of an application, and what the Governance Profile fixes

