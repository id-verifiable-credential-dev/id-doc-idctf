---
title: "Technology choices per layer"
description: The language, database, cache, key store, and policy engine behind each layer of a Module, and which of those choices something else depends on.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §6 (Kep. 15, 16, 17) -->

# 8. Technology choices per layer

Go for every service, React for every console, Flutter for both applications,
and one container image per Module. Those four decisions settle most of the
stack before a single Module is designed.

This page is where the product names live. The Module Map describes what each
Module is built as in generic terms, a REST API or a web application, because
the shape of a Module outlives the technology that implements it. What that
shape is built from is here, in one table, so a later change of tooling touches
one page rather than ten entries.

## 8.1 The stack, layer by layer

| Layer | Where it applies | Technology | Why this one |
|---|---|---|---|
| Service and API | Issuer Core, Verifier Core, Trust Registry, DID Service, Wallet Backend Service, Trust Authority's API | Go | A static binary in a small image, a mature `crypto/x509`, and [PKCS#11](../references.md#key-storage-interfaces) bindings that already exist |
| Web application | Issuer Console, Verifier Console, Trust Authority's portal | React | Widely known, so a team is easy to staff, and each console calls its Admin Controller and nothing else |
| Mobile application | Mobile Wallet, Mobile Verifier | Flutter, on Android and iOS | One codebase for two platforms. The secure element and the BLE session still need Kotlin and Swift plugins underneath |
| Library | [Trust SDK](components-inside-a-module.md#25-trust-sdk) | Go and Dart, two implementations | A server runtime and a mobile runtime share nothing, so the library is written twice and held together by shared test vectors |
| Extension point | Claims Provider | Follows Issuer Core, or anything the institution runs when it is deployed as a separate service | It reaches into a source system nobody in the ecosystem governs |
| Database | Every server Module | PostgreSQL | `jsonb` and `bytea` carry the record shapes these Modules store, and the engine is mature |
| Cache and session | Issuer Core, Verifier Core, Trust SDK on the server | Redis | A nonce issued by one instance has to be readable by the next, which is what lets these Modules scale sideways |
| Entity keys | Key Manager in Issuer Core, Verifier Core, and Wallet Backend Service; Trust Authority | An encrypted software keystore by default, a cloud KMS, or an HSM over [PKCS#11](../references.md#key-storage-interfaces); P-256 and Ed25519. Trust Authority runs on an HSM and has no software option | Whichever is used is recorded as `keyStorage`, and that value sets the entity's `issuer_assurance` |
| Device keys | Mobile Wallet, Mobile Verifier | Android Keystore and StrongBox, iOS Secure Enclave | The key cannot be extracted, and the platform attests to where it lives |
| Storage on the device | Mobile Wallet | SQLCipher, keyed from the platform keystore | The credential store is encrypted at rest |
| Static artifacts | Trust Registry, DID Service | Object storage behind a CDN | The trusted list, the Credential Rulebook, and VICAL are files on the central CDN; a DID Document sits on the entity's own domain |
| Policy | Trust Evaluator | [OPA with Rego](../references.md#schema-display-and-policy) | The entity chain, the transaction chain, and accreditation scope are written as rules rather than as branches in Go |

## 8.2 Three rows that are not preferences

Most of the table could be decided again tomorrow without anything else
moving. Three rows could not.

**Redis is not a cache in the usual sense.** A nonce issued by one instance
has to be readable by the next, because the request that carries it back may
land anywhere. Take Redis out and Issuer Core and Verifier Core run as single
instances, which is a scaling limit rather than a slower build.

**The Trust SDK is written twice because nothing lets it be written once.**
Go runs on the servers and Dart runs in the applications, and no runtime spans
both. The pair is held together by a shared set of test vectors rather than by
shared code, and
[Section 2.5, Trust SDK](components-inside-a-module.md#25-trust-sdk) names the
six parts and the drift risk each one carries.

**Where an entity keeps its keys is a governance fact, not an operations
choice.** The three options behind Key Manager are not interchangeable: which
one an entity uses is recorded as `keyStorage` when it registers a public key,
and that value is what its `issuer_assurance` is read from. An entity that
keeps its keys in the software keystore its own software ships with sits at the
lowest one, which decides the credential types it can be authorized to issue
rather than how fast it runs.
