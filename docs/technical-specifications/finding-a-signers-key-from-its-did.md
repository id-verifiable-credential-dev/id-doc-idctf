---
title: "[TS-01] Finding a signer's key from its DID"
description: How every JSON Web Signature IDCTF signs with a did:webvh or a did:key names its key, and how a reader finds that key, including the issuer signature mechanism of SD-JWT VC.
---

<!-- Sumber: tracks/0269, tracks/0270, tracks/0355, tracks/0368; SD-JWT VC draft -13 §3.5; publishing-and-resolving-a-did-webvh-identifier.md; deriving-a-did-key-and-a-device-identifier.md; publishing-and-reading-the-trusted-list.md -->

<p class="ekdn-docid">TS-01</p>

# Finding a signer's key from its DID {#ts-01-finding-a-signers-key-from-its-did}

<p class="ekdn-lead" markdown="span">
Most signers in the ecosystem are named by a Decentralized Identifier (DID),
and every token such a signer signs names the key it used. This specification fixes how
a token names that key, how a reader finds it, and which algorithm signs it,
once for every format and for both DID methods.
</p>

Every sentence on this page binds its targets, and an Assessment Body tests
them against it in the version the Governance Profile puts in force. The key
words and the identifier `REQ-TS-01-nnn` follow
[Common provisions](common-provisions.md).

## Who runs this and what it needs {#ts-01-who-runs-this-and-what-it-needs}

This specification binds every JSON Web Signature (JWS) the ecosystem signs
with a key named by a DID:

- Under `did:webvh`, a key of the signer's DID Document:
    - The issuer-signed JSON Web Token (JWT) of an SD-JWT-based Verifiable
      Credential (SD-JWT VC) draft -13.
    - The signed metadata of a credential issuer.
    - The Status List Token.
    - The Accreditation Credential.
    - The Authority Statement.
    - The Use Statement.
    - The Key Attestation.
    - The Request Object of a presentation request.
- Under `did:key`, a key that is its own identifier:
    - The trusted list.
    - The Governance Profile.

The specification applies alongside the specification of each of those
formats, which names the key the format is signed with and the time the token
states it was made.

Its conformance targets are three:

- A *signer*, every Module that signs one of those tokens: Issuer Core,
  Verifier Core, Wallet Backend Service, and Trust Authority.
- A *reader*, every Module that verifies one: Issuer Core, Verifier Core,
  Mobile Wallet, and Mobile Verifier, each through Trust SDK, and for the
  Governance Profile every reader
  [Publishing and reading the Governance Profile](publishing-and-reading-the-governance-profile.md)
  names.
- Issuer Core, for the one requirement that names it alone: how it signs an
  SD-JWT VC.

It leaves to other specifications:

- The profile of a `did:webvh`, its log, its DID Document, and the rules by
  which a reader resolves it, which
  [Publishing and resolving a did:webvh identifier](publishing-and-resolving-a-did-webvh-identifier.md)
  holds.
- How a `did:key` is encoded and decoded, which
  [Deriving a did:key and a device identifier](deriving-a-did-key-and-a-device-identifier.md)
  holds.
- The proofs on a log entry and the witness proofs, which are Data Integrity
  proofs and not JWS, and name their `did:key` in their own
  `verificationMethod`.
- The mdoc, which is verified through its certificate, as
  [Issuing and validating the X.509 certificates and the VICAL](issuing-and-validating-the-x509-certificates-and-the-vical.md)
  sets out.
- The Data Integrity proof of an `ldp_vc` credential.
- The key proof of a holder, which
  [Issuing and reading a Key Attestation](issuing-and-reading-a-key-attestation.md)
  holds.
- The proof of possession of a key a log entry publishes, a request at
  Trust Authority's entity endpoint with its countersignature, and the binding
  of a registration's first entry, which name a key no published DID Document or
  trusted list carries yet, or the update key, or are keyed by a registration
  code, and which
  [Witnessing a log entry and serving its copy](witnessing-a-log-entry-and-serving-its-copy.md)
  and
  [Onboarding an entity and registering its keys](onboarding-an-entity-and-registering-its-keys.md)
  check.

