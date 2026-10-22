---
title: "Constraints, decisions, and targets"
description: The rules every implementation is held to and why, the software decisions that carry them, where data is kept and for how long, how each Module scales, the rules every Module shares, and the targets the system is measured against.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §8.3, §8.4, §8.5, §8.6, §8.7; Rincian Perangkat Lunak dan Deployment §1, §6, §7; Rincian Module dan Operasi §5.5, §7.5; Panduan mdoc §8.6. Kode K/T/D/V/A dari draft tidak dipakai karena T1–T6 sudah dipakai rantai transaksi -->

# Constraints, decisions, and targets {#constraints-decisions-and-targets}

The other chapters say what IDCTF is made of. This page says what an
implementation of it is held to. A reviewer judges a vendor's work against the
constraints below, and breaking one is an architectural defect. The decisions, the storage split, and the scaling strategy
carry those constraints into code, and the quality targets say how the result
is measured.

## Constraints binding implementations {#constraints-binding-implementations}

Each constraint is one rule and the reason for it. They fall into four groups:
the keys, the paths between Modules, the data a Module may keep, and what a
verification checks.

The keys:

<figure markdown="1" class="ekdn-table">

| Rule | Why |
|---|---|
| An entity signs only inside itself, through its Key Manager. Issuer Core never asks another party to sign for it | Non-repudiation, and no single party can sign on behalf of every entity |
| The credential key is born and destroyed in the secure element of the citizen's device | Device binding in ISO/IEC 18013-5 and the `cnf` claim of SD-JWT VC depend on it |
| Trust Authority holds no entity's private key | No single point can forge the whole ecosystem |
| Trust Authority's fourteen keys sit only in its own HSMs, never in an entity's Key Manager: each root in an offline HSM of its own, and the witness key in a separate partition | A compromise of an entity key, of one root, or of an online key does not reach the others |
| The device key and the credential key are two different keys | The key the vouching party knows never appears in a presentation |
| An mdoc issuer uses two keys, `issuance-jose` and `issuance-cose` | The Document Signer Certificate's validity, 457 days for an mDL, does not drag the key in the DID Document along with it |
| `x5chain` goes in the unprotected header of `COSE_Sign1` | ISO/IEC 18013-5 clause 9.1.2.4 puts it there. [RFC 9360][ref-rfc9360] permits it, because the certificate authority issues the Document Signer Certificate from a certification request and so has proof of possession of the key |
| A verifier never pins an issuer's Document Signer Certificate in its configuration. Its trust anchor is the Issuer Root CA | Every renewal of a pinned certificate would force every verifier to update |

</figure>

The paths between Modules:

<figure markdown="1" class="ekdn-table">

| Rule | Why |
|---|---|
| Verifier Core does not contact Issuer Core during verification | The citizen's privacy, and verification does not depend on the issuer being up |
| Issuer Core does not contact Wallet Backend Service during issuance | A Wallet Provider does not become a national point of failure |
| Trust Infrastructure is not on the transaction path | Verification keeps running while Trust Infrastructure is down |
| No console holds a database connection | One path for every change, a complete audit trail, and no race on the status list |
| Public endpoints and the Admin API sit on separate ingress | A smaller attack surface |

</figure>

The data a Module may keep:

<figure markdown="1" class="ekdn-table">

| Rule | Why |
|---|---|
| Issuer Core keeps neither claim contents nor whole credentials | IDCTF does not create a second population database |
| Verifier Core keeps no attribute it verified | Verification infrastructure is not a store of citizen data |
| A subject is stored as a pseudonym, salted per credential type | Two archives cannot be joined into one profile |
| Trust Infrastructure records no citizen transaction | Trust Infrastructure is not a surveillance system |
| Every table has a written retention policy | Nothing is kept by default |

</figure>

What a verification checks:

<figure markdown="1" class="ekdn-table">

| Rule | Why |
|---|---|
| An artifact's signature is checked each time it is read from cache | A poisoned cache is still caught |
| The entity chain and the transaction chain are both evaluated in full | Each chain closes a gap the other leaves open, as [entity chain and transaction chain][entity-chain-and-transaction-chain] explains |
| Trust anchors are built in at build time, never downloaded. A root the VICAL carries counts only once the VICAL verifies against a built-in root, and never checks the next VICAL | The chain of trust cannot loop back on itself |
| The wallet refuses a request for attributes outside the verifier's scope | The citizen is protected at the moment of the request, not only by a later audit |

</figure>

## Typical software decisions {#typical-software-decisions}

The constraints say what must not happen. These decisions shape the code so
that it does not.

<figure markdown="1" class="ekdn-table">

