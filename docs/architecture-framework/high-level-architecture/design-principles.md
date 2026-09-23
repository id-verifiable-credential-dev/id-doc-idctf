---
title: Design Principles
description: The six constraints this architecture already obeys, and the one obligation it does not yet enforce.
---

<!-- Sumber: EUDI Architecture and Reference Framework 3.0.0, §4.2, disesuaikan; Arsitektur Ekosistem Identitas Digital v0.2, §1 (Kep. 3, 5, 8, 9, 12, 16, 20, 21, 23, 25, 26, 27), §3, §8.7 -->

# 1. Design Principles

A principle on this page is a constraint the architecture already obeys, not an
ambition it works toward. Each of the first six can be traced to a numbered
decision in the draft or to a rule the pipeline tests, and each one forbids
something specific. The seventh is different, and it is marked as such.

| Principle | What it forbids | Where it is enforced |
|---|---|---|
| [1.1](#11-the-transaction-path-and-the-trust-path-never-cross) The two paths never cross | A call to Trust Infrastructure while a credential is being issued or verified | Four dependency bans tested in the pipeline |
| [1.2](#12-the-ecosystem-keeps-working-when-the-centre-is-down) The centre may be down | Any national component whose outage stops verification | Cache tolerance limits, issuer-hosted status lists |
| [1.3](#13-interoperability-through-finished-specifications) Finished specifications only | Building a normative rule on an Internet-Draft | Governance Profile, shared Trust SDK test vectors |
| [1.4](#14-privacy-by-design-through-minimal-disclosure) Minimal disclosure | Handing a verifier an attribute it has no registered need for | Credential Rulebook, `allowed_attrs`, `ReaderAuthRole` |
| [1.5](#15-security-by-design) Security by design | A signing key leaving the place that holds it | Network zones, secure elements, a KMS that cannot sign |
| [1.6](#16-the-citizen-sees-who-is-asking-and-decides) The citizen decides | Presenting a credential to a party the citizen has not seen named | Consent UI, Trust Display, consent receipt |
| [1.7](#17-accessibility) Accessibility | Nothing yet | Nowhere yet |

## 1.1 The transaction path and the trust path never cross

Two planes run through this ecosystem and they do not meet at runtime. On the
transaction path, Issuer Core issues to Mobile Wallet over OpenID4VCI, and
Mobile Wallet presents to Verifier Core or Mobile Verifier over
OpenID4VP and ISO 18013-5. On the trust path, Trust Authority drives Trust
Registry, DID Service, and KMS. No message crosses from one to the other while
a credential is being issued or verified.

What makes this possible is that every artifact the transaction path needs was
published as a static file and cached before the transaction started: the
trusted list, the Credential Rulebook, DID Documents, VICAL. The issuer hosts
its own status list, so even revocation checking is a read of a file the issuer
published rather than a question put to the centre.

This is the principle that lets a single national Trust Infrastructure be
acceptable. One instance of anything is a single point of failure only if it is
on the path. Because it is not, its outage costs nothing until the caches age
out. The rule is not left to discipline: four call paths are forbidden outright
and the pipeline fails if any of them appears. They are listed in
[Section 4.2, Who may call whom](module-map.md).

## 1.2 The ecosystem keeps working when the centre is down

If the whole of Trust Infrastructure stops, issuance and verification continue
from cache until the tolerance limit runs out. Offline verification is stronger still and has to succeed with the
device in airplane mode, because proximity verification over ISO 18013-5
reaches no network at all.

Three decisions carry this. Status lists are published, signed, and hosted by
each issuer rather than centrally, so revocation data survives a central outage
and scales with the number of issuers. Trusted lists, Credential Rulebooks, and
VICAL are static files behind a CDN, which fails differently and more gracefully
than an API. Every Module that consumes them holds a cache with a stated
tolerance limit, and the limit, not the network, decides when verification stops.

The measurable targets for all of this live in
[Quality goals](../software-architecture/quality-targets.md), and the cache
tolerance policy is set in the
[Governance Framework](../../governance-framework/index.md), not here.

## 1.3 Interoperability through finished specifications

Only final specifications are normative in this ecosystem. OpenID4VCI 1.0,
OpenID4VP 1.0, ISO/IEC 18013-5, SD-JWT VC, and VC-JOSE-COSE bind
implementations. An Internet-Draft does not, no matter how widely it is
implemented elsewhere. HAIP is read as a comparison, never as a requirement.

The rule has already cost the architecture something, which is how you can tell
it is real. Attestation-based client authentication at the PAR and token
endpoints would have been a natural fit for proving a wallet installation is
genuine, and it is not used, because it is still a draft. Key Attestation is
carried instead through mechanisms that OpenID4VCI 1.0 itself defines.

| What is fixed | Decision |
|---|---|
| Issuance protocol | OpenID4VCI 1.0 |
| Online presentation | OpenID4VP 1.0 with DCQL |
| Proximity presentation | ISO/IEC 18013-5, and mdoc is used for proximity only |
| Trust query | ToIP TRQP v2.0 |
| Trusted list | ETSI TS 119 602 (LoTE JSON) only, with no TSL XML |
| Entity identifier | did:webvh |

Interoperability also has to survive two codebases. The Trust SDK exists twice,
once in Go for the server Modules and once in Dart for the two applications,
and the two are held together by a shared set of test vectors rather than by a
shared implementation. Where a standard leaves a choice open, the Governance
Profile closes it, so that two independent implementations reach the same
answer.

## 1.4 Privacy by design, through minimal disclosure

A verifier receives the attributes it has registered a need for and no others.
This is enforced in four places at once, which is the only reason it holds.

The credential format decides what is technically possible. SD-JWT VC and ISO
mdoc support selective disclosure, so a holder can reveal a birth date without
revealing an address. The third format does not: `ldp_vc` secured with the
`ecdsa-jcs-2019` cryptosuite has no selective disclosure at all, and the
architecture responds by restricting it rather than by accepting the leak. A
credential type may use `ldp_vc` only when every one of its attributes is
classified `open` or `normal`.

The Credential Rulebook classifies each attribute of each credential type, and
that classification is what the restriction above is measured against. On the
verifier side, a registered merchant is bounded twice over: by
`allowed_attrs`, configured for it in the Verifier Console, and by the
`ReaderAuthRole` extension carried inside its Verifier Device Certificate,
which states its attribute authority cryptographically rather than by
configuration alone.

Correlation is attacked separately from disclosure. The holder identifier is a
`did:key` created fresh for every credential, so two credentials held by the
same citizen carry no shared identifier that would let two verifiers, or an
issuer and a verifier, recognise them as one person.

## 1.5 Security by design

The architecture assumes that a key which can be moved will eventually be
moved, and removes the ability to move it.

The KMS generates, rotates, and revokes entity keys, and it has no sign
operation. Nothing can ask it to sign; an entity that needs a signature uses its
own local keystore through a Signing Provider. On the device, the device key and
the per-credential credential keys live in StrongBox or the Secure Enclave, and
a merchant's key never leaves the merchant's own device even though the
Verifier Core behind it belongs to an RP Intermediary.

Placement backs this up. KMS, the HSM, and both offline CA roots sit in a zone
reachable only by Trust Authority. Public protocol endpoints and the Admin APIs
sit on separate ingresses, so one application exposes two doors with different
exposure. Consoles reach their Core only through the Admin API and never touch a
database. The layout is set out in
[Section 5, Network zones and placement](network-zones-and-placement.md).

The trust anchors are split for the same reason. There are two X.509 roots,
Issuer Root CA for the issuing side and Verifier Root CA for the reading side,
kept separate so that compromise on one side does not authorise the other. At
the protocol layer, PKCE and PAR are both mandatory, a transaction code binds
the pre-authorized code flow, and DPoP binds every access token to a key. The
wallet is treated as a public client throughout, because it is one.

## 1.6 The citizen sees who is asking, and decides

Before a credential leaves the wallet, the citizen is shown who is requesting
it, what is being requested, and on what authority. The Mobile Wallet's
interface layer exists for this: a Trust Display that resolves the requester to
a named, accredited entity, a Consent UI that states the attributes, and a
Credential Renderer that shows what is held. The citizen authenticates to the
wallet through CONNECTIDN before any of it.

The requester cannot stay anonymous, and how it identifies itself depends on
what it is. An accredited relying party operating online presents a
`did:webvh` as its `client_id` and signs the Request Object with a key
published in its DID Document, which the wallet resolves against the trusted
list. A merchant presents the Verifier Device Certificate its RP Intermediary
issued, online as
`x509_hash` with `x5c` and offline as `x5chain`. Either way the wallet has
something to show the citizen that a third party stands behind, rather than a
name the requester chose for itself.

What was consented to is recorded afterward as a consent receipt, so the
decision is auditable later by someone other than the party that benefited from
it. The record's format is specified in
[TS-12](../../technical-specifications/index.md),
and the retention rules belong to the
[Governance Framework](../../governance-framework/index.md).

## 1.7 Accessibility

Every surface a person touches has to be usable by people with disabilities:
the Mobile Wallet, the Mobile Verifier, both Consoles, and the Trust
Authority portal. In Indonesia this is not a preference. UU No. 8 Tahun 2016
tentang Penyandang Disabilitas obliges state administration and public services
to provide accessibility and reasonable accommodation, and a national credential
ecosystem is both.

This is the one principle on the page that the architecture does not currently
enforce. The draft names no accessibility standard, sets no requirement on any
user-facing Module, and defines no test. Nothing elsewhere in this repository
fills the gap either. Six of the seven principles above can be checked against
something; this one cannot.

Where it belongs is the Governance Framework rather than this document, for the
same reason privacy retention rules do: it binds participants and is verified
by assessment, not by architecture. Until it is written there, treat this
section as a statement of the obligation and not as evidence that anything
satisfies it.
