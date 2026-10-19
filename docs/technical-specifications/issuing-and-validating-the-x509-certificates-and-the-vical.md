---
title: "[TS-5-04] Issuing and validating the X.509 certificates and the VICAL"
description: The profile of every X.509 certificate in the ecosystem, both roots, the Document Signer Certificate, the status list signer certificate, the Verifier Issuing CA and the Verifier Device Certificate, the two certificate revocation lists, and the VICAL that carries the issuer root to a reader abroad.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, Kep. 8, §4.6, §5.2, §5.3, §5.5, §5.7, §7.5; Panduan mdoc §2.3, §8, §9, Lampiran A; Bentuk Data Attestation §3; Rincian Module dan Operasi §2.1, §4, §8; tracks/0101, tracks/0107, tracks/0249, tracks/0327, tracks/0346, tracks/0370, tracks/0436 -->

<p class="ekdn-docid">TS-5-04</p>

# Issuing and validating the X.509 certificates and the VICAL {#ts-5-04-issuing-and-validating-the-x509-certificates-and-the-vical}

<p class="ekdn-lead" markdown="span">
Two roots that never sign each other, four leaves under them, the lists
that withdraw one early, and the Verified Issuer Certificate Authority List
(VICAL) that carries the issuer root to a reader which has never seen the
trusted list.
</p>

Every sentence on this page binds Trust Authority, Trust Registry, and every
Module that requests, holds, or checks a certificate, and an Assessment Body
tests them against it in the version the Governance Profile puts in force.
The key words and the identifier `REQ-TS-5-04-nnn` follow
[Common provisions](common-provisions.md).

## Who runs this and what it needs {#ts-5-04-who-runs-this-and-what-it-needs}

This specification fixes the profile of every X.509 certificate the
ecosystem issues, how each one is requested, issued, renewed, and withdrawn,
the two certificate revocation lists (CRL) that withdraw one early, and the
VICAL: its structure, its signature, where it is served, and what a reader
does with the copy it holds. The profiles follow
[ISO/IEC 18013-5:2021][ref-iso-18013-5] Annex B, which is mandatory for the
issuer side, and [RFC 5280][ref-rfc5280] for everything Annex B leaves open.

Its conformance targets are Trust Authority, which holds both roots, issues
from them, and signs the VICAL; Trust Registry, which builds the VICAL and
serves it and both certificate revocation lists; Issuer Core, which requests and holds a
Document Signer Certificate and, where it issues in mdoc, a status list
signer certificate; Verifier Core, which holds a Verifier Issuing
CA, issues a Verifier Device Certificate to each device it vouches for, and
publishes the list that withdraws one; Mobile Verifier, which holds a device
certificate and validates the issuer chain of every mdoc it reads; and
Mobile Wallet, which validates the reader chain of every request it answers.
A target meets a requirement through the X.509 Validator of Trust SDK where
the library performs the check, and the requirement still binds the Module.

It leaves to other documents: the validity period of a Verifier Device
Certificate and how long a stale certificate revocation list is still
accepted, which the Governance Profile holds; [the grounds on which a certificate is withdrawn, which the Governance Framework holds][gf-grounds]; the trusted list, which
names each Verifier Issuing CA and is what ties a chain to an accredited
entity, which
[Publishing and reading the trusted list](publishing-and-reading-the-trusted-list.md)
holds; the keys that are published in a Decentralized Identifier (DID)
Document instead of a certificate, which
[Publishing and resolving a did:webvh identifier](publishing-and-resolving-a-did-webvh-identifier.md)
holds; where `x5chain` sits inside IssuerAuth and what else an mdoc carries,
which [Issuing a credential in SD-JWT VC, mdoc, and `ldp_vc`](issuing-a-credential-in-sd-jwt-vc-mdoc-and-ldp-vc.md) holds; how a merchant carries its
certificate in an online request, which the Verifier Services specifications
hold; the exchange that carries a reader device's evidence to Verifier Core,
which belongs to whoever runs Verifier Core; and the exchange in which a certificate signing request (CSR) reaches
Trust Authority and the certificate comes back, which [Onboarding an entity and registering its keys](onboarding-an-entity-and-registering-its-keys.md) holds.

Before the first exchange, each target holds what the rules below assume:

- **Trust Authority** holds the Issuer Root CA in one offline hardware
  security module (HSM) and the Verifier Root CA in a second, each validated
  to [FIPS 140-3][ref-fips-140-3] Level 3, along with the key that signs the
  VICAL.
- **Issuer Core** holds the `issuance-cose` key and the `status-list` key in
  its Key Manager, in the driver its grade allows.
- **Verifier Core** holds its Verifier Issuing CA key in a cloud Key
  Management Service or an HSM, never in the software keystore, and the
  identity of the official build of each application it certifies devices for,
  Mobile Verifier or a Relying Party's own application carrying Reader SDK: the
  Android package name and signing certificate digest, and the iOS App ID.
- **A reader device** holds its device key in its secure element, and the
  party that vouches for it holds the public half.
- **Mobile Wallet and Mobile Verifier** carry both roots from build time and
  embed Trust SDK.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-04-001 }**REQ-TS-5-04-001** Every certificate this specification names MUST meet every requirement in [Common rules][ts-5-04-common-rules].
