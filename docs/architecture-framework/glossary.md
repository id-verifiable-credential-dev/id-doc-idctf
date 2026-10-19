---
title: Glossary
description: What each term in this framework means, in one or two sentences, with the standard or the regulation it comes from.
---

<!-- Sumber: Glosarium dan Konvensi IDCTF, §A, §B, §C, §G; tracks/0169 (fallback log DID ke DID Service, tidak ada di sumber); tracks/0213, tracks/0215 -->

# Glossary {#glossary}

The terms the Architecture Framework defines or narrows, arranged
alphabetically; Modules and Components are described in
[Module Map](high-level-architecture/module-map.md) and
[Components inside a Module](software-architecture/components-inside-a-module.md).
Each entry says what the term means. Where the meaning belongs to a standard rather than to
IDCTF, the entry names that standard and links to it in
[References](../references/index.md); where the meaning comes from Indonesian law, the
entry names the regulation. Terms that IDCTF narrows say what the narrowing is.

This page defines; it obliges nobody. Obligations live in the Technical
Specifications, the Governance Framework, and the Credential Rulebook Catalog.

<div class="glossary-list" markdown>

## A {#glossary-a}

Accreditation
:   The second stage of authority, in which the Root Authority judges whether a party is fit to take part. A party that passes becomes visible to everyone else: its status is granted, it receives an Accreditation Credential, and it is added to the trusted list. <span class="glossary-meta">See [Accreditation][accreditation].</span>

Accreditation Credential
:   The SD-JWT VC draft -13 an accredited entity carries as evidence of its own accreditation. It is a convenience and not an authority, because the trusted list stays the source of truth about who is accredited.

Admin API
:   The interface a Console reaches its Core through: Issuer Console works Issuer Core through it, Verifier Console works Verifier Core, and neither opens a database connection of its own. Issuer Core, Verifier Core, and DID Service answer it in the internal network zone, on a separate ingress from their public protocol endpoints. <span class="glossary-meta">See [Module Map](high-level-architecture/module-map.md).</span>

Approval Tier A, B, C
:   The three depths of review an authorization request can receive. Which tier applies follows from the minimization class of the attributes being asked for, so a tier grades one request and never the party that made it. <span class="glossary-meta">See [Authorization][authorization].</span>

Assessment Body
:   A conformance testing and security audit organization the Root Authority recognizes. It measures an entity's implementation against the Governance Profile, audits that entity's security, and hands its findings over as a report; it decides nothing about participation. <span class="glossary-meta">See [Assessment Body][assessment-body].</span>

Assurance level
:   A grade of how well a key is protected and how strongly its user is authenticated, written as `low`, `substantial`, or `high`. IDCTF uses the scale in two unrelated places: once for an issuer's signing key, and once for the credential key held on a citizen's device. <span class="glossary-meta">See [Implementing Regulation (EU) 2015/1502][ref-eu-2015-1502] and [Two assurance levels](trust-model/two-assurance-levels.md).</span>

Attestation
:   A signed statement by one trusted party about another party, which the receiver verifies instead of taking the subject's own word for it. Four such statements exist in the ecosystem: the attestation platform, the Key Attestation, the Verifier Device Certificate, and the Accreditation Credential. <span class="glossary-meta">See [Short-lived attestations][short-lived-attestations].</span>

Attribute identifier
:   The name by which one attribute of one credential type is requested or granted, written as the credential type identifier, a `#`, and the attribute name.

Attribute Issuer
:   The issuer role for everything other than basic identity, such as a degree certificate, a professional license, or an employment record, issued from records the institution already holds. It runs its own Issuer Core and signs with its own key. <span class="glossary-meta">See [Attribute Issuer][attribute-issuer].</span>

Authority Statement
:   The signed answer to whether one entity may perform one action on one resource, which Trust Registry builds when a participant asks and Trust Authority signs from its record of the permission the Root Authority granted. It carries its own issue and expiry times, and it is never handed out in advance or published as a file.

Authorization
:   The third stage of authority, in which an accredited party is granted one specific permission at a time. It is the only stage that repeats, because a permission can be added or withdrawn without reassessing the party that holds it. <span class="glossary-meta">See [Authorization][authorization].</span>

## B {#glossary-b}

Bitstring Status List
:   The revocation and suspension mechanism for credentials in W3C VCDM form, in which each credential points at one bit of a published list. IDCTF uses it for the `ldp_vc` format only. <span class="glossary-meta">See [W3C Bitstring Status List v1.0][ref-bitstring-status-list].</span>

Business system
:   The Relying Party's own system that asks Verifier Core for a check and receives the result over OpenID Connect Core 1.0 or SAML 2.0. It is not a Module, and whether it trusts the Relying Party's own Verifier Core is the Relying Party's internal matter. <span class="glossary-meta">See [Verifier to business system][verifier-to-business-system].</span>

