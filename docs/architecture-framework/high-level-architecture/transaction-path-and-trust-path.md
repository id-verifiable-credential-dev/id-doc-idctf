---
title: The transaction path and the trust path
description: How the ten Modules divide into a data plane, a control plane, and an operations group, and what passes between them.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §3 (pengantar dan diagram), §4.6, Kep. 9, 12, 28, 30; tracks/0169 (fallback log DID ke DID Service, tidak ada di sumber); tracks/0382 (Governance Profile di band Artifacts) -->

# The transaction path and the trust path {#the-transaction-path-and-the-trust-path}

Four Services, ten Modules. The separation that shapes everything else is
between the transaction path, which is the data plane, and the trust path,
which is the control plane. They do not meet at runtime, which the chapter overview
states as the design principle
[the two paths never cross][the-two-paths-never-cross]. This page is the
mechanism: which Module sits on which plane, what each plane is allowed to
carry, and what passes between them.

A third group falls out of the same split and is easy to miss, because it is
neither. Issuer Console, Verifier Console, and Wallet Backend Service configure
and vouch for the parties on the transaction path without ever issuing or
verifying anything themselves. They are the operations group.

<figure markdown="1" class="ekdn-table">

| Plane | Modules | What it does |
|---|---|---|
| Transaction path (data plane) | Issuer Core, Mobile Wallet, Verifier Core, Mobile Verifier | Issues and presents credentials |
| Trust path (control plane) | Trust Authority, Trust Registry, DID Service | Records who is trusted, and publishes the answer |
| Operations group | Issuer Console, Verifier Console, Wallet Backend Service | Configures an entity's own Module, and vouches for its devices |

</figure>

