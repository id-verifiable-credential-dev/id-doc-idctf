---
title: "[TS-5-06] Registering and carrying a Use Statement"
description: The Use Statement Trust Authority issues for one registered use, what it names, the signature on it, how a verifier carries it online and in proximity, and the checks a wallet runs before it shows the consent screen.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, Kep. 30, §3.3, §5.5, §7.2; Rincian Module dan Operasi §2.4, §4; JWT di OpenID4VCI dan OpenID4VP §3, §5 -->

<p class="ekdn-docid">TS-5-06</p>

# Registering and carrying a Use Statement {#ts-5-06-registering-and-carrying-a-use-statement}

<p class="ekdn-lead" markdown="span">
A Use Statement is one registered use of one Relying Party, signed by Trust
Authority. Nobody fetches it: the verifier carries it inside its own request,
and the wallet reads the approved purpose from it before it asks the citizen
for anything.
</p>

Every sentence on this page binds Trust Authority, the Modules that carry a
Use Statement, and Mobile Wallet, which reads one, and an Assessment Body
tests them against it in the version the Governance Profile puts in force.
The key words and the identifier `REQ-TS-5-06-nnn` follow
[Common provisions](common-provisions.md).

## Who runs this and what it needs {#ts-5-06-who-runs-this-and-what-it-needs}

This specification fixes the Use Statement: the claims it carries, the
attributes a use may reach, the signature Trust Authority puts on it, how
long it lives and how it is revoked, how a verifier carries it in an online
request and in a proximity request, and what Mobile Wallet checks before it
acts on one.

Its conformance targets are Trust Authority, which records each use and
signs the statement; Trust Registry, which publishes the status that revokes
one; Verifier Core, which carries a statement in the requests it builds and
hands the category statements to a device it onboards; Verifier Console,
which validates each request template against the use it names; Mobile
Verifier, which carries a statement in proximity; and Mobile Wallet, which
reads one. The requirements that name an RP Intermediary bind it as it
registers one use per business category, and no conformance target is tested
against them, because an RP Intermediary is a participant and not a Module.
A reader meets its requirements through Trust SDK where the library performs
the check.

It leaves to other documents: who may register a use and on what grounds,
[the approval tiers][gf-approval-tiers] behind one, and [the sanctions behind a withdrawal][gf-ladder-of-sanctions], which
the Governance Framework holds; the validity period of a statement, the
signature algorithms allowed, the tolerance limit, and the cut-off after
which a request carrying no statement is refused, which the Governance
Profile holds; the submission and collection interface an entity uses, which
[Onboarding an entity and registering its keys](onboarding-an-entity-and-registering-its-keys.md) holds; the
format, the signature and the publication of the status list a statement
points into, which [Publishing and reading a status list](publishing-and-reading-a-status-list.md)
holds; the permission that is the ceiling over a use, which
[Answering with an Authority Statement](answering-with-an-authority-statement.md)
holds; the keys of Trust Authority and the log they live in, which
[Publishing and resolving a did:webvh identifier](publishing-and-resolving-a-did-webvh-identifier.md)
holds; the Verifier Device Certificate and its `ReaderAuthRole`, which
[Issuing and validating the X.509 certificates and the VICAL](issuing-and-validating-the-x509-certificates-and-the-vical.md)
holds; and the rest of the request the statement travels in, which the
presentation specifications hold.

Before the first exchange, each target holds what the rules below assume:

- **Trust Authority** holds the Root Authority's decision on each registered
  use with its history, holds the Use Statement key in its hardware security
  module (HSM), and publishes the matching public key in its own
  Decentralized Identifier (DID) Document.
- **Trust Registry** publishes the Use Statement status list and holds the
  index each statement was allocated.
- **A verifier** holds the statement of every use it runs, collected from
  Trust Authority, and, for a device it onboards, the statements of the
  business categories that device is bound to.
- **Mobile Wallet** carries Trust Authority's self-certifying identifier
  (SCID) from build time, resolves Trust Authority's DID Document from it,
  and holds a copy of the Use Statement status list and of the trusted list.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-06-001 }**REQ-TS-5-06-001** Trust Authority MUST meet every requirement on this page that names Trust Authority, and every requirement on what Trust Authority writes: the Use Statement, with its protected header, its claims and its signature.
