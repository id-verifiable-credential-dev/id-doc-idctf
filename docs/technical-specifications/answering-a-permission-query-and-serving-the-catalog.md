---
title: "[TS-4-02] Answering a permission query and serving the catalog"
description: The two Trust Registry Query Protocol endpoints Trust Registry answers, the signed answer to a recognition query, the errors either endpoint returns, and the signed catalog of Credential Rulebooks it publishes beside them.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, Kep. 6; Rincian Module dan Operasi §2.1, §2.2, §2.5, §7.4; ToIP TRQP v2.0; tracks/0251, tracks/0264, tracks/0266, tracks/0323 -->

<p class="ekdn-docid">TS-4-02</p>

# Answering a permission query and serving the catalog {#ts-4-02-answering-a-permission-query-and-serving-the-catalog}

<p class="ekdn-lead" markdown="span">
Trust Registry answers two questions on request, whether an entity may do
something and whether another ecosystem's authority is recognized, and
publishes the catalog of Credential Rulebooks as files. This specification
fixes the endpoints, the answers, the errors, and the catalog.
</p>

Every sentence on this page binds Trust Registry, Trust Authority, and every
Module that asks Trust Registry a question or reads its catalog, and an
Assessment Body tests them against it in the version the Governance Profile
puts in force. The key words and the identifier `REQ-TS-4-02-nnn` follow
[Common provisions](common-provisions.md).

## Who runs this and what it needs {#ts-4-02-who-runs-this-and-what-it-needs}

This specification binds the interface of Trust Registry: the two endpoints
of the Trust Registry Query Protocol (TRQP) v2.0, `authorization` and
`recognition`, as Trust Registry runs them; the answer to a recognition
query and the signature on it; the errors either endpoint returns; the
catalog of Credential Rulebooks and the checks a proposed Rulebook passes
before review; and where each artifact Trust Registry publishes can be
fetched.

Its conformance targets are Trust Registry, which answers the queries and
publishes the catalog; Trust Authority, which records each recognition and
signs each recognition answer and each catalog list; and the four Modules
that ask Trust Registry a question or read its catalog: Issuer Core,
Verifier Core, Mobile Wallet, and Mobile Verifier. A reader meets its
requirements through Trust SDK where the library performs the check.

It leaves to other documents: the answer to an authorization query, its
signature and its lifetime, which
[Answering with an Authority Statement](answering-with-an-authority-statement.md)
holds; [which foreign authority is recognized, for what, and on what terms, which the Governance Framework holds][gf-recognition]; the address of each endpoint and of
the catalog, the actions admitted, the signature algorithms allowed, the
lifetime of each answer and of the catalog list, the tolerance limit, and
the rate limit, which the Governance Profile holds; what a Rulebook
contains and how its vocabulary is named, which the
[Credential Rulebook Catalog](../credential-rulebook/index.md) holds; and
each artifact served from a distribution point, which the specification
that defines it holds.

Before the first exchange, each target holds what the rules below assume:

- **Trust Registry** holds the Root Authority's authorization and
  recognition decisions with their history, and every published Rulebook
  version. It reaches the recognition statement key and the catalog key
  through Trust Authority, whose Certificate Authority Component signs with
  both; it holds no private key of its own. Its query endpoint sits in the
  public zone, as [network zones and placement][network-zones-and-placement]
  sets out.
- **Trust Authority** holds the recognition statement key and the catalog
  key in its hardware security module (HSM), and publishes the matching
  public keys in its own Decentralized Identifier (DID) Document.
- **A reader** carries Trust Authority's self-certifying identifier (SCID)
  from build time, holds the query endpoint address and the catalog address
  the Governance Profile publishes, and embeds Trust SDK.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-4-02-001 }**REQ-TS-4-02-001** Trust Registry MUST meet every requirement in [The HTTPS binding][ts-4-02-the-https-binding], [Authorization query][ts-4-02-authorization-query], [Recognition query][ts-4-02-recognition-query], [Errors][ts-4-02-errors] and [The catalog][ts-4-02-the-catalog].
