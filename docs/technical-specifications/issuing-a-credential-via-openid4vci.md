---
title: "[TS-1-01] Issuing a credential via OpenID4VCI"
description: The OpenID4VCI profile Issuer Core exposes and Mobile Wallet runs against it, from the signed issuer metadata and the credential offer, through authorization, DPoP, and the nonce, to the credential request, deferred issuance, the notification, and renewal.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §4.5, §7.2, §9.1, Kep. 1, Kep. 5, Kep. 21, Kep. 26, Kep. 27; JWT di OpenID4VCI dan OpenID4VP, bagian OpenID4VCI; Peta Alur Penerbitan dan Presentasi §2.1, §2.2, §2.3; Rincian Module dan Operasi §5.2, §5.5, §7.2; OpenID4VCI 1.0; OpenID4VC HAIP 1.0; RFC 9449; RFC 9126; RFC 9207; tracks/0129, tracks/0155, tracks/0165, tracks/0175, tracks/0180, tracks/0269, tracks/0298, tracks/0310, tracks/0344; EUDI ARF Annex 2 ISSU_42, ISSU_65 -->

<p class="ekdn-docid">TS-1-01</p>

# Issuing a credential via OpenID4VCI {#ts-1-01-issuing-a-credential-via-openid4vci}

<p class="ekdn-lead" markdown="span">
Issuance is the one exchange that puts a credential in a citizen's wallet.
This specification fixes how Issuer Core and Mobile Wallet run it.
</p>

Every sentence on this page binds Issuer Core, which runs the credential
issuer and its authorization server, and Mobile Wallet, which runs the
client, and an Assessment Body tests them against it in the version the
Governance Profile puts in force. The key words and the identifier
`REQ-TS-1-01-nnn` follow [Common provisions](common-provisions.md).

## Who runs this and what it needs {#ts-1-01-who-runs-this-and-what-it-needs}

This specification fixes the profile of
[OpenID for Verifiable Credential Issuance (OpenID4VCI) 1.0][ref-openid4vci]
that IDCTF runs:

- The issuer metadata and its signature.
- The credential offer.
- Authorization through the Authorization Code flow with a pushed
  authorization request (PAR) and through the Pre-Authorized Code flow.
- The access token and its binding through Demonstrating Proof of Possession
  (DPoP).
- The nonce.
- The credential request and its answer.
- Deferred issuance.
- The notification.
- Renewal.
- The errors.

Its conformance targets are Issuer Core, which is both the credential issuer
and its own authorization server, and Mobile Wallet, which is the client.

It leaves to other documents:

- The credential in each of its three representations, which
  [Issuing a credential in SD-JWT VC, mdoc, and `ldp_vc`](issuing-a-credential-in-sd-jwt-vc-mdoc-and-ldp-vc.md)
  holds.
- The Key Attestation, the proof that carries it, and the checks Issuer Core
  runs on both, which
  [Issuing and reading a Key Attestation](issuing-and-reading-a-key-attestation.md)
  holds, this page saying only which proof types an issuer announces and where
  the proof travels.