## C {#glossary-c}

Catalog
:   What Trust Registry publishes on the central CDN so that anyone can read a Credential Rulebook: one signed catalog list naming every Rulebook version with the digest of its file, and the Rulebook files themselves, so one signature covers every Rulebook. A type that is not in the catalog has no Rulebook anyone can read. <span class="glossary-meta">See [Credential Rulebook Catalog](../credential-rulebook/index.md).</span>

Certificate revocation list (CRL)
:   The list a certificate authority publishes of the certificates it has revoked before their expiry. IDCTF publishes one for Document Signer Certificates, Verifier Issuing CAs, and Verifier Device Certificates. <span class="glossary-meta">See [RFC 5280][ref-rfc5280].</span>

Claim
:   A statement a credential makes about its subject. Claims are the data inside the credential; what a verifier asks for is an attribute, and the two are the same thing seen from opposite sides. <span class="glossary-meta">See [W3C VCDM 2.0][ref-vc-data-2-0].</span>

Component
:   A part inside a Module that is not deployed on its own, the third tier of the structure. <span class="glossary-meta">See [Components inside a Module](software-architecture/components-inside-a-module.md).</span>

Consent receipt
:   The record a verifier keeps of what a citizen agreed to release and for which purpose, so the decision can be audited later by someone other than the party that benefited from it. It holds no attribute the citizen released.

Credential key
:   The key a citizen's wallet holds to prove that the credentials it presents are its own. There is one per Mobile Wallet installation, shared by every credential in it, and it is not the device key. It is what SD-JWT calls the holder's key and ISO/IEC 18013-5:2021 calls `DeviceKey`.

Credential Rulebook
:   The document that settles everything about one credential type: its schema, the formats it may be issued in, how it is displayed, how far each attribute may be minimized, and the assurance demanded of the keys on both sides.

Credential Rulebook Provider
:   The authority that proposes one credential type and then owns its Rulebook across every later version. It proposes; the Root Authority approves and publishes. <span class="glossary-meta">See [Credential Rulebook Provider][credential-rulebook-provider].</span>

Credential type identifier
:   The name that identifies one credential type everywhere it appears, written in lowercase with an integer version, and used unchanged as the `vct`, the `docType`, and the mdoc namespace. The `id.idctf` namespace belongs to the ecosystem and is held by the Trust Authority, so an identifier does not move when an issuer's domain does; a type owned by another body keeps that body's own namespace, and a private party names its type under a domain it owns, as `<reverse-domain>.<type>.<N>`.

## D {#glossary-d}

Decentralized Identifier (DID)
:   An identifier a party controls itself, resolvable to a DID Document, with no registry handing it out. <span class="glossary-meta">See [W3C DID 1.0][ref-did-core].</span>

Device engagement
:   The opening step of a proximity exchange, in which the two devices swap the parameters they need to talk, over a QR code or NFC. <span class="glossary-meta">See [ISO/IEC 18013-5][ref-iso-18013-5].</span>

Device identifier
:   The name an installation is known by to the party that vouches for it, computed from its device key. The key itself is never sent. <span class="glossary-meta">See [RFC 7638][ref-rfc7638].</span>

Device key
:   The one key an installation holds in its secure element for the party that vouches for it: Wallet Backend Service for a wallet, Verifier Core for a Mobile Verifier. On a wallet it serves that dealing alone and is not the credential key. On a Mobile Verifier it is also the key in the Verifier Device Certificate, and so signs the reader's requests.

DeviceAuth
:   The proof a wallet gives, during a proximity exchange, that it holds the key the credential was bound to. IDCTF accepts the signature form and not the shared-secret form. <span class="glossary-meta">See [ISO/IEC 18013-5][ref-iso-18013-5].</span>

DID Document
:   The document a DID resolves to, holding the public keys and verification methods that DID stands behind. Each entity hosts its own on its own domain rather than on a central service; DID Service keeps the copy it witnessed, which the scheduled sync reads only when that domain is unreachable. <span class="glossary-meta">See [W3C DID 1.0][ref-did-core].</span>

DID route
:   The way a verifier introduces itself by DID, one of the two routes to a trust anchor IDCTF allows, and the one every online transaction takes. The other is the X.509 route. <span class="glossary-meta">See [OpenID4VP 1.0][ref-openid4vp] and [Two trust anchor paths: DID and X.509][two-trust-anchor-paths].</span>

did:key
:   A DID method in which the identifier is derived from a public key, so nothing has to be hosted anywhere. IDCTF uses it for the holder, one per Mobile Wallet installation, and to name Trust Authority's witness key and trusted list key in the trusted list. <span class="glossary-meta">See [did:key v0.9][ref-did-key].</span>

did:webvh
:   A web-hosted DID method whose history is a signed log, so a change of key can be verified against what came before. IDCTF uses it for every entity. <span class="glossary-meta">See [did:webvh v1.0][ref-did-webvh].</span>

