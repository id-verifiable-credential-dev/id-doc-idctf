---
title: "[TS-5-02] Publishing and resolving a did:webvh identifier"
description: The did:webvh profile every entity and Trust Authority use, the DID Document and its keys, the witness proof DID Service adds, how the log is published and copied, and how a reader resolves it.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, Kep. 4, 9, §3.3, §4.1, §4.3, §4.6, §5.4, §5.7, §7.1, §7.7, §9.4; Rincian Module dan Operasi §3, §4; tracks/0240, tracks/0246 -->

<p class="ekdn-docid">TS-5-02</p>

# Publishing and resolving a did:webvh identifier {#ts-5-02-publishing-and-resolving-a-did-webvh-identifier}

<p class="ekdn-lead" markdown="span">
Every entity, and Trust Authority itself, is known by a `did:webvh`
identifier backed by a signed, append-only log on its own domain. This
specification fixes the profile of that method: what the log carries, what
the Decentralized Identifier (DID) Document holds, what DID Service witnesses, and how a reader
resolves it.
</p>

Every sentence on this page binds the Modules that keep a `did:webvh` log
and the Modules that resolve one, and an Assessment Body tests them against
it in the version the Governance Profile puts in force. The key words and
the identifier `REQ-TS-5-02-nnn` follow [Common provisions](common-provisions.md).

## Who runs this and what it needs {#ts-5-02-who-runs-this-and-what-it-needs}

This specification is a profile of [`did:webvh`][ref-did-webvh] version 1.0
for the identifiers of IDCTF. It fixes:

- The form of the identifier.
- The parameters of every log entry.
- The keys that sign the log and the keys the DID Document publishes.
- How the entity rotates a key and publishes its log.
- The rules a reader applies when it resolves an identifier.

Entity means a party that holds a `did:webvh`: every accredited registration, and
the Root Authority, whose log Trust Authority maintains.

Its conformance targets are:

- Issuer Core, Verifier Core, and Wallet Backend Service, the three
  Modules that maintain an entity's log through their Key Manager
  Component.
- Trust Authority, which maintains its own log.
- Issuer Core, Verifier Core, Mobile Wallet, and Mobile Verifier, the four
  Modules that resolve identifiers, which meet the reader requirements
  through Trust SDK where the library performs the check.

It leaves to other documents:

- What DID Service checks before it witnesses an entry, the proof it
  returns, and the copy it serves, which
  [Witnessing a log entry and serving its copy](witnessing-a-log-entry-and-serving-its-copy.md)
  holds.
- The door through which an entity submits an entry,
  `POST /entities/me/keys` on Trust Authority, with its proof of possession
  and its `keyStorage` evidence, which
  [Onboarding an entity and registering its keys](onboarding-an-entity-and-registering-its-keys.md)
  holds.
- Which witness keys and which revoked keys a reader accepts, which
  [Publishing and reading the trusted list](publishing-and-reading-the-trusted-list.md)
  holds.
- The rotation schedule of each key and the tolerance limit of a cached
  log, which the Governance Profile holds.
- The certificates an entity's keys may also carry, which
  [Issuing and validating the X.509 certificates and the VICAL](issuing-and-validating-the-x509-certificates-and-the-vical.md)
  holds.
- The form of every `did:key` a log or a proof names, the holder's
  `did:key`, and the device identifier, which
  [Deriving a did:key and a device identifier](deriving-a-did-key-and-a-device-identifier.md)
  holds.

Before the first exchange, each target holds what the rules below assume:

- **The holder of a log** holds a Key Manager Component with the driver it
  chose, or, for Trust Authority, its hardware security module (HSM); a
  domain it controls, served over Transport Layer Security (TLS); and access
  to Trust Authority's entity door.
