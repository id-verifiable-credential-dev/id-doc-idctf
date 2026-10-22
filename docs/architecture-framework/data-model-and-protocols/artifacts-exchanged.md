---
title: "Artifacts exchanged"
description: The sixteen artifacts of the ecosystem, one section each, with who publishes it, what reads it, where it lives, and how long a copy stays good.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §4.6, §5.7 (Kep. 9, 28, 30); Rincian Module dan Operasi, siklus scope verifier; tracks/0169 (fallback log DID ke DID Service, tidak ada di sumber); tracks/0213; tracks/0305, tracks/0368, tracks/0376 (Governance Profile) -->

# Artifacts exchanged {#artifacts-exchanged}

An artifact is something one party produces and another relies on: a signed
list, a certificate, a credential, an answer to a query. Sixteen of them exist
in the ecosystem and there are no others. A request is not one of them, because
it asks rather than states; what vouches for a request is the artifact it
carries.

[The table of artifacts][tbl-artifacts] names each one, and the section it
points to opens with who publishes it, what reads it, where it lives, and how
long a copy stays good.

[](){ #tbl-artifacts }

<figure markdown="1" class="ekdn-table">

| Artifact | Description | Details |
|---|---|---|
| Trusted list | The roll of accredited entities, naming each one along with the certificate authorities it issues from. A party absent from it is rejected however well everything else about it checks out. | [Trusted list][trusted-list] |
| Credential Rulebook | The rules for one credential type: its schema, its attributes, and the assurance each side has to meet. A version is frozen when it is published, so two parties holding the same version hold the same rules. | [Credential Rulebook][credential-rulebook] |
| Catalog list | The signed index of every published Rulebook version, each entry carrying the digest of its file. One signature covers every Rulebook, and a type the list does not name has no Rulebook anyone may read. | [Catalog list][catalog-list] |
| VICAL | The signed list of certificate roots allowed to sign an mdoc. It is what lets an offline verifier accept a credential from an issuer it has never met. | [VICAL][vical] |
| Governance Profile | The numbers and algorithms the ecosystem may change without changing an interface, and the address of everything Trust Infrastructure serves. It is the first thing every Module fetches, from the one address it is built with. | [Governance Profile][governance-profile] |
| DID Document | An entity's public keys and the methods for verifying against them. It proves a signature belongs to the entity that claims it, and answers nothing else. | [DID Document][did-document] |
| Status list | Which of one issuer's credentials have been revoked. Each issuer publishes its own, so revocation data never accumulates in a single national service. | [Status list][status-list] |
| Authority Statement | A signed answer on one permission of one entity, an `action` on a `resource`. It is built for a TRQP query rather than published, and an entity holding several permissions is the subject of several statements. | [Authority Statement][authority-statement] |
| Recognition statement | A signed answer on whether another ecosystem's authority is recognized for one action on one credential type. It is built for a TRQP query as an Authority Statement is, and it says nothing about any IDCTF entity. | [Recognition statement][recognition-statement] |
| Use Statement | One registered use of one Relying Party: the purpose shown to the citizen, its legal basis, and the attributes that use may reach. The verifier carries it in its own request, so a wallet reads an approved purpose without asking anyone. | [Use Statement][use-statement] |
| Accreditation Credential | An entity's own proof that it was accredited, carried by that entity. It is evidence about itself, and everyone else checks the trusted list instead. | [Accreditation Credential][accreditation-credential] |
| Key Attestation | Proof that a wallet installation's keys sit in storage the device platform vouches for. An issuer demands one before issuing any credential, and the Rulebook sets the storage it must report. | [Key Attestation][key-attestation] |
| Verifier Device Certificate | The certificate standing behind one reading device, carrying the attributes that device may ask for. It is what lets a wallet trust a merchant that appears in no trusted list, and it vouches for a Relying Party's own counter device the same way. | [Verifier Device Certificate][verifier-device-certificate] |
| Credential | The signed claims about a citizen that an issuer built from its own records. It lives on the citizen's device and in no register, so a verifier checks a signature rather than a lookup. | [Credential][credential] |
| Presentation | The attributes a citizen chose to disclose in one exchange, bound to the request that asked for them. It is good for a single use, and nobody keeps it whole; a verifier keeps a digest of an online one. | [Presentation][presentation] |
| Document Signer Certificate, Verifier Issuing CA, CRL | The X.509 certificates that chain an issuer's signature to the Issuer Root CA and a merchant's device to the Verifier Root CA, and the list that withdraws either one early. | [Document Signer Certificate, Verifier Issuing CA, and CRL][document-signer-certificate-verifier-issuing-ca-and-crl] |

</figure>

Trust SDK is named under Read by in two of the artifact sections, and it is not a
Module. It is a library embedded inside four Modules, and what it holds is in
[Trust SDK][sa-trust-sdk].
Which identifier appears inside which artifact is in
[Identifier](identifier.md), and the message each protocol wraps them
in is in [Protocols per interaction][protocols-per-interaction].

The four groups that follow take the sixteen one at a time, grouped by where
each one lives, because that decides how an artifact behaves when something is
unreachable: one published to a single national address fails differently from
one each entity serves itself, and differently again from one that is never
published anywhere. Which of them cross between the two planes,
and what each does for that crossing, is a different question, answered in
[what connects the two planes][what-connects-the-two-planes].

[](){ #fig-where-artifacts-live }

<figure markdown="1">
  ![Four stacked groups, one per place an artifact can live, holding sixteen artifacts between them](../../images/architecture-framework/data-model-and-protocols/where-artifacts-live.svg){ loading=lazy }
  <figcaption><span class="ekdn-fignum"></span> The four places an artifact can live.</figcaption>
</figure>

- **Published to the central CDN.** Fetched from Trust Infrastructure, once for
  everyone.
- **Hosted by the entity that owns it.** Fetched from the entity itself.
- **Answered rather than published.** Asked for one at a time and answered.
- **Carried in the exchange itself.** Never fetched at all.

## Published to the central CDN {#published-to-the-central-cdn}

Seven artifacts are published once for everyone: the five below, and the
Use Statement status list and the accreditation status list that
[Status list][status-list] covers. Trust Registry publishes all of them and puts
them behind a content delivery network (CDN), and every Module that needs one
keeps its own copy. None of them carries citizen data, and a static file behind
a CDN fails more gracefully than an interface does.

### Trusted list {#trusted-list}

- **Published by** Trust Registry, as a List of Trusted Entities (LoTE) JSON document signed with a [JSON
  Web Signature (JWS)][ref-rfc7515].
- **Read by** Issuer Core, Verifier Core, Mobile Wallet and Mobile Verifier,
  each from its own cached copy.
- **Where it lives** on the central CDN, as a static file anyone may fetch.
- **Lifetime** until the `NextUpdate` it carries, then discarded with no grace
  period, as ETSI TS 119 602 V1.1.1 requires. How that date is chosen is in
  [Trusted list and cache][trusted-list-and-cache].

Each entry names the legal body behind the entity and the intermediary
certificate authorities (CA) it issues from, so an RP Intermediary's
Verifier Issuing CA appears beside the entity itself.

The list answers one question: whether a party is accredited. Which key that party
signs with, and what it may do, are answered elsewhere, as
[three questions, three answers][three-questions-three-answers] sets out. The
key still comes from the DID Document or the certificate. The entry only names
any of the party's keys revoked early, with the time from which each is
revoked, so that a verifier can refuse a signature made with one.

The ecosystem publishes the LoTE JSON encoding only, and no XML trust-service
status list.

### Credential Rulebook {#credential-rulebook}

- **Published by** Trust Registry, from a Rulebook that a
  Credential Rulebook Provider proposed and the Root Authority approved.
- **Read by** Issuer Core to know what to build, Verifier Core to know what to
  expect and which attributes it may ask for at all, and Issuer Console to
  configure a credential type in the first place.
- **Where it lives** on the central CDN.
- **Lifetime** frozen the moment a version is published. A change becomes a new
  version rather than an edit.

The rules it holds are the schema, the attributes, the minimization class of
each attribute, the display metadata, the assurance demanded of the
credential key, and the assurance demanded of the issuer's signing key.

Freezing a version lets a cache be trusted. Where the Rulebook
sits among the three levels of rules is in
[The Credential Rulebook][the-credential-rulebook].

### Catalog list {#catalog-list}

- **Published by** Trust Registry, as a JSON Web Token (JWT) signed with
  Trust Authority's catalog key, beside the Rulebook files the list names.
- **Read by** Issuer Core, Verifier Core, Mobile Wallet and Mobile Verifier,
  each of which reads a Rulebook only through the list.
- **Where it lives** on the central CDN, at the catalog address the
  Governance Profile carries.
- **Lifetime** until its `exp`, then as a last-known-good copy up to the
  tolerance limit. Trust Registry publishes a new list whenever it publishes a
  Rulebook version, and before the current list expires.

A reader checks a Rulebook against the digest the list carries rather than
against a signature of its own, which lets a Rulebook be served as a plain
static file and still be trusted. What a Rulebook contains is in
[The Credential Rulebook][the-credential-rulebook].

### VICAL {#vical}

- **Published by** Trust Registry, as a `COSE_Sign1` structure defined in
  [ISO/IEC 18013-5:2021 Annex C][ref-iso-18013-5].
- **Read by** any mdoc verifier, including one operated in another country.
- **Where it lives** on the central CDN.
- **Lifetime** one day, on the publication interval the Governance Profile
  sets, with a cached copy good for the tolerance it allows past
  `nextUpdate`.

Verified Issuer Certificate Authority List (VICAL) exists for the verifier
that has no network: an offline verifier holding a cached copy accepts an mdoc
from an issuer it has never met, because the issuer's root is in the list and
the list is signed.

It is also the one artifact here written for verifiers outside the ecosystem as
well as inside it, which is how a verifier in another country can check an
Indonesian mdoc.

### Governance Profile {#governance-profile}

- **Published by** Trust Registry, as a JWS that Trust Authority signs with
  its Governance Profile key.
- **Read by** every Module that applies one of its values, each from its own
  cached copy, Trust Infrastructure's own Modules included.
- **Where it lives** on the central CDN, at the one address every Module is
  built with.
- **Lifetime** until the `next_update` it carries, plus seven days, after
  which a Module holding no newer edition refuses every check that depends on
  it.

What it holds is the version of each Technical Specification in force, the
algorithms each key may use, and the lifetimes, tolerances, and intervals.
Every edition is complete and carries a sequence number,
so a Module never applies half of one. The Root Authority approves what it says,
and where it sits among the levels of rules is in
[Data Model and Protocols](index.md). Its members and how a copy is read are in
[Publishing and reading the Governance Profile](../../technical-specifications/publishing-and-reading-the-governance-profile.md).

## Hosted by the entity that owns it {#hosted-by-the-entity-that-owns-it}

Two artifacts are served by the entity they describe, the DID Document and an
issuer's own status list, so neither depends on Trust Infrastructure being
reachable.

### DID Document {#did-document}

- **Published by** the entity, which signs each `did.jsonl` entry with its own
  update key and serves the file. Decentralized Identifier (DID) Service adds a witness proof to every new
  entry, and a resolver rejects an entry without one.
- **Read by** Issuer Core, Verifier Core, Mobile Wallet and Mobile Verifier,
  through the Trust SDK embedded in each.
- **Where it lives** at the entity's own domain rather than the central CDN,
  because [`did:webvh`][ref-did-webvh] v1.0 derives the address from the
  DID itself. DID Service keeps the copy it witnessed as a fallback.
- **Lifetime** versioned, with a history a resolver can follow through a key
  rotation.

DID Service witnesses and does not publish. `did:webvh:<scid>:kampus.ac.id`
resolves at that university's own domain. Only when
[the scheduled sync][trust-cache-sync] cannot reach that
domain does it read DID Service's copy of the log instead, and it checks that
copy's signatures exactly as it would the original. A merchant has none,
because it is never accredited and borrows its cryptographic identity from
the device certificate its RP Intermediary issues. How the identifiers are formed
is in [Identifier](identifier.md), and the two routes a verifier can
take to an anchor are in
[Two trust anchor paths][two-trust-anchor-paths].

### Status list {#status-list}

- **Published by** Issuer Core for the credentials an issuer signed, and Trust
  Registry for the Use Statements and the accreditations Trust Authority signed.
- **Read by** Verifier Core and Mobile Verifier for a credential, Mobile Wallet
  for the credentials it holds and for a Use Statement, and whoever is shown an
  Accreditation Credential.
- **Where it lives** at the issuer's own domain for an issuer's lists, and on
  the central CDN for the two Trust Registry
  publishes.
- **Lifetime** a time to live set by how much risk a stale answer carries.

The encoding follows [IETF Token Status List][ref-i-d-ietf-oauth-status-list] draft
-14 for SD-JWT-based Verifiable Credentials (SD-JWT VC) draft -13 and mdoc, and
[W3C Bitstring Status List][ref-bitstring-status-list] v1.0 for `ldp_vc`.

Four kinds exist. An issuer publishes one list for the credentials it issued
in SD-JWT VC and mdoc, and one more per purpose for those it issued in
`ldp_vc`, because a Bitstring Status List entry is one bit and revocation and
suspension are two purposes. Trust Registry publishes the list that revokes a
Use Statement and the list that revokes an Accreditation Credential. What is
revoked differs; the mechanism does not, and
[Publishing and reading a status list](../../technical-specifications/publishing-and-reading-a-status-list.md)
fixes all four.

Publishing it per issuer rather than centrally buys three things at once.
Revocation data scales with the number of issuers instead of accumulating
nationally. It survives an outage of Trust Infrastructure, because it never lived there.
And it keeps a count off Trust Infrastructure, since a national revocation service would
know how many credentials are in circulation.

It is also the only thing an issuer ever gives a verifier. The two never speak,
and a static file is all that passes between them.

## Answered rather than published {#answered-rather-than-published}

Two artifacts are no file at all. Neither is published like the seven
[published to the central CDN][published-to-the-central-cdn] nor carried like
the seven [carried in the exchange itself][carried-in-the-exchange-itself].
Each is asked for, one question at a time, and answered.

### Authority Statement {#authority-statement}

- **Published by** nobody. Trust Registry builds one for each query, and
  Trust Authority signs it with its Authority Statement key, from its own
  record of the permission the Root Authority granted.
- **Read by** any participant, through a [Trust Registry Query Protocol
  (TRQP)][ref-trqp] v2.0 query that Trust Registry
  answers, asked on the participant's [trust cache sync][trust-cache-sync].
- **Where it lives** in the answer to that query, and in the reader's cache
  after it. It is never a file and nobody hosts it.
- **Lifetime** from the `iat` to the `exp` it carries, then as a
  last-known-good copy up to the tolerance limit, past which a reader refuses
  it.

The answer is a token of type `vnd.id.idctf.authority-statement+jwt` that
Trust Authority signs. The permission itself stays in Trust Authority's record
until the Root Authority withdraws it.

Caching the signed answer lets a verifier check a permission
while Trust Registry is unreachable. What a statement covers, and how one is granted, is in
[Authorization][authorization].

### Recognition statement {#recognition-statement}

- **Published by** nobody. Trust Registry builds one for each query, and
  Trust Authority signs it with its recognition statement key, from its own
  record of the recognition the Root Authority decided.
- **Read by** Issuer Core, Verifier Core, Mobile Wallet and Mobile Verifier,
  through a TRQP query asked on the
  [trust cache sync][trust-cache-sync].
- **Where it lives** in the answer to that query, and in the reader's cache
  after it. It is never a file and nobody hosts it.
- **Lifetime** from the `iat` to the `exp` it carries, then as a
  last-known-good copy up to the tolerance limit.

The answer is a token of type `vnd.id.idctf.recognition-statement+jwt`. It
takes a key and a type of its own because it says nothing about any IDCTF
entity: it carries what the Root Authority accepts from outside, which
[Recognition][gf-recognition] governs. A verifier holding no usable statement
for an authority refuses the credential issued under it.

## Carried in the exchange itself {#carried-in-the-exchange-itself}

The remaining seven reach the party that needs them inside the exchange, rather
than being fetched from an address beforehand. Everything in this group except
the certificate revocation list (CRL) travels with the message that relies on
it, so it cannot be unreachable. What withdraws one is published, and is
fetched: the issuer's status list for a credential, the status lists that
revoke a Use Statement and an Accreditation Credential, Trust Authority's
CRLs, which Trust Registry serves, and each Verifier Issuing CA's, which its
holder serves at its own domain. A reader takes all of them on its
[trust cache sync][trust-cache-sync] and never during a transaction.

Three of the seven have three parties rather than two. A Key Attestation is carried by Mobile Wallet and read by
Issuer Core; a Verifier Device Certificate is carried by Mobile Verifier and
read by Mobile Wallet; a Use Statement is carried by whichever verifier the
request comes from and read by Mobile Wallet. In each case the artifact travels
to the party being vouched for and is read by the party on the other side of the
transaction, so for those three the Module that carries the artifact is not
the Module that reads it. The mechanism is in
[the operations group][the-operations-group].

### Use Statement {#use-statement}

- **Published by** Trust Authority, as a JWT of type
  `vnd.id.idctf.use-statement+jwt`, when the Root Authority approves one use.
- **Read by** Mobile Wallet, before it shows the consent screen, and by Verifier
  Console, which validates each request template against the use it names.
- **Where it lives** with the verifier, which attaches it to its own request: in
  the OpenID for Verifiable Presentations (OpenID4VP) 1.0 `verifier_info`
  parameter online, and in the `requestInfo` map of the ISO/IEC 18013-5
  `ItemsRequest` offline, under the key `idUseStatement`, as the same JWT
  wrapped in a byte string. Only the status list that revokes it sits on the
  central CDN.
- **Lifetime** until its `exp`, or until the Root Authority withdraws it and
  the status list Trust Registry publishes flips its bit.

A Use Statement records one registered use of one Relying Party: a `use_id`, the
purpose the citizen is shown, the legal basis behind it, and the list of
attributes that use may reach. That list is always a subset of what the entity's
[Authority Statement][authority-statement] allows, so the two together give a
ceiling per entity and a narrower limit per use. How a use is granted is in
[Registered use][registered-use].

The wallet does five things with it, all from its own cache and without a call
to Trust Infrastructure:

- it checks the signature against Trust Authority's key;
- it confirms the `sub` names the same party as the `client_id`, which for an
  accredited Relying Party is its own DID and for a merchant is its
  RP Intermediary, the entity holding the Verifier Issuing CA in `x5c` or
  `x5chain` where a certificate chain is presented;
- it confirms the statement has not expired or been revoked;
- it confirms the attributes requested are a subset of the ones the statement
  lists;
- it takes the purpose it displays from the statement rather than from the
  request.

Matching is attribute by attribute rather than by a hash over the whole query, so
a Relying Party can reword a request without invalidating its registration.

Carrying it rather than fetching it keeps Trust Infrastructure out of the
transaction. A wallet that had to resolve a registration at request time would
tell Trust Authority which citizen was dealing with which Relying Party every time
somebody presented a credential.

Proximity leaves no gap, because it carries the same statement: ReaderAuth signs
it along with the rest of the `ItemsRequest`, binding it to the session, and the
wallet runs the same checks against it that it runs online.

Only a wallet outside IDCTF that ignores `requestInfo` falls back to the
`ReaderAuthRole` in the certificate alone. That limit is a second bound
alongside the Use Statement offline rather than a substitute for it, because
every device carries a certificate there, where only a merchant carries one
online.

During the transition, a request that carries none at all is still served,
with the wallet warning the citizen that the request is not registered, until
the cut-off the Governance Profile sets.

### Accreditation Credential {#accreditation-credential}

- **Published by** Trust Authority, as an [SD-JWT VC][ref-i-d-ietf-oauth-sd-jwt-vc], when an accreditation is
  granted.
- **Read by** the entity it was issued to. Nothing in the ecosystem reads one,
  and a party outside it that is shown one decides on the trusted list.
- **Where it lives** with that entity, carried rather than published.
- **Lifetime** the accreditation period, with a `status` reference into the
  accreditation status list that ends it earlier.

### Key Attestation {#key-attestation}

- **Published by** Wallet Backend Service, as a JWT of type
  `key-attestation+jwt`, to each wallet installation.
- **Read by** Issuer Core, before it issues any credential.
- **Where it lives** with the Mobile Wallet installation it was issued to.
- **Lifetime** a day at most, one per issuance.

It carries the resistance values the Governance Profile maps assurance onto. A
Rulebook that asks only for `low` lowers the storage it accepts, not the need
for the attestation.

The refusal to mint is itself the revocation mechanism, and it reaches
issuance alone. An attestation is minted for one issuance and lives a day at
most, so an installation the Wallet Provider has disowned obtains no further
credential from its next issuance on, with no revocation list to distribute
and no message that has to arrive. The credentials it already holds
go on being presented: no verifier reads a Key Attestation, so reaching those is
the issuer's job, through the status list its own revocation sets.

### Verifier Device Certificate {#verifier-device-certificate}

- **Published by** the Verifier Core that answers for the device, as an
  [X.509][ref-rfc5280] certificate bound to
  one device and issued from that Verifier Core's own Verifier Issuing CA: an
  RP Intermediary's for a merchant's device, a Relying Party's own for its
  counter device.
- **Read by** Mobile Wallet, before it releases an attribute to that device.
- **Where it lives** on that device: with Mobile Verifier, or a
  Relying Party's own application built on the Reader SDK.
- **Lifetime** set by the Governance Profile, at most 1187 days, and
  withdrawn early through a CRL.

The `ReaderAuthRole` it carries makes that bound provable rather than merely
configured.

Before releasing an attribute, the wallet validates the chain up to the
Verifier Root CA, confirms the Verifier Issuing CA is on the trusted list, and
rejects any attribute outside the role in the certificate. Because the
certificate lives longer than a day it is withdrawn the ordinary X.509 way: the
issuing entity publishes a CRL and the wallet checks its cached copy. The
arrangement is set out in
[RP Intermediary and merchant](../roles/rp-intermediary-and-merchant.md).

### Credential {#credential}

- **Published by** Issuer Core, signed as a JWS, as [CBOR Object Signing and
  Encryption (COSE)][ref-rfc9052], or with a Data Integrity 1.0 proof,
  depending on the format.
- **Read by** Verifier Core and Mobile Verifier.
- **Where it lives** on the citizen's device, and in no register anywhere.
- **Lifetime** until its `exp` passes or its issuer revokes it.

The three formats are in
[three credential formats][three-credential-formats].

There is no directory of holders and no record that a given person holds a
given credential, so revocation is read from that issuer's status list rather
than from Trust Infrastructure.

### Presentation {#presentation}

- **Published by** Mobile Wallet, built from a credential when somebody asks.
- **Read by** Verifier Core or Mobile Verifier, once.
- **Where it lives** nowhere. A verifier keeps a digest of an online
  presentation for its archive, nothing derived from one in proximity, and
  never the attributes themselves.
- **Lifetime** one use, bound to one session.

The credential key the wallet controls binds it to the request, and binding it
to one session stops a captured presentation being replayed somewhere else.

### Document Signer Certificate, Verifier Issuing CA, and CRL {#document-signer-certificate-verifier-issuing-ca-and-crl}

- **Published by** Trust Authority, which issues all three.
- **Read by** Issuer Core, Verifier Core, Mobile Wallet and Mobile Verifier,
  through the Trust SDK.
- **Where it lives** with the entity's Key Manager and inside the `x5chain` of a
  message; the CRL at the address its certificates name, which Trust Registry
  serves.
- **Lifetime** a Document Signer Certificate at most 457 days for a mobile
  driving license (mDL) and at most 3650 days for any other document type; a
  Verifier Issuing CA the period the Governance Profile sets; a CRL carries a
  next update rather than a lifetime.

These three are the X.509 plumbing that holds the certificate chains together.

The CRL here is one of Trust Authority's two, one per root, and covers only
the certificates it issues. A
[Verifier Device Certificate][verifier-device-certificate] is withdrawn through
a CRL of its own.

Because the Verifier Issuing CA appears in the trusted list, a wallet can tell a
genuine RP Intermediary from an invented one. The two roots never sign each other,
and both chains are set out in
[Two trust anchor paths][two-trust-anchor-paths].
