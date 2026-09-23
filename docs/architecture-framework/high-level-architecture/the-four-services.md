---
title: The four Services
description: Issuer, Wallet, Verifier, and Trust Infrastructure, the roles that run each one, and the Modules they contain.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §2.3 -->

# 2. The four Services

A Service groups functions that belong together. A role runs a Service; a
Service contains Modules.

| Service | Roles that run it | Parties riding on it | How many | Modules |
|---|---|---|---|---|
| **Issuer Services** | Identity Issuer, Attribute Issuer | None; every issuer runs its own | Many | Issuer Core, Issuer Console |
| **Wallet Services** | Wallet Provider; the Mobile Wallet is installed by the citizen | None | Many | Mobile Wallet, Wallet Backend Service |
| **Verifier Services** | Relying Party, RP Intermediary | Merchants, registered by an RP Intermediary, using the Mobile Verifier | Many | Verifier Core, Verifier Console, Mobile Verifier |
| **Trust Infrastructure** | Root Authority; its portal is used by entities applying and by accredited ones | None | One | Trust Authority, Trust Registry, DID Service, KMS |

## 2.1 Trust Infrastructure is not a role

The first three Services are roles in a transaction. Trust Infrastructure is
not. It is the foundation that lets the other three be trusted, and it is never
on the transaction path. A credential is issued and verified without any call
reaching it, because the artifacts it publishes were downloaded and cached
beforehand.

That is what the *one* in its count column protects. A single Trust
Infrastructure is acceptable precisely because it is absent at the moment of
use. Were it on the transaction path, one national instance would be a single
point of failure for every verification in the country.

## 2.2 The counts are the design

Issuer Services, Wallet Services and Verifier Services are many: any accredited
entity runs its own, and the ecosystem scales by adding instances. A citizen
chooses among the wallets on offer, and an issuer accepts a Key Attestation from
any provider the trusted list carries. What stays single is Trust
Infrastructure, and the reason is that one of its jobs is to be the thing
everybody else agrees on. The wallet's protocol layer stays separable from its
interface for the same reason the counts run this way: it can be extracted as an
SDK, so a second provider builds on the implementation the first one proved
rather than starting over.

The Module-by-Module breakdown of each Service is in
[Section 4, Module map, components, and dependencies](module-map.md).