A Request Object a merchant device signs under `x509_hash` names its key by
certificate and is not in scope.

Before the first token, each conformance target holds what the rules below
assume:

- **A signer under `did:webvh`** holds:
    - Its key, in its Key Manager or, for Trust Authority, in the hardware
      security module its Certificate Authority Component drives.
    - That key, published in its DID Document under the purpose the format
      names.
- **A signer under `did:key`** holds a key the trusted list names in the
  service the format requires or, for the Governance Profile, a key an
  edition names in `signers`.
- **A reader** holds a verified copy of every log and of the trusted list,
  filled by the [trust cache sync][trust-cache-sync].

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-01-001 }**REQ-TS-01-001** A signer MUST meet every requirement on this page that names a signer, and every requirement on what a signer writes: the protected header of its token, the claims this page requires in it, and its signature.
- [](){ #req-ts-01-002 }**REQ-TS-01-002** A reader MUST meet every requirement on this page that names a reader.
- [](){ #req-ts-01-036 }**REQ-TS-01-036** Issuer Core MUST meet every requirement on this page that names Issuer Core.

</div>

## What a reader learns from the header {#ts-01-overview}

A token names its key in `kid`, as a DID or a DID URL. The method of that
DID tells the reader where the key is, as
[Finding the key][ts-01-finding-the-key] sets out, and nothing is fetched
during a transaction.

A DID gives no authority on its own: a `did:webvh` key signs for
its entity only when the DID Document lists it for the right purpose, and a
`did:key` signs only when the trusted list names it for that job.

## Signed header and the key it names {#ts-01-signed-header-and-the-key-it-names}

### A key named under did:webvh {#ts-01-a-key-named-under-did-webvh}

The credential status list of an issuer, as
[Publishing and reading a status list](publishing-and-reading-a-status-list.md)
publishes it, names its signer in `iss` and its key in `kid`:

``` { .json title="Protected header of the credential status list" data-format="JSON" }
{
  "typ": "statuslist+jwt",
  "alg": "ES256",
  "kid": "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id#status-list-1"
}
```

``` { .json title="Signer named in the claims" data-format="JSON" }
{
  "iss": "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id",
  "iat": 1792216800
}
```

The token was made at `iat`, 17 October 2026 06:00 UTC. The DID Document
version in force at that time is the second entry of the issuer's log, of
15 September 2026, as
[Publishing and resolving a did:webvh identifier](publishing-and-resolving-a-did-webvh-identifier.md)
shows it. That version lists the key the `kid` names, and lists it under
`assertionMethod`:

``` { .json title="Verification method the kid names" data-format="JSON" }
{
  "id": "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id#status-list-1",
  "type": "Multikey",
  "controller": "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id",
  "publicKeyMultibase": "zDnaeamPEKdV4VYmsDaPr9f3LyENGRFTwHRpoNvRLyi2gznvD"
}
```

The signature of the status list verifies under that public key. The
fragment `status-list-1` carries the purpose `status-list`, which is the
purpose the status list specification names for this token.

### A key named under did:key {#ts-01-a-key-named-under-did-key}

The trusted list, as
[Publishing and reading the trusted list](publishing-and-reading-the-trusted-list.md)
publishes it, carries no signer claim and names its key in `kid` alone:

``` { .json title="Protected header of the trusted list" data-format="JSON" }
{"alg":"ES256","kid":"did:key:zDnaeSCzChDqLTnobz1iquKetDC1piuwydzo3jkpiEHNwtX7q"}
```

The value after `did:key:z` decodes to the multicodec header of a P-256 public
key followed by the 33-byte compressed key, which is the key the signature is
checked with. The key is authorized because the Root Authority's entry in a list
the reader already verified names that same `did:key` in a trusted list signer
service at status `granted`:

``` { .json title="Trusted list signer service that names the key" data-format="JSON" }
{
  "ServiceInformation": {
    "ServiceTypeIdentifier": "https://idctf.id/ns/19602/SvcType/TrustedListSigner",
    "ServiceName": [
      { "lang": "id", "value": "Trusted list signer" },
      { "lang": "en", "value": "Trusted list signer" }
    ],
    "ServiceDigitalIdentity": {
      "OtherIds": ["did:key:zDnaeSCzChDqLTnobz1iquKetDC1piuwydzo3jkpiEHNwtX7q"]
    },
    "ServiceStatus": "https://idctf.id/ns/19602/SvcStatus/granted",
    "StatusStartingTime": "2026-01-01T00:00:00Z"
  }
}
```

## The signature and its algorithm {#ts-01-the-signature-and-its-algorithm}

A format specification names the key purpose and the algorithms that purpose
admits, and leaves the rest to this page.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-01-033 }**REQ-TS-01-033** The `alg` header parameter MUST name a digital signature algorithm.
- [](){ #req-ts-01-034 }**REQ-TS-01-034** The `alg` header parameter MUST NOT be `none`.
- [](){ #req-ts-01-035 }**REQ-TS-01-035** The signature MUST cover the encoded header and the encoded payload as [RFC 7515][ref-rfc7515] fixes.

</div>

An unsigned token carries no evidence of who made it, so a reader that
accepted `alg` set to `none` would take the payload on the word of whoever
delivered it.

## Naming the key {#ts-01-naming-the-key}

A signer names its key in `kid` by the method of the DID it signs under.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-01-003 }**REQ-TS-01-003** A signer MUST set the `kid` header parameter in every token in scope.
- [](){ #req-ts-01-004 }**REQ-TS-01-004** The protected header MUST NOT carry `x5c`, `x5u`, `jwk`, `jku`, or `trust_chain`.

</div>

A certificate or a raw key in the header would give a reader a second place
to find a key, and a token that a reader accepts through it would bypass the
trusted list.

### Under did:webvh {#ts-01-naming-under-did-webvh}

A signer names itself by its DID and its key by the identifier of the
verification method that holds it.

1. The signer takes the DID it is named by in the trusted list.
2. It takes the verification method of its current DID Document that holds
   the key of the purpose the format names.
3. It writes the DID in the token's signer claim, the method's `id` in
   `kid`, and signs.

The signer claim is `iss`, except in a Request Object, where it is
`client_id`, written with the `decentralized_identifier:` prefix of
[OpenID4VP 1.0][ref-openid4vp]. An Authority Statement carries no signer
claim: its signer is always Trust Authority, whose DID a reader holds from
build time, as
[Answering with an Authority Statement](answering-with-an-authority-statement.md)
sets out. Where this page says the signer's DID, for an Authority Statement
it means that DID.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-01-005 }**REQ-TS-01-005** A signer MUST write its own `did:webvh`, with no query and no fragment, in the signer claim of every format that has one.
- [](){ #req-ts-01-006 }**REQ-TS-01-006** A signer MUST set `kid` to the `id` of the verification method that holds the signing key.
- [](){ #req-ts-01-007 }**REQ-TS-01-007** The DID part of `kid`, before the `#`, MUST equal the signer's DID.
- [](){ #req-ts-01-008 }**REQ-TS-01-008** A signer MUST sign with a key listed under `assertionMethod` in its current DID Document.
- [](){ #req-ts-01-009 }**REQ-TS-01-009** A signer MUST sign with a key of the purpose the format specification names for the token.

</div>

### Under did:key {#ts-01-naming-under-did-key}

A signer under `did:key` is the key itself. It writes the `did:key` of its
key in `kid`, in the form the format specification fixes, and the token
names no other signer.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-01-010 }**REQ-TS-01-010** A signer MUST set `kid` to the `did:key` of the signing key, encoded as [Encoding][ts-5-03-encoding] requires.
- [](){ #req-ts-01-011 }**REQ-TS-01-011** A signer MUST sign under `did:key` only with a key the trusted list names in the service the format specification requires, at status `granted`, or, for the Governance Profile, with a key an edition names in `signers` at `granted`.

</div>

## Finding the key {#ts-01-finding-the-key}

A reader reads `kid`, takes the method of the DID it names, and finds the
key by that method. It refuses a token whose `kid` names any other method.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-01-012 }**REQ-TS-01-012** A reader MUST refuse a token whose `kid` is absent.
- [](){ #req-ts-01-013 }**REQ-TS-01-013** A reader MUST refuse a token whose `kid` names a DID of a method other than `did:webvh` or `did:key`.
- [](){ #req-ts-01-014 }**REQ-TS-01-014** A reader MUST refuse a token whose protected header carries `x5c`, `x5u`, `jwk`, `jku`, or `trust_chain`.
- [](){ #req-ts-01-015 }**REQ-TS-01-015** A reader MUST NOT take a key from any source other than the signer's DID Document under `did:webvh`, or the `did:key` itself under `did:key`.

</div>

### Under did:webvh {#ts-01-finding-under-did-webvh}

A reader finds the key in its cached copy of the signer's log.

1. It reads the signer's DID and refuses the token if the DID is not a
   `did:webvh`.
2. It checks that the DID part of `kid` equals the signer.
3. It takes, from its copy of the log, the DID Document version in force at
   the time the token states it was made.
4. It finds in that version the verification method whose `id` equals
   `kid`, listed under `assertionMethod`.
5. It checks that the purpose in the fragment is the purpose the format
   names, and that the trusted list does not name the key as revoked.
6. It verifies the signature with that key.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-01-016 }**REQ-TS-01-016** A reader MUST refuse a token whose signer's DID is not a `did:webvh` when the format names its signer by a `did:webvh`.
- [](){ #req-ts-01-017 }**REQ-TS-01-017** A reader MUST refuse a token whose `kid` names a DID other than the signer's.
- [](){ #req-ts-01-018 }**REQ-TS-01-018** A reader MUST resolve the signer's DID from its cached copy of the log, as [Resolving][ts-5-02-resolving] requires.
- [](){ #req-ts-01-031 }**REQ-TS-01-031** A reader MUST NOT fetch the signer's DID during the transaction.
- [](){ #req-ts-01-019 }**REQ-TS-01-019** A reader MUST take the key from the DID Document version in force at the time the token states it was made, as [REQ-TS-5-02-065][req-ts-5-02-065] requires.
- [](){ #req-ts-01-020 }**REQ-TS-01-020** A reader MUST refuse a token whose `kid` matches no verification method of that version.
- [](){ #req-ts-01-021 }**REQ-TS-01-021** A reader MUST refuse a token whose key that version does not list under `assertionMethod`.
- [](){ #req-ts-01-022 }**REQ-TS-01-022** A reader MUST refuse a token whose key is of a purpose other than the one the format specification names.
- [](){ #req-ts-01-023 }**REQ-TS-01-023** A reader MUST refuse a token whose key the trusted list names as revoked, as [REQ-TS-5-02-067][req-ts-5-02-067] requires.

</div>

### Under did:key {#ts-01-finding-under-did-key}

A reader decodes the key from `kid` and accepts it only where the trusted list
gives it the job.

1. It decodes the `did:key` in `kid` locally, as
   [Encoding][ts-5-03-encoding] sets out.
2. It checks that the format specification allows a `did:key` signer for
   this token. For the trusted list, the key must be the one the reader
   carries from build time, or one that a list it already verified names in a
   trusted list signer service at status `granted`, as
   [REQ-TS-5-01-067][req-ts-5-01-067] requires.
3. It verifies the signature with that key.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-01-024 }**REQ-TS-01-024** A reader MUST decode a `did:key` in `kid` locally, as [REQ-TS-5-03-007][req-ts-5-03-007] requires.
- [](){ #req-ts-01-032 }**REQ-TS-01-032** A reader MUST NOT resolve a `did:key` in `kid` over the network.
- [](){ #req-ts-01-025 }**REQ-TS-01-025** A reader MUST refuse a token signed under `did:key` when its format specification names its signer by a `did:webvh`.
- [](){ #req-ts-01-026 }**REQ-TS-01-026** A reader MUST accept a signature under `did:key` only from a key the format specification accepts for that token.

</div>

## The issuer signature mechanism of SD-JWT VC {#ts-01-the-issuer-signature-mechanism-of-sd-jwt-vc}

[SD-JWT VC][ref-i-d-ietf-oauth-sd-jwt-vc] section 3.5 has a
recipient find the issuer's key through an issuer signature mechanism that
its policy permits, and rejects the credential when it cannot. The draft
defines two, JWT VC Issuer Metadata for an `https` `iss` and X.509
certificates in `x5c`, and lets an ecosystem define others. IDCTF defines
one, the *DID issuer signature mechanism*: `iss` is the issuer's `did:webvh`,
and the key is found as [Under did:webvh][ts-01-finding-under-did-webvh] sets out,
under the purpose `issuance-jose`. It is the only mechanism the ecosystem
permits.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-01-027 }**REQ-TS-01-027** Issuer Core MUST sign the issuer-signed JWT of an SD-JWT VC under the DID issuer signature mechanism.
- [](){ #req-ts-01-028 }**REQ-TS-01-028** The issuer-signed JWT of an SD-JWT VC MUST carry `iss`.
- [](){ #req-ts-01-029 }**REQ-TS-01-029** A reader MUST NOT find an SD-JWT VC issuer's key through JWT VC Issuer Metadata or through X.509 certificates.
- [](){ #req-ts-01-030 }**REQ-TS-01-030** A reader MUST reject an SD-JWT VC whose issuer key it cannot find under the DID issuer signature mechanism.

</div>

`iss` is optional in the draft, which lets the subject of an `x5c`
certificate name the issuer instead. Here no certificate travels, so `iss`
is the only place the issuer is named. A wallet or verifier from outside
the ecosystem that permits only the two mechanisms of the draft cannot find
the key of an IDCTF credential, so recognition of another ecosystem works
only if it carries this mechanism.

## Security considerations {#ts-01-security-considerations}

- **A token that names one signer and another signer's key.** Without the
  check that `kid` names the signer's own DID, a reader that trusts the
  first signer would accept a signature made by the second,
  [REQ-TS-01-007][req-ts-01-007] and [REQ-TS-01-017][req-ts-01-017].
- **A key published for one job used for another.** A stolen status list
  key cannot sign a credential, because [REQ-TS-01-009][req-ts-01-009] and
  [REQ-TS-01-022][req-ts-01-022] require a key of the purpose the format
  names.
- **A key withdrawn early, or a backdated token.** The key comes from the
  DID Document version in force at signing time, which keeps a retired key
  valid for what it signed. A key the trusted list names as revoked is
  refused whatever time the token claims,
  [REQ-TS-01-019][req-ts-01-019] and [REQ-TS-01-023][req-ts-01-023].
- **A second place to find a key.** A certificate or a raw key in the
  header would let a token bypass the trusted list,
  [REQ-TS-01-004][req-ts-01-004], [REQ-TS-01-014][req-ts-01-014], and
  [REQ-TS-01-015][req-ts-01-015].
- **A `did:key` anyone can make.** A `did:key` proves which key signed and
  nothing more; its authority comes only from the trusted list, so a reader
  accepts it only where the format specification accepts that key,
  [REQ-TS-01-011][req-ts-01-011] and [REQ-TS-01-026][req-ts-01-026].
- **A resolver that hands over a different key.** The reader decodes a
  `did:key` itself and resolves a `did:webvh` from its own cache, never over
  the network during a transaction, [REQ-TS-01-018][req-ts-01-018],
  [REQ-TS-01-024][req-ts-01-024], [REQ-TS-01-031][req-ts-01-031], and
  [REQ-TS-01-032][req-ts-01-032].

## Privacy considerations {#ts-01-privacy-considerations}

A reader resolves from its cache and never asks the signer for its key
during a transaction, so an issuer cannot learn from a key request when,
where, or to whom its credential was presented.

## Changelog {#ts-01-changelog}

<figure markdown="1" class="ekdn-table">

| Version | Date | Change |
|---|---|---|
| 1.0 draft | 21 October 2026 | First draft |

</figure>
