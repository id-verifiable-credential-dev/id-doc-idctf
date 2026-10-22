---
title: "[TS-5-08] Issuing and reading a Key Attestation"
description: The Key Attestation Wallet Backend Service issues for a wallet installation's credential key, what it states about the storage that key sits in, the signature on it, how it is carried to an issuer, and the checks Issuer Core runs before it issues anything.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, Kep. 26, §5.5, §7.6; Bentuk Data Attestation §1, §2; JWT di OpenID4VCI dan OpenID4VP §0, §3, §4; Rincian Module dan Operasi §6, §8 -->

<p class="ekdn-docid">TS-5-08</p>

# Issuing and reading a Key Attestation {#ts-5-08-issuing-and-reading-a-key-attestation}

<p class="ekdn-lead" markdown="span">
A Key Attestation is what a Wallet Provider says about one wallet
installation's credential key: it sits in storage of a stated strength, and the
installation is still entitled to use it. It lives at most a day, nobody
revokes it, and only an issuer ever reads one.
</p>

Every sentence on this page binds Wallet Backend Service, which issues the
attestation, Mobile Wallet, which obtains and carries it, and Issuer Core,
which reads it before it issues anything, and an Assessment Body tests them
against it in the version the Governance Profile puts in force. The key words
and the identifier `REQ-TS-5-08-nnn` follow
[Common provisions](common-provisions.md).

## Who runs this and what it needs {#ts-5-08-who-runs-this-and-what-it-needs}

This specification fixes the Key Attestation:

- The claims it carries.
- Which key it covers.
- What its resistance values mean.
- The signature the Wallet Provider puts on it.
- How long it is good for.
- How it reaches an issuer inside a credential request.
- What Issuer Core checks before it acts on one.

Its conformance targets are Wallet Backend Service, which decides whether to
issue one and signs it; Mobile Wallet, which asks for one and carries it; and
Issuer Core, which validates one at every issuance.

It leaves to other documents:

- The request a wallet sends its own Wallet Backend Service to enroll an
  installation and to obtain an attestation, which is internal to a
  Wallet Provider and which
  [Enrolling a wallet installation and attesting its key](enrolling-a-wallet-installation-and-attesting-its-key.md)
  holds.
- The credential request as a whole, its authorization, and the metadata an
  issuer publishes, which
  [Issuing a credential via OpenID4VCI](issuing-a-credential-via-openid4vci.md)
  holds, this page fixing only the proof object that carries the attestation
  and the checks an issuer runs on it.
- Which storage a credential type demands, which the Credential Rulebook of
  that type holds through `min_assurance`.
- The mapping from an assurance level to the resistance values an issuer
  announces, which the Governance Profile holds.
- The form of the identifiers a device and a holder are known by, which
  [Deriving a did:key and a device identifier](deriving-a-did-key-and-a-device-identifier.md)
  holds.
- The keys of a Wallet Provider and the log they live in, which
  [Publishing and resolving a did:webvh identifier](publishing-and-resolving-a-did-webvh-identifier.md)
  holds.
- The entry that says a Wallet Provider is accredited, which
  [Publishing and reading the trusted list](publishing-and-reading-the-trusted-list.md)
  holds.

Before the first issuance, each target holds what the rules below assume:

- **Wallet Backend Service** holds the registry of the installations it
  vouches for, with the device key each enrolled with and whether it is
  revoked; holds the Key Attestation key; and publishes the matching public key
  in the Wallet Provider's Decentralized Identifier (DID) Document.
- **Mobile Wallet** holds one credential key and one device key in the device's
  secure element, and the attestation platform its operating system issued for
  the credential key.
- **Issuer Core** holds a cached copy of the trusted list, publishes a Nonce
  Endpoint, and announces the resistance values it requires for each credential
  type in the `key_attestations_required` metadata of that credential
  configuration.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-08-001 }**REQ-TS-5-08-001** Wallet Backend Service MUST meet every requirement on this page that names Wallet Backend Service, and every requirement on what Wallet Backend Service writes: the Key Attestation, with its header, its claims, and its signature.
