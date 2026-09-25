---
title: "Architecture on the device: Mobile Wallet and Mobile Verifier"
description: The layout both applications share, the one-way dependency that keeps an SDK extractable, and where the two differ.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §3.4 -->

# 4. Architecture on the device: Mobile Wallet and Mobile Verifier

Mobile Wallet and Mobile Verifier have the same shape. Each is an
interface layer over a protocol layer, with encrypted storage and a secure
element beside them, all on a device the ecosystem does not own.

## 4.1 The four parts

In Mobile Wallet, the interface layer holds Consent UI, Trust Display,
Credential Renderer, and App Lock. The protocol layer under it holds Issuance
Client, Presentation Client, Credential Codec, Attestation Client, Auth Client,
and the Trust SDK. The Credential Store sits alongside, encrypted with
SQLCipher. The secure element, StrongBox on Android or the Secure Enclave on
iOS, holds the device key and one credential key for every credential the
wallet carries. The component-by-component breakdown of both applications is in
[Section 2.2.1, Mobile Wallet](../software-architecture/components-inside-a-module.md#221-mobile-wallet)
and
[Section 2.3.3, Mobile Verifier](../software-architecture/components-inside-a-module.md#233-mobile-verifier).

The citizen touches only the interface layer. Everything that leaves the device
leaves through the protocol layer, which is also the only part that reaches the
secure element, through a Keystore Manager, and the Credential Store. What that
one layer talks to falls into four kinds.

1. The transaction itself, which reaches three counterparties. CONNECTIDN
   authenticates the citizen over OpenID Connect. Issuer Core delivers a
   credential over OpenID4VCI. The verifier side receives a presentation in two
   forms: Verifier Core over OpenID4VP, and Mobile Verifier, at a merchant or
   at a Relying Party's counter, over OpenID4VP online and over ISO/IEC 18013-5
   in proximity.
2. The application's own backing. Wallet Backend Service carries Key
   Attestation, device binding, recovery, and push notification, and no issuer
   or verifier is party to any of it.
3. A read-only feed. Trust Registry supplies the trusted list, the Credential
   Rulebook, and VICAL, all of which the application reads from its local cache
   rather than fetching mid-transaction.
4. What is not remote at all. The secure element and the Credential Store are
   reached on the device, and what passes between them and the protocol layer
   never leaves it.

Which Module is allowed to call which is set out in
[Section 3.3, Who may call whom](module-map.md#33-who-may-call-whom).

Which of these interfaces the Governance Profile fixes, and to what degree, is a
separate question from who talks to whom. It is answered in
[Section 4.4](#44-which-interfaces-the-governance-profile-sets).

## 4.2 The protocol layer does not import the interface layer

The dependency runs one way. The protocol layer must not import anything from
the interface layer, which is what lets it be pulled out as a standalone SDK.

That is the reason the rule exists. The ecosystem takes many Wallet Providers,
each publishing a Mobile Wallet of its own, and every one of them has to get the
same protocols right against the same issuers and verifiers. A shared protocol
layer is how a second provider starts from a proven implementation instead of a
specification, and this one-way dependency is what keeps that extraction
affordable.

## 4.3 Where the two applications differ

Both applications have the layout above, and one part of it behaves identically
in each: the Trust SDK reads from a local cache on both, so neither application
queries Trust Registry while a citizen waits.

The differences are elsewhere. They come down to who vouches for the
application, what its secure element holds, which side of a presentation it
plays, what it stores, and how its user signs in. The table below takes those
one row at a time.

| | Mobile Wallet | Mobile Verifier |
|---|---|---|
| Backed by | Wallet Backend Service (Wallet Provider) | Verifier Core (the RP Intermediary for a merchant's device, the Relying Party for its own counter device) |
| What vouches for the device | Key Attestation, daily | Verifier Device Certificate, limited lifetime plus a CRL |
| Keys in the secure element | Device key, plus a credential key per credential | Device key |
| Role in the protocol | Presents, as holder | Requests, as reader |
| Storage | Encrypted Credential Store | On-device Activity Repository |
| User login | CONNECTIDN | Merchant account at the RP Intermediary, or a staff account at the Relying Party |

The asymmetry in the key row is the substantive one. A wallet accumulates a key
per credential, because each credential is bound to its own holder key; a
verifier device needs one key and keeps one.

## 4.4 Which interfaces the Governance Profile sets

Not every connection is fixed to the same degree, and two are not the
Governance Profile's to fix at all. The table below answers that single question
for each interface, alongside the standard the interface runs on. Read the last
column first: it is what an implementer has to comply with.

| Interface | Standard | Set by the Governance Profile |
|---|---|---|
| Issuer Core to Mobile Wallet | OpenID4VCI 1.0 | Yes |
| Mobile Wallet to Verifier Core | OpenID4VP 1.0 | Yes |
| Mobile Wallet to Mobile Verifier | OpenID4VP 1.0, ISO/IEC 18013-5 | Yes |
| Mobile Wallet and Mobile Verifier to Trust Registry | LoTE JSON, TRQP, Credential Rulebook, VICAL | Yes |
| Mobile Wallet to Wallet Backend Service | Key Attestation, OpenID4VCI Appendix D.1 | Partly |
| Mobile Verifier to Verifier Core | Verifier Device Certificate, ISO/IEC 18013-5 Annex B | Partly |
| Mobile Wallet to CONNECTIDN | OpenID Connect | Set by BSSN |
| Application to secure element | Google and Apple platform APIs | No |

The two partial rows are where the ecosystem stops short on purpose. On each of
them the artifact is specified and the protocol carrying it is not. What a Key
Attestation or a Verifier Device Certificate looks like has to be fixed, because
another party verifies it: an issuer reads the attestation a wallet sends, and a
wallet reads the certificate a Mobile Verifier presents. The rest stays with
the party that runs it: how a Wallet Provider registers and recovers its own
installations, and how a Verifier Core provisions the devices it answers for.
Nobody outside that party ever sees those messages.

The last two rows are fixed somewhere else entirely. CONNECTIDN's interface is
set by BSSN, the agency that runs the national digital identity connector
service. The platform APIs belong to Google and Apple. The Governance Profile
takes both as given.
