---
title: The transaction path and the trust path
description: How the eleven Modules divide into a data plane, a control plane, and an operations layer, and what passes between them.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §3 (pengantar dan diagram), Kep. 12 -->

# 3. The transaction path and the trust path

Four Services, eleven Modules. The separation that shapes everything else is
between the transaction path, which is the data plane, and the trust path,
which is the control plane. They do not meet at runtime.
[Section 1.1](design-principles.md#11-the-transaction-path-and-the-trust-path-never-cross)
states that as a principle. This page is the mechanism: which Module sits on
which plane, what each plane is allowed to carry, and what passes between them.

A third group falls out of the same split and is easy to miss, because it is
neither. Issuer Console, Verifier Console, and Wallet Backend Service configure
and vouch for the parties on the transaction path without ever issuing or
verifying anything themselves. They are the operations layer.

| Plane | Modules | What it does |
|---|---|---|
| Transaction path (data plane) | Issuer Core, Mobile Wallet, Verifier Core, Verifier Application | Issues and presents credentials |
| Trust path (control plane) | Trust Authority, Trust Registry, DID Service, KMS | Decides who is trusted, and publishes the answer |
| Operations layer | Issuer Console, Verifier Console, Wallet Backend Service | Configures an entity's own Module, and vouches for its devices |

## 3.1 The transaction path

Three protocol exchanges carry every credential in the ecosystem, and there are
no others.

| From | To | Protocol |
|---|---|---|
| Issuer Core | Mobile Wallet | OpenID4VCI |
| Mobile Wallet | Verifier Core | OpenID4VP for online, ISO 18013-5 for proximity |
| Mobile Wallet | Verifier Application | OpenID4VP for online, ISO 18013-5 for proximity |

The wallet is the only Module that appears on both sides. It receives from an
issuer and presents to a verifier, and nothing moves between an issuer and a
verifier directly. That absence is deliberate and is the third of the three
statements in [Section 3.4](#34-the-only-thing-that-crosses-is-a-static-file).

Both verifier Modules appear because they are alternatives, not stages. An
accredited relying party runs Verifier Core and receives presentations at its own
endpoint. A merchant has no server and runs Verifier Application on a device
instead. The credential and the protocol are the same in both cases; what
differs is who holds the reader.

## 3.2 The trust path

Trust Authority drives the other three Trust Infrastructure Modules and nothing
else. It tells Trust Registry what to publish, DID Service which entity
identifiers to create and resolve, and KMS which keys to generate, rotate, or
revoke. The direction is one way in a second sense too: no Module in Trust
Infrastructure ever calls a Module outside it, and none of them calls an entity
back.

This is why the plane can be one instance nationally without being a single
point of failure. It is absent at the moment of use, so its availability is not
the ecosystem's availability. The four call prohibitions that hold the line,
including the one forbidding Trust Infrastructure from reaching outward, are in
[Section 4.2, Who may call whom](module-map.md).

## 3.3 The operations layer

Three Modules configure and vouch. None of them issues a credential or verifies
one, and each is reached differently from the Module it serves.

Issuer Console and Verifier Console are web applications used by staff inside
an entity. Each reaches its own Core through that Core's Admin API and through
nothing else, with no database connection of its own. An operator configures
credential types, onboards merchants, sets `allowed_attrs`, revokes, and reads
reports, and every one of those actions travels the same documented API that
any other client would use.

Wallet Backend Service does something different. It vouches. It issues a Key
Attestation to each Mobile Wallet daily, binds the installation to its
device, and can revoke that device. It holds no credentials, which is the point:
it can disown a wallet without being able to read what the wallet carries.
Verifier Core plays the same vouching role toward Verifier Application, issuing
each merchant device a Verifier Device Certificate whose lifetime the
Governance Profile sets.

On the wallet side the daily cadence is itself the revocation mechanism. An
installation that stops being reissued stops working when its current
attestation expires, with no revocation list to distribute and no message that
has to arrive. A merchant certificate lives longer than a day, so it is
withdrawn the ordinary X.509 way instead: the operator publishes a CRL, and a
reader checks its cached copy.

## 3.4 The only thing that crosses is a static file

The two planes are connected by published files, read from a cache, and by
nothing else.

| Artifact | Published by | Read by |
|---|---|---|
| Trusted list, Credential Rulebook, VICAL | Trust Registry, through a CDN | Issuer Core, Mobile Wallet, Verifier Core, Verifier Application |
| DID Documents | DID Service, through a CDN | The same four |
| Status list | Each issuer, hosted by that issuer | Verifier Core, Verifier Application |

Two properties follow, and they are the first two of the three statements the
architecture makes about this split.

Trust Infrastructure is not on the transaction path. Every artifact a
transaction needs was fetched and cached before the transaction began, so a
verification that starts while Trust Infrastructure is unreachable still
completes. Issuance and verification continue from cache until the tolerance
limit expires, and the limit is a policy decision rather than a network
condition. The targets are in
[Quality goals](../software-architecture/quality-targets.md) and the
tolerance is set by the
[Governance Framework](../../governance-framework/index.md).

The status list is published by the issuer, not by the centre. Revocation data
scales with the number of issuers rather than accumulating in one national
service, and it survives a central outage because it never lived there. It is
also the third statement in disguise: the only connection an issuer has to a
verifier is a static file that the verifier fetches. The two never speak.