Digital Credentials Query Language (DCQL)
:   The query language a verifier uses to say which credentials and which attributes it wants. It replaces Presentation Exchange. <span class="glossary-meta">See [OpenID4VP 1.0][ref-openid4vp].</span>

Digital Population Identity (IKD)
:   Electronic information that represents a Population Document inside a digital application. It is not a credential in the IDCTF sense: it is one scheme run by the civil registration authority, while IDCTF carries many credential types from many issuers. <span class="glossary-meta">Source: [Permendagri 72/2022][ref-permendagri-72-2022].</span>

Direct Trust
:   The arrangement in which an entity issues, signs, and hosts its own artifacts, so whoever needs one fetches it from that entity rather than from a central distributor.

docType
:   The field that names a credential's type inside an mdoc. Its value is the credential type identifier set by the Credential Rulebook. <span class="glossary-meta">See [ISO/IEC 18013-5][ref-iso-18013-5].</span>

Document Signer Certificate (DSC)
:   The certificate an mdoc issuer signs individual credentials with, held one step below its own root. <span class="glossary-meta">See [ISO/IEC 18013-5 Annex B][ref-iso-18013-5].</span>

## E {#glossary-e}

Electronic Certificate
:   An electronic certificate, issued by a PSrE, that carries an Electronic Signature and the identity showing the legal status of the parties to an electronic transaction. <span class="glossary-meta">Source: [UU 11/2008][ref-uu-11-2008] Pasal 1 angka 9; [PP 71/2019][ref-pp-71-2019] Pasal 1 angka 20.</span>

Electronic Certification Provider (PSrE)
:   A legal body that issues and audits Electronic Certificates. It is not the Indonesian equivalent of an issuer: a PSrE certifies signatures by people and bodies, while an issuer attests facts about a subject. A PSrE may also provide digital identity services under UU 11/2008 Pasal 13A, as inserted by UU 1/2024; when it issues credentials in IDCTF, it does so as an issuer, under the same rules as any other. <span class="glossary-meta">Source: [PP 71/2019][ref-pp-71-2019]; [UU 11/2008][ref-uu-11-2008].</span>

Electronic Document
:   Electronic Information that has been created, forwarded, or stored in electronic form. <span class="glossary-meta">Source: [UU 11/2008][ref-uu-11-2008] jo. UU 19/2016 and UU 1/2024.</span>

Electronic Information
:   One piece or a set of electronic data that carries meaning. <span class="glossary-meta">Source: [UU 11/2008][ref-uu-11-2008] jo. UU 19/2016 and UU 1/2024.</span>

Electronic System Provider (PSE)
:   Any person, state body, business entity, or community that provides, manages, or operates an Electronic System, for its own needs or for others'. <span class="glossary-meta">Source: [PP 71/2019][ref-pp-71-2019] Pasal 1 angka 4.</span>

Entity chain
:   The set of checks that establish whether a party is a participant in good standing. They are answered from cached data, and their answers stay usable for hours or days. <span class="glossary-meta">See [Entity chain and transaction chain][entity-chain-and-transaction-chain].</span>

Extension point (SPI)
:   An interface at the Provider layer that IDCTF defines and the implementer fills in, which is how an institution plugs its own records, signing arrangements, and key storage into a Module without changing it.

External system
:   A system IDCTF depends on but does not govern, which means it can be neither accredited nor revoked. There are four: the source systems an issuer copies from, the identity provider behind each wallet, the device platforms, and the key management service providers. <span class="glossary-meta">See [External systems][external-systems].</span>

## G {#glossary-g}

Governance Framework
:   The IDCTF document that settles the rules for institutions and people: who decides what, how a request is approved, and what follows when an obligation is broken.

Governance Profile
:   The settings that hold across every credential type, such as the algorithms allowed, how long a cached copy stays usable, which protocol versions are in force, and how long a certificate may live.

## H {#glossary-h}

Holder
:   The person a credential is about, and the only role in the ecosystem held by a person rather than an institution. A holder registers nowhere and holds no obligations: the framework places every requirement on an institution. <span class="glossary-meta">See [W3C VCDM 2.0][ref-vc-data-2-0] and [the holder role][holder].</span>

Holder binding
:   The tie between a credential and a key the holder controls, which is what stops a credential from being useful to anyone who copies it. <span class="glossary-meta">See [IETF SD-JWT VC][ref-i-d-ietf-oauth-sd-jwt-vc] and [ISO/IEC 18013-5][ref-iso-18013-5].</span>

## I {#glossary-i}

Identity Issuer
:   The issuer role for basic identity, held by the national civil registration authority. Every other issuer rests on an identity it established. <span class="glossary-meta">See [Identity Issuer][identity-issuer].</span>

