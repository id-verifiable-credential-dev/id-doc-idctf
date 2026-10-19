---
title: Technical Specifications
description: "IDCTF-TS: the normative specifications that bind implementations, written so that conformance can be tested."
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §0; tracks/0236, tracks/0241, tracks/0269, tracks/0270, tracks/0368 -->

# Technical Specifications {#technical-specifications}

<p class="ekdn-lead" markdown="span">
<code>IDCTF-TS-g-nn</code>. How the ecosystem works exactly, written so that an
implementation can be tested against it. Each specification is referred to by
its identifier and versioned on its own.
</p>

The Architecture Framework says what exists and why. A Technical
Specification says what an implementation has to do, in sentences an
Assessment Body can test one at a time. Every specification rests on the
[Architecture Framework](../architecture-framework/index.md) and repeats none
of its reasons: where a rule needs its why, the specification links the page
that holds it.

Each specification covers one thing a test can be written for: one family of
artifacts, with its format, its signature, how it is published and how a
reader checks it, or one interface, between two Modules or between a Module
and a system outside the ecosystem. The requirements in it are addressed to
named Modules, and a participant is compliant when it meets every
specification for the interfaces it runs and the artifacts it produces or
reads, as
[Common provisions](common-provisions.md) sets out.

## Specifications {#ts-specifications}

A specification is numbered by its group and its place in it,
`TS-<group>-<nn>`: 1 for Issuer Services, 2 for Wallet Services, 3 for
Verifier Services, 4 for Trust Infrastructure, and 5 for Artifacts, each
group counting from 01. A Service group holds the interfaces that Service's
Modules expose; the Artifacts group holds one specification per artifact
family, its format, signature, lifecycle, publication and reader rules.
Three specifications stand outside the groups because every other one rests on them: Common provisions as `TS-00`, Finding a signer's key from its DID as `TS-01`, and Publishing and reading the Governance Profile as `TS-02`. A title names the
task and the protocol or artifact it runs on. A specification marked
planned has a title and a scope and no page yet.

<figure markdown="1" class="ekdn-table">

