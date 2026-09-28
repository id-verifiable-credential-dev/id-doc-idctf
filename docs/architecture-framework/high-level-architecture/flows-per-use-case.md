---
title: Flows per use case
description: The minimum path through each use case, from entity onboarding to key revocation, and which of them run without reaching Trust Infrastructure.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §7, Kep. 5, 9, 28; siklus hidup kredensial belum ada di draft -->

# 5. Flows per use case

Each flow below is the minimum path, not a complete protocol trace. The steps
name who acts and what they send, and stop where the
[Technical Specifications](../../technical-specifications/index.md) take over
with the wire format.

Three of them run without reaching Trust Infrastructure at all: credential
issuance, online verification, and offline verification each read what they
need from cache. That is
[Principle 1, The two paths never cross](index.md#1-the-two-paths-never-cross)
in operation rather than in principle.

## 5.1 Entity onboarding

Onboarding brings a new entity into the control plane, the step that has to
happen before the entity can sign anything on the transaction path. The entity
generates its own keys, and Trust Authority, DID Service, and Trust Registry
each play a distinct part in accepting them.

1. The entity sends `POST /entities` to Trust Authority, with its legal-entity
   documentation and a conformance test.
2. The entity's Key Manager generates `issuance-jose`, `issuance-cose`, and an
   Ed25519 update key, in whichever driver the entity uses: an encrypted
   software keystore by default, a cloud KMS, or an HSM.
3. The entity sends DID Service its genesis `did.jsonl`, a proof of possession
   for each key, and the `keyStorage` of the driver.
4. DID Service returns a witness proof signed with `eddsa-jcs-2022`.
5. The entity sends Trust Authority a CSR from the `issuance-cose` key, and
   Trust Authority returns a DSC for the mdoc path.
6. Trust Authority sends Trust Registry an Authority Statement, naming an
   action and a resource, together with the public keys and their
   `keyStorage`.
7. Trust Registry returns a new trusted list and an Accreditation Credential
   to the entity, and the entity publishes `did.jsonl` on its own domain.

Rotation follows the same path: a new log entry, signed with the current update
key and matching the pre-rotation hash, is witnessed before it counts. After
onboarding, the entity signs through its own Key Manager, and Trust
Infrastructure is not called once transactions start.

## 5.2 Credential issuance

This flow issues a credential to a citizen's wallet over [OpenID4VCI](../references.md#exchange-protocols), online.
Mobile Wallet, Wallet Backend Service, Issuer Core, and Claims Provider each
take part, and the trusted list is read from cache throughout.

1. Issuer Core sends a credential offer to Mobile Wallet, by QR code or
   deeplink.
2. Mobile Wallet sends `GET /.well-known/openid-credential-issuer` to
   Issuer Core, and reads `proof_types_supported` and
   `key_attestations_required` from the response.
3. Mobile Wallet sends PAR and PKCE to Issuer Core, then requests a
   token with the pre-authorized code, `tx_code`, and DPoP.
4. Mobile Wallet sends `POST /nonce` to Issuer Core.
5. Mobile Wallet takes its credential key, created inside the secure element
   at its first issuance and reused for every credential after, and obtains a
   platform attestation.
6. Mobile Wallet exchanges the platform attestation and the issuer's
   nonce with Wallet Backend Service.
7. Wallet Backend Service returns a Key Attestation, carrying `attested_keys`
   and `key_storage`.
8. Mobile Wallet sends `POST /credential` to Issuer Core, with
   `proofs.attestation`.
9. Issuer Core checks the trusted list for whether the Key Attestation's
   signer is listed there.
10. Issuer Core calls `getClaims(subjectRef, credentialType)` on Claims
    Provider.
11. Claims Provider returns the claims and a `data_as_of` value.
12. Issuer Core assembles an SD-JWT VC carrying `cnf`, and an mdoc carrying an
    MSO and a DeviceKey, and signs both locally.
13. Issuer Core returns the SD-JWT VC and the mdoc to Mobile Wallet.

`subjectRef` never arrives from the wallet. It comes from how the citizen was
authenticated: the citizen logs into an agency's own system, an officer
selects a record and creates the offer on the citizen's behalf, or the offer
chains from a credential the citizen already holds, with Issuer Core
verifying that credential (a KTP Digital) first. When the source system
answers slowly, issuance is deferred and Issuer Core returns a
`transaction_id` instead of the credential.

## 5.3 Online verification

This flow lets a Relying Party's own application verify a credential over
[OpenID4VP](../references.md#exchange-protocols), with Verifier Core mediating between it and Mobile Wallet. The
trusted list and the status list are both read from cache.

1. The RP application asks Verifier Core to run a verification, using a
   template.
2. Verifier Core sends an authorization request carrying DCQL to Mobile
   Wallet, with `client_id` set to the verifier's `did:webvh`, by QR
   code or deeplink.
3. Mobile Wallet resolves the `client_id` against the trusted list and
   checks the requested scope through TRQP, both from cache.
4. Mobile Wallet shows the citizen consent, for example that Bank XYZ is
   requesting confirmation of age over 17, and signs a Key Binding JWT over
   the nonce and the audience.
5. Mobile Wallet sends the `vp_token` to Verifier Core through
   `direct_post.jwt`.
6. Verifier Core runs Chain 1 against the trusted list: checks E1 through E4,
   from cache.
7. Verifier Core runs Chain 2 against the trusted list: T1 the signature, T2
   the status list, T3 the KB-JWT against `cnf`, T4 the nonce and audience,
   T5 the scope.
8. Verifier Core records the transaction ID and the consent receipt as T6,
   storing only the `vp_digest`.
9. Verifier Core returns an OpenID Connect or SAML session, carrying the
   attributes, to the RP application.

Verifier Core does not store the resulting attributes. Keeping them is the RP
application's responsibility.

## 5.4 Offline verification

This flow verifies a credential over [ISO/IEC 18013-5](../references.md#exchange-protocols), in proximity, between a
reader and Mobile Wallet. The reader is always a device: Mobile Verifier on a
merchant's phone or a Relying Party's counter device, or a Relying Party's own
app built on the Reader SDK. It is never Verifier Core. No network is reachable
during it at all.

1. The reader engages Mobile Wallet by QR code or NFC tap.
2. The reader and Mobile Wallet establish a session over BLE, using
   ephemeral ECDH.
3. The reader sends a request to Mobile Wallet, with ReaderAuth carrying
   its Verifier Device Certificate.
4. Mobile Wallet validates the certificate chain to Verifier Root CA
   from cache, and the citizen selects which attributes to release.
5. Mobile Wallet returns a DeviceResponse: the mdoc and DeviceAuth.
6. The reader validates IssuerAuth by chaining `x5chain` to Issuer Root CA
   (from cache), recomputes the digest, checks DeviceAuth against the
   SessionTranscript, and checks the status list (from cache).

Zero network calls happen during this flow. The status list and the trusted
list can both be stale by the time it runs; the tolerance limit, seven days
for example, is set by the Governance Framework. DeviceAuth is a
`deviceSignature`, following EUDI, which leaves `deviceMac` out of scope. The
consequence is that a presentation cannot be denied afterward: a verifier can
prove to a third party that the citizen presented.

## 5.5 Verification by a merchant

This flow lets a merchant verify a credential through Mobile Verifier,
standing in for the Verifier Core it does not run itself. Three parties take
part: Mobile Verifier on the merchant's own device, Verifier Core run by the
RP Intermediary that registered the merchant, and Mobile Wallet.

1. Mobile Verifier sends Verifier Core proof of possession of its
   device key and an integrity token, at provisioning and at every renewal.
2. Verifier Core returns a Verifier Device Certificate carrying the
   `ReaderAuthRole` extension and the device key. Its lifetime is set by the
   Governance Profile, and the RP Intermediary withdraws it early through a
   CRL.
3. Mobile Verifier leaves a Request Object with Verifier Core, signed with
   the device key and carrying that certificate as `x5c`, and shows Mobile
   Wallet a QR code whose `request_uri` points at Verifier Core.
4. Mobile Wallet fetches the Request Object and checks whether the chain
   reaches Verifier Root CA, whether the issuing CA is on the trusted list,
   whether the certificate hash matches the `client_id`, and whether the
   requested attributes are a subset of `ReaderAuthRole`.
5. Mobile Wallet sends the presentation to Verifier Core by `direct_post.jwt`,
   encrypted to the merchant's device key.
6. Verifier Core passes the ciphertext to Mobile Verifier and deletes it;
   Mobile Verifier decrypts and verifies on the device.

The key is born on the merchant's own device and signs there too. The RP
Intermediary's Verifier Core holds only the Request Object and the encrypted
response, for a short time and without logging them; it vouches for the
merchant but never sees the citizen's data. A merchant is registered, not
accredited.

## 5.6 Wallet registration and attestation

This flow registers a wallet installation with Wallet Backend Service and
keeps it supplied with a Key Attestation, drawing on the device's own OS or
chip and on CONNECTIDN.

1. Mobile Wallet logs into CONNECTIDN over OpenID Connect.
2. CONNECTIDN returns an `id_token`.
3. Mobile Wallet asks the OS to create a device key, produce a platform
   attestation, and return an integrity verdict.
4. Mobile Wallet registers the instance with Wallet Backend Service,
   sending the public key, the platform attestation, and the CONNECTIDN
   token.
5. Wallet Backend Service confirms the instance is active.
6. For every issuance after that, and at least once a day, Mobile Wallet sends
   Wallet Backend Service proof of possession of the device key, an integrity
   token, and the issuer's nonce.
7. Wallet Backend Service returns a new Key Attestation, or refuses if the
   device has been revoked.

Wallet Backend Service knows the account and the device. It knows neither the
credential, the issuer, nor the verifier. Replacing the phone means
re-issuance, because a hardware key cannot be backed up.

## 5.7 Entity key revocation

This flow runs when an entity's signing key is compromised, moving through
five phases from the freeze to the post-mortem.

| Phase | Target | Action |
|---|---|---|
| 1. Freeze | Under 1 hour | Trust Registry sets the entity's status to suspended and issues an emergency trusted list; Issuer Core stops issuing; verifiers are notified directly. |
| 2. Key revocation | Same day | The entity rotates the key at once through its Key Manager, with pre-rotation in `did:webvh` and Trust Authority's witness; the DSC is added to the CRL; the old key leaves `assertionMethod` without the entry being deleted; the witness refuses any new entry signed by the revoked key. |
| 3. Fate of credentials | No fixed target | Every credential signed with the compromised key is revoked: `issuance_record` points to that credential's index in the status list, and Status Manager sets the bit and republishes the Status List Token. Periodic key rotation limits how many credentials this reaches. |
| 4. Recovery | No fixed target | A new key and a new DSC are issued, status is set to granted, and affected credentials are reissued; the wallet can receive a push notice to update its credential. |
| 5. Afterward | No fixed target | A post-mortem is filed to the transparency log; the issuer's Key Manager driver is reviewed. |

Two things have to exist from phase 1 for this flow to run at all: an
`issuance_record` that records a `signing_key_ref` per credential, and a DID
Service that keeps history and holds two active keys at once. Scheduled key
rotation, a DSC valid at most 457 days for an mDL, decides how many
credentials get caught up when one key leaks: the more often a key rotates,
the fewer credentials need reissuing.

## 5.8 Credential lifecycle: expiry, reissuance, device change

<p class="ekdn-soon">(soon)</p>
