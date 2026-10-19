---
title: "[TS-5-10] Issuing a credential in SD-JWT VC, mdoc, and ldp_vc"
description: The three representations a credential is issued in, what each carries, how the issuer signs it, how the holder's key is bound into it, where its status entry points, and what a reader checks before it believes any of it.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §4.1, §4.2 (Kep. 3, 5, 11, 14), §4.3, §4.4; Bentuk Data Attestation §1; Peta Alur Penerbitan dan Presentasi §1, §2.2; Panduan mdoc §2, §8, Lampiran A; tracks/0323 -->

<p class="ekdn-docid">TS-5-10</p>

# Issuing a credential in SD-JWT VC, mdoc, and `ldp_vc` {#ts-5-10-issuing-a-credential-in-sd-jwt-vc-mdoc-and-ldp-vc}

<p class="ekdn-lead" markdown="span">
A credential is the signed set of statements an issuer hands a citizen, and it
takes one of three shapes on the wire. This specification fixes all three: what
each carries, which key signs it, how the citizen's key is bound into it, and
what a reader checks before it believes a single claim.
</p>

Every sentence on this page binds Issuer Core, which assembles and signs a
credential, Mobile Wallet, which receives and stores one, and Verifier Core and
Mobile Verifier, which read one, and an Assessment Body tests them against it in
the version the Governance Profile puts in force. The key words and the
identifier `REQ-TS-5-10-nnn` follow
[Common provisions](common-provisions.md).

## Who runs this and what it needs {#ts-5-10-who-runs-this-and-what-it-needs}

This specification fixes the three representations a credential is issued in:
an [SD-JWT-based Verifiable Credential (SD-JWT VC)][ref-i-d-ietf-oauth-sd-jwt-vc]
draft -13, an [ISO mdoc][ref-iso-18013-5] under ISO/IEC 18013-5:2021, and a
[W3C Verifiable Credentials Data Model (VCDM) 2.0][ref-vc-data-2-0] document
secured with a Data Integrity proof, which OpenID4VCI 1.0 calls `ldp_vc`. For
each it fixes the claims and fields, the encoding of a value, the signature, the
holder binding, the status pointer, the validity period, and the checks a reader
runs on the credential itself.

Its conformance targets are Issuer Core, which builds and signs a credential;
Mobile Wallet, which receives, stores and parses one; and Verifier Core and
Mobile Verifier, which read one. A Relying Party's own application built on
Reader SDK reads an mdoc through that library, and the requirements addressed to
Mobile Verifier bind the application as well.

This specification binds a credential of a type a Credential Rulebook
governs. The Accreditation Credential is an SD-JWT VC that no Rulebook
governs, and
[Issuing and carrying an Accreditation Credential](issuing-and-carrying-an-accreditation-credential.md)
fixes it on its own terms; nothing on this page binds it.

