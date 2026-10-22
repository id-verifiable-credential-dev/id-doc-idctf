---
title: "[TS-5-09] Publishing and reading a status list"
description: The status lists the ecosystem publishes, their encoding and their signatures, where each one is hosted, how often it is republished, and how a reader reads one entry from a cached copy.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, Kep. 11, §4.6, §7.7; Rincian Module dan Operasi §4, §7; JWT di OpenID4VCI dan OpenID4VP §5; Bentuk Data Attestation §4; tracks/0345, tracks/0346 -->

<p class="ekdn-docid">TS-5-09</p>

# Publishing and reading a status list {#ts-5-09-publishing-and-reading-a-status-list}

<p class="ekdn-lead" markdown="span">
A status list is one compressed array of bits, signed and published whole, in
which one entry says whether one artifact is still good. Four kinds exist.
They are what ends a credential, a registered use, or an accreditation before
the date written inside it.
</p>

Every sentence on this page binds Issuer Core and Trust Registry, which publish
these lists, Trust Authority, which signs the two Trust Registry publishes,
and every Module that reads one, and an Assessment Body tests them
against it in the version the Governance Profile puts in force. The key words
and the identifier `REQ-TS-5-09-nnn` follow
[Common provisions](common-provisions.md).

## Who runs this and what it needs {#ts-5-09-who-runs-this-and-what-it-needs}

This specification fixes the status lists of the ecosystem:

- How the bits are packed and compressed.
- What each value means.
- The token the array is published inside.
- The signature on it.
- Where it is hosted.
- How often it is republished.
- How a reader reads one entry out of a cached copy.

It fixes one encoding for the three lists that cover JSON Web Token artifacts
and one for the list that covers `ldp_vc` credentials.

Its conformance targets are:

- Issuer Core.
- Trust Registry.
- Trust Authority.
- The Modules that read one: Mobile Wallet, Mobile Verifier, and Verifier
  Core.

A reader meets its requirements through Trust SDK where the library performs
the check.

It leaves to other documents:

- Which registered use a given index stands for and what a reader does when
  that index is set, which
  [Registering and carrying a Use Statement](registering-and-carrying-a-use-statement.md)
  holds.
- Which accreditation a given index stands for and what a reader does when
  that index is set, which
  [Issuing and carrying an Accreditation Credential](issuing-and-carrying-an-accreditation-credential.md)
  holds.
- The formats a credential is issued in and the `status` claim an
  SD-JWT-based Verifiable Credential (SD-JWT VC) draft -13 or an mdoc
  carries, which
  [Issuing a credential in SD-JWT VC, mdoc, and `ldp_vc`](issuing-a-credential-in-sd-jwt-vc-mdoc-and-ldp-vc.md)
  holds.
- The Time to Live (TTL) of each list, the tolerance limit past which a
  cached copy is refused, and the republication interval, which the
  Governance Profile holds.
- [The grounds on which a status is changed][gf-grounds], which the
  Governance Framework holds.
- The keys that sign the lists and the logs they live in, which
  [Publishing and resolving a did:webvh identifier](publishing-and-resolving-a-did-webvh-identifier.md)
  holds.

Before the first publication, each target holds what the rules below assume:

- **Issuer Core** holds the `status-list` key of its entity, an index for every
  credential it has issued, and its own domain to publish from.
- **Trust Registry** holds an index for every registered use and every
  accredited registration, and reaches the two keys that sign those lists
  through Trust Authority.
- **A reader** holds a cached copy of each list it needs, with the time it was
  fetched, and resolves the publisher's Decentralized Identifier (DID) Document
  to check the signature on it.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-09-001 }**REQ-TS-5-09-001** Issuer Core MUST meet every requirement that names a publisher, wherever it stands on this page, except one that names Trust Registry or Trust Authority.
