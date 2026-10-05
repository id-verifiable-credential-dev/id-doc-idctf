---
title: Glossary
description: What each term in this framework means, in one or two sentences, with the standard or the regulation it comes from.
---

<!-- Sumber: Glosarium dan Konvensi IDCTF, §A, §B, §C -->

# Glossary {#glossary}

Every term the Architecture Framework uses, arranged alphabetically. Each entry
says what the term means. Where the meaning belongs to a standard rather than to
IDCTF, the entry names that standard and links to it in
[References](references.md); where the meaning comes from Indonesian law, the
entry names the regulation. Terms that IDCTF narrows say what the narrowing is.

This page defines; it obliges nobody. Obligations live in the Technical
Specifications, the Governance Framework, and the Credential Rulebook Catalog.

<div class="glossary-list" markdown>

## A {#glossary-a}

Access certificate
:   The certificate that identifies one Relying Party Instance to a wallet in the European reference framework. IDCTF issues no certificate under this name: what it carries is folded into the Verifier Device Certificate, and an Instance that works remotely introduces itself with a did:webvh instead of a certificate. <span class="glossary-meta">See [Architecture and Reference Framework](references.md#frameworks-read-as-comparison).</span>

Accreditation
:   The second stage of authority, in which the Root Authority judges whether a party is fit to take part. A party that passes becomes visible to everyone else: its status is granted, it receives an Accreditation Credential, and it is added to the trusted list. <span class="glossary-meta">See [Accreditation][accreditation].</span>

Accreditation Credential
:   The SD-JWT VC an accredited entity carries as evidence of its own accreditation. It is a convenience and not an authority, because the trusted list stays the source of truth about who is accredited.

Approval Tier A, B, C
:   The three depths of review an authorization request can receive. Which tier applies follows from the sensitivity of the attributes being asked for, so a tier grades one request and never the party that made it. <span class="glossary-meta">See [Authorization][authorization].</span>

Assessment Body
:   A conformance testing and security audit organization the Root Authority recognizes. It measures an entity's implementation against the Governance Profile, audits that entity's security, and hands its findings over as a report; it decides nothing about participation. <span class="glossary-meta">See [Assessment Body][assessment-body].</span>

Assurance level
:   A grade of how well a key is protected and how strongly its user is authenticated, written as `low`, `substantial`, or `high`. IDCTF uses the scale in two unrelated places: once for an issuer's signing key, and once for the key held on a citizen's device. <span class="glossary-meta">See [Implementing Regulation (EU) 2015/1502](references.md#device-attestation-and-assurance) and [Two assurance levels](trust-model/two-assurance-levels.md).</span>

Attestation
:   A signed statement by one trusted party about another party, which the receiver verifies instead of taking the subject's own word for it.

Attribute identifier
:   The name by which one attribute of one credential type is requested or granted, written as the credential type identifier, a `#`, and the attribute name.

Attribute Issuer
:   The issuer role for everything other than basic identity, such as a degree certificate, a professional license, or an employment record, issued from records the institution already holds. It runs its own Issuer Core and signs with its own key. <span class="glossary-meta">See [Attribute Issuer][attribute-issuer].</span>

Authority Statement
:   The record of one permission the Root Authority granted to one entity, naming what that entity may do and what it may do it to. It is kept in the Trust Registry and answered when a participant asks, rather than handed out or published as a file.

Authorization
:   The third stage of authority, in which an accredited party is granted one specific permission at a time. It is the only stage that repeats, because a permission can be added or withdrawn without reassessing the party that holds it. <span class="glossary-meta">See [Authorization][authorization].</span>

## B {#glossary-b}

Bitstring Status List
:   The revocation and suspension mechanism for credentials in W3C VCDM form, in which each credential points at one bit of a published list. IDCTF uses it for the `ldp_vc` format only. <span class="glossary-meta">See [W3C Bitstring Status List](references.md#trust-lists-and-credential-status).</span>

## C {#glossary-c}

Claim
:   A statement a credential makes about its subject. Claims are the data inside the credential; what a verifier asks for is an attribute, and the two are the same thing seen from opposite sides. <span class="glossary-meta">See [W3C VCDM 2.0](references.md#credential-formats-and-their-signatures).</span>

Component
:   A part inside a Module that is not deployed on its own, the third tier of the structure. <span class="glossary-meta">See [Components inside a Module](software-architecture/components-inside-a-module.md).</span>

CONNECTIDN
:   The national digital identity hub service run by BLPID, which brokers logins between identity providers and the services that rely on them. It is an external system: IDCTF uses it to authenticate a citizen's account and nothing else, and it never sees a credential or a presentation. <span class="glossary-meta">Source: BSSN Regulation Number 1 of 2025.</span>

Credential key
:   The key a citizen's wallet holds to prove that the credentials it presents are its own. There is one per Mobile Wallet installation, shared by every credential in it, and it is not the device key.

Credential Rulebook
:   The document that settles everything about one credential type: its schema, the formats it may be issued in, how it is displayed, how far each attribute may be minimized, and the assurance demanded of the keys on both sides.

Credential Rulebook Provider
:   The authority that proposes one credential type and then owns its Rulebook across every later version. It proposes; the Root Authority approves and publishes. <span class="glossary-meta">See [Credential Rulebook Provider][credential-rulebook-provider].</span>

Credential type identifier
:   The name that identifies one credential type everywhere it appears, written in lowercase with an integer version, and used unchanged as the `vct`, the `docType`, and the mdoc namespace. The `id.idctf` namespace belongs to the ecosystem and is held by the Trust Authority, so an identifier does not move when an issuer's domain does; a type owned by another body keeps that body's own namespace.

CRL
:   The list a certificate authority publishes of the certificates it has revoked before their expiry. IDCTF publishes one for Document Signer Certificates, Verifier Issuing CAs, and Verifier Device Certificates. <span class="glossary-meta">See [RFC 5280](references.md#certificates-and-revocation).</span>

## D {#glossary-d}

DCQL
:   The query language a verifier uses to say which credentials and which attributes it wants. It replaces Presentation Exchange. <span class="glossary-meta">See [OpenID4VP 1.0](references.md#exchange-protocols).</span>

Device engagement
:   The opening step of a proximity exchange, in which the two devices swap the parameters they need to talk, over a QR code or NFC. <span class="glossary-meta">See [ISO/IEC 18013-5](references.md#exchange-protocols).</span>

Device identifier
:   The name an installation is known by to the party that vouches for it, computed from its device key. The key itself is never sent. <span class="glossary-meta">See [RFC 7638](references.md#identifiers-and-keys).</span>

Device key
:   The key one installation uses for its own dealings with the party that vouches for it, which is the Wallet Backend Service for a wallet and the Verifier Core for a Mobile Verifier. It is not the credential key.

DeviceAuth
:   The proof a wallet gives, during a proximity exchange, that it holds the key the credential was bound to. IDCTF accepts the signature form and not the shared-secret form. <span class="glossary-meta">See [ISO/IEC 18013-5](references.md#exchange-protocols).</span>

DID
:   An identifier a party controls itself, resolvable to a DID Document, with no registry handing it out. <span class="glossary-meta">See [W3C DID 1.0](references.md#identifiers-and-keys).</span>

DID Document
:   The document a DID resolves to, holding the public keys and verification methods that DID stands behind. Each entity hosts its own on its own domain rather than on a central service. <span class="glossary-meta">See [W3C DID 1.0](references.md#identifiers-and-keys).</span>

DID path
:   The way a verifier introduces itself by DID, one of the two ways IDCTF allows in an online presentation. The other is the certificate path. <span class="glossary-meta">See [OpenID4VP 1.0](references.md#exchange-protocols).</span>

did:key
:   A DID method in which the identifier is derived from a public key, so nothing has to be hosted anywhere. IDCTF uses it for the holder, one per Mobile Wallet installation. <span class="glossary-meta">See [did:key](references.md#identifiers-and-keys).</span>

did:webvh
:   A web-hosted DID method whose history is a signed log, so a change of key can be verified against what came before. IDCTF uses it for every entity. <span class="glossary-meta">See [did:webvh v1.0](references.md#identifiers-and-keys).</span>

Digital Identity Hub Service Center (BLPID)
:   The technical implementation unit of BSSN that runs the national digital identity hub service. <span class="glossary-meta">Source: BSSN Regulation Number 1 of 2025.</span>

Digital Population Identity (IKD)
:   Electronic information that represents a Population Document inside a digital application. It is not a credential in the IDCTF sense: it is one scheme run by the civil registration authority, while IDCTF carries many credential types from many issuers. <span class="glossary-meta">Source: Permendagri 72/2022.</span>

Direct Trust
:   The arrangement in which an entity issues, signs, and hosts its own artifacts, so whoever needs one fetches it from that entity rather than from a central distributor.

docType
:   The field that names a credential's type inside an mdoc. Its value is the credential type identifier set by the Credential Rulebook. <span class="glossary-meta">See [ISO/IEC 18013-5](references.md#credential-formats-and-their-signatures).</span>

DSC
:   The certificate an mdoc issuer signs individual credentials with, held one step below its own root. <span class="glossary-meta">See [ISO/IEC 18013-5 Annex B](references.md#certificates-and-revocation).</span>

## E {#glossary-e}

Electronic Certificate
:   A certificate that carries an Electronic Signature together with the identity of the party that owns it. <span class="glossary-meta">Source: PP 71/2019.</span>

Electronic Certification Provider (PSrE)
:   A legal entity that issues and manages Electronic Certificates. It is not the Indonesian equivalent of an issuer: a PSrE certifies signatures by people and bodies, while an issuer attests facts about a subject. <span class="glossary-meta">Source: PP 71/2019.</span>

Electronic Document
:   Electronic Information that has been created, forwarded, or stored in electronic form. <span class="glossary-meta">Source: UU 11/2008 jo. UU 19/2016.</span>

Electronic Information
:   One piece or a set of electronic data that carries meaning. <span class="glossary-meta">Source: UU 11/2008 jo. UU 19/2016.</span>

Electronic System Provider (PSE)
:   A party that operates an Electronic System. <span class="glossary-meta">Source: PP 71/2019.</span>

Entity chain
:   The set of checks that establish whether a party is a participant in good standing. They are answered from cached data, and their answers stay usable for hours or days. <span class="glossary-meta">See [Entity chain and transaction chain](trust-model/entity-chain-and-transaction-chain.md).</span>

Extension point (SPI)
:   An interface at the Provider layer that IDCTF defines and the implementer fills in, which is how an institution plugs its own records, signing arrangements, and key storage into a Module without changing it.

External system
:   A system IDCTF depends on but does not govern, which means it can be neither accredited nor revoked. There are four: the source systems an issuer copies from, CONNECTIDN, the device platforms, and the key management service providers. <span class="glossary-meta">See [External systems][external-systems].</span>

## G {#glossary-g}

Governance Framework
:   The IDCTF document that settles the rules for institutions and people: who decides what, how a request is approved, and what follows when an obligation is broken.

Governance Profile
:   The settings that hold across every credential type, such as the algorithms allowed, how long a cached copy stays usable, which protocol versions are in force, and how long a certificate may live.

## H {#glossary-h}

Holder
:   The person a credential is about, and the only role in the ecosystem held by a person rather than an institution. A holder registers nowhere and holds no obligations: the framework places every requirement on an institution. <span class="glossary-meta">See [W3C VCDM 2.0](references.md#credential-formats-and-their-signatures) and [the holder role][holder].</span>

Holder binding
:   The tie between a credential and a key the holder controls, which is what stops a credential from being useful to anyone who copies it. <span class="glossary-meta">See [IETF SD-JWT VC](references.md#credential-formats-and-their-signatures) and [ISO/IEC 18013-5](references.md#credential-formats-and-their-signatures).</span>

## I {#glossary-i}

IACA
:   The root certificate authority of an mdoc issuer in ISO terms. IDCTF calls it the Issuer Root CA. <span class="glossary-meta">See [ISO/IEC 18013-5 Annex B](references.md#certificates-and-revocation).</span>

IDCTF
:   The name of this framework as a whole, the Indonesia Digital Credential Trust Framework. *Ecosystem* is an ordinary noun in the prose and never a name.

Identity Issuer
:   The issuer role for basic identity, held by the national civil registration authority. Every other issuer rests on an identity it established. <span class="glossary-meta">See [Identity Issuer][identity-issuer].</span>

Intended use
:   One registered purpose a verifier may act for, together with the attributes that purpose allows it to ask for. A verifier registers each one separately and every request it sends points at exactly one. <span class="glossary-meta">See [Architecture and Reference Framework](references.md#frameworks-read-as-comparison).</span>

Intermediary
:   A Relying Party that talks to a wallet on behalf of another Relying Party without keeping the transaction data. IDCTF calls it the Relying Party Intermediary, and narrows it further: it cannot read the response either, because the response is encrypted to the merchant's own device key. <span class="glossary-meta">See [Architecture and Reference Framework](references.md#frameworks-read-as-comparison).</span>

iso_18045_*
:   The attack-resistance values a wallet reports for its key storage and its user authentication. The Governance Profile maps them from the assurance a Credential Rulebook demands. <span class="glossary-meta">See [OpenID4VCI 1.0 and ISO/IEC 18045](references.md#device-attestation-and-assurance).</span>

issuance-cose
:   The mdoc issuer's signing key in COSE form, the one wrapped by the Document Signer Certificate.

issuance-jose
:   The mdoc issuer's signing key in JWS form, the one published in its DID Document.

issuance_record
:   The archive an issuer keeps of what it issued and when, holding neither claims nor attributes.

Issuer
:   The party that issues a credential and signs it. In IDCTF the role is split in two by what may be issued, the Identity Issuer and the Attribute Issuer. <span class="glossary-meta">See [W3C VCDM 2.0](references.md#credential-formats-and-their-signatures).</span>

Issuer Root CA
:   The X.509 root the Trust Authority holds for the issuing side, kept in an offline HSM separate from the verifying side's root.

issuer_assurance
:   The grade recorded against an issuer's own signing key, which follows from where that key is stored. It is a governance matter and is unrelated to the assurance demanded of a citizen's key.

## K {#glossary-k}

Key Attestation
:   The signed statement that a wallet's key really sits in secure storage on the device. The Wallet Backend Service issues it, and an issuer asks for one when the Credential Rulebook demands that level of protection. <span class="glossary-meta">See [OpenID4VCI 1.0](references.md#device-attestation-and-assurance).</span>

Key Manager
:   The Component that generates, stores, rotates, and registers an entity's keys. It appears in Issuer Core, Verifier Core, and Wallet Backend Service, and a driver decides where the keys actually live.

keyStorage
:   The tag that records where a key is kept, which is what an assurance grade is read from.

## L {#glossary-l}

Last-known-good
:   The last signed copy of something an entity fetched, which it keeps using after the copy's lifetime runs out rather than failing at once. It stops being accepted at the tolerance limit.

Layer
:   What a Component is responsible for: Controller, Domain, Repository, or Provider, with Client and View sitting outside the server. It is a way of dividing one Component's work and not a fourth tier of the structure.

ldp_vc
:   A W3C VCDM credential secured by Data Integrity rather than by a JWT. IDCTF pins it to one cryptosuite, and it carries no selective disclosure, so a presentation of one discloses the whole credential. <span class="glossary-meta">See [W3C VCDM 2.0 and VC Data Integrity](references.md#credential-formats-and-their-signatures).</span>

LoTE
:   List of Trusted Entities, the data model a trusted list is written in. IDCTF publishes it in its JSON encoding. <span class="glossary-meta">See [ETSI TS 119 602](references.md#trust-lists-and-credential-status).</span>

LoTL
:   List of Trusted Lists, a trusted list whose entries point at other trusted lists instead of at entities. Whether IDCTF publishes one is still open. <span class="glossary-meta">See [ETSI TS 119 602](references.md#trust-lists-and-credential-status).</span>

## M {#glossary-m}

mDL
:   A driving license issued as an mdoc. <span class="glossary-meta">See [ISO/IEC 18013-5](references.md#credential-formats-and-their-signatures).</span>

mdoc
:   A credential encoded in CBOR and signed with COSE, designed to be read from a phone without a network. IDCTF uses it for proximity only. <span class="glossary-meta">See [ISO/IEC 18013-5](references.md#credential-formats-and-their-signatures).</span>

mdoc reader
:   The device that asks for an mdoc and verifies it within one proximity session, the counterpart of the device holding the mdoc. It is a protocol role on the proximity channel alone: an Instance working remotely is never a reader, and an Instance running an online check is not a reader while it does so. <span class="glossary-meta">See [ISO/IEC 18013-5](references.md#exchange-protocols).</span>

mdoc reader authentication certificate
:   The certificate a reader authenticates itself with in ISO terms. IDCTF calls it the Verifier Device Certificate. <span class="glossary-meta">See [ISO/IEC 18013-5 Annex B](references.md#certificates-and-revocation).</span>

Merchant
:   A small business that reads credentials through an RP Intermediary rather than through infrastructure of its own. It is registered by that intermediary and stops there: it is never accredited, never appears in the trusted list, holds no Authority Statement, and borrows the authority it acts under from the intermediary. <span class="glossary-meta">See [RP Intermediary and merchant](roles/rp-intermediary-and-merchant.md).</span>

min_assurance
:   The protection a Credential Rulebook demands of the key on the citizen's device before a credential of that type may be issued to it.

Minimization class
:   How sensitive one attribute is, set in its Credential Rulebook as `open`, `normal`, or `restricted`. The class decides how deeply a request for that attribute is reviewed.

Module
:   A unit deployed on its own as a single container image, the second tier of the structure. There are ten. <span class="glossary-meta">See [Module Map](high-level-architecture/module-map.md).</span>

MSO
:   The signed object inside an mdoc that carries a digest of every attribute, which is what makes the credential verifiable when only some attributes are shown. <span class="glossary-meta">See [ISO/IEC 18013-5](references.md#credential-formats-and-their-signatures).</span>

## O {#glossary-o}

Operator
:   A person who works the Console or the back office on behalf of an entity. The word names a person doing a job and is never used for the RP Intermediary.

## P {#glossary-p}

Participant Model
:   The three layers every participant is described in: the **Institution**, the legal body that exists before it touches the ecosystem; the **Entity**, which is born at accreditation and holds the DID, the keys, the certificate, and the status; and the **Role**, which is the authority that entity was granted. It holds without exception, and the holder and the merchant sit outside it. <span class="glossary-meta">See [Role map](roles/role-map.md).</span>

Personal Data
:   Data about an identified or identifiable natural person. <span class="glossary-meta">Source: UU 27/2022 on Personal Data Protection.</span>

Personal Data Controller
:   The party that determines the purpose of processing personal data and controls it. <span class="glossary-meta">Source: UU 27/2022.</span>

Personal Data Processor
:   The party that processes personal data on the Controller's behalf. <span class="glossary-meta">Source: UU 27/2022.</span>

Population Document
:   An official document issued by the civil registration authority. <span class="glossary-meta">Source: UU 24/2013 on Population Administration.</span>

Population Identification Number (NIK)
:   The unique and single identity number carried by a resident. <span class="glossary-meta">Source: UU 24/2013.</span>

Public Key Registry
:   The Trust Authority's record of every public key an entity has registered, with what each key is for, where it is stored, how long it is valid, and whether it still is. It holds no private keys.

purpose
:   The tag that records what a key is for, so a key registered for one job cannot quietly be used for another.

## R {#glossary-r}

Reader SDK
:   The library that gives an application the proximity reading side of ISO/IEC 18013-5. It is embedded in Mobile Verifier or in a Relying Party's own application, and it is not a Module.

ReaderAuth
:   The proof a reader gives, during a proximity exchange, that it is the party its certificate says it is. The certificate it uses is the Verifier Device Certificate. <span class="glossary-meta">See [ISO/IEC 18013-5](references.md#exchange-protocols).</span>

Recognition
:   The acceptance of another ecosystem's participants, asked for and answered over the trust query protocol.

Registration
:   The first stage of authority, in which a party becomes known and its file is opened. Everyone passes through it, merchants included, and a party that has only registered may do nothing at all. <span class="glossary-meta">See [Registration][registration].</span>

Registration certificate
:   The certificate that states the scope of one Relying Party Service in the European reference framework. IDCTF issues no certificate under this name: what it would carry, the purpose and the attributes of a given use, is carried by the Use Statement instead. <span class="glossary-meta">See [Architecture and Reference Framework](references.md#frameworks-read-as-comparison).</span>

Release train
:   The manifest of which Module versions were tested together, so an operator knows which combination is safe to deploy.

Relying Party
:   The organization that relies on a credential to serve someone, within the scope its accreditation allows. It is the only role on the verifier side; the RP Intermediary and the merchant are subtypes of it rather than roles of their own. <span class="glossary-meta">See [Relying Party][relying-party].</span>

Relying Party Instance
:   The software and hardware a Relying Party actually runs to talk to a wallet and to authenticate itself to it. It is remote when it is a Verifier Core deployment, and on the device when it is Mobile Verifier or an application carrying the Reader SDK. <span class="glossary-meta">See [Architecture and Reference Framework](references.md#frameworks-read-as-comparison).</span>

Relying Party Intermediary
:   A Relying Party that also runs a Verifier Core for the merchants it registers. It is accredited on the same terms as any Relying Party and receives two further permissions: to register merchants, and to hold a Verifier Issuing CA. <span class="glossary-meta">See [RP Intermediary and merchant](roles/rp-intermediary-and-merchant.md).</span>

Relying Party Service
:   A line of service inside one Relying Party with attributes and purposes of its own. IDCTF does not make it a layer: separate services are separate Entities, and what a given use may ask for is carried by the Use Statement. <span class="glossary-meta">See [Architecture and Reference Framework](references.md#frameworks-read-as-comparison).</span>

requestInfo
:   The field of a proximity request that carries data the reader signs along with the request itself. IDCTF uses it to carry the Use Statement offline, where there is no network to fetch one over. <span class="glossary-meta">See [ISO/IEC 18013-5](references.md#exchange-protocols).</span>

Role
:   Something the Root Authority can accredit, register, or recognize. There are eight: three governance roles and five primary roles. <span class="glossary-meta">See [Role map](roles/role-map.md).</span>

Root Authority
:   The state institution that decides both questions about every entity, whether it may take part and what it may then do. It decides them directly, with no sectoral body in between, and it takes no part in any citizen's transaction. <span class="glossary-meta">See [Root Authority][root-authority].</span>

## S {#glossary-s}

SD-JWT VC
:   A credential built on the JSON Web Token, in which the holder can disclose some attributes and withhold the rest. It is the main online format in IDCTF, pinned to one revision because the specification is still a draft. <span class="glossary-meta">See [IETF SD-JWT VC](references.md#credential-formats-and-their-signatures).</span>

Selective disclosure
:   Showing some attributes of a credential while the rest stay hidden, with the credential still verifiable. The `ldp_vc` format does not offer it. <span class="glossary-meta">See [IETF SD-JWT VC and ISO/IEC 18013-5](references.md#credential-formats-and-their-signatures).</span>

Services
:   A set of Modules that serve the same function, the first tier of the structure. There are four: Issuer Services, Wallet Services, Verifier Services, and Trust Infrastructure. <span class="glossary-meta">See [Module Map](high-level-architecture/module-map.md).</span>

SessionTranscript
:   The record of one proximity session that both sides sign, which ties a presentation to that session alone and makes it useless if it is replayed. <span class="glossary-meta">See [ISO/IEC 18013-5](references.md#exchange-protocols).</span>

Shared test vector
:   A test case, including a deliberately malicious one, run against both implementations of the Trust SDK so that the two agree on what they accept and what they reject.

Subject
:   The party a claim is about, which is not always the party holding the credential. <span class="glossary-meta">See [W3C VCDM 2.0](references.md#credential-formats-and-their-signatures).</span>

## T {#glossary-t}

Token Status List
:   The revocation and suspension mechanism in which each credential points at one bit of a compressed published list. IDCTF uses it for SD-JWT VC and mdoc, pinned to one revision because the specification is still a draft. <span class="glossary-meta">See [IETF Token Status List](references.md#trust-lists-and-credential-status).</span>

Tolerance limit
:   How far past its stated lifetime a cached signed copy may still be used. Beyond it the copy is rejected, however recently it was fetched.

Transaction chain
:   The set of checks made on a presentation while it happens. They run in real time, and their answers are worth seconds. <span class="glossary-meta">See [Entity chain and transaction chain](trust-model/entity-chain-and-transaction-chain.md).</span>

Transaction path
:   The route a credential or a presentation travels between an issuer, a wallet, and a verifier, the data plane of the ecosystem. It never crosses the trust path while a transaction is running. <span class="glossary-meta">See [Transaction path and trust path](high-level-architecture/transaction-path-and-trust-path.md).</span>

Trust anchor
:   The key a chain of trust is checked back to, which is trusted because it was built into the software rather than because something else vouched for it.

Trust Authority
:   The Module that holds the ecosystem's own records, keys, and roots. It is software, run by the Root Authority, and the two names are never interchangeable.

Trust path
:   The route the answers about trust travel, such as a trusted list, a status list, or a query about authority, the control plane of the ecosystem. It never crosses the transaction path while a transaction is running. <span class="glossary-meta">See [Transaction path and trust path](high-level-architecture/transaction-path-and-trust-path.md).</span>

Trust SDK
:   The library that performs the trust checks, embedded as a Provider Component in four Modules so that every participant checks the same things the same way. It is written twice, in Go and in Dart, and it is not a Module.

Trusted list
:   The signed list of the entities the ecosystem accredited, which every participant carries a copy of and checks against. It is the source of truth about who takes part. <span class="glossary-meta">See [ETSI TS 119 602](references.md#trust-lists-and-credential-status).</span>

TSL
:   The XML trusted list format used under eIDAS. IDCTF does not publish one. <span class="glossary-meta">See [ETSI TS 119 612](references.md#trust-lists-and-credential-status).</span>

## U {#glossary-u}

Use Statement
:   The statement, signed by the Trust Authority, that records one registered use of one verifier: its purpose, its legal basis, and the attributes that use may reach, always a subset of what the verifier's Authority Statement allows. The verifier carries it in the request, so the wallet has it without fetching anything, and it is revoked through a status list.

use_id
:   The identifier of one registered use, assigned by the Trust Authority when it approves that use and unique within the Entity that holds it.

## V {#glossary-v}

Verifiable Credential (VC)
:   A credential whose authenticity anyone can check by cryptography, without asking the issuer. <span class="glossary-meta">See [W3C VCDM 2.0](references.md#credential-formats-and-their-signatures).</span>

Verifiable Data Registry
:   Whatever system mediates the identifiers, keys, schemas, and statuses that verification depends on. In IDCTF that is the Trust Infrastructure. <span class="glossary-meta">See [W3C VCDM 2.0](references.md#credential-formats-and-their-signatures).</span>

Verifiable Presentation (VP)
:   One or more credentials shown by a holder, packaged so that the showing itself can be verified. <span class="glossary-meta">See [W3C VCDM 2.0](references.md#credential-formats-and-their-signatures).</span>

Verifier
:   The software that verifies a presentation. The organization behind it is the Relying Party; *verifier* names the software and never the role. <span class="glossary-meta">See [W3C VCDM 2.0](references.md#credential-formats-and-their-signatures).</span>

Verifier Device Certificate
:   The certificate carried by one device that reads credentials face to face. It is issued by the Verifier Core that vouches for that device, lives for a short time, and is revoked through a CRL.

Verifier Issuing CA
:   The intermediate certificate authority held by an RP Intermediary, and by a Relying Party that reads credentials offline, from which the certificates for individual devices are cut. The entity generates its own key; the Verifier Root CA issues the certificate for it.

Verifier Root CA
:   The X.509 root the Trust Authority holds for the verifying side, kept in an offline HSM separate from the issuing side's root.

verifier_info
:   The field of an online presentation request that carries statements about the verifier itself. IDCTF uses it to carry the Use Statement. <span class="glossary-meta">See [OpenID4VP 1.0](references.md#exchange-protocols).</span>

VICAL
:   The signed list of the root certificates of mdoc issuers, which is how a reader learns which issuers to accept. The Trust Registry publishes it. <span class="glossary-meta">See [ISO/IEC 18013-5 Annex C](references.md#trust-lists-and-credential-status).</span>

## W {#glossary-w}

Wallet Provider
:   The role answerable for the wallet a citizen carries: it publishes the wallet, vouches that the device and its keys are genuine, binds each installation to the citizen who enrolled it, and revokes one that is lost. Many institutions hold the role at once, and a citizen chooses among them. <span class="glossary-meta">See [Wallet Provider][wallet-provider].</span>

Witness did:webvh
:   The Trust Authority's countersignature on an entry in an entity's DID log, which is what stops an entity from rewriting its own key history unnoticed. An entry without one is rejected.

</div>
