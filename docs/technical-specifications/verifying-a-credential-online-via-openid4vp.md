---
title: "[TS-3-01] Verifying a credential online via OpenID4VP"
description: The OpenID4VP profile Verifier Core exposes and Mobile Wallet answers, from the authorization request in a QR code, through the signed Request Object and the checks a wallet runs on it, to the encrypted response, the relay a merchant's check runs through, and the errors.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §4.5, §7.3, §7.5, §9.3, Kep. 29, Kep. 30; JWT di OpenID4VCI dan OpenID4VP, bagian OpenID4VP; Peta Alur Penerbitan dan Presentasi §3.1, §3.2, §6; Rincian Module dan Operasi §7.3; OpenID4VP 1.0; OpenID4VC HAIP 1.0; RFC 9101; RFC 7516; RFC 7518; tracks/0074, tracks/0093, tracks/0096, tracks/0265, tracks/0348, tracks/0350, tracks/0352, tracks/0380, tracks/0369, tracks/0370 -->

<p class="ekdn-docid">TS-3-01</p>

# Verifying a credential online via OpenID4VP {#ts-3-01-verifying-a-credential-online-via-openid4vp}

<p class="ekdn-lead" markdown="span">
Online verification is the exchange in which a verifier asks a citizen's
wallet for a credential over the internet. This specification fixes how
Verifier Core and Mobile Wallet run it: how the request reaches the wallet,
what the signed request carries and how the wallet checks it, and how the
answer comes back encrypted to the verifier alone.
</p>

Every sentence on this page binds Verifier Core, which asks, Mobile Verifier,
which asks online through a relay, and Mobile Wallet, which answers, and an
Assessment Body tests them against it in the version the Governance Profile
puts in force. The key words and the identifier `REQ-TS-3-01-nnn` follow
[Common provisions](common-provisions.md).

## Who runs this and what it needs {#ts-3-01-who-runs-this-and-what-it-needs}

This specification fixes the profile of
[OpenID for Verifiable Presentations (OpenID4VP) 1.0][ref-openid4vp] that
IDCTF runs:

- The authorization request a wallet receives.
- The signed Request Object behind it and how the wallet fetches it.
- The two Client Identifier Prefixes a verifier introduces itself with.
- The checks the wallet runs before the citizen is asked.
- The response mode and its encryption.
- The answer at the response endpoint.
- The relay through which a merchant's device asks.
- The errors.

Its conformance targets are:

- Verifier Core, which runs as the remote Relying Party Instance of a Relying
  Party or an RP Intermediary and relays a merchant's request and response,
  as [Relying Party Instance][relying-party-instance] sets out.
- Mobile Verifier, as
  [Mobile Verifier to Verifier Core][mobile-verifier-to-verifier-core] sets
  out.
- Mobile Wallet.

It leaves to other documents:

- The presentation itself, which claims travel, the proof of the credential key,
  and the checks a verifier runs on both, which
  [Building and verifying a presentation](building-and-verifying-a-presentation.md)
  holds.
- The Use Statement a request carries in `verifier_info` and the checks a
  wallet runs on it, which
  [Registering and carrying a Use Statement](registering-and-carrying-a-use-statement.md)
  holds.
- How a signer under a Decentralized Identifier (DID) names its key and how a
  reader finds it, which
  [Finding a signer's key from its DID](finding-a-signers-key-from-its-did.md)
  holds.
- The Verifier Device Certificate, its `ReaderAuthRole`, and how a chain to
  the Verifier Root CA is validated, which
  [Issuing and validating the X.509 certificates and the VICAL](issuing-and-validating-the-x509-certificates-and-the-vical.md)
  holds.
- The trusted list and the Authority Statement a wallet reads to decide
  whether a verifier may ask at all, which
  [Publishing and reading the trusted list](publishing-and-reading-the-trusted-list.md)
  and [Answering with an Authority Statement](answering-with-an-authority-statement.md)
  hold.
- The proximity exchange, which
  [Verifying a credential in proximity via ISO/IEC 18013-5](verifying-a-credential-in-proximity-via-iso-iec-18013-5.md)
  holds.
- The session through which Verifier Core hands the result to the
  Relying Party's business system, which carries no ecosystem artifact, as
  [verifier to business system][verifier-to-business-system] sets out.
- [What a merchant does with the data it receives][gf-what-a-merchant-does-with-what-it-is-shown],
  which the Governance Framework holds.
- The numbers, which the Governance Profile holds:
    - The lifetime of a Request Object.
    - The time a relay holds a response nobody collected.
    - The time Verifier Core keeps the record of a relayed request.
    - The algorithms a Request Object key, an issuance key, and a credential key
      may use.

The profile follows the
[OpenID4VC High Assurance Interoperability Profile (HAIP) 1.0][ref-openid4vc-haip],
which IDCTF reads as a comparison and is not bound by, except in these
places:

- A Relying Party and an RP Intermediary introduce themselves with the
  `decentralized_identifier` prefix and their `did:webvh`, where HAIP asks
  for `x509_hash` on every signed request. Only a merchant uses `x509_hash`,
  because it has no DID, as
  [Wallet to Verifier, online][wallet-to-verifier-online] sets out.
- A response is encrypted with `ECDH-ES` and `A128GCM` alone, the key
  agreement OpenID4VP fixes for an encrypted response and its default
  content encryption, where HAIP asks a verifier to offer `A256GCM` as well.
  Neither is a Governance Profile member, because both come from the
  protocol.
- A verifier may ask across devices, from a QR code, where HAIP recommends
  the same-device flow alone.
- Mobile Verifier asks across devices only, where HAIP requires every
  verifier to support the same-device flow. Where Verifier Core asks on the
  same device it runs the redirect HAIP requires.
- A credential query carries no `trusted_authorities`, which HAIP requires a
  verifier to support, because the trusted list decides which issuers a
  verifier accepts.
- The presented SD-JWT-based Verifiable Credential (SD-JWT VC) draft -13
  names its issuer's key by `kid` and not by the `x5c` HAIP requires, as
  [Issuing a credential via OpenID4VCI](issuing-a-credential-via-openid4vci.md)
  records.

Appendix A of OpenID4VP, which runs the exchange over a platform credential
interface, is not used.

Before the first exchange, each target holds what the rules below assume:

- **Verifier Core** holds:
    - An entry in the trusted list whose Relying Party service reads
      `granted`, which is the role an RP Intermediary is accredited in as
      well.
    - Its Request Object key in its DID Document under the purpose
      `request-object`.
    - The Use Statement of every use it runs.
    - Where it vouches for reader devices, its Verifier Issuing CA and a
      public address of its own for the relay.
- **Mobile Verifier** holds its device key in the secure element it was
  generated in, its Verifier Device Certificate, and the category Use Statements
  its device is bound to, all handed over at provisioning.
- **Mobile Wallet** holds:
    - The credentials of the citizen with their disclosures.
    - The credential key in its secure storage.
    - The Verifier Root CA, from build time.
    - What its [trust cache sync][trust-cache-sync] fetched: the trusted list,
      the Authority Statements, every entity's `did:webvh` log, the
      certificate revocation lists (CRLs), and the Use Statement status list.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-3-01-001 }**REQ-TS-3-01-001** Verifier Core MUST meet every requirement on this page that names Verifier Core, and every requirement on what Verifier Core writes: its authorization requests, its Request Objects, and its answers.