- [](){ #req-ts-5-04-002 }**REQ-TS-5-04-002** Trust Authority MUST meet every requirement on this page that names Trust Authority or an authority, and every requirement on what Trust Authority writes: its roots and link certificates, the certificates it issues, its certificate revocation lists, and the `COSE_Sign1` that carries the VICAL.
- [](){ #req-ts-5-04-003 }**REQ-TS-5-04-003** Issuer Core MUST meet every requirement on this page that names Issuer Core.
- [](){ #req-ts-5-04-004 }**REQ-TS-5-04-004** Verifier Core MUST meet every requirement on this page that names Verifier Core, an authority, or the holder of a Verifier Issuing CA, and every requirement on what Verifier Core writes: the Verifier Device Certificates it issues, their `ReaderAuthRole` extension, and its certificate revocation list.
- [](){ #req-ts-5-04-005 }**REQ-TS-5-04-005** Trust Registry MUST meet every requirement on this page that names Trust Registry, and every requirement on what Trust Registry writes: the VICAL and its entries.
- [](){ #req-ts-5-04-006 }**REQ-TS-5-04-006** Mobile Wallet and Mobile Verifier MUST each meet every requirement on this page that names it or names a reader, except that a requirement on reading `ReaderAuthRole` binds Mobile Wallet alone.

</div>

## What these certificates prove {#ts-5-04-overview}

ISO/IEC 18013-5 knows no DID. An mdoc is signed under a certificate and a
reader authenticates with one, so the ecosystem runs an X.509 trust path
beside the DID path, built from two roots that never sign each other, as
[two trust anchor paths][two-trust-anchor-paths] sets out. The issuer side
proves that a credential is genuine: the Issuer Root CA signs a Document
Signer Certificate for each issuer, and that leaf signs the Mobile Security
Object of every mdoc the issuer produces. Beside it, a status list signer
certificate certifies the key that signs the issuer's status list, so a
reader holding the same root can check that list as well. The reader side proves that the
party asking is authorized to ask: the Verifier Root CA signs a Verifier
Issuing CA for each RP Intermediary and for each Relying Party that reads in
proximity, and that intermediate signs one Verifier Device Certificate per
reader device, which signs the ReaderAuth of a DeviceRequest.

A certificate says which key, never whether the party behind it is still
accredited. That second answer comes from the trusted list, which names each
Verifier Issuing CA and each entity's status, as
[the reader side][the-reader-side] sets out. The VICAL answers a third
question for a reader that holds no trusted list at all, abroad or inside
the ecosystem: which issuer roots to accept, and for which document types.

A holder never has a certificate. The certificates above, with the two roots
and the VICAL, are every certificate the ecosystem issues.

## The certificates as issued {#ts-5-04-the-certificates-as-issued}

Every certificate, certificate revocation list, and list below is an
illustration: the organizations, the domains, and the keys are invented, and
no production authority has issued anything yet. The fields are not
illustrations. Each artifact was generated against the profiles on this page,
signed, and verified, so an implementation can parse any block here and find
exactly the extensions, the object identifiers, the key usages, and the
ceilings the clauses below require. What an implementation copies from them
is the shape, never the values.

``` { .text title="Signature checks over every artifact below" data-format="Output" }
Issuer Root CA self-signature              OK
CSR self-signature                         OK
Document Signer Certificate <- root        OK
Korlantas Document Signer <- root          OK
VICAL signer certificate <- root           OK
Status list signer certificates <- root    OK
Verifier Root CA self-signature            OK
Verifier Issuing CA <- Verifier Root CA    OK
Verifier Device Certificate <- Issuing CA  OK
Issuer Root CA certificate revocation list OK
Verifier Issuing CA revocation list        OK
VICAL COSE_Sign1 signature                 OK
```

### Issuer Root CA {#ts-5-04-issuer-root-ca-as-issued}

Self-signed in the offline hardware security module, 15 years, path length
zero, signing certificates and certificate revocation lists and nothing else.

<figure markdown="1" class="ekdn-table">

| Field | Value |
|---|---|
| Subject, and Issuer | `CN=IDCTF Issuer Root CA,O=Trust Authority Republik Indonesia,C=ID` |
| Serial number | `0x2C799082EE4470F97328DDCD`, 12 octets, 94 bits |
| Validity | 2026-01-01T00:00:00Z to 2041-01-01T00:00:00Z |
| Public key | Elliptic curve, P-256, uncompressed |
| Signature algorithm | `1.2.840.10045.4.3.2`, ECDSA with SHA-256 |
| Basic constraints | `CA:TRUE`, `pathLenConstraint:0`, critical |
| Key usage | `keyCertSign`, `cRLSign`, critical |
| Subject key identifier | `FBF0D56AB0BFDA804A32EDDD33CCC9DDD283799A` |
| Issuer alternative name | `https://trust.go.id` |
| CRL distribution points | `https://registry.trust.go.id/crl/issuer-root-ca` |
| Extended key usage | Absent |
| DER size | 600 bytes |

</figure>

``` { .text title="issuer-root-ca.pem, the Issuer Root CA certificate" data-format="PEM" }
-----BEGIN CERTIFICATE-----
MIICVDCCAfugAwIBAgIMLHmQgu5EcPlzKN3NMAoGCCqGSM49BAMCMFkxCzAJBgNV
BAYTAklEMSswKQYDVQQKDCJUcnVzdCBBdXRob3JpdHkgUmVwdWJsaWsgSW5kb25l
c2lhMR0wGwYDVQQDDBRJRENURiBJc3N1ZXIgUm9vdCBDQTAeFw0yNjAxMDEwMDAw
MDBaFw00MTAxMDEwMDAwMDBaMFkxCzAJBgNVBAYTAklEMSswKQYDVQQKDCJUcnVz
dCBBdXRob3JpdHkgUmVwdWJsaWsgSW5kb25lc2lhMR0wGwYDVQQDDBRJRENURiBJ
c3N1ZXIgUm9vdCBDQTBZMBMGByqGSM49AgEGCCqGSM49AwEHA0IABL8oqZiTgz5E
kIXc3BlxDYn5EksxzptRzXvjKZ3IFtiny63cDZW9s9R2103afsgXcb55xjONscPB
JE7BlyMugp2jgagwgaUwEgYDVR0TAQH/BAgwBgEB/wIBADAOBgNVHQ8BAf8EBAMC
AQYwHQYDVR0OBBYEFPvw1Wqwv9qASjLt3TPMyd3Sg3maMB4GA1UdEgQXMBWGE2h0
dHBzOi8vdHJ1c3QuZ28uaWQwQAYDVR0fBDkwNzA1oDOgMYYvaHR0cHM6Ly9yZWdp
c3RyeS50cnVzdC5nby5pZC9jcmwvaXNzdWVyLXJvb3QtY2EwCgYIKoZIzj0EAwID
RwAwRAIgYrR4LSlAZD8MyJFtNezLqC7mdghZm92JKlIJXobXTjICIG71862xJbD/
UYOSeUeaMloZ5EkecOL9L5e9IJjQ+XwU
-----END CERTIFICATE-----
```

### The certificate signing request {#ts-5-04-the-certificate-signing-request}

Built by the issuer's Key Manager over the `issuance-cose` key and signed
with that key, which is the proof the issuer holds it. 315 bytes of DER
under [RFC 2986][ref-rfc2986], carrying the subject and the public key and
no extension.

``` { .text title="document-signer.csr, the certificate signing request" data-format="PEM" }
-----BEGIN CERTIFICATE REQUEST-----
MIIBNzCB3gIBADB8MQswCQYDVQQGEwJJRDE+MDwGA1UECgw1RGlyZWt0b3JhdCBK
ZW5kZXJhbCBLZXBlbmR1ZHVrYW4gZGFuIFBlbmNhdGF0YW4gU2lwaWwxLTArBgNV
BAMMJER1a2NhcGlsIG1kb2MgRG9jdW1lbnQgU2lnbmVyIDIwMjYtQTBZMBMGByqG
SM49AgEGCCqGSM49AwEHA0IABNGGzGNnN9NBiCV64zB06osfQKOOMSdr6b9U6Bom
NFyjBMfYrfCC67ewUAQXeOwM4Z8UPkB2GXwCajMfUy+ng2SgADAKBggqhkjOPQQD
AgNIADBFAiEAuk8C+F6Lo9m6Z7E5W59j2Zcb32QcK/eA4duzasK5MusCIANXavJU
uXJj6sl1OqGkJO9QUKzNx4KqOrJs7sTL2zL4
-----END CERTIFICATE REQUEST-----
```

### Document Signer Certificate {#ts-5-04-document-signer-certificate-as-issued}

Issued from the request above, 426 days, inside the 3650-day ceiling that
binds a KTP Digital. [The SIM issuer's certificate][ts-5-04-document-signer-certificate-of-the-sim-issuer]
carries the same 426 days under the 457-day ceiling that binds a Mobile
Driving License (mDL). This is what travels in `x5chain` inside every mdoc
the issuer signs.

<figure markdown="1" class="ekdn-table">

| Field | Value |
|---|---|
| Subject | `CN=Dukcapil mdoc Document Signer 2026-A,O=Direktorat Jenderal Kependudukan dan Pencatatan Sipil,C=ID` |
| Issuer | `CN=IDCTF Issuer Root CA,O=Trust Authority Republik Indonesia,C=ID` |
| Serial number | `0x16A98534626A68B21D10C09B`, 12 octets, 93 bits |
| Validity | 2026-09-01T00:00:00Z to 2027-11-01T00:00:00Z, 426 days |
| Public key | Elliptic curve, P-256, the `issuance-cose` key of the request |
| Basic constraints | `CA:FALSE`, critical |
| Key usage | `digitalSignature`, critical |
| Extended key usage | `1.0.18013.5.1.2`, mdoc document signing, critical |
| Authority key identifier | `FBF0D56AB0BFDA804A32EDDD33CCC9DDD283799A`, the root |
| Subject key identifier | `EEADD07E695E6A68950188F2CF92E6C566C9A8DD` |
| Issuer alternative name | `https://trust.go.id` |
| CRL distribution points | `https://registry.trust.go.id/crl/issuer-root-ca` |
| DER size | 686 bytes |

</figure>

``` { .text title="document-signer.pem, the Document Signer Certificate" data-format="PEM" }
-----BEGIN CERTIFICATE-----
MIICqjCCAlCgAwIBAgIMFqmFNGJqaLIdEMCbMAoGCCqGSM49BAMCMFkxCzAJBgNV
BAYTAklEMSswKQYDVQQKDCJUcnVzdCBBdXRob3JpdHkgUmVwdWJsaWsgSW5kb25l
c2lhMR0wGwYDVQQDDBRJRENURiBJc3N1ZXIgUm9vdCBDQTAeFw0yNjA5MDEwMDAw
MDBaFw0yNzExMDEwMDAwMDBaMHwxCzAJBgNVBAYTAklEMT4wPAYDVQQKDDVEaXJl
a3RvcmF0IEplbmRlcmFsIEtlcGVuZHVkdWthbiBkYW4gUGVuY2F0YXRhbiBTaXBp
bDEtMCsGA1UEAwwkRHVrY2FwaWwgbWRvYyBEb2N1bWVudCBTaWduZXIgMjAyNi1B
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE0YbMY2c300GIJXrjMHTqix9Ao44x
J2vpv1ToGiY0XKMEx9it8ILrt7BQBBd47AzhnxQ+QHYZfAJqMx9TL6eDZKOB2jCB
1zAMBgNVHRMBAf8EAjAAMA4GA1UdDwEB/wQEAwIHgDAVBgNVHSUBAf8ECzAJBgco
gYxdBQECMB8GA1UdIwQYMBaAFPvw1Wqwv9qASjLt3TPMyd3Sg3maMB0GA1UdDgQW
BBTurdB+aV5qaJUBiPLPkubFZsmo3TAeBgNVHRIEFzAVhhNodHRwczovL3RydXN0
LmdvLmlkMEAGA1UdHwQ5MDcwNaAzoDGGL2h0dHBzOi8vcmVnaXN0cnkudHJ1c3Qu
Z28uaWQvY3JsL2lzc3Vlci1yb290LWNhMAoGCCqGSM49BAMCA0gAMEUCIB7a47Xa
yNlMAd68To0wXzx+OpBwHYci/FWqKKm+kMppAiEA4fMeNqaylzA+OovL4A05fUWr
dfb5eyKg7MXTU90r2O8=
-----END CERTIFICATE-----
```

### Document Signer Certificate of the SIM issuer {#ts-5-04-document-signer-certificate-of-the-sim-issuer}

The certificate of Korps Lalu Lintas Polri, the second issuer under the
root, which signs the SIM under the document type
`org.iso.18013.5.1.mDL`. It follows the same profile as the one above and
certifies a key of its own, and it is why the first entry of
[the VICAL payload][ts-5-04-vical-payload] names that document type.

<figure markdown="1" class="ekdn-table">

| Field | Value |
|---|---|
| Subject | `CN=Korlantas mdoc Document Signer 2026-A,O=Korps Lalu Lintas Kepolisian Negara Republik Indonesia,C=ID` |
| Issuer | `CN=IDCTF Issuer Root CA,O=Trust Authority Republik Indonesia,C=ID` |
| Serial number | `0x4B1D7E30C95A26F3880E1D52`, 12 octets, 95 bits |
| Validity | 2026-09-01T00:00:00Z to 2027-11-01T00:00:00Z, 426 days |
| Public key | Elliptic curve, P-256, the issuer's `issuance-cose` key |
| Basic constraints | `CA:FALSE`, critical |
| Key usage | `digitalSignature`, critical |
| Extended key usage | `1.0.18013.5.1.2`, mdoc document signing, critical |
| Authority key identifier | `FBF0D56AB0BFDA804A32EDDD33CCC9DDD283799A`, the root |
| Subject key identifier | `EE598A37400F670F0E370515897398BE1EC8D9AB` |
| Issuer alternative name | `https://trust.go.id` |
| CRL distribution points | `https://registry.trust.go.id/crl/issuer-root-ca` |
| DER size | 688 bytes |

</figure>

``` { .text title="document-signer-korlantas.pem, the Document Signer Certificate of the SIM issuer" data-format="PEM" }
-----BEGIN CERTIFICATE-----
MIICrDCCAlKgAwIBAgIMSx1+MMlaJvOIDh1SMAoGCCqGSM49BAMCMFkxCzAJBgNV
BAYTAklEMSswKQYDVQQKDCJUcnVzdCBBdXRob3JpdHkgUmVwdWJsaWsgSW5kb25l
c2lhMR0wGwYDVQQDDBRJRENURiBJc3N1ZXIgUm9vdCBDQTAeFw0yNjA5MDEwMDAw
MDBaFw0yNzExMDEwMDAwMDBaMH4xCzAJBgNVBAYTAklEMT8wPQYDVQQKDDZLb3Jw
cyBMYWx1IExpbnRhcyBLZXBvbGlzaWFuIE5lZ2FyYSBSZXB1YmxpayBJbmRvbmVz
aWExLjAsBgNVBAMMJUtvcmxhbnRhcyBtZG9jIERvY3VtZW50IFNpZ25lciAyMDI2
LUEwWTATBgcqhkjOPQIBBggqhkjOPQMBBwNCAATQRi7NDhBXVZlFZOCtqpfVqXUQ
oB+SHdFjWwEwE4DoFm4SSApw0EMmZsb+FL6BR1ZVdVEZt+ZVQ+rU/GNS7SZRo4Ha
MIHXMAwGA1UdEwEB/wQCMAAwDgYDVR0PAQH/BAQDAgeAMBUGA1UdJQEB/wQLMAkG
ByiBjF0FAQIwHwYDVR0jBBgwFoAU+/DVarC/2oBKMu3dM8zJ3dKDeZowHQYDVR0O
BBYEFO5ZijdAD2cPDjcFFYlzmL4eyNmrMB4GA1UdEgQXMBWGE2h0dHBzOi8vdHJ1
c3QuZ28uaWQwQAYDVR0fBDkwNzA1oDOgMYYvaHR0cHM6Ly9yZWdpc3RyeS50cnVz
dC5nby5pZC9jcmwvaXNzdWVyLXJvb3QtY2EwCgYIKoZIzj0EAwIDSAAwRQIhAOgI
a56Q9zufUC9i7J9fICkn9OKdqqKmDqPahEyIpwjjAiBAuEatCQo5uIzAeb2BLW8p
d9p2ROxyjK8OQhbrMQvpZw==
-----END CERTIFICATE-----
```

### VICAL signer certificate {#ts-5-04-vical-signer-certificate-as-issued}

The third certificate under the Issuer Root CA, over the VICAL key in Trust
Authority's hardware security module. It signs the VICAL and nothing else,
which is why its key usage is `nonRepudiation` alone, and it sits at the
1187-day ceiling of the Annex C profile.

<figure markdown="1" class="ekdn-table">

| Field | Value |
|---|---|
| Subject | `CN=IDCTF VICAL Signer 2026,O=Trust Authority Republik Indonesia,C=ID` |
| Issuer | `CN=IDCTF Issuer Root CA,O=Trust Authority Republik Indonesia,C=ID` |
| Serial number | `0x309A194F9588B631B53120DF`, 12 octets, 94 bits |
| Validity | 2026-10-01T00:00:00Z to 2029-12-31T00:00:00Z, 1187 days |
| Public key | Elliptic curve, P-256, the VICAL key |
| Basic constraints | `CA:FALSE`, critical |
| Key usage | `nonRepudiation`, critical, with `digitalSignature` unset |
| Extended key usage | `1.0.18013.5.1.8`, mdoc VICAL signing, critical |
| Authority key identifier | `FBF0D56AB0BFDA804A32EDDD33CCC9DDD283799A`, the root |
| Subject key identifier | `23FA31350E7315728FC4D5097B658AA2F3049B9D` |
| Issuer alternative name | `https://trust.go.id` |
| CRL distribution points | `https://registry.trust.go.id/crl/issuer-root-ca` |
| DER size | 654 bytes |

</figure>

``` { .text title="vical-signer.pem, the VICAL signer certificate" data-format="PEM" }
-----BEGIN CERTIFICATE-----
MIICijCCAjCgAwIBAgIMMJoZT5WItjG1MSDfMAoGCCqGSM49BAMCMFkxCzAJBgNV
BAYTAklEMSswKQYDVQQKDCJUcnVzdCBBdXRob3JpdHkgUmVwdWJsaWsgSW5kb25l
c2lhMR0wGwYDVQQDDBRJRENURiBJc3N1ZXIgUm9vdCBDQTAeFw0yNjEwMDEwMDAw
MDBaFw0yOTEyMzEwMDAwMDBaMFwxCzAJBgNVBAYTAklEMSswKQYDVQQKDCJUcnVz
dCBBdXRob3JpdHkgUmVwdWJsaWsgSW5kb25lc2lhMSAwHgYDVQQDDBdJRENURiBW
SUNBTCBTaWduZXIgMjAyNjBZMBMGByqGSM49AgEGCCqGSM49AwEHA0IABM6mKlme
7Ns/3J0kWAbktB9RSWdAmM9Ls/nkZ0AkSE6zzFrZf+9CuGpyLhcfH1LT7bHJm+D9
LdSchLuz7BerepujgdowgdcwDAYDVR0TAQH/BAIwADAOBgNVHQ8BAf8EBAMCBkAw
FQYDVR0lAQH/BAswCQYHKIGMXQUBCDAfBgNVHSMEGDAWgBT78NVqsL/agEoy7d0z
zMnd0oN5mjAdBgNVHQ4EFgQUI/oxNQ5zFXKPxNUJe2WKovMEm50wHgYDVR0SBBcw
FYYTaHR0cHM6Ly90cnVzdC5nby5pZDBABgNVHR8EOTA3MDWgM6Axhi9odHRwczov
L3JlZ2lzdHJ5LnRydXN0LmdvLmlkL2NybC9pc3N1ZXItcm9vdC1jYTAKBggqhkjO
PQQDAgNIADBFAiEA6qxS69dBbmTVKgKDT+JW6ybdlf4pyDBG2LeIm8fijhYCIFpP
R3+8jH7T3bDdRA6bApmrAApuAjduXcxLVHUc4G2I
-----END CERTIFICATE-----
```

### Status list signer certificate {#ts-5-04-status-list-signer-certificate-as-issued}

The fourth certificate under the Issuer Root CA, over Dukcapil's
`status-list` key, the key whose verification method
`did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id#status-list-1`
names in its DID Document. Its subject carries the same `organizationName`
as Dukcapil's Document Signer Certificate, which is what lets a reader tie
the status list to the issuer of the mdoc. The CWT form of the credential
status list carries it in `x5chain`, as
[Publishing and reading a status list](publishing-and-reading-a-status-list.md)
shows.

<figure markdown="1" class="ekdn-table">

| Field | Value |
|---|---|
| Subject | `CN=Dukcapil Status List Signer 2026-A,O=Direktorat Jenderal Kependudukan dan Pencatatan Sipil,C=ID` |
| Issuer | `CN=IDCTF Issuer Root CA,O=Trust Authority Republik Indonesia,C=ID` |
| Serial number | `0x393F3B03452AAC04524969A3`, 12 octets, 94 bits |
| Validity | 2026-09-01T00:00:00Z to 2029-09-01T00:00:00Z, 1096 days |
| Public key | Elliptic curve, P-256, the `status-list` key |
| Basic constraints | `CA:FALSE`, critical |
| Key usage | `digitalSignature`, critical |
| Extended key usage | Absent |
| Authority key identifier | `FBF0D56AB0BFDA804A32EDDD33CCC9DDD283799A`, the root |
| Subject key identifier | `85C506BB6757839D75AFC75D9BEC9AF029E67D80` |
| Issuer alternative name | `https://trust.go.id` |
| CRL distribution points | `https://registry.trust.go.id/crl/issuer-root-ca` |
| DER size | 660 bytes |

</figure>

``` { .text title="status-list-signer.pem, the status list signer certificate" data-format="PEM" }
-----BEGIN CERTIFICATE-----
MIICkDCCAjegAwIBAgIMOT87A0UqrARSSWmjMAoGCCqGSM49BAMCMFkxCzAJBgNV
BAYTAklEMSswKQYDVQQKDCJUcnVzdCBBdXRob3JpdHkgUmVwdWJsaWsgSW5kb25l
c2lhMR0wGwYDVQQDDBRJRENURiBJc3N1ZXIgUm9vdCBDQTAeFw0yNjA5MDEwMDAw
MDBaFw0yOTA5MDEwMDAwMDBaMHoxCzAJBgNVBAYTAklEMT4wPAYDVQQKDDVEaXJl
a3RvcmF0IEplbmRlcmFsIEtlcGVuZHVkdWthbiBkYW4gUGVuY2F0YXRhbiBTaXBp
bDErMCkGA1UEAwwiRHVrY2FwaWwgU3RhdHVzIExpc3QgU2lnbmVyIDIwMjYtQTBZ
MBMGByqGSM49AgEGCCqGSM49AwEHA0IABJmOP/rxO8ku/q14SfTNiSPwrKXfwVjc
yrRF2vq0bOyaXPft9vxqVGJzvXCrwjl3Yfg1XcFTxYbdva+bKRdcXayjgcMwgcAw
DAYDVR0TAQH/BAIwADAOBgNVHQ8BAf8EBAMCB4AwHwYDVR0jBBgwFoAU+/DVarC/
2oBKMu3dM8zJ3dKDeZowHQYDVR0OBBYEFIXFBrtnV4Odda/HXZvsmvAp5n2AMB4G
A1UdEgQXMBWGE2h0dHBzOi8vdHJ1c3QuZ28uaWQwQAYDVR0fBDkwNzA1oDOgMYYv
aHR0cHM6Ly9yZWdpc3RyeS50cnVzdC5nby5pZC9jcmwvaXNzdWVyLXJvb3QtY2Ew
CgYIKoZIzj0EAwIDRwAwRAIgOyA/D0tKOX0VLFgnzP9FM5r6PRYbiJnqVglVv5MD
l0sCIBUVE0N58jwFGeU7hLCHckCj1BC5WC9LDs3iwF8SKn/P
-----END CERTIFICATE-----
```

### Verifier Root CA {#ts-5-04-verifier-root-ca-as-issued}

The second root, self-signed in a second offline hardware security module.
It differs from the first in one field: the reader side is three levels
deep, so its path length is one.

<figure markdown="1" class="ekdn-table">

| Field | Value |
|---|---|
| Subject, and Issuer | `CN=IDCTF Verifier Root CA,O=Trust Authority Republik Indonesia,C=ID` |
| Serial number | `0x2FD61D5785EF16C777E4CB5F`, 12 octets, 94 bits |
| Validity | 2026-01-01T00:00:00Z to 2041-01-01T00:00:00Z |
| Basic constraints | `CA:TRUE`, `pathLenConstraint:1`, critical |
| Key usage | `keyCertSign`, `cRLSign`, critical |
| Subject key identifier | `59C5F043786877C6E2E2A12544A4303D4AEE04F3` |
| Issuer alternative name | `https://trust.go.id` |
| CRL distribution points | `https://registry.trust.go.id/crl/verifier-root-ca` |
| Extended key usage | Absent |
| DER size | 607 bytes |

</figure>

``` { .text title="verifier-root-ca.pem, the Verifier Root CA certificate" data-format="PEM" }
-----BEGIN CERTIFICATE-----
MIICWzCCAgGgAwIBAgIML9YdV4XvFsd35MtfMAoGCCqGSM49BAMCMFsxCzAJBgNV
BAYTAklEMSswKQYDVQQKDCJUcnVzdCBBdXRob3JpdHkgUmVwdWJsaWsgSW5kb25l
c2lhMR8wHQYDVQQDDBZJRENURiBWZXJpZmllciBSb290IENBMB4XDTI2MDEwMTAw
MDAwMFoXDTQxMDEwMTAwMDAwMFowWzELMAkGA1UEBhMCSUQxKzApBgNVBAoMIlRy
dXN0IEF1dGhvcml0eSBSZXB1YmxpayBJbmRvbmVzaWExHzAdBgNVBAMMFklEQ1RG
IFZlcmlmaWVyIFJvb3QgQ0EwWTATBgcqhkjOPQIBBggqhkjOPQMBBwNCAATPmK/7
xcBqrKDLh1W0SpM7t2hf1OiDy887AL4PvrRsyLP892Ayec/RjLXEUGFJ4bqPV1eA
bMgmO4C9/bUSOl1Fo4GqMIGnMBIGA1UdEwEB/wQIMAYBAf8CAQEwDgYDVR0PAQH/
BAQDAgEGMB0GA1UdDgQWBBRZxfBDeGh3xuLioSVEpDA9Su4E8zAeBgNVHRIEFzAV
hhNodHRwczovL3RydXN0LmdvLmlkMEIGA1UdHwQ7MDkwN6A1oDOGMWh0dHBzOi8v
cmVnaXN0cnkudHJ1c3QuZ28uaWQvY3JsL3ZlcmlmaWVyLXJvb3QtY2EwCgYIKoZI
zj0EAwIDSAAwRQIhAKrjhq0mUDdl+902EA+NVN8UMBJHolqCI6+y+LADGdTzAiAL
lOaue8F55EWMHWcCEYOGir98KzK1UzfePAZcaXPTGg==
-----END CERTIFICATE-----
```

### Verifier Issuing CA {#ts-5-04-verifier-issuing-ca-as-issued}

The intermediate, held by an RP Intermediary. Its subject key identifier is
the value the entity's trusted list entry names, which is how a wallet ties
a reader chain to an accredited entity.

<figure markdown="1" class="ekdn-table">

| Field | Value |
|---|---|
| Subject | `CN=Terminal Nusantara Verifier Issuing CA,O=Terminal Nusantara,C=ID` |
| Issuer | `CN=IDCTF Verifier Root CA,O=Trust Authority Republik Indonesia,C=ID` |
| Serial number | `0xB589CDF61B889EBF0A9CCE05`, 12 octets, 96 bits |
| Validity | 2026-06-01T00:00:00Z to 2031-06-01T00:00:00Z |
| Basic constraints | `CA:TRUE`, `pathLenConstraint:0`, critical |
| Key usage | `keyCertSign`, `cRLSign`, critical |
| Extended key usage | `1.0.18013.5.1.6`, mdoc reader authentication, non-critical |
| Authority key identifier | `59C5F043786877C6E2E2A12544A4303D4AEE04F3`, the Verifier Root CA |
| Subject key identifier | `2EA3B6F5A1D3E7F7F920605EFFE880A059817933`, the value the trusted list names |
| CRL distribution points | `https://registry.trust.go.id/crl/verifier-root-ca` |
| DER size | 628 bytes |

</figure>

``` { .text title="verifier-issuing-ca.pem, the Verifier Issuing CA certificate" data-format="PEM" }
-----BEGIN CERTIFICATE-----
MIICcDCCAhegAwIBAgINALWJzfYbiJ6/CpzOBTAKBggqhkjOPQQDAjBbMQswCQYD
VQQGEwJJRDErMCkGA1UECgwiVHJ1c3QgQXV0aG9yaXR5IFJlcHVibGlrIEluZG9u
ZXNpYTEfMB0GA1UEAwwWSURDVEYgVmVyaWZpZXIgUm9vdCBDQTAeFw0yNjA2MDEw
MDAwMDBaFw0zMTA2MDEwMDAwMDBaMFsxCzAJBgNVBAYTAklEMRswGQYDVQQKDBJU
ZXJtaW5hbCBOdXNhbnRhcmExLzAtBgNVBAMMJlRlcm1pbmFsIE51c2FudGFyYSBW
ZXJpZmllciBJc3N1aW5nIENBMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAElUF1
hsWuBgIrtSf93F93N9xc01IYQG7Nsz+8A+EV7IrxgWYzM0GPaTYMC+z60sBWjVvu
gNB0but2v89nRQ9/faOBvzCBvDASBgNVHRMBAf8ECDAGAQH/AgEAMA4GA1UdDwEB
/wQEAwIBBjASBgNVHSUECzAJBgcogYxdBQEGMB8GA1UdIwQYMBaAFFnF8EN4aHfG
4uKhJUSkMD1K7gTzMB0GA1UdDgQWBBQuo7b1odPn9/kgYF7/6ICgWYF5MzBCBgNV
HR8EOzA5MDegNaAzhjFodHRwczovL3JlZ2lzdHJ5LnRydXN0LmdvLmlkL2NybC92
ZXJpZmllci1yb290LWNhMAoGCCqGSM49BAMCA0cAMEQCICG2iSLIuvM1F8n0ZjzN
VRBhsY/aWRe6s9BMBmhN7PNGAiASz3+SCPOvuVg4P8+qIfaeGtkuO4Mv13sfZgKZ
z6rlrQ==
-----END CERTIFICATE-----
```

### Verifier Device Certificate {#ts-5-04-verifier-device-certificate-as-issued}

The leaf of the reader side, over the device key in one merchant phone,
carrying the bound on what that device may ask for. Its validity period is
the Governance Profile's to set; 730 days is shown, inside the 1187-day
ceiling of the Annex B profile.

<figure markdown="1" class="ekdn-table">

| Field | Value |
|---|---|
| Subject | `CN=Warung Bu Ani,O=Terminal Nusantara,C=ID` |
| Issuer | `CN=Terminal Nusantara Verifier Issuing CA,O=Terminal Nusantara,C=ID` |
| Serial number | `0x598BDB20342F8D4489AB2C0F`, 12 octets, 95 bits |
| Validity | 2026-09-20T00:00:00Z to 2028-09-19T00:00:00Z, 730 days |
| Public key | Elliptic curve, P-256, the device key in the secure element |
| Basic constraints | `CA:FALSE`, critical |
| Key usage | `digitalSignature`, critical |
| Extended key usage | `1.0.18013.5.1.6`, mdoc reader authentication, critical |
| Authority key identifier | `2EA3B6F5A1D3E7F7F920605EFFE880A059817933`, the Verifier Issuing CA |
| Subject key identifier | `4B80B91CB6FF7CF1BD5459679A7A0BF748A8BC3A` |
| `ReaderAuthRole` | `1.3.6.1.4.1.32473.1.1`, non-critical, 121 bytes of DER |
| CRL distribution points | `https://terminal-nusantara.co.id/crl/verifier-issuing-ca` |
| DER size | 747 bytes |

</figure>

``` { .text title="verifier-device.pem, the Verifier Device Certificate" data-format="PEM" }
-----BEGIN CERTIFICATE-----
MIIC5zCCAo2gAwIBAgIMWYvbIDQvjUSJqywPMAoGCCqGSM49BAMCMFsxCzAJBgNV
BAYTAklEMRswGQYDVQQKDBJUZXJtaW5hbCBOdXNhbnRhcmExLzAtBgNVBAMMJlRl
cm1pbmFsIE51c2FudGFyYSBWZXJpZmllciBJc3N1aW5nIENBMB4XDTI2MDkyMDAw
MDAwMFoXDTI4MDkxOTAwMDAwMFowQjELMAkGA1UEBhMCSUQxGzAZBgNVBAoMElRl
cm1pbmFsIE51c2FudGFyYTEWMBQGA1UEAwwNV2FydW5nIEJ1IEFuaTBZMBMGByqG
SM49AgEGCCqGSM49AwEHA0IABJznsDzsHvue2THWxJElUQUTWWtjiqLEFf3Fueuq
o/V5Cjf35Frm95LJTqo+VeTlIoHUrXQOJ/NQ5ikmknkyBK+jggFOMIIBSjAMBgNV
HRMBAf8EAjAAMA4GA1UdDwEB/wQEAwIHgDAVBgNVHSUBAf8ECzAJBgcogYxdBQEG
MB8GA1UdIwQYMBaAFC6jtvWh0+f3+SBgXv/ogKBZgXkzMB0GA1UdDgQWBBRLgLkc
tv988b1UWWeaegv3SKi8OjCBhwYKKwYBBAGB/VkBAQR5MHcwIwwOaWQuaWRjdGYu
a3RwLjEwEQwPdXNpYV9kaV9hdGFzXzE3MCYMFW9yZy5pc28uMTgwMTMuNS4xLm1E
TDANDAthZ2Vfb3Zlcl8xODAoDBRpZC5pZGN0Zi5rYXJ0dS1hc24uMTAQDARuYW1h
DAhpbnN0YW5zaTBJBgNVHR8EQjBAMD6gPKA6hjhodHRwczovL3Rlcm1pbmFsLW51
c2FudGFyYS5jby5pZC9jcmwvdmVyaWZpZXItaXNzdWluZy1jYTAKBggqhkjOPQQD
AgNIADBFAiEA4UH2aXmGaS/fI2JVLDhiQKlscwJgomrG1WGMKx4JtEQCIELIZnzQ
tWu3M8VzBxgSq2g1Wuo/le7JmMuHjFPwAi6F
-----END CERTIFICATE-----
```

The `ReaderAuthRole` of that certificate, as its own DER and as the
structure [the ReaderAuthRole extension][ts-5-04-the-readerauthrole-extension]
defines, bounding the device to one data element of a KTP Digital, one of
an mDL, and two of a Kartu ASN, the union of the two business categories
[Registering and carrying a Use Statement](registering-and-carrying-a-use-statement.md)
shows the device bound to:

``` { .text title="The ReaderAuthRole of verifier-device.pem, as DER" data-format="DER hex" }
30 77
   30 23
      0C 0E "id.idctf.ktp.1"
      30 11
         0C 0F "usia_di_atas_17"
   30 26
      0C 15 "org.iso.18013.5.1.mDL"
      30 0D
         0C 0B "age_over_18"
   30 28
      0C 14 "id.idctf.kartu-asn.1"
      30 10
         0C 04 "nama"
         0C 08 "instansi"

307730230C0E69642E69646374662E6B74702E3130110C0F757369615F64695F
617461735F313730260C156F72672E69736F2E31383031332E352E312E6D444C
300D0C0B6167655F6F7665725F313830280C1469642E69646374662E6B617274
752D61736E2E3130100C046E616D610C08696E7374616E7369
```

### The two certificate revocation lists {#ts-5-04-the-two-revocation-lists-as-issued}

Trust Authority's list for the Issuer Root CA, with one withdrawn Document
Signer Certificate, and the RP Intermediary's list, with one withdrawn
device. Both are version 2, both carry an authority key identifier and a
certificate revocation list number, and neither carries an entry extension.

<figure markdown="1" class="ekdn-table">

| Field | Issuer Root CA list | Verifier Issuing CA list |
|---|---|---|
| Issuer name | `CN=IDCTF Issuer Root CA,O=Trust Authority Republik Indonesia,C=ID` | `CN=Terminal Nusantara Verifier Issuing CA,O=Terminal Nusantara,C=ID` |
| This update | 2026-10-01T00:00:00Z | 2026-10-15T00:00:00Z |
| Next update | 2026-10-02T00:00:00Z, 1 day | 2026-10-16T00:00:00Z, 1 day |
| Revoked | `0xF9218BDD107B1B04FC1F16E5`, revoked 2026-09-15 | `0x80D376F5BF5FC52A9BC78E9D`, revoked 2026-10-12 |
| Authority key identifier | `FBF0D56AB0BFDA804A32EDDD33CCC9DDD283799A` | `2EA3B6F5A1D3E7F7F920605EFFE880A059817933` |
| CRL number | `7` | `31` |
| DER size | 312 bytes | 315 bytes |

</figure>

``` { .text title="issuer-root-ca.crl, served at https://registry.trust.go.id/crl/issuer-root-ca" data-format="PEM" }
-----BEGIN X509 CRL-----
MIIBNDCB2wIBATAKBggqhkjOPQQDAjBZMQswCQYDVQQGEwJJRDErMCkGA1UECgwi
VHJ1c3QgQXV0aG9yaXR5IFJlcHVibGlrIEluZG9uZXNpYTEdMBsGA1UEAwwUSURD
VEYgSXNzdWVyIFJvb3QgQ0EXDTI2MTAwMTAwMDAwMFoXDTI2MTAwMjAwMDAwMFow
IDAeAg0A+SGL3RB7GwT8HxblFw0yNjA5MTUwMDAwMDBaoC8wLTAfBgNVHSMEGDAW
gBT78NVqsL/agEoy7d0zzMnd0oN5mjAKBgNVHRQEAwIBBzAKBggqhkjOPQQDAgNI
ADBFAiEA7ydNQ5Mvh5+kseISesDs2rC/seyRp9i/9mQbnwcnMzUCIDLAHZBu9NF6
p6+75XBC3xEz90yYrIKNysWg93yn7MB9
-----END X509 CRL-----
```

``` { .text title="verifier-issuing-ca.crl, served at https://terminal-nusantara.co.id/crl/verifier-issuing-ca" data-format="PEM" }
-----BEGIN X509 CRL-----
MIIBNzCB3QIBATAKBggqhkjOPQQDAjBbMQswCQYDVQQGEwJJRDEbMBkGA1UECgwS
VGVybWluYWwgTnVzYW50YXJhMS8wLQYDVQQDDCZUZXJtaW5hbCBOdXNhbnRhcmEg
VmVyaWZpZXIgSXNzdWluZyBDQRcNMjYxMDE1MDAwMDAwWhcNMjYxMDE2MDAwMDAw
WjAgMB4CDQCA03b1v1/FKpvHjp0XDTI2MTAxMjAwMDAwMFqgLzAtMB8GA1UdIwQY
MBaAFC6jtvWh0+f3+SBgXv/ogKBZgXkzMAoGA1UdFAQDAgEfMAoGCCqGSM49BAMC
A0kAMEYCIQDy5qeynkSiHAYmFIuMSYS6fwiWJoT/ENvrhr5MF+lkuwIhAL1v3+zP
eEhMKRyg/q0BueRfgdtQRPtSxMNAMrMn3HkG
-----END X509 CRL-----
```

## VICAL payload {#ts-5-04-vical-payload}

The payload of the VICAL in Concise Binary Object Representation (CBOR)
diagnostic notation, before [The VICAL][ts-5-04-the-vical] wraps it in the
`COSE_Sign1`. It carries two entries: the Issuer Root CA shown above, with
the two document types its issuers sign, and the root of a recognized
foreign authority, which carries its own country and its own document type.
Every member the profile requires is present and every optional member the
profile forbids is absent. The two `certificate` byte strings are the DER of
those two certificates, shown here by their first and last 16 bytes; the
signed list below carries them in full.

``` { .text title="The VICAL payload, in CBOR diagnostic notation" data-format="CBOR diag" }
{
  "version": "1.0",
  "vicalProvider": "Trust Authority Republik Indonesia",
  "date": 0("2026-10-17T06:00:00Z"),
  "vicalIssueID": 4,
  "nextUpdate": 0("2026-10-18T06:00:00Z"),
  "certificateInfos": [
    {
      "certificate": h'30820254308201FBA003020102020C2C ... 19E4491E70E2FD2F97BD2098D0F97C14',   / 600 bytes /
      "serialNumber": 2(h'2C799082EE4470F97328DDCD'),
      "ski": h'FBF0D56AB0BFDA804A32EDDD33CCC9DDD283799A',
      "docType": ["id.idctf.ktp.1", "org.iso.18013.5.1.mDL"],
      "certificateProfile": ["1.0.18013.5.1.7"],
      "issuingAuthority": "Trust Authority Republik Indonesia",
      "issuingCountry": "ID",
      "issuer": h'3059310B300906035504061302494431 ... 462049737375657220526F6F74204341',   / 91 bytes /
      "subject": h'3059310B300906035504061302494431 ... 462049737375657220526F6F74204341',   / 91 bytes /
      "notBefore": 0("2026-01-01T00:00:00Z"),
      "notAfter": 0("2041-01-01T00:00:00Z")
    },
    {
      "certificate": h'30820253308201FAA003020102020C5B ... 28B66B784E8B83E8D83ECF803B7981C3',   / 599 bytes /
      "serialNumber": 2(h'5BBBA9D4E105FF74AE84C5ED'),
      "ski": h'E15C396F2CF2600007CA5AD2A9149DDC5314FA48',
      "docType": ["org.iso.18013.5.1.mDL"],
      "certificateProfile": ["1.0.18013.5.1.7"],
      "issuingAuthority": "Jabatan Pengangkutan Jalan Malaysia",
      "issuingCountry": "MY",
      "issuer": h'3061310B3009060355040613024D5931 ... 6720417574686F7269747920526F6F74',   / 99 bytes /
      "subject": h'3061310B3009060355040613024D5931 ... 6720417574686F7269747920526F6F74',   / 99 bytes /
      "notBefore": 0("2025-03-01T00:00:00Z"),
      "notAfter": 0("2035-03-01T00:00:00Z")
    }
  ]
}
```

The payload is 2326 bytes. Signed, it is a four-element array: the protected
header `a10126`, which is the map `{1: -7}` for `ES256`; an unprotected
header carrying the VICAL signer certificate under label `33`, `x5chain`;
the payload; and a 64-byte signature, the concatenation of `r` and `s`
rather than a DER sequence. The whole list is 3060 bytes, and this is it,
base64 of the untagged `COSE_Sign1` exactly as `GET /vical` serves it in
binary.

``` { .text title="GET /vical, the signed COSE_Sign1 in base64" data-format="COSE base64" }
hEOhASahGCFZAo4wggKKMIICMKADAgECAgwwmhlPlYi2MbUxIN8wCgYIKoZIzj0E
AwIwWTELMAkGA1UEBhMCSUQxKzApBgNVBAoMIlRydXN0IEF1dGhvcml0eSBSZXB1
YmxpayBJbmRvbmVzaWExHTAbBgNVBAMMFElEQ1RGIElzc3VlciBSb290IENBMB4X
DTI2MTAwMTAwMDAwMFoXDTI5MTIzMTAwMDAwMFowXDELMAkGA1UEBhMCSUQxKzAp
BgNVBAoMIlRydXN0IEF1dGhvcml0eSBSZXB1YmxpayBJbmRvbmVzaWExIDAeBgNV
BAMMF0lEQ1RGIFZJQ0FMIFNpZ25lciAyMDI2MFkwEwYHKoZIzj0CAQYIKoZIzj0D
AQcDQgAEzqYqWZ7s2z/cnSRYBuS0H1FJZ0CYz0uz+eRnQCRITrPMWtl/70K4anIu
Fx8fUtPtscmb4P0t1JyEu7PsF6t6m6OB2jCB1zAMBgNVHRMBAf8EAjAAMA4GA1Ud
DwEB/wQEAwIGQDAVBgNVHSUBAf8ECzAJBgcogYxdBQEIMB8GA1UdIwQYMBaAFPvw
1Wqwv9qASjLt3TPMyd3Sg3maMB0GA1UdDgQWBBQj+jE1DnMVco/E1Ql7ZYqi8wSb
nTAeBgNVHRIEFzAVhhNodHRwczovL3RydXN0LmdvLmlkMEAGA1UdHwQ5MDcwNaAz
oDGGL2h0dHBzOi8vcmVnaXN0cnkudHJ1c3QuZ28uaWQvY3JsL2lzc3Vlci1yb290
LWNhMAoGCCqGSM49BAMCA0gAMEUCIQDqrFLr10FuZNUqAoNP4lbrJt2V/inIMEbY
t4ibx+KOFgIgWk9Hf7yMftPdsN1EDpsCmasACm4CN25dzEtUdRzgbYhZCRamZ3Zl
cnNpb25jMS4wbXZpY2FsUHJvdmlkZXJ4IlRydXN0IEF1dGhvcml0eSBSZXB1Ymxp
ayBJbmRvbmVzaWFkZGF0ZcB0MjAyNi0xMC0xN1QwNjowMDowMFpsdmljYWxJc3N1
ZUlEBGpuZXh0VXBkYXRlwHQyMDI2LTEwLTE4VDA2OjAwOjAwWnBjZXJ0aWZpY2F0
ZUluZm9zgqtrY2VydGlmaWNhdGVZAlgwggJUMIIB+6ADAgECAgwseZCC7kRw+XMo
3c0wCgYIKoZIzj0EAwIwWTELMAkGA1UEBhMCSUQxKzApBgNVBAoMIlRydXN0IEF1
dGhvcml0eSBSZXB1YmxpayBJbmRvbmVzaWExHTAbBgNVBAMMFElEQ1RGIElzc3Vl
ciBSb290IENBMB4XDTI2MDEwMTAwMDAwMFoXDTQxMDEwMTAwMDAwMFowWTELMAkG
A1UEBhMCSUQxKzApBgNVBAoMIlRydXN0IEF1dGhvcml0eSBSZXB1YmxpayBJbmRv
bmVzaWExHTAbBgNVBAMMFElEQ1RGIElzc3VlciBSb290IENBMFkwEwYHKoZIzj0C
AQYIKoZIzj0DAQcDQgAEvyipmJODPkSQhdzcGXENifkSSzHOm1HNe+MpncgW2KfL
rdwNlb2z1HbXTdp+yBdxvnnGM42xw8EkTsGXIy6CnaOBqDCBpTASBgNVHRMBAf8E
CDAGAQH/AgEAMA4GA1UdDwEB/wQEAwIBBjAdBgNVHQ4EFgQU+/DVarC/2oBKMu3d
M8zJ3dKDeZowHgYDVR0SBBcwFYYTaHR0cHM6Ly90cnVzdC5nby5pZDBABgNVHR8E
OTA3MDWgM6Axhi9odHRwczovL3JlZ2lzdHJ5LnRydXN0LmdvLmlkL2NybC9pc3N1
ZXItcm9vdC1jYTAKBggqhkjOPQQDAgNHADBEAiBitHgtKUBkPwzIkW017MuoLuZ2
CFmb3YkqUglehtdOMgIgbvXzrbElsP9Rg5J5R5oyWhnkSR5w4v0vl70gmND5fBRs
c2VyaWFsTnVtYmVywkwseZCC7kRw+XMo3c1jc2tpVPvw1Wqwv9qASjLt3TPMyd3S
g3maZ2RvY1R5cGWCbmlkLmlkY3RmLmt0cC4xdW9yZy5pc28uMTgwMTMuNS4xLm1E
THJjZXJ0aWZpY2F0ZVByb2ZpbGWBbzEuMC4xODAxMy41LjEuN3Bpc3N1aW5nQXV0
aG9yaXR5eCJUcnVzdCBBdXRob3JpdHkgUmVwdWJsaWsgSW5kb25lc2lhbmlzc3Vp
bmdDb3VudHJ5YklEZmlzc3VlclhbMFkxCzAJBgNVBAYTAklEMSswKQYDVQQKDCJU
cnVzdCBBdXRob3JpdHkgUmVwdWJsaWsgSW5kb25lc2lhMR0wGwYDVQQDDBRJRENU
RiBJc3N1ZXIgUm9vdCBDQWdzdWJqZWN0WFswWTELMAkGA1UEBhMCSUQxKzApBgNV
BAoMIlRydXN0IEF1dGhvcml0eSBSZXB1YmxpayBJbmRvbmVzaWExHTAbBgNVBAMM
FElEQ1RGIElzc3VlciBSb290IENBaW5vdEJlZm9yZcB0MjAyNi0wMS0wMVQwMDow
MDowMFpobm90QWZ0ZXLAdDIwNDEtMDEtMDFUMDA6MDA6MDBaq2tjZXJ0aWZpY2F0
ZVkCVzCCAlMwggH6oAMCAQICDFu7qdThBf90roTF7TAKBggqhkjOPQQDAjBhMQsw
CQYDVQQGEwJNWTEsMCoGA1UECgwjSmFiYXRhbiBQZW5nYW5na3V0YW4gSmFsYW4g
TWFsYXlzaWExJDAiBgNVBAMMG01ZREwgSXNzdWluZyBBdXRob3JpdHkgUm9vdDAe
Fw0yNTAzMDEwMDAwMDBaFw0zNTAzMDEwMDAwMDBaMGExCzAJBgNVBAYTAk1ZMSww
KgYDVQQKDCNKYWJhdGFuIFBlbmdhbmdrdXRhbiBKYWxhbiBNYWxheXNpYTEkMCIG
A1UEAwwbTVlETCBJc3N1aW5nIEF1dGhvcml0eSBSb290MFkwEwYHKoZIzj0CAQYI
KoZIzj0DAQcDQgAEuX1BRzeX9rjEAqpkWP51kLS2jVkeF45rCH2YFnWFlHXtbTEa
ub1kMjXQ8pAIJnhbkFNu8j2HAMEsM0C3Gayxz6OBlzCBlDASBgNVHRMBAf8ECDAG
AQH/AgEAMA4GA1UdDwEB/wQEAwIBBjAdBgNVHQ4EFgQU4Vw5byzyYAAHylrSqRSd
3FMU+kgwHQYDVR0SBBYwFIYSaHR0cHM6Ly9qcGouZ292Lm15MDAGA1UdHwQpMCcw
JaAjoCGGH2h0dHBzOi8vcGtpLmpwai5nb3YubXkvY3JsL2lhY2EwCgYIKoZIzj0E
AwIDRwAwRAIgK/VvTpxvCepCFkGVFNS1pEx1Susk9cPvNBurUOejAsQCIHYugMos
l8NK/YQftsOTDC4otmt4TouD6Ng+z4A7eYHDbHNlcmlhbE51bWJlcsJMW7up1OEF
/3SuhMXtY3NraVThXDlvLPJgAAfKWtKpFJ3cUxT6SGdkb2NUeXBlgXVvcmcuaXNv
LjE4MDEzLjUuMS5tRExyY2VydGlmaWNhdGVQcm9maWxlgW8xLjAuMTgwMTMuNS4x
LjdwaXNzdWluZ0F1dGhvcml0eXgjSmFiYXRhbiBQZW5nYW5na3V0YW4gSmFsYW4g
TWFsYXlzaWFuaXNzdWluZ0NvdW50cnliTVlmaXNzdWVyWGMwYTELMAkGA1UEBhMC
TVkxLDAqBgNVBAoMI0phYmF0YW4gUGVuZ2FuZ2t1dGFuIEphbGFuIE1hbGF5c2lh
MSQwIgYDVQQDDBtNWURMIElzc3VpbmcgQXV0aG9yaXR5IFJvb3Rnc3ViamVjdFhj
MGExCzAJBgNVBAYTAk1ZMSwwKgYDVQQKDCNKYWJhdGFuIFBlbmdhbmdrdXRhbiBK
YWxhbiBNYWxheXNpYTEkMCIGA1UEAwwbTVlETCBJc3N1aW5nIEF1dGhvcml0eSBS
b290aW5vdEJlZm9yZcB0MjAyNS0wMy0wMVQwMDowMDowMFpobm90QWZ0ZXLAdDIw
MzUtMDMtMDFUMDA6MDA6MDBaWECCaoGAsXUfRs6PNbxTBsMkGGbLD3Dh2X6aVwXy
a67GNmrCK7yu1RMZxrylvF+o6ewDy6tO8SgEm0lAzgPkuxnX
```

## Common rules {#ts-5-04-common-rules}

Every certificate below is read by implementations the ecosystem does not
write, so the room a profile leaves is room for a reader to disagree. These
rules hold for all seven certificates the ecosystem issues. They bind no
certificate of another ecosystem, which reaches a reader through the VICAL
under the profile its own authority issued it in.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-04-007 }**REQ-TS-5-04-007** Every certificate MUST be an X.509 version 3 certificate, DER encoded, as [RFC 5280][ref-rfc5280] and [ISO/IEC 18013-5][ref-iso-18013-5] Annex B require.
- [](){ #req-ts-5-04-008 }**REQ-TS-5-04-008** The issuer of a certificate MUST set its serial number to a positive, non-sequential, non-zero integer carrying at least 63 bits from a cryptographically secure random number generator, at most 20 octets long.
- [](){ #req-ts-5-04-009 }**REQ-TS-5-04-009** The issuer of a certificate SHOULD set a serial number carrying at least 71 bits from that generator.
- [](){ #req-ts-5-04-010 }**REQ-TS-5-04-010** Every certified public key MUST be an elliptic curve key on P-256, encoded in uncompressed form, with the curve named by the object identifier `1.2.840.10045.3.1.7`.
- [](){ #req-ts-5-04-011 }**REQ-TS-5-04-011** Every certificate MUST be signed with ECDSA and SHA-256, the object identifier `1.2.840.10045.4.3.2`.
- [](){ #req-ts-5-04-012 }**REQ-TS-5-04-012** Every certificate MUST carry a subject key identifier, the SHA-1 hash of the subject public key bit string as [ISO/IEC 18013-5][ref-iso-18013-5] Annex B defines it, marked non-critical.
- [](){ #req-ts-5-04-013 }**REQ-TS-5-04-013** Every certificate except a self-signed root MUST carry an authority key identifier holding the subject key identifier of the certificate that signed it, marked non-critical.
- [](){ #req-ts-5-04-014 }**REQ-TS-5-04-014** Every certificate MUST carry a `countryName` of `ID` in its subject, in upper case, as a `PrintableString`.
- [](){ #req-ts-5-04-015 }**REQ-TS-5-04-015** Every certificate MUST carry a `commonName` in its subject.
- [](){ #req-ts-5-04-016 }**REQ-TS-5-04-016** A certificate MUST NOT carry a `PolicyMappings`, `NameConstraints`, `PolicyConstraints`, `InhibitAnyPolicy`, or `FreshestCRL` extension.
- [](){ #req-ts-5-04-017 }**REQ-TS-5-04-017** A certificate MUST NOT carry a critical extension this specification does not name.
- [](){ #req-ts-5-04-018 }**REQ-TS-5-04-018** Trust Authority MUST NOT generate or hold the private key of any certificate it issues.

</div>

One curve and one signature algorithm, where Annex B admits several, because
every key in the ecosystem outside the `did:webvh` log is P-256, as
[the technology map][technology-map] records, and a reader that meets only
what it was built for meets everything. The last rule is the one the whole
chain rests on: a certificate introduces no new key, and the key it certifies
was born in the Key Manager, the secure element, or the HSM of the party the
certificate names, as [three places a key can live][three-places-a-key-can-live]
sets out.

## The two roots {#ts-5-04-the-two-roots}

The Issuer Root CA is the root of the issuer side and the Verifier Root CA
of the reader side. Each is self-signed in an offline HSM of its own, and
neither ever signs the other, for the reason
[two parallel roots that never sign each other][two-parallel-roots-that-never-sign-each-other]
gives: a key leaked on one side must not let anyone act on the other. They
are the only certificates in the ecosystem not issued from a certificate
signing request.

The Issuer Root CA is the Issuing Authority Certificate Authority (IACA) root certificate of
[ISO/IEC 18013-5][ref-iso-18013-5] Annex B, and its profile is that one. The
standard says nothing about the reader side beyond the leaf, and leaves the
certificate authority above it out of scope, so the Verifier Root CA and the
Verifier Issuing CA take the profile below, built on [RFC 5280][ref-rfc5280]
and shaped like the issuer side so that one validator serves both. The two
differ in one place: the issuer side is two levels deep and the reader side
three, so the Issuer Root CA carries a path length of zero and the Verifier
Root CA a path length of one.

[](){ #tbl-ts-5-04-root-profile }

<figure markdown="1" class="ekdn-table">

| Field | Presence | Value |
|---|---|---|
| Version | Mandatory | v3 |
| Serial number | Mandatory | As [Common rules][ts-5-04-common-rules] |
| Issuer, and Subject | Mandatory | The same binary value: `countryName` `ID`, `commonName`, and the `organizationName` of the body that holds the Root Authority role |
| Validity, not before | Mandatory | The date the root enters use |
| Validity, not after | Mandatory | At most 20 years after not before, and no longer than the sum the Governance Profile computes |
| Subject public key info | Mandatory | P-256, uncompressed |
| Basic constraints | Mandatory, critical | `CA:TRUE`; `pathLenConstraint` `0` for the Issuer Root CA, `1` for the Verifier Root CA |
| Key usage | Mandatory, critical | `keyCertSign` and `cRLSign` only |
| Subject key identifier | Mandatory, non-critical | As [Common rules][ts-5-04-common-rules] |
| Issuer alternative name | Mandatory, non-critical | At least one of `rfc822Name` or `uniformResourceIdentifier`, the contact address of Trust Authority |
| CRL distribution points | Mandatory, non-critical | The address at which Trust Registry serves that root's certificate revocation list; no `reasons` and no `cRLIssuer` field |
| Extended key usage | Absent | Absent |
| Signature algorithm | Mandatory | ECDSA with SHA-256 |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-04-019 }**REQ-TS-5-04-019** Trust Authority MUST issue the Issuer Root CA as a self-signed certificate meeting [the root profile][tbl-ts-5-04-root-profile] and the IACA root certificate profile of [ISO/IEC 18013-5][ref-iso-18013-5] Annex B.
- [](){ #req-ts-5-04-020 }**REQ-TS-5-04-020** Trust Authority MUST issue the Verifier Root CA as a self-signed certificate meeting [the root profile][tbl-ts-5-04-root-profile].
- [](){ #req-ts-5-04-021 }**REQ-TS-5-04-021** Trust Authority MUST hold each root key in an offline HSM validated to [FIPS 140-3][ref-fips-140-3] Level 3, one HSM per root.
- [](){ #req-ts-5-04-022 }**REQ-TS-5-04-022** Trust Authority MUST NOT hold a root key in a software HSM, including in a sandbox that will later carry production traffic.
- [](){ #req-ts-5-04-023 }**REQ-TS-5-04-023** Trust Authority MUST NOT sign a certificate with one root whose subject public key is that of the other root.
- [](){ #req-ts-5-04-024 }**REQ-TS-5-04-024** Trust Authority MUST NOT sign any certificate with the Issuer Root CA except a Document Signer Certificate, a status list signer certificate, a VICAL signer certificate, and a link certificate.
- [](){ #req-ts-5-04-025 }**REQ-TS-5-04-025** Trust Authority MUST NOT sign any certificate with the Verifier Root CA except a Verifier Issuing CA certificate and a link certificate.
- [](){ #req-ts-5-04-026 }**REQ-TS-5-04-026** Trust Authority MUST set the not after date of a root to the sum of the longest validity period of the certificates it will sign, the period during which it will sign them, and the lead time to distribute it, as the Governance Profile fixes each of the three.
- [](){ #req-ts-5-04-027 }**REQ-TS-5-04-027** Trust Authority MUST NOT issue a certificate whose not after date is later than that of the root that signs it.

</div>

A root reaches a reader at build time, so replacing
one is planned long before it is needed and cut while the old root is still
valid. The old root signs a link certificate over the new one, which is the
re-key mechanism of Annex B, so a reader holding the old root can follow it
to the new; the new root also travels in the VICAL and in the next release
of Mobile Wallet, Mobile Verifier, and Trust SDK, as
[how Trust Authority's keys are replaced][how-trust-authoritys-keys-are-replaced]
sets out.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-04-028 }**REQ-TS-5-04-028** When Trust Authority replaces a root, it MUST issue a link certificate signed with the old root key, whose subject and subject public key are those of the new root, meeting the IACA link certificate profile of [ISO/IEC 18013-5][ref-iso-18013-5] Annex B.
- [](){ #req-ts-5-04-029 }**REQ-TS-5-04-029** The not after date of a link certificate MUST NOT be later than that of the old root.
- [](){ #req-ts-5-04-030 }**REQ-TS-5-04-030** Trust Authority MUST go on issuing certificates under the old root until the new root has reached the field.
- [](){ #req-ts-5-04-113 }**REQ-TS-5-04-113** Trust Authority MUST NOT withdraw a certificate issued under the old root because the root was replaced.

</div>

## Document Signer Certificate {#ts-5-04-document-signer-certificate}

The leaf of the issuer side. An issuer holds one, unless the
`dsc_per_group_of_types` member of the Governance Profile, which
[Key storage and permissions][ts-02-key-storage-and-permissions] defines,
lets it hold one per group of credential types whose ceilings under
[REQ-TS-5-04-036][req-ts-5-04-036] and [REQ-TS-5-04-037][req-ts-5-04-037]
differ. One certificate answers to the shortest ceiling among the types its
issuer signs, so an issuer of an mDL and of any other document type holds
one valid at most 457 days. The mdoc carries whichever certificate signed
it, so nothing downstream depends on the count.

A certificate is issued in six steps, and the key never moves.

1. The issuer's Key Manager generates the `issuance-cose` key in the driver
   the issuer's grade allows.
2. Key Manager builds a certificate signing request under
   [RFC 2986][ref-rfc2986] over that key and signs it with the key itself.
3. The issuer submits the request to Trust Authority.
4. Trust Authority checks the signature on the request, the subject against
   the registration, and the storage evidence of the driver the key lives in.
5. Trust Authority issues the certificate from the Issuer Root CA and
   records the key in its Public Key Registry.
6. The issuer downloads the certificate and loads it at startup, after
   checking it chains to the root and matches the key in its keystore.

[](){ #tbl-ts-5-04-dsc-profile }

<figure markdown="1" class="ekdn-table">

| Field | Presence | Value |
|---|---|---|
| Version | Mandatory | v3 |
| Serial number | Mandatory | As [Common rules][ts-5-04-common-rules] |
| Issuer | Mandatory | The same binary value as the subject of the Issuer Root CA |
| Validity, not after | Mandatory | At most 457 days after not before for an mDL, at most 3650 days for any other document type, and never later than the root |
| Subject | Mandatory | `countryName` `ID`, the `organizationName` of the issuing body, and a `commonName` naming the certificate |
| Subject public key info | Mandatory | P-256, uncompressed, the `issuance-cose` key of the request |
| Basic constraints | Mandatory, critical | `CA:FALSE` |
| Key usage | Mandatory, critical | `digitalSignature` only |
| Extended key usage | Mandatory, critical | `1.0.18013.5.1.2`, mdoc document signing, and nothing else |
| Authority key identifier | Mandatory, non-critical | The subject key identifier of the Issuer Root CA |
| Subject key identifier | Mandatory, non-critical | As [Common rules][ts-5-04-common-rules] |
| Issuer alternative name | Mandatory, non-critical | At least one of `rfc822Name` or `uniformResourceIdentifier`, the contact address of Trust Authority |
| CRL distribution points | Mandatory, non-critical | The address at which Trust Registry serves the Issuer Root CA certificate revocation list |
| Signature algorithm | Mandatory | ECDSA with SHA-256 |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-04-031 }**REQ-TS-5-04-031** Issuer Core MUST generate the `issuance-cose` key in its Key Manager.
- [](){ #req-ts-5-04-114 }**REQ-TS-5-04-114** Issuer Core MUST NOT send the private key of `issuance-cose` anywhere.
- [](){ #req-ts-5-04-032 }**REQ-TS-5-04-032** Issuer Core MUST request a Document Signer Certificate with a certificate signing request under [RFC 2986][ref-rfc2986], signed with the key the request carries.
- [](){ #req-ts-5-04-033 }**REQ-TS-5-04-033** Trust Authority MUST verify the signature on a certificate signing request with the public key inside it before issuing anything.
- [](){ #req-ts-5-04-034 }**REQ-TS-5-04-034** Trust Authority MUST refuse a request whose subject does not match the registration that submitted it.
- [](){ #req-ts-5-04-165 }**REQ-TS-5-04-165** Trust Authority MUST refuse a certificate signing request for a Document Signer Certificate from an issuer that holds no permission in force to issue a type whose Credential Rulebook names an mdoc representation.
- [](){ #req-ts-5-04-035 }**REQ-TS-5-04-035** Trust Authority MUST issue a Document Signer Certificate from the Issuer Root CA, meeting [the Document Signer Certificate profile][tbl-ts-5-04-dsc-profile] and the issuer-side leaf profile of [ISO/IEC 18013-5][ref-iso-18013-5] Annex B.
- [](){ #req-ts-5-04-036 }**REQ-TS-5-04-036** Trust Authority MUST NOT issue a Document Signer Certificate valid for more than 457 days to an issuer of an mDL.
- [](){ #req-ts-5-04-037 }**REQ-TS-5-04-037** Trust Authority MUST NOT issue a Document Signer Certificate valid for more than 3650 days for any other document type.
- [](){ #req-ts-5-04-038 }**REQ-TS-5-04-038** Trust Authority MUST record the certified key in its Public Key Registry, with its purpose and its storage evidence, before returning the certificate.
- [](){ #req-ts-5-04-039 }**REQ-TS-5-04-039** Issuer Core MUST check, at startup, that its Document Signer Certificate chains to the Issuer Root CA, is inside its validity period, and certifies the key its Key Manager holds.
- [](){ #req-ts-5-04-040 }**REQ-TS-5-04-040** Issuer Core MUST stop issuing mdoc credentials when that check fails.
- [](){ #req-ts-5-04-041 }**REQ-TS-5-04-041** Issuer Core MUST place its Document Signer Certificate in the `x5chain` of every mdoc it signs.
- [](){ #req-ts-5-04-042 }**REQ-TS-5-04-042** Issuer Core MUST NOT place the Issuer Root CA in `x5chain`.
- [](){ #req-ts-5-04-043 }**REQ-TS-5-04-043** Issuer Core MUST renew a Document Signer Certificate with a new certificate signing request over the key it already holds.
- [](){ #req-ts-5-04-115 }**REQ-TS-5-04-115** Issuer Core MUST NOT generate a new key to renew a Document Signer Certificate.
- [](){ #req-ts-5-04-162 }**REQ-TS-5-04-162** Trust Authority MUST warn the issuer by e-mail, at the address of its registration and at the address of the person answerable for it, once less than the warning period the Governance Profile sets remains before a Document Signer Certificate it issued expires and no renewed certificate has been issued.
- [](){ #req-ts-5-04-163 }**REQ-TS-5-04-163** Trust Authority MUST show the same warning in the portal until a renewed certificate is issued or the certificate expires.
- [](){ #req-ts-5-04-164 }**REQ-TS-5-04-164** Issuer Core SHOULD report to its operator, from the same moment, that its Document Signer Certificate is about to expire.

</div>

Renewal keeps the key, so the DID Document is untouched and nothing that the
old certificate signed stops verifying. Replacing the key is a rotation
instead, which runs the path
[how an entity rotates a key][how-an-entity-rotates-a-key] sets out and ends
with a certificate issued from a request over the new key. An expired
certificate stops the whole of an issuer's mdoc issuance, and Issuer Core
checks its certificate only at startup, so the warning that expiry is
approaching is set far ahead; how far is the Governance Profile's to say.
Trust Authority sends it, because it holds the registration's contact data,
and Issuer Core repeats it to its own operator,
[REQ-TS-5-04-162][req-ts-5-04-162] to [REQ-TS-5-04-164][req-ts-5-04-164].

## Status list signer certificate {#ts-5-04-status-list-signer-certificate}

The leaf that certifies an issuer's `status-list` key. The key stays where
[Publishing and resolving a did:webvh identifier](publishing-and-resolving-a-did-webvh-identifier.md)
puts it, in the issuer's DID Document, and signs both forms of the issuer's
credential status list. The certificate gives the same key an X.509 path for
the CWT form, which an mdoc reader checks the way it checks the mdoc: under
the Issuer Root CA it carries from build time, or under the root a verified
VICAL carries. A key published only in a DID Document has no such path, and
a reader with no DID resolver could not check the status of an mdoc at all.

The certificate is issued in the six steps of
[Document Signer Certificate][ts-5-04-document-signer-certificate], over the
`status-list` key instead of `issuance-cose`. It is a key of its own rather
than the Document Signer Certificate, because the list that revokes what a
key signed cannot be signed by that key, as
[Signature][ts-5-09-signature] of TS-5-09 sets out. Its subject repeats the
`organizationName` of the issuer's Document Signer Certificate, and that
name is the link: one Issuer Root CA certifies every issuer, so a chain to
it proves that a certificate is accredited, and only the name says whose it
is.

It carries no extended key usage. [IETF Token Status List][ref-i-d-ietf-oauth-status-list]
defines `id-kp-oauthStatusSigning` for this certificate, and the second
edition of [ISO/IEC 18013-5][ref-iso-18013-5], still a draft, makes it
optional and non-critical. The object identifier is still unassigned, so a
certificate cannot carry it yet. Without it, the profile still keeps the
certificate apart from the Document Signer Certificate, whose extended key
usage is critical.

[](){ #tbl-ts-5-04-status-list-signer-profile }

<figure markdown="1" class="ekdn-table">

| Field | Presence | Value |
|---|---|---|
| Version | Mandatory | v3 |
| Serial number | Mandatory | As [Common rules][ts-5-04-common-rules] |
| Issuer | Mandatory | The same binary value as the subject of the Issuer Root CA |
| Validity, not after | Mandatory | At most 1187 days after not before, and never later than the root |
| Subject | Mandatory | `countryName` `ID`, the `organizationName` of the issuing body as the same binary value its Document Signer Certificate carries, and a `commonName` naming the certificate |
| Subject public key info | Mandatory | P-256, uncompressed, the `status-list` key of the request |
| Basic constraints | Mandatory, critical | `CA:FALSE` |
| Key usage | Mandatory, critical | `digitalSignature` only |
| Extended key usage | Absent | Absent |
| Authority key identifier | Mandatory, non-critical | The subject key identifier of the Issuer Root CA |
| Subject key identifier | Mandatory, non-critical | As [Common rules][ts-5-04-common-rules] |
| Issuer alternative name | Mandatory, non-critical | At least one of `rfc822Name` or `uniformResourceIdentifier`, the contact address of Trust Authority |
| CRL distribution points | Mandatory, non-critical | The address at which Trust Registry serves the Issuer Root CA certificate revocation list |
| Signature algorithm | Mandatory | ECDSA with SHA-256 |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-04-129 }**REQ-TS-5-04-129** Issuer Core that issues credentials in mdoc MUST hold a status list signer certificate over its `status-list` key.
- [](){ #req-ts-5-04-130 }**REQ-TS-5-04-130** Issuer Core MUST request a status list signer certificate with a certificate signing request under [RFC 2986][ref-rfc2986], signed with the `status-list` key the request carries.
- [](){ #req-ts-5-04-131 }**REQ-TS-5-04-131** Trust Authority MUST refuse a request for a status list signer certificate whose key is not the `status-list` key the issuer's DID Document publishes.
- [](){ #req-ts-5-04-132 }**REQ-TS-5-04-132** Trust Authority MUST issue a status list signer certificate from the Issuer Root CA, meeting [the status list signer certificate profile][tbl-ts-5-04-status-list-signer-profile].
- [](){ #req-ts-5-04-133 }**REQ-TS-5-04-133** Trust Authority MUST set the `organizationName` of a status list signer certificate to the same binary value as that of the issuer's Document Signer Certificate.
- [](){ #req-ts-5-04-134 }**REQ-TS-5-04-134** Trust Authority MUST NOT issue a status list signer certificate valid for more than 1187 days.
- [](){ #req-ts-5-04-135 }**REQ-TS-5-04-135** Trust Authority MUST NOT issue a status list signer certificate over a key that a Document Signer Certificate certifies.
- [](){ #req-ts-5-04-136 }**REQ-TS-5-04-136** Issuer Core MUST renew a status list signer certificate with a new certificate signing request over the key it already holds.

</div>

Renewal keeps the key, as it does for the Document Signer Certificate, so
the DID Document and every list already published are untouched. A rotation
of the `status-list` key ends with a certificate issued from a request over
the new key.

## Verifier Issuing CA {#ts-5-04-verifier-issuing-ca}

The intermediate of the reader side, held by an RP Intermediary and by a
Relying Party that reads credentials in proximity at its own counter. It is
issued the same way a Document Signer Certificate is, from a certificate
signing request, and it is the certificate the trusted list names, which is
what ties a reader chain to an accredited entity.

[](){ #tbl-ts-5-04-issuing-ca-profile }

<figure markdown="1" class="ekdn-table">

| Field | Presence | Value |
|---|---|---|
| Version | Mandatory | v3 |
| Serial number | Mandatory | As [Common rules][ts-5-04-common-rules] |
| Issuer | Mandatory | The same binary value as the subject of the Verifier Root CA |
| Validity, not after | Mandatory | The period the Governance Profile sets, never later than the root |
| Subject | Mandatory | `countryName` `ID`, the `organizationName` of the entity, and a `commonName` naming the certificate authority |
| Subject public key info | Mandatory | P-256, uncompressed, the Verifier Issuing CA key of the request |
| Basic constraints | Mandatory, critical | `CA:TRUE`, `pathLenConstraint` `0` |
| Key usage | Mandatory, critical | `keyCertSign` and `cRLSign` only |
| Extended key usage | Mandatory, non-critical | `1.0.18013.5.1.6`, mdoc reader authentication, and nothing else |
| Authority key identifier | Mandatory, non-critical | The subject key identifier of the Verifier Root CA |
| Subject key identifier | Mandatory, non-critical | The value the entity's trusted list entry names for this certificate authority |
| CRL distribution points | Mandatory, non-critical | The address at which Trust Registry serves the Verifier Root CA certificate revocation list |
| Signature algorithm | Mandatory | ECDSA with SHA-256 |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-04-044 }**REQ-TS-5-04-044** Verifier Core MUST generate its Verifier Issuing CA key in a cloud Key Management Service or an HSM.
- [](){ #req-ts-5-04-116 }**REQ-TS-5-04-116** Verifier Core MUST NOT hold its Verifier Issuing CA key in the software keystore.
- [](){ #req-ts-5-04-045 }**REQ-TS-5-04-045** Verifier Core MUST request its Verifier Issuing CA certificate with a certificate signing request under [RFC 2986][ref-rfc2986], signed with the key the request carries.
- [](){ #req-ts-5-04-046 }**REQ-TS-5-04-046** Trust Authority MUST issue a Verifier Issuing CA certificate from the Verifier Root CA, meeting [the Verifier Issuing CA profile][tbl-ts-5-04-issuing-ca-profile].
- [](){ #req-ts-5-04-047 }**REQ-TS-5-04-047** Trust Authority MUST issue a Verifier Issuing CA certificate only to a registration the trusted list carries as an RP Intermediary, or as a Relying Party that reads credentials in proximity.
- [](){ #req-ts-5-04-048 }**REQ-TS-5-04-048** Trust Authority MUST record the subject key identifier of every Verifier Issuing CA certificate it issues against the entity's registration, so that Trust Registry names it in the entity's trusted list entry.
- [](){ #req-ts-5-04-049 }**REQ-TS-5-04-049** Trust Authority MUST NOT issue a Verifier Issuing CA certificate whose `pathLenConstraint` is other than `0`.
- [](){ #req-ts-5-04-050 }**REQ-TS-5-04-050** Verifier Core MUST NOT sign anything with the Verifier Issuing CA key except a Verifier Device Certificate and the certificate revocation list that withdraws one.
- [](){ #req-ts-5-04-051 }**REQ-TS-5-04-051** Verifier Core MUST NOT issue a Verifier Device Certificate whose not after date is later than that of its Verifier Issuing CA certificate.
- [](){ #req-ts-5-04-052 }**REQ-TS-5-04-052** Trust Authority MUST withdraw a Verifier Issuing CA certificate on the Verifier Root CA certificate revocation list when the Root Authority revokes that certificate authority.

</div>

The extended key usage sits on the intermediate as well as on the leaf, so
that a validator which carries the purpose down the chain refuses a device
certificate issued for anything else. It is non-critical there because a
certificate authority signs certificates rather than requests, and a
validator that reads a critical extended key usage as a bound on the
certificate itself would reject a key that legitimately signs certificates.

A stolen Verifier Issuing CA key mints reader devices that chain correctly
until the certificate authority is struck, which is why the key may not live
in the software driver and why the trusted list carries the certificate
authority by its subject key identifier: the entry is struck and the
certificate put on the list, while the entity itself stays granted, as
[the reader side][the-reader-side] sets out.

## Verifier Device Certificate {#ts-5-04-verifier-device-certificate}

One certificate per reader device, over the device key that was generated in
that device's secure element. It is the mdoc reader authentication
certificate of [ISO/IEC 18013-5][ref-iso-18013-5] Annex B, with one
extension of the ecosystem's own, and it serves both channels: in proximity
it signs the ReaderAuth of a DeviceRequest, and online a merchant signs its
request with the same certificate.

A certificate is issued in five steps.

1. The device generates its device key in the secure element at
   provisioning.
2. The device sends the public key with the platform evidence of the chip to
   the Verifier Core that vouches for it.
3. Verifier Core checks that evidence and the registration behind the
   device, and takes the attributes the device may ask for from the Use
   Statement handed over with it.
4. Verifier Core issues the certificate from its Verifier Issuing CA, with
   those attributes in `ReaderAuthRole`.
5. The device loads the certificate and signs with the key that never left
   its secure element.

[](){ #tbl-ts-5-04-device-certificate-profile }

<figure markdown="1" class="ekdn-table">

| Field | Presence | Value |
|---|---|---|
| Version | Mandatory | v3 |
| Serial number | Mandatory | As [Common rules][ts-5-04-common-rules] |
| Issuer | Mandatory | The same binary value as the subject of the Verifier Issuing CA certificate |
| Validity, not after | Mandatory | At most 1187 days after not before, and at most the period the Governance Profile sets |
| Subject | Mandatory | `countryName` `ID`, a `commonName` naming the device holder, and the `organizationName` of the entity that vouches for it |
| Subject public key info | Mandatory | P-256, uncompressed, the device key |
| Basic constraints | Mandatory, critical | `CA:FALSE` |
| Key usage | Mandatory, critical | `digitalSignature` only |
| Extended key usage | Mandatory, critical | `1.0.18013.5.1.6`, mdoc reader authentication, and nothing else |
| Authority key identifier | Mandatory, non-critical | The subject key identifier of the Verifier Issuing CA certificate |
| Subject key identifier | Mandatory, non-critical | As [Common rules][ts-5-04-common-rules] |
| `ReaderAuthRole` | Mandatory, non-critical | The document types and the data elements this device may ask for |
| CRL distribution points | Mandatory, non-critical | The address at which the holder of the Verifier Issuing CA serves its certificate revocation list |
| Signature algorithm | Mandatory | ECDSA with SHA-256 |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-04-053 }**REQ-TS-5-04-053** Verifier Core MUST issue one Verifier Device Certificate per reader device, from its own Verifier Issuing CA, meeting [the Verifier Device Certificate profile][tbl-ts-5-04-device-certificate-profile] and the mdoc reader authentication certificate profile of [ISO/IEC 18013-5][ref-iso-18013-5] Annex B.
- [](){ #req-ts-5-04-054 }**REQ-TS-5-04-054** Verifier Core MUST certify the device key the device generated in its secure element.
- [](){ #req-ts-5-04-117 }**REQ-TS-5-04-117** Verifier Core MUST NOT certify a device key generated anywhere but the secure element of the device.
- [](){ #req-ts-5-04-055 }**REQ-TS-5-04-055** Verifier Core MUST check the platform evidence of the device, as [The platform evidence of a reader device][ts-5-04-the-platform-evidence-of-a-reader-device] requires, before issuing or renewing the certificate.
- [](){ #req-ts-5-04-056 }**REQ-TS-5-04-056** Verifier Core MUST carry in `ReaderAuthRole` every document type and data element the device may ask for, and nothing else.
- [](){ #req-ts-5-04-057 }**REQ-TS-5-04-057** The set in `ReaderAuthRole` MUST be a subset of the union of the `claims` of the Use Statements the entity registered and bound to that device, each document type read as the `id` of the Rulebook whose mdoc `docType` it is or, where no Rulebook has that `docType`, as the `id` of a Rulebook that names no mdoc representation.
- [](){ #req-ts-5-04-058 }**REQ-TS-5-04-058** `ReaderAuthRole` MUST be marked non-critical, so that a reader outside the ecosystem ignores an extension it does not know rather than rejecting the certificate.
- [](){ #req-ts-5-04-059 }**REQ-TS-5-04-059** Verifier Core MUST NOT issue a Verifier Device Certificate to a device whose registration is withdrawn.
- [](){ #req-ts-5-04-060 }**REQ-TS-5-04-060** Verifier Core MUST issue a new certificate rather than extend one.
- [](){ #req-ts-5-04-118 }**REQ-TS-5-04-118** Verifier Core MUST NOT reissue a certificate over a key the device has replaced.
- [](){ #req-ts-5-04-061 }**REQ-TS-5-04-061** Mobile Verifier MUST hold its Verifier Device Certificate and the private key of the device key in the secure element that generated the key.
- [](){ #req-ts-5-04-062 }**REQ-TS-5-04-062** Mobile Verifier MUST NOT sign a DeviceRequest with any key but the one its certificate certifies.
- [](){ #req-ts-5-04-063 }**REQ-TS-5-04-063** Mobile Verifier MUST NOT ask for a document type or a data element outside the `ReaderAuthRole` of its certificate.
- [](){ #req-ts-5-04-064 }**REQ-TS-5-04-064** Verifier Core MUST put a device certificate on its certificate revocation list when the device is lost, replaced, or withdrawn before the certificate expires.

</div>

`ReaderAuthRole` carries the bound a wallet checks a request against before
the citizen is asked, as
[a central Relying Party vouching for a small one][verifier-device-certificate-for-a-small-verifier]
sets out. It is the second of three bounds on a merchant, the others being
the entity's accreditation and the Use Statement the request carries.

### The platform evidence of a reader device {#ts-5-04-the-platform-evidence-of-a-reader-device}

The platform evidence shows three things about a reader device: that its
device key sits in the device's secure hardware, that the official build of the
application that holds it generated it, and that the device is not tampered
with. It is the same kind of evidence
[Enrolling a wallet installation and attesting its key](enrolling-a-wallet-installation-and-attesting-its-key.md)
fixes for a wallet installation, and the rules below reuse its checks by
reference instead of restating them. On iOS the App Attest key is not the
device key: it signs only the assertions Verifier Core reads at renewal and
nothing a wallet reads, so the device still holds one device key.

This section fixes what each message proves and leaves how the message
travels. The transport, the endpoints and the encoding between Mobile
Verifier and Verifier Core belong to whoever runs Verifier Core, an RP
Intermediary or a Relying Party for its own counter device. An Assessment
Body tests the outcome: it hands Verifier Core good evidence and bad, and
checks which it certifies, which it renews, and which it refuses.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-04-138 }**REQ-TS-5-04-138** Verifier Core MUST issue a challenge that meets [REQ-TS-2-01-003][req-ts-2-01-003] and [REQ-TS-2-01-004][req-ts-2-01-004] for each activation and each renewal of a reader device.
- [](){ #req-ts-5-04-139 }**REQ-TS-5-04-139** Verifier Core MUST refuse an activation or a renewal whose challenge is older than the lifetime the Governance Profile sets for an enrollment challenge.
- [](){ #req-ts-5-04-140 }**REQ-TS-5-04-140** Mobile Verifier MUST form the activation binding string as the challenge, a period, and the base64url SHA-256 [RFC 7638][ref-rfc7638] thumbprint of the device key to be certified.
- [](){ #req-ts-5-04-141 }**REQ-TS-5-04-141** Verifier Core MUST recompute the activation binding string from the challenge and the device key the activation carries, and MUST refuse an activation whose integrity verdict on Android, or whose App Attest attestation on iOS, does not commit to the hash of that string.
- [](){ #req-ts-5-04-142 }**REQ-TS-5-04-142** On Android, Mobile Verifier MUST generate the device key in the Android keystore as a P-256 key whose only purposes are signing and verifying, with the activation challenge as the attestation challenge.
- [](){ #req-ts-5-04-143 }**REQ-TS-5-04-143** On Android, Mobile Verifier MUST obtain the integrity verdict with the base64url hash of the activation binding string as its request hash.
- [](){ #req-ts-5-04-144 }**REQ-TS-5-04-144** On Android, Mobile Verifier MUST send Verifier Core the device key, the attestation certificate chain of the device key, and the integrity token.
- [](){ #req-ts-5-04-145 }**REQ-TS-5-04-145** On Android, Verifier Core MUST check the chain and the KeyDescription of the device key as [REQ-TS-2-01-021][req-ts-2-01-021] to [REQ-TS-2-01-027][req-ts-2-01-027] and [REQ-TS-2-01-030][req-ts-2-01-030] require, with the activation challenge in place of the enrollment challenge and the package name and signing certificate digest of the official build of the application that holds the device key in place of the official Mobile Wallet build's.
- [](){ #req-ts-5-04-146 }**REQ-TS-5-04-146** On Android, Verifier Core MUST check the integrity verdict as [REQ-TS-2-01-031][req-ts-2-01-031] to [REQ-TS-2-01-034][req-ts-2-01-034] and [REQ-TS-02-027][req-ts-02-027] require, with the activation binding string in place of the enrollment binding string and the official build of the application that holds the device key in place of the official Mobile Wallet build.
- [](){ #req-ts-5-04-147 }**REQ-TS-5-04-147** On iOS, Mobile Verifier MUST generate the device key as a P-256 key in the Secure Enclave, not exportable, and MUST NOT use the App Attest key as the device key, because an App Attest key signs only assertions and never the `COSE_Sign1` of a ReaderAuth.
- [](){ #req-ts-5-04-148 }**REQ-TS-5-04-148** On iOS, Mobile Verifier MUST make the App Attest attestation with the hash of the activation binding string as its `clientDataHash`, and MUST send Verifier Core the device key, the App Attest key identifier, and the attestation.
- [](){ #req-ts-5-04-149 }**REQ-TS-5-04-149** On iOS, Verifier Core MUST check the attestation as [REQ-TS-2-01-039][req-ts-2-01-039] to [REQ-TS-2-01-043][req-ts-2-01-043] require, with the activation binding string in place of the enrollment binding string and the App ID of the official build of the application that holds the device key in place of the official Mobile Wallet build's.
- [](){ #req-ts-5-04-150 }**REQ-TS-5-04-150** On iOS, Verifier Core MUST treat the App Attest attestation that commits to the thumbprint of the device key as the evidence that the official build of the application that holds the device key generated that key in the Secure Enclave, as [REQ-TS-5-04-117][req-ts-5-04-117] requires and in the way [REQ-TS-2-01-044][req-ts-2-01-044] treats the credential key of a wallet.
- [](){ #req-ts-5-04-151 }**REQ-TS-5-04-151** Verifier Core MUST accept an attestation chain only if it ends at a root of [the table of accepted roots][tbl-ts-2-01-accepted-roots], and MUST apply [REQ-TS-2-01-045][req-ts-2-01-045] to [REQ-TS-2-01-048][req-ts-2-01-048] to the chains of reader devices.
- [](){ #req-ts-5-04-152 }**REQ-TS-5-04-152** Verifier Core MUST record for each reader device the public device key and, on iOS, the public key of the App Attest key and the counter of the last assertion it accepted.
- [](){ #req-ts-5-04-153 }**REQ-TS-5-04-153** Mobile Verifier MUST renew its Verifier Device Certificate over the same device key, and MUST form the renewal binding string as a fresh challenge from Verifier Core, a period, and the base64url SHA-256 [RFC 7638][ref-rfc7638] thumbprint of that key.
- [](){ #req-ts-5-04-154 }**REQ-TS-5-04-154** On Android, Mobile Verifier MUST sign the UTF-8 octets of the renewal binding string with the device key, as ES256 in the form Section 3.4 of [RFC 7518][ref-rfc7518] defines, and MUST obtain a fresh integrity verdict with the base64url hash of that string as its request hash.
- [](){ #req-ts-5-04-155 }**REQ-TS-5-04-155** On Android, Verifier Core MUST refuse a renewal whose signature does not verify under the recorded device key, and MUST check the verdict as [REQ-TS-2-01-031][req-ts-2-01-031] to [REQ-TS-2-01-034][req-ts-2-01-034] require, with the renewal binding string in place of the enrollment binding string.
- [](){ #req-ts-5-04-156 }**REQ-TS-5-04-156** On iOS, Mobile Verifier MUST sign the UTF-8 octets of the renewal binding string with the device key, as ES256 in the form Section 3.4 of [RFC 7518][ref-rfc7518] defines, and MUST generate an App Attest assertion with the hash of that string as its `clientDataHash`.
- [](){ #req-ts-5-04-157 }**REQ-TS-5-04-157** On iOS, Verifier Core MUST refuse a renewal whose signature does not verify under the recorded device key, and MUST check the assertion as [REQ-TS-2-01-066][req-ts-2-01-066] to [REQ-TS-2-01-068][req-ts-2-01-068] require, against the recorded App Attest key and counter.

</div>

### The ReaderAuthRole extension {#ts-5-04-the-readerauthrole-extension}

ISO/IEC 18013-5 defines no extension that bounds what a reader may ask for,
so this one is the ecosystem's own. It is a `SEQUENCE OF` one entry per
document type, each entry naming the document type and the data elements
the device may ask for under it, every string a `UTF8String` holding an
identifier exactly as the Credential Rulebook of that type writes it. An
entry names no namespace, because a Rulebook that names an mdoc
representation fixes one namespace for it. An entry names a type by its mdoc
`docType` where the Rulebook of the type names an mdoc representation, and by
the `id` of that Rulebook where it names none, so that a type issued only as
SD-JWT VC or `ldp_vc` can be named too.

``` { .text title="The ReaderAuthRole structure, in ASN.1" data-format="ASN.1" }
ReaderAuthRole ::= SEQUENCE OF ReaderAuthRoleEntry

ReaderAuthRoleEntry ::= SEQUENCE {
    docType       UTF8String,
    dataElements  SEQUENCE OF UTF8String
}
```

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-04-105 }**REQ-TS-5-04-105** `ReaderAuthRole` MUST be the extension whose object identifier is `1.3.6.1.4.1.32473.1.1`.
- [](){ #req-ts-5-04-119 }**REQ-TS-5-04-119** The `extnValue` of `ReaderAuthRole` MUST be the DER of the `ReaderAuthRole` structure above.
- [](){ #req-ts-5-04-106 }**REQ-TS-5-04-106** `ReaderAuthRole` MUST hold at least one entry.
- [](){ #req-ts-5-04-120 }**REQ-TS-5-04-120** Each entry of `ReaderAuthRole` MUST hold at least one data element.
- [](){ #req-ts-5-04-121 }**REQ-TS-5-04-121** Verifier Core MUST NOT write the same document type in more than one entry of `ReaderAuthRole`.
- [](){ #req-ts-5-04-128 }**REQ-TS-5-04-128** A reader MUST read each data element of an entry in the namespace the Credential Rulebook of the entry's document type fixes, as [REQ-CR-061][req-cr-061] and [REQ-CR-080][req-cr-080] set out, and as the attribute name that Rulebook gives it where it names no mdoc representation.
- [](){ #req-ts-5-04-107 }**REQ-TS-5-04-107** A reader MUST treat a certificate whose `ReaderAuthRole` does not parse as the structure above as a certificate carrying no permission at all.

</div>

The identifier in force is the one [REQ-TS-5-04-105][req-ts-5-04-105]
names. Its arc is the enterprise number [RFC 5612][ref-rfc5612] reserves
for documentation, `1.3.6.1.4.1.32473`, which carries no claim on any
registry and commits the ecosystem to no application for an arc of its own. Whether the
ecosystem later takes an arc of its own, and when, is a matter for the
Root Authority and not for this specification. What this specification
fixes is the identifier an implementation writes today and the way the
identifier is moved, which is the clause below.

### Moving the ReaderAuthRole identifier {#ts-5-04-moving-the-readerauthrole-identifier}

A change of the object identifier is a change an implementation conformant
to the previous version may fail, so it is a major version of this
specification under [Common provisions](common-provisions.md), published
with the transition period that version names. A reader accepts both
identifiers during the transition and only the new one after it, which is
why a certificate issued today goes on being read until it expires and
nothing has to be reissued early.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-04-108 }**REQ-TS-5-04-108** Verifier Core MUST write `ReaderAuthRole` under the object identifier named by the version of this specification it conforms to, and under no other.
- [](){ #req-ts-5-04-109 }**REQ-TS-5-04-109** Verifier Core MUST NOT issue a certificate carrying `ReaderAuthRole` under more than one object identifier.
- [](){ #req-ts-5-04-110 }**REQ-TS-5-04-110** During the transition period of a major version that replaces the object identifier, a reader MUST accept `ReaderAuthRole` under either the superseded identifier or the new one.
- [](){ #req-ts-5-04-122 }**REQ-TS-5-04-122** During that transition period, a reader MUST apply the bound `ReaderAuthRole` carries the same way under the superseded identifier and under the new one.
- [](){ #req-ts-5-04-111 }**REQ-TS-5-04-111** After that transition period, a reader MUST treat a certificate carrying `ReaderAuthRole` only under the superseded identifier as a certificate carrying no permission at all.
- [](){ #req-ts-5-04-112 }**REQ-TS-5-04-112** A reader MUST treat a certificate carrying `ReaderAuthRole` under two or more object identifiers as a certificate carrying no permission at all.

</div>

A reader therefore holds the identifiers it accepts as a set it can be
configured with, rather than as one constant compiled into it, because
during a transition the set has two members. The failure mode on both
sides is the same as [REQ-TS-5-04-107][req-ts-5-04-107]: a bound that
cannot be read is no permission, never a permission that is assumed.

## Revocation {#ts-5-04-revocation}

Two certificate revocation lists, each published by the authority that
issued the certificates on it. Trust Authority publishes one list per root,
covering every Document Signer Certificate, status list signer certificate,
VICAL signer certificate, and Verifier Issuing CA certificate it issued; each holder of a Verifier Issuing
CA publishes its own, covering the device certificates it issued. Trust
Authority issues no device certificate and lists none.

[](){ #tbl-ts-5-04-crl-profile }

<figure markdown="1" class="ekdn-table">

| Field | Presence | Value |
|---|---|---|
| Version | Mandatory | v2 |
| Issuer name | Mandatory | The same binary value as the subject of the certificate authority that signs the list |
| This update | Mandatory | The issue date of this list |
| Next update | Mandatory | The date by which the next list will be issued |
| Revoked certificates | Conditional | Absent when nothing is revoked; otherwise one entry per revoked certificate, carrying its serial number and the revocation date, with no entry extension |
| Authority key identifier | Mandatory, non-critical | The subject key identifier of the signing certificate authority |
| CRL number | Mandatory, non-critical | Sequential, one higher on every list issued |
| Other extensions | Absent | Absent |
| Signature algorithm | Mandatory | ECDSA with SHA-256 |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-04-065 }**REQ-TS-5-04-065** Trust Authority MUST publish one certificate revocation list per root, meeting [the certificate revocation list profile][tbl-ts-5-04-crl-profile] and the profile of [ISO/IEC 18013-5][ref-iso-18013-5] Annex B.
- [](){ #req-ts-5-04-066 }**REQ-TS-5-04-066** Verifier Core MUST publish a certificate revocation list for the device certificates its Verifier Issuing CA issued, meeting the same profile.
- [](){ #req-ts-5-04-067 }**REQ-TS-5-04-067** A certificate revocation list MUST be complete, listing every unexpired certificate the authority has revoked for any reason.
- [](){ #req-ts-5-04-068 }**REQ-TS-5-04-068** An authority MUST NOT publish an indirect or a delta certificate revocation list.
- [](){ #req-ts-5-04-069 }**REQ-TS-5-04-069** An authority MUST issue a new certificate revocation list within the `crl_publication` interval the Governance Profile sets, whether or not anything was revoked.
- [](){ #req-ts-5-04-166 }**REQ-TS-5-04-166** An authority MUST NOT set the `nextUpdate` of a certificate revocation list later than its `thisUpdate` plus the `crl_publication` interval.
- [](){ #req-ts-5-04-070 }**REQ-TS-5-04-070** An authority MUST issue a new certificate revocation list naming a revoked certificate within 48 hours of the revocation.
- [](){ #req-ts-5-04-071 }**REQ-TS-5-04-071** An authority MUST sign a certificate revocation list with the key of the certificate authority that issued the certificates on it.
- [](){ #req-ts-5-04-072 }**REQ-TS-5-04-072** Trust Registry MUST serve each of Trust Authority's certificate revocation lists at the address the certificates name, over HTTP with Transport Layer Security (TLS), as a static file, without authentication and without any identifier of the reader.
- [](){ #req-ts-5-04-073 }**REQ-TS-5-04-073** The holder of a Verifier Issuing CA MUST serve its certificate revocation list the same way, at the address its device certificates name.
- [](){ #req-ts-5-04-074 }**REQ-TS-5-04-074** Trust Authority MUST place a Document Signer Certificate on the Issuer Root CA list within 24 hours of the key it certifies being revoked.
- [](){ #req-ts-5-04-137 }**REQ-TS-5-04-137** Trust Authority MUST place a status list signer certificate on the Issuer Root CA list within 24 hours of the key it certifies being revoked.
- [](){ #req-ts-5-04-075 }**REQ-TS-5-04-075** An authority MUST NOT remove an entry from its certificate revocation list before the certificate it names has expired.
- [](){ #req-ts-5-04-076 }**REQ-TS-5-04-076** A reader MUST fetch every certificate revocation list it needs on its trust cache sync.
- [](){ #req-ts-5-04-123 }**REQ-TS-5-04-123** A reader MUST NOT fetch a certificate revocation list during a transaction.
- [](){ #req-ts-5-04-158 }**REQ-TS-5-04-158** A reader MAY use a cached certificate revocation list whose `nextUpdate` has passed, up to the tolerance limit the Governance Profile sets.
- [](){ #req-ts-5-04-159 }**REQ-TS-5-04-159** A reader MUST refuse a certificate whose authority's certificate revocation list it does not hold, or holds only as a copy past the tolerance limit.

</div>

The 48 hours are the standard's ceiling. The standard also allows 90 days
between two lists, and the `crl_publication` interval replaces that for every
list in the ecosystem, Trust Authority's included: an mdoc read face to face
by a reader that cannot sync learns of a revoked Document Signer Certificate
from the Issuer Root CA list alone, so that list keeps to [the window the
Governance Framework fixes][gf-constraints-on-the-governance-profile] like
every other. A key revoked on the issuer side is placed on the
list within 24 hours, the limit [ETSI EN 319 411-1 V1.4.1][ref-etsi-en-319411-1] sets, as the second phase of
[entity key revocation][entity-key-revocation] requires. How stale a cached
list may be before a reader stops accepting it is the `crl` tolerance the
Governance Profile sets, one value for every reader, online or not, which
[REQ-TS-5-04-158][req-ts-5-04-158] and [REQ-TS-5-04-159][req-ts-5-04-159]
apply.

## The VICAL {#ts-5-04-the-vical}

The VICAL is the signed list of issuer roots an mdoc reader accepts, under
[ISO/IEC 18013-5][ref-iso-18013-5] Annex C. It carries the ecosystem's own
Issuer Root CA and the issuer root of every ecosystem the Root Authority
recognizes, each with the document types it may be a trust point for. It is
what lets a reader abroad, which never sees the trusted list, accept an mdoc
from an Indonesian issuer, and what lets a reader inside the ecosystem learn
a foreign root without one. Withdrawing a foreign root is a new VICAL
without it.

The list reaches a reader in four steps, each on the trust path.

1. Trust Registry builds the list from the roots the Root Authority
   accredited or recognized, using its List Publisher Component.
2. Trust Authority signs it with the VICAL key, using its Certificate
   Authority Component, and returns the `COSE_Sign1`.
3. Trust Registry serves it from the central content delivery network.
4. Every reader fetches it on its next trust cache sync, never on demand.

[](){ #tbl-ts-5-04-vical-members }

<figure markdown="1" class="ekdn-table">

| Member | Type | Presence | Value |
|---|---|---|---|
| `version` | `tstr` | Present | `1.0` |
| `vicalProvider` | `tstr` | Present | The formal legal name of the body that holds the Root Authority role |
| `date` | `tdate` | Present | The time the list was issued |
| `vicalIssueID` | `uint` | Present | `1` for the first list ever published, then one more for every list after it |
| `nextUpdate` | `tdate` | Present | The time by which the next list will be issued |
| `certificateInfos` | array | Present | One entry per root the list carries |
| `extensions` | map | Absent | Absent |
| `certificate` | `bstr` | Present | The DER of the root certificate |
| `serialNumber` | `biguint` | Present | The serial number of that certificate |
| `ski` | `bstr` | Present | The subject key identifier of that certificate |
| `docType` | array of `tstr` | Present | Every document type the root may be a trust point for |
| `certificateProfile` | array of `tstr` | Present | `1.0.18013.5.1.7`, the mDL IACA object identifier |
| `issuingAuthority` | `tstr` | Present | The name of the authority behind the root |
| `issuingCountry` | `tstr` | Present | The ISO 3166-1 code of that authority |
| `stateOrProvinceName` | `tstr` | Absent | Absent: no root is limited to a province |
| `issuer`, `subject` | `bstr` | Present | The DER of the issuer and subject names of that certificate |
| `notBefore`, `notAfter` | `tdate` | Present | The validity period of that certificate |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-04-077 }**REQ-TS-5-04-077** Trust Registry MUST publish the VICAL as the VICAL structure of [ISO/IEC 18013-5][ref-iso-18013-5] Annex C, with every member as [the table of VICAL members][tbl-ts-5-04-vical-members] gives it.
- [](){ #req-ts-5-04-078 }**REQ-TS-5-04-078** The VICAL MUST carry one `CertificateInfo` for the Issuer Root CA.
- [](){ #req-ts-5-04-079 }**REQ-TS-5-04-079** The VICAL MUST carry one `CertificateInfo` for the issuer root of every ecosystem the Root Authority recognizes, and for no other root.
- [](){ #req-ts-5-04-080 }**REQ-TS-5-04-080** Trust Registry MUST set `docType` of an entry to every document type whose credentials that root's issuers sign.
- [](){ #req-ts-5-04-124 }**REQ-TS-5-04-124** Trust Registry MUST NOT leave the `docType` of an entry empty.
- [](){ #req-ts-5-04-081 }**REQ-TS-5-04-081** Trust Registry MUST increase `vicalIssueID` by exactly one on every list it publishes.
- [](){ #req-ts-5-04-125 }**REQ-TS-5-04-125** Trust Registry MUST NOT publish a VICAL whose `vicalIssueID` is lower than or equal to that of a list already published.
- [](){ #req-ts-5-04-082 }**REQ-TS-5-04-082** Trust Registry MUST publish a new VICAL before the `nextUpdate` of the current one.
- [](){ #req-ts-5-04-167 }**REQ-TS-5-04-167** Trust Registry MUST NOT set the `nextUpdate` of a VICAL later than its `date` plus the `vical_publication` interval the Governance Profile sets.
- [](){ #req-ts-5-04-083 }**REQ-TS-5-04-083** Trust Registry MUST publish a new VICAL within one hour of Trust Authority ordering the withdrawal of a root it carries.
- [](){ #req-ts-5-04-084 }**REQ-TS-5-04-084** The VICAL MUST be encapsulated in an untagged `COSE_Sign1` structure whose payload is the VICAL, with a zero-length `external_aad`.
- [](){ #req-ts-5-04-085 }**REQ-TS-5-04-085** The protected header of that structure MUST carry the `alg` element, set to `ES256`.
- [](){ #req-ts-5-04-126 }**REQ-TS-5-04-126** The protected header of that structure MUST NOT carry any element other than `alg`.
- [](){ #req-ts-5-04-086 }**REQ-TS-5-04-086** The unprotected header MUST carry the VICAL signer certificate in `x5chain`.
- [](){ #req-ts-5-04-087 }**REQ-TS-5-04-087** Trust Authority MUST sign the VICAL with the VICAL key held in its HSM.
- [](){ #req-ts-5-04-127 }**REQ-TS-5-04-127** Trust Registry MUST NOT hold the VICAL key.
- [](){ #req-ts-5-04-088 }**REQ-TS-5-04-088** Trust Authority MUST issue the VICAL signer certificate from the Issuer Root CA, from a certificate signing request over the VICAL key, meeting the VICAL signer certificate profile of [ISO/IEC 18013-5][ref-iso-18013-5] Annex C: extended key usage `1.0.18013.5.1.8`, key usage `nonRepudiation` only, and at most 1187 days.
- [](){ #req-ts-5-04-089 }**REQ-TS-5-04-089** Trust Authority MUST NOT sign the VICAL with the key that signs the trusted list.
- [](){ #req-ts-5-04-090 }**REQ-TS-5-04-090** Trust Registry MUST serve the current VICAL at `GET /vical`, over HTTP with TLS, as a static file, without authentication and without any identifier of the reader.
- [](){ #req-ts-5-04-091 }**REQ-TS-5-04-091** Trust Registry MUST keep every VICAL it published.
- [](){ #req-ts-5-04-092 }**REQ-TS-5-04-092** Trust Registry MUST serve the same bytes from every address at which it serves the VICAL.

</div>

The VICAL is signed with a key of its own because its readers are not the
trusted list's: it is read by mdoc readers abroad, in a format they already
parse, and a leak on one list does not reach the other, as
[Trust Authority's own keys][trust-authoritys-own-keys] sets out. The signer
certificate chains to the Issuer Root CA because every certificate in the
ecosystem but the two roots is issued from a certificate signing request,
and the VICAL belongs to the issuer side. What a reader abroad is handed so
that it can check that chain is part of the terms of recognition, which the
Governance Framework governs, and those terms say it in [what IDCTF hands over][gf-what-idctf-hands-over].

## Validating a chain {#ts-5-04-validating-a-chain}

A reader works from cache in both directions. Mobile Verifier validates the
issuer chain of an mdoc it reads; Mobile Wallet validates the reader chain
of a request it answers. Neither makes a network call inside a transaction,
because the roots came at build time and the VICAL and the certificate
revocation lists came on the sync.

Mobile Verifier, on the issuer side, in five steps.

1. It takes the Document Signer Certificate from `x5chain` in IssuerAuth.
2. It validates the chain from that certificate to the Issuer Root CA it
   carries from build time, with a path length of zero, or to a root its
   cached VICAL carries for this document type.
3. It checks the validity period of every certificate in the chain.
4. It checks the certificate against its cached copy of the Issuer Root CA
   certificate revocation list.
5. It checks that the extended key usage of the leaf is
   `1.0.18013.5.1.2` before using the key.

Mobile Wallet, on the reader side, in five steps.

1. It takes the Verifier Device Certificate from ReaderAuth, or from `x5c`
   in an online request from a merchant.
2. It validates the chain from that certificate, through the Verifier
   Issuing CA, to the Verifier Root CA it carries from build time.
3. It confirms from its cached trusted list that the Verifier Issuing CA is
   named at status granted in the entry of an entity whose role service is
   granted.
4. It checks the device certificate against its cached copy of that
   authority's certificate revocation list.
5. It refuses every document type and data element outside the
   `ReaderAuthRole` of the certificate.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-04-093 }**REQ-TS-5-04-093** Mobile Verifier MUST validate the chain of a Document Signer Certificate to the Issuer Root CA it carries from build time, or to a root its cached VICAL carries.
- [](){ #req-ts-5-04-094 }**REQ-TS-5-04-094** Mobile Verifier MUST NOT accept a Document Signer Certificate carried in a credential as a trust anchor, however it chains.
- [](){ #req-ts-5-04-095 }**REQ-TS-5-04-095** Mobile Verifier MUST NOT hold an issuer's Document Signer Certificate in its own configuration as a trust anchor.
- [](){ #req-ts-5-04-096 }**REQ-TS-5-04-096** Mobile Verifier MUST verify the `COSE_Sign1` of its cached VICAL against the VICAL signer certificate in `x5chain`, chained to the Issuer Root CA it carries from build time.
- [](){ #req-ts-5-04-097 }**REQ-TS-5-04-097** Mobile Verifier MUST accept a root from the VICAL only for a document type that root's `docType` names.
- [](){ #req-ts-5-04-098 }**REQ-TS-5-04-098** Mobile Verifier MUST reject a VICAL whose `vicalIssueID` is lower than that of the copy it holds.
- [](){ #req-ts-5-04-099 }**REQ-TS-5-04-099** Mobile Wallet MUST validate the chain of a Verifier Device Certificate through the Verifier Issuing CA to the Verifier Root CA it carries from build time.
- [](){ #req-ts-5-04-100 }**REQ-TS-5-04-100** Mobile Wallet MUST refuse a reader whose Verifier Issuing CA its cached trusted list does not name at status granted.
- [](){ #req-ts-5-04-101 }**REQ-TS-5-04-101** Mobile Wallet MUST refuse every document type and every data element a request asks for outside the `ReaderAuthRole` of the certificate that signed it.
- [](){ #req-ts-5-04-102 }**REQ-TS-5-04-102** A reader MUST refuse a certificate that is outside its validity period, that its cached certificate revocation list names, or whose extended key usage is not the one its position in the chain requires.
- [](){ #req-ts-5-04-103 }**REQ-TS-5-04-103** A reader MUST refuse a chain longer than the `pathLenConstraint` of the root it validates against allows.
- [](){ #req-ts-5-04-104 }**REQ-TS-5-04-104** A reader MUST NOT take a downloaded root certificate as a trust anchor, except a root its cached VICAL carries once that VICAL has verified under [REQ-TS-5-04-096][req-ts-5-04-096].
- [](){ #req-ts-5-04-160 }**REQ-TS-5-04-160** A reader MAY use a cached VICAL whose `nextUpdate` has passed, up to the tolerance limit the Governance Profile sets.
- [](){ #req-ts-5-04-161 }**REQ-TS-5-04-161** A reader MUST NOT take a root from a cached VICAL past that tolerance limit as a trust anchor, except the Issuer Root CA it carries from build time.

</div>

Holding an issuer's Document Signer Certificate as a trust anchor looks like
a tightening and is the opposite: every renewal would then oblige every
verifier to be updated, which is the thing a root exists to avoid. What a
reader may cache for speed is the result of a validation, keyed by the
fingerprint of the certificate.

## Security considerations {#ts-5-04-security-considerations}

Each threat below is answered by the requirement named with it.

- **A forged credential under a self-made certificate.** A reader validates
  every chain to a root it carries from build time or to one a verified
  VICAL carries, [REQ-TS-5-04-093][req-ts-5-04-093], and never treats the certificate
  inside a credential as an anchor, [REQ-TS-5-04-094][req-ts-5-04-094].
- **A leaked root key used on the other side.** The roots sit in two offline
  HSMs, [REQ-TS-5-04-021][req-ts-5-04-021], neither signs the other,
  [REQ-TS-5-04-023][req-ts-5-04-023], and each signs only the certificates
  of its own side, [REQ-TS-5-04-024][req-ts-5-04-024] and
  [REQ-TS-5-04-025][req-ts-5-04-025].
- **A stolen Verifier Issuing CA key minting readers.** The key may not live
  in the software keystore, [REQ-TS-5-04-116][req-ts-5-04-116], the
  authority is struck in the trusted list and its certificate placed on the
  root list, [REQ-TS-5-04-052][req-ts-5-04-052], and a wallet checks both,
  [REQ-TS-5-04-100][req-ts-5-04-100].
- **A reader asking for more than it was approved for.** The bound is in the
  certificate, [REQ-TS-5-04-056][req-ts-5-04-056] and
  [REQ-TS-5-04-057][req-ts-5-04-057], and the wallet refuses the difference
  before the citizen is asked, [REQ-TS-5-04-101][req-ts-5-04-101].
- **A certificate used past its withdrawal.** Each authority publishes a
  complete list within 48 hours of a revocation,
  [REQ-TS-5-04-067][req-ts-5-04-067] and
  [REQ-TS-5-04-070][req-ts-5-04-070], and a reader checks its cached copy on
  every read, [REQ-TS-5-04-102][req-ts-5-04-102].
- **A rolled-back VICAL.** A reader refuses a list older than the copy it
  holds, [REQ-TS-5-04-098][req-ts-5-04-098], and a published list is never
  withdrawn, only replaced, [REQ-TS-5-04-082][req-ts-5-04-082].
- **A root accepted for a credential it was never meant to sign.** A root
  from the VICAL counts only for the document types its entry names,
  [REQ-TS-5-04-080][req-ts-5-04-080] and
  [REQ-TS-5-04-097][req-ts-5-04-097].
- **A certificate whose key was never held by the party it names.** Every
  certificate is issued from a request signed with the key itself,
  [REQ-TS-5-04-032][req-ts-5-04-032] and
  [REQ-TS-5-04-033][req-ts-5-04-033], and Trust Authority holds no private
  key, [REQ-TS-5-04-018][req-ts-5-04-018].

- **A status list signed for another issuer.** One root certifies every
  issuer, so a chain to it does not say whose list it is. The status list
  signer certificate repeats the `organizationName` of the issuer's Document
  Signer Certificate, [REQ-TS-5-04-133][req-ts-5-04-133], and a reader
  compares the two, as
  [Publishing and reading a status list](publishing-and-reading-a-status-list.md)
  requires.

A reader that verifies through the VICAL alone and holds no Trust SDK checks
the status of an mdoc through the status list signer certificate in the CWT
form, under the same root as the mdoc,
[REQ-TS-5-04-129][req-ts-5-04-129] and
[REQ-TS-5-04-132][req-ts-5-04-132].

## Privacy considerations {#ts-5-04-privacy-considerations}

A certificate carries no citizen and no device holder beyond the name of the
party that operates the device, and a holder has no certificate at all,
which is one reason the architecture gives for keeping the holder's key out
of one: a certificate would carry a subject that correlates across verifiers.

Both lists are fetched in bulk, outside any transaction, and served without
authentication and without any identifier of the reader,
[REQ-TS-5-04-072][req-ts-5-04-072] and
[REQ-TS-5-04-090][req-ts-5-04-090], so neither Trust Registry nor the holder
of a Verifier Issuing CA learns which citizen dealt with which counterpart.
A reader fetches a certificate revocation list on the sync and never during
a transaction, [REQ-TS-5-04-076][req-ts-5-04-076] and
[REQ-TS-5-04-123][req-ts-5-04-123], for the same reason: a check made at the
moment of use would tell the publisher that the check was being made.

A merchant's certificate is the same artifact in both channels, so the name
of the merchant reaches the wallet the same way online and in proximity, and
nothing more about the device travels with it: the device key is identified
to the party that vouches for it by a thumbprint, as
[the device identifier][ts-5-03-the-device-identifier] sets out.

## Changelog {#ts-5-04-changelog}

<figure markdown="1" class="ekdn-table">

| Version | Date | Change |
|---|---|---|
| 1.0 draft | 19 October 2026 | First draft |

</figure>