- [](){ #req-ts-5-09-002 }**REQ-TS-5-09-002** Trust Registry MUST meet every requirement that names a publisher or names Trust Registry, wherever it stands on this page, except one that names the `ldp_vc` list.
- [](){ #req-ts-5-09-003 }**REQ-TS-5-09-003** Mobile Wallet, Mobile Verifier, and Verifier Core MUST each meet every requirement that names a reader, wherever it stands on this page.
- [](){ #req-ts-5-09-088 }**REQ-TS-5-09-088** A party that acts on an Accreditation Credential MUST meet every requirement that names a reader when it reads the accreditation status list, as [REQ-TS-5-07-003][req-ts-5-07-003] requires of it.
- [](){ #req-ts-5-09-079 }**REQ-TS-5-09-079** Trust Authority MUST meet every requirement in [Signature][ts-5-09-signature] that names it.

</div>

## The four lists {#ts-5-09-the-four-lists}

Every list works the same way and they differ in three things: who publishes
it, how wide an entry is, and which key signs it.
[The table of status lists][tbl-ts-5-09-lists] gives all four.

[](){ #tbl-ts-5-09-lists }

<figure markdown="1" class="ekdn-table">

| List | Published by | Read by | Covers | Bits | Key |
|---|---|---|---|---|---|
| Credential status list | Issuer Core, on the issuer's own domain | Mobile Wallet, Verifier Core, Mobile Verifier | The credentials that issuer issued in SD-JWT VC or mdoc, served in the JWT form and, where the entity issues in mdoc, in the CWT form as well | 2 | The entity's `status-list` key |
| `ldp_vc` status list | Issuer Core, on the issuer's own domain | Mobile Wallet, Verifier Core, Mobile Verifier | The credentials that issuer issued in `ldp_vc`, one list per purpose | 1 | The entity's `status-list` key |
| Use Statement status list | Trust Registry, on the central CDN | Mobile Wallet | The registered uses Trust Authority has signed | 1 | Trust Authority's Use Statement status list key |
| Accreditation status list | Trust Registry, on the central CDN | A party shown an Accreditation Credential | The accreditations the Root Authority has granted | 2 | Trust Authority's accreditation status list key |

</figure>

An issuer publishes its own lists rather than handing them to Trust
Infrastructure, so that nobody at the center learns how many credentials are in
circulation or how often one citizen's credential is checked. The central
content delivery network (CDN) is the host the Governance Profile names,
`registry.trust.go.id` in
[The lists as published][ts-5-09-the-lists-as-published]. The two lists Trust
Registry publishes cover artifacts that are already public, so hosting them
centrally reveals nothing that the trusted list does not.

A list is published whole. No endpoint answers a question about one index,
because an answer about one index would name the artifact a reader is
interested in. Nothing in the
ecosystem consumes an aggregation of lists either, so none is published.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-09-004 }**REQ-TS-5-09-004** Issuer Core MUST publish its status lists on a domain of the entity that runs it.
- [](){ #req-ts-5-09-005 }**REQ-TS-5-09-005** Issuer Core MUST NOT publish a status list through Trust Registry or through the central CDN.
- [](){ #req-ts-5-09-006 }**REQ-TS-5-09-006** Trust Registry MUST publish the Use Statement status list and the accreditation status list on the central CDN.
- [](){ #req-ts-5-09-007 }**REQ-TS-5-09-007** A publisher MUST serve a status list whole.
- [](){ #req-ts-5-09-008 }**REQ-TS-5-09-008** A publisher MUST NOT offer an interface that answers the status of one index.
- [](){ #req-ts-5-09-009 }**REQ-TS-5-09-009** A publisher MUST NOT require authentication, authorization, or a client identifier to fetch a status list.

</div>

## The lists as published {#ts-5-09-the-lists-as-published}

The four lists below are an illustration: the issuers, the domains, the keys,
and the indices are invented, and no credential has been issued. Every field is
exact. Each was signed with the key its `kid` or its `verificationMethod`
names, each signature
verifies, and each array decodes to the entries described beneath it, so an
implementation can decompress these lists and find what the clauses below
require.

The lists agree with the other examples on two points:

- The entities are the ones [the trusted list][ts-5-01-trusted-list-payload]
  carries, with the same DIDs.
- The indices are the ones
  [Registering and carrying a Use Statement](registering-and-carrying-a-use-statement.md)
  and
  [Issuing and carrying an Accreditation Credential](issuing-and-carrying-an-accreditation-credential.md)
  name.

An issuer's credential status list, two bits per entry, with index 481920
valid, 481921 invalid, and 481922 suspended:

``` { .text title="Credential status list, as served" data-format="JWT" }
eyJ0eXAiOiJzdGF0dXNsaXN0K2p3dCIsImFsZyI6IkVTMjU2Iiwia2lkIjoiZGlkOndlYnZoOlFtY0VWVDJpSlNyc3M1aGd3aU1Gc01VeEtrUm96Z0ZGNDU4UmNnZ1Q0TUYyTDQ6ZHVrY2FwaWwuZ28uaWQjc3RhdHVzLWxpc3QtMSJ9.eyJpc3MiOiJkaWQ6d2Vidmg6UW1jRVZUMmlKU3JzczVoZ3dpTUZzTVV4S2tSb3pnRkY0NThSY2dnVDRNRjJMNDpkdWtjYXBpbC5nby5pZCIsInN1YiI6Imh0dHBzOi8vZHVrY2FwaWwuZ28uaWQvc3RhdHVzL2t0cC03IiwiaWF0IjoxNzkyMjE2ODAwLCJleHAiOjE3OTQ4MDg4MDAsInR0bCI6NDMyMDAsInN0YXR1c19saXN0Ijp7ImJpdHMiOjIsImxzdCI6ImVOcnQwREVCQUFBTUFpREQyRC1qOXpJTUlwQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFNQmZWUUFBQUFBQUFBQUFBQUJ3RE5IcEFDVSJ9fQ.xKRMUIwvpQWlnI8QJGGwRpKtub9qZYCLd54pey6p0OuJsM6EkL6aXrYd_sr_wOjwA-Y_KOcaPA7f1eHJ1yoP0g
```

``` { .json title="Credential status list claims" data-format="JSON" }
{
  "iss": "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id",
  "sub": "https://dukcapil.go.id/status/ktp-7",
  "iat": 1792216800,
  "exp": 1794808800,
  "ttl": 43200,
  "status_list": {
    "bits": 2,
    "lst": "eNrt0DEBAAAMAiDD2D-j9zIMIpAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMBfVQAAAAAAAAAAAABwDNHpACU"
  }
}
```

The credential status list of an issuer that has revoked nothing, at the
address its Kartu ASN credentials point at, in which index 481920 is valid:

``` { .text title="Kartu ASN status list, as served" data-format="JWT" }
eyJ0eXAiOiJzdGF0dXNsaXN0K2p3dCIsImFsZyI6IkVTMjU2Iiwia2lkIjoiZGlkOndlYnZoOlFtZThScmlHbkt4NWoyUWpvYVkxU2dSU3B4VEhkanExMUwyRXhneTF6VjJ4c0o6YmtuLmdvLmlkI3N0YXR1cy1saXN0LTEifQ.eyJpc3MiOiJkaWQ6d2Vidmg6UW1lOFJyaUduS3g1ajJRam9hWTFTZ1JTcHhUSGRqcTExTDJFeGd5MXpWMnhzSjpia24uZ28uaWQiLCJzdWIiOiJodHRwczovL2Jrbi5nby5pZC9zdGF0dXMva2FydHUtYXNuLTEiLCJpYXQiOjE3OTIyMTY4MDAsImV4cCI6MTc5NDgwODgwMCwidHRsIjo0MzIwMCwic3RhdHVzX2xpc3QiOnsiYml0cyI6MiwibHN0IjoiZU5ydHdURUJBQUFBd3FEMVQtMWhEYUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBYmdBZUFBRSJ9fQ.hDYEzpgsvch0jthCX8N7IIkETKkSM3P_eufwqWO9a3XX0hU5lvEWOl50THRdULVHW3aKQldJO2p93zzjNCqbcQ
```

``` { .json title="Kartu ASN status list claims" data-format="JSON" }
{
  "iss": "did:webvh:Qme8RriGnKx5j2QjoaY1SgRSpxTHdjq11L2Exgy1zV2xsJ:bkn.go.id",
  "sub": "https://bkn.go.id/status/kartu-asn-1",
  "iat": 1792216800,
  "exp": 1794808800,
  "ttl": 43200,
  "status_list": {
    "bits": 2,
    "lst": "eNrtwTEBAAAAwqD1T-1hDaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAbgAeAAE"
  }
}
```

The Use Statement status list, one bit per entry, in which the five statements
[Registering and carrying a Use Statement](registering-and-carrying-a-use-statement.md)
carries are valid and index 2077 is invalid:

``` { .text title="Use Statement status list, as served" data-format="JWT" }
eyJ0eXAiOiJzdGF0dXNsaXN0K2p3dCIsImFsZyI6IkVTMjU2Iiwia2lkIjoiZGlkOndlYnZoOlFtWmp5MXQ5b0ZpYUZqaFgyZTM4dU11UjdtZ3RkTGpIUE1HZmpFZnZyc21haXE6dHJ1c3QuZ28uaWQjdXNlLXN0YXRlbWVudC1zdGF0dXMtbGlzdC0xIn0.eyJpc3MiOiJkaWQ6d2Vidmg6UW1aankxdDlvRmlhRmpoWDJlMzh1TXVSN21ndGRMakhQTUdmakVmdnJzbWFpcTp0cnVzdC5nby5pZCIsInN1YiI6Imh0dHBzOi8vcmVnaXN0cnkudHJ1c3QuZ28uaWQvc3RhdHVzL3VzZS1zdGF0ZW1lbnRzLTEiLCJpYXQiOjE3OTIyMTY4MDAsImV4cCI6MTc5NDgwODgwMCwidHRsIjo0MzIwMCwic3RhdHVzX2xpc3QiOnsiYml0cyI6MSwibHN0IjoiZU5ydDBERUJBQUFNQWlDajJELWxNWFlNSXBDOFZ3VUFBQUFBQUFBQUFBQUFBQUFBQUFCY0d5QVlBQ0UifX0.l69W6WMRKbvpBo001Rov0ZPd4YkQApzJb8IMCr-WB-XC5zB_V_K_tlXyh9jiO1aXOsL7PQKb-Xv4FhWz-z3QRA
```

``` { .json title="Use Statement status list claims" data-format="JSON" }
{
  "iss": "did:webvh:QmZjy1t9oFiaFjhX2e38uMuR7mgtdLjHPMGfjEfvrsmaiq:trust.go.id",
  "sub": "https://registry.trust.go.id/status/use-statements-1",
  "iat": 1792216800,
  "exp": 1794808800,
  "ttl": 43200,
  "status_list": {
    "bits": 1,
    "lst": "eNrt0DEBAAAMAiCj2D-lMXYMIpC8VwUAAAAAAAAAAAAAAAAAAABcGyAYACE"
  }
}
```

The accreditation status list, two bits per entry, in which the three
registrations
[Issuing and carrying an Accreditation Credential](issuing-and-carrying-an-accreditation-credential.md)
carries are valid, index 23 is invalid, and index 31 is suspended:

``` { .text title="Accreditation status list, as served" data-format="JWT" }
eyJ0eXAiOiJzdGF0dXNsaXN0K2p3dCIsImFsZyI6IkVTMjU2Iiwia2lkIjoiZGlkOndlYnZoOlFtWmp5MXQ5b0ZpYUZqaFgyZTM4dU11UjdtZ3RkTGpIUE1HZmpFZnZyc21haXE6dHJ1c3QuZ28uaWQjYWNjcmVkaXRhdGlvbi1zdGF0dXMtbGlzdC0xIn0.eyJpc3MiOiJkaWQ6d2Vidmg6UW1aankxdDlvRmlhRmpoWDJlMzh1TXVSN21ndGRMakhQTUdmakVmdnJzbWFpcTp0cnVzdC5nby5pZCIsInN1YiI6Imh0dHBzOi8vcmVnaXN0cnkudHJ1c3QuZ28uaWQvc3RhdHVzL2FjY3JlZGl0YXRpb25zLTEiLCJpYXQiOjE3OTIyMTY4MDAsImV4cCI6MTc5NDgwODgwMCwidHRsIjo0MzIwMCwic3RhdHVzX2xpc3QiOnsiYml0cyI6MiwibHN0IjoiZU5ydHdRRUJBREFJd0tCRk05cWphNDhEZGFZWEFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBSHhzQVlEZ0FNRSJ9fQ.JX3cKeo9uUAAs8WwBjLKIdBd3IuWLSmKnH6hDhQHvL-Q9VTuq_SBEisDGhkPvQAhOy_cWCDijBaOT2IbIS-TBg
```

``` { .json title="Accreditation status list claims" data-format="JSON" }
{
  "iss": "did:webvh:QmZjy1t9oFiaFjhX2e38uMuR7mgtdLjHPMGfjEfvrsmaiq:trust.go.id",
  "sub": "https://registry.trust.go.id/status/accreditations-1",
  "iat": 1792216800,
  "exp": 1794808800,
  "ttl": 43200,
  "status_list": {
    "bits": 2,
    "lst": "eNrtwQEBADAIwKBFM9qja48DdaYXAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHxsAYDgAME"
  }
}
```

The lists below are those
of the Ministry of Religious Affairs, which issues the Kartu Nikah in
`ldp_vc`; each holds 524288 entries, index 94721 is revoked, and every other
entry is valid:

``` { .json title="Bitstring Status List credential, revocation purpose" data-format="JSON-LD" }
{
  "@context": [
    "https://www.w3.org/ns/credentials/v2"
  ],
  "id": "https://kemenag.go.id/status/kartu-nikah-1-revocation",
  "type": [
    "VerifiableCredential",
    "BitstringStatusListCredential"
  ],
  "issuer": "did:webvh:QmbAb7u9RMjqsZ9L98pe47szJZdnKQLh9KizqNW2WwKac1:kemenag.go.id",
  "validFrom": "2026-10-17T06:00:00Z",
  "validUntil": "2026-11-16T06:00:00Z",
  "credentialSubject": {
    "id": "https://kemenag.go.id/status/kartu-nikah-1-revocation#list",
    "type": "BitstringStatusList",
    "statusPurpose": "revocation",
    "encodedList": "uH4sIAAAAAAAC_-3QgQAAAAwCsNDypwrhAN8QlgAAAAAAAAAAAAAA8EEVAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIcBmv3GRwAAAQA"
  },
  "proof": {
    "type": "DataIntegrityProof",
    "cryptosuite": "ecdsa-rdfc-2019",
    "created": "2026-10-17T06:00:00Z",
    "verificationMethod": "did:webvh:QmbAb7u9RMjqsZ9L98pe47szJZdnKQLh9KizqNW2WwKac1:kemenag.go.id#status-list-1",
    "proofPurpose": "assertionMethod",
    "proofValue": "z5AuBTuDiDWRXVY2Y6umFM9D1E426xjQEYmhxw2DmrRV9SaGfPceSLexR24o9yvPUFtEQWJUigMtHpxBdwgRHKynR"
  }
}
```

The suspension list of the same credentials, in which no entry is set:

``` { .json title="Bitstring Status List credential, suspension purpose" data-format="JSON-LD" }
{
  "@context": [
    "https://www.w3.org/ns/credentials/v2"
  ],
  "id": "https://kemenag.go.id/status/kartu-nikah-1-suspension",
  "type": [
    "VerifiableCredential",
    "BitstringStatusListCredential"
  ],
  "issuer": "did:webvh:QmbAb7u9RMjqsZ9L98pe47szJZdnKQLh9KizqNW2WwKac1:kemenag.go.id",
  "validFrom": "2026-10-17T06:00:00Z",
  "validUntil": "2026-11-16T06:00:00Z",
  "credentialSubject": {
    "id": "https://kemenag.go.id/status/kartu-nikah-1-suspension#list",
    "type": "BitstringStatusList",
    "statusPurpose": "suspension",
    "encodedList": "uH4sIAAAAAAAC_-3BAQEAAACAkP6v7ggKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAauuOl9cAAAEA"
  },
  "proof": {
    "type": "DataIntegrityProof",
    "cryptosuite": "ecdsa-rdfc-2019",
    "created": "2026-10-17T06:00:00Z",
    "verificationMethod": "did:webvh:QmbAb7u9RMjqsZ9L98pe47szJZdnKQLh9KizqNW2WwKac1:kemenag.go.id#status-list-1",
    "proofPurpose": "assertionMethod",
    "proofValue": "z5DvyCm7eroKFiHCwjKKynQ7gqiKfvDgPoZHRgW6XzYfycLAfjBA8a2oZpgMUcTWmZ4iLSQRCtxM3CNfsgDUA2AJf"
  }
}
```

A credential in `ldp_vc` points into both with a `credentialStatus` entry, one
per purpose. The Kartu Nikah below sits at index 481920, which is clear in
both lists, so it is valid:

``` { .json title="The credentialStatus entries of an ldp_vc credential" data-format="JSON" }
[
  {
    "id": "https://kemenag.go.id/status/kartu-nikah-1-revocation#481920",
    "type": "BitstringStatusListEntry",
    "statusPurpose": "revocation",
    "statusListIndex": "481920",
    "statusListCredential": "https://kemenag.go.id/status/kartu-nikah-1-revocation"
  },
  {
    "id": "https://kemenag.go.id/status/kartu-nikah-1-suspension#481920",
    "type": "BitstringStatusListEntry",
    "statusPurpose": "suspension",
    "statusListIndex": "481920",
    "statusListCredential": "https://kemenag.go.id/status/kartu-nikah-1-suspension"
  }
]
```

## Format {#ts-5-09-format}

The three lists that cover JSON Web Token (JWT) artifacts are published as a
Status List Token in JWT format, which
[IETF Token Status List draft -14][ref-i-d-ietf-oauth-status-list] defines as a
JSON Web Signature in compact serialization, [RFC 7515][ref-rfc7515], over a
claims set, [RFC 7519][ref-rfc7519]. Of the claims in
[the table of claims][tbl-ts-5-09-claims], `iss` is the one the standard does
not define for a Status List Token; the ecosystem adds it so that a reader
resolves the signing key from the token itself.

[](){ #tbl-ts-5-09-claims }

<figure markdown="1" class="ekdn-table">

| Claim | Type | Presence | What it carries |
|---|---|---|---|
| `iss` | string | Present | The `did:webvh` of the entity that publishes the list |
| `sub` | string | Present | The address the list is published at, the same string an artifact points at |
| `iat` | number | Present | The moment this copy of the list was issued |
| `exp` | number | Present | The moment this copy is considered expired by its publisher |
| `ttl` | number | Present | The seconds a reader may use this copy before fetching a fresh one |
| `status_list` | object | Present | The array itself, as `bits` and `lst` |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-09-010 }**REQ-TS-5-09-010** A status list over JSON Web Token artifacts MUST be published as a Status List Token in JWT format.
- [](){ #req-ts-5-09-011 }**REQ-TS-5-09-011** The `typ` header parameter MUST be `statuslist+jwt`.
- [](){ #req-ts-5-09-012 }**REQ-TS-5-09-012** The `alg` header parameter MUST be one the Governance Profile allows for the signing key.
- [](){ #req-ts-5-09-013 }**REQ-TS-5-09-013** The `kid` header parameter MUST name the publisher's signing key, as [Naming the key][ts-01-naming-the-key] of TS-01 requires.
- [](){ #req-ts-5-09-014 }**REQ-TS-5-09-014** A publisher MUST include every claim [the table of claims][tbl-ts-5-09-claims] lists.
- [](){ #req-ts-5-09-015 }**REQ-TS-5-09-015** `sub` MUST be the address the list is published at, byte for byte the string the artifacts covered by it carry.
- [](){ #req-ts-5-09-016 }**REQ-TS-5-09-016** `status_list` MUST carry `bits` and `lst`.
- [](){ #req-ts-5-09-017 }**REQ-TS-5-09-017** A publisher MUST NOT include `aggregation_uri`.
- [](){ #req-ts-5-09-080 }**REQ-TS-5-09-080** A publisher MUST NOT publish an aggregation of its status lists.
- [](){ #req-ts-5-09-018 }**REQ-TS-5-09-018** Trust Registry MUST NOT publish the Use Statement status list or the accreditation status list in Concise Binary Object Representation (CBOR) Web Token (CWT) format.
- [](){ #req-ts-5-09-019 }**REQ-TS-5-09-019** A reader MUST refuse a token whose `typ` is not `statuslist+jwt`.
- [](){ #req-ts-5-09-020 }**REQ-TS-5-09-020** A reader MUST refuse a token whose `sub` is not the address the artifact it is checking names.

</div>

## The byte array {#ts-5-09-the-byte-array}

A reader tells one list from another by the address it fetched it from and by
the `sub` inside it, which is the same string; nothing inside the array says
which list it is.

`lst` is the array of statuses, packed, compressed, and encoded in the order
[IETF Token Status List][ref-i-d-ietf-oauth-status-list] fixes:

- each index addresses a block of `bits` bits;
- blocks are packed into each byte from the least significant bit upward;
- the byte array is compressed with DEFLATE in the ZLIB data format;
- the result is base64url encoded without padding, as
  [RFC 4648][ref-rfc4648] defines it.

How wide an entry is follows from how many states the artifact has.
[The table of status values][tbl-ts-5-09-values] gives the values in use.

[](){ #tbl-ts-5-09-values }

<figure markdown="1" class="ekdn-table">

| Value | Name | What it says | Used by |
|---|---|---|---|
| `0x00` | Valid | The artifact has not been revoked or suspended | Every list |
| `0x01` | Invalid | The artifact is revoked, and the decision is final | Every Status List Token, and the Bitstring revocation list |
| `0x02` | Suspended | The artifact is set aside while a doubt is resolved, and may return to valid | The credential status list and the accreditation status list |

</figure>

A revocation is final: an index set to invalid is never set back to valid. A
suspension is not, and the same index moves between valid and suspended as
often as the doubt behind it is raised and resolved.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-09-021 }**REQ-TS-5-09-021** `bits` MUST be 1 for the Use Statement status list and 2 for the credential status list and the accreditation status list.
- [](){ #req-ts-5-09-022 }**REQ-TS-5-09-022** A publisher MUST pack the entries, compress the byte array with DEFLATE in the ZLIB data format, and encode the result as base64url without padding.
- [](){ #req-ts-5-09-023 }**REQ-TS-5-09-023** A publisher MUST use a value from [the table of status values][tbl-ts-5-09-values] for every entry.
- [](){ #req-ts-5-09-024 }**REQ-TS-5-09-024** A publisher MUST NOT set an entry of a one-bit list to any value other than `0x00` or `0x01`.
- [](){ #req-ts-5-09-025 }**REQ-TS-5-09-025** A publisher MUST NOT set an entry from invalid back to valid.
- [](){ #req-ts-5-09-026 }**REQ-TS-5-09-026** A publisher MUST set an entry from suspended back to valid when the suspension of that artifact ends.
- [](){ #req-ts-5-09-027 }**REQ-TS-5-09-027** A publisher MUST set every index it has not allocated to `0x00`.
- [](){ #req-ts-5-09-028 }**REQ-TS-5-09-028** A reader MUST refuse the artifact when the value at its index is not one [the table of status values][tbl-ts-5-09-values] lists.
- [](){ #req-ts-5-09-029 }**REQ-TS-5-09-029** A reader MUST refuse a list whose `bits` is not the width this specification fixes for that list.

</div>

## Suspending a credential {#ts-5-09-suspending-a-credential}

A suspension sets a credential aside while a doubt about it is resolved, and
the credential may return to valid. The Root Authority does not suspend a
credential. It acts on the issuer's registration, and the suspension of that
registration stops every credential of the issuer. The Governance Profile bounds how long a
suspension may last in its `lifetimes.credential_suspension` member.

The citizen learns of a suspension from Mobile Wallet, as
[REQ-TS-5-09-120][req-ts-5-09-120] requires. The issuer has no channel to push
it to the citizen, and the notification endpoint of
[Issuing a credential via OpenID4VCI](issuing-a-credential-via-openid4vci.md)
is not used for it. While the entry of a credential is suspended, Issuer Core
defers the renewal of that credential, as
[REQ-TS-1-01-151][req-ts-1-01-151] fixes.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-09-122 }**REQ-TS-5-09-122** An entry of the credential status list MUST be set to suspended by Issuer Core alone, using its Status Manager Component.
- [](){ #req-ts-5-09-123 }**REQ-TS-5-09-123** Issuer Core MUST set the entry of a credential to suspended only on a citizen's report that the credential is lost, a correction or dispute from the issuer's source system, or the issuer's own check.
- [](){ #req-ts-5-09-124 }**REQ-TS-5-09-124** Issuer Core MUST set the entry of a credential back to valid or to invalid before the time `lifetimes.credential_suspension` of the Governance Profile fixes has passed since it set the entry to suspended.

</div>

## Indices {#ts-5-09-indices}

An index is allocated once and belongs to one artifact for as long as the list
exists. It is handed to another only where a replacement artifact's own
specification requires it to carry the index of the artifact it replaces. A
freed index is never allocated again. A list is published at a fixed length
whatever share of it is allocated, so that the size of a list says nothing
about how many credentials an issuer has issued.

Inside that length an index is drawn at random from the unallocated ones rather
than taken in sequence. A sequential index would say when an artifact was
issued relative to every other, and two verifiers comparing indices would learn
the order in which two citizens were served.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-09-030 }**REQ-TS-5-09-030** A publisher MUST allocate each artifact its own index.
- [](){ #req-ts-5-09-104 }**REQ-TS-5-09-104** A publisher MUST give a replacement artifact the index of the artifact it replaces where the specification of that artifact requires it.
- [](){ #req-ts-5-09-031 }**REQ-TS-5-09-031** A publisher MUST NOT allocate one index to two artifacts, in the same copy of a list or in any later copy, other than as [REQ-TS-5-09-104][req-ts-5-09-104] requires.
- [](){ #req-ts-5-09-032 }**REQ-TS-5-09-032** A publisher MUST draw an index at random from the indices of the list it has not allocated.
- [](){ #req-ts-5-09-033 }**REQ-TS-5-09-033** A publisher MUST keep the number of entries in a list the same in every copy it publishes.
- [](){ #req-ts-5-09-034 }**REQ-TS-5-09-034** A publisher MUST publish a list of at least 131072 entries.
- [](){ #req-ts-5-09-035 }**REQ-TS-5-09-035** A publisher MUST open a further list, at its own address, rather than lengthen a list whose indices are exhausted.
- [](){ #req-ts-5-09-036 }**REQ-TS-5-09-036** A publisher MUST go on publishing a list for as long as any artifact that points into it has not expired.
- [](){ #req-ts-5-09-087 }**REQ-TS-5-09-087** A publisher MUST allocate an index from the list it opened most recently.

</div>

## Signature {#ts-5-09-signature}

A status list is signed with a key that exists for signing status lists and for
nothing else.

The separation keeps revocation working. A list that revokes what a
compromised key signed cannot be signed by that same key. The key is frozen the
moment the compromise is found, and the republication that revokes its
credentials is what has to happen next.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-09-037 }**REQ-TS-5-09-037** Issuer Core MUST sign a status list with the `status-list` key of its entity.
- [](){ #req-ts-5-09-038 }**REQ-TS-5-09-038** Issuer Core MUST NOT sign a status list with the `issuance-jose` key, the `issuance-cose` key, or a Document Signer Certificate.
- [](){ #req-ts-5-09-039 }**REQ-TS-5-09-039** Trust Authority MUST sign the Use Statement status list with the Use Statement status list key.
- [](){ #req-ts-5-09-040 }**REQ-TS-5-09-040** Trust Authority MUST sign the accreditation status list with the accreditation status list key.
- [](){ #req-ts-5-09-041 }**REQ-TS-5-09-041** Trust Authority MUST NOT sign a status list with the key that signs the artifacts that list covers.
- [](){ #req-ts-5-09-042 }**REQ-TS-5-09-042** A signing key MUST be a P-256 key published in the publisher's DID Document under the purpose named for it.
- [](){ #req-ts-5-09-043 }**REQ-TS-5-09-043** A reader MUST find the signing key as [Finding the key][ts-01-finding-the-key] of TS-01 requires.
- [](){ #req-ts-5-09-044 }**REQ-TS-5-09-044** *Withdrawn: [REQ-TS-01-022][req-ts-01-022] covers it.*
- [](){ #req-ts-5-09-045 }**REQ-TS-5-09-045** A reader MUST refuse a list signed with a key the trusted list names as revoked in the publisher's entry, as [Publishing and reading the trusted list](publishing-and-reading-the-trusted-list.md) fixes.
- [](){ #req-ts-5-09-046 }**REQ-TS-5-09-046** A reader MUST refuse a list whose `iss` is not the entity that issued the artifact the index belongs to.

</div>

## Publication {#ts-5-09-publication}

A list is republished on a schedule, and again whenever an entry changes. A
revocation therefore does not wait for the schedule, and a reader cannot tell a
revocation from a routine republication by the time it arrives. Each copy
carries the moment it was issued, the moment it expires, and how long a reader
may use it before looking for a fresh one.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-09-047 }**REQ-TS-5-09-047** A publisher MUST serve a Status List Token with the media type `application/statuslist+jwt`.
- [](){ #req-ts-5-09-085 }**REQ-TS-5-09-085** A reader MUST fetch a Status List Token with `application/statuslist+jwt` in its `Accept` header.
- [](){ #req-ts-5-09-086 }**REQ-TS-5-09-086** A publisher MUST serve a Bitstring Status List credential with the media type `application/vc`.
- [](){ #req-ts-5-09-048 }**REQ-TS-5-09-048** A publisher MUST republish a list on the interval the Governance Profile sets, whether or not an entry has changed.
- [](){ #req-ts-5-09-049 }**REQ-TS-5-09-049** A publisher MUST republish a list within the time the Governance Profile allows after an entry changes.
- [](){ #req-ts-5-09-050 }**REQ-TS-5-09-050** `iat` MUST be the moment the copy was issued.
- [](){ #req-ts-5-09-051 }**REQ-TS-5-09-051** `exp` MUST be later than `iat`.
- [](){ #req-ts-5-09-052 }**REQ-TS-5-09-052** `ttl` MUST be the TTL the Governance Profile sets for that list.
- [](){ #req-ts-5-09-053 }**REQ-TS-5-09-053** A publisher MUST serve the list at the address the artifacts covered by it carry, for as long as [REQ-TS-5-09-036][req-ts-5-09-036] requires it to publish that list.
- [](){ #req-ts-5-09-054 }**REQ-TS-5-09-054** A publisher MUST NOT vary the response it serves by who asks for it.
- [](){ #req-ts-5-09-055 }**REQ-TS-5-09-055** A publisher MUST serve a status list over HTTPS.

</div>

## The CWT form, for mdoc {#ts-5-09-the-cwt-form-for-mdoc}

An mdoc does not carry its status reference as a claim in a JSON object; it
carries the Status CBOR structure in its Mobile Security Object. A reader
that opens one has a CBOR Object Signing and Encryption (COSE) stack and no
JSON Object Signing and Encryption (JOSE) stack, because the mdoc's own issuer
authentication is a CWT.

So an issuer that issues credentials in mdoc publishes its credential
status list twice, in the JWT form and in the CWT form. One
address serves both, and which one a reader gets follows from the `Accept`
header it sends, as [IETF Token Status List][ref-i-d-ietf-oauth-status-list]
fixes. The two tokens carry the same `bits`, the same array, and the same times,
so there is one list and two encodings of it rather than two lists. An mdoc
is the format the ecosystem exports to readers it does not run.

An issuer that issues in no other format than SD-JWT VC or `ldp_vc` has no
reader that arrives carrying a COSE stack, so it publishes the JWT form
alone. What the Credential Rulebook of each type it issues names as the
format decides this, and nothing else.

The CWT form of the list in
[The lists as published][ts-5-09-the-lists-as-published], as served, tagged as a
`COSE_Sign1` and carrying the same three entries:

``` { .text title="Credential status list, CWT form, in hex" data-format="CBOR" }
d2845902b9a3012610781a6170706c69636174696f6e2f7374617475736c6973
742b63777418215902943082029030820237a003020102020c393f3b03452aac
04524969a3300a06082a8648ce3d0403023059310b3009060355040613024944
312b3029060355040a0c22547275737420417574686f72697479205265707562
6c696b20496e646f6e65736961311d301b06035504030c144944435446204973
7375657220526f6f74204341301e170d3236303930313030303030305a170d32
39303930313030303030305a307a310b3009060355040613024944313e303c06
0355040a0c35446972656b746f726174204a656e646572616c204b6570656e64
7564756b616e2064616e2050656e6361746174616e20536970696c312b302906
035504030c2244756b636170696c20537461747573204c697374205369676e65
7220323032362d413059301306072a8648ce3d020106082a8648ce3d03010703
420004998e3ffaf13bc92efead7849f4cd8923f0aca5dfc158dccab445dafab4
6cec9a5cf7edf6fc6a546273bd70abc2397761f8355dc153c586ddbdaf9b2917
5c5daca381c33081c0300c0603551d130101ff04023000300e0603551d0f0101
ff040403020780301f0603551d23041830168014fbf0d56ab0bfda804a32eddd
33ccc9ddd283799a301d0603551d0e0416041485c506bb6757839d75afc75d9b
ec9af029e67d80301e0603551d1204173015861368747470733a2f2f74727573
742e676f2e696430400603551d1f043930373035a033a031862f68747470733a
2f2f72656769737472792e74727573742e676f2e69642f63726c2f6973737565
722d726f6f742d6361300a06082a8648ce3d040302034700304402203b203f0f
4b4a397d152c5827ccff45339afa3d161b8899ea560955bf9303974b02201515
134379f23c0519e53b84b0877240a3d410b9582f4b0ecde2c05f122a7fcfa104
58556469643a77656276683a516d6345565432694a5372737335686777694d46
734d55784b6b526f7a6746463435385263676754344d46324c343a64756b6361
70696c2e676f2e6964237374617475732d6c6973742d3159012ea60178476469
643a77656276683a516d6345565432694a5372737335686777694d46734d5578
4b6b526f7a6746463435385263676754344d46324c343a64756b636170696c2e
676f2e696402782368747470733a2f2f64756b636170696c2e676f2e69642f73
74617475732f6b74702d37061a6ad30ee0041a6afa9be019fffe19a8c019fffd
a2646269747302636c7374589b78daedd0310100000c0220c3d83fa3f7320c22
9000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000c05f550000000000000000
0000700cd1e9002558404b6e6ca2aa15736567c7177f8cff7c73e68562625551
9d85140a0e42e23b952cab0af39bb497e35f5646d08af45dc971bbddf9f817f4
c94dcf8360f2b051b0ee
```

Its protected header is `{1: -7, 16: "application/statuslist+cwt", 33: …}`.
`-7` is `ES256`, [RFC 9053][ref-rfc9053], and label 33 is `x5chain`,
[RFC 9360][ref-rfc9360], holding Dukcapil's status list signer certificate, the
one
[Issuing and validating the X.509 certificates and the VICAL](issuing-and-validating-the-x509-certificates-and-the-vical.md)
shows. Its unprotected header carries the `kid`
`did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id#status-list-1`,
and its claims are the issuer, the subject, the issued-at, the expiry, the time
to live, and the status list under the labels
[the table of CWT claims][tbl-ts-5-09-cwt] gives. [RFC 9864][ref-rfc9864]
deprecates `-7` in favor of `ESP256`, `-9`; the CWT form keeps `-7` because
ISO/IEC 18013-5:2021, which an mdoc reader is built to, requires it.

The Kartu ASN is issued in mdoc as well as in SD-JWT VC, so its issuer
publishes the CWT form of its list too. It sits at the same address, with the
same array and the same times as the JWT form in
[The lists as published][ts-5-09-the-lists-as-published], and index 481920
valid:

``` { .text title="Kartu ASN status list, CWT form, in hex" data-format="CBOR" }
d284590298a3012610781a6170706c69636174696f6e2f7374617475736c6973
742b63777418215902733082026f30820215a003020102020c24e85e631baf6f
0f571315a0300a06082a8648ce3d0403023059310b3009060355040613024944
312b3029060355040a0c22547275737420417574686f72697479205265707562
6c696b20496e646f6e65736961311d301b06035504030c144944435446204973
7375657220526f6f74204341301e170d3236303930313030303030305a170d32
39303930313030303030305a3058310b30090603550406130249443121301f06
0355040a0c18426164616e204b6570656761776169616e204e65676172613126
302406035504030c1d424b4e20537461747573204c697374205369676e657220
323032362d413059301306072a8648ce3d020106082a8648ce3d030107034200
045d844822beca068d6170270756dc21830672dbf0cd5b5899e28dfa0f5b6200
0b0d77af7818a95bb146a364f3f0a24e1f2c1bd1d84dc4555655b2a795b263ba
23a381c33081c0300c0603551d130101ff04023000300e0603551d0f0101ff04
0403020780301f0603551d23041830168014fbf0d56ab0bfda804a32eddd33cc
c9ddd283799a301d0603551d0e0416041457d594570230059fd4a9c126570666
1b403661a2301e0603551d1204173015861368747470733a2f2f74727573742e
676f2e696430400603551d1f043930373035a033a031862f68747470733a2f2f
72656769737472792e74727573742e676f2e69642f63726c2f6973737565722d
726f6f742d6361300a06082a8648ce3d040302034800304502200810dab87da6
4d16e3df44948add8a73684eb4c3944d3ef8506e7326de9ac913022100fba4f4
6abda428babb286806132fbaf37c156b99fa09ca01066422cfb69b5943a10458
506469643a77656276683a516d6538527269476e4b78356a32516a6f61593153
67525370785448646a7131314c3245786779317a563278734a3a626b6e2e676f
2e6964237374617475732d6c6973742d31590124a60178426469643a77656276
683a516d6538527269476e4b78356a32516a6f6159315367525370785448646a
7131314c3245786779317a563278734a3a626b6e2e676f2e6964027824687474
70733a2f2f626b6e2e676f2e69642f7374617475732f6b617274752d61736e2d
31061a6ad30ee0041a6afa9be019fffe19a8c019fffda2646269747302636c73
74589578daedc13101000000c2a0f54fed610da0000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000006e001e00015840a22fc359dbda
81ac14e9174d26d5ce151a342da1a55307e0acea18c711f9037db229bd3395e1
8bfa7729e997c97463602f1def4c2af4e10e92d9d564aa814922
```

Its protected header is the same, except that `x5chain` holds the status list
signer certificate of the Kartu ASN issuer. Its unprotected header carries the
`kid`
`did:webvh:Qme8RriGnKx5j2QjoaY1SgRSpxTHdjq11L2Exgy1zV2xsJ:bkn.go.id#status-list-1`,
its issuer is the DID before the `#` of that `kid`, and its subject is
`https://bkn.go.id/status/kartu-asn-1`.

[](){ #tbl-ts-5-09-cwt }

<figure markdown="1" class="ekdn-table">

| Label | Claim | Type | Presence | What it carries |
|---|---|---|---|---|
| 1 | issuer | text string | Present | The `did:webvh` of the entity that publishes the list |
| 2 | subject | text string | Present | The address the list is published at |
| 6 | issued at | integer | Present | The moment this copy was issued |
| 4 | expiration | integer | Present | The moment this copy expires |
| 65534 | time to live | unsigned integer | Present | The seconds a reader may use this copy |
| 65533 | status list | map | Present | `bits` and `lst`, the array as a byte string |

</figure>

Of the claims in [the table of CWT claims][tbl-ts-5-09-cwt], the issuer is
the one [IETF Token Status List][ref-i-d-ietf-oauth-status-list] does not
define for the CWT form, and the ecosystem adds it for the reason it adds
`iss` to the JWT form.

[Finding a signer's key from its DID](finding-a-signers-key-from-its-did.md)
fixes how a JSON Web Signature names its key and leaves COSE out, so the
clauses below carry its rules over to the CWT form. The `kid` sits in the
unprotected header, where [RFC 9052][ref-rfc9052] allows a key identifier
because it is a hint about which key to use. The issuer in the signed payload
ties the key to the publisher, which the DID part of `kid` matches under
[REQ-TS-5-09-110][req-ts-5-09-110].

The protected header also carries `x5chain`, because a reader that came to the
list from an mdoc verified that mdoc through the Issuer Root CA and may hold no
DID resolver. The certificate in it certifies the same `status-list` key
`kid` names, under the same root as the Document Signer Certificate. That is
the one path such a reader can already walk.

One root certifies every issuer, so for an
mdoc the entity that issued it is the `organizationName` of its
Document Signer Certificate, and a reader refuses a CWT form whose status list
signer certificate carries another, [REQ-TS-5-09-118][req-ts-5-09-118]. The JWT
form has no such certificate, so it cannot be tied to the issuer of an mdoc, and
a reader checks an mdoc against the CWT form alone.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-09-089 }**REQ-TS-5-09-089** Issuer Core MUST publish the credential status list in the CWT form as well as the JWT form where the entity issues credentials in mdoc.
- [](){ #req-ts-5-09-090 }**REQ-TS-5-09-090** Issuer Core MUST serve both forms at the address the credentials covered by the list carry.
- [](){ #req-ts-5-09-091 }**REQ-TS-5-09-091** Issuer Core MUST answer a request whose `Accept` header names `application/statuslist+cwt` with the CWT form, and one that names `application/statuslist+jwt` with the JWT form.
- [](){ #req-ts-5-09-102 }**REQ-TS-5-09-102** Issuer Core that publishes no CWT form MUST answer a request that accepts the CWT form alone with status code 406.
- [](){ #req-ts-5-09-103 }**REQ-TS-5-09-103** Issuer Core MUST publish the CWT form from the day it issues its first credential in mdoc.
- [](){ #req-ts-5-09-105 }**REQ-TS-5-09-105** Issuer Core MUST go on publishing the CWT form for as long as any credential it issued in mdoc has not expired.
- [](){ #req-ts-5-09-092 }**REQ-TS-5-09-092** Issuer Core MUST serve the CWT form with the media type `application/statuslist+cwt`.
- [](){ #req-ts-5-09-093 }**REQ-TS-5-09-093** The CWT form MUST be a `COSE_Sign1` structure tagged with CBOR tag 18.
- [](){ #req-ts-5-09-094 }**REQ-TS-5-09-094** The protected header of the CWT form MUST carry label 16 with the value `application/statuslist+cwt`.
- [](){ #req-ts-5-09-095 }**REQ-TS-5-09-095** The CWT form MUST carry every claim [the table of CWT claims][tbl-ts-5-09-cwt] marks present, under the labels that table gives.
- [](){ #req-ts-5-09-096 }**REQ-TS-5-09-096** `lst` in the CWT form MUST be a byte string holding the compressed array.
- [](){ #req-ts-5-09-106 }**REQ-TS-5-09-106** `lst` in the CWT form MUST NOT be base64url encoded.
- [](){ #req-ts-5-09-097 }**REQ-TS-5-09-097** Issuer Core MUST sign the CWT form with the same `status-list` key it signs the JWT form with.
- [](){ #req-ts-5-09-098 }**REQ-TS-5-09-098** The two forms MUST carry the same `bits`, the same array, the same issued-at, the same expiry, and the same time to live.
- [](){ #req-ts-5-09-099 }**REQ-TS-5-09-099** Issuer Core MUST republish both forms together.
- [](){ #req-ts-5-09-100 }**REQ-TS-5-09-100** Mobile Verifier MUST ask for the CWT form when it checks the status of an mdoc.
- [](){ #req-ts-5-09-107 }**REQ-TS-5-09-107** *Withdrawn: [REQ-TS-5-09-119][req-ts-5-09-119] covers it.*
- [](){ #req-ts-5-09-101 }**REQ-TS-5-09-101** A reader MUST refuse a CWT form whose protected header does not carry label 16 with that value.
- [](){ #req-ts-5-09-108 }**REQ-TS-5-09-108** Label 1 of the CWT form MUST be the `did:webvh` the JWT form carries in `iss`.
- [](){ #req-ts-5-09-109 }**REQ-TS-5-09-109** Issuer Core MUST carry `kid` in the unprotected header of the CWT form, under label 4, as a byte string holding the UTF-8 encoding of the `kid` the JWT form carries.
- [](){ #req-ts-5-09-110 }**REQ-TS-5-09-110** The DID part of that `kid`, before the `#`, MUST equal label 1.
- [](){ #req-ts-5-09-111 }**REQ-TS-5-09-111** A reader MUST find the signing key of the CWT form as [Finding the key][ts-01-finding-the-key] of TS-01 requires, taking `kid` from label 4 and the signer's DID from label 1.
- [](){ #req-ts-5-09-112 }**REQ-TS-5-09-112** A reader MUST refuse a CWT form that does not carry label 1.
- [](){ #req-ts-5-09-113 }**REQ-TS-5-09-113** The protected header of the CWT form MUST carry label 33, `x5chain`, holding the issuer's status list signer certificate as a single byte string.
- [](){ #req-ts-5-09-114 }**REQ-TS-5-09-114** Issuer Core MUST NOT place the Issuer Root CA in that `x5chain`.
- [](){ #req-ts-5-09-115 }**REQ-TS-5-09-115** The certificate in that `x5chain` MUST certify the key `kid` names.
- [](){ #req-ts-5-09-116 }**REQ-TS-5-09-116** A reader MUST validate the certificate in `x5chain` as [Validating a chain][ts-5-04-validating-a-chain] of TS-5-04 requires for a Document Signer Certificate.
- [](){ #req-ts-5-09-117 }**REQ-TS-5-09-117** A reader MUST refuse a CWT form whose certificate in `x5chain` does not certify the key `kid` names.
- [](){ #req-ts-5-09-118 }**REQ-TS-5-09-118** A reader checking an mdoc MUST refuse a CWT form whose certificate in `x5chain` carries an `organizationName` other than that of the Document Signer Certificate that signed the mdoc.
- [](){ #req-ts-5-09-119 }**REQ-TS-5-09-119** Mobile Wallet, Verifier Core, and Mobile Verifier MUST check the status of an mdoc against the CWT form only.

</div>

## The list for `ldp_vc` {#ts-5-09-the-list-for-ldp-vc}

A credential issued in `ldp_vc` points into a Bitstring Status List instead,
which is a credential rather than a token, as
[W3C Bitstring Status List v1.0][ref-bitstring-status-list] defines it. The standard
advises that a status list be secured the way the credentials it covers are
secured. An `ldp_vc` credential is secured with a Data Integrity proof, so its
status list is too.

The encoding differs from the Status List Token in three ways. An entry is one
bit, so a purpose that needs a second state takes a second list: revocation and
suspension are two credentials at two addresses, and a credential carries one
`credentialStatus` entry for each. A set bit says the list's `statusPurpose`. The standard defines two: revoked
and final in the revocation list, suspended and reversible in the suspension
list, so [the table of status values][tbl-ts-5-09-values] reads `0x01` for the
revocation list alone. The bits are packed from the most
significant bit of each byte downward. The array is compressed with GZIP and
written as a multibase string, `u` followed by base64url without padding.

[](){ #tbl-ts-5-09-bsl }

<figure markdown="1" class="ekdn-table">

| Property | Type | Presence | What it carries |
|---|---|---|---|
| `id` | string | Present | The address the list credential is published at |
| `type` | array of strings | Present | `VerifiableCredential` and `BitstringStatusListCredential` |
| `issuer` | string | Present | The `did:webvh` of the issuer |
| `validFrom` | string | Present | The moment this copy takes effect |
| `validUntil` | string | Present | The moment this copy expires |
| `credentialSubject.id` | string | Present | The address of the list inside the credential |
| `credentialSubject.type` | string | Present | `BitstringStatusList` |
| `credentialSubject.statusPurpose` | string | Present | `revocation` or `suspension` |
| `credentialSubject.encodedList` | string | Present | The compressed bitstring, multibase encoded |
| `proof` | object | Present | The Data Integrity proof in `ecdsa-rdfc-2019` |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-09-056 }**REQ-TS-5-09-056** Issuer Core MUST publish the status of a credential issued in `ldp_vc` as a Bitstring Status List credential, carrying every property [the table of list credential properties][tbl-ts-5-09-bsl] marks present.
- [](){ #req-ts-5-09-057 }**REQ-TS-5-09-057** The credential MUST carry `BitstringStatusListCredential` in its `type` and `BitstringStatusList` in the `type` of its `credentialSubject`.
- [](){ #req-ts-5-09-058 }**REQ-TS-5-09-058** `credentialSubject.statusPurpose` MUST be `revocation` or `suspension`.
- [](){ #req-ts-5-09-059 }**REQ-TS-5-09-059** Issuer Core MUST publish one credential per purpose, each at its own address.
- [](){ #req-ts-5-09-060 }**REQ-TS-5-09-060** `credentialSubject.encodedList` MUST be the GZIP-compressed bitstring, multibase encoded as base64url without padding.
- [](){ #req-ts-5-09-061 }**REQ-TS-5-09-061** The bitstring MUST hold at least 131072 entries.
- [](){ #req-ts-5-09-062 }**REQ-TS-5-09-062** Issuer Core MUST secure the credential with a Data Integrity proof in the `ecdsa-rdfc-2019` cryptosuite, signed with the entity's `status-list` key.
- [](){ #req-ts-5-09-063 }**REQ-TS-5-09-063** The credential MUST carry `https://www.w3.org/ns/credentials/v2` as its only context.
- [](){ #req-ts-5-09-064 }**REQ-TS-5-09-064** The credential MUST carry `validFrom` and `validUntil`.
- [](){ #req-ts-5-09-065 }**REQ-TS-5-09-065** A credential issued in `ldp_vc` MUST carry one `BitstringStatusListEntry` per purpose, each naming the address of the credential for that purpose and the index inside it.
- [](){ #req-ts-5-09-066 }**REQ-TS-5-09-066** The index of one credential MUST be the same in the revocation list and in the suspension list.
- [](){ #req-ts-5-09-067 }**REQ-TS-5-09-067** A reader MUST verify the Data Integrity proof before it reads an entry.
- [](){ #req-ts-5-09-068 }**REQ-TS-5-09-068** A reader MUST refuse a Bitstring Status List credential whose `statusPurpose` is not the purpose of the entry it is reading.
- [](){ #req-ts-5-09-125 }**REQ-TS-5-09-125** A set bit in a Bitstring Status List credential whose `statusPurpose` is `suspension` MUST be read as suspended and not as invalid, so that [REQ-TS-5-09-026][req-ts-5-09-026] applies to it and [REQ-TS-5-09-025][req-ts-5-09-025] does not.

</div>

## Reading an entry {#ts-5-09-reading-an-entry}

A reader works from a cached copy and fetches a list on its own schedule, never
while a transaction is in hand. A fetch at that moment would tell the
publisher which artifact is being checked, and would make the check fail
whenever the network does.

1. Take the address and the index out of the artifact being checked.
2. Find the cached copy fetched from that address. There is none when the
   reader's sync has not yet fetched that publisher's list, and then no status
   can be established.
3. Check the signature on the copy, every time, not only when it was fetched.
4. Check that `sub` is the address the artifact named.
5. Decode `lst`, decompress it, and read the block of `bits` bits at the index.
6. Decide on the value, and on how old the copy is.

A copy is good until its `ttl` has passed. After that the reader goes on using
it as its last-known-good copy, up to the tolerance limit. Past that limit it
refuses to act on the copy, as
[three rules for reading the copy][three-rules-for-reading-the-copy] sets out.
The limit costs a transaction when it bites: a status that cannot be
established may have been revoked weeks ago.

A verifier's refusal says only that the credential was refused, as
[REQ-TS-5-10-121][req-ts-5-10-121] requires. Mobile Wallet tells the citizen
which it was, as [REQ-TS-5-09-120][req-ts-5-09-120] requires.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-09-069 }**REQ-TS-5-09-069** A reader MUST read a status from a cached copy of the list.
- [](){ #req-ts-5-09-070 }**REQ-TS-5-09-070** A reader MUST NOT fetch a status list while a transaction is in hand.
- [](){ #req-ts-5-09-071 }**REQ-TS-5-09-071** A reader MUST check the signature on a cached copy every time it reads from it.
- [](){ #req-ts-5-09-072 }**REQ-TS-5-09-072** A reader MUST read the entry at the index the artifact names.
- [](){ #req-ts-5-09-081 }**REQ-TS-5-09-081** A reader MUST NOT read an entry the artifact does not name.
- [](){ #req-ts-5-09-073 }**REQ-TS-5-09-073** A reader MUST refuse the artifact when its index is beyond the end of the array.
- [](){ #req-ts-5-09-074 }**REQ-TS-5-09-074** A reader MAY use a copy whose `ttl` has passed, up to the tolerance limit the Governance Profile sets.
- [](){ #req-ts-5-09-083 }**REQ-TS-5-09-083** A reader MUST refuse a copy whose `exp` has passed, whatever the tolerance limit allows.
- [](){ #req-ts-5-09-084 }**REQ-TS-5-09-084** A publisher MUST set `exp` no earlier than `iat` plus the `ttl` and the tolerance limit the Governance Profile sets, so that a copy a reader may still use has not expired.
- [](){ #req-ts-5-09-075 }**REQ-TS-5-09-075** A reader MUST refuse to act on a copy older than the tolerance limit.
- [](){ #req-ts-5-09-076 }**REQ-TS-5-09-076** A reader MUST refuse the artifact when it can establish no status for it.
- [](){ #req-ts-5-09-120 }**REQ-TS-5-09-120** Mobile Wallet MUST show the citizen, for a credential it holds whose entry on a credential status list is set, whether the credential is suspended or revoked.
- [](){ #req-ts-5-09-121 }**REQ-TS-5-09-121** Where the entry of a credential issued in `ldp_vc` is set in the revocation list its `credentialStatus` names, Mobile Wallet MUST show the credential as revoked, whatever the suspension list says.
- [](){ #req-ts-5-09-077 }**REQ-TS-5-09-077** A reader MUST NOT act on an entry read from a copy it has discarded.
- [](){ #req-ts-5-09-078 }**REQ-TS-5-09-078** A reader MUST discard a cached copy whose signature no longer verifies.
- [](){ #req-ts-5-09-082 }**REQ-TS-5-09-082** A reader MUST fetch the list again at its next sync after it discards a copy.

</div>

## Security considerations {#ts-5-09-security-considerations}

- **A replaced list.** An attacker who serves an older copy hides a
  revocation. [REQ-TS-5-09-071][req-ts-5-09-071] makes a reader check the
  signature on every read, and [REQ-TS-5-09-075][req-ts-5-09-075] puts a
  ceiling on how old a copy may be whatever its signature says.
- **A list signed by the key it is supposed to revoke.** This is the failure
  the separate key exists for. [REQ-TS-5-09-038][req-ts-5-09-038] and
  [REQ-TS-5-09-041][req-ts-5-09-041] keep the signing key of the artifact away
  from the list that revokes it, so a frozen issuance key does not freeze
  revocation with it.
- **A list that stops being published.** A publisher that withdraws a list
  leaves every artifact pointing into it unverifiable.
  [REQ-TS-5-09-036][req-ts-5-09-036] makes publication last as long as the
  artifacts do, and [REQ-TS-5-09-076][req-ts-5-09-076] makes the reader's
  answer a refusal rather than an assumption.
- **A substituted list from another publisher.**
  [REQ-TS-5-09-020][req-ts-5-09-020] and [REQ-TS-5-09-046][req-ts-5-09-046] tie
  the copy to the address the artifact named and to the entity that issued the
  artifact, so a valid list from the wrong issuer is refused. For an mdoc,
  [REQ-TS-5-09-118][req-ts-5-09-118] reads that entity from the
  Document Signer Certificate, and [REQ-TS-5-09-119][req-ts-5-09-119] keeps the
  JWT form, which carries no certificate, out of the check.
- **A list served differently to different readers.** A publisher that answers
  one reader with a clean list and everyone else with a revoked one would make
  revocation untestable. [REQ-TS-5-09-054][req-ts-5-09-054] forbids it, and a
  signed list that is published whole makes the difference provable.

## Privacy considerations {#ts-5-09-privacy-considerations}

The point of publishing a list whole is that reading it says nothing. A reader
fetches the same bytes as everyone else, on its own schedule, and the publisher
learns that someone fetched the list and nothing about which artifact was
checked. [REQ-TS-5-09-008][req-ts-5-09-008] and
[REQ-TS-5-09-070][req-ts-5-09-070] keep it that way, and
[REQ-TS-5-09-055][req-ts-5-09-055] keeps the fetch itself from becoming a
record.

Two things about an issuer would otherwise leak through the list: how many
credentials it has issued, and the order in which it issued them. The fixed
length of [REQ-TS-5-09-033][req-ts-5-09-033] hides the first, and the random
allocation of [REQ-TS-5-09-032][req-ts-5-09-032] the second.
Neither is the citizen's secret, but both would let an outsider watch an
agency's operations through a public file.

An index is a correlator for as long as a credential lives: two verifiers that
see the same credential see the same index. That belongs to the credential
rather than to the list, and the index tells neither of them anything about the
citizen it belongs to.

## Changelog {#ts-5-09-changelog}

<figure markdown="1" class="ekdn-table">

| Version | Date | Change |
|---|---|---|
| 1.0 draft | 21 October 2026 | First draft |

</figure>
