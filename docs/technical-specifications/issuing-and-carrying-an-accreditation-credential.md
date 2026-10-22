---
title: "[TS-5-07] Issuing and carrying an Accreditation Credential"
description: The Accreditation Credential Trust Authority issues to an accredited entity, what it names, the signature on it, how long it lives, the status list that revokes it early, and what a party shown one may conclude from it.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §2.4, §4.6, §5.7; Bentuk Data Attestation §4; Rincian Module dan Operasi §1.2, §8 -->

<p class="ekdn-docid">TS-5-07</p>

# Issuing and carrying an Accreditation Credential {#ts-5-07-issuing-and-carrying-an-accreditation-credential}

<p class="ekdn-lead" markdown="span">
An Accreditation Credential is the evidence an accredited entity holds about
itself. It lives as long as the accreditation, so a status list ends it early.
</p>

Every sentence on this page binds Trust Authority, which issues and signs the
credential, and Trust Registry, which publishes the status list it points into,
and an Assessment Body tests them against it in the version the
Governance Profile puts in force. The key words and the identifier
`REQ-TS-5-07-nnn` follow [Common provisions](common-provisions.md).

## Who runs this and what it needs {#ts-5-07-who-runs-this-and-what-it-needs}

This specification fixes the Accreditation Credential:

- The claims it carries.
- What each of them names.
- The signature Trust Authority puts on it.
- How long it lives.
- The status reference that revokes it before it expires.
- What a party that is shown one may conclude from it.

Its conformance targets are Trust Authority, which records the accreditation,
builds the credential, and signs it; and Trust Registry, which publishes the
status list that revokes one and the trusted list entry that answers the same
question for everybody else. No Module of the ecosystem reads an
Accreditation Credential: the entity it was issued to is its only reader inside
the ecosystem. [Reading it][ts-5-07-reading-it] binds a party outside the
ecosystem that is shown one and chooses to act on it, and no conformance target
is tested against that clause.

It leaves to other documents:

- Who is accredited, on what grounds,
  [how the assessment is run][gf-conformance-testing], and
  [the sanctions behind a suspension or a withdrawal][gf-ladder-of-sanctions],
  which the Governance Framework holds.
- The length of an accreditation period, the lead time for a renewal, and the
  rotation interval of the signing key, which the Governance Profile holds.
- The exchange the credential is delivered in and the place an entity
  collects a later copy from, which
  [Onboarding an entity and registering its keys](onboarding-an-entity-and-registering-its-keys.md)
  holds.
- The format, the signature, and the publication of the status list the
  credential points into, which
  [Publishing and reading a status list](publishing-and-reading-a-status-list.md)
  holds.
- The entry that decides whether a party takes part, which
  [Publishing and reading the trusted list](publishing-and-reading-the-trusted-list.md)
  holds.
- The keys of Trust Authority, their rotation, and the log they live in, which
  [Publishing and resolving a did:webvh identifier](publishing-and-resolving-a-did-webvh-identifier.md)
  holds.
- What an entity may do, which is answered by query and never read
  from this credential, and which
  [Answering with an Authority Statement](answering-with-an-authority-statement.md)
  holds.

Before the first issuance, each target holds what the rules below assume:

- **Trust Authority** holds the Root Authority's accreditation decisions with
  their history, holds the Accreditation Credential key in its hardware
  security module (HSM), and publishes the matching public key in its own
  Decentralized Identifier (DID) Document.
- **Trust Registry** holds the trusted list and the accreditation status list,
  and reaches the key that signs the list through Trust Authority; it holds no
  private key of its own.
- **The entity** holds a `did:webvh` of its own, published and witnessed, which
  is the identifier the credential names as its subject.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-07-001 }**REQ-TS-5-07-001** Trust Authority MUST meet every requirement on this page that names Trust Authority, and every requirement on what Trust Authority writes: the Accreditation Credential, with its header, its claims, and its signature.
