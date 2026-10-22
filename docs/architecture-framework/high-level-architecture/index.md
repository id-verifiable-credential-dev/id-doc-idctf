---
title: "High-Level Architecture"
description: What the ecosystem is made of, how its parts are kept apart, and the principles that separation serves.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §3 (pembuka), §1 (Kep. 21); tracks/0212. Di luar source-data, disadur dari EUDI ARF 3.0.0 §4.2 (tracks/0007): Minimal disclosure §4.2.4, Security by design §4.2.5, The citizen decides §4.2.1, Accessibility §4.2.2 dan UU No. 8 Tahun 2016 Pasal 18–19 -->

# High-Level Architecture {#high-level-architecture}

<p class="ekdn-lead" markdown="span">
The ecosystem's software is four Services, ten Modules, and the Components
inside them. This chapter names what runs, where each piece sits, and which
pieces are forbidden to speak to one another.
</p>

Three words carry the chapter, and they nest: Service, Module, and Component.
[Services](services.md) defines them beside the figure that
shows how they sit inside one another, and describes the four Services and the
ten Modules that fill them.

The separation that shapes everything else runs between the transaction path
and the trust path, set out in
[the two paths never cross][the-two-paths-never-cross]. A third group sits on
neither: the consoles and Wallet Backend Service configure and vouch for the
parties on the transaction path without issuing or verifying anything
themselves.

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

On the transaction path, an issuer hands a credential to a wallet, and the
wallet shows it to a verifier. On the trust path, Trust Authority drives Trust Registry and
Decentralized Identifier (DID) Service, which stand behind all of them. No message crosses from
one to the other while a credential is being issued or verified.

Everything the transaction path needs was published in advance as a file and
copied into a local cache before the transaction began: the list of accredited entities, the rules for the credential
type, each entity's published keys.

This is the principle that makes a single national Trust Infrastructure
acceptable: a single instance is a point of failure only if it sits on the
path, and [the trust path][the-trust-path] sets out why this one does not. How
the two planes are drawn is
[The transaction path and the trust path](transaction-path-and-trust-path.md).

### Trust Infrastructure may be down {#trust-infrastructure-may-be-down}

If the whole of Trust Infrastructure stops, issuance and verification carry on
from cache until the tolerance limit runs out. Verification in person asks more
than that again: it has to succeed with the phone in airplane mode, because two
devices held next to each other reach no network at all.

Three decisions carry this. Revocation data is published and hosted by each
issuer rather than centrally, so it survives an outage of Trust Infrastructure and grows with the
number of issuers instead of concentrating in one place. The lists and Rulebooks
everyone reads are static files behind a content delivery network, which fails
more gracefully than an API does. And every Module that consumes them keeps a
cache with a stated tolerance limit, so what ends a verification is the limit
rather than the network.

The measurable targets live in
[quality targets][quality-targets], and how
long a cache may be trusted belongs to the
Governance Profile, not here. Nothing
has set it there yet, which [the trust path][the-trust-path] states in full.

### Finished specifications only {#finished-specifications-only}

Only final specifications bind implementations in this ecosystem. A draft does
not, however widely it is implemented elsewhere, and four drafts are the
exception. A profile over those specifications, such as the
[OpenID4VC High Assurance Interoperability Profile (HAIP) 1.0][ref-openid4vc-haip],
is read as a comparison rather than as a requirement.

A wallet installation is proven genuine with mechanisms the final issuance
specification defines, not with a draft mechanism. Which specification
is fixed for which job is set out in
[the technology map][technology-map].

Four drafts are admitted, because the credential formats and the identifiers
cannot work without them.

- [SD-JWT-based Verifiable Credentials (SD-JWT VC)][ref-i-d-ietf-oauth-sd-jwt-vc]
  defines the credential that
  [OpenID for Verifiable Credential Issuance (OpenID4VCI) 1.0][ref-openid4vci]
  and [OpenID for Verifiable Presentations (OpenID4VP) 1.0][ref-openid4vp] carry
  as `dc+sd-jwt`. Those two specifications fix the format identifier and how it
  is requested, and leave the contents of the credential to the draft. The
  salted-hash mechanism underneath is already final as
  [RFC 9901][ref-rfc9901]. It is pinned to draft -13, the revision HAIP
  references, and moves to the RFC once one is published.
- [IETF Token Status List][ref-i-d-ietf-oauth-status-list] is the revocation
  mechanism for SD-JWT VC and mdoc, and it is waiting in the RFC Editor queue.
  It is pinned to draft -14, the revision HAIP references, and moves to the RFC
  once it is published.
- [W3C VC JSON Schema][ref-vc-json-schema] is the only way a W3C Verifiable
  Credentials Data Model (VCDM) 2.0 credential names its schema, in
  `credentialSchema`, and it is still a Candidate Recommendation Draft. It is
  pinned to the draft of 4 February 2025 and moves to the Recommendation once
  one is published.
- [did:key][ref-did-key] v0.9 is a Community Group draft, and the holder's
  identifier, the witness keys, and the trusted list key are all written in it.
  It is pinned to the commit of 2 November 2025.

No other draft is admitted on the same grounds.

Interoperability also has to survive two codebases. The Trust SDK exists twice,
once for the server Modules and once for the two applications, and the two are
held together by a shared set of test vectors rather than by shared code. Where
a standard leaves a choice open, the Governance Profile closes it, so that two
independent implementations reach the same answer.

### Minimal disclosure {#minimal-disclosure}

