---
title: "[TS-4-01] Witnessing a log entry and serving its copy"
description: What DID Service checks before it witnesses a log entry, the witness proof it returns to Trust Authority, and the copy of every log it serves from its Resolver endpoint.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §3.1, §3.2, §3.3, §4.6, §5.4, §7.1, §7.7, §9.4; Rincian Module dan Operasi §3; tracks/0240, tracks/0241 -->

<p class="ekdn-docid">TS-4-01</p>

# Witnessing a log entry and serving its copy {#ts-4-01-witnessing-a-log-entry-and-serving-its-copy}

<p class="ekdn-lead" markdown="span">
Decentralized Identifier (DID) Service is the one witness in the ecosystem
and the keeper of a copy of every log it witnessed. This specification fixes what it checks before it
signs, what it returns, and what it serves.
</p>

Every sentence on this page binds DID Service, and an Assessment Body
tests it against them in the version the Governance Profile puts in force.
The key words and the identifier `REQ-TS-4-01-nnn` follow
[Common provisions](common-provisions.md).

## Who runs this and what it needs {#ts-4-01-who-runs-this-and-what-it-needs}

This specification binds the two interfaces of DID Service: the Publisher
endpoint, at which it receives a candidate log entry from Trust Authority
and answers with a witness proof or a refusal, and the Resolver endpoint,
at which it serves its copy of every log it witnessed and resolves
`did:webvh` for the Modules of Trust Infrastructure. Its conformance target
is DID Service.

It leaves to other documents: the profile of the log, the DID Document, and
the rules a reader applies to a log, which
[Publishing and resolving a did:webvh identifier](publishing-and-resolving-a-did-webvh-identifier.md) holds; the door through which an
entity submits an entry to Trust Authority, which [Onboarding an entity and registering its keys](onboarding-an-entity-and-registering-its-keys.md) holds; and which witness keys the trusted list
names, which [Publishing and reading the trusted list](publishing-and-reading-the-trusted-list.md)
holds.

Before the first exchange, DID Service holds what the rules below assume:
the witness key in its own partition of Trust Authority's hardware security
module (HSM), reachable by its Log Service Component alone; a copy of every
log it has witnessed; and the Publisher endpoint in the internal zone, where
Trust Authority is its only caller.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-4-01-001 }**REQ-TS-4-01-001** DID Service MUST meet every requirement in [Witnessing][ts-4-01-witnessing], [The hand-off to the Publisher endpoint][ts-4-01-the-hand-off-to-the-publisher-endpoint] and [The copy DID Service keeps][ts-4-01-the-copy-did-service-keeps].

</div>

## What DID Service does {#ts-4-01-overview}

DID Service witnesses and does not publish. Every entity signs its own log
and serves it on its own domain; DID Service validates each new entry and
adds the witness proof without which no reader accepts it, as
[DID Service][hla-did-service] and [the DID Document][did-document] set
out. It is never on the transaction path: a reader resolves from a cached
copy of each log, and asks DID Service for its copy only when the entity's
domain cannot be reached during the [trust cache sync][trust-cache-sync].
Its five Components, and which of them does what below, are in
[DID Service][sa-did-service].

## The exchange {#ts-4-01-the-exchange}

One candidate entry is witnessed in eight steps, all inside Trust
Infrastructure.

1. Trust Authority hands the candidate entry to the Publisher endpoint,
   with the proof of possession of each new key and the nonce those
   proofs answer.
2. DID Service verifies the candidate as the next entry of the log it
   holds, by every step of the method's Read operation.
3. It verifies each proof of possession.
4. It checks the parameters and the DID Document against the profile.
5. It checks that the update key is not one the Public Key Registry
   records as revoked.
6. It signs the witness proof with the witness key.
7. It stores the entry with its proof.
8. It returns the proof, or a refusal with its reason, in the same
   exchange.

## The witness proof as returned {#ts-4-01-the-witness-proof-as-returned}

Below is the witness proof DID Service returns for one candidate entry, in
the form the entity writes into `did-witness.json`. It is the one message
this specification defines; the log it answers is shown in
[the log as published][ts-5-02-the-log-as-published]. The entity, its
domain and the keys are invented, and no log has been witnessed yet. Every
field is exact: the `versionId` is the one that log's second entry carries,
the proof is a real `eddsa-jcs-2022` signature over it by Trust Authority's
first witness key, and it verifies against the `did:key` the trusted list
names as that witness.