- [](){ #req-ts-5-07-002 }**REQ-TS-5-07-002** Trust Registry MUST meet every requirement on this page that names Trust Registry.
- [](){ #req-ts-5-07-003 }**REQ-TS-5-07-003** A party that acts on an Accreditation Credential MUST meet every requirement that names a reader, wherever it stands on this page.

</div>

## What the credential is for {#ts-5-07-what-the-credential-is-for}

An Accreditation Credential is one statement by Trust Authority that one
registration was accredited. The entity carries it and shows it where it
chooses; no issuance, presentation, or permission check depends on one being
produced.

What everybody else checks is the trusted list. A party absent from that list
is refused however valid the credential it shows, and a party present in it is
accepted without one, as
[Publishing and reading the trusted list](publishing-and-reading-the-trusted-list.md)
sets out.

Four roles reach accreditation: Identity Issuer, Attribute Issuer,
Wallet Provider, and Relying Party, as
[Three stages of authority](../architecture-framework/roles/three-stages-of-authority.md)
sets out. An RP Intermediary is a Relying Party that registers merchants and
holds the standing to issue Verifier Device Certificates, rather than a fifth
role, and it holds one credential like any other. A merchant is registered by
its RP Intermediary and never accredited, so it holds none. An Assessment Body
is recognized rather than accredited, so it holds none either.

One registration, one credential. A legal body that registers twice is two
entities and holds one credential for each.

## Accreditation Credentials as issued {#ts-5-07-accreditation-credentials-as-issued}

The three credentials below are an illustration: the entities, the domains, and
the keys are invented, and no registration has been accredited. Every field is
exact. Each was signed with the Accreditation Credential key of the
Trust Authority DID its `iss` names, and each signature verifies, so an
implementation can parse these credentials and find what the clauses below
require.

The entities are the ones [the trusted list][ts-5-01-trusted-list-payload]
carries, with the same DIDs. Each `iat` is the moment Trust Authority issued
the copy.

``` { .text title="The credential of an accredited Identity Issuer" data-format="SD-JWT" }
eyJ0eXAiOiJkYytzZC1qd3QiLCJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDp3ZWJ2aDpRbVpqeTF0OW9GaWFGamhYMmUzOHVNdVI3bWd0ZExqSFBNR2ZqRWZ2cnNtYWlxOnRydXN0LmdvLmlkI2FjY3JlZGl0YXRpb24tY3JlZGVudGlhbC0xIn0.eyJpc3MiOiJkaWQ6d2Vidmg6UW1aankxdDlvRmlhRmpoWDJlMzh1TXVSN21ndGRMakhQTUdmakVmdnJzbWFpcTp0cnVzdC5nby5pZCIsInZjdCI6ImlkLmlkY3RmLmFjY3JlZGl0YXRpb24uMSIsInN1YiI6ImRpZDp3ZWJ2aDpRbWNFVlQyaUpTcnNzNWhnd2lNRnNNVXhLa1JvemdGRjQ1OFJjZ2dUNE1GMkw0OmR1a2NhcGlsLmdvLmlkIiwiZW50aXR5X25hbWUiOiJEaXJla3RvcmF0IEplbmRlcmFsIEtlcGVuZHVkdWthbiBkYW4gUGVuY2F0YXRhbiBTaXBpbCIsImVudGl0eV90eXBlIjpbImh0dHBzOi8vaWRjdGYuaWQvbnMvMTk2MDIvU3ZjVHlwZS9JZGVudGl0eUlzc3VlciJdLCJzY29wZSI6W3siYWN0aW9uIjoiaXNzdWUiLCJyZXNvdXJjZSI6ImlkLmlkY3RmLmt0cC4xIn1dLCJzdGF0dXMiOnsic3RhdHVzX2xpc3QiOnsiaWR4IjoxNywidXJpIjoiaHR0cHM6Ly9yZWdpc3RyeS50cnVzdC5nby5pZC9zdGF0dXMvYWNjcmVkaXRhdGlvbnMtMSJ9fSwiaWF0IjoxNzY5OTA0MDAwLCJleHAiOjE4MzI5NzYwMDB9.kQVtLszmfPhVBfSdumMGFHCV7GB9y1QWmaScMCn_f8tHbHW6kjTw5qmR4B9A2DZBmNtlQxtH3W1j3eRSS_f3vA~
```

``` { .text title="The credential of an accredited Relying Party" data-format="SD-JWT" }
eyJ0eXAiOiJkYytzZC1qd3QiLCJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDp3ZWJ2aDpRbVpqeTF0OW9GaWFGamhYMmUzOHVNdVI3bWd0ZExqSFBNR2ZqRWZ2cnNtYWlxOnRydXN0LmdvLmlkI2FjY3JlZGl0YXRpb24tY3JlZGVudGlhbC0xIn0.eyJpc3MiOiJkaWQ6d2Vidmg6UW1aankxdDlvRmlhRmpoWDJlMzh1TXVSN21ndGRMakhQTUdmakVmdnJzbWFpcTp0cnVzdC5nby5pZCIsInZjdCI6ImlkLmlkY3RmLmFjY3JlZGl0YXRpb24uMSIsInN1YiI6ImRpZDp3ZWJ2aDpRbVVBVEM1anlmNXlWeTcyR1lBcDhuU3Z1d3NoekR5NndZWDdXbU5ZNVVKdFhUOnRlcm1pbmFsLW51c2FudGFyYS5jby5pZCIsImVudGl0eV9uYW1lIjoiUFQgVGVybWluYWwgTnVzYW50YXJhIiwiZW50aXR5X3R5cGUiOlsiaHR0cHM6Ly9pZGN0Zi5pZC9ucy8xOTYwMi9TdmNUeXBlL1JlbHlpbmdQYXJ0eSJdLCJzY29wZSI6W3siYWN0aW9uIjoicmVxdWVzdCIsInJlc291cmNlIjoiaWQuaWRjdGYua3RwLjEjdXNpYV9kaV9hdGFzXzE3In0seyJhY3Rpb24iOiJyZXF1ZXN0IiwicmVzb3VyY2UiOiJpZC5pZGN0Zi5rdHAuMSNuaWsifSx7ImFjdGlvbiI6InJlcXVlc3QiLCJyZXNvdXJjZSI6ImlkLmlkY3RmLmt0cC4xI25hbWEifSx7ImFjdGlvbiI6InJlcXVlc3QiLCJyZXNvdXJjZSI6Im9yZy5pc28uMTgwMTMuNS4xLm1ETC4xI2FnZV9vdmVyXzE4In0seyJhY3Rpb24iOiJyZXF1ZXN0IiwicmVzb3VyY2UiOiJpZC5pZGN0Zi5rYXJ0dS1hc24uMSNuYW1hIn0seyJhY3Rpb24iOiJyZXF1ZXN0IiwicmVzb3VyY2UiOiJpZC5pZGN0Zi5rYXJ0dS1hc24uMSNuaXAifSx7ImFjdGlvbiI6InJlcXVlc3QiLCJyZXNvdXJjZSI6ImlkLmlkY3RmLmthcnR1LWFzbi4xI2luc3RhbnNpIn0seyJhY3Rpb24iOiJyZXF1ZXN0IiwicmVzb3VyY2UiOiJpZC5pZGN0Zi5rYXJ0dS1uaWthaC4xIn1dLCJzdGF0dXMiOnsic3RhdHVzX2xpc3QiOnsiaWR4Ijo0MiwidXJpIjoiaHR0cHM6Ly9yZWdpc3RyeS50cnVzdC5nby5pZC9zdGF0dXMvYWNjcmVkaXRhdGlvbnMtMSJ9fSwiaWF0IjoxNzcyMzIzMjAwLCJleHAiOjE4MzU0ODE2MDB9.sdpnogfa3nrtyLsouRrAwbGvNGyOgfVg8dm4b0PcZ0qsESwLWADLtDgjL8V7J9E72ZoqRrZBzusN3hym1TEJCQ~
```

``` { .text title="The credential of an accredited Wallet Provider, which holds no permission" data-format="SD-JWT" }
eyJ0eXAiOiJkYytzZC1qd3QiLCJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDp3ZWJ2aDpRbVpqeTF0OW9GaWFGamhYMmUzOHVNdVI3bWd0ZExqSFBNR2ZqRWZ2cnNtYWlxOnRydXN0LmdvLmlkI2FjY3JlZGl0YXRpb24tY3JlZGVudGlhbC0xIn0.eyJpc3MiOiJkaWQ6d2Vidmg6UW1aankxdDlvRmlhRmpoWDJlMzh1TXVSN21ndGRMakhQTUdmakVmdnJzbWFpcTp0cnVzdC5nby5pZCIsInZjdCI6ImlkLmlkY3RmLmFjY3JlZGl0YXRpb24uMSIsInN1YiI6ImRpZDp3ZWJ2aDpRbWVUVzEzNHFqVUM2RUtYVTZKTDNkVlJnZDNmWW1VcE1ib29FRG9rU3BGRUFIOmRvbXBldC5jby5pZCIsImVudGl0eV9uYW1lIjoiUFQgRG9tcGV0IERpZ2l0YWwgTnVzYW50YXJhIiwiZW50aXR5X3R5cGUiOlsiaHR0cHM6Ly9pZGN0Zi5pZC9ucy8xOTYwMi9TdmNUeXBlL1dhbGxldFByb3ZpZGVyIl0sInNjb3BlIjpbXSwic3RhdHVzIjp7InN0YXR1c19saXN0Ijp7ImlkeCI6OCwidXJpIjoiaHR0cHM6Ly9yZWdpc3RyeS50cnVzdC5nby5pZC9zdGF0dXMvYWNjcmVkaXRhdGlvbnMtMSJ9fSwiaWF0IjoxNzcyMzIzMjAwLCJleHAiOjE4MzU0ODE2MDB9.oknVsYWOjio6Kg1SOJRFx9jUdyGfNQl5OD8AEp7thUPGTrFdZV3QjzKJRQxi3Y_fAw5nUdBonmK6h_ysB6HHZg~
```

Each is an SD-JWT-based Verifiable Credential (SD-JWT VC) draft -13 issued with no
disclosure, so the serialization is one
JSON Web Signature followed by the `~` that closes an empty disclosure list.
Nothing is withheld, because nothing presents the credential selectively.

The claims of the first of them, decoded:

``` { .json title="The claims of the Identity Issuer's credential" data-format="JSON" }
{
  "iss": "did:webvh:QmZjy1t9oFiaFjhX2e38uMuR7mgtdLjHPMGfjEfvrsmaiq:trust.go.id",
  "vct": "id.idctf.accreditation.1",
  "sub": "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id",
  "entity_name": "Direktorat Jenderal Kependudukan dan Pencatatan Sipil",
  "entity_type": [
    "https://idctf.id/ns/19602/SvcType/IdentityIssuer"
  ],
  "scope": [
    {
      "action": "issue",
      "resource": "id.idctf.ktp.1"
    }
  ],
  "status": {
    "status_list": {
      "idx": 17,
      "uri": "https://registry.trust.go.id/status/accreditations-1"
    }
  },
  "iat": 1769904000,
  "exp": 1832976000
}
```

## Format {#ts-5-07-format}

The credential is an SD-JWT VC over SD-JWT, with the issuer-signed part a
JSON Web Signature in compact serialization and a claims set:
[IETF SD-JWT VC][ref-i-d-ietf-oauth-sd-jwt-vc] defines the credential,
[RFC 9901][ref-rfc9901] the SD-JWT under it, [RFC 7515][ref-rfc7515] the
compact serialization, and [RFC 7519][ref-rfc7519] the claims set. The header
carries three parameters and nothing else: `typ`, `alg`, and `kid`.

[](){ #tbl-ts-5-07-claims }

<figure markdown="1" class="ekdn-table">

| Claim | Type | Presence | What it carries |
|---|---|---|---|
| `iss` | string | Present | The `did:webvh` of Trust Authority, which signed the credential |
| `vct` | string | Present | `id.idctf.accreditation.1`, the type of the credential |
| `sub` | string | Present | The `did:webvh` of the accredited registration |
| `entity_name` | string | Present | The legal name of the body behind the registration, as its trusted list entry carries it |
| `entity_type` | array of strings | Present | The role service type identifiers the registration was accredited for |
| `scope` | array of objects | Present | The permissions the registration held when the credential was issued, each an `action` on a `resource` |
| `status` | object | Present | The reference into the accreditation status list |
| `iat` | number | Present | The moment Trust Authority issued this copy of the credential |
| `exp` | number | Present | The moment the accreditation period ends |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-07-004 }**REQ-TS-5-07-004** An Accreditation Credential MUST be an SD-JWT VC whose issuer-signed part is a JSON Web Signature in compact serialization.
- [](){ #req-ts-5-07-005 }**REQ-TS-5-07-005** The `typ` header parameter MUST be `dc+sd-jwt`.
- [](){ #req-ts-5-07-006 }**REQ-TS-5-07-006** The `alg` header parameter MUST be one the Governance Profile allows for the Accreditation Credential key.
- [](){ #req-ts-5-07-007 }**REQ-TS-5-07-007** *Withdrawn: [REQ-TS-01-033][req-ts-01-033] covers it.*
- [](){ #req-ts-5-07-008 }**REQ-TS-5-07-008** The `kid` header parameter MUST name a key of the purpose `accreditation-credential`, as [Naming the key][ts-01-naming-the-key] of TS-01 requires.
- [](){ #req-ts-5-07-009 }**REQ-TS-5-07-009** The header MUST NOT carry a parameter other than `typ`, `alg`, and `kid`.
- [](){ #req-ts-5-07-010 }**REQ-TS-5-07-010** Trust Authority MUST include every claim [the table of claims][tbl-ts-5-07-claims] lists.
- [](){ #req-ts-5-07-011 }**REQ-TS-5-07-011** Trust Authority MUST NOT include a claim [the table of claims][tbl-ts-5-07-claims] does not list.
- [](){ #req-ts-5-07-012 }**REQ-TS-5-07-012** `iss` MUST be the `did:webvh` of Trust Authority.
- [](){ #req-ts-5-07-013 }**REQ-TS-5-07-013** `vct` MUST be `id.idctf.accreditation.1`.
- [](){ #req-ts-5-07-014 }**REQ-TS-5-07-014** A reader MUST take the claims of `id.idctf.accreditation.1` from this specification, because no Credential Rulebook governs that type.
- [](){ #req-ts-5-07-015 }**REQ-TS-5-07-015** Trust Authority MUST NOT issue a credential of this type to a party that is not an accredited registration.
- [](){ #req-ts-5-07-016 }**REQ-TS-5-07-016** Trust Authority MUST issue the credential with no selective disclosure, so that it carries no `_sd` array, no `_sd_alg` claim, and no disclosure after the tilde.
- [](){ #req-ts-5-07-017 }**REQ-TS-5-07-017** Trust Authority MUST NOT include a `cnf` claim, because no protocol presents the credential and no party authenticates its holder.
- [](){ #req-ts-5-07-018 }**REQ-TS-5-07-018** A reader MUST refuse a credential whose `typ` is not `dc+sd-jwt`, whose `vct` is not `id.idctf.accreditation.1`, or which carries a disclosure or a `cnf` claim.

</div>

## What the credential names {#ts-5-07-what-the-credential-names}

### The entity {#ts-5-07-the-entity}

`sub` is the registration's `did:webvh`, the identifier its trusted list entry
carries in `OtherIds`. That identifier survives every key rotation, so a
rotation changes nothing in the credential.

`entity_name` is the legal name of the body behind the registration, copied
from the `TEName` of its trusted list entry in Indonesian, so that the two
documents cannot drift apart.

`entity_type` names the roles. Its values are the role service type identifiers
of [the table of service types][tbl-ts-5-01-service-types]:
`https://idctf.id/ns/19602/SvcType/IdentityIssuer`,
`https://idctf.id/ns/19602/SvcType/AttributeIssuer`,
`https://idctf.id/ns/19602/SvcType/WalletProvider`, and
`https://idctf.id/ns/19602/SvcType/RelyingParty`. A Verifier Issuing CA
service, a witness service, a trusted list signer service, and a revoked key
service say nothing about a role.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-07-019 }**REQ-TS-5-07-019** `sub` MUST be the `did:webvh` of the accredited registration, the identifier its trusted list entry carries in the `ServiceDigitalIdentity` of its role services.
- [](){ #req-ts-5-07-020 }**REQ-TS-5-07-020** `sub` MUST NOT be a `did:key`, a domain name, or any identifier other than that one.
- [](){ #req-ts-5-07-021 }**REQ-TS-5-07-021** `entity_name` MUST be the `TEName` of that entry in Indonesian, byte for byte.
- [](){ #req-ts-5-07-022 }**REQ-TS-5-07-022** `entity_type` MUST be a non-empty array of role service type identifiers from [the table of service types][tbl-ts-5-01-service-types].
- [](){ #req-ts-5-07-023 }**REQ-TS-5-07-023** `entity_type` MUST carry one identifier for each role service of that entry at status `granted`, and no other identifier.
- [](){ #req-ts-5-07-024 }**REQ-TS-5-07-024** `entity_type` MUST NOT carry the identifier of a Verifier Issuing CA service, a witness service, a trusted list signer service, or a revoked key service.
- [](){ #req-ts-5-07-025 }**REQ-TS-5-07-025** A reader MUST NOT read a role from the credential that `entity_type` does not name.
- [](){ #req-ts-5-07-026 }**REQ-TS-5-07-026** A reader MUST compare an identifier in `entity_type` with the value it expects byte for byte, after no transformation of any kind.

</div>

### The scope {#ts-5-07-the-scope}

`scope` is the list of permissions the Root Authority had granted to the
registration when the credential was issued. Each entry is an object with
`action` and `resource`, written the way
[Answering with an Authority Statement](answering-with-an-authority-statement.md)
fixes them: an action from [the table of actions][tbl-ts-5-05-actions], and a
resource that is a credential type or one attribute of one.

It is a record of what was granted, never an authority. Trust Authority
reissues the credential when the permissions change, but the entity goes on
holding every copy it was ever sent. The `scope` in front of a reader may
therefore be months out of date, and nothing in the credential says which copy
is current. A
party that has to know what an entity may do asks Trust Registry and reads the
Authority Statement it answers with.

The array is empty for a registration that holds no permission, which is every
registration that holds the Wallet Provider role alone: a Wallet Provider issues
no credential and requests none, so no permission can be scoped to that role.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-07-027 }**REQ-TS-5-07-027** `scope` MUST be an array.
- [](){ #req-ts-5-07-087 }**REQ-TS-5-07-087** `scope` MAY be empty.
- [](){ #req-ts-5-07-028 }**REQ-TS-5-07-028** Each entry of `scope` MUST carry `action` and `resource` and no other member.
- [](){ #req-ts-5-07-029 }**REQ-TS-5-07-029** `action` MUST be a value the Governance Profile lists, as [REQ-TS-5-05-013][req-ts-5-05-013] requires of an Authority Statement.
- [](){ #req-ts-5-07-030 }**REQ-TS-5-07-030** `resource` MUST take the form [REQ-TS-5-05-016][req-ts-5-05-016] fixes for the resource of a permission.
- [](){ #req-ts-5-07-031 }**REQ-TS-5-07-031** `scope` MUST hold one entry for each permission the registration held when the credential was issued, and no entry for a permission it did not hold.
- [](){ #req-ts-5-07-032 }**REQ-TS-5-07-032** A reader MUST NOT act on an entry of `scope` as a permission.
- [](){ #req-ts-5-07-033 }**REQ-TS-5-07-033** A reader that has to establish what an entity may do MUST obtain an Authority Statement for the action and the resource in question.

</div>

### What it does not carry {#ts-5-07-what-it-does-not-carry}

The credential names no assurance level. An issuer's grade follows from where
its signing key lives and changes with an ordinary key change rather than with
a reaccreditation, as
[two assurance levels](../architecture-framework/trust-model/two-assurance-levels.md)
sets out. A claim that moved without the accreditation moving would be wrong for
most of the credential's life.

It names no approval tier, because no participant carries one: a tier grades a
request, not a party. It names no accrediting party beyond `iss`, because the
Root Authority accredits directly and the ecosystem has no intermediate
authority to name.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-07-034 }**REQ-TS-5-07-034** Trust Authority MUST NOT include an assurance level in the credential.
- [](){ #req-ts-5-07-035 }**REQ-TS-5-07-035** Trust Authority MUST NOT include an approval tier in the credential.
- [](){ #req-ts-5-07-036 }**REQ-TS-5-07-036** Trust Authority MUST NOT name an accrediting party in the credential other than in `iss`.

</div>

## Signature {#ts-5-07-signature}

Trust Authority signs each credential with the Accreditation Credential key, a
P-256 key held in its HSM and published as the `accreditation-credential`
purpose in its own DID Document, as
[Publishing and resolving a did:webvh identifier](publishing-and-resolving-a-did-webvh-identifier.md)
fixes. The key signs Accreditation Credentials and nothing else: a key that
also signed a published list would carry the forgery of an accreditation into
that list.

`kid` is the `id` of the signing key's verification method, formed as
[REQ-TS-5-02-023][req-ts-5-02-023] requires; in
[Accreditation Credentials as issued][ts-5-07-accreditation-credentials-as-issued]
it is
`did:webvh:QmZjy1t9oFiaFjhX2e38uMuR7mgtdLjHPMGfjEfvrsmaiq:trust.go.id#accreditation-credential-1`.

A new signing key is a new entry in Trust Authority's log, announced the way
every other key of an entity is announced. A credential signed by a superseded
key goes on verifying, because the entry that carried that key stays in the
log, so a rotation reissues nothing.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-07-037 }**REQ-TS-5-07-037** Trust Authority MUST sign every Accreditation Credential with the Accreditation Credential key.
- [](){ #req-ts-5-07-038 }**REQ-TS-5-07-038** The Accreditation Credential key MUST be the key published as the `accreditation-credential` purpose in Trust Authority's DID Document.
- [](){ #req-ts-5-07-039 }**REQ-TS-5-07-039** Trust Authority MUST NOT sign any other artifact with that key.
- [](){ #req-ts-5-07-040 }**REQ-TS-5-07-040** Trust Authority MUST hold the private half of that key in its HSM.
- [](){ #req-ts-5-07-041 }**REQ-TS-5-07-041** *Withdrawn: [REQ-TS-01-035][req-ts-01-035] covers it.*
- [](){ #req-ts-5-07-042 }**REQ-TS-5-07-042** A credential MUST carry exactly one signature.
- [](){ #req-ts-5-07-043 }**REQ-TS-5-07-043** A reader MUST find the signing key as [Finding the key][ts-01-finding-the-key] of TS-01 requires, under the purpose `accreditation-credential`.
- [](){ #req-ts-5-07-044 }**REQ-TS-5-07-044** *Withdrawn: [REQ-TS-01-022][req-ts-01-022] covers it.*
- [](){ #req-ts-5-07-045 }**REQ-TS-5-07-045** *Withdrawn: [REQ-TS-01-020][req-ts-01-020] covers it.*
- [](){ #req-ts-5-07-046 }**REQ-TS-5-07-046** Trust Authority MUST NOT reissue a credential on a rotation of the Accreditation Credential key.

</div>

## Lifetime {#ts-5-07-lifetime}

The Governance Profile sets how long an accreditation period runs and how far
before `exp` a renewal is prepared. When the accreditation first took effect is
read from the `StatusStartingTime` of the entry's role services on the
trusted list, which a suspension and a restoration do not move, and not from
this credential.

A renewal is a new credential. It carries a new `iat`, a new `exp`, the same
`sub`, and the same index in the status list, so the entity's place in that
list never moves.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-07-047 }**REQ-TS-5-07-047** `iat` and `exp` MUST each be a number of seconds since the Unix epoch.
- [](){ #req-ts-5-07-048 }**REQ-TS-5-07-048** `iat` MUST be the moment Trust Authority issued the credential.
- [](){ #req-ts-5-07-049 }**REQ-TS-5-07-049** `exp` MUST be later than `iat`.
- [](){ #req-ts-5-07-050 }**REQ-TS-5-07-050** `exp` MUST NOT be later than the end of the accreditation period.
- [](){ #req-ts-5-07-051 }**REQ-TS-5-07-051** Trust Authority MUST issue a replacement credential before `exp` when the accreditation continues past it.
- [](){ #req-ts-5-07-052 }**REQ-TS-5-07-052** A replacement credential MUST carry the same `sub` and the same `status.status_list.idx` as the credential it replaces.
- [](){ #req-ts-5-07-053 }**REQ-TS-5-07-053** A reader MUST refuse a credential whose `exp` has passed.
- [](){ #req-ts-5-07-054 }**REQ-TS-5-07-054** A reader MUST refuse a credential whose `iat` is later than the moment it reads it.

</div>

## Status and revocation {#ts-5-07-status-and-revocation}

An accreditation that is withdrawn after two months leaves a credential that
expires in two years, which is why the credential carries a status reference.
`status.status_list` names an index and the address of the accreditation status
list, as [IETF Token Status List draft -14][ref-i-d-ietf-oauth-status-list] fixes the
claim, and in
[Accreditation Credentials as issued][ts-5-07-accreditation-credentials-as-issued]
that address is
`https://registry.trust.go.id/status/accreditations-1`.

The format of the list, the signature on it, how often it is republished, and
how a reader fetches a copy are fixed by
[Publishing and reading a status list](publishing-and-reading-a-status-list.md).

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-07-055 }**REQ-TS-5-07-055** `status` MUST carry `status_list` and no other member.
- [](){ #req-ts-5-07-056 }**REQ-TS-5-07-056** `status.status_list` MUST carry `idx` and `uri` and no other member.
- [](){ #req-ts-5-07-057 }**REQ-TS-5-07-057** `status.status_list.idx` MUST be the index of the registration in the accreditation status list.
- [](){ #req-ts-5-07-058 }**REQ-TS-5-07-058** `status.status_list.uri` MUST be the address the accreditation status list is published at.
- [](){ #req-ts-5-07-059 }**REQ-TS-5-07-059** Trust Registry MUST allocate one index per registration, on the day the accreditation is granted.
- [](){ #req-ts-5-07-060 }**REQ-TS-5-07-060** Trust Registry MUST NOT allocate an index that another registration has held.
- [](){ #req-ts-5-07-061 }**REQ-TS-5-07-061** Trust Registry MUST set the entry of a registration to valid while its accreditation is granted.
- [](){ #req-ts-5-07-062 }**REQ-TS-5-07-062** Trust Registry MUST set the entry to suspended when the Root Authority suspends the accreditation.
- [](){ #req-ts-5-07-063 }**REQ-TS-5-07-063** Trust Registry MUST set the entry to invalid when the Root Authority withdraws the accreditation.
- [](){ #req-ts-5-07-064 }**REQ-TS-5-07-064** Trust Registry MUST set the entry back to valid when a suspended accreditation is restored.
- [](){ #req-ts-5-07-065 }**REQ-TS-5-07-065** Trust Registry MUST set the entry within the time the Governance Profile allows after the Root Authority changes the status.
- [](){ #req-ts-5-07-066 }**REQ-TS-5-07-066** Trust Registry MUST set the entry of a registration and the status of its trusted list entry from one decision, so that the two cannot disagree.

</div>

## Reading it {#ts-5-07-reading-it}

A party shown an Accreditation Credential runs the steps below. Every step up
to the status list entry establishes that the credential is what it claims to
be; the trusted list lookup is the one that answers the question the party has.

1. Resolve the DID in `iss` to Trust Authority's DID Document.
2. Find the verification method `kid` names among its verification methods, and
   confirm that its purpose is `accreditation-credential`.
3. Check the signature over the encoded header and payload with the public key
   of that verification method.
4. Check that `typ` is `dc+sd-jwt` and that `vct` is
   `id.idctf.accreditation.1`.
5. Check that `iat` is in the past and `exp` is in the future.
6. Fetch the accreditation status list `status.status_list.uri` names and read
   the entry at `status.status_list.idx`.
7. Look the registration up in the trusted list by the `did:webvh` in `sub`,
   and act on what that entry says.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-07-067 }**REQ-TS-5-07-067** A reader MUST run the steps of [Reading it][ts-5-07-reading-it] in the order given.
- [](){ #req-ts-5-07-068 }**REQ-TS-5-07-068** A reader MUST refuse a credential whose signature does not verify.
- [](){ #req-ts-5-07-069 }**REQ-TS-5-07-069** A reader MUST refuse a credential whose status list entry is invalid or suspended.
- [](){ #req-ts-5-07-070 }**REQ-TS-5-07-070** A reader that cannot read the status list entry MUST act on the trusted list alone.
- [](){ #req-ts-5-07-071 }**REQ-TS-5-07-071** A reader MUST NOT treat an Accreditation Credential as evidence that its subject takes part in the ecosystem.
- [](){ #req-ts-5-07-072 }**REQ-TS-5-07-072** A reader MUST refuse an entity whose registration is absent from the trusted list, whatever its credential says.
- [](){ #req-ts-5-07-073 }**REQ-TS-5-07-073** A reader MUST refuse an entity whose trusted list entry is `suspended`, `withdrawn`, or `revoked` for the role in question, whatever its credential says.
- [](){ #req-ts-5-07-074 }**REQ-TS-5-07-074** A reader MUST NOT conclude from the absence of a credential, or from a credential it cannot verify, that the entity is not accredited, because the trusted list answers that question and the credential does not.
- [](){ #req-ts-5-07-075 }**REQ-TS-5-07-075** A Module MUST NOT require an Accreditation Credential before it acts.

</div>

## Issuing, reissuing, and withdrawing {#ts-5-07-issuing-reissuing-and-withdrawing}

Trust Authority issues the credential when the Root Authority grants the
accreditation, and returns it in the exchange that returns the entity's witness
proof and its certificate, as
[Onboarding an entity and registering its keys](onboarding-an-entity-and-registering-its-keys.md)
fixes.

A credential is reissued when what it says stops being true: a permission is
granted, narrowed, or withdrawn, a role service is added or ends, the legal name
on the entry changes, or the accreditation is renewed. A key rotation is none
of these, and neither is a change in where the entity's signing key lives.

A suspension reissues nothing: the status list carries it, and the credential
is unchanged while it lasts. Trust Authority issues no credential to a
suspended registration, so a change to the permissions or the role services of
one waits. Restoration is where the wait ends: the registration is accredited
again, and Trust Authority reissues then if what the credential says changed
meanwhile.

A replacement before `exp` and a reissue after a change both supersede the
credential in force at that moment. The earlier copy stays unexpired and valid
in the status list, because the two share an index. Nothing in the ecosystem
acts on either of them, so no reader has to tell them apart.

A withdrawal ends the accreditation, not the copy the entity holds. Trust
Registry sets the status list entry to invalid and sets every role service and
every Verifier Issuing CA service of the trusted list entry to `withdrawn`;
nothing recalls the file on the entity's disk. The Use Statements of that entity end with the
accreditation, as [REQ-TS-5-06-083][req-ts-5-06-083] requires.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-07-076 }**REQ-TS-5-07-076** Trust Authority MUST issue an Accreditation Credential when the Root Authority grants an accreditation.
- [](){ #req-ts-5-07-077 }**REQ-TS-5-07-077** Trust Authority MUST treat the last Accreditation Credential it issued to a registration as the one in force, and every earlier one as superseded.
- [](){ #req-ts-5-07-078 }**REQ-TS-5-07-078** Trust Authority MUST reissue the credential when the set of permissions of the registration changes, unless its accreditation is suspended.
- [](){ #req-ts-5-07-079 }**REQ-TS-5-07-079** Trust Authority MUST reissue the credential when a role service of the registration is added or ends, unless its accreditation is suspended.
- [](){ #req-ts-5-07-080 }**REQ-TS-5-07-080** Trust Authority MUST reissue the credential when the `TEName` of the registration's trusted list entry changes, unless its accreditation is suspended.
- [](){ #req-ts-5-07-081 }**REQ-TS-5-07-081** Trust Authority MUST NOT reissue the credential when the entity rotates a key.
- [](){ #req-ts-5-07-082 }**REQ-TS-5-07-082** Trust Authority MUST NOT issue a credential to a registration whose accreditation is suspended or withdrawn.
- [](){ #req-ts-5-07-088 }**REQ-TS-5-07-088** Trust Authority MUST reissue the credential when an accreditation is restored and anything [REQ-TS-5-07-078][req-ts-5-07-078], [REQ-TS-5-07-079][req-ts-5-07-079], or [REQ-TS-5-07-080][req-ts-5-07-080] names changed during the suspension.
- [](){ #req-ts-5-07-083 }**REQ-TS-5-07-083** Trust Authority MUST record the credentials it issued to a registration with their `iat`, `exp`, and the reason for each reissue.
- [](){ #req-ts-5-07-084 }**REQ-TS-5-07-084** Trust Authority MUST NOT require an entity to return or destroy a credential that has been superseded or withdrawn.

</div>

## Security considerations {#ts-5-07-security-considerations}

- **A forged credential.** Anyone can mint a JSON Web Signature and call it an
  accreditation. [REQ-TS-5-07-043][req-ts-5-07-043] and
  [REQ-TS-5-07-068][req-ts-5-07-068] make a reader resolve the key in
  Trust Authority's DID Document and refuse a signature that does not verify,
  and [REQ-TS-5-07-072][req-ts-5-07-072] makes the trusted list decide the
  question anyway, so a forgery that never reaches the list buys nothing.
- **A credential that outlives its accreditation.** A withdrawal takes effect
  the moment the Root Authority makes it, and the entity still holds a file
  that says otherwise until `exp`.
  [REQ-TS-5-07-063][req-ts-5-07-063] and [REQ-TS-5-07-069][req-ts-5-07-069]
  close that window through the status list, and
  [REQ-TS-5-07-066][req-ts-5-07-066] keeps the list and the trusted list from
  disagreeing about the same decision.
- **A credential presented by a party that is not its subject.** The credential
  has no key binding, so possession proves nothing.
  [REQ-TS-5-07-071][req-ts-5-07-071] and [REQ-TS-5-07-075][req-ts-5-07-075]
  keep anything in the ecosystem from turning on possession, and a party
  outside it that acts on one acts on the trusted list entry in `sub` rather
  than on the party in front of it.
- **The signing key.** A stolen Accreditation Credential key forges an
  accreditation for any entity the thief names.
  [REQ-TS-5-07-039][req-ts-5-07-039] and [REQ-TS-5-07-040][req-ts-5-07-040]
  keep it in the HSM and keep it from signing anything else, so its theft
  cannot reach a published list, and the trusted list is what a reader acts on.
- **A reader that trusts the credential over the list.** A credential that is
  genuine, unexpired, and valid in the status list still says nothing about
  whether its subject takes part today, and a party that stops reading there
  accepts an entity the Root Authority removed this morning.
  [REQ-TS-5-07-032][req-ts-5-07-032], [REQ-TS-5-07-071][req-ts-5-07-071], and
  [REQ-TS-5-07-074][req-ts-5-07-074] each close one direction of that mistake:
  the permission, the participation, and the refusal read from an absence.

## Privacy considerations {#ts-5-07-privacy-considerations}

The credential carries no personal data. It names a legal body, its identifier,
its roles, and its permissions, and the trusted list publishes the legal body,
its identifier, and its roles to everyone already.

Fetching the status list shows the publisher which registration a reader is
interested in. The list is published whole and read from a cached copy rather
than queried per index. A reader that keeps a copy reveals nothing about the
entity it is checking, and one that fetches a fresh copy reveals only that it
is checking something.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-07-085 }**REQ-TS-5-07-085** Trust Authority MUST NOT include personal data in an Accreditation Credential.
- [](){ #req-ts-5-07-086 }**REQ-TS-5-07-086** A reader MUST NOT ask Trust Registry for the status of one index.

</div>

## Changelog {#ts-5-07-changelog}

<figure markdown="1" class="ekdn-table">

| Version | Date | Change |
|---|---|---|
| 1.0 draft | 21 October 2026 | First draft |

</figure>