A Relying Party receives the attributes it has registered a need for and no others.
That holds because five separate things enforce it at once, not because any one
of them is strong enough alone.

The credential format decides what is possible at all. Two of the three formats
let a holder reveal one attribute without revealing its neighbors. The third
cannot, and the architecture answers by restricting where that format may be
used rather than by accepting the leak. Both the formats and the restriction are
in
[Three credential formats][three-credential-formats].

The Credential Rulebook classifies every attribute of every credential type, and
that classification is the measure the restriction is read against. On the
verifier's side a Relying Party is bounded twice over: by its permissions, each
answered by an Authority Statement, which together are its accreditation scope,
and by its Use Statement (per registered use, which sets the purpose and
approved attribute subset for that transaction). A merchant is bounded three
times over: by the accreditation scope and the category Use Statement of the
RP Intermediary it works under, and by its Verifier Device Certificate, whose
`ReaderAuthRole` adds the third boundary.

A Relying Party states each use it intends before it runs it, and the
Use Statement it is granted bounds one transaction instead of the whole of its
scope. [Registered use][registered-use] sets it out.

Correlation is the one exposure IDCTF accepts knowingly. A holder has one
credential key per wallet installation, and so one identifier, for every
credential it holds, which means two verifiers comparing notes can match
the same holder.
[Identifier](../data-model-and-protocols/identifier.md) says which
identifier is used where.

### Security by design {#security-by-design}

A key that can be moved will eventually be moved, so the architecture removes
the ability to move it.

An entity's keys are generated and kept on the entity's own side, by its
Key Manager, and Trust Authority never holds one of them. What Trust Authority
receives is a public key, proof that the entity holds the matching private key,
and a certificate request where one is needed. Every key change goes into the
entity's `did:webvh` log, and an entry without DID Service's witness is rejected
by every resolver, so no key can be swapped quietly. On a phone, the keys live
in hardware the operating system keeps apart from ordinary storage, and a
merchant's key never leaves the merchant's own device even though the Verifier
Core behind it belongs to an RP Intermediary.

Placement backs this up. Trust Authority's hardware security modules (HSMs) sit
in the secure zone: each offline certificate root in an HSM of its own, and the
online keys in a third, with the did:webvh witness key in a separate partition
of it. Only Trust Authority and, for that witness key partition alone, the Log
Service of DID Service may reach them.
Public endpoints and administrative ones sit on separate doors of the same
application, so one Module is exposed in two different degrees. A Console
reaches its Core through the administrative door and never touches a database.
The layout is
[network zones and placement][network-zones-and-placement].

The trust anchors are split for the same reason. There are two roots, one for
the issuing side and one for the reading side, kept apart so that a compromise
on one side does not authorize the other. Below that, every protocol option that
could be left loose is fastened down, and the wallet is treated throughout as
software an attacker may take apart.

### The citizen decides {#the-citizen-decides}

Before a credential leaves the wallet, the citizen is shown who is asking, what
is being asked for, and on what authority. The citizen authenticates to the
wallet before any of it.

The requester cannot stay anonymous, and how it identifies itself depends on
what it is. An accredited Relying Party publishes an identifier and signs its
request with a key the wallet can look up in the trusted list. A merchant
presents the certificate its RP Intermediary issued to
it, which carries the
merchant's authority inside it. Either way the wallet has something to show the
citizen that a third party stands behind, rather than a name the requester chose
for itself. The second case is
[RP Intermediary and merchant](../roles/rp-intermediary-and-merchant.md).

The purpose is read from the Use Statement Trust Authority signed for that use,
not from the request the verifier composed. Where a request carries none, during
the transition period, the wallet says so on the consent screen.

What was consented to is recorded afterward as a consent receipt, so the
decision is auditable later by someone other than the party that benefited from
it. The record's format is fixed in
[what the verifier keeps][ts-5-11-what-the-verifier-keeps], and how long it is
kept is set by the Governance Profile, as a value the Governance Framework holds
participants to under [retention][gf-retention].

The citizen keeps a record too, and it is made of what the verifier already
signed. Every request arrives signed, under the Relying Party's own key or under
a merchant's device certificate, and carries the Use Statement Trust Authority
signed for that use. The wallet holds both before anyone is asked to decide, so
it keeps them afterward alongside the outcome and the time. Nothing is signed
anew for this, and no attribute value is ever written down.
[What the wallet keeps][ts-5-11-what-the-wallet-keeps]
fixes its format, the Governance Profile sets the longest it is kept, and the
citizen may delete it sooner.

### Accessibility {#accessibility}

Every surface a person touches has to be usable by people with disabilities: the
Mobile Wallet, the Mobile Verifier, both Consoles, and the Trust Authority
portal. In Indonesia, [UU No. 8 Tahun 2016 tentang
Penyandang Disabilitas][ref-uu-8-2016], the 2016 law on persons with disabilities,
obliges state administration and public services to provide accessibility and
reasonable accommodation, and a national credential ecosystem is both.

The Governance Framework binds every surface a person uses to Web Content
Accessibility Guidelines (WCAG) 2.2 Level AA and has an Assessment Body audit
it, as [accessibility][gf-accessibility] sets out.

## Chapter contents {#hla-chapter-contents}

1. [Services](services.md)
2. [The transaction path and the trust path](transaction-path-and-trust-path.md)
3. [Module Map](module-map.md)
4. [Flows per use case](flows-per-use-case.md)
5. [Architecture on the device: Mobile Wallet and Mobile Verifier](architecture-on-the-device.md)