- **A reader** carries Trust Authority's self-certifying identifier (SCID)
  and the trusted list key from build time, holds a cached trusted list, and
  embeds Trust SDK, which performs the checks of
  [Resolving][ts-5-02-resolving].

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-02-001 }**REQ-TS-5-02-001** Issuer Core, Verifier Core, and Wallet Backend Service MUST each meet every requirement in [The identifier][ts-5-02-the-identifier], [The log][ts-5-02-the-log], [The DID Document][ts-5-02-the-did-document], [Rotation][ts-5-02-rotation], and [Publication][ts-5-02-publication].
- [](){ #req-ts-5-02-002 }**REQ-TS-5-02-002** Trust Authority MUST meet every requirement in [Trust Authority's own identifier][ts-5-02-trust-authoritys-own-identifier] and, as the holder of its own log, every requirement addressed to the holder of a log.
- [](){ #req-ts-5-02-003 }**REQ-TS-5-02-003** Issuer Core, Verifier Core, Mobile Wallet, and Mobile Verifier MUST each meet every requirement in [Resolving][ts-5-02-resolving].

</div>

## What an identifier proves {#ts-5-02-overview}

An entity's identifier proves one thing: that a signature belongs to the
entity that claims it. Whether the entity is accredited, and what it may do,
are answered by the trusted list and the Authority Statement, as
[three questions, three answers][three-questions-three-answers] sets out. A DID
absent from the trusted list is refused however well its log verifies. [Entities: did:webvh][entities-didwebvh] says why the method was
chosen and [the DID Document][did-document] says where the log lives, who
reads it, and that DID Service witnesses and does not publish.

`did:webvh` publishes the whole history of a DID as a log, one entry per version
of the DID Document, each entry chained to the one before by a hash, signed by
the entity's update key, and countersigned by a witness. The SCID inside the DID
is a hash of the first entry, so the identifier binds the history without
depending on the domain that serves it. Pre-rotation commits each entry to the
hash of the next update key, so a stolen key cannot rotate to a key of the
thief's choosing. [The update key][the-update-key] explains the three
properties and [how an entity rotates a key][how-an-entity-rotates-a-key]
shows the path a new entry takes.

## The log as published {#ts-5-02-the-log-as-published}

The log is an illustration: the issuer, its domain, and its keys are
invented, and no registration has been accredited. Every field is exact.
The self-certifying identifier, both entry hashes, and the pre-rotation
hash were computed with the algorithms of
[did:webvh][ref-did-webvh], every proof is a real `eddsa-jcs-2022`
signature, and the whole log passes the method's Read steps, so an
implementation can replay it and get the same values.

The log and the witness file beside it show every option this profile
admits:

- The first entry, with `method`, `scid`, `portable`, and the full
  `witness` and `watchers`.
- A second entry that rotates both the update key and a transaction key,
  with the old `issuance-jose` key kept in `verificationMethod` and gone
  from `assertionMethod`.
- The second witness key beside the first in that entry, while Trust Authority
  rotates its witness key.
- Both issuer purposes.
- The witness file, carrying the latest proof per witness.

The log agrees with the other pages on three points:

- The identifier is the one [the trusted list][ts-5-01-trusted-list-payload]
  carries for that issuer.
- The times match [the trusted list payload][ts-5-01-trusted-list-payload],
  where the first witness key is `granted` from 1 January 2026 and
  `withdrawn` from 1 October 2026 and the second is `granted` from
  1 September 2026.
- The witness proof is the one
  [Witnessing a log entry and serving its copy](witnessing-a-log-entry-and-serving-its-copy.md)
  returns.

The keys of a Relying Party and of a Wallet Provider follow
[the table of keys by role][tbl-ts-5-02-keys-by-role] in the same shape,
and carry no `keyAgreement` entry, because the key a wallet encrypts a
presentation to is not published in the DID Document.

``` { .json title="did.jsonl, served at https://dukcapil.go.id/.well-known/did.jsonl" data-format="JSONL" }
{"versionId": "1-QmVKY1B6GfgWufkmEJ8NWR83QbYUjgcFrx1VJaFrqLrsje", "versionTime": "2026-02-01T00:00:00Z", "parameters": {"method": "did:webvh:1.0", "scid": "QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4", "updateKeys": ["z6MkhDXZtBHLUKK27G1d5s5CN4J6ekJwBhRrfmkBKMKD5DVX"], "nextKeyHashes": ["QmVC43PqjprVjnkqf8nEKScSwBE8BvJqrfhBW23BBaMj7s"], "witness": {"threshold": 1, "witnesses": [{"id": "did:key:z6MkrGRs1p2FjsQsxJtKwmaUotzGtjmjcvM7uKcnXU7ffLKe"}]}, "watchers": ["https://did.trust.go.id"], "portable": false}, "state": {"@context": ["https://www.w3.org/ns/did/v1", "https://w3id.org/security/multikey/v1"], "id": "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id", "verificationMethod": [{"id": "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id#issuance-jose-1", "type": "Multikey", "controller": "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id", "publicKeyMultibase": "zDnaeWSwJDrKLraHe5w4vA39xFW2TnZaDDNEGGWSyHYSC9Nfp"}, {"id": "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id#status-list-1", "type": "Multikey", "controller": "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id", "publicKeyMultibase": "zDnaeamPEKdV4VYmsDaPr9f3LyENGRFTwHRpoNvRLyi2gznvD"}], "assertionMethod": ["did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id#issuance-jose-1", "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id#status-list-1"]}, "proof": [{"type": "DataIntegrityProof", "cryptosuite": "eddsa-jcs-2022", "verificationMethod": "did:key:z6MkhDXZtBHLUKK27G1d5s5CN4J6ekJwBhRrfmkBKMKD5DVX#z6MkhDXZtBHLUKK27G1d5s5CN4J6ekJwBhRrfmkBKMKD5DVX", "proofPurpose": "assertionMethod", "proofValue": "z67gL2PpK1JnCw3C5MNyX9xxEqGb628bSe6AT1PnED54jbryYqAGw4VXMZDaY1GhqXbMGPXfybXAAnb811UmeEbah"}]}
{"versionId": "2-QmNr7vHPCnSA8GVeQpeBZdj1vNheZviyVjRwiJy3gt1zJE", "versionTime": "2026-09-15T09:00:00Z", "parameters": {"updateKeys": ["z6MkgneGrxeNdi2mi6swidp38iqtkk6r2iaEgf25Kufb7rRL"], "nextKeyHashes": ["QmXVqEyGwzQHfLQ1SG4MCKA5GHNvuJRDV22XX5CCQrsjcw"], "witness": {"threshold": 1, "witnesses": [{"id": "did:key:z6MkrGRs1p2FjsQsxJtKwmaUotzGtjmjcvM7uKcnXU7ffLKe"}, {"id": "did:key:z6MktqjEVK1P1HgMSJYGpPYjuLjEa13u26WEhf7dvCWPYZj1"}]}}, "state": {"@context": ["https://www.w3.org/ns/did/v1", "https://w3id.org/security/multikey/v1"], "id": "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id", "verificationMethod": [{"id": "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id#issuance-jose-1", "type": "Multikey", "controller": "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id", "publicKeyMultibase": "zDnaeWSwJDrKLraHe5w4vA39xFW2TnZaDDNEGGWSyHYSC9Nfp"}, {"id": "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id#status-list-1", "type": "Multikey", "controller": "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id", "publicKeyMultibase": "zDnaeamPEKdV4VYmsDaPr9f3LyENGRFTwHRpoNvRLyi2gznvD"}, {"id": "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id#issuance-jose-2", "type": "Multikey", "controller": "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id", "publicKeyMultibase": "zDnaegmvjP5yMynYdQDsDyRAtCKHooT7PuhqVaxN7RSAgBZ6E"}], "assertionMethod": ["did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id#issuance-jose-2", "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id#status-list-1"]}, "proof": [{"type": "DataIntegrityProof", "cryptosuite": "eddsa-jcs-2022", "verificationMethod": "did:key:z6MkgneGrxeNdi2mi6swidp38iqtkk6r2iaEgf25Kufb7rRL#z6MkgneGrxeNdi2mi6swidp38iqtkk6r2iaEgf25Kufb7rRL", "proofPurpose": "assertionMethod", "proofValue": "z2mudE1JVEhZQgxeN5duy1PmeChmo9r9mRzZrpEcPVWJA9Jp6nZ92PC3t8SfeMGscGCMfdDhwPg13F9CyWwJZyALV"}]}
```

``` { .json title="did-witness.json, served at https://dukcapil.go.id/.well-known/did-witness.json" data-format="JSON" }
[
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
]
```

The second entry is signed with the key the first entry announced in
`nextKeyHashes`, because pre-rotation is active, and it announces the key
after that. Its witness proof is from the first witness key, because a
change to the witness list takes effect only after the entry that makes it
is published; from the third entry on, either key may witness, until the
first is withdrawn.

The witness file holds one proof, on the second entry,
because a proof on a later entry vouches for every earlier one and the
entity removed the older proof, as the method allows.

The `issuance-jose-1` key stays in `verificationMethod`, so a reader checking a credential it
signed before 15 September 2026 still finds it in the first version, and it
is absent from `assertionMethod` of the second, so it signs nothing new.
Staying in the document settles where the key is published, not whether a
signature it made is accepted: the log cannot tell a retired key from a
revoked one. The trusted list names this one revoked from 16 October 2026,
which makes a reader refuse it whatever date the signature claims,
[REQ-TS-5-01-075][req-ts-5-01-075].

## The identifier {#ts-5-02-the-identifier}

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-02-004 }**REQ-TS-5-02-004** An entity's identifier MUST be a `did:webvh` DID as [did:webvh][ref-did-webvh] version 1.0 defines it: `did:webvh:<scid>:<domain>`, optionally followed by path segments.
- [](){ #req-ts-5-02-005 }**REQ-TS-5-02-005** The domain MUST be a domain the registration's legal body controls.
- [](){ #req-ts-5-02-006 }**REQ-TS-5-02-006** The log MUST be served from the domain the identifier names.
- [](){ #req-ts-5-02-007 }**REQ-TS-5-02-007** The identifier MUST NOT carry a port.
- [](){ #req-ts-5-02-008 }**REQ-TS-5-02-008** Every registration MUST have an identifier of its own.
- [](){ #req-ts-5-02-009 }**REQ-TS-5-02-009** Two registrations MUST NOT share a log.
- [](){ #req-ts-5-02-010 }**REQ-TS-5-02-010** The DID Document's `id` MUST be the bare DID, with no query and no fragment.

</div>

The DID transforms to the address of the log as the method defines:
`https://<domain>/.well-known/did.jsonl` when the identifier carries no
path segment, and `https://<domain>/<path>/did.jsonl` when it does, each
path segment becoming one segment of the path. The witness file sits beside
the log, as `did-witness.json` in place of `did.jsonl`. One legal body that
holds several registrations gives each its own identifier; whether that is
a subdomain or a path under one domain is the body's choice, and
[one entry per registration][ts-5-01-one-entry-per-registration] tells them
apart on the trusted list.

## The log {#ts-5-02-the-log}

The log is the file `did.jsonl`, one JSON object per line, each object a
log entry with `versionId`, `versionTime`, `parameters`, `state`, and
`proof`, as the method defines them. This profile fixes the parameters an
IDCTF log carries; [the table of parameters][tbl-ts-5-02-parameters] gives
each one in the order the method lists them.

[](){ #tbl-ts-5-02-parameters }

<figure markdown="1" class="ekdn-table">

| Parameter | First entry | Later entries |
|---|---|---|
| `method` | `did:webvh:1.0` | Absent, until a later version of this specification raises it |
| `scid` | The SCID, computed as the method defines | Absent |
| `updateKeys` | Exactly one Ed25519 public key, as a Multikey string | Present in every entry, exactly one key, because pre-rotation is active |
| `nextKeyHashes` | Exactly one hash, of the next update key | Present in every entry, exactly one hash |
| `witness` | `threshold` `1`; one `witnesses` item per `did:key` the trusted list names as a witness at status `granted` | Repeated only when the witness list changes |
| `watchers` | One address: DID Service's Resolver endpoint | Repeated only when the address changes |
| `portable` | `false` | Absent |
| `deactivated` | Absent | Absent |
| `ttl` | Absent | Absent |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-02-011 }**REQ-TS-5-02-011** Every log entry MUST follow [did:webvh][ref-did-webvh] version 1.0, with `parameters` set as [the table of parameters][tbl-ts-5-02-parameters] requires.
- [](){ #req-ts-5-02-012 }**REQ-TS-5-02-012** `updateKeys` MUST hold exactly one key, the entity's current update key, as an Ed25519 Multikey string.
- [](){ #req-ts-5-02-013 }**REQ-TS-5-02-013** `nextKeyHashes` MUST hold exactly one hash, that of the update key the next entry will carry, so that pre-rotation is active from the first entry and is never switched off.
- [](){ #req-ts-5-02-074 }**REQ-TS-5-02-074** `nextKeyHashes` MUST NOT hold the hash of a key that the same entry carries in `updateKeys`, so that the update key an entry reveals never signs the next entry.
- [](){ #req-ts-5-02-014 }**REQ-TS-5-02-014** `witness` MUST name, with `threshold` `1`, every `did:key` that the trusted list names in a witness service at status `granted` at the time the entry is made.
- [](){ #req-ts-5-02-015 }**REQ-TS-5-02-015** `watchers` MUST hold the address of DID Service's Resolver endpoint and no other address.
- [](){ #req-ts-5-02-016 }**REQ-TS-5-02-016** `portable` MUST be `false`.
- [](){ #req-ts-5-02-017 }**REQ-TS-5-02-017** An entity MUST NOT set `deactivated`.
- [](){ #req-ts-5-02-018 }**REQ-TS-5-02-018** An entity MUST NOT set `ttl`.
- [](){ #req-ts-5-02-019 }**REQ-TS-5-02-019** The `proof` of every entry MUST be a Data Integrity proof with cryptosuite [`eddsa-jcs-2022`][ref-vc-di-eddsa], `proofPurpose` `assertionMethod`, and a `verificationMethod` of the form `did:key:<key>#<key>` where `<key>` is the update key the entry is authorized by.
- [](){ #req-ts-5-02-020 }**REQ-TS-5-02-020** `versionTime` MUST be the time the entry was made, in Coordinated Universal Time (UTC) with the `Z` designator and without a fraction of a second, later than the previous entry's.

</div>

One update key, one next key, and a threshold of one follow the
architecture: an entity holds one key that maintains its identifier and each
entry announces the hash of the next one, as
[the update key][the-update-key] sets out. The witness is a single Module, as
[Trust Infrastructure is not a role][trust-infrastructure-is-not-a-role] sets
out, and the witness list holds two keys only while Trust Authority rotates
its witness key, as [the witness key][the-witness-key] describes.

A DID is never deactivated: a withdrawn registration is answered by the trusted list, and its
log stays resolvable so that what it signed while accredited still verifies.
`ttl` stays at the method's default because a reader refreshes its copy through
the trust cache sync and not on a timer the entity sets.

## The DID Document {#ts-5-02-the-did-document}

The `state` of each entry is the DID Document of that version. It holds the
entity's public transaction keys, and nothing else: no service endpoints,
no controller, no alias.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-02-021 }**REQ-TS-5-02-021** The DID Document MUST carry `@context` with the values `https://www.w3.org/ns/did/v1` and `https://w3id.org/security/multikey/v1`, in that order.
- [](){ #req-ts-5-02-022 }**REQ-TS-5-02-022** Every verification method MUST be of type `Multikey` as [W3C Controlled Identifiers 1.0][ref-cid] defines it, with `controller` equal to the DID and the public key in `publicKeyMultibase`.
- [](){ #req-ts-5-02-023 }**REQ-TS-5-02-023** The `id` of a verification method MUST be the DID followed by `#`, the key's `purpose`, a hyphen, and a sequence number that starts at `1` and rises by one for each key of that purpose the entity has ever published.
- [](){ #req-ts-5-02-024 }**REQ-TS-5-02-024** Every transaction key MUST be a P-256 key, encoded as the Multikey of a P-256 public key.
- [](){ #req-ts-5-02-025 }**REQ-TS-5-02-025** The DID Document MUST list each key under the verification relationship [the table of keys by role][tbl-ts-5-02-keys-by-role] gives it, and under no other.
- [](){ #req-ts-5-02-026 }**REQ-TS-5-02-026** The DID Document MUST NOT carry the update key.
- [](){ #req-ts-5-02-027 }**REQ-TS-5-02-027** The DID Document MUST NOT carry `service`, `controller`, or `alsoKnownAs`.
- [](){ #req-ts-5-02-028 }**REQ-TS-5-02-028** A verification method, once published, MUST stay in `verificationMethod` in every later version.
- [](){ #req-ts-5-02-029 }**REQ-TS-5-02-029** A key that is retired or revoked MUST be removed from every verification relationship in the next version.
- [](){ #req-ts-5-02-030 }**REQ-TS-5-02-030** A key removed from a verification relationship MUST NOT be returned to one.

</div>

[](){ #tbl-ts-5-02-keys-by-role }

<figure markdown="1" class="ekdn-table">

| Who | `purpose` | Signs or decrypts | Relationship |
|---|---|---|---|
| Identity Issuer, Attribute Issuer | `issuance-jose` | SD-JWT VC, the Data Integrity proof of `ldp_vc`, and the signed issuer metadata | `assertionMethod` |
| Identity Issuer, Attribute Issuer | `status-list` | The Status List Token and the Bitstring Status List | `assertionMethod` |
| Relying Party | `request-object` | The Request Object of a presentation request | `assertionMethod` |
| Wallet Provider | `key-attestation` | The Key Attestation | `assertionMethod` |
| Trust Authority | `accreditation-credential` | The Accreditation Credential | `assertionMethod` |
| Trust Authority | `authority-statement` | Each answer Trust Registry returns to a permission query | `assertionMethod` |
| Trust Authority | `recognition-statement` | Each answer Trust Registry returns to a recognition query | `assertionMethod` |
| Trust Authority | `catalog` | The catalog list | `assertionMethod` |
| Trust Authority | `use-statement` | Each Use Statement | `assertionMethod` |
| Trust Authority | `use-statement-status-list` | The Use Statement status list | `assertionMethod` |
| Trust Authority | `accreditation-status-list` | The accreditation status list | `assertionMethod` |

</figure>

The keys an entity holds, and why an issuer's `issuance-cose` key and a
Verifier Issuing CA key appear in no DID Document, are in
[the entity's keys][the-entitys-keys]: those two live in certificates, and
the certificate travels with what they sign. The key the wallet encrypts the
presentation to travels in the Request Object, as
[Verifying a credential online via OpenID4VP](verifying-a-credential-online-via-openid4vp.md)
fixes, and is not in the DID Document. Which keys were valid when is read
from the log's versions, and a key revoked early is named by the
trusted list, never by the DID Document.

## Rotation {#ts-5-02-rotation}

A rotation runs in five steps, the same for the first entry and for every
later one.

1. The holder generates the new key where its keys live, and builds the
   next log entry signed with the update key the entry carries.
2. It submits the entry to Trust Authority through the entity door, with a
   proof of possession of each new key and its `keyStorage` evidence.
3. Trust Authority checks the governance side and hands the entry to DID
   Service, which checks the chain and returns the witness proof.
4. Trust Authority returns the witness proof, and any certificate, in the
   same exchange.
5. The holder publishes `did-witness.json`, then `did.jsonl`, on its
   domain, and signs with the new key from then on.

A rotation is a new log entry. It rotates a transaction key by adding a
verification method and moving the relationship to it, or the update key by
carrying in `updateKeys` the key whose hash the previous entry announced, or
both at once. The entry takes the path
[how an entity rotates a key][how-an-entity-rotates-a-key] shows, through
Trust Authority, and counts only once DID Service has witnessed it.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-02-031 }**REQ-TS-5-02-031** The holder of a log MUST generate every key it publishes itself: an entity in its Key Manager Component, in the driver it uses, and Trust Authority in its HSM.
- [](){ #req-ts-5-02-032 }**REQ-TS-5-02-032** The holder of a log MUST NOT publish a key generated outside the place [REQ-TS-5-02-031][req-ts-5-02-031] names.
- [](){ #req-ts-5-02-033 }**REQ-TS-5-02-033** The holder of a log MUST submit every new entry to Trust Authority, signed with the update key that entry carries, before publishing it.
- [](){ #req-ts-5-02-034 }**REQ-TS-5-02-034** The holder of a log MUST NOT publish an entry that carries no witness proof.
- [](){ #req-ts-5-02-035 }**REQ-TS-5-02-035** An entry that rotates the update key MUST carry in `updateKeys` the key whose hash the previous entry's `nextKeyHashes` holds.
- [](){ #req-ts-5-02-036 }**REQ-TS-5-02-036** Every entry after the first MUST be signed with the update key it carries in `updateKeys`, which is the key the previous entry committed to, because pre-rotation is active.
- [](){ #req-ts-5-02-037 }**REQ-TS-5-02-037** After an update key is rotated out, its private key SHOULD be destroyed, as [did:webvh][ref-did-webvh] recommends for a spent pre-rotation key.
- [](){ #req-ts-5-02-038 }**REQ-TS-5-02-038** A rotated-out update key MUST NOT sign a later entry.
- [](){ #req-ts-5-02-039 }**REQ-TS-5-02-039** When DID Service refuses an entry, the holder of a log MUST NOT publish it.
- [](){ #req-ts-5-02-040 }**REQ-TS-5-02-040** After a refusal, the holder of a log MUST submit a corrected entry through Trust Authority.
- [](){ #req-ts-5-02-041 }**REQ-TS-5-02-041** When DID Service is unreachable, the holder of a log MUST keep the signed entry and resubmit it until a witness proof comes back.
- [](){ #req-ts-5-02-042 }**REQ-TS-5-02-042** The holder of a log MUST NOT publish an entry while its witness proof is outstanding.

</div>

[REQ-TS-5-02-041][req-ts-5-02-041] and [REQ-TS-5-02-042][req-ts-5-02-042] keep
the witness requirement in force while DID Service is down, which is what
[why nobody can rotate quietly][why-nobody-can-rotate-quietly] sets out.
Every reader refuses an entry that was never witnessed, and DID Service keeps no
queue. The entity's Key Manager therefore holds the entry until the witness
answers. An emergency rotation after a key
compromise runs the same path the same day, as
[entity key revocation][entity-key-revocation] sets out.

## Publication {#ts-5-02-publication}

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-02-043 }**REQ-TS-5-02-043** The holder of a log MUST serve `did.jsonl` and `did-witness.json` at the addresses the method derives from its identifier, over HTTP with TLS.
- [](){ #req-ts-5-02-044 }**REQ-TS-5-02-044** `did.jsonl` MUST hold every entry from the first.
- [](){ #req-ts-5-02-045 }**REQ-TS-5-02-045** An entry once published MUST NOT be altered or removed.
- [](){ #req-ts-5-02-046 }**REQ-TS-5-02-046** The holder of a log MUST publish the witness proof of a new entry in `did-witness.json` before it publishes the entry in `did.jsonl`.
- [](){ #req-ts-5-02-047 }**REQ-TS-5-02-047** `did-witness.json` MUST carry, for each witness, the latest proof for a published entry.
- [](){ #req-ts-5-02-048 }**REQ-TS-5-02-048** `did-witness.json` MAY carry, for each witness, one more proof for an entry not yet published.
- [](){ #req-ts-5-02-049 }**REQ-TS-5-02-049** The holder of a log MUST serve `did.jsonl` as `text/jsonl` and `did-witness.json` as `application/json`.
- [](){ #req-ts-5-02-050 }**REQ-TS-5-02-050** The holder of a log MUST serve both files without authentication and without any identifier of the reader.
- [](){ #req-ts-5-02-051 }**REQ-TS-5-02-051** The holder of a log MUST NOT redirect a request for either file.

</div>

Nothing of the log is published on the central content delivery network
(CDN), as
[the DID Document is not on the central CDN][the-did-document-is-not-on-the-central-cdn]
explains. The order of the two files is the method's: a reader that finds
an entry without its proof refuses it, so [REQ-TS-5-02-046][req-ts-5-02-046]
has the proof published first.

## Resolving {#ts-5-02-resolving}

A reader works in two moments: the sync, outside any transaction, and the
read, inside one.

1. On the sync, the reader fetches `did.jsonl` and `did-witness.json` of
   every entity the trusted list names, from the entity's domain, or from
   DID Service's Resolver endpoint when the domain cannot be reached.
2. It replays each log from the first entry, verifying the chain, each
   proof, pre-rotation, and the witness proofs, and stores the DID Document
   versions it resolved.
3. On a read, it takes the key from the stored version in force at the time the
   signed object states, checks the relationship, checks the trusted list for a
   revoked key, and verifies the signature.
4. It never fetches a log in between.

A reader in this section is any of the four Modules that resolve an entity's
identifier: Issuer Core, Verifier Core, Mobile Wallet, and Mobile Verifier, each
through Trust SDK.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-02-052 }**REQ-TS-5-02-052** A reader MUST resolve a log by every step of the method's Read operation, for every entry.
- [](){ #req-ts-5-02-053 }**REQ-TS-5-02-053** A reader MUST NOT skip a check on an intermediate entry.
- [](){ #req-ts-5-02-054 }**REQ-TS-5-02-054** A reader MUST accept a witness proof only as [REQ-TS-5-01-077][req-ts-5-01-077] allows.
- [](){ #req-ts-5-02-055 }**REQ-TS-5-02-055** A reader MUST refuse an entry that carries no accepted witness proof on itself or on a later published entry.
- [](){ #req-ts-5-02-056 }**REQ-TS-5-02-056** A reader MUST refuse a log whose parameters differ from [the table of parameters][tbl-ts-5-02-parameters].
- [](){ #req-ts-5-02-057 }**REQ-TS-5-02-057** A reader MUST fetch every log it holds through the trust cache sync, from the entity's domain first and from DID Service's Resolver endpoint only when the domain cannot be reached or answers with an error.
- [](){ #req-ts-5-02-058 }**REQ-TS-5-02-058** A reader MUST verify a copy fetched from DID Service exactly as one fetched from the entity's domain.
- [](){ #req-ts-5-02-059 }**REQ-TS-5-02-059** A reader MUST NOT fetch a log during a transaction.
- [](){ #req-ts-5-02-060 }**REQ-TS-5-02-060** A reader MUST refuse a counterpart whose log it does not hold.
- [](){ #req-ts-5-02-061 }**REQ-TS-5-02-061** A reader MUST keep a log that neither source returned as its last-known-good copy until the tolerance limit the Governance Profile sets.
- [](){ #req-ts-5-02-062 }**REQ-TS-5-02-062** A reader MUST refuse a last-known-good copy past the tolerance limit.
- [](){ #req-ts-5-02-063 }**REQ-TS-5-02-063** A reader MUST NOT keep a log that failed verification.
- [](){ #req-ts-5-02-064 }**REQ-TS-5-02-064** A reader MUST resolve the `versionId` and `versionTime` resolution options as the method defines them.
- [](){ #req-ts-5-02-065 }**REQ-TS-5-02-065** A reader MUST verify a signature against a verification method of the DID Document version in force at the time the signed object states it was made.
- [](){ #req-ts-5-02-066 }**REQ-TS-5-02-066** A reader MUST accept a signature only when that version lists the key under the relationship the purpose needs.
- [](){ #req-ts-5-02-067 }**REQ-TS-5-02-067** A reader MUST refuse a signature made with a key the trusted list names in a revoked key service, as [REQ-TS-5-01-075][req-ts-5-01-075] requires, whatever version of the DID Document lists it.
- [](){ #req-ts-5-02-068 }**REQ-TS-5-02-068** A reader MUST apply the resolver transport rules of the method's security considerations when it fetches a log: no redirect followed, no address written as a raw Internet Protocol (IP) address or resolving to a private or loopback range, a size cap and a timeout on each fetch, and `https` only.

</div>

Verifying against the version in force at signing time lets a retired key go
on vouching for what it signed. A signed object states its time in its own
format, `iat` in a JSON Web Token (JWT) or the `created` of a Data Integrity
proof, and the format specifications name it for each; an mdoc is verified
through its certificate and never against a DID Document.

A key revoked early is refused whatever time the object claims, because a
thief can backdate, as
[what happens to the old key][what-happens-to-the-old-key] sets out.

Which checks run in which flow is in
[flows per use case](../architecture-framework/high-level-architecture/flows-per-use-case.md),
and the [trust cache sync][trust-cache-sync] is where the fetch and the
fallback happen.

## Trust Authority's own identifier {#ts-5-02-trust-authoritys-own-identifier}

Trust Authority holds a `did:webvh` of its own, maintained by the same
rules, so that the Accreditation Credential and the Use Statement it signs
carry an issuer a reader can resolve. Its witness is its own witness key, which
proves nothing about it. Its SCID anchors it instead, and every reader carries
that from build time, as
[Trust Authority's own keys][trust-authoritys-own-keys] sets out.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-02-069 }**REQ-TS-5-02-069** Trust Authority's log MUST follow every requirement of [The log][ts-5-02-the-log], [The DID Document][ts-5-02-the-did-document], and [Publication][ts-5-02-publication].
- [](){ #req-ts-5-02-070 }**REQ-TS-5-02-070** Trust Authority's DID Document MUST carry the seven keys [the table of keys by role][tbl-ts-5-02-keys-by-role] names for it, and no other.
- [](){ #req-ts-5-02-071 }**REQ-TS-5-02-071** Trust Authority's update key MUST be held in its HSM.
- [](){ #req-ts-5-02-072 }**REQ-TS-5-02-072** A reader MUST carry Trust Authority's SCID from build time.
- [](){ #req-ts-5-02-073 }**REQ-TS-5-02-073** A reader MUST verify a signature of Trust Authority only against a key that the log of that SCID resolves to.

</div>

## Security considerations {#ts-5-02-security-considerations}

- **A rewritten history.** An entry once published cannot be altered
  without breaking the hash chain, and no entry counts without the witness,
  [REQ-TS-5-02-045][req-ts-5-02-045] and [REQ-TS-5-02-054][req-ts-5-02-054], so an
  entity that controls its own web server still cannot rewrite its past
  unnoticed. The copy DID Service keeps, [REQ-TS-4-01-017][req-ts-4-01-017],
  and its monitoring, [REQ-TS-4-01-018][req-ts-4-01-018], detect the
  attempt.
- **A stolen update key.** Pre-rotation is always on,
  [REQ-TS-5-02-013][req-ts-5-02-013], so a thief cannot rotate to a key of
  their own, and a revoked update key witnesses nothing,
  [REQ-TS-4-01-008][req-ts-4-01-008]. An entry never commits to the update key
  it carries, [REQ-TS-5-02-074][req-ts-5-02-074], so the update key an entry
  reveals cannot sign the next one.
- **A stolen witness key.** The trusted list strikes it, and a reader
  counts its proofs only as [REQ-TS-5-02-054][req-ts-5-02-054] allows.
- **A domain taken over.** The SCID binds the identifier to its first
  entry, so a log forged at the same domain fails the SCID check,
  [REQ-TS-5-02-052][req-ts-5-02-052], and nothing on it signs without the update
  key and the witness.
- **A backdated signature.** A key revoked early is refused whatever time
  the object claims, [REQ-TS-5-02-067][req-ts-5-02-067].
- **A resolver used as a proxy.** The transport rules of
  [REQ-TS-5-02-068][req-ts-5-02-068] keep a reader from fetching from an address
  an attacker chose.
- **A forged Trust Authority.** Its SCID is carried from build time,
  [REQ-TS-5-02-072][req-ts-5-02-072], so no log at any domain can stand in for
  it.

## Privacy considerations {#ts-5-02-privacy-considerations}

A log carries an entity's public keys and nothing about any citizen. A
reader fetches every log through the trust cache sync and never one log at
the moment of a transaction, [REQ-TS-5-02-057][req-ts-5-02-057] and
[REQ-TS-5-02-059][req-ts-5-02-059], so neither an entity's domain nor DID
Service learns which citizen is dealing with which entity, and when. The
holder's identifier is not a `did:webvh`; what it exposes is in
[Deriving a did:key and a device identifier](deriving-a-did-key-and-a-device-identifier.md).

## Changelog {#ts-5-02-changelog}

<figure markdown="1" class="ekdn-table">

| Version | Date | Change |
|---|---|---|
| 1.0 draft | 21 October 2026 | First draft |

</figure>