Identity provider
:   The service a citizen signs in to when enrolling a Mobile Wallet, over OpenID Connect. It is an external system, and each Wallet Provider chooses its own: IDCTF uses it to authenticate an account and nothing else. It does not establish who the citizen is, because identity proofing happens at issuance and is rooted in the Identity Issuer, and it never sees a credential or a presentation. <span class="glossary-meta">See [External systems][external-systems].</span>

Indonesia Digital Credential Trust Framework (IDCTF)
:   The name of this framework as a whole. *Ecosystem* is an ordinary noun in the prose and never a name.

Intended use
:   One registered purpose a Relying Party may act for, together with the attributes that purpose allows it to ask for. A Relying Party registers each one separately and every request it sends points at exactly one.

Intermediary
:   A Relying Party that talks to a wallet on behalf of another Relying Party without keeping the transaction data. IDCTF calls it the Relying Party Intermediary, and narrows it further: it cannot read the response either, because the response is encrypted to a key the merchant's own device drew for that request.

iso_18045_*
:   The attack-resistance values a wallet reports for its key storage and its user authentication. The Governance Profile maps them from the assurance a Credential Rulebook demands. <span class="glossary-meta">See [OpenID4VCI 1.0][ref-openid4vci] and [ISO/IEC 18045:2022][ref-iso-18045].</span>

issuance-cose
:   The issuer's signing key in COSE form, wrapped by the Document Signer Certificate. It signs the MSO of an mdoc.

issuance-jose
:   The issuer's signing key for JOSE and Data Integrity signatures, published in its DID Document as a [`Multikey`][ref-cid] (Controlled Identifiers 1.0). It signs SD-JWT VC and `ldp_vc`.

issuance_record
:   The archive an issuer keeps of what it issued and when, holding neither claims nor attributes.

Issuer
:   The party that issues a credential and signs it. In IDCTF the role is split in two by what may be issued, the Identity Issuer and the Attribute Issuer. <span class="glossary-meta">See [W3C VCDM 2.0][ref-vc-data-2-0].</span>

Issuer Root CA
:   The X.509 root the Trust Authority holds for the issuing side, kept in an offline HSM separate from the verifying side's root.

issuer_assurance
:   The grade recorded against an issuer's own signing key, which follows from where that key is stored. It is a governance matter and is unrelated to the assurance demanded of the credential key.

Issuing Authority Certificate Authority (IACA)
:   The root certificate authority of an mdoc issuer in ISO terms. IDCTF calls it the Issuer Root CA. <span class="glossary-meta">See [ISO/IEC 18013-5 Annex B][ref-iso-18013-5].</span>

## K {#glossary-k}

Key Attestation
:   The signed statement that a wallet's credential key really sits in secure storage on the device. The Wallet Backend Service issues it, and an issuer asks for one before every issuance, and the Credential Rulebook sets how strong the storage must be. <span class="glossary-meta">See [OpenID4VCI 1.0][ref-openid4vci].</span>

Key Binding JWT (KB-JWT)
:   The JWT a wallet signs with the credential key named in an SD-JWT VC's `cnf`, over the verifier's nonce and audience, which proves that the party presenting the credential holds the key it was issued to. <span class="glossary-meta">See [IETF SD-JWT VC][ref-i-d-ietf-oauth-sd-jwt-vc].</span>

Key Manager
:   The Component that generates, stores, rotates, and registers an entity's keys. It appears in Issuer Core, Verifier Core, and Wallet Backend Service, and a driver decides where the keys actually live.

keyStorage
:   The tag that records where a key is kept, backed by evidence, which is what an assurance grade is read from.

## L {#glossary-l}

Last-known-good
:   The last signed copy of a status list, a CRL, a VICAL, a TRQP answer, or an entity's `did:webvh` log, which a participant keeps using after the copy's lifetime runs out rather than failing at once. It stops being accepted at the tolerance limit. The trusted list is never kept this way: past its `NextUpdate` it is discarded.

Layer
:   What a Component is responsible for: Controller, Domain, Repository, or Provider, with Client and View sitting outside the server. It is a way of dividing one Module's work and not a fourth tier of the structure.

ldp_vc
:   A W3C VCDM credential secured by Data Integrity rather than by a JWT. IDCTF pins it to one cryptosuite, and it carries no selective disclosure, so a presentation of one discloses the whole credential. <span class="glossary-meta">See [W3C VCDM 2.0][ref-vc-data-2-0] and [VC Data Integrity 1.0][ref-vc-data-integrity].</span>

List of Trusted Entities (LoTE)
:   The data model a trusted list is written in. IDCTF publishes it in its JSON encoding. <span class="glossary-meta">See [ETSI TS 119 602 V1.1.1][ref-etsi-ts-119602].</span>

List of Trusted Lists (LoTL)
:   A trusted list that points at other trusted lists. IDCTF publishes none. <span class="glossary-meta">See [ETSI TS 119 602][ref-etsi-ts-119602].</span>

