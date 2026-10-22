---
title: "[TS-2-01] Enrolling a wallet installation and attesting its key"
description: How a Mobile Wallet installation enrolls with its Wallet Backend Service, the platform evidence each of its two keys is checked against on Android and iOS, the record Wallet Backend Service keeps, what a request for a Key Attestation proves, and when an installation is revoked.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §3.4, §7.6, §9.2; Bentuk Data Attestation §1; Rincian Module dan Operasi §6, §8; tracks/0085, tracks/0133, tracks/0149, tracks/0273; debt/0155, debt/0156 -->

<p class="ekdn-docid">TS-2-01</p>

# Enrolling a wallet installation and attesting its key {#ts-2-01-enrolling-a-wallet-installation-and-attesting-its-key}

<p class="ekdn-lead" markdown="span">
Enrollment is where a Wallet Provider first meets a wallet installation. It
checks that the two keys the installation made sit in hardware and belong to
the official build, binds the installation to the citizen's account, and
records what it will later vouch for. Every Key Attestation the installation
obtains afterward rests on that record.
</p>

Every sentence on this page binds Mobile Wallet, which enrolls and asks, and
Wallet Backend Service, which checks, records, and attests, and an
Assessment Body tests them against it in the version the Governance Profile puts
in force. The key words and the identifier `REQ-TS-2-01-nnn` follow
[Common provisions](common-provisions.md).

## Who runs this and what it needs {#ts-2-01-who-runs-this-and-what-it-needs}

This specification fixes:

- What an enrollment carries and what Wallet Backend Service checks before it
  records an installation.
- What a request for a Key Attestation carries and what Wallet Backend Service
  checks before it issues one.
- The record Wallet Backend Service keeps for each installation.
- When an installation is revoked.

It fixes what each message proves and leaves how the message travels. The
transport, the endpoints, and the encoding between a Mobile Wallet and its own
Wallet Backend Service belong to the Wallet Provider, as
[the interface table][tbl-interfaces-and-standards] sets out, because no other
party ever reads them. What an Assessment Body tests is the outcome: it hands
Wallet Backend Service good evidence and bad, and checks which it records,
which it attests, and which it refuses.

Its conformance targets are Mobile Wallet, which enrolls its installation and
asks for each attestation, and Wallet Backend Service, which checks the
evidence, keeps the record, and issues or refuses.

It leaves to other documents:

- The Key Attestation itself, its claims, its signature, how it is carried, and
  what an issuer checks, which
  [Issuing and reading a Key Attestation](issuing-and-reading-a-key-attestation.md)
  holds.
- The form of the device identifier, which
  [Deriving a did:key and a device identifier](deriving-a-did-key-and-a-device-identifier.md)
  holds.
- The identity provider's own interface, which belongs to whoever runs it.
- Which evaluations count and the mapping from an assurance level to the
  resistance values an issuer announces, which the Governance Profile holds.
- [Who decides to revoke an installation on grounds other than the two this page names][gf-revoking-an-installation]
  and [how long a record is kept][gf-retention], which the Governance Framework
  holds.
- The encrypted backup and the push notifications Wallet Backend Service also
  runs, which no other party reads.

Before the first enrollment, each target holds what the rules below assume:

- **Wallet Backend Service** holds:
    - A client registration at the identity provider the Wallet Provider chose.
    - The identity of the official Mobile Wallet build: its Android package
      name and signing certificate digest, and its iOS App ID.
    - The roots [Accepted roots][ts-2-01-accepted-roots] names.
    - For each device model and key storage component it vouches for, the
      evaluation the resistance values rest on.
    - The Key Attestation key
      [Issuing and reading a Key Attestation](issuing-and-reading-a-key-attestation.md)
      fixes.