| Decision | Described in |
|---|---|
| Every server Module uses the same layers: Controller, then Domain, then Repository or Provider | [Layers inside a Module](layers-inside-a-module.md) |
| A Module that verifies a published trust artifact does so only through Trust SDK | [Trust SDK][sa-trust-sdk] |
| No console has a database connection | The paths between Modules |
| Sessions and nonces live in a shared Redis, not in process memory | [The stack][the-stack] |
| Trusted artifacts are static files behind a content delivery network | [Trusted list and cache][trusted-list-and-cache] |
| Claims Provider is an extension point, not a fixed Module | [Issuer Core][sa-issuer-core] |
| The Key Manager drivers (`software`, `cloudkms`, `hsm`) and Signing Provider are extension points | [PKCS#11][ref-pkcs11] and [KMIP][ref-kmip] |

</figure>

## Storage: sessions and archive {#storage-sessions-and-archive}

A Module keeps two kinds of data, and they are split by how long the data
lives.

<figure markdown="1" class="ekdn-table">

| Kind | Holds | Lives for | Technology |
|---|---|---|---|
| Hot, the session | Authorization codes, nonces, OpenID4VCI and OpenID4VP state | Seconds to minutes | Redis |
| Cold, the archive | `issuance_record`, `verification_record`, the status list | Years | PostgreSQL |

</figure>

The table that matters most is `issuance_record` in Issuer Core. It holds no
claim, no whole credential, and no plain Population Identification Number
(NIK). It holds enough to find which credentials have to be
revoked when a signing key leaks: the key that signed each one, and where its
status sits in the status list. Its columns are listed under
[Issuer Core][sa-issuer-core].

[Retention][gf-retention] is set by the Governance Framework, not left to each
institution. An `issuance_record` and its status list are kept at least as long
as the longest-lived credential plus a dispute period, because a leaked key
cannot be handled without them. A diploma never expires, so its archive never
closes: each signed copy's record is kept until that copy's technical validity
ends plus the dispute period, and renewal writes the next one. A
`verification_record` is kept for the period the Governance Profile sets, and
longer only where a law binding the Relying Party requires it. Sessions and
nonces last minutes.

## Scale and resilience {#scale-and-resilience}

<figure markdown="1" class="ekdn-table">

| Module | Strategy |
|---|---|
| Issuer Core, Verifier Core | Stateless and horizontal, with sessions in Redis |
| Trust Registry, DID Service | Mostly read, horizontal behind a content delivery network |
| DID Service witnessing | At least two replicas, all signing with the one witness key in its partition of Trust Authority's hardware security module (HSM) |
| Trust Authority | One instance is enough |

</figure>

Every cache in IDCTF is a requirement for resilience and privacy. It lets
verification run while Trust Infrastructure is down, and it keeps a citizen's
pattern of use from reaching Trust Infrastructure at all. Each cache
adds jitter to its refresh, so that caches expiring together do not all hit
the source in the same moment.

Witnessing is the one write DID Service takes. While it is down, entities
cannot onboard or rotate a key, and resolution and containment carry on, as
[Trust Infrastructure is not a role][trust-infrastructure-is-not-a-role]
sets out. A second replica shortens that outage without adding a witness:
`did:webvh` v1.0 counts one approval per witness `did:key` v0.9, so replicas that share
the witness key are still the one witness.

DID Service keeps no queue of entries waiting for it. When the witness cannot
be reached, Trust Authority returns the refusal, and the entity's Key Manager
Component keeps the signed entry and submits it again until a witness proof
comes back. Until then the entry is not published and the new key is not used.
This is the order `did:webvh` sets, where the controller collects the witness
proofs and publishes only once it holds them, and it is why the metric of
entries waiting for the witness is counted at the entity.

[Entity key revocation][entity-key-revocation] gives the rotation the same day.
An outage longer than that delays it, and nothing goes around the witness. The compromised key
stays revoked from the first hour, the entity's other keys keep working, and
the delay goes into the post-mortem the entity files at the end of the
incident.

## Rules every Module shares {#rules-every-module-shares}

<figure markdown="1" class="ekdn-table">

| Concern | Rule |
|---|---|
| Transport | TLS 1.3 to the outside, mutual TLS between internal Modules |
| Database rights | One database user per Module, with the least privilege it needs and none shared |
| Algorithms and protocol versions | Set by the Governance Profile, never chosen per implementation |
| Rate limits | On every public endpoint, and on `tx_code` against PIN guessing |
| Issuance failure | Data not found, data found but not yet eligible, and a source system that cannot be reached are three different answers, never one message: the first sends the citizen to the institution, the third only asks them to wait |
| Trust Registry and Trust Authority errors | Problem Details, RFC 9457 |
| Logs | Structured, and correlated by `txId` |
| Metrics | Issuance rate, verification rate, cache hit ratio, trusted list age, Key Manager driver latency, and `did:webvh` entries waiting for the witness |
| Tracing | OpenTelemetry, across the Modules of one entity |
| Audit | Kept apart from operational logs, with longer retention |
| Never logged | Private keys, claim contents, a plain NIK, a whole `vp_token`, the KEK, and the contents of the Key Manager's software keystore |
| Credential Rulebook | Frozen once published; a change is a new version |
| Module API | Semantic versioning. A breaking change takes a major version and a transition period |
| Trust SDK | Backward compatible for at least two major versions |
| Trusted list | Carries a version field, so a move to a new LoTE format does not force every verifier to update at once |
| Time | Every Module runs on UTC, synchronized by NTP. The one-day ceiling on a Key Attestation's `exp`, a short-lived `nonce`, the validity of a Verifier Device Certificate, and `StatusStartingTime` in the trusted list all depend on clocks that agree |

</figure>

## Quality targets {#quality-targets}

<figure markdown="1" class="ekdn-table">

| Attribute | Target | How it is measured |
|---|---|---|
| Verification while Trust Infrastructure is down | Still succeeds, up to the cache tolerance limit | A test that cuts access to Trust Registry |
| Issuance latency | Under 3 seconds at the 95th percentile, not counting the source system's time | The p95 metric |
| Verification latency from cache | Under 1 second at the 95th percentile | The p95 metric |
| Offline verification | Succeeds in airplane mode | A field test in airplane mode |
| Key revocation | An emergency trusted list is published within 1 hour | An incident drill |
| Witness availability | 99.5% over a rolling 90 days, and back within 4 hours of an outage | Uptime of the witness endpoint, and an incident drill |
| Dependency bans | Zero violations | An automated test in the pipeline |
| Key portability | An entity moves from a software keystore to an HSM without a change to Issuer Core's code | A migration test |

</figure>

The target for verification while Trust Infrastructure is down depends on
the tolerance limits the Governance Profile sets, one per cached artifact,
and [the trust path][the-trust-path] states what each of them bounds.
