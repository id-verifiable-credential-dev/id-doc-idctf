---
title: "[TS-5-05] Answering with an Authority Statement"
description: The Authority Statement Trust Registry answers a permission query with, the permission it names, the signature Trust Authority puts on each answer, how long a reader may keep it, and the checks a reader runs before it acts on one.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, Kep. 6, §2.4, §4.3, §5.4, §5.7; Rincian Module dan Operasi §2.1, §2.2, §2.5, §7.4; tracks/0251 -->

<p class="ekdn-docid">TS-5-05</p>

# Answering with an Authority Statement {#ts-5-05-answering-with-an-authority-statement}

<p class="ekdn-lead" markdown="span">
An Authority Statement is the record of one permission the Root Authority
granted to one entity. Nobody publishes it and nobody carries it. Trust
Registry answers a permission query with it, signed, and the reader keeps
the answer until it expires.
</p>

Every sentence on this page binds Trust Registry, Trust Authority, and every
Module that acts on a permission, and an Assessment Body tests them against
it in the version the Governance Profile puts in force. The key words and
the identifier `REQ-TS-5-05-nnn` follow
[Common provisions](common-provisions.md).

## Who runs this and what it needs {#ts-5-05-who-runs-this-and-what-it-needs}

This specification fixes the answer Trust Registry returns to a Trust
Registry Query Protocol (TRQP) v2.0 authorization query: what the answer carries,
what a permission names, the signature Trust Authority puts on it, how long
a reader may use it, and what a reader checks before acting on it. It also
fixes when a statement comes into force and when it stops.

Its conformance targets are Trust Registry, which answers the query; Trust
Authority, which records each permission and signs each answer; and the four
Modules that act on a permission: Issuer Core, Verifier Core, Mobile Wallet,
and Mobile Verifier. A reader meets its requirements through Trust SDK where
the library performs the check.

It leaves to other documents: who is granted a permission and on what
grounds, [the approval tiers][gf-approval-tiers], and [the sanctions behind a withdrawal][gf-ladder-of-sanctions], which
the Governance Framework holds; the list of admitted `action` values, the
signature algorithms allowed, the lifetime of an answer, and the tolerance
limit, which the Governance Profile holds; the request, the endpoint, the
error responses, the recognition query, and the catalog Trust Registry
serves beside them, which
[Answering a permission query and serving the catalog](answering-a-permission-query-and-serving-the-catalog.md)
holds; the trusted
list, which
[Publishing and reading the trusted list](publishing-and-reading-the-trusted-list.md)
holds; the keys of Trust Authority and the log they live in, which
[Publishing and resolving a did:webvh identifier](publishing-and-resolving-a-did-webvh-identifier.md)
holds; and the registered use that narrows a permission further, which
[Registering and carrying a Use Statement](registering-and-carrying-a-use-statement.md)
holds.

Before the first exchange, each target holds what the rules below assume:

- **Trust Registry** holds the Root Authority's authorization decisions with
  their history, and reaches the Authority Statement key through Trust
  Authority, whose Certificate Authority Component signs each answer; it
  holds no private key of its own.
- **Trust Authority** holds the Authority Statement key in its hardware
  security module (HSM), and publishes the matching public key in its own
  Decentralized Identifier (DID) Document.