## M {#glossary-m}

mdoc
:   A credential encoded in CBOR and signed with COSE, designed to be read from a phone without a network. IDCTF uses it for proximity only. <span class="glossary-meta">See [ISO/IEC 18013-5][ref-iso-18013-5].</span>

mdoc reader
:   The device that asks for an mdoc and verifies it within one proximity session, the counterpart of the device holding the mdoc. It is a protocol role on the proximity channel alone: an Instance working remotely is never a reader, and an Instance running an online check is not a reader while it does so. <span class="glossary-meta">See [ISO/IEC 18013-5][ref-iso-18013-5].</span>

mdoc reader authentication certificate
:   The certificate a reader authenticates itself with in ISO terms. IDCTF calls it the Verifier Device Certificate. <span class="glossary-meta">See [ISO/IEC 18013-5 Annex B][ref-iso-18013-5].</span>

Merchant
:   A small business that reads credentials through an RP Intermediary rather than through infrastructure of its own. It is registered by that intermediary and stops there: it is never accredited, never appears in the trusted list, holds no Authority Statement, and borrows the authority it acts under from the intermediary. <span class="glossary-meta">See [RP Intermediary and merchant](roles/rp-intermediary-and-merchant.md).</span>

min_assurance
:   The protection a Credential Rulebook demands of the credential key on the citizen's device before a credential of that type may be issued to it.

Minimization class
:   The value set on one attribute in its Credential Rulebook, `open`, `normal`, or `restricted`, that decides which approval tier a request for that attribute takes. The tier decides how deeply the request is reviewed.

Mobile Driving License (mDL)
:   A driving license issued as an mdoc. <span class="glossary-meta">See [ISO/IEC 18013-5][ref-iso-18013-5].</span>

Mobile Security Object (MSO)
:   The signed object inside an mdoc that carries a digest of every attribute, which is what makes the credential verifiable when only some attributes are shown. <span class="glossary-meta">See [ISO/IEC 18013-5][ref-iso-18013-5].</span>

Module
:   A unit deployed on its own as a single container image, the second tier of the structure. There are ten. <span class="glossary-meta">See [Module Map](high-level-architecture/module-map.md).</span>

## O {#glossary-o}

OpenID for Verifiable Credential Issuance (OpenID4VCI)
:   The protocol that carries issuance from an issuer to a wallet: the credential offer, the authorization step, and the credential request. It is the only issuance protocol in IDCTF. <span class="glossary-meta">See [OpenID4VCI 1.0][ref-openid4vci] and [Issuer to Wallet][issuer-to-wallet].</span>

OpenID for Verifiable Presentations (OpenID4VP)
:   The protocol that carries an online presentation from a wallet to a verifier, used for SD-JWT VC and `ldp_vc`. It supplies DCQL, the two ways a verifier introduces itself, and the `verifier_info` parameter. <span class="glossary-meta">See [OpenID4VP 1.0][ref-openid4vp] and [Wallet to Verifier, online][wallet-to-verifier-online].</span>

Operator
:   A person who works the Console or the back office on behalf of an entity. The word names a person doing a job and is never used for the RP Intermediary.

## P {#glossary-p}

Personal Data
:   Data about an identified or identifiable natural person. <span class="glossary-meta">Source: [UU 27/2022][ref-uu-27-2022] on Personal Data Protection.</span>

Personal Data Controller
:   The party that determines the purpose of processing personal data and controls it. <span class="glossary-meta">Source: [UU 27/2022][ref-uu-27-2022].</span>

Personal Data Processor
:   The party that processes personal data on the Controller's behalf. <span class="glossary-meta">Source: [UU 27/2022][ref-uu-27-2022].</span>

Population Document
:   An official document issued by the Implementing Agency (*Instansi Pelaksana*), with legal force as authentic evidence, resulting from population registration and civil registration. <span class="glossary-meta">Source: UU 23/2006 as amended by [UU 24/2013][ref-uu-24-2013] on Population Administration, Pasal 1 angka 8.</span>

Population Identification Number (NIK)
:   The unique and single identity number carried by a resident. <span class="glossary-meta">Source: [UU 24/2013][ref-uu-24-2013].</span>

Pre-rotation
:   The `did:webvh` mechanism by which each entry of an entity's log commits to the hash of the next update key before that key is ever used, so a thief who steals the current key cannot also claim the one after it. <span class="glossary-meta">See [did:webvh v1.0][ref-did-webvh].</span>

Public Key Registry
:   The Trust Authority's record of every public key an entity has registered, with what each key is for, where it is stored, how long it is valid, and whether it still is. It holds no private keys.

purpose
:   The tag that records what a key is for, so a key registered for one job cannot quietly be used for another.

## R {#glossary-r}

Reader SDK
:   The library that gives an application the proximity reading side of ISO/IEC 18013-5. It is embedded in Mobile Verifier or in a Relying Party's own application, and it is not a Module.