Six things a credential depends on sit elsewhere. Which representations a
credential type takes, what its claims are called, and how each value is typed
come from its Credential Rulebook, whose fields
[Rulebook structure](../credential-rulebook/rulebook-structure.md) fixes. The
exchange that carries a credential to a wallet is OpenID4VCI, which
[Issuing a credential via OpenID4VCI](issuing-a-credential-via-openid4vci.md)
fixes. The presentation of a credential is
[Building and verifying a presentation](building-and-verifying-a-presentation.md).
The status list a credential points into is
[Publishing and reading a status list](publishing-and-reading-a-status-list.md).
The Document Signer Certificate an mdoc carries is
[Issuing and validating the X.509 certificates and the VICAL](issuing-and-validating-the-x509-certificates-and-the-vical.md).
Finding the issuer's signing key from its identifier is
[Finding a signer's key from its DID](finding-a-signers-key-from-its-did.md).
Each signature algorithm, and the ceiling on a technical validity period, are
values the Governance Profile sets; this specification names where each one
applies.

Before Issuer Core signs anything it holds four things: the credential key the
wallet attested, as
[Issuing and reading a Key Attestation](issuing-and-reading-a-key-attestation.md)
requires; the Credential Rulebook of the type, with the formats it names; the
claim values, read from the issuer's own source system; and the status entry the
credential is allocated. Mobile Wallet holds the credential key in the storage
the Rulebook's `min_assurance` demands. A reader holds a cached trusted list, the
issuer's Decentralized Identifier (DID) Document or the Issuer Root CA, and the status list, all fetched
before the transaction.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-10-001 }**REQ-TS-5-10-001** Issuer Core MUST meet every requirement this specification addresses to it before it issues a credential of any type.
- [](){ #req-ts-5-10-002 }**REQ-TS-5-10-002** Mobile Wallet MUST meet every requirement this specification addresses to it in [Serialization][ts-5-10-serialization] and in [Reading a credential][ts-5-10-reading-a-credential].
- [](){ #req-ts-5-10-003 }**REQ-TS-5-10-003** Verifier Core and Mobile Verifier MUST meet every requirement in [Reading a credential][ts-5-10-reading-a-credential].
- [](){ #req-ts-5-10-128 }**REQ-TS-5-10-128** Issuer Core MUST validate the claims its source system returns against the type's `schema` before it builds any representation.
- [](){ #req-ts-5-10-129 }**REQ-TS-5-10-129** Issuer Core MUST check [`format`][ref-json-schema] as an assertion when it validates, so a `date` or `date-time` value in any other form fails.
- [](){ #req-ts-5-10-130 }**REQ-TS-5-10-130** Issuer Core MUST reject the claims if a value whose schema sets [`contentEncoding: base64`][ref-json-schema] fails to decode.

</div>

## What a credential is {#ts-5-10-what-a-credential-is}

A credential carries five things, as
[what one credential carries][what-one-credential-carries] sets out: the claims,
the type identifier that names the governing Credential Rulebook, the holder
binding, the status pointer, and the issuer's signature over all four. The three
representations differ in how each of the five is written down, and in nothing
else. [The table of five parts][tbl-ts-5-10-five-parts] gives the field that
carries each one.

[](){ #tbl-ts-5-10-five-parts }

<figure markdown="1" class="ekdn-table">

| Part | SD-JWT VC | mdoc | `ldp_vc` |
|---|---|---|---|
| Claims | A disclosure per claim, digested in `_sd` | An `IssuerSignedItem` per claim, digested in `valueDigests` | Members of `credentialSubject` |
| Type identifier | `vct` | `docType`, and the one namespace of `nameSpaces` | `type`, after `VerifiableCredential` |
| Holder binding | `cnf.jwk` | `deviceKeyInfo.deviceKey` | `credentialSubject.id` |
| Status pointer | `status.status_list` | `status.status_list` in the Mobile Security Object | One `credentialStatus` entry per purpose |
| Issuer's signature | A JSON Web Signature in compact serialization | A `COSE_Sign1` as `issuerAuth` | A Data Integrity proof in `ecdsa-rdfc-2019` |

</figure>

A citizen holds one credential and the wallet may hold it twice, as
[one credential, two representations][one-credential-two-representations] sets
out. An SD-JWT VC and an mdoc of the same credential carry the same claim values,
the same credential key, and the same status entry, which is how a verifier can tell they are two
views of one thing rather than two credentials that happen to agree. `ldp_vc`
never pairs with either, because a Credential Rulebook that lists it lists
nothing else.

There are three because each one does a job the others cannot. An
SD-JWT VC is read online and has no proximity profile. An mdoc is the only
representation a verifier can check with no network at either end. `ldp_vc`
exists so that a credential issued here is readable by JSON-LD software written
outside the ecosystem, and it pays for that with no selective disclosure at all.

## The credentials as issued {#ts-5-10-the-credentials-as-issued}

The three credentials below are an illustration: the citizens, the issuers, the
addresses and the keys are invented, and no credential has been issued. Every
field is exact. Each was signed with the key its `kid`, its certificate, or its
`verificationMethod` names, each signature verifies, and each digest recomputes,
so an implementation can parse these artifacts and find what the clauses below
require. There is one per representation, each of a type whose Credential
Rulebook names that representation, and all three are bound to the one
credential key
[Issuing and reading a Key Attestation](issuing-and-reading-a-key-attestation.md)
attests, whose holder identifier
[Deriving a did:key and a device identifier](deriving-a-did-key-and-a-device-identifier.md)
publishes. Their three issuers are the ones
[the trusted list][ts-5-01-trusted-list-payload] carries. Each
signature was made with the key its `kid` or its `verificationMethod` names,
under the key purposes
[the table of keys by role][tbl-ts-5-02-keys-by-role] fixes, and the mdoc was
signed under the Document Signer Certificate
[the Document Signer Certificate as issued][ts-5-04-document-signer-certificate-as-issued]
publishes. Each status pointer names a list
[Publishing and reading a status list](publishing-and-reading-a-status-list.md)
serves, at an index that page shows as valid.

### A Kartu ASN as an SD-JWT VC {#ts-5-10-a-kartu-asn-as-an-sd-jwt-vc}

The credential as the wallet receives it: the issuer-signed JSON Web Token
(JWT), then one disclosure per claim, then the empty slot where a Key Binding
JWT goes at presentation time.

``` { .text title="A Kartu ASN in SD-JWT VC, as issued" data-format="SD-JWT VC" }
eyJ0eXAiOiJkYytzZC1qd3QiLCJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDp3ZWJ2aDpRbWU4UnJp
R25LeDVqMlFqb2FZMVNnUlNweFRIZGpxMTFMMkV4Z3kxelYyeHNKOmJrbi5nby5pZCNpc3N1YW5j
ZS1qb3NlLTEifQ.eyJpc3MiOiJkaWQ6d2Vidmg6UW1lOFJyaUduS3g1ajJRam9hWTFTZ1JTcHhUS
GRqcTExTDJFeGd5MXpWMnhzSjpia24uZ28uaWQiLCJ2Y3QiOiJpZC5pZGN0Zi5rYXJ0dS1hc24uM
SIsImNuZiI6eyJqd2siOnsia3R5IjoiRUMiLCJjcnYiOiJQLTI1NiIsIngiOiIzQ09oeE9lT3hwQ
k9qVUpncVdTQVUwUUFBWWFZZ3VnUFZKXzJYMnFHZGtjIiwieSI6IjJrOTg4NTRwQjc3dWRkUnZlO
E80a2c1bklQVDdFakVncGJlS3FXTHVNRUUifX0sIl9zZF9hbGciOiJzaGEtMjU2IiwiX3NkIjpbI
jF6QTdMcXNPdGJoTFZRaG9fUlNlMFRHcVJyZmctUzU4SlpHV1NmZzZabU0iLCJDZnVRdi1jS3Jne
mYwdXpIeHUtVEJFQkp2dFo0UEE3U0RhVjloOFQ5TF9RIiwiRVQ5QmlsbFV3VmRoYkhjNnRmXy0xW
EFDRWdWUDRiX2lVUHhIQ2FYQlNiYyIsIkhMeVU4aHRZWno0TmkyZlJkN3BTWWRpQ2JCLXF0NDhwQ
lM5aDJCR013VFEiLCJlNlVoQk44QXk1emRVUGdDX2htbnBXbGR3QnhpWDhGN2tPVzRuUklwNXdNI
iwiZkFoREt6VjNVMzlqQzZiN0dMaEdGRGw3NnVnVy1tN0R6N1hxcUJuamxkYyIsImhLTUpsakZJT
lQtd0ljUDhFUnJhWURrSExyMjZPWUJTQUlHS0ItMG5ORzgiLCJ3N0MxZXJCNno4OG1oRVZzTm5hU
VlEZ2JacUNIakxsM2NieDFFemllUnFzIl0sInN0YXR1cyI6eyJzdGF0dXNfbGlzdCI6eyJpZHgiO
jQ4MTkyMCwidXJpIjoiaHR0cHM6Ly9ia24uZ28uaWQvc3RhdHVzL2thcnR1LWFzbi0xIn19LCJuY
mYiOjE3OTIyMTY4MTAsImlhdCI6MTc5MjIxNjgxMCwiZXhwIjoxODIzNzUyODEwfQ.Rtt14iNH1C
OHmkwCwvzkYcg2RftZdls7V1WghZc1xZC3GmENzivjroJTPBu2C83Qy4pbdbNsX0lorDW26kbPLg
~WyJ3SXVNc2VoQTM1UEp0RU1yUzRub0NRIiwibmFtYSIsIkJ1ZGkgU2FudG9zbyBXaWNha3Nvbm8
iXQ~WyJ1b19YWTdpUXQtZGRMZk4yTVZMZEdnIiwibmlwIiwiMTk4NzAzMTUyMDEwMDExMDAyIl0~
WyJMSjBmYk54N3ZwT2h4UlpCVjNhNTB3IiwiZ29sb25nYW4iLCJJSUkvYyJd~WyJWTmRqX2xoU00
xTXBWTktMOW1HMTR3Iiwic3RhdHVzX2tlcGVnYXdhaWFuIiwiUE5TIl0~WyJwZVViQWhBdlZiUkN
hdkoxbm5mNmRBIiwiamFiYXRhbiIsIkFuYWxpcyBLZWJpamFrYW4gQWhsaSBNdWRhIl0~WyJNNW8
1SnZyU0ZpeHZvUjNLZWk1VTFnIiwidW5pdF9rZXJqYSIsIkRpcmVrdG9yYXQgSmFiYXRhbiBBU04
iXQ~WyJSb1o4SHRpMk9JVkJ4NHlNd3Q0UkZRIiwiaW5zdGFuc2kiLCJCYWRhbiBLZXBlZ2F3YWlh
biBOZWdhcmEiXQ~WyJNa0FESE9vcHFJSGJvbEJISHVBNmNnIiwiZm90byIsImRhdGE6aW1hZ2Uva
nBlZztiYXNlNjQsLzlqLzRBQVFTa1pKUmdBQkFRRUFZQUJnQUFELzJ3QkRBQWdHQmdjR0JRZ0hCd
2NKQ1FnS0RCUU5EQXNMREJrU0V3OFVIUm9mSGgwYUhCd2dKQzRuSUNJc0l4d2NLRGNwTERBeE5EU
TBIeWM1UFRneVBDNHpOREwvd0FBTENBQUJBQUVCQVJFQS84UUFGQUFCQUFBQUFBQUFBQUFBQUFBQ
UFBQUFDZi9FQUJRUUFRQUFBQUFBQUFBQUFBQUFBQUFBQUFELzJnQUlBUUVBQUQ4QUtwLy8yUT09I
l0~
```

Its header and its claims, decoded. The eight type claims are not among them:
each one sits behind a digest in `_sd`.

``` { .json title="SD-JWT VC header" data-format="JSON" }
{
  "typ": "dc+sd-jwt",
  "alg": "ES256",
  "kid": "did:webvh:Qme8RriGnKx5j2QjoaY1SgRSpxTHdjq11L2Exgy1zV2xsJ:bkn.go.id#issuance-jose-1"
}
```

``` { .json title="SD-JWT VC claims" data-format="JSON" }
{
  "iss": "did:webvh:Qme8RriGnKx5j2QjoaY1SgRSpxTHdjq11L2Exgy1zV2xsJ:bkn.go.id",
  "vct": "id.idctf.kartu-asn.1",
  "cnf": {
    "jwk": {
      "kty": "EC",
      "crv": "P-256",
      "x": "3COhxOeOxpBOjUJgqWSAU0QAAYaYgugPVJ_2X2qGdkc",
      "y": "2k98854pB77uddRve8O4kg5nIPT7EjEgpbeKqWLuMEE"
    }
  },
  "_sd_alg": "sha-256",
  "_sd": [
    "1zA7LqsOtbhLVQho_RSe0TGqRrfg-S58JZGWSfg6ZmM",
    "CfuQv-cKrgzf0uzHxu-TBEBJvtZ4PA7SDaV9h8T9L_Q",
    "ET9BillUwVdhbHc6tf_-1XACEgVP4b_iUPxHCaXBSbc",
    "HLyU8htYZz4Ni2fRd7pSYdiCbB-qt48pBS9h2BGMwTQ",
    "e6UhBN8Ay5zdUPgC_hmnpWldwBxiX8F7kOW4nRIp5wM",
    "fAhDKzV3U39jC6b7GLhGFDl76ugW-m7Dz7XqqBnjldc",
    "hKMJljFINT-wIcP8ERraYDkHLr26OYBSAIGKB-0nNG8",
    "w7C1erB6z88mhEVsNnaQYDgbZqCHjLl3cbx1EzieRqs"
  ],
  "status": {
    "status_list": {
      "idx": 481920,
      "uri": "https://bkn.go.id/status/kartu-asn-1"
    }
  },
  "nbf": 1792216810,
  "iat": 1792216810,
  "exp": 1823752810
}
```

The eight disclosures, each shown with the array it decodes to. Every one is a
salt, a claim name, and a value, and the order they travel in is the order the
issuer put them in, which is not the order of `_sd`:

``` { .text title="The eight disclosures, with their decoded arrays" data-format="SD-JWT VC" }
~WyJ3SXVNc2VoQTM1UEp0RU1yUzRub0NRIiwibmFtYSIsIkJ1ZGkgU2FudG9zbyBXaWNha3Nvbm8iXQ
  ["wIuMsehA35PJtEMrS4noCQ","nama","Budi Santoso Wicaksono"]
~WyJ1b19YWTdpUXQtZGRMZk4yTVZMZEdnIiwibmlwIiwiMTk4NzAzMTUyMDEwMDExMDAyIl0
  ["uo_XY7iQt-ddLfN2MVLdGg","nip","198703152010011002"]
~WyJMSjBmYk54N3ZwT2h4UlpCVjNhNTB3IiwiZ29sb25nYW4iLCJJSUkvYyJd
  ["LJ0fbNx7vpOhxRZBV3a50w","golongan","III/c"]
~WyJWTmRqX2xoU00xTXBWTktMOW1HMTR3Iiwic3RhdHVzX2tlcGVnYXdhaWFuIiwiUE5TIl0
  ["VNdj_lhSM1MpVNKL9mG14w","status_kepegawaian","PNS"]
~WyJwZVViQWhBdlZiUkNhdkoxbm5mNmRBIiwiamFiYXRhbiIsIkFuYWxpcyBLZWJpamFrYW4gQWhsaSBNdWRhIl0
  ["peUbAhAvVbRCavJ1nnf6dA","jabatan","Analis Kebijakan Ahli Muda"]
~WyJNNW81SnZyU0ZpeHZvUjNLZWk1VTFnIiwidW5pdF9rZXJqYSIsIkRpcmVrdG9yYXQgSmFiYXRhbiBBU04iXQ
  ["M5o5JvrSFixvoR3Kei5U1g","unit_kerja","Direktorat Jabatan ASN"]
~WyJSb1o4SHRpMk9JVkJ4NHlNd3Q0UkZRIiwiaW5zdGFuc2kiLCJCYWRhbiBLZXBlZ2F3YWlhbiBOZWdhcmEiXQ
  ["RoZ8Hti2OIVBx4yMwt4RFQ","instansi","Badan Kepegawaian Negara"]
~WyJNa0FESE9vcHFJSGJvbEJISHVBNmNnIiwiZm90byIsImRhdGE6aW1hZ2UvanBlZztiYXNlNjQsLzlqLzRBQVFTa1pKUmdBQkFRRUFZQUJnQUFELzJ3QkRBQWdHQmdjR0JRZ0hCd2NKQ1FnS0RCUU5EQXNMREJrU0V3OFVIUm9mSGgwYUhCd2dKQzRuSUNJc0l4d2NLRGNwTERBeE5EUTBIeWM1UFRneVBDNHpOREwvd0FBTENBQUJBQUVCQVJFQS84UUFGQUFCQUFBQUFBQUFBQUFBQUFBQUFBQUFDZi9FQUJRUUFRQUFBQUFBQUFBQUFBQUFBQUFBQUFELzJnQUlBUUVBQUQ4QUtwLy8yUT09Il0
  ["MkADHOopqIHbolBHHuA6cg","foto","data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/wAALCAABAAEBAREA/8QAFAABAAAAAAAAAAAAAAAAAAAACf/EABQQAQAAAAAAAAAAAAAAAAAAAAD/2gAIAQEAAD8AKp//2Q=="]
```

### A KTP Digital as an mdoc {#ts-5-10-a-ktp-digital-as-an-mdoc}

A second type, in the representation a verifier reads in proximity. This is the
`IssuerSigned` structure as the wallet stores it, in full:

``` { .text title="The mdoc IssuerSigned, as issued" data-format="CBOR" }
a26a697373756572417574688443a10126a118215902ae308202aa30820250a003020102020c
16a98534626a68b21d10c09b300a06082a8648ce3d0403023059310b30090603550406130249
44312b3029060355040a0c22547275737420417574686f726974792052657075626c696b2049
6e646f6e65736961311d301b06035504030c1449444354462049737375657220526f6f742043
41301e170d3236303930313030303030305a170d3237313130313030303030305a307c310b30
09060355040613024944313e303c060355040a0c35446972656b746f726174204a656e646572
616c204b6570656e647564756b616e2064616e2050656e6361746174616e20536970696c312d
302b06035504030c2444756b636170696c206d646f6320446f63756d656e74205369676e6572
20323032362d413059301306072a8648ce3d020106082a8648ce3d03010703420004d186cc63
6737d34188257ae33074ea8b1f40a38e31276be9bf54e81a26345ca304c7d8adf082ebb7b050
041778ec0ce19f143e4076197c026a331f532fa78364a381da3081d7300c0603551d130101ff
04023000300e0603551d0f0101ff04040302078030150603551d250101ff040b300906072881
8c5d050102301f0603551d23041830168014fbf0d56ab0bfda804a32eddd33ccc9ddd283799a
301d0603551d0e04160414eeadd07e695e6a68950188f2cf92e6c566c9a8dd301e0603551d12
04173015861368747470733a2f2f74727573742e676f2e696430400603551d1f043930373035
a033a031862f68747470733a2f2f72656769737472792e74727573742e676f2e69642f63726c
2f6973737565722d726f6f742d6361300a06082a8648ce3d040302034800304502201edae3b5
dac8d94c01debc4e8d305f3c7e3a90701d8722fc55aa28a9be90ca69022100e1f31e36a6b297
303e3a8bcbe00d397d45ab75f6f97b22a0ecc5d353dd2bd8ef590482d81859047da766737461
747573a16b7374617475735f6c697374a2636964781a00075a8063757269782368747470733a
2f2f64756b636170696c2e676f2e69642f7374617475732f6b74702d3767646f63547970656e
69642e69646374662e6b74702e316776657273696f6e63312e306c76616c6964697479496e66
6fa3667369676e6564c074323032362d31302d31375430363a30303a31305a6976616c696446
726f6dc074323032362d31302d31375430363a30303a31305a6a76616c6964556e74696cc074
323032372d30312d31355430363a30303a31305a6c76616c756544696765737473a16e69642e
69646374662e6b74702e31b41a1eae7aca5820969d6b9f8caa888adeb8511704351b467c4b15
f1a8d0bf742d7c4b81c41c52d51a2a153b8f5820d3d5963f3eaaabcd9934287091b698d0191d
4560b272706c65bcac4187fdf5bd1a305148c5582033f032060e3078ab96b4a75966d14a8a11
163607158b61b5e0907c28ffe31ec41a3df00192582071234abfed33dacc47a2404b3a27ed46
d3fa3e95628195c0aa7597346a3432031a3f3e48cb58207232a83d154a2985fd0edad4b60ad4
af1a12a3ff9e3aee98433753a0ca6f0ff71a4282129c5820ad9c266608d711d800a1cca8f38e
c66af1291b33ba999902bd0923731b1c62a01a4a29657d5820b98635a8c8af79dcbd2643bd1a
b02ae6936b510a4f06ec167fb697ff4a6a5adb1a5a29effe58209568842eaae203290039cc50
7e59b5f1d6c6fb34a26662d2c4c7218762c5c6ce1a5bc6a7d35820fb441e9a38cf10d9185e5b
cefdd8299f3185a582dc25a2228e6752849332ae391a6512f3795820459eb92c0576083efdf0
79bc2cdcaa8ca73b17a403ff80d74eb094d5982d71a81a69eae2365820b88abb8ed9ba4fcbc2
f9ad23372a7d14a696edf9f26c6523428a26f427b71dc41a6a5c174b5820a3f6dbb37157efdb
b00010f95ce5e61af30520017eb7e8ae26930242b5ca4cac1a6d4bbc005820d0de7fa5c7c564
5872f3e4d1333226cb9efe9398ed4399437dd525305b9be8691a6e4a87475820909e6f33c99a
5057c507e626fa93db18aa966eaf79b27117ef6040e4528acd8a1a7174245c5820e0421c7acb
5c6ce84a4d9d8fac575cec4cba3d934b5560c75df632a187e18ecd1a71864e715820aeb439ba
aa64f3dc57bc818ee92c7b8cc10e6d0abe1f7bd7a5847b00ed51cfa41a736348c95820d0d95b
c8a974e5ea4df2c46dcffd259fbe46cdea94f3a07f1c54d8d447c29f211a79bc264d5820c280
534630b1a8c1632d1f9c4480e7841a35135eb363f2b8bf6d41531ebb177f1a7b134d3b5820a0
75f55adbf32598926cf59efb120270a9d4f5e199dbd42e88547a950afe5f061a7e81a8d65820
0a641643c3d05b4092912a6b5b16db84f200731a5dda44d1731b2469c0cd96036d6465766963
654b6579496e666fa1696465766963654b6579a401022001215820dc23a1c4e78ec6904e8d42
60a9648053440001869882e80f549ff65f6a867647225820da4f7cf39e2907beee75d46f7bc3
b8920e6720f4fb123120a5b78aa962ee30416f646967657374416c676f726974686d67534841
2d323536584034f75e1ce8f1d897d0f7044679bcfcdfebc870c8cb17c8e431bd210b93db7507
3fe12adaba811ad5641fe245092a77d77f731967cc431b4d301c0d9ea1b72d146a6e616d6553
7061636573a16e69642e69646374662e6b74702e3194d818585ba46672616e646f6d5081f5f2
2818a83bdf839e4565ea4590566864696765737449441a6a5c174b6c656c656d656e7456616c
7565703331373430313532303139353030303371656c656d656e744964656e74696669657263
6e696bd818585da46672616e646f6d500dbbb070f43fe1dcb3145b8cf582d776686469676573
7449441a736348c96c656c656d656e7456616c75657152696e61204b617274696b6120536172
6971656c656d656e744964656e746966696572646e616d61d818585ba46672616e646f6d506f
6e11c8610fecb6bb143c3e564907b86864696765737449441a6d4bbc006c656c656d656e7456
616c7565674a616b6172746171656c656d656e744964656e7469666965726c74656d7061745f
6c61686972d8185862a46672616e646f6d50e15336da27bfcb551fdeaddd1874696968646967
65737449441a5a29effe6c656c656d656e7456616c7565d903ec6a313939352d30312d313271
656c656d656e744964656e7469666965726d74616e6767616c5f6c61686972d8185857a46672
616e646f6d50e22dfff74e8aa035175b4e2a29e897896864696765737449441a71864e716c65
6c656d656e7456616c7565f571656c656d656e744964656e7469666965726f757369615f6469
5f617461735f3137d818585ea46672616e646f6d50713ac10c6f40d4b9d249c9ad2c9e1f9368
64696765737449441a5bc6a7d36c656c656d656e7456616c756569504552454d5055414e7165
6c656d656e744964656e7469666965726d6a656e69735f6b656c616d696ed8185857a4667261
6e646f6d50ce252487a3ab5767f7b5d859fd370a3e6864696765737449441a3df001926c656c
656d656e7456616c7565614271656c656d656e744964656e7469666965726e676f6c6f6e6761
6e5f6461726168d8185864a46672616e646f6d5075e8c8d784a3f81d1e5fb8b96ca4ab1b6864
696765737449441a79bc264d6c656c656d656e7456616c7565764a616c616e204b656e616e67
61204e6f6d6f7220313271656c656d656e744964656e74696669657266616c616d6174d81858
54a46672616e646f6d502083912dcc83d1282059af664b9cb8fe6864696765737449441a6512
f3796c656c656d656e7456616c7565673030342f30303771656c656d656e744964656e746966
6965726572745f7277d8185860a46672616e646f6d506a1117b6b2c20a09323b1020e1438baa
6864696765737449441a1eae7aca6c656c656d656e7456616c75656a476f6e64616e67646961
71656c656d656e744964656e7469666965726e6b656c75726168616e5f64657361d8185858a4
6672616e646f6d50f7951c2e684abe9b11effe558bf7ae8a6864696765737449441a7174245c
6c656c656d656e7456616c7565674d656e74656e6771656c656d656e744964656e7469666965
72696b6563616d6174616ed8185863a46672616e646f6d50e49fd723c6cf6e449201a60231f7
af9e6864696765737449441a4a29657d6c656c656d656e7456616c75656d4a616b6172746120
507573617471656c656d656e744964656e7469666965726e6b616275706174656e5f6b6f7461
d818585ba46672616e646f6d502f85eb4474086989e829791131c959a8686469676573744944
1a2a153b8f6c656c656d656e7456616c75656b444b49204a616b6172746171656c656d656e74
4964656e7469666965726870726f76696e7369d8185852a46672616e646f6d5099c6154c0c41
c3b169d3d9e4645379266864696765737449441a3f3e48cb6c656c656d656e7456616c756565
49534c414d71656c656d656e744964656e746966696572656167616d61d8185864a46672616e
646f6d50792870492760192a7a1c40431634d8856864696765737449441a4282129c6c656c65
6d656e7456616c75656b42454c554d204b4157494e71656c656d656e744964656e7469666965
72717374617475735f7065726b6177696e616ed8185860a46672616e646f6d50791383134263
55d01a6a1c60752e9cd16864696765737449441a7e81a8d66c656c656d656e7456616c75656f
4b4152594157414e2053574153544171656c656d656e744964656e7469666965726970656b65
726a61616ed818585aa46672616e646f6d50f9646611eaa18ea5f59423437d26110568646967
65737449441a305148c56c656c656d656e7456616c756563574e4971656c656d656e74496465
6e7469666965726f6b6577617267616e6567617261616ed8185867a46672616e646f6d5032be
f7dd836dd6ee3b168b32754dffec6864696765737449441a69eae2366c656c656d656e745661
6c75656d4a414b4152544120505553415471656c656d656e744964656e746966696572727465
6d7061745f64696b656c7561726b616ed8185862a46672616e646f6d508f60d442ca76eb68ec
bea4b6846244236864696765737449441a6e4a87476c656c656d656e7456616c7565d903ec6a
323032302d30312d323871656c656d656e744964656e7469666965726d69737375616e63655f
64617465d81858eda46672616e646f6d5017dd402ae5505d63635fd23944d9ac4c6864696765
737449441a7b134d3b6c656c656d656e7456616c756558a0ffd8ffe000104a46494600010101
006000600000ffdb004300080606070605080707070909080a0c140d0c0b0b0c1912130f141d
1a1f1e1d1a1c1c20242e2720222c231c1c2837292c30313434341f27393d38323c2e333432ff
c0000b080001000101011100ffc40014000100000000000000000000000000000009ffc40014
100100000000000000000000000000000000ffda0008010100003f002a9fffd971656c656d65
6e744964656e74696669657264666f746f
```

The same bytes in Concise Binary Object Representation (CBOR) diagnostic
notation. `issuerAuth` is a `COSE_Sign1` of four members: the protected header,
the unprotected header carrying the Document Signer Certificate under label 33,
the payload, and the signature:

``` { .text title="The mdoc IssuerSigned, in CBOR diagnostic notation" data-format="CBOR diag" }
{
  "issuerAuth": [
    h'a10126',
    {
      33: h'308202aa30820250a003020102020c16a98534626a68b21d10c09b300a06082a8648ce3d0403023059310b3009060355040613024944312b3029060355040a0c22547275737420417574686f726974792052657075626c696b20496e646f6e65736961311d301b06035504030c1449444354462049737375657220526f6f74204341301e170d3236303930313030303030305a170d3237313130313030303030305a307c310b3009060355040613024944313e303c060355040a0c35446972656b746f726174204a656e646572616c204b6570656e647564756b616e2064616e2050656e6361746174616e20536970696c312d302b06035504030c2444756b636170696c206d646f6320446f63756d656e74205369676e657220323032362d413059301306072a8648ce3d020106082a8648ce3d03010703420004d186cc636737d34188257ae33074ea8b1f40a38e31276be9bf54e81a26345ca304c7d8adf082ebb7b050041778ec0ce19f143e4076197c026a331f532fa78364a381da3081d7300c0603551d130101ff04023000300e0603551d0f0101ff04040302078030150603551d250101ff040b3009060728818c5d050102301f0603551d23041830168014fbf0d56ab0bfda804a32eddd33ccc9ddd283799a301d0603551d0e04160414eeadd07e695e6a68950188f2cf92e6c566c9a8dd301e0603551d1204173015861368747470733a2f2f74727573742e676f2e696430400603551d1f043930373035a033a031862f68747470733a2f2f72656769737472792e74727573742e676f2e69642f63726c2f6973737565722d726f6f742d6361300a06082a8648ce3d040302034800304502201edae3b5dac8d94c01debc4e8d305f3c7e3a90701d8722fc55aa28a9be90ca69022100e1f31e36a6b297303e3a8bcbe00d397d45ab75f6f97b22a0ecc5d353dd2bd8ef'
    },
    h'd81859047da766737461747573a16b7374617475735f6c697374a2636964781a00075a8063757269782368747470733a2f2f64756b636170696c2e676f2e69642f7374617475732f6b74702d3767646f63547970656e69642e69646374662e6b74702e316776657273696f6e63312e306c76616c6964697479496e666fa3667369676e6564c074323032362d31302d31375430363a30303a31305a6976616c696446726f6dc074323032362d31302d31375430363a30303a31305a6a76616c6964556e74696cc074323032372d30312d31355430363a30303a31305a6c76616c756544696765737473a16e69642e69646374662e6b74702e31b41a1eae7aca5820969d6b9f8caa888adeb8511704351b467c4b15f1a8d0bf742d7c4b81c41c52d51a2a153b8f5820d3d5963f3eaaabcd9934287091b698d0191d4560b272706c65bcac4187fdf5bd1a305148c5582033f032060e3078ab96b4a75966d14a8a11163607158b61b5e0907c28ffe31ec41a3df00192582071234abfed33dacc47a2404b3a27ed46d3fa3e95628195c0aa7597346a3432031a3f3e48cb58207232a83d154a2985fd0edad4b60ad4af1a12a3ff9e3aee98433753a0ca6f0ff71a4282129c5820ad9c266608d711d800a1cca8f38ec66af1291b33ba999902bd0923731b1c62a01a4a29657d5820b98635a8c8af79dcbd2643bd1ab02ae6936b510a4f06ec167fb697ff4a6a5adb1a5a29effe58209568842eaae203290039cc507e59b5f1d6c6fb34a26662d2c4c7218762c5c6ce1a5bc6a7d35820fb441e9a38cf10d9185e5bcefdd8299f3185a582dc25a2228e6752849332ae391a6512f3795820459eb92c0576083efdf079bc2cdcaa8ca73b17a403ff80d74eb094d5982d71a81a69eae2365820b88abb8ed9ba4fcbc2f9ad23372a7d14a696edf9f26c6523428a26f427b71dc41a6a5c174b5820a3f6dbb37157efdbb00010f95ce5e61af30520017eb7e8ae26930242b5ca4cac1a6d4bbc005820d0de7fa5c7c5645872f3e4d1333226cb9efe9398ed4399437dd525305b9be8691a6e4a87475820909e6f33c99a5057c507e626fa93db18aa966eaf79b27117ef6040e4528acd8a1a7174245c5820e0421c7acb5c6ce84a4d9d8fac575cec4cba3d934b5560c75df632a187e18ecd1a71864e715820aeb439baaa64f3dc57bc818ee92c7b8cc10e6d0abe1f7bd7a5847b00ed51cfa41a736348c95820d0d95bc8a974e5ea4df2c46dcffd259fbe46cdea94f3a07f1c54d8d447c29f211a79bc264d5820c280534630b1a8c1632d1f9c4480e7841a35135eb363f2b8bf6d41531ebb177f1a7b134d3b5820a075f55adbf32598926cf59efb120270a9d4f5e199dbd42e88547a950afe5f061a7e81a8d658200a641643c3d05b4092912a6b5b16db84f200731a5dda44d1731b2469c0cd96036d6465766963654b6579496e666fa1696465766963654b6579a401022001215820dc23a1c4e78ec6904e8d4260a9648053440001869882e80f549ff65f6a867647225820da4f7cf39e2907beee75d46f7bc3b8920e6720f4fb123120a5b78aa962ee30416f646967657374416c676f726974686d675348412d323536',
    h'34f75e1ce8f1d897d0f7044679bcfcdfebc870c8cb17c8e431bd210b93db75073fe12adaba811ad5641fe245092a77d77f731967cc431b4d301c0d9ea1b72d14'
  ],
  "nameSpaces": {
    "id.idctf.ktp.1": [
      24(<< {
        "random": h'81f5f22818a83bdf839e4565ea459056',
        "digestID": 1784420171,
        "elementValue": "3174015201950003",
        "elementIdentifier": "nik"
      } >>),
      24(<< {
        "random": h'0dbbb070f43fe1dcb3145b8cf582d776',
        "digestID": 1935886537,
        "elementValue": "Rina Kartika Sari",
        "elementIdentifier": "nama"
      } >>),
      24(<< {
        "random": h'6f6e11c8610fecb6bb143c3e564907b8',
        "digestID": 1833679872,
        "elementValue": "Jakarta",
        "elementIdentifier": "tempat_lahir"
      } >>),
      24(<< {
        "random": h'e15336da27bfcb551fdeaddd18746969',
        "digestID": 1512697854,
        "elementValue": 1004("1995-01-12"),
        "elementIdentifier": "tanggal_lahir"
      } >>),
      24(<< {
        "random": h'e22dfff74e8aa035175b4e2a29e89789',
        "digestID": 1904627313,
        "elementValue": true,
        "elementIdentifier": "usia_di_atas_17"
      } >>),
      24(<< {
        "random": h'713ac10c6f40d4b9d249c9ad2c9e1f93',
        "digestID": 1539745747,
        "elementValue": "PEREMPUAN",
        "elementIdentifier": "jenis_kelamin"
      } >>),
      24(<< {
        "random": h'ce252487a3ab5767f7b5d859fd370a3e',
        "digestID": 1039139218,
        "elementValue": "B",
        "elementIdentifier": "golongan_darah"
      } >>),
      24(<< {
        "random": h'75e8c8d784a3f81d1e5fb8b96ca4ab1b',
        "digestID": 2042373709,
        "elementValue": "Jalan Kenanga Nomor 12",
        "elementIdentifier": "alamat"
      } >>),
      24(<< {
        "random": h'2083912dcc83d1282059af664b9cb8fe',
        "digestID": 1695740793,
        "elementValue": "004/007",
        "elementIdentifier": "rt_rw"
      } >>),
      24(<< {
        "random": h'6a1117b6b2c20a09323b1020e1438baa',
        "digestID": 514751178,
        "elementValue": "Gondangdia",
        "elementIdentifier": "kelurahan_desa"
      } >>),
      24(<< {
        "random": h'f7951c2e684abe9b11effe558bf7ae8a',
        "digestID": 1903436892,
        "elementValue": "Menteng",
        "elementIdentifier": "kecamatan"
      } >>),
      24(<< {
        "random": h'e49fd723c6cf6e449201a60231f7af9e',
        "digestID": 1244226941,
        "elementValue": "Jakarta Pusat",
        "elementIdentifier": "kabupaten_kota"
      } >>),
      24(<< {
        "random": h'2f85eb4474086989e829791131c959a8',
        "digestID": 706034575,
        "elementValue": "DKI Jakarta",
        "elementIdentifier": "provinsi"
      } >>),
      24(<< {
        "random": h'99c6154c0c41c3b169d3d9e464537926',
        "digestID": 1061046475,
        "elementValue": "ISLAM",
        "elementIdentifier": "agama"
      } >>),
      24(<< {
        "random": h'792870492760192a7a1c40431634d885',
        "digestID": 1115820700,
        "elementValue": "BELUM KAWIN",
        "elementIdentifier": "status_perkawinan"
      } >>),
      24(<< {
        "random": h'79138313426355d01a6a1c60752e9cd1',
        "digestID": 2122426582,
        "elementValue": "KARYAWAN SWASTA",
        "elementIdentifier": "pekerjaan"
      } >>),
      24(<< {
        "random": h'f9646611eaa18ea5f59423437d261105',
        "digestID": 810633413,
        "elementValue": "WNI",
        "elementIdentifier": "kewarganegaraan"
      } >>),
      24(<< {
        "random": h'32bef7dd836dd6ee3b168b32754dffec',
        "digestID": 1777001014,
        "elementValue": "JAKARTA PUSAT",
        "elementIdentifier": "tempat_dikeluarkan"
      } >>),
      24(<< {
        "random": h'8f60d442ca76eb68ecbea4b684624423',
        "digestID": 1850378055,
        "elementValue": 1004("2020-01-28"),
        "elementIdentifier": "issuance_date"
      } >>),
      24(<< {
        "random": h'17dd402ae5505d63635fd23944d9ac4c',
        "digestID": 2064862523,
        "elementValue": h'ffd8ffe000104a46494600010101006000600000ffdb004300080606070605080707070909080a0c140d0c0b0b0c1912130f141d1a1f1e1d1a1c1c20242e2720222c231c1c2837292c30313434341f27393d38323c2e333432ffc0000b080001000101011100ffc40014000100000000000000000000000000000009ffc40014100100000000000000000000000000000000ffda0008010100003f002a9fffd9',
        "elementIdentifier": "foto"
      } >>)
    ]
  }
}
```

The payload of that `COSE_Sign1`, decoded, is the Mobile Security Object:

``` { .text title="The Mobile Security Object" data-format="CBOR diag" }
{
  "status": {
    "status_list": {
      "idx": 481920,
      "uri": "https://dukcapil.go.id/status/ktp-7"
    }
  },
  "docType": "id.idctf.ktp.1",
  "version": "1.0",
  "validityInfo": {
    "signed": 0("2026-10-17T06:00:10Z"),
    "validFrom": 0("2026-10-17T06:00:10Z"),
    "validUntil": 0("2027-01-15T06:00:10Z")
  },
  "valueDigests": {
    "id.idctf.ktp.1": {
      514751178: h'969d6b9f8caa888adeb8511704351b467c4b15f1a8d0bf742d7c4b81c41c52d5',
      706034575: h'd3d5963f3eaaabcd9934287091b698d0191d4560b272706c65bcac4187fdf5bd',
      810633413: h'33f032060e3078ab96b4a75966d14a8a11163607158b61b5e0907c28ffe31ec4',
      1039139218: h'71234abfed33dacc47a2404b3a27ed46d3fa3e95628195c0aa7597346a343203',
      1061046475: h'7232a83d154a2985fd0edad4b60ad4af1a12a3ff9e3aee98433753a0ca6f0ff7',
      1115820700: h'ad9c266608d711d800a1cca8f38ec66af1291b33ba999902bd0923731b1c62a0',
      1244226941: h'b98635a8c8af79dcbd2643bd1ab02ae6936b510a4f06ec167fb697ff4a6a5adb',
      1512697854: h'9568842eaae203290039cc507e59b5f1d6c6fb34a26662d2c4c7218762c5c6ce',
      1539745747: h'fb441e9a38cf10d9185e5bcefdd8299f3185a582dc25a2228e6752849332ae39',
      1695740793: h'459eb92c0576083efdf079bc2cdcaa8ca73b17a403ff80d74eb094d5982d71a8',
      1777001014: h'b88abb8ed9ba4fcbc2f9ad23372a7d14a696edf9f26c6523428a26f427b71dc4',
      1784420171: h'a3f6dbb37157efdbb00010f95ce5e61af30520017eb7e8ae26930242b5ca4cac',
      1833679872: h'd0de7fa5c7c5645872f3e4d1333226cb9efe9398ed4399437dd525305b9be869',
      1850378055: h'909e6f33c99a5057c507e626fa93db18aa966eaf79b27117ef6040e4528acd8a',
      1903436892: h'e0421c7acb5c6ce84a4d9d8fac575cec4cba3d934b5560c75df632a187e18ecd',
      1904627313: h'aeb439baaa64f3dc57bc818ee92c7b8cc10e6d0abe1f7bd7a5847b00ed51cfa4',
      1935886537: h'd0d95bc8a974e5ea4df2c46dcffd259fbe46cdea94f3a07f1c54d8d447c29f21',
      2042373709: h'c280534630b1a8c1632d1f9c4480e7841a35135eb363f2b8bf6d41531ebb177f',
      2064862523: h'a075f55adbf32598926cf59efb120270a9d4f5e199dbd42e88547a950afe5f06',
      2122426582: h'0a641643c3d05b4092912a6b5b16db84f200731a5dda44d1731b2469c0cd9603'
    }
  },
  "deviceKeyInfo": {
    "deviceKey": {
      1: 2,
      -1: 1,
      -2: h'dc23a1c4e78ec6904e8d4260a9648053440001869882e80f549ff65f6a867647',
      -3: h'da4f7cf39e2907beee75d46f7bc3b8920e6720f4fb123120a5b78aa962ee3041'
    }
  },
  "digestAlgorithm": "SHA-256"
}
```

### A Kartu Nikah as an `ldp_vc` {#ts-5-10-a-kartu-nikah-as-an-ldp-vc}

A third type, from a second Attribute Issuer, in the representation that carries
no selective disclosure. Its claims are open or normal throughout, which is what
lets its Credential Rulebook name `ldp_vc` at all:

``` { .json title="A Kartu Nikah in ldp_vc, as issued" data-format="JSON-LD" }
{
  "@context": [
    "https://www.w3.org/ns/credentials/v2",
    "https://catalog.trust.go.id/type-metadata/kartu-nikah-v1/context.jsonld"
  ],
  "type": [
    "VerifiableCredential",
    "KartuNikah"
  ],
  "issuer": "did:webvh:QmbAb7u9RMjqsZ9L98pe47szJZdnKQLh9KizqNW2WwKac1:kemenag.go.id",
  "validFrom": "2026-10-17T06:00:10Z",
  "validUntil": "2027-10-17T06:00:10Z",
  "credentialSubject": {
    "id": "did:key:zDnaexUcd7ETfUxHRrCKpKq7tYbfJCH1AWNN5WDppWYj2RS7Q",
    "nama_suami": "Arif Setiawan Nugroho",
    "nama_istri": "Nurul Aini Safitri",
    "tanggal_akad": "2025-05-17",
    "nomor_akta_nikah": "0123/0007/V/2025",
    "kua": "KUA Kec. Cibinong",
    "kabupaten_kota": "Kabupaten Bogor",
    "provinsi": "Jawa Barat",
    "foto_suami": "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/wAALCAABAAEBAREA/8QAFAABAAAAAAAAAAAAAAAAAAAACf/EABQQAQAAAAAAAAAAAAAAAAAAAAD/2gAIAQEAAD8AKp//2Q==",
    "foto_istri": "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/wAALCAABAAEBAREA/8QAFAABAAAAAAAAAAAAAAAAAAAACf/EABQQAQAAAAAAAAAAAAAAAAAAAAD/2gAIAQEAAD8AKp//2Q=="
  },
  "credentialStatus": [
    {
      "id": "https://kemenag.go.id/status/kartu-nikah-1-revocation#481920",
      "type": "BitstringStatusListEntry",
      "statusPurpose": "revocation",
      "statusListIndex": "481920",
      "statusListCredential": "https://kemenag.go.id/status/kartu-nikah-1-revocation"
    },
    {
      "id": "https://kemenag.go.id/status/kartu-nikah-1-suspension#481920",
      "type": "BitstringStatusListEntry",
      "statusPurpose": "suspension",
      "statusListIndex": "481920",
      "statusListCredential": "https://kemenag.go.id/status/kartu-nikah-1-suspension"
    }
  ],
  "credentialSchema": {
    "id": "https://catalog.trust.go.id/type-metadata/kartu-nikah-v1/credential-schema.json",
    "type": "JsonSchema",
    "digestSRI": "sha384-ZgGlm2JwrvKbb05pUITOcjghTRr1ImjyhgXstLXKDA/j2LzIwpgUSZwbk7ABXxpn"
  },
  "proof": {
    "type": "DataIntegrityProof",
    "cryptosuite": "ecdsa-rdfc-2019",
    "created": "2026-10-17T06:00:10Z",
    "verificationMethod": "did:webvh:QmbAb7u9RMjqsZ9L98pe47szJZdnKQLh9KizqNW2WwKac1:kemenag.go.id#issuance-jose-1",
    "proofPurpose": "assertionMethod",
    "proofValue": "z23RrsniSuQSX6EgQ5VByC1PYJhY8P9TFupfVXiJoiaaEqdDKYrXj36hFVXaUUinQVoRNfLrWGodfjWM9XCqRaQao"
  }
}
```

## Choosing the representations {#ts-5-10-choosing-the-representations}

A credential type is issued in the representations its Credential Rulebook
names, and in no other. The Rulebook is the only place the choice is written
down, so an issuer cannot add a representation for one citizen and withhold it
from another.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-10-004 }**REQ-TS-5-10-004** Issuer Core MUST issue a credential in every representation the type's Credential Rulebook names under `formats`.
- [](){ #req-ts-5-10-005 }**REQ-TS-5-10-005** Issuer Core MUST NOT issue a credential in a representation that Rulebook does not name.
- [](){ #req-ts-5-10-006 }**REQ-TS-5-10-006** An Identity Issuer's Issuer Core MUST NOT issue a credential as `ldp_vc`, because a basic identity credential carries a restricted attribute and `ecdsa-rdfc-2019` discloses the whole document.
- [](){ #req-ts-5-10-007 }**REQ-TS-5-10-007** Issuer Core MUST bind every representation of one credential to the same credential key.
- [](){ #req-ts-5-10-008 }**REQ-TS-5-10-008** Issuer Core MUST give every representation of one credential the same claim values.
- [](){ #req-ts-5-10-009 }**REQ-TS-5-10-009** Issuer Core MUST give every representation of one credential the same status list index on the same list, so that revoking the credential revokes all of it.
- [](){ #req-ts-5-10-010 }**REQ-TS-5-10-010** Issuer Core MUST give every representation of one credential the same technical validity period.

</div>

Which representations an issuer offers for a type, and how they reach a wallet
in one exchange, belong to
[Issuing a credential via OpenID4VCI](issuing-a-credential-via-openid4vci.md):
the issuer announces them in `credential_configurations_supported`, and a wallet
that received one representation of a credential and not the other has a
credential it cannot present in both modes.

## The SD-JWT VC representation {#ts-5-10-the-sd-jwt-vc-representation}

An SD-JWT VC is a JSON Web Signature in compact serialization as
[RFC 7515][ref-rfc7515] defines it, over a claims set as
[RFC 7519][ref-rfc7519] defines it, followed by the disclosures.
[SD-JWT VC][ref-i-d-ietf-oauth-sd-jwt-vc] defines the claims that make
it a credential, and [RFC 9901][ref-rfc9901] defines the digests and disclosures
that make its claims selectively disclosable.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-10-011 }**REQ-TS-5-10-011** The issuer-signed part MUST be a JSON Web Signature in compact serialization.
- [](){ #req-ts-5-10-012 }**REQ-TS-5-10-012** The `typ` header parameter MUST be `dc+sd-jwt`.
- [](){ #req-ts-5-10-013 }**REQ-TS-5-10-013** The `alg` header parameter MUST be one the Governance Profile allows for an issuance key.
- [](){ #req-ts-5-10-014 }**REQ-TS-5-10-014** *Withdrawn: [REQ-TS-01-033][req-ts-01-033] covers it.*
- [](){ #req-ts-5-10-015 }**REQ-TS-5-10-015** The `kid` header parameter MUST name a key of the purpose `issuance-jose`, as [Naming the key][ts-01-naming-the-key] of TS-01 requires.
- [](){ #req-ts-5-10-016 }**REQ-TS-5-10-016** The header MUST carry `typ`, `alg` and `kid` and no other parameter.

</div>

### The claims of an SD-JWT VC {#ts-5-10-the-claims-of-an-sd-jwt-vc}

[The table of SD-JWT VC claims][tbl-ts-5-10-sd-jwt-claims] gives every claim the
issuer-signed part carries. The type claims of the credential are not among
them: each one travels as a disclosure, and only its digest is signed.

[](){ #tbl-ts-5-10-sd-jwt-claims }

<figure markdown="1" class="ekdn-table">

| Claim | Type | Presence | What it carries |
|---|---|---|---|
| `iss` | string | Present | The `did:webvh` of the issuer |
| `vct` | string | Present | The `id` of the Credential Rulebook that governs the type, or, for a type another body named, that body's name |
| `cnf` | object | Present | The credential key, under `jwk` |
| `_sd_alg` | string | Present | The hash the digests in `_sd` were taken with |
| `_sd` | array of strings | Present | One digest per type claim |
| `status` | object | Present | The credential's entry in the issuer's status list |
| `nbf` | number | Present | The start of the credential's technical validity period |
| `iat` | number | Present | The moment Issuer Core signed |
| `exp` | number | Present | The end of the credential's technical validity period |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-10-017 }**REQ-TS-5-10-017** Issuer Core MUST include every claim [the table of SD-JWT VC claims][tbl-ts-5-10-sd-jwt-claims] lists.
- [](){ #req-ts-5-10-018 }**REQ-TS-5-10-018** Issuer Core MUST NOT include a claim [the table of SD-JWT VC claims][tbl-ts-5-10-sd-jwt-claims] does not list in the issuer-signed part.
- [](){ #req-ts-5-10-019 }**REQ-TS-5-10-019** `iss` MUST be the bare `did:webvh` of the issuer, with no query and no fragment.
- [](){ #req-ts-5-10-020 }**REQ-TS-5-10-020** `vct` MUST equal the `id` of the type's Credential Rulebook, except for a type [REQ-CR-005][req-cr-005] covers, whose `vct` is the name that body gave it.
- [](){ #req-ts-5-10-021 }**REQ-TS-5-10-021** Issuer Core MUST NOT include a `sub` claim, because the holder is identified by `cnf` and a second identifier would be a second thing to correlate on.
- [](){ #req-ts-5-10-022 }**REQ-TS-5-10-022** `nbf` MUST be the start of the credential's technical validity period.
- [](){ #req-ts-5-10-023 }**REQ-TS-5-10-023** `nbf` MUST NOT be earlier than `iat`, because a credential cannot be usable before it was signed.
- [](){ #req-ts-5-10-024 }**REQ-TS-5-10-024** Issuer Core MUST NOT place a type claim in the issuer-signed part in the clear where the type's Type Metadata sets `sd` to `always` for it.

</div>

### Disclosures and selective disclosure {#ts-5-10-disclosures-and-selective-disclosure}

Every attribute of a type carries an `sd` flag in its Type Metadata, and it is
`always` whatever the attribute's minimization class, as
[the schema in each format][schema-in-each-format] requires. Every type claim
is therefore selectively disclosable and none of them travels in the clear, so
the issuer makes no choice here and two issuers of one type cannot disclose
differently. Issuer Core builds one disclosure per type claim and signs its
digest.

1. **Draw a salt.** Issuer Core draws fresh random bytes for this claim and no
   other.
2. **Build the array.** The salt, the claim name, and the value, in that order,
   as a JSON array with no whitespace between its members.
3. **Encode it.** The array is serialized in UTF-8 and encoded with base64url as
   [RFC 4648][ref-rfc4648] section 5 defines it, with no padding. That string is
   the disclosure.
4. **Digest it.** The digest is the hash of the ASCII bytes of that string, under
   the algorithm `_sd_alg` names, encoded with base64url.
5. **Pad the count, where the type has an optional attribute.** A credential
   that carries a digest per claim it holds tells a verifier how many claims
   the citizen has, and for a type whose schema leaves an attribute out of
   `required` that count says whether the citizen has that attribute at all.
   Issuer Core adds decoy digests until the count is the same for every
   credential of the type.
6. **Collect the digests.** The digests go into `_sd`, sorted ascending.
   [RFC 9901][ref-rfc9901] section 4.2.4.1 requires the issuer to hide the
   original order of the claims and leaves the method open; sorting is the
   method IDCTF uses, because an Assessment Body can test it against the
   artifact alone, and a shuffle it cannot.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-10-025 }**REQ-TS-5-10-025** Issuer Core MUST build one disclosure for every type claim whose attribute the Type Metadata marks `sd: always` and whose value the source record holds.
- [](){ #req-ts-5-10-026 }**REQ-TS-5-10-026** A disclosure MUST be the base64url encoding, without padding, of a JSON array of exactly three members: the salt, the claim name, and the value.
- [](){ #req-ts-5-10-027 }**REQ-TS-5-10-027** Issuer Core MUST draw each salt from a cryptographically secure random number generator.
- [](){ #req-ts-5-10-028 }**REQ-TS-5-10-028** Each salt MUST carry at least 128 bits of randomness, which raises to a requirement the minimum [RFC 9901][ref-rfc9901] section 9.3 recommends.
- [](){ #req-ts-5-10-029 }**REQ-TS-5-10-029** Issuer Core MUST use a salt in one disclosure only, and never in a second disclosure of the same credential or of another credential.
- [](){ #req-ts-5-10-030 }**REQ-TS-5-10-030** `_sd_alg` MUST be `sha-256`.
- [](){ #req-ts-5-10-031 }**REQ-TS-5-10-031** Issuer Core MUST add decoy digests to `_sd` until the number of digests is the same in every credential of the type, where the type's schema does not list every attribute in `required`.
- [](){ #req-ts-5-10-032 }**REQ-TS-5-10-032** Issuer Core MUST NOT add a decoy digest where the type's schema lists every attribute in `required`, because the count is then fixed by the published Credential Rulebook and a decoy would only add bytes.
- [](){ #req-ts-5-10-033 }**REQ-TS-5-10-033** A decoy digest MUST be the digest, under the algorithm `_sd_alg` names, of a value drawn from a cryptographically secure random number generator.
- [](){ #req-ts-5-10-034 }**REQ-TS-5-10-034** Issuer Core MUST NOT place the same digest in `_sd` twice.
- [](){ #req-ts-5-10-035 }**REQ-TS-5-10-035** Issuer Core MUST sort the digests in `_sd` in ascending order of their encoded form.
- [](){ #req-ts-5-10-036 }**REQ-TS-5-10-036** Issuer Core MUST sort `_sd` after it has added every decoy digest, so that a decoy cannot be told from a real digest by its position.
- [](){ #req-ts-5-10-037 }**REQ-TS-5-10-037** Issuer Core MUST NOT use a recursive disclosure or an array-element disclosure, so that every disclosure stands on its own.

</div>

A value whose schema sets `contentEncoding: base64` travels as a data URI,
which [REQ-CR-070][req-cr-070] fixes for every SD-JWT VC.

None of the three illustrative types carries a decoy. The Kartu ASN and the
Kartu Nikah require every attribute of their schema, and the KTP Digital
requires every attribute of its own because [REQ-CR-077][req-cr-077] admits a
type as an mdoc on no other terms, so all three have the same digest count for
every citizen. The rule bites on a type whose schema leaves an attribute out
of `required`.

### Serialization {#ts-5-10-serialization}

The credential travels as one string. The issuer-signed JWT comes first, then
each disclosure, each introduced by a tilde, and the string ends with a tilde
that marks the place a Key Binding JWT takes at presentation time.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-10-038 }**REQ-TS-5-10-038** Issuer Core MUST serialize an issued SD-JWT VC as the issuer-signed JWT, then every disclosure, each preceded by `~`, and then a final `~`.
- [](){ #req-ts-5-10-039 }**REQ-TS-5-10-039** Issuer Core MUST NOT append a Key Binding JWT to an issued credential.
- [](){ #req-ts-5-10-040 }**REQ-TS-5-10-040** Mobile Wallet MUST store every disclosure it receives, because a disclosure it discards cannot be recovered from the credential.
- [](){ #req-ts-5-10-041 }**REQ-TS-5-10-041** Where a media type is carried for an issued SD-JWT VC, it MUST be `application/dc+sd-jwt`.

</div>

## The mdoc representation {#ts-5-10-the-mdoc-representation}

An mdoc is the `IssuerSigned` structure of the proximity standard, encoded in
CBOR as [RFC 8949][ref-rfc8949] defines it. It holds the claims as
`IssuerSignedItem` structures and a Mobile Security Object, signed as a
`COSE_Sign1` under [RFC 9052][ref-rfc9052], that digests each of them. No
registry names a media type for an mdoc standing on its own, so one that moves
over HTTP outside the issuance exchange carries `application/cbor`, the type
[ISO/IEC 18013-5][ref-iso-18013-5] gives the messages in which an mdoc already
travels.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-10-042 }**REQ-TS-5-10-042** An issued mdoc MUST be an `IssuerSigned` structure as [ISO/IEC 18013-5][ref-iso-18013-5] defines it, carrying `nameSpaces` and `issuerAuth`.
- [](){ #req-ts-5-10-043 }**REQ-TS-5-10-043** Issuer Core MUST place every data element of the credential in the one namespace [REQ-CR-061][req-cr-061] and [REQ-CR-080][req-cr-080] fix for the type.
- [](){ #req-ts-5-10-044 }**REQ-TS-5-10-044** Issuer Core MUST encode every CBOR structure of an mdoc with the deterministic encoding [ISO/IEC 18013-5][ref-iso-18013-5] requires, which orders the keys of a map by length and then by value.
- [](){ #req-ts-5-10-125 }**REQ-TS-5-10-125** Where a media type is carried for an issued mdoc, it MUST be `application/cbor`.

</div>

### Each claim as an IssuerSignedItem {#ts-5-10-each-claim-as-an-issuersigneditem}

One `IssuerSignedItem` carries one claim. The item is encoded, wrapped in CBOR
tag 24, and it is the tagged form that the digest is taken over, because it is
the tagged form that travels: a reader that digests the untagged item gets a
value that matches nothing.

The `digestID` is the key the item's digest sits under, and it is drawn at
random. [ISO/IEC 18013-5][ref-iso-18013-5] asks for no correlation between the
`digestID` values two Mobile Security Objects give the same claim, and this
specification makes that a requirement: a value a verifier can predict turns
`valueDigests` into a list of which claims a credential carries, including the
claims the holder withheld.

[](){ #tbl-ts-5-10-issuer-signed-item }

<figure markdown="1" class="ekdn-table">

| Field | Type | Presence | What it carries |
|---|---|---|---|
| `digestID` | `uint` | Present | The key this item's digest sits under in `valueDigests` |
| `random` | `bstr` | Present | Fresh random bytes, so a digest cannot be brute-forced back to its value |
| `elementIdentifier` | `tstr` | Present | The claim's name, as the Credential Rulebook spells it |
| `elementValue` | any | Present | The value, encoded as [the table of mdoc encodings][tbl-mdoc-encodings] sets out |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-10-045 }**REQ-TS-5-10-045** Issuer Core MUST build one `IssuerSignedItem` for every type claim the Credential Rulebook names and the source record holds.
- [](){ #req-ts-5-10-127 }**REQ-TS-5-10-127** Issuer Core MUST build an item for every attribute the type's schema requires, carrying the value [REQ-CR-077][req-cr-077] names where the source record holds none, so that two credentials of the type never differ in how many items they carry.
- [](){ #req-ts-5-10-046 }**REQ-TS-5-10-046** An `IssuerSignedItem` MUST carry every field [the table of an IssuerSignedItem][tbl-ts-5-10-issuer-signed-item] lists and no other field.
- [](){ #req-ts-5-10-047 }**REQ-TS-5-10-047** `random` MUST be at least sixteen bytes drawn from a cryptographically secure random number generator.
- [](){ #req-ts-5-10-048 }**REQ-TS-5-10-048** Issuer Core MUST use a `random` value in one item only.
- [](){ #req-ts-5-10-049 }**REQ-TS-5-10-049** `digestID` MUST be unique within its namespace.
- [](){ #req-ts-5-10-122 }**REQ-TS-5-10-122** Issuer Core MUST draw each `digestID` from a cryptographically secure random number generator, smaller than 2^31 as [ISO/IEC 18013-5][ref-iso-18013-5] requires.
- [](){ #req-ts-5-10-123 }**REQ-TS-5-10-123** Issuer Core MUST NOT number the items of a credential from zero in the order the Credential Rulebook lists the claims, because a run a verifier can predict names the claim behind every digest in `valueDigests`.
- [](){ #req-ts-5-10-124 }**REQ-TS-5-10-124** Issuer Core MUST draw the `digestID` values of each credential independently of every other credential it issues, so that one claim does not keep one `digestID` across credentials.
- [](){ #req-ts-5-10-050 }**REQ-TS-5-10-050** Issuer Core MUST encode `elementValue` as [the table of mdoc encodings][tbl-mdoc-encodings] sets out for the claim's schema type.
- [](){ #req-ts-5-10-051 }**REQ-TS-5-10-051** Issuer Core MUST place each item in `nameSpaces` wrapped in CBOR tag 24 over its encoded form.

</div>

### The Mobile Security Object {#ts-5-10-the-mobile-security-object}

The Mobile Security Object is what the issuer actually signs. It carries a
digest of every item, the credential key, the type, the validity period, and the
status entry.

[](){ #tbl-ts-5-10-mso }

<figure markdown="1" class="ekdn-table">

| Field | Type | Presence | What it carries |
|---|---|---|---|
| `version` | `tstr` | Present | `1.0` |
| `digestAlgorithm` | `tstr` | Present | `SHA-256` |
| `valueDigests` | map | Present | The digest of every item, by namespace and `digestID` |
| `deviceKeyInfo` | map | Present | The credential key, under `deviceKey`, as a COSE key |
| `docType` | `tstr` | Present | The `id` of the Credential Rulebook that governs the type, or, for a type another body named, that body's name |
| `validityInfo` | map | Present | `signed`, `validFrom` and `validUntil` |
| `status` | map | Present | The credential's entry in the issuer's status list |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-10-052 }**REQ-TS-5-10-052** The Mobile Security Object MUST carry every field [the table of the Mobile Security Object][tbl-ts-5-10-mso] lists and no other field.
- [](){ #req-ts-5-10-053 }**REQ-TS-5-10-053** `version` MUST be `1.0`.
- [](){ #req-ts-5-10-054 }**REQ-TS-5-10-054** `digestAlgorithm` MUST be `SHA-256`.
- [](){ #req-ts-5-10-055 }**REQ-TS-5-10-055** Each entry of `valueDigests` MUST be the digest of the encoded tag 24 form of its item, and not of the item itself.
- [](){ #req-ts-5-10-056 }**REQ-TS-5-10-056** `valueDigests` MUST hold one digest for every item in `nameSpaces` and no digest without an item.
- [](){ #req-ts-5-10-057 }**REQ-TS-5-10-057** `docType` MUST equal the `id` of the type's Credential Rulebook, except for a type [REQ-CR-005][req-cr-005] covers, whose `docType` is the name that body gave it.
- [](){ #req-ts-5-10-058 }**REQ-TS-5-10-058** `deviceKeyInfo` MUST carry `deviceKey`.
- [](){ #req-ts-5-10-059 }**REQ-TS-5-10-059** `deviceKeyInfo` MUST NOT carry `keyAuthorizations` or `keyInfo`, because the credential key is authorized for the whole credential and for nothing else.
- [](){ #req-ts-5-10-060 }**REQ-TS-5-10-060** Issuer Core MUST sign the Mobile Security Object wrapped in CBOR tag 24 over its encoded form.

</div>

### The issuerAuth signature {#ts-5-10-the-issuerauth-signature}

`issuerAuth` is a `COSE_Sign1` of four members. Its protected header carries the
algorithm and nothing else, and the Document Signer Certificate travels in the
unprotected header, in the `x5chain` parameter [RFC 9360][ref-rfc9360] registers
as label 33, where clause 9.1.2.4 of the proximity standard places it. A reader
that looks for the certificate in the protected header finds nothing, and JSON Object Signing and Encryption (JOSE)
habit is to look there.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-10-061 }**REQ-TS-5-10-061** `issuerAuth` MUST be a `COSE_Sign1` as [RFC 9052][ref-rfc9052] defines it, with the payload attached.
- [](){ #req-ts-5-10-062 }**REQ-TS-5-10-062** The protected header MUST carry label 1 and no other label.
- [](){ #req-ts-5-10-063 }**REQ-TS-5-10-063** Label 1 MUST name an algorithm the Governance Profile allows for an issuance key.
- [](){ #req-ts-5-10-064 }**REQ-TS-5-10-064** The unprotected header MUST carry label 33 holding the issuer's Document Signer Certificate in DER, as [REQ-TS-5-04-041][req-ts-5-04-041] requires.
- [](){ #req-ts-5-10-065 }**REQ-TS-5-10-065** The unprotected header MUST NOT carry any other label.
- [](){ #req-ts-5-10-066 }**REQ-TS-5-10-066** Issuer Core MUST sign an mdoc with the private key of the Document Signer Certificate in label 33, which is the key of the purpose `issuance-cose`.
- [](){ #req-ts-5-10-067 }**REQ-TS-5-10-067** Issuer Core MUST set `signed` to a moment inside the validity period of that Document Signer Certificate.
- [](){ #req-ts-5-10-068 }**REQ-TS-5-10-068** The external additional authenticated data of the signature MUST be empty.

</div>

## The `ldp_vc` representation {#ts-5-10-the-ldp-vc-representation}

An `ldp_vc` credential is a W3C VCDM 2.0 document secured with a
[Data Integrity][ref-vc-data-integrity] proof in the `ecdsa-rdfc-2019`
cryptosuite of [VC-DI-ECDSA][ref-vc-di-ecdsa], which signs the
[RDFC-1.0][ref-rdfc-1-0] canonicalization of the document's
[JSON-LD 1.1][ref-json-ld] expansion. The whole document is signed and nothing
in it can be withheld, which is why a Credential Rulebook that names `ldp_vc`
carries no restricted attribute and names no second representation. The proof
sits inside the document, so the credential is a VCDM 2.0 document on the wire
and carries that model's own media type, `application/vc`.

[](){ #tbl-ts-5-10-ldp-vc }

<figure markdown="1" class="ekdn-table">

| Member | Type | Presence | What it carries |
|---|---|---|---|
| `@context` | array of strings | Present | The VCDM 2.0 context, then the Rulebook's `formats.ldp_vc.context` |
| `type` | array of strings | Present | `VerifiableCredential`, then the Rulebook's `formats.ldp_vc.type` |
| `issuer` | string | Present | The `did:webvh` of the issuer |
| `validFrom` | string | Present | The start of the credential's technical validity period |
| `validUntil` | string | Present | The end of the credential's technical validity period |
| `credentialSubject` | object | Present | The holder's identifier under `id`, then one member per claim |
| `credentialStatus` | array of objects | Present | One entry per status purpose |
| `credentialSchema` | object | Present | The Rulebook's `credential_schema` and its digest |
| `proof` | object | Present | The Data Integrity proof |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-10-069 }**REQ-TS-5-10-069** An `ldp_vc` credential MUST carry every member [the table of an ldp_vc credential][tbl-ts-5-10-ldp-vc] lists.
- [](){ #req-ts-5-10-070 }**REQ-TS-5-10-070** `@context` MUST hold the W3C Verifiable Credentials Data Model 2.0 context first and the Rulebook's `formats.ldp_vc.context` second, and no other context.
- [](){ #req-ts-5-10-071 }**REQ-TS-5-10-071** `type` MUST hold `VerifiableCredential` first and the Rulebook's `formats.ldp_vc.type` second.
- [](){ #req-ts-5-10-072 }**REQ-TS-5-10-072** `issuer` MUST be the bare `did:webvh` of the issuer.
- [](){ #req-ts-5-10-073 }**REQ-TS-5-10-073** `credentialSubject.id` MUST be the holder identifier, as [The holder identifier][ts-5-03-the-holder-identifier] forms it.
- [](){ #req-ts-5-10-074 }**REQ-TS-5-10-074** Issuer Core MUST encode a value whose schema sets `contentEncoding: base64` as the base64 string that encoding names.
- [](){ #req-ts-5-10-075 }**REQ-TS-5-10-075** Issuer Core MUST NOT wrap such a value in a data URI, because the data URI form is the SD-JWT VC one.
- [](){ #req-ts-5-10-076 }**REQ-TS-5-10-076** The proof MUST be a Data Integrity proof with `cryptosuite` `ecdsa-rdfc-2019` and `proofPurpose` `assertionMethod`.
- [](){ #req-ts-5-10-077 }**REQ-TS-5-10-077** The `verificationMethod` of the proof MUST be the DID URL of a key of the purpose `issuance-jose` in the issuer's DID Document.
- [](){ #req-ts-5-10-078 }**REQ-TS-5-10-078** `created` MUST be the moment Issuer Core signed.
- [](){ #req-ts-5-10-079 }**REQ-TS-5-10-079** `created` MUST NOT be later than `validFrom`.
- [](){ #req-ts-5-10-080 }**REQ-TS-5-10-080** Issuer Core MUST NOT fetch a context while it signs.
- [](){ #req-ts-5-10-081 }**REQ-TS-5-10-081** Issuer Core MUST read every context from its own cache.
- [](){ #req-ts-5-10-126 }**REQ-TS-5-10-126** Where a media type is carried for an issued `ldp_vc` credential, it MUST be `application/vc`.
- [](){ #req-ts-5-10-135 }**REQ-TS-5-10-135** `credentialSchema` MUST be one [`JsonSchema`][ref-vc-json-schema] entry whose `id` is the Rulebook's `credential_schema` and whose `digestSRI` is the digest of that file.

</div>

`credentialSchema` carries the Rulebook's `credential_schema` with its digest,
which [REQ-TS-5-10-135][req-ts-5-10-135] fixes.

## Holder binding {#ts-5-10-holder-binding}

One wallet installation holds one credential key, and every credential it holds
is bound to that key, whatever the representation. The holder identifier is the
`did:key` of that key, as
[The holder identifier][ts-5-03-the-holder-identifier] forms it, and the three
representations write the binding down differently: two carry the key itself,
in the encoding their own standard uses for a key, and the third carries the
identifier. An `ldp_vc` credential names its holder and proves nothing about
who holds it, because its proof is the issuer's; the proof that the holder
holds the key is made at presentation time, as
[the three presentations compared][tbl-ts-5-11-three-presentations] sets out.
The key a credential is bound to is the one the Key Attestation of that
issuance attests, which [REQ-TS-5-08-062][req-ts-5-08-062] fixes.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-10-082 }**REQ-TS-5-10-082** In an SD-JWT VC, `cnf` MUST carry the credential key under `jwk`, as a JSON Web Key with `kty`, `crv`, `x` and `y` and no other member.
- [](){ #req-ts-5-10-083 }**REQ-TS-5-10-083** In an SD-JWT VC, `cnf` MUST NOT carry `kid`, `jwe`, or `jku`.
- [](){ #req-ts-5-10-084 }**REQ-TS-5-10-084** In an mdoc, `deviceKeyInfo.deviceKey` MUST carry the credential key as a COSE key.
- [](){ #req-ts-5-10-085 }**REQ-TS-5-10-085** In an `ldp_vc`, `credentialSubject.id` MUST carry the holder identifier of the credential key.
- [](){ #req-ts-5-10-086 }**REQ-TS-5-10-086** Issuer Core MUST NOT issue a credential bound to a key the wallet has not attested in the same exchange.

</div>

## The status pointer {#ts-5-10-the-status-pointer}

Every credential carries a pointer into a status list its issuer publishes, so
that a verifier can learn the credential was withdrawn before it expired. The
list itself, its format, its indices and how a reader decodes an entry are
[Publishing and reading a status list](publishing-and-reading-a-status-list.md);
what the credential carries is here.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-10-087 }**REQ-TS-5-10-087** Issuer Core MUST give every credential it issues a status pointer, whatever its type and whatever its representation.
- [](){ #req-ts-5-10-088 }**REQ-TS-5-10-088** In an SD-JWT VC and in an mdoc, the pointer MUST be a `status` member carrying `status_list` with `idx` and `uri`, as [IETF Token Status List draft -14][ref-i-d-ietf-oauth-status-list] defines it.
- [](){ #req-ts-5-10-089 }**REQ-TS-5-10-089** `uri` MUST be the address at which the issuer serves that list.
- [](){ #req-ts-5-10-090 }**REQ-TS-5-10-090** `uri` MUST equal the `sub` of the Status List Token served there.
- [](){ #req-ts-5-10-091 }**REQ-TS-5-10-091** `idx` MUST be the index the issuer allocated to this credential, drawn as [REQ-TS-5-09-032][req-ts-5-09-032] requires.
- [](){ #req-ts-5-10-092 }**REQ-TS-5-10-092** In an mdoc, `status` MUST sit in the Mobile Security Object, so that it is covered by `issuerAuth`.
- [](){ #req-ts-5-10-093 }**REQ-TS-5-10-093** In an `ldp_vc`, the pointer MUST be a `credentialStatus` array holding one `BitstringStatusListEntry` for the `revocation` purpose and one for the `suspension` purpose, as [REQ-TS-5-09-065][req-ts-5-09-065] requires.

</div>

Both entries of an `ldp_vc` carry one index, and no index is ever reused, which
[REQ-TS-5-09-066][req-ts-5-09-066] and [REQ-TS-5-09-031][req-ts-5-09-031] fix on
the publishing side.

## Validity periods {#ts-5-10-validity-periods}

A credential has two validity periods, as
[Expiry and validity periods][expiry-and-validity-periods] sets out. The
administrative period is the one the underlying document has in law, and where a
type has one it is a claim of the credential, named by the Credential Rulebook.
The technical period is how long this issued artifact may be presented, and it
is what the fields below carry. Every representation records two moments and
not one: when the issuer signed, and when the credential becomes usable. They
are usually the same moment, and an issuer that prepares a credential ahead of
the day it takes effect sets them apart. The technical period is the shorter of the two,
because a credential that outlives the document behind it states something that
is no longer true. [The table of validity fields][tbl-ts-5-10-validity] gives
the field each representation carries it in.

[](){ #tbl-ts-5-10-validity }

<figure markdown="1" class="ekdn-table">

| Representation | Start of the technical period | End of the technical period |
|---|---|---|
| SD-JWT VC | `nbf`, with `iat` beside it | `exp` |
| mdoc | `validFrom` of `validityInfo`, with `signed` beside it | `validUntil` of `validityInfo` |
| `ldp_vc` | `validFrom`, with `created` of the proof beside it | `validUntil` |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-10-094 }**REQ-TS-5-10-094** Issuer Core MUST NOT set the start of the technical validity period earlier than the moment it signed.
- [](){ #req-ts-5-10-095 }**REQ-TS-5-10-095** In an mdoc, `signed` MUST be the moment Issuer Core signed.
- [](){ #req-ts-5-10-096 }**REQ-TS-5-10-096** In an mdoc, `validFrom` MUST be the start of the technical validity period.
- [](){ #req-ts-5-10-097 }**REQ-TS-5-10-097** Issuer Core MUST set the end of the technical validity period no later than the ceiling the Governance Profile sets for the type.
- [](){ #req-ts-5-10-098 }**REQ-TS-5-10-098** Issuer Core MUST set the end of the technical validity period no later than the end of the credential's administrative validity period, where the type has one.
- [](){ #req-ts-5-10-099 }**REQ-TS-5-10-099** Issuer Core MAY set `validUntil` of an mdoc beyond the expiry of its Document Signer Certificate, because a reader checks the signing time against that certificate and not the presentation time.
- [](){ #req-ts-5-10-100 }**REQ-TS-5-10-100** In an mdoc, every member of `validityInfo` MUST be a `tdate`.
- [](){ #req-ts-5-10-101 }**REQ-TS-5-10-101** In an `ldp_vc`, `validFrom` and `validUntil` MUST be a date and time with an explicit `Z`.

</div>

## Reading a credential {#ts-5-10-reading-a-credential}

A reader checks the credential itself before it checks anything about the party
that presented it. These are the checks of the transaction chain that reach the
credential, T1 and T2 of
[entity chain and transaction chain][entity-chain-and-transaction-chain]; the
proof that the presenter holds the credential key is T3, which
[Building and verifying a presentation](building-and-verifying-a-presentation.md)
fixes. For an SD-JWT VC and an `ldp_vc` the reader also runs E3 of the entity
chain, in step 8, because those two name their issuer by a DID that an
Authority Statement can be asked about.

1. **Parse it.** The reader decodes the representation and refuses a credential
   it cannot decode, without reporting which field failed.
2. **Find the issuer's key.** For an SD-JWT VC and an `ldp_vc` the reader
   resolves the issuer's DID and takes the key `kid` or `verificationMethod`
   names, as
   [Finding the key][ts-01-finding-the-key] sets out. For an mdoc it takes the
   public key of the Document Signer Certificate in label 33 and validates that
   certificate, as
   [Validating a chain][ts-5-04-validating-a-chain] sets out.
3. **Verify the signature.** Over the issuer-signed JWT, over the
   `Sig_structure` of the `COSE_Sign1`, or over the canonicalized document and
   proof configuration.
4. **Recompute the digests.** For an SD-JWT VC, the digest of every disclosure
   received has to be in `_sd`. For an mdoc, the digest of every item received
   has to match its entry in `valueDigests`.
5. **Check the type.** `vct`, `docType` or `type` has to be the type the reader
   asked for.
6. **Check the validity period.** The present moment has to fall inside the
   technical validity period, and for an mdoc the signing time has to fall
   inside the validity period of the Document Signer Certificate.
7. **Check the status.** The reader reads the entry the status pointer names
   from its own cache and refuses a credential whose entry is not valid.
8. **Check the permission.** For an SD-JWT VC and an `ldp_vc`, the reader takes
   from its own cache the Authority Statement answer for the issuer's DID, the
   action `issue`, and the type and version the credential names, and the
   signing time, `iat` or the proof's `created`, has to fall inside one of the
   `periods` of that answer. An mdoc carries no DID, so E3 does not reach it;
   its issuer is checked by the chain to the Issuer Root CA, E4.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-10-102 }**REQ-TS-5-10-102** Mobile Wallet, Verifier Core and Mobile Verifier MUST verify the issuer's signature before it reads any claim of a credential.
- [](){ #req-ts-5-10-103 }**REQ-TS-5-10-103** Mobile Wallet, Verifier Core and Mobile Verifier MUST refuse a credential whose signature does not verify.
- [](){ #req-ts-5-10-104 }**REQ-TS-5-10-104** Mobile Wallet, Verifier Core and Mobile Verifier MUST refuse an SD-JWT VC whose `typ` is not `dc+sd-jwt`.
- [](){ #req-ts-5-10-105 }**REQ-TS-5-10-105** Mobile Wallet, Verifier Core and Mobile Verifier MUST recompute the digest of every disclosure it received.
- [](){ #req-ts-5-10-106 }**REQ-TS-5-10-106** Mobile Wallet, Verifier Core and Mobile Verifier MUST refuse the credential if the digest of a disclosure it received is absent from `_sd`.
- [](){ #req-ts-5-10-107 }**REQ-TS-5-10-107** Mobile Wallet, Verifier Core and Mobile Verifier MUST ignore a digest in `_sd` that matches no disclosure it received, because a decoy digest matches none by design.
- [](){ #req-ts-5-10-108 }**REQ-TS-5-10-108** Mobile Wallet, Verifier Core and Mobile Verifier MUST refuse a credential in which the same digest appears twice.
- [](){ #req-ts-5-10-109 }**REQ-TS-5-10-109** Mobile Wallet, Verifier Core and Mobile Verifier MUST refuse an SD-JWT VC that carries two disclosures for one claim name.
- [](){ #req-ts-5-10-110 }**REQ-TS-5-10-110** Mobile Wallet, Verifier Core and Mobile Verifier MUST recompute the digest of the encoded tag 24 form of every `IssuerSignedItem` it received.
- [](){ #req-ts-5-10-111 }**REQ-TS-5-10-111** Mobile Wallet, Verifier Core and Mobile Verifier MUST refuse the mdoc if the digest of an item it received does not match its entry in `valueDigests`.
- [](){ #req-ts-5-10-112 }**REQ-TS-5-10-112** Mobile Wallet, Verifier Core and Mobile Verifier MUST refuse an mdoc whose `docType` does not equal the namespace of the items it received, unless the Credential Rulebook names a separate `namespace`.
- [](){ #req-ts-5-10-113 }**REQ-TS-5-10-113** Mobile Wallet, Verifier Core and Mobile Verifier MUST read `x5chain` from the unprotected header of `issuerAuth`.
- [](){ #req-ts-5-10-114 }**REQ-TS-5-10-114** Mobile Wallet, Verifier Core and Mobile Verifier MUST refuse an mdoc whose `signed` falls outside the validity period of the Document Signer Certificate that signed it.
- [](){ #req-ts-5-10-115 }**REQ-TS-5-10-115** Mobile Wallet, Verifier Core and Mobile Verifier MUST refuse a credential presented before the start or after the end of its technical validity period.
- [](){ #req-ts-5-10-116 }**REQ-TS-5-10-116** Mobile Wallet, Verifier Core and Mobile Verifier MUST check every status entry the credential points at.
- [](){ #req-ts-5-10-117 }**REQ-TS-5-10-117** Mobile Wallet, Verifier Core and Mobile Verifier MUST refuse an SD-JWT VC or an mdoc whose status entry is not `0x00`.
- [](){ #req-ts-5-10-118 }**REQ-TS-5-10-118** Mobile Wallet, Verifier Core and Mobile Verifier MUST refuse an `ldp_vc` credential whose entry is set in either of the two lists its `credentialStatus` entries name.
- [](){ #req-ts-5-10-119 }**REQ-TS-5-10-119** Mobile Wallet, Verifier Core and Mobile Verifier MUST canonicalize an `ldp_vc` credential with RDFC-1.0 over its JSON-LD expansion, reading every context from its own cache.
- [](){ #req-ts-5-10-120 }**REQ-TS-5-10-120** Mobile Wallet, Verifier Core and Mobile Verifier MUST NOT fetch a status list, a schema, or a context while it verifies a credential.
- [](){ #req-ts-5-10-121 }**REQ-TS-5-10-121** Mobile Wallet, Verifier Core and Mobile Verifier MUST NOT report which check failed to the party that presented the credential, beyond that the credential was refused.
- [](){ #req-ts-5-10-131 }**REQ-TS-5-10-131** Mobile Wallet, Verifier Core and Mobile Verifier MUST check a cached context against the `context_digest` of the Rulebook that names it before it uses the context.
- [](){ #req-ts-5-10-132 }**REQ-TS-5-10-132** Mobile Wallet, Verifier Core and Mobile Verifier MUST refuse an `ldp_vc` credential whose `@context` names a context that is neither the [VCDM 2.0][ref-vc-data-2-0] context nor the `context` of a published Rulebook.
- [](){ #req-ts-5-10-133 }**REQ-TS-5-10-133** Mobile Wallet, Verifier Core and Mobile Verifier MUST NOT refuse a credential only because the permission to issue its version has been withdrawn.
- [](){ #req-ts-5-10-138 }**REQ-TS-5-10-138** Mobile Wallet, Verifier Core and Mobile Verifier MUST find the issuer's key of an `ldp_vc` credential as [Finding the key][ts-01-finding-the-key] of TS-01 requires, taking `kid` from the proof's `verificationMethod`, the signer's DID from `issuer`, and the time the credential states it was made from the proof's `created`.
- [](){ #req-ts-5-10-139 }**REQ-TS-5-10-139** Mobile Wallet, Verifier Core and Mobile Verifier MUST refuse an `ldp_vc` credential whose proof carries no `created`.
- [](){ #req-ts-5-10-140 }**REQ-TS-5-10-140** Mobile Wallet, Verifier Core and Mobile Verifier MUST refuse an `ldp_vc` credential whose proof has a `proofPurpose` other than `assertionMethod`.
- [](){ #req-ts-5-10-141 }**REQ-TS-5-10-141** Mobile Wallet, Verifier Core and Mobile Verifier MUST refuse an SD-JWT VC or an `ldp_vc` credential unless a cached Authority Statement answer for the issuer's DID, the action `issue` and the credential's `resource`, verified as [Reading the answer][ts-5-05-reading-the-answer] of TS-5-05 requires, holds in `periods` a period that contains the signing time.
- [](){ #req-ts-5-10-142 }**REQ-TS-5-10-142** The signing time of an SD-JWT VC MUST be its `iat`, and that of an `ldp_vc` credential the `created` of its proof.
- [](){ #req-ts-5-10-143 }**REQ-TS-5-10-143** A period MUST contain the signing time when `valid_from` is not later than it and `valid_until`, where the period carries one, is later than it.
- [](){ #req-ts-5-10-144 }**REQ-TS-5-10-144** Mobile Wallet, Verifier Core and Mobile Verifier MUST refuse an SD-JWT VC or an `ldp_vc` credential when its cache holds no such answer.
- [](){ #req-ts-5-10-145 }**REQ-TS-5-10-145** Mobile Wallet, Verifier Core and Mobile Verifier MUST NOT fetch an Authority Statement answer while they verify a credential.
- [](){ #req-ts-5-10-146 }**REQ-TS-5-10-146** Mobile Wallet, Verifier Core and Mobile Verifier MUST fill their cache at [trust cache sync][trust-cache-sync] with an answer for each issuer granted on the trusted list and for each type and version they accept.
- [](){ #req-ts-5-10-147 }**REQ-TS-5-10-147** The `resource` of an SD-JWT VC MUST be its `vct`, and that of an `ldp_vc` credential MUST be the `id` of the Credential Rulebook whose `formats.ldp_vc.context` is the second entry of its `@context`.

</div>

The version is named in the type identifier of an SD-JWT VC, whose `vct` is the
`id` of its Rulebook, and not in the `type` of an `ldp_vc`, which names the type
alone. A reader finds the version of an `ldp_vc` through its context, which each
Rulebook version defines for itself, and builds the `resource` the way
[Resources][ts-5-05-resources] of TS-5-05 forms one.

The step asks about the signing time and not about today, which keeps
[REQ-TS-5-10-133][req-ts-5-10-133] true. A withdrawal of the permission to
issue a version closes the period that was open, so a credential signed before
the withdrawal still falls inside that period, and a credential signed after it
falls inside none. A reader never asks the registry at verification time,
because [REQ-TS-5-10-120][req-ts-5-10-120] keeps it from fetching anything
then and a proximity check has no network to ask.

The card a wallet draws is not one of these checks, and a rendered card
proves nothing. A wallet draws the templates of a type, and its name, only for
a credential whose issuer the ecosystem's own roots vouch for; a credential
whose root reached the wallet through the [VICAL][vical] is drawn with the
issuer and the country its own attributes give.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-10-134 }**REQ-TS-5-10-134** Mobile Wallet MUST draw a type's `display[].rendering.svg_templates`, and the type's name from its [Type Metadata][ref-i-d-ietf-oauth-sd-jwt-vc], only for a credential whose signer chains to a root the Root Authority publishes.
- [](){ #req-ts-5-10-136 }**REQ-TS-5-10-136** Mobile Wallet MUST draw neither the templates nor the type's name for a credential of the same type whose root reached it through the [VICAL][vical].
- [](){ #req-ts-5-10-137 }**REQ-TS-5-10-137** Mobile Wallet MUST name the issuer and the country of such a credential from the credential's own attributes.

</div>

## Security considerations {#ts-5-10-security-considerations}

Each threat below is answered by the requirement named with it.

- **A digest taken over the wrong bytes passes nothing.** The commonest mdoc
  defect is digesting the `IssuerSignedItem` instead of its tag 24 form,
  which produces a credential that no conformant reader accepts and that an
  issuer's own tests pass if they make the same mistake on both sides.
  [REQ-TS-5-10-055][req-ts-5-10-055] and [REQ-TS-5-10-110][req-ts-5-10-110]
  state the rule for the writer and the reader separately, so a test can
  catch one without the other.
- **A guessable salt undoes selective disclosure.** A digest of a claim
  whose value comes from a small set, a blood type or a marital status, is a
  dictionary away from being recovered if the salt is short or predictable.
  The salt makes the digest unguessable, so
  [REQ-TS-5-10-027][req-ts-5-10-027] and [REQ-TS-5-10-028][req-ts-5-10-028]
  fix its source and its width, and [REQ-TS-5-10-047][req-ts-5-10-047] does
  the same for the `random` of an mdoc item.
- **The certificate in an mdoc is not a trust anchor.** Label 33 carries the
  Document Signer Certificate the issuer chose to send. It proves nothing
  until the reader validates it to the Issuer Root CA it already holds, or
  finds it through the VICAL. [REQ-TS-5-10-064][req-ts-5-10-064] fixes what
  travels and [Validating a chain][ts-5-04-validating-a-chain] fixes what
  the reader does with it.
- **An unverified context decides what the signature covers.** In
  `ecdsa-rdfc-2019` the signature is taken over the canonicalization of the
  expanded document, and the expansion depends on every context. A context
  fetched at verification time, or a context the issuer named freely, lets
  whoever serves that document change the meaning of a signed credential.
  [REQ-TS-5-10-080][req-ts-5-10-080], [REQ-TS-5-10-120][req-ts-5-10-120] and
  [REQ-TS-5-10-121][req-ts-5-10-121] close all three doors.
- **A credential copied off a device is inert.** Every representation binds
  the credential key, and nothing in a credential is useful to a party that
  cannot sign with it. That is why [REQ-TS-5-10-086][req-ts-5-10-086]
  refuses to issue against a key the wallet has not attested in the same
  exchange: an unattested key may already be in someone else's hands.
- **A long technical validity period is a long window.** A credential whose
  `exp` is years away is a credential a verifier accepts for years on the
  strength of a status list it may not have refreshed.
  [REQ-TS-5-10-097][req-ts-5-10-097] holds the period to the Governance
  Profile's ceiling, and the ceiling is what the Governance Profile has to
  set with the offline tolerance limit in mind.

## Privacy considerations {#ts-5-10-privacy-considerations}

Each exposure below is named with what bounds it.

- **One credential key means one identifier.** Every credential a wallet
  holds carries the same key, so two verifiers that compare notes can match
  the holder, as [the holder
  identifier][holder-one-didkey-per-wallet-installation] sets out. The
  ecosystem accepts that exposure; this specification does not widen it, and
  [REQ-TS-5-10-021][req-ts-5-10-021] refuses a `sub` claim that would add a
  second identifier to correlate on.
- **`ldp_vc` discloses everything.** A presentation of an `ldp_vc`
  credential carries every claim in it, because the proof covers the whole
  document. The ecosystem answers by keeping the format away from restricted
  attributes rather than by accepting the disclosure, which is what
  [REQ-TS-5-10-006][req-ts-5-10-006] and [REQ-CR-017][req-cr-017] enforce
  from two sides.
- **The number of claims is public; whether the citizen has one need not
  be.** A verifier that receives two disclosures learns how many digests it
  did not match. For a type whose schema requires every attribute, that
  count is the same for everyone and already public, because the Credential
  Rulebook lists the claims of the type. For a type with an optional
  attribute the count would say whether this citizen has it, which is the
  side channel [RFC 9901][ref-rfc9901] section 10.4 names.
  [REQ-TS-5-10-031][req-ts-5-10-031] pads the count with decoys where the
  type needs it, and [REQ-TS-5-10-032][req-ts-5-10-032] spends no bytes
  where it does not. None of the illustrative types needs it.
- **An mdoc closes the same count from the other side.** The `valueDigests`
  of a Mobile Security Object carry one digest per item in the same way, and
  ISO/IEC 18013-5 defines no decoy to pad the count with. The answer is the
  Rulebook rather than the credential: [REQ-CR-077][req-cr-077] admits an
  mdoc type only when its schema requires every attribute and names the value
  that stands for no value, so every credential of the type carries the same
  number of digests and a citizen with no blood type on record is not the one
  carrying fewer. [REQ-TS-5-10-122][req-ts-5-10-122] and
  [REQ-TS-5-10-123][req-ts-5-10-123] close the second half of it, where the
  key of a digest rather than the count of them would name the claim.
- **A status list index is a handle.** The index in a credential is stable
  for the life of that credential, and a verifier that records it can
  recognize the same credential later. The defense is on the publishing
  side, where [REQ-TS-5-09-032][req-ts-5-09-032] draws the index at random
  inside a large list so that it reveals nothing about when the credential
  was issued or by whom it was held.
- **An issuer learns nothing from a presentation.** Nothing in a credential
  points back at its issuer in a way that makes the issuer reachable during
  verification, and [REQ-TS-5-10-120][req-ts-5-10-120] forbids the fetch
  that would. An issuer that wanted a record of where its credentials are
  used would have to be asked, and no interface asks it.

## Changelog {#ts-5-10-changelog}

<figure markdown="1" class="ekdn-table">

| Version | Date | Change |
|---|---|---|
| 1.0 draft | 19 October 2026 | First draft |

</figure>
