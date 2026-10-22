---
title: "Credential lifecycle"
description: What ends a credential's life early, from its own expiry and a revoked status list entry to a compromised signing key and a lost or replaced device.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §4.6, §7.7; Rincian Module dan Operasi, §8 siklus hidup kredensial (tracks/0157) -->

# Credential lifecycle {#credential-lifecycle}

A credential's lifetime is bounded by more than its own content. Three other
things can end it early: the status list entry attached to it, the key that
signed it, and the device that holds it. The four rules below set out how
each boundary works.

## Expiry and validity periods {#expiry-and-validity-periods}

A credential remains technically valid until its `exp` timestamp, unless it is
revoked earlier through
[status list checking][status-list-checking-and-revocation]. What signs the
credential, and what bounds that signer's own lifetime, differs by format.

ISO/IEC 18013-5:2021 caps the lifetime of the
[Document Signer Certificate][document-signer-certificate-verifier-issuing-ca-and-crl]
that signs a mobile driving license (mDL) at 457 days. That cap bounds the
moment of signing rather than the window the mdoc verifies for, because a reader
checks the signing time against the certificate and not the time it reads the
credential.

An SD-JWT-based Verifiable Credential (SD-JWT VC) draft -13 is
signed with the issuer's `issuance-jose` key, which no certificate wraps.

In every format a credential has a technical validity period, and it has an
administrative one where the document underneath it has one. The administrative
period is how long the credential is legally valid. It mirrors the underlying
document, and [the Credential Rulebook][the-credential-rulebook] for that
credential type names the law or issuing authority it comes from. A type whose
document is valid for life, as a KTP Digital is, carries no administrative
period, and its Rulebook names none. The technical period is how long one signed
copy verifies, the window that `exp` closes. The issuer chooses it within a
ceiling the Governance Profile sets, and never past the administrative period
where the type has one.

## Status list checking and revocation {#status-list-checking-and-revocation}

Each issuer hosts its own Status List Token on its own domain, rather than
behind a shared content delivery network (CDN). Hosting it this way keeps
Trust Infrastructure from learning how many credentials are in circulation
or tracking any one citizen's activity.

A credential's `issuance_record` points to the index that carries its
status in the issuer's [status list][status-list]. Each entry is two bits
wide, enough for the three states IETF Token Status List draft -14 defines: valid,
invalid, and suspended. To revoke the credential, the issuer's Status
Manager sets its entry to invalid and republishes the Status List Token, the
mechanism behind [citizen-initiated
revocation][citizen-initiated-revocation]. Revocation is final.

Suspension is not. The Status Manager sets an entry to suspended while a
doubt about the credential is being resolved, then back to valid or on to
invalid once it is. A verifier refuses a suspended credential as it refuses
a revoked one. For `ldp_vc`, W3C Bitstring Status List v1.0 carries the same
state as a second list, with the `suspension` purpose, beside the revocation
list.

Verifiers do not fetch
the token during a check: they read it from a cached copy, held for a
Time to Live (TTL) the Governance Profile sets for that kind of status list,
one value for every issuer and every credential type.

## Scheduled key rotation and blast radius {#scheduled-key-rotation-and-blast-radius}

A credential's lifecycle is tied to the key that signed it, the
Document Signer Certificate for an mdoc and `issuance-jose` for an SD-JWT VC or
an `ldp_vc`. If that signing key is compromised, every credential it signed has
to be revoked and reissued, the chain of events
[entity key revocation][entity-key-revocation] sets out in full.

Scheduled key rotation keeps that chain short. The more often an
issuer rotates its signing key, the fewer credentials share any one key, and
the fewer credentials an incident forces back through reissuance.

## Device migration and reissuance {#device-migration-and-reissuance}

The credential key is born inside the device's secure element and cannot be
exported or backed up. A citizen who loses or replaces their phone ends the
credential's life on that device, with nothing to carry over to the next
one.

[Device migration][device-migration] follows: the old wallet
installation is revoked under
[revoking an installation][gf-revoking-an-installation] and obtains no further
[Key Attestation][key-attestation], the citizen enrolls the new device, and the
credential is requested again from the issuer rather than restored from a
backup.

The presentation history does carry over. It holds no key and no
attribute value, only what each verifier signed and the outcome, so it goes into
the wallet's encrypted client-side backup. The wallet encrypts it on the device
and Wallet Backend Service stores the ciphertext; the citizen holds the key. On the
new device Mobile Wallet offers to restore the history and the citizen decides;
a restored history goes on from where it stopped.