- **A reader** carries Trust Authority's self-certifying identifier (SCID)
  from build time, resolves Trust Authority's DID Document from it, and
  embeds Trust SDK, which performs the checks of
  [Reading the answer][ts-5-05-reading-the-answer].

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-05-001 }**REQ-TS-5-05-001** Trust Registry MUST meet every requirement on this page that names Trust Registry, and every requirement on what Trust Registry writes: its answer and every member of it, `statement` included, and every requirement on how a permission is read.
- [](){ #req-ts-5-05-002 }**REQ-TS-5-05-002** Trust Authority MUST meet every requirement on this page that names Trust Authority, and every requirement on what Trust Authority writes: the `statement` it signs, with its protected header, its claims and its signature.
- [](){ #req-ts-5-05-003 }**REQ-TS-5-05-003** Issuer Core, Verifier Core, Mobile Wallet, and Mobile Verifier MUST each meet every requirement that names a reader, and every requirement on how a permission is read, wherever it stands on this page.

</div>

## What the statement answers {#ts-5-05-overview}

The trusted list says whether an entity is accredited. An Authority
Statement says what that entity may do: one `action` on one `resource`,
granted by the Root Authority and recorded by Trust Authority, as
[Authorization][authorization] sets out. An entity holding several
permissions has several statements, and nothing combines them into one
record.

It is the one artifact of the ecosystem that nobody publishes and nobody
carries. There is no file to fetch and no address to go to: a participant
asks whether a named entity may take a named action on a named resource,
and Trust Registry answers, as
[Authority Statement][authority-statement] explains. The answer is signed,
so a reader that keeps it can check it again later without asking again,
which is what lets a permission check survive an unreachable registry.

A permission is the ceiling for an entity. A Use Statement narrows it to one
registered use of one Relying Party and travels in the request instead, as
[Registered use][registered-use] sets out. The two are read together: a
verifier may ask for an attribute only when its Authority Statement covers
that attribute and the Use Statement it carries names it.

## Authority Statement answer {#ts-5-05-authority-statement-answer}

The body Trust Registry returns, for the four forms this specification
admits: a permission to issue a credential type, a permission to request one
attribute under a query evaluated at a stated time, a permission to request
one attribute of a credential type another body named, and a query for a
permission the entity does not hold. The permission to issue is shown four
times: for the types the ecosystem names, the KTP, the Kartu ASN and the Kartu
Nikah, and for the mobile driving license, which another body named.

The seven answers are an illustration: the entities, the domains and the
keys are invented, and no registration has been accredited. Every field is
exact. Each answer was signed with the Authority Statement key of the Trust
Authority DID shown in `authority_id`, and each signature verifies, so an
implementation can parse these answers and find what the clauses below
require. The entities are the ones
[the trusted list][ts-5-01-trusted-list-payload] carries, with
the same DIDs.

``` { .json title="The answer to an issuing permission that is granted" data-format="JSON" }
{
  "authority_id": "did:webvh:QmZjy1t9oFiaFjhX2e38uMuR7mgtdLjHPMGfjEfvrsmaiq:trust.go.id",
  "entity_id": "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id",
  "action": "issue",
  "resource": "id.idctf.ktp.1",
  "authorized": true,
  "time_evaluated": "2026-10-17T03:11:20Z",
  "message": "Granted 2026-02-01T00:00:00Z.",
  "statement": "eyJ0eXAiOiJ2bmQuaWQuaWRjdGYuYXV0aG9yaXR5LXN0YXRlbWVudCtqd3QiLCJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDp3ZWJ2aDpRbVpqeTF0OW9GaWFGamhYMmUzOHVNdVI3bWd0ZExqSFBNR2ZqRWZ2cnNtYWlxOnRydXN0LmdvLmlkI2F1dGhvcml0eS1zdGF0ZW1lbnQtMSJ9.eyJhdXRob3JpdHlfaWQiOiJkaWQ6d2Vidmg6UW1aankxdDlvRmlhRmpoWDJlMzh1TXVSN21ndGRMakhQTUdmakVmdnJzbWFpcTp0cnVzdC5nby5pZCIsImVudGl0eV9pZCI6ImRpZDp3ZWJ2aDpRbWNFVlQyaUpTcnNzNWhnd2lNRnNNVXhLa1JvemdGRjQ1OFJjZ2dUNE1GMkw0OmR1a2NhcGlsLmdvLmlkIiwiYWN0aW9uIjoiaXNzdWUiLCJyZXNvdXJjZSI6ImlkLmlkY3RmLmt0cC4xIiwiYXV0aG9yaXplZCI6dHJ1ZSwidGltZV9ldmFsdWF0ZWQiOiIyMDI2LTEwLTE3VDAzOjExOjIwWiIsInBlcmlvZHMiOlt7InZhbGlkX2Zyb20iOiIyMDI2LTAyLTAxVDAwOjAwOjAwWiJ9XSwiaWF0IjoxNzkyMjA2NjgwLCJleHAiOjE3OTIyNDk4ODB9.j9z10GOFWuNr9EMiLI48YAZ74C71hIwH6e-FTf0XDr2BeqtgJNziZeYlm5-PiaK6Nqj6p8GklWLz-v-7WVqYOQ"
}
```

``` { .json title="The answer to a request permission, evaluated at a stated time" data-format="JSON" }
{
  "authority_id": "did:webvh:QmZjy1t9oFiaFjhX2e38uMuR7mgtdLjHPMGfjEfvrsmaiq:trust.go.id",
  "entity_id": "did:webvh:QmUATC5jyf5yVy72GYAp8nSvuwshzDy6wYX7WmNY5UJtXT:terminal-nusantara.co.id",
  "action": "request",
  "resource": "id.idctf.ktp.1#usia_di_atas_17",
  "authorized": true,
  "time_requested": "2026-09-01T00:00:00Z",
  "time_evaluated": "2026-10-17T03:11:20Z",
  "context": {
    "time": "2026-09-01T00:00:00Z"
  },
  "message": "Granted 2026-02-18T00:00:00Z.",
  "statement": "eyJ0eXAiOiJ2bmQuaWQuaWRjdGYuYXV0aG9yaXR5LXN0YXRlbWVudCtqd3QiLCJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDp3ZWJ2aDpRbVpqeTF0OW9GaWFGamhYMmUzOHVNdVI3bWd0ZExqSFBNR2ZqRWZ2cnNtYWlxOnRydXN0LmdvLmlkI2F1dGhvcml0eS1zdGF0ZW1lbnQtMSJ9.eyJhdXRob3JpdHlfaWQiOiJkaWQ6d2Vidmg6UW1aankxdDlvRmlhRmpoWDJlMzh1TXVSN21ndGRMakhQTUdmakVmdnJzbWFpcTp0cnVzdC5nby5pZCIsImVudGl0eV9pZCI6ImRpZDp3ZWJ2aDpRbVVBVEM1anlmNXlWeTcyR1lBcDhuU3Z1d3NoekR5NndZWDdXbU5ZNVVKdFhUOnRlcm1pbmFsLW51c2FudGFyYS5jby5pZCIsImFjdGlvbiI6InJlcXVlc3QiLCJyZXNvdXJjZSI6ImlkLmlkY3RmLmt0cC4xI3VzaWFfZGlfYXRhc18xNyIsImF1dGhvcml6ZWQiOnRydWUsInRpbWVfcmVxdWVzdGVkIjoiMjAyNi0wOS0wMVQwMDowMDowMFoiLCJ0aW1lX2V2YWx1YXRlZCI6IjIwMjYtMTAtMTdUMDM6MTE6MjBaIiwicGVyaW9kcyI6W3sidmFsaWRfZnJvbSI6IjIwMjYtMDgtMDFUMDA6MDA6MDBaIn0seyJ2YWxpZF9mcm9tIjoiMjAyNi0wMi0xOFQwMDowMDowMFoiLCJ2YWxpZF91bnRpbCI6IjIwMjYtMDctMDFUMDA6MDA6MDBaIn1dLCJpYXQiOjE3OTIyMDY2ODAsImV4cCI6MTc5MjI0OTg4MH0.0qY602jIFU2z9Fd2CR7AL22oEhCPMt_RkOTUNYm_ux2OtrejK7-5-w76tVHQYx1iIknjvlYigx1tRkKs5YB2MQ"
}
```

``` { .json title="The answer to a request permission over a type another body names" data-format="JSON" }
{
  "authority_id": "did:webvh:QmZjy1t9oFiaFjhX2e38uMuR7mgtdLjHPMGfjEfvrsmaiq:trust.go.id",
  "entity_id": "did:webvh:QmUATC5jyf5yVy72GYAp8nSvuwshzDy6wYX7WmNY5UJtXT:terminal-nusantara.co.id",
  "action": "request",
  "resource": "org.iso.18013.5.1.mDL.1#age_over_18",
  "authorized": true,
  "time_evaluated": "2026-10-17T03:11:20Z",
  "message": "Granted 2026-02-20T00:00:00Z.",
  "statement": "eyJ0eXAiOiJ2bmQuaWQuaWRjdGYuYXV0aG9yaXR5LXN0YXRlbWVudCtqd3QiLCJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDp3ZWJ2aDpRbVpqeTF0OW9GaWFGamhYMmUzOHVNdVI3bWd0ZExqSFBNR2ZqRWZ2cnNtYWlxOnRydXN0LmdvLmlkI2F1dGhvcml0eS1zdGF0ZW1lbnQtMSJ9.eyJhdXRob3JpdHlfaWQiOiJkaWQ6d2Vidmg6UW1aankxdDlvRmlhRmpoWDJlMzh1TXVSN21ndGRMakhQTUdmakVmdnJzbWFpcTp0cnVzdC5nby5pZCIsImVudGl0eV9pZCI6ImRpZDp3ZWJ2aDpRbVVBVEM1anlmNXlWeTcyR1lBcDhuU3Z1d3NoekR5NndZWDdXbU5ZNVVKdFhUOnRlcm1pbmFsLW51c2FudGFyYS5jby5pZCIsImFjdGlvbiI6InJlcXVlc3QiLCJyZXNvdXJjZSI6Im9yZy5pc28uMTgwMTMuNS4xLm1ETC4xI2FnZV9vdmVyXzE4IiwiYXV0aG9yaXplZCI6dHJ1ZSwidGltZV9ldmFsdWF0ZWQiOiIyMDI2LTEwLTE3VDAzOjExOjIwWiIsInBlcmlvZHMiOlt7InZhbGlkX2Zyb20iOiIyMDI2LTAyLTIwVDAwOjAwOjAwWiJ9XSwiaWF0IjoxNzkyMjA2NjgwLCJleHAiOjE3OTIyNDk4ODB9.ZCKcmfCloXYCrdqBUg7NkWQil-uD7OP-5J-sLmDPTIfGUWscnt322LSO8iu3_U8DncXAZkv4C89U2IPqcjkk4A"
}
```

``` { .json title="The answer to an issuing permission over a type another body names" data-format="JSON" }
{
  "authority_id": "did:webvh:QmZjy1t9oFiaFjhX2e38uMuR7mgtdLjHPMGfjEfvrsmaiq:trust.go.id",
  "entity_id": "did:webvh:QmZQeFgp3SBDLmidt4TiZhix8u5b2oPSqvQFhuSF8BoN6F:korlantas.polri.go.id",
  "action": "issue",
  "resource": "org.iso.18013.5.1.mDL.1",
  "authorized": true,
  "time_evaluated": "2026-10-17T03:11:20Z",
  "message": "Granted 2026-03-01T00:00:00Z.",
  "statement": "eyJ0eXAiOiJ2bmQuaWQuaWRjdGYuYXV0aG9yaXR5LXN0YXRlbWVudCtqd3QiLCJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDp3ZWJ2aDpRbVpqeTF0OW9GaWFGamhYMmUzOHVNdVI3bWd0ZExqSFBNR2ZqRWZ2cnNtYWlxOnRydXN0LmdvLmlkI2F1dGhvcml0eS1zdGF0ZW1lbnQtMSJ9.eyJhdXRob3JpdHlfaWQiOiJkaWQ6d2Vidmg6UW1aankxdDlvRmlhRmpoWDJlMzh1TXVSN21ndGRMakhQTUdmakVmdnJzbWFpcTp0cnVzdC5nby5pZCIsImVudGl0eV9pZCI6ImRpZDp3ZWJ2aDpRbVpRZUZncDNTQkRMbWlkdDRUaVpoaXg4dTViMm9QU3F2UUZodVNGOEJvTjZGOmtvcmxhbnRhcy5wb2xyaS5nby5pZCIsImFjdGlvbiI6Imlzc3VlIiwicmVzb3VyY2UiOiJvcmcuaXNvLjE4MDEzLjUuMS5tREwuMSIsImF1dGhvcml6ZWQiOnRydWUsInRpbWVfZXZhbHVhdGVkIjoiMjAyNi0xMC0xN1QwMzoxMToyMFoiLCJwZXJpb2RzIjpbeyJ2YWxpZF9mcm9tIjoiMjAyNi0wMy0wMVQwMDowMDowMFoifV0sImlhdCI6MTc5MjIwNjY4MCwiZXhwIjoxNzkyMjQ5ODgwfQ.zZmIxbbmZ1OsiqRRoDCfrDXuDmMRQPLQRj5LwYPEXAlEuov0BOHoXMe2qwDL35nzI90x0cAO-HSp8V5otxxpww"
}
```

``` { .json title="The answer to an issuing permission over the Kartu ASN" data-format="JSON" }
{
  "authority_id": "did:webvh:QmZjy1t9oFiaFjhX2e38uMuR7mgtdLjHPMGfjEfvrsmaiq:trust.go.id",
  "entity_id": "did:webvh:Qme8RriGnKx5j2QjoaY1SgRSpxTHdjq11L2Exgy1zV2xsJ:bkn.go.id",
  "action": "issue",
  "resource": "id.idctf.kartu-asn.1",
  "authorized": true,
  "time_evaluated": "2026-10-17T03:11:20Z",
  "message": "Granted 2026-03-01T00:00:00Z.",
  "statement": "eyJ0eXAiOiJ2bmQuaWQuaWRjdGYuYXV0aG9yaXR5LXN0YXRlbWVudCtqd3QiLCJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDp3ZWJ2aDpRbVpqeTF0OW9GaWFGamhYMmUzOHVNdVI3bWd0ZExqSFBNR2ZqRWZ2cnNtYWlxOnRydXN0LmdvLmlkI2F1dGhvcml0eS1zdGF0ZW1lbnQtMSJ9.eyJhdXRob3JpdHlfaWQiOiJkaWQ6d2Vidmg6UW1aankxdDlvRmlhRmpoWDJlMzh1TXVSN21ndGRMakhQTUdmakVmdnJzbWFpcTp0cnVzdC5nby5pZCIsImVudGl0eV9pZCI6ImRpZDp3ZWJ2aDpRbWU4UnJpR25LeDVqMlFqb2FZMVNnUlNweFRIZGpxMTFMMkV4Z3kxelYyeHNKOmJrbi5nby5pZCIsImFjdGlvbiI6Imlzc3VlIiwicmVzb3VyY2UiOiJpZC5pZGN0Zi5rYXJ0dS1hc24uMSIsImF1dGhvcml6ZWQiOnRydWUsInRpbWVfZXZhbHVhdGVkIjoiMjAyNi0xMC0xN1QwMzoxMToyMFoiLCJwZXJpb2RzIjpbeyJ2YWxpZF9mcm9tIjoiMjAyNi0wMy0wMVQwMDowMDowMFoifV0sImlhdCI6MTc5MjIwNjY4MCwiZXhwIjoxNzkyMjQ5ODgwfQ.S8UI7FVczrZNxIlEuiJNLylnswPaSznY53_mcjrvHQzlm9khLE7-eFqMCkryQOl-jxsFOZjC_vXRFQ3ZzFTvbw"
}
```

``` { .json title="The answer to an issuing permission over the Kartu Nikah" data-format="JSON" }
{
  "authority_id": "did:webvh:QmZjy1t9oFiaFjhX2e38uMuR7mgtdLjHPMGfjEfvrsmaiq:trust.go.id",
  "entity_id": "did:webvh:QmbAb7u9RMjqsZ9L98pe47szJZdnKQLh9KizqNW2WwKac1:kemenag.go.id",
  "action": "issue",
  "resource": "id.idctf.kartu-nikah.1",
  "authorized": true,
  "time_evaluated": "2026-10-17T03:11:20Z",
  "message": "Granted 2026-03-01T00:00:00Z.",
  "statement": "eyJ0eXAiOiJ2bmQuaWQuaWRjdGYuYXV0aG9yaXR5LXN0YXRlbWVudCtqd3QiLCJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDp3ZWJ2aDpRbVpqeTF0OW9GaWFGamhYMmUzOHVNdVI3bWd0ZExqSFBNR2ZqRWZ2cnNtYWlxOnRydXN0LmdvLmlkI2F1dGhvcml0eS1zdGF0ZW1lbnQtMSJ9.eyJhdXRob3JpdHlfaWQiOiJkaWQ6d2Vidmg6UW1aankxdDlvRmlhRmpoWDJlMzh1TXVSN21ndGRMakhQTUdmakVmdnJzbWFpcTp0cnVzdC5nby5pZCIsImVudGl0eV9pZCI6ImRpZDp3ZWJ2aDpRbWJBYjd1OVJNanFzWjlMOThwZTQ3c3pKWmRuS1FMaDlLaXpxTlcyV3dLYWMxOmtlbWVuYWcuZ28uaWQiLCJhY3Rpb24iOiJpc3N1ZSIsInJlc291cmNlIjoiaWQuaWRjdGYua2FydHUtbmlrYWguMSIsImF1dGhvcml6ZWQiOnRydWUsInRpbWVfZXZhbHVhdGVkIjoiMjAyNi0xMC0xN1QwMzoxMToyMFoiLCJwZXJpb2RzIjpbeyJ2YWxpZF9mcm9tIjoiMjAyNi0wMy0wMVQwMDowMDowMFoifV0sImlhdCI6MTc5MjIwNjY4MCwiZXhwIjoxNzkyMjQ5ODgwfQ.GjcgXQPdqYXe8Mwv0dPEz1dDSbDJhzvKusbPSH_TYK_mHs3CjTQE3nnzNuJySRJGaZ6dzUY5E8hRviRvzsIRag"
}
```

``` { .json title="The answer to a permission the entity does not hold" data-format="JSON" }
{
  "authority_id": "did:webvh:QmZjy1t9oFiaFjhX2e38uMuR7mgtdLjHPMGfjEfvrsmaiq:trust.go.id",
  "entity_id": "did:webvh:Qme8RriGnKx5j2QjoaY1SgRSpxTHdjq11L2Exgy1zV2xsJ:bkn.go.id",
  "action": "issue",
  "resource": "id.idctf.kartu-nikah.1",
  "authorized": false,
  "time_evaluated": "2026-10-17T03:11:20Z",
  "message": "Not granted.",
  "statement": "eyJ0eXAiOiJ2bmQuaWQuaWRjdGYuYXV0aG9yaXR5LXN0YXRlbWVudCtqd3QiLCJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDp3ZWJ2aDpRbVpqeTF0OW9GaWFGamhYMmUzOHVNdVI3bWd0ZExqSFBNR2ZqRWZ2cnNtYWlxOnRydXN0LmdvLmlkI2F1dGhvcml0eS1zdGF0ZW1lbnQtMSJ9.eyJhdXRob3JpdHlfaWQiOiJkaWQ6d2Vidmg6UW1aankxdDlvRmlhRmpoWDJlMzh1TXVSN21ndGRMakhQTUdmakVmdnJzbWFpcTp0cnVzdC5nby5pZCIsImVudGl0eV9pZCI6ImRpZDp3ZWJ2aDpRbWU4UnJpR25LeDVqMlFqb2FZMVNnUlNweFRIZGpxMTFMMkV4Z3kxelYyeHNKOmJrbi5nby5pZCIsImFjdGlvbiI6Imlzc3VlIiwicmVzb3VyY2UiOiJpZC5pZGN0Zi5rYXJ0dS1uaWthaC4xIiwiYXV0aG9yaXplZCI6ZmFsc2UsInRpbWVfZXZhbHVhdGVkIjoiMjAyNi0xMC0xN1QwMzoxMToyMFoiLCJwZXJpb2RzIjpbXSwiaWF0IjoxNzkyMjA2NjgwLCJleHAiOjE3OTIyNDk4ODB9.7vwRkX-foV235g54n2KfhGISriCWzkLUSyGTxelCzAma53oU4o2lVNr3Hd-wmLec433sU6e4dSL3fJZw8QD_Hw"
}
```

## Format {#ts-5-05-format}

The answer is the `AuthorizationResponse` of [TRQP][ref-trqp] with one
member added. The added member carries the signature, which TRQP leaves to
the deployment, and TRQP admits it because a response may carry members the
protocol does not define.
[The table of answer members][tbl-ts-5-05-answer-members] gives each one.

[](){ #tbl-ts-5-05-answer-members }

<figure markdown="1" class="ekdn-table">

| Member | Type | Presence | Value |
|---|---|---|---|
| `authority_id` | string | Present | Trust Authority's `did:webvh` |
| `entity_id` | string | Present | The entity the query named, as a `did:webvh` |
| `action` | string | Present | The action the query named |
| `resource` | string | Present | The resource the query named |
| `authorized` | boolean | Present | `true` when the entity holds the permission at the time evaluated, `false` otherwise |
| `time_requested` | string | Present when the query carried `context.time` | The time the query asked about |
| `time_evaluated` | string | Present | The time Trust Registry evaluated the query at |
| `context` | object | Present when the query carried one | The context object of the query, returned unchanged |
| `message` | string | Optional | Text for an operator reading a log |
| `statement` | string | Present | The signed answer, as [Signature][ts-5-05-signature] gives it |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-05-004 }**REQ-TS-5-05-004** Trust Registry MUST return an answer that conforms to the `AuthorizationResponse` schema of [TRQP][ref-trqp].
- [](){ #req-ts-5-05-005 }**REQ-TS-5-05-005** Trust Registry MUST carry every member [the table of answer members][tbl-ts-5-05-answer-members] marks present.
- [](){ #req-ts-5-05-006 }**REQ-TS-5-05-006** `authority_id` MUST be the `did:webvh` of Trust Authority.
- [](){ #req-ts-5-05-007 }**REQ-TS-5-05-007** `entity_id`, `action`, and `resource` MUST repeat the values the query carried, byte for byte.
- [](){ #req-ts-5-05-008 }**REQ-TS-5-05-008** `authorized` MUST be `true` only when the entity named in `entity_id` holds the permission at the time in `time_evaluated`, or at the time in `time_requested` where the query carried one.
- [](){ #req-ts-5-05-009 }**REQ-TS-5-05-009** Trust Registry MUST answer `authorized: false` for a permission that was never granted, for one that has been withdrawn, and for one whose entity is suspended or withdrawn on the trusted list.
- [](){ #req-ts-5-05-010 }**REQ-TS-5-05-010** Trust Registry MUST write `time_evaluated` and `time_requested` as the date and time format [TRQP][ref-trqp] requires, in Coordinated Universal Time (UTC) with the `Z` offset.
- [](){ #req-ts-5-05-011 }**REQ-TS-5-05-011** Trust Registry MUST NOT state a permission in `message` that `authorized` does not state.
- [](){ #req-ts-5-05-012 }**REQ-TS-5-05-012** Trust Registry MUST NOT carry a citizen's data, a transaction identifier, or the identity of the party that asked in any member of the answer.

</div>

A negative answer carries the same members as a positive one, the signature
included. There is no permission to show in that case, and the signature is
over Trust Authority's assertion that the entity holds no such permission,
which is what keeps a cached `false` from being turned into a `true`.

## What a permission names {#ts-5-05-what-a-permission-names}

A permission is one `action` on one `resource`. Nothing else is part of it:
not a purpose, not a legal basis, and not a list of attributes beyond the
one the resource names. Those belong to a registered use.

### Actions {#ts-5-05-actions}

An action names what the entity may do.
[The table of actions][tbl-ts-5-05-actions] gives the two the ecosystem uses
today; the Governance Profile holds the list in force, and a Governance
Service maintains it.

[](){ #tbl-ts-5-05-actions }

<figure markdown="1" class="ekdn-table">

| Action | Held by | What it permits |
|---|---|---|
| `issue` | An Identity Issuer or an Attribute Issuer | Issuing credentials of the credential type the resource names |
| `request` | A Relying Party, an RP Intermediary among them | Asking for the credential type or the attribute the resource names |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-05-013 }**REQ-TS-5-05-013** `action` MUST be a non-empty string that the Governance Profile lists.
- [](){ #req-ts-5-05-014 }**REQ-TS-5-05-014** Trust Registry MUST answer `authorized: false` for an `action` the Governance Profile does not list.
- [](){ #req-ts-5-05-015 }**REQ-TS-5-05-015** A reader MUST compare an `action` with the value it asked for byte for byte, after no transformation of any kind.

</div>

### Resources {#ts-5-05-resources}

A resource names what the action is permitted on. It is a credential type,
or one attribute inside a credential type, in the forms
[Identifier](../architecture-framework/data-model-and-protocols/identifier.md)
fixes: `id.idctf.<type>.<N>` for a type Trust Authority publishes,
`<reverse-domain>.<type>.<N>` for a private party's, and the type followed by
`#<attribute>` for one attribute of it. The version is part of the name, so
a permission over `id.idctf.ktp.1` says nothing about `id.idctf.ktp.2`.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-05-016 }**REQ-TS-5-05-016** `resource` MUST be a credential type identifier, or a credential type identifier followed by `#` and an attribute name.
- [](){ #req-ts-5-05-017 }**REQ-TS-5-05-017** The credential type in `resource` MUST be one the Credential Rulebook Catalog registers.
- [](){ #req-ts-5-05-018 }**REQ-TS-5-05-018** A permission over a credential type MUST NOT be read as a permission over another version of that type.
- [](){ #req-ts-5-05-019 }**REQ-TS-5-05-019** A permission over a credential type MUST be read as covering every attribute of that type.
- [](){ #req-ts-5-05-020 }**REQ-TS-5-05-020** A permission over one attribute MUST NOT be read as covering another attribute of the same type.

</div>

## Signature {#ts-5-05-signature}

Each answer is signed as a JSON Web Token (JWT) as
[RFC 7519][ref-rfc7519] defines one, signed as a JSON Web Signature (JWS) in
the compact serialization of [RFC 7515][ref-rfc7515], and carried in the
`statement` member.
Its payload is a JSON object that repeats the answer and adds the two times
that bound it and the periods in which the permission was in force.
[The table of statement claims][tbl-ts-5-05-statement-claims] gives each
claim.

The signing key is the Authority Statement key that
[Trust Authority's own keys][trust-authoritys-own-keys] names, held in Trust
Authority's HSM, where the Certificate Authority Component signs with it.
Trust Registry builds the answer and asks Trust Authority to sign it, as it
reaches the trusted list key for the list it publishes. Trust Authority does
not sign what it is handed. It builds the payload again from the record it
holds and refuses the request when the two disagree, so a Trust Registry in
someone else's hands cannot have a permission signed that the Root Authority
never granted. The key is published
in Trust Authority's DID Document, so it rotates the way Trust Authority's
other signing keys do, and a reader finds it by resolving the SCID it
carries from build time.

[](){ #tbl-ts-5-05-statement-claims }

<figure markdown="1" class="ekdn-table">

| Claim | Type | Presence | Value |
|---|---|---|---|
| `authority_id` | string | Present | As the answer carries it |
| `entity_id` | string | Present | As the answer carries it |
| `action` | string | Present | As the answer carries it |
| `resource` | string | Present | As the answer carries it |
| `authorized` | boolean | Present | As the answer carries it |
| `time_requested` | string | Present when the answer carries it | As the answer carries it |
| `time_evaluated` | string | Present | As the answer carries it |
| `iat` | number | Present | The time the answer was signed, in seconds since the Unix epoch |
| `exp` | number | Present | The time the answer stops being current, in seconds since the Unix epoch |
| `periods` | array of objects | Present | Every interval in which the permission was in force, newest first, each with `valid_from` and, once the permission has been withdrawn, `valid_until`; an empty array when the permission was never granted |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-05-021 }**REQ-TS-5-05-021** The `statement` member MUST be a JWS in the compact serialization of [RFC 7515][ref-rfc7515] whose payload is the JSON claims set of [RFC 7519][ref-rfc7519].
- [](){ #req-ts-5-05-022 }**REQ-TS-5-05-022** The `typ` header parameter MUST be `vnd.id.idctf.authority-statement+jwt`.
- [](){ #req-ts-5-05-023 }**REQ-TS-5-05-023** The `alg` header parameter MUST be one the Governance Profile allows for an Authority Statement.
- [](){ #req-ts-5-05-024 }**REQ-TS-5-05-024** *Withdrawn: [REQ-TS-01-034][req-ts-01-034] covers it.*
- [](){ #req-ts-5-05-025 }**REQ-TS-5-05-025** The `kid` header parameter MUST name a key of the purpose `authority-statement`, as [Naming the key][ts-01-naming-the-key] of TS-01 requires.
- [](){ #req-ts-5-05-026 }**REQ-TS-5-05-026** The payload MUST carry every claim [the table of statement claims][tbl-ts-5-05-statement-claims] marks present.
- [](){ #req-ts-5-05-027 }**REQ-TS-5-05-027** Every claim the payload carries that the answer also carries as a member MUST hold the value of that member.
- [](){ #req-ts-5-05-028 }**REQ-TS-5-05-028** Trust Authority MUST hold the private key in its HSM.
- [](){ #req-ts-5-05-029 }**REQ-TS-5-05-029** Trust Registry MUST NOT hold the private key.
- [](){ #req-ts-5-05-030 }**REQ-TS-5-05-030** Trust Authority MUST publish the public key as a verification method of its own DID Document.
- [](){ #req-ts-5-05-031 }**REQ-TS-5-05-031** Trust Authority MUST NOT sign an Authority Statement with the trusted list key, the Verified Issuer Certificate Authority List (VICAL) key, the Use Statement key, or any other key that [Trust Authority's own keys][trust-authoritys-own-keys] names.
- [](){ #req-ts-5-05-055 }**REQ-TS-5-05-055** Trust Authority MUST build the payload it signs from its own record of the permission, not from the payload Trust Registry presents.
- [](){ #req-ts-5-05-056 }**REQ-TS-5-05-056** Trust Authority MUST refuse a signing request whose answer does not match that record.
- [](){ #req-ts-5-05-057 }**REQ-TS-5-05-057** Trust Authority MUST carry in `periods` every interval taken from the times [REQ-TS-5-05-048][req-ts-5-05-048] records, and MUST NOT drop one.
- [](){ #req-ts-5-05-058 }**REQ-TS-5-05-058** Each entry of `periods` MUST be an object with `valid_from` and, once the permission has been withdrawn, `valid_until`, each a date and time in UTC with the `Z` offset, and MUST omit `valid_until` while the permission is in force.
- [](){ #req-ts-5-05-059 }**REQ-TS-5-05-059** Trust Authority MUST order `periods` by `valid_from`, newest first, and MUST carry an empty array for a permission that was never granted.
- [](){ #req-ts-5-05-060 }**REQ-TS-5-05-060** Trust Registry MUST NOT carry `periods` as a member of the answer.

</div>

The periods are a claim of the signed payload alone, as `iat` and `exp` are.
[TRQP][ref-trqp] defines no member that says when a permission began or
ended, and a member it does not define would sit outside the signature
unless the payload repeated it. `valid_until` may lie in the future when
the Root Authority has decided a withdrawal with notice, as
[how Rulebook versions end][rulebook-versions]
sets out; a reader treats the time as reached only when it arrives.

The last rule is the blast-radius rule the rest of Trust Authority's keys
follow. An Authority Statement key signs on every query, so it is the key
most exposed to a fault in the query path, and a key that also signed the
trusted list would carry that exposure into the list.

## Lifetime {#ts-5-05-lifetime}

An answer is current until the `exp` it carries. Past that, a reader keeps
using it as a last-known-good copy up to the tolerance limit, and refuses it
after, which is how every cached artifact other than the trusted list
behaves, as
[three rules for reading the copy][three-rules-for-reading-the-copy] sets out. The
Governance Profile holds both numbers, because the right interval is a
balance between how fast a withdrawal has to reach a reader and how much
traffic the registry carries.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-05-032 }**REQ-TS-5-05-032** Trust Authority MUST set `exp` to `iat` plus the Time to Live (TTL) the Governance Profile sets for an Authority Statement.
- [](){ #req-ts-5-05-033 }**REQ-TS-5-05-033** A reader MUST treat an answer as current until its `exp`.
- [](){ #req-ts-5-05-034 }**REQ-TS-5-05-034** A reader MAY use an answer past its `exp` as a last-known-good copy, up to the tolerance limit the Governance Profile sets.
- [](){ #req-ts-5-05-035 }**REQ-TS-5-05-035** A reader MUST refuse an answer past the tolerance limit, however recently it was fetched.
- [](){ #req-ts-5-05-036 }**REQ-TS-5-05-036** A reader MUST keep the answer it caches for one `entity_id`, `action`, and `resource` separate from the answer it caches for any other.
- [](){ #req-ts-5-05-037 }**REQ-TS-5-05-037** A reader MUST discard its cached answers for an entity whose status on the trusted list changes.

</div>

## Reading the answer {#ts-5-05-reading-the-answer}

A reader runs the same steps on an answer it has just received and on one it
takes out of its cache, because a cached answer is the same bytes.

1. **Check the signature.** Resolve Trust Authority's DID Document from the
   SCID carried at build time, take the key the `kid` names, and verify the
   JWS. An answer whose signature does not verify is refused.
2. **Check the payload against the body.** Every claim of the payload has to
   equal the member of the same name in the answer. Where they differ, the
   answer is refused, because the members outside the signature are the ones
   an attacker can edit.
3. **Check the query.** `entity_id`, `action`, and `resource` have to be the
   values the reader asked about. An answer about anything else is refused,
   whoever signed it.
4. **Check the time.** The answer is current when `exp` has not passed, and
   usable as a last-known-good copy up to the tolerance limit after that.
5. **Read `authorized`.** A `true` lets the reader go on; a `false` stops
   it. Nothing in `message` changes either.
6. **Read `periods` for a past time.** A reader that has to know whether the
   permission held at a time before the answer was signed looks for that
   time in `periods`. A time falls in a period from its `valid_from`, which
   counts, up to its `valid_until`, which does not; a period with no
   `valid_until` has no end. `authorized` says nothing about that time.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-05-038 }**REQ-TS-5-05-038** A reader MUST verify the `statement` JWS against a key published in the DID Document of the SCID it carries from build time.
- [](){ #req-ts-5-05-039 }**REQ-TS-5-05-039** A reader MUST refuse an answer whose `statement` is absent, whose signature does not verify, or whose `typ` is not `vnd.id.idctf.authority-statement+jwt`.
- [](){ #req-ts-5-05-040 }**REQ-TS-5-05-040** A reader MUST refuse an answer where a member of the body differs from the claim of the same name in the payload.
- [](){ #req-ts-5-05-041 }**REQ-TS-5-05-041** A reader MUST refuse an answer whose `authority_id` is not the Trust Authority it carries the SCID of.
- [](){ #req-ts-5-05-042 }**REQ-TS-5-05-042** A reader MUST refuse an answer whose `entity_id`, `action`, or `resource` differs from the one it asked about.
- [](){ #req-ts-5-05-043 }**REQ-TS-5-05-043** A reader MUST verify the signature again on every read of a cached answer.
- [](){ #req-ts-5-05-044 }**REQ-TS-5-05-044** A reader MUST treat a refused answer as no answer.
- [](){ #req-ts-5-05-053 }**REQ-TS-5-05-053** A reader MUST NOT act on the permission a refused answer names.
- [](){ #req-ts-5-05-045 }**REQ-TS-5-05-045** A reader MUST NOT act on `message`.
- [](){ #req-ts-5-05-046 }**REQ-TS-5-05-046** A reader MUST check the entity's status on the trusted list as well.
- [](){ #req-ts-5-05-054 }**REQ-TS-5-05-054** A reader MUST NOT accept a permission for an entity that is not granted on the trusted list.
- [](){ #req-ts-5-05-061 }**REQ-TS-5-05-061** A reader that reads a permission for a past time MUST read it from `periods`, and MUST NOT read it from `authorized`.
- [](){ #req-ts-5-05-062 }**REQ-TS-5-05-062** A reader MUST count a time as inside a period when it is not before `valid_from` and, where the period carries `valid_until`, is before it.

</div>

The last rule is what keeps the two answers in their places. The trusted
list says whether the entity is accredited and the Authority Statement says
what it may do, as
[three questions, three answers][three-questions-three-answers] sets out,
and a reader that checked only one of them would accept a withdrawn entity
holding an old permission.

## Lifecycle {#ts-5-05-lifecycle}

A permission begins when the Root Authority grants it and Trust Authority
records it, and ends when the Root Authority withdraws it. Between those two
points it does not change: a narrower grant is a different permission, and
a wider one is a new permission beside it rather than an edit of the first.
Trust Authority records that new permission instead of editing the one it
holds. Trust Authority keeps the history, so a question asked about a past
time is answered from the status that held then.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-05-047 }**REQ-TS-5-05-047** Trust Authority MUST record one Authority Statement for each permission the Root Authority grants, naming one `action` and one `resource`.
- [](){ #req-ts-5-05-048 }**REQ-TS-5-05-048** Trust Authority MUST record the time a permission came into force and the time it was withdrawn.
- [](){ #req-ts-5-05-049 }**REQ-TS-5-05-049** Trust Authority MUST keep a withdrawn permission with its history rather than deleting it.
- [](){ #req-ts-5-05-050 }**REQ-TS-5-05-050** Trust Authority MUST NOT widen or narrow a recorded permission.
- [](){ #req-ts-5-05-051 }**REQ-TS-5-05-051** Trust Registry MUST answer a query carrying `context.time` from the status that held at that time.
- [](){ #req-ts-5-05-052 }**REQ-TS-5-05-052** Trust Registry MUST answer a query carrying no `context.time` from the status that holds at `time_evaluated`.
- [](){ #req-ts-5-05-063 }**REQ-TS-5-05-063** Trust Authority MUST NOT open or close a period because the entity is suspended or withdrawn on the trusted list, which [REQ-TS-5-05-046][req-ts-5-05-046] has a reader check apart from the permission.

</div>

## Security considerations {#ts-5-05-security-considerations}

Each threat below is answered by the requirement named with it.

- **An answer edited in the cache or on the wire.** The signature covers
  every field a reader acts on, [REQ-TS-5-05-026][req-ts-5-05-026], the
  reader checks the body against it,
  [REQ-TS-5-05-040][req-ts-5-05-040], and it checks the signature again on
  every read rather than trusting what it stored,
  [REQ-TS-5-05-043][req-ts-5-05-043].
- **An answer replayed against a different question.** The payload names
  the entity, the action, and the resource, and a reader refuses an answer
  that is not about what it asked,
  [REQ-TS-5-05-042][req-ts-5-05-042].
- **An answer that outlives a withdrawal.** The TTL bounds how long a
  granted permission survives the decision that ended it,
  [REQ-TS-5-05-032][req-ts-5-05-032], the tolerance limit bounds the
  last-known-good copy, [REQ-TS-5-05-035][req-ts-5-05-035], and a change of
  status on the trusted list clears the cache for that entity,
  [REQ-TS-5-05-037][req-ts-5-05-037].
- **A forged Trust Authority.** A reader verifies against a key published
  in the DID Document of the SCID it was built with,
  [REQ-TS-5-05-038][req-ts-5-05-038], and refuses an answer that claims a
  different authority, [REQ-TS-5-05-041][req-ts-5-05-041].
- **One stolen key reaching every artifact.** The Authority Statement key
  signs nothing else, [REQ-TS-5-05-031][req-ts-5-05-031], and Trust Registry
  never holds it, [REQ-TS-5-05-029][req-ts-5-05-029].
- **A captured Trust Registry having a permission signed.** Trust Registry
  reaches the signer on every query, so a registry in someone else's hands
  would be a signing service for whatever it presented. Trust Authority
  signs from its own record instead,
  [REQ-TS-5-05-055][req-ts-5-05-055], and refuses a request that does not
  match it, [REQ-TS-5-05-056][req-ts-5-05-056], which leaves the attacker a
  path to answers that were true anyway.
- **A permission read wider than it was granted.** A version is part of the
  resource name, [REQ-TS-5-05-018][req-ts-5-05-018], and an attribute grant
  covers that attribute alone, [REQ-TS-5-05-020][req-ts-5-05-020].

Trust Authority signing every answer is also what bounds availability: when
its signer cannot be reached, Trust Registry answers with the
`signer-unavailable` problem of [Answering a permission query and serving the catalog](answering-a-permission-query-and-serving-the-catalog.md)
and no statement, and a reader
falls back to the copy it already holds until the tolerance limit. That is
the behavior the architecture asks for, since an unreachable registry must
not stop a transaction that was already provided for.

## Privacy considerations {#ts-5-05-privacy-considerations}

A query tells Trust Registry which entity a participant is interested in.
Cached answers are what keep that from being a record of transactions: a
reader that holds a current answer asks nothing, so the registry sees one
query per entity per TTL rather than one per transaction, and a wallet
asks on its trust cache sync rather than during a transaction. The architecture
sets that bound in
[what connects the two planes][what-connects-the-two-planes].

The answer itself carries nothing about a citizen,
[REQ-TS-5-05-012][req-ts-5-05-012]. It names an entity, an action, a
resource, and a decision, and the same answer serves every reader that asks
the same question, so nothing in it identifies who asked.

## Changelog {#ts-5-05-changelog}

<figure markdown="1" class="ekdn-table">

| Version | Date | Change |
|---|---|---|
| 1.0 draft | 19 October 2026 | First draft |

</figure>