[](){ #fig-planes-and-artifact-lane }

<figure markdown="1" class="ekdn-fig-wide">
  ![The two planes, the operations group, and the artifacts between them](../../images/architecture-framework/high-level-architecture/transaction-and-trust-path.svg){ loading=lazy }
  <figcaption><span class="ekdn-fignum"></span> The trust path, the band Artifacts, the transaction path, and the operations group.</figcaption>
</figure>

[The diagram of the two planes][fig-planes-and-artifact-lane] reads downward,
and each of its four bands has a section:
[the trust path][the-trust-path], the band Artifacts in
[what connects the two planes][what-connects-the-two-planes],
[the transaction path][the-transaction-path], and
[the operations group][the-operations-group].

The band Artifacts draws the eight artifacts that settle a question before a
transaction runs. Six are fetched from an address and cached, which is what its
dashed arrows mean; one is answered over Trust Registry Query
Protocol (TRQP) v2.0 rather than published as a file; and one, the Use Statement, is
carried by the verifier inside the request itself. Six more are never fetched at
all, traveling with a party or with a message instead. All fourteen are in
[Artifacts exchanged](../data-model-and-protocols/artifacts-exchanged.md).

## The transaction path {#the-transaction-path}

Three protocol exchanges carry every credential in the ecosystem, and there are
no others.

<figure markdown="1" class="ekdn-table">

| From | To | Protocol |
|---|---|---|
| Issuer Core | Mobile Wallet | [OpenID4VCI][ref-openid4vci] |
| Mobile Wallet | Verifier Core | [OpenID4VP][ref-openid4vp], online only |
| Mobile Wallet | Mobile Verifier | OpenID4VP for online, relayed by the RP Intermediary's Verifier Core; [ISO/IEC 18013-5][ref-iso-18013-5] for proximity |

</figure>

The wallet is the only Module that appears on both sides. It receives from an
issuer and presents to a verifier, and nothing moves between an issuer and a
verifier directly. That absence is deliberate and is the third of the three
statements in [what connects the two planes][what-connects-the-two-planes].

Both verifier Modules appear because each covers a different setting. Verifier
Core receives a presentation online, at the Relying Party's own endpoint.
Mobile Verifier reads on a device, online or in proximity: a merchant with no
server uses it, and so does a Relying Party at its counter. Online, a merchant's
device leaves its signed request with the RP Intermediary's Verifier Core and
collects the encrypted response from it, and Verifier Core passes both along
without opening them. Proximity reading happens on the device alone, in Mobile
Verifier or in a Relying Party's own application built on the Reader SDK, so an offline
check makes no network call on either side.

## The trust path {#the-trust-path}

Trust Authority drives the other two Trust Infrastructure Modules and nothing
else. It tells Trust Registry what to publish, while Decentralized Identifier (DID) Service witnesses every
entry an entity adds to its own identifier log using the witness key held in a
separate partition of Trust Authority's hardware security module (HSM). The keys themselves are generated
and held by each entity; Trust Infrastructure receives only public keys and
certificate requests. The direction is one way in a second sense too: no Module in Trust
Infrastructure ever calls a Module outside it, and none of them calls an entity
back.

One call runs the other way. Issuer Core, Verifier Core and Wallet Backend
Service each call Trust Authority only to register or rotate their own keys,
never during a transaction, and Trust Authority hands the entry to DID Service
for its witness; they read DID Service from cache and never submit to it. That
call is the only one that enters the trust path, from the transaction path or
the operations group, and it is stated for each of the three in
[who may call whom][who-may-call-whom].

This is why the plane can be one instance nationally without being a single
point of failure. It is absent at the moment of use, so its availability is not
the ecosystem's availability. The four call prohibitions that hold the line,
including the one forbidding Trust Infrastructure from reaching outward, are in
[who may call whom][who-may-call-whom].

## The operations group {#the-operations-group}

Three Modules configure and vouch. None of them issues a credential or verifies
one, and each is reached differently from the Module it serves.

Issuer Console and Verifier Console are web applications used by staff inside
an entity. Each reaches its own Core through that Core's Admin API and through
nothing else, with no database connection of its own. An operator configures
credential types, onboards merchants, sets `allowed_attrs`, revokes, and reads
reports, and every one of those actions travels the same documented API that
any other client would use.

Wallet Backend Service does something different. It vouches. It issues a Key
Attestation to a Mobile Wallet before each issuance, binds the installation
to its device, and can revoke that device. It holds no credentials, which is the point:
it can disown a wallet without being able to read what the wallet carries.
Verifier Core does the same vouching toward Mobile Verifier. It issues a
Verifier Device Certificate to each device it answers for, a merchant's or the
Relying Party's own counter device, and the Governance Profile sets how long
that certificate lives. Provisioning and every renewal hand over both at once:
the certificate, and, for a merchant, the [Use Statements][use-statement] for
the business categories its device is bound to.

Each of these two artifacts has three parties rather than two. Wallet Backend
Service issues a Key Attestation, Mobile Wallet carries it, and Issuer Core
reads it before issuing a credential that demands one. Verifier Core issues a
Verifier Device Certificate, Mobile Verifier carries it, and Mobile Wallet
reads it before releasing an attribute to that device.

On the wallet side the refusal to mint is itself the revocation mechanism, and
it reaches issuance alone. An attestation is minted for one issuance and lives
a day at most, so an installation the Wallet Provider has disowned obtains no
further credential from its next issuance on, with no revocation list to
distribute and no message that has to arrive. The credentials it already
holds go on being presented, because no verifier reads a Key Attestation, and
reaching those is the issuer's job through its status list. A merchant
certificate lives longer than a day, so it is
withdrawn the ordinary [X.509][ref-rfc5280]
way instead: the intermediary publishes a certificate revocation list (CRL),
and the wallet checks its cached copy.

## What connects the two planes {#what-connects-the-two-planes}

The two planes are connected by published artifacts, by one query, and by one
artifact a verifier carries into the transaction itself. All three are settled
before a transaction begins, so nothing reaches across while a credential is
being issued or verified.

Eight artifacts carry that connection, and they are the ones drawn in the
band Artifacts of [the diagram of the two planes][fig-planes-and-artifact-lane].
Each does the same job in a different form: it settles a question the trust path
decided earlier, so that no Module has to call the trust path to ask.

- The trusted list, published by Trust Registry to a central content delivery
  network (CDN), tells a Module that the party in front of it is accredited at
  all. It is the one cached copy with a hard expiry: past the `NextUpdate` it
  carries, the copy is discarded and the transaction stops. See [Trusted
  list][trusted-list].
- The Credential Rulebook, from the same CDN, is why an issuer and a verifier
  that have never spoken agree on what a credential of a given type contains.
  See [Credential
  Rulebook][credential-rulebook].
- Verified Issuer Certificate Authority List (VICAL), from the same CDN, lets an
  offline verifier accept an issuer it has never met with the network switched
  off, which is the hardest case this chapter has to serve. See
  [VICAL][vical].
- The DID Document, signed by the entity and witnessed by DID Service, served
  by the entity itself, with DID Service's copy as the sync's fallback,
  turns a signature into proof that a named entity made it. See [DID
  Document][did-document].
- The status list, published by each issuer at its own domain, is the only
  thing that ever passes from an issuer to a verifier, and it is a file rather
  than a call, which is what keeps the two from speaking. See [Status
  list][status-list].
- The Authority Statement is published nowhere at all. It is the query. See
  [Authority
  Statement][authority-statement].
- The Use Statement is published nowhere either, and it is not a query. The
  verifier carries it in the request it sends, so a wallet reads an approved
  purpose out of the message already in front of it; only the status list that
  withdraws one sits on the central CDN. See [Use
  Statement][use-statement].
- The Governance Profile, from the central CDN like the trusted list, carries
  the numbers and algorithms the Root Authority set and the address of
  everything Trust Infrastructure serves, so every check on the transaction
  path runs on values decided on the trust path. See [Governance
  Profile][governance-profile].

No artifact on the central CDN carries citizen data.

Two of the eight are not files a participant fetches, and they fail differently for
it. The Authority Statement is the query: a participant asks Trust Registry over
[TRQP][ref-trqp] whether a given party may do a given thing, on its
[trust cache sync][trust-cache-sync], and caches the answer like everything else, so a permission check survives an unreachable registry exactly
as a cached file does. The Use Statement is neither fetched nor asked for; it
arrives inside the request, which is what lets a wallet check an approved purpose
without Trust Infrastructure learning that the transaction happened. What each covers, and
how one is granted, is in [Authorization][authorization] and
[Registered use][registered-use].

What each of the eight contains, and the six further artifacts that nobody
publishes to an address at all, are in
[Artifacts exchanged](../data-model-and-protocols/artifacts-exchanged.md).

Two properties follow, and they are the first two of the three statements the
architecture makes about this split.

Trust Infrastructure is not on the transaction path. Every artifact a
transaction needs was fetched and cached before the transaction began, so a
verification that starts while Trust Infrastructure is unreachable still
completes. Issuance and verification continue from cache until the tolerance
limit expires, and the limit is a policy decision rather than a network
condition. The targets are in
[quality targets][quality-targets], and the tolerance
belongs to the
Governance Profile.

Every limit is set for the pilot: the Governance Profile carries one
tolerance for each cached artifact, a TRQP answer, the catalog, a status list,
a CRL, the VICAL, an Authority Statement and a `did:webvh` log, and
[constraints on the values of the Governance Profile][gf-constraints-on-the-governance-profile]
keeps each of them inside the trusted list horizon. A cache with no stated
ceiling would be a cache that never ages out, which is why no artifact is
read without one, and why a claim that a transaction survives an outage is
true for exactly as long as the number says.

What the limit bounds is how long a revocation can go unseen. The notice that
goes with an emergency trusted list reaches a Relying Party within the hour,
and the list reaches every cache at its next sync. A device
verifying in proximity learns of it only at its next successful sync, and a
device that cannot sync keeps working from its copy until that copy expires:
the trusted list at its `NextUpdate`, every other cached artifact at the
tolerance limit. That expiry sets the longest a revoked key can still be
accepted face to face, and the one-hour response does not shorten it. [Whoever sets the number][gf-constraints-on-the-governance-profile] is setting that exposure. A limit longer than a credential type
can bear leaves the emergency response reaching only the verifiers that are
online.

Keeping the status list off Trust Infrastructure also keeps a count off it: were revocation data
collected nationally, Trust Infrastructure would know how many credentials are
in circulation. The third statement follows from it. The only connection an
issuer has to a verifier is a static file that the verifier fetches, so the two
never speak.
