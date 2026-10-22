---
title: "References"
description: Every standard and law the five IDCTF documents build on, split into normative and informative references, with a link to each and what IDCTF uses it for.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §11; Glosarium dan Konvensi IDCTF, §B; Rincian Perangkat Lunak dan Deployment; Panduan mdoc; tracks/0208, tracks/0211, tracks/0213, tracks/0215; normative and informative split after OpenID4VCI 1.0 §16 and §17; version sweep 17 October 2026 -->

# References {#references}

Every format and every protocol in IDCTF comes from a specification somebody
else wrote and maintains, for all five IDCTF documents. Each entry carries a
link to the document, one line on what IDCTF uses it for, and a label in square
brackets, and the entries in each section are in alphabetical order of that
label. Indonesian laws and regulations run in
order of enactment instead, because a reader looking one up knows its year.

Each entry names, in brackets after its title, the version IDCTF is written
against and how mature that version is, and its link points at that version.
A draft is pinned to one revision, so the link keeps showing that revision after
newer ones are published. A law has no version; its entry names the amendments
in force instead.

A normative reference is one an implementation of IDCTF cannot do without:
the protocols, formats, and profiles IDCTF is built from, and the Indonesian
law it operates under. An informative reference is cited for background: a
model IDCTF follows, a scale it maps onto, a profile it is not bound by, or a
specification it departs from on purpose.

Definitions are not repeated here. The standards that were considered and
turned down are in the [technology map][technology-map].

## Normative references {#normative-references}

