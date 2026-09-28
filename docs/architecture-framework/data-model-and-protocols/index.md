---
title: "Data Model and Protocols"
description: The standards this ecosystem adopted, the ones it turned down, and where each format, identifier, protocol, and artifact is specified.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §4 (pengantar), §4.1 (Kep. 9) -->

# Data Model and Protocols

<p class="ekdn-lead" markdown="span">
Take, do not build. Every format and every protocol in this chapter is a
standard that already exists, already has implementations, and was already
argued over by people outside Indonesia. What the ecosystem writes for itself is
the layer of rules sitting on top of them.
</p>

That layer has three levels, and only the first of them belongs to this
document. A **Credential Rulebook** covers one credential type: its schema, the
formats it may take, how it is displayed, how far each attribute may be
minimized, and the assurance it demands. Its shape is in [Section 1.6](credential-formats.md#16-the-credential-rulebook), and the
rulebooks themselves are a document of their own, [Credential Rulebook Catalog](../../credential-rulebook/index.md).
Above it, a **Governance Profile** fixes the technical choices a standard
leaves open across every credential type, such as algorithms, cache lifetimes,
protocol versions, and how an assurance level maps onto an [ISO/IEC 18045](../references.md#device-attestation-and-assurance) value.
Above that, the **Governance Framework** covers institutions and people: who
decides what, which approval a change has to walk through, and what happens
when a rule is broken. Both are set out in [Governance Framework](../../governance-framework/index.md), not here.

## Technology map

Choosing a standard means turning others down, and a rejected standard is worth
recording because the question comes back. The right column is the one that
saves an argument later.

| Category | Used | Deliberately dropped |
|---|---|---|
| Protocols | [OpenID4VCI](../references.md#exchange-protocols), [OpenID4VP](../references.md#exchange-protocols) with DCQL, [ISO/IEC 18013-5](../references.md#exchange-protocols), [ToIP TRQP](../references.md#exchange-protocols) | DIDComm, Presentation Exchange, SIOPv2 |
| Credential formats | [SD-JWT VC](../references.md#credential-formats-and-their-signatures), [mdoc](../references.md#credential-formats-and-their-signatures), [W3C VCDM 2.0](../references.md#credential-formats-and-their-signatures) (`ldp_vc`) | AnonCreds, JWT-VC 1.1 (`jwt_vc_json`), SD-JWT VCLD, BBS |
| DID methods | [did:webvh](../references.md#identifiers-and-keys), [did:key](../references.md#identifiers-and-keys) | did:web, did:ebsi, did:ion, did:jwk |
| Key algorithms | ES256 on P-256 for every key; Ed25519 (`eddsa-jcs-2022`) only for did:webvh update and witness keys, as did:webvh v1.0 requires | secp256k1, RSA; Ed25519 anywhere else |
| Key storage | Secure element on devices; each entity's Key Manager: an encrypted software keystore by default, a cloud KMS, or an HSM over [PKCS#11](../references.md#key-storage-interfaces) | Entity keys generated outside the entity; an unencrypted software key |
| Status | [IETF Token Status List](../references.md#trust-lists-and-credential-status), [W3C Bitstring Status List](../references.md#trust-lists-and-credential-status), [CRL](../references.md#certificates-and-revocation) | OCSP, a status register of its own |
| Trust lists | LoTE JSON as in [ETSI TS 119 602](../references.md#trust-lists-and-credential-status), [VICAL](../references.md#trust-lists-and-credential-status) | TSL XML as in ETSI TS 119 612, OpenID Federation, a ledger |

One pattern runs down the right column. Almost everything dropped is a second
way of doing something the left column already does, and a second way costs an
implementation in every wallet, every verifier, and both copies of the Trust
SDK. The exceptions are the entries dropped for a different reason: an entity
key generated anywhere but at the entity, or kept unencrypted, because a key
that can be moved or read will eventually be; and a status register of its own,
because it would tell Trust Infrastructure how many credentials are in
circulation.

## Chapter contents

1. [Section 1, Credential formats](credential-formats.md), what a credential
   carries, the three shapes it can take, which participant issues and verifies
   each one, and the Credential Rulebook that fixes the choice per credential
   type
2. [Section 2, Identifier](identifier.md), what names an entity, a holder, a
   credential type, an attribute, and a device, and why the holder uses one for
   now
3. [Section 3, Protocols and modes](protocols-and-modes.md), the protocol used
   for each interaction in the ecosystem, and what changes between the online
   path and the offline one
4. [Section 4, Artifacts exchanged](artifacts-exchanged.md), every artifact that
   crosses between two parties, who publishes it, who reads it, where it sits,
   and how long it lasts