``` { .json title="did-witness.json, the proof DID Service returns" data-format="JSON" }
{
  "versionId": "2-QmNr7vHPCnSA8GVeQpeBZdj1vNheZviyVjRwiJy3gt1zJE",
  "proof": [
    {
      "type": "DataIntegrityProof",
      "cryptosuite": "eddsa-jcs-2022",
      "verificationMethod": "did:key:z6MkrGRs1p2FjsQsxJtKwmaUotzGtjmjcvM7uKcnXU7ffLKe#z6MkrGRs1p2FjsQsxJtKwmaUotzGtjmjcvM7uKcnXU7ffLKe",
      "proofPurpose": "assertionMethod",
      "proofValue": "z5tQ7npYT9Hhe59U4oXarFcq7kYJmP2yR5AdGQT67R6oPgpypgktjZEPX9SPwc89h2XDtMnk6PJuuneNGgUn2wMZL"
    }
  ]
}
```

## Witnessing {#ts-4-01-witnessing}

DID Service is the one witness of every log in the ecosystem, Trust
Authority's own included. It receives each candidate entry at its Publisher
endpoint from Trust Authority, which collected it from the entity through
the door [Onboarding an entity and registering its keys](onboarding-an-entity-and-registering-its-keys.md) fixes, together
with the proof of possession of every new key. What DID Service checks, and
what it returns, is fixed here.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-4-01-002 }**REQ-TS-4-01-002** DID Service MUST accept a candidate entry from Trust Authority only.
- [](){ #req-ts-4-01-003 }**REQ-TS-4-01-003** DID Service MUST NOT expose the interface that receives a candidate entry outside Trust Infrastructure.
- [](){ #req-ts-4-01-004 }**REQ-TS-4-01-004** Before witnessing any entry after the first, DID Service MUST hold the published log of the DID.
- [](){ #req-ts-4-01-005 }**REQ-TS-4-01-005** DID Service MUST verify the candidate as the next entry of that log by every step of the method's Read operation.
- [](){ #req-ts-4-01-006 }**REQ-TS-4-01-006** DID Service MUST verify the proof of possession of every key the candidate publishes for the first time, as a signature by that key over the nonce Trust Authority supplied.
- [](){ #req-ts-4-01-007 }**REQ-TS-4-01-007** DID Service MUST refuse a candidate whose `parameters` differ from [the table of parameters][tbl-ts-5-02-parameters] or whose `state` differs from [The DID Document][ts-5-02-the-did-document].
- [](){ #req-ts-4-01-008 }**REQ-TS-4-01-008** DID Service MUST refuse a candidate whose proof was made with an update key that Trust Authority's Public Key Registry records as revoked.
- [](){ #req-ts-4-01-009 }**REQ-TS-4-01-009** A witness proof MUST be a Data Integrity proof with cryptosuite [`eddsa-jcs-2022`][ref-vc-di-eddsa] and `proofPurpose` `assertionMethod`, made with the witness key over the candidate's `versionId` as the method defines, with `verificationMethod` the witness key's `did:key` followed by `#` and the same key.
- [](){ #req-ts-4-01-010 }**REQ-TS-4-01-010** DID Service MUST sign the witness proof with the witness key held in Trust Authority's HSM.
- [](){ #req-ts-4-01-011 }**REQ-TS-4-01-011** DID Service MUST NOT hold the witness key anywhere but in that HSM.
- [](){ #req-ts-4-01-012 }**REQ-TS-4-01-012** DID Service MUST return the witness proof, or the refusal with its reason, to Trust Authority in the same exchange.
- [](){ #req-ts-4-01-013 }**REQ-TS-4-01-013** DID Service MUST NOT queue a candidate for a later answer.
- [](){ #req-ts-4-01-014 }**REQ-TS-4-01-014** DID Service MUST be available for the share of time, over the rolling window, that the Governance Profile sets.
- [](){ #req-ts-4-01-015 }**REQ-TS-4-01-015** After an outage, DID Service MUST be back within the recovery time the Governance Profile sets.
- [](){ #req-ts-4-01-016 }**REQ-TS-4-01-016** DID Service MUST store every entry it witnessed, with its witness proof, before returning the proof.

</div>

The proof of possession reaches DID Service through Trust Authority because
an entity never submits an entry to DID Service, as
[who may call whom][who-may-call-whom] fixes, and the second phase of
[entity key revocation][entity-key-revocation] is this same exchange run the
same day. The two availability numbers are the witness target in
[quality targets][quality-targets]; what waits when the witness is down is
the replacement key, and nothing else.

## The hand-off to the Publisher endpoint {#ts-4-01-the-hand-off-to-the-publisher-endpoint}

The hand-off is one request and one answer on one connection inside Trust
Infrastructure. Trust Authority sends the candidate entry, the proofs of
possession it collected from the entity, and the nonce those proofs answer.
DID Service runs the checks above and answers on the same connection, with
the witness proof or with the reason it refused. Nothing is called back and
nothing is polled, because the entity waits at Trust Authority's door for
that answer.

A refusal names one reason from a closed list, one reason per check, so
that Trust Authority can tell the entity what to correct and an Assessment
Body can test each check on its own.
[The table of refusal reasons][tbl-ts-4-01-refusal-reasons] gives each
reason with the status it is answered with. A request that is not a
candidate, and a candidate DID Service could not judge, are answered by
status alone, with no body, as the Resolver answers a copy it does not hold.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-4-01-023 }**REQ-TS-4-01-023** DID Service MUST receive a candidate entry at `POST <endpoint>/entries` on its Publisher endpoint, with a request body of media type `application/json`.
- [](){ #req-ts-4-01-024 }**REQ-TS-4-01-024** DID Service MUST read the candidate entry from the request body's `logEntry`, the proofs of possession from its `proofOfPossession`, and the nonce those proofs answer from its `nonce`.
- [](){ #req-ts-4-01-025 }**REQ-TS-4-01-025** DID Service MUST accept a request only over a mutually authenticated Transport Layer Security (TLS) connection on which Trust Authority presented its client certificate.
- [](){ #req-ts-4-01-035 }**REQ-TS-4-01-035** DID Service MUST end the TLS handshake, and send no HTTP answer, when the client presents no certificate or one that does not authenticate Trust Authority.
- [](){ #req-ts-4-01-026 }**REQ-TS-4-01-026** DID Service MUST answer a candidate it witnessed with `200`, media type `application/json`, and the witness proof in the form [The witness proof as returned][ts-4-01-the-witness-proof-as-returned] shows.
- [](){ #req-ts-4-01-027 }**REQ-TS-4-01-027** DID Service MUST answer a candidate it refuses with the status and the `reason` that [the table of refusal reasons][tbl-ts-4-01-refusal-reasons] gives for the check that failed.
- [](){ #req-ts-4-01-028 }**REQ-TS-4-01-028** DID Service MUST NOT answer with a `reason` that table does not hold.
- [](){ #req-ts-4-01-029 }**REQ-TS-4-01-029** DID Service MUST answer `503` when it cannot reach the witness key.
- [](){ #req-ts-4-01-030 }**REQ-TS-4-01-030** DID Service MUST NOT treat a candidate it answered with `503` as refused.
- [](){ #req-ts-4-01-037 }**REQ-TS-4-01-037** DID Service MUST send no body with a `503`.
- [](){ #req-ts-4-01-031 }**REQ-TS-4-01-031** DID Service MUST NOT serve any operation other than `POST <endpoint>/entries` at its Publisher endpoint.
- [](){ #req-ts-4-01-036 }**REQ-TS-4-01-036** DID Service MUST answer a request for any other operation with `404` and no body.
- [](){ #req-ts-4-01-032 }**REQ-TS-4-01-032** Each item of `proofOfPossession` MUST be a JSON Web Signature (JWS) in the compact serialization of [RFC 7515][ref-rfc7515] whose protected header carries `typ` `vnd.id.idctf.key-pop+jwt`, `alg` the algorithm of the key proving possession, and `kid` that key's identifier in the DID Document the candidate publishes, or, where the key is the update key, `did:key:<multikey>#<multikey>`.
- [](){ #req-ts-4-01-033 }**REQ-TS-4-01-033** The payload of each proof of possession MUST carry `aud`, Trust Authority's identifier, `nonce`, the value the request carries in `nonce`, and `iat`, the time the proof was made.
- [](){ #req-ts-4-01-034 }**REQ-TS-4-01-034** DID Service MUST refuse a candidate with `proof-of-possession-invalid` when a proof of possession carries a `nonce` other than the one the request carries.

</div>

A reason is a code and carries no detail of its own: what the entity has to
correct follows from the check that raised it, and Trust Authority holds
the exchange with the entity.

[](){ #tbl-ts-4-01-refusal-reasons }

<figure markdown="1" class="ekdn-table">

| Reason | Status | Raised when | Check |
|---|---|---|---|
| `malformed-request` | `400` | the body is not JSON, or one of its three members is absent | [REQ-TS-4-01-024][req-ts-4-01-024] |
| `log-unknown` | `422` | the candidate follows an earlier entry and DID Service holds no published log of that DID | [REQ-TS-4-01-004][req-ts-4-01-004] |
| `not-next-entry` | `422` | the candidate fails a step of the method's Read operation against the log DID Service holds | [REQ-TS-4-01-005][req-ts-4-01-005] |
| `proof-of-possession-invalid` | `422` | a key the candidate publishes for the first time carries no valid signature over the nonce | [REQ-TS-4-01-006][req-ts-4-01-006] |
| `parameters-rejected` | `422` | `parameters` differ from the profile | [REQ-TS-4-01-007][req-ts-4-01-007] |
| `did-document-rejected` | `422` | `state` differs from the profile | [REQ-TS-4-01-007][req-ts-4-01-007] |
| `update-key-revoked` | `422` | the Public Key Registry records the update key as revoked | [REQ-TS-4-01-008][req-ts-4-01-008] |

</figure>

The request Trust Authority sends. Its body carries the entry
[the log as published][ts-5-02-the-log-as-published] shows as the second
line of that log, one proof of possession for each key that entry publishes
for the first time, and the nonce those proofs answer. The entry publishes
two such keys, its new update key and `issuance-jose-2`, so the body carries
two proofs, and each names in `kid` the key it proves: the identifier the
DID Document gives the issuance key, and the `did:key` form for the update
key, which the DID Document does not carry.

``` { .http title="POST /entries, DID Service Publisher endpoint" data-format="HTTP" }
POST /entries HTTP/1.1
Host: did-publisher.trust.internal
Content-Type: application/json

{
  "logEntry": {
    "versionId": "2-QmNr7vHPCnSA8GVeQpeBZdj1vNheZviyVjRwiJy3gt1zJE",
    "versionTime": "2026-09-15T09:00:00Z",
    "parameters": {
      "updateKeys": [
        "z6MkgneGrxeNdi2mi6swidp38iqtkk6r2iaEgf25Kufb7rRL"
      ],
      "nextKeyHashes": [
        "QmXVqEyGwzQHfLQ1SG4MCKA5GHNvuJRDV22XX5CCQrsjcw"
      ],
      "witness": {
        "threshold": 1,
        "witnesses": [
          {
            "id": "did:key:z6MkrGRs1p2FjsQsxJtKwmaUotzGtjmjcvM7uKcnXU7ffLKe"
          },
          {
            "id": "did:key:z6MktqjEVK1P1HgMSJYGpPYjuLjEa13u26WEhf7dvCWPYZj1"
          }
        ]
      }
    },
    "state": {
      "@context": [
        "https://www.w3.org/ns/did/v1",
        "https://w3id.org/security/multikey/v1"
      ],
      "id": "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id",
      "verificationMethod": [
        {
          "id": "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id#issuance-jose-1",
          "type": "Multikey",
          "controller": "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id",
          "publicKeyMultibase": "zDnaeWSwJDrKLraHe5w4vA39xFW2TnZaDDNEGGWSyHYSC9Nfp"
        },
        {
          "id": "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id#status-list-1",
          "type": "Multikey",
          "controller": "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id",
          "publicKeyMultibase": "zDnaeamPEKdV4VYmsDaPr9f3LyENGRFTwHRpoNvRLyi2gznvD"
        },
        {
          "id": "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id#issuance-jose-2",
          "type": "Multikey",
          "controller": "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id",
          "publicKeyMultibase": "zDnaegmvjP5yMynYdQDsDyRAtCKHooT7PuhqVaxN7RSAgBZ6E"
        }
      ],
      "assertionMethod": [
        "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id#issuance-jose-2",
        "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id#status-list-1"
      ]
    },
    "proof": [
      {
        "type": "DataIntegrityProof",
        "cryptosuite": "eddsa-jcs-2022",
        "verificationMethod": "did:key:z6MkgneGrxeNdi2mi6swidp38iqtkk6r2iaEgf25Kufb7rRL#z6MkgneGrxeNdi2mi6swidp38iqtkk6r2iaEgf25Kufb7rRL",
        "proofPurpose": "assertionMethod",
        "proofValue": "z2mudE1JVEhZQgxeN5duy1PmeChmo9r9mRzZrpEcPVWJA9Jp6nZ92PC3t8SfeMGscGCMfdDhwPg13F9CyWwJZyALV"
      }
    ]
  },
  "proofOfPossession": [
    "eyJ0eXAiOiJ2bmQuaWQuaWRjdGYua2V5LXBvcCtqd3QiLCJhbGciOiJFZERTQSIsImtpZCI6ImRpZDprZXk6ejZNa2duZUdyeGVOZGkybWk2c3dpZHAzOGlxdGtrNnIyaWFFZ2YyNUt1ZmI3clJMI3o2TWtnbmVHcnhlTmRpMm1pNnN3aWRwMzhpcXRrazZyMmlhRWdmMjVLdWZiN3JSTCJ9.eyJhdWQiOiJkaWQ6d2Vidmg6UW1aankxdDlvRmlhRmpoWDJlMzh1TXVSN21ndGRMakhQTUdmakVmdnJzbWFpcTp0cnVzdC5nby5pZCIsIm5vbmNlIjoiZ3BrRi0zaW1MOVRfLVVNZlRDbzVwZmE2elJOUXUxc0oiLCJpYXQiOjE3ODk0NjI4NjB9.3uebBOGVvFHJJkmtpWna4anvkba5h5aTzJI3cCTml4oUwWcuNOxlc0YIABiZZGX1pmQCCql8T29YWaidek1YDQ",
    "eyJ0eXAiOiJ2bmQuaWQuaWRjdGYua2V5LXBvcCtqd3QiLCJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDp3ZWJ2aDpRbWNFVlQyaUpTcnNzNWhnd2lNRnNNVXhLa1JvemdGRjQ1OFJjZ2dUNE1GMkw0OmR1a2NhcGlsLmdvLmlkI2lzc3VhbmNlLWpvc2UtMiJ9.eyJhdWQiOiJkaWQ6d2Vidmg6UW1aankxdDlvRmlhRmpoWDJlMzh1TXVSN21ndGRMakhQTUdmakVmdnJzbWFpcTp0cnVzdC5nby5pZCIsIm5vbmNlIjoiZ3BrRi0zaW1MOVRfLVVNZlRDbzVwZmE2elJOUXUxc0oiLCJpYXQiOjE3ODk0NjI4NjB9.thmJEqH3TC590LFjLitxDakM-cOly1GnPv13lMBdqWZ4czY1VATjx57hHZVqamGjSRwflUcg8GJH69EXXtBRtg"
  ],
  "nonce": "gpkF-3imL9T_-UMfTCo5pfa6zRNQu1sJ"
}
```

The host is the Publisher endpoint's address inside Trust Infrastructure,
which the Root Authority's deployment sets and no document publishes,
because nothing outside Trust Infrastructure resolves it. A refusal of that
same candidate, had the Public Key Registry recorded its update key as
revoked:

``` { .http title="422, the answer to a candidate DID Service refuses" data-format="HTTP" }
HTTP/1.1 422 Unprocessable Content
Content-Type: application/json

{"reason": "update-key-revoked"}
```

## The copy DID Service keeps {#ts-4-01-the-copy-did-service-keeps}

DID Service keeps a copy of every log it witnessed and serves it from its
Resolver endpoint, which is a watcher in the method's sense: the entity
names it in `watchers`, and a reader that cannot reach the entity's domain
asks it for the log. It is a copy and nothing more; a reader verifies it
exactly as it verifies the original, and the copy adds no trust in DID
Service. The same endpoint resolves `did:webvh` for the Modules of Trust
Infrastructure, which carry no Trust SDK, as
[DID Service][hla-did-service] sets out.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-4-01-017 }**REQ-TS-4-01-017** DID Service MUST keep every log it witnessed as the sequence of entries it witnessed, each with its witness proof.
- [](){ #req-ts-4-01-018 }**REQ-TS-4-01-018** DID Service MUST watch that each log it witnessed stays available on its entity's domain.
- [](){ #req-ts-4-01-019 }**REQ-TS-4-01-019** DID Service MUST serve, at its Resolver endpoint, `GET <endpoint>/log?scid=<scid>` and `GET <endpoint>/witness?scid=<scid>` as the watcher interface of [did:webvh v1.0][ref-did-webvh] defines them, returning its copy of the log and of the witness file for that self-certifying identifier (SCID).
- [](){ #req-ts-4-01-020 }**REQ-TS-4-01-020** DID Service MUST serve the Resolver endpoint publicly, without authentication and without any identifier of the reader.
- [](){ #req-ts-4-01-021 }**REQ-TS-4-01-021** DID Service MUST NOT expose the method's watcher notification and deletion operations.
- [](){ #req-ts-4-01-022 }**REQ-TS-4-01-022** DID Service MUST record a log that has become unavailable as a finding for Trust Authority to read, because DID Service calls no Module.

</div>

The notification operations are not used because no entity submits
anything to DID Service: it learns of a new entry by witnessing it. Its Log
Delivery Component watches that the log stays available, as
[DID Service][sa-did-service] sets out, and an entry that appears on a
domain without having been witnessed is what Trust Registry's conformance
crawler catches, as [why nobody can rotate quietly][why-nobody-can-rotate-quietly]
sets out.

The two operations of the Resolver endpoint, as a reader calls them during
the sync, and what each returns:

``` { .http title="GET /log, DID Service Resolver endpoint" data-format="HTTP" }
GET /log?scid=QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4 HTTP/1.1
Host: did.trust.go.id
```

returns the copy of `did.jsonl` for that SCID, as `text/jsonl`, the file
shown in [the log as published][ts-5-02-the-log-as-published]; and

``` { .http title="GET /witness, DID Service Resolver endpoint" data-format="HTTP" }
GET /witness?scid=QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4 HTTP/1.1
Host: did.trust.go.id
```

returns the copy of `did-witness.json`, as `application/json`. A SCID DID
Service never witnessed answers `404`. The host is DID Service's Resolver
endpoint, the address each entity writes in `watchers`; the one shown is an
illustration, and the Governance Profile publishes the address in force.

## Security considerations {#ts-4-01-security-considerations}

Each threat below is answered by the requirement named with it.

- **A rewritten history.** DID Service holds the published log before it
  witnesses the next entry and verifies the candidate against it,
  [REQ-TS-4-01-004][req-ts-4-01-004] and [REQ-TS-4-01-005][req-ts-4-01-005],
  so an entry that does not chain to what was published is refused, and
  the copy it keeps, [REQ-TS-4-01-017][req-ts-4-01-017], is what a dispute
  is settled against.
- **A compromised update key.** A candidate signed with a key the Public
  Key Registry records as revoked is refused, [REQ-TS-4-01-008][req-ts-4-01-008].
- **A witness key used elsewhere.** The key never leaves Trust Authority's
  HSM, [REQ-TS-4-01-011][req-ts-4-01-011].
- **An entry submitted around Trust Authority.** The Publisher endpoint
  accepts candidates from Trust Authority only and is not exposed outside
  Trust Infrastructure, [REQ-TS-4-01-002][req-ts-4-01-002] and
  [REQ-TS-4-01-003][req-ts-4-01-003], and it answers no request that
  Trust Authority's client certificate did not authenticate, and it ends the
  handshake with a client that cannot be authenticated as Trust Authority,
  [REQ-TS-4-01-025][req-ts-4-01-025] and [REQ-TS-4-01-035][req-ts-4-01-035].
- **A log that disappears.** Log Delivery watches each domain and records a
  log that has become unavailable, [REQ-TS-4-01-018][req-ts-4-01-018] and [REQ-TS-4-01-022][req-ts-4-01-022].

## Privacy considerations {#ts-4-01-privacy-considerations}

DID Service holds public keys and nothing about any citizen. Its Resolver
endpoint is asked only during the trust cache sync, and only when an
entity's domain cannot be reached, so DID Service learns nothing about
which citizen deals with which entity, and it serves the copy without
authentication and without any identifier of the reader,
[REQ-TS-4-01-020][req-ts-4-01-020].

## Changelog {#ts-4-01-changelog}

<figure markdown="1" class="ekdn-table">

| Version | Date | Change |
|---|---|---|
| 1.0 draft | 19 October 2026 | First draft |

</figure>
