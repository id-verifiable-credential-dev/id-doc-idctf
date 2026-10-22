---
title: "Technology stack"
description: The language, database, cache, keystore, and policy engine behind each building block of a Module, which of those choices something else depends on, how each Module is packaged and shipped, and the four risks the stack carries.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §6 (Kep. 15, 16, 17), §6.2; Rincian Perangkat Lunak dan Deployment §3, §4, §5. Trust Authority satu image atas keputusan user (13 Oktober 2026), bukan dua seperti Rincian §3; tracks/0211, tracks/0407 -->

# Technology stack {#technology-stack}

Go for every server Module, React for every web application, Flutter for both
mobile applications, and one container image per Module. Those four decisions
settle most of the stack before a single Module is designed.

The Module Map describes what each Module is built as in generic terms, a
REST API or a web application, because the shape of a Module outlives the
technology that implements it. What that shape is built from is here, in one
table, so a later change of tooling touches one page rather than ten
entries.

## The stack {#the-stack}

[](){ #tbl-stack }

<figure markdown="1" class="ekdn-table">

| Building block | Where it applies | Technology | Why this one |
|---|---|---|---|
| REST API | Issuer Core, Verifier Core, Trust Registry, DID Service, Wallet Backend Service, Trust Authority's API | Go | A static binary in a small image, a mature `crypto/x509`, and [PKCS#11][ref-pkcs11] bindings that already exist |
| Web application | Issuer Console, Verifier Console, Trust Authority's portal | React | Widely known, so a team is easy to staff, and each console calls its Admin Controller, and the portal its Registrar Controller, and nothing else |
| Mobile application | Mobile Wallet, Mobile Verifier | Flutter, on Android and iOS | One codebase for two platforms. The secure element and the BLE session still need Kotlin and Swift plugins underneath |
| Library | [Trust SDK][sa-trust-sdk] | Go and Dart, two implementations | A server runtime and a mobile runtime share nothing, so the library is written twice and held together by shared test vectors |
| Extension point | Claims Provider | Follows Issuer Core, or anything the institution runs when it is deployed on its own | It reaches into a source system nobody in the ecosystem governs |
| Database | Every server Module | PostgreSQL | `jsonb` and `bytea` carry the record shapes these Modules store, and the engine is mature |
| Cache and session | Issuer Core, Verifier Core, Trust SDK on the server | Redis | A nonce issued by one instance has to be readable by the next, which is what lets these Modules scale sideways |
| Entity keys | Key Manager in Issuer Core, Verifier Core, and Wallet Backend Service; Trust Authority | An encrypted software keystore by default, a cloud KMS, or an HSM over [PKCS#11][ref-pkcs11]; P-256 and Ed25519. Trust Authority runs on an HSM and has no software option | The driver holding the transaction keys is recorded as `keyStorage`, and that value sets the entity's `issuer_assurance`; the Ed25519 update key may stay in the software keystore whatever the other keys use |
| Device keys | Mobile Wallet, Mobile Verifier | Android Keystore and StrongBox, iOS Secure Enclave | The key cannot be extracted, and the platform attests to where it lives |
| Storage on the device | Mobile Wallet | SQLCipher, keyed from the platform keystore | The credential store is encrypted at rest |
| Static artifacts | Trust Registry | Object storage behind a CDN | The trusted list, the Credential Rulebook, VICAL, and the Use Statement status list are files on the central CDN; a DID Document sits on the entity's own domain |
| Policy | Trust Evaluator | [OPA with Rego][ref-rego] | The entity chain, the transaction chain, and accreditation scope are written as rules rather than as branches in Go |

</figure>

## Three rows that are not preferences {#three-rows-that-are-not-preferences}

Most of [the stack][tbl-stack] could be decided again tomorrow
without anything
else moving. Three rows could not:

- **Redis is not a cache in the usual sense.** A nonce issued by one instance
  has to be readable by the next, because the request that carries it back may
  land anywhere. Take Redis out and Issuer Core and Verifier Core run as single
  instances, which is a scaling limit rather than a slower build.
- **The Trust SDK is written twice.** Go runs on the servers and Dart runs in
  the applications, and no runtime spans both. The pair is held together by a shared set of test vectors rather
  than by shared code, and [Trust SDK][sa-trust-sdk] names the six parts and
  the drift risk each one carries.
- **Where an entity keeps its keys is a governance fact, not an operations
  choice.** The three options behind Key Manager are not interchangeable: which
  one an entity uses is recorded as `keyStorage` when it registers a public
  key, and its `issuer_assurance` is read from that value. An entity
  that keeps its keys in the software keystore its own software ships with sits
  at the lowest one, which decides the credential types it can be authorized to
  issue rather than how fast it runs.

## Packaging and deployment {#packaging-and-deployment}

Each Module ships as one container image, never one image per Service. Issuer
Core faces the Internet and runs as many instances as its load needs; Issuer
Console sits in the internal zone and carries little load. Packing the two
together would pull the Console into the public zone, which the
[network zones][network-zones-and-placement] do not allow.

### Images {#images-per-module}

<figure markdown="1" class="ekdn-table">

| Image | Contents | Base image | Approximate size |
|---|---|---|---|
| `issuer-core` | A static Go binary | distroless | 20 MB |
| `issuer-console` | The React build | nginx-alpine | 30 MB |
| `claims-provider-<system>` | Optional, only when Claims Provider runs as a separate process | distroless | 20 MB |
| `verifier-core`, `verifier-console` | The same as the issuer pair | As the issuer pair | As the issuer pair |
| `wallet-backend-service` | A Go binary | distroless | 20 MB |
| `trust-authority` | A Go binary carrying its API, with the portal's React build embedded | distroless | As `issuer-core`, plus the portal build |
| `trust-registry`, `did-service` | A Go binary each | distroless | 20 MB each |

</figure>

Running in an image of its own does not make
Claims Provider a Module: it still belongs to Issuer Core, as
[Module Map](../high-level-architecture/module-map.md) says. Trust Authority is
one image holding both its API and its portal. The entity endpoint and the
portal answer in the public zone and the back office in the internal one, which
is [one application, two doors][one-application-two-doors] as for Issuer Core.
Placement is no reason to split them, and one image per Module holds for every
Module that ships one. The Go binary embeds the portal's React build and
serves it, so the image needs no web server and takes the same distroless base
as the other Go images.

Four of the things the pipeline builds are not container images:

<figure markdown="1" class="ekdn-table">

| Build output | Form |
|---|---|
| Mobile Wallet, Mobile Verifier | An Android App Bundle (AAB) and an iOS App Store Package (IPA) |
| Trust SDK for Go | A Go module |
| Trust SDK for Dart | A package on pub.dev, with a separate platform plugin for the secure element |
| Reader SDK | A package on pub.dev with BLE and NFC plugins, embedded in Mobile Verifier or in a Relying Party's own application |

</figure>

### Deployment profiles {#deployment-profiles}

Both profiles run the same images, and they differ in how those images are put together.

<figure markdown="1" class="ekdn-table">

| Profile | Shape | For whom |
|---|---|---|
| A, a small institution | Docker Compose: Issuer Core or Verifier Core, its Console, PostgreSQL, and Redis, with Claims Provider as a Component inside Issuer Core | A small issuer or a small Relying Party |
| B, national scale | Kubernetes, with autoscaling on Issuer Core or Verifier Core, Claims Provider as a separate process, and a managed database | An Identity Issuer, a large Relying Party, an RP Intermediary |

</figure>

Every issuer runs its own Issuer Core, for the reason given under
[Issuer Services][issuer-services].

### Placement rules {#placement-rules}

Four rules complete the [network zones][network-zones-and-placement].

- **Reports read from a replica.** Reporting queries go to a read replica,
  through a database user that can only read.
- **An entity's keys stay with the entity.** Key Manager and its driver run in
  the entity's own zone, and the key encryption key (KEK) of the software
  keystore never comes from the database it protects, as
  [where an entity key lives][where-an-entity-key-lives] sets out.
  Trust Authority receives a public key, a proof of possession, and a
  certificate request, and nothing more.
- **The source system is not opened.** Claims Provider enters the agency's
  closed network, and that network is never opened toward the ecosystem.
- **Claims Provider scales with its source.** How many instances it needs
  follows from how that source is integrated: read over REST, or
  replicated overnight, as on
  [Layers inside a Module](layers-inside-a-module.md).

### Configuration and release {#configuration-and-release}

<figure markdown="1" class="ekdn-table">

| Concern | Rule |
|---|---|
| Configuration | Environment variables, following the twelve-factor method, plus one mounted file for configuration with nested structure, such as a Cryptographic Provider profile |
| Secrets | From a secret manager, or from a file mounted at run time, such as a Docker Compose secret on deployment profile A. Never baked into an image, and never in an environment variable |
| Database migration | A separate job holding a lock, never run when the application starts, so that adding instances cannot start two migrations at once |
| Image version | Semantic versioning, per Module |
| Release train | One manifest of the Module versions tested together. It is needed because Trust SDK compatibility cuts across every Module |

</figure>

## Technology risks and mitigation {#technology-risks-and-mitigation}

Four risks come with the stack itself. Each has a mitigation that starts
before the choice it threatens is locked.

<figure markdown="1" class="ekdn-table">

| Risk | Mitigation |
|---|---|
| Go libraries for OpenID4VCI, OpenID4VP, SD-JWT VC, and mdoc are immature; the mature ones are written in Kotlin, Java, or Python | Credential Builder and Credential Verifier are split out as Go libraries of their own, and conformance tests run from the start |
| The secure element, Key Attestation, and BLE reach Flutter only through platform-specific plugins | A proof of concept of all three, on both platforms, before the decision is locked |
| Few did:webvh libraries in Go and Dart support [`eddsa-jcs-2022`][ref-vc-di-eddsa] | Evaluate the implementations registered with the Decentralized Identity Foundation (DIF), wrap the library inside Key Manager and the Trust SDK, and hold the two implementations together with shared test vectors |
| No JSON-LD 1.1 processor or RDFC-1.0 canonicalizer in Go or Dart appears in the W3C implementation reports, and none carries the complexity limit RDFC-1.0 requires against poison graphs | Run the W3C RDF canonicalization and Data Integrity ECDSA test suites against the chosen libraries in the pipeline, add the complexity limit where a library lacks one, and hold the two implementations together with shared test vectors |

</figure>