- How a signer names its key and how a reader finds it, which
  [Finding a signer's key from its DID](finding-a-signers-key-from-its-did.md)
  holds.
- The status list a credential points into, which
  [Publishing and reading a status list](publishing-and-reading-a-status-list.md)
  holds.
- The trusted list and the Authority Statement the wallet reads before it asks
  for anything, which
  [Publishing and reading the trusted list](publishing-and-reading-the-trusted-list.md)
  and [Answering with an Authority Statement](answering-with-an-authority-statement.md)
  hold.
- The representations, the assurance level, and the display of a type, which
  its Credential Rulebook holds under
  [Rulebook structure](../credential-rulebook/rulebook-structure.md).
- How a citizen signs in at the authorization endpoint and how an issuer binds
  the citizen to a record in its source system, which the issuer settles within
  [the Governance Framework's obligations of issuers][gf-issuers].
- How a wallet installation enrolls with its Wallet Backend Service, which
  [Enrolling a wallet installation and attesting its key](enrolling-a-wallet-installation-and-attesting-its-key.md)
  holds.
- The numbers, which the Governance Profile holds:
    - The lifetime of a pre-authorized code, an authorization code, a request
      Uniform Resource Identifier (URI), an access token, a nonce, a DPoP
      nonce, and a deferred request.
    - The inactivity period after which a refresh token is refused.
    - The attempts allowed on a transaction code.
    - The algorithms an issuance key, a credential key, a Key Attestation key,
      and a DPoP key may use.
    - How long before `exp` a wallet starts renewal.

The profile follows the
[OpenID4VC High Assurance Interoperability Profile (HAIP) 1.0][ref-openid4vc-haip],
which IDCTF reads as a comparison and is not bound by, except in these
places:

- The wallet is a public client and does not authenticate at the PAR and
  token endpoints, and an issuer may let it reach the token endpoint
  anonymously in the Pre-Authorized Code flow, because the attestation-based
  client authentication HAIP asks for there is still an Internet-Draft. The
  wallet proves what it is where it hands over the key, as
  [Issuer to Wallet][issuer-to-wallet] sets out.
- Every token signed under a Decentralized Identifier (DID), the issuer's
  metadata, its SD-JWT-based Verifiable Credential (SD-JWT VC) draft -13, and
  the Wallet Provider's Key Attestation included, names its key by `kid` and
  not by `x5c`, as
  [Finding a signer's key from its DID](finding-a-signers-key-from-its-did.md)
  fixes.
- A wallet asks for credential configurations through `authorization_details`,
  which names each one exactly, and not through `scope`.
- A refresh token lasts as long as the credential's administrative validity
  period, where HAIP advises against a refresh more than a year after
  issuance, for the reason [Renewal][ts-1-01-renewal] gives.

An issuer announces no batch issuance, which HAIP leaves to it, because a
wallet installation has [one credential key][the-credential-key].

Before the first exchange, each target holds what the rules below assume:

- **Issuer Core** holds:
    - An entry in the trusted list that reads `granted` as an Identity Issuer
      or an Attribute Issuer.
    - An Authority Statement letting it issue each type it offers.
    - The Credential Rulebook of each such type and the Type Metadata its
      `display` points at.
    - Its `issuance-jose` key in its DID Document.
    - For a type issued as an mdoc, its Document Signer Certificate.
    - A cached copy of the trusted list.
    - A public address of its own, as [Issuer Core][hla-issuer-core] sets out.
- **Mobile Wallet** holds:
    - The credential key in the device's secure element, enrolled with its
      Wallet Backend Service.
    - The trusted list, the Authority Statements, and every entity's
      `did:webvh` log its [trust cache sync][trust-cache-sync] fetched.
    - The client identifier and redirect address its Wallet Provider chose for
      it.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-1-01-001 }**REQ-TS-1-01-001** Issuer Core MUST meet every requirement on this page that names Issuer Core, and every requirement on what Issuer Core writes: its metadata, its offers, its tokens, and its answers.
- [](){ #req-ts-1-01-002 }**REQ-TS-1-01-002** Mobile Wallet MUST meet every requirement on this page that names Mobile Wallet, and every requirement on what Mobile Wallet sends: its requests, its DPoP proofs, and its notifications.

</div>

## What issuance does {#ts-1-01-what-issuance-does}

Issuance hands a citizen a credential bound to the credential key of their
wallet installation, signed by an issuer the trusted list accredits and the
Root Authority permitted to issue that type. One protocol carries all three
representations; what changes from one to the next is only what Issuer Core
assembles at the end, as
[one credential, two representations][one-credential-two-representations]
sets out.

Two grants start it. In the Authorization Code flow the citizen signs in at
the issuer, through the browser, and the issuer learns who they are from that
sign-in. In the Pre-Authorized Code flow the issuer already knows the citizen,
because an officer found the record or the citizen signed in to the
institution's own service, and it hands the wallet a code with the offer and a
second code by another channel. Either way the identity of the citizen comes
from the issuer's side and never from the wallet, as
[how `subjectRef` reaches Issuer Core][subjectref-origin] sets out. The
[Authorization Code flow][authorization-code-flow] and the
[Pre-Authorized Code flow][pre-authorized-code-flow] draw both paths.

Before the citizen types a code or signs in anywhere, the wallet has checked
the issuer against its cached trusted list, as
[Signed metadata][ts-1-01-signed-metadata] sets out. Nothing in that check
touches the network beyond the issuer itself.

The wallet is a public client: it holds no secret the issuer gave it, and anyone
can claim its client identifier. What protects the exchange is a Proof Key for
Code Exchange (PKCE) on the authorization code, the transaction code the citizen
types on the pre-authorized code, DPoP on every token, and the Key Attestation
at the credential request, where the wallet shows that the key the credential
will be bound to sits in storage of the strength the type demands.

## The exchange {#ts-1-01-the-exchange}

An issuance runs in twelve steps.

1. Issuer Core makes a credential offer, and Mobile Wallet receives it through
   a QR code or a deeplink.
2. Mobile Wallet fetches the issuer's signed metadata and its authorization
   server metadata.
3. It verifies the metadata, takes the issuer's DID from it, and reads the
   issuer's trusted list entry and Authority Statement from its cache. It
   refuses the offer if either fails.
4. In the Authorization Code flow it sends a pushed authorization request,
   opens the authorization endpoint for the citizen to sign in, and receives
   an authorization code. In the Pre-Authorized Code flow it asks the citizen
   for the transaction code.
5. It exchanges the code at the token endpoint for an access token and a
   refresh token bound to its DPoP key, with one credential identifier for
   each credential configuration of the offer.
6. It fetches a nonce from the Nonce Endpoint.
7. It obtains a Key Attestation carrying that nonce from its Wallet Backend
   Service.
8. It sends a credential request for one credential identifier, with the proof
   that carries the Key Attestation.
9. Issuer Core checks its own standing, the proof, and the attestation, reads
   the claims from its source system, and builds and signs the credential.
10. It answers with the credential, or with a transaction identifier that the
    wallet presents at the deferred credential endpoint until the credential
    is ready.
11. Mobile Wallet checks the credential, stores it, and reports the outcome at
    the notification endpoint.
12. Mobile Wallet runs steps 6 to 11 again for each other credential
    identifier it received at step 5.

Renewal takes the same path from step 5, with the refresh token in place of
the code.

## An issuance, as exchanged {#ts-1-01-an-issuance-as-exchanged}

The citizens, the issuers, their addresses, and every key are invented, and
nothing has been issued. Every field is exact.

The examples agree with the rest of these pages:

- The issuers: the ones [the trusted list][ts-5-01-trusted-list-payload]
  carries, with the same DIDs.
- Each signed issuer metadata verifies under the `issuance-jose` key its `kid`
  names.
- Each DPoP proof verifies under the key its header carries.
- The Key Attestations verify under the Key Attestation key of the
  Wallet Provider.
- The key proof and the first Key Attestation: the ones
  [Issuing and reading a Key Attestation](issuing-and-reading-a-key-attestation.md)
  shows.
- The three credentials: the ones
  [Issuing a credential in SD-JWT VC, mdoc, and `ldp_vc`](issuing-a-credential-in-sd-jwt-vc-mdoc-and-ldp-vc.md)
  shows, byte for byte.

Access tokens, refresh tokens, codes, and identifiers are opaque strings Issuer
Core drew; nothing reads them but the issuer that drew them.

### The Kartu ASN, through the Pre-Authorized Code flow {#ts-1-01-the-kartu-asn-through-the-pre-authorized-code-flow}

The Badan Kepegawaian Negara (BKN) issues the Kartu ASN, a type whose Credential Rulebook names SD-JWT VC and
mdoc and sets `min_assurance` to `substantial`. An officer has checked the
civil servant's record, and BKN's portal shows the offer as a QR code. The
offer names both credential configurations of the type, and its transaction
code went to the civil servant's telephone:

``` { .text title="A credential offer with a pre-authorized code, as the QR code carries it" data-format="URI" }
openid-credential-offer://?credential_offer=%7B%22credential_issuer%22%3A%22https%3A%2F%2Fissuer.bkn.go.id%22%2C%22credential_configuration_ids%22%3A%5B%22id.idctf.kartu-asn.1%3Asd-jwt-vc%22%2C%22id.idctf.kartu-asn.1%3Amdoc%22%5D%2C%22grants%22%3A%7B%22urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Apre-authorized_code%22%3A%7B%22pre-authorized_code%22%3A%22n3b2wEVTT9PYmMug8RpcyeaK%22%2C%22tx_code%22%3A%7B%22input_mode%22%3A%22numeric%22%2C%22length%22%3A6%2C%22description%22%3A%22Kode%20enam%20angka%20yang%20dikirim%20BKN%20lewat%20SMS%22%7D%7D%7D%7D
```

``` { .json title="The same credential offer, decoded" data-format="JSON" }
{
  "credential_issuer": "https://issuer.bkn.go.id",
  "credential_configuration_ids": [
    "id.idctf.kartu-asn.1:sd-jwt-vc",
    "id.idctf.kartu-asn.1:mdoc"
  ],
  "grants": {
    "urn:ietf:params:oauth:grant-type:pre-authorized_code": {
      "pre-authorized_code": "n3b2wEVTT9PYmMug8RpcyeaK",
      "tx_code": {
        "input_mode": "numeric",
        "length": 6,
        "description": "Kode enam angka yang dikirim BKN lewat SMS"
      }
    }
  }
}
```

The wallet asks for the metadata in its signed form:

``` { .http title="GET /.well-known/openid-credential-issuer, asking for the signed form" data-format="HTTP" }
GET /.well-known/openid-credential-issuer HTTP/1.1
Host: issuer.bkn.go.id
Accept: application/jwt
```

``` { .http title="200, the signed issuer metadata" data-format="HTTP" }
HTTP/1.1 200 OK
Content-Type: application/jwt

eyJ0eXAiOiJvcGVuaWR2Y2ktaXNzdWVyLW1ldGFkYXRhK2p3dCIsImFsZyI6IkVTMjU2Iiwia2lkIjoiZGlkOndlYnZoOlFtZThScmlHbkt4NWoyUWpvYVkxU2dSU3B4VEhkanExMUwyRXhneTF6VjJ4c0o6YmtuLmdvLmlkI2lzc3VhbmNlLWpvc2UtMSJ9.eyJpc3MiOiJkaWQ6d2Vidmg6UW1lOFJyaUduS3g1ajJRam9hWTFTZ1JTcHhUSGRqcTExTDJFeGd5MXpWMnhzSjpia24uZ28uaWQiLCJzdWIiOiJodHRwczovL2lzc3Vlci5ia24uZ28uaWQiLCJpYXQiOjE3OTIxOTUyMDAsImNyZWRlbnRpYWxfaXNzdWVyIjoiaHR0cHM6Ly9pc3N1ZXIuYmtuLmdvLmlkIiwiY3JlZGVudGlhbF9lbmRwb2ludCI6Imh0dHBzOi8vaXNzdWVyLmJrbi5nby5pZC9jcmVkZW50aWFsIiwibm9uY2VfZW5kcG9pbnQiOiJodHRwczovL2lzc3Vlci5ia24uZ28uaWQvbm9uY2UiLCJkZWZlcnJlZF9jcmVkZW50aWFsX2VuZHBvaW50IjoiaHR0cHM6Ly9pc3N1ZXIuYmtuLmdvLmlkL2RlZmVycmVkX2NyZWRlbnRpYWwiLCJub3RpZmljYXRpb25fZW5kcG9pbnQiOiJodHRwczovL2lzc3Vlci5ia24uZ28uaWQvbm90aWZpY2F0aW9uIiwiY3JlZGVudGlhbF9jb25maWd1cmF0aW9uc19zdXBwb3J0ZWQiOnsiaWQuaWRjdGYua2FydHUtYXNuLjE6c2Qtand0LXZjIjp7ImZvcm1hdCI6ImRjK3NkLWp3dCIsInZjdCI6ImlkLmlkY3RmLmthcnR1LWFzbi4xIiwiY3J5cHRvZ3JhcGhpY19iaW5kaW5nX21ldGhvZHNfc3VwcG9ydGVkIjpbImp3ayJdLCJjcmVkZW50aWFsX3NpZ25pbmdfYWxnX3ZhbHVlc19zdXBwb3J0ZWQiOlsiRVMyNTYiXSwicHJvb2ZfdHlwZXNfc3VwcG9ydGVkIjp7Imp3dCI6eyJwcm9vZl9zaWduaW5nX2FsZ192YWx1ZXNfc3VwcG9ydGVkIjpbIkVTMjU2Il0sImtleV9hdHRlc3RhdGlvbnNfcmVxdWlyZWQiOnsia2V5X3N0b3JhZ2UiOlsiaXNvXzE4MDQ1X21vZGVyYXRlIiwiaXNvXzE4MDQ1X2hpZ2giXSwidXNlcl9hdXRoZW50aWNhdGlvbiI6WyJpc29fMTgwNDVfbW9kZXJhdGUiLCJpc29fMTgwNDVfaGlnaCJdfX0sImF0dGVzdGF0aW9uIjp7InByb29mX3NpZ25pbmdfYWxnX3ZhbHVlc19zdXBwb3J0ZWQiOlsiRVMyNTYiXSwia2V5X2F0dGVzdGF0aW9uc19yZXF1aXJlZCI6eyJrZXlfc3RvcmFnZSI6WyJpc29fMTgwNDVfbW9kZXJhdGUiLCJpc29fMTgwNDVfaGlnaCJdLCJ1c2VyX2F1dGhlbnRpY2F0aW9uIjpbImlzb18xODA0NV9tb2RlcmF0ZSIsImlzb18xODA0NV9oaWdoIl19fX0sImNyZWRlbnRpYWxfbWV0YWRhdGEiOnsiZGlzcGxheSI6W3sibmFtZSI6IkthcnR1IEFTTiIsImxvY2FsZSI6ImlkIiwiZGVzY3JpcHRpb24iOiJLYXJ0dSBpZGVudGl0YXMgQXBhcmF0dXIgU2lwaWwgTmVnYXJhIiwibG9nbyI6eyJ1cmkiOiJodHRwczovL2NhdGFsb2cudHJ1c3QuZ28uaWQvdHlwZS1tZXRhZGF0YS9rYXJ0dS1hc24tdjEvbG9nby5wbmciLCJhbHRfdGV4dCI6IkxhbWJhbmcgR2FydWRhIFBhbmNhc2lsYSJ9LCJiYWNrZ3JvdW5kX2NvbG9yIjoiI0ZGRkZGRiIsInRleHRfY29sb3IiOiIjOEExQjNEIn0seyJuYW1lIjoiQ2l2aWwgU2VydmFudCBDYXJkIiwibG9jYWxlIjoiZW4iLCJkZXNjcmlwdGlvbiI6IklkZW50aXR5IGNhcmQgb2YgYW4gSW5kb25lc2lhbiBjaXZpbCBzZXJ2YW50IiwibG9nbyI6eyJ1cmkiOiJodHRwczovL2NhdGFsb2cudHJ1c3QuZ28uaWQvdHlwZS1tZXRhZGF0YS9rYXJ0dS1hc24tdjEvbG9nby5wbmciLCJhbHRfdGV4dCI6IkdhcnVkYSBQYW5jYXNpbGEgZW1ibGVtIn0sImJhY2tncm91bmRfY29sb3IiOiIjRkZGRkZGIiwidGV4dF9jb2xvciI6IiM4QTFCM0QifV0sImNsYWltcyI6W3sicGF0aCI6WyJuYW1hIl0sIm1hbmRhdG9yeSI6dHJ1ZSwiZGlzcGxheSI6W3sibmFtZSI6Ik5hbWEiLCJsb2NhbGUiOiJpZCJ9LHsibmFtZSI6Ik5hbWUiLCJsb2NhbGUiOiJlbiJ9XX0seyJwYXRoIjpbIm5pcCJdLCJtYW5kYXRvcnkiOnRydWUsImRpc3BsYXkiOlt7Im5hbWUiOiJOSVAiLCJsb2NhbGUiOiJpZCJ9LHsibmFtZSI6IkNpdmlsIFNlcnZhbnQgSUQgTnVtYmVyIiwibG9jYWxlIjoiZW4ifV19LHsicGF0aCI6WyJnb2xvbmdhbiJdLCJtYW5kYXRvcnkiOnRydWUsImRpc3BsYXkiOlt7Im5hbWUiOiJHb2xvbmdhbiIsImxvY2FsZSI6ImlkIn0seyJuYW1lIjoiUmFuayIsImxvY2FsZSI6ImVuIn1dfSx7InBhdGgiOlsic3RhdHVzX2tlcGVnYXdhaWFuIl0sIm1hbmRhdG9yeSI6dHJ1ZSwiZGlzcGxheSI6W3sibmFtZSI6IlN0YXR1cyBLZXBlZ2F3YWlhbiIsImxvY2FsZSI6ImlkIn0seyJuYW1lIjoiRW1wbG95bWVudCBTdGF0dXMiLCJsb2NhbGUiOiJlbiJ9XX0seyJwYXRoIjpbImphYmF0YW4iXSwibWFuZGF0b3J5Ijp0cnVlLCJkaXNwbGF5IjpbeyJuYW1lIjoiSmFiYXRhbiIsImxvY2FsZSI6ImlkIn0seyJuYW1lIjoiUG9zaXRpb24iLCJsb2NhbGUiOiJlbiJ9XX0seyJwYXRoIjpbInVuaXRfa2VyamEiXSwibWFuZGF0b3J5Ijp0cnVlLCJkaXNwbGF5IjpbeyJuYW1lIjoiVW5pdCBLZXJqYSIsImxvY2FsZSI6ImlkIn0seyJuYW1lIjoiV29yayBVbml0IiwibG9jYWxlIjoiZW4ifV19LHsicGF0aCI6WyJpbnN0YW5zaSJdLCJtYW5kYXRvcnkiOnRydWUsImRpc3BsYXkiOlt7Im5hbWUiOiJJbnN0YW5zaSIsImxvY2FsZSI6ImlkIn0seyJuYW1lIjoiQWdlbmN5IiwibG9jYWxlIjoiZW4ifV19LHsicGF0aCI6WyJmb3RvIl0sIm1hbmRhdG9yeSI6dHJ1ZSwiZGlzcGxheSI6W3sibmFtZSI6IkZvdG8iLCJsb2NhbGUiOiJpZCJ9LHsibmFtZSI6IlBob3RvIiwibG9jYWxlIjoiZW4ifV19XX19LCJpZC5pZGN0Zi5rYXJ0dS1hc24uMTptZG9jIjp7ImZvcm1hdCI6Im1zb19tZG9jIiwiZG9jdHlwZSI6ImlkLmlkY3RmLmthcnR1LWFzbi4xIiwiY3J5cHRvZ3JhcGhpY19iaW5kaW5nX21ldGhvZHNfc3VwcG9ydGVkIjpbImNvc2Vfa2V5Il0sImNyZWRlbnRpYWxfc2lnbmluZ19hbGdfdmFsdWVzX3N1cHBvcnRlZCI6Wy03XSwicHJvb2ZfdHlwZXNfc3VwcG9ydGVkIjp7Imp3dCI6eyJwcm9vZl9zaWduaW5nX2FsZ192YWx1ZXNfc3VwcG9ydGVkIjpbIkVTMjU2Il0sImtleV9hdHRlc3RhdGlvbnNfcmVxdWlyZWQiOnsia2V5X3N0b3JhZ2UiOlsiaXNvXzE4MDQ1X21vZGVyYXRlIiwiaXNvXzE4MDQ1X2hpZ2giXSwidXNlcl9hdXRoZW50aWNhdGlvbiI6WyJpc29fMTgwNDVfbW9kZXJhdGUiLCJpc29fMTgwNDVfaGlnaCJdfX0sImF0dGVzdGF0aW9uIjp7InByb29mX3NpZ25pbmdfYWxnX3ZhbHVlc19zdXBwb3J0ZWQiOlsiRVMyNTYiXSwia2V5X2F0dGVzdGF0aW9uc19yZXF1aXJlZCI6eyJrZXlfc3RvcmFnZSI6WyJpc29fMTgwNDVfbW9kZXJhdGUiLCJpc29fMTgwNDVfaGlnaCJdLCJ1c2VyX2F1dGhlbnRpY2F0aW9uIjpbImlzb18xODA0NV9tb2RlcmF0ZSIsImlzb18xODA0NV9oaWdoIl19fX0sImNyZWRlbnRpYWxfbWV0YWRhdGEiOnsiZGlzcGxheSI6W3sibmFtZSI6IkthcnR1IEFTTiIsImxvY2FsZSI6ImlkIiwiZGVzY3JpcHRpb24iOiJLYXJ0dSBpZGVudGl0YXMgQXBhcmF0dXIgU2lwaWwgTmVnYXJhIiwibG9nbyI6eyJ1cmkiOiJodHRwczovL2NhdGFsb2cudHJ1c3QuZ28uaWQvdHlwZS1tZXRhZGF0YS9rYXJ0dS1hc24tdjEvbG9nby5wbmciLCJhbHRfdGV4dCI6IkxhbWJhbmcgR2FydWRhIFBhbmNhc2lsYSJ9LCJiYWNrZ3JvdW5kX2NvbG9yIjoiI0ZGRkZGRiIsInRleHRfY29sb3IiOiIjOEExQjNEIn0seyJuYW1lIjoiQ2l2aWwgU2VydmFudCBDYXJkIiwibG9jYWxlIjoiZW4iLCJkZXNjcmlwdGlvbiI6IklkZW50aXR5IGNhcmQgb2YgYW4gSW5kb25lc2lhbiBjaXZpbCBzZXJ2YW50IiwibG9nbyI6eyJ1cmkiOiJodHRwczovL2NhdGFsb2cudHJ1c3QuZ28uaWQvdHlwZS1tZXRhZGF0YS9rYXJ0dS1hc24tdjEvbG9nby5wbmciLCJhbHRfdGV4dCI6IkdhcnVkYSBQYW5jYXNpbGEgZW1ibGVtIn0sImJhY2tncm91bmRfY29sb3IiOiIjRkZGRkZGIiwidGV4dF9jb2xvciI6IiM4QTFCM0QifV0sImNsYWltcyI6W3sicGF0aCI6WyJpZC5pZGN0Zi5rYXJ0dS1hc24uMSIsIm5hbWEiXSwibWFuZGF0b3J5Ijp0cnVlLCJkaXNwbGF5IjpbeyJuYW1lIjoiTmFtYSIsImxvY2FsZSI6ImlkIn0seyJuYW1lIjoiTmFtZSIsImxvY2FsZSI6ImVuIn1dfSx7InBhdGgiOlsiaWQuaWRjdGYua2FydHUtYXNuLjEiLCJuaXAiXSwibWFuZGF0b3J5Ijp0cnVlLCJkaXNwbGF5IjpbeyJuYW1lIjoiTklQIiwibG9jYWxlIjoiaWQifSx7Im5hbWUiOiJDaXZpbCBTZXJ2YW50IElEIE51bWJlciIsImxvY2FsZSI6ImVuIn1dfSx7InBhdGgiOlsiaWQuaWRjdGYua2FydHUtYXNuLjEiLCJnb2xvbmdhbiJdLCJtYW5kYXRvcnkiOnRydWUsImRpc3BsYXkiOlt7Im5hbWUiOiJHb2xvbmdhbiIsImxvY2FsZSI6ImlkIn0seyJuYW1lIjoiUmFuayIsImxvY2FsZSI6ImVuIn1dfSx7InBhdGgiOlsiaWQuaWRjdGYua2FydHUtYXNuLjEiLCJzdGF0dXNfa2VwZWdhd2FpYW4iXSwibWFuZGF0b3J5Ijp0cnVlLCJkaXNwbGF5IjpbeyJuYW1lIjoiU3RhdHVzIEtlcGVnYXdhaWFuIiwibG9jYWxlIjoiaWQifSx7Im5hbWUiOiJFbXBsb3ltZW50IFN0YXR1cyIsImxvY2FsZSI6ImVuIn1dfSx7InBhdGgiOlsiaWQuaWRjdGYua2FydHUtYXNuLjEiLCJqYWJhdGFuIl0sIm1hbmRhdG9yeSI6dHJ1ZSwiZGlzcGxheSI6W3sibmFtZSI6IkphYmF0YW4iLCJsb2NhbGUiOiJpZCJ9LHsibmFtZSI6IlBvc2l0aW9uIiwibG9jYWxlIjoiZW4ifV19LHsicGF0aCI6WyJpZC5pZGN0Zi5rYXJ0dS1hc24uMSIsInVuaXRfa2VyamEiXSwibWFuZGF0b3J5Ijp0cnVlLCJkaXNwbGF5IjpbeyJuYW1lIjoiVW5pdCBLZXJqYSIsImxvY2FsZSI6ImlkIn0seyJuYW1lIjoiV29yayBVbml0IiwibG9jYWxlIjoiZW4ifV19LHsicGF0aCI6WyJpZC5pZGN0Zi5rYXJ0dS1hc24uMSIsImluc3RhbnNpIl0sIm1hbmRhdG9yeSI6dHJ1ZSwiZGlzcGxheSI6W3sibmFtZSI6Ikluc3RhbnNpIiwibG9jYWxlIjoiaWQifSx7Im5hbWUiOiJBZ2VuY3kiLCJsb2NhbGUiOiJlbiJ9XX0seyJwYXRoIjpbImlkLmlkY3RmLmthcnR1LWFzbi4xIiwiZm90byJdLCJtYW5kYXRvcnkiOnRydWUsImRpc3BsYXkiOlt7Im5hbWUiOiJGb3RvIiwibG9jYWxlIjoiaWQifSx7Im5hbWUiOiJQaG90byIsImxvY2FsZSI6ImVuIn1dfV19fX19._hWRXvzc-4jxincyXdlBDSMmtqYYJ9k0CJGgL9ath5FWHTBZySAFRrzSOGx4yJzmgcV_nhBHeqI25AgXLBHFVg
```

``` { .json title="Signed issuer metadata header" data-format="JSON" }
{
  "typ": "openidvci-issuer-metadata+jwt",
  "alg": "ES256",
  "kid": "did:webvh:Qme8RriGnKx5j2QjoaY1SgRSpxTHdjq11L2Exgy1zV2xsJ:bkn.go.id#issuance-jose-1"
}
```

``` { .json title="Signed issuer metadata claims" data-format="JSON" }
{
  "iss": "did:webvh:Qme8RriGnKx5j2QjoaY1SgRSpxTHdjq11L2Exgy1zV2xsJ:bkn.go.id",
  "sub": "https://issuer.bkn.go.id",
  "iat": 1792195200,
  "credential_issuer": "https://issuer.bkn.go.id",
  "credential_endpoint": "https://issuer.bkn.go.id/credential",
  "nonce_endpoint": "https://issuer.bkn.go.id/nonce",
  "deferred_credential_endpoint": "https://issuer.bkn.go.id/deferred_credential",
  "notification_endpoint": "https://issuer.bkn.go.id/notification",
  "credential_configurations_supported": {
    "id.idctf.kartu-asn.1:sd-jwt-vc": {
      "format": "dc+sd-jwt",
      "vct": "id.idctf.kartu-asn.1",
      "cryptographic_binding_methods_supported": [
        "jwk"
      ],
      "credential_signing_alg_values_supported": [
        "ES256"
      ],
      "proof_types_supported": {
        "jwt": {
          "proof_signing_alg_values_supported": [
            "ES256"
          ],
          "key_attestations_required": {
            "key_storage": [
              "iso_18045_moderate",
              "iso_18045_high"
            ],
            "user_authentication": [
              "iso_18045_moderate",
              "iso_18045_high"
            ]
          }
        },
        "attestation": {
          "proof_signing_alg_values_supported": [
            "ES256"
          ],
          "key_attestations_required": {
            "key_storage": [
              "iso_18045_moderate",
              "iso_18045_high"
            ],
            "user_authentication": [
              "iso_18045_moderate",
              "iso_18045_high"
            ]
          }
        }
      },
      "credential_metadata": {
        "display": [
          {
            "name": "Kartu ASN",
            "locale": "id",
            "description": "Kartu identitas Aparatur Sipil Negara",
            "logo": {
              "uri": "https://catalog.trust.go.id/type-metadata/kartu-asn-v1/logo.png",
              "alt_text": "Lambang Garuda Pancasila"
            },
            "background_color": "#FFFFFF",
            "text_color": "#8A1B3D"
          },
          {
            "name": "Civil Servant Card",
            "locale": "en",
            "description": "Identity card of an Indonesian civil servant",
            "logo": {
              "uri": "https://catalog.trust.go.id/type-metadata/kartu-asn-v1/logo.png",
              "alt_text": "Garuda Pancasila emblem"
            },
            "background_color": "#FFFFFF",
            "text_color": "#8A1B3D"
          }
        ],
        "claims": [
          {
            "path": [
              "nama"
            ],
            "mandatory": true,
            "display": [
              {
                "name": "Nama",
                "locale": "id"
              },
              {
                "name": "Name",
                "locale": "en"
              }
            ]
          },
          {
            "path": [
              "nip"
            ],
            "mandatory": true,
            "display": [
              {
                "name": "NIP",
                "locale": "id"
              },
              {
                "name": "Civil Servant ID Number",
                "locale": "en"
              }
            ]
          },
          {
            "path": [
              "golongan"
            ],
            "mandatory": true,
            "display": [
              {
                "name": "Golongan",
                "locale": "id"
              },
              {
                "name": "Rank",
                "locale": "en"
              }
            ]
          },
          {
            "path": [
              "status_kepegawaian"
            ],
            "mandatory": true,
            "display": [
              {
                "name": "Status Kepegawaian",
                "locale": "id"
              },
              {
                "name": "Employment Status",
                "locale": "en"
              }
            ]
          },
          {
            "path": [
              "jabatan"
            ],
            "mandatory": true,
            "display": [
              {
                "name": "Jabatan",
                "locale": "id"
              },
              {
                "name": "Position",
                "locale": "en"
              }
            ]
          },
          {
            "path": [
              "unit_kerja"
            ],
            "mandatory": true,
            "display": [
              {
                "name": "Unit Kerja",
                "locale": "id"
              },
              {
                "name": "Work Unit",
                "locale": "en"
              }
            ]
          },
          {
            "path": [
              "instansi"
            ],
            "mandatory": true,
            "display": [
              {
                "name": "Instansi",
                "locale": "id"
              },
              {
                "name": "Agency",
                "locale": "en"
              }
            ]
          },
          {
            "path": [
              "foto"
            ],
            "mandatory": true,
            "display": [
              {
                "name": "Foto",
                "locale": "id"
              },
              {
                "name": "Photo",
                "locale": "en"
              }
            ]
          }
        ]
      }
    },
    "id.idctf.kartu-asn.1:mdoc": {
      "format": "mso_mdoc",
      "doctype": "id.idctf.kartu-asn.1",
      "cryptographic_binding_methods_supported": [
        "cose_key"
      ],
      "credential_signing_alg_values_supported": [
        -7
      ],
      "proof_types_supported": {
        "jwt": {
          "proof_signing_alg_values_supported": [
            "ES256"
          ],
          "key_attestations_required": {
            "key_storage": [
              "iso_18045_moderate",
              "iso_18045_high"
            ],
            "user_authentication": [
              "iso_18045_moderate",
              "iso_18045_high"
            ]
          }
        },
        "attestation": {
          "proof_signing_alg_values_supported": [
            "ES256"
          ],
          "key_attestations_required": {
            "key_storage": [
              "iso_18045_moderate",
              "iso_18045_high"
            ],
            "user_authentication": [
              "iso_18045_moderate",
              "iso_18045_high"
            ]
          }
        }
      },
      "credential_metadata": {
        "display": [
          {
            "name": "Kartu ASN",
            "locale": "id",
            "description": "Kartu identitas Aparatur Sipil Negara",
            "logo": {
              "uri": "https://catalog.trust.go.id/type-metadata/kartu-asn-v1/logo.png",
              "alt_text": "Lambang Garuda Pancasila"
            },
            "background_color": "#FFFFFF",
            "text_color": "#8A1B3D"
          },
          {
            "name": "Civil Servant Card",
            "locale": "en",
            "description": "Identity card of an Indonesian civil servant",
            "logo": {
              "uri": "https://catalog.trust.go.id/type-metadata/kartu-asn-v1/logo.png",
              "alt_text": "Garuda Pancasila emblem"
            },
            "background_color": "#FFFFFF",
            "text_color": "#8A1B3D"
          }
        ],
        "claims": [
          {
            "path": [
              "id.idctf.kartu-asn.1",
              "nama"
            ],
            "mandatory": true,
            "display": [
              {
                "name": "Nama",
                "locale": "id"
              },
              {
                "name": "Name",
                "locale": "en"
              }
            ]
          },
          {
            "path": [
              "id.idctf.kartu-asn.1",
              "nip"
            ],
            "mandatory": true,
            "display": [
              {
                "name": "NIP",
                "locale": "id"
              },
              {
                "name": "Civil Servant ID Number",
                "locale": "en"
              }
            ]
          },
          {
            "path": [
              "id.idctf.kartu-asn.1",
              "golongan"
            ],
            "mandatory": true,
            "display": [
              {
                "name": "Golongan",
                "locale": "id"
              },
              {
                "name": "Rank",
                "locale": "en"
              }
            ]
          },
          {
            "path": [
              "id.idctf.kartu-asn.1",
              "status_kepegawaian"
            ],
            "mandatory": true,
            "display": [
              {
                "name": "Status Kepegawaian",
                "locale": "id"
              },
              {
                "name": "Employment Status",
                "locale": "en"
              }
            ]
          },
          {
            "path": [
              "id.idctf.kartu-asn.1",
              "jabatan"
            ],
            "mandatory": true,
            "display": [
              {
                "name": "Jabatan",
                "locale": "id"
              },
              {
                "name": "Position",
                "locale": "en"
              }
            ]
          },
          {
            "path": [
              "id.idctf.kartu-asn.1",
              "unit_kerja"
            ],
            "mandatory": true,
            "display": [
              {
                "name": "Unit Kerja",
                "locale": "id"
              },
              {
                "name": "Work Unit",
                "locale": "en"
              }
            ]
          },
          {
            "path": [
              "id.idctf.kartu-asn.1",
              "instansi"
            ],
            "mandatory": true,
            "display": [
              {
                "name": "Instansi",
                "locale": "id"
              },
              {
                "name": "Agency",
                "locale": "en"
              }
            ]
          },
          {
            "path": [
              "id.idctf.kartu-asn.1",
              "foto"
            ],
            "mandatory": true,
            "display": [
              {
                "name": "Foto",
                "locale": "id"
              },
              {
                "name": "Photo",
                "locale": "en"
              }
            ]
          }
        ]
      }
    }
  }
}
```

`iss` is the DID the wallet looks up in its trusted list, and BKN's entry
reads `granted`. Then it reads the authorization server metadata, which needs
no signature, because nothing in it decides whom the wallet trusts:

``` { .http title="GET /.well-known/oauth-authorization-server" data-format="HTTP" }
GET /.well-known/oauth-authorization-server HTTP/1.1
Host: issuer.bkn.go.id
Accept: application/json
```

``` { .http title="200, the authorization server metadata" data-format="HTTP" }
HTTP/1.1 200 OK
Content-Type: application/json

{
  "issuer": "https://issuer.bkn.go.id",
  "authorization_endpoint": "https://issuer.bkn.go.id/authorize",
  "token_endpoint": "https://issuer.bkn.go.id/token",
  "pushed_authorization_request_endpoint": "https://issuer.bkn.go.id/par",
  "require_pushed_authorization_requests": true,
  "response_types_supported": [
    "code"
  ],
  "grant_types_supported": [
    "authorization_code",
    "urn:ietf:params:oauth:grant-type:pre-authorized_code",
    "refresh_token"
  ],
  "code_challenge_methods_supported": [
    "S256"
  ],
  "token_endpoint_auth_methods_supported": [
    "none"
  ],
  "authorization_details_types_supported": [
    "openid_credential"
  ],
  "authorization_response_iss_parameter_supported": true,
  "dpop_signing_alg_values_supported": [
    "ES256"
  ],
  "pre-authorized_grant_anonymous_access_supported": true
}
```

The citizen types the transaction code. The first token request carries no
DPoP nonce, and Issuer Core answers with one:

``` { .http title="POST /token, a first attempt with no DPoP nonce" data-format="HTTP" }
POST /token HTTP/1.1
Host: issuer.bkn.go.id
Content-Type: application/x-www-form-urlencoded
DPoP: eyJ0eXAiOiJkcG9wK2p3dCIsImFsZyI6IkVTMjU2IiwiandrIjp7Imt0eSI6IkVDIiwiY3J2IjoiUC0yNTYiLCJ4IjoieHJDQXdRb3lfeEJpWFowaXBpdGNaQno3QXNsS2ZLVXBJWUMyQUVldkpXYyIsInkiOiJEWF8wZmtLUVRQQjUtY0txVmtVcF9GMXJCTE5KU3BOQlY5SWstWmJObWEwIn19.eyJqdGkiOiJoZnJ2bERtbkQ1TEF1NXNhSDd5MEZnIiwiaHRtIjoiUE9TVCIsImh0dSI6Imh0dHBzOi8vaXNzdWVyLmJrbi5nby5pZC90b2tlbiIsImlhdCI6MTc5MjIxNjc5MH0.Qc3ts_T2ejl20BAR6kgf_EM4ZYt64BpcDwQadGufknbm2g9s0YgZPGU9dONkabAPyyLlQAvbkB7H_yCpnzguQg

grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Apre-authorized_code&pre-authorized_code=n3b2wEVTT9PYmMug8RpcyeaK&tx_code=493817&authorization_details=%5B%7B%22type%22%3A%22openid_credential%22%2C%22credential_configuration_id%22%3A%22id.idctf.kartu-asn.1%3Asd-jwt-vc%22%7D%2C%7B%22type%22%3A%22openid_credential%22%2C%22credential_configuration_id%22%3A%22id.idctf.kartu-asn.1%3Amdoc%22%7D%5D
```

``` { .http title="400, asking for a DPoP nonce" data-format="HTTP" }
HTTP/1.1 400 Bad Request
DPoP-Nonce: PaP4xcQXkKmA0vcaioIbUg_i
Cache-Control: no-store
Content-Type: application/json

{
  "error": "use_dpop_nonce",
  "error_description": "Authorization server requires nonce in DPoP proof"
}
```

The wallet signs a new DPoP proof with that nonce and sends the request again.
It sends no `client_id`, because BKN allows anonymous access to its token
endpoint in this flow:

``` { .http title="POST /token, the pre-authorized code" data-format="HTTP" }
POST /token HTTP/1.1
Host: issuer.bkn.go.id
Content-Type: application/x-www-form-urlencoded
DPoP: eyJ0eXAiOiJkcG9wK2p3dCIsImFsZyI6IkVTMjU2IiwiandrIjp7Imt0eSI6IkVDIiwiY3J2IjoiUC0yNTYiLCJ4IjoieHJDQXdRb3lfeEJpWFowaXBpdGNaQno3QXNsS2ZLVXBJWUMyQUVldkpXYyIsInkiOiJEWF8wZmtLUVRQQjUtY0txVmtVcF9GMXJCTE5KU3BOQlY5SWstWmJObWEwIn19.eyJqdGkiOiJQd0VsSk5GSHVhTEFQVjBRMVRYVFdBIiwiaHRtIjoiUE9TVCIsImh0dSI6Imh0dHBzOi8vaXNzdWVyLmJrbi5nby5pZC90b2tlbiIsImlhdCI6MTc5MjIxNjc5MSwibm9uY2UiOiJQYVA0eGNRWGtLbUEwdmNhaW9JYlVnX2kifQ.MR9V1ipJws-z2ZNRSpT_1fffYleac9DNyezDXSZH-npoFcNYlcvo0We6DItw94j-s3sCt6eXI_pK_p8yxBkVMg

grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Apre-authorized_code&pre-authorized_code=n3b2wEVTT9PYmMug8RpcyeaK&tx_code=493817&authorization_details=%5B%7B%22type%22%3A%22openid_credential%22%2C%22credential_configuration_id%22%3A%22id.idctf.kartu-asn.1%3Asd-jwt-vc%22%7D%2C%7B%22type%22%3A%22openid_credential%22%2C%22credential_configuration_id%22%3A%22id.idctf.kartu-asn.1%3Amdoc%22%7D%5D
```

``` { .json title="The DPoP proof of the token request, decoded" data-format="JSON" }
{
  "header": {
    "typ": "dpop+jwt",
    "alg": "ES256",
    "jwk": {
      "kty": "EC",
      "crv": "P-256",
      "x": "xrCAwQoy_xBiXZ0ipitcZBz7AslKfKUpIYC2AEevJWc",
      "y": "DX_0fkKQTPB5-cKqVkUp_F1rBLNJSpNBV9Ik-ZbNma0"
    }
  },
  "payload": {
    "jti": "PwElJNFHuaLAPV0Q1TXTWA",
    "htm": "POST",
    "htu": "https://issuer.bkn.go.id/token",
    "iat": 1792216791,
    "nonce": "PaP4xcQXkKmA0vcaioIbUg_i"
  }
}
```

``` { .http title="200, the access token and the credential identifiers" data-format="HTTP" }
HTTP/1.1 200 OK
DPoP-Nonce: mvCOydrZb767MV4u3J9a3GWh
Cache-Control: no-store
Content-Type: application/json

{
  "access_token": "ni_IZoW82gn6GQVQbDshjrWOj3XoRiVU-pfY_vzdd4w",
  "token_type": "DPoP",
  "expires_in": 300,
  "refresh_token": "EgFeS5xiitMMzdR3HQP-2F9koJeCL1t-s8kPozZedzU",
  "authorization_details": [
    {
      "type": "openid_credential",
      "credential_configuration_id": "id.idctf.kartu-asn.1:sd-jwt-vc",
      "credential_identifiers": [
        "asn-jb0YglbvHGNb"
      ]
    },
    {
      "type": "openid_credential",
      "credential_configuration_id": "id.idctf.kartu-asn.1:mdoc",
      "credential_identifiers": [
        "asn-Kr-gBP15sIJO"
      ]
    }
  ]
}
```

The wallet fetches a nonce, which its Wallet Backend Service writes into the
Key Attestation:

``` { .http title="POST /nonce" data-format="HTTP" }
POST /nonce HTTP/1.1
Host: issuer.bkn.go.id
Content-Length: 0
```

``` { .http title="200, a fresh c_nonce" data-format="HTTP" }
HTTP/1.1 200 OK
DPoP-Nonce: T4w0HylTpVJUuZ25KkxSFeXQ
Cache-Control: no-store
Content-Type: application/json

{
  "c_nonce": "kQ8vZ2mH7rT1"
}
```

and asks for the first credential identifier. The proof is the `jwt` key proof
[Issuing and reading a Key Attestation](issuing-and-reading-a-key-attestation.md)
shows, with the attestation in its header, `aud` set to BKN's credential issuer
identifier, and no `iss`:

``` { .http title="POST /credential, the Kartu ASN as SD-JWT VC" data-format="HTTP" }
POST /credential HTTP/1.1
Host: issuer.bkn.go.id
Content-Type: application/json
Authorization: DPoP ni_IZoW82gn6GQVQbDshjrWOj3XoRiVU-pfY_vzdd4w
DPoP: eyJ0eXAiOiJkcG9wK2p3dCIsImFsZyI6IkVTMjU2IiwiandrIjp7Imt0eSI6IkVDIiwiY3J2IjoiUC0yNTYiLCJ4IjoieHJDQXdRb3lfeEJpWFowaXBpdGNaQno3QXNsS2ZLVXBJWUMyQUVldkpXYyIsInkiOiJEWF8wZmtLUVRQQjUtY0txVmtVcF9GMXJCTE5KU3BOQlY5SWstWmJObWEwIn19.eyJqdGkiOiJtaW1NQVAzLUtjZ0E0Q1VFR2tWRlhRIiwiaHRtIjoiUE9TVCIsImh0dSI6Imh0dHBzOi8vaXNzdWVyLmJrbi5nby5pZC9jcmVkZW50aWFsIiwiaWF0IjoxNzkyMjE2ODA2LCJub25jZSI6IlQ0dzBIeWxUcFZKVXVaMjVLa3hTRmVYUSIsImF0aCI6InA4Nmlwd2Y2MXcybzVYSGx3VlVDQVRBWHNzUGlwS3FEdGxTb2syajJ1NjQifQ.omPGOtKf-psUEsVIFKPqOJTGbK10uj-O1_PBazT_KN5OLQaHxVhpO32zHILIv_P-RNs-256H-5fVAd4-KzxZww

{
  "credential_identifier": "asn-jb0YglbvHGNb",
  "proofs": {
    "jwt": [
      "eyJ0eXAiOiJvcGVuaWQ0dmNpLXByb29mK2p3dCIsImFsZyI6IkVTMjU2IiwiandrIjp7Imt0eSI6IkVDIiwiY3J2IjoiUC0yNTYiLCJ4IjoiM0NPaHhPZU94cEJPalVKZ3FXU0FVMFFBQVlhWWd1Z1BWSl8yWDJxR2RrYyIsInkiOiIyazk4ODU0cEI3N3VkZFJ2ZThPNGtnNW5JUFQ3RWpFZ3BiZUtxV0x1TUVFIn0sImtleV9hdHRlc3RhdGlvbiI6ImV5SjBlWEFpT2lKclpYa3RZWFIwWlhOMFlYUnBiMjRyYW5kMElpd2lZV3huSWpvaVJWTXlOVFlpTENKcmFXUWlPaUprYVdRNmQyVmlkbWc2VVcxbFZGY3hNelJ4YWxWRE5rVkxXRlUyU2t3elpGWlNaMlF6WmxsdFZYQk5ZbTl2UlVSdmExTndSa1ZCU0Rwa2IyMXdaWFF1WTI4dWFXUWphMlY1TFdGMGRHVnpkR0YwYVc5dUxURWlmUS5leUpwYzNNaU9pSmthV1E2ZDJWaWRtZzZVVzFsVkZjeE16UnhhbFZETmtWTFdGVTJTa3d6WkZaU1oyUXpabGx0VlhCTlltOXZSVVJ2YTFOd1JrVkJTRHBrYjIxd1pYUXVZMjh1YVdRaUxDSmhkSFJsYzNSbFpGOXJaWGx6SWpwYmV5SnJkSGtpT2lKRlF5SXNJbU55ZGlJNklsQXRNalUySWl3aWVDSTZJak5EVDJoNFQyVlBlSEJDVDJwVlNtZHhWMU5CVlRCUlFVRlpZVmxuZFdkUVZrcGZNbGd5Y1Vka2EyTWlMQ0o1SWpvaU1tczVPRGcxTkhCQ056ZDFaR1JTZG1VNFR6UnJaelZ1U1ZCVU4wVnFSV2R3WW1WTGNWZE1kVTFGUlNKOVhTd2lhMlY1WDNOMGIzSmhaMlVpT2xzaWFYTnZYekU0TURRMVgyaHBaMmdpWFN3aWRYTmxjbDloZFhSb1pXNTBhV05oZEdsdmJpSTZXeUpwYzI5Zk1UZ3dORFZmYlc5a1pYSmhkR1VpWFN3aVkyVnlkR2xtYVdOaGRHbHZiaUk2SW1oMGRIQnpPaTh2Wkc5dGNHVjBMbU52TG1sa0wyTmxjblJwWm1sallYUnBiMjR2YzJVdE1qQXlOaTFoSWl3aWJtOXVZMlVpT2lKclVUaDJXakp0U0RkeVZERWlMQ0pwWVhRaU9qRTNPVEl5TVRZNE1EQXNJbVY0Y0NJNk1UYzVNak13TXpJd01IMC5CUmtJa0lNSHYyV1BOQzRWZlJwRFBERjdwSUtsMlRZZmRldlR4eEpINGtCQjRGQmFMdmZZZDBKUmJ3RGQ3NnVfbDd1TVEtN210bEktc2Jra3NndnZEQSJ9.eyJhdWQiOiJodHRwczovL2lzc3Vlci5ia24uZ28uaWQiLCJpYXQiOjE3OTIyMTY4MDUsIm5vbmNlIjoia1E4dloybUg3clQxIn0.KedVy6MjilzJ8yHTA70rs9lgrrVJDp2SwSv6_IH9GsMSBImEwU7HfkfVuBAXWCizv2CeL-8cJ4-63DcYzdnrEg"
    ]
  }
}
```

``` { .json title="The DPoP proof of the credential request, decoded" data-format="JSON" }
{
  "header": {
    "typ": "dpop+jwt",
    "alg": "ES256",
    "jwk": {
      "kty": "EC",
      "crv": "P-256",
      "x": "xrCAwQoy_xBiXZ0ipitcZBz7AslKfKUpIYC2AEevJWc",
      "y": "DX_0fkKQTPB5-cKqVkUp_F1rBLNJSpNBV9Ik-ZbNma0"
    }
  },
  "payload": {
    "jti": "mimMAP3-KcgA4CUEGkVFXQ",
    "htm": "POST",
    "htu": "https://issuer.bkn.go.id/credential",
    "iat": 1792216806,
    "nonce": "T4w0HylTpVJUuZ25KkxSFeXQ",
    "ath": "p86ipwf61w2o5XHlwVUCATAXssPipKqDtlSok2j2u64"
  }
}
```

``` { .http title="200, the Kartu ASN as SD-JWT VC" data-format="HTTP" }
HTTP/1.1 200 OK
DPoP-Nonce: FmIuUPPQPekxDZk4cEvfesCL
Cache-Control: no-store
Content-Type: application/json

{
  "credentials": [
    {
      "credential": "eyJ0eXAiOiJkYytzZC1qd3QiLCJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDp3ZWJ2aDpRbWU4UnJpR25LeDVqMlFqb2FZMVNnUlNweFRIZGpxMTFMMkV4Z3kxelYyeHNKOmJrbi5nby5pZCNpc3N1YW5jZS1qb3NlLTEifQ.eyJpc3MiOiJkaWQ6d2Vidmg6UW1lOFJyaUduS3g1ajJRam9hWTFTZ1JTcHhUSGRqcTExTDJFeGd5MXpWMnhzSjpia24uZ28uaWQiLCJ2Y3QiOiJpZC5pZGN0Zi5rYXJ0dS1hc24uMSIsImNuZiI6eyJqd2siOnsia3R5IjoiRUMiLCJjcnYiOiJQLTI1NiIsIngiOiIzQ09oeE9lT3hwQk9qVUpncVdTQVUwUUFBWWFZZ3VnUFZKXzJYMnFHZGtjIiwieSI6IjJrOTg4NTRwQjc3dWRkUnZlOE80a2c1bklQVDdFakVncGJlS3FXTHVNRUUifX0sIl9zZF9hbGciOiJzaGEtMjU2IiwiX3NkIjpbIjF6QTdMcXNPdGJoTFZRaG9fUlNlMFRHcVJyZmctUzU4SlpHV1NmZzZabU0iLCJDZnVRdi1jS3JnemYwdXpIeHUtVEJFQkp2dFo0UEE3U0RhVjloOFQ5TF9RIiwiRVQ5QmlsbFV3VmRoYkhjNnRmXy0xWEFDRWdWUDRiX2lVUHhIQ2FYQlNiYyIsIkhMeVU4aHRZWno0TmkyZlJkN3BTWWRpQ2JCLXF0NDhwQlM5aDJCR013VFEiLCJlNlVoQk44QXk1emRVUGdDX2htbnBXbGR3QnhpWDhGN2tPVzRuUklwNXdNIiwiZkFoREt6VjNVMzlqQzZiN0dMaEdGRGw3NnVnVy1tN0R6N1hxcUJuamxkYyIsImhLTUpsakZJTlQtd0ljUDhFUnJhWURrSExyMjZPWUJTQUlHS0ItMG5ORzgiLCJ3N0MxZXJCNno4OG1oRVZzTm5hUVlEZ2JacUNIakxsM2NieDFFemllUnFzIl0sInN0YXR1cyI6eyJzdGF0dXNfbGlzdCI6eyJpZHgiOjQ4MTkyMCwidXJpIjoiaHR0cHM6Ly9ia24uZ28uaWQvc3RhdHVzL2thcnR1LWFzbi0xIn19LCJuYmYiOjE3OTIyMTY4MTAsImlhdCI6MTc5MjIxNjgxMCwiZXhwIjoxODIzNzUyODEwfQ.Rtt14iNH1COHmkwCwvzkYcg2RftZdls7V1WghZc1xZC3GmENzivjroJTPBu2C83Qy4pbdbNsX0lorDW26kbPLg~WyJ3SXVNc2VoQTM1UEp0RU1yUzRub0NRIiwibmFtYSIsIkJ1ZGkgU2FudG9zbyBXaWNha3Nvbm8iXQ~WyJ1b19YWTdpUXQtZGRMZk4yTVZMZEdnIiwibmlwIiwiMTk4NzAzMTUyMDEwMDExMDAyIl0~WyJMSjBmYk54N3ZwT2h4UlpCVjNhNTB3IiwiZ29sb25nYW4iLCJJSUkvYyJd~WyJWTmRqX2xoU00xTXBWTktMOW1HMTR3Iiwic3RhdHVzX2tlcGVnYXdhaWFuIiwiUE5TIl0~WyJwZVViQWhBdlZiUkNhdkoxbm5mNmRBIiwiamFiYXRhbiIsIkFuYWxpcyBLZWJpamFrYW4gQWhsaSBNdWRhIl0~WyJNNW81SnZyU0ZpeHZvUjNLZWk1VTFnIiwidW5pdF9rZXJqYSIsIkRpcmVrdG9yYXQgSmFiYXRhbiBBU04iXQ~WyJSb1o4SHRpMk9JVkJ4NHlNd3Q0UkZRIiwiaW5zdGFuc2kiLCJCYWRhbiBLZXBlZ2F3YWlhbiBOZWdhcmEiXQ~WyJNa0FESE9vcHFJSGJvbEJISHVBNmNnIiwiZm90byIsImRhdGE6aW1hZ2UvanBlZztiYXNlNjQsLzlqLzRBQVFTa1pKUmdBQkFRRUFZQUJnQUFELzJ3QkRBQWdHQmdjR0JRZ0hCd2NKQ1FnS0RCUU5EQXNMREJrU0V3OFVIUm9mSGgwYUhCd2dKQzRuSUNJc0l4d2NLRGNwTERBeE5EUTBIeWM1UFRneVBDNHpOREwvd0FBTENBQUJBQUVCQVJFQS84UUFGQUFCQUFBQUFBQUFBQUFBQUFBQUFBQUFDZi9FQUJRUUFRQUFBQUFBQUFBQUFBQUFBQUFBQUFELzJnQUlBUUVBQUQ4QUtwLy8yUT09Il0~"
    }
  ],
  "notification_id": "CMemYMX-3nU0WGfu"
}
```

The credential is bound to the key in `attested_keys`, and its `iss` is the
DID the signed metadata named. The wallet stores it and says so:

``` { .http title="POST /notification, the credential stored" data-format="HTTP" }
POST /notification HTTP/1.1
Host: issuer.bkn.go.id
Content-Type: application/json
Authorization: DPoP ni_IZoW82gn6GQVQbDshjrWOj3XoRiVU-pfY_vzdd4w
DPoP: eyJ0eXAiOiJkcG9wK2p3dCIsImFsZyI6IkVTMjU2IiwiandrIjp7Imt0eSI6IkVDIiwiY3J2IjoiUC0yNTYiLCJ4IjoieHJDQXdRb3lfeEJpWFowaXBpdGNaQno3QXNsS2ZLVXBJWUMyQUVldkpXYyIsInkiOiJEWF8wZmtLUVRQQjUtY0txVmtVcF9GMXJCTE5KU3BOQlY5SWstWmJObWEwIn19.eyJqdGkiOiJEak9KQ1RGNnRhbWJ5cDlMSlNjUGNBIiwiaHRtIjoiUE9TVCIsImh0dSI6Imh0dHBzOi8vaXNzdWVyLmJrbi5nby5pZC9ub3RpZmljYXRpb24iLCJpYXQiOjE3OTIyMTY4MTIsIm5vbmNlIjoiRm1JdVVQUFFQZWt4RFprNGNFdmZlc0NMIiwiYXRoIjoicDg2aXB3ZjYxdzJvNVhIbHdWVUNBVEFYc3NQaXBLcUR0bFNvazJqMnU2NCJ9.dijyIEknpF2E9u7EZ0FQjfhxACVXIv_xwf_Iw2jAkbczYbBLG37_NU2W3fsJf5JbedWtNqPK7WJJy_d0tiWTBw

{
  "notification_id": "CMemYMX-3nU0WGfu",
  "event": "credential_accepted"
}
```

``` { .http title="204, the notification taken" data-format="HTTP" }
HTTP/1.1 204 No Content
DPoP-Nonce: 5IjZ8J3IQaL1HIuKDYGkOB9g
Cache-Control: no-store
```

The wallet then asks for the second credential identifier, the mdoc of the same
credential, in a request of the same form: a new nonce, a new Key Attestation
carrying it, and a new proof. Issuer Core gives the mdoc the claim values, the
credential key, the status entry, and the validity period of the SD-JWT VC.

Close to the credential's `exp`, the wallet renews it with the refresh token.
The DPoP nonce it held has long expired, so the first attempt is answered
with a new one:

``` { .http title="400, the refresh token request asked for a DPoP nonce" data-format="HTTP" }
HTTP/1.1 400 Bad Request
DPoP-Nonce: xLMjVBt-mSmOv4Oz1_t9VCPq
Cache-Control: no-store
Content-Type: application/json

{
  "error": "use_dpop_nonce",
  "error_description": "Authorization server requires nonce in DPoP proof"
}
```

and the request is sent again, signed by the same DPoP key:

``` { .http title="POST /token, the refresh token" data-format="HTTP" }
POST /token HTTP/1.1
Host: issuer.bkn.go.id
Content-Type: application/x-www-form-urlencoded
DPoP: eyJ0eXAiOiJkcG9wK2p3dCIsImFsZyI6IkVTMjU2IiwiandrIjp7Imt0eSI6IkVDIiwiY3J2IjoiUC0yNTYiLCJ4IjoieHJDQXdRb3lfeEJpWFowaXBpdGNaQno3QXNsS2ZLVXBJWUMyQUVldkpXYyIsInkiOiJEWF8wZmtLUVRQQjUtY0txVmtVcF9GMXJCTE5KU3BOQlY5SWstWmJObWEwIn19.eyJqdGkiOiJXcFNIS01fRHVuU1NLaUhwNlluQ2dBIiwiaHRtIjoiUE9TVCIsImh0dSI6Imh0dHBzOi8vaXNzdWVyLmJrbi5nby5pZC90b2tlbiIsImlhdCI6MTgyMTQyMDAwMCwibm9uY2UiOiJ4TE1qVkJ0LW1TbU92NE96MV90OVZDUHEifQ.7y4S9TcNVAHeOcqHHIC8vfX-Vi65qSpqsldDzvxZp2N8hDgsg3BqpBW64cNKMMR5dqbcsTK92PdPqeZvrmEB2Q

grant_type=refresh_token&refresh_token=EgFeS5xiitMMzdR3HQP-2F9koJeCL1t-s8kPozZedzU
```

``` { .http title="200, a new access token for renewal" data-format="HTTP" }
HTTP/1.1 200 OK
DPoP-Nonce: 1oyChAvOX2-W17uOkhQHXNxE
Cache-Control: no-store
Content-Type: application/json

{
  "access_token": "vvXTdxI-880foVorXZLZqfLW1Xs5SYuD8jkQwEd3DBk",
  "token_type": "DPoP",
  "expires_in": 300,
  "authorization_details": [
    {
      "type": "openid_credential",
      "credential_configuration_id": "id.idctf.kartu-asn.1:sd-jwt-vc",
      "credential_identifiers": [
        "asn-jb0YglbvHGNb"
      ]
    },
    {
      "type": "openid_credential",
      "credential_configuration_id": "id.idctf.kartu-asn.1:mdoc",
      "credential_identifiers": [
        "asn-Kr-gBP15sIJO"
      ]
    }
  ]
}
```

and runs the credential requests again, each with a new nonce and a new
Key Attestation sent as the `attestation` proof.

### The KTP Digital, through the Authorization Code flow {#ts-1-01-the-ktp-digital-through-the-authorization-code-flow}

The Direktorat Jenderal Kependudukan dan Pencatatan Sipil (Dukcapil) issues
the KTP Digital, a type whose Credential Rulebook names mdoc
alone and sets `min_assurance` to `high`. Its offer travels by reference, so
the QR code stays small:

``` { .text title="A credential offer by reference, as the QR code carries it" data-format="URI" }
openid-credential-offer://?credential_offer_uri=https%3A%2F%2Fissuer.dukcapil.go.id%2Foffer%2F5OHndM4_wEq3K1Y4
```

``` { .http title="GET the credential offer" data-format="HTTP" }
GET /offer/5OHndM4_wEq3K1Y4 HTTP/1.1
Host: issuer.dukcapil.go.id
Accept: application/json
```

``` { .http title="200, the credential offer" data-format="HTTP" }
HTTP/1.1 200 OK
Cache-Control: no-store
Content-Type: application/json

{
  "credential_issuer": "https://issuer.dukcapil.go.id",
  "credential_configuration_ids": [
    "id.idctf.ktp.1:mdoc"
  ],
  "grants": {
    "authorization_code": {
      "issuer_state": "VUp0BI5QAzIzYeRILtoC7TTq"
    }
  }
}
```

Dukcapil's signed metadata announces the one configuration, and at `high` it
accepts the `attestation` proof type alone:

``` { .http title="200, Dukcapil's signed issuer metadata" data-format="HTTP" }
HTTP/1.1 200 OK
Content-Type: application/jwt

eyJ0eXAiOiJvcGVuaWR2Y2ktaXNzdWVyLW1ldGFkYXRhK2p3dCIsImFsZyI6IkVTMjU2Iiwia2lkIjoiZGlkOndlYnZoOlFtY0VWVDJpSlNyc3M1aGd3aU1Gc01VeEtrUm96Z0ZGNDU4UmNnZ1Q0TUYyTDQ6ZHVrY2FwaWwuZ28uaWQjaXNzdWFuY2Utam9zZS0yIn0.eyJpc3MiOiJkaWQ6d2Vidmg6UW1jRVZUMmlKU3JzczVoZ3dpTUZzTVV4S2tSb3pnRkY0NThSY2dnVDRNRjJMNDpkdWtjYXBpbC5nby5pZCIsInN1YiI6Imh0dHBzOi8vaXNzdWVyLmR1a2NhcGlsLmdvLmlkIiwiaWF0IjoxNzkyMTk1MjAwLCJjcmVkZW50aWFsX2lzc3VlciI6Imh0dHBzOi8vaXNzdWVyLmR1a2NhcGlsLmdvLmlkIiwiY3JlZGVudGlhbF9lbmRwb2ludCI6Imh0dHBzOi8vaXNzdWVyLmR1a2NhcGlsLmdvLmlkL2NyZWRlbnRpYWwiLCJub25jZV9lbmRwb2ludCI6Imh0dHBzOi8vaXNzdWVyLmR1a2NhcGlsLmdvLmlkL25vbmNlIiwiZGVmZXJyZWRfY3JlZGVudGlhbF9lbmRwb2ludCI6Imh0dHBzOi8vaXNzdWVyLmR1a2NhcGlsLmdvLmlkL2RlZmVycmVkX2NyZWRlbnRpYWwiLCJub3RpZmljYXRpb25fZW5kcG9pbnQiOiJodHRwczovL2lzc3Vlci5kdWtjYXBpbC5nby5pZC9ub3RpZmljYXRpb24iLCJjcmVkZW50aWFsX2NvbmZpZ3VyYXRpb25zX3N1cHBvcnRlZCI6eyJpZC5pZGN0Zi5rdHAuMTptZG9jIjp7ImZvcm1hdCI6Im1zb19tZG9jIiwiZG9jdHlwZSI6ImlkLmlkY3RmLmt0cC4xIiwiY3J5cHRvZ3JhcGhpY19iaW5kaW5nX21ldGhvZHNfc3VwcG9ydGVkIjpbImNvc2Vfa2V5Il0sImNyZWRlbnRpYWxfc2lnbmluZ19hbGdfdmFsdWVzX3N1cHBvcnRlZCI6Wy03XSwicHJvb2ZfdHlwZXNfc3VwcG9ydGVkIjp7ImF0dGVzdGF0aW9uIjp7InByb29mX3NpZ25pbmdfYWxnX3ZhbHVlc19zdXBwb3J0ZWQiOlsiRVMyNTYiXSwia2V5X2F0dGVzdGF0aW9uc19yZXF1aXJlZCI6eyJrZXlfc3RvcmFnZSI6WyJpc29fMTgwNDVfaGlnaCJdLCJ1c2VyX2F1dGhlbnRpY2F0aW9uIjpbImlzb18xODA0NV9tb2RlcmF0ZSIsImlzb18xODA0NV9oaWdoIl19fX0sImNyZWRlbnRpYWxfbWV0YWRhdGEiOnsiZGlzcGxheSI6W3sibmFtZSI6IktUUCBEaWdpdGFsIiwibG9jYWxlIjoiaWQiLCJkZXNjcmlwdGlvbiI6IkthcnR1IFRhbmRhIFBlbmR1ZHVrIGRpZ2l0YWwiLCJsb2dvIjp7InVyaSI6Imh0dHBzOi8vY2F0YWxvZy50cnVzdC5nby5pZC90eXBlLW1ldGFkYXRhL2t0cC12MS9sb2dvLnBuZyIsImFsdF90ZXh0IjoiTGFtYmFuZyBHYXJ1ZGEgUGFuY2FzaWxhIn0sImJhY2tncm91bmRfY29sb3IiOiIjRERFQkZBIiwidGV4dF9jb2xvciI6IiMwQjFGM0EifSx7Im5hbWUiOiJEaWdpdGFsIElkZW50aXR5IENhcmQiLCJsb2NhbGUiOiJlbiIsImRlc2NyaXB0aW9uIjoiSW5kb25lc2lhbiByZXNpZGVudCBpZGVudGl0eSBjYXJkIiwibG9nbyI6eyJ1cmkiOiJodHRwczovL2NhdGFsb2cudHJ1c3QuZ28uaWQvdHlwZS1tZXRhZGF0YS9rdHAtdjEvbG9nby5wbmciLCJhbHRfdGV4dCI6IkdhcnVkYSBQYW5jYXNpbGEgZW1ibGVtIn0sImJhY2tncm91bmRfY29sb3IiOiIjRERFQkZBIiwidGV4dF9jb2xvciI6IiMwQjFGM0EifV0sImNsYWltcyI6W3sicGF0aCI6WyJpZC5pZGN0Zi5rdHAuMSIsIm5payJdLCJkaXNwbGF5IjpbeyJuYW1lIjoiTklLIiwibG9jYWxlIjoiaWQifSx7Im5hbWUiOiJQb3B1bGF0aW9uIElkZW50aWZpY2F0aW9uIE51bWJlciIsImxvY2FsZSI6ImVuIn1dfSx7InBhdGgiOlsiaWQuaWRjdGYua3RwLjEiLCJuYW1hIl0sImRpc3BsYXkiOlt7Im5hbWUiOiJOYW1hIiwibG9jYWxlIjoiaWQifSx7Im5hbWUiOiJOYW1lIiwibG9jYWxlIjoiZW4ifV19LHsicGF0aCI6WyJpZC5pZGN0Zi5rdHAuMSIsInRlbXBhdF9sYWhpciJdLCJkaXNwbGF5IjpbeyJuYW1lIjoiVGVtcGF0IExhaGlyIiwibG9jYWxlIjoiaWQifSx7Im5hbWUiOiJQbGFjZSBvZiBCaXJ0aCIsImxvY2FsZSI6ImVuIn1dfSx7InBhdGgiOlsiaWQuaWRjdGYua3RwLjEiLCJ0YW5nZ2FsX2xhaGlyIl0sImRpc3BsYXkiOlt7Im5hbWUiOiJUYW5nZ2FsIExhaGlyIiwibG9jYWxlIjoiaWQifSx7Im5hbWUiOiJEYXRlIG9mIEJpcnRoIiwibG9jYWxlIjoiZW4ifV19LHsicGF0aCI6WyJpZC5pZGN0Zi5rdHAuMSIsInVzaWFfZGlfYXRhc18xNyJdLCJkaXNwbGF5IjpbeyJuYW1lIjoiQmVydXNpYSAxNyBUYWh1biBrZSBBdGFzIiwibG9jYWxlIjoiaWQifSx7Im5hbWUiOiJBZ2VkIDE3IG9yIE92ZXIiLCJsb2NhbGUiOiJlbiJ9XX0seyJwYXRoIjpbImlkLmlkY3RmLmt0cC4xIiwiamVuaXNfa2VsYW1pbiJdLCJkaXNwbGF5IjpbeyJuYW1lIjoiSmVuaXMgS2VsYW1pbiIsImxvY2FsZSI6ImlkIn0seyJuYW1lIjoiU2V4IiwibG9jYWxlIjoiZW4ifV19LHsicGF0aCI6WyJpZC5pZGN0Zi5rdHAuMSIsImdvbG9uZ2FuX2RhcmFoIl0sImRpc3BsYXkiOlt7Im5hbWUiOiJHb2xvbmdhbiBEYXJhaCIsImxvY2FsZSI6ImlkIn0seyJuYW1lIjoiQmxvb2QgVHlwZSIsImxvY2FsZSI6ImVuIn1dfSx7InBhdGgiOlsiaWQuaWRjdGYua3RwLjEiLCJhbGFtYXQiXSwiZGlzcGxheSI6W3sibmFtZSI6IkFsYW1hdCIsImxvY2FsZSI6ImlkIn0seyJuYW1lIjoiQWRkcmVzcyIsImxvY2FsZSI6ImVuIn1dfSx7InBhdGgiOlsiaWQuaWRjdGYua3RwLjEiLCJydF9ydyJdLCJkaXNwbGF5IjpbeyJuYW1lIjoiUlQvUlciLCJsb2NhbGUiOiJpZCJ9LHsibmFtZSI6Ik5laWdoYm9yaG9vZCBVbml0IiwibG9jYWxlIjoiZW4ifV19LHsicGF0aCI6WyJpZC5pZGN0Zi5rdHAuMSIsImtlbHVyYWhhbl9kZXNhIl0sImRpc3BsYXkiOlt7Im5hbWUiOiJLZWx1cmFoYW4vRGVzYSIsImxvY2FsZSI6ImlkIn0seyJuYW1lIjoiVXJiYW4gVmlsbGFnZS9WaWxsYWdlIiwibG9jYWxlIjoiZW4ifV19LHsicGF0aCI6WyJpZC5pZGN0Zi5rdHAuMSIsImtlY2FtYXRhbiJdLCJkaXNwbGF5IjpbeyJuYW1lIjoiS2VjYW1hdGFuIiwibG9jYWxlIjoiaWQifSx7Im5hbWUiOiJEaXN0cmljdCIsImxvY2FsZSI6ImVuIn1dfSx7InBhdGgiOlsiaWQuaWRjdGYua3RwLjEiLCJrYWJ1cGF0ZW5fa290YSJdLCJkaXNwbGF5IjpbeyJuYW1lIjoiS2FidXBhdGVuL0tvdGEiLCJsb2NhbGUiOiJpZCJ9LHsibmFtZSI6IlJlZ2VuY3kvQ2l0eSIsImxvY2FsZSI6ImVuIn1dfSx7InBhdGgiOlsiaWQuaWRjdGYua3RwLjEiLCJwcm92aW5zaSJdLCJkaXNwbGF5IjpbeyJuYW1lIjoiUHJvdmluc2kiLCJsb2NhbGUiOiJpZCJ9LHsibmFtZSI6IlByb3ZpbmNlIiwibG9jYWxlIjoiZW4ifV19LHsicGF0aCI6WyJpZC5pZGN0Zi5rdHAuMSIsImFnYW1hIl0sImRpc3BsYXkiOlt7Im5hbWUiOiJBZ2FtYSIsImxvY2FsZSI6ImlkIn0seyJuYW1lIjoiUmVsaWdpb24iLCJsb2NhbGUiOiJlbiJ9XX0seyJwYXRoIjpbImlkLmlkY3RmLmt0cC4xIiwic3RhdHVzX3Blcmthd2luYW4iXSwiZGlzcGxheSI6W3sibmFtZSI6IlN0YXR1cyBQZXJrYXdpbmFuIiwibG9jYWxlIjoiaWQifSx7Im5hbWUiOiJNYXJpdGFsIFN0YXR1cyIsImxvY2FsZSI6ImVuIn1dfSx7InBhdGgiOlsiaWQuaWRjdGYua3RwLjEiLCJwZWtlcmphYW4iXSwiZGlzcGxheSI6W3sibmFtZSI6IlBla2VyamFhbiIsImxvY2FsZSI6ImlkIn0seyJuYW1lIjoiT2NjdXBhdGlvbiIsImxvY2FsZSI6ImVuIn1dfSx7InBhdGgiOlsiaWQuaWRjdGYua3RwLjEiLCJrZXdhcmdhbmVnYXJhYW4iXSwiZGlzcGxheSI6W3sibmFtZSI6Iktld2FyZ2FuZWdhcmFhbiIsImxvY2FsZSI6ImlkIn0seyJuYW1lIjoiQ2l0aXplbnNoaXAiLCJsb2NhbGUiOiJlbiJ9XX0seyJwYXRoIjpbImlkLmlkY3RmLmt0cC4xIiwidGVtcGF0X2Rpa2VsdWFya2FuIl0sImRpc3BsYXkiOlt7Im5hbWUiOiJUZW1wYXQgRGlrZWx1YXJrYW4iLCJsb2NhbGUiOiJpZCJ9LHsibmFtZSI6IlBsYWNlIG9mIElzc3VhbmNlIiwibG9jYWxlIjoiZW4ifV19LHsicGF0aCI6WyJpZC5pZGN0Zi5rdHAuMSIsImlzc3VhbmNlX2RhdGUiXSwiZGlzcGxheSI6W3sibmFtZSI6IlRhbmdnYWwgRGlrZWx1YXJrYW4iLCJsb2NhbGUiOiJpZCJ9LHsibmFtZSI6IkRhdGUgb2YgSXNzdWFuY2UiLCJsb2NhbGUiOiJlbiJ9XX0seyJwYXRoIjpbImlkLmlkY3RmLmt0cC4xIiwiZm90byJdLCJkaXNwbGF5IjpbeyJuYW1lIjoiRm90byIsImxvY2FsZSI6ImlkIn0seyJuYW1lIjoiUGhvdG8iLCJsb2NhbGUiOiJlbiJ9XX1dfX19fQ.6oyNrd2H1aulyOVL4wE2HyCvLzRG_ZeLkj2vWT6NjtM6eFQia946pHNPRUre1P4MiTonGxZ1FVrlDp_jEZ8M4A
```

``` { .json title="Dukcapil's issuer metadata claims" data-format="JSON" }
{
  "iss": "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id",
  "sub": "https://issuer.dukcapil.go.id",
  "iat": 1792195200,
  "credential_issuer": "https://issuer.dukcapil.go.id",
  "credential_endpoint": "https://issuer.dukcapil.go.id/credential",
  "nonce_endpoint": "https://issuer.dukcapil.go.id/nonce",
  "deferred_credential_endpoint": "https://issuer.dukcapil.go.id/deferred_credential",
  "notification_endpoint": "https://issuer.dukcapil.go.id/notification",
  "credential_configurations_supported": {
    "id.idctf.ktp.1:mdoc": {
      "format": "mso_mdoc",
      "doctype": "id.idctf.ktp.1",
      "cryptographic_binding_methods_supported": [
        "cose_key"
      ],
      "credential_signing_alg_values_supported": [
        -7
      ],
      "proof_types_supported": {
        "attestation": {
          "proof_signing_alg_values_supported": [
            "ES256"
          ],
          "key_attestations_required": {
            "key_storage": [
              "iso_18045_high"
            ],
            "user_authentication": [
              "iso_18045_moderate",
              "iso_18045_high"
            ]
          }
        }
      },
      "credential_metadata": {
        "display": [
          {
            "name": "KTP Digital",
            "locale": "id",
            "description": "Kartu Tanda Penduduk digital",
            "logo": {
              "uri": "https://catalog.trust.go.id/type-metadata/ktp-v1/logo.png",
              "alt_text": "Lambang Garuda Pancasila"
            },
            "background_color": "#DDEBFA",
            "text_color": "#0B1F3A"
          },
          {
            "name": "Digital Identity Card",
            "locale": "en",
            "description": "Indonesian resident identity card",
            "logo": {
              "uri": "https://catalog.trust.go.id/type-metadata/ktp-v1/logo.png",
              "alt_text": "Garuda Pancasila emblem"
            },
            "background_color": "#DDEBFA",
            "text_color": "#0B1F3A"
          }
        ],
        "claims": [
          {
            "path": [
              "id.idctf.ktp.1",
              "nik"
            ],
            "display": [
              {
                "name": "NIK",
                "locale": "id"
              },
              {
                "name": "Population Identification Number",
                "locale": "en"
              }
            ]
          },
          {
            "path": [
              "id.idctf.ktp.1",
              "nama"
            ],
            "display": [
              {
                "name": "Nama",
                "locale": "id"
              },
              {
                "name": "Name",
                "locale": "en"
              }
            ]
          },
          {
            "path": [
              "id.idctf.ktp.1",
              "tempat_lahir"
            ],
            "display": [
              {
                "name": "Tempat Lahir",
                "locale": "id"
              },
              {
                "name": "Place of Birth",
                "locale": "en"
              }
            ]
          },
          {
            "path": [
              "id.idctf.ktp.1",
              "tanggal_lahir"
            ],
            "display": [
              {
                "name": "Tanggal Lahir",
                "locale": "id"
              },
              {
                "name": "Date of Birth",
                "locale": "en"
              }
            ]
          },
          {
            "path": [
              "id.idctf.ktp.1",
              "usia_di_atas_17"
            ],
            "display": [
              {
                "name": "Berusia 17 Tahun ke Atas",
                "locale": "id"
              },
              {
                "name": "Aged 17 or Over",
                "locale": "en"
              }
            ]
          },
          {
            "path": [
              "id.idctf.ktp.1",
              "jenis_kelamin"
            ],
            "display": [
              {
                "name": "Jenis Kelamin",
                "locale": "id"
              },
              {
                "name": "Sex",
                "locale": "en"
              }
            ]
          },
          {
            "path": [
              "id.idctf.ktp.1",
              "golongan_darah"
            ],
            "display": [
              {
                "name": "Golongan Darah",
                "locale": "id"
              },
              {
                "name": "Blood Type",
                "locale": "en"
              }
            ]
          },
          {
            "path": [
              "id.idctf.ktp.1",
              "alamat"
            ],
            "display": [
              {
                "name": "Alamat",
                "locale": "id"
              },
              {
                "name": "Address",
                "locale": "en"
              }
            ]
          },
          {
            "path": [
              "id.idctf.ktp.1",
              "rt_rw"
            ],
            "display": [
              {
                "name": "RT/RW",
                "locale": "id"
              },
              {
                "name": "Neighborhood Unit",
                "locale": "en"
              }
            ]
          },
          {
            "path": [
              "id.idctf.ktp.1",
              "kelurahan_desa"
            ],
            "display": [
              {
                "name": "Kelurahan/Desa",
                "locale": "id"
              },
              {
                "name": "Urban Village/Village",
                "locale": "en"
              }
            ]
          },
          {
            "path": [
              "id.idctf.ktp.1",
              "kecamatan"
            ],
            "display": [
              {
                "name": "Kecamatan",
                "locale": "id"
              },
              {
                "name": "District",
                "locale": "en"
              }
            ]
          },
          {
            "path": [
              "id.idctf.ktp.1",
              "kabupaten_kota"
            ],
            "display": [
              {
                "name": "Kabupaten/Kota",
                "locale": "id"
              },
              {
                "name": "Regency/City",
                "locale": "en"
              }
            ]
          },
          {
            "path": [
              "id.idctf.ktp.1",
              "provinsi"
            ],
            "display": [
              {
                "name": "Provinsi",
                "locale": "id"
              },
              {
                "name": "Province",
                "locale": "en"
              }
            ]
          },
          {
            "path": [
              "id.idctf.ktp.1",
              "agama"
            ],
            "display": [
              {
                "name": "Agama",
                "locale": "id"
              },
              {
                "name": "Religion",
                "locale": "en"
              }
            ]
          },
          {
            "path": [
              "id.idctf.ktp.1",
              "status_perkawinan"
            ],
            "display": [
              {
                "name": "Status Perkawinan",
                "locale": "id"
              },
              {
                "name": "Marital Status",
                "locale": "en"
              }
            ]
          },
          {
            "path": [
              "id.idctf.ktp.1",
              "pekerjaan"
            ],
            "display": [
              {
                "name": "Pekerjaan",
                "locale": "id"
              },
              {
                "name": "Occupation",
                "locale": "en"
              }
            ]
          },
          {
            "path": [
              "id.idctf.ktp.1",
              "kewarganegaraan"
            ],
            "display": [
              {
                "name": "Kewarganegaraan",
                "locale": "id"
              },
              {
                "name": "Citizenship",
                "locale": "en"
              }
            ]
          },
          {
            "path": [
              "id.idctf.ktp.1",
              "tempat_dikeluarkan"
            ],
            "display": [
              {
                "name": "Tempat Dikeluarkan",
                "locale": "id"
              },
              {
                "name": "Place of Issuance",
                "locale": "en"
              }
            ]
          },
          {
            "path": [
              "id.idctf.ktp.1",
              "issuance_date"
            ],
            "display": [
              {
                "name": "Tanggal Dikeluarkan",
                "locale": "id"
              },
              {
                "name": "Date of Issuance",
                "locale": "en"
              }
            ]
          },
          {
            "path": [
              "id.idctf.ktp.1",
              "foto"
            ],
            "display": [
              {
                "name": "Foto",
                "locale": "id"
              },
              {
                "name": "Photo",
                "locale": "en"
              }
            ]
          }
        ]
      }
    }
  }
}
```

The wallet pushes its authorization request. Its first attempt carries no
DPoP nonce, and Dukcapil answers the way BKN's token endpoint did in
[the Kartu ASN exchange][ts-1-01-the-kartu-asn-through-the-pre-authorized-code-flow]:

``` { .http title="400, the pushed authorization request asked for a DPoP nonce" data-format="HTTP" }
HTTP/1.1 400 Bad Request
DPoP-Nonce: 3arJkPcL6HoSItjXnwm96C5b
Cache-Control: no-store
Content-Type: application/json

{
  "error": "use_dpop_nonce",
  "error_description": "Authorization server requires nonce in DPoP proof"
}
```

The second attempt carries that nonce, and its DPoP proof binds the
authorization code to the DPoP key:

``` { .http title="POST /par, the pushed authorization request" data-format="HTTP" }
POST /par HTTP/1.1
Host: issuer.dukcapil.go.id
Content-Type: application/x-www-form-urlencoded
DPoP: eyJ0eXAiOiJkcG9wK2p3dCIsImFsZyI6IkVTMjU2IiwiandrIjp7Imt0eSI6IkVDIiwiY3J2IjoiUC0yNTYiLCJ4IjoiRm5XVm9nZnpLem1HX1lPQ21FY2VoSnZaVFM0YlJ6Z21qeXBNMjRCUVoycyIsInkiOiJIN2l5RGpRMGR3U25OOExKZUtXRmlRcHdCLVBJYWVtaldNWmsySXZ3RndNIn19.eyJqdGkiOiIzTXZmeVU0QmpBNUxDVzEtZzctanJRIiwiaHRtIjoiUE9TVCIsImh0dSI6Imh0dHBzOi8vaXNzdWVyLmR1a2NhcGlsLmdvLmlkL3BhciIsImlhdCI6MTc5MjIxNjY4MCwibm9uY2UiOiIzYXJKa1BjTDZIb1NJdGpYbndtOTZDNWIifQ.yZK8P_e6NDWDW0P1VfBOw4Nkg4kSqN8ZOyjdYLQ_lgT-OnIakWTXy-d2b2pegMeg8XO4gG8Txgpaq8blg4gZiw

response_type=code&client_id=id.wallet&redirect_uri=https%3A%2F%2Fdompet.co.id%2Fwallet%2Fcb&state=NPWhJ5Ok_Y_lNX7w&code_challenge=1ZN5qntmoz0kzaFPzY1S7Sf7-uhuSmfWRd9S8j2XfSY&code_challenge_method=S256&authorization_details=%5B%7B%22type%22%3A%22openid_credential%22%2C%22credential_configuration_id%22%3A%22id.idctf.ktp.1%3Amdoc%22%7D%5D&issuer_state=VUp0BI5QAzIzYeRILtoC7TTq
```

``` { .json title="The DPoP proof of the pushed authorization request, decoded" data-format="JSON" }
{
  "header": {
    "typ": "dpop+jwt",
    "alg": "ES256",
    "jwk": {
      "kty": "EC",
      "crv": "P-256",
      "x": "FnWVogfzKzmG_YOCmEcehJvZTS4bRzgmjypM24BQZ2s",
      "y": "H7iyDjQ0dwSnN8LJeKWFiQpwB-PIaemjWMZk2IvwFwM"
    }
  },
  "payload": {
    "jti": "3MvfyU4BjA5LCW1-g7-jrQ",
    "htm": "POST",
    "htu": "https://issuer.dukcapil.go.id/par",
    "iat": 1792216680,
    "nonce": "3arJkPcL6HoSItjXnwm96C5b"
  }
}
```

``` { .http title="201, the request URI" data-format="HTTP" }
HTTP/1.1 201 Created
DPoP-Nonce: Lm4aQAcgS6XG9xSnXqayAfRb
Cache-Control: no-store
Content-Type: application/json

{
  "request_uri": "urn:ietf:params:oauth:request_uri:fM3E8PC4VL7qQCgC9IacmRer",
  "expires_in": 60
}
```

The wallet opens the authorization endpoint in the browser with the request
URI alone. The citizen signs in at Dukcapil, and the browser comes back to the
wallet with the code, the state, and the issuer that sent it:

``` { .text title="The authorization request the wallet opens" data-format="URI" }
https://issuer.dukcapil.go.id/authorize?client_id=id.wallet&request_uri=urn%3Aietf%3Aparams%3Aoauth%3Arequest_uri%3AfM3E8PC4VL7qQCgC9IacmRer
```

``` { .http title="303, back to the wallet with the code" data-format="HTTP" }
HTTP/1.1 303 See Other
Location: https://dompet.co.id/wallet/cb?code=FbUYKg77K-KSHfwtr0cu9xg1&state=NPWhJ5Ok_Y_lNX7w&iss=https%3A%2F%2Fissuer.dukcapil.go.id
Cache-Control: no-store
```

``` { .http title="POST /token, the authorization code" data-format="HTTP" }
POST /token HTTP/1.1
Host: issuer.dukcapil.go.id
Content-Type: application/x-www-form-urlencoded
DPoP: eyJ0eXAiOiJkcG9wK2p3dCIsImFsZyI6IkVTMjU2IiwiandrIjp7Imt0eSI6IkVDIiwiY3J2IjoiUC0yNTYiLCJ4IjoiRm5XVm9nZnpLem1HX1lPQ21FY2VoSnZaVFM0YlJ6Z21qeXBNMjRCUVoycyIsInkiOiJIN2l5RGpRMGR3U25OOExKZUtXRmlRcHdCLVBJYWVtaldNWmsySXZ3RndNIn19.eyJqdGkiOiJEekNnRE5objk5VmJNdXRWVndndUV3IiwiaHRtIjoiUE9TVCIsImh0dSI6Imh0dHBzOi8vaXNzdWVyLmR1a2NhcGlsLmdvLmlkL3Rva2VuIiwiaWF0IjoxNzkyMjE2NzQwLCJub25jZSI6IkxtNGFRQWNnUzZYRzl4U25YcWF5QWZSYiJ9.2uNYWQKfe48H0UqG8ycErSFa00uX9np1DRdGpVd4ZrYY-jJcTJV33BKo8DqQD6iZswenbvuKy8nXL4XbaGlqgg

grant_type=authorization_code&code=FbUYKg77K-KSHfwtr0cu9xg1&code_verifier=K2TweqCNe2OXhlDw2MyLu3p75hj6eB2LCHL2mvO4C1M&redirect_uri=https%3A%2F%2Fdompet.co.id%2Fwallet%2Fcb&client_id=id.wallet
```

``` { .http title="200, the access token after an authorization code" data-format="HTTP" }
HTTP/1.1 200 OK
DPoP-Nonce: Gc-C1CcfLdwj0swK9vyflPPz
Cache-Control: no-store
Content-Type: application/json

{
  "access_token": "WpTmPmsFknmKmrZe3PrHdu4ulfxtCsKHcRQzGY8yjuE",
  "token_type": "DPoP",
  "expires_in": 300,
  "refresh_token": "pCxSU86PMpd3LhVyYpm_c6_rLDSoXCXKGZVAJEcPFr8",
  "authorization_details": [
    {
      "type": "openid_credential",
      "credential_configuration_id": "id.idctf.ktp.1:mdoc",
      "credential_identifiers": [
        "ktp-j8rgoQh6XyyU"
      ]
    }
  ]
}
```

The wallet fetches a nonce from Dukcapil's Nonce Endpoint, the way it did at
BKN. The answer also carries the DPoP nonce the credential request will use:

``` { .http title="200, Dukcapil's c_nonce" data-format="HTTP" }
HTTP/1.1 200 OK
DPoP-Nonce: qOfWnWfZ2H7DztJCKvGMYbpQ
Cache-Control: no-store
Content-Type: application/json

{
  "c_nonce": "puumixknia5A"
}
```

Its Wallet Backend Service writes the `c_nonce` into a new Key Attestation:

``` { .json title="The Key Attestation for Dukcapil's nonce, decoded" data-format="JSON" }
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
  "nonce": "puumixknia5A",
  "iat": 1792216750,
  "exp": 1792303150
}
```

At `high` the attestation is the proof itself:

``` { .http title="POST /credential, the KTP Digital with an attestation proof" data-format="HTTP" }
POST /credential HTTP/1.1
Host: issuer.dukcapil.go.id
Content-Type: application/json
Authorization: DPoP WpTmPmsFknmKmrZe3PrHdu4ulfxtCsKHcRQzGY8yjuE
DPoP: eyJ0eXAiOiJkcG9wK2p3dCIsImFsZyI6IkVTMjU2IiwiandrIjp7Imt0eSI6IkVDIiwiY3J2IjoiUC0yNTYiLCJ4IjoiRm5XVm9nZnpLem1HX1lPQ21FY2VoSnZaVFM0YlJ6Z21qeXBNMjRCUVoycyIsInkiOiJIN2l5RGpRMGR3U25OOExKZUtXRmlRcHdCLVBJYWVtaldNWmsySXZ3RndNIn19.eyJqdGkiOiJVbEdzRnlzbkh5U2tHcDVqOWVQcUtBIiwiaHRtIjoiUE9TVCIsImh0dSI6Imh0dHBzOi8vaXNzdWVyLmR1a2NhcGlsLmdvLmlkL2NyZWRlbnRpYWwiLCJpYXQiOjE3OTIyMTY3NTUsIm5vbmNlIjoicU9mV25XZloySDdEenRKQ0t2R01ZYnBRIiwiYXRoIjoianVwMmtmVEhFclVwQnNocWVYVGNZWEtSMFpBZ3ltWjM5LUtMLVpQSU5pdyJ9.FF4jkeO9pbHIdb16HTcbxzn78wwTxtkLWpwngPvz_DpA-RYM8cYSKz312TXSjEIpkZ_YqC9iJNQgTD5-hAdIow

{
  "credential_identifier": "ktp-j8rgoQh6XyyU",
  "proofs": {
    "attestation": [
      "eyJ0eXAiOiJrZXktYXR0ZXN0YXRpb24rand0IiwiYWxnIjoiRVMyNTYiLCJraWQiOiJkaWQ6d2Vidmg6UW1lVFcxMzRxalVDNkVLWFU2SkwzZFZSZ2QzZlltVXBNYm9vRURva1NwRkVBSDpkb21wZXQuY28uaWQja2V5LWF0dGVzdGF0aW9uLTEifQ.eyJpc3MiOiJkaWQ6d2Vidmg6UW1lVFcxMzRxalVDNkVLWFU2SkwzZFZSZ2QzZlltVXBNYm9vRURva1NwRkVBSDpkb21wZXQuY28uaWQiLCJhdHRlc3RlZF9rZXlzIjpbeyJrdHkiOiJFQyIsImNydiI6IlAtMjU2IiwieCI6IjNDT2h4T2VPeHBCT2pVSmdxV1NBVTBRQUFZYVlndWdQVkpfMlgycUdka2MiLCJ5IjoiMms5ODg1NHBCNzd1ZGRSdmU4TzRrZzVuSVBUN0VqRWdwYmVLcVdMdU1FRSJ9XSwia2V5X3N0b3JhZ2UiOlsiaXNvXzE4MDQ1X2hpZ2giXSwidXNlcl9hdXRoZW50aWNhdGlvbiI6WyJpc29fMTgwNDVfbW9kZXJhdGUiXSwiY2VydGlmaWNhdGlvbiI6Imh0dHBzOi8vZG9tcGV0LmNvLmlkL2NlcnRpZmljYXRpb24vc2UtMjAyNi1hIiwibm9uY2UiOiJwdXVtaXhrbmlhNUEiLCJpYXQiOjE3OTIyMTY3NTAsImV4cCI6MTc5MjMwMzE1MH0.ZrVqqTXkABk-YDxAz1FP-p8MdEXRgg_HQ6xoHy-g3M-NqJ2pKeAWBHZ7snmDG-4QZE_WI7Bvb86ybtN06oBAFA"
    ]
  }
}
```

Dukcapil's source system does not answer in time, so Issuer Core defers:

``` { .http title="202, the KTP Digital deferred" data-format="HTTP" }
HTTP/1.1 202 Accepted
DPoP-Nonce: iWGWloMMrXZK-xEWfuyzLHug
Cache-Control: no-store
Content-Type: application/json

{
  "transaction_id": "QicBL_TslEJHsBAIeYHh",
  "interval": 30
}
```

After the interval the wallet asks again, and the credential is ready. The
`credential` is the `IssuerSigned` structure
[Issuing a credential in SD-JWT VC, mdoc, and `ldp_vc`](issuing-a-credential-in-sd-jwt-vc-mdoc-and-ldp-vc.md)
shows, encoded in base64url:

``` { .http title="POST /deferred_credential" data-format="HTTP" }
POST /deferred_credential HTTP/1.1
Host: issuer.dukcapil.go.id
Content-Type: application/json
Authorization: DPoP WpTmPmsFknmKmrZe3PrHdu4ulfxtCsKHcRQzGY8yjuE
DPoP: eyJ0eXAiOiJkcG9wK2p3dCIsImFsZyI6IkVTMjU2IiwiandrIjp7Imt0eSI6IkVDIiwiY3J2IjoiUC0yNTYiLCJ4IjoiRm5XVm9nZnpLem1HX1lPQ21FY2VoSnZaVFM0YlJ6Z21qeXBNMjRCUVoycyIsInkiOiJIN2l5RGpRMGR3U25OOExKZUtXRmlRcHdCLVBJYWVtaldNWmsySXZ3RndNIn19.eyJqdGkiOiIwY0tJZUVKeGhCWHdsTXhjYjBHeEhRIiwiaHRtIjoiUE9TVCIsImh0dSI6Imh0dHBzOi8vaXNzdWVyLmR1a2NhcGlsLmdvLmlkL2RlZmVycmVkX2NyZWRlbnRpYWwiLCJpYXQiOjE3OTIyMTY4MTUsIm5vbmNlIjoiaVdHV2xvTU1yWFpLLXhFV2Z1eXpMSHVnIiwiYXRoIjoianVwMmtmVEhFclVwQnNocWVYVGNZWEtSMFpBZ3ltWjM5LUtMLVpQSU5pdyJ9.EicbSUChl_XTYhqQI3RGOimEmd2txEZQHisytMvrtZvBIKGKVcEJwb323SsvqModqxxvT1VTZTXq0Jmnwf4rng

{
  "transaction_id": "QicBL_TslEJHsBAIeYHh"
}
```

``` { .http title="200, the KTP Digital as mdoc" data-format="HTTP" }
HTTP/1.1 200 OK
DPoP-Nonce: l6Jil1if5KXeDK6aWFvWgaRY
Cache-Control: no-store
Content-Type: application/json

{
  "credentials": [
    {
      "credential": "omppc3N1ZXJBdXRohEOhASahGCFZAq4wggKqMIICUKADAgECAgwWqYU0Ymposh0QwJswCgYIKoZIzj0EAwIwWTELMAkGA1UEBhMCSUQxKzApBgNVBAoMIlRydXN0IEF1dGhvcml0eSBSZXB1YmxpayBJbmRvbmVzaWExHTAbBgNVBAMMFElEQ1RGIElzc3VlciBSb290IENBMB4XDTI2MDkwMTAwMDAwMFoXDTI3MTEwMTAwMDAwMFowfDELMAkGA1UEBhMCSUQxPjA8BgNVBAoMNURpcmVrdG9yYXQgSmVuZGVyYWwgS2VwZW5kdWR1a2FuIGRhbiBQZW5jYXRhdGFuIFNpcGlsMS0wKwYDVQQDDCREdWtjYXBpbCBtZG9jIERvY3VtZW50IFNpZ25lciAyMDI2LUEwWTATBgcqhkjOPQIBBggqhkjOPQMBBwNCAATRhsxjZzfTQYgleuMwdOqLH0CjjjEna-m_VOgaJjRcowTH2K3wguu3sFAEF3jsDOGfFD5Adhl8AmozH1Mvp4Nko4HaMIHXMAwGA1UdEwEB_wQCMAAwDgYDVR0PAQH_BAQDAgeAMBUGA1UdJQEB_wQLMAkGByiBjF0FAQIwHwYDVR0jBBgwFoAU-_DVarC_2oBKMu3dM8zJ3dKDeZowHQYDVR0OBBYEFO6t0H5pXmpolQGI8s-S5sVmyajdMB4GA1UdEgQXMBWGE2h0dHBzOi8vdHJ1c3QuZ28uaWQwQAYDVR0fBDkwNzA1oDOgMYYvaHR0cHM6Ly9yZWdpc3RyeS50cnVzdC5nby5pZC9jcmwvaXNzdWVyLXJvb3QtY2EwCgYIKoZIzj0EAwIDSAAwRQIgHtrjtdrI2UwB3rxOjTBfPH46kHAdhyL8Vaooqb6QymkCIQDh8x42prKXMD46i8vgDTl9Rat19vl7IqDsxdNT3SvY71kEgtgYWQR9p2ZzdGF0dXOha3N0YXR1c19saXN0omNpZHgaAAdagGN1cml4I2h0dHBzOi8vZHVrY2FwaWwuZ28uaWQvc3RhdHVzL2t0cC03Z2RvY1R5cGVuaWQuaWRjdGYua3RwLjFndmVyc2lvbmMxLjBsdmFsaWRpdHlJbmZvo2ZzaWduZWTAdDIwMjYtMTAtMTdUMDY6MDA6MTBaaXZhbGlkRnJvbcB0MjAyNi0xMC0xN1QwNjowMDoxMFpqdmFsaWRVbnRpbMB0MjAyNy0wMS0xNVQwNjowMDoxMFpsdmFsdWVEaWdlc3RzoW5pZC5pZGN0Zi5rdHAuMbQaHq56ylgglp1rn4yqiIreuFEXBDUbRnxLFfGo0L90LXxLgcQcUtUaKhU7j1gg09WWPz6qq82ZNChwkbaY0BkdRWCycnBsZbysQYf99b0aMFFIxVggM_AyBg4weKuWtKdZZtFKihEWNgcVi2G14JB8KP_jHsQaPfABklggcSNKv-0z2sxHokBLOiftRtP6PpVigZXAqnWXNGo0MgMaPz5Iy1ggcjKoPRVKKYX9DtrUtgrUrxoSo_-eOu6YQzdToMpvD_caQoISnFggrZwmZgjXEdgAocyo847GavEpGzO6mZkCvQkjcxscYqAaSillfVgguYY1qMivedy9JkO9GrAq5pNrUQpPBuwWf7aX_0pqWtsaWinv_lgglWiELqriAykAOcxQflm18dbG-zSiZmLSxMchh2LFxs4aW8an01gg-0QemjjPENkYXlvO_dgpnzGFpYLcJaIijmdShJMyrjkaZRLzeVggRZ65LAV2CD798Hm8LNyqjKc7F6QD_4DXTrCU1ZgtcagaaeriNlgguIq7jtm6T8vC-a0jNyp9FKaW7fnybGUjQoom9Ce3HcQaalwXS1ggo_bbs3FX79uwABD5XOXmGvMFIAF-t-iuJpMCQrXKTKwabUu8AFgg0N5_pcfFZFhy8-TRMzImy57-k5jtQ5lDfdUlMFub6GkabkqHR1ggkJ5vM8maUFfFB-Ym-pPbGKqWbq95snEX72BA5FKKzYoacXQkXFgg4EIcestcbOhKTZ2PrFdc7Ey6PZNLVWDHXfYyoYfhjs0acYZOcVggrrQ5uqpk89xXvIGO6Sx7jMEObQq-H3vXpYR7AO1Rz6Qac2NIyVgg0NlbyKl05epN8sRtz_0ln75GzeqU86B_HFTY1EfCnyEaebwmTVggwoBTRjCxqMFjLR-cRIDnhBo1E16zY_K4v21BUx67F38aexNNO1ggoHX1WtvzJZiSbPWe-xICcKnU9eGZ29QuiFR6lQr-XwYafoGo1lggCmQWQ8PQW0CSkSprWxbbhPIAcxpd2kTRcxskacDNlgNtZGV2aWNlS2V5SW5mb6FpZGV2aWNlS2V5pAECIAEhWCDcI6HE547GkE6NQmCpZIBTRAABhpiC6A9Un_ZfaoZ2RyJYINpPfPOeKQe-7nXUb3vDuJIOZyD0-xIxIKW3iqli7jBBb2RpZ2VzdEFsZ29yaXRobWdTSEEtMjU2WEA0914c6PHYl9D3BEZ5vPzf68hwyMsXyOQxvSELk9t1Bz_hKtq6gRrVZB_iRQkqd9d_cxlnzEMbTTAcDZ6hty0Uam5hbWVTcGFjZXOhbmlkLmlkY3RmLmt0cC4xlNgYWFukZnJhbmRvbVCB9fIoGKg734OeRWXqRZBWaGRpZ2VzdElEGmpcF0tsZWxlbWVudFZhbHVlcDMxNzQwMTUyMDE5NTAwMDNxZWxlbWVudElkZW50aWZpZXJjbmlr2BhYXaRmcmFuZG9tUA27sHD0P-HcsxRbjPWC13ZoZGlnZXN0SUQac2NIyWxlbGVtZW50VmFsdWVxUmluYSBLYXJ0aWthIFNhcmlxZWxlbWVudElkZW50aWZpZXJkbmFtYdgYWFukZnJhbmRvbVBvbhHIYQ_strsUPD5WSQe4aGRpZ2VzdElEGm1LvABsZWxlbWVudFZhbHVlZ0pha2FydGFxZWxlbWVudElkZW50aWZpZXJsdGVtcGF0X2xhaGly2BhYYqRmcmFuZG9tUOFTNtonv8tVH96t3Rh0aWloZGlnZXN0SUQaWinv_mxlbGVtZW50VmFsdWXZA-xqMTk5NS0wMS0xMnFlbGVtZW50SWRlbnRpZmllcm10YW5nZ2FsX2xhaGly2BhYV6RmcmFuZG9tUOIt__dOiqA1F1tOKinol4loZGlnZXN0SUQacYZOcWxlbGVtZW50VmFsdWX1cWVsZW1lbnRJZGVudGlmaWVyb3VzaWFfZGlfYXRhc18xN9gYWF6kZnJhbmRvbVBxOsEMb0DUudJJya0snh-TaGRpZ2VzdElEGlvGp9NsZWxlbWVudFZhbHVlaVBFUkVNUFVBTnFlbGVtZW50SWRlbnRpZmllcm1qZW5pc19rZWxhbWlu2BhYV6RmcmFuZG9tUM4lJIejq1dn97XYWf03Cj5oZGlnZXN0SUQaPfABkmxlbGVtZW50VmFsdWVhQnFlbGVtZW50SWRlbnRpZmllcm5nb2xvbmdhbl9kYXJhaNgYWGSkZnJhbmRvbVB16MjXhKP4HR5fuLlspKsbaGRpZ2VzdElEGnm8Jk1sZWxlbWVudFZhbHVldkphbGFuIEtlbmFuZ2EgTm9tb3IgMTJxZWxlbWVudElkZW50aWZpZXJmYWxhbWF02BhYVKRmcmFuZG9tUCCDkS3Mg9EoIFmvZkucuP5oZGlnZXN0SUQaZRLzeWxlbGVtZW50VmFsdWVnMDA0LzAwN3FlbGVtZW50SWRlbnRpZmllcmVydF9yd9gYWGCkZnJhbmRvbVBqERe2ssIKCTI7ECDhQ4uqaGRpZ2VzdElEGh6uespsZWxlbWVudFZhbHVlakdvbmRhbmdkaWFxZWxlbWVudElkZW50aWZpZXJua2VsdXJhaGFuX2Rlc2HYGFhYpGZyYW5kb21Q95UcLmhKvpsR7_5Vi_euimhkaWdlc3RJRBpxdCRcbGVsZW1lbnRWYWx1ZWdNZW50ZW5ncWVsZW1lbnRJZGVudGlmaWVyaWtlY2FtYXRhbtgYWGOkZnJhbmRvbVDkn9cjxs9uRJIBpgIx96-eaGRpZ2VzdElEGkopZX1sZWxlbWVudFZhbHVlbUpha2FydGEgUHVzYXRxZWxlbWVudElkZW50aWZpZXJua2FidXBhdGVuX2tvdGHYGFhbpGZyYW5kb21QL4XrRHQIaYnoKXkRMclZqGhkaWdlc3RJRBoqFTuPbGVsZW1lbnRWYWx1ZWtES0kgSmFrYXJ0YXFlbGVtZW50SWRlbnRpZmllcmhwcm92aW5zadgYWFKkZnJhbmRvbVCZxhVMDEHDsWnT2eRkU3kmaGRpZ2VzdElEGj8-SMtsZWxlbWVudFZhbHVlZUlTTEFNcWVsZW1lbnRJZGVudGlmaWVyZWFnYW1h2BhYZKRmcmFuZG9tUHkocEknYBkqehxAQxY02IVoZGlnZXN0SUQaQoISnGxlbGVtZW50VmFsdWVrQkVMVU0gS0FXSU5xZWxlbWVudElkZW50aWZpZXJxc3RhdHVzX3Blcmthd2luYW7YGFhgpGZyYW5kb21QeRODE0JjVdAaahxgdS6c0WhkaWdlc3RJRBp-gajWbGVsZW1lbnRWYWx1ZW9LQVJZQVdBTiBTV0FTVEFxZWxlbWVudElkZW50aWZpZXJpcGVrZXJqYWFu2BhYWqRmcmFuZG9tUPlkZhHqoY6l9ZQjQ30mEQVoZGlnZXN0SUQaMFFIxWxlbGVtZW50VmFsdWVjV05JcWVsZW1lbnRJZGVudGlmaWVyb2tld2FyZ2FuZWdhcmFhbtgYWGekZnJhbmRvbVAyvvfdg23W7jsWizJ1Tf_saGRpZ2VzdElEGmnq4jZsZWxlbWVudFZhbHVlbUpBS0FSVEEgUFVTQVRxZWxlbWVudElkZW50aWZpZXJydGVtcGF0X2Rpa2VsdWFya2Fu2BhYYqRmcmFuZG9tUI9g1ELKduto7L6ktoRiRCNoZGlnZXN0SUQabkqHR2xlbGVtZW50VmFsdWXZA-xqMjAyMC0wMS0yOHFlbGVtZW50SWRlbnRpZmllcm1pc3N1YW5jZV9kYXRl2BhY7aRmcmFuZG9tUBfdQCrlUF1jY1_SOUTZrExoZGlnZXN0SUQaexNNO2xlbGVtZW50VmFsdWVYoP_Y_-AAEEpGSUYAAQEBAGAAYAAA_9sAQwAIBgYHBgUIBwcHCQkICgwUDQwLCwwZEhMPFB0aHx4dGhwcICQuJyAiLCMcHCg3KSwwMTQ0NB8nOT04MjwuMzQy_8AACwgAAQABAQERAP_EABQAAQAAAAAAAAAAAAAAAAAAAAn_xAAUEAEAAAAAAAAAAAAAAAAAAAAA_9oACAEBAAA_ACqf_9lxZWxlbWVudElkZW50aWZpZXJkZm90bw"
    }
  ],
  "notification_id": "vRDIbWKivcuZiTte"
}
```

### The Kartu Nikah, as `ldp_vc` {#ts-1-01-the-kartu-nikah-as-ldp-vc}

The Kementerian Agama (Kemenag) issues the Kartu Nikah as `ldp_vc` alone. Its configuration names the
contexts and types of the credential, and the credential comes back as a JSON
object rather than a string:

``` { .json title="The ldp_vc configuration in Kemenag's issuer metadata" data-format="JSON" }
{
  "credential_configurations_supported": {
    "id.idctf.kartu-nikah.1:ldp_vc": {
      "format": "ldp_vc",
      "credential_definition": {
        "@context": [
          "https://www.w3.org/ns/credentials/v2",
          "https://catalog.trust.go.id/type-metadata/kartu-nikah-v1/context.jsonld"
        ],
        "type": [
          "VerifiableCredential",
          "KartuNikah"
        ]
      },
      "cryptographic_binding_methods_supported": [
        "did:key"
      ],
      "credential_signing_alg_values_supported": [
        "ecdsa-rdfc-2019"
      ],
      "proof_types_supported": {
        "jwt": {
          "proof_signing_alg_values_supported": [
            "ES256"
          ],
          "key_attestations_required": {
            "key_storage": [
              "iso_18045_moderate",
              "iso_18045_high"
            ],
            "user_authentication": [
              "iso_18045_moderate",
              "iso_18045_high"
            ]
          }
        },
        "attestation": {
          "proof_signing_alg_values_supported": [
            "ES256"
          ],
          "key_attestations_required": {
            "key_storage": [
              "iso_18045_moderate",
              "iso_18045_high"
            ],
            "user_authentication": [
              "iso_18045_moderate",
              "iso_18045_high"
            ]
          }
        }
      },
      "credential_metadata": {
        "display": [
          {
            "name": "Kartu Nikah",
            "locale": "id",
            "description": "Kartu bukti pencatatan pernikahan",
            "logo": {
              "uri": "https://catalog.trust.go.id/type-metadata/kartu-nikah-v1/logo.png",
              "alt_text": "Logo Kementerian Agama"
            },
            "background_color": "#F4F9F2",
            "text_color": "#1B7A3E"
          },
          {
            "name": "Marriage Card",
            "locale": "en",
            "description": "Card recording a registered marriage",
            "logo": {
              "uri": "https://catalog.trust.go.id/type-metadata/kartu-nikah-v1/logo.png",
              "alt_text": "Ministry of Religious Affairs logo"
            },
            "background_color": "#F4F9F2",
            "text_color": "#1B7A3E"
          }
        ],
        "claims": [
          {
            "path": [
              "credentialSubject",
              "nama_suami"
            ],
            "display": [
              {
                "name": "Nama Suami",
                "locale": "id"
              },
              {
                "name": "Husband's Name",
                "locale": "en"
              }
            ]
          },
          {
            "path": [
              "credentialSubject",
              "nama_istri"
            ],
            "display": [
              {
                "name": "Nama Istri",
                "locale": "id"
              },
              {
                "name": "Wife's Name",
                "locale": "en"
              }
            ]
          },
          {
            "path": [
              "credentialSubject",
              "tanggal_akad"
            ],
            "display": [
              {
                "name": "Tanggal Akad Nikah",
                "locale": "id"
              },
              {
                "name": "Date of Marriage",
                "locale": "en"
              }
            ]
          },
          {
            "path": [
              "credentialSubject",
              "nomor_akta_nikah"
            ],
            "display": [
              {
                "name": "Akta Nikah",
                "locale": "id"
              },
              {
                "name": "Marriage Certificate Number",
                "locale": "en"
              }
            ]
          },
          {
            "path": [
              "credentialSubject",
              "kua"
            ],
            "display": [
              {
                "name": "KUA",
                "locale": "id"
              },
              {
                "name": "Office of Religious Affairs",
                "locale": "en"
              }
            ]
          },
          {
            "path": [
              "credentialSubject",
              "kabupaten_kota"
            ],
            "display": [
              {
                "name": "Kabupaten/Kota",
                "locale": "id"
              },
              {
                "name": "Regency or City",
                "locale": "en"
              }
            ]
          },
          {
            "path": [
              "credentialSubject",
              "provinsi"
            ],
            "display": [
              {
                "name": "Provinsi",
                "locale": "id"
              },
              {
                "name": "Province",
                "locale": "en"
              }
            ]
          }
        ]
      }
    }
  }
}
```

``` { .http title="200, the Kartu Nikah as ldp_vc" data-format="HTTP" }
HTTP/1.1 200 OK
DPoP-Nonce: frK_B3bB7TgsvlGBBCoQE2Mp
Cache-Control: no-store
Content-Type: application/json

{
  "credentials": [
    {
      "credential": {
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
          "provinsi": "Jawa Barat"
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
          "proofValue": "z3JTvebTQCkzF6G4dX57mTnykwTtDGWD1gBCfBjzpWmkx2PdTocdowomBTR7Qzaef1L34erTcPA16ArhQhiNxS5UW"
        }
      }
    }
  ],
  "notification_id": "JUAJNT18SWEzKdxJ"
}
```

## The HTTPS binding {#ts-1-01-the-https-binding}

Issuer Core answers every request of this specification at a public address,
because a wallet reaches it from the open internet and
[every issuer runs its own public endpoint][network-zones-and-placement].
[The table of endpoints][tbl-ts-1-01-endpoints] gives each one, where the
wallet learns its address, and the clause that fixes it.

[](){ #tbl-ts-1-01-endpoints }

<figure markdown="1" class="ekdn-table">

| Endpoint | Method | Address from | Clause |
|---|---|---|---|
| Credential issuer metadata | `GET` | The credential issuer identifier, as `/.well-known/openid-credential-issuer` | [Issuer metadata][ts-1-01-issuer-metadata] |
| Authorization server metadata | `GET` | The credential issuer identifier, as `/.well-known/oauth-authorization-server` | [Authorization server metadata][ts-1-01-authorization-server-metadata] |
| Credential offer, by reference | `GET` | `credential_offer_uri` in the offer | [The credential offer][ts-1-01-the-credential-offer] |
| Pushed authorization request | `POST` | `pushed_authorization_request_endpoint` | [Authorization][ts-1-01-authorization] |
| Authorization | `GET` | `authorization_endpoint` | [Authorization][ts-1-01-authorization] |
| Token | `POST` | `token_endpoint` | [The token endpoint][ts-1-01-the-token-endpoint] |
| Nonce | `POST` | `nonce_endpoint` | [The nonce][ts-1-01-the-nonce] |
| Credential | `POST` | `credential_endpoint` | [The credential request][ts-1-01-the-credential-request] |
| Deferred credential | `POST` | `deferred_credential_endpoint` | [Deferred issuance][ts-1-01-deferred-issuance] |
| Notification | `POST` | `notification_endpoint` | [The notification][ts-1-01-the-notification] |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-1-01-003 }**REQ-TS-1-01-003** Issuer Core MUST serve every endpoint of [the table of endpoints][tbl-ts-1-01-endpoints] over HTTP with Transport Layer Security (TLS) only.
- [](){ #req-ts-1-01-004 }**REQ-TS-1-01-004** Issuer Core MUST serve every endpoint of [the table of endpoints][tbl-ts-1-01-endpoints] at an address a wallet on the public internet can reach.
- [](){ #req-ts-1-01-005 }**REQ-TS-1-01-005** The credential issuer identifier MUST be an `https` address with a host and no path, query, or fragment.
- [](){ #req-ts-1-01-006 }**REQ-TS-1-01-006** Issuer Core MUST carry a `Cache-Control: no-store` header on every answer that carries an offer, a code, a token, a nonce, or a credential.
- [](){ #req-ts-1-01-007 }**REQ-TS-1-01-007** Issuer Core MUST NOT call Mobile Wallet, because [nothing calls the wallet][who-may-call-whom]: every exchange of this specification starts at the wallet.

</div>

## Issuer metadata {#ts-1-01-issuer-metadata}

The credential issuer metadata tells a wallet where each endpoint is and what
the issuer issues, in what representation, and against what proof. Issuer
Core serves it as [OpenID4VCI][ref-openid4vci] section 12.2 defines, and signs
it, as [Signed metadata][ts-1-01-signed-metadata] sets out.

### Members {#ts-1-01-metadata-members}

[The table of metadata members][tbl-ts-1-01-metadata-members] gives every
top-level member Issuer Core writes, and the ones it leaves out.

[](){ #tbl-ts-1-01-metadata-members }

<figure markdown="1" class="ekdn-table">

| Member | Type | Presence | Value |
|---|---|---|---|
| `credential_issuer` | string | Present | The credential issuer identifier |
| `credential_endpoint` | string | Present | The credential endpoint |
| `nonce_endpoint` | string | Present | The Nonce Endpoint |
| `deferred_credential_endpoint` | string | Present | The deferred credential endpoint |
| `notification_endpoint` | string | Present | The notification endpoint |
| `credential_configurations_supported` | object | Present | One configuration for each representation of each type the issuer offers, as [A credential configuration][ts-1-01-a-credential-configuration] fixes |
| `authorization_servers` | array | Absent | None: Issuer Core is its own authorization server |
| `credential_request_encryption` | object | Absent | None |
| `credential_response_encryption` | object | Absent | None |
| `batch_credential_issuance` | object | Absent | None: one credential key, one credential |
| `display` | array | Absent | None: a logo an issuer supplies about itself is checked by no one, so the wallet names the issuer from the trusted list |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-1-01-008 }**REQ-TS-1-01-008** Issuer Core MUST write every member [the table of metadata members][tbl-ts-1-01-metadata-members] marks present.
- [](){ #req-ts-1-01-009 }**REQ-TS-1-01-009** Issuer Core MUST NOT write a member [the table of metadata members][tbl-ts-1-01-metadata-members] marks absent.
- [](){ #req-ts-1-01-010 }**REQ-TS-1-01-010** `credential_issuer` MUST equal the credential issuer identifier the metadata was fetched under.

</div>

### A credential configuration {#ts-1-01-a-credential-configuration}

A credential configuration is one representation of one type. A type whose
Credential Rulebook names SD-JWT VC and mdoc has two, and a wallet asks for
both, because a credential held in one representation alone cannot be shown
in both modes. The identifier of a configuration is composed as
[REQ-TS-1-01-012][req-ts-1-01-012] fixes, so every issuer of a type names its
configurations the same way, and a wallet finds the Rulebook from the
identifier alone.

[](){ #tbl-ts-1-01-configuration-members }

<figure markdown="1" class="ekdn-table">

| Member | Type | Presence | Value |
|---|---|---|---|
| `format` | string | Present | `dc+sd-jwt` for `sd-jwt-vc`, `mso_mdoc` for `mdoc`, `ldp_vc` for `ldp_vc` |
| `vct` | string | Present for `dc+sd-jwt` | The `vct` the Rulebook's `sd-jwt-vc` entry names |
| `doctype` | string | Present for `mso_mdoc` | The `docType` the Rulebook's `mdoc` entry names |
| `credential_definition` | object | Present for `ldp_vc` | `@context` and `type`, the values the issued credential carries |
| `cryptographic_binding_methods_supported` | array | Present | `jwk` for `dc+sd-jwt`, `cose_key` for `mso_mdoc`, `did:key` for `ldp_vc` |
| `credential_signing_alg_values_supported` | array | Present | The algorithms Issuer Core signs the representation with |
| `proof_types_supported` | object | Present | The proof types the Governance Profile maps from the Rulebook's `min_assurance`, each with `proof_signing_alg_values_supported` and `key_attestations_required` |
| `credential_metadata` | object | Present | `display` and `claims`, copied from the Type Metadata |
| `scope` | string | Absent | None: a wallet asks through `authorization_details` |

</figure>

For `ldp_vc`, `credential_signing_alg_values_supported` carries the
cryptosuite name, `ecdsa-rdfc-2019`. Appendix A.1.2.2 of
[OpenID4VCI][ref-openid4vci] says the value should come from a registry of
linked data signature suites. That registry has not changed since 2020 and names
no Data Integrity cryptosuite, so the profile takes the name the credential's own
`proof.cryptosuite` carries. OpenID4VCI's `di_vp` proof type and the
`cryptosuite_values` of
[OpenID for Verifiable Presentations (OpenID4VP) 1.0][ref-openid4vp] name one
the same way.

The proof types an issuer accepts follow from the Rulebook's `min_assurance`,
and so do the values it requires of a Key Attestation. The Governance Profile
holds both, in one member per level under `mappings.min_assurance`, which
[Mappings][ts-02-mappings] lists and
[the mapping of assurance to key storage][tbl-min-assurance-mapping] explains.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-1-01-011 }**REQ-TS-1-01-011** Issuer Core MUST announce one credential configuration for each representation the Credential Rulebook of each type it offers names under `formats`, and no other.
- [](){ #req-ts-1-01-012 }**REQ-TS-1-01-012** The identifier of a credential configuration MUST be the Rulebook's `id`, a colon, and the name of the representation under `formats`.
- [](){ #req-ts-1-01-013 }**REQ-TS-1-01-013** A credential configuration MUST carry the members [the table of configuration members][tbl-ts-1-01-configuration-members] marks present for its `format`, with the values that table gives, and no member it marks absent.
- [](){ #req-ts-1-01-014 }**REQ-TS-1-01-014** `credential_signing_alg_values_supported` MUST list only algorithms the Governance Profile allows for an issuance key, written as the `alg` names of [RFC 7518][ref-rfc7518] for `dc+sd-jwt`, as the algorithm numbers of [RFC 9053][ref-rfc9053] for `mso_mdoc`, and as the cryptosuite name for `ldp_vc`.
- [](){ #req-ts-1-01-015 }**REQ-TS-1-01-015** `proof_types_supported` MUST name the proof types the Governance Profile holds under `mappings.min_assurance` for the Rulebook's `min_assurance`, and no other.
- [](){ #req-ts-1-01-016 }**REQ-TS-1-01-016** Each proof type MUST carry `key_attestations_required` with the `key_storage` and `user_authentication` values the Governance Profile maps from the Rulebook's `min_assurance`.
- [](){ #req-ts-1-01-017 }**REQ-TS-1-01-017** For the `attestation` proof type, `proof_signing_alg_values_supported` MUST list only algorithms the Governance Profile allows for a Key Attestation key.
- [](){ #req-ts-1-01-018 }**REQ-TS-1-01-018** For the `jwt` proof type, `proof_signing_alg_values_supported` MUST list only algorithms the Governance Profile allows for a credential key or for a Key Attestation key, because the proof and the attestation in its header are each checked against it.
- [](){ #req-ts-1-01-019 }**REQ-TS-1-01-019** Issuer Core MUST copy `credential_metadata.display` and the `display` of each claim from the Type Metadata the Rulebook's `display` points at, and add nothing: the type's name and description per locale, the logo, background color, and text color of `display[].rendering.simple`, and each attribute's label as the claim's display `name`.
- [](){ #req-ts-1-01-020 }**REQ-TS-1-01-020** Issuer Core MUST write `credential_metadata.claims` with one claim for each claim of the Type Metadata, carrying its `path` as [REQ-CR-074][req-cr-074] and [REQ-CR-075][req-cr-075] form it and, where the Type Metadata sets it, its `mandatory`.
- [](){ #req-ts-1-01-143 }**REQ-TS-1-01-143** In the `mso_mdoc` configuration of a type whose Rulebook lists both `sd-jwt-vc` and `mdoc`, Issuer Core MUST put the namespace in front of each claim's `path`, the Rulebook's `id` or the `namespace` its `mdoc` entry names, so that the path is the claims path pointer [OpenID4VCI][ref-openid4vci] defines for an mdoc.

</div>

That namespace is the one addition [REQ-TS-1-01-019][req-ts-1-01-019] allows.

### Signed metadata {#ts-1-01-signed-metadata}

Issuer Core signs its metadata as a JSON Web Token (JWT), the form
[OpenID4VCI][ref-openid4vci] section 12.2.3 defines, with its `issuance-jose`
key, the key it signs an SD-JWT VC and an `ldp_vc` with. The token names its key
the way every token an issuer signs does, as
[Finding a signer's key from its DID](finding-a-signers-key-from-its-did.md)
fixes. An issuer that can sign metadata for an address is the issuer behind it,
and a wallet asks for the signed form and takes no other.

[](){ #tbl-ts-1-01-metadata-header }

<figure markdown="1" class="ekdn-table">

| Member | Type | Presence | Value |
|---|---|---|---|
| `typ` | string | Present | `openidvci-issuer-metadata+jwt` |
| `alg` | string | Present | An algorithm the Governance Profile allows for an issuance key |
| `kid` | string | Present | A key of the purpose `issuance-jose` in the issuer's DID Document |

</figure>

[](){ #tbl-ts-1-01-metadata-claims }

<figure markdown="1" class="ekdn-table">

| Claim | Type | Presence | Value |
|---|---|---|---|
| `iss` | string | Present | The issuer's `did:webvh` |
| `sub` | string | Present | The credential issuer identifier |
| `iat` | number | Present | The moment Issuer Core signed |
| `exp` | number | Absent | None: the metadata holds until the issuer signs a new one |
| Every member of [the table of metadata members][tbl-ts-1-01-metadata-members] | | As that table gives | As that table gives |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-1-01-021 }**REQ-TS-1-01-021** Issuer Core MUST answer a request for its metadata carrying `Accept: application/jwt` with the signed metadata, as a JSON Web Signature (JWS) in compact serialization with `Content-Type: application/jwt`.
- [](){ #req-ts-1-01-022 }**REQ-TS-1-01-022** The protected header MUST carry the members [the table of signed metadata header members][tbl-ts-1-01-metadata-header] gives, and no other.
- [](){ #req-ts-1-01-023 }**REQ-TS-1-01-023** `kid` MUST name a key of the purpose `issuance-jose`, as [Naming the key][ts-01-naming-the-key] of TS-01 requires.
- [](){ #req-ts-1-01-024 }**REQ-TS-1-01-024** The payload MUST carry the claims [the table of signed metadata claims][tbl-ts-1-01-metadata-claims] gives, with every metadata member as a claim of its own.
- [](){ #req-ts-1-01-025 }**REQ-TS-1-01-025** Issuer Core MUST sign its metadata again whenever a member changes.
- [](){ #req-ts-1-01-026 }**REQ-TS-1-01-026** Issuer Core MUST NOT serve signed metadata that differs from its current metadata.
- [](){ #req-ts-1-01-027 }**REQ-TS-1-01-027** Mobile Wallet MUST ask for the metadata with `Accept: application/jwt`.
- [](){ #req-ts-1-01-028 }**REQ-TS-1-01-028** Mobile Wallet MUST refuse an offer whose issuer answers with metadata that is not signed.
- [](){ #req-ts-1-01-029 }**REQ-TS-1-01-029** Mobile Wallet MUST refuse signed metadata whose `typ` is not `openidvci-issuer-metadata+jwt`.
- [](){ #req-ts-1-01-030 }**REQ-TS-1-01-030** Mobile Wallet MUST find the signing key as [Finding the key][ts-01-finding-the-key] of TS-01 requires, under the purpose `issuance-jose`, with `iss` as the signer.
- [](){ #req-ts-1-01-031 }**REQ-TS-1-01-031** Mobile Wallet MUST refuse signed metadata whose `sub` or `credential_issuer` differs from the `credential_issuer` of the offer.

</div>

### Checking the issuer {#ts-1-01-checking-the-issuer}

With the DID in hand, the wallet asks its cache the two questions
[three questions, three answers][three-questions-three-answers] keeps apart:
whether the issuer is accredited, and whether it may issue the type offered.
It asks both before it sends anything else to the issuer, so a citizen never
types a code or signs in for an issuer that the trusted list does not carry.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-1-01-032 }**REQ-TS-1-01-032** Mobile Wallet MUST refuse an offer whose metadata `iss` is not the DID of an entry in its cached trusted list with an Identity Issuer or Attribute Issuer service at status `granted`.
- [](){ #req-ts-1-01-033 }**REQ-TS-1-01-033** Mobile Wallet MUST refuse an offer unless its cache holds, for that DID, an Authority Statement with `action` `issue` and the Rulebook `id` of the offered type as `resource` that answers `true`, read as [Reading the answer][ts-5-05-reading-the-answer] of TS-5-05 requires.
- [](){ #req-ts-1-01-034 }**REQ-TS-1-01-034** Mobile Wallet MUST refuse an offer that names a credential configuration the signed metadata does not announce.
- [](){ #req-ts-1-01-035 }**REQ-TS-1-01-035** Mobile Wallet MUST run the checks of this clause before it sends any request to the issuer other than the request for a `credential_offer_uri` and the metadata requests.
- [](){ #req-ts-1-01-036 }**REQ-TS-1-01-036** Mobile Wallet MUST run the checks of this clause from its own cache, with no request to Trust Infrastructure.

</div>

### Authorization server metadata {#ts-1-01-authorization-server-metadata}

Issuer Core is its own authorization server and publishes the metadata
[RFC 8414][ref-rfc8414] defines under its credential issuer identifier.
[The table of authorization server members][tbl-ts-1-01-as-members] gives the
members this profile fixes.

[](){ #tbl-ts-1-01-as-members }

<figure markdown="1" class="ekdn-table">

| Member | Presence | Value |
|---|---|---|
| `issuer` | Present | The credential issuer identifier |
| `token_endpoint` | Present | The token endpoint |
| `grant_types_supported` | Present | `authorization_code` and `refresh_token`, and `urn:ietf:params:oauth:grant-type:pre-authorized_code` where the Pre-Authorized Code flow is supported |
| `token_endpoint_auth_methods_supported` | Present | `none` |
| `dpop_signing_alg_values_supported` | Present | The algorithms the Governance Profile allows for a DPoP key |
| `authorization_details_types_supported` | Present | `openid_credential` |
| `pre-authorized_grant_anonymous_access_supported` | Present where the Pre-Authorized Code flow is supported | `true` |
| `authorization_endpoint` | Present | The authorization endpoint |
| `pushed_authorization_request_endpoint` | Present | The pushed authorization request endpoint |
| `require_pushed_authorization_requests` | Present | `true` |
| `response_types_supported` | Present | `code` |
| `code_challenge_methods_supported` | Present | `S256` |
| `authorization_response_iss_parameter_supported` | Present | `true` |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-1-01-037 }**REQ-TS-1-01-037** Issuer Core MUST serve its authorization server metadata at the credential issuer identifier followed by `/.well-known/oauth-authorization-server`, with the members [the table of authorization server members][tbl-ts-1-01-as-members] gives.
- [](){ #req-ts-1-01-038 }**REQ-TS-1-01-038** Issuer Core MUST support the Authorization Code flow, because a wallet whose refresh token is refused falls back to it, as [credential renewal][credential-renewal] sets out.
- [](){ #req-ts-1-01-039 }**REQ-TS-1-01-039** Mobile Wallet MUST refuse authorization server metadata whose `issuer` differs from the credential issuer identifier.
- [](){ #req-ts-1-01-040 }**REQ-TS-1-01-040** Mobile Wallet MUST support both flows.

</div>

## The credential offer {#ts-1-01-the-credential-offer}

An offer is how an issuer starts an issuance. It carries no signature and
nothing a wallet trusts on its own: it names the issuer, the configurations,
and the grant, and the wallet checks the issuer before it uses any of them.

[](){ #tbl-ts-1-01-offer-members }

<figure markdown="1" class="ekdn-table">

| Member | Type | Presence | Value |
|---|---|---|---|
| `credential_issuer` | string | Present | The credential issuer identifier |
| `credential_configuration_ids` | array of string | Present | Every configuration Issuer Core announces for one type |
| `grants` | object | Present | Exactly one grant |
| `grants.authorization_code.issuer_state` | string | Optional | A value the wallet sends back at the pushed authorization request |
| `grants["urn:ietf:params:oauth:grant-type:pre-authorized_code"].pre-authorized_code` | string | Present in that grant | The pre-authorized code |
| `grants["urn:ietf:params:oauth:grant-type:pre-authorized_code"].tx_code` | object | Present in that grant | `input_mode` `numeric`, `length`, and an optional `description` |
| `authorization_server`, in either grant | string | Absent | None |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-1-01-041 }**REQ-TS-1-01-041** Issuer Core MUST write an offer with the members [the table of offer members][tbl-ts-1-01-offer-members] gives, and no other.
- [](){ #req-ts-1-01-042 }**REQ-TS-1-01-042** An offer MUST name the configurations of one credential type, and every configuration Issuer Core announces for that type.
- [](){ #req-ts-1-01-043 }**REQ-TS-1-01-043** Issuer Core MUST deliver an offer through the `openid-credential-offer` scheme, as a QR code or a deeplink, carrying either `credential_offer` or `credential_offer_uri`.
- [](){ #req-ts-1-01-044 }**REQ-TS-1-01-044** Issuer Core MUST answer a request for a `credential_offer_uri` with the offer as `application/json`.
- [](){ #req-ts-1-01-045 }**REQ-TS-1-01-045** Issuer Core MUST accept a pre-authorized code in one token request only.
- [](){ #req-ts-1-01-046 }**REQ-TS-1-01-046** Issuer Core MUST refuse a pre-authorized code issued longer ago than the lifetime the Governance Profile sets.
- [](){ #req-ts-1-01-047 }**REQ-TS-1-01-047** Issuer Core MUST deliver the transaction code to the citizen through a channel other than the one that carries the offer.
- [](){ #req-ts-1-01-048 }**REQ-TS-1-01-048** A transaction code MUST be numeric and at least six digits long.
- [](){ #req-ts-1-01-049 }**REQ-TS-1-01-049** `tx_code.description` MUST NOT carry personal data or the transaction code itself.
- [](){ #req-ts-1-01-050 }**REQ-TS-1-01-050** An offer MUST NOT carry a claim of the credential or an identifier of the citizen.

</div>

## Authorization {#ts-1-01-authorization}

In the Authorization Code flow the wallet pushes its authorization request
to the issuer directly, as [RFC 9126][ref-rfc9126] defines, and the browser
carries nothing but the reference to it. The request asks for each
configuration of the offer through `authorization_details`, the structure
[RFC 9396][ref-rfc9396] defines, and carries a PKCE challenge. The wallet sends a DPoP proof
with the request. That binds the authorization code to the wallet's DPoP
key, as section 10.1 of [RFC 9449][ref-rfc9449] defines. The authorization
response names the issuer that sent it, as [RFC 9207][ref-rfc9207] defines, so
that a wallet talking to many issuers cannot be handed one issuer's code by
another.

[](){ #tbl-ts-1-01-par-members }

<figure markdown="1" class="ekdn-table">

| Parameter | Presence | Value |
|---|---|---|
| `response_type` | Present | `code` |
| `client_id` | Present | The client identifier the Wallet Provider chose |
| `redirect_uri` | Present | An `https` address under the Wallet Provider's domain that opens the wallet |
| `state` | Present | A value the wallet drew for this request |
| `code_challenge` | Present | The PKCE challenge |
| `code_challenge_method` | Present | `S256` |
| `authorization_details` | Present | One `openid_credential` entry for each configuration of the offer, each with `credential_configuration_id` and nothing else |
| `issuer_state` | Present where the offer carried it | The value of the offer |
| `scope` | Absent | None |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-1-01-051 }**REQ-TS-1-01-051** Issuer Core MUST refuse an authorization request that does not reference a pushed authorization request.
- [](){ #req-ts-1-01-052 }**REQ-TS-1-01-052** Mobile Wallet MUST send a pushed authorization request with the parameters [the table of pushed authorization request parameters][tbl-ts-1-01-par-members] gives.
- [](){ #req-ts-1-01-053 }**REQ-TS-1-01-053** Mobile Wallet MUST send a DPoP proof with the pushed authorization request.
- [](){ #req-ts-1-01-054 }**REQ-TS-1-01-054** Issuer Core MUST bind the authorization code to the key of the DPoP proof sent with the pushed authorization request.
- [](){ #req-ts-1-01-055 }**REQ-TS-1-01-055** Issuer Core MUST refuse a pushed authorization request that carries `dpop_jkt` naming a key other than the key of its DPoP proof.
- [](){ #req-ts-1-01-056 }**REQ-TS-1-01-056** Issuer Core MUST refuse a pushed authorization request with no `code_challenge` or with a `code_challenge_method` other than `S256`.
- [](){ #req-ts-1-01-057 }**REQ-TS-1-01-057** Issuer Core MUST refuse with `invalid_authorization_details` a pushed authorization request whose `authorization_details` names a configuration it does not announce, or configurations of more than one type.
- [](){ #req-ts-1-01-058 }**REQ-TS-1-01-058** Issuer Core MUST accept a request URI in one authorization request only.
- [](){ #req-ts-1-01-059 }**REQ-TS-1-01-059** Issuer Core MUST refuse a request URI issued longer ago than the lifetime the Governance Profile sets.
- [](){ #req-ts-1-01-060 }**REQ-TS-1-01-060** Mobile Wallet MUST open the authorization endpoint with `client_id` and `request_uri` alone.
- [](){ #req-ts-1-01-061 }**REQ-TS-1-01-061** Issuer Core MUST take the citizen the credential is for from the citizen's authentication at its authorization endpoint, or from the record it bound to the pre-authorized code, and never from a parameter the wallet sends.
- [](){ #req-ts-1-01-062 }**REQ-TS-1-01-062** Issuer Core MUST carry `iss`, its credential issuer identifier, in every authorization response.
- [](){ #req-ts-1-01-063 }**REQ-TS-1-01-063** Mobile Wallet MUST refuse an authorization response whose `iss` is not the issuer it sent the request to, or whose `state` is not the value it sent.

</div>

## The token endpoint {#ts-1-01-the-token-endpoint}

The token endpoint exchanges an authorization code, a pre-authorized code, or
a refresh token for an access token. The wallet does not authenticate, and
every token is bound to the wallet's DPoP key, so a token copied off the wire
is of no use to anyone without that key.

[](){ #tbl-ts-1-01-token-parameters }

<figure markdown="1" class="ekdn-table">

| Parameter | Authorization code | Pre-authorized code | Refresh token |
|---|---|---|---|
| `grant_type` | `authorization_code` | `urn:ietf:params:oauth:grant-type:pre-authorized_code` | `refresh_token` |
| `code` | Present | Absent | Absent |
| `code_verifier` | Present | Absent | Absent |
| `redirect_uri` | Present | Absent | Absent |
| `client_id` | Present | Absent | Absent |
| `pre-authorized_code` | Absent | Present | Absent |
| `tx_code` | Absent | Present | Absent |
| `authorization_details` | Absent | Present, as at the pushed authorization request | Absent |
| `refresh_token` | Absent | Absent | Present |

</figure>

[](){ #tbl-ts-1-01-token-response }

<figure markdown="1" class="ekdn-table">

| Member | Type | Presence | Value |
|---|---|---|---|
| `access_token` | string | Present | The access token |
| `token_type` | string | Present | `DPoP` |
| `expires_in` | number | Present | The lifetime of the access token, in seconds |
| `refresh_token` | string | Present after a code, absent after a refresh token | The refresh token |
| `authorization_details` | array | Present | One `openid_credential` entry for each configuration granted, each with `credential_configuration_id` and `credential_identifiers` |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-1-01-064 }**REQ-TS-1-01-064** Mobile Wallet MUST send the parameters [the table of token request parameters][tbl-ts-1-01-token-parameters] gives for the grant, and no other.
- [](){ #req-ts-1-01-065 }**REQ-TS-1-01-065** Issuer Core MUST NOT require client authentication at the token endpoint or at the pushed authorization request endpoint.
- [](){ #req-ts-1-01-066 }**REQ-TS-1-01-066** Issuer Core MUST accept a pre-authorized code token request that carries no `client_id`.
- [](){ #req-ts-1-01-067 }**REQ-TS-1-01-067** Issuer Core MUST refuse an authorization code whose `code_verifier` does not hash, under SHA-256, to the challenge of its pushed authorization request.
- [](){ #req-ts-1-01-068 }**REQ-TS-1-01-068** Issuer Core MUST accept an authorization code in one token request only.
- [](){ #req-ts-1-01-069 }**REQ-TS-1-01-069** Issuer Core MUST refuse an authorization code issued longer ago than the lifetime the Governance Profile sets.
- [](){ #req-ts-1-01-070 }**REQ-TS-1-01-070** Issuer Core MUST refuse an authorization code presented with a DPoP proof under a key other than the one the code is bound to.
- [](){ #req-ts-1-01-071 }**REQ-TS-1-01-071** Issuer Core MUST refuse a pre-authorized code token request whose `tx_code` is not the transaction code of that pre-authorized code.
- [](){ #req-ts-1-01-072 }**REQ-TS-1-01-072** Issuer Core MUST invalidate a pre-authorized code after the number of wrong transaction codes the Governance Profile allows.
- [](){ #req-ts-1-01-073 }**REQ-TS-1-01-073** Issuer Core MUST bind every access token and every refresh token to the key of the DPoP proof sent with the token request.
- [](){ #req-ts-1-01-074 }**REQ-TS-1-01-074** Issuer Core MUST answer a token request with `token_type` `DPoP` and the members [the table of token response members][tbl-ts-1-01-token-response] gives.
- [](){ #req-ts-1-01-075 }**REQ-TS-1-01-075** Issuer Core MUST give an access token the lifetime the Governance Profile sets.
- [](){ #req-ts-1-01-146 }**REQ-TS-1-01-146** Issuer Core MUST NOT end a refresh token for its age before the administrative validity period of the credential it was issued for ends, where the type has one.
- [](){ #req-ts-1-01-147 }**REQ-TS-1-01-147** Issuer Core MUST refuse a refresh token once the administrative validity period of the credential it was issued for has ended, where the type has one.
- [](){ #req-ts-1-01-148 }**REQ-TS-1-01-148** Issuer Core MUST refuse a refresh token once the inactivity period the Governance Profile sets has passed since the end of the technical validity period of the latest credential issued under it.
- [](){ #req-ts-1-01-076 }**REQ-TS-1-01-076** Issuer Core MUST issue a refresh token with every access token it issues for an authorization code or a pre-authorized code.
- [](){ #req-ts-1-01-077 }**REQ-TS-1-01-077** Issuer Core MUST answer with one `authorization_details` entry for each configuration the authorization covers, each carrying exactly one credential identifier.
- [](){ #req-ts-1-01-078 }**REQ-TS-1-01-078** Issuer Core MUST tie every credential identifier of one access token to one credential of one citizen.

</div>

## DPoP {#ts-1-01-dpop}

Every request a wallet sends to the pushed authorization request endpoint, the
token endpoint, the credential endpoint, the deferred credential endpoint, and
the notification endpoint carries a DPoP proof, as [RFC 9449][ref-rfc9449]
defines it. The key that signs it is the wallet's DPoP key for that issuer:
not the credential key, which only the citizen's authentication releases and
which signs presentations, and not the device key, which the Wallet Backend
Service alone knows.

Renewal runs without the citizen, so the key that signs its DPoP proofs
cannot be one that asks for the citizen, as [the DPoP key][the-dpop-key] sets
out. A wallet makes one DPoP key for each issuer, keeps it as long as it
holds a refresh token from that issuer, and signs nothing else with it, which
keeps renewal on the phone that received the refresh token, as
[credential renewal][credential-renewal] requires.

Issuer Core hands out the nonce each proof carries, in the `DPoP-Nonce` header,
so that a proof cannot be made ahead of time.

[](){ #tbl-ts-1-01-dpop-proof }

<figure markdown="1" class="ekdn-table">

| Member | Where | Presence | Value |
|---|---|---|---|
| `typ` | Header | Present | `dpop+jwt` |
| `alg` | Header | Present | An algorithm the Governance Profile allows for a DPoP key |
| `jwk` | Header | Present | The public DPoP key, as a JSON Web Key with no private member |
| `jti` | Claims | Present | A value the wallet drew for this proof |
| `htm` | Claims | Present | The method of the request |
| `htu` | Claims | Present | The address of the request, with no query and no fragment |
| `iat` | Claims | Present | The moment the wallet signed |
| `nonce` | Claims | Present once Issuer Core has given a DPoP nonce | The latest DPoP nonce Issuer Core gave |
| `ath` | Claims | Present at the credential, deferred credential, and notification endpoints | The base64url SHA-256 hash of the access token |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-1-01-079 }**REQ-TS-1-01-079** Mobile Wallet MUST sign every DPoP proof to an issuer with a key it generated for that issuer, of a type the Governance Profile allows for a DPoP key.
- [](){ #req-ts-1-01-080 }**REQ-TS-1-01-080** Mobile Wallet MUST NOT use the credential key or the device key as a DPoP key.
- [](){ #req-ts-1-01-081 }**REQ-TS-1-01-081** Mobile Wallet MUST NOT use one DPoP key with more than one issuer.
- [](){ #req-ts-1-01-082 }**REQ-TS-1-01-082** Mobile Wallet MUST generate each DPoP key inside the device's secure element, where it cannot be exported.
- [](){ #req-ts-1-01-083 }**REQ-TS-1-01-083** A DPoP proof MUST carry the members [the table of DPoP proof members][tbl-ts-1-01-dpop-proof] gives, and no other.
- [](){ #req-ts-1-01-084 }**REQ-TS-1-01-084** Mobile Wallet MUST send a DPoP proof with every request to the pushed authorization request, token, credential, deferred credential, and notification endpoints.
- [](){ #req-ts-1-01-085 }**REQ-TS-1-01-085** Issuer Core MUST carry a fresh DPoP nonce in a `DPoP-Nonce` header on every answer of the endpoints [REQ-TS-1-01-084][req-ts-1-01-084] names and of the Nonce Endpoint.
- [](){ #req-ts-1-01-086 }**REQ-TS-1-01-086** Issuer Core MUST refuse with `use_dpop_nonce` a DPoP proof that carries no `nonce`, a `nonce` it did not issue, or one it issued longer ago than the lifetime the Governance Profile sets.
- [](){ #req-ts-1-01-087 }**REQ-TS-1-01-087** Issuer Core MUST refuse a DPoP proof whose `jti` it already accepted under the same DPoP nonce.
- [](){ #req-ts-1-01-088 }**REQ-TS-1-01-088** Issuer Core MUST refuse a DPoP proof whose signature does not verify under its `jwk`, whose `htm` or `htu` differs from the request, or whose `ath` is not the hash of the access token the request carries.
- [](){ #req-ts-1-01-089 }**REQ-TS-1-01-089** Issuer Core MUST refuse a DPoP proof whose `typ` is not `dpop+jwt`, or whose `alg` is not one it announces in `dpop_signing_alg_values_supported`.
- [](){ #req-ts-1-01-090 }**REQ-TS-1-01-090** Issuer Core MUST refuse an access token presented with a DPoP proof under a key other than the one the token is bound to.
- [](){ #req-ts-1-01-091 }**REQ-TS-1-01-091** Mobile Wallet MUST send the access token in an `Authorization: DPoP` header.

</div>

## The nonce {#ts-1-01-the-nonce}

The Nonce Endpoint gives the `c_nonce` a Key Attestation carries, as
[OpenID4VCI][ref-openid4vci] section 7 defines it. It takes no access token,
because the wallet asks for the nonce before its Wallet Backend Service signs
the attestation. How Issuer Core matches a nonce to the attestation and the
request is fixed by [Freshness and lifetime][ts-5-08-freshness-and-lifetime]
in TS-5-08; how long a nonce lasts is fixed here.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-1-01-092 }**REQ-TS-1-01-092** Issuer Core MUST answer a `POST` to its Nonce Endpoint with `200` and a JSON object carrying `c_nonce` and no other member.
- [](){ #req-ts-1-01-093 }**REQ-TS-1-01-093** Issuer Core MUST draw each `c_nonce` from a cryptographically secure random source.
- [](){ #req-ts-1-01-094 }**REQ-TS-1-01-094** Issuer Core MUST refuse with `invalid_nonce` a `c_nonce` issued longer ago than the lifetime the Governance Profile sets.
- [](){ #req-ts-1-01-095 }**REQ-TS-1-01-095** Mobile Wallet MUST fetch a new `c_nonce` for each credential request.

</div>

## The credential request {#ts-1-01-the-credential-request}

A credential request asks for one credential identifier and carries one proof.
The wallet sends one for each identifier the token response gave, so that it
ends up with every representation of the credential.

[](){ #tbl-ts-1-01-request-members }

<figure markdown="1" class="ekdn-table">

| Member | Type | Presence | Value |
|---|---|---|---|
| `credential_identifier` | string | Present | One identifier of the token response |
| `proofs` | object | Present | One member, `jwt` or `attestation`, holding an array of exactly one proof |
| `credential_configuration_id` | string | Absent | None: the identifier names the configuration |
| `credential_response_encryption` | object | Absent | None |

</figure>

The proof is the one [Carrying it to an issuer][ts-5-08-carrying-it-to-an-issuer]
fixes: an `attestation` proof, which is the Key Attestation itself, or a `jwt`
proof signed with the credential key, with the attestation in its
`key_attestation` header and `aud` set to the credential issuer identifier.

Issuer Core runs these steps on every credential request, in this order, and
stops at the first that fails.

1. Check the access token and its DPoP proof.
2. Check that the credential identifier was issued with that access token.
3. Check, in its cached trusted list, that its own entry still reads `granted`
   for its role. A suspended issuer stops here.
4. Check, in its cache, that it still holds the permission to issue the type,
   through an Authority Statement that answers `true`.
5. Run every check of [Reading it][ts-5-08-reading-it] in TS-5-08 on the proof
   and the Key Attestation.
6. Read the citizen's claims from its source system, using its Claims Provider
   Component, for the citizen bound at authorization.
7. Build and sign the representation the configuration names, bound to the key
   in `attested_keys`, as
   [Issuing a credential in SD-JWT VC, mdoc, and `ldp_vc`](issuing-a-credential-in-sd-jwt-vc-mdoc-and-ldp-vc.md)
   fixes.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-1-01-096 }**REQ-TS-1-01-096** Mobile Wallet MUST send a credential request with the members [the table of credential request members][tbl-ts-1-01-request-members] gives, as `application/json`.
- [](){ #req-ts-1-01-097 }**REQ-TS-1-01-097** Mobile Wallet MUST send a credential request for every credential identifier the token response gave.
- [](){ #req-ts-1-01-098 }**REQ-TS-1-01-098** Mobile Wallet MUST carry the Key Attestation as [Carrying it to an issuer][ts-5-08-carrying-it-to-an-issuer] of TS-5-08 requires.
- [](){ #req-ts-1-01-099 }**REQ-TS-1-01-099** Issuer Core MUST run every step of this clause before it signs a credential.
- [](){ #req-ts-1-01-100 }**REQ-TS-1-01-100** Issuer Core MUST refuse with `unknown_credential_identifier` a credential identifier it did not issue with the access token the request carries.
- [](){ #req-ts-1-01-101 }**REQ-TS-1-01-101** Issuer Core MUST refuse with `credential_request_denied` every credential request while its own trusted list entry does not read `granted`.
- [](){ #req-ts-1-01-102 }**REQ-TS-1-01-102** Issuer Core MUST refuse with `credential_request_denied` a credential request for a type it holds no current permission to issue.
- [](){ #req-ts-1-01-103 }**REQ-TS-1-01-103** Issuer Core MUST refuse with `invalid_proof` a request whose `proofs` carries more than one member, or an array of more than one proof.
- [](){ #req-ts-1-01-104 }**REQ-TS-1-01-104** Issuer Core MUST issue every representation asked for under one access token as one credential, as [REQ-TS-5-10-007][req-ts-5-10-007] to [REQ-TS-5-10-010][req-ts-5-10-010] require.
- [](){ #req-ts-1-01-105 }**REQ-TS-1-01-105** Issuer Core MUST refuse with `invalid_proof` a credential request whose attested key differs from the key of a representation it already issued under the same access token.
- [](){ #req-ts-1-01-106 }**REQ-TS-1-01-106** Issuer Core MUST refuse with `invalid_credential_request` a request for a credential identifier it already answered with a credential under the same access token.

</div>

## The credential response {#ts-1-01-the-credential-response}

Issuer Core answers with the credential, or, where it cannot finish at once,
with a transaction identifier. [The table of credential response
members][tbl-ts-1-01-response-members] gives both forms, and
[the table of credential forms][tbl-ts-1-01-credential-forms] what
`credential` holds in each representation.

[](){ #tbl-ts-1-01-response-members }

<figure markdown="1" class="ekdn-table">

| Member | Type | `200` | `202` |
|---|---|---|---|
| `credentials` | array | Present: exactly one object, with `credential` | Absent |
| `notification_id` | string | Present | Absent |
| `transaction_id` | string | Absent | Present |
| `interval` | number | Absent | Present: the seconds the wallet waits before it asks again |

</figure>

[](){ #tbl-ts-1-01-credential-forms }

<figure markdown="1" class="ekdn-table">

| `format` | `credential` |
|---|---|
| `dc+sd-jwt` | A string: the SD-JWT VC in compact serialization, with its disclosures, ending with `~` |
| `mso_mdoc` | A string: the CBOR encoding of `IssuerSigned`, in base64url without padding |
| `ldp_vc` | An object: the credential with its Data Integrity proof |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-1-01-107 }**REQ-TS-1-01-107** Issuer Core MUST answer a credential request it fulfills with `200` and the members [the table of credential response members][tbl-ts-1-01-response-members] gives for `200`.
- [](){ #req-ts-1-01-108 }**REQ-TS-1-01-108** Issuer Core MUST write `credential` in the form [the table of credential forms][tbl-ts-1-01-credential-forms] gives for the configuration's `format`.
- [](){ #req-ts-1-01-109 }**REQ-TS-1-01-109** Mobile Wallet MUST refuse a credential that is not bound to its credential key.
- [](){ #req-ts-1-01-110 }**REQ-TS-1-01-110** Mobile Wallet MUST refuse an SD-JWT VC whose `iss`, or an `ldp_vc` whose `issuer`, is not the DID the signed metadata named in `iss`.
- [](){ #req-ts-1-01-111 }**REQ-TS-1-01-111** Mobile Wallet MUST check a credential as [Reading a credential][ts-5-10-reading-a-credential] of TS-5-10 requires before it stores it.

</div>

## Deferred issuance {#ts-1-01-deferred-issuance}

A source system that cannot answer in time is not a refusal. Issuer Core answers
`202` with a transaction identifier, the wallet asks again at the deferred
credential endpoint, and the issuer never calls the wallet to say the credential
is ready, as [who may call whom][who-may-call-whom] fixes. A record that is not
there, or that does not meet the conditions of the type, is a refusal, and the
[Errors][ts-1-01-errors] clause gives its answer. A refused citizen has to go to
the institution, while a deferred one only has to wait, so a refusal and a
deferral never look alike.

A renewal of a credential whose entry is suspended is
deferred in the same way: the suspended citizen only has to wait, and a refusal
would send the wallet into a new Authorization Code issuance that bypasses the
suspension. A wait longer than the lifetime of a deferred request ends with
`credential_request_denied`, and the wallet starts renewal again as
[REQ-TS-1-01-127][req-ts-1-01-127] requires.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-1-01-112 }**REQ-TS-1-01-112** Issuer Core MUST answer `202` with `transaction_id` and `interval` when its source system cannot be reached or does not answer in time, and in the case [REQ-TS-1-01-151][req-ts-1-01-151] fixes.
- [](){ #req-ts-1-01-113 }**REQ-TS-1-01-113** Issuer Core MUST NOT defer a request whose record its source system reports missing or not eligible.
- [](){ #req-ts-1-01-114 }**REQ-TS-1-01-114** Mobile Wallet MUST send a deferred credential request, carrying `transaction_id` and no other member, no sooner than `interval` seconds after the answer that gave it.
- [](){ #req-ts-1-01-115 }**REQ-TS-1-01-115** Mobile Wallet MUST obtain a new access token with its refresh token where the access token expired before it asks again.
- [](){ #req-ts-1-01-116 }**REQ-TS-1-01-116** Issuer Core MUST accept a transaction identifier under any access token issued from the same grant, including one obtained with the refresh token.
- [](){ #req-ts-1-01-117 }**REQ-TS-1-01-117** Issuer Core MUST answer a deferred credential request with `200` and the credential, or with `202` and the same `transaction_id` and an `interval`, or with an error.
- [](){ #req-ts-1-01-118 }**REQ-TS-1-01-118** Issuer Core MUST invalidate a transaction identifier once it has answered it with the credential.
- [](){ #req-ts-1-01-119 }**REQ-TS-1-01-119** Issuer Core MUST answer `credential_request_denied` to a deferred request that has stayed open longer than the lifetime the Governance Profile sets.
- [](){ #req-ts-1-01-151 }**REQ-TS-1-01-151** Issuer Core MUST answer a credential request of a renewal with `202`, `transaction_id`, and `interval` while the entry of the credential it replaces is suspended.
- [](){ #req-ts-1-01-155 }**REQ-TS-1-01-155** Issuer Core MUST NOT issue a renewal until the entry of the credential it replaces is valid again.
- [](){ #req-ts-1-01-152 }**REQ-TS-1-01-152** Issuer Core MUST answer `credential_request_denied` to a deferred request of a renewal when the entry of the credential it replaces has become invalid.
- [](){ #req-ts-1-01-156 }**REQ-TS-1-01-156** Issuer Core MUST revoke the refresh token a renewal was made under when the entry of the credential it replaces has become invalid.
- [](){ #req-ts-1-01-120 }**REQ-TS-1-01-120** Mobile Wallet MUST stop asking after an answer of `credential_request_denied` or `invalid_transaction_id`.

</div>

## The notification {#ts-1-01-the-notification}

The notification closes an issuance: it tells Issuer Core whether the credential
reached the wallet, so that its issuance record says what happened. It is the
only thing the wallet tells the issuer after the credential has arrived.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-1-01-121 }**REQ-TS-1-01-121** Mobile Wallet MUST send a notification for each `notification_id` it receives, carrying `notification_id` and `event`.
- [](){ #req-ts-1-01-122 }**REQ-TS-1-01-122** `event` MUST be `credential_accepted` when the wallet stored the credential, `credential_deleted` when the citizen declined to store it, and `credential_failure` in every other case.
- [](){ #req-ts-1-01-123 }**REQ-TS-1-01-123** Mobile Wallet MUST NOT carry a claim of the credential or any other personal data in `event_description`.
- [](){ #req-ts-1-01-124 }**REQ-TS-1-01-124** Issuer Core MUST answer a notification it accepts with `204`.
- [](){ #req-ts-1-01-125 }**REQ-TS-1-01-125** Issuer Core MUST record the event with the issuance record of the credential.
- [](){ #req-ts-1-01-126 }**REQ-TS-1-01-126** Issuer Core MUST NOT use a notification for anything but its issuance record.

</div>

## Renewal {#ts-1-01-renewal}

A credential is renewed before its `exp` without the citizen, as
[credential renewal][credential-renewal] sets out: the wallet exchanges the
refresh token for a new access token and asks for each representation again,
each time with a new nonce and a new Key Attestation sent as the proof itself,
and Issuer Core reads the claims again and signs a new credential for the same
credential key. The `attestation` proof type lets renewal run with the
citizen away: a `jwt` proof is signed with the credential key, and only the
citizen's authentication releases it.

The same path brings a replacement after the issuer's key was revoked, as
[entity key revocation][entity-key-revocation] sets out, where the credential
replaced was revoked with the key. Any other revocation ends the refresh
token with the credential, so a credential revoked for cause is never renewed
and the citizen goes through a new issuance. A credential renewed because its `exp` is
near is not revoked; it runs out at its own `exp`. The renewal therefore takes
an index of its own in the credential status list, because the credential it
replaces holds its own entry until then and may be revoked on its own, as it is
when the issuer's signing key is revoked.

The Governance Profile sets one lead time for every credential, while an
issuer may sign one that is valid for a day. The wallet therefore starts at
the later of that lead time before `exp` and the middle of the technical
period. It never renews for its `exp` a credential whose `exp` is already the
end of its administrative period, which no renewal can pass.

A refresh token lives as long as the administrative validity period of its
credential, as [expiry and validity periods][expiry-and-validity-periods] sets
that period apart from the technical one, and runs out sooner only when the
wallet does not come back for it. Where the type has no administrative period,
nothing ends the token for its age and the inactivity period alone bounds it.

The inactivity period the Governance Profile sets counts from the end of the
technical validity period of the latest credential issued under the token, the
moment the wallet is due back, and not from the token's last use, which for a
credential valid for years lies years back.

The trust a fresh sign-in would give
comes from elsewhere: the token works only with the DPoP key on the phone that
received it, and every renewal carries a new Key Attestation for the same
credential key, which Wallet Backend Service no longer issues once it has
revoked the installation, as
[Issuing and reading a Key Attestation](issuing-and-reading-a-key-attestation.md)
fixes. A credential whose administrative period runs for years would
otherwise send the citizen back to sign in once a year for no added
assurance.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-1-01-127 }**REQ-TS-1-01-127** Mobile Wallet MUST start renewal of a credential no later than the later of two moments: the lead time before its `exp` the Governance Profile sets, and the middle of its technical validity period.
- [](){ #req-ts-1-01-149 }**REQ-TS-1-01-149** Mobile Wallet MUST NOT start renewal of a credential because of its `exp` before the middle of its technical validity period.
- [](){ #req-ts-1-01-150 }**REQ-TS-1-01-150** Mobile Wallet MUST NOT start renewal of a credential because of its `exp` when that `exp` is the end of the credential's administrative validity period.
- [](){ #req-ts-1-01-128 }**REQ-TS-1-01-128** Mobile Wallet MUST sign the DPoP proof of a refresh token request with the DPoP key the refresh token is bound to.
- [](){ #req-ts-1-01-144 }**REQ-TS-1-01-144** Mobile Wallet MUST send the `attestation` proof type in every credential request of a renewal, so that renewal never needs the credential key, which only the citizen's authentication releases.
- [](){ #req-ts-1-01-145 }**REQ-TS-1-01-145** Issuer Core MUST refuse with `invalid_proof` a credential request of a renewal whose attested key differs from the key of the credential the refresh token was issued for.
- [](){ #req-ts-1-01-129 }**REQ-TS-1-01-129** Issuer Core MUST answer a refresh token request with the credential identifiers of the credential the refresh token was issued for.
- [](){ #req-ts-1-01-130 }**REQ-TS-1-01-130** Issuer Core MUST read the claims from its source system again for a renewal.
- [](){ #req-ts-1-01-131 }**REQ-TS-1-01-131** Issuer Core MUST NOT copy the claims of a renewal from the credential it replaces.
- [](){ #req-ts-1-01-132 }**REQ-TS-1-01-132** Issuer Core MUST NOT revoke a credential because it issued its renewal.
- [](){ #req-ts-1-01-154 }**REQ-TS-1-01-154** Issuer Core MUST allocate a renewal its own index.
- [](){ #req-ts-1-01-153 }**REQ-TS-1-01-153** Issuer Core MUST revoke the refresh token of a credential when it sets that credential's entry to invalid, unless the credential was revoked with the issuer's key.
- [](){ #req-ts-1-01-133 }**REQ-TS-1-01-133** Mobile Wallet MUST NOT present a refresh token again after the token endpoint refused it with `invalid_grant`.
- [](){ #req-ts-1-01-134 }**REQ-TS-1-01-134** Mobile Wallet MUST start a new issuance through the Authorization Code flow to replace a credential whose refresh token was refused.

</div>

## Errors {#ts-1-01-errors}

An endpoint that does not carry out a request answers with an error object as
[OpenID4VCI][ref-openid4vci], [RFC 6749][ref-rfc6749], and
[RFC 9449][ref-rfc9449] define one, with `error` holding a code and an
optional `error_description`. The codes come from those documents, not from
IDCTF, so the answers keep the form a wallet from outside IDCTF expects.
[The table of error codes][tbl-ts-1-01-errors] gives each code this profile
uses and when Issuer Core raises it.

[](){ #tbl-ts-1-01-errors }

<figure markdown="1" class="ekdn-table">

| Endpoint | Code | Status | Raised when |
|---|---|---|---|
| Pushed authorization request, token | `use_dpop_nonce` | `400` | [REQ-TS-1-01-086][req-ts-1-01-086] |
| Pushed authorization request, token | `invalid_dpop_proof` | `400` | [REQ-TS-1-01-087][req-ts-1-01-087], [REQ-TS-1-01-088][req-ts-1-01-088], [REQ-TS-1-01-089][req-ts-1-01-089] |
| Pushed authorization request, token | `invalid_authorization_details` | `400` | [REQ-TS-1-01-057][req-ts-1-01-057] |
| Pushed authorization request | `invalid_request` | `400` | [REQ-TS-1-01-056][req-ts-1-01-056], [REQ-TS-1-01-055][req-ts-1-01-055], or a parameter [the table of pushed authorization request parameters][tbl-ts-1-01-par-members] marks absent |
| Token | `invalid_grant` | `400` | [REQ-TS-1-01-046][req-ts-1-01-046], [REQ-TS-1-01-067][req-ts-1-01-067] to [REQ-TS-1-01-072][req-ts-1-01-072], a used code, [REQ-TS-1-01-147][req-ts-1-01-147], [REQ-TS-1-01-148][req-ts-1-01-148], a revoked refresh token |
| Token | `invalid_request` | `400` | A parameter [the table of token request parameters][tbl-ts-1-01-token-parameters] marks absent for the grant |
| Credential, deferred credential, notification | `use_dpop_nonce`, in `WWW-Authenticate` | `401` | [REQ-TS-1-01-086][req-ts-1-01-086] |
| Credential, deferred credential, notification | `invalid_dpop_proof`, in `WWW-Authenticate` | `401` | [REQ-TS-1-01-087][req-ts-1-01-087], [REQ-TS-1-01-088][req-ts-1-01-088], [REQ-TS-1-01-089][req-ts-1-01-089] |
| Credential, deferred credential, notification | `invalid_token`, in `WWW-Authenticate` | `401` | [REQ-TS-1-01-090][req-ts-1-01-090], or an access token that is unknown or expired |
| Credential | `invalid_credential_request` | `400` | [REQ-TS-1-01-106][req-ts-1-01-106], or a member [the table of credential request members][tbl-ts-1-01-request-members] marks absent |
| Credential | `unknown_credential_identifier` | `400` | [REQ-TS-1-01-100][req-ts-1-01-100] |
| Credential | `invalid_proof` | `400` | A check of [Reading it][ts-5-08-reading-it] in TS-5-08 other than the nonce fails, [REQ-TS-1-01-103][req-ts-1-01-103], [REQ-TS-1-01-105][req-ts-1-01-105], [REQ-TS-1-01-145][req-ts-1-01-145] |
| Credential | `invalid_nonce` | `400` | [REQ-TS-5-08-039][req-ts-5-08-039], [REQ-TS-5-08-040][req-ts-5-08-040], [REQ-TS-1-01-094][req-ts-1-01-094] |
| Credential, deferred credential | `credential_request_denied` | `400` | [REQ-TS-1-01-101][req-ts-1-01-101], [REQ-TS-1-01-102][req-ts-1-01-102], [REQ-TS-1-01-119][req-ts-1-01-119], [REQ-TS-1-01-152][req-ts-1-01-152], or the source system holds no eligible record |
| Deferred credential | `invalid_transaction_id` | `400` | The transaction identifier is unknown, answered, or of another grant |
| Notification | `invalid_notification_id` | `400` | The notification identifier is unknown |
| Notification | `invalid_notification_request` | `400` | A member is missing or `event` is not one of the three values |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-1-01-135 }**REQ-TS-1-01-135** Issuer Core MUST answer a request it does not carry out with the code and the status [the table of error codes][tbl-ts-1-01-errors] gives.
- [](){ #req-ts-1-01-136 }**REQ-TS-1-01-136** Issuer Core MUST ignore a parameter or member that no table of this page names, as [OpenID4VCI][ref-openid4vci] sections 6.1 and 8.2 require.
- [](){ #req-ts-1-01-137 }**REQ-TS-1-01-137** Issuer Core SHOULD say in `error_description` of `credential_request_denied`, for the wallet's developers, whether the source system holds no record for the citizen or holds one that does not meet the conditions of the type.
- [](){ #req-ts-1-01-138 }**REQ-TS-1-01-138** Issuer Core MUST NOT carry a claim of the citizen in an error.
- [](){ #req-ts-1-01-139 }**REQ-TS-1-01-139** Mobile Wallet MUST answer `invalid_nonce` by fetching a new `c_nonce` and a new Key Attestation before it asks again.
- [](){ #req-ts-1-01-140 }**REQ-TS-1-01-140** Mobile Wallet MUST NOT repeat a credential request answered with `credential_request_denied`.

</div>

A credential request whose nonce was already used, and one for a citizen the
source system does not know:

``` { .http title="400, a credential request whose nonce was used" data-format="HTTP" }
HTTP/1.1 400 Bad Request
DPoP-Nonce: jnkyu4vnuHMxuoNusb-15yGr
Cache-Control: no-store
Content-Type: application/json

{
  "error": "invalid_nonce"
}
```

``` { .http title="400, a credential request the source system refuses" data-format="HTTP" }
HTTP/1.1 400 Bad Request
DPoP-Nonce: ig4MAL-vn8YRk_KS0rWqZex9
Cache-Control: no-store
Content-Type: application/json

{
  "error": "credential_request_denied",
  "error_description": "No record of this citizen in the source system"
}
```

## Security considerations {#ts-1-01-security-considerations}

- **An offer from an issuer that is not accredited.** The wallet takes signed
  metadata only, finds the signer's DID from it, and checks the trusted list
  and the Authority Statement before the citizen types a code or signs in,
  [REQ-TS-1-01-028][req-ts-1-01-028],
  [REQ-TS-1-01-032][req-ts-1-01-032],
  [REQ-TS-1-01-033][req-ts-1-01-033], and
  [REQ-TS-1-01-035][req-ts-1-01-035].
- **An address that claims an accredited issuer's DID.** Only the holder of
  that issuer's `issuance-jose` key can sign metadata naming its DID for the
  address, [REQ-TS-1-01-030][req-ts-1-01-030] and
  [REQ-TS-1-01-031][req-ts-1-01-031], and an SD-JWT VC or an `ldp_vc`
  signed by anyone else fails at the wallet,
  [REQ-TS-1-01-110][req-ts-1-01-110]. An mdoc names its issuer through
  its Document Signer Certificate, which carries no DID, so the wallet ties it
  to the Issuer Root CA, not to the issuer the metadata named.
- **A photographed offer.** The pre-authorized code is useless without the
  transaction code, which travels by another channel and allows only the
  attempts the Governance Profile sets, [REQ-TS-1-01-047][req-ts-1-01-047] and
  [REQ-TS-1-01-072][req-ts-1-01-072], and the code works once,
  [REQ-TS-1-01-045][req-ts-1-01-045].
- **An authorization code caught in the browser.** It is redeemed only with
  the PKCE verifier and under the DPoP key it was bound to,
  [REQ-TS-1-01-067][req-ts-1-01-067] and
  [REQ-TS-1-01-070][req-ts-1-01-070], and the authorization
  request never travels through the browser,
  [REQ-TS-1-01-051][req-ts-1-01-051].
- **A code from one issuer handed back to another.** The authorization
  response names its issuer and the wallet checks it,
  [REQ-TS-1-01-062][req-ts-1-01-062] and
  [REQ-TS-1-01-063][req-ts-1-01-063].
- **A stolen access token or refresh token.** Every token is bound to a DPoP
  key that never leaves the installation,
  [REQ-TS-1-01-073][req-ts-1-01-073],
  [REQ-TS-1-01-082][req-ts-1-01-082], and
  [REQ-TS-1-01-090][req-ts-1-01-090], and a proof cannot be
  made ahead of time or replayed,
  [REQ-TS-1-01-086][req-ts-1-01-086] and
  [REQ-TS-1-01-087][req-ts-1-01-087].
- **A wallet that is not what it claims.** The wallet does not authenticate as
  a client, [REQ-TS-1-01-065][req-ts-1-01-065]. What
  stands in for it is the Key Attestation at the credential request, signed by
  a Wallet Provider the trusted list carries,
  [REQ-TS-1-01-098][req-ts-1-01-098] and
  [REQ-TS-1-01-099][req-ts-1-01-099]. An issuer therefore learns
  that the wallet is genuine when the key is handed over and not at the token
  endpoint; with the transaction code or the citizen's sign-in in front of it,
  that is enough.
- **A suspended issuer that keeps issuing.** It checks its own entry and its
  own permission before it signs,
  [REQ-TS-1-01-101][req-ts-1-01-101] and
  [REQ-TS-1-01-102][req-ts-1-01-102].
- **One credential put together from two citizens or two keys.** Every
  identifier of one access token is tied to one credential of one citizen,
  and every representation to one key,
  [REQ-TS-1-01-078][req-ts-1-01-078] and
  [REQ-TS-1-01-105][req-ts-1-01-105].
- **A credential read off the wire.** The channel is TLS to the issuer's own
  endpoint, [REQ-TS-1-01-003][req-ts-1-01-003]. The credential is not
  encrypted to the wallet as well, so whatever stands in front of Issuer Core
  at the issuer, a reverse proxy or a gateway, sees the credential, and is the
  issuer's own to secure.

## Privacy considerations {#ts-1-01-privacy-considerations}

An issuer learns which Wallet Provider a citizen uses, from the Key Attestation,
and the credential key, which it writes into the credential. It learns no
identifier of the installation or the device, as
[What it does not carry][ts-5-08-what-it-does-not-carry] in TS-5-08 fixes. The
DPoP key is one per issuer, so it gives two issuers nothing to compare. The
credential key is the same at every issuer, as
[the credential key][the-credential-key] accepts, and a DPoP key per issuer adds
no link of its own.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-1-01-141 }**REQ-TS-1-01-141** Issuer Core MUST NOT keep the claims of a credential after it has answered every credential identifier of the grant, or after the grant has ended.
- [](){ #req-ts-1-01-142 }**REQ-TS-1-01-142** Mobile Wallet MUST NOT send an identifier of the citizen, a claim, or a credential of another issuer to the token, credential, or deferred credential endpoint.

</div>

The notification says whether a credential reached the wallet and nothing
about how the citizen uses it, [REQ-TS-1-01-123][req-ts-1-01-123]
and [REQ-TS-1-01-125][req-ts-1-01-125], and the issuer never
contacts the wallet, [REQ-TS-1-01-007][req-ts-1-01-007].

## Changelog {#ts-1-01-changelog}

<figure markdown="1" class="ekdn-table">

| Version | Date | Change |
|---|---|---|
| 1.0 draft | 21 October 2026 | First draft |

</figure>