| Identifier | Group | Specification | Covers | Status |
|---|---|---|---|---|
| `TS-00` | Common | [Common provisions](common-provisions.md) | The key words, the requirement identifiers, what conformance means, and how a specification is versioned | Drafting |
| `TS-01` | Common | [Finding a signer's key from its DID](finding-a-signers-key-from-its-did.md) | How every token signed under a `did:webvh` or a `did:key` names its key, how a reader finds it, and the issuer signature mechanism of SD-JWT VC | Drafting |
| `TS-02` | Common | [Publishing and reading the Governance Profile](publishing-and-reading-the-governance-profile.md) | The signed file every specification takes its numbers and algorithms from: its members and their types, its signature with the Governance Profile key, its fixed address, and how long a reader's copy counts | Drafting |
| `TS-1-01` | Issuer Services | [Issuing a credential via OpenID4VCI](issuing-a-credential-via-openid4vci.md) | The OpenID4VCI profile Issuer Core exposes and Mobile Wallet runs: the signed issuer metadata, the credential offer, both grants with PAR and DPoP, the nonce, the credential request and its answer, deferred issuance, the notification, and renewal | Drafting |
| `TS-2-01` | Wallet Services | [Enrolling a wallet installation and attesting its key](enrolling-a-wallet-installation-and-attesting-its-key.md) | The evidence each key of a wallet installation is checked against at enrollment, the record Wallet Backend Service keeps, what a request for a Key Attestation proves, and when an installation is revoked | Drafting |
| `TS-3-01` | Verifier Services | [Verifying a credential online via OpenID4VP](verifying-a-credential-online-via-openid4vp.md) | The OpenID4VP profile Verifier Core and Mobile Verifier expose and Mobile Wallet answers: the authorization request, the signed Request Object under `decentralized_identifier` or `x509_hash`, the checks on the request, the encrypted response, the relay for a merchant's check, and the errors | Drafting |
| `TS-3-02` | Verifier Services | [Verifying a credential in proximity via ISO/IEC 18013-5](verifying-a-credential-in-proximity-via-iso-iec-18013-5.md) | The ISO/IEC 18013-5 profile Mobile Verifier and Mobile Wallet run face to face: device engagement by QR code and NFC, the BLE transport, the encrypted session, the DeviceRequest and its ReaderAuth, the checks on the request, the response, and the end of the session | Drafting |
| `TS-4-01` | Trust Infrastructure | [Witnessing a log entry and serving its copy](witnessing-a-log-entry-and-serving-its-copy.md) | What DID Service checks before it witnesses an entry, the proof it returns, and the copy it serves | Drafting |
| `TS-4-02` | Trust Infrastructure | [Answering a permission query and serving the catalog](answering-a-permission-query-and-serving-the-catalog.md) | The Trust Registry Query Protocol as IDCTF runs it, the signed answer to a recognition query, the errors, the signed catalog of Rulebooks, and where each published artifact is fetched | Drafting |
| `TS-4-03` | Trust Infrastructure | [Onboarding an entity and registering its keys](onboarding-an-entity-and-registering-its-keys.md) | Trust Authority's portal, where an entity's staff register a body and manage its uses, permissions, incidents and record, and its entity endpoint, where the Key Manager registers keys and certificate requests | Drafting |
| `TS-5-01` | Artifacts | [Publishing and reading the trusted list](publishing-and-reading-the-trusted-list.md) | The profile of ETSI TS 119 602 the trusted list is published in, its signature, its publication, and how a reader checks its copy | Drafting |
| `TS-5-02` | Artifacts | [Publishing and resolving a did:webvh identifier](publishing-and-resolving-a-did-webvh-identifier.md) | The `did:webvh` profile every entity and Trust Authority use, the DID Document and its keys, rotation, publication, and how a reader resolves it | Drafting |
| `TS-5-03` | Artifacts | [Deriving a did:key and a device identifier](deriving-a-did-key-and-a-device-identifier.md) | How every `did:key` is formed and decoded, where each appears, the holder's identifier from the credential key, and the device thumbprint | Drafting |
| `TS-5-04` | Artifacts | [Issuing and validating the X.509 certificates and the VICAL](issuing-and-validating-the-x509-certificates-and-the-vical.md) | The certificate profiles of both roots, the Document Signer Certificate, the Verifier Issuing CA, the Verifier Device Certificate, the CRL, and the VICAL | Drafting |
| `TS-5-05` | Artifacts | [Answering with an Authority Statement](answering-with-an-authority-statement.md) | The statement Trust Registry answers a permission query with, the permission it names, its signature, and how a reader checks and caches it | Drafting |
| `TS-5-06` | Artifacts | [Registering and carrying a Use Statement](registering-and-carrying-a-use-statement.md) | The Use Statement of one registered use, its attributes, its signature, how a verifier carries it online and in proximity, and how a wallet checks it | Drafting |
| `TS-5-07` | Artifacts | [Issuing and carrying an Accreditation Credential](issuing-and-carrying-an-accreditation-credential.md) | The credential an entity carries as evidence of its accreditation, what it names, and why the trusted list still decides | Drafting |
| `TS-5-08` | Artifacts | [Issuing and reading a Key Attestation](issuing-and-reading-a-key-attestation.md) | The attestation Wallet Backend Service issues for a wallet installation's credential key, how it is carried, and what Issuer Core checks | Drafting |
| `TS-5-09` | Artifacts | [Publishing and reading a status list](publishing-and-reading-a-status-list.md) | The Token Status List and the Bitstring Status List an issuer publishes, and the Use Statement and accreditation status lists Trust Registry publishes | Drafting |
| `TS-5-10` | Artifacts | [Issuing a credential in SD-JWT VC, mdoc, and `ldp_vc`](issuing-a-credential-in-sd-jwt-vc-mdoc-and-ldp-vc.md) | The SD-JWT VC, mdoc and `ldp_vc` profiles a credential is issued in, the holder binding and status pointer of each, and the checks a reader runs | Drafting |
| `TS-5-11` | Artifacts | [Building and verifying a presentation](building-and-verifying-a-presentation.md) | What a wallet discloses in one exchange, the proof that it holds the credential key, and how both are bound to the request | Drafting |

</figure>

## Contents {#ts-contents}

1. [Common provisions](common-provisions.md)
2. [Finding a signer's key from its DID](finding-a-signers-key-from-its-did.md)
3. [Publishing and reading the Governance Profile](publishing-and-reading-the-governance-profile.md)
4. [Issuing a credential via OpenID4VCI](issuing-a-credential-via-openid4vci.md)
5. [Enrolling a wallet installation and attesting its key](enrolling-a-wallet-installation-and-attesting-its-key.md)
6. [Verifying a credential online via OpenID4VP](verifying-a-credential-online-via-openid4vp.md)
7. [Verifying a credential in proximity via ISO/IEC 18013-5](verifying-a-credential-in-proximity-via-iso-iec-18013-5.md)
8. [Witnessing a log entry and serving its copy](witnessing-a-log-entry-and-serving-its-copy.md)
9. [Answering a permission query and serving the catalog](answering-a-permission-query-and-serving-the-catalog.md)
10. [Onboarding an entity and registering its keys](onboarding-an-entity-and-registering-its-keys.md)
11. [Publishing and reading the trusted list](publishing-and-reading-the-trusted-list.md)
12. [Publishing and resolving a did:webvh identifier](publishing-and-resolving-a-did-webvh-identifier.md)
13. [Deriving a did:key and a device identifier](deriving-a-did-key-and-a-device-identifier.md)
14. [Issuing and validating the X.509 certificates and the VICAL](issuing-and-validating-the-x509-certificates-and-the-vical.md)
15. [Answering with an Authority Statement](answering-with-an-authority-statement.md)
16. [Registering and carrying a Use Statement](registering-and-carrying-a-use-statement.md)
17. [Issuing and carrying an Accreditation Credential](issuing-and-carrying-an-accreditation-credential.md)
18. [Issuing and reading a Key Attestation](issuing-and-reading-a-key-attestation.md)
19. [Publishing and reading a status list](publishing-and-reading-a-status-list.md)
20. [Issuing a credential in SD-JWT VC, mdoc, and `ldp_vc`](issuing-a-credential-in-sd-jwt-vc-mdoc-and-ldp-vc.md)
21. [Building and verifying a presentation](building-and-verifying-a-presentation.md)
