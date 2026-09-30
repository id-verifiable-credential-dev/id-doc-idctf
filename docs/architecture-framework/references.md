---
title: "References"
description: Every standard the ecosystem builds on, grouped by the job it does, with a link to the specification and what IDCTF uses it for.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §11; Glosarium dan Konvensi IDCTF, §B; Rincian Perangkat Lunak dan Deployment; Panduan mdoc -->

# References {#references}

Every format and every protocol in this ecosystem comes from a specification
somebody else wrote and maintains. This page lists them, grouped by the job each
one does, with a link to the document and one line on what IDCTF uses it for.

Definitions are not repeated here. Every name that belongs to IDCTF rather than
to a standard has one home page, and
[Where the ecosystem's own names are defined](#where-the-ecosystems-own-names-are-defined)
lists them at the end of this page. The standards that were considered and
turned down are in the
[technology map](data-model-and-protocols/index.md#technology-map). This page
names the source and points at the page that puts it to work.

## Exchange protocols {#exchange-protocols}

- [OpenID4VCI
  1.0](https://openid.net/specs/openid-4-verifiable-credential-issuance-1_0.html),
  issuance from an issuer to a wallet: the credential offer, the authorization
  step, the credential request, and the proof of the key the credential is
  bound to. It is the only issuance protocol in the ecosystem.
- [OpenID4VP
  1.0](https://openid.net/specs/openid-4-verifiable-presentations-1_0.html),
  online presentation from a wallet to a verifier. It also supplies DCQL, the
  query language a verifier states its request in, the `client_id` schemes
  `decentralized_identifier` and `x509_hash` that say how a verifier introduces
  itself, and the `verifier_info` parameter an attestation about the verifier
  travels in.
- [ISO/IEC 18013-5](https://www.iso.org/standard/69084.html), the mobile
  driving license standard. IDCTF takes three things from it: the mdoc
  credential format, the whole proximity path (device engagement over QR or
  Near Field Communication (NFC), the encrypted Bluetooth Low Energy (BLE)
  session, ReaderAuth and DeviceAuth over a shared SessionTranscript), and the
  certificate profiles in Annex B and Annex C.
- [ToIP TRQP
  v2.0](https://trustoverip.github.io/tswg-trust-registry-protocol/approved/),
  the Trust Registry Query Protocol (TRQP) behind `POST /authorization` and
  `POST /recognition`. Authority is asked for at the moment it matters rather
  than downloaded in advance.
- [OpenID Connect Core
  1.0](https://openid.net/specs/openid-connect-core-1_0.html), which carries a
  verifier's result into the Relying Party's own application. It is also how a
  Mobile Wallet authenticates a citizen through CONNECTIDN.
- [SAML
  2.0](https://docs.oasis-open.org/security/saml/v2.0/saml-core-2.0-os.pdf),
  the alternative to OpenID Connect for that same handoff to an application.
- [OpenID4VC High Assurance Interoperability
  Profile](https://openid.net/specs/openid4vc-high-assurance-interoperability-profile-1_0.html),
  a strict profile over OpenID4VCI and OpenID4VP. IDCTF reads it as a
  comparison and is not bound by it: the Governance Profile narrows the same
  optionality for itself.

Where these appear:
[Protocols and modes](data-model-and-protocols/protocols-and-modes.md).

## OAuth 2.0 and the endpoints it secures {#oauth-20-and-the-endpoints-it-secures}

- [RFC 6749](https://www.rfc-editor.org/rfc/rfc6749.html), the OAuth 2.0
  authorization framework OpenID4VCI is built on.
- [RFC 9126](https://www.rfc-editor.org/rfc/rfc9126.html), pushed authorization
  requests. Mandatory at issuance: the request goes to the issuer directly
  instead of through the browser.
- [RFC 7636](https://www.rfc-editor.org/rfc/rfc7636.html), PKCE, which binds an
  authorization code to the client that started the flow.
- [RFC 9449](https://www.rfc-editor.org/rfc/rfc9449.html), DPoP, which binds an
  access token to the key that asked for it, so a stolen token is useless in
  another pair of hands.
- [RFC 9396](https://www.rfc-editor.org/rfc/rfc9396.html), rich authorization
  requests, the structured authorization detail Issuer Core accepts.
- [RFC 9101](https://www.rfc-editor.org/rfc/rfc9101.html), the signed Request
  Object a verifier publishes behind a `request_uri`.
- [RFC 8414](https://www.rfc-editor.org/rfc/rfc8414.html), authorization server
  metadata, which is how an issuer's `.well-known` document and its JSON Web Key
  Set (JWKS) are found.
- [RFC 7807](https://www.rfc-editor.org/rfc/rfc7807.html), problem details, the
  error shape TRQP responses use.

## Credential formats and their signatures {#credential-formats-and-their-signatures}

- [RFC 9901](https://www.rfc-editor.org/rfc/rfc9901.html), selective disclosure
  for JSON Web Tokens, the salted-hash mechanism SD-JWT VC is built on.
- [IETF SD-JWT
  VC](https://datatracker.ietf.org/doc/draft-ietf-oauth-sd-jwt-vc/), the
  credential type over SD-JWT, format `dc+sd-jwt`, carrying `vct` and the `cnf`
  holder binding. It is the main online path, and it is still an
  Internet-Draft.
- [ISO/IEC 18013-5](https://www.iso.org/standard/69084.html) again for the mdoc
  side: Concise Binary Object Representation (CBOR) and CBOR Object Signing and
  Encryption (COSE), the Mobile Security Object (MSO) with its `valueDigests`
  and `DeviceKey`, and `docType` as the type identifier.
- [W3C VCDM 2.0](https://www.w3.org/TR/vc-data-model-2.0/), the data model
  carried as `ldp_vc`, kept for interoperability with JSON-LD systems.
- [VC Data Integrity](https://www.w3.org/TR/vc-data-integrity/) and [ECDSA
  Cryptosuites v1.0](https://www.w3.org/TR/vc-di-ecdsa/), the Elliptic Curve
  Digital Signature Algorithm (ECDSA) proof that secures `ldp_vc`, with
  `ecdsa-jcs-2019` as the cryptosuite.
- [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785.html), JSON
  canonicalization, which is what `ecdsa-jcs-2019` canonicalizes with instead
  of the Resource Description Framework (RDF).
- [VC-JOSE-COSE](https://www.w3.org/TR/vc-jose-cose/), securing W3C credentials
  with JSON Object Signing and Encryption (JOSE) and COSE, one of the final
  specifications the interoperability profile is drawn from.

Where these appear:
[Credential formats](data-model-and-protocols/credential-formats.md).

## Identifiers and keys {#identifiers-and-keys}

- [W3C DID 1.0](https://www.w3.org/TR/did-1.0/), the decentralized identifier
  (DID) data model and the shape of a DID Document.
- [W3C DID Resolution](https://www.w3.org/TR/did-resolution/), the resolution
  contract DID Service answers against.
- [did:webvh v1.0](https://identity.foundation/didwebvh/v1.0/), the DID method
  every issuer, verifier, and Wallet Provider is named by: an append-only
  `did.jsonl` log the entity signs itself, with a self-certifying identifier,
  pre-rotation, and a witness proof from Trust Authority on every entry. v1.0
  permits one cryptosuite for those proofs, `eddsa-jcs-2022`, which is the only
  place Ed25519 is used.
- [Data Integrity EdDSA Cryptosuites v1.0](https://www.w3.org/TR/vc-di-eddsa/),
  the definition of `eddsa-jcs-2022`, the proof on every `did:webvh` log entry
  and witness.
- [did:key](https://w3c-ccg.github.io/did-key-spec/), the method derived
  entirely from a public key. In this phase a holder has one per wallet
  installation, shared by every credential it holds.
- [RFC 7638](https://www.rfc-editor.org/rfc/rfc7638.html), JSON Web Key (JWK)
  thumbprints, which name a wallet or merchant device without ever transmitting
  the device key.

Where these appear: [Identifier](data-model-and-protocols/identifier.md).

## Encoding and signing {#encoding-and-signing}

- [RFC 7515](https://www.rfc-editor.org/rfc/rfc7515.html), JSON Web Signature
  (JWS), the signature
  over an SD-JWT VC, a Key Attestation, and a published trusted list.
- [RFC 7516](https://www.rfc-editor.org/rfc/rfc7516.html), JSON Web Encryption
  (JWE), which encrypts
  a presentation response returned through `direct_post.jwt`.
- [RFC 9052](https://www.rfc-editor.org/rfc/rfc9052.html), COSE, the signature
  over an mdoc: `COSE_Sign1` with the Document Signer Certificate in
  `x5chain`.
- [RFC 8949](https://www.rfc-editor.org/rfc/rfc8949.html), CBOR, the binary
  encoding everything on the mdoc side is serialized in.
- [RFC 9360](https://www.rfc-editor.org/rfc/rfc9360.html), the COSE header
  parameters for X.509 certificates. IDCTF departs from it on purpose and
  follows ISO/IEC 18013-5 clause 9.1.2.4, which puts `x5chain` in the
  unprotected header, because that is where existing mdoc implementations read
  it from.

## Certificates and revocation {#certificates-and-revocation}

- [RFC 5280](https://www.rfc-editor.org/rfc/rfc5280.html), the X.509 profile
  and the certificate revocation list (CRL) format, which is what withdraws a
  Document Signer Certificate, a Verifier Issuing CA, or a Verifier Device
  Certificate before it expires.
- [RFC 2986](https://www.rfc-editor.org/rfc/rfc2986.html), certification
  requests, the form a Module asks a certificate authority for a certificate
  in.
- [ISO/IEC 18013-5](https://www.iso.org/standard/69084.html) Annex B, the
  certificate profiles the ecosystem's own certificates follow, including the
  extended key usages `1.0.18013.5.1.2` for a Document Signer Certificate and
  `1.0.18013.5.1.6` for a reader.
- [RFC 6962](https://www.rfc-editor.org/rfc/rfc6962.html) and [RFC
  9162](https://www.rfc-editor.org/rfc/rfc9162.html), certificate transparency,
  the model behind the append-only log Trust Authority keeps of entity events.

## Trust lists and credential status {#trust-lists-and-credential-status}

- [ETSI TS 119
  602](https://www.etsi.org/deliver/etsi_ts/119600_119699/119602/01.01.01_60/ts_119602v010101p.pdf),
  the LoTE data model the trusted list is published as. IDCTF publishes the
  JSON encoding only.
- [ISO/IEC 18013-5](https://www.iso.org/standard/69084.html) Annex C, the
  Verified Issuer Certificate Authority List (VICAL), the signed list of
  certificate roots an mdoc reader accepts issuers from with no network at all.
- [IETF Token Status
  List](https://datatracker.ietf.org/doc/draft-ietf-oauth-status-list/), the
  compressed status list SD-JWT VC and mdoc point at. It is still an
  Internet-Draft.
- [W3C Bitstring Status List](https://www.w3.org/TR/vc-bitstring-status-list/),
  the equivalent for `ldp_vc`.

Where these appear:
[Artifacts exchanged](data-model-and-protocols/artifacts-exchanged.md).

## Device attestation and assurance {#device-attestation-and-assurance}

- [OpenID4VCI 1.0](https://openid.net/specs/openid-4-verifiable-credential-issuance-1_0.html)
  Appendix D.1, F.1, and F.3, the Key Attestation format a Wallet Backend
  Service issues and an issuer validates, including `attested_keys` and
  `key_storage`.
- [Play Integrity](https://developer.android.com/google/play/integrity) and
  [Android Key Attestation](https://developer.android.com/privacy-and-security/security-key-attestation),
  the platform evidence an Android wallet exchanges for a Key Attestation.
- [App Attest](https://developer.apple.com/documentation/devicecheck/establishing-your-app-s-integrity),
  the same evidence on iOS.
- [ISO/IEC 18045](https://www.iso.org/standard/18045), the evaluation
  methodology the `iso_18045_*` attack-resistance values in a Key Attestation
  are named after.
- [Implementing Regulation (EU) 2015/1502](https://eur-lex.europa.eu/eli/reg_impl/2015/1502/oj),
  the eIDAS source of the three assurance levels `low`, `substantial`, and
  `high`.

Where these appear:
[Key Attestation][key-attestation].

## Key storage interfaces {#key-storage-interfaces}

- [PKCS#11](https://docs.oasis-open.org/pkcs11/pkcs11-spec/v3.1/os/pkcs11-spec-v3.1-os.html),
  the interface a Key Manager driver, and Trust Authority, reach a hardware
  security module (HSM) through, so a signing key can be used without being
  exported.
- [KMIP](https://www.oasis-open.org/committees/kmip/), the Key Management
  Interoperability Protocol, which a Key Manager driver may use to reach a
  cloud key management service (KMS) or an HSM.

## Schema, display, and policy {#schema-display-and-policy}

- [JSON Schema](https://json-schema.org/), which validates a Credential
  Rulebook and the claims an institution's source system returns.
- [SD-JWT VC Type Metadata](https://datatracker.ietf.org/doc/draft-ietf-oauth-sd-jwt-vc/),
  the metadata a `vct` resolves to, published alongside a Rulebook.
- [Overlays Capture Architecture](https://oca.colossi.network/), the display
  overlay that says how a credential is rendered to a citizen.
- [Rego](https://www.openpolicyagent.org/docs/policy-language), the policy
  language a verifier evaluates its trust rules in.
- [ISO/IEC 29184](https://www.iso.org/standard/70331.html), online privacy
  notices and consent, the reference behind the consent receipt a verifier
  records with a verification.

## Frameworks read as comparison {#frameworks-read-as-comparison}

- [Architecture and Reference Framework](https://eu-digital-identity-wallet.github.io/eudi-doc-architecture-and-reference-framework/),
  the architecture behind the European Digital Identity (EUDI) Wallet. IDCTF
  takes its verifier-side vocabulary from it, Relying Party, Relying Party
  Instance, intermediary and intended use, so that the two ecosystems describe
  the same arrangement with the same words. It is a comparison and not a binding
  standard: where IDCTF diverges, in keeping one certificate instead of two and
  in leaving Relying Party Service out as a layer, the divergence is stated
  where it applies.

Where this appears:
[Role map](roles/role-map.md),
[RP Intermediary and merchant](roles/rp-intermediary-and-merchant.md).

## Document conventions {#document-conventions}

- [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119.html), the requirement
  keywords normative text is written with. Their capitalized form carries the
  obligation; the same words uncapitalized do not.

## Where the ecosystem's own names are defined {#where-the-ecosystems-own-names-are-defined}

Some names in this document belong to IDCTF rather than to a standard. Each has
one home page, and this list points at it:

- Roles and the institutions that hold them, and the Relying Party Instance each
  verifier role runs, in [Role map](roles/role-map.md).
- Services and Modules, in
  [Module Map](high-level-architecture/module-map.md).
- Components inside a Module, in
  [Components inside a Module](software-architecture/components-inside-a-module.md).
- Artifacts, including Authority Statement, Use Statement, Key Attestation,
  Verifier Device Certificate, and the certificate authorities, in
  [Artifacts exchanged](data-model-and-protocols/artifacts-exchanged.md).
- Identifier shapes, including the `id.idctf.<type>.<N>` namespace,
  in [Identifier](data-model-and-protocols/identifier.md).
- The Credential Rulebook and what it fixes per credential type, in
  [The Credential Rulebook][the-credential-rulebook].