- **Mobile Wallet** is the official build, running on an Android device with
  a hardware-backed keystore or on an iOS device with the Secure Enclave and
  App Attest.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-2-01-001 }**REQ-TS-2-01-001** Mobile Wallet MUST meet every requirement addressed to it in [The enrollment challenge][ts-2-01-the-enrollment-challenge], [The identity provider's token][ts-2-01-the-identity-providers-token], [The enrollment binding][ts-2-01-the-enrollment-binding], [Evidence on Android][ts-2-01-evidence-on-android], [Evidence on iOS][ts-2-01-evidence-on-ios], [Asking for a Key Attestation][ts-2-01-asking-for-a-key-attestation], and [Revoking an installation][ts-2-01-revoking-an-installation].
- [](){ #req-ts-2-01-002 }**REQ-TS-2-01-002** Wallet Backend Service MUST meet every requirement addressed to it in the sections REQ-TS-2-01-001 names, in [Accepted roots][ts-2-01-accepted-roots], in [The installation record][ts-2-01-the-installation-record], and in [Privacy considerations][ts-2-01-privacy-considerations].

</div>

## What enrollment does {#ts-2-01-what-enrollment-does}

At the citizen's first login to the wallet, Mobile Wallet creates two keys in
the device's secure hardware. The [device key][the-device-key] identifies the
installation to its own Wallet Backend Service and nothing else; every
credential the installation receives is bound to the
[credential key][the-credential-key]. The two are never the same key, so the key
that identifies the installation never appears in a presentation. Enrollment is the one
moment Wallet Backend Service sees both public keys together, checks the
platform's evidence for each, and ties them to an account at the identity
provider. The flow as a whole is in
[wallet enrollment and attestation][wallet-enrollment-and-attestation].

Each piece of evidence comes from a different source: the identity provider's
token, the chip's attestation platform, the operating system's integrity verdict.
Each one is made to commit to the same string, the *binding string*, so that
pieces from two sessions or two devices cannot be put together into one
enrollment.

The two platforms differ in what they attest. Android attests any key its
keystore generates, so both keys arrive with their own certificate chain.
Apple attests only the App Attest key, and
[Evidence on iOS][ts-2-01-evidence-on-ios] sets out what then vouches for the
credential key.

After enrollment, the installation asks for a Key Attestation once for each
credential request, and Wallet Backend Service vouches for the credential key
it recorded and no other. When an installation is revoked, and what that cuts
off, is in [Revoking an installation][ts-2-01-revoking-an-installation].

What an installation can report is bounded by the evaluation of its key
storage. A component reaches high only through the evaluation
[REQ-TS-5-08-087][req-ts-5-08-087] names, so the installations of a device
model without one obtain no attestation an issuer accepts for a credential
type at `high`.

## An enrollment and a request, as exchanged {#ts-2-01-an-enrollment-and-a-request-as-exchanged}

The values below are an illustration: the Wallet Provider, the identity
provider, the installations, and the keys are invented, and no wallet has
enrolled. Every field is exact.

The Android installation's credential key is the key the
[Key Attestation][ts-5-08-key-attestations-as-issued] of TS-5-08 attests,
and its request carries that attestation's nonce, so the two pages show one
installation. The certificate chains themselves are signed by
Google's and Apple's roots, which an illustration does not imitate, so the
evidence appears as Wallet Backend Service reads it once the chain is checked
and the structure decoded. The device key's signature and the App Attest
assertion are made with the illustration keys and verify.

### On Android {#ts-2-01-on-android}

The identity provider's token, which Mobile Wallet obtained with the
enrollment challenge as its nonce:

``` { .json title="The identity provider's token claims, decoded" data-format="JSON" }
{
  "iss": "https://login.akunnusantara.co.id",
  "sub": "5f0c9a1e-7b3d-4c2e-9a61-2d8e4b7f3c10",
  "aud": "dompet-wallet",
  "nonce": "Yb3xQ0nR7vLp2sKd9WfH1g",
  "iat": 1792214982,
  "exp": 1792215282
}
```

The attestation platform of each key, generated with the same challenge:

``` { .text title="KeyDescription of the credential key, decoded" data-format="ASN.1" }
attestationVersion        300
attestationSecurityLevel  StrongBox
keyMintVersion            300
keyMintSecurityLevel      StrongBox
attestationChallenge      "Yb3xQ0nR7vLp2sKd9WfH1g"
softwareEnforced {
  attestationApplicationId {
    packageInfos {
      packageName         "id.co.dompet.wallet"
      version             42
    }
    signatureDigests {
      a62fcc2f2f21221e480e72adef626f7277b259c1f5e51f8742567e5cf884d6bb
    }
  }
}
hardwareEnforced {
  purpose                 [SIGN]
  algorithm               EC
  ecCurve                 P_256
  userSecureId            7406185221307495937
  userAuthType            FINGERPRINT | PASSWORD
  origin                  GENERATED
  rootOfTrust {
    verifiedBootKey       fad3936e891c8ab06bcdd7b8996cbdac5a94b155834b5b4db198beeca41abb0f
    deviceLocked          true
    verifiedBootState     Verified
    verifiedBootHash      d58b7344e1c016564431f23d45c16a75b669685e9b0189e20e589d009159df09
  }
  attestationIdBrand      "nusa"
  attestationIdManufacturer "Nusa Teknologi"
  attestationIdModel      "Nusa Phone 8 Pro"
}
```

``` { .text title="KeyDescription of the device key, decoded" data-format="ASN.1" }
attestationVersion        300
attestationSecurityLevel  StrongBox
keyMintVersion            300
keyMintSecurityLevel      StrongBox
attestationChallenge      "Yb3xQ0nR7vLp2sKd9WfH1g"
softwareEnforced {
  attestationApplicationId {
    packageInfos {
      packageName         "id.co.dompet.wallet"
      version             42
    }
    signatureDigests {
      a62fcc2f2f21221e480e72adef626f7277b259c1f5e51f8742567e5cf884d6bb
    }
  }
}
hardwareEnforced {
  purpose                 [SIGN]
  algorithm               EC
  ecCurve                 P_256
  noAuthRequired
  origin                  GENERATED
  rootOfTrust {
    verifiedBootKey       fad3936e891c8ab06bcdd7b8996cbdac5a94b155834b5b4db198beeca41abb0f
    deviceLocked          true
    verifiedBootState     Verified
    verifiedBootHash      d58b7344e1c016564431f23d45c16a75b669685e9b0189e20e589d009159df09
  }
  attestationIdBrand      "nusa"
  attestationIdManufacturer "Nusa Teknologi"
  attestationIdModel      "Nusa Phone 8 Pro"
}
```

The enrollment binding string, the challenge and the thumbprint of the
credential key, and the integrity verdict whose `requestHash` is its hash:

``` { .text title="The enrollment binding string" data-format="Output" }
Yb3xQ0nR7vLp2sKd9WfH1g.-wnrmeXLSC4x4INmzIdjNoDDE_7axmfgCymzfJBOhxk
```

``` { .json title="The integrity verdict at enrollment, decoded" data-format="JSON" }
{
  "requestDetails": {
    "requestPackageName": "id.co.dompet.wallet",
    "timestampMillis": "1792215001000",
    "requestHash": "NufGcckVgxViBia0hefsyrz5b7OrhzKVeBgkEkEl7jE"
  },
  "appIntegrity": {
    "appRecognitionVerdict": "PLAY_RECOGNIZED",
    "packageName": "id.co.dompet.wallet",
    "certificateSha256Digest": [
      "pi_MLy8hIh5IDnKt72JvcneyWcH15R-HQlZ-XPiE1rs"
    ],
    "versionCode": "42"
  },
  "deviceIntegrity": {
    "deviceRecognitionVerdict": [
      "MEETS_BASIC_INTEGRITY",
      "MEETS_DEVICE_INTEGRITY",
      "MEETS_STRONG_INTEGRITY"
    ]
  },
  "accountDetails": {
    "appLicensingVerdict": "LICENSED"
  }
}
```

The record Wallet Backend Service keeps once every check passes, and the
record of the installation the same account held before, which it revoked in
the same step:

``` { .json title="The installation record" data-format="JSON" }
{
  "installation": "KrCmnBrdPMJHuRg9i5S0mWRagm8mkS-fJrdlvaKLfII",
  "platform": "android",
  "account": {
    "iss": "https://login.akunnusantara.co.id",
    "sub": "5f0c9a1e-7b3d-4c2e-9a61-2d8e4b7f3c10"
  },
  "device_key": {
    "kty": "EC",
    "crv": "P-256",
    "x": "94rg-4VtzLsCnokXp72epEl2qybQMWJrg5pX-gfICu4",
    "y": "ZEhnwu4lH0vyvOvGZtXevhuALd9S2JLu6GwNlUmA1-U"
  },
  "credential_key": {
    "kty": "EC",
    "crv": "P-256",
    "x": "3COhxOeOxpBOjUJgqWSAU0QAAYaYgugPVJ_2X2qGdkc",
    "y": "2k98854pB77uddRve8O4kg5nIPT7EjEgpbeKqWLuMEE"
  },
  "device_model": "Nusa Phone 8 Pro",
  "key_storage_component": "StrongBox",
  "key_storage": [
    "iso_18045_high"
  ],
  "user_authentication": [
    "iso_18045_moderate"
  ],
  "certification": "https://dompet.co.id/certification/se-2026-a",
  "state": "active",
  "enrolled_at": 1792215002
}
```

``` { .json title="The previous installation's record, revoked" data-format="JSON" }
{
  "installation": "HHndPnzUf9bkrWbBlkPkqZKtism_aONMZZ_BA0Ny-wA",
  "platform": "android",
  "account": {
    "iss": "https://login.akunnusantara.co.id",
    "sub": "5f0c9a1e-7b3d-4c2e-9a61-2d8e4b7f3c10"
  },
  "device_key": {
    "kty": "EC",
    "crv": "P-256",
    "x": "6WFWz66Iex614Z6AERLZATKOtuVJE4PMv33zq0XhfPU",
    "y": "vUIUIeuP2IKGh6K5OlbdOrJYI1h8OzjAUm3AVC_rEf8"
  },
  "credential_key": {
    "kty": "EC",
    "crv": "P-256",
    "x": "f1wrMBa9eUZygruZK63t-zYvICmNicJgzjf9p8S2msk",
    "y": "Lftk9gJsE1VH3Mo0uy2ncZ3H976ttxhnTDSY9yspFwE"
  },
  "device_model": "Nusa Phone 5",
  "key_storage_component": "TrustedEnvironment",
  "key_storage": [
    "iso_18045_enhanced-basic"
  ],
  "user_authentication": [
    "iso_18045_enhanced-basic"
  ],
  "state": "revoked",
  "enrolled_at": 1760000000,
  "revoked_at": 1792215002
}
```

A request for the Key Attestation of TS-5-08. The request binding string is
the issuer's nonce and the same thumbprint; the device key signs it, and the
integrity verdict carries its hash:

``` { .text title="The request binding string" data-format="Output" }
kQ8vZ2mH7rT1.-wnrmeXLSC4x4INmzIdjNoDDE_7axmfgCymzfJBOhxk
```

``` { .text title="The device key's signature over the request binding string" data-format="Output" }
XALG00hj-ofGcBJFK3Dk1T6QOVf4u4WFvBE2il2Vj1Dyhx_vtQDJ1da_fw6GMqh6EhrYq7qJuSZWW_EgzgtphA
```

``` { .json title="The integrity verdict in the request, decoded" data-format="JSON" }
{
  "requestDetails": {
    "requestPackageName": "id.co.dompet.wallet",
    "timestampMillis": "1792216798000",
    "requestHash": "LBNBlJZrWiVUnxSqmpgvXhPDDSCR6-__2Ko78TOYJ0w"
  },
  "appIntegrity": {
    "appRecognitionVerdict": "PLAY_RECOGNIZED",
    "packageName": "id.co.dompet.wallet",
    "certificateSha256Digest": [
      "pi_MLy8hIh5IDnKt72JvcneyWcH15R-HQlZ-XPiE1rs"
    ],
    "versionCode": "42"
  },
  "deviceIntegrity": {
    "deviceRecognitionVerdict": [
      "MEETS_BASIC_INTEGRITY",
      "MEETS_DEVICE_INTEGRITY",
      "MEETS_STRONG_INTEGRITY"
    ]
  },
  "accountDetails": {
    "appLicensingVerdict": "LICENSED"
  }
}
```

### On iOS {#ts-2-01-on-ios}

The enrollment binding string of an iOS installation, and the App Attest
attestation whose `clientDataHash` is its hash, with the credential key sent
beside it:

``` { .text title="The iOS enrollment binding string" data-format="Output" }
tK7vN2qZ8mR4xW1cL5pD0s.4bnPfCMFs05m-gYcmTLwVK8uOS9Tvlm5x_p_-dyUa20
```

``` { .json title="The App Attest attestation, as Wallet Backend Service checks it" data-format="JSON" }
{
  "attestation": {
    "fmt": "apple-appattest",
    "keyId": "xWXvGeWF72AQ6T34yWQ4yTr4geBqCs1eBqxKgxIDNWI=",
    "clientDataHash": "OSJ-AcTWBecuW7UPs2zA32hs2_pM0UPtXt8IqH7zAQM",
    "authData": {
      "rpIdHash": "1e87b17335bf3cd31ea3e24aacff7ba2e8bef93b9854ec7474d790541d12d11f",
      "signCount": 0,
      "aaguid": "61707061747465737400000000000000",
      "credentialId": "c565ef19e585ef6010e93df8c96438c93af881e06a0acd5e06ac4a8312033562"
    }
  },
  "credential_key": {
    "kty": "EC",
    "crv": "P-256",
    "x": "UCIh4eXZKHOgNHcfmGU1VDwds8crXFplFZZMowzwHEk",
    "y": "YgPwNckYtXKTAJRGbiXDFPx62gUw_3KaFe9TFWB5lxA"
  }
}
```

A request for a Key Attestation, carried by an App Attest assertion over the
request binding string, and the record after Wallet Backend Service accepted
it:

``` { .text title="The iOS request binding string" data-format="Output" }
kQ8vZ2mH7rT1.4bnPfCMFs05m-gYcmTLwVK8uOS9Tvlm5x_p_-dyUa20
```

``` { .text title="The App Attest assertion, in hex" data-format="CBOR hex" }
a2697369676e61747572655847304502205df63f5d7680bda3621760193268e4
4f92b8a67f8cf15f56ed6cef523e0ec0f0022100fc32c85299742cf868353c2e
09de89331d0dd58416a6d7cd5d7e2c6be92caa7b7161757468656e7469636174
6f724461746158251e87b17335bf3cd31ea3e24aacff7ba2e8bef93b9854ec74
74d790541d12d11f0000000001
```

``` { .json title="The installation record on iOS" data-format="JSON" }
{
  "installation": "b0uE9XPaRarQEvJS5mK5FwR9tR_WgHVUWF8AVMDrFrI",
  "platform": "ios",
  "account": {
    "iss": "https://login.akunnusantara.co.id",
    "sub": "a3e17c52-08d4-4f9b-b6c2-71d0e95a4b28"
  },
  "device_key": {
    "kty": "EC",
    "crv": "P-256",
    "x": "e9Wm27_r2GgZxLwczDgckiICOmZxPILOHWg_RmkNXHA",
    "y": "9_o9QfRIJUjWTE2UAnpskh4gDe0Tpel0PCLicMn6g2A"
  },
  "credential_key": {
    "kty": "EC",
    "crv": "P-256",
    "x": "UCIh4eXZKHOgNHcfmGU1VDwds8crXFplFZZMowzwHEk",
    "y": "YgPwNckYtXKTAJRGbiXDFPx62gUw_3KaFe9TFWB5lxA"
  },
  "device_model": "iPhone17,1",
  "key_storage_component": "SecureEnclave",
  "key_storage": [
    "iso_18045_enhanced-basic"
  ],
  "user_authentication": [
    "iso_18045_enhanced-basic"
  ],
  "sign_count": 1,
  "state": "active",
  "enrolled_at": 1792215600
}
```

## The enrollment challenge {#ts-2-01-the-enrollment-challenge}

An enrollment runs in six steps.

1. Mobile Wallet asks Wallet Backend Service for an enrollment challenge.
2. Mobile Wallet logs the citizen in at the identity provider over
   [OpenID Connect Core 1.0][ref-openid-core], with the challenge as the
   `nonce` of the authentication request, and receives an ID Token.
3. Mobile Wallet creates the device key and the credential key, as
   [Evidence on Android][ts-2-01-evidence-on-android] or
   [Evidence on iOS][ts-2-01-evidence-on-ios] fixes.
4. Mobile Wallet forms the enrollment binding string and obtains the
   platform's evidence over it.
5. Mobile Wallet sends Wallet Backend Service the enrollment, which carries
   what [the table of enrollment contents][tbl-ts-2-01-enrollment] lists.
6. Wallet Backend Service runs every check this specification names, records
   the installation, revokes any other active installation of the same
   account, and confirms the enrollment, or refuses it.

[](){ #tbl-ts-2-01-enrollment }

<figure markdown="1" class="ekdn-table">

| Item | Type | Presence | What it carries |
|---|---|---|---|
| Challenge | string | Present | The enrollment challenge Wallet Backend Service issued |
| ID Token | JSON Web Token | Present | The identity provider's token, with the challenge as `nonce` |
| Platform | string | Present | `android` or `ios` |
| Credential key | JSON Web Key | Present | The public credential key, with `kty`, `crv`, `x` and `y` |
| Device key | JSON Web Key | Present on Android | The public device key; on iOS it is read from the App Attest attestation |
| Credential key chain | X.509 certificates | Present on Android | The attestation platform of the credential key, as a certificate chain |
| Device key chain | X.509 certificates | Present on Android | The attestation platform of the device key, as a certificate chain |
| Integrity token | string | Present on Android | The Play Integrity token over the enrollment binding |
| App Attest key identifier | string | Present on iOS | The `keyId` of the App Attest key |
| App Attest attestation | CBOR | Present on iOS | The attestation object over the enrollment binding |
| Device model | string | Present on iOS | The hardware model identifier the official build reads |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-2-01-003 }**REQ-TS-2-01-003** Wallet Backend Service MUST make each enrollment challenge from at least 128 bits of a cryptographically secure random source, encoded in base64url without padding.
- [](){ #req-ts-2-01-004 }**REQ-TS-2-01-004** Wallet Backend Service MUST accept a challenge in one enrollment only.
- [](){ #req-ts-2-01-005 }**REQ-TS-2-01-005** Wallet Backend Service MUST refuse an enrollment whose challenge is older than the lifetime the Governance Profile sets.
- [](){ #req-ts-2-01-006 }**REQ-TS-2-01-006** Mobile Wallet MUST use one challenge for every piece of evidence in one enrollment.
- [](){ #req-ts-2-01-007 }**REQ-TS-2-01-007** Mobile Wallet MUST send every item [the table of enrollment contents][tbl-ts-2-01-enrollment] marks present for its platform.
- [](){ #req-ts-2-01-008 }**REQ-TS-2-01-008** Wallet Backend Service MUST refuse an enrollment that lacks an item [the table of enrollment contents][tbl-ts-2-01-enrollment] marks present for its platform.
- [](){ #req-ts-2-01-009 }**REQ-TS-2-01-009** Wallet Backend Service MUST NOT record an installation before every check of this specification has passed for it.

</div>

## The identity provider's token {#ts-2-01-the-identity-providers-token}

The ID Token establishes an account, not who the citizen is: identity
proofing happens at issuance and is rooted in the Identity Issuer. The
account lets the Wallet Provider recognize the same citizen on a new
device and revoke the old installation.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-2-01-010 }**REQ-TS-2-01-010** Mobile Wallet MUST send the enrollment challenge as the `nonce` of the authentication request it makes to the identity provider.
- [](){ #req-ts-2-01-011 }**REQ-TS-2-01-011** Wallet Backend Service MUST validate the ID Token as Section 3.1.3.7 of [OpenID Connect Core][ref-openid-core] requires, with its own client registration as the audience.
- [](){ #req-ts-2-01-012 }**REQ-TS-2-01-012** Wallet Backend Service MUST refuse an ID Token whose `nonce` is not the challenge of the enrollment that carries it.
- [](){ #req-ts-2-01-013 }**REQ-TS-2-01-013** Wallet Backend Service MUST identify the account by the pair of `iss` and `sub`.
- [](){ #req-ts-2-01-014 }**REQ-TS-2-01-014** Wallet Backend Service MUST NOT treat the ID Token as evidence of the citizen's identity.

</div>

## The enrollment binding {#ts-2-01-the-enrollment-binding}

The hash of the enrollment binding string is the SHA-256 of the string's
UTF-8 octets. On Android the integrity verdict carries the hash as its
`requestHash`; on iOS the App Attest attestation is made over it as its
`clientDataHash`. The challenge itself is the `attestationChallenge` of both
Android attestation platforms, because a key's thumbprint cannot be known before
the key exists.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-2-01-015 }**REQ-TS-2-01-015** Mobile Wallet MUST form the enrollment binding string as the challenge, a period, and the base64url SHA-256 [RFC 7638][ref-rfc7638] thumbprint of the credential key.
- [](){ #req-ts-2-01-016 }**REQ-TS-2-01-016** Wallet Backend Service MUST recompute the enrollment binding string from the challenge and the credential key the enrollment carries.
- [](){ #req-ts-2-01-017 }**REQ-TS-2-01-017** Wallet Backend Service MUST refuse an enrollment whose integrity verdict on Android, or whose App Attest attestation on iOS, does not commit to the hash of that string.

</div>

## Evidence on Android {#ts-2-01-evidence-on-android}

Mobile Wallet generates both keys in the Android Keystore as P-256 signing
keys, with the challenge as their attestation challenge and the device
properties included. Each certificate chain then says where its key sits,
which application holds it, on which device model, and in which boot state.
The credential key is bound to the citizen's authentication; the device key
is not, because it signs requests the citizen does not see.

Wallet Backend Service checks the evidence in five steps.

1. Validate each chain as [RFC 5280][ref-rfc5280] requires, up to a root
   [Accepted roots][ts-2-01-accepted-roots] names, and check that no
   certificate in it is on Google's attestation revocation list.
2. Read the KeyDescription extension of each leaf, object identifier
   1.3.6.1.4.1.11129.2.1.17, as
   [Android Key Attestation][ref-android-key-attestation] defines it.
3. Check each key's KeyDescription against the requirements below.
4. Decode the integrity token through Google's server, as
   [Play Integrity][ref-play-integrity] defines it, and check the verdict.
5. Take the device model and the security level, and establish the
   resistance values from the evaluation that covers them.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-2-01-018 }**REQ-TS-2-01-018** Mobile Wallet MUST generate the device key and the credential key on Android as P-256 keys whose only purposes are signing and verifying, with the enrollment challenge as the attestation challenge and with device property attestation included.
- [](){ #req-ts-2-01-019 }**REQ-TS-2-01-019** Mobile Wallet MUST generate the credential key on Android so that the keystore releases it only after the citizen authenticates.
- [](){ #req-ts-2-01-020 }**REQ-TS-2-01-020** Mobile Wallet MUST obtain the integrity verdict with the base64url hash of the enrollment binding string as its request hash.
- [](){ #req-ts-2-01-021 }**REQ-TS-2-01-021** Wallet Backend Service MUST refuse a chain that does not end at a root [Accepted roots][ts-2-01-accepted-roots] names.
- [](){ #req-ts-2-01-022 }**REQ-TS-2-01-022** Wallet Backend Service MUST refuse a chain any of whose certificates Google's attestation revocation list names as revoked or suspended.
- [](){ #req-ts-2-01-023 }**REQ-TS-2-01-023** Wallet Backend Service MUST refuse a key whose `attestationSecurityLevel` or `keyMintSecurityLevel` is `Software`.
- [](){ #req-ts-2-01-024 }**REQ-TS-2-01-024** Wallet Backend Service MUST refuse a key whose `attestationChallenge` is not the enrollment challenge.
- [](){ #req-ts-2-01-025 }**REQ-TS-2-01-025** Wallet Backend Service MUST refuse a key whose `attestationApplicationId` does not carry the package name and the signing certificate digest of the official build.
- [](){ #req-ts-2-01-026 }**REQ-TS-2-01-026** Wallet Backend Service MUST refuse a key whose `rootOfTrust` does not carry `verifiedBootState` `Verified` and `deviceLocked` `true`.
- [](){ #req-ts-2-01-027 }**REQ-TS-2-01-027** Wallet Backend Service MUST refuse a key whose `hardwareEnforced` list does not carry `origin` `GENERATED`, `algorithm` `EC`, `ecCurve` `P_256`, and no `purpose` other than `SIGN` and `VERIFY`.
- [](){ #req-ts-2-01-028 }**REQ-TS-2-01-028** Wallet Backend Service MUST refuse a credential key whose `hardwareEnforced` list carries `noAuthRequired` or carries no `userAuthType`.
- [](){ #req-ts-2-01-029 }**REQ-TS-2-01-029** Wallet Backend Service MUST refuse an enrollment whose two keys do not carry the same `attestationIdModel`.
- [](){ #req-ts-2-01-030 }**REQ-TS-2-01-030** Wallet Backend Service MUST refuse a key whose leaf certificate does not carry the public key the enrollment sends for it.
- [](){ #req-ts-2-01-031 }**REQ-TS-2-01-031** Wallet Backend Service MUST refuse an integrity verdict whose `requestHash` is not the base64url hash of the enrollment binding string.
- [](){ #req-ts-2-01-032 }**REQ-TS-2-01-032** Wallet Backend Service MUST refuse an integrity verdict whose `appRecognitionVerdict` is not `PLAY_RECOGNIZED` or whose package name and certificate digest are not the official build's.
- [](){ #req-ts-2-01-033 }**REQ-TS-2-01-033** Wallet Backend Service MUST refuse an integrity verdict whose `deviceRecognitionVerdict` does not hold the value the Governance Profile requires for the device's Android version.
- [](){ #req-ts-2-01-034 }**REQ-TS-2-01-034** Wallet Backend Service MUST refuse an integrity verdict whose `timestampMillis` lies further from the moment it reads it than the window the Governance Profile sets.
- [](){ #req-ts-2-01-080 }**REQ-TS-2-01-080** Wallet Backend Service MUST refuse an integrity verdict from a device whose Android version is below the lowest the Governance Profile names a required value for.

</div>

## Evidence on iOS {#ts-2-01-evidence-on-ios}

On iOS the device key is the App Attest key: the Secure Enclave generates
it, Apple attests it, and it signs only App Attest assertions, which is all
the device key does.

The credential key is a separate P-256 key in the Secure Enclave, because
the App Attest key cannot sign a JSON Web Signature or a `COSE_Sign1`. Apple
attests no key but the App Attest key, so the evidence for the credential key
is the App Attest attestation whose `clientDataHash` is the hash of the
enrollment binding, which carries the credential key's thumbprint.

That attestation is the *attestation platform* of the iOS credential key: it
shows that the official build produced the key. That build, which an
Assessment Body has tested, fixes where the key sits and what releases it.

Wallet Backend Service checks the attestation object as
[App Attest][ref-app-attest] defines it, in five steps.

1. Validate the `x5c` chain up to the Apple App Attestation Root CA.
2. Compute the nonce as the SHA-256 of `authData` followed by the
   `clientDataHash`, and check it against the extension of the leaf
   certificate under object identifier 1.2.840.113635.100.8.2.
3. Check that `rpIdHash` is the SHA-256 of the official build's App ID, that
   the counter is zero, and that `aaguid` is the production value.
4. Check that `credentialId` and the key identifier are the SHA-256 of the
   leaf certificate's public key.
5. Take the device model the enrollment carries, and establish the
   resistance values from the evaluation that covers the Secure Enclave of
   that model and the official build's access control.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-2-01-035 }**REQ-TS-2-01-035** Mobile Wallet MUST use the App Attest key as the device key on iOS.
- [](){ #req-ts-2-01-036 }**REQ-TS-2-01-036** Mobile Wallet MUST generate the credential key on iOS as a P-256 key in the Secure Enclave, not exportable, whose access control requires the citizen's authentication for each use of the private key.
- [](){ #req-ts-2-01-037 }**REQ-TS-2-01-037** Mobile Wallet MUST make the App Attest attestation with the hash of the enrollment binding string as its `clientDataHash`.
- [](){ #req-ts-2-01-038 }**REQ-TS-2-01-038** Mobile Wallet MUST send the hardware model identifier of the device it runs on.
- [](){ #req-ts-2-01-039 }**REQ-TS-2-01-039** Wallet Backend Service MUST refuse an attestation object whose chain does not end at the root [Accepted roots][ts-2-01-accepted-roots] names for iOS.
- [](){ #req-ts-2-01-040 }**REQ-TS-2-01-040** Wallet Backend Service MUST refuse an attestation object whose certified nonce is not the SHA-256 of its `authData` followed by the hash of the enrollment binding string.
- [](){ #req-ts-2-01-041 }**REQ-TS-2-01-041** Wallet Backend Service MUST refuse an attestation object whose `rpIdHash` is not the SHA-256 of the official build's App ID.
- [](){ #req-ts-2-01-042 }**REQ-TS-2-01-042** Wallet Backend Service MUST refuse an attestation object whose counter is not zero or whose `aaguid` is not the production value `appattest` followed by seven zero octets.
- [](){ #req-ts-2-01-043 }**REQ-TS-2-01-043** Wallet Backend Service MUST refuse an attestation object whose `credentialId` or key identifier is not the SHA-256 of its leaf certificate's public key.
- [](){ #req-ts-2-01-044 }**REQ-TS-2-01-044** Wallet Backend Service MUST treat the App Attest attestation that commits to the credential key's thumbprint as the attestation platform of the iOS credential key, for the requirements of [Issuing and reading a Key Attestation](issuing-and-reading-a-key-attestation.md).

</div>

## Accepted roots {#ts-2-01-accepted-roots}

Google publishes the roots of Android Key Attestation at
`https://android.googleapis.com/attestation/root`. Since 1 February 2026 it
signs new chains under an Elliptic Curve Digital Signature Algorithm (ECDSA)
P-384 root while the older RSA root stays valid, so a device enrolled before
that date and one enrolled after it present chains to different roots. Apple
publishes one root for App Attest. A root is identified by the SHA-256
fingerprint of its certificate.

[](){ #tbl-ts-2-01-accepted-roots }

<figure markdown="1" class="ekdn-table">

| Platform | Root | SHA-256 fingerprint | Valid until |
|---|---|---|---|
| Android | Google RSA root, serial number `f92009e853b6b045` | `CEDB1CB6DC896AE5EC797348BCE9286753C2B38EE71CE0FBE34A9A1248800DFC` | 15 March 2042 |
| Android | `CN=Key Attestation CA1, OU=Android, O=Google LLC, C=US`, ECDSA P-384 | `6D9DB4CE6C5C0B293166D08986E05774A8776CEB525D9E4329520DE12BA4BCC0` | 15 July 2035 |
| iOS | `CN=Apple App Attestation Root CA, O=Apple Inc., ST=California` | `1CB9823BA28BA6AD2D33A006941DE2AE4F513EF1D4E831B9F7E0FA7B6242C932` | 15 March 2045 |

</figure>

A root joins the table through a minor version of this specification. A root
leaves it when its owner withdraws it from the address it publishes roots at,
or on the date the Governance Profile names for it, whichever comes first.
An installation enrolled under a root that has left keeps its record; only a
new enrollment needs a root in the table.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-2-01-045 }**REQ-TS-2-01-045** Wallet Backend Service MUST accept an Android chain that ends at either Android root of [the table of accepted roots][tbl-ts-2-01-accepted-roots], unless [REQ-TS-2-01-047][req-ts-2-01-047] applies.
- [](){ #req-ts-2-01-046 }**REQ-TS-2-01-046** Wallet Backend Service MUST identify a root by the SHA-256 fingerprint of its certificate.
- [](){ #req-ts-2-01-047 }**REQ-TS-2-01-047** Wallet Backend Service MUST refuse a chain that ends at a root its owner has withdrawn or whose date in the Governance Profile has passed.
- [](){ #req-ts-2-01-048 }**REQ-TS-2-01-048** Wallet Backend Service MUST refresh its copy of Google's attestation revocation list within the time its `Cache-Control` header allows.

</div>

## The installation record {#ts-2-01-the-installation-record}

Wallet Backend Service keeps one record for each installation it has
enrolled. Every later Key Attestation is read from it: the credential key
it names, and the resistance values established for it. The
encrypted backup the same service runs is outside this specification: it holds
ciphertext the citizen alone holds the key to, so it records none of what
[REQ-TS-2-01-054][req-ts-2-01-054] names.

<figure markdown="1" class="ekdn-table">

| Field | Type | Presence | What it carries |
|---|---|---|---|
| `installation` | string | Present | The device identifier, the thumbprint of the device key |
| `platform` | string | Present | `android` or `ios` |
| `account` | object | Present | The `iss` and `sub` of the ID Token |
| `device_key` | JSON Web Key | Present | The public device key |
| `credential_key` | JSON Web Key | Present | The public credential key |
| `device_model` | string | Present | The device model the evidence names on Android, or the enrollment on iOS |
| `key_storage_component` | string | Present | The component the credential key sits in: `StrongBox` or `TrustedEnvironment` on Android, `SecureEnclave` on iOS |
| `key_storage` | array of strings | Present | The resistance of the credential key's storage, as the evaluation establishes it |
| `user_authentication` | array of strings | Present | The resistance of the authentication that releases it |
| `certification` | string | Present where a value above `iso_18045_enhanced-basic` is recorded | The address of the evaluation those values rest on |
| `sign_count` | number | Present on iOS | The counter of the last App Attest assertion accepted |
| `state` | string | Present | `active` or `revoked` |
| `enrolled_at` | number | Present | The moment the installation was recorded |
| `revoked_at` | number | Present once revoked | The moment it was revoked |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-2-01-049 }**REQ-TS-2-01-049** Wallet Backend Service MUST compute `installation` as [The device identifier][ts-5-03-the-device-identifier] of TS-5-03 requires, from the device key the installation enrolled with.
- [](){ #req-ts-2-01-050 }**REQ-TS-2-01-050** Wallet Backend Service MUST record exactly one credential key for an installation.
- [](){ #req-ts-2-01-051 }**REQ-TS-2-01-051** Wallet Backend Service MUST NOT replace the credential key of a record.
- [](){ #req-ts-2-01-052 }**REQ-TS-2-01-052** Wallet Backend Service MUST establish `key_storage` and `user_authentication` per key storage component and device model, as [Resistance values][ts-5-08-resistance-values] of TS-5-08 requires.
- [](){ #req-ts-2-01-053 }**REQ-TS-2-01-053** Wallet Backend Service MUST establish the two values again when an evaluation they rest on is withdrawn or replaced.
- [](){ #req-ts-2-01-054 }**REQ-TS-2-01-054** Wallet Backend Service MUST NOT record a credential, an issuer, a verifier, or an attribute of the citizen.
- [](){ #req-ts-2-01-055 }**REQ-TS-2-01-055** Wallet Backend Service MUST hold at most one installation in the state `active` for one account.

</div>

## Asking for a Key Attestation {#ts-2-01-asking-for-a-key-attestation}

A request for a Key Attestation runs inside one credential request, in six
steps.

1. Mobile Wallet obtains a nonce from Issuer Core, as
   [Freshness and lifetime][ts-5-08-freshness-and-lifetime] of TS-5-08
   requires.
2. Mobile Wallet forms the request binding string: the nonce, a period,
   and the thumbprint of the credential key.
3. On Android, Mobile Wallet signs the request binding string with the
   device key and obtains an integrity verdict over its hash. On iOS, it
   generates an App Attest assertion with the hash of the string as its
   `clientDataHash`.
4. Mobile Wallet sends Wallet Backend Service what
   [the table of request contents][tbl-ts-2-01-request] lists.
5. Wallet Backend Service finds the record, recomputes the request binding
   string from the nonce and the recorded credential key, and checks the
   evidence against it.
6. Wallet Backend Service issues the Key Attestation, with the recorded
   credential key in `attested_keys`, as
   [REQ-TS-5-08-016][req-ts-5-08-016] requires, the nonce in `nonce`, and the recorded
   resistance values, or refuses.

[](){ #tbl-ts-2-01-request }

<figure markdown="1" class="ekdn-table">

| Item | Type | Presence | What it carries |
|---|---|---|---|
| Installation | string | Present | The device identifier |
| Credential key | string | Present | The [RFC 7638][ref-rfc7638] thumbprint of the credential key to be attested |
| Nonce | string | Present | The nonce Issuer Core issued for this credential request |
| Signature | string | Present on Android | The device key's ES256 signature over the request binding string, base64url |
| Integrity token | string | Present on Android | The Play Integrity token over the request binding |
| App Attest assertion | CBOR | Present on iOS | The assertion over the request binding |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-2-01-056 }**REQ-TS-2-01-056** Mobile Wallet MUST form the request binding string as the nonce, a period, and the base64url SHA-256 [RFC 7638][ref-rfc7638] thumbprint of the credential key.
- [](){ #req-ts-2-01-057 }**REQ-TS-2-01-057** On Android, Mobile Wallet MUST sign the UTF-8 octets of the request binding string with the device key, as ES256 in the form Section 3.4 of [RFC 7518][ref-rfc7518] defines.
- [](){ #req-ts-2-01-058 }**REQ-TS-2-01-058** On Android, Mobile Wallet MUST obtain the integrity verdict with the base64url hash of the request binding string as its request hash.
- [](){ #req-ts-2-01-059 }**REQ-TS-2-01-059** On iOS, Mobile Wallet MUST generate the assertion with the hash of the request binding string as its `clientDataHash`.
- [](){ #req-ts-2-01-060 }**REQ-TS-2-01-060** Mobile Wallet MUST send every item [the table of request contents][tbl-ts-2-01-request] marks present for its platform.
- [](){ #req-ts-2-01-061 }**REQ-TS-2-01-061** Wallet Backend Service MUST refuse a request whose installation has no record.
- [](){ #req-ts-2-01-062 }**REQ-TS-2-01-062** Wallet Backend Service MUST refuse a request whose credential key is not the thumbprint of the credential key of the record.
- [](){ #req-ts-2-01-063 }**REQ-TS-2-01-063** Wallet Backend Service MUST recompute the request binding string from the nonce the request carries and the credential key of the record.
- [](){ #req-ts-2-01-064 }**REQ-TS-2-01-064** On Android, Wallet Backend Service MUST refuse a request whose signature does not verify under the recorded device key.
- [](){ #req-ts-2-01-065 }**REQ-TS-2-01-065** On Android, Wallet Backend Service MUST check the integrity verdict of the request as REQ-TS-2-01-031 to REQ-TS-2-01-034 require, with the hash of the request binding string in place of the enrollment's.
- [](){ #req-ts-2-01-066 }**REQ-TS-2-01-066** On iOS, Wallet Backend Service MUST refuse an assertion whose signature does not verify under the recorded device key over the SHA-256 of its `authenticatorData` followed by the hash of the request binding string.
- [](){ #req-ts-2-01-067 }**REQ-TS-2-01-067** On iOS, Wallet Backend Service MUST refuse an assertion whose `rpIdHash` is not the official build's or whose counter is not greater than the recorded `sign_count`.
- [](){ #req-ts-2-01-068 }**REQ-TS-2-01-068** On iOS, Wallet Backend Service MUST record the counter of an assertion it accepts as `sign_count`.
- [](){ #req-ts-2-01-069 }**REQ-TS-2-01-069** Wallet Backend Service MUST report in the Key Attestation the resistance values of the record.
- [](){ #req-ts-2-01-070 }**REQ-TS-2-01-070** Wallet Backend Service MUST NOT revoke an installation because one of its requests failed a check.

</div>

## Revoking an installation {#ts-2-01-revoking-an-installation}

An installation has two states, `active` and `revoked`, and a revoked one
never returns. Two events revoke it under this specification: its account
enrolls another installation, which is how
[device migration][device-migration] cuts off the old phone, and the citizen
reports the device lost. Revocation is a line in the record and nothing more.
Wallet Backend Service refuses the next request, as
[REQ-TS-5-08-019][req-ts-5-08-019] requires, the last attestation expires
within a day, and no list is published.

A reinstalled application enrolls again with new keys, whatever the platform
kept of the previous installation's keys, so a reinstallation is a new
installation.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-2-01-071 }**REQ-TS-2-01-071** Wallet Backend Service MUST revoke every other active installation of an account when it records a new installation for that account.
- [](){ #req-ts-2-01-072 }**REQ-TS-2-01-072** Wallet Backend Service MUST revoke an installation when the citizen reports its device lost.
- [](){ #req-ts-2-01-073 }**REQ-TS-2-01-073** Wallet Backend Service MUST authenticate the citizen who reports a device lost through the installation's account at the identity provider before it revokes the installation.
- [](){ #req-ts-2-01-074 }**REQ-TS-2-01-074** Wallet Backend Service MUST NOT return a revoked installation to `active`.
- [](){ #req-ts-2-01-075 }**REQ-TS-2-01-075** Wallet Backend Service MUST NOT publish a list of revoked installations.
- [](){ #req-ts-2-01-076 }**REQ-TS-2-01-076** Mobile Wallet MUST create a new device key and a new credential key for each enrollment.

</div>

## Security considerations {#ts-2-01-security-considerations}

- **Evidence from two sessions put together.** An attacker could pair the
  attestation of a genuine device with a key it controls.
  [REQ-TS-2-01-006][req-ts-2-01-006] keeps one challenge across the
  enrollment, and [REQ-TS-2-01-017][req-ts-2-01-017] makes the integrity
  verdict or the App Attest attestation commit to the credential key's
  thumbprint.
- **A replayed enrollment.** [REQ-TS-2-01-004][req-ts-2-01-004] and
  [REQ-TS-2-01-005][req-ts-2-01-005] make a challenge good for one
  enrollment and a short time.
- **A key outside the hardware.** [REQ-TS-2-01-023][req-ts-2-01-023] refuses
  a software key on Android, and [REQ-TS-2-01-044][req-ts-2-01-044] makes
  the iOS credential key rest on the build that App Attest shows running.
- **A repackaged or modified application.**
  [REQ-TS-2-01-025][req-ts-2-01-025], [REQ-TS-2-01-032][req-ts-2-01-032], and
  [REQ-TS-2-01-041][req-ts-2-01-041] tie every key to the official build.
- **A rooted device or an unlocked bootloader.**
  [REQ-TS-2-01-026][req-ts-2-01-026] and [REQ-TS-2-01-033][req-ts-2-01-033]
  refuse it at enrollment, and [REQ-TS-2-01-065][req-ts-2-01-065] at every
  request.
- **A flaw in the official iOS build.** The iOS credential key's storage is
  vouched for by the build rather than by the chip, so a build that made the
  key outside the Secure Enclave would be believed.
  An Assessment Body tests [REQ-TS-2-01-036][req-ts-2-01-036] in the
  build, and [REQ-TS-2-01-042][req-ts-2-01-042] refuses a development build.
- **A replayed request for an attestation.** On iOS
  [REQ-TS-2-01-067][req-ts-2-01-067] refuses a counter seen before. On
  Android a replayed signature yields an attestation for a nonce the issuer
  accepts once, as [REQ-TS-5-08-040][req-ts-5-08-040] requires.
- **A stolen phone.** [REQ-TS-2-01-019][req-ts-2-01-019] and
  [REQ-TS-2-01-036][req-ts-2-01-036] keep the credential key behind the
  citizen's authentication, and [REQ-TS-2-01-072][req-ts-2-01-072] stops the
  next attestation once the loss is reported.
- **An account taken over at the identity provider.** An attacker who
  enrolls a device under the citizen's account revokes the citizen's
  installation through [REQ-TS-2-01-071][req-ts-2-01-071], which stops new
  issuance to it and leaves the credentials it holds presentable. The
  attacker's installation holds no credential until an issuer has proofed
  the citizen again, and [REQ-TS-2-01-014][req-ts-2-01-014] keeps the account
  from standing in for that proofing.
- **A withdrawn attestation root.** [REQ-TS-2-01-047][req-ts-2-01-047] stops
  enrollments under it without touching the installations already recorded.

## Privacy considerations {#ts-2-01-privacy-considerations}

Wallet Backend Service learns the account, the device model, the two public
keys, and the moments the installation enrolled and asked for an
attestation. It does not learn which issuer a request was for, nor which
credential followed, nor any verifier: a nonce names nobody. The
device key never appears in a presentation, so the installation's identifier
does not reach a verifier.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-2-01-077 }**REQ-TS-2-01-077** Wallet Backend Service MUST NOT keep the ID Token after the enrollment it was carried in.
- [](){ #req-ts-2-01-078 }**REQ-TS-2-01-078** Wallet Backend Service MUST NOT disclose an installation record to an issuer or a verifier.
- [](){ #req-ts-2-01-079 }**REQ-TS-2-01-079** Wallet Backend Service MUST NOT keep the platform evidence of a request after it has issued or refused the attestation.

</div>

## Changelog {#ts-2-01-changelog}

<figure markdown="1" class="ekdn-table">

| Version | Date | Change |
|---|---|---|
| 1.0 draft | 21 October 2026 | First draft |

</figure>