ReaderAuth
:   The proof a reader gives, during a proximity exchange, that it is the party its certificate says it is. The certificate it uses is the Verifier Device Certificate. <span class="glossary-meta">See [ISO/IEC 18013-5][ref-iso-18013-5].</span>

ReaderAuthRole
:   The extension of a Verifier Device Certificate that names the document types and data elements the reader device may ask for, written as the bare `docType` and element names ISO/IEC 18013-5 uses. A wallet refuses a request for any attribute outside it.

Recognition
:   The acceptance of another ecosystem's participants, asked for and answered over the trust query protocol.

Recognition statement
:   The signed answer to a recognition query, which Trust Registry builds and Trust Authority signs with its recognition statement key from its own record of the recognition, as it does an Authority Statement for a permission.

Registration
:   The first stage of authority, in which a party becomes known and its file is opened. Every party passes through it, merchants included, whom their RP Intermediary registers in its own records, and a party that has only registered may do nothing at all. <span class="glossary-meta">See [Registration][registration].</span>

Release train
:   The manifest of which Module versions were tested together, so an operator knows which combination is safe to deploy.

Relying Party
:   The organization that relies on a credential to serve someone, within the scope its accreditation allows. It is the only role on the verifier side; the RP Intermediary and the merchant are subtypes of it rather than roles of their own. <span class="glossary-meta">See [Relying Party][relying-party].</span>

Relying Party Instance
:   The software and hardware a Relying Party actually runs to talk to a wallet and to authenticate itself to it. It is remote when it is a Verifier Core deployment, and on the device when it is Mobile Verifier or an application carrying the Reader SDK. <span class="glossary-meta">See [Relying Party Instance][relying-party-instance].</span>

Relying Party Intermediary
:   A Relying Party that also runs a Verifier Core for the merchants it registers. It is accredited on the same terms as any Relying Party and receives two further permissions: to register merchants, and to hold a Verifier Issuing CA. <span class="glossary-meta">See [RP Intermediary and merchant](roles/rp-intermediary-and-merchant.md).</span>