- [](){ #req-ts-5-06-002 }**REQ-TS-5-06-002** Trust Registry MUST meet every requirement on this page that names Trust Registry, and every requirement on what Trust Registry writes: the Use Statement status list.
- [](){ #req-ts-5-06-003 }**REQ-TS-5-06-003** Verifier Core MUST meet every requirement on this page that names Verifier Core, and every requirement on what Verifier Core writes: the `verifier_info` entry that carries a Use Statement, with its `format` and `data` members.
- [](){ #req-ts-5-06-004 }**REQ-TS-5-06-004** Mobile Verifier MUST meet every requirement on this page that names Mobile Verifier, and every requirement on what Mobile Verifier writes: the `requestInfo` entry that carries a Use Statement in each `ItemsRequest` of its `DeviceRequest`.
- [](){ #req-ts-5-06-005 }**REQ-TS-5-06-005** Verifier Console MUST meet every requirement on this page that names Verifier Console.
- [](){ #req-ts-5-06-006 }**REQ-TS-5-06-006** Mobile Wallet MUST meet every requirement on this page that names Mobile Wallet.
- [](){ #req-ts-5-06-116 }**REQ-TS-5-06-116** An RP Intermediary MUST meet every requirement on this page that names an RP Intermediary.

</div>

## What a registered use is {#ts-5-06-what-a-registered-use-is}

An Authority Statement says what attributes an entity may ask for. It says
nothing about what the entity may ask for them for, so a Relying Party
holding a wide permission could put any purpose it liked on the consent
screen. A Use Statement closes that gap: one use, one purpose, one legal
basis, and the attributes that use may reach, as
[Registered use][registered-use] sets out. An entity holds one ceiling and
as many registered uses as it runs, and every use is a subset of the
ceiling.

The statement travels with the verifier rather than with the citizen or the
registry. Trust Authority signs it once, the verifier collects it and
attaches it to each request it sends, and Mobile Wallet checks it from its
own cache. Nothing about the transaction reaches Trust Authority, which is
the reason for carrying it rather than resolving it, as
[Use Statement][use-statement] explains.

A merchant registers no use of its own. It works under a business category
its RP Intermediary registered, handed to the device at provisioning, which
is the same shape as every other authority a merchant borrows.

## Use Statements as issued {#ts-5-06-use-statements-as-issued}

Five statements of one entity: a business category a merchant device reads
under, bounded to one attribute of the KTP Digital and one of a mobile
driving license, because the same age check serves a resident and a visitor;
a use the entity runs itself, bounded to two
attributes of the KTP Digital; a second use it runs itself, bounded to three
attributes of the Kartu ASN, which the online request in
[Carrying it online][ts-5-06-carrying-it-online] carries; a third,
bounded to every attribute of the Kartu Nikah, which the second request there
carries; and a second business category, bounded to two attributes of the
Kartu ASN, which a merchant's online request in
[the Kartu ASN, from a merchant][ts-3-01-the-kartu-asn-from-a-merchant]
carries. A use of a type issued only in
`ldp_vc` names every attribute, because an `ldp_vc` presentation discloses the
whole credential and cannot withhold one. A use may reach more than one
credential type, as the business category does, and `claims` names each
attribute under the type it belongs to.

The statements are an illustration: the entity, its domain, the uses and the
keys are invented, and no registration has been approved. Every field is
exact. All five were signed with the Use Statement key of the Trust Authority
DID in `iss`, and every signature verifies, so an implementation can parse
them and find what the clauses below require. The entity is the Relying
Party [the trusted list][ts-5-01-trusted-list-payload]
carries, with the same DID, and the attributes the category reaches are the
ones the Verifier Device Certificate of
[Issuing and validating the X.509 certificates and the VICAL](issuing-and-validating-the-x509-certificates-and-the-vical.md)
bounds its device to.

``` { .json title="The Use Statement of a business category, decoded" data-format="JSON" }
{
  "typ": "vnd.id.idctf.use-statement+jwt",
  "alg": "ES256",
  "kid": "did:webvh:QmZjy1t9oFiaFjhX2e38uMuR7mgtdLjHPMGfjEfvrsmaiq:trust.go.id#use-statement-1"
}
.
{
  "iss": "did:webvh:QmZjy1t9oFiaFjhX2e38uMuR7mgtdLjHPMGfjEfvrsmaiq:trust.go.id",
  "sub": "did:webvh:QmUATC5jyf5yVy72GYAp8nSvuwshzDy6wYX7WmNY5UJtXT:terminal-nusantara.co.id",
  "use_id": "kategori-tembakau",
  "purpose": {
    "id": "Verifikasi usia pembeli produk tembakau",
    "en": "Age verification for the purchase of tobacco products"
  },
  "legal_basis": "PP 109/2012 Pasal 25 huruf b",
  "claims": [
    "id.idctf.ktp.1#usia_di_atas_17",
    "org.iso.18013.5.1.mDL.1#age_over_18"
  ],
  "status": {
    "status_list": {
      "idx": 812,
      "uri": "https://registry.trust.go.id/status/use-statements-1"
    }
  },
  "iat": 1776470400,
  "exp": 1808006400
}
```

``` { .text title="The same statement, as the verifier carries it" data-format="JWT" }
eyJ0eXAiOiJ2bmQuaWQuaWRjdGYudXNlLXN0YXRlbWVudCtqd3QiLCJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDp3ZWJ2aDpRbVpqeTF0OW9GaWFGamhYMmUzOHVNdVI3bWd0ZExqSFBNR2ZqRWZ2cnNtYWlxOnRydXN0LmdvLmlkI3VzZS1zdGF0ZW1lbnQtMSJ9.eyJpc3MiOiJkaWQ6d2Vidmg6UW1aankxdDlvRmlhRmpoWDJlMzh1TXVSN21ndGRMakhQTUdmakVmdnJzbWFpcTp0cnVzdC5nby5pZCIsInN1YiI6ImRpZDp3ZWJ2aDpRbVVBVEM1anlmNXlWeTcyR1lBcDhuU3Z1d3NoekR5NndZWDdXbU5ZNVVKdFhUOnRlcm1pbmFsLW51c2FudGFyYS5jby5pZCIsInVzZV9pZCI6ImthdGVnb3JpLXRlbWJha2F1IiwicHVycG9zZSI6eyJpZCI6IlZlcmlmaWthc2kgdXNpYSBwZW1iZWxpIHByb2R1ayB0ZW1iYWthdSIsImVuIjoiQWdlIHZlcmlmaWNhdGlvbiBmb3IgdGhlIHB1cmNoYXNlIG9mIHRvYmFjY28gcHJvZHVjdHMifSwibGVnYWxfYmFzaXMiOiJQUCAxMDkvMjAxMiBQYXNhbCAyNSBodXJ1ZiBiIiwiY2xhaW1zIjpbImlkLmlkY3RmLmt0cC4xI3VzaWFfZGlfYXRhc18xNyIsIm9yZy5pc28uMTgwMTMuNS4xLm1ETC4xI2FnZV9vdmVyXzE4Il0sInN0YXR1cyI6eyJzdGF0dXNfbGlzdCI6eyJpZHgiOjgxMiwidXJpIjoiaHR0cHM6Ly9yZWdpc3RyeS50cnVzdC5nby5pZC9zdGF0dXMvdXNlLXN0YXRlbWVudHMtMSJ9fSwiaWF0IjoxNzc2NDcwNDAwLCJleHAiOjE4MDgwMDY0MDB9.Jji2ue0AO4C-NpZbZ8ttzs7DsqWLTZbm2JGAsDw7Utb_ctPZUVZxFXeH-xTm0e7LxrSfq0Mhw24vHfu3yFcDzA
```

``` { .json title="The Use Statement of a use the entity runs itself, decoded" data-format="JSON" }
{
  "typ": "vnd.id.idctf.use-statement+jwt",
  "alg": "ES256",
  "kid": "did:webvh:QmZjy1t9oFiaFjhX2e38uMuR7mgtdLjHPMGfjEfvrsmaiq:trust.go.id#use-statement-1"
}
.
{
  "iss": "did:webvh:QmZjy1t9oFiaFjhX2e38uMuR7mgtdLjHPMGfjEfvrsmaiq:trust.go.id",
  "sub": "did:webvh:QmUATC5jyf5yVy72GYAp8nSvuwshzDy6wYX7WmNY5UJtXT:terminal-nusantara.co.id",
  "use_id": "penukaran-valas",
  "purpose": {
    "id": "Verifikasi identitas penukaran valuta asing",
    "en": "Identity verification for a foreign exchange transaction"
  },
  "legal_basis": "Ketentuan APU PPT sektor jasa keuangan",
  "claims": [
    "id.idctf.ktp.1#nik",
    "id.idctf.ktp.1#nama"
  ],
  "status": {
    "status_list": {
      "idx": 4219,
      "uri": "https://registry.trust.go.id/status/use-statements-1"
    }
  },
  "iat": 1777852800,
  "exp": 1809388800
}
```

``` { .text title="The same statement, as the verifier carries it" data-format="JWT" }
eyJ0eXAiOiJ2bmQuaWQuaWRjdGYudXNlLXN0YXRlbWVudCtqd3QiLCJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDp3ZWJ2aDpRbVpqeTF0OW9GaWFGamhYMmUzOHVNdVI3bWd0ZExqSFBNR2ZqRWZ2cnNtYWlxOnRydXN0LmdvLmlkI3VzZS1zdGF0ZW1lbnQtMSJ9.eyJpc3MiOiJkaWQ6d2Vidmg6UW1aankxdDlvRmlhRmpoWDJlMzh1TXVSN21ndGRMakhQTUdmakVmdnJzbWFpcTp0cnVzdC5nby5pZCIsInN1YiI6ImRpZDp3ZWJ2aDpRbVVBVEM1anlmNXlWeTcyR1lBcDhuU3Z1d3NoekR5NndZWDdXbU5ZNVVKdFhUOnRlcm1pbmFsLW51c2FudGFyYS5jby5pZCIsInVzZV9pZCI6InBlbnVrYXJhbi12YWxhcyIsInB1cnBvc2UiOnsiaWQiOiJWZXJpZmlrYXNpIGlkZW50aXRhcyBwZW51a2FyYW4gdmFsdXRhIGFzaW5nIiwiZW4iOiJJZGVudGl0eSB2ZXJpZmljYXRpb24gZm9yIGEgZm9yZWlnbiBleGNoYW5nZSB0cmFuc2FjdGlvbiJ9LCJsZWdhbF9iYXNpcyI6IktldGVudHVhbiBBUFUgUFBUIHNla3RvciBqYXNhIGtldWFuZ2FuIiwiY2xhaW1zIjpbImlkLmlkY3RmLmt0cC4xI25payIsImlkLmlkY3RmLmt0cC4xI25hbWEiXSwic3RhdHVzIjp7InN0YXR1c19saXN0Ijp7ImlkeCI6NDIxOSwidXJpIjoiaHR0cHM6Ly9yZWdpc3RyeS50cnVzdC5nby5pZC9zdGF0dXMvdXNlLXN0YXRlbWVudHMtMSJ9fSwiaWF0IjoxNzc3ODUyODAwLCJleHAiOjE4MDkzODg4MDB9.D6HoVJbxgZYKOYKqRV9k9_Q_YIPIdDS_EmvInP0GZGJWI5AbJclHeUlt178zbrcikBWZAzQUoOv0hjzkvpJrKQ
```

``` { .json title="The Use Statement of a use the entity runs online, decoded" data-format="JSON" }
{
  "typ": "vnd.id.idctf.use-statement+jwt",
  "alg": "ES256",
  "kid": "did:webvh:QmZjy1t9oFiaFjhX2e38uMuR7mgtdLjHPMGfjEfvrsmaiq:trust.go.id#use-statement-1"
}
.
{
  "iss": "did:webvh:QmZjy1t9oFiaFjhX2e38uMuR7mgtdLjHPMGfjEfvrsmaiq:trust.go.id",
  "sub": "did:webvh:QmUATC5jyf5yVy72GYAp8nSvuwshzDy6wYX7WmNY5UJtXT:terminal-nusantara.co.id",
  "use_id": "tarif-dinas-asn",
  "purpose": {
    "id": "Verifikasi status ASN untuk tarif perjalanan dinas",
    "en": "Civil servant status check for the official travel fare"
  },
  "legal_basis": "Perjanjian kerja sama tarif perjalanan dinas dengan instansi pemerintah",
  "claims": [
    "id.idctf.kartu-asn.1#nama",
    "id.idctf.kartu-asn.1#nip",
    "id.idctf.kartu-asn.1#instansi"
  ],
  "status": {
    "status_list": {
      "idx": 6350,
      "uri": "https://registry.trust.go.id/status/use-statements-1"
    }
  },
  "iat": 1780272000,
  "exp": 1811808000
}
```

``` { .text title="The same statement, as the verifier carries it" data-format="JWT" }
eyJ0eXAiOiJ2bmQuaWQuaWRjdGYudXNlLXN0YXRlbWVudCtqd3QiLCJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDp3ZWJ2aDpRbVpqeTF0OW9GaWFGamhYMmUzOHVNdVI3bWd0ZExqSFBNR2ZqRWZ2cnNtYWlxOnRydXN0LmdvLmlkI3VzZS1zdGF0ZW1lbnQtMSJ9.eyJpc3MiOiJkaWQ6d2Vidmg6UW1aankxdDlvRmlhRmpoWDJlMzh1TXVSN21ndGRMakhQTUdmakVmdnJzbWFpcTp0cnVzdC5nby5pZCIsInN1YiI6ImRpZDp3ZWJ2aDpRbVVBVEM1anlmNXlWeTcyR1lBcDhuU3Z1d3NoekR5NndZWDdXbU5ZNVVKdFhUOnRlcm1pbmFsLW51c2FudGFyYS5jby5pZCIsInVzZV9pZCI6InRhcmlmLWRpbmFzLWFzbiIsInB1cnBvc2UiOnsiaWQiOiJWZXJpZmlrYXNpIHN0YXR1cyBBU04gdW50dWsgdGFyaWYgcGVyamFsYW5hbiBkaW5hcyIsImVuIjoiQ2l2aWwgc2VydmFudCBzdGF0dXMgY2hlY2sgZm9yIHRoZSBvZmZpY2lhbCB0cmF2ZWwgZmFyZSJ9LCJsZWdhbF9iYXNpcyI6IlBlcmphbmppYW4ga2VyamEgc2FtYSB0YXJpZiBwZXJqYWxhbmFuIGRpbmFzIGRlbmdhbiBpbnN0YW5zaSBwZW1lcmludGFoIiwiY2xhaW1zIjpbImlkLmlkY3RmLmthcnR1LWFzbi4xI25hbWEiLCJpZC5pZGN0Zi5rYXJ0dS1hc24uMSNuaXAiLCJpZC5pZGN0Zi5rYXJ0dS1hc24uMSNpbnN0YW5zaSJdLCJzdGF0dXMiOnsic3RhdHVzX2xpc3QiOnsiaWR4Ijo2MzUwLCJ1cmkiOiJodHRwczovL3JlZ2lzdHJ5LnRydXN0LmdvLmlkL3N0YXR1cy91c2Utc3RhdGVtZW50cy0xIn19LCJpYXQiOjE3ODAyNzIwMDAsImV4cCI6MTgxMTgwODAwMH0.RCnnWXP8-pHc4PrAh3qtc-sSxFXDc1mn-YepQ1EZ6FNsO2G7BI2yTkbCKNHokrwfJ78k3ikcQ8SPphaDvWAacg
```

``` { .json title="The Use Statement of a use of every Kartu Nikah attribute, decoded" data-format="JSON" }
{
  "typ": "vnd.id.idctf.use-statement+jwt",
  "alg": "ES256",
  "kid": "did:webvh:QmZjy1t9oFiaFjhX2e38uMuR7mgtdLjHPMGfjEfvrsmaiq:trust.go.id#use-statement-1"
}
.
{
  "iss": "did:webvh:QmZjy1t9oFiaFjhX2e38uMuR7mgtdLjHPMGfjEfvrsmaiq:trust.go.id",
  "sub": "did:webvh:QmUATC5jyf5yVy72GYAp8nSvuwshzDy6wYX7WmNY5UJtXT:terminal-nusantara.co.id",
  "use_id": "pencatatan-ahli-waris",
  "purpose": {
    "id": "Verifikasi status perkawinan untuk pencatatan ahli waris",
    "en": "Verification of marital status for recording a beneficiary"
  },
  "legal_basis": "Perjanjian layanan dengan pengguna untuk pencatatan ahli waris",
  "claims": [
    "id.idctf.kartu-nikah.1#nama_suami",
    "id.idctf.kartu-nikah.1#nama_istri",
    "id.idctf.kartu-nikah.1#tanggal_akad",
    "id.idctf.kartu-nikah.1#nomor_akta_nikah",
    "id.idctf.kartu-nikah.1#kua",
    "id.idctf.kartu-nikah.1#kabupaten_kota",
    "id.idctf.kartu-nikah.1#provinsi",
    "id.idctf.kartu-nikah.1#foto_suami",
    "id.idctf.kartu-nikah.1#foto_istri"
  ],
  "status": {
    "status_list": {
      "idx": 7408,
      "uri": "https://registry.trust.go.id/status/use-statements-1"
    }
  },
  "iat": 1782864000,
  "exp": 1814400000
}
```

``` { .text title="The same statement, as the verifier carries it" data-format="JWT" }
eyJ0eXAiOiJ2bmQuaWQuaWRjdGYudXNlLXN0YXRlbWVudCtqd3QiLCJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDp3ZWJ2aDpRbVpqeTF0OW9GaWFGamhYMmUzOHVNdVI3bWd0ZExqSFBNR2ZqRWZ2cnNtYWlxOnRydXN0LmdvLmlkI3VzZS1zdGF0ZW1lbnQtMSJ9.eyJpc3MiOiJkaWQ6d2Vidmg6UW1aankxdDlvRmlhRmpoWDJlMzh1TXVSN21ndGRMakhQTUdmakVmdnJzbWFpcTp0cnVzdC5nby5pZCIsInN1YiI6ImRpZDp3ZWJ2aDpRbVVBVEM1anlmNXlWeTcyR1lBcDhuU3Z1d3NoekR5NndZWDdXbU5ZNVVKdFhUOnRlcm1pbmFsLW51c2FudGFyYS5jby5pZCIsInVzZV9pZCI6InBlbmNhdGF0YW4tYWhsaS13YXJpcyIsInB1cnBvc2UiOnsiaWQiOiJWZXJpZmlrYXNpIHN0YXR1cyBwZXJrYXdpbmFuIHVudHVrIHBlbmNhdGF0YW4gYWhsaSB3YXJpcyIsImVuIjoiVmVyaWZpY2F0aW9uIG9mIG1hcml0YWwgc3RhdHVzIGZvciByZWNvcmRpbmcgYSBiZW5lZmljaWFyeSJ9LCJsZWdhbF9iYXNpcyI6IlBlcmphbmppYW4gbGF5YW5hbiBkZW5nYW4gcGVuZ2d1bmEgdW50dWsgcGVuY2F0YXRhbiBhaGxpIHdhcmlzIiwiY2xhaW1zIjpbImlkLmlkY3RmLmthcnR1LW5pa2FoLjEjbmFtYV9zdWFtaSIsImlkLmlkY3RmLmthcnR1LW5pa2FoLjEjbmFtYV9pc3RyaSIsImlkLmlkY3RmLmthcnR1LW5pa2FoLjEjdGFuZ2dhbF9ha2FkIiwiaWQuaWRjdGYua2FydHUtbmlrYWguMSNub21vcl9ha3RhX25pa2FoIiwiaWQuaWRjdGYua2FydHUtbmlrYWguMSNrdWEiLCJpZC5pZGN0Zi5rYXJ0dS1uaWthaC4xI2thYnVwYXRlbl9rb3RhIiwiaWQuaWRjdGYua2FydHUtbmlrYWguMSNwcm92aW5zaSIsImlkLmlkY3RmLmthcnR1LW5pa2FoLjEjZm90b19zdWFtaSIsImlkLmlkY3RmLmthcnR1LW5pa2FoLjEjZm90b19pc3RyaSJdLCJzdGF0dXMiOnsic3RhdHVzX2xpc3QiOnsiaWR4Ijo3NDA4LCJ1cmkiOiJodHRwczovL3JlZ2lzdHJ5LnRydXN0LmdvLmlkL3N0YXR1cy91c2Utc3RhdGVtZW50cy0xIn19LCJpYXQiOjE3ODI4NjQwMDAsImV4cCI6MTgxNDQwMDAwMH0.3D5_Cry8wIeJypqTBCx_1cQ30xxcwj_83CjahWCXd9eMqj-9ThdHyQCAKNt_fgLPQlzau3fHl28kVCX74t976g
```

``` { .json title="The Use Statement of a second business category, decoded" data-format="JSON" }
{
  "typ": "vnd.id.idctf.use-statement+jwt",
  "alg": "ES256",
  "kid": "did:webvh:QmZjy1t9oFiaFjhX2e38uMuR7mgtdLjHPMGfjEfvrsmaiq:trust.go.id#use-statement-1"
}
.
{
  "iss": "did:webvh:QmZjy1t9oFiaFjhX2e38uMuR7mgtdLjHPMGfjEfvrsmaiq:trust.go.id",
  "sub": "did:webvh:QmUATC5jyf5yVy72GYAp8nSvuwshzDy6wYX7WmNY5UJtXT:terminal-nusantara.co.id",
  "use_id": "kategori-diskon-asn",
  "purpose": {
    "id": "Verifikasi status ASN untuk potongan harga",
    "en": "Civil servant status check for a discount"
  },
  "legal_basis": "Perjanjian kerja sama program potongan harga ASN dengan pedagang mitra",
  "claims": [
    "id.idctf.kartu-asn.1#nama",
    "id.idctf.kartu-asn.1#instansi"
  ],
  "status": {
    "status_list": {
      "idx": 9031,
      "uri": "https://registry.trust.go.id/status/use-statements-1"
    }
  },
  "iat": 1792022400,
  "exp": 1823558400
}
```

``` { .text title="The same statement, as the verifier carries it" data-format="JWT" }
eyJ0eXAiOiJ2bmQuaWQuaWRjdGYudXNlLXN0YXRlbWVudCtqd3QiLCJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDp3ZWJ2aDpRbVpqeTF0OW9GaWFGamhYMmUzOHVNdVI3bWd0ZExqSFBNR2ZqRWZ2cnNtYWlxOnRydXN0LmdvLmlkI3VzZS1zdGF0ZW1lbnQtMSJ9.eyJpc3MiOiJkaWQ6d2Vidmg6UW1aankxdDlvRmlhRmpoWDJlMzh1TXVSN21ndGRMakhQTUdmakVmdnJzbWFpcTp0cnVzdC5nby5pZCIsInN1YiI6ImRpZDp3ZWJ2aDpRbVVBVEM1anlmNXlWeTcyR1lBcDhuU3Z1d3NoekR5NndZWDdXbU5ZNVVKdFhUOnRlcm1pbmFsLW51c2FudGFyYS5jby5pZCIsInVzZV9pZCI6ImthdGVnb3JpLWRpc2tvbi1hc24iLCJwdXJwb3NlIjp7ImlkIjoiVmVyaWZpa2FzaSBzdGF0dXMgQVNOIHVudHVrIHBvdG9uZ2FuIGhhcmdhIiwiZW4iOiJDaXZpbCBzZXJ2YW50IHN0YXR1cyBjaGVjayBmb3IgYSBkaXNjb3VudCJ9LCJsZWdhbF9iYXNpcyI6IlBlcmphbmppYW4ga2VyamEgc2FtYSBwcm9ncmFtIHBvdG9uZ2FuIGhhcmdhIEFTTiBkZW5nYW4gcGVkYWdhbmcgbWl0cmEiLCJjbGFpbXMiOlsiaWQuaWRjdGYua2FydHUtYXNuLjEjbmFtYSIsImlkLmlkY3RmLmthcnR1LWFzbi4xI2luc3RhbnNpIl0sInN0YXR1cyI6eyJzdGF0dXNfbGlzdCI6eyJpZHgiOjkwMzEsInVyaSI6Imh0dHBzOi8vcmVnaXN0cnkudHJ1c3QuZ28uaWQvc3RhdHVzL3VzZS1zdGF0ZW1lbnRzLTEifX0sImlhdCI6MTc5MjAyMjQwMCwiZXhwIjoxODIzNTU4NDAwfQ.iKZdxP5DTz3wqJTryqpldc6oVPc6TcdSWcGVJmz-fuKTIu6JWjLWClkC6ZxF_wEch5LAjpwY-kLwwHjnWQDOew
```

## Format {#ts-5-06-format}

A Use Statement is a JSON Web Token (JWT) as [RFC 7519][ref-rfc7519] defines
one, signed as a JSON Web Signature (JWS) in the compact serialization of
[RFC 7515][ref-rfc7515].
[The table of statement claims][tbl-ts-5-06-statement-claims] gives each
claim of its payload.

[](){ #tbl-ts-5-06-statement-claims }

<figure markdown="1" class="ekdn-table">

| Claim | Type | Presence | Value |
|---|---|---|---|
| `iss` | string | Present | Trust Authority's `did:webvh` |
| `sub` | string | Present | The `did:webvh` of the entity the use is registered to |
| `use_id` | string | Present | The identifier of the use, unique within that entity |
| `purpose` | object | Present | The purpose shown to the citizen, in each language |
| `legal_basis` | string | Present | The ground on which the entity may reach those attributes |
| `claims` | array of strings | Present | The attributes the use may reach |
| `status` | object | Present | Where the status of this statement is published |
| `iat` | number | Present | The time the statement was signed, in seconds since the Unix epoch |
| `exp` | number | Present | The time the statement stops being valid, in seconds since the Unix epoch |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-06-007 }**REQ-TS-5-06-007** A Use Statement MUST be a JWS in the compact serialization of [RFC 7515][ref-rfc7515] whose payload is the JSON claims set of [RFC 7519][ref-rfc7519].
- [](){ #req-ts-5-06-008 }**REQ-TS-5-06-008** The `typ` header parameter MUST be `vnd.id.idctf.use-statement+jwt`.
- [](){ #req-ts-5-06-009 }**REQ-TS-5-06-009** The payload MUST carry every claim [the table of statement claims][tbl-ts-5-06-statement-claims] marks present.
- [](){ #req-ts-5-06-010 }**REQ-TS-5-06-010** `iss` MUST be the `did:webvh` of Trust Authority.
- [](){ #req-ts-5-06-011 }**REQ-TS-5-06-011** `sub` MUST be the `did:webvh` of the entity that registered the use.
- [](){ #req-ts-5-06-092 }**REQ-TS-5-06-092** The entity named in `sub` MUST hold the Relying Party service on the trusted list.
- [](){ #req-ts-5-06-012 }**REQ-TS-5-06-012** `use_id` MUST be unique within the entity named in `sub`.
- [](){ #req-ts-5-06-013 }**REQ-TS-5-06-013** Trust Authority MUST NOT allocate a `use_id` that entity has held before.
- [](){ #req-ts-5-06-014 }**REQ-TS-5-06-014** A Use Statement MUST name one use.
- [](){ #req-ts-5-06-093 }**REQ-TS-5-06-093** Trust Authority MUST issue one Use Statement for each use rather than one statement listing several.
- [](){ #req-ts-5-06-015 }**REQ-TS-5-06-015** Trust Authority MUST NOT carry a citizen's data, a transaction identifier, or the identity of a merchant in a Use Statement.

</div>

The last rule is what keeps the statement small enough to travel in every
request and keeps a merchant out of Trust Authority's records. A merchant is
named by the Subject of its Verifier Device Certificate, never by the
statement it reads under, as
[what the intermediary takes on][what-the-intermediary-takes-on] sets out.

## What a use names {#ts-5-06-what-a-use-names}

Three claims carry the registration itself: what the citizen is told, what
the entity relies on, and what the use may reach.

### The purpose {#ts-5-06-the-purpose}

`purpose` is the sentence Mobile Wallet shows the citizen before consent. It
comes from the statement rather than from the request, so a verifier cannot
word it afresh for each transaction, and it is written in both languages of
the ecosystem, as the trusted list writes every string a person reads.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-06-016 }**REQ-TS-5-06-016** `purpose` MUST be an object carrying the purpose in Indonesian, tagged `id`, and in English, tagged `en`.
- [](){ #req-ts-5-06-017 }**REQ-TS-5-06-017** Each value of `purpose` MUST state what the entity does with the attributes the use reaches.
- [](){ #req-ts-5-06-018 }**REQ-TS-5-06-018** Each value of `purpose` MUST be a single sentence.
- [](){ #req-ts-5-06-094 }**REQ-TS-5-06-094** Each value of `purpose` MUST NOT be the entity's name alone.
- [](){ #req-ts-5-06-019 }**REQ-TS-5-06-019** Trust Authority MUST NOT issue a Use Statement whose `purpose` names a use wider than the attributes in `claims` serve.

</div>

### The legal basis {#ts-5-06-the-legal-basis}

`legal_basis` records what the entity gave as its ground for reaching those
attributes: a law, a regulation of its sector, or the contract it performs
for the citizen. It is what an Assessment Body and the Root Authority read
when a registration is reviewed, and it is not what the consent screen is
built from.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-06-020 }**REQ-TS-5-06-020** `legal_basis` MUST name the law, the sector regulation, or the contractual ground the entity relies on.
- [](){ #req-ts-5-06-021 }**REQ-TS-5-06-021** Mobile Wallet MUST NOT show `legal_basis` in place of `purpose`.

</div>

### The attributes a use may reach {#ts-5-06-the-attributes-a-use-may-reach}

`claims` is the list of attributes, each written as a credential type
followed by `#` and an attribute name, in the form
[Identifier](../architecture-framework/data-model-and-protocols/identifier.md)
fixes. A use that reaches every attribute of a type lists each of them, so
that reading the statement never requires reading a Credential Rulebook as
well, and so that adding an attribute to a type widens no registration that
already exists.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-06-022 }**REQ-TS-5-06-022** `claims` MUST hold at least one entry.
- [](){ #req-ts-5-06-023 }**REQ-TS-5-06-023** Each entry of `claims` MUST be a credential type identifier followed by `#` and the name of one attribute of that type.
- [](){ #req-ts-5-06-024 }**REQ-TS-5-06-024** `claims` MUST NOT carry an entry naming a credential type without an attribute.
- [](){ #req-ts-5-06-025 }**REQ-TS-5-06-025** `claims` MUST NOT carry the same entry twice.
- [](){ #req-ts-5-06-026 }**REQ-TS-5-06-026** Every entry of `claims` MUST be covered by a permission the entity named in `sub` holds, as [Answering with an Authority Statement](answering-with-an-authority-statement.md) records it.
- [](){ #req-ts-5-06-027 }**REQ-TS-5-06-027** Trust Authority MUST NOT issue a Use Statement carrying an attribute the entity's permissions do not cover.
- [](){ #req-ts-5-06-028 }**REQ-TS-5-06-028** A permission over a credential type MUST be read as covering every attribute of that type for the purpose of [REQ-TS-5-06-026][req-ts-5-06-026].

</div>

Two bounds therefore apply to one request, and they are read together: the
permission is the ceiling for the entity, and the statement is the limit for
the use in hand. An attribute inside the ceiling and outside the statement
is refused, as
[three questions, three answers][three-questions-three-answers] sets out.

## Signature {#ts-5-06-signature}

Trust Authority signs each statement with the Use Statement key that
[Trust Authority's own keys][trust-authoritys-own-keys] names, held in its
HSM, where the Certificate Authority Component signs with it. The key is
published in Trust Authority's DID Document under the `use-statement`
purpose, so it rotates the way Trust Authority's other signing keys do, and
a reader finds it by resolving the SCID it carries from build time.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-06-029 }**REQ-TS-5-06-029** The `alg` header parameter MUST be one the Governance Profile allows for a Use Statement.
- [](){ #req-ts-5-06-030 }**REQ-TS-5-06-030** *Withdrawn: [REQ-TS-01-034][req-ts-01-034] covers it.*
- [](){ #req-ts-5-06-031 }**REQ-TS-5-06-031** The `kid` header parameter MUST name a key of the purpose `use-statement`, as [Naming the key][ts-01-naming-the-key] of TS-01 requires.
- [](){ #req-ts-5-06-032 }**REQ-TS-5-06-032** Trust Authority MUST hold the private key in its HSM.
- [](){ #req-ts-5-06-033 }**REQ-TS-5-06-033** Trust Authority MUST publish the public key as a verification method of its own DID Document, under the `use-statement` purpose.
- [](){ #req-ts-5-06-034 }**REQ-TS-5-06-034** Trust Authority MUST NOT sign a Use Statement with the trusted list key, the Verified Issuer Certificate Authority List (VICAL) key, the Authority Statement key, the Use Statement status list key, or any other key that [Trust Authority's own keys][trust-authoritys-own-keys] names.
- [](){ #req-ts-5-06-035 }**REQ-TS-5-06-035** An entity MUST NOT sign a Use Statement.
- [](){ #req-ts-5-06-095 }**REQ-TS-5-06-095** Mobile Wallet MUST refuse a Use Statement signed by any key other than one published by Trust Authority.

</div>

The Use Statement key and the key that signs the list revoking a statement
are deliberately two keys. A list that revokes what a compromised key signed
cannot be signed by that same key, which is why Trust Authority holds a Use
Statement status list key beside this one.

## Lifetime and status {#ts-5-06-lifetime-and-status}

A statement is valid until the `exp` it carries. It is withdrawn before that
by flipping its bit in the Use Statement status list, which Trust Registry
publishes as a Status List Token in the form
[IETF Token Status List draft -14][ref-i-d-ietf-oauth-status-list] fixes and signs with
the Use Statement status list key. A reader reads the bit from its cached
copy of that list and never fetches it inside a transaction.

[](){ #tbl-ts-5-06-status-members }

<figure markdown="1" class="ekdn-table">

| Member | Type | Presence | Value |
|---|---|---|---|
| `status.status_list` | object | Present | The reference into the Use Statement status list |
| `status.status_list.idx` | number | Present | The index of this statement in that list |
| `status.status_list.uri` | string | Present | The address the Status List Token is published at |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-06-036 }**REQ-TS-5-06-036** The interval between `iat` and `exp` MUST be the validity period the Governance Profile sets for a registered use, except where [REQ-TS-5-06-117][req-ts-5-06-117] shortens it.
- [](){ #req-ts-5-06-117 }**REQ-TS-5-06-117** Where `iat` plus that validity period falls after the end of the accreditation period of the entity `sub` names, `exp` MUST be the end of that accreditation period.
- [](){ #req-ts-5-06-037 }**REQ-TS-5-06-037** `status` MUST carry `status_list` with the members [the table of status members][tbl-ts-5-06-status-members] marks present, as [IETF Token Status List][ref-i-d-ietf-oauth-status-list] defines them.
- [](){ #req-ts-5-06-038 }**REQ-TS-5-06-038** `status.status_list.uri` MUST be the address of the Use Statement status list Trust Registry publishes.
- [](){ #req-ts-5-06-039 }**REQ-TS-5-06-039** Trust Registry MUST allocate each statement its own index.
- [](){ #req-ts-5-06-096 }**REQ-TS-5-06-096** Trust Registry MUST NOT allocate one index to two statements.
- [](){ #req-ts-5-06-040 }**REQ-TS-5-06-040** Trust Registry MUST set the index of a statement to revoked when the Root Authority withdraws that use.
- [](){ #req-ts-5-06-097 }**REQ-TS-5-06-097** Trust Registry MUST publish the Use Statement status list again once it has set the index of a statement to revoked.
- [](){ #req-ts-5-06-041 }**REQ-TS-5-06-041** Trust Registry MUST keep the index of a withdrawn statement allocated to it, so that the index is never read as the status of another statement.
- [](){ #req-ts-5-06-042 }**REQ-TS-5-06-042** Mobile Wallet MUST read the status of a statement from its cached copy of the Use Statement status list.
- [](){ #req-ts-5-06-098 }**REQ-TS-5-06-098** Mobile Wallet MUST NOT fetch the Use Statement status list while a request is in hand.
- [](){ #req-ts-5-06-043 }**REQ-TS-5-06-043** Mobile Wallet MAY use its last-known-good copy of the Use Statement status list past the Time to Live (TTL) of that copy, up to the tolerance limit the Governance Profile sets.
- [](){ #req-ts-5-06-044 }**REQ-TS-5-06-044** Mobile Wallet MUST refuse a Use Statement whose status it can only read from a copy past the tolerance limit.

</div>

The last rule is the one that costs a transaction, and it is deliberate. A
statement whose status cannot be established is a statement that may have
been withdrawn weeks ago, and the only safe reading of it is none, as
[three rules for reading the copy][three-rules-for-reading-the-copy] sets
out.

## Carrying it online {#ts-5-06-carrying-it-online}

Online, the statement travels in the `verifier_info` parameter of the signed
Request Object, which OpenID for Verifiable Presentations
([OpenID4VP 1.0][ref-openid4vp]) defines for attestations
about the verifier. A Use Statement is a claim-bound attestation in the
sense that specification gives the term: it is not signed by the verifier,
it is bound to it by `sub`, and the wallet checks that binding against the
identifier the request came under.

1. **Verifier Core builds the request.** It takes the template the operator
   chose, reads the `use_id` that template names, and loads the statement
   for that use.
2. **It attaches the statement.** One entry goes into `verifier_info`,
   carrying the compact statement as the verifier collected it, unchanged.
3. **It signs the Request Object.** The signature covers `verifier_info`
   along with the rest of the request, so neither the statement nor the
   attributes asked for can be edited in transit.

The request below runs the civil servant fare check: it points at three
attributes of a Kartu ASN in SD-JWT-based Verifiable Credential (SD-JWT VC) draft -13, the online format, and carries the
statement of that use, which names the same three. Its `claim_sets` asks
for one of two combinations of them, `nama` and `instansi` first and
`nama`, `nip` and `instansi` second, so that the `restricted` `nip` travels
only where the first cannot be answered.

``` { .json title="The Use Statement in a Request Object, online" data-format="JSON" }
{
  "client_id": "decentralized_identifier:did:webvh:QmUATC5jyf5yVy72GYAp8nSvuwshzDy6wYX7WmNY5UJtXT:terminal-nusantara.co.id",
  "aud": "https://self-issued.me/v2",
  "response_type": "vp_token",
  "response_mode": "direct_post.jwt",
  "response_uri": "https://terminal-nusantara.co.id/presentation/response",
  "client_metadata": {
    "jwks": {
      "keys": [
        {
          "kty": "EC",
          "crv": "P-256",
          "x": "Tvz5Pa9PJyu-PCY_aUt9MsXJnP_Aazn0vYWR7m8H8MM",
          "y": "nmUzQIm5F_NWeCQaXxebnvyjLfnD4-WtgVThJ5502wk",
          "use": "enc",
          "alg": "ECDH-ES",
          "kid": "oMguraoK95YAKSJLswX3aLwf9SHYJTCS9AG2g37NFQ4"
        }
      ]
    },
    "vp_formats_supported": {
      "dc+sd-jwt": {
        "sd-jwt_alg_values": ["ES256"],
        "kb-jwt_alg_values": ["ES256"]
      },
      "ldp_vc": {
        "proof_type_values": ["DataIntegrityProof"],
        "cryptosuite_values": ["ecdsa-rdfc-2019"]
      }
    }
  },
  "nonce": "lDBtAJCIkEhdHMvK0Vp6rQ",
  "state": "LMvHXBmP9koh5LKQbQcv6A",
  "dcql_query": {
    "credentials": [
      {
        "id": "kartu-asn",
        "format": "dc+sd-jwt",
        "meta": { "vct_values": ["id.idctf.kartu-asn.1"] },
        "claims": [
          { "id": "nama", "path": ["nama"] },
          { "id": "nip", "path": ["nip"] },
          { "id": "instansi", "path": ["instansi"] }
        ],
        "claim_sets": [
          ["nama", "instansi"],
          ["nama", "nip", "instansi"]
        ]
      }
    ]
  },
  "verifier_info": [
    {
      "format": "vnd.id.idctf.use-statement+jwt",
      "data": "eyJ0eXAiOiJ2bmQuaWQuaWRjdGYudXNlLXN0YXRlbWVudCtqd3QiLCJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDp3ZWJ2aDpRbVpqeTF0OW9GaWFGamhYMmUzOHVNdVI3bWd0ZExqSFBNR2ZqRWZ2cnNtYWlxOnRydXN0LmdvLmlkI3VzZS1zdGF0ZW1lbnQtMSJ9.eyJpc3MiOiJkaWQ6d2Vidmg6UW1aankxdDlvRmlhRmpoWDJlMzh1TXVSN21ndGRMakhQTUdmakVmdnJzbWFpcTp0cnVzdC5nby5pZCIsInN1YiI6ImRpZDp3ZWJ2aDpRbVVBVEM1anlmNXlWeTcyR1lBcDhuU3Z1d3NoekR5NndZWDdXbU5ZNVVKdFhUOnRlcm1pbmFsLW51c2FudGFyYS5jby5pZCIsInVzZV9pZCI6InRhcmlmLWRpbmFzLWFzbiIsInB1cnBvc2UiOnsiaWQiOiJWZXJpZmlrYXNpIHN0YXR1cyBBU04gdW50dWsgdGFyaWYgcGVyamFsYW5hbiBkaW5hcyIsImVuIjoiQ2l2aWwgc2VydmFudCBzdGF0dXMgY2hlY2sgZm9yIHRoZSBvZmZpY2lhbCB0cmF2ZWwgZmFyZSJ9LCJsZWdhbF9iYXNpcyI6IlBlcmphbmppYW4ga2VyamEgc2FtYSB0YXJpZiBwZXJqYWxhbmFuIGRpbmFzIGRlbmdhbiBpbnN0YW5zaSBwZW1lcmludGFoIiwiY2xhaW1zIjpbImlkLmlkY3RmLmthcnR1LWFzbi4xI25hbWEiLCJpZC5pZGN0Zi5rYXJ0dS1hc24uMSNuaXAiLCJpZC5pZGN0Zi5rYXJ0dS1hc24uMSNpbnN0YW5zaSJdLCJzdGF0dXMiOnsic3RhdHVzX2xpc3QiOnsiaWR4Ijo2MzUwLCJ1cmkiOiJodHRwczovL3JlZ2lzdHJ5LnRydXN0LmdvLmlkL3N0YXR1cy91c2Utc3RhdGVtZW50cy0xIn19LCJpYXQiOjE3ODAyNzIwMDAsImV4cCI6MTgxMTgwODAwMH0.RCnnWXP8-pHc4PrAh3qtc-sSxFXDc1mn-YepQ1EZ6FNsO2G7BI2yTkbCKNHokrwfJ78k3ikcQ8SPphaDvWAacg"
    }
  ],
  "iat": 1792221240,
  "exp": 1792221540
}
```

Three of these claims matter to the statement: the identifier the verifier
came under, the query the statement bounds, and the signature over both.
The others are what
[Verifying a credential online via OpenID4VP](verifying-a-credential-online-via-openid4vp.md)
requires of a signed Request Object answered by `direct_post.jwt`: `aud`,
the static value a wallet without dynamic discovery is addressed by;
`response_uri`, where the wallet posts its answer; `client_metadata`, whose
`jwks` holds the key, drawn for this request alone, that the answer is
encrypted to, and whose
`vp_formats_supported` names the formats the verifier accepts, because under
the `decentralized_identifier` prefix every verifier metadata value other
than the signing key comes from `client_metadata`; `state`, which the
answer returns; and `iat` and `exp`, which bound the request in time.

A credential query may offer the claims it points at in more than one
combination through `claim_sets`, as [OpenID4VP][ref-openid4vp] section
6.4.1 defines it. The wallet answers the first option it can, and an option
is a whole answer the verifier set out, never a choice left to the citizen.
The statement bounds every option, so `claims` names each attribute any
option reaches. The options are ordered for least disclosure, by the
minimization class [the attributes field][rulebook-attributes-field] gives
each attribute: an option that reaches a `restricted` attribute comes after
every option that reaches none. Under a type whose schema requires every
attribute, as every illustrative type's does, the first option can always
be answered; a later one serves a credential that cannot answer it, such as
one issued under a version of the type without that attribute. An `ldp_vc`
query offers no options, because the credential travels whole. How the wallet fetches the
Request Object is fixed by
[Verifying a credential online via OpenID4VP](verifying-a-credential-online-via-openid4vp.md).

The second request runs the beneficiary record, a further use of the same
entity. It asks for the Kartu Nikah in `ldp_vc`, and its query names all nine
attributes, as the statement it carries does, because the credential travels
whole. Under OpenID4VP, `type_values` holds the types of the credential as
fully expanded Internationalized Resource Identifiers (IRIs), after its
`@context` is applied, and each claim path starts at `credentialSubject`.
Everything else is the request above, with a `nonce`, a `state` and times of its own.

``` { .json title="The Use Statement of the Kartu Nikah use in a Request Object, online" data-format="JSON" }
{
  "client_id": "decentralized_identifier:did:webvh:QmUATC5jyf5yVy72GYAp8nSvuwshzDy6wYX7WmNY5UJtXT:terminal-nusantara.co.id",
  "aud": "https://self-issued.me/v2",
  "response_type": "vp_token",
  "response_mode": "direct_post.jwt",
  "response_uri": "https://terminal-nusantara.co.id/presentation/response",
  "client_metadata": {
    "jwks": {
      "keys": [
        {
          "kty": "EC",
          "crv": "P-256",
          "x": "gIu62YUQgMYORr4kRYaN4BBMM8vuNmxvN3MM24fgmKg",
          "y": "-iKvHFs5uDtZtX6SnUna8ZUMGaOz_w7kA2U0z0EJ4Es",
          "use": "enc",
          "alg": "ECDH-ES",
          "kid": "ciRZcaQa7yTSIQeuPgVq-rs6FJKtvrQzN8bXvlL5nGY"
        }
      ]
    },
    "vp_formats_supported": {
      "dc+sd-jwt": {
        "sd-jwt_alg_values": ["ES256"],
        "kb-jwt_alg_values": ["ES256"]
      },
      "ldp_vc": {
        "proof_type_values": ["DataIntegrityProof"],
        "cryptosuite_values": ["ecdsa-rdfc-2019"]
      }
    }
  },
  "nonce": "RuHSu26QAGIX4UP7H-ulTA",
  "state": "407uibewmpIt7GXwpP4eHA",
  "dcql_query": {
    "credentials": [
      {
        "id": "kartu-nikah",
        "format": "ldp_vc",
        "meta": {
          "type_values": [
            [
              "https://www.w3.org/2018/credentials#VerifiableCredential",
              "https://catalog.trust.go.id/vocab/id.idctf.kartu-nikah#KartuNikah"
            ]
          ]
        },
        "claims": [
          { "path": ["credentialSubject", "nama_suami"] },
          { "path": ["credentialSubject", "nama_istri"] },
          { "path": ["credentialSubject", "tanggal_akad"] },
          { "path": ["credentialSubject", "nomor_akta_nikah"] },
          { "path": ["credentialSubject", "kua"] },
          { "path": ["credentialSubject", "kabupaten_kota"] },
          { "path": ["credentialSubject", "provinsi"] },
          { "path": ["credentialSubject", "foto_suami"] },
          { "path": ["credentialSubject", "foto_istri"] }
        ]
      }
    ]
  },
  "verifier_info": [
    {
      "format": "vnd.id.idctf.use-statement+jwt",
      "data": "eyJ0eXAiOiJ2bmQuaWQuaWRjdGYudXNlLXN0YXRlbWVudCtqd3QiLCJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDp3ZWJ2aDpRbVpqeTF0OW9GaWFGamhYMmUzOHVNdVI3bWd0ZExqSFBNR2ZqRWZ2cnNtYWlxOnRydXN0LmdvLmlkI3VzZS1zdGF0ZW1lbnQtMSJ9.eyJpc3MiOiJkaWQ6d2Vidmg6UW1aankxdDlvRmlhRmpoWDJlMzh1TXVSN21ndGRMakhQTUdmakVmdnJzbWFpcTp0cnVzdC5nby5pZCIsInN1YiI6ImRpZDp3ZWJ2aDpRbVVBVEM1anlmNXlWeTcyR1lBcDhuU3Z1d3NoekR5NndZWDdXbU5ZNVVKdFhUOnRlcm1pbmFsLW51c2FudGFyYS5jby5pZCIsInVzZV9pZCI6InBlbmNhdGF0YW4tYWhsaS13YXJpcyIsInB1cnBvc2UiOnsiaWQiOiJWZXJpZmlrYXNpIHN0YXR1cyBwZXJrYXdpbmFuIHVudHVrIHBlbmNhdGF0YW4gYWhsaSB3YXJpcyIsImVuIjoiVmVyaWZpY2F0aW9uIG9mIG1hcml0YWwgc3RhdHVzIGZvciByZWNvcmRpbmcgYSBiZW5lZmljaWFyeSJ9LCJsZWdhbF9iYXNpcyI6IlBlcmphbmppYW4gbGF5YW5hbiBkZW5nYW4gcGVuZ2d1bmEgdW50dWsgcGVuY2F0YXRhbiBhaGxpIHdhcmlzIiwiY2xhaW1zIjpbImlkLmlkY3RmLmthcnR1LW5pa2FoLjEjbmFtYV9zdWFtaSIsImlkLmlkY3RmLmthcnR1LW5pa2FoLjEjbmFtYV9pc3RyaSIsImlkLmlkY3RmLmthcnR1LW5pa2FoLjEjdGFuZ2dhbF9ha2FkIiwiaWQuaWRjdGYua2FydHUtbmlrYWguMSNub21vcl9ha3RhX25pa2FoIiwiaWQuaWRjdGYua2FydHUtbmlrYWguMSNrdWEiLCJpZC5pZGN0Zi5rYXJ0dS1uaWthaC4xI2thYnVwYXRlbl9rb3RhIiwiaWQuaWRjdGYua2FydHUtbmlrYWguMSNwcm92aW5zaSIsImlkLmlkY3RmLmthcnR1LW5pa2FoLjEjZm90b19zdWFtaSIsImlkLmlkY3RmLmthcnR1LW5pa2FoLjEjZm90b19pc3RyaSJdLCJzdGF0dXMiOnsic3RhdHVzX2xpc3QiOnsiaWR4Ijo3NDA4LCJ1cmkiOiJodHRwczovL3JlZ2lzdHJ5LnRydXN0LmdvLmlkL3N0YXR1cy91c2Utc3RhdGVtZW50cy0xIn19LCJpYXQiOjE3ODI4NjQwMDAsImV4cCI6MTgxNDQwMDAwMH0.3D5_Cry8wIeJypqTBCx_1cQ30xxcwj_83CjahWCXd9eMqj-9ThdHyQCAKNt_fgLPQlzau3fHl28kVCX74t976g"
    }
  ],
  "iat": 1792221250,
  "exp": 1792221550
}
```

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-06-045 }**REQ-TS-5-06-045** Verifier Core MUST carry the Use Statement of the use the request serves in the `verifier_info` parameter of that request.
- [](){ #req-ts-5-06-046 }**REQ-TS-5-06-046** The `format` member of that entry MUST be `vnd.id.idctf.use-statement+jwt`.
- [](){ #req-ts-5-06-047 }**REQ-TS-5-06-047** The `data` member of that entry MUST be the compact statement as Trust Authority issued it, byte for byte.
- [](){ #req-ts-5-06-048 }**REQ-TS-5-06-048** Verifier Core MUST NOT carry `credential_ids` in that entry, because the use bounds every credential the request asks for.
- [](){ #req-ts-5-06-049 }**REQ-TS-5-06-049** Verifier Core MUST carry exactly one entry whose `format` is `vnd.id.idctf.use-statement+jwt`.
- [](){ #req-ts-5-06-050 }**REQ-TS-5-06-050** Verifier Core MUST carry the statement inside a signed Request Object.
- [](){ #req-ts-5-06-099 }**REQ-TS-5-06-099** Verifier Core MUST NOT send a Use Statement in an unsigned request.
- [](){ #req-ts-5-06-051 }**REQ-TS-5-06-051** Verifier Core MUST NOT ask for an attribute outside the `claims` of the statement it carries.
- [](){ #req-ts-5-06-113 }**REQ-TS-5-06-113** Verifier Core MAY offer the claims of an SD-JWT VC credential query in more than one combination through `claim_sets`.
- [](){ #req-ts-5-06-114 }**REQ-TS-5-06-114** Verifier Core MUST NOT carry `claim_sets` in an `ldp_vc` credential query.
- [](){ #req-ts-5-06-115 }**REQ-TS-5-06-115** Verifier Core SHOULD place an option of `claim_sets` that reaches a `restricted` attribute after every option that reaches none.
- [](){ #req-ts-5-06-108 }**REQ-TS-5-06-108** Verifier Core MUST read an attribute it asks for under a `docType` as covered only by an entry of `claims` that names the `id` of a Rulebook whose mdoc `docType` is that `docType`.

</div>

A merchant's online request is the same request, relayed. Mobile Verifier
builds and signs it with the device key, the RP Intermediary's Verifier Core
holds it at the address the wallet fetches it from, and the statement in it
is the category statement, issued to the intermediary rather than to the
merchant. That is why the wallet's check on `sub` has two forms, one per
identifier the request came under.

## Carrying it in proximity {#ts-5-06-carrying-it-in-proximity}

In proximity there is no OpenID4VP request to put a parameter in. The same
statement travels in `requestInfo`, the open map
[ISO/IEC 18013-5:2021][ref-iso-18013-5] defines on every `ItemsRequest`, under the
key `idUseStatement`, as the bytes of the compact statement in a Concise
Binary Object Representation (CBOR) byte string. ReaderAuth
signs the `ItemsRequest` it sits in, so the statement is bound to the
session and to the device certificate that signed the request.

1. **The cashier picks the category.** Mobile Verifier loads the statement
   of the business category the transaction falls under, from the ones its
   device was given at provisioning.
2. **It builds each `ItemsRequest`.** The statement goes into `requestInfo`
   under `idUseStatement`, as a byte string holding the compact statement.
3. **It signs each one.** ReaderAuth covers the `ItemsRequest`, and with it
   the statement, the document type and the data elements asked for.
4. **A request for two documents repeats the statement.** `requestInfo` is
   per `ItemsRequest`, so each one carries the same statement.

``` { .text title="The ItemsRequest of a proximity age check, in CBOR diagnostic notation" data-format="CBOR diag" }
{
  "docType": "id.idctf.ktp.1",
  "nameSpaces": {
    "id.idctf.ktp.1": {
      "usia_di_atas_17": false
    }
  },
  "requestInfo": {
    "idUseStatement": 'eyJ0eXAiOiJ2bmQuaWQuaWRjdGYudXNlLXN0YXRlbWVudCtqd3QiLCJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDp3ZWJ2aDpRbVpqeTF0OW9GaWFGamhYMmUzOHVNdVI3bWd0ZExqSFBNR2ZqRWZ2cnNtYWlxOnRydXN0LmdvLmlkI3VzZS1zdGF0ZW1lbnQtMSJ9.eyJpc3MiOiJkaWQ6d2Vidmg6UW1aankxdDlvRmlhRmpoWDJlMzh1TXVSN21ndGRMakhQTUdmakVmdnJzbWFpcTp0cnVzdC5nby5pZCIsInN1YiI6ImRpZDp3ZWJ2aDpRbVVBVEM1anlmNXlWeTcyR1lBcDhuU3Z1d3NoekR5NndZWDdXbU5ZNVVKdFhUOnRlcm1pbmFsLW51c2FudGFyYS5jby5pZCIsInVzZV9pZCI6ImthdGVnb3JpLXRlbWJha2F1IiwicHVycG9zZSI6eyJpZCI6IlZlcmlmaWthc2kgdXNpYSBwZW1iZWxpIHByb2R1ayB0ZW1iYWthdSIsImVuIjoiQWdlIHZlcmlmaWNhdGlvbiBmb3IgdGhlIHB1cmNoYXNlIG9mIHRvYmFjY28gcHJvZHVjdHMifSwibGVnYWxfYmFzaXMiOiJQUCAxMDkvMjAxMiBQYXNhbCAyNSBodXJ1ZiBiIiwiY2xhaW1zIjpbImlkLmlkY3RmLmt0cC4xI3VzaWFfZGlfYXRhc18xNyIsIm9yZy5pc28uMTgwMTMuNS4xLm1ETC4xI2FnZV9vdmVyXzE4Il0sInN0YXR1cyI6eyJzdGF0dXNfbGlzdCI6eyJpZHgiOjgxMiwidXJpIjoiaHR0cHM6Ly9yZWdpc3RyeS50cnVzdC5nby5pZC9zdGF0dXMvdXNlLXN0YXRlbWVudHMtMSJ9fSwiaWF0IjoxNzc2NDcwNDAwLCJleHAiOjE4MDgwMDY0MDB9.Jji2ue0AO4C-NpZbZ8ttzs7DsqWLTZbm2JGAsDw7Utb_ctPZUVZxFXeH-xTm0e7LxrSfq0Mhw24vHfu3yFcDzA'
  }
}
```

``` { .text title="The same ItemsRequest, as CBOR" data-format="CBOR hex" }
a367646f63547970656e69642e69646374662e6b74702e316a6e616d65537061
636573a16e69642e69646374662e6b74702e31a16f757369615f64695f617461
735f3137f46b72657175657374496e666fa16e696455736553746174656d656e
7459041c65794a30655841694f694a32626d5175615751756157526a64475975
64584e6c4c584e305958526c6257567564437471643351694c434a6862476369
4f694a46557a49314e694973496d74705a434936496d52705a4470335a574a32
6144705262567071655446304f57394761574647616d68594d6d557a4f48564e
64564933625764305a4578715346424e52325a7152575a32636e4e7459576c78
4f6e527964584e304c6d64764c6d6c6b4933567a5a53317a644746305a57316c
626e51744d534a392e65794a7063334d694f694a6b6157513664325669646d67
3655573161616e6b7864446c76526d6c68526d706f57444a6c4d7a6831545856
534e32316e6447524d616b68515455646d616b566d646e4a7a62574670635470
30636e567a6443356e627935705a434973496e4e3159694936496d52705a4470
335a574a32614470526256564256454d31616e6c6d4e586c576554637952316c
426344687555335a3164334e6f656b52354e6e645a574464586255355a4e5656
4b644668554f6e526c636d3170626d46734c5735316332467564474679595335
6a627935705a434973496e567a5a5639705a434936496d74686447566e62334a
704c58526c62574a686132463149697769634856796347397a5a53493665794a
705a434936496c5a6c636d6c6d6157746863326b6764584e70595342775a5731
695a5778704948427962325231617942305a5731695957746864534973496d56
75496a6f695157646c49485a6c636d6c6d61574e6864476c766269426d623349
676447686c49484231636d4e6f59584e6c4947396d49485276596d466a593238
6763484a765a48566a64484d69665377696247566e59577866596d467a61584d
694f694a51554341784d446b764d6a41784d69425159584e68624341794e5342
6f64584a315a69426949697769593278686157317a496a7062496d6c6b4c6d6c
6b5933526d4c6d7430634334784933567a615746665a476c6659585268633138
784e794973496d39795a793570633238754d5467774d544d754e5334784c6d31
45544334784932466e5a563976646d5679587a4534496c3073496e4e30595852
316379493665794a7a6447463064584e6662476c7a6443493665794a705a4867
694f6a67784d69776964584a70496a6f696148523063484d364c7939795a5764
706333527965533530636e567a6443356e627935705a43397a6447463064584d
7664584e6c4c584e305958526c6257567564484d744d534a3966537769615746
30496a6f784e7a63324e4463774e4441774c434a6c654841694f6a45344d4467
774d4459304d4442392e4a6a6932756530414f34432d4e705a625a3874747a73
37447371574c545a626d324a4741734477375574625f6374505a55565a784658
65482d78546d3065374c7872536671304d687732347648667533794663447a41
```

A type another body named keeps that body's `docType` and namespace on the
wire, so a request for the mobile driving license names
`org.iso.18013.5.1.mDL` while the statement's `claims` name
`org.iso.18013.5.1.mDL.1#age_over_18`. Mobile Verifier reads the two as one
type through the Rulebook whose mdoc `docType` the request names, the same
mapping Verifier Core applies online.

``` { .text title="The ItemsRequest of a proximity age check on a mobile driving license, in CBOR diagnostic notation" data-format="CBOR diag" }
{
  "docType": "org.iso.18013.5.1.mDL",
  "nameSpaces": {
    "org.iso.18013.5.1": {
      "age_over_18": false
    }
  },
  "requestInfo": {
    "idUseStatement": 'eyJ0eXAiOiJ2bmQuaWQuaWRjdGYudXNlLXN0YXRlbWVudCtqd3QiLCJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDp3ZWJ2aDpRbVpqeTF0OW9GaWFGamhYMmUzOHVNdVI3bWd0ZExqSFBNR2ZqRWZ2cnNtYWlxOnRydXN0LmdvLmlkI3VzZS1zdGF0ZW1lbnQtMSJ9.eyJpc3MiOiJkaWQ6d2Vidmg6UW1aankxdDlvRmlhRmpoWDJlMzh1TXVSN21ndGRMakhQTUdmakVmdnJzbWFpcTp0cnVzdC5nby5pZCIsInN1YiI6ImRpZDp3ZWJ2aDpRbVVBVEM1anlmNXlWeTcyR1lBcDhuU3Z1d3NoekR5NndZWDdXbU5ZNVVKdFhUOnRlcm1pbmFsLW51c2FudGFyYS5jby5pZCIsInVzZV9pZCI6ImthdGVnb3JpLXRlbWJha2F1IiwicHVycG9zZSI6eyJpZCI6IlZlcmlmaWthc2kgdXNpYSBwZW1iZWxpIHByb2R1ayB0ZW1iYWthdSIsImVuIjoiQWdlIHZlcmlmaWNhdGlvbiBmb3IgdGhlIHB1cmNoYXNlIG9mIHRvYmFjY28gcHJvZHVjdHMifSwibGVnYWxfYmFzaXMiOiJQUCAxMDkvMjAxMiBQYXNhbCAyNSBodXJ1ZiBiIiwiY2xhaW1zIjpbImlkLmlkY3RmLmt0cC4xI3VzaWFfZGlfYXRhc18xNyIsIm9yZy5pc28uMTgwMTMuNS4xLm1ETC4xI2FnZV9vdmVyXzE4Il0sInN0YXR1cyI6eyJzdGF0dXNfbGlzdCI6eyJpZHgiOjgxMiwidXJpIjoiaHR0cHM6Ly9yZWdpc3RyeS50cnVzdC5nby5pZC9zdGF0dXMvdXNlLXN0YXRlbWVudHMtMSJ9fSwiaWF0IjoxNzc2NDcwNDAwLCJleHAiOjE4MDgwMDY0MDB9.Jji2ue0AO4C-NpZbZ8ttzs7DsqWLTZbm2JGAsDw7Utb_ctPZUVZxFXeH-xTm0e7LxrSfq0Mhw24vHfu3yFcDzA'
  }
}
```

``` { .text title="The same mobile driving license ItemsRequest, as CBOR" data-format="CBOR hex" }
a367646f6354797065756f72672e69736f2e31383031332e352e312e6d444c6a
6e616d65537061636573a1716f72672e69736f2e31383031332e352e31a16b61
67655f6f7665725f3138f46b72657175657374496e666fa16e69645573655374
6174656d656e7459041c65794a30655841694f694a32626d5175615751756157
526a6447597564584e6c4c584e305958526c6257567564437471643351694c43
4a68624763694f694a46557a49314e694973496d74705a434936496d52705a44
70335a574a326144705262567071655446304f57394761574647616d68594d6d
557a4f48564e64564933625764305a4578715346424e52325a7152575a32636e
4e7459576c784f6e527964584e304c6d64764c6d6c6b4933567a5a53317a6447
46305a57316c626e51744d534a392e65794a7063334d694f694a6b6157513664
325669646d673655573161616e6b7864446c76526d6c68526d706f57444a6c4d
7a6831545856534e32316e6447524d616b68515455646d616b566d646e4a7a62
57467063547030636e567a6443356e627935705a434973496e4e315969493649
6d52705a4470335a574a32614470526256564256454d31616e6c6d4e586c5765
54637952316c426344687555335a3164334e6f656b52354e6e645a5744645862
55355a4e56564b644668554f6e526c636d3170626d46734c5735316332467564
4746795953356a627935705a434973496e567a5a5639705a434936496d746864
47566e62334a704c58526c62574a686132463149697769634856796347397a5a
53493665794a705a434936496c5a6c636d6c6d6157746863326b6764584e7059
5342775a5731695a5778704948427962325231617942305a5731695957746864
534973496d5675496a6f695157646c49485a6c636d6c6d61574e6864476c7662
69426d623349676447686c49484231636d4e6f59584e6c4947396d4948527659
6d466a5932386763484a765a48566a64484d69665377696247566e5957786659
6d467a61584d694f694a51554341784d446b764d6a41784d69425159584e6862
4341794e53426f64584a315a69426949697769593278686157317a496a706249
6d6c6b4c6d6c6b5933526d4c6d7430634334784933567a615746665a476c6659
585268633138784e794973496d39795a793570633238754d5467774d544d754e
5334784c6d3145544334784932466e5a563976646d5679587a4534496c307349
6e4e30595852316379493665794a7a6447463064584e6662476c7a6443493665
794a705a4867694f6a67784d69776964584a70496a6f696148523063484d364c
7939795a5764706333527965533530636e567a6443356e627935705a43397a64
47463064584d7664584e6c4c584e305958526c6257567564484d744d534a3966
53776961574630496a6f784e7a63324e4463774e4441774c434a6c654841694f
6a45344d4467774d4459304d4442392e4a6a6932756530414f34432d4e705a62
5a3874747a7337447371574c545a626d324a4741734477375574625f6374505a
55565a78465865482d78546d3065374c7872536671304d687732347648667533
794663447a41
```

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-06-052 }**REQ-TS-5-06-052** Mobile Verifier MUST carry the Use Statement of the category the transaction falls under in the `requestInfo` map of every `ItemsRequest` of the `DeviceRequest`.
- [](){ #req-ts-5-06-053 }**REQ-TS-5-06-053** The key MUST be `idUseStatement`.
- [](){ #req-ts-5-06-054 }**REQ-TS-5-06-054** The value MUST be a CBOR byte string holding the compact statement as Trust Authority issued it, byte for byte.
- [](){ #req-ts-5-06-055 }**REQ-TS-5-06-055** Every `ItemsRequest` of one `DeviceRequest` MUST carry the same statement.
- [](){ #req-ts-5-06-056 }**REQ-TS-5-06-056** Mobile Verifier MUST sign each `ItemsRequest` with ReaderAuth, so that the statement is covered by that signature.
- [](){ #req-ts-5-06-057 }**REQ-TS-5-06-057** Mobile Verifier MUST NOT ask for a document type or a data element outside the `claims` of the statement it carries.
- [](){ #req-ts-5-06-109 }**REQ-TS-5-06-109** Mobile Verifier MUST read a data element it asks for under a `docType` as covered only by an entry of `claims` that names the `id` of a Rulebook whose mdoc `docType` is that `docType`.

</div>

A wallet outside IDCTF ignores a `requestInfo` key it does not know, which
the standard requires of it, and falls back to the `ReaderAuthRole` of the
certificate alone. That is why the extension is a second bound in proximity
rather than a substitute for the statement, as
[REQ-TS-5-04-057][req-ts-5-04-057] keeps it a subset of the registered uses bound to the device.

## Reading it {#ts-5-06-reading-it}

Mobile Wallet runs the same steps on a statement that arrives online and on
one that arrives in proximity, and runs all of them from its own cache,
before the consent screen.

1. **Find the statement.** Online it is the `verifier_info` entry whose
   `format` is `vnd.id.idctf.use-statement+jwt`; in proximity it is the `idUseStatement`
   value of `requestInfo`. A request carrying two of them is refused whole.
2. **Check the signature.** Resolve Trust Authority's DID Document from the
   SCID carried at build time, take the key the `kid` names, and verify the
   JWS. A statement whose signature does not verify is no statement.
3. **Check who it was issued to.** `sub` has to name the party the request
   came from: online from an accredited Relying Party, the DID in
   `client_id`; from a merchant, and in proximity, the entity holding the
   Verifier Issuing CA in the certificate chain of the request.
4. **Check the time and the status.** The statement is valid until `exp`,
   and its bit in the cached Use Statement status list has to be unset.
5. **Check the attributes.** A request names an attribute in the form its
   own protocol uses, never as the identifier `claims` carries, so the
   wallet builds that identifier first: the `id` of the Rulebook of the
   credential it would present, then `#`, then the name of the attribute.
   The type comes from the credential the wallet holds rather than from the
   request, because a type another body named keeps that body's `docType`
   without the Rulebook's version: the mobile driving license is
   `org.iso.18013.5.1.mDL` in a request and `org.iso.18013.5.1.mDL.1` in
   `claims`. Online the name comes from the claim the query asks for; in
   proximity it is the data element identifier. Each identifier so built has to appear in `claims`, compared
   one attribute at a time rather than as a hash over the query, so that a
   verifier may reword a request without invalidating its registration. An
   attribute outside `claims` is refused, and the wallet then treats it as
   a claim it cannot deliver. Online, a credential is presented only where
   the claims its query asks for, or one option of its `claim_sets`, need
   no refused attribute, and an answer that would leave out a credential
   the request requires is not sent at all, as
   [OpenID4VP][ref-openid4vp] sets out for a claim or a credential the
   wallet cannot deliver. In proximity, a document is returned only where
   no data element asked for in it was refused, here or under the
   `ReaderAuthRole` of the certificate that signed the request.
6. **Show the purpose.** The consent screen names the requester and the
   `purpose` of the statement, in the citizen's language.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-06-058 }**REQ-TS-5-06-058** Mobile Wallet MUST verify the statement against a key published in the DID Document of the SCID it carries from build time.
- [](){ #req-ts-5-06-059 }**REQ-TS-5-06-059** Mobile Wallet MUST refuse a statement whose signature does not verify, whose `typ` is not `vnd.id.idctf.use-statement+jwt`, or whose `iss` is not the Trust Authority it carries the SCID of.
- [](){ #req-ts-5-06-060 }**REQ-TS-5-06-060** Mobile Wallet MUST refuse a request carrying more than one Use Statement.
- [](){ #req-ts-5-06-061 }**REQ-TS-5-06-061** Mobile Wallet MUST refuse a `DeviceRequest` whose `ItemsRequest` structures do not all carry the same statement.
- [](){ #req-ts-5-06-062 }**REQ-TS-5-06-062** Mobile Wallet MUST check that `sub` is the DID in `client_id`, where the request came under a DID.
- [](){ #req-ts-5-06-063 }**REQ-TS-5-06-063** Mobile Wallet MUST check that `sub` is the entity holding the Verifier Issuing CA of the certificate chain, where the request came under a Verifier Device Certificate.
- [](){ #req-ts-5-06-064 }**REQ-TS-5-06-064** Mobile Wallet MUST refuse a statement whose `sub` names neither, however valid its signature.
- [](){ #req-ts-5-06-065 }**REQ-TS-5-06-065** Mobile Wallet MUST refuse a statement whose `exp` has passed.
- [](){ #req-ts-5-06-066 }**REQ-TS-5-06-066** Mobile Wallet MUST refuse a statement whose bit in the Use Statement status list is set to revoked.
- [](){ #req-ts-5-06-067 }**REQ-TS-5-06-067** Mobile Wallet MUST refuse every attribute the request asks for that `claims` does not carry.
- [](){ #req-ts-5-06-110 }**REQ-TS-5-06-110** In an OpenID4VP request, Mobile Wallet MUST NOT present a credential unless the claims its query asks for, or the claims of one option of its `claim_sets`, include no attribute refused under [REQ-TS-5-06-067][req-ts-5-06-067].
- [](){ #req-ts-5-06-111 }**REQ-TS-5-06-111** In an OpenID4VP request, Mobile Wallet MUST NOT present any credential where a credential the request requires is left out under [REQ-TS-5-06-110][req-ts-5-06-110].
- [](){ #req-ts-5-06-112 }**REQ-TS-5-06-112** In proximity, Mobile Wallet MUST NOT return a document of a `DeviceRequest` where a data element asked for in it was refused under [REQ-TS-5-06-067][req-ts-5-06-067] or [REQ-TS-5-04-101][req-ts-5-04-101].
- [](){ #req-ts-5-06-068 }**REQ-TS-5-06-068** Mobile Wallet MUST build the identifier of each attribute a request asks for as the `id` of the Rulebook of the credential it would present, followed by `#` and the name of the attribute.
- [](){ #req-ts-5-06-069 }**REQ-TS-5-06-069** Mobile Wallet MUST take the attribute name from the claim the query asks for in an online request and from the data element identifier of an `ItemsRequest` in proximity.
- [](){ #req-ts-5-06-070 }**REQ-TS-5-06-070** Mobile Wallet MUST compare the identifier it built with an entry of `claims` byte for byte, after no further transformation of any kind.
- [](){ #req-ts-5-06-071 }**REQ-TS-5-06-071** Mobile Wallet MUST take the purpose it shows from `purpose`.
- [](){ #req-ts-5-06-100 }**REQ-TS-5-06-100** Mobile Wallet MUST NOT take the purpose it shows from the request.
- [](){ #req-ts-5-06-072 }**REQ-TS-5-06-072** Mobile Wallet MUST check the requester's status on the trusted list as well.
- [](){ #req-ts-5-06-101 }**REQ-TS-5-06-101** Mobile Wallet MUST NOT accept a statement whose `sub` is not granted on the trusted list.
- [](){ #req-ts-5-06-073 }**REQ-TS-5-06-073** Mobile Wallet MUST NOT fetch a Use Statement from Trust Registry or from Trust Authority while a request is in hand.
- [](){ #req-ts-5-06-074 }**REQ-TS-5-06-074** Mobile Wallet MUST verify the statement again on every request that carries it, rather than trusting a result it cached for that use.

</div>

A request carrying no statement at all is a case of its own, and it survives
only as long as the transition does. Before the cut-off the Governance
Profile sets, the wallet serves the request and tells the citizen it is not
registered; from the cut-off on it refuses it. The permission check through
the Authority Statement runs either way, and an attribute outside the
statement is refused from the first day, transition or not.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-06-075 }**REQ-TS-5-06-075** Before the cut-off the Governance Profile sets, Mobile Wallet MUST serve a request carrying no Use Statement.
- [](){ #req-ts-5-06-102 }**REQ-TS-5-06-102** Before the cut-off the Governance Profile sets, Mobile Wallet MUST tell the citizen on the consent screen that a request carrying no Use Statement is not registered.
- [](){ #req-ts-5-06-076 }**REQ-TS-5-06-076** From that cut-off on, Mobile Wallet MUST refuse a request carrying no Use Statement.
- [](){ #req-ts-5-06-077 }**REQ-TS-5-06-077** Mobile Wallet MUST check the requester's permissions whether or not the request carries a Use Statement.

</div>

## Registering, renewing, and withdrawing a use {#ts-5-06-registering-renewing-and-withdrawing-a-use}

A use is submitted by the entity, approved by the Root Authority through the
tier its most sensitive attribute sets, and issued by Trust Authority as one
statement. It does not change after that: a new purpose or a different list
of attributes is a new use with a new `use_id`, and the statement already
issued is withdrawn or left to expire. A renewal is the same use again, the
same `use_id` and the same content, with new times and a new index.

1. **Submission.** The entity submits the purpose, the legal basis, and the
   attributes it asks for, through the interface [Onboarding an entity and registering its keys](onboarding-an-entity-and-registering-its-keys.md) fixes.
2. **Approval.** The Root Authority approves the use, in full or narrowed,
   through the tier the most sensitive attribute in it sets.
3. **Issuance.** Trust Authority allocates the `use_id`, Trust Registry
   allocates the status index, and Trust Authority signs the statement.
4. **Collection.** The entity collects the statement and loads it into the
   Verifier Core that will carry it, and into the devices that read under
   it.
5. **Enforcement.** Verifier Console validates each request template against
   the statement of the use it names, and refuses a template asking for more.
6. **Withdrawal.** The Root Authority withdraws the use, Trust Registry
   flips the bit, and every wallet refuses the statement at its next read.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-06-078 }**REQ-TS-5-06-078** Trust Authority MUST issue a Use Statement only for a use the Root Authority has approved.
- [](){ #req-ts-5-06-079 }**REQ-TS-5-06-079** Trust Authority MUST record the time a use was approved and the time it was withdrawn.
- [](){ #req-ts-5-06-103 }**REQ-TS-5-06-103** Trust Authority MUST keep a withdrawn use with its history rather than deleting it.
- [](){ #req-ts-5-06-080 }**REQ-TS-5-06-080** Trust Authority MUST NOT alter the `purpose`, the `legal_basis`, or the `claims` of a Use Statement it has issued.
- [](){ #req-ts-5-06-081 }**REQ-TS-5-06-081** Trust Authority MUST issue a change of purpose or of attributes as a new use with a new `use_id`.
- [](){ #req-ts-5-06-082 }**REQ-TS-5-06-082** Trust Authority MAY issue a renewal of a use as a new statement carrying the same `use_id`, the same `purpose`, the same `legal_basis`, and the same `claims`.
- [](){ #req-ts-5-06-083 }**REQ-TS-5-06-083** Trust Authority MUST withdraw every Use Statement of an entity whose accreditation is withdrawn.
- [](){ #req-ts-5-06-118 }**REQ-TS-5-06-118** Trust Authority MUST withdraw every Use Statement of an entity whose accreditation period ends without renewal.
- [](){ #req-ts-5-06-084 }**REQ-TS-5-06-084** Trust Authority MUST withdraw a Use Statement whose attributes a withdrawn permission no longer covers.
- [](){ #req-ts-5-06-085 }**REQ-TS-5-06-085** Verifier Console MUST validate each request template against the Use Statement of the use it names.
- [](){ #req-ts-5-06-104 }**REQ-TS-5-06-104** Verifier Console MUST refuse a request template asking for an attribute outside the Use Statement of the use that template names.
- [](){ #req-ts-5-06-086 }**REQ-TS-5-06-086** Verifier Console MUST NOT let a request template name a use whose statement has expired or been withdrawn.

</div>

### Business categories and merchant devices {#ts-5-06-business-categories-and-merchant-devices}

An RP Intermediary registers one use per business category it serves, age
verification for the sale of tobacco products among them, and binds each
merchant device to one or more of those categories when it onboards the
device. The cashier picks the category the transaction falls under, and the
request carries that one statement. The intermediary answers for putting a
merchant in the right category, and the `ReaderAuthRole` of the device
certificate keeps the device inside the categories it was given.

IDCTF registers a purpose per category rather than per merchant. The reason
is arithmetic: a Root
Authority that registered a use for every warung in the country would be
approving millions of registrations that all say the same thing.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-5-06-087 }**REQ-TS-5-06-087** An RP Intermediary MUST register one use per business category.
- [](){ #req-ts-5-06-105 }**REQ-TS-5-06-105** An RP Intermediary MUST NOT register a use per merchant.
- [](){ #req-ts-5-06-088 }**REQ-TS-5-06-088** Verifier Core MUST hand a device the Use Statement of every category that device is bound to, together with its Verifier Device Certificate.
- [](){ #req-ts-5-06-089 }**REQ-TS-5-06-089** Verifier Core MUST hand a device the renewed statement of a category before the statement that device holds expires.
- [](){ #req-ts-5-06-106 }**REQ-TS-5-06-106** Verifier Core MUST hand a device the withdrawal of a category by removing that category from the device.
- [](){ #req-ts-5-06-090 }**REQ-TS-5-06-090** Verifier Core MUST keep the `ReaderAuthRole` of a device certificate within the union of the `claims` of the statements that device is bound to, as [REQ-TS-5-04-057][req-ts-5-04-057] requires.
- [](){ #req-ts-5-06-091 }**REQ-TS-5-06-091** Mobile Verifier MUST carry the statement of one category in one request.
- [](){ #req-ts-5-06-107 }**REQ-TS-5-06-107** Mobile Verifier MUST NOT combine the `claims` of two statements in one request.

</div>

## Security considerations {#ts-5-06-security-considerations}

Each threat below is answered by the requirement named with it.

- **A statement edited on the way to the wallet.** The signature covers
  every claim a wallet acts on, [REQ-TS-5-06-007][req-ts-5-06-007], and the
  wallet verifies it on every request rather than caching a verdict,
  [REQ-TS-5-06-074][req-ts-5-06-074]. Online the Request Object signature
  covers the statement as well, [REQ-TS-5-06-050][req-ts-5-06-050]; in
  proximity ReaderAuth does,
  [REQ-TS-5-06-056][req-ts-5-06-056].
- **One verifier presenting another verifier's registration.** A statement
  names the entity it was issued to in `sub`, and the wallet refuses one
  that does not name the party the request came under,
  [REQ-TS-5-06-062][req-ts-5-06-062],
  [REQ-TS-5-06-063][req-ts-5-06-063],
  [REQ-TS-5-06-064][req-ts-5-06-064].
- **Two statements in one request, each covering part of the query.** The
  wallet refuses a request carrying more than one,
  [REQ-TS-5-06-060][req-ts-5-06-060], and a proximity request whose parts
  disagree, [REQ-TS-5-06-061][req-ts-5-06-061], so the attributes are
  always matched against one registration rather than a union of several.
- **A statement that outlives its withdrawal.** The validity period bounds
  how long it survives the decision that ended it,
  [REQ-TS-5-06-036][req-ts-5-06-036], the status list carries the
  withdrawal before that, [REQ-TS-5-06-040][req-ts-5-06-040], and a wallet
  that cannot establish the status within the tolerance limit refuses the
  statement, [REQ-TS-5-06-044][req-ts-5-06-044].
- **A merchant reaching past its category.** The device certificate bounds
  it, [REQ-TS-5-06-090][req-ts-5-06-090], the statement bounds it again,
  [REQ-TS-5-06-067][req-ts-5-06-067], and a device does not combine two
  categories into one request,
  [REQ-TS-5-06-107][req-ts-5-06-107].
- **A purpose written for the transaction rather than registered.** The
  consent screen is built from the statement,
  [REQ-TS-5-06-071][req-ts-5-06-071], and Verifier Console refuses a
  template that asks for more than the use it names,
  [REQ-TS-5-06-104][req-ts-5-06-104].
- **One stolen key reaching every artifact.** The Use Statement key signs
  nothing else, [REQ-TS-5-06-034][req-ts-5-06-034], and the list that
  revokes what it signed is signed by another key.
- **The transition used as a way around registration.** A request carrying
  no statement is marked as unregistered to the citizen while the transition
  lasts, [REQ-TS-5-06-075][req-ts-5-06-075],
  [REQ-TS-5-06-102][req-ts-5-06-102], refused after it,
  [REQ-TS-5-06-076][req-ts-5-06-076], and the permission check runs in
  either case, [REQ-TS-5-06-077][req-ts-5-06-077].

## Privacy considerations {#ts-5-06-privacy-considerations}

Carrying the statement rather than fetching it is the privacy property of
this specification. A wallet that resolved a registration at request time
would tell Trust Authority which citizen was dealing with which Relying
Party at what moment, every time anyone showed a credential. Nothing of the
kind reaches Trust Authority here: the statement arrives with the request
and is checked against artifacts the wallet already holds,
[REQ-TS-5-06-073][req-ts-5-06-073], as
[what connects the two planes][what-connects-the-two-planes] sets out.

The statement itself carries nothing about a citizen,
[REQ-TS-5-06-015][req-ts-5-06-015]. It names an entity, a purpose, a legal
basis, and a list of attributes, and the same statement goes to every wallet
the entity asks, so nothing in it marks one transaction apart from another.

What a use reaches is what minimization is enforced on. The list in `claims`
is the one an approval was given for, and the wallet refuses anything
outside it, [REQ-TS-5-06-067][req-ts-5-06-067], so a verifier cannot widen a
request by rewording it. Showing the registered purpose rather than the one
the request carries, [REQ-TS-5-06-071][req-ts-5-06-071],
[REQ-TS-5-06-100][req-ts-5-06-100], is what makes
consent informed by something that was reviewed.

## Changelog {#ts-5-06-changelog}

<figure markdown="1" class="ekdn-table">

| Version | Date | Change |
|---|---|---|
| 1.0 draft | 19 October 2026 | First draft |

</figure>
