---
title: "Architecture on the device: Mobile Wallet and Verifier Application"
description: The layout both applications share, the one-way dependency that keeps an SDK extractable, and where the two differ.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §3.4 -->

# 7. Architecture on the device: Mobile Wallet and Verifier Application

Mobile Wallet and Verifier Application have the same shape. Each is an
interface layer over a protocol layer, with encrypted storage and a secure
element beside them, all on a device the ecosystem does not own.

## 7.1 The four parts

In Mobile Wallet, the interface layer holds Consent UI, Trust Display,
Credential Renderer, and App Lock. The protocol layer under it holds Issuance
Client, Presentation Client, Credential Codec, Attestation Client, Auth Client,
and the Trust SDK. The Credential Store sits alongside, encrypted with
SQLCipher. The secure element, StrongBox on Android or the Secure Enclave on
iOS, holds the device key and one credential key for every credential the
wallet carries.

The citizen touches only the interface layer. Everything that leaves the device
leaves through the protocol layer, which is also the only part that reaches the
secure element, through a Keystore Manager, and the Credential Store.

| What the protocol layer talks to | What passes |
|---|---|
| CONNECTIDN | The citizen's OIDC login |
| Issuer Core | Issuance over OpenID4VCI |
| Verifier Core, Verifier Application | Presentation over OpenID4VP, or ISO 18013-5 in proximity |
| Wallet Backend Service | Key Attestation, device binding, recovery, push notification |
| Trust Registry | Trusted list, Credential Rulebook, and VICAL, read from cache |
| Secure element, Credential Store | Keys and stored credentials, without leaving the device |

Which of these the Governance Profile fixes, and to what degree, is a separate
question from who talks to whom. It is answered in
[Section 7.4](#74-which-interfaces-the-governance-profile-sets).

## 7.2 The protocol layer does not import the interface layer

The dependency runs one way. The protocol layer must not import anything from
the interface layer, which is what lets it be pulled out as a standalone SDK.

That is the reason the rule exists. The ecosystem takes many Wallet Providers,
each publishing a Mobile Wallet of its own, and every one of them has to get the
same protocols right against the same issuers and verifiers. A shared protocol
layer is how a second provider starts from a proven implementation instead of a
specification, and this one-way dependency is what keeps that extraction
affordable.

## 7.3 Where the two applications differ

Both applications have the layout above. They differ on who vouches for them,
what their secure element holds, and which side of a presentation they play.

| | Mobile Wallet | Verifier Application |
|---|---|---|
| Backed by | Wallet Backend Service (Wallet Provider) | Verifier Core (RP Intermediary) |
| What vouches for the device | Key Attestation, daily | Verifier Device Certificate, limited lifetime plus a CRL |
| Keys in the secure element | Device key, plus a credential key per credential | Device key |
| Role in the protocol | Presents, as holder | Requests, as reader |
| Storage | Encrypted Credential Store | On-device Activity Repository |
| User login | CONNECTIDN | Merchant account at the RP Intermediary |
| Trust SDK | From local cache | From local cache |

The asymmetry in the key row is the substantive one. A wallet accumulates a key
per credential, because each credential is bound to its own holder key; a
verifier device needs one key and keeps one.

## 7.4 Which interfaces the Governance Profile sets

Not every connection is fixed to the same degree, and two are not the
Governance Profile's to fix at all. Where an interface is marked partial, the
wire format is specified and the protocol around it is left to the party that
operates both ends.

| Interface | Standard | Set by the Governance Profile |
|---|---|---|
| Issuer Core to Mobile Wallet | OpenID4VCI 1.0 | Yes |
| Mobile Wallet to Verifier Core or Verifier Application | OpenID4VP 1.0, ISO 18013-5 | Yes |
| Mobile Wallet and Verifier Application to Trust Registry | LoTE JSON, TRQP, Credential Rulebook, VICAL | Yes |
| Mobile Wallet to Wallet Backend Service | Key Attestation format yes (OpenID4VCI Appendix D.1); the Wallet Provider's own registration and recovery protocol no | Partly |
| Verifier Application to Verifier Core | Verifier Device Certificate format yes (ISO 18013-5 Annex B); the intermediary's own provisioning protocol no | Partly |
| Mobile Wallet to CONNECTIDN | OpenID Connect | Set by BSSN |
| Application to secure element | Google and Apple platform APIs | No |

The two partial rows are where the ecosystem stops short on purpose. What a Key
Attestation or a Verifier Device Certificate looks like has to be fixed, because
another party verifies it. How a Wallet Provider registers its own installations
does not, because nobody outside that provider ever sees it.
