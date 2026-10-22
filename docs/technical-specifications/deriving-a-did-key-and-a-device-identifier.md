---
title: "[TS-5-03] Deriving a did:key and a device identifier"
description: How every did:key in the ecosystem is formed and decoded, where each one appears, how a wallet derives the holder's identifier from its credential key, and how a device is identified by the thumbprint of its device key.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, Kep. 5, §3.4, §4.1, §4.2, §4.3, §5.7, §7.6, §9.2, §9.3; Rincian Module dan Operasi §6; Panduan mdoc §2.1; tracks/0243 -->

<p class="ekdn-docid">TS-5-03</p>

# Deriving a did:key and a device identifier {#ts-5-03-deriving-a-did-key-and-a-device-identifier}

<p class="ekdn-lead" markdown="span">
A `did:key` is a public key written as an identifier, with nothing to host and
nothing to resolve. The ecosystem uses it for the holder, for Trust Authority's
witness and signing keys, and for any key the trusted list names. A device is
identified by a hash of its key instead, so the key itself is never the
name.
</p>

Every sentence on this page binds every Module that writes or decodes a
`did:key`, and the four that hold or vouch for a device, and an Assessment Body
tests them against it in the version the Governance Profile puts in force. The
key words and the identifier `REQ-TS-5-03-nnn` follow
[Common provisions](common-provisions.md).

## Who runs this and what it needs {#ts-5-03-who-runs-this-and-what-it-needs}

This specification fixes the `did:key` and the device identifier:

- How a `did:key` is formed and decoded wherever the ecosystem uses one.
- Which keys are written that way.
- How Mobile Wallet derives the holder's identifier from its credential key.
- How a wallet installation or a verifier device is identified to the party
  that vouches for it.

Its conformance targets are:

- Every Module that writes a `did:key` or decodes one, which today means
  Trust Registry and Decentralized Identifier (DID) Service in Trust
  Infrastructure, the holders of a `did:webvh` log, and the four Modules
  that read trust artifacts through Trust SDK.
- For the holder and device identifiers, Mobile Wallet, Wallet Backend
  Service, Verifier Core, and Mobile Verifier.

It leaves to other documents:

- The `did:webvh` log in which a `did:key` names the update key and the
  witness, which
  [Publishing and resolving a did:webvh identifier](publishing-and-resolving-a-did-webvh-identifier.md)
  holds.
- The trusted list services that carry a `did:key`, which
  [Publishing and reading the trusted list](publishing-and-reading-the-trusted-list.md)
  holds.
- Where the holder's identifier appears inside a credential and a
  presentation, which
  [Issuing a credential in SD-JWT VC, mdoc, and `ldp_vc`](issuing-a-credential-in-sd-jwt-vc-mdoc-and-ldp-vc.md)
  and [Building and verifying a presentation](building-and-verifying-a-presentation.md)
  hold.
- The messages in which a device sends its identifier, which
  [Enrolling a wallet installation and attesting its key](enrolling-a-wallet-installation-and-attesting-its-key.md)
  and [Issuing and reading a Key Attestation](issuing-and-reading-a-key-attestation.md)
  hold.

