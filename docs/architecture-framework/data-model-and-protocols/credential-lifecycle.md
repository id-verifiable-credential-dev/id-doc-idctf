---
title: "Credential lifecycle"
description: What ends a credential's life early, from its own expiry and a revoked status list entry to a compromised signing key and a lost or replaced device.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §4.6, §7.7 -->

# Credential lifecycle {#credential-lifecycle}

A credential's lifetime is bounded by more than its own content. Three other
things can end it early: the status list entry attached to it, the key that
signed it, and the device that holds it. The four rules below set out how
each boundary works.

## Expiry and validity periods {#expiry-and-validity-periods}

A credential remains valid until its `exp` timestamp, unless it is revoked
earlier through the status list checking described below. How long that
window runs depends on the format. mdoc is governed by ISO/IEC 18013-5, which
caps the lifetime of the [Document Signer
Certificate][document-signer-certificate-verifier-issuing-ca-and-crl] (DSC)
that signs a Mobile Driving License (mDL) at 457 days. SD-JWT VC carries no
such fixed ceiling: its validity period is set by [the Credential
Rulebook][the-credential-rulebook] for that credential type.

## Status list checking and revocation {#status-list-checking-and-revocation}

Each issuer hosts its own Status List Token on its own domain, rather than
behind a shared content delivery network (CDN). Hosting it this way keeps
Trust Infrastructure from learning how many credentials are in circulation
or tracking any one citizen's activity.

A credential's `issuance_record` points to the bit index that carries its
status in the issuer's [status list][status-list]. To revoke the credential,
the issuer's Status Manager flips that bit and republishes the
Status List Token, the mechanism behind [citizen-initiated
revocation][citizen-initiated-revocation]. Verifiers and wallets do not fetch
the token on every check: they read it from a cached copy, held for a
Time to Live (TTL) set by the credential's risk profile.

## Scheduled key rotation and blast radius {#scheduled-key-rotation-and-blast-radius}

A credential's lifecycle is tied to the Document Signer Certificate that
signed it. If that signing key is compromised, every credential it signed
has to be revoked and reissued, the chain of events [entity key
revocation][entity-key-revocation] sets out in full.

Scheduled key rotation is what keeps that chain short. The more often an
issuer rotates its signing key, the fewer credentials share any one key, and
the fewer credentials an incident forces back through reissuance.

## Device migration and reissuance {#device-migration-and-reissuance}

Holder keys are born inside the device's secure element and cannot be
exported or backed up. A citizen who loses or replaces their phone ends the
credential's life on that device, with nothing to carry over to the next
one.

What follows is [device migration][device-migration]: the old wallet
instance's [Key Attestation][key-attestation] is revoked, the citizen
registers the new device, and the credential is requested again from the
issuer rather than restored from a backup.