- [](){ #req-ts-5-08-002 }**REQ-TS-5-08-002** Mobile Wallet MUST meet every requirement on this page that names Mobile Wallet, and every requirement on what Mobile Wallet writes: the `jwt` proof it builds.
- [](){ #req-ts-5-08-003 }**REQ-TS-5-08-003** Issuer Core MUST meet every requirement on this page that names Issuer Core.

</div>

## What the attestation states {#ts-5-08-what-the-attestation-states}

A Key Attestation answers one question an issuer has before it signs anything:
is the key this credential will be bound to held where the Wallet Provider says
it is held, and is this installation still one the Wallet Provider stands behind. It
says nothing about the citizen, nothing about the credential, and nothing about
what the data in that credential will be.

The evidence behind it stays with the Wallet Provider. A wallet shows its
Wallet Backend Service an attestation platform, the chain the chip or the
operating system issues for a key it generated, and Wallet Backend Service
checks that chain and its own record of the installation. An issuer never sees
the chain: it reads one artifact in one format, as
[two assurance levels](../architecture-framework/trust-model/two-assurance-levels.md)
sets out.

On iOS the platform attests no key but the App Attest key. The
attestation platform of the credential key is therefore the App Attest
attestation that commits to the key's thumbprint. The official build it shows
running stands behind where the key sits and what releases it, as
[Enrolling a wallet installation and attesting its key](enrolling-a-wallet-installation-and-attesting-its-key.md)
fixes.

Every issuance demands one, whatever the credential type,
[REQ-TS-5-08-059][req-ts-5-08-059]. What the Credential Rulebook of a type
sets through `min_assurance` is the storage the attestation reports,
[REQ-TS-5-08-028][req-ts-5-08-028], not whether an attestation is asked for.

An attestation is never revoked. It expires a day after it was issued at the
latest, and an installation the Wallet Provider has disowned obtains no
further one, so
nothing has to be distributed and no message has to arrive. Expiry reaches
issuance alone: no verifier reads a Key Attestation, so a credential already on
the device goes on being presented until the issuer's status list says
otherwise.

## Key Attestations as issued {#ts-5-08-key-attestations-as-issued}

The attestation below is an illustration: the Wallet Provider, the issuer, the
installation, and the keys are invented, and no wallet has enrolled. Every field
is exact. It was signed with the Key Attestation key of the Wallet Provider DID
its `iss` names, and the signature verifies.

The attestation agrees with the other examples on two points:

- The Wallet Provider is the one
  [the trusted list][ts-5-01-trusted-list-payload] carries, with the same DID.
- The key it attests is the credential key whose holder identifier
  [Deriving a did:key and a device identifier](deriving-a-did-key-and-a-device-identifier.md)
  publishes.

``` { .text title="A Key Attestation, in compact serialization" data-format="JWT" }
eyJ0eXAiOiJrZXktYXR0ZXN0YXRpb24rand0IiwiYWxnIjoiRVMyNTYiLCJraWQiOiJkaWQ6d2Vidmg6UW1lVFcxMzRxalVDNkVLWFU2SkwzZFZSZ2QzZlltVXBNYm9vRURva1NwRkVBSDpkb21wZXQuY28uaWQja2V5LWF0dGVzdGF0aW9uLTEifQ.eyJpc3MiOiJkaWQ6d2Vidmg6UW1lVFcxMzRxalVDNkVLWFU2SkwzZFZSZ2QzZlltVXBNYm9vRURva1NwRkVBSDpkb21wZXQuY28uaWQiLCJhdHRlc3RlZF9rZXlzIjpbeyJrdHkiOiJFQyIsImNydiI6IlAtMjU2IiwieCI6IjNDT2h4T2VPeHBCT2pVSmdxV1NBVTBRQUFZYVlndWdQVkpfMlgycUdka2MiLCJ5IjoiMms5ODg1NHBCNzd1ZGRSdmU4TzRrZzVuSVBUN0VqRWdwYmVLcVdMdU1FRSJ9XSwia2V5X3N0b3JhZ2UiOlsiaXNvXzE4MDQ1X2hpZ2giXSwidXNlcl9hdXRoZW50aWNhdGlvbiI6WyJpc29fMTgwNDVfbW9kZXJhdGUiXSwiY2VydGlmaWNhdGlvbiI6Imh0dHBzOi8vZG9tcGV0LmNvLmlkL2NlcnRpZmljYXRpb24vc2UtMjAyNi1hIiwibm9uY2UiOiJrUTh2WjJtSDdyVDEiLCJpYXQiOjE3OTIyMTY4MDAsImV4cCI6MTc5MjMwMzIwMH0.BRkIkIMHv2WPNC4VfRpDPDF7pIKl2TYfdevTxxJH4kBB4FBaLvfYd0JRbwDd76u_l7uMQ-7mtlI-sbkksgvvDA
```

Its header and its claims, decoded:

``` { .json title="Key Attestation header" data-format="JSON" }
{
  "typ": "key-attestation+jwt",
  "alg": "ES256",
  "kid": "did:webvh:QmeTW134qjUC6EKXU6JL3dVRgd3fYmUpMbooEDokSpFEAH:dompet.co.id#key-attestation-1"
}
```

``` { .json title="Key Attestation claims" data-format="JSON" }
{
  "iss": "did:webvh:QmeTW134qjUC6EKXU6JL3dVRgd3fYmUpMbooEDokSpFEAH:dompet.co.id",
  "attested_keys": [
    {
      "kty": "EC",
      "crv": "P-256",
      "x": "3COhxOeOxpBOjUJgqWSAU0QAAYaYgugPVJ_2X2qGdkc",
      "y": "2k98854pB77uddRve8O4kg5nIPT7EjEgpbeKqWLuMEE"
    }
  ],
  "key_storage": [
    "iso_18045_high"
  ],
  "user_authentication": [
    "iso_18045_moderate"
  ],
  "certification": "https://dompet.co.id/certification/se-2026-a",
  "nonce": "kQ8vZ2mH7rT1",
  "iat": 1792216800,
  "exp": 1792303200
}
```

The same attestation appears inside the header of a key proof, the second of
the two ways it reaches an issuer. The proof goes to the issuer of the Kartu
ASN, a type whose Rulebook sets `substantial`: an issuer at `high`
accepts the `attestation` proof type alone, as
[the mapping][tbl-min-assurance-mapping] sets out. The wallet obtained its
access token through anonymous access to the token endpoint in the
Pre-Authorized Code flow, so the proof carries no `iss`, as
[REQ-TS-5-08-074][req-ts-5-08-074] allows. The proof is signed by the
credential key the attestation covers, and `key_attestation` carries the
attestation of
[Key Attestations as issued][ts-5-08-key-attestations-as-issued] unchanged:

``` { .text title="A key proof carrying the attestation in its header" data-format="JWT" }
eyJ0eXAiOiJvcGVuaWQ0dmNpLXByb29mK2p3dCIsImFsZyI6IkVTMjU2IiwiandrIjp7Imt0eSI6IkVDIiwiY3J2IjoiUC0yNTYiLCJ4IjoiM0NPaHhPZU94cEJPalVKZ3FXU0FVMFFBQVlhWWd1Z1BWSl8yWDJxR2RrYyIsInkiOiIyazk4ODU0cEI3N3VkZFJ2ZThPNGtnNW5JUFQ3RWpFZ3BiZUtxV0x1TUVFIn0sImtleV9hdHRlc3RhdGlvbiI6ImV5SjBlWEFpT2lKclpYa3RZWFIwWlhOMFlYUnBiMjRyYW5kMElpd2lZV3huSWpvaVJWTXlOVFlpTENKcmFXUWlPaUprYVdRNmQyVmlkbWc2VVcxbFZGY3hNelJ4YWxWRE5rVkxXRlUyU2t3elpGWlNaMlF6WmxsdFZYQk5ZbTl2UlVSdmExTndSa1ZCU0Rwa2IyMXdaWFF1WTI4dWFXUWphMlY1TFdGMGRHVnpkR0YwYVc5dUxURWlmUS5leUpwYzNNaU9pSmthV1E2ZDJWaWRtZzZVVzFsVkZjeE16UnhhbFZETmtWTFdGVTJTa3d6WkZaU1oyUXpabGx0VlhCTlltOXZSVVJ2YTFOd1JrVkJTRHBrYjIxd1pYUXVZMjh1YVdRaUxDSmhkSFJsYzNSbFpGOXJaWGx6SWpwYmV5SnJkSGtpT2lKRlF5SXNJbU55ZGlJNklsQXRNalUySWl3aWVDSTZJak5EVDJoNFQyVlBlSEJDVDJwVlNtZHhWMU5CVlRCUlFVRlpZVmxuZFdkUVZrcGZNbGd5Y1Vka2EyTWlMQ0o1SWpvaU1tczVPRGcxTkhCQ056ZDFaR1JTZG1VNFR6UnJaelZ1U1ZCVU4wVnFSV2R3WW1WTGNWZE1kVTFGUlNKOVhTd2lhMlY1WDNOMGIzSmhaMlVpT2xzaWFYTnZYekU0TURRMVgyaHBaMmdpWFN3aWRYTmxjbDloZFhSb1pXNTBhV05oZEdsdmJpSTZXeUpwYzI5Zk1UZ3dORFZmYlc5a1pYSmhkR1VpWFN3aVkyVnlkR2xtYVdOaGRHbHZiaUk2SW1oMGRIQnpPaTh2Wkc5dGNHVjBMbU52TG1sa0wyTmxjblJwWm1sallYUnBiMjR2YzJVdE1qQXlOaTFoSWl3aWJtOXVZMlVpT2lKclVUaDJXakp0U0RkeVZERWlMQ0pwWVhRaU9qRTNPVEl5TVRZNE1EQXNJbVY0Y0NJNk1UYzVNak13TXpJd01IMC5CUmtJa0lNSHYyV1BOQzRWZlJwRFBERjdwSUtsMlRZZmRldlR4eEpINGtCQjRGQmFMdmZZZDBKUmJ3RGQ3NnVfbDd1TVEtN210bEktc2Jra3NndnZEQSJ9.eyJhdWQiOiJodHRwczovL2lzc3Vlci5ia24uZ28uaWQiLCJpYXQiOjE3OTIyMTY4MDUsIm5vbmNlIjoia1E4dloybUg3clQxIn0.KedVy6MjilzJ8yHTA70rs9lgrrVJDp2SwSv6_IH9GsMSBImEwU7HfkfVuBAXWCizv2CeL-8cJ4-63DcYzdnrEg
```

``` { .json title="Key proof header, with the attestation abbreviated" data-format="JSON" }
{
  "typ": "openid4vci-proof+jwt",
  "alg": "ES256",
  "jwk": {
    "kty": "EC",
    "crv": "P-256",
    "x": "3COhxOeOxpBOjUJgqWSAU0QAAYaYgugPVJ_2X2qGdkc",
    "y": "2k98854pB77uddRve8O4kg5nIPT7EjEgpbeKqWLuMEE"
  },
  "key_attestation": "eyJ0eXAiOiJrZXktYXR0ZXN0YXRpb24rand0Iiwi..."
}
```

``` { .json title="Key proof claims" data-format="JSON" }
{
  "aud": "https://issuer.bkn.go.id",
  "iat": 1792216805,
  "nonce": "kQ8vZ2mH7rT1"
}
```

The same attestation travels as the `attestation` proof type, in the `proofs`
member of the credential request:

``` { .json title="The attestation as the proof itself, abbreviated" data-format="JSON" }
{
  "proofs": {
    "attestation": [
      "eyJ0eXAiOiJrZXktYXR0ZXN0YXRpb24rand0IiwiYWxnIjoiRVMyNTYiLCJr..."
    ]
  }
}
```

## Format {#ts-5-08-format}

A Key Attestation takes the JSON Web Token (JWT) form Appendix D.1 of
[OpenID4VCI 1.0][ref-openid4vci] defines for one: a JSON Web Signature in compact
serialization as [RFC 7515][ref-rfc7515] defines it, over a claims set as
[RFC 7519][ref-rfc7519] defines it.

[](){ #tbl-ts-5-08-claims }

<figure markdown="1" class="ekdn-table">

| Claim | Type | Presence | What it carries |
|---|---|---|---|
| `iss` | string | Present | The `did:webvh` of the Wallet Provider whose Wallet Backend Service issued the attestation |
| `attested_keys` | array of objects | Present | The installation's credential key, as a JSON Web Key |
| `key_storage` | array of strings | Present | The attack resistance of the storage that key sits in |
| `user_authentication` | array of strings | Present | The attack resistance of the user authentication that releases it |
| `certification` | string | Present where a value above `iso_18045_enhanced-basic` is reported | The address of the evaluation the reported values rest on |
| `nonce` | string | Present | The nonce the issuer handed the wallet for this issuance |
| `iat` | number | Present | The moment the attestation was issued |
| `exp` | number | Present | The moment it expires, a day after `iat` at the latest |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-08-004 }**REQ-TS-5-08-004** A Key Attestation MUST be a JSON Web Signature in compact serialization.
- [](){ #req-ts-5-08-005 }**REQ-TS-5-08-005** The `typ` header parameter MUST be `key-attestation+jwt`.
- [](){ #req-ts-5-08-006 }**REQ-TS-5-08-006** The `alg` header parameter MUST be one the Governance Profile allows for the Key Attestation key.
- [](){ #req-ts-5-08-007 }**REQ-TS-5-08-007** *Withdrawn: [REQ-TS-01-033][req-ts-01-033] covers it.*
- [](){ #req-ts-5-08-008 }**REQ-TS-5-08-008** The `kid` header parameter MUST name a key of the purpose `key-attestation`, as [Naming the key][ts-01-naming-the-key] of TS-01 requires.
- [](){ #req-ts-5-08-009 }**REQ-TS-5-08-009** *Withdrawn: [REQ-TS-01-004][req-ts-01-004] covers it.*
- [](){ #req-ts-5-08-010 }**REQ-TS-5-08-010** Wallet Backend Service MUST include every claim [the table of claims][tbl-ts-5-08-claims] lists.
- [](){ #req-ts-5-08-011 }**REQ-TS-5-08-011** Wallet Backend Service MUST NOT include a claim [the table of claims][tbl-ts-5-08-claims] does not list.
- [](){ #req-ts-5-08-012 }**REQ-TS-5-08-012** `iss` MUST be the `did:webvh` of the Wallet Provider that runs the Wallet Backend Service.
- [](){ #req-ts-5-08-013 }**REQ-TS-5-08-013** Issuer Core MUST refuse an attestation whose `typ` is not `key-attestation+jwt`.
- [](){ #req-ts-5-08-078 }**REQ-TS-5-08-078** *Withdrawn: [REQ-TS-01-014][req-ts-01-014] covers it.*
- [](){ #req-ts-5-08-014 }**REQ-TS-5-08-014** Issuer Core MUST ignore a claim [the table of claims][tbl-ts-5-08-claims] does not list.
- [](){ #req-ts-5-08-079 }**REQ-TS-5-08-079** Issuer Core MUST NOT refuse an attestation for carrying a claim [the table of claims][tbl-ts-5-08-claims] does not list.

</div>

## What it covers {#ts-5-08-what-it-covers}

A wallet installation holds one credential key, and every credential it carries
is bound to that key, so an attestation covers exactly one key. The batch form
Appendix D.1 allows, one attestation over many keys from the same storage, has
no instance here.

The holder identifier an issuer binds the credential to is the `did:key` of
that credential key, as
[Deriving a did:key and a device identifier](deriving-a-did-key-and-a-device-identifier.md)
fixes.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-08-015 }**REQ-TS-5-08-015** `attested_keys` MUST carry exactly one key.
- [](){ #req-ts-5-08-016 }**REQ-TS-5-08-016** That key MUST be the credential key of the wallet installation the attestation is issued to.
- [](){ #req-ts-5-08-017 }**REQ-TS-5-08-017** That key MUST be a P-256 key, written as a JSON Web Key with `kty`, `crv`, `x`, and `y` and no other member.
- [](){ #req-ts-5-08-018 }**REQ-TS-5-08-018** Wallet Backend Service MUST NOT attest a key it has not seen an attestation platform for.
- [](){ #req-ts-5-08-019 }**REQ-TS-5-08-019** Wallet Backend Service MUST NOT attest a key of an installation it has revoked.
- [](){ #req-ts-5-08-020 }**REQ-TS-5-08-020** Wallet Backend Service MUST NOT attest the device key of an installation.
- [](){ #req-ts-5-08-021 }**REQ-TS-5-08-021** Issuer Core MUST refuse an attestation whose `attested_keys` carries more than one key.

</div>

## Resistance values {#ts-5-08-resistance-values}

`key_storage` says how hard it is to get the private key out of the storage it
sits in. `user_authentication` says how hard it is to make that storage use the
key without the citizen. Both take the values Appendix D.2 of
[OpenID4VCI][ref-openid4vci] defines, each the attack potential
[ISO/IEC 18045:2022][ref-iso-18045] names: `iso_18045_high`,
`iso_18045_moderate`, `iso_18045_enhanced-basic`, and `iso_18045_basic`.

Two things meet here. What an installation can report follows from the device:
an installation whose key storage component is evaluated at high reports
`iso_18045_high` whatever is being issued. What an issuer accepts follows from
the credential type, and it announces that per credential configuration in
`key_attestations_required`, which the Governance Profile maps from
`min_assurance`, as
[the mapping of assurance to key storage][tbl-min-assurance-mapping] sets out.
Issuer Core refuses an attestation that reports less than the issuer
announced, and the wallet learns it from the refusal.

What a value rests on is set by
[REQ-TS-5-08-081][req-ts-5-08-081] to [REQ-TS-5-08-091][req-ts-5-08-091], and
[two assurance levels][two-assurance-levels] gives the reasoning behind
them. An embedded Universal Integrated Circuit Card (eUICC) holding the key
can show what an evaluation at high asks for; a key in a trusted execution
environment or in a phone's general keystore cannot. The key management
software that runs on the secure element (on Android, KeyMint) need not be
inside the target of evaluation, provided the attestation platform
shows that the key was generated and is held inside the secure element (on
Android, `attestationSecurityLevel` and `keyMintSecurityLevel` both
`StrongBox`).

The attestation of
[Key Attestations as issued][ts-5-08-key-attestations-as-issued] reports such a
secure element and user authentication at moderate, which meets `high` in
[the mapping][tbl-min-assurance-mapping], because the mapping asks moderate of
user authentication at every level from `substantial` up.

Which evaluations count is the Governance Profile's to say. Its
`recognized_evaluation_schemes` list names the certification schemes whose
certificates are accepted. An Assessment Body checks each evaluation, and the
device models the Wallet Provider maps to it, when the Wallet Provider files it
with Trust Authority. The Root Authority decides on its report, so an
issuer reading `certification` finds an evaluation already checked.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-08-081 }**REQ-TS-5-08-081** Wallet Backend Service MUST report `iso_18045_high` for a resistance only where an evaluation under a scheme the `recognized_evaluation_schemes` list of the [Governance Profile][ts-02-closed-lists] names covers the component that provides that resistance and reaches the attack potential [ISO/IEC 18045][ref-iso-18045] calls high.
- [](){ #req-ts-5-08-087 }**REQ-TS-5-08-087** Wallet Backend Service MUST NOT treat an evaluation as reaching high unless it is a [Common Criteria][ref-iso-15408-3] certification that includes `AVA_VAN.5` and whose target of evaluation includes the component that provides the resistance.
- [](){ #req-ts-5-08-091 }**REQ-TS-5-08-091** Wallet Backend Service MUST treat the secure element in which the key is generated and held, together with the cryptographic library that operates on the key, as the component that provides the key storage resistance.
- [](){ #req-ts-5-08-092 }**REQ-TS-5-08-092** Wallet Backend Service MUST NOT require the key management software that runs on that secure element to be inside the target of evaluation, where the attestation platform shows the key generated and held inside that secure element.
- [](){ #req-ts-5-08-088 }**REQ-TS-5-08-088** Wallet Backend Service MUST NOT treat an evaluation as reaching high unless its certificate was issued under a scheme the `recognized_evaluation_schemes` list of the Governance Profile names.
- [](){ #req-ts-5-08-089 }**REQ-TS-5-08-089** Wallet Backend Service MUST NOT treat an evaluation as reaching high unless a laboratory that the scheme which issued the certificate licenses or accredits carried it out.
- [](){ #req-ts-5-08-090 }**REQ-TS-5-08-090** Wallet Backend Service MUST NOT put in `certification` the address of an evaluation it has not filed with Trust Authority as [Onboarding an entity and registering its keys](onboarding-an-entity-and-registering-its-keys.md) requires.
- [](){ #req-ts-5-08-082 }**REQ-TS-5-08-082** Wallet Backend Service MUST establish each resistance per key storage component and per device model.
- [](){ #req-ts-5-08-083 }**REQ-TS-5-08-083** Wallet Backend Service MUST NOT read a certification of a key storage component as establishing the resistance of user authentication.
- [](){ #req-ts-5-08-084 }**REQ-TS-5-08-084** Wallet Backend Service MUST NOT report a resistance from the name of a platform, a chip, or a key storage interface alone.
- [](){ #req-ts-5-08-085 }**REQ-TS-5-08-085** `certification` MUST be the address of the evaluation the reported values rest on.
- [](){ #req-ts-5-08-086 }**REQ-TS-5-08-086** Issuer Core MUST refuse an attestation that reports a value above `iso_18045_enhanced-basic` and carries no `certification`.
- [](){ #req-ts-5-08-022 }**REQ-TS-5-08-022** `key_storage` MUST be a non-empty array of values Appendix D.2 of [OpenID4VCI][ref-openid4vci] defines.
- [](){ #req-ts-5-08-023 }**REQ-TS-5-08-023** `user_authentication` MUST be a non-empty array of values Appendix D.2 of [OpenID4VCI][ref-openid4vci] defines.
- [](){ #req-ts-5-08-024 }**REQ-TS-5-08-024** Wallet Backend Service MUST report in `key_storage` the resistance of the storage the attested key sits in, as the attestation platform of that key establishes it, or, for an iOS credential key, as the official build the attestation platform shows running establishes it.
- [](){ #req-ts-5-08-025 }**REQ-TS-5-08-025** Wallet Backend Service MUST report in `user_authentication` the resistance of the authentication that releases the attested key.
- [](){ #req-ts-5-08-026 }**REQ-TS-5-08-026** Wallet Backend Service MUST NOT report a resistance that neither the attestation platform nor, for an iOS credential key, the official build it shows running establishes.
- [](){ #req-ts-5-08-027 }**REQ-TS-5-08-027** Wallet Backend Service MUST be able to show, for each resistance value it reports, the field of the attestation platform it derived that value from, or, for an iOS credential key, the device model and the evaluated build it derived that value from.
- [](){ #req-ts-5-08-028 }**REQ-TS-5-08-028** Issuer Core MUST refuse an attestation whose `key_storage` holds no value it announced for the credential type being issued.
- [](){ #req-ts-5-08-029 }**REQ-TS-5-08-029** Issuer Core MUST refuse an attestation whose `user_authentication` holds no value it announced for the credential type being issued.
- [](){ #req-ts-5-08-030 }**REQ-TS-5-08-030** Issuer Core MUST NOT accept `iso_18045_basic` for any credential type.

</div>

## Freshness and lifetime {#ts-5-08-freshness-and-lifetime}

An attestation is minted for one issuance. The wallet asks the issuer for a
nonce, hands that nonce to Wallet Backend Service, which writes it into the
attestation, so an attestation is bound to the issuer that handed out the nonce
and cannot be replayed at another one.

The lifetime the Governance Profile sets is a ceiling on how long one
lasts, not a schedule: an attestation is minted inside an
issuance and spent on it, and a wallet that asks for nothing holds nothing an
issuer would accept tomorrow.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-08-031 }**REQ-TS-5-08-031** Mobile Wallet MUST give Wallet Backend Service the nonce Issuer Core issued for the issuance the attestation is made for.
- [](){ #req-ts-5-08-032 }**REQ-TS-5-08-032** Mobile Wallet MUST obtain a nonce from Issuer Core before it asks Wallet Backend Service for an attestation.
- [](){ #req-ts-5-08-033 }**REQ-TS-5-08-033** Mobile Wallet MUST obtain a new attestation for each credential request.
- [](){ #req-ts-5-08-034 }**REQ-TS-5-08-034** Mobile Wallet MUST NOT send an attestation to an issuer other than the one whose nonce it carries.
- [](){ #req-ts-5-08-035 }**REQ-TS-5-08-035** `iat` and `exp` MUST each be a number of seconds since the Unix epoch.
- [](){ #req-ts-5-08-036 }**REQ-TS-5-08-036** `exp` MUST NOT be later than `iat` plus the lifetime the Governance Profile sets for a Key Attestation.
- [](){ #req-ts-5-08-037 }**REQ-TS-5-08-037** Issuer Core MUST refuse an attestation whose `exp` has passed.
- [](){ #req-ts-5-08-038 }**REQ-TS-5-08-038** Issuer Core MUST refuse an attestation whose `iat` is later than the moment it reads it by more than the clock skew the Governance Profile allows.
- [](){ #req-ts-5-08-039 }**REQ-TS-5-08-039** Issuer Core MUST refuse an attestation whose `nonce` is not the one it issued for that credential request.
- [](){ #req-ts-5-08-040 }**REQ-TS-5-08-040** Issuer Core MUST NOT accept the same `nonce` in two credential requests.
- [](){ #req-ts-5-08-041 }**REQ-TS-5-08-041** Issuer Core MUST issue the nonce an attestation carries from its Nonce Endpoint.

</div>

## Signature {#ts-5-08-signature}

Wallet Backend Service signs each attestation with the Key Attestation key,
as
[Publishing and resolving a did:webvh identifier](publishing-and-resolving-a-did-webvh-identifier.md)
fixes. It is the Wallet Provider's only transaction key, and it carries no
certificate: what says the Wallet Provider is accredited is its entry in the
trusted list, not a chain.

A reader finds the key by resolving the DID in `iss` and taking the
verification method `kid` names. A key the trusted list names as revoked in
that Wallet Provider's entry signs nothing, whatever date an attestation carries.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-08-042 }**REQ-TS-5-08-042** Wallet Backend Service MUST sign every Key Attestation with the Key Attestation key.
- [](){ #req-ts-5-08-043 }**REQ-TS-5-08-043** The Key Attestation key MUST be a P-256 key published as the `key-attestation` purpose in the Wallet Provider's DID Document.
- [](){ #req-ts-5-08-044 }**REQ-TS-5-08-044** *Withdrawn: [REQ-TS-01-035][req-ts-01-035] covers it.*
- [](){ #req-ts-5-08-045 }**REQ-TS-5-08-045** An attestation MUST carry exactly one signature.
- [](){ #req-ts-5-08-046 }**REQ-TS-5-08-046** Issuer Core MUST find the signing key as [Finding the key][ts-01-finding-the-key] of TS-01 requires, under the purpose `key-attestation`.
- [](){ #req-ts-5-08-047 }**REQ-TS-5-08-047** *Withdrawn: [REQ-TS-01-022][req-ts-01-022] covers it.*
- [](){ #req-ts-5-08-048 }**REQ-TS-5-08-048** Issuer Core MUST refuse an attestation signed with a key the trusted list names as revoked in the Wallet Provider's entry.
- [](){ #req-ts-5-08-049 }**REQ-TS-5-08-049** Issuer Core MUST refuse an attestation whose `iss` is not a Wallet Provider whose trusted list entry reads `granted` for that role.

</div>

## Carrying it to an issuer {#ts-5-08-carrying-it-to-an-issuer}

The attestation travels in the credential request, with the key it attests.
It is not client authentication.

[OpenID4VCI][ref-openid4vci] admits two carriers and the ecosystem uses both.
The `attestation` proof type of Appendix F.3 sends the attestation as the proof
itself, which an issuer that accepts only that proof type receives. The
`jwt` proof type of Appendix F.1 sends an ordinary key proof signed by the
credential key, with the attestation in its `key_attestation` header, which
adds a separate proof of possession of the key.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-08-050 }**REQ-TS-5-08-050** Mobile Wallet MUST send the attestation in the credential request, as the `attestation` proof type or in the `key_attestation` header of a `jwt` proof.
- [](){ #req-ts-5-08-051 }**REQ-TS-5-08-051** Mobile Wallet MUST NOT send a Key Attestation at the pushed authorization request or at the token endpoint.
- [](){ #req-ts-5-08-052 }**REQ-TS-5-08-052** Mobile Wallet MUST choose a proof type the issuer announced for the credential type it is asking for.
- [](){ #req-ts-5-08-053 }**REQ-TS-5-08-053** A `jwt` proof MUST be signed by the key the attestation covers.
- [](){ #req-ts-5-08-054 }**REQ-TS-5-08-054** A `jwt` proof MUST carry the same `nonce` as the attestation in its header.
- [](){ #req-ts-5-08-055 }**REQ-TS-5-08-055** A `jwt` proof MUST carry the identifier of the issuer it is sent to in `aud`.
- [](){ #req-ts-5-08-056 }**REQ-TS-5-08-056** Mobile Wallet MUST NOT send a Key Attestation to a verifier.
- [](){ #req-ts-5-08-073 }**REQ-TS-5-08-073** A `jwt` proof MUST carry the key it is signed with in `jwk`.
- [](){ #req-ts-5-08-080 }**REQ-TS-5-08-080** A `jwt` proof MUST NOT carry `kid` or `x5c`.
- [](){ #req-ts-5-08-074 }**REQ-TS-5-08-074** A `jwt` proof MUST carry `iss` with the wallet's client identifier, except where the access token was obtained through anonymous access to the token endpoint in the Pre-Authorized Code flow.
- [](){ #req-ts-5-08-057 }**REQ-TS-5-08-057** Mobile Wallet MUST NOT withhold a credential from a presentation because its attestation has expired.

</div>

## Reading it {#ts-5-08-reading-it}

Issuer Core runs the steps below before it signs anything, and runs all of them
from its own cached copies: none of them contacts the Wallet Provider.

1. Read the attestation out of the credential request, from the proof itself or
   from the `key_attestation` header of the proof.
2. Check that `typ` is `key-attestation+jwt` and that `alg` is one the
   Governance Profile allows for a Key Attestation key.
3. Look `iss` up in the cached trusted list and confirm it is a Wallet Provider
   whose entry reads `granted`.
4. Resolve the DID in `iss`, take the verification method `kid` names, and
   confirm the entry does not name that key as revoked.
5. Check the signature over the encoded header and payload with that key.
6. Check that `nonce` is the nonce it issued for this request and that `exp`
   has not passed.
7. Where the request carries a `jwt` proof, check the signature on that proof
   and that the key it was signed with is the key in `attested_keys`.
8. Check `key_storage` and `user_authentication` against the values it
   announced for the credential type being issued.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-08-058 }**REQ-TS-5-08-058** Issuer Core MUST run every check of [Reading it][ts-5-08-reading-it] before it issues a credential.
- [](){ #req-ts-5-08-059 }**REQ-TS-5-08-059** Issuer Core MUST refuse a credential request that carries no Key Attestation.
- [](){ #req-ts-5-08-060 }**REQ-TS-5-08-060** Issuer Core MUST refuse an attestation whose signature does not verify.
- [](){ #req-ts-5-08-061 }**REQ-TS-5-08-061** Issuer Core MUST refuse a credential request carrying a `jwt` proof whose signing key is not the key in `attested_keys`.
- [](){ #req-ts-5-08-062 }**REQ-TS-5-08-062** Issuer Core MUST bind the credential it issues to the key in `attested_keys` and to no other key.
- [](){ #req-ts-5-08-063 }**REQ-TS-5-08-063** Issuer Core MUST NOT call Wallet Backend Service while it validates an attestation.
- [](){ #req-ts-5-08-064 }**REQ-TS-5-08-064** Issuer Core MUST record the `key_storage` an accepted attestation reported, with the credential it issued.
- [](){ #req-ts-5-08-065 }**REQ-TS-5-08-065** Issuer Core MUST NOT treat a Key Attestation as evidence about the citizen, the device's owner, or the truth of any attribute it is about to issue.
- [](){ #req-ts-5-08-075 }**REQ-TS-5-08-075** Issuer Core MUST verify the signature on a `jwt` proof before it acts on the attestation in its header.
- [](){ #req-ts-5-08-076 }**REQ-TS-5-08-076** Issuer Core MUST accept a credential request carrying an `attestation` proof without a separate proof of possession, because that proof type carries none.

</div>

## What it does not carry {#ts-5-08-what-it-does-not-carry}

An attestation names no installation and no device: the thumbprint of the
device key identifies an installation to its own Wallet Backend Service and goes
no further. What an issuer can group is the attested key itself: every attestation of one
installation carries that installation's single credential key, which
[Privacy considerations][ts-5-08-privacy-considerations] records as the one
correlation the design keeps.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-08-066 }**REQ-TS-5-08-066** A Key Attestation MUST NOT carry an identifier of the wallet installation, or any identifier of the hardware it runs on.
- [](){ #req-ts-5-08-067 }**REQ-TS-5-08-067** A Key Attestation MUST NOT carry a `status` claim.
- [](){ #req-ts-5-08-068 }**REQ-TS-5-08-068** A Key Attestation MUST carry `certification` where it reports a value above `iso_18045_enhanced-basic` for either resistance.
- [](){ #req-ts-5-08-069 }**REQ-TS-5-08-069** A Key Attestation MUST NOT carry personal data, an attribute of the citizen, or a list of the credentials the installation holds.
- [](){ #req-ts-5-08-070 }**REQ-TS-5-08-070** Wallet Backend Service MUST NOT revoke a Key Attestation it has issued.
- [](){ #req-ts-5-08-077 }**REQ-TS-5-08-077** Wallet Backend Service MUST NOT publish a status list for the attestations it has issued.

</div>

## Security considerations {#ts-5-08-security-considerations}

- **An attestation replayed at another issuer.** A valid attestation is a
  reusable pass for a day unless it is bound to one exchange.
  [REQ-TS-5-08-031][req-ts-5-08-031] binds it to the nonce the issuer handed
  out, [REQ-TS-5-08-039][req-ts-5-08-039] makes an issuer refuse any other
  nonce, and [REQ-TS-5-08-040][req-ts-5-08-040] keeps a nonce from serving
  twice.
- **A credential bound to a key nobody attested.** A wallet could attest one
  key and prove possession of another. [REQ-TS-5-08-061][req-ts-5-08-061] and
  [REQ-TS-5-08-062][req-ts-5-08-062] tie the proof key, the attested key, and
  the key the credential is bound to together.
- **A forged attestation.** [REQ-TS-5-08-046][req-ts-5-08-046] to
  [REQ-TS-5-08-049][req-ts-5-08-049] make an issuer resolve the signing key in
  the Wallet Provider's own DID Document, refuse a revoked key, and refuse a
  Wallet Provider the trusted list does not carry at `granted`.
- **A disowned installation that goes on being issued to.**
  [REQ-TS-5-08-019][req-ts-5-08-019] stops the next attestation at
  Wallet Backend Service and [REQ-TS-5-08-036][req-ts-5-08-036] caps how long
  the last one lasts, so the window is a day and nothing has to be
  distributed to close it.
- **An over-reported resistance value.** A Wallet Provider that claims
  `iso_18045_high` for a software keystore sells an assurance it does not have.
  [REQ-TS-5-08-024][req-ts-5-08-024] and [REQ-TS-5-08-026][req-ts-5-08-026]
  tie the value to the platform's own evidence, and
  [REQ-TS-5-08-027][req-ts-5-08-027] makes the derivation public, which an
  Assessment Body tests.
- **A stolen Key Attestation key.** Its holder can attest any key as sitting in
  a secure element until the trusted list names the key revoked.
  [REQ-TS-5-08-048][req-ts-5-08-048] ends that, and the attestation's
  own daily expiry limits what was minted before it.

## Privacy considerations {#ts-5-08-privacy-considerations}

The Wallet Provider learns that an installation asked for an attestation, and
nothing about the issuer or the credential that follows: a nonce is an opaque
string and names nobody.
The issuer learns a public key, two resistance values, and which Wallet Provider
vouched for them, and nothing that identifies the device.
[REQ-TS-5-08-063][req-ts-5-08-063] keeps the two apart at issuance time, so
neither can watch the other's side of the exchange.

One correlation stays. Every credential of one installation is bound to the
same credential key, so two issuers that compare what they attested see the
same key. That is a property of the single credential key rather than of the
attestation, and
[Deriving a did:key and a device identifier](deriving-a-did-key-and-a-device-identifier.md)
is where it is recorded.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-08-071 }**REQ-TS-5-08-071** Wallet Backend Service MUST discard the nonce it wrote into an attestation once that attestation is issued.
- [](){ #req-ts-5-08-072 }**REQ-TS-5-08-072** Issuer Core MUST NOT disclose a Key Attestation it received to a third party.

</div>

## Changelog {#ts-5-08-changelog}

<figure markdown="1" class="ekdn-table">

| Version | Date | Change |
|---|---|---|
| 1.0 draft | 21 October 2026 | First draft |

</figure>