- [](){ #ref-android-key-attestation } **[AndroidKeyAttestation]**
  [Android Key Attestation](https://source.android.com/docs/security/features/keystore/attestation)
  (vendor documentation, no version, read on 17 October 2026), platform evidence
  an Android wallet exchanges for a Key Attestation, together with Play
  Integrity.
- [](){ #ref-app-attest } **[AppAttest]**
  [App Attest](https://developer.apple.com/documentation/devicecheck/establishing-your-app-s-integrity)
  (vendor documentation, no version, read on 17 October 2026), the same evidence on iOS.
- [](){ #ref-bitstring-status-list } **[BitstringStatusList]**
  [W3C Bitstring Status List](https://www.w3.org/TR/2025/REC-vc-bitstring-status-list-20250515/)
  (W3C Recommendation, 15 May 2025), the status list for `ldp_vc`, the
  equivalent of the IETF Token Status List.
- [](){ #ref-cid } **[CID]**
  [W3C Controlled Identifiers v1.0](https://www.w3.org/TR/2025/REC-cid-1.0-20250515/)
  (W3C Recommendation, 15 May 2025), the
  definition of `Multikey`, the verification method type that `issuance-jose`
  and `status-list` take in an issuer's Decentralized Identifier (DID)
  Document.
- [](){ #ref-did-core } **[DID-Core]**
  [W3C DID 1.0](https://www.w3.org/TR/2022/REC-did-core-20220719/) (W3C
  Recommendation, 19 July 2022), the DID data model and the
  shape of a DID Document.
- [](){ #ref-did-key } **[DID-Key]**
  [did:key](https://w3c-ccg.github.io/did-key-spec/) (W3C Credentials
  Community Group draft v0.9, pinned at commit
  [2cc490c](https://github.com/w3c-ccg/did-key-spec/blob/2cc490c38c5aacf58497a87fc0cf8794668bf716/index.html)
  of 2 November 2025), the method derived
  entirely from a public key. It is a draft IDCTF admits because the holder,
  the witness, and the trusted list are named by it. A holder has one per wallet installation, shared
  by every credential it holds.
- [](){ #ref-did-webvh } **[DID-WebVH]**
  [did:webvh v1.0](https://identity.foundation/didwebvh/v1.0/) (DIF Ratified
  Specification, pinned at commit
  [91f3cba](https://github.com/decentralized-identity/didwebvh/tree/91f3cba7b09f7552e9a19ac447ee91b66057f5d1/spec-v1.0)
  of 23 September 2026), the DID method
  every issuer, Relying Party, and Wallet Provider is named by: an append-only
  `did.jsonl` log the entity signs itself, with a self-certifying identifier,
  pre-rotation, and a witness proof from DID Service on every entry. v1.0
  permits one cryptosuite for those proofs, `eddsa-jcs-2022`, which is the only
  place Ed25519 is used.
- [](){ #ref-etsi-ts-119602 } **[ETSI.TS.119602]**
  [ETSI TS 119 602](https://www.etsi.org/deliver/etsi_ts/119600_119699/119602/01.01.01_60/ts_119602v010101p.pdf)
  (V1.1.1, 2025-11), the List of Trusted Entities (LoTE) data model the
  trusted list is published as. IDCTF publishes the JSON encoding only.
- [](){ #ref-eucc } **[EUCC]**
  [Implementing Regulation (EU) 2024/482](https://eur-lex.europa.eu/eli/reg_impl/2024/482/oj)
  (adopted 31 January 2024), the European Union cybersecurity
  certification scheme on Common Criteria, one of the schemes a `keyStorage`
  value in the Governance Profile names for a certified secure element.
- [](){ #ref-fips-140-3 } **[FIPS.140-3]**
  [FIPS 140-3](https://csrc.nist.gov/pubs/fips/140-3/final) (final, 22 March
  2019), the validation
  standard for cryptographic modules. The hardware security module (HSM) that
  holds Issuer Root CA is validated to its Level 3.
- [](){ #ref-i-d-ietf-oauth-sd-jwt-vc } **[I-D.ietf-oauth-sd-jwt-vc]**
  [IETF SD-JWT VC](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-sd-jwt-vc-13)
  (draft-ietf-oauth-sd-jwt-vc-13, 6 November 2025, Internet-Draft), the
  credential type over selective disclosure for JSON Web Tokens (SD-JWT), format
  `dc+sd-jwt`, carrying `vct` and the `cnf` holder binding. It is the main
  online path. The same
  document defines SD-JWT VC Type Metadata, the metadata a `vct` resolves to,
  published alongside a Rulebook, and the display metadata that says how a
  credential is rendered to a citizen.
- [](){ #ref-i-d-ietf-oauth-status-list } **[I-D.ietf-oauth-status-list]**
  [IETF Token Status List](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-status-list-14)
  (draft-ietf-oauth-status-list-14, 10 December 2025, Internet-Draft), the
  compressed status list SD-JWT-based Verifiable Credentials (SD-JWT VC) and
  mdoc point at.
- [](){ #ref-iso-15408-3 } **[ISO.15408-3]**
  [ISO/IEC 15408-3](https://www.iso.org/standard/72906.html) (ISO/IEC
  15408-3:2022, fourth edition), the Common Criteria assurance components, among
  them `AVA_VAN.5`, the vulnerability analysis against an attacker of high
  attack potential that a certification has to include before a Key Attestation
  reports `iso_18045_high`.
- [](){ #ref-iso-17021-1 } **[ISO.17021-1]**
  [ISO/IEC 17021-1](https://www.iso.org/standard/61651.html) (ISO/IEC
  17021-1:2015, first edition), conformity assessment, requirements for bodies
  providing audit and certification of management systems, Part 1, the
  accreditation an Assessment Body may hold for the security audit scope.
- [](){ #ref-iso-17025 } **[ISO.17025]**
  [ISO/IEC 17025](https://www.iso.org/standard/66912.html) (ISO/IEC
  17025:2017, third edition), general requirements for the competence of testing
  and calibration laboratories, the accreditation an Assessment Body holds for
  conformance testing, adopted in Indonesia as SNI ISO/IEC 17025:2017.
- [](){ #ref-iso-18013-5 } **[ISO.18013-5]**
  [ISO/IEC 18013-5](https://www.iso.org/standard/69084.html)
  (ISO/IEC 18013-5:2021, first edition), the mobile driving license standard.
  IDCTF takes four things from it:
    - The mdoc credential format: Concise Binary Object Representation (CBOR)
      and CBOR Object Signing and Encryption (COSE), the Mobile Security
      Object (MSO) with its `valueDigests` and `DeviceKey`, and `docType` as
      the type identifier.
    - The whole proximity path: device engagement over QR or Near Field
      Communication (NFC), the encrypted Bluetooth Low Energy (BLE) session,
      and ReaderAuth and DeviceAuth over a shared SessionTranscript.
    - The certificate profiles in Annex B, which the ecosystem's own
      certificates follow, including the extended key usages `1.0.18013.5.1.2`
      for a Document Signer Certificate and `1.0.18013.5.1.6` for a reader.
    - The Verified Issuer Certificate Authority List (VICAL) in Annex C, the
      signed list of certificate roots an mdoc reader accepts issuers from
      with no network.
- [](){ #ref-iso-18045 } **[ISO.18045]**
  [ISO/IEC 18045](https://www.iso.org/standard/72889.html) (ISO/IEC
  18045:2022, third edition), the evaluation
  methodology the `iso_18045_*` attack-resistance values in a Key Attestation
  are named after.
- [](){ #ref-json-ld } **[JSON-LD]**
  [JSON-LD 1.1](https://www.w3.org/TR/2020/REC-json-ld11-20200716/) (W3C
  Recommendation, 16 July 2020), the syntax an `ldp_vc`
  credential is written in, which a verifier expands before it canonicalizes.
- [](){ #ref-json-schema } **[JSON-Schema]**
  [JSON Schema](https://json-schema.org/draft/2020-12) (Draft 2020-12, published
  as Internet-Drafts on 16 June 2022), which validates a Credential Rulebook and
  the claims an institution's source system returns.
- [](){ #ref-openid-core } **[OpenID.Core]**
  [OpenID Connect Core
  1.0](https://openid.net/specs/openid-connect-core-1_0.html) (Final,
  incorporating errata set 2, 15 December 2023), which carries a
  verifier's result into the Relying Party's business system. It is also how a
  Mobile Wallet authenticates a citizen at its identity provider.
- [](){ #ref-openid4vci } **[OpenID4VCI]**
  [OpenID for Verifiable Credential Issuance (OpenID4VCI)
  1.0](https://openid.net/specs/openid-4-verifiable-credential-issuance-1_0.html)
  (Final, 16 September 2025), issuance from an issuer to a wallet: the credential offer, the authorization
  step, the credential request, and the proof of the key the credential is
  bound to. It is the only issuance protocol in the ecosystem. Its Appendix
  D.1, F.1, and F.3 define the Key Attestation format a Wallet Backend Service
  issues and an issuer validates, including `attested_keys` and `key_storage`.
- [](){ #ref-openid4vp } **[OpenID4VP]**
  [OpenID for Verifiable Presentations (OpenID4VP)
  1.0](https://openid.net/specs/openid-4-verifiable-presentations-1_0.html)
  (Final, 9 July 2025), online presentation from a wallet to a verifier. It also supplies DCQL, the
  query language a verifier states its request in, the Client Identifier Prefixes
  `decentralized_identifier` and `x509_hash` that say how a verifier introduces
  itself, and the `verifier_info` parameter an attestation about the verifier
  travels in.
- [](){ #ref-permendagri-72-2022 } **[Permendagri.72-2022]**
  [Permendagri No. 72 Tahun 2022](https://peraturan.bpk.go.id/Details/247759)
  tentang Standar dan Spesifikasi Perangkat Keras, Perangkat Lunak, dan Blangko
  Kartu Tanda Penduduk Elektronik serta Penyelenggaraan Identitas Kependudukan
  Digital, the ministerial regulation behind *Digital Population Identity
  (IKD)*, enacted 1 April 2022 and in force since 13 April 2022.
- [](){ #ref-pkcs11 } **[PKCS11]**
  [PKCS#11](https://docs.oasis-open.org/pkcs11/pkcs11-spec/v3.1/os/pkcs11-spec-v3.1-os.html)
  (v3.1, OASIS Standard, 23 July 2023), the interface a Key Manager driver, and Trust Authority, reach an HSM
  through, so a signing key can be used without being exported.
- [](){ #ref-play-integrity } **[PlayIntegrity]**
  [Play Integrity](https://developer.android.com/google/play/integrity) (vendor
  documentation, no version, read on 17 October 2026), the other half of the
  platform evidence an Android wallet exchanges for a Key Attestation.
- [](){ #ref-pp-71-2019 } **[PP.71-2019]**
  [PP No. 71 Tahun 2019](https://peraturan.bpk.go.id/Details/122030/pp-no-71-tahun-2019)
  tentang Penyelenggaraan Sistem dan Transaksi Elektronik, the government
  regulation on electronic systems and transactions, the source of *Electronic
  Certificate*, *Electronic Certification Provider (PSrE)*, and *Electronic
  System Provider (PSE)*. Enacted 4 October 2019 and in force since 10 October
  2019.
- [](){ #ref-pp-42-2020 } **[PP.42-2020]**
  [PP No. 42 Tahun 2020](https://peraturan.bpk.go.id/Details/142301/pp-no-42-tahun-2020)
  tentang Aksesibilitas terhadap Permukiman, Pelayanan Publik, dan Pelindungan
  dari Bencana bagi Penyandang Disabilitas, the government regulation whose
  Pasal 17 obliges a public service that uses technology to make it accessible
  to persons with disabilities.
- [](){ #ref-rdfc-1-0 } **[RDFC-1.0]**
  [RDFC-1.0](https://www.w3.org/TR/2024/REC-rdf-canon-20240521/) (W3C
  Recommendation, 21 May 2024), the Resource Description
  Framework (RDF) Dataset Canonicalization that `ecdsa-rdfc-2019` signs over,
  and the guard against poison graphs it requires.
- [](){ #ref-rfc2119 } **[RFC2119]**
  [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119.html) (March 1997), the requirement key
  words, written in capitals, that the normative pages of IDCTF are
  interpreted by.
- [](){ #ref-rfc2397 } **[RFC2397]**
  [RFC 2397](https://www.rfc-editor.org/rfc/rfc2397.html) (August 1998), the `data:` URI
  scheme, which carries a base64 attribute value in an SD-JWT VC with its media
  type in front.
- [](){ #ref-rfc2986 } **[RFC2986]**
  [RFC 2986](https://www.rfc-editor.org/rfc/rfc2986.html) (November 2000), certification
  requests, the form a Module asks a certificate authority for a certificate
  in.
- [](){ #ref-rfc3339 } **[RFC3339]**
  [RFC 3339](https://www.rfc-editor.org/rfc/rfc3339.html) (July 2002), the
  date-time and, in its Appendix A, the duration the Governance Profile writes
  its times and periods in.
- [](){ #ref-rfc4648 } **[RFC4648]**
  [RFC 4648](https://www.rfc-editor.org/rfc/rfc4648.html) (October 2006), the base64 encoding
  a Credential Rulebook schema marks a binary attribute value with.
- [](){ #ref-rfc5280 } **[RFC5280]**
  [RFC 5280](https://www.rfc-editor.org/rfc/rfc5280.html) (May 2008), the X.509
  profile and the certificate revocation list (CRL) format, which withdraws a
  Document Signer Certificate, a Verifier Issuing CA, or a
  Verifier Device Certificate before it expires.
- [](){ #ref-rfc5612 } **[RFC5612]**
  [RFC 5612](https://www.rfc-editor.org/rfc/rfc5612.html) (August 2009), the enterprise
  number reserved for documentation, `32473`, the arc the `ReaderAuthRole`
  extension stands under, which carries no claim on any registry.
- [](){ #ref-rfc6749 } **[RFC6749]**
  [RFC 6749](https://www.rfc-editor.org/rfc/rfc6749.html) (October 2012), the OAuth 2.0
  authorization framework OpenID4VCI is built on.
- [](){ #ref-rfc7515 } **[RFC7515]**
  [RFC 7515](https://www.rfc-editor.org/rfc/rfc7515.html) (May 2015), JSON Web Signature
  (JWS), the signature over an SD-JWT VC, a Key Attestation, and a published
  trusted list.
- [](){ #ref-rfc7516 } **[RFC7516]**
  [RFC 7516](https://www.rfc-editor.org/rfc/rfc7516.html) (May 2015), JSON Web Encryption
  (JWE), which encrypts a presentation response returned through
  `direct_post.jwt`.
- [](){ #ref-rfc7518 } **[RFC7518]**
  [RFC 7518](https://www.rfc-editor.org/rfc/rfc7518.html) (May 2015), JSON Web
  Algorithms (JWA), which defines `HS256`, the message authentication code that binds an entity's first
  log entry to its registration.
- [](){ #ref-rfc7519 } **[RFC7519]**
  [RFC 7519](https://www.rfc-editor.org/rfc/rfc7519.html) (May 2015), JSON Web
  Token (JWT), the claims set and the validation rules a Use Statement, an
  Authority Statement, and a Key Attestation are read by.
- [](){ #ref-rfc7636 } **[RFC7636]**
  [RFC 7636](https://www.rfc-editor.org/rfc/rfc7636.html) (September 2015), PKCE, which binds an
  authorization code to the client that started the flow.
- [](){ #ref-rfc7638 } **[RFC7638]**
  [RFC 7638](https://www.rfc-editor.org/rfc/rfc7638.html) (September 2015), JSON Web Key (JWK)
  thumbprints, which name a wallet or merchant device without ever transmitting
  the device key.
- [](){ #ref-rfc8174 } **[RFC8174]**
  [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174.html) (May 2017), which updates
  RFC 2119 so that only the capitalized key words carry its meaning.
- [](){ #ref-rfc8414 } **[RFC8414]**
  [RFC 8414](https://www.rfc-editor.org/rfc/rfc8414.html) (June 2018), authorization server
  metadata, which names where an authorization server's `.well-known` document
  and its JSON Web Key Set (JWKS) are found.
- [](){ #ref-rfc8446 } **[RFC8446]**
  [RFC 8446](https://www.rfc-editor.org/rfc/rfc8446.html) (August 2018), TLS 1.3,
  the transport every interface a Technical Specification binds is served over.
- [](){ #ref-rfc8555 } **[RFC8555]**
  [RFC 8555](https://www.rfc-editor.org/rfc/rfc8555.html) (March 2019), Automatic
  Certificate Management Environment (ACME), whose signed request, `Replay-Nonce`
  header, and External Account Binding the entity endpoint of Trust Authority
  follows.
- [](){ #ref-rfc8785 } **[RFC8785]**
  [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785.html) (June 2020), JSON
  canonicalization, which `eddsa-jcs-2022` canonicalizes a `did:webvh` log
  entry with.
- [](){ #ref-rfc8943 } **[RFC8943]**
  [RFC 8943](https://www.rfc-editor.org/rfc/rfc8943.html) (November 2020), the CBOR tag 1004
  for a date without a time, which an mdoc data element declared as a date
  carries.
- [](){ #ref-rfc8949 } **[RFC8949]**
  [RFC 8949](https://www.rfc-editor.org/rfc/rfc8949.html) (December 2020), CBOR, the binary
  encoding everything on the mdoc side is serialized in.
- [](){ #ref-rfc9052 } **[RFC9052]**
  [RFC 9052](https://www.rfc-editor.org/rfc/rfc9052.html) (August 2022), COSE, the signature
  over an mdoc: `COSE_Sign1`.
- [](){ #ref-rfc9053 } **[RFC9053]**
  [RFC 9053](https://www.rfc-editor.org/rfc/rfc9053.html) (August 2022), the
  initial COSE algorithms, which define `ES256` as the value `-7`, the
  algorithm of every COSE signature in IDCTF: the mdoc's IssuerAuth,
  DeviceAuth, and ReaderAuth, and the CWT form of a status list.
- [](){ #ref-rfc9101 } **[RFC9101]**
  [RFC 9101](https://www.rfc-editor.org/rfc/rfc9101.html) (August 2021), the signed Request
  Object a verifier publishes behind a `request_uri`.
- [](){ #ref-rfc9126 } **[RFC9126]**
  [RFC 9126](https://www.rfc-editor.org/rfc/rfc9126.html) (September 2021), pushed authorization
  requests. Mandatory at issuance: the request goes to the issuer directly
  instead of through the browser.
- [](){ #ref-rfc9207 } **[RFC9207]**
  [RFC 9207](https://www.rfc-editor.org/rfc/rfc9207.html) (March 2022), the `iss`
  parameter of an authorization response, which tells a wallet that talks to
  many issuers which one sent the code.
- [](){ #ref-rfc9360 } **[RFC9360]**
  [RFC 9360](https://www.rfc-editor.org/rfc/rfc9360.html) (February 2023), the COSE header
  parameters for X.509 certificates, including `x5chain`, which carries the
  Document Signer Certificate in an mdoc. ISO/IEC 18013-5:2021 clause 9.1.2.4
  puts `x5chain` in the unprotected header. RFC 9360 permits that when the
  certificate authority required proof of possession of the subject's key. The
  certification request a Document Signer Certificate is issued from gives that
  proof.
- [](){ #ref-rfc9396 } **[RFC9396]**
  [RFC 9396](https://www.rfc-editor.org/rfc/rfc9396.html) (May 2023), rich authorization
  requests, the structured authorization detail Issuer Core accepts.
- [](){ #ref-rfc9449 } **[RFC9449]**
  [RFC 9449](https://www.rfc-editor.org/rfc/rfc9449.html) (September 2023), DPoP, which binds an
  access token to the key that asked for it, so a stolen token is useless in
  another pair of hands.
- [](){ #ref-rfc9457 } **[RFC9457]**
  [RFC 9457](https://www.rfc-editor.org/rfc/rfc9457.html) (July 2023), problem
  details for HTTP APIs, the error shape responses of the Trust Registry Query
  Protocol (TRQP) use.
- [](){ #ref-rfc9901 } **[RFC9901]**
  [RFC 9901](https://www.rfc-editor.org/rfc/rfc9901.html) (November 2025), SD-JWT, the
  salted-hash mechanism SD-JWT VC is built on.
- [](){ #ref-sogis-mra } **[SOGIS.MRA]**
  [SOG-IS MRA](https://www.sogis.eu/uk/mra_en.html)
  (Version 3.0, 8 January 2010), the Senior Officials Group Information
  Systems Security Mutual Recognition Agreement, under which the participating
  states recognize one another's Common Criteria certificates. It is one of
  the schemes a `keyStorage` value in the Governance Profile names.
- [](){ #ref-sri } **[SRI]**
  [W3C Subresource Integrity](https://www.w3.org/TR/2016/REC-SRI-20160623/)
  (Level 1, W3C Recommendation, 23 June 2016), the digest form a
  Credential Rulebook pins its JSON-LD context with, the same form
  `credentialSchema` carries in `digestSRI`.
- [](){ #ref-svg2 } **[SVG2]**
  [Scalable Vector Graphics (SVG) 2](https://www.w3.org/TR/2026/CR-SVG2-20261006/) (W3C Candidate
  Recommendation Snapshot, 6 October 2026), the image
  format of the card template SD-JWT VC Type Metadata carries in
  `rendering.svg_templates`.
- [](){ #ref-trqp } **[TRQP]**
  [ToIP TRQP v2.0](https://doi.org/10.5281/zenodo.18789010) (ToIP Approved
  Deliverable, April 2026), the TRQP behind `POST /authorization` and
  `POST /recognition`. Authority is asked for at the moment it matters rather
  than downloaded in advance.
- [](){ #ref-uu-11-2008 } **[UU.11-2008]**
  [UU No. 11 Tahun 2008](https://peraturan.bpk.go.id/Details/37589/uu-no-11-tahun-2008)
  tentang Informasi dan Transaksi Elektronik, as amended by
  [UU No. 19 Tahun 2016](https://peraturan.bpk.go.id/Details/37582/uu-no-19-tahun-2016)
  and, last, by
  [UU No. 1 Tahun 2024](https://peraturan.bpk.go.id/Details/274494/uu-no-1-tahun-2024),
  the law on electronic information and transactions, the source of
  *Electronic Information* and *Electronic Document*.
- [](){ #ref-uu-24-2013 } **[UU.24-2013]**
  [UU No. 24 Tahun 2013](https://peraturan.bpk.go.id/Details/38985/uu-no-24-tahun-2013)
  tentang Perubahan atas Undang-Undang Nomor 23 Tahun 2006 tentang Administrasi
  Kependudukan, the population administration law, the source of *Population
  Document* and *Population Identification Number (NIK)*.
- [](){ #ref-uu-20-2014 } **[UU.20-2014]**
  [UU No. 20 Tahun 2014](https://peraturan.bpk.go.id/Details/38663/uu-no-20-tahun-2014)
  tentang Standardisasi dan Penilaian Kesesuaian, the law under which Komite
  Akreditasi Nasional (KAN) accredits a conformity assessment organization;
  the Governance Framework uses that accreditation as the condition for
  recognizing an Assessment Body.
- [](){ #ref-uu-30-2014 } **[UU.30-2014]**
  [UU No. 30 Tahun 2014](https://peraturan.bpk.go.id/Details/38695/uu-no-30-tahun-2014)
  tentang Administrasi Pemerintahan, as amended by
  [UU No. 6 Tahun 2023](https://peraturan.bpk.go.id/Details/246523),
  the government administration law, the source of the objection (keberatan)
  and administrative appeal (banding) a body may lodge against a decision of
  the Root Authority.
- [](){ #ref-uu-8-2016 } **[UU.8-2016]**
  [UU No. 8 Tahun 2016](https://peraturan.bpk.go.id/Details/37251/uu-no-8-tahun-2016)
  tentang Penyandang Disabilitas, the law on persons with disabilities, which
  obliges state administration and public services to provide accessibility
  and reasonable accommodation.
- [](){ #ref-uu-27-2022 } **[UU.27-2022]**
  [UU No. 27 Tahun 2022](https://peraturan.bpk.go.id/Details/229798/uu-no-27-tahun-2022)
  tentang Pelindungan Data Pribadi, the personal data protection law, the
  source of *Personal Data*, *Personal Data Controller*, and *Personal Data
  Processor*. In force since 17 October 2022.
- [](){ #ref-vc-data-2-0 } **[VC-DATA-2.0]**
  [W3C VCDM 2.0](https://www.w3.org/TR/2025/REC-vc-data-model-2.0-20250515/)
  (W3C Recommendation, 15 May 2025), the data model
  carried as `ldp_vc`, kept for interoperability with JSON-LD systems.
- [](){ #ref-vc-data-integrity } **[VC-Data-Integrity]**
  [VC Data Integrity](https://www.w3.org/TR/2025/REC-vc-data-integrity-20250515/)
  (W3C Recommendation, 15 May 2025), the proof
  framework the ECDSA cryptosuite plugs into to secure `ldp_vc`.
- [](){ #ref-vc-di-ecdsa } **[VC-DI-ECDSA]**
  [ECDSA Cryptosuites v1.0](https://www.w3.org/TR/2025/REC-vc-di-ecdsa-20250515/)
  (W3C Recommendation, 15 May 2025), the Elliptic
  Curve Digital Signature Algorithm (ECDSA) proof that secures `ldp_vc`, with
  `ecdsa-rdfc-2019` as the cryptosuite.
- [](){ #ref-vc-di-eddsa } **[VC-DI-EdDSA]**
  [Data Integrity EdDSA Cryptosuites v1.0](https://www.w3.org/TR/2025/REC-vc-di-eddsa-20250515/)
  (W3C Recommendation, 15 May 2025), the definition of `eddsa-jcs-2022`, the
  proof on every `did:webvh` log entry and witness.
- [](){ #ref-vc-json-schema } **[VC-JSON-Schema]**
  [W3C VC JSON Schema](https://www.w3.org/TR/2025/CRD-vc-json-schema-20250204/)
  (W3C Candidate Recommendation Draft, 4 February 2025), the
  `credentialSchema` entry of type `JsonSchema` an `ldp_vc` credential names
  its schema in, with a `digestSRI`.
- [](){ #ref-wcag-2-2 } **[WCAG-2.2]**
  [Web Content Accessibility Guidelines (WCAG) 2.2](https://www.w3.org/TR/2024/REC-WCAG22-20241212/)
  (W3C Recommendation, 12 December 2024), the accessibility standard every
  surface a person uses in IDCTF is audited against, at Level AA. It is also
  published as ISO/IEC 40500:2025.

## Informative references {#informative-references}

- [](){ #ref-did-resolution } **[DID-Resolution]**
  [W3C DID Resolution](https://www.w3.org/TR/2026/CRD-did-resolution-1.0-20261001/)
  (W3C Candidate Recommendation Draft, 1 October 2026), the generic resolution
  contract. IDCTF does not resolve through it: a `did:webvh` is resolved by the
  Read operation of its method and a `did:key` is decoded locally.
- [](){ #ref-etsi-en-319411-1 } **[ETSI.EN.319411-1]**
  [ETSI EN 319
  411-1](https://www.etsi.org/deliver/etsi_en/319400_319499/31941101/01.04.01_60/en_31941101v010401p.pdf)
  (V1.4.1, 2023-10), the policy requirements for a trust service provider
  issuing certificates. Its REV-6.2.4-03A limits the time between a
  revocation request and the revocation status reaching every reader to 24
  hours, the limit IDCTF takes for placing a revoked key's certificate on a
  certificate revocation list.
- [](){ #ref-etsi-ts-119182-1 } **[ETSI.TS.119182-1]**
  [ETSI TS 119
  182-1](https://www.etsi.org/deliver/etsi_ts/119100_119199/11918201/01.02.01_60/ts_11918201v010201p.pdf)
  (V1.2.1, 2024-07), JAdES digital signatures, the signature ETSI TS 119 602 asks for on a JSON
  List of Trusted Entities, and from which the trusted list specification
  departs.
- [](){ #ref-eu-2015-1502 } **[EU.2015-1502]**
  [Implementing Regulation (EU) 2015/1502](https://eur-lex.europa.eu/eli/reg_impl/2015/1502/oj)
  (of 8 September 2015, as originally published), the eIDAS source of the three
  assurance levels `low`, `substantial`, and `high`.
- [](){ #ref-iso-27560 } **[ISO.27560]**
  [ISO/IEC TS 27560](https://www.iso.org/standard/80392.html) (ISO/IEC TS
  27560:2023, Technical Specification), the consent record information
  structure, the model behind the consent receipt a verifier records with a
  verification. It supplements ISO/IEC 29184 and is based on the consent receipt
  specification of the Kantara Initiative.
- [](){ #ref-iso-29184 } **[ISO.29184]**
  [ISO/IEC 29184](https://www.iso.org/standard/70331.html) (ISO/IEC
  29184:2020, first edition), online privacy notices and how consent is asked
  for, the consent a consent receipt records.
- [](){ #ref-kmip } **[KMIP]**
  [KMIP](https://docs.oasis-open.org/kmip/kmip-spec/v2.1/os/kmip-spec-v2.1-os.html)
  (KMIP 2.1, OASIS Standard, 14 December 2020), the Key Management
  Interoperability Protocol, which a Key Manager driver may use to reach a
  cloud key management service (KMS) or an HSM.
- [](){ #ref-openid4vc-haip } **[OpenID4VC-HAIP]**
  [OpenID4VC High Assurance Interoperability Profile
  (HAIP)](https://openid.net/specs/openid4vc-high-assurance-interoperability-profile-1_0.html)
  (Final, 24 December 2025), a strict profile over OpenID4VCI and OpenID4VP. IDCTF is not bound by it:
  the Governance Profile narrows the same optionality for itself.
- [](){ #ref-rego } **[Rego]**
  [Rego](https://www.openpolicyagent.org/docs/policy-language) (vendor
  documentation, no version, read on 17 October 2026), the policy
  language a verifier evaluates its trust rules in.
- [](){ #ref-rfc6962 } **[RFC6962]**
  [RFC 6962](https://www.rfc-editor.org/rfc/rfc6962.html) (June 2013, Experimental,
  obsoleted by RFC 9162), certificate
  transparency, the model behind the append-only log Trust Authority keeps of
  entity events.
- [](){ #ref-rfc9162 } **[RFC9162]**
  [RFC 9162](https://www.rfc-editor.org/rfc/rfc9162.html) (December 2021,
  Experimental), certificate
  transparency, the same model as RFC 6962.
- [](){ #ref-rfc9864 } **[RFC9864]**
  [RFC 9864](https://www.rfc-editor.org/rfc/rfc9864.html) (October 2025),
  fully-specified algorithms for JOSE and COSE. It deprecates the COSE value
  `-7` for `ES256`, which leaves the curve to the key, in favor of `ESP256`,
  `-9`. IDCTF keeps `-7` because ISO/IEC 18013-5:2021 requires it, the
  operational requirement under which RFC 9864 lets a deployment stay on a
  deprecated value. JOSE `ES256` is fully specified and not affected.
- [](){ #ref-saml2 } **[SAML2]**
  [SAML 2.0](https://docs.oasis-open.org/security/saml/v2.0/saml-core-2.0-os.pdf)
  (OASIS Standard, 15 March 2005), the alternative to OpenID Connect for that
  same handoff to the Relying Party's business system.
- [](){ #ref-wcag2ict } **[WCAG2ICT]**
  [Guidance on Applying WCAG 2 to Non-Web Information and Communications Technologies (WCAG2ICT)](https://www.w3.org/TR/2025/NOTE-wcag2ict-22-20251211/)
  (W3C Group Note, 11 December 2025), how the WCAG 2.2 success criteria are read
  for Mobile Wallet and Mobile Verifier, which are native applications.