- [](){ #req-ts-3-01-002 }**REQ-TS-3-01-002** Mobile Verifier MUST meet every requirement on this page that names Mobile Verifier, and every requirement on what Mobile Verifier writes: its authorization requests and the Request Objects it signs.
- [](){ #req-ts-3-01-003 }**REQ-TS-3-01-003** Mobile Wallet MUST meet every requirement on this page that names Mobile Wallet, and every requirement on what Mobile Wallet sends: its fetch of a Request Object and its responses.

</div>

## What online verification does {#ts-3-01-what-online-verification-does}

A verifier asks for the claims a registered use allows, and a citizen
answers from their wallet with a presentation bound to that one request. One
protocol carries both representations that travel online, an SD-JWT VC
and an `ldp_vc`; an mdoc is presented in proximity only, as
[online and offline][online-and-offline] sets out.

The verifier proves who it is before the citizen sees anything. It signs the
request, a JSON Web Token (JWT), and the shape of its `client_id` tells the
wallet how to check that signature. A Relying Party and an RP Intermediary sign
with the Request Object key their DID Document lists, and the wallet finds that
key in its own cache. A merchant signs with the device key its
Verifier Device Certificate certifies, and the wallet validates that certificate
up to the Verifier Root CA it carries from build time. Either way, the wallet
reads from the same cache whether the verifier is accredited and what it
registered the request for, and the network carries nothing beyond the request
and the answer.

The answer travels encrypted as a JSON Web Encryption (JWE) to a key the
verifier drew for that one request and named in its signed request, as
[a Relying Party's keys][a-relying-partys-keys] and
[keys on devices][keys-on-devices] set out. A merchant's device draws that
key itself and keeps it, so the RP Intermediary whose Verifier Core relays
the answer holds ciphertext it cannot open, as
[verification by a merchant][verification-by-a-merchant] sets out.

## The exchange {#ts-3-01-the-exchange}

An online verification runs in nine steps.

1. The verifier builds and signs a Request Object for one transaction, and
   places it at a request Uniform Resource Identifier (URI). Verifier Core holds its own; Mobile Verifier
   leaves its own with the relay.
2. The verifier shows Mobile Wallet an authorization request carrying
   `client_id` and `request_uri`, as a QR code, or as a link on the device
   the wallet runs on.
3. Mobile Wallet fetches the Request Object from the request URI.
4. It checks the signature by the prefix of `client_id`, the verifier's
   standing in its cached trusted list, the verifier's permissions, and the
   Use Statement in `verifier_info`. It refuses the request if any fails.
5. It shows the citizen the requester and the registered purpose, and the
   citizen approves the request whole or refuses it.
6. It builds the presentation, encrypts the response to the key in
   `client_metadata`, and posts it to `response_uri`.
7. The response endpoint answers the wallet, with a redirect where the
   request was opened on the same device.
8. The verifier decrypts the response, matches it to the request by `state`,
   and verifies the presentation.
9. Verifier Core hands the result to the business system that asked.
   Mobile Verifier collects the ciphertext from the relay, and decrypts and
   verifies it on the merchant's device.

## An exchange, as exchanged {#ts-3-01-an-exchange-as-exchanged}

The citizen, the verifier, its domain, the merchant, and every key are
invented, and no transaction has taken place. Every field is exact.

The examples agree with the pages that show the same parties and artifacts:

- The verifier is the Relying Party [the trusted list][ts-5-01-trusted-list-payload]
  carries, with the same DID.
- The merchant's device is the one whose Verifier Device Certificate
  [Issuing and validating the X.509 certificates and the VICAL](issuing-and-validating-the-x509-certificates-and-the-vical.md)
  shows.
- Each Request Object verifies, and each response decrypts, under the key its
  header names.
- Each presentation is the Kartu ASN that
  [Issuing a credential in SD-JWT VC, mdoc, and `ldp_vc`](issuing-a-credential-in-sd-jwt-vc-mdoc-and-ldp-vc.md)
  issues.

Request identifiers, `state` values, and response codes are opaque strings
the verifier drew; nothing reads them but the verifier that drew them.

### The Kartu ASN, from a Relying Party {#ts-3-01-the-kartu-asn-from-a-relying-party}

Terminal Nusantara checks a civil servant's status for the official travel
fare. Its Verifier Core builds the Request Object
[carrying it online][ts-5-06-carrying-it-online] publishes, places it at a
request URI of its own, and shows a QR code at the ticket counter. The QR
code carries the authorization request:

``` { .text title="The authorization request in the QR code" data-format="URL" }
openid4vp://?client_id=decentralized_identifier%3Adid%3Awebvh%3AQmUATC5jyf5yVy72GYAp8nSvuwshzDy6wYX7WmNY5UJtXT%3Aterminal-nusantara.co.id&request_uri=https%3A%2F%2Fterminal-nusantara.co.id%2Fpresentation%2Frequest%2F9vbqGNHdLrd781dSqQvJtQ
```

The wallet fetches the Request Object:

``` { .http title="GET of the request URI" data-format="HTTP" }
GET /presentation/request/9vbqGNHdLrd781dSqQvJtQ HTTP/1.1
Host: terminal-nusantara.co.id
Accept: application/oauth-authz-req+jwt
```

``` { .http title="200, the signed Request Object" data-format="HTTP" }
HTTP/1.1 200 OK
Content-Type: application/oauth-authz-req+jwt
Cache-Control: no-store

eyJ0eXAiOiJvYXV0aC1hdXRoei1yZXErand0IiwiYWxnIjoiRVMyNTYiLCJraWQiOiJkaWQ6d2Vidmg6UW1VQVRDNWp5ZjV5Vnk3MkdZQXA4blN2dXdzaHpEeTZ3WVg3V21OWTVVSnRYVDp0ZXJtaW5hbC1udXNhbnRhcmEuY28uaWQjcmVxdWVzdC1vYmplY3QtMSJ9.eyJjbGllbnRfaWQiOiJkZWNlbnRyYWxpemVkX2lkZW50aWZpZXI6ZGlkOndlYnZoOlFtVUFUQzVqeWY1eVZ5NzJHWUFwOG5TdnV3c2h6RHk2d1lYN1dtTlk1VUp0WFQ6dGVybWluYWwtbnVzYW50YXJhLmNvLmlkIiwiYXVkIjoiaHR0cHM6Ly9zZWxmLWlzc3VlZC5tZS92MiIsInJlc3BvbnNlX3R5cGUiOiJ2cF90b2tlbiIsInJlc3BvbnNlX21vZGUiOiJkaXJlY3RfcG9zdC5qd3QiLCJyZXNwb25zZV91cmkiOiJodHRwczovL3Rlcm1pbmFsLW51c2FudGFyYS5jby5pZC9wcmVzZW50YXRpb24vcmVzcG9uc2UiLCJjbGllbnRfbWV0YWRhdGEiOnsiandrcyI6eyJrZXlzIjpbeyJrdHkiOiJFQyIsImNydiI6IlAtMjU2IiwieCI6IlR2ejVQYTlQSnl1LVBDWV9hVXQ5TXNYSm5QX0Fhem4wdllXUjdtOEg4TU0iLCJ5Ijoibm1VelFJbTVGX05XZUNRYVh4ZWJudnlqTGZuRDQtV3RnVlRoSjU1MDJ3ayIsInVzZSI6ImVuYyIsImFsZyI6IkVDREgtRVMiLCJraWQiOiJvTWd1cmFvSzk1WUFLU0pMc3dYM2FMd2Y5U0hZSlRDUzlBRzJnMzdORlE0In1dfSwidnBfZm9ybWF0c19zdXBwb3J0ZWQiOnsiZGMrc2Qtand0Ijp7InNkLWp3dF9hbGdfdmFsdWVzIjpbIkVTMjU2Il0sImtiLWp3dF9hbGdfdmFsdWVzIjpbIkVTMjU2Il19LCJsZHBfdmMiOnsicHJvb2ZfdHlwZV92YWx1ZXMiOlsiRGF0YUludGVncml0eVByb29mIl0sImNyeXB0b3N1aXRlX3ZhbHVlcyI6WyJlY2RzYS1yZGZjLTIwMTkiXX19fSwibm9uY2UiOiJsREJ0QUpDSWtFaGRITXZLMFZwNnJRIiwic3RhdGUiOiJMTXZIWEJtUDlrb2g1TEtRYlFjdjZBIiwiZGNxbF9xdWVyeSI6eyJjcmVkZW50aWFscyI6W3siaWQiOiJrYXJ0dS1hc24iLCJmb3JtYXQiOiJkYytzZC1qd3QiLCJtZXRhIjp7InZjdF92YWx1ZXMiOlsiaWQuaWRjdGYua2FydHUtYXNuLjEiXX0sImNsYWltcyI6W3siaWQiOiJuYW1hIiwicGF0aCI6WyJuYW1hIl19LHsiaWQiOiJuaXAiLCJwYXRoIjpbIm5pcCJdfSx7ImlkIjoiaW5zdGFuc2kiLCJwYXRoIjpbImluc3RhbnNpIl19XSwiY2xhaW1fc2V0cyI6W1sibmFtYSIsImluc3RhbnNpIl0sWyJuYW1hIiwibmlwIiwiaW5zdGFuc2kiXV19XX0sInZlcmlmaWVyX2luZm8iOlt7ImZvcm1hdCI6InZuZC5pZC5pZGN0Zi51c2Utc3RhdGVtZW50K2p3dCIsImRhdGEiOiJleUowZVhBaU9pSjJibVF1YVdRdWFXUmpkR1l1ZFhObExYTjBZWFJsYldWdWRDdHFkM1FpTENKaGJHY2lPaUpGVXpJMU5pSXNJbXRwWkNJNkltUnBaRHAzWldKMmFEcFJiVnBxZVRGME9XOUdhV0ZHYW1oWU1tVXpPSFZOZFZJM2JXZDBaRXhxU0ZCTlIyWnFSV1oyY25OdFlXbHhPblJ5ZFhOMExtZHZMbWxrSTNWelpTMXpkR0YwWlcxbGJuUXRNU0o5LmV5SnBjM01pT2lKa2FXUTZkMlZpZG1nNlVXMWFhbmt4ZERsdlJtbGhSbXBvV0RKbE16aDFUWFZTTjIxbmRHUk1ha2hRVFVkbWFrVm1kbkp6YldGcGNUcDBjblZ6ZEM1bmJ5NXBaQ0lzSW5OMVlpSTZJbVJwWkRwM1pXSjJhRHBSYlZWQlZFTTFhbmxtTlhsV2VUY3lSMWxCY0RodVUzWjFkM05vZWtSNU5uZFpXRGRYYlU1Wk5WVktkRmhVT25SbGNtMXBibUZzTFc1MWMyRnVkR0Z5WVM1amJ5NXBaQ0lzSW5WelpWOXBaQ0k2SW5SaGNtbG1MV1JwYm1GekxXRnpiaUlzSW5CMWNuQnZjMlVpT25zaWFXUWlPaUpXWlhKcFptbHJZWE5wSUhOMFlYUjFjeUJCVTA0Z2RXNTBkV3NnZEdGeWFXWWdjR1Z5YW1Gc1lXNWhiaUJrYVc1aGN5SXNJbVZ1SWpvaVEybDJhV3dnYzJWeWRtRnVkQ0J6ZEdGMGRYTWdZMmhsWTJzZ1ptOXlJSFJvWlNCdlptWnBZMmxoYkNCMGNtRjJaV3dnWm1GeVpTSjlMQ0pzWldkaGJGOWlZWE5wY3lJNklsQmxjbXBoYm1wcFlXNGdhMlZ5YW1FZ2MyRnRZU0IwWVhKcFppQndaWEpxWVd4aGJtRnVJR1JwYm1GeklHUmxibWRoYmlCcGJuTjBZVzV6YVNCd1pXMWxjbWx1ZEdGb0lpd2lZMnhoYVcxeklqcGJJbWxrTG1sa1kzUm1MbXRoY25SMUxXRnpiaTR4STI1aGJXRWlMQ0pwWkM1cFpHTjBaaTVyWVhKMGRTMWhjMjR1TVNOdWFYQWlMQ0pwWkM1cFpHTjBaaTVyWVhKMGRTMWhjMjR1TVNOcGJuTjBZVzV6YVNKZExDSnpkR0YwZFhNaU9uc2ljM1JoZEhWelgyeHBjM1FpT25zaWFXUjRJam8yTXpVd0xDSjFjbWtpT2lKb2RIUndjem92TDNKbFoybHpkSEo1TG5SeWRYTjBMbWR2TG1sa0wzTjBZWFIxY3k5MWMyVXRjM1JoZEdWdFpXNTBjeTB4SW4xOUxDSnBZWFFpT2pFM09EQXlOekl3TURBc0ltVjRjQ0k2TVRneE1UZ3dPREF3TUgwLlJDbm5XWFA4LXBIYzRQckFoM3F0Yy1zU3hGWERjMW1uLVllcFExRVo2Rk5zTzJHN0JJMnlUa2JDS05Ib2tyd2ZKNzhrM2lrY1E4U1BwaGFEdldBYWNnIn1dLCJpYXQiOjE3OTIyMjEyNDAsImV4cCI6MTc5MjIyMTU0MH0.SFLsmnRDOK_-fyIDjznRy3Ad-HDYqeRtMe9Bz9RGKpsnJhE8YALkhJtkCLW2X8l6Sa7veTCIrRoZbhXFjHqFIg
```

The protected header names the Request Object key in Terminal Nusantara's
DID Document, and its claims are the ones
[carrying it online][ts-5-06-carrying-it-online] shows:

``` { .json title="Protected header of the Request Object" data-format="JSON" }
{
  "typ": "oauth-authz-req+jwt",
  "alg": "ES256",
  "kid": "did:webvh:QmUATC5jyf5yVy72GYAp8nSvuwshzDy6wYX7WmNY5UJtXT:terminal-nusantara.co.id#request-object-1"
}
```

The wallet checks the request, the citizen approves it, the wallet answers
the first option of its `claim_sets`, and posts the encrypted response to `response_uri`:

``` { .http title="POST of the encrypted response" data-format="HTTP" }
POST /presentation/response HTTP/1.1
Host: terminal-nusantara.co.id
Content-Type: application/x-www-form-urlencoded

response=eyJhbGciOiJFQ0RILUVTIiwiZW5jIjoiQTEyOEdDTSIsImtpZCI6Im9NZ3VyYW9LOTVZQUtTSkxzd1gzYUx3ZjlTSFlKVENTOUFHMmczN05GUTQiLCJlcGsiOnsia3R5IjoiRUMiLCJjcnYiOiJQLTI1NiIsIngiOiI3QS1lM0g4dC1LRE1fdksxTV8teUo0Ukk2TzNzQXRhUmFDTEhfcXpsSEs4IiwieSI6IlVtRl9SVkRTTERPNXMxa0g1YnJWOEx6RTFRWlhnU3pnaUg2OUEwXzdvYzgifX0..9ba13_BN3YtPO-Ld.pNlYlx4usPOX0cB-V1ZfhMQ1ykFq4j8mjQLlghvS98Z00Ma_D_UKoJOGGquMpf6ytgDiK-ZCYotr3dpvIbourr20eYbNj99aT9-Sus24ZGh3_KjL6RHULAnYRLiKzzZa1VtrOjbnx5dmTSotOKpsFpnUoc9aOhkWorAaD0RZUGTZmi5qLqY8DXdPBqAa-THE9kbwUv1D3f3DovgZps5CApjO6fvYOWs6EL4dGw1yYpYdUV9bSbB0sVsknU9W72qCAiNjvw-l8dyETrGMO0Om3hujWi2ZZjCAbKTVw52fplFK9avpz0o3OkvmtSVZLuj2eO73a2Gs6mMC1N5LKCPKgiTN5JhP0cona_wNzmZvjUAZBrvTxivVNkO4PFmy6AbxCcqijejIVfaYjX1lPD-wILwq7MM9f-BR6_e1lb0JrMPSZbpdetk8C5UervOk8hGmcmU4T7zWBHonEySnZadwPFBiKBlkKYCfv7P3ct0OyZl_jNYbDajf90XZ-DUI9BDXIhrqWVXLG2zJ9oAxin-JihcVjwz3iF71n8l6H0nAI2hhZLDd8RPgM_4BU_yGZJMmiiS7nwU8YRyR_vt5Xaoq5QarZlTwlZWAscZUdd8cP7G7F1GSWdQir2onAYkWGzh9GNDaXW3nOSQMOPFG5-h1spnHq7YDSaa0Y4Kjb74VAygNV7pwijfHNG5Pf1_GiHxF-b3tlwaFrEw7F7ueXgMa0fOuPn68eAV_Mobk0fS3Pee5oVi566pCiSLyQlXBaNy556zH5-FISjX7AnGZC4I_uTGL4j6shnyoVZJkfnEMGbTpL-7oAmViIuLIlxQG0NlWdSq76qjzt7St5QLzTcbf2LHBOIgKGedQ_D1tP-iPBBOSyzMtkcjMeB3Om52AuJ_fo8pmX5tMALXJBzOQNT3mRZ09yBkdwL1oRljuWxg0x0MXU7qjWDKuD_p-l2hADFca0KziqK4C3hCk6VKokhVEgs009sjgCDH_Q2ukO4MEi91hZNsBzZtI3DuEKkNqyy2_tGYxBraiymfVLSPmu2O87pk2n-XjvUXRB-uxPWDGKTvN4yA77qAUBA9i_Z_Hx7ytDKSZSXVrY3vm1cRdNUzkqtjBF3GytBL3bZEL9iTkwA2fpt9RrzdBXnn33e5KZqCx83lwbouddsDxYD7kwjxHtp962g0YPcJ4F2OkB7MT1Dw9iQnMhwC3jXg5Pe3q8ffugCuTw6VI7upMDBKwHKch0Nxz0ZicDnZHyPbVSJkuelzxP0E68o3pMUyeMUliNHtg3-Lxt4XZs9s23-yuoBnM2kYz1vVHcQVjDJr6cTwazvkTNE6rDsAKrRpq-vE18xF2xn5fQNJTBP5sqE9z4ykKke5wILAq67x5jzdn38hVb19G9q7BGiINSzOP4zWaHaKwV_7812c7QNWpTRsxkvXbdUP9j0o8J_HOqSJNwqCYIOzuHtADL0p3eJiEeMnrVr-HSS6ewOanvLQK8R0uy9avB8cD_9F0dYFiqJu6V4sxZ49cqDM1a5qSeRJKKwudFE1SDa62EQNshakFaJ2hrOX1IE-oemF-UCpJ9cf9wxWotoFAqQbov0ClVUVu8UDZ5UjjIXt1elnrK9fKRA7oXSRZU8q3KOslANj8X_jhBDfcfzsKuCQDcx2Z-KzOwelmrLMqXRwR0Z98z4Uz6PKcwGG79rzXe8GstfcsMfr3pJs429pcypbPENTJCQB23R7PTkO1-8HjHfAPlh5mZWwuDZm-PUxOWqLhPORSfvtpHcLsau29H6rOkLiO1j4-8iYvhAF0XM_Iw_T6QhaHyG_WH9rWyTlgElkYLQKWldgod-P3B3Aqqm0Ya7ooAhkIxXlVG48zat4orlEyYTDkRelxjyxzJjLkI1nXnCQYaN9gOSjP9IZy-jrsF0gz3uHkOUA2A513LQ1glyZV45owCKAUVSyMyCPFLZ7zgWL3TpNPbmJALIw4PwUa5yo8H7xpS_2pwzaODvsDp-I6QZWseJYO8YRFViPdA59h8bSGnxcqv0QLrC9bnE3wdqwxkc9D5VyvbPUKk97IuMS6mWQQlYjtQeEbZ06yInEwEU33cVVJHICwG1dw9EVV4zFGpXcKaz2YlWa64UcZJO2Xk9mCDppOQlaiA6bjFymJypGXtV5pZBBE7Z83JC-WY7mYs1EpODKcJogzMtQkjZXVfEYkSMHMZcJqRvaW1XkdIvrJbZ3FtFZGdQ1lIPZBjh2Ih7Y5c2xKtU_eC-NLQ6C7empJycPPt-kNZtO3ZFKSG9A5IyE46DedhhFWxMvjo26gckhyD8tbjpMP89XJXWh0ZQUTRrxzNap6YkThcAr0qBZRgt_LQMbgvPCflP4R04SE50gllI3fikyc021hZIBNRZ_eWpSt9pXLdX5KcNaNd-GY4mvfBTEvlgWDKN2q71PzC6nZBQ41RPWrlP0m8bJ5guKDYmCT0II_UZmEUoSQtKbOnNEhFmSKEujj77dJ306O1CBAq5MWjrdAQHSPc6w7HwCW7otFG1_vg4tW92sHbUoUxuTPGQRaVxV7WrXY4B8NOF_3UVHbge-fXu7iD0B_vk_AAdDuVopT7HiPYbxdylRFRjv-.adjEA6B1FUSqF93_jQW-Eg
```

``` { .json title="Protected header of the encrypted response" data-format="JSON" }
{
  "alg": "ECDH-ES",
  "enc": "A128GCM",
  "kid": "oMguraoK95YAKSJLswX3aLwf9SHYJTCS9AG2g37NFQ4",
  "epk": {
    "kty": "EC",
    "crv": "P-256",
    "x": "7A-e3H8t-KDM_vK1M_-yJ4RI6O3sAtaRaCLH_qzlHK8",
    "y": "UmF_RVDSLDO5s1kH5brV8LzE1QZXgSzgiH69A0_7oc8"
  }
}
```

Decrypted with the private half of the key Verifier Core drew for this
request, which it then discards, the response carries the
`vp_token` [an SD-JWT VC presentation][ts-5-11-an-sd-jwt-vc-presentation]
shows, and the `state` of the request:

``` { .json title="The response, decrypted" data-format="JSON" }
{
  "vp_token": {
    "kartu-asn": [
      "eyJ0eXAiOiJkYytzZC1qd3QiLCJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDp3ZWJ2aDpRbWU4UnJpR25LeDVqMlFqb2FZMVNnUlNweFRIZGpxMTFMMkV4Z3kxelYyeHNKOmJrbi5nby5pZCNpc3N1YW5jZS1qb3NlLTEifQ.eyJpc3MiOiJkaWQ6d2Vidmg6UW1lOFJyaUduS3g1ajJRam9hWTFTZ1JTcHhUSGRqcTExTDJFeGd5MXpWMnhzSjpia24uZ28uaWQiLCJ2Y3QiOiJpZC5pZGN0Zi5rYXJ0dS1hc24uMSIsImNuZiI6eyJqd2siOnsia3R5IjoiRUMiLCJjcnYiOiJQLTI1NiIsIngiOiIzQ09oeE9lT3hwQk9qVUpncVdTQVUwUUFBWWFZZ3VnUFZKXzJYMnFHZGtjIiwieSI6IjJrOTg4NTRwQjc3dWRkUnZlOE80a2c1bklQVDdFakVncGJlS3FXTHVNRUUifX0sIl9zZF9hbGciOiJzaGEtMjU2IiwiX3NkIjpbIjF6QTdMcXNPdGJoTFZRaG9fUlNlMFRHcVJyZmctUzU4SlpHV1NmZzZabU0iLCJDZnVRdi1jS3JnemYwdXpIeHUtVEJFQkp2dFo0UEE3U0RhVjloOFQ5TF9RIiwiRVQ5QmlsbFV3VmRoYkhjNnRmXy0xWEFDRWdWUDRiX2lVUHhIQ2FYQlNiYyIsIkhMeVU4aHRZWno0TmkyZlJkN3BTWWRpQ2JCLXF0NDhwQlM5aDJCR013VFEiLCJlNlVoQk44QXk1emRVUGdDX2htbnBXbGR3QnhpWDhGN2tPVzRuUklwNXdNIiwiZkFoREt6VjNVMzlqQzZiN0dMaEdGRGw3NnVnVy1tN0R6N1hxcUJuamxkYyIsImhLTUpsakZJTlQtd0ljUDhFUnJhWURrSExyMjZPWUJTQUlHS0ItMG5ORzgiLCJ3N0MxZXJCNno4OG1oRVZzTm5hUVlEZ2JacUNIakxsM2NieDFFemllUnFzIl0sInN0YXR1cyI6eyJzdGF0dXNfbGlzdCI6eyJpZHgiOjQ4MTkyMCwidXJpIjoiaHR0cHM6Ly9ia24uZ28uaWQvc3RhdHVzL2thcnR1LWFzbi0xIn19LCJuYmYiOjE3OTIyMTY4MTAsImlhdCI6MTc5MjIxNjgxMCwiZXhwIjoxODIzNzUyODEwfQ.Rtt14iNH1COHmkwCwvzkYcg2RftZdls7V1WghZc1xZC3GmENzivjroJTPBu2C83Qy4pbdbNsX0lorDW26kbPLg~WyJ3SXVNc2VoQTM1UEp0RU1yUzRub0NRIiwibmFtYSIsIkJ1ZGkgU2FudG9zbyBXaWNha3Nvbm8iXQ~WyJSb1o4SHRpMk9JVkJ4NHlNd3Q0UkZRIiwiaW5zdGFuc2kiLCJCYWRhbiBLZXBlZ2F3YWlhbiBOZWdhcmEiXQ~eyJ0eXAiOiJrYitqd3QiLCJhbGciOiJFUzI1NiJ9.eyJpYXQiOjE3OTIyMjEzMDAsImF1ZCI6ImRlY2VudHJhbGl6ZWRfaWRlbnRpZmllcjpkaWQ6d2Vidmg6UW1VQVRDNWp5ZjV5Vnk3MkdZQXA4blN2dXdzaHpEeTZ3WVg3V21OWTVVSnRYVDp0ZXJtaW5hbC1udXNhbnRhcmEuY28uaWQiLCJub25jZSI6ImxEQnRBSkNJa0VoZEhNdkswVnA2clEiLCJzZF9oYXNoIjoiNEtCeEdNWUwwVk5rMjk2bDVBYW03TW8yN3czd2VzZk45LW5JVUNCZEh6ZyJ9.VX1bqErPuXtjNRRHFLYG3Si5LTdc4xUfeYgvq_WnpfGx8SnHio0C9pxEfDhhGEJ_603yMcH9Ygm8J4EK0ooBKw"
    ]
  },
  "state": "LMvHXBmP9koh5LKQbQcv6A"
}
```

The QR code was read across devices, so Verifier Core answers with an empty
object:

``` { .http title="200, the response received" data-format="HTTP" }
HTTP/1.1 200 OK
Content-Type: application/json
Cache-Control: no-store

{}
```

Had the citizen opened the same request from a link on their own phone,
Verifier Core would have answered with a redirect carrying a response code,
which the browser session that started the request presents before Verifier
Core hands it the result:

``` { .http title="200, the response received on the same device" data-format="HTTP" }
HTTP/1.1 200 OK
Content-Type: application/json
Cache-Control: no-store

{
  "redirect_uri": "https://terminal-nusantara.co.id/presentation/done#response_code=l6vA73NPFTCvmWg6kTQLPA"
}
```

Had the citizen refused the Kartu Nikah request
[carrying it online][ts-5-06-carrying-it-online] publishes, the wallet would
have posted, encrypted the same way, a response carrying an error and that
request's `state` alone:

``` { .json title="The response of a citizen who refuses, decrypted" data-format="JSON" }
{
  "error": "access_denied",
  "state": "407uibewmpIt7GXwpP4eHA"
}
```

### The Kartu ASN, from a merchant {#ts-3-01-the-kartu-asn-from-a-merchant}

Warung Bu Ani gives civil servants a discount, under a business category
Terminal Nusantara registered for its merchants and bound the warung's device
to. The device has no DID, so it introduces itself by its
Verifier Device Certificate. It builds the Request Object, signs it with its
device key, leaves it with the relay at Terminal Nusantara's Verifier Core, and
shows a QR code that points there:

``` { .text title="The authorization request in the merchant's QR code" data-format="URL" }
openid4vp://?client_id=x509_hash%3Anrb1LsGT1vejNwIrM61-cW5NM-6Q566oi7dPE3lTMa4&request_uri=https%3A%2F%2Fterminal-nusantara.co.id%2Frelay%2FBmLpWLcn9GF1Tw2O8Jb5Uw%2Frequest
```

The relay serves the Request Object as the device left it:

``` { .text title="The merchant's Request Object, as the relay serves it" data-format="JWT" }
eyJ0eXAiOiJvYXV0aC1hdXRoei1yZXErand0IiwiYWxnIjoiRVMyNTYiLCJ4NWMiOlsiTUlJQzV6
Q0NBbzJnQXdJQkFnSU1XWXZiSURRdmpVU0pxeXdQTUFvR0NDcUdTTTQ5QkFNQ01Gc3hDekFKQmdO
VkJBWVRBa2xFTVJzd0dRWURWUVFLREJKVVpYSnRhVzVoYkNCT2RYTmhiblJoY21FeEx6QXRCZ05W
QkFNTUpsUmxjbTFwYm1Gc0lFNTFjMkZ1ZEdGeVlTQldaWEpwWm1sbGNpQkpjM04xYVc1bklFTkJN
QjRYRFRJMk1Ea3lNREF3TURBd01Gb1hEVEk0TURreE9UQXdNREF3TUZvd1FqRUxNQWtHQTFVRUJo
TUNTVVF4R3pBWkJnTlZCQW9NRWxSbGNtMXBibUZzSUU1MWMyRnVkR0Z5WVRFV01CUUdBMVVFQXd3
TlYyRnlkVzVuSUVKMUlFRnVhVEJaTUJNR0J5cUdTTTQ5QWdFR0NDcUdTTTQ5QXdFSEEwSUFCSnpu
c0R6c0h2dWUyVEhXeEpFbFVRVVRXV3RqaXFMRUZmM0Z1ZXVxby9WNUNqZjM1RnJtOTVMSlRxbytW
ZVRsSW9IVXJYUU9KL05RNWlrbWtua3lCSytqZ2dGT01JSUJTakFNQmdOVkhSTUJBZjhFQWpBQU1B
NEdBMVVkRHdFQi93UUVBd0lIZ0RBVkJnTlZIU1VCQWY4RUN6QUpCZ2NvZ1l4ZEJRRUdNQjhHQTFV
ZEl3UVlNQmFBRkM2anR2V2gwK2YzK1NCZ1h2L29nS0JaZ1hrek1CMEdBMVVkRGdRV0JCUkxnTGtj
dHY5ODhiMVVXV2VhZWd2M1NLaThPakNCaHdZS0t3WUJCQUdCL1ZrQkFRUjVNSGN3SXd3T2FXUXVh
V1JqZEdZdWEzUndMakV3RVF3UGRYTnBZVjlrYVY5aGRHRnpYekUzTUNZTUZXOXlaeTVwYzI4dU1U
Z3dNVE11TlM0eExtMUVUREFOREF0aFoyVmZiM1psY2w4eE9EQW9EQlJwWkM1cFpHTjBaaTVyWVhK
MGRTMWhjMjR1TVRBUURBUnVZVzFoREFocGJuTjBZVzV6YVRCSkJnTlZIUjhFUWpCQU1ENmdQS0E2
aGpob2RIUndjem92TDNSbGNtMXBibUZzTFc1MWMyRnVkR0Z5WVM1amJ5NXBaQzlqY213dmRtVnlh
V1pwWlhJdGFYTnpkV2x1WnkxallUQUtCZ2dxaGtqT1BRUURBZ05JQURCRkFpRUE0VUgyYVhtR2FT
L2ZJMkpWTERoaVFLbHNjd0pnb21yRzFXR01LeDRKdEVRQ0lFTElabnpRdFd1M004VnpCeGdTcTJn
MVd1by9sZTdKbU11SGpGUHdBaTZGIiwiTUlJQ2NEQ0NBaGVnQXdJQkFnSU5BTFdKemZZYmlKNi9D
cHpPQlRBS0JnZ3Foa2pPUFFRREFqQmJNUXN3Q1FZRFZRUUdFd0pKUkRFck1Da0dBMVVFQ2d3aVZI
SjFjM1FnUVhWMGFHOXlhWFI1SUZKbGNIVmliR2xySUVsdVpHOXVaWE5wWVRFZk1CMEdBMVVFQXd3
V1NVUkRWRVlnVm1WeWFXWnBaWElnVW05dmRDQkRRVEFlRncweU5qQTJNREV3TURBd01EQmFGdzB6
TVRBMk1ERXdNREF3TURCYU1Gc3hDekFKQmdOVkJBWVRBa2xFTVJzd0dRWURWUVFLREJKVVpYSnRh
VzVoYkNCT2RYTmhiblJoY21FeEx6QXRCZ05WQkFNTUpsUmxjbTFwYm1Gc0lFNTFjMkZ1ZEdGeVlT
QldaWEpwWm1sbGNpQkpjM04xYVc1bklFTkJNRmt3RXdZSEtvWkl6ajBDQVFZSUtvWkl6ajBEQVFj
RFFnQUVsVUYxaHNXdUJnSXJ0U2Y5M0Y5M045eGMwMUlZUUc3TnN6KzhBK0VWN0lyeGdXWXpNMEdQ
YVRZTUMrejYwc0JXalZ2dWdOQjBidXQydjg5blJROS9mYU9CdnpDQnZEQVNCZ05WSFJNQkFmOEVD
REFHQVFIL0FnRUFNQTRHQTFVZER3RUIvd1FFQXdJQkJqQVNCZ05WSFNVRUN6QUpCZ2NvZ1l4ZEJR
RUdNQjhHQTFVZEl3UVlNQmFBRkZuRjhFTjRhSGZHNHVLaEpVU2tNRDFLN2dUek1CMEdBMVVkRGdR
V0JCUXVvN2Ixb2RQbjkva2dZRjcvNklDZ1dZRjVNekJDQmdOVkhSOEVPekE1TURlZ05hQXpoakZv
ZEhSd2N6b3ZMM0psWjJsemRISjVMblJ5ZFhOMExtZHZMbWxrTDJOeWJDOTJaWEpwWm1sbGNpMXli
MjkwTFdOaE1Bb0dDQ3FHU000OUJBTUNBMGNBTUVRQ0lDRzJpU0xJdXZNMUY4bjBaanpOVlJCaHNZ
L2FXUmU2czlCTUJtaE43UE5HQWlBU3ozK1NDUE92dVZnNFA4K3FJZmFlR3RrdU80TXYxM3NmWmdL
Wno2cmxyUT09Il19.eyJjbGllbnRfaWQiOiJ4NTA5X2hhc2g6bnJiMUxzR1QxdmVqTndJck02MS1
jVzVOTS02UTU2Nm9pN2RQRTNsVE1hNCIsImF1ZCI6Imh0dHBzOi8vc2VsZi1pc3N1ZWQubWUvdjI
iLCJyZXNwb25zZV90eXBlIjoidnBfdG9rZW4iLCJyZXNwb25zZV9tb2RlIjoiZGlyZWN0X3Bvc3Q
uand0IiwicmVzcG9uc2VfdXJpIjoiaHR0cHM6Ly90ZXJtaW5hbC1udXNhbnRhcmEuY28uaWQvcmV
sYXkvQm1McFdMY245R0YxVHcyTzhKYjVVdy9yZXNwb25zZSIsImNsaWVudF9tZXRhZGF0YSI6eyJ
qd2tzIjp7ImtleXMiOlt7Imt0eSI6IkVDIiwiY3J2IjoiUC0yNTYiLCJ4IjoiN2tFT2tpY25Rek1
0SGJJU1U4VGRFODE2TlJSSVVhaTJDb0g0TWp3cHprUSIsInkiOiJxTDM2alpsWFg5SzZCRU13YVh
QOFduZkRMZ3ZSWmlFZDZGamcxMVRBNWZBIiwidXNlIjoiZW5jIiwiYWxnIjoiRUNESC1FUyIsImt
pZCI6Im93NkUyUmxsVEVnWkZ3d0RhVzhkak1jOVJVNDFhSjVsUWl5RHZack05VnMifV19LCJ2cF9
mb3JtYXRzX3N1cHBvcnRlZCI6eyJkYytzZC1qd3QiOnsic2Qtand0X2FsZ192YWx1ZXMiOlsiRVM
yNTYiXSwia2Itand0X2FsZ192YWx1ZXMiOlsiRVMyNTYiXX0sImxkcF92YyI6eyJwcm9vZl90eXB
lX3ZhbHVlcyI6WyJEYXRhSW50ZWdyaXR5UHJvb2YiXSwiY3J5cHRvc3VpdGVfdmFsdWVzIjpbImV
jZHNhLXJkZmMtMjAxOSJdfX19LCJub25jZSI6Ind0bEU5TGs3YWJkSHFoMlpUYkRKbUEiLCJzdGF
0ZSI6IkJIWGExS0Z2R3VEZEt2YWJNdVVOenciLCJkY3FsX3F1ZXJ5Ijp7ImNyZWRlbnRpYWxzIjp
beyJpZCI6ImthcnR1LWFzbiIsImZvcm1hdCI6ImRjK3NkLWp3dCIsIm1ldGEiOnsidmN0X3ZhbHV
lcyI6WyJpZC5pZGN0Zi5rYXJ0dS1hc24uMSJdfSwiY2xhaW1zIjpbeyJwYXRoIjpbIm5hbWEiXX0
seyJwYXRoIjpbImluc3RhbnNpIl19XX1dfSwidmVyaWZpZXJfaW5mbyI6W3siZm9ybWF0Ijoidm5
kLmlkLmlkY3RmLnVzZS1zdGF0ZW1lbnQrand0IiwiZGF0YSI6ImV5SjBlWEFpT2lKMmJtUXVhV1F
1YVdSamRHWXVkWE5sTFhOMFlYUmxiV1Z1ZEN0cWQzUWlMQ0poYkdjaU9pSkZVekkxTmlJc0ltdHB
aQ0k2SW1ScFpEcDNaV0oyYURwUmJWcHFlVEYwT1c5R2FXRkdhbWhZTW1Vek9IVk5kVkkzYldkMFp
FeHFTRkJOUjJacVJXWjJjbk50WVdseE9uUnlkWE4wTG1kdkxtbGtJM1Z6WlMxemRHRjBaVzFsYm5
RdE1TSjkuZXlKcGMzTWlPaUprYVdRNmQyVmlkbWc2VVcxYWFua3hkRGx2Um1saFJtcG9XREpsTXp
oMVRYVlNOMjFuZEdSTWFraFFUVWRtYWtWbWRuSnpiV0ZwY1RwMGNuVnpkQzVuYnk1cFpDSXNJbk4
xWWlJNkltUnBaRHAzWldKMmFEcFJiVlZCVkVNMWFubG1OWGxXZVRjeVIxbEJjRGh1VTNaMWQzTm9
la1I1Tm5kWldEZFhiVTVaTlZWS2RGaFVPblJsY20xcGJtRnNMVzUxYzJGdWRHRnlZUzVqYnk1cFp
DSXNJblZ6WlY5cFpDSTZJbXRoZEdWbmIzSnBMV1JwYzJ0dmJpMWhjMjRpTENKd2RYSndiM05sSWp
wN0ltbGtJam9pVm1WeWFXWnBhMkZ6YVNCemRHRjBkWE1nUVZOT0lIVnVkSFZySUhCdmRHOXVaMkZ
1SUdoaGNtZGhJaXdpWlc0aU9pSkRhWFpwYkNCelpYSjJZVzUwSUhOMFlYUjFjeUJqYUdWamF5Qm1
iM0lnWVNCa2FYTmpiM1Z1ZENKOUxDSnNaV2RoYkY5aVlYTnBjeUk2SWxCbGNtcGhibXBwWVc0Z2E
yVnlhbUVnYzJGdFlTQndjbTluY21GdElIQnZkRzl1WjJGdUlHaGhjbWRoSUVGVFRpQmtaVzVuWVc
0Z2NHVmtZV2RoYm1jZ2JXbDBjbUVpTENKamJHRnBiWE1pT2xzaWFXUXVhV1JqZEdZdWEyRnlkSFV
0WVhOdUxqRWpibUZ0WVNJc0ltbGtMbWxrWTNSbUxtdGhjblIxTFdGemJpNHhJMmx1YzNSaGJuTnB
JbDBzSW5OMFlYUjFjeUk2ZXlKemRHRjBkWE5mYkdsemRDSTZleUpwWkhnaU9qa3dNekVzSW5WeWF
TSTZJbWgwZEhCek9pOHZjbVZuYVhOMGNua3VkSEoxYzNRdVoyOHVhV1F2YzNSaGRIVnpMM1Z6WlM
xemRHRjBaVzFsYm5SekxURWlmWDBzSW1saGRDSTZNVGM1TWpBeU1qUXdNQ3dpWlhod0lqb3hPREl
6TlRVNE5EQXdmUS5pS1pkeFA1RFR6M3dxSlRyeXFwbGRjNm9WUGM2VGNkU1djR1ZKbXotZnVLVEl
1NkpXakxXQ2xrQzZaeEZfd0VjaDVMQWpwd1kta0x3d0hqbldRRE9ldyJ9XSwiaWF0IjoxNzkyMjI
0MDAwLCJleHAiOjE3OTIyMjQzMDB9.guKZ2qNQgkTvMUa22LOtxsAMmuLavc0XaLI5M2PKAuNup8
hsrXyGrAySC0nPTr8Uro3B6k2Jr-zz3jt829rmpA
```

Its protected header carries the device certificate and the Verifier Issuing CA
certificate that issued it, and not the Verifier Root CA, which the wallet
carries from build time:

``` { .json title="Protected header of the merchant's Request Object" data-format="JSON" }
{
  "typ": "oauth-authz-req+jwt",
  "alg": "ES256",
  "x5c": [
    "MIIC5zCCAo2gAwIBAgIMWYvbIDQvjUSJqywPMAoGCCqGSM49BAMCMFsxCzAJBgNVBAYTAklEMRswGQYDVQQKDBJUZXJtaW5hbCBOdXNhbnRhcmExLzAtBgNVBAMMJlRlcm1pbmFsIE51c2FudGFyYSBWZXJpZmllciBJc3N1aW5nIENBMB4XDTI2MDkyMDAwMDAwMFoXDTI4MDkxOTAwMDAwMFowQjELMAkGA1UEBhMCSUQxGzAZBgNVBAoMElRlcm1pbmFsIE51c2FudGFyYTEWMBQGA1UEAwwNV2FydW5nIEJ1IEFuaTBZMBMGByqGSM49AgEGCCqGSM49AwEHA0IABJznsDzsHvue2THWxJElUQUTWWtjiqLEFf3Fueuqo/V5Cjf35Frm95LJTqo+VeTlIoHUrXQOJ/NQ5ikmknkyBK+jggFOMIIBSjAMBgNVHRMBAf8EAjAAMA4GA1UdDwEB/wQEAwIHgDAVBgNVHSUBAf8ECzAJBgcogYxdBQEGMB8GA1UdIwQYMBaAFC6jtvWh0+f3+SBgXv/ogKBZgXkzMB0GA1UdDgQWBBRLgLkctv988b1UWWeaegv3SKi8OjCBhwYKKwYBBAGB/VkBAQR5MHcwIwwOaWQuaWRjdGYua3RwLjEwEQwPdXNpYV9kaV9hdGFzXzE3MCYMFW9yZy5pc28uMTgwMTMuNS4xLm1ETDANDAthZ2Vfb3Zlcl8xODAoDBRpZC5pZGN0Zi5rYXJ0dS1hc24uMTAQDARuYW1hDAhpbnN0YW5zaTBJBgNVHR8EQjBAMD6gPKA6hjhodHRwczovL3Rlcm1pbmFsLW51c2FudGFyYS5jby5pZC9jcmwvdmVyaWZpZXItaXNzdWluZy1jYTAKBggqhkjOPQQDAgNIADBFAiEA4UH2aXmGaS/fI2JVLDhiQKlscwJgomrG1WGMKx4JtEQCIELIZnzQtWu3M8VzBxgSq2g1Wuo/le7JmMuHjFPwAi6F",
    "MIICcDCCAhegAwIBAgINALWJzfYbiJ6/CpzOBTAKBggqhkjOPQQDAjBbMQswCQYDVQQGEwJJRDErMCkGA1UECgwiVHJ1c3QgQXV0aG9yaXR5IFJlcHVibGlrIEluZG9uZXNpYTEfMB0GA1UEAwwWSURDVEYgVmVyaWZpZXIgUm9vdCBDQTAeFw0yNjA2MDEwMDAwMDBaFw0zMTA2MDEwMDAwMDBaMFsxCzAJBgNVBAYTAklEMRswGQYDVQQKDBJUZXJtaW5hbCBOdXNhbnRhcmExLzAtBgNVBAMMJlRlcm1pbmFsIE51c2FudGFyYSBWZXJpZmllciBJc3N1aW5nIENBMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAElUF1hsWuBgIrtSf93F93N9xc01IYQG7Nsz+8A+EV7IrxgWYzM0GPaTYMC+z60sBWjVvugNB0but2v89nRQ9/faOBvzCBvDASBgNVHRMBAf8ECDAGAQH/AgEAMA4GA1UdDwEB/wQEAwIBBjASBgNVHSUECzAJBgcogYxdBQEGMB8GA1UdIwQYMBaAFFnF8EN4aHfG4uKhJUSkMD1K7gTzMB0GA1UdDgQWBBQuo7b1odPn9/kgYF7/6ICgWYF5MzBCBgNVHR8EOzA5MDegNaAzhjFodHRwczovL3JlZ2lzdHJ5LnRydXN0LmdvLmlkL2NybC92ZXJpZmllci1yb290LWNhMAoGCCqGSM49BAMCA0cAMEQCICG2iSLIuvM1F8n0ZjzNVRBhsY/aWRe6s9BMBmhN7PNGAiASz3+SCPOvuVg4P8+qIfaeGtkuO4Mv13sfZgKZz6rlrQ=="
  ]
}
```

Its claims name a key the device drew for this request as the key to
encrypt to, ask for the two
attributes the category reaches, and carry the category Use Statement:

``` { .json title="Claims of the merchant's Request Object" data-format="JSON" }
{
  "client_id": "x509_hash:nrb1LsGT1vejNwIrM61-cW5NM-6Q566oi7dPE3lTMa4",
  "aud": "https://self-issued.me/v2",
  "response_type": "vp_token",
  "response_mode": "direct_post.jwt",
  "response_uri": "https://terminal-nusantara.co.id/relay/BmLpWLcn9GF1Tw2O8Jb5Uw/response",
  "client_metadata": {
    "jwks": {
      "keys": [
        {
          "kty": "EC",
          "crv": "P-256",
          "x": "7kEOkicnQzMtHbISU8TdE816NRRIUai2CoH4MjwpzkQ",
          "y": "qL36jZlXX9K6BEMwaXP8WnfDLgvRZiEd6Fjg11TA5fA",
          "use": "enc",
          "alg": "ECDH-ES",
          "kid": "ow6E2RllTEgZFwwDaW8djMc9RU41aJ5lQiyDvZrM9Vs"
        }
      ]
    },
    "vp_formats_supported": {
      "dc+sd-jwt": {
        "sd-jwt_alg_values": [
          "ES256"
        ],
        "kb-jwt_alg_values": [
          "ES256"
        ]
      },
      "ldp_vc": {
        "proof_type_values": [
          "DataIntegrityProof"
        ],
        "cryptosuite_values": [
          "ecdsa-rdfc-2019"
        ]
      }
    }
  },
  "nonce": "wtlE9Lk7abdHqh2ZTbDJmA",
  "state": "BHXa1KFvGuDdKvabMuUNzw",
  "dcql_query": {
    "credentials": [
      {
        "id": "kartu-asn",
        "format": "dc+sd-jwt",
        "meta": {
          "vct_values": [
            "id.idctf.kartu-asn.1"
          ]
        },
        "claims": [
          {
            "path": [
              "nama"
            ]
          },
          {
            "path": [
              "instansi"
            ]
          }
        ]
      }
    ]
  },
  "verifier_info": [
    {
      "format": "vnd.id.idctf.use-statement+jwt",
      "data": "eyJ0eXAiOiJ2bmQuaWQuaWRjdGYudXNlLXN0YXRlbWVudCtqd3QiLCJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDp3ZWJ2aDpRbVpqeTF0OW9GaWFGamhYMmUzOHVNdVI3bWd0ZExqSFBNR2ZqRWZ2cnNtYWlxOnRydXN0LmdvLmlkI3VzZS1zdGF0ZW1lbnQtMSJ9.eyJpc3MiOiJkaWQ6d2Vidmg6UW1aankxdDlvRmlhRmpoWDJlMzh1TXVSN21ndGRMakhQTUdmakVmdnJzbWFpcTp0cnVzdC5nby5pZCIsInN1YiI6ImRpZDp3ZWJ2aDpRbVVBVEM1anlmNXlWeTcyR1lBcDhuU3Z1d3NoekR5NndZWDdXbU5ZNVVKdFhUOnRlcm1pbmFsLW51c2FudGFyYS5jby5pZCIsInVzZV9pZCI6ImthdGVnb3JpLWRpc2tvbi1hc24iLCJwdXJwb3NlIjp7ImlkIjoiVmVyaWZpa2FzaSBzdGF0dXMgQVNOIHVudHVrIHBvdG9uZ2FuIGhhcmdhIiwiZW4iOiJDaXZpbCBzZXJ2YW50IHN0YXR1cyBjaGVjayBmb3IgYSBkaXNjb3VudCJ9LCJsZWdhbF9iYXNpcyI6IlBlcmphbmppYW4ga2VyamEgc2FtYSBwcm9ncmFtIHBvdG9uZ2FuIGhhcmdhIEFTTiBkZW5nYW4gcGVkYWdhbmcgbWl0cmEiLCJjbGFpbXMiOlsiaWQuaWRjdGYua2FydHUtYXNuLjEjbmFtYSIsImlkLmlkY3RmLmthcnR1LWFzbi4xI2luc3RhbnNpIl0sInN0YXR1cyI6eyJzdGF0dXNfbGlzdCI6eyJpZHgiOjkwMzEsInVyaSI6Imh0dHBzOi8vcmVnaXN0cnkudHJ1c3QuZ28uaWQvc3RhdHVzL3VzZS1zdGF0ZW1lbnRzLTEifX0sImlhdCI6MTc5MjAyMjQwMCwiZXhwIjoxODIzNTU4NDAwfQ.iKZdxP5DTz3wqJTryqpldc6oVPc6TcdSWcGVJmz-fuKTIu6JWjLWClkC6ZxF_wEch5LAjpwY-kLwwHjnWQDOew"
    }
  ],
  "iat": 1792224000,
  "exp": 1792224300
}
```

The wallet posts the response to the relay. The relay can read the
protected header, which names that key, and cannot read the content:

``` { .http title="POST of the merchant's encrypted response to the relay" data-format="HTTP" }
POST /relay/BmLpWLcn9GF1Tw2O8Jb5Uw/response HTTP/1.1
Host: terminal-nusantara.co.id
Content-Type: application/x-www-form-urlencoded

response=eyJhbGciOiJFQ0RILUVTIiwiZW5jIjoiQTEyOEdDTSIsImtpZCI6Im93NkUyUmxsVEVnWkZ3d0RhVzhkak1jOVJVNDFhSjVsUWl5RHZack05VnMiLCJlcGsiOnsia3R5IjoiRUMiLCJjcnYiOiJQLTI1NiIsIngiOiI0Z2pqZkczUjM4RzhEb1Y1ZWN3WkplY2pTcnJ3UEpfR1NKZ2llcVlCdEpNIiwieSI6Ik5ycE9GMGJGcVFMZTdDS3RWNzBtMnBocmJhYmQ5cDJET0F2a3I0MkFxc28ifX0..hXgSTbTBRGPSMvEk.D9s_-VIdstxBqiw6VVuzRhXmZrqChVApCBZ62pQMgC3FZfimu5g01hra4b8qQK1UMGgNbu8U7CdRn_6eYnA1yuab3DkSki1Ff2D02fR8fYIM1Oqcxzol2v46VVpVzIexR72odI8f9zFpYs5hT_1XLFSNCYnjPeJ80WcMrDXpTDG6uwVTOgqczhjCzkj0j7TTLkH7rDxuOrMrzFU68GwZcsNCU_6D4HpzBdbjwbbwf5Pa2OtelBwEtoPfuanSlowGNdcSIFwtOL_nIZE8RQmyYf8YT7EW4-NvnEqJDlf0NSIqZfsG50vZMamCYbMS-SVULImpnQ_pJIS8PxKEeAQKmOttzgV-8lnHNVmL-Y2fboYEsBDFcRg8IKbKrC-yuoO4gzPHDvkr-liI8bAbW3pwVZOaqDZljkcpp9ttNjJcx_7VlnbbO83cklJ-YVIwcrN6kjGRscRx2pbSWyo0yQZqUIVGfYXcAnDFDUsUfr5kPbTt3bwLyYwpOljuOw2flIv0qWPMKyuyA1iMogfGzPnfgkajal5iiMYVwp1jVJZyM0lXTjJzJPIqdDjTMClxNUhsZqis-Y7UH8DbeNIe6SEinRnO_MEYuRCeuOEQSVRHQYIAb7VIjQT2R3TFjl6G4TnBR3bJ42Ri1sM6ysfslte-10f-tq0Px0itWuuP5kpCLu_tP56N87CUziszDdHGzSoSZSyoRXyaQaOCqCs2xwdq7bzMVo7CBM37s2SsCPfy3HqKRDO8P1vUSBKX37Ug4yrxIcd6rlWOxiyXV_mqmxylr_pZ2A93UNRtpeL9orB1Q8orr8TVXedY0tOO4R-aypv1t46MJdXvaGV6N-fM8NK8clOVECbnAuVSHcDyWRy4Frr8eJz2sz0XRjgyM0jSyxVUXAUfTD9Ph7rHxXvfPBTmQKmTP8pUvBKRm8_T6xWVQhI3K7ZwdBd0tcb-VSaXoDASpcNM_hu7vkCHFARvuUWqGca6rCHBYe8owkcwemtXErmxr3mCVHd0c2M_xW7f3N0nn9A_acwND6AoWQd_IgV_7YHcbiR0lBALFUIjGLoMtvYwKeed7rN4j57mPAQV8pJNjYu_kL32ssF0TErhN5CeMmsjY9HUL6MYYrK7ucNO0PH4VE_M7AQRIK3djgX55mQcyidnp5PrG8Kc-pY9i1DG-9BnKimvS_v_3p5umQty0KLI253Tpbrw3q7bn1ISIFHefcHuOJIaBhfZ-jYjVhpzQ6NtkwcRk96HOeF6gwPBHKXp8Ewe88OWvLCDKhow531GcymDBLGVUfxnnvhWAvsCDqVGntBLhjZFpH8kTPGbgOb8d7fgCezVwFAH0MMQ5yX3AU3_JeweyG8Txfh6KhoswIwadISWUdsD318oo96Wn1zZ5A8qA7kmEG56p-EtILJPBQFWK39yAEnEjCq2NPjMS-gHCk6Sqmh8Sl5-fV7cSAN_9sC0CWMoDk8h7trHNhPRfxxTHLz_UyAqEHn98Ju1nc00AusLfg6RYMDl6F3P5Gndq8e5X0ZQgyocjcnDFbL5Yvo87X8Q9DneH1VEf_RPdNQ1iDCJ5YQg_w9_ESCfCmPVhn984et7pRShrB66m_CwBVjrlhooOTEeYhZzh5Kp5IZLvHDTBU2cqsL12ff3roOfB332ixfRNZendORJWB4WZiTFq-6AjwaxpfESWYfM-mcqUlY62kKj-PYAqrP0ry3Daec-DVKHvo6lxH-7ahR8gt5Y33j_a5Fu-vb50nahTFT4Y0OmlGkxwMIKNlhHUStann-NY7Z6s6tHb9kAlgJG8KRHLhlEu2Gjh9kcibKys0PTmdd5Vjm-AB6ZhUWTBQoL7OxBcah4gZEOFZnfQQU8OvpsNhUo23uzE1HiaqknmUpk9fAUgLtObP5sy6KMYnbfQNjaR6RSexI-MICQYDqbszdfKMJsfNcR56GvxEXc6J6XGcev0YDVhVVoURWbUqhr-nV2j3ggLc40IyPPgLeIwA5qFslS45J1IYPISNNbFz45dwNACr9KkZ_1ojmqdSDx9LDOY40zBP-SmiAfnv8joyfTULWSIFHZ9XWjXyQmSNiJdHMqiEpi6ob2ZsXhLqJ4Q7DkEtdus8vYCBbFGNPgYJ308Ba1qoOXIfohU5E60IphgqNp1omi4didJhNLJqZgOP7UewVPYKWPAHrrAs22H095nnJTJtINWZdMvwSz1Vc9ezIew8VX2EHxeDsRpwEUM9Ykq6Fmb0XL5UwQ6L9sJXmLtkDmaYhjciS83iz4MbIe_VFQr225e0wAYkl-pgb-DVYwmTOdvaz9qS9dC8NqGrj8prfztwDvPyjJUovBzn__GIGhkMmsW2otH6OI0rbIfqreK1oO7Hayd3yWI4uT5W25F0nr2B3yZon4fYaMro0TCHmH1uoUSI27vrDmqtQZt39LpkcdX20sgUu2ILX078kzFuectPhhfxAJoweQUBw0BKvVAy0--zsqs5VCvxLgQibLm_O8QgYywBFqe0OZ9Vh_Bm8.KHT83lCZnJyAdBpcY42I1g
```

``` { .json title="Protected header of the merchant's encrypted response" data-format="JSON" }
{
  "alg": "ECDH-ES",
  "enc": "A128GCM",
  "kid": "ow6E2RllTEgZFwwDaW8djMc9RU41aJ5lQiyDvZrM9Vs",
  "epk": {
    "kty": "EC",
    "crv": "P-256",
    "x": "4gjjfG3R38G8DoV5ecwZJecjSrrwPJ_GSJgieqYBtJM",
    "y": "NrpOF0bFqQLe7CKtV70m2phrbabd9p2DOAvkr42Aqso"
  }
}
```

The device collects the ciphertext from the relay and decrypts it with the
key it drew for the request. The presentation's Key Binding JWT carries the merchant's
`client_id`, with its `x509_hash` prefix, as `aud`:

``` { .json title="The merchant's response, decrypted on the device" data-format="JSON" }
{
  "vp_token": {
    "kartu-asn": [
      "eyJ0eXAiOiJkYytzZC1qd3QiLCJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDp3ZWJ2aDpRbWU4UnJpR25LeDVqMlFqb2FZMVNnUlNweFRIZGpxMTFMMkV4Z3kxelYyeHNKOmJrbi5nby5pZCNpc3N1YW5jZS1qb3NlLTEifQ.eyJpc3MiOiJkaWQ6d2Vidmg6UW1lOFJyaUduS3g1ajJRam9hWTFTZ1JTcHhUSGRqcTExTDJFeGd5MXpWMnhzSjpia24uZ28uaWQiLCJ2Y3QiOiJpZC5pZGN0Zi5rYXJ0dS1hc24uMSIsImNuZiI6eyJqd2siOnsia3R5IjoiRUMiLCJjcnYiOiJQLTI1NiIsIngiOiIzQ09oeE9lT3hwQk9qVUpncVdTQVUwUUFBWWFZZ3VnUFZKXzJYMnFHZGtjIiwieSI6IjJrOTg4NTRwQjc3dWRkUnZlOE80a2c1bklQVDdFakVncGJlS3FXTHVNRUUifX0sIl9zZF9hbGciOiJzaGEtMjU2IiwiX3NkIjpbIjF6QTdMcXNPdGJoTFZRaG9fUlNlMFRHcVJyZmctUzU4SlpHV1NmZzZabU0iLCJDZnVRdi1jS3JnemYwdXpIeHUtVEJFQkp2dFo0UEE3U0RhVjloOFQ5TF9RIiwiRVQ5QmlsbFV3VmRoYkhjNnRmXy0xWEFDRWdWUDRiX2lVUHhIQ2FYQlNiYyIsIkhMeVU4aHRZWno0TmkyZlJkN3BTWWRpQ2JCLXF0NDhwQlM5aDJCR013VFEiLCJlNlVoQk44QXk1emRVUGdDX2htbnBXbGR3QnhpWDhGN2tPVzRuUklwNXdNIiwiZkFoREt6VjNVMzlqQzZiN0dMaEdGRGw3NnVnVy1tN0R6N1hxcUJuamxkYyIsImhLTUpsakZJTlQtd0ljUDhFUnJhWURrSExyMjZPWUJTQUlHS0ItMG5ORzgiLCJ3N0MxZXJCNno4OG1oRVZzTm5hUVlEZ2JacUNIakxsM2NieDFFemllUnFzIl0sInN0YXR1cyI6eyJzdGF0dXNfbGlzdCI6eyJpZHgiOjQ4MTkyMCwidXJpIjoiaHR0cHM6Ly9ia24uZ28uaWQvc3RhdHVzL2thcnR1LWFzbi0xIn19LCJuYmYiOjE3OTIyMTY4MTAsImlhdCI6MTc5MjIxNjgxMCwiZXhwIjoxODIzNzUyODEwfQ.Rtt14iNH1COHmkwCwvzkYcg2RftZdls7V1WghZc1xZC3GmENzivjroJTPBu2C83Qy4pbdbNsX0lorDW26kbPLg~WyJ3SXVNc2VoQTM1UEp0RU1yUzRub0NRIiwibmFtYSIsIkJ1ZGkgU2FudG9zbyBXaWNha3Nvbm8iXQ~WyJSb1o4SHRpMk9JVkJ4NHlNd3Q0UkZRIiwiaW5zdGFuc2kiLCJCYWRhbiBLZXBlZ2F3YWlhbiBOZWdhcmEiXQ~eyJ0eXAiOiJrYitqd3QiLCJhbGciOiJFUzI1NiJ9.eyJpYXQiOjE3OTIyMjQwNDAsImF1ZCI6Ing1MDlfaGFzaDpucmIxTHNHVDF2ZWpOd0lyTTYxLWNXNU5NLTZRNTY2b2k3ZFBFM2xUTWE0Iiwibm9uY2UiOiJ3dGxFOUxrN2FiZEhxaDJaVGJESm1BIiwic2RfaGFzaCI6IjRLQnhHTVlMMFZOazI5Nmw1QWFtN01vMjd3M3dlc2ZOOS1uSVVDQmRIemcifQ._p7fpejK2grf4EMFQh6et5EVPllf7_r9LwsYHaiI6lLwKc3KYr9l-eYuDkIypCYTuHIZq9aUZo3fg-a_vLZT_Q"
    ]
  },
  "state": "BHXa1KFvGuDdKvabMuUNzw"
}
```

## The HTTPS binding {#ts-3-01-the-https-binding}

Every message of this specification travels over HTTP with Transport Layer
Security (TLS), from the wallet to the verifier. A Relying Party's Verifier
Core answers at a public address of its own, and a merchant's device answers
nothing: the relay at its RP Intermediary's Verifier Core answers for it.
[The table of endpoints][tbl-ts-3-01-endpoints] gives each endpoint, where
the wallet learns its address, and the clause that fixes it.

[](){ #tbl-ts-3-01-endpoints }

<figure markdown="1" class="ekdn-table">

| Endpoint | Method | Address from | Clause |
|---|---|---|---|
| Request URI | `GET` | `request_uri` in the authorization request | [The Request Object][ts-3-01-the-request-object] |
| Response URI | `POST` | `response_uri` in the Request Object | [The response][ts-3-01-the-response] |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-3-01-004 }**REQ-TS-3-01-004** Verifier Core MUST serve every endpoint of [the table of endpoints][tbl-ts-3-01-endpoints] over HTTP with TLS only.
- [](){ #req-ts-3-01-005 }**REQ-TS-3-01-005** Verifier Core MUST serve every endpoint of [the table of endpoints][tbl-ts-3-01-endpoints] at an address a wallet on the public internet can reach.
- [](){ #req-ts-3-01-006 }**REQ-TS-3-01-006** Verifier Core MUST carry a `Cache-Control: no-store` header on every answer of either endpoint.
- [](){ #req-ts-3-01-007 }**REQ-TS-3-01-007** Mobile Wallet MUST NOT send a request of this specification over anything but HTTP with TLS.
- [](){ #req-ts-3-01-008 }**REQ-TS-3-01-008** Verifier Core and Mobile Verifier MUST NOT call Mobile Wallet, because [nothing calls the wallet][who-may-call-whom]: every message of this specification is a request the wallet sends, or the answer to one.
- [](){ #req-ts-3-01-009 }**REQ-TS-3-01-009** Mobile Wallet MUST NOT send an identifier of the citizen, of the wallet installation, or of the device, or a header that names its software version, to either endpoint, as [OpenID4VP][ref-openid4vp] section 15.8 asks.

</div>

## The authorization request {#ts-3-01-the-authorization-request}

The authorization request is what the verifier shows the citizen: a QR
code when the wallet runs on another device, or a link when it runs on the
same one. Its scheme is `openid4vp://`, the custom scheme OpenID4VP section 9
names for invoking a wallet. It carries two parameters and nothing else. A
request passed across devices goes by reference, as
[OpenID4VP][ref-openid4vp] section 5.7 recommends, so the QR code stays small
enough to read. Every other value travels signed inside the Request Object.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-3-01-010 }**REQ-TS-3-01-010** Verifier Core and Mobile Verifier MUST write the authorization request as a URI of the scheme `openid4vp`, with an empty authority and path, and a query.
- [](){ #req-ts-3-01-011 }**REQ-TS-3-01-011** The query MUST carry `client_id` and `request_uri`, each percent-encoded, and no other parameter.
- [](){ #req-ts-3-01-012 }**REQ-TS-3-01-012** `client_id` MUST be the `client_id` of the Request Object behind `request_uri`, byte for byte.
- [](){ #req-ts-3-01-013 }**REQ-TS-3-01-013** `request_uri` MUST be an `https` URI that names one transaction and holds at least 128 bits drawn from a cryptographically secure random number generator.
- [](){ #req-ts-3-01-014 }**REQ-TS-3-01-014** Mobile Verifier MUST show the authorization request as a QR code.
- [](){ #req-ts-3-01-015 }**REQ-TS-3-01-015** Verifier Core MUST show the authorization request as a QR code when the wallet runs on another device.
- [](){ #req-ts-3-01-016 }**REQ-TS-3-01-016** Verifier Core MAY open the authorization request as a link when the wallet runs on the same device.
- [](){ #req-ts-3-01-017 }**REQ-TS-3-01-017** Mobile Wallet MUST NOT refuse an authorization request for carrying a parameter other than `client_id` and `request_uri`, because [OpenID4VP][ref-openid4vp] section 5 requires a wallet to ignore a parameter it does not recognize.
- [](){ #req-ts-3-01-018 }**REQ-TS-3-01-018** Mobile Wallet MUST NOT act on a parameter of the authorization request other than to fetch the Request Object and to compare `client_id` with it.

</div>

## The Request Object {#ts-3-01-the-request-object}

The Request Object is a JWT the verifier signs, as
[RFC 9101][ref-rfc9101] defines one, and every value the wallet acts on is
inside it. The wallet fetches it with a `GET` to `request_uri`;
the `post` method of OpenID4VP section 5.10 is not used, because a wallet in
IDCTF has no metadata the verifier needs to tailor a request to.

### Fetching it {#ts-3-01-fetching-it}

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-3-01-019 }**REQ-TS-3-01-019** Mobile Wallet MUST fetch the Request Object with a `GET` to `request_uri`, carrying an `Accept` header of `application/oauth-authz-req+jwt`.
- [](){ #req-ts-3-01-020 }**REQ-TS-3-01-020** Verifier Core MUST answer a fetch of a request URI it holds with status `200`, a `Content-Type` of `application/oauth-authz-req+jwt`, and the Request Object in compact serialization as the body.
- [](){ #req-ts-3-01-021 }**REQ-TS-3-01-021** Verifier Core MUST NOT serve a Request Object after its `exp`, or after it has received a response to it.
- [](){ #req-ts-3-01-022 }**REQ-TS-3-01-022** Verifier Core MUST answer a fetch of a request URI it does not hold, or no longer serves, with status `404`.
- [](){ #req-ts-3-01-023 }**REQ-TS-3-01-023** Mobile Wallet MUST stop the exchange when the fetch is answered with any status other than `200`, because without the Request Object it holds nothing it may act on.
- [](){ #req-ts-3-01-024 }**REQ-TS-3-01-024** Mobile Wallet MUST NOT fetch a request URI a second time for one authorization request.

</div>

### Its header {#ts-3-01-its-header}

The header carries what the prefix of `client_id` needs to find the key, and
nothing else. [The table of Request Object headers][tbl-ts-3-01-header] gives
both forms.

[](){ #tbl-ts-3-01-header }

<figure markdown="1" class="ekdn-table">

| Parameter | `decentralized_identifier` | `x509_hash` | Value |
|---|---|---|---|
| `typ` | Present | Present | `oauth-authz-req+jwt` |
| `alg` | Present | Present | An algorithm the Governance Profile allows for a Request Object key; `ES256` for a merchant's device key |
| `kid` | Present | Absent | The verification method of the Request Object key, as [Finding a signer's key from its DID](finding-a-signers-key-from-its-did.md) fixes |
| `x5c` | Absent | Present | The Verifier Device Certificate, then the Verifier Issuing CA certificate that issued it |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-3-01-025 }**REQ-TS-3-01-025** Verifier Core and Mobile Verifier MUST write the header parameters [the table of Request Object headers][tbl-ts-3-01-header] marks present for the prefix of its `client_id`, and no other.
- [](){ #req-ts-3-01-026 }**REQ-TS-3-01-026** `typ` MUST be `oauth-authz-req+jwt`.
- [](){ #req-ts-3-01-027 }**REQ-TS-3-01-027** Under `decentralized_identifier`, `alg` MUST name an algorithm the Governance Profile allows for a Request Object key.
- [](){ #req-ts-3-01-028 }**REQ-TS-3-01-028** Under `x509_hash`, `alg` MUST be `ES256`, the algorithm of the P-256 device key its Verifier Device Certificate certifies under [Issuing and validating the X.509 certificates and the VICAL](issuing-and-validating-the-x509-certificates-and-the-vical.md), and not a Governance Profile member.
- [](){ #req-ts-3-01-029 }**REQ-TS-3-01-029** Under `x509_hash`, `x5c` MUST hold exactly two certificates, the Verifier Device Certificate first and the Verifier Issuing CA certificate second.
- [](){ #req-ts-3-01-102 }**REQ-TS-3-01-102** Under `x509_hash`, `x5c` MUST NOT hold the Verifier Root CA certificate, which the wallet carries from build time.
- [](){ #req-ts-3-01-030 }**REQ-TS-3-01-030** Mobile Wallet MUST refuse a Request Object whose `typ` is absent or is not `oauth-authz-req+jwt`, as [OpenID4VP][ref-openid4vp] section 5 requires.

</div>

### Its claims {#ts-3-01-its-claims}

[The table of Request Object claims][tbl-ts-3-01-claims] gives every claim a
verifier writes and the ones it leaves out. The claims of a request from
Verifier Core are shown in
[carrying it online][ts-5-06-carrying-it-online], and those of a merchant's
request in [the Kartu ASN, from a merchant][ts-3-01-the-kartu-asn-from-a-merchant].

[](){ #tbl-ts-3-01-claims }

<figure markdown="1" class="ekdn-table">

| Claim | Presence | Value |
|---|---|---|
| `client_id` | Present | The verifier's Client Identifier, with its prefix, as [Client Identifier Prefixes][ts-3-01-client-identifier-prefixes] fixes |
| `aud` | Present | `https://self-issued.me/v2`, the value [OpenID4VP][ref-openid4vp] section 5.8 fixes for a wallet the verifier did not discover |
| `response_type` | Present | `vp_token` |
| `response_mode` | Present | `direct_post.jwt` |
| `response_uri` | Present | The response endpoint, as [The response][ts-3-01-the-response] fixes |
| `client_metadata` | Present | As [the table of client metadata][tbl-ts-3-01-client-metadata] fixes |
| `nonce` | Present | A value drawn for this request, as [REQ-TS-5-11-070][req-ts-5-11-070] fixes |
| `state` | Present | A value drawn for this request, which the response returns |
| `dcql_query` | Present | The query, as [The query][ts-3-01-the-query] fixes |
| `verifier_info` | Present | The Use Statement of the use the request serves, as [carrying it online][ts-5-06-carrying-it-online] fixes |
| `iat` | Present | The moment the verifier signed |
| `exp` | Present | The moment after which no wallet acts on the request |
| `iss` | Absent | None: `client_id` names the signer |
| `redirect_uri` | Absent | None: [OpenID4VP][ref-openid4vp] section 8.2 forbids it beside `response_uri` |
| `scope` | Absent | None: the query is always written out |
| `request_uri_method` | Absent | None |
| `transaction_data` | Absent | None |
| `wallet_nonce` | Absent | None |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-3-01-031 }**REQ-TS-3-01-031** Verifier Core and Mobile Verifier MUST write every claim [the table of Request Object claims][tbl-ts-3-01-claims] marks present.
- [](){ #req-ts-3-01-032 }**REQ-TS-3-01-032** Verifier Core and Mobile Verifier MUST NOT write a claim [the table of Request Object claims][tbl-ts-3-01-claims] marks absent.
- [](){ #req-ts-3-01-033 }**REQ-TS-3-01-033** Verifier Core and Mobile Verifier MUST draw `state` afresh for every Request Object, from a cryptographically secure random number generator, with at least 128 bits of entropy, the strength [OpenID4VP][ref-openid4vp] section 5.3 asks of `state` where it requires one.
- [](){ #req-ts-3-01-034 }**REQ-TS-3-01-034** `nonce` and `state` MUST hold only the characters [OpenID4VP][ref-openid4vp] section 5.2 allows: letters, digits, hyphen, period, underscore, and tilde.
- [](){ #req-ts-3-01-035 }**REQ-TS-3-01-035** `exp` MUST be later than `iat` by no more than the lifetime the Governance Profile sets for a Request Object.
- [](){ #req-ts-3-01-036 }**REQ-TS-3-01-036** Verifier Core and Mobile Verifier MUST sign one Request Object for one transaction.
- [](){ #req-ts-3-01-103 }**REQ-TS-3-01-103** Verifier Core MUST NOT serve a Request Object for any transaction but the one it was signed for.

</div>

### Client metadata {#ts-3-01-client-metadata}

`client_metadata` carries the key the response is encrypted to and the
formats the verifier accepts. Under both prefixes, every value of the
verifier's metadata but the signing key comes from it, as
[OpenID4VP][ref-openid4vp] section 5.9.3 requires.

[](){ #tbl-ts-3-01-client-metadata }

<figure markdown="1" class="ekdn-table">

| Member | Presence | Value |
|---|---|---|
| `jwks` | Present | One key, as [the table of the encryption key][tbl-ts-3-01-encryption-key] fixes |
| `vp_formats_supported` | Present | `dc+sd-jwt` with `sd-jwt_alg_values` and `kb-jwt_alg_values`, and `ldp_vc` with `proof_type_values` `DataIntegrityProof` and `cryptosuite_values` `ecdsa-rdfc-2019` |
| `encrypted_response_enc_values_supported` | Absent | None: the response is encrypted with `A128GCM`, the default |

</figure>

[](){ #tbl-ts-3-01-encryption-key }

<figure markdown="1" class="ekdn-table">

| Member | Value |
|---|---|
| `kty` | `EC` |
| `crv` | `P-256` |
| `x`, `y` | The public key |
| `use` | `enc` |
| `alg` | `ECDH-ES` |
| `kid` | The JSON Web Key thumbprint of the key, computed as [RFC 7638][ref-rfc7638] defines it |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-3-01-037 }**REQ-TS-3-01-037** Verifier Core and Mobile Verifier MUST write every member [the table of client metadata][tbl-ts-3-01-client-metadata] marks present, and no member it marks absent.
- [](){ #req-ts-3-01-038 }**REQ-TS-3-01-038** `jwks` MUST hold exactly one key, with the members [the table of the encryption key][tbl-ts-3-01-encryption-key] gives and no other.
- [](){ #req-ts-3-01-039 }**REQ-TS-3-01-039** Verifier Core MUST place in `jwks` the public half of a key pair it draws for this Request Object.
- [](){ #req-ts-3-01-040 }**REQ-TS-3-01-040** Mobile Verifier MUST place in `jwks` the public half of a key pair it draws on the device for this Request Object, and keeps there.
- [](){ #req-ts-3-01-108 }**REQ-TS-3-01-108** Verifier Core and Mobile Verifier MUST NOT place the same key in the `jwks` of two Request Objects.
- [](){ #req-ts-3-01-109 }**REQ-TS-3-01-109** Mobile Verifier MUST NOT place its device key in `jwks`, because its Verifier Device Certificate certifies that key for signing alone.
- [](){ #req-ts-3-01-110 }**REQ-TS-3-01-110** Verifier Core and Mobile Verifier MUST delete the private half of the key once the response to its Request Object is decrypted, or once that Request Object's `exp` has passed, whichever comes first.
- [](){ #req-ts-3-01-041 }**REQ-TS-3-01-041** `sd-jwt_alg_values` MUST list the algorithms the Governance Profile allows for an issuance key, and `kb-jwt_alg_values` those it allows for a credential key.
- [](){ #req-ts-3-01-042 }**REQ-TS-3-01-042** Mobile Wallet MUST NOT verify the signature of a Request Object with a key from `jwks`, as [OpenID4VP][ref-openid4vp] section 5.1 forbids.

</div>

### The query {#ts-3-01-the-query}

The query is written in the Digital Credentials Query Language (DCQL) of
[OpenID4VP][ref-openid4vp] section 6. [The table of credential query
members][tbl-ts-3-01-dcql] gives the members a credential query carries in
IDCTF. What each claim names, and the options of `claim_sets`, are fixed by
[carrying it online][ts-5-06-carrying-it-online].

[](){ #tbl-ts-3-01-dcql }

<figure markdown="1" class="ekdn-table">

| Member | Presence | Value |
|---|---|---|
| `id` | Present | An identifier unique within the query |
| `format` | Present | `dc+sd-jwt` or `ldp_vc` |
| `meta` | Present | `vct_values` naming the Rulebook `id` for `dc+sd-jwt`; `type_values` naming the expanded types for `ldp_vc` |
| `claims` | Present | One claims query per attribute, each with `path`, and each with `id` where the query carries `claim_sets`, as [OpenID4VP][ref-openid4vp] section 6.3 requires; for `ldp_vc`, one per attribute of the type |
| `claim_sets` | Optional | As [carrying it online][ts-5-06-carrying-it-online] fixes; never for `ldp_vc` |
| `multiple` | Absent | None: one credential answers one query |
| `trusted_authorities` | Absent | None: the trusted list decides which issuers a verifier accepts |
| `require_cryptographic_holder_binding` | Absent | None: every presentation proves the credential key |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-3-01-043 }**REQ-TS-3-01-043** Verifier Core and Mobile Verifier MUST write each credential query with the members [the table of credential query members][tbl-ts-3-01-dcql] marks present, and no member it marks absent.
- [](){ #req-ts-3-01-044 }**REQ-TS-3-01-044** Verifier Core and Mobile Verifier MUST NOT write a credential query whose `format` is `mso_mdoc`, because an mdoc is presented in proximity alone, as [REQ-TS-5-11-007][req-ts-5-11-007] sets out.
- [](){ #req-ts-3-01-045 }**REQ-TS-3-01-045** Verifier Core and Mobile Verifier MUST NOT write `values` in a claims query, because a match on a value tells the verifier something about the value whether or not the citizen consents, as [OpenID4VP][ref-openid4vp] section 15.4.1 warns.
- [](){ #req-ts-3-01-046 }**REQ-TS-3-01-046** Mobile Wallet MUST refuse a credential query that carries a member [the table of credential query members][tbl-ts-3-01-dcql] marks absent, or a claims query that carries `values`.
- [](){ #req-ts-3-01-115 }**REQ-TS-3-01-115** Verifier Core and Mobile Verifier MUST name in `claims` every attribute of the credential type in a credential query whose `format` is `ldp_vc`, because an `ldp_vc` presentation carries every claim, as [REQ-TS-5-11-010][req-ts-5-11-010] sets out.
- [](){ #req-ts-3-01-116 }**REQ-TS-3-01-116** Mobile Wallet MUST refuse a credential query whose `format` is `ldp_vc` and whose `claims` names fewer than every attribute of the credential type.

</div>

## Client Identifier Prefixes {#ts-3-01-client-identifier-prefixes}

`client_id` tells the wallet who the verifier claims to be and how to check
it, as [OpenID4VP][ref-openid4vp] section 5.9 defines it. IDCTF uses two of
its prefixes, one per kind of verifier.

[](){ #tbl-ts-3-01-prefixes }

<figure markdown="1" class="ekdn-table">

| Prefix | Used by | What follows the prefix | Key that signs | Trust anchor |
|---|---|---|---|---|
| `decentralized_identifier` | A Relying Party, an RP Intermediary | The verifier's `did:webvh` | The Request Object key in its DID Document | The trusted list |
| `x509_hash` | A merchant's Mobile Verifier | The base64url SHA-256 of the DER of its Verifier Device Certificate | The device key that certificate certifies | The Verifier Root CA, with the Verifier Issuing CA on the trusted list |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-3-01-047 }**REQ-TS-3-01-047** Verifier Core MUST write `client_id` with the `decentralized_identifier` prefix followed by the `did:webvh` under which its entity is named in the trusted list.
- [](){ #req-ts-3-01-048 }**REQ-TS-3-01-048** Verifier Core MUST sign a Request Object with the Request Object key its DID Document lists under the purpose `request-object`, naming it as [Naming the key][ts-01-naming-the-key] requires.
- [](){ #req-ts-3-01-049 }**REQ-TS-3-01-049** Mobile Verifier MUST write `client_id` with the `x509_hash` prefix followed by the base64url encoding, without padding, of the SHA-256 digest of the Distinguished Encoding Rules (DER) encoding of its Verifier Device Certificate.
- [](){ #req-ts-3-01-050 }**REQ-TS-3-01-050** Mobile Verifier MUST sign a Request Object with its device key.
- [](){ #req-ts-3-01-051 }**REQ-TS-3-01-051** Mobile Wallet MUST refuse a Request Object whose `client_id` carries any prefix other than `decentralized_identifier` or `x509_hash`, or no prefix.
- [](){ #req-ts-3-01-052 }**REQ-TS-3-01-052** Mobile Wallet MUST use `client_id` whole, prefix included, wherever it names the verifier, as [OpenID4VP][ref-openid4vp] section 14.8 requires.

</div>

## Checking the request {#ts-3-01-checking-the-request}

Mobile Wallet checks a request from its own cache before it shows the
citizen anything, in the order below, and nothing in it touches the network
beyond the fetch of the Request Object. Steps 1 to 5, and steps 1 to 4 of
[Reading it][ts-5-06-reading-it], refuse the request whole: a request that
fails one of them *fails a check*. So does a request refused under one of
three requirements that no step repeats, each leaving the wallet nothing to
answer with:

- a query the wallet cannot read, [REQ-TS-3-01-046][req-ts-3-01-046];
- a `client_id` prefix it does not know,
  [REQ-TS-3-01-051][req-ts-3-01-051];
- a request that names no response mode or no key to encrypt an answer to,
  [REQ-TS-3-01-105][req-ts-3-01-105].

Step 6 refuses attributes one at a time,
and what it refuses decides what can be presented, as
[REQ-TS-5-06-110][req-ts-5-06-110] and [REQ-TS-5-06-111][req-ts-5-06-111]
set out; a refused attribute is not a failed check.

1. **Match the request.** The `client_id` of the authorization request equals
   the `client_id` of the Request Object, including its prefix.
2. **Check the signature by the prefix.**

      - Under `decentralized_identifier`, check that `typ` is
        `oauth-authz-req+jwt`, find the key the `kid` names in the verifier's
        DID Document version in force at `iat`, as
        [Finding the key][ts-01-finding-the-key] sets out, and check that the
        purpose is `request-object`.
      - Under `x509_hash`, validate the chain of `x5c` to the Verifier Root CA,
        as [Validating a chain][ts-5-04-validating-a-chain] sets out, check
        `typ` the same way, check that the digest of `x5c[0]` equals the value
        after the prefix, and verify the signature with the key of `x5c[0]`.
3. **Check the time and the audience.** `exp` has not passed, and `aud` is
   `https://self-issued.me/v2`.
4. **Check the verifier's standing.** Under `decentralized_identifier`, the
   DID is named in the cached trusted list in an entry whose Relying Party
   service reads `granted`, an RP Intermediary included. Under `x509_hash`,
   the Verifier Issuing CA of `x5c[1]` is named there at status `granted`, in
   the entry of an entity whose Relying Party service reads `granted`.
5. **Check the permissions.** For every attribute the query asks for, the cached
   Authority Statement of the verifier, or under `x509_hash` of the entity
   holding the Verifier Issuing CA, is present, within its tolerance limit, and
   answers `true`, as [Reading the answer][ts-5-05-reading-the-answer] sets out.
6. **Check the Use Statement and the attributes**, as
   [Reading it][ts-5-06-reading-it] sets out; under `x509_hash`, an attribute
   outside the `ReaderAuthRole` of `x5c[0]`, or one its Credential Rulebook
   classes `restricted`, which a merchant does not reach, is refused as well.
7. **Show the requester.** Under `decentralized_identifier`, the name the
   trusted list gives the entity; under `x509_hash`, the `commonName` of the
   subject of `x5c[0]`, which names the merchant.

The `ReaderAuthRole` names a type by its mdoc `docType` where its Rulebook
names an mdoc representation, and by the Rulebook `id` where it names none.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-3-01-053 }**REQ-TS-3-01-053** Mobile Wallet MUST stop the exchange when the `client_id` of the authorization request and that of the Request Object differ, as [OpenID4VP][ref-openid4vp] section 5.10.1 requires.
- [](){ #req-ts-3-01-054 }**REQ-TS-3-01-054** Mobile Wallet MUST take every parameter it acts on from the Request Object, and none from the authorization request.
- [](){ #req-ts-3-01-055 }**REQ-TS-3-01-055** Under `decentralized_identifier`, Mobile Wallet MUST verify the Request Object as a reader under [Finding a signer's key from its DID](finding-a-signers-key-from-its-did.md), with `request-object` as the purpose the format names and `iat` as the time the token states it was made.
- [](){ #req-ts-3-01-056 }**REQ-TS-3-01-056** Under `x509_hash`, Mobile Wallet MUST validate the chain of `x5c` to the Verifier Root CA as [REQ-TS-5-04-099][req-ts-5-04-099], [REQ-TS-5-04-102][req-ts-5-04-102], and [REQ-TS-5-04-103][req-ts-5-04-103] require.
- [](){ #req-ts-3-01-057 }**REQ-TS-3-01-057** Under `x509_hash`, Mobile Wallet MUST refuse a Request Object unless the base64url SHA-256 of the DER of `x5c[0]` equals the value after the prefix.
- [](){ #req-ts-3-01-058 }**REQ-TS-3-01-058** Under `x509_hash`, Mobile Wallet MUST verify the signature of the Request Object with the public key of `x5c[0]`.
- [](){ #req-ts-3-01-059 }**REQ-TS-3-01-059** Mobile Wallet MUST refuse a Request Object whose `exp` has passed, or whose `aud` is not `https://self-issued.me/v2`.
- [](){ #req-ts-3-01-060 }**REQ-TS-3-01-060** Under `decentralized_identifier`, Mobile Wallet MUST refuse a verifier whose DID its cached trusted list does not name in an entry whose Relying Party service reads `granted`.
- [](){ #req-ts-3-01-061 }**REQ-TS-3-01-061** Mobile Wallet MUST refuse a request when, for any attribute its query asks for, the cached Authority Statement of the verifier, or under `x509_hash` of the entity holding the Verifier Issuing CA, is missing, is past its tolerance limit, or answers `false`, as the [online verification][online-verification] flow sets out.
- [](){ #req-ts-3-01-062 }**REQ-TS-3-01-062** Under `x509_hash`, Mobile Wallet MUST refuse every attribute the query asks for outside the `ReaderAuthRole` of `x5c[0]`, as [REQ-TS-5-04-101][req-ts-5-04-101] requires, reading each credential query against the entry whose `docType` is the mdoc `docType` of the Rulebook it names, or the `id` of that Rulebook where it names no mdoc representation.
- [](){ #req-ts-3-01-063 }**REQ-TS-3-01-063** Under `x509_hash`, Mobile Wallet MUST refuse every attribute the query asks for that its Credential Rulebook classes `restricted`.
- [](){ #req-ts-3-01-064 }**REQ-TS-3-01-064** Mobile Wallet MUST treat an attribute refused under [REQ-TS-3-01-062][req-ts-3-01-062] or [REQ-TS-3-01-063][req-ts-3-01-063] as one refused under [REQ-TS-5-06-067][req-ts-5-06-067], so that [REQ-TS-5-06-110][req-ts-5-06-110] and [REQ-TS-5-06-111][req-ts-5-06-111] decide what is presented.
- [](){ #req-ts-3-01-065 }**REQ-TS-3-01-065** Mobile Wallet MUST run [Reading it][ts-5-06-reading-it] on the Use Statement the request carries.
- [](){ #req-ts-3-01-066 }**REQ-TS-3-01-066** Mobile Wallet MUST show the citizen the requester's name as the trusted list gives it under `decentralized_identifier`, and as the `commonName` of the subject of `x5c[0]` under `x509_hash`.
- [](){ #req-ts-3-01-067 }**REQ-TS-3-01-067** Mobile Wallet MUST NOT fetch anything but the Request Object while it checks a request.
- [](){ #req-ts-3-01-106 }**REQ-TS-3-01-106** Under `x509_hash`, Mobile Wallet MUST refuse a Request Object whose Verifier Issuing CA its cached trusted list does not name at status `granted` in the entry of an entity whose Relying Party service reads `granted`, as [REQ-TS-5-04-100][req-ts-5-04-100] requires.
- [](){ #req-ts-3-01-105 }**REQ-TS-3-01-105** Mobile Wallet MUST refuse a Request Object whose `response_type` is not `vp_token`, whose `response_mode` is not `direct_post.jwt`, or whose `jwks` holds no key with `alg` `ECDH-ES` on P-256.

</div>

## The response {#ts-3-01-the-response}

The wallet answers with `direct_post.jwt`, as
[OpenID4VP][ref-openid4vp] section 8.3.1 defines it: an HTTP `POST` to
`response_uri`, carrying one parameter, `response`, whose value is a JWE.
The JWE is the unsigned, encrypted JWT section 8.3 describes. What proves the
answer is the presentation inside it, which the credential key signs; the
encryption keeps it from everyone on the way, the relay included.

[](){ #tbl-ts-3-01-jwe-header }

<figure markdown="1" class="ekdn-table">

| Parameter | Value |
|---|---|
| `alg` | `ECDH-ES`, the `alg` of the key in `jwks` |
| `enc` | `A128GCM` |
| `kid` | The `kid` of the key in `jwks` |
| `epk` | The ephemeral public key the wallet drew for this response, on P-256 |

</figure>

The payload is a JSON object. A response that answers carries `vp_token`, as
[Building and verifying a presentation](building-and-verifying-a-presentation.md)
fixes, and `state`. A response that does not answer carries `error` and
`state`.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-3-01-068 }**REQ-TS-3-01-068** Verifier Core MUST write `response_uri` as an `https` URI at its own public address.
- [](){ #req-ts-3-01-069 }**REQ-TS-3-01-069** Mobile Verifier MUST write `response_uri` as the response address the relay assigned to this transaction.
- [](){ #req-ts-3-01-070 }**REQ-TS-3-01-070** Mobile Wallet MUST send the response as an HTTP `POST` to `response_uri`, with a `Content-Type` of `application/x-www-form-urlencoded` and the single parameter `response`.
- [](){ #req-ts-3-01-071 }**REQ-TS-3-01-071** `response` MUST be a JWE in compact serialization, as [RFC 7516][ref-rfc7516] defines it, with the protected header [the table of the response header][tbl-ts-3-01-jwe-header] gives and no other parameter.
- [](){ #req-ts-3-01-072 }**REQ-TS-3-01-072** Mobile Wallet MUST encrypt the response by direct key agreement with `ECDH-ES`, as [RFC 7518][ref-rfc7518] section 4.6 defines it, to the key in `jwks`, with an ephemeral key it draws for this response and uses for no other.
- [](){ #req-ts-3-01-073 }**REQ-TS-3-01-073** Mobile Wallet MUST NOT carry `apu` or `apv` in the protected header.
- [](){ #req-ts-3-01-074 }**REQ-TS-3-01-074** The payload MUST carry `vp_token` and `state` where the wallet answers, and `error` and `state` where it does not, and no other member.
- [](){ #req-ts-3-01-075 }**REQ-TS-3-01-075** `state` MUST be the `state` of the Request Object, byte for byte.
- [](){ #req-ts-3-01-076 }**REQ-TS-3-01-076** Mobile Wallet MUST NOT send any part of a response unencrypted, an error included.
- [](){ #req-ts-3-01-077 }**REQ-TS-3-01-077** Mobile Wallet MUST send at most one response for one Request Object.

</div>

### When the wallet does not answer {#ts-3-01-when-the-wallet-does-not-answer}

A wallet tells a verifier that it will not answer only when the verifier has
proven who it is. A request that fails a check gets no response at all,
because a `response_uri` from an unchecked request may belong to anyone, and
the verifier's request expires on its own. A request that passed every check
and was refused gets `access_denied`, whatever the reason: the citizen
refused, the wallet holds no credential that answers, or the attributes
refused under [REQ-TS-5-06-067][req-ts-5-06-067],
[REQ-TS-3-01-062][req-ts-3-01-062], or [REQ-TS-3-01-063][req-ts-3-01-063] left
nothing that could be presented.

The three reasons are one code, so that a verifier cannot tell from the
answer what the citizen holds, as [OpenID4VP][ref-openid4vp] sections 15.4.1
and 15.9 ask. Where the wallet holds no credential that answers, or the
attributes refused leave nothing to present, the refusal is settled under the
request, the Use Statement, and the certificate of
[Choosing what to disclose][ts-5-11-choosing-what-to-disclose], before the
citizen is shown anything, and the wallet shows the request even so:
[REQ-TS-3-01-117][req-ts-3-01-117] has it name the requester and the purpose
and say that it cannot answer. A verifier therefore learns no more from how
long a refusal took than from the code it carries.

Two mistakes of a verifier that has proven who it is get `invalid_request`
instead: a Request Object that carries `redirect_uri`, and one that carries
`transaction_data`, which no wallet in IDCTF supports.
[OpenID4VP][ref-openid4vp] sections 8.2 and 8.4 require a wallet to answer both
with an error.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-3-01-078 }**REQ-TS-3-01-078** Mobile Wallet MUST NOT send a response to a Request Object that failed a check of [Checking the request][ts-3-01-checking-the-request].
- [](){ #req-ts-3-01-104 }**REQ-TS-3-01-104** Mobile Wallet MUST answer with `error` set to `invalid_request`, and not present, where a Request Object that fails no check carries `redirect_uri` or `transaction_data`.
- [](){ #req-ts-3-01-079 }**REQ-TS-3-01-079** Mobile Wallet MUST answer with `error` set to `access_denied` where the request passed every check, carries neither `redirect_uri` nor `transaction_data`, and the wallet does not present.
- [](){ #req-ts-3-01-080 }**REQ-TS-3-01-080** Mobile Wallet MUST NOT carry `error_description` or any other member that says why it did not present.
- [](){ #req-ts-3-01-081 }**REQ-TS-3-01-081** Mobile Wallet MUST NOT send `access_denied` before the citizen has seen the request.
- [](){ #req-ts-3-01-117 }**REQ-TS-3-01-117** Mobile Wallet MUST show the citizen the requester and the registered purpose, as [REQ-TS-3-01-066][req-ts-3-01-066] requires, and that it cannot answer the request, before it sends `access_denied` where the request, the Use Statement, and the certificate of [Choosing what to disclose][ts-5-11-choosing-what-to-disclose] leave no claim to present.

</div>

## Answering the response {#ts-3-01-answering-the-response}

The response endpoint decrypts what it can, matches the response to its
request by `state`, and answers the wallet before it verifies the
presentation. The answer says only that the response arrived, so that a
wallet learns nothing from it about which check of
[Verifying a presentation][ts-5-11-verifying-a-presentation] failed, as
[REQ-TS-5-10-121][req-ts-5-10-121] requires.

Where the request was opened as a link on the device the wallet runs on, the
answer carries a `redirect_uri`, and [REQ-TS-3-01-087][req-ts-3-01-087] has the
browser session that started the request come back with the response code inside
it before Verifier Core hands over the result. That stops an attacker
who started a request on their own device and relayed it to a victim from
collecting the victim's answer, the session fixation of
[OpenID4VP][ref-openid4vp] section 14.2. A QR code read across devices has no
browser session on the wallet's side to come back to, so it gets an empty
answer.

Verifier Core and Mobile Verifier refuse a response arriving after the Request
Object's `exp`. The time a
citizen takes to read the consent screen and decide is therefore bounded by the
lifetime of the Request Object, and the value the Governance Profile sets
leaves room for it. A response posted to a relayed response URI is the
relay's, which [The relay][ts-3-01-the-relay] fixes, and none of the
requirements below on decrypting, matching, or answering applies to it.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-3-01-082 }**REQ-TS-3-01-082** Verifier Core MUST decrypt a response posted to the response URI of its own request with the key the `kid` of its header names.
- [](){ #req-ts-3-01-083 }**REQ-TS-3-01-083** Verifier Core MUST refuse a response to its own response URI whose `state` matches no Request Object it signed and has not yet received a response to, or whose Request Object's `exp` has passed.
- [](){ #req-ts-3-01-084 }**REQ-TS-3-01-084** Verifier Core MUST answer a response it decrypted and matched with status `200`, a `Content-Type` of `application/json`, and a JSON object, whatever the outcome of verifying the presentation inside it.
- [](){ #req-ts-3-01-085 }**REQ-TS-3-01-085** Verifier Core MUST answer a response to its own response URI that it cannot decrypt or match with status `400` and `error` set to `invalid_request`.
- [](){ #req-ts-3-01-086 }**REQ-TS-3-01-086** Where it opened the authorization request as a link on the device the wallet runs on, Verifier Core MUST carry in its answer a `redirect_uri` holding a response code of at least 128 bits drawn for this response.
- [](){ #req-ts-3-01-087 }**REQ-TS-3-01-087** Verifier Core MUST NOT hand the result of such a request to a session that does not present the response code.
- [](){ #req-ts-3-01-088 }**REQ-TS-3-01-088** Where it showed the authorization request as a QR code, Verifier Core MUST answer with an empty JSON object.
- [](){ #req-ts-3-01-089 }**REQ-TS-3-01-089** Mobile Wallet MUST follow `redirect_uri` where the answer carries one.
- [](){ #req-ts-3-01-090 }**REQ-TS-3-01-090** Verifier Core, for a response to its own request, and Mobile Verifier MUST verify the presentation as [Verifying a presentation][ts-5-11-verifying-a-presentation] requires, with the `nonce` and the `client_id` of the Request Object that `state` matched.

</div>

## The relay {#ts-3-01-the-relay}

A merchant's device asks online through the Verifier Core of the RP Intermediary
that vouches for it, because a phone at a warung has no public address a wallet
can post to. The relay holds two things for one transaction: the Request Object
the device signed, for the wallet to fetch, and the encrypted response, for the
device to collect. It reads the first, which is signed and not encrypted, and
cannot read the second, which is encrypted to a key only the device holds.

How the device leaves a Request Object and collects a response is between
the device and the Verifier Core that vouches for it, both of the same
RP Intermediary. This specification fixes what the relay checks and holds, and
leaves the messages to that RP Intermediary.

Verifier Core also keeps a record of each Request Object it receives for the
relay, so that the RP Intermediary can tell which merchant asked for what, and
when, a refused request included: the refusal under
[REQ-TS-3-01-092][req-ts-3-01-092] shows a merchant asking beyond its category,
which [merchant certificate withdrawal][merchant-certificate-withdrawal] rests
on.

[](){ #tbl-ts-3-01-relay-record }

<figure markdown="1" class="ekdn-table">

| Field | What it holds | Where Verifier Core takes it from |
|---|---|---|
| Merchant instance | The device that asked | The `client_id` as the Request Object names it: `x509_hash` and the digest of the Verifier Device Certificate in `x5c[0]` |
| Registered use | The business category the request serves | The `use_id` of the Use Statement in `verifier_info`, where the Request Object carries one |
| Attributes requested | What the request asks for | For each credential query of `dcql_query`, the `vct_values` or `type_values` it carries and the `path` of each of its claims queries |
| Request identifier | The transaction the record belongs to | The request URI Verifier Core assigned, as [REQ-TS-3-01-093][req-ts-3-01-093] requires; for a refused request, an identifier Verifier Core draws for it |
| Time | When the request was received | Verifier Core's own clock, at the moment it received the Request Object, before it applied [REQ-TS-3-01-091][req-ts-3-01-091] and [REQ-TS-3-01-092][req-ts-3-01-092] |
| Outcome | Whether Verifier Core accepted the request | `accepted`, or `refused` with the number of the requirement it failed, [REQ-TS-3-01-091][req-ts-3-01-091] or [REQ-TS-3-01-092][req-ts-3-01-092] |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-3-01-091 }**REQ-TS-3-01-091** Verifier Core MUST accept a Request Object for the relay only after it has verified its signature under the key of `x5c[0]` and found that certificate issued by its own Verifier Issuing CA, unexpired, and not on its own CRL.
- [](){ #req-ts-3-01-092 }**REQ-TS-3-01-092** Verifier Core MUST refuse for the relay a Request Object whose query asks for an attribute outside the `claims` of the Use Statement it carries, or a Use Statement of a category the device is not bound to.
- [](){ #req-ts-3-01-093 }**REQ-TS-3-01-093** Verifier Core MUST assign each relayed transaction its own request URI and its own response URI.
- [](){ #req-ts-3-01-107 }**REQ-TS-3-01-107** Verifier Core MUST serve a relayed Request Object at its request URI byte for byte as the device signed it.
- [](){ #req-ts-3-01-094 }**REQ-TS-3-01-094** Verifier Core MUST hand a response posted to a relayed response URI to the device that left the Request Object, and to no one else.
- [](){ #req-ts-3-01-095 }**REQ-TS-3-01-095** Verifier Core MUST delete a relayed response once the device has collected it, or once the time the Governance Profile sets has passed, whichever comes first.
- [](){ #req-ts-3-01-096 }**REQ-TS-3-01-096** Verifier Core MUST NOT decrypt, log, or keep a copy of a relayed response.
- [](){ #req-ts-3-01-097 }**REQ-TS-3-01-097** Verifier Core MUST answer the wallet's `POST` to a relayed response URI with status `200` and an empty JSON object once it holds the response, because the device and not the relay matches it to its request.
- [](){ #req-ts-3-01-098 }**REQ-TS-3-01-098** Verifier Core MUST NOT link two relayed transactions as coming from one wallet, by the network address a response came from or by any other value.
- [](){ #req-ts-3-01-099 }**REQ-TS-3-01-099** Mobile Verifier MUST decrypt a response and match it by `state` on the device, as [REQ-TS-3-01-082][req-ts-3-01-082] and [REQ-TS-3-01-083][req-ts-3-01-083] require of Verifier Core.
- [](){ #req-ts-3-01-111 }**REQ-TS-3-01-111** Verifier Core MUST record the fields of [the table of relay record fields][tbl-ts-3-01-relay-record] for each Request Object it receives for the relay, whether it accepts it or refuses it.
- [](){ #req-ts-3-01-112 }**REQ-TS-3-01-112** Verifier Core MUST NOT keep in the record any value that [the table of relay record fields][tbl-ts-3-01-relay-record] does not list.
- [](){ #req-ts-3-01-113 }**REQ-TS-3-01-113** Verifier Core MUST delete a record once the time the Governance Profile sets for keeping it has passed.
- [](){ #req-ts-3-01-114 }**REQ-TS-3-01-114** Verifier Core MUST NOT write a value of a relayed Request Object into any log other than the record, except the request identifier.

</div>

## Errors {#ts-3-01-errors}

Verifier Core answers with an error at two endpoints, the request URI and the
response URI of its own requests, and never at that of a relayed one. The
wallet's own refusal travels as a response, as
[When the wallet does not answer][ts-3-01-when-the-wallet-does-not-answer]
fixes. [The table of errors][tbl-ts-3-01-errors] gives every error this
profile uses.

[](){ #tbl-ts-3-01-errors }

<figure markdown="1" class="ekdn-table">

| Sent by | Where | Code | Status | Raised when |
|---|---|---|---|---|
| Verifier Core | Request URI | None | `404` | [REQ-TS-3-01-021][req-ts-3-01-021], [REQ-TS-3-01-022][req-ts-3-01-022] |
| Verifier Core | Response URI of its own request | `invalid_request` | `400` | [REQ-TS-3-01-083][req-ts-3-01-083], [REQ-TS-3-01-085][req-ts-3-01-085] |
| Mobile Wallet | Response, encrypted | `access_denied` | None | [REQ-TS-3-01-079][req-ts-3-01-079] |
| Mobile Wallet | Response, encrypted | `invalid_request` | None | [REQ-TS-3-01-104][req-ts-3-01-104] |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-3-01-100 }**REQ-TS-3-01-100** Verifier Core MUST NOT carry a claim of the citizen, or the reason a presentation failed, in an error.
- [](){ #req-ts-3-01-101 }**REQ-TS-3-01-101** Verifier Core and Mobile Wallet MUST ignore a parameter or member that no table of this page names, except where a requirement of this page refuses it.

</div>

## Security considerations {#ts-3-01-security-considerations}

- **A request from a party that is not what it claims.** Every request is
  signed, and the wallet checks the signature by the prefix before anything
  else, [REQ-TS-3-01-055][req-ts-3-01-055] to
  [REQ-TS-3-01-058][req-ts-3-01-058], then the verifier's standing in the
  trusted list, [REQ-TS-3-01-060][req-ts-3-01-060] and [REQ-TS-3-01-106][req-ts-3-01-106]. Nothing an unsigned
  authorization request carries is acted on,
  [REQ-TS-3-01-054][req-ts-3-01-054].
- **A request URI that serves another verifier's request.** A Request Object
  copied from one verifier and served from another address still names its
  own `response_uri` and `client_id` under its signature, so the answer goes
  to the verifier that signed it, and the wallet stops when the `client_id` of the QR
  code does not match, [REQ-TS-3-01-053][req-ts-3-01-053].
- **A request replayed.** A Request Object expires,
  [REQ-TS-3-01-059][req-ts-3-01-059], serves one transaction,
  [REQ-TS-3-01-036][req-ts-3-01-036], and stops being served once
  answered, [REQ-TS-3-01-021][req-ts-3-01-021]; a presentation made for
  it carries its `nonce`, which the verifier accepts once.
- **A response read on the way.** It is encrypted to a key the verifier
  named in its signed request, [REQ-TS-3-01-072][req-ts-3-01-072] and
  [REQ-TS-3-01-076][req-ts-3-01-076]; for a merchant that key never leaves
  the device, so the relay holds ciphertext,
  [REQ-TS-3-01-040][req-ts-3-01-040] and [REQ-TS-3-01-096][req-ts-3-01-096].
- **A key stolen later.** Each key opens one response and is discarded once
  that response is decrypted or its request has expired,
  [REQ-TS-3-01-108][req-ts-3-01-108] and [REQ-TS-3-01-110][req-ts-3-01-110],
  so a ciphertext someone kept on the way, at a gateway in front of Verifier
  Core or at the relay, cannot be opened afterwards.
- **A response forged and encrypted to the verifier's public key.** The JWE
  carries no signature, and anyone can encrypt to a public key. What it
  carries is a presentation, whose signature by the credential key and whose
  `nonce` and `aud` the verifier checks,
  [REQ-TS-3-01-090][req-ts-3-01-090], as [OpenID4VP][ref-openid4vp] section
  14.5 explains.
- **A session started by an attacker and finished by a victim.** On the same
  device the redirect and its response code close it,
  [REQ-TS-3-01-086][req-ts-3-01-086] and
  [REQ-TS-3-01-087][req-ts-3-01-087]. Across devices nothing in the protocol
  closes it, because the wallet has no session to come back to. The consent
  screen stands in for it: it names the requester and the registered purpose,
  [REQ-TS-3-01-066][req-ts-3-01-066], so the citizen sees who is asking before
  anything is sent.
- **A merchant reaching past its category.** The relay refuses the request
  before it serves it, [REQ-TS-3-01-092][req-ts-3-01-092], and the wallet
  refuses what lies outside the certificate and the statement,
  [REQ-TS-3-01-062][req-ts-3-01-062] and
  [REQ-TS-3-01-065][req-ts-3-01-065].
- **A refusal used to probe the wallet.** An unchecked request gets no
  answer, [REQ-TS-3-01-078][req-ts-3-01-078], and a checked one gets one code
  for every reason, [REQ-TS-3-01-079][req-ts-3-01-079] and
  [REQ-TS-3-01-080][req-ts-3-01-080].

## Privacy considerations {#ts-3-01-privacy-considerations}

A verifier learns from an exchange the presentation and nothing about the
wallet that made it. The wallet sends no identifier of the installation, of
the device, or of its software, [REQ-TS-3-01-009][req-ts-3-01-009], and the
checks it runs read its own cache, [REQ-TS-3-01-067][req-ts-3-01-067], so
neither Trust Infrastructure nor the issuer learns that an exchange
happened.

The relay learns which merchant asked for what and when, because it reads
the request side, as
[verification by a merchant][verification-by-a-merchant] accepts. It learns
nothing of the answer, [REQ-TS-3-01-096][req-ts-3-01-096], and nothing that
lets it tell one citizen's wallet from another's,
[REQ-TS-3-01-098][req-ts-3-01-098].

What the verifier keeps of a verified presentation, and what it may not
keep, is fixed by
[What the verifier keeps][ts-5-11-what-the-verifier-keeps].

## Changelog {#ts-3-01-changelog}

<figure markdown="1" class="ekdn-table">

| Version | Date | Change |
|---|---|---|
| 1.0 draft | 21 October 2026 | First draft |

</figure>