Before the first exchange, each target holds what the rules below assume:
Mobile Wallet holds a credential key and a device key in its secure
element; Mobile Verifier holds a device key in its secure element; Wallet
Backend Service and Verifier Core hold the public key each device enrolled
with.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-03-001 }**REQ-TS-5-03-001** Every Module that writes a `did:key` or decodes one MUST meet every requirement in [Encoding][ts-5-03-encoding].
- [](){ #req-ts-5-03-002 }**REQ-TS-5-03-002** Mobile Wallet MUST meet every requirement in [The holder identifier][ts-5-03-the-holder-identifier].
- [](){ #req-ts-5-03-003 }**REQ-TS-5-03-003** Mobile Wallet, Mobile Verifier, Wallet Backend Service, and Verifier Core MUST each meet every requirement in [The device identifier][ts-5-03-the-device-identifier] that names it.

</div>

## What a did:key is {#ts-5-03-what-a-did-key-is}

[`did:key`][ref-did-key] v0.9 derives the whole identifier from one public key:
the key bytes, prefixed with the code of their type, encoded in base58btc
behind the `z` of Multibase. Whoever holds the key can write the identifier.
A `did:key` says which key, never whose, and the trusted list says whose.

## The did:key as written {#ts-5-03-the-did-key-as-written}

The keys are invented and no wallet has enrolled, but the three strings are
exact: each was produced by the encoding below from a real key of the named
type. The strings are:

- A holder's identifier from a P-256 credential key.
- Trust Authority's witness key from an Ed25519 key, the one
  [the log as published][ts-5-02-the-log-as-published] names in `witness` and
  [the trusted list][ts-5-01-trusted-list-payload] carries as Trust Authority's
  first witness.
- The DID URL that names the one verification method of a `did:key`, as a
  proof's `verificationMethod` and a witness `id` use it.

``` { .text title="Three did:key identifiers and one DID URL" data-format="DID" }
did:key:zDnaexUcd7ETfUxHRrCKpKq7tYbfJCH1AWNN5WDppWYj2RS7Q
did:key:z6MkrGRs1p2FjsQsxJtKwmaUotzGtjmjcvM7uKcnXU7ffLKe
did:key:z6MkrGRs1p2FjsQsxJtKwmaUotzGtjmjcvM7uKcnXU7ffLKe#z6MkrGRs1p2FjsQsxJtKwmaUotzGtjmjcvM7uKcnXU7ffLKe
```

## Encoding {#ts-5-03-encoding}

A `did:key` is the Multikey encoding of [W3C Controlled Identifiers 1.0][ref-cid]
behind the `did:key:` prefix. The two key types the ecosystem uses give the
two prefixes [the table of key types][tbl-ts-5-03-key-types] lists; no
other type appears in a `did:key` here.

[](){ #tbl-ts-5-03-key-types }

<figure markdown="1" class="ekdn-table">

| Key type | Multicodec header | Key bytes | Identifier starts with | Used for |
|---|---|---|---|---|
| P-256 | `0x8024`, the varint of `0x1200` | 33, compressed point | `did:key:zDn` | The holder identifier; the trusted list signing key; a revoked transaction key named on the trusted list |
| Ed25519 | `0xed01`, the varint of `0xed` | 32 | `did:key:z6Mk` | The witness key; the update key in a log entry's proof |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-03-004 }**REQ-TS-5-03-004** A `did:key` MUST be formed as [did:key][ref-did-key] defines it: `did:key:` followed by the base58btc Multibase encoding, with the `z` prefix, of the multicodec header and the public key bytes.
- [](){ #req-ts-5-03-005 }**REQ-TS-5-03-005** The key inside a `did:key` MUST be a P-256 key or an Ed25519 key, encoded as [the table of key types][tbl-ts-5-03-key-types] gives.
- [](){ #req-ts-5-03-006 }**REQ-TS-5-03-006** A DID URL that names the verification method of a `did:key` MUST be the identifier followed by `#` and the same Multibase value, byte for byte.
- [](){ #req-ts-5-03-007 }**REQ-TS-5-03-007** A Module MUST decode a `did:key` locally, from the key inside it.
- [](){ #req-ts-5-03-008 }**REQ-TS-5-03-008** A Module MUST NOT resolve a `did:key` over the network or look it up in any keystore.
- [](){ #req-ts-5-03-009 }**REQ-TS-5-03-009** A Module MUST reject a `did:key` whose key type is neither of the two, or a DID URL whose fragment differs from its body.
- [](){ #req-ts-5-03-010 }**REQ-TS-5-03-010** A Module that compares two keys MUST compare their `did:key` strings after encoding each the same way.

</div>

The fragment check is the one [did:webvh v1.0][ref-did-webvh] requires of a
witness: the body defines the key and the fragment names it, so a fragment
that differs would let a proof claim one key while signing with another.

## Where a did:key appears {#ts-5-03-where-a-did-key-appears}

[The table of uses][tbl-ts-5-03-uses] names every place the ecosystem writes
a `did:key`, and the specification that fixes that place.

[](){ #tbl-ts-5-03-uses }

<figure markdown="1" class="ekdn-table">

| Where | Which key | Fixed by |
|---|---|---|
| The holder's identifier, in `credentialSubject.id` of an `ldp_vc` credential and in the presentation that carries it | The credential key | This specification, and the credential format specifications for the field it sits in |
| A witness service on the trusted list, and the `witness` parameter of every log | The witness key | [Publishing and reading the trusted list](publishing-and-reading-the-trusted-list.md), [Publishing and resolving a did:webvh identifier](publishing-and-resolving-a-did-webvh-identifier.md) |
| A trusted list signer service, and the `kid` of the list's JWS | The trusted list key | [Publishing and reading the trusted list](publishing-and-reading-the-trusted-list.md) |
| An entry of `signers` in the Governance Profile, and the `kid` of its JWS | The Governance Profile key | [Publishing and reading the Governance Profile](publishing-and-reading-the-governance-profile.md) |
| A revoked key service | A DID Document key revoked early | [Publishing and reading the trusted list](publishing-and-reading-the-trusted-list.md) |
| The `verificationMethod` of a log entry's proof | The update key | [Publishing and resolving a did:webvh identifier](publishing-and-resolving-a-did-webvh-identifier.md) |
| The `verificationMethod` of a witness proof | The witness key | [Witnessing a log entry and serving its copy](witnessing-a-log-entry-and-serving-its-copy.md) |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-03-011 }**REQ-TS-5-03-011** A Module MUST write a key in each place [the table of uses][tbl-ts-5-03-uses] names as a `did:key` formed under [Encoding][ts-5-03-encoding], and in no other form.

</div>

The credential key is also written where
[the table of uses][tbl-ts-5-03-uses] does not reach, in the form each
credential format's own standard fixes for holder binding. An
SD-JWT-based Verifiable Credential (SD-JWT VC) carries it as a JSON Web Key in
`cnf.jwk`, as [SD-JWT VC draft -13][ref-i-d-ietf-oauth-sd-jwt-vc] defines. An
mdoc carries it as a CBOR Object Signing and Encryption (COSE) key in
`deviceKeyInfo.deviceKey` of the Mobile Security Object, as
[ISO/IEC 18013-5:2021][ref-iso-18013-5] defines. Neither place holds an
identifier, so neither takes a `did:key`; all three forms carry the same key.

## The holder identifier {#ts-5-03-the-holder-identifier}

A citizen's wallet installation holds one credential key, generated in the
secure element at the citizen's first login, and its `did:key` is the
holder's identifier for every credential the installation holds, as
[holder: one did:key per wallet installation][holder-one-didkey-per-wallet-installation]
sets out. The correlation that one identifier allows between two verifiers
is accepted there.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-03-012 }**REQ-TS-5-03-012** Mobile Wallet MUST derive the holder's identifier as the `did:key` of its credential key, a P-256 key.
- [](){ #req-ts-5-03-013 }**REQ-TS-5-03-013** Mobile Wallet MUST bind every credential it holds, whatever its format, to the same credential key.
- [](){ #req-ts-5-03-014 }**REQ-TS-5-03-014** Mobile Wallet MUST NOT derive a holder identifier from its device key.

</div>

## The device identifier {#ts-5-03-the-device-identifier}

A wallet installation and a verifier device each hold a device key in the secure
element, beside the credential key on a wallet. Each is known to the party that
vouches for it by the [RFC 7638][ref-rfc7638] thumbprint of that key:
Wallet Backend Service for a wallet, Verifier Core for a Mobile Verifier, as
[devices][devices] sets out.

The three parts are:

- The device key of the Android wallet installation that
  [Enrolling a wallet installation and attesting its key](enrolling-a-wallet-installation-and-attesting-its-key.md)
  enrolls, written as a JSON Web Key.
- The canonical JSON the thumbprint hashes: the members `crv`, `kty`, `x`,
  and `y` in lexicographic order, without whitespace.
- The SHA-256 hash of that string, base64url encoded, which is the
  `installation` that [the installation record][ts-2-01-the-installation-record]
  carries.

``` { .text title="A device key and its device identifier" data-format="JWK" }
{
  "kty": "EC",
  "crv": "P-256",
  "x": "94rg-4VtzLsCnokXp72epEl2qybQMWJrg5pX-gfICu4",
  "y": "ZEhnwu4lH0vyvOvGZtXevhuALd9S2JLu6GwNlUmA1-U"
}

{"crv":"P-256","kty":"EC","x":"94rg-4VtzLsCnokXp72epEl2qybQMWJrg5pX-gfICu4","y":"ZEhnwu4lH0vyvOvGZtXevhuALd9S2JLu6GwNlUmA1-U"}

KrCmnBrdPMJHuRg9i5S0mWRagm8mkS-fJrdlvaKLfII
```

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-03-015 }**REQ-TS-5-03-015** Mobile Wallet MUST identify its installation, and Mobile Verifier its device, to the party that vouches for it by the [RFC 7638][ref-rfc7638] thumbprint of the device key, computed with SHA-256.
- [](){ #req-ts-5-03-016 }**REQ-TS-5-03-016** Mobile Wallet and Mobile Verifier MUST NOT send the device key itself as an identifier.
- [](){ #req-ts-5-03-017 }**REQ-TS-5-03-017** Wallet Backend Service and Verifier Core MUST compute the identifier of a device the same way, from the public key the device enrolled with.

</div>

## Security considerations {#ts-5-03-security-considerations}

- **A key that is not whose it claims.** A `did:key` proves possession of
  nothing and belongs to nobody; what makes a witness key or a signing key
  trusted is the trusted list naming it, and what makes a holder's key
  bound is the credential's holder binding. This specification fixes only
  the form, and [REQ-TS-5-03-008][req-ts-5-03-008] keeps a Module from
  treating a `did:key` as something it can look up.
- **A proof that names one key and signs with another.** A Module rejects
  a fragment that differs from the body, [REQ-TS-5-03-009][req-ts-5-03-009].
- **A key of an unexpected type.** Only P-256 and Ed25519 are decoded,
  [REQ-TS-5-03-005][req-ts-5-03-005] and [REQ-TS-5-03-009][req-ts-5-03-009],
  so a Module never verifies against a curve the ecosystem did not choose.
- **A device impersonated from its identifier.** The thumbprint gives an
  attacker nothing to sign with, [REQ-TS-5-03-016][req-ts-5-03-016].

## Privacy considerations {#ts-5-03-privacy-considerations}

The holder's identifier is one `did:key` for every credential,
[REQ-TS-5-03-013][req-ts-5-03-013], which lets two verifiers match a holder
by comparing notes without reading a disclosed attribute. The architecture
accepts that exposure and [the holder identifier][holder-one-didkey-per-wallet-installation]
names it. A device identifier is a hash that only the vouching party ever
receives, [REQ-TS-5-03-015][req-ts-5-03-015]; it appears in no credential
and in no presentation.

## Changelog {#ts-5-03-changelog}

<figure markdown="1" class="ekdn-table">

| Version | Date | Change |
|---|---|---|
| 1.0 draft | 21 October 2026 | First draft |

</figure>