- [](){ #req-ts-4-02-002 }**REQ-TS-4-02-002** Trust Authority MUST meet every requirement in [The recognition statement][ts-4-02-the-recognition-statement], [Recognition lifecycle][ts-4-02-recognition-lifecycle] and [The catalog list][ts-4-02-the-catalog-list], and [REQ-TS-4-02-085][req-ts-4-02-085].
- [](){ #req-ts-4-02-003 }**REQ-TS-4-02-003** Issuer Core, Verifier Core, Mobile Wallet, and Mobile Verifier MUST each meet every requirement that names a reader, wherever it stands on this page.

</div>

## What Trust Registry serves {#ts-4-02-overview}

Trust Registry serves two kinds of traffic, as
[Trust Registry][hla-trust-registry] sets out. The query endpoint answers
questions one at a time: a participant names an entity, an action and a
resource, and Trust Registry answers from the decisions Trust Authority
recorded, as [Entity to Trust Registry][entity-to-trust-registry] explains.
Everything else leaves as a static file through the central content
delivery network (CDN): the trusted list, the Verified Issuer Certificate
Authority List (VICAL), the revocation and
status lists, and the catalog. Its six Components, and which of them does
what below, are in [Trust Registry][sa-trust-registry].

Every answer is signed, so a reader keeps it and checks it again without
asking again. That is what lets a permission check survive an unreachable
registry, and it is why a reader asks only when it holds no current answer.

## The exchange {#ts-4-02-the-exchange}

One query is answered in eight steps. The same steps serve both endpoints.

1. The reader looks in its cache for a current answer to the same entity,
   action and resource. If it holds one, it asks nothing.
2. The reader sends the query to the endpoint the Governance Profile
   publishes, with nothing that identifies itself.
3. Trust Registry checks that the body is a well-formed query.
4. It checks that the query is addressed to Trust Authority.
5. It evaluates the query against the decisions recorded at the time the
   query names, or at the time it evaluates it.
6. It builds the answer and asks Trust Authority to sign it.
7. It returns the answer, or a problem document when one of the checks in
   steps 3 and 4 fails, or when the signer cannot be reached or refuses to
   sign.
8. The reader checks the answer and keeps it until it is no longer usable.

## Queries as exchanged {#ts-4-02-queries-as-exchanged}

Below are the queries this specification admits and the answers they
receive. The entities, the domains and the keys are invented, and no
registration has been accredited and no ecosystem recognized. Every field
is exact. Each answer was signed with the key of the Trust Authority DID
shown in `authority_id`, and each signature verifies. The entities are the
ones [the trusted list][ts-5-01-trusted-list-payload] carries,
with the same DIDs, and the two foreign authorities are named under the
`.example` domain, which no ecosystem can hold.

An authorization query for a permission to issue, as Issuer Core or a
reader sends it:

``` { .http title="POST /authorization, Trust Registry query endpoint" data-format="HTTP" }
POST /authorization HTTP/1.1
Host: query.trust.go.id
Content-Type: application/json

{
  "authority_id": "did:webvh:QmZjy1t9oFiaFjhX2e38uMuR7mgtdLjHPMGfjEfvrsmaiq:trust.go.id",
  "entity_id": "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id",
  "action": "issue",
  "resource": "id.idctf.ktp.1"
}
```

Trust Registry answers with the head below, and the body is
[the answer to an issuing permission that is granted][ts-5-05-authority-statement-answer],
byte for byte:

``` { .http title="200, the answer to an authorization query" data-format="HTTP" }
HTTP/1.1 200 OK
Content-Type: application/json
```

A recognition query asks whether a foreign authority is recognized as
authoritative for issuing a credential type, here the mobile driving
license:

``` { .http title="POST /recognition, Trust Registry query endpoint" data-format="HTTP" }
POST /recognition HTTP/1.1
Host: query.trust.go.id
Content-Type: application/json

{
  "authority_id": "did:webvh:QmZjy1t9oFiaFjhX2e38uMuR7mgtdLjHPMGfjEfvrsmaiq:trust.go.id",
  "entity_id": "did:web:trust-registry.partner.example",
  "action": "issue",
  "resource": "org.iso.18013.5.1.mDL.1"
}
```

The answer, `200` with media type `application/json`:

``` { .json title="The answer to a recognition query that is recognized" data-format="JSON" }
{
  "authority_id": "did:webvh:QmZjy1t9oFiaFjhX2e38uMuR7mgtdLjHPMGfjEfvrsmaiq:trust.go.id",
  "entity_id": "did:web:trust-registry.partner.example",
  "action": "issue",
  "resource": "org.iso.18013.5.1.mDL.1",
  "recognized": true,
  "time_evaluated": "2026-10-17T03:11:20Z",
  "message": "Recognized 2026-03-01T00:00:00Z.",
  "statement": "eyJ0eXAiOiJ2bmQuaWQuaWRjdGYucmVjb2duaXRpb24tc3RhdGVtZW50K2p3dCIsImFsZyI6IkVTMjU2Iiwia2lkIjoiZGlkOndlYnZoOlFtWmp5MXQ5b0ZpYUZqaFgyZTM4dU11UjdtZ3RkTGpIUE1HZmpFZnZyc21haXE6dHJ1c3QuZ28uaWQjcmVjb2duaXRpb24tc3RhdGVtZW50LTEifQ.eyJhdXRob3JpdHlfaWQiOiJkaWQ6d2Vidmg6UW1aankxdDlvRmlhRmpoWDJlMzh1TXVSN21ndGRMakhQTUdmakVmdnJzbWFpcTp0cnVzdC5nby5pZCIsImVudGl0eV9pZCI6ImRpZDp3ZWI6dHJ1c3QtcmVnaXN0cnkucGFydG5lci5leGFtcGxlIiwiYWN0aW9uIjoiaXNzdWUiLCJyZXNvdXJjZSI6Im9yZy5pc28uMTgwMTMuNS4xLm1ETC4xIiwicmVjb2duaXplZCI6dHJ1ZSwidGltZV9ldmFsdWF0ZWQiOiIyMDI2LTEwLTE3VDAzOjExOjIwWiIsImlhdCI6MTc5MjIwNjY4MCwiZXhwIjoxNzkyMjQ5ODgwfQ.ZlfjKXH0SWSMUgiV_PD8AjcnYfQV6SyeC_qtw1GtNHRAvBQMQFacUpJKXc5SjttoYDD1AyCcVBd0_m4MO_U0bQ"
}
```

The same question about another foreign authority, evaluated at a stated
time, which Trust Registry answers from the decisions that held then. The
answer carries no `message`, which is optional:

``` { .http title="POST /recognition, evaluated at a stated time" data-format="HTTP" }
POST /recognition HTTP/1.1
Host: query.trust.go.id
Content-Type: application/json

{
  "authority_id": "did:webvh:QmZjy1t9oFiaFjhX2e38uMuR7mgtdLjHPMGfjEfvrsmaiq:trust.go.id",
  "entity_id": "did:web:registry.other-ecosystem.example",
  "action": "issue",
  "resource": "org.iso.18013.5.1.mDL.1",
  "context": {
    "time": "2026-09-01T00:00:00Z"
  }
}
```

``` { .json title="The answer to a recognition query that is not recognized" data-format="JSON" }
{
  "authority_id": "did:webvh:QmZjy1t9oFiaFjhX2e38uMuR7mgtdLjHPMGfjEfvrsmaiq:trust.go.id",
  "entity_id": "did:web:registry.other-ecosystem.example",
  "action": "issue",
  "resource": "org.iso.18013.5.1.mDL.1",
  "recognized": false,
  "time_requested": "2026-09-01T00:00:00Z",
  "time_evaluated": "2026-10-17T03:11:20Z",
  "context": {
    "time": "2026-09-01T00:00:00Z"
  },
  "statement": "eyJ0eXAiOiJ2bmQuaWQuaWRjdGYucmVjb2duaXRpb24tc3RhdGVtZW50K2p3dCIsImFsZyI6IkVTMjU2Iiwia2lkIjoiZGlkOndlYnZoOlFtWmp5MXQ5b0ZpYUZqaFgyZTM4dU11UjdtZ3RkTGpIUE1HZmpFZnZyc21haXE6dHJ1c3QuZ28uaWQjcmVjb2duaXRpb24tc3RhdGVtZW50LTEifQ.eyJhdXRob3JpdHlfaWQiOiJkaWQ6d2Vidmg6UW1aankxdDlvRmlhRmpoWDJlMzh1TXVSN21ndGRMakhQTUdmakVmdnJzbWFpcTp0cnVzdC5nby5pZCIsImVudGl0eV9pZCI6ImRpZDp3ZWI6cmVnaXN0cnkub3RoZXItZWNvc3lzdGVtLmV4YW1wbGUiLCJhY3Rpb24iOiJpc3N1ZSIsInJlc291cmNlIjoib3JnLmlzby4xODAxMy41LjEubURMLjEiLCJyZWNvZ25pemVkIjpmYWxzZSwidGltZV9yZXF1ZXN0ZWQiOiIyMDI2LTA5LTAxVDAwOjAwOjAwWiIsInRpbWVfZXZhbHVhdGVkIjoiMjAyNi0xMC0xN1QwMzoxMToyMFoiLCJpYXQiOjE3OTIyMDY2ODAsImV4cCI6MTc5MjI0OTg4MH0.RVgEDCZcFcIGUgSRD16ALbicYeMyGQpwpd4gNRRtVHYf-_ZPKVyofq8L-UBl_Rj6F-dEbbdkSi7KYHHlguk2wA"
}
```

The host is an illustration; the Governance Profile publishes the address
of the query endpoint in force.

## The HTTPS binding {#ts-4-02-the-https-binding}

Both endpoints are public. Anyone may ask, nobody is asked who they are,
and the same question receives the same answer whoever asks it. That is
what keeps the registry from learning which citizen deals with which
party, the rule the trusted list already follows in
[Publication][ts-5-01-publication].

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-4-02-004 }**REQ-TS-4-02-004** Trust Registry MUST serve the query endpoint over HTTP with Transport Layer Security (TLS) only.
- [](){ #req-ts-4-02-005 }**REQ-TS-4-02-005** Trust Registry MUST serve `POST <endpoint>/authorization` and `POST <endpoint>/recognition` at the query endpoint, where `<endpoint>` is the address the Governance Profile publishes.
- [](){ #req-ts-4-02-006 }**REQ-TS-4-02-006** Trust Registry MUST NOT serve any other operation at the query endpoint.
- [](){ #req-ts-4-02-007 }**REQ-TS-4-02-007** Trust Registry MUST answer a query without authentication.
- [](){ #req-ts-4-02-008 }**REQ-TS-4-02-008** Trust Registry MUST NOT require any identifier of the reader.
- [](){ #req-ts-4-02-009 }**REQ-TS-4-02-009** A reader MUST send a query with the header `Content-Type: application/json` and a body of that media type.
- [](){ #req-ts-4-02-010 }**REQ-TS-4-02-010** A reader MUST NOT send any header, cookie, or member that identifies a holder, a device, an installation, a transaction, or the reader itself, `X-Request-ID` and `Authorization` included.
- [](){ #req-ts-4-02-011 }**REQ-TS-4-02-011** A reader MUST NOT send a query for an entity, action and resource it holds a current answer for.
- [](){ #req-ts-4-02-012 }**REQ-TS-4-02-012** Trust Registry MUST answer a query it evaluated with `200` and media type `application/json`.
- [](){ #req-ts-4-02-013 }**REQ-TS-4-02-013** Trust Registry MUST limit the rate of queries from one network address to the limit the Governance Profile sets.
- [](){ #req-ts-4-02-014 }**REQ-TS-4-02-014** Trust Registry MUST NOT record which query a network address sent.

</div>

The rate limit is keyed on the one thing the transport shows, the network
address, because nothing else identifies a caller and nothing else is
asked for. Counting queries per address needs no record of what each one
asked.

IDCTF departs from the HTTPS binding of [TRQP][ref-trqp] in five places,
each on purpose:

- **No bearer token and no `401`.** TRQP leaves authentication to the
  deployment, and a public registry asks for none.
- **No `X-Request-ID`.** TRQP offers it for tracing; it would let the
  registry link queries to one caller.
- **A query for something Trust Registry does not know is answered `200`
  with a signed negative**, where TRQP lists `404` for an entity, action or
  resource it does not recognize. Only a signed answer can be cached, and a
  `404` would also tell anyone who asks whether a party has registered
  without being accredited.
- **`429` and `503` are added** to the four statuses TRQP lists, for the
  rate limit and for an unreachable signer.
- **Every answer carries a `statement` member**, the signature TRQP leaves
  to the deployment.

The endpoint is not discoverable from Trust Authority's DID Document, the
second path TRQP names, because
[REQ-TS-5-02-027][req-ts-5-02-027] forbids a `service` there.

## Authorization query {#ts-4-02-authorization-query}

An authorization query asks whether Trust Authority holds a record that the
entity may take the action on the resource.
[The table of query members][tbl-ts-4-02-query-members] gives each member of
its body, and the same table serves the recognition query. The answer,
what a permission names, and how a reader checks the answer are in
[Answering with an Authority Statement](answering-with-an-authority-statement.md).

[](){ #tbl-ts-4-02-query-members }

<figure markdown="1" class="ekdn-table">

| Member | Type | Presence | Value |
|---|---|---|---|
| `authority_id` | string | Present | Trust Authority's `did:webvh` |
| `entity_id` | string | Present | The entity asked about: an entity's `did:webvh` in an authorization query, a foreign authority's identifier in a recognition query |
| `action` | string | Present | The action asked about |
| `resource` | string | Present | The resource asked about |
| `context` | object | Optional | Carries `time` and nothing else |
| `context.time` | string | Present when `context` is | The time the query asks about, in UTC with the `Z` offset |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-4-02-015 }**REQ-TS-4-02-015** A reader MUST send an authorization query whose body conforms to the `AuthorizationRequest` schema of [TRQP][ref-trqp] and carries every member [the table of query members][tbl-ts-4-02-query-members] marks present.
- [](){ #req-ts-4-02-016 }**REQ-TS-4-02-016** `authority_id` MUST be the `did:webvh` of Trust Authority whose SCID the reader carries.
- [](){ #req-ts-4-02-017 }**REQ-TS-4-02-017** In an authorization query, `entity_id` MUST be the `did:webvh` of the entity.
- [](){ #req-ts-4-02-089 }**REQ-TS-4-02-089** In an authorization query, `action` and `resource` MUST take the forms [What a permission names][ts-5-05-what-a-permission-names] fixes.
- [](){ #req-ts-4-02-018 }**REQ-TS-4-02-018** A reader MUST NOT send a `context` member other than `time`.
- [](){ #req-ts-4-02-019 }**REQ-TS-4-02-019** Trust Registry MUST ignore a `context` member other than `time`, as [TRQP][ref-trqp] requires of an endpoint.
- [](){ #req-ts-4-02-020 }**REQ-TS-4-02-020** Trust Registry MUST answer an authorization query with the answer [Answering with an Authority Statement](answering-with-an-authority-statement.md) fixes.
- [](){ #req-ts-4-02-021 }**REQ-TS-4-02-021** Trust Registry MUST answer `authorized: false` for an `entity_id` it holds no record of, and for a `resource` whose credential type the catalog does not register, as for a permission that was never granted.
- [](){ #req-ts-4-02-022 }**REQ-TS-4-02-022** Trust Registry MUST NOT answer a query about an entity it holds no record of with a `message` that differs from the one it gives for a permission that was never granted.

</div>

The last two rules keep the endpoint from becoming a register of who has
applied. The trusted list already says who is accredited; a party that has
only registered may do nothing, and the answer about it is the same as the
answer about a party nobody has heard of.

## Recognition query {#ts-4-02-recognition-query}

A recognition query asks whether the Root Authority recognizes a foreign
authority as authoritative for an action on a credential type, the first
meaning [recognition][glossary-r] has in IDCTF. Recognition is granted per
credential type: an authority recognized for issuing the mobile driving
license is not thereby recognized for anything else. Who is recognized, and
on what terms, [is the Governance Framework's to decide][gf-recognition]; this clause fixes
how the question is asked and answered, and [chain of trust][chain-of-trust]
sets out where the answer is used.

The query carries the members of
[the table of query members][tbl-ts-4-02-query-members].
[The table of recognition actions][tbl-ts-4-02-recognition-actions] gives the
one action the ecosystem recognizes today; the Governance Profile holds the
list in force.

[](){ #tbl-ts-4-02-recognition-actions }

<figure markdown="1" class="ekdn-table">

| Action | What it recognizes |
|---|---|
| `issue` | The foreign authority's issuers, as issuers of the credential type the resource names |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-4-02-023 }**REQ-TS-4-02-023** A reader MUST send a recognition query whose body conforms to the `RecognitionRequest` schema of [TRQP][ref-trqp] and carries every member [the table of query members][tbl-ts-4-02-query-members] marks present.
- [](){ #req-ts-4-02-024 }**REQ-TS-4-02-024** In a recognition query, `entity_id` MUST be the identifier the foreign authority is recognized under, as a Uniform Resource Identifier (URI).
- [](){ #req-ts-4-02-025 }**REQ-TS-4-02-025** In a recognition query, `action` MUST be one the Governance Profile lists for recognition.
- [](){ #req-ts-4-02-026 }**REQ-TS-4-02-026** In a recognition query, `resource` MUST be a credential type identifier, with its version and without an attribute.
- [](){ #req-ts-4-02-027 }**REQ-TS-4-02-027** The credential type in `resource` MUST be one the Credential Rulebook Catalog registers.

</div>

### The recognition answer {#ts-4-02-the-recognition-answer}

The answer is the `RecognitionResponse` of [TRQP][ref-trqp] with one member
added, `statement`, which carries the signature the way an Authority
Statement does. [The table of recognition answer members][tbl-ts-4-02-recognition-answer-members]
gives each member.

[](){ #tbl-ts-4-02-recognition-answer-members }

<figure markdown="1" class="ekdn-table">

| Member | Type | Presence | Value |
|---|---|---|---|
| `authority_id` | string | Present | Trust Authority's `did:webvh` |
| `entity_id` | string | Present | The foreign authority the query named |
| `action` | string | Present | The action the query named |
| `resource` | string | Present | The credential type the query named |
| `recognized` | boolean | Present | `true` when the Root Authority recognizes the foreign authority for the action on the credential type at the time evaluated, `false` otherwise |
| `time_requested` | string | Present when the query carried `context.time` | The time the query asked about |
| `time_evaluated` | string | Present | The time Trust Registry evaluated the query at |
| `context` | object | Present when the query carried one | The context object of the query, returned unchanged |
| `message` | string | Optional | Text for an operator reading a log |
| `statement` | string | Present | The signed answer, as [The recognition statement][ts-4-02-the-recognition-statement] gives it |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-4-02-028 }**REQ-TS-4-02-028** Trust Registry MUST return an answer that conforms to the `RecognitionResponse` schema of [TRQP][ref-trqp].
- [](){ #req-ts-4-02-029 }**REQ-TS-4-02-029** Trust Registry MUST carry every member [the table of recognition answer members][tbl-ts-4-02-recognition-answer-members] marks present.
- [](){ #req-ts-4-02-030 }**REQ-TS-4-02-030** `authority_id` MUST be the `did:webvh` of Trust Authority.
- [](){ #req-ts-4-02-031 }**REQ-TS-4-02-031** `entity_id`, `action`, and `resource` MUST repeat the values the query carried, byte for byte.
- [](){ #req-ts-4-02-032 }**REQ-TS-4-02-032** `recognized` MUST be `true` only when the Root Authority recognizes the foreign authority for that action on that credential type at the time in `time_evaluated`, or at the time in `time_requested` where the query carried one.
- [](){ #req-ts-4-02-033 }**REQ-TS-4-02-033** Trust Registry MUST answer `recognized: false` for an authority never recognized, for a recognition that has been withdrawn, for an `action` the Governance Profile does not list for recognition, and for a credential type the catalog does not register.
- [](){ #req-ts-4-02-034 }**REQ-TS-4-02-034** Trust Registry MUST write `time_evaluated` and `time_requested` in the date and time format [TRQP][ref-trqp] requires, in Coordinated Universal Time (UTC) with the `Z` offset.
- [](){ #req-ts-4-02-035 }**REQ-TS-4-02-035** Trust Registry MUST NOT state a recognition in `message` that `recognized` does not state.
- [](){ #req-ts-4-02-036 }**REQ-TS-4-02-036** Trust Registry MUST NOT carry a citizen's data, a transaction identifier, or the identity of the party that asked in any member of the answer.

</div>

### The recognition statement {#ts-4-02-the-recognition-statement}

Each answer is signed as a JSON Web Token (JWT) as
[RFC 7519][ref-rfc7519] defines one, signed as a JSON Web Signature (JWS) in
the compact serialization of [RFC 7515][ref-rfc7515], and carried in the
`statement` member. Its payload repeats the answer and adds the two times
that bound it. [The table of recognition statement claims][tbl-ts-4-02-recognition-statement-claims]
gives each claim.

The signing key is the recognition statement key that
[Trust Authority's own keys][trust-authoritys-own-keys] names, held in Trust
Authority's HSM. Trust Registry builds the answer and asks Trust Authority
to sign it, as it does for an Authority Statement, and Trust Authority
builds the payload again from its own record and refuses a request the two
disagree on. A recognition answer is
not an Authority Statement: it records what the Root Authority accepts from
another ecosystem, not what one entity may do, so it takes a key and a
`typ` of its own.

[](){ #tbl-ts-4-02-recognition-statement-claims }

<figure markdown="1" class="ekdn-table">

| Claim | Type | Presence | Value |
|---|---|---|---|
| `authority_id` | string | Present | As the answer carries it |
| `entity_id` | string | Present | As the answer carries it |
| `action` | string | Present | As the answer carries it |
| `resource` | string | Present | As the answer carries it |
| `recognized` | boolean | Present | As the answer carries it |
| `time_requested` | string | Present when the answer carries it | As the answer carries it |
| `time_evaluated` | string | Present | As the answer carries it |
| `iat` | number | Present | The time the answer was signed, in seconds since the Unix epoch |
| `exp` | number | Present | The time the answer stops being current, in seconds since the Unix epoch |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-4-02-037 }**REQ-TS-4-02-037** The `statement` member MUST be a JWS in the compact serialization of [RFC 7515][ref-rfc7515] whose payload is the JSON claims set of [RFC 7519][ref-rfc7519].
- [](){ #req-ts-4-02-038 }**REQ-TS-4-02-038** The `typ` header parameter MUST be `vnd.id.idctf.recognition-statement+jwt`.
- [](){ #req-ts-4-02-039 }**REQ-TS-4-02-039** The `alg` header parameter MUST be one the Governance Profile allows for a recognition answer.
- [](){ #req-ts-4-02-040 }**REQ-TS-4-02-040** The `kid` header parameter MUST name a key of the purpose `recognition-statement`, as [Naming the key][ts-01-naming-the-key] of TS-01 requires.
- [](){ #req-ts-4-02-041 }**REQ-TS-4-02-041** The payload MUST carry every claim [the table of recognition statement claims][tbl-ts-4-02-recognition-statement-claims] marks present, each holding the value the answer carries in the member of the same name.
- [](){ #req-ts-4-02-042 }**REQ-TS-4-02-042** The interval between `iat` and `exp` MUST be the Time to Live (TTL) the Governance Profile sets for a recognition answer.
- [](){ #req-ts-4-02-043 }**REQ-TS-4-02-043** Trust Authority MUST hold the private key in its HSM.
- [](){ #req-ts-4-02-044 }**REQ-TS-4-02-044** Trust Registry MUST NOT hold the private key.
- [](){ #req-ts-4-02-045 }**REQ-TS-4-02-045** Trust Authority MUST publish the public key as a verification method of its own DID Document.
- [](){ #req-ts-4-02-046 }**REQ-TS-4-02-046** Trust Authority MUST NOT sign a recognition answer with any other key that [Trust Authority's own keys][trust-authoritys-own-keys] names, nor sign anything else with the recognition statement key.
- [](){ #req-ts-4-02-082 }**REQ-TS-4-02-082** Trust Authority MUST build the payload it signs from its own record of the recognition, not from the payload Trust Registry presents.
- [](){ #req-ts-4-02-083 }**REQ-TS-4-02-083** Trust Authority MUST refuse a signing request whose answer does not match that record.

</div>

### Reading a recognition answer {#ts-4-02-reading-a-recognition-answer}

A reader checks a recognition answer the way it checks an Authority
Statement, in the steps of
[Reading the answer][ts-5-05-reading-the-answer], with three things read in
place of their counterparts: the tolerance limit the Governance Profile sets
for a recognition answer, the `typ` of a recognition answer, and the
recognition in place of the permission. The rules are the same rules,
applied to a second artifact, so they are cited here rather than written
twice. One rule of that page is not applied: a foreign authority has no
entry on the trusted list, so a change there cannot discard a cached
recognition answer. A withdrawn recognition reaches a reader on its next
fetch, no later than the answer's `exp` plus the tolerance limit.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-4-02-047 }**REQ-TS-4-02-047** A reader MUST apply [REQ-TS-5-05-033][req-ts-5-05-033] to [REQ-TS-5-05-036][req-ts-5-05-036], [REQ-TS-5-05-038][req-ts-5-05-038] to [REQ-TS-5-05-045][req-ts-5-05-045], and [REQ-TS-5-05-053][req-ts-5-05-053] to a recognition answer, reading the tolerance limit the Governance Profile sets for a recognition answer for the one [REQ-TS-5-05-034][req-ts-5-05-034] names, `vnd.id.idctf.recognition-statement+jwt` for the `typ` [REQ-TS-5-05-039][req-ts-5-05-039] names, and the recognition for the permission [REQ-TS-5-05-053][req-ts-5-05-053] names.
- [](){ #req-ts-4-02-048 }**REQ-TS-4-02-048** A reader MUST NOT accept a credential issued under a foreign authority for a credential type unless it holds a usable recognition answer for that authority, the action `issue`, and that type, whose `recognized` is `true`.

</div>

### Recognition lifecycle {#ts-4-02-recognition-lifecycle}

A recognition begins when the Root Authority grants it and Trust Authority
records it, and ends when the Root Authority withdraws it. It names one
foreign authority, one action and one credential type, and it does not
change: recognizing the same authority for another type is a second
recognition beside the first.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-4-02-049 }**REQ-TS-4-02-049** Trust Authority MUST record one recognition for each foreign authority, action and credential type the Root Authority recognizes.
- [](){ #req-ts-4-02-050 }**REQ-TS-4-02-050** Trust Authority MUST record the time a recognition came into force and the time it was withdrawn, and keep a withdrawn recognition with its history rather than deleting it.
- [](){ #req-ts-4-02-051 }**REQ-TS-4-02-051** Trust Authority MUST NOT widen or narrow a recorded recognition.
- [](){ #req-ts-4-02-052 }**REQ-TS-4-02-052** Trust Registry MUST answer a recognition query carrying `context.time` from the status that held at that time, and one carrying no `context.time` from the status that holds at `time_evaluated`.

</div>

## Errors {#ts-4-02-errors}

A query Trust Registry cannot evaluate is answered with a problem document
as [RFC 9457][ref-rfc9457] defines one. The `type` member is the code: it
names one entry of a closed list, so that a reader and an Assessment Body
can act on it without reading prose. [The table of problem types][tbl-ts-4-02-problem-types]
gives each entry with its status and its title. Each `type` is the IDCTF
root `https://idctf.id/ns/` followed by `problems/` and the code.

[](){ #tbl-ts-4-02-problem-types }

<figure markdown="1" class="ekdn-table">

| Code | Status | Title | Raised when |
|---|---|---|---|
| `malformed-query` | `400` | `Malformed query` | The body is not JSON, a member [the table of query members][tbl-ts-4-02-query-members] marks present is absent, a member has the wrong type, or `context.time` is not in UTC with the `Z` offset |
| `unknown-authority` | `404` | `Unknown authority` | `authority_id` is not Trust Authority's `did:webvh` |
| `unknown-operation` | `404` | `Unknown operation` | The method or the path is not one of the two operations of the query endpoint |
| `rate-limited` | `429` | `Rate limited` | The network address has passed the rate limit |
| `server-error` | `500` | `Server error` | Trust Registry failed for a reason none of the other codes names, Trust Authority refusing to sign the answer included |
| `signer-unavailable` | `503` | `Signer unavailable` | Trust Registry cannot reach the key that signs the answer |

</figure>

A query addressed to another authority receives a problem document rather
than a negative answer, because Trust Authority speaks only for itself and
signs nothing about another authority's records:

``` { .http title="404, the answer to a query addressed to another authority" data-format="HTTP" }
HTTP/1.1 404 Not Found
Content-Type: application/problem+json

{
  "type": "https://idctf.id/ns/problems/unknown-authority",
  "title": "Unknown authority",
  "status": 404
}
```

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-4-02-053 }**REQ-TS-4-02-053** Trust Registry MUST answer a query it cannot evaluate with the status [the table of problem types][tbl-ts-4-02-problem-types] gives for the condition, media type `application/problem+json`, and a problem document whose `type` and `title` are the ones that table gives and whose `status` equals the status of the response.
- [](){ #req-ts-4-02-054 }**REQ-TS-4-02-054** Trust Registry MUST NOT answer with a `type` that table does not hold.
- [](){ #req-ts-4-02-055 }**REQ-TS-4-02-055** Trust Registry MUST NOT carry in `detail` or `instance` anything about an entity, a foreign authority, or the party that asked.
- [](){ #req-ts-4-02-056 }**REQ-TS-4-02-056** Trust Registry MUST write every `type` under the root named by the version of this specification it conforms to.
- [](){ #req-ts-4-02-090 }**REQ-TS-4-02-090** A reader MUST treat the root of a `type` as [REQ-TS-5-01-084][req-ts-5-01-084] to [REQ-TS-5-01-086][req-ts-5-01-086] treat the root of the trusted list's identifiers.
- [](){ #req-ts-4-02-057 }**REQ-TS-4-02-057** A reader MUST compare a `type` with the value [the table of problem types][tbl-ts-4-02-problem-types] gives byte for byte.
- [](){ #req-ts-4-02-091 }**REQ-TS-4-02-091** A reader MUST NOT dereference a `type`.
- [](){ #req-ts-4-02-058 }**REQ-TS-4-02-058** A reader MUST treat a problem document, whatever its `type`, as no answer.
- [](){ #req-ts-4-02-059 }**REQ-TS-4-02-059** A reader MUST NOT cache a problem document.
- [](){ #req-ts-4-02-092 }**REQ-TS-4-02-092** A reader MUST NOT read a problem document as a negative answer.
- [](){ #req-ts-4-02-060 }**REQ-TS-4-02-060** A reader that receives a problem document MUST go on using the answer it already holds for the same query, within the limits [Lifetime][ts-5-05-lifetime] sets.
- [](){ #req-ts-4-02-084 }**REQ-TS-4-02-084** Trust Registry MUST answer a query whose answer Trust Authority refused to sign with `server-error`.
- [](){ #req-ts-4-02-093 }**REQ-TS-4-02-093** Trust Registry MUST NOT state in the problem document or in any header that Trust Authority refused to sign the answer.
- [](){ #req-ts-4-02-085 }**REQ-TS-4-02-085** Trust Authority MUST record each signing request it refuses under [REQ-TS-4-02-083][req-ts-4-02-083] or [REQ-TS-5-05-056][req-ts-5-05-056] as a security incident for the Root Authority to decide on.

</div>

A problem document carries no signature, so a reader can trust nothing in
it and does not try: it neither grants nor withdraws anything. That is also
why an unreachable signer is answered `503` rather than with an unsigned
answer, and why the reader falls back to the copy it holds, the behavior
[the three rules for reading the copy][three-rules-for-reading-the-copy]
ask for.

A signer that refuses is answered `server-error`, like any other failure
inside Trust Registry. A refusal means the registry built an answer its own
authority does not hold, through a defect or because someone else controls
it. That is an incident for the Root Authority, not a condition a reader can
act on, and naming it on the wire would tell anyone watching the endpoint
which check the registry has started to fail. It is not `503` either: that
status asks a client to try again, and a refusal does not go away on a
retry.

## The catalog {#ts-4-02-the-catalog}

Trust Registry publishes the catalog on the central CDN as a list of types
and one file per Rulebook version, as the
[Credential Rulebook Catalog](../credential-rulebook/index.md) sets out. The
list is signed; each Rulebook file is plain JSON and is bound to the list by
its digest, so one signature covers every Rulebook and a published Rulebook
stays the file its Provider proposed, unchanged. Every published
version is listed, a private party's as much as one under the `id.idctf`
root: a type that is not in the catalog has no Rulebook anyone can read.

The catalog has three addresses under `<catalog>`, the address the
Governance Profile publishes:

- `GET <catalog>/rulebooks`, the catalog list;
- `GET <catalog>/rulebooks/{id}`, one Rulebook version, where `{id}` is the
  Rulebook's `id` with its version, `id.idctf.ktp.1`;
- `<catalog>/vocab/<type>`, the page each term of an `ldp_vc` context
  expands to, which [REQ-CR-056][req-cr-056] names and
  [REQ-TS-4-02-086][req-ts-4-02-086] serves.

The schema, the display metadata, and the context a Rulebook names are
fetched at the addresses its own fields carry, which need not sit under
`/rulebooks/`.

### Catalog list payload {#ts-4-02-catalog-list-payload}

The list as Trust Registry serves it, for the five Rulebooks the
[registered Rulebooks][registered-rulebooks] table carries as illustrations.
None of them is registered. Each `rulebook_digest` is the digest of the
`rulebook.json` its example page shows, and the list was signed with the
catalog key of the Trust Authority DID shown in `iss` and verifies.

``` { .http title="GET /rulebooks, Trust Registry catalog" data-format="HTTP" }
GET /rulebooks HTTP/1.1
Host: catalog.trust.go.id
```

``` { .text title="The catalog list as served" data-format="JWS" }
eyJ0eXAiOiJ2bmQuaWQuaWRjdGYuY2F0YWxvZytqd3QiLCJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDp3ZWJ2aDpRbVpqeTF0OW9GaWFGamhYMmUzOHVNdVI3bWd0ZExqSFBNR2ZqRWZ2cnNtYWlxOnRydXN0LmdvLmlkI2NhdGFsb2ctMSJ9.eyJpc3MiOiJkaWQ6d2Vidmg6UW1aankxdDlvRmlhRmpoWDJlMzh1TXVSN21ndGRMakhQTUdmakVmdnJzbWFpcTp0cnVzdC5nby5pZCIsImlhdCI6MTc5MjIwNjY4MCwiZXhwIjoxNzkyMjkzMDgwLCJydWxlYm9va3MiOlt7ImlkIjoiaWQuaWRjdGYua3RwLjEiLCJydWxlYm9vayI6Imh0dHBzOi8vY2F0YWxvZy50cnVzdC5nby5pZC9ydWxlYm9va3MvaWQuaWRjdGYua3RwLjEiLCJydWxlYm9va19kaWdlc3QiOiJzaGEzODQtZVpwZk9WSmo4TVU0MWNBSWNmTldkdDRwM2dNUmJVbUJPZGowc3JPWDFXWmZ5TllSSjZHcmsvMStNNnJzN3ZYQyJ9LHsiaWQiOiJpZC5pZGN0Zi5rYXJ0dS1pbmRvbmVzaWEtc2VoYXQuMSIsInJ1bGVib29rIjoiaHR0cHM6Ly9jYXRhbG9nLnRydXN0LmdvLmlkL3J1bGVib29rcy9pZC5pZGN0Zi5rYXJ0dS1pbmRvbmVzaWEtc2VoYXQuMSIsInJ1bGVib29rX2RpZ2VzdCI6InNoYTM4NC01aklqdXp5QkNYd0NUMWZSRFBWOGtsYmlXdGQ5SStzT2VSQ3ZtVXp5VDZDcTJLLzBqNXZtVkluU1p6ZWFrTjZkIn0seyJpZCI6ImlkLmlkY3RmLmthcnR1LWFzbi4xIiwicnVsZWJvb2siOiJodHRwczovL2NhdGFsb2cudHJ1c3QuZ28uaWQvcnVsZWJvb2tzL2lkLmlkY3RmLmthcnR1LWFzbi4xIiwicnVsZWJvb2tfZGlnZXN0Ijoic2hhMzg0LURuWUEySEVJRlFFSjlJclMxeXJrOWFGT0J6Skx0QTFlajYyWHE0MnZtM1Fma0ZWMXlnZmdXenZvUEtqZGFZN3YifSx7ImlkIjoiaWQuaWRjdGYua2FydHUtbmlrYWguMSIsInJ1bGVib29rIjoiaHR0cHM6Ly9jYXRhbG9nLnRydXN0LmdvLmlkL3J1bGVib29rcy9pZC5pZGN0Zi5rYXJ0dS1uaWthaC4xIiwicnVsZWJvb2tfZGlnZXN0Ijoic2hhMzg0LUFnMFRtRC9RVitjR09aaEN4VVdyVjV1TEQ0YTR1cXVUREJib3lmeDIwcnFjenQ4ek5PU2FOeGQrYUw3VHhRclYifSx7ImlkIjoib3JnLmlzby4xODAxMy41LjEubURMLjEiLCJydWxlYm9vayI6Imh0dHBzOi8vY2F0YWxvZy50cnVzdC5nby5pZC9ydWxlYm9va3Mvb3JnLmlzby4xODAxMy41LjEubURMLjEiLCJydWxlYm9va19kaWdlc3QiOiJzaGEzODQtbW5hTDhRTnMvNWlVYnR6V0QrQlBScTJleVIzTVhMYUxvYVZrTEg1bE40TklON0UvdHJaNE5rUitKUHpDR01sMSJ9XX0.Nnd5wRhEQ0Vhq6NE8xxzVVB35NGTu_KT2DjftWRzct_pzU_nG7RELT5P0mgTfx6WQR8qZXaai9psSB78zGbNnQ
```

``` { .json title="Catalog list payload, decoded" data-format="JSON" }
{
  "iss": "did:webvh:QmZjy1t9oFiaFjhX2e38uMuR7mgtdLjHPMGfjEfvrsmaiq:trust.go.id",
  "iat": 1792206680,
  "exp": 1792293080,
  "rulebooks": [
    {
      "id": "id.idctf.ktp.1",
      "rulebook": "https://catalog.trust.go.id/rulebooks/id.idctf.ktp.1",
      "rulebook_digest": "sha384-eZpfOVJj8MU41cAIcfNWdt4p3gMRbUmBOdj0srOX1WZfyNYRJ6Grk/1+M6rs7vXC"
    },
    {
      "id": "id.idctf.kartu-indonesia-sehat.1",
      "rulebook": "https://catalog.trust.go.id/rulebooks/id.idctf.kartu-indonesia-sehat.1",
      "rulebook_digest": "sha384-5jIjuzyBCXwCT1fRDPV8klbiWtd9I+sOeRCvmUzyT6Cq2K/0j5vmVInSZzeakN6d"
    },
    {
      "id": "id.idctf.kartu-asn.1",
      "rulebook": "https://catalog.trust.go.id/rulebooks/id.idctf.kartu-asn.1",
      "rulebook_digest": "sha384-DnYA2HEIFQEJ9IrS1yrk9aFOBzJLtA1ej62Xq42vm3QfkFV1ygfgWzvoPKjdaY7v"
    },
    {
      "id": "id.idctf.kartu-nikah.1",
      "rulebook": "https://catalog.trust.go.id/rulebooks/id.idctf.kartu-nikah.1",
      "rulebook_digest": "sha384-Ag0TmD/QV+cGOZhCxUWrV5uLD4a4uquTDBboyfx20rqczt8zNOSaNxd+aL7TxQrV"
    },
    {
      "id": "org.iso.18013.5.1.mDL.1",
      "rulebook": "https://catalog.trust.go.id/rulebooks/org.iso.18013.5.1.mDL.1",
      "rulebook_digest": "sha384-mnaL8QNs/5iUbtzWD+BPRq2eyR3MXLaLoaVkLH5lN4NIN7E/trZ4NkR+JPzCGMl1"
    }
  ]
}
```

The host is an illustration; the Governance Profile publishes the catalog
address in force.

### The catalog list {#ts-4-02-the-catalog-list}

The list is a JWT signed as a JWS in the compact serialization.
[The table of catalog list claims][tbl-ts-4-02-catalog-list-claims] gives
each claim of its payload, and
[the table of catalog entry members][tbl-ts-4-02-catalog-entry-members] each
member of one entry.

[](){ #tbl-ts-4-02-catalog-list-claims }

<figure markdown="1" class="ekdn-table">

| Claim | Type | Presence | Value |
|---|---|---|---|
| `iss` | string | Present | Trust Authority's `did:webvh` |
| `iat` | number | Present | The time the list was signed, in seconds since the Unix epoch |
| `exp` | number | Present | The time the list stops being current, in seconds since the Unix epoch |
| `rulebooks` | array of object | Present | One entry for each published Rulebook version |

</figure>

[](){ #tbl-ts-4-02-catalog-entry-members }

<figure markdown="1" class="ekdn-table">

| Member | Type | Presence | Value |
|---|---|---|---|
| `id` | string | Present | The Rulebook's `id`, with its version |
| `rulebook` | string | Present | `<catalog>/rulebooks/` followed by `id` |
| `rulebook_digest` | string | Present | The [Subresource Integrity (SRI)][ref-sri] digest of the Rulebook file, in `sha384` |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-4-02-061 }**REQ-TS-4-02-061** The catalog list MUST be a JWS in the compact serialization of [RFC 7515][ref-rfc7515] whose payload is the JSON claims set of [RFC 7519][ref-rfc7519].
- [](){ #req-ts-4-02-062 }**REQ-TS-4-02-062** The `typ` header parameter MUST be `vnd.id.idctf.catalog+jwt`.
- [](){ #req-ts-4-02-063 }**REQ-TS-4-02-063** The `alg` header parameter MUST be one the Governance Profile allows for the catalog list.
- [](){ #req-ts-4-02-064 }**REQ-TS-4-02-064** The `kid` header parameter MUST name a key of the purpose `catalog`, as [Naming the key][ts-01-naming-the-key] of TS-01 requires.
- [](){ #req-ts-4-02-065 }**REQ-TS-4-02-065** The payload MUST carry every claim and every entry member the two tables mark present.
- [](){ #req-ts-4-02-066 }**REQ-TS-4-02-066** The list MUST carry one entry for every published Rulebook version, public and private alike.
- [](){ #req-ts-4-02-094 }**REQ-TS-4-02-094** The list MUST NOT drop an entry once published.
- [](){ #req-ts-4-02-067 }**REQ-TS-4-02-067** The interval between `iat` and `exp` MUST be the TTL the Governance Profile sets for the catalog list.
- [](){ #req-ts-4-02-068 }**REQ-TS-4-02-068** Trust Authority MUST hold the private key of the catalog key in its HSM.
- [](){ #req-ts-4-02-095 }**REQ-TS-4-02-095** Trust Registry MUST NOT hold the private key of the catalog key.
- [](){ #req-ts-4-02-069 }**REQ-TS-4-02-069** Trust Authority MUST publish the public key as a verification method of its own DID Document.
- [](){ #req-ts-4-02-070 }**REQ-TS-4-02-070** Trust Authority MUST NOT sign the catalog list with any other key that [Trust Authority's own keys][trust-authoritys-own-keys] names, nor sign anything else with the catalog key.

</div>

### Publishing the catalog {#ts-4-02-publishing-the-catalog}

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-4-02-071 }**REQ-TS-4-02-071** Trust Registry MUST serve the current catalog list at `<catalog>/rulebooks` and each Rulebook version at `<catalog>/rulebooks/{id}`, over HTTP with TLS, as static files, without authentication and without any identifier of the reader.
- [](){ #req-ts-4-02-072 }**REQ-TS-4-02-072** Trust Registry MUST serve the catalog list with media type `application/jwt` and a Rulebook file with media type `application/json`.
- [](){ #req-ts-4-02-073 }**REQ-TS-4-02-073** Trust Registry MUST serve a Rulebook file as the bytes its `rulebook_digest` was computed over, and never change them, as [REQ-CR-049][req-cr-049] requires of the version.
- [](){ #req-ts-4-02-074 }**REQ-TS-4-02-074** Trust Registry MUST publish a new list when it publishes a Rulebook version, and before the `exp` of the current list.
- [](){ #req-ts-4-02-075 }**REQ-TS-4-02-075** Trust Registry MUST answer `404`, with no body, for a Rulebook version it has not published.
- [](){ #req-ts-4-02-086 }**REQ-TS-4-02-086** Trust Registry MUST answer each IRI [REQ-CR-056][req-cr-056] names with the catalog page of the credential type, which shows each term's schema type and its labels from `display`.
- [](){ #req-ts-4-02-087 }**REQ-TS-4-02-087** Trust Registry MUST NOT take a Rulebook from an entity's own `.well-known` metadata.
- [](){ #req-ts-4-02-088 }**REQ-TS-4-02-088** Trust Registry MUST refuse a proposed Rulebook at submission, before any review, when:
    - its `id` is already in the catalog;
    - it is a new version of a credential type and was submitted by anyone other than that type's Provider;
    - it comes from a private party and its `id` begins with `id.idctf.`;
    - it lists `ldp_vc` in `formats` alongside a `restricted` attribute;
    - it lists `ldp_vc` in `formats` alongside another format.
- [](){ #req-ts-4-02-099 }**REQ-TS-4-02-099** Trust Registry MUST refuse a proposed Rulebook at submission, before any review, when:
    - its `id` equals the mdoc `docType` of another Rulebook in the catalog;
    - its mdoc `docType` equals the `id` of another Rulebook in the catalog.

A `ReaderAuthRole` entry is read as a `docType` first, so a Rulebook `id` that equals another Rulebook's `docType` could never be named, as [REQ-TS-5-04-057][req-ts-5-04-057] sets out.

</div>

The catalog is served as static files from the CDN, so a missing file is a
bare `404` rather than a problem document; a problem document belongs to
the query endpoint alone.

### Reading the catalog {#ts-4-02-reading-the-catalog}

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-4-02-076 }**REQ-TS-4-02-076** A reader MUST verify the catalog list against a key published in the DID Document of the SCID it carries from build time, and refuse a list whose signature does not verify, whose `typ` is not `vnd.id.idctf.catalog+jwt`, or whose `iss` is not that Trust Authority.
- [](){ #req-ts-4-02-077 }**REQ-TS-4-02-077** A reader MUST treat a list as current until its `exp`.
- [](){ #req-ts-4-02-096 }**REQ-TS-4-02-096** A reader MAY keep using a list past its `exp` as a last-known-good copy, up to the tolerance limit the Governance Profile sets.
- [](){ #req-ts-4-02-097 }**REQ-TS-4-02-097** A reader MUST refuse a list past the tolerance limit the Governance Profile sets.
- [](){ #req-ts-4-02-078 }**REQ-TS-4-02-078** A reader MUST check a Rulebook file against the `rulebook_digest` its entry carries before it uses the file, and refuse a file that does not match.
- [](){ #req-ts-4-02-079 }**REQ-TS-4-02-079** A reader MUST refuse a Rulebook whose `id` no entry of the list it holds carries.
- [](){ #req-ts-4-02-080 }**REQ-TS-4-02-080** A reader MUST read the catalog list and every Rulebook from cache.
- [](){ #req-ts-4-02-098 }**REQ-TS-4-02-098** A reader MUST NOT fetch the catalog list or a Rulebook while a transaction runs.
- [](){ #req-ts-4-02-081 }**REQ-TS-4-02-081** *Withdrawn: [Versions][rulebook-versions] covers it.*

</div>

## Distribution points {#ts-4-02-distribution-points}

Beside the query endpoint and the catalog, Trust Registry serves the
artifacts other specifications define, each as a static file from the
central CDN. [The table of distribution points][tbl-ts-4-02-distribution-points]
gives where a reader finds the address of each and the specification that
binds it; no address is fixed on this page.

[](){ #tbl-ts-4-02-distribution-points }

<figure markdown="1" class="ekdn-table">

| Artifact | Where the address comes from | Bound by |
|---|---|---|
| The query endpoint | The Governance Profile | This specification |
| The catalog list and each Rulebook version | The Governance Profile, then the paths of [The catalog][ts-4-02-the-catalog] | This specification |
| The schema, display metadata, and context of a Rulebook | The fields of the Rulebook | [Rulebook structure](../credential-rulebook/rulebook-structure.md) |
| The trusted list | The Governance Profile, which `DistributionPoints` in the list repeats | [Publishing and reading the trusted list](publishing-and-reading-the-trusted-list.md) |
| The VICAL | `GET /vical` on Trust Registry | [Issuing and validating the X.509 certificates and the VICAL](issuing-and-validating-the-x509-certificates-and-the-vical.md) |
| The certificate revocation lists of the Issuer Root CA and the Verifier Root CA | The certificates each list covers | [Issuing and validating the X.509 certificates and the VICAL](issuing-and-validating-the-x509-certificates-and-the-vical.md) |
| The Use Statement status list and the accreditation status list | The `status_list` of the artifact each one covers, on the host the Governance Profile names | [Publishing and reading a status list](publishing-and-reading-a-status-list.md) |

</figure>

A credential's own status list is not on this table: an issuer publishes it
on its own domain, never through Trust Registry.

## Security considerations {#ts-4-02-security-considerations}

Each threat below is answered by the requirement named with it.

- **A recognition answer edited in the cache or on the wire.** The
  signature covers every field a reader acts on, and the reader checks the
  body against it on every read, [REQ-TS-4-02-041][req-ts-4-02-041] and
  [REQ-TS-4-02-047][req-ts-4-02-047].
- **A forged recognition.** A reader verifies against a key of the SCID it
  was built with, and accepts a foreign credential only with a usable
  answer that says `true`, [REQ-TS-4-02-047][req-ts-4-02-047] and
  [REQ-TS-4-02-048][req-ts-4-02-048].
- **A Rulebook swapped on the CDN.** A reader checks each file against the
  digest the signed list carries, [REQ-TS-4-02-078][req-ts-4-02-078], and
  refuses a Rulebook the list does not name,
  [REQ-TS-4-02-079][req-ts-4-02-079].
- **A catalog that hides a published version.** The list is signed and has
  a lifetime, so an old list stops being usable at the tolerance limit,
  [REQ-TS-4-02-077][req-ts-4-02-077] and [REQ-TS-4-02-097][req-ts-4-02-097].
- **One stolen key reaching every artifact.** The recognition statement key
  and the catalog key each sign one thing, and Trust Registry holds
  neither, [REQ-TS-4-02-044][req-ts-4-02-044],
  [REQ-TS-4-02-046][req-ts-4-02-046], [REQ-TS-4-02-068][req-ts-4-02-068],
  [REQ-TS-4-02-070][req-ts-4-02-070] and
  [REQ-TS-4-02-095][req-ts-4-02-095].
- **A captured Trust Registry having a recognition signed.** Trust Authority
  signs from its own record rather than from what the registry presents,
  [REQ-TS-4-02-082][req-ts-4-02-082], and refuses a request that does not
  match it, [REQ-TS-4-02-083][req-ts-4-02-083].
- **A refusal that shows which check failed.** A refused signing request is
  answered like any other internal failure,
  [REQ-TS-4-02-084][req-ts-4-02-084], without saying that Trust Authority refused,
  [REQ-TS-4-02-093][req-ts-4-02-093], and recorded as an incident,
  [REQ-TS-4-02-085][req-ts-4-02-085].
- **An error read as a decision.** A problem document carries no signature
  and grants or withdraws nothing, [REQ-TS-4-02-058][req-ts-4-02-058] and
  [REQ-TS-4-02-092][req-ts-4-02-092].
- **A problem type URI used to steer a reader.** A reader compares it and
  never fetches it, [REQ-TS-4-02-091][req-ts-4-02-091].
- **A flood of queries.** Trust Registry limits each network address,
  [REQ-TS-4-02-013][req-ts-4-02-013], and a reader that holds a current
  answer asks nothing, [REQ-TS-4-02-011][req-ts-4-02-011].

## Privacy considerations {#ts-4-02-privacy-considerations}

A query tells Trust Registry which entity or which foreign authority a
participant is interested in, and nothing about who the participant is: a
reader sends no identifier, [REQ-TS-4-02-010][req-ts-4-02-010], and Trust
Registry asks for none, [REQ-TS-4-02-008][req-ts-4-02-008]. What the
transport still shows is a network address, and Trust Registry counts
queries per address without recording which query each one sent,
[REQ-TS-4-02-014][req-ts-4-02-014]. Cached answers keep the rest from
becoming a record of transactions, as
[what connects the two planes][what-connects-the-two-planes] sets out.

An answer about a party that has only registered reads the same as one
about a party nobody knows, [REQ-TS-4-02-021][req-ts-4-02-021] and
[REQ-TS-4-02-022][req-ts-4-02-022], so the endpoint discloses no more than
the trusted list already does. The catalog is a set of public files fetched
from cache, and a reader fetches none of them during a transaction,
[REQ-TS-4-02-080][req-ts-4-02-080] and [REQ-TS-4-02-098][req-ts-4-02-098].

## Changelog {#ts-4-02-changelog}

<figure markdown="1" class="ekdn-table">

| Version | Date | Change |
|---|---|---|
| 1.0 draft | 19 October 2026 | First draft |

</figure>