Request Object
:   The signed presentation request a verifier publishes behind a `request_uri` and a wallet fetches at the start of an online presentation. A Relying Party signs it with the Request Object key published in its DID Document; a merchant signs it with the key in its Verifier Device Certificate. <span class="glossary-meta">See [RFC 9101][ref-rfc9101] and [A Relying Party's keys][a-relying-partys-keys].</span>

requestInfo
:   The field of a proximity request that carries data the reader signs along with the request itself. IDCTF uses it to carry the Use Statement offline, where there is no network to fetch one over. <span class="glossary-meta">See [ISO/IEC 18013-5][ref-iso-18013-5].</span>

Role
:   Something the Root Authority can accredit, register, or recognize. The holder is the one exception: the test does not reach a person, and the holder is a role because the ecosystem exists to serve them. There are eight: three governance roles and five primary roles. <span class="glossary-meta">See [Role map](roles/role-map.md).</span>

Root Authority
:   The state institution that decides both questions about every entity, whether it may take part and what it may then do. It decides them directly, with no sectoral body in between, and it takes no part in any citizen's transaction. <span class="glossary-meta">See [Root Authority][root-authority].</span>

RP Intermediary
:   The short form of Relying Party Intermediary, and the one the pages use.

## S {#glossary-s}

SD-JWT-based Verifiable Credentials (SD-JWT VC)
:   A credential built on the JSON Web Token, in which the holder can disclose some attributes and withhold the rest. It is the main online format in IDCTF, pinned to draft -13 because the specification is still a draft. <span class="glossary-meta">See [IETF SD-JWT VC][ref-i-d-ietf-oauth-sd-jwt-vc].</span>

Selective disclosure
:   Showing some attributes of a credential while the rest stay hidden, with the credential still verifiable. The `ldp_vc` format does not offer it. <span class="glossary-meta">See [IETF SD-JWT VC][ref-i-d-ietf-oauth-sd-jwt-vc] and [ISO/IEC 18013-5][ref-iso-18013-5].</span>

Self-certifying identifier (SCID)
:   The identifier inside a `did:webvh`, a hash of the first entry of the entity's log, so the identifier binds its whole key history without depending on the domain that serves it. Trust SDK carries Trust Authority's SCID at build time, which is what anchors Trust Authority's own signatures. <span class="glossary-meta">See [did:webvh v1.0][ref-did-webvh].</span>

Services
:   A set of Modules that serve the same function, the first tier of the structure. There are four: Issuer Services, Wallet Services, Verifier Services, and Trust Infrastructure. <span class="glossary-meta">See [Services](high-level-architecture/services.md).</span>

SessionTranscript
:   The record of one proximity session that both sides sign, which ties a presentation to that session alone and makes it useless if it is replayed. <span class="glossary-meta">See [ISO/IEC 18013-5][ref-iso-18013-5].</span>

Shared test vector
:   A test case, including a deliberately malicious one, run against both implementations of the Trust SDK so that the two agree on what they accept and what they reject.

Status List Token
:   The signed token that carries an issuer's status list in the IETF Token Status List form, which an SD-JWT VC or an mdoc points into by bit index. An issuer hosts its own on its own domain and signs it with its `status-list` key, and Trust Registry hosts the Use Statement and accreditation lists on the central content delivery network; each is republished when a bit is flipped. <span class="glossary-meta">See [IETF Token Status List draft -14][ref-i-d-ietf-oauth-status-list] and [Status list checking and revocation][status-list-checking-and-revocation].</span>

status-list
:   The issuer's third signing key, published in its DID Document beside `issuance-jose`. It signs the Status List Token and the Bitstring Status List and nothing else, so that revocation keeps working while a credential signing key is revoked.

Subject
:   The party a claim is about, which is not always the party holding the credential. <span class="glossary-meta">See [W3C VCDM 2.0][ref-vc-data-2-0].</span>

## T {#glossary-t}

Time to Live (TTL)
:   How long a cached signed copy still counts as current, set by the risk profile of what the copy protects. Past it the copy is a last-known-good copy, used up to the tolerance limit and refused after.

Token Status List
:   The revocation and suspension mechanism in which each credential points at a two-bit entry, revoked and suspended, of a compressed published list. IDCTF uses it for SD-JWT VC and mdoc, pinned to draft -14 because the specification is still a draft. <span class="glossary-meta">See [IETF Token Status List][ref-i-d-ietf-oauth-status-list].</span>

Tolerance limit
:   How far past its stated lifetime a cached signed copy of a status list, a CRL, a VICAL, a TRQP answer, or an entity's `did:webvh` log may still be used. Beyond it the copy is rejected, however recently it was fetched. The trusted list has no tolerance; its copy expires at `NextUpdate`. <span class="glossary-meta">See [Three rules for reading the copy][three-rules-for-reading-the-copy].</span>

Transaction chain
:   The set of checks made on a presentation while it happens. They run in real time, and their answers are worth seconds. <span class="glossary-meta">See [Entity chain and transaction chain][entity-chain-and-transaction-chain].</span>

Transaction path
:   The route a credential or a presentation travels between an issuer, a wallet, and a verifier, the data plane of the ecosystem. It never crosses the trust path while a transaction is running. <span class="glossary-meta">See [The transaction path and the trust path](high-level-architecture/transaction-path-and-trust-path.md).</span>

Trust anchor
:   The key a chain of trust is checked back to, which is trusted because it was built into the software rather than because something else vouched for it.

Trust Authority
:   The Module that holds the ecosystem's own records, keys, and roots. It is software, run by the Root Authority, and the two names are never interchangeable.

Trust path
:   The route the answers about trust travel, such as a trusted list, a status list, or a query about authority, the control plane of the ecosystem. It never crosses the transaction path while a transaction is running. <span class="glossary-meta">See [The transaction path and the trust path](high-level-architecture/transaction-path-and-trust-path.md).</span>

Trust Registry Query Protocol (TRQP)
:   The protocol over which an entity asks Trust Registry a question rather than downloading the answer in advance: `POST /authorization` asks whether an entity holds a given permission, `POST /recognition` whether another ecosystem is recognized. <span class="glossary-meta">See [ToIP TRQP v2.0][ref-trqp] and [Entity to Trust Registry][entity-to-trust-registry].</span>

Trust SDK
:   The library that performs the trust checks, embedded as a Provider Component in four Modules so that every participant checks the same things the same way. It is written twice, in Go and in Dart, and it is not a Module.

Trusted list
:   The signed list of the entities the ecosystem accredited, which every participant carries a copy of and checks against. It is the source of truth about who takes part, and it names the keys an entity has had revoked early. <span class="glossary-meta">See [ETSI TS 119 602][ref-etsi-ts-119602].</span>

Trust-service status list (TSL)
:   The XML trusted list format used under eIDAS. IDCTF does not publish one. <span class="glossary-meta">See [Technology map][technology-map].</span>

## U {#glossary-u}

Use Statement
:   The statement, signed by the Trust Authority, that records one registered use of one Relying Party: its purpose, its legal basis, and the attributes that use may reach, always a subset of what the Relying Party's Authority Statement allows. The verifier carries it in the request, so the wallet has it without fetching anything, and it is revoked through a status list.

use_id
:   The identifier of one registered use, assigned by the Trust Authority when the Root Authority approves that use and unique within the entity that holds it.

## V {#glossary-v}

vct
:   The field that names a credential's type inside an SD-JWT VC. Its value is the credential type identifier set by the Credential Rulebook. <span class="glossary-meta">See [IETF SD-JWT VC][ref-i-d-ietf-oauth-sd-jwt-vc].</span>

Verifiable Credential (VC)
:   A credential whose authenticity anyone can check by cryptography, without asking the issuer. <span class="glossary-meta">See [W3C VCDM 2.0][ref-vc-data-2-0].</span>

Verifiable Data Registry
:   Whatever system mediates the identifiers, keys, schemas, and statuses that verification depends on. In IDCTF that is the Trust Infrastructure. <span class="glossary-meta">See [W3C VCDM 2.0][ref-vc-data-2-0].</span>

Verifiable Presentation (VP)
:   One or more credentials shown by a holder, packaged so that the showing itself can be verified. <span class="glossary-meta">See [W3C VCDM 2.0][ref-vc-data-2-0].</span>

verification_record
:   The archive a Relying Party keeps of what it verified and when, holding neither claims nor attributes. It is kept as long as the Relying Party's legal duty requires. <span class="glossary-meta">See [Storage: sessions and archive][storage-sessions-and-archive].</span>

Verified Issuer Certificate Authority List (VICAL)
:   The signed list of the root certificates of mdoc issuers, which is how a reader learns which issuers to accept. The Trust Registry publishes it. <span class="glossary-meta">See [ISO/IEC 18013-5 Annex C][ref-iso-18013-5].</span>

Verifier
:   The software that verifies a presentation. The organization behind it is the Relying Party; *verifier* names the software and never the role. <span class="glossary-meta">See [W3C VCDM 2.0][ref-vc-data-2-0].</span>

Verifier Device Certificate
:   The X.509 certificate carried by one reader device, a merchant's or a Relying Party's own counter device. It is issued by the Verifier Core that vouches for that device from its own Verifier Issuing CA, carries the attributes the device may ask for in `ReaderAuthRole`, lives for a period the Governance Profile sets, and is withdrawn early through a CRL. A merchant presents it online as well as in proximity.

Verifier Issuing CA
:   The intermediate certificate authority held by an RP Intermediary, and by a Relying Party that reads credentials offline, from which the certificates for individual devices are cut. The entity generates its own key; the Verifier Root CA issues the certificate for it.

Verifier Root CA
:   The X.509 root the Trust Authority holds for the verifying side, kept in an offline HSM separate from the issuing side's root.

verifier_info
:   The field of an online presentation request that carries statements about the verifier itself. IDCTF uses it to carry the Use Statement. <span class="glossary-meta">See [OpenID4VP 1.0][ref-openid4vp].</span>

VICAL key
:   The key in the Trust Authority's HSM that signs each published version of the VICAL. It is not the key that signs the trusted list, because the two lists have different formats and different readers: the VICAL is read by mdoc readers, among them readers abroad that never see the trusted list. <span class="glossary-meta">See [ISO/IEC 18013-5 Annex C][ref-iso-18013-5].</span>

## W {#glossary-w}

Wallet Provider
:   The role answerable for the wallet a citizen carries: it publishes the wallet, vouches that the device and its keys are genuine, binds each installation to the citizen who enrolled it, and revokes one that is lost. Many institutions hold the role at once, and a citizen chooses among them. <span class="glossary-meta">See [Wallet Provider][wallet-provider].</span>

Witness did:webvh
:   DID Service's countersignature, made with Trust Authority's witness key, on an entry in an entity's DID log, which is what stops an entity from rewriting its own key history unnoticed. An entry without one is rejected.

Witness file
:   The `did-witness.json` file an entity serves beside its `did.jsonl` log, holding DID Service's witness proof on each entry. A reader fetches the two together on its sync. <span class="glossary-meta">See [did:webvh v1.0][ref-did-webvh].</span>

## X {#glossary-x}

X.509 route
:   The way a verifier reaches a trust anchor through a certificate chain, the other of the two routes. Proximity reading obliges every reader to hold it, because ISO/IEC 18013-5 knows no DID, and a merchant takes it online as well, introducing itself with `x509_hash`. <span class="glossary-meta">See [Two trust anchor paths: DID and X.509][two-trust-anchor-paths].</span>

x5chain
:   The COSE header that carries an X.509 certificate chain inside a signed structure: the Document Signer Certificate in an mdoc's IssuerAuth, the Verifier Device Certificate in ReaderAuth, the VICAL signer certificate in the VICAL, and the status list signer certificate in the CWT form of a status list. A reader finds the certificate inside the object it is checking. <span class="glossary-meta">See [ISO/IEC 18013-5][ref-iso-18013-5].</span>

</div>

## Where the ecosystem's own names are defined {#where-the-ecosystems-own-names-are-defined}

Some names in this document belong to IDCTF rather than to a standard. Each has
one home page, and this list points at it:

- Roles and the institutions that hold them, and the Relying Party Instance each
  Relying Party runs, in [Role map](roles/role-map.md).
- Services, in [Services](high-level-architecture/services.md), and Modules, in
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
