---
title: "[TS-4-03] Onboarding an entity and registering its keys"
description: Trust Authority's portal, where an entity's staff register a body and manage it under a second factor, and its entity endpoint, where the entity's Key Manager registers keys and certificate requests in requests signed with the update key.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §2.4, §5.7, §7.1, §7.7, Kep. 9, Kep. 28, Kep. 30; Rincian Module dan Operasi §1.1, §1.2, §2.4, §4.2; RFC 8555; tracks/0100, tracks/0151, tracks/0152, tracks/0291, tracks/0293, tracks/0346, tracks/0354, tracks/0355, tracks/0356 -->

<p class="ekdn-docid">TS-4-03</p>

# Onboarding an entity and registering its keys {#ts-4-03-onboarding-an-entity-and-registering-its-keys}

<p class="ekdn-lead" markdown="span">
An entity reaches Trust Authority through two doors: a portal where its
staff work, signed in with a second factor, and an entity endpoint where its
Key Manager registers keys. This specification fixes what each door takes
and what Trust Authority checks.
</p>

Every sentence on this page binds Trust Authority and every Module that
registers keys with it, and an Assessment Body tests them against it in the
version the Governance Profile puts in force. The key words and the
identifier `REQ-TS-4-03-nnn` follow [Common provisions](common-provisions.md).

## Who runs this and what it needs {#ts-4-03-who-runs-this-and-what-it-needs}

This specification binds two doors of Trust Authority. The portal is where
an entity's staff register a body, collect the registration code, submit
uses and ask for further permissions, report a key incident and file its
post-mortem, ask for the registration to be withdrawn, and read the
registration's record and audit trail. The entity endpoint is where the
entity's Key Manager registers keys: the nonce, the signed request, log
entries with their proofs of possession, key storage evidence, certificate
signing requests (CSRs), the binding of a registration's first entry, and
the errors.

Its conformance targets are Trust Authority, which runs both doors, and the
three Modules that hold an entity's keys in their Key Manager Component and
call the entity endpoint: Issuer Core, Verifier Core, and Wallet Backend
Service. A requirement that names *the calling Module* binds whichever of
the three holds the registration's update key.

It leaves to other documents: whether a body is registered, accredited,
authorized, or granted a use, [which the Root Authority decides under the Governance Framework][gf-approval-tiers]; how the portal looks and how a person proves who
they are before an account is opened, which are Trust Authority's and [the Governance Framework's][gf-obligations-of-every-participant]; the log and its keys, which
[Publishing and resolving a did:webvh identifier](publishing-and-resolving-a-did-webvh-identifier.md)
holds; what Decentralized Identifier (DID) Service checks before it
witnesses an entry, which
[Witnessing a log entry and serving its copy](witnessing-a-log-entry-and-serving-its-copy.md)
holds; the profile of each certificate, which
[Issuing and validating the X.509 certificates and the VICAL](issuing-and-validating-the-x509-certificates-and-the-vical.md)
holds; the Use Statement and the lifecycle of a use, which
[Registering and carrying a Use Statement](registering-and-carrying-a-use-statement.md)
holds; the Accreditation Credential, which
[Issuing and carrying an Accreditation Credential](issuing-and-carrying-an-accreditation-credential.md)
holds; the entry a registration gets on the trusted list, which
[Publishing and reading the trusted list](publishing-and-reading-the-trusted-list.md)
holds; and the address of each door, the second factors accepted at the
portal, the lifetime of a nonce and of a registration code, the rate
limits, the roots accepted for each storage value, and the grade each
storage value gives, which the Governance Profile holds. A request at the
entity endpoint names the update key by its `did:key`, which the trusted
list never carries, its countersignature is checked only here, and its
first entry carries a binding that is a message authentication code, not a
signature:
neither is one of the tokens
[Finding a signer's key from its DID](finding-a-signers-key-from-its-did.md)
lists, and this specification alone says how each is checked.

Before the first exchange, each target holds what the rules below assume:

- **Trust Authority** holds the Entity Repository, the Public Key Registry
  and the Transparency Log as its Components, the two certificate authority
  roots, each in an offline hardware security module (HSM) of its own, the
  Accreditation Credential key in its HSM, and the client certificate it
  presents to DID Service's Publisher endpoint. Its portal and its entity
  endpoint answer in the public zone, and its back office in the internal
  one.
- **A body that applies** holds the documents that establish it as a legal
  body, a person answerable for it, and the domain its identifier will
  name.
- **The calling Module** holds a Key Manager with the driver the body
  chose, the Ed25519 update key of the next log entry, and the endpoint
  address the Governance Profile publishes.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-4-03-001 }**REQ-TS-4-03-001** Trust Authority MUST meet every requirement that names Trust Authority, wherever it stands on this page.
- [](){ #req-ts-4-03-002 }**REQ-TS-4-03-002** Issuer Core, Verifier Core, and Wallet Backend Service MUST each meet every requirement that names the calling Module, wherever it stands on this page.

</div>

## What the two doors do {#ts-4-03-overview}

People and Modules come to Trust Authority for different things, and each
gets its own door. A body's staff register it, follow the Root Authority's
decisions, and act for it afterward; that work runs through the portal,
under an account bound to one person and a second factor at every sign-in,
the way a certificate authority runs an account portal beside its
certificate protocol. A body's Key Manager registers and rotates keys as a
step of its own `rotate` operation, with nobody signing in; that runs
through the entity endpoint, and it is the only reason Issuer Core,
Verifier Core and Wallet Backend Service call Trust Authority, never while a
transaction runs, as [who may call whom][who-may-call-whom] fixes.

The two meet at one point. The registration code the portal shows once,
after the Root Authority approves a registration, is what binds the first
log entry the Key Manager sends to that registration. After that the
entity endpoint knows the registration by its update key: every request is
signed with the update key of the latest log entry Trust Authority
witnessed for it, or, once that key is revoked, with the next one, and
carries a nonce Trust Authority issued and the address it was sent to, the
pattern [RFC 8555][ref-rfc8555] uses for an account. The update key signs
nothing but the log, its own proof of possession, and those requests.

Registration opens a file that is pending; the first log entry, bound to
the registration the Root Authority approved, is what makes its
accreditation granted. [Three stages of authority][three-stages-of-authority]
says what each stage decides, and [entity onboarding][entity-onboarding]
draws the path. Trust Authority holds no private key of an entity: it
receives public keys, a proof that the entity holds each matching private
key, evidence of where each key is stored, and certificate signing
requests, as [how an entity rotates a key][how-an-entity-rotates-a-key] sets
out. Its Registrar Controller answers both doors, and the other Components
each take one part of the work, as [Trust Authority][sa-trust-authority]
sets out.

## The exchange {#ts-4-03-the-exchange}

A body joins in twelve steps.

1. The person answerable for the body opens an account in the portal and
   registers the body; Trust Authority opens a pending registration.
2. The Root Authority decides on the registration and its accreditation,
   reading the report of an Assessment Body.
3. When the Root Authority approves it, the portal shows the registration
   code, once, to an account of the registration.
4. The calling Module generates the body's keys and builds the first log
   entry, carrying the update key that signs it.
5. It fetches a nonce from the entity endpoint.
6. It sends the first entry, a proof of possession of each key, the
   storage evidence of each transaction key, any certificate signing
   request, and the binding made with the registration code, signed with
   the update key.
7. Trust Authority checks the request, the binding, the storage evidence,
   and each certificate signing request.
8. It hands the entry to DID Service and receives the witness proof.
9. It issues each certificate, records each key, sets the registration
   granted, issues the Accreditation Credential, and records the
   registration's entry in Trust Registry.
10. It answers with the witness proof, any certificate, and the
    Accreditation Credential.
11. Trust Registry publishes the new trusted list.
12. The calling Module publishes the witness file, then the log, on the
    body's domain.

A later rotation takes the same path from step 4, signed with the update
key of the latest witnessed entry, or the next one once that key is
revoked, with no binding, and with no grant and
no credential at step 9. A certificate request without an entry skips the
witness at step 8 as well.

## The first entry, as exchanged {#ts-4-03-the-first-entry-as-exchanged}

Below is the exchange that brings a body into the ecosystem, from the
nonce to the answer that carries its first witness proof. The body, its
domain, its keys, and the HSM its keys live in are invented, and nothing
has been registered. Every field is exact. The body is the Identity Issuer
[the trusted list][ts-5-01-trusted-list-payload] carries, with the same
domain; the entry is the first line of
[the log as published][ts-5-02-the-log-as-published]; the request signature
verifies under the update key its `kid` names, each proof of possession
under the key it proves, and the binding under the registration code
`y2iq8fghK-zVwWZBPvUolZecIMURxv-tOfrDeGV7eZQ`, shown here so that it can be checked, which the portal showed
with the registration identifier `R2026-000117`. The witness proof is a
real `eddsa-jcs-2022` signature by Trust Authority's first witness key, and
the Accreditation Credential is the one
[Issuing and carrying an Accreditation Credential](issuing-and-carrying-an-accreditation-credential.md)
shows for the same body.

The calling Module fetches a nonce:

``` { .http title="GET /nonce, Trust Authority entity endpoint" data-format="HTTP" }
GET /nonce HTTP/1.1
Host: entities.trust.go.id
```

``` { .http title="204, a fresh nonce" data-format="HTTP" }
HTTP/1.1 204 No Content
Replay-Nonce: Stz075TjIIctkvRXPDYW0T2Lr1Ru8ud3
Cache-Control: no-store
```

and sends the first entry. The body of the request is one JSON Web
Signature (JWS) in compact serialization:

``` { .http title="POST /entities/me/keys, the first entry" data-format="HTTP" }
POST /entities/me/keys HTTP/1.1
Host: entities.trust.go.id
Content-Type: application/jose

eyJhbGciOiJFZERTQSIsImtpZCI6ImRpZDprZXk6ejZNa2hEWFp0QkhMVUtLMjdHMWQ1czVDTjRKNmVrSndCaFJyZm1rQktNS0Q1RFZYI3o2TWtoRFhadEJITFVLSzI3RzFkNXM1Q040SjZla0p3QmhScmZta0JLTUtENURWWCIsIm5vbmNlIjoiU3R6MDc1VGpJSWN0a3ZSWFBEWVcwVDJMcjFSdTh1ZDMiLCJ1cmwiOiJodHRwczovL2VudGl0aWVzLnRydXN0LmdvLmlkL2VudGl0aWVzL21lL2tleXMifQ.eyJsb2dFbnRyeSI6eyJ2ZXJzaW9uSWQiOiIxLVFtVktZMUI2R2ZnV3Vma21FSjhOV1I4M1FiWVVqZ2NGcngxVkphRnJxTHJzamUiLCJ2ZXJzaW9uVGltZSI6IjIwMjYtMDItMDFUMDA6MDA6MDBaIiwicGFyYW1ldGVycyI6eyJtZXRob2QiOiJkaWQ6d2Vidmg6MS4wIiwic2NpZCI6IlFtY0VWVDJpSlNyc3M1aGd3aU1Gc01VeEtrUm96Z0ZGNDU4UmNnZ1Q0TUYyTDQiLCJ1cGRhdGVLZXlzIjpbIno2TWtoRFhadEJITFVLSzI3RzFkNXM1Q040SjZla0p3QmhScmZta0JLTUtENURWWCJdLCJuZXh0S2V5SGFzaGVzIjpbIlFtVkM0M1BxanByVmpua3FmOG5FS1NjU3dCRThCdkpxcmZoQlcyM0JCYU1qN3MiXSwid2l0bmVzcyI6eyJ0aHJlc2hvbGQiOjEsIndpdG5lc3NlcyI6W3siaWQiOiJkaWQ6a2V5Ono2TWtyR1JzMXAyRmpzUXN4SnRLd21hVW90ekd0am1qY3ZNN3VLY25YVTdmZkxLZSJ9XX0sIndhdGNoZXJzIjpbImh0dHBzOi8vZGlkLnRydXN0LmdvLmlkIl0sInBvcnRhYmxlIjpmYWxzZX0sInN0YXRlIjp7IkBjb250ZXh0IjpbImh0dHBzOi8vd3d3LnczLm9yZy9ucy9kaWQvdjEiLCJodHRwczovL3czaWQub3JnL3NlY3VyaXR5L211bHRpa2V5L3YxIl0sImlkIjoiZGlkOndlYnZoOlFtY0VWVDJpSlNyc3M1aGd3aU1Gc01VeEtrUm96Z0ZGNDU4UmNnZ1Q0TUYyTDQ6ZHVrY2FwaWwuZ28uaWQiLCJ2ZXJpZmljYXRpb25NZXRob2QiOlt7ImlkIjoiZGlkOndlYnZoOlFtY0VWVDJpSlNyc3M1aGd3aU1Gc01VeEtrUm96Z0ZGNDU4UmNnZ1Q0TUYyTDQ6ZHVrY2FwaWwuZ28uaWQjaXNzdWFuY2Utam9zZS0xIiwidHlwZSI6Ik11bHRpa2V5IiwiY29udHJvbGxlciI6ImRpZDp3ZWJ2aDpRbWNFVlQyaUpTcnNzNWhnd2lNRnNNVXhLa1JvemdGRjQ1OFJjZ2dUNE1GMkw0OmR1a2NhcGlsLmdvLmlkIiwicHVibGljS2V5TXVsdGliYXNlIjoiekRuYWVXU3dKRHJLTHJhSGU1dzR2QTM5eEZXMlRuWmFERE5FR0dXU3lIWVNDOU5mcCJ9LHsiaWQiOiJkaWQ6d2Vidmg6UW1jRVZUMmlKU3JzczVoZ3dpTUZzTVV4S2tSb3pnRkY0NThSY2dnVDRNRjJMNDpkdWtjYXBpbC5nby5pZCNzdGF0dXMtbGlzdC0xIiwidHlwZSI6Ik11bHRpa2V5IiwiY29udHJvbGxlciI6ImRpZDp3ZWJ2aDpRbWNFVlQyaUpTcnNzNWhnd2lNRnNNVXhLa1JvemdGRjQ1OFJjZ2dUNE1GMkw0OmR1a2NhcGlsLmdvLmlkIiwicHVibGljS2V5TXVsdGliYXNlIjoiekRuYWVhbVBFS2RWNFZZbXNEYVByOWYzTHlFTkdSRlR3SFJwb052Ukx5aTJnem52RCJ9XSwiYXNzZXJ0aW9uTWV0aG9kIjpbImRpZDp3ZWJ2aDpRbWNFVlQyaUpTcnNzNWhnd2lNRnNNVXhLa1JvemdGRjQ1OFJjZ2dUNE1GMkw0OmR1a2NhcGlsLmdvLmlkI2lzc3VhbmNlLWpvc2UtMSIsImRpZDp3ZWJ2aDpRbWNFVlQyaUpTcnNzNWhnd2lNRnNNVXhLa1JvemdGRjQ1OFJjZ2dUNE1GMkw0OmR1a2NhcGlsLmdvLmlkI3N0YXR1cy1saXN0LTEiXX0sInByb29mIjpbeyJ0eXBlIjoiRGF0YUludGVncml0eVByb29mIiwiY3J5cHRvc3VpdGUiOiJlZGRzYS1qY3MtMjAyMiIsInZlcmlmaWNhdGlvbk1ldGhvZCI6ImRpZDprZXk6ejZNa2hEWFp0QkhMVUtLMjdHMWQ1czVDTjRKNmVrSndCaFJyZm1rQktNS0Q1RFZYI3o2TWtoRFhadEJITFVLSzI3RzFkNXM1Q040SjZla0p3QmhScmZta0JLTUtENURWWCIsInByb29mUHVycG9zZSI6ImFzc2VydGlvbk1ldGhvZCIsInByb29mVmFsdWUiOiJ6NjdnTDJQcEsxSm5DdzNDNU1OeVg5eHhFcUdiNjI4YlNlNkFUMVBuRUQ1NGpicnlZcUFHdzRWWE1aRGFZMUdocVhiTUdQWGZ5YlhBQW5iODExVW1lRWJhaCJ9XX0sInByb29mT2ZQb3NzZXNzaW9uIjpbImV5SjBlWEFpT2lKMmJtUXVhV1F1YVdSamRHWXVhMlY1TFhCdmNDdHFkM1FpTENKaGJHY2lPaUpGWkVSVFFTSXNJbXRwWkNJNkltUnBaRHByWlhrNmVqWk5hMmhFV0ZwMFFraE1WVXRMTWpkSE1XUTFjelZEVGpSS05tVnJTbmRDYUZKeVptMXJRa3ROUzBRMVJGWllJM28yVFd0b1JGaGFkRUpJVEZWTFN6STNSekZrTlhNMVEwNDBTalpsYTBwM1FtaFNjbVp0YTBKTFRVdEVOVVJXV0NKOS5leUpoZFdRaU9pSmthV1E2ZDJWaWRtZzZVVzFhYW5reGREbHZSbWxoUm1wb1dESmxNemgxVFhWU04yMW5kR1JNYWtoUVRVZG1ha1ZtZG5KemJXRnBjVHAwY25WemRDNW5ieTVwWkNJc0ltNXZibU5sSWpvaVUzUjZNRGMxVkdwSlNXTjBhM1pTV0ZCRVdWY3dWREpNY2pGU2RUaDFaRE1pTENKcFlYUWlPakUzTmprNU1EUXdOakI5LkI4OVNocjVrcnBEcVZwd1ZCbmlFZVBIdzFwcnZLX1dGbm5KR1RzWmhQMDk2aWlHYjJBNDJCSHliWFpXbXF5cDk1SWtaTERHTU1ubmRwZlo1SWZNRUN3IiwiZXlKMGVYQWlPaUoyYm1RdWFXUXVhV1JqZEdZdWEyVjVMWEJ2Y0N0cWQzUWlMQ0poYkdjaU9pSkZVekkxTmlJc0ltdHBaQ0k2SW1ScFpEcDNaV0oyYURwUmJXTkZWbFF5YVVwVGNuTnpOV2huZDJsTlJuTk5WWGhMYTFKdmVtZEdSalExT0ZKaloyZFVORTFHTWt3ME9tUjFhMk5oY0dsc0xtZHZMbWxrSTJsemMzVmhibU5sTFdwdmMyVXRNU0o5LmV5SmhkV1FpT2lKa2FXUTZkMlZpZG1nNlVXMWFhbmt4ZERsdlJtbGhSbXBvV0RKbE16aDFUWFZTTjIxbmRHUk1ha2hRVFVkbWFrVm1kbkp6YldGcGNUcDBjblZ6ZEM1bmJ5NXBaQ0lzSW01dmJtTmxJam9pVTNSNk1EYzFWR3BKU1dOMGEzWlNXRkJFV1Zjd1ZESk1jakZTZFRoMVpETWlMQ0pwWVhRaU9qRTNOams1TURRd05qQjkuSnpxNU1qM0xaTnVWSHhzTmlxOE50c3lyRXVKa2NmUWJ0WkVhUlRUa0dWbHpzWGhTTWR5WmRvTEZwOVM0TkhRbm8zUEU1U1hwN0VmWHlEd1dnS1dDTGciLCJleUowZVhBaU9pSjJibVF1YVdRdWFXUmpkR1l1YTJWNUxYQnZjQ3RxZDNRaUxDSmhiR2NpT2lKRlV6STFOaUlzSW10cFpDSTZJbVJwWkRwM1pXSjJhRHBSYldORlZsUXlhVXBUY25Oek5XaG5kMmxOUm5OTlZYaExhMUp2ZW1kR1JqUTFPRkpqWjJkVU5FMUdNa3cwT21SMWEyTmhjR2xzTG1kdkxtbGtJM04wWVhSMWN5MXNhWE4wTFRFaWZRLmV5SmhkV1FpT2lKa2FXUTZkMlZpZG1nNlVXMWFhbmt4ZERsdlJtbGhSbXBvV0RKbE16aDFUWFZTTjIxbmRHUk1ha2hRVFVkbWFrVm1kbkp6YldGcGNUcDBjblZ6ZEM1bmJ5NXBaQ0lzSW01dmJtTmxJam9pVTNSNk1EYzFWR3BKU1dOMGEzWlNXRkJFV1Zjd1ZESk1jakZTZFRoMVpETWlMQ0pwWVhRaU9qRTNOams1TURRd05qQjkuS1h0MFlCUUt6QVpKOFBRai1JNURrRWwzcWVIWkdQdUpsUVRUZ3pSRWtFRUhGdEt6Y3B5VWpXSnkzSHdsUldTZ29adDZLWk5lSGgyRVQxQ0l1UlY3c1EiXSwia2V5U3RvcmFnZSI6W3sia2V5IjoiekRuYWVXU3dKRHJLTHJhSGU1dzR2QTM5eEZXMlRuWmFERE5FR0dXU3lIWVNDOU5mcCIsInN0b3JhZ2UiOiJoc20iLCJldmlkZW5jZSI6eyJmb3JtYXQiOiJ4NTA5LWNoYWluIiwiY2VydHMiOlsiTUlJQjVUQ0NBWXVnQXdJQkFnSUJRVEFLQmdncWhrak9QUVFEQWpCUk1Rc3dDUVlEVlFRR0V3SkpSREVqTUNFR0ExVUVDZ3dhVUZRZ1EyOXVkRzlvSUZCbGNtRnVaMnRoZENCTGNtbHdkRzh4SFRBYkJnTlZCQU1NRkVOdmJuUnZhQ0JJVTAwZ04xRTBTeTB3TWpFNU1CNFhEVEkyTURFek1EQXdNREF3TUZvWERUUTFNRFl3TVRBd01EQXdNRm93UlRFTE1Ba0dBMVVFQmhNQ1NVUXhJekFoQmdOVkJBb01HbEJVSUVOdmJuUnZhQ0JRWlhKaGJtZHJZWFFnUzNKcGNIUnZNUkV3RHdZRFZRUUREQWhMWlhrZ01EQTBNVEJaTUJNR0J5cUdTTTQ5QWdFR0NDcUdTTTQ5QXdFSEEwSUFCRmxsdWJPbmRZUmZ0TFg1RlBMWkdaZGVHUzdrSkcwbUZ4TUNSLVg0akVJUFJWR1J1NHlQSlktcHYzM0F4OFhYbDFsQ21wS2xweV9LTTF0V1pOdzNDZHFqWURCZU1Bd0dBMVVkRXdFQl93UUNNQUF3RGdZRFZSMFBBUUhfQkFRREFnZUFNQjBHQTFVZERnUVdCQlF1TzRZN0lFVHJVN1pfWXhldS1wS1dhQ29xNmpBZkJnTlZIU01FR0RBV2dCVGI3NFZqY0l2Q2gxakFVbmxGVzNndlFkcm5wVEFLQmdncWhrak9QUVFEQWdOSUFEQkZBaUVBaDQ4R2Q2dlg3VE9LdTFGVUk2M01PeXA1SGlPeHlXWnNRbXFzanpjeXNGRUNJQ0FkU1FBRHdBdnEwLXJtaEx6MlNiUTdPNE05ZDJFbmMwS2ZHZUMwZ2tURCIsIk1JSUItakNDQVotZ0F3SUJBZ0lGQkxIWEFoa3dDZ1lJS29aSXpqMEVBd0l3VHpFTE1Ba0dBMVVFQmhNQ1NVUXhJekFoQmdOVkJBb01HbEJVSUVOdmJuUnZhQ0JRWlhKaGJtZHJZWFFnUzNKcGNIUnZNUnN3R1FZRFZRUUREQkpEYjI1MGIyZ2dTRk5OSUZKdmIzUWdRMEV3SGhjTk1qVXdOakF4TURBd01EQXdXaGNOTkRVd05qQXhNREF3TURBd1dqQlJNUXN3Q1FZRFZRUUdFd0pKUkRFak1DRUdBMVVFQ2d3YVVGUWdRMjl1ZEc5b0lGQmxjbUZ1WjJ0aGRDQkxjbWx3ZEc4eEhUQWJCZ05WQkFNTUZFTnZiblJ2YUNCSVUwMGdOMUUwU3kwd01qRTVNRmt3RXdZSEtvWkl6ajBDQVFZSUtvWkl6ajBEQVFjRFFnQUVuMmZfZUxvOW1pM2VHMlA3elJLSDBndEptbkJ3U3ZhdnNYN0ZqT1FsOEJvYTFqc0pZc3dndkFBaXJYankwZU9OekpHa29KNXU4VFhsNE1pZW5iX2VnYU5tTUdRd0VnWURWUjBUQVFIX0JBZ3dCZ0VCX3dJQkFEQU9CZ05WSFE4QkFmOEVCQU1DQWdRd0hRWURWUjBPQkJZRUZOdnZoV053aThLSFdNQlNlVVZiZUM5QjJ1ZWxNQjhHQTFVZEl3UVlNQmFBRktjN0ZpRlV6azktNzRFSDdGdnNSTExHaXVoaE1Bb0dDQ3FHU000OUJBTUNBMGtBTUVZQ0lRRFBjS0xfT3QyNmhDQTl3SUdicjhYTzc2QlZIMU1HQjNjV2pqdnh4SVZLakFJaEFPQWxNbDk2TkVKMjhKV19DZlFiNWNvSGVzNkNBN3czaWJEd3FWSldwczFqIl19fSx7ImtleSI6InpEbmFlYW1QRUtkVjRWWW1zRGFQcjlmM0x5RU5HUkZUd0hScG9OdlJMeWkyZ3pudkQiLCJzdG9yYWdlIjoiaHNtIiwiZXZpZGVuY2UiOnsiZm9ybWF0IjoieDUwOS1jaGFpbiIsImNlcnRzIjpbIk1JSUI1VENDQVl1Z0F3SUJBZ0lCUWpBS0JnZ3Foa2pPUFFRREFqQlJNUXN3Q1FZRFZRUUdFd0pKUkRFak1DRUdBMVVFQ2d3YVVGUWdRMjl1ZEc5b0lGQmxjbUZ1WjJ0aGRDQkxjbWx3ZEc4eEhUQWJCZ05WQkFNTUZFTnZiblJ2YUNCSVUwMGdOMUUwU3kwd01qRTVNQjRYRFRJMk1ERXpNREF3TURBd01Gb1hEVFExTURZd01UQXdNREF3TUZvd1JURUxNQWtHQTFVRUJoTUNTVVF4SXpBaEJnTlZCQW9NR2xCVUlFTnZiblJ2YUNCUVpYSmhibWRyWVhRZ1MzSnBjSFJ2TVJFd0R3WURWUVFEREFoTFpYa2dNREEwTWpCWk1CTUdCeXFHU000OUFnRUdDQ3FHU000OUF3RUhBMElBQkptT1BfcnhPOGt1X3ExNFNmVE5pU1B3cktYZndWamN5clJGMnZxMGJPeWFYUGZ0OXZ4cVZHSnp2WENyd2psM1lmZzFYY0ZUeFliZHZhLWJLUmRjWGF5allEQmVNQXdHQTFVZEV3RUJfd1FDTUFBd0RnWURWUjBQQVFIX0JBUURBZ2VBTUIwR0ExVWREZ1FXQkJTRnhRYTdaMWVEblhXdngxMmI3SnJ3S2VaOWdEQWZCZ05WSFNNRUdEQVdnQlRiNzRWamNJdkNoMWpBVW5sRlczZ3ZRZHJucFRBS0JnZ3Foa2pPUFFRREFnTklBREJGQWlCcjFZZ3RzcFZ3Rk4xT3dUaWhYSU1BcDZKeGRUWG9lam5ZWm13bmNkTHEyZ0loQUlsd1FjdS12VmM0SmFCMUlWMmg0RFhMdGp2ckNjQmdsUXFCdFM4RHVXTzEiLCJNSUlCLWpDQ0FaLWdBd0lCQWdJRkJMSFhBaGt3Q2dZSUtvWkl6ajBFQXdJd1R6RUxNQWtHQTFVRUJoTUNTVVF4SXpBaEJnTlZCQW9NR2xCVUlFTnZiblJ2YUNCUVpYSmhibWRyWVhRZ1MzSnBjSFJ2TVJzd0dRWURWUVFEREJKRGIyNTBiMmdnU0ZOTklGSnZiM1FnUTBFd0hoY05NalV3TmpBeE1EQXdNREF3V2hjTk5EVXdOakF4TURBd01EQXdXakJSTVFzd0NRWURWUVFHRXdKSlJERWpNQ0VHQTFVRUNnd2FVRlFnUTI5dWRHOW9JRkJsY21GdVoydGhkQ0JMY21sd2RHOHhIVEFiQmdOVkJBTU1GRU52Ym5SdmFDQklVMDBnTjFFMFN5MHdNakU1TUZrd0V3WUhLb1pJemowQ0FRWUlLb1pJemowREFRY0RRZ0FFbjJmX2VMbzltaTNlRzJQN3pSS0gwZ3RKbW5Cd1N2YXZzWDdGak9RbDhCb2ExanNKWXN3Z3ZBQWlyWGp5MGVPTnpKR2tvSjV1OFRYbDRNaWVuYl9lZ2FObU1HUXdFZ1lEVlIwVEFRSF9CQWd3QmdFQl93SUJBREFPQmdOVkhROEJBZjhFQkFNQ0FnUXdIUVlEVlIwT0JCWUVGTnZ2aFdOd2k4S0hXTUJTZVVWYmVDOUIydWVsTUI4R0ExVWRJd1FZTUJhQUZLYzdGaUZVems5LTc0RUg3RnZzUkxMR2l1aGhNQW9HQ0NxR1NNNDlCQU1DQTBrQU1FWUNJUURQY0tMX090MjZoQ0E5d0lHYnI4WE83NkJWSDFNR0IzY1dqanZ4eElWS2pBSWhBT0FsTWw5Nk5FSjI4SldfQ2ZRYjVjb0hlczZDQTd3M2liRHdxVkpXcHMxaiJdfX0seyJrZXkiOiJ6RG5hZVZnN1ZvN0o5RTd3UWFYQW8zNFhNUWNzblBXUGg0TFJmeEhRQjFrNnpiQ3NZIiwic3RvcmFnZSI6ImhzbSIsImV2aWRlbmNlIjp7ImZvcm1hdCI6Ing1MDktY2hhaW4iLCJjZXJ0cyI6WyJNSUlCNVRDQ0FZdWdBd0lCQWdJQlF6QUtCZ2dxaGtqT1BRUURBakJSTVFzd0NRWURWUVFHRXdKSlJERWpNQ0VHQTFVRUNnd2FVRlFnUTI5dWRHOW9JRkJsY21GdVoydGhkQ0JMY21sd2RHOHhIVEFiQmdOVkJBTU1GRU52Ym5SdmFDQklVMDBnTjFFMFN5MHdNakU1TUI0WERUSTJNREV6TURBd01EQXdNRm9YRFRRMU1EWXdNVEF3TURBd01Gb3dSVEVMTUFrR0ExVUVCaE1DU1VReEl6QWhCZ05WQkFvTUdsQlVJRU52Ym5SdmFDQlFaWEpoYm1kcllYUWdTM0pwY0hSdk1SRXdEd1lEVlFRRERBaExaWGtnTURBME16QlpNQk1HQnlxR1NNNDlBZ0VHQ0NxR1NNNDlBd0VIQTBJQUJFM3FIeVJPWjBIVzNPTTQzZm9TY0d5V3ZYb1NnaFp3d1E2MUhPa09mNDZfWEtSLVRCYzdZWmlOS0dkcjdJYWFMZ09FdGh0UEpzblhaeXd0X08tRWl2Q2pZREJlTUF3R0ExVWRFd0VCX3dRQ01BQXdEZ1lEVlIwUEFRSF9CQVFEQWdlQU1CMEdBMVVkRGdRV0JCVFZES3BsdEdEaEJBTFRseTl6dUREYml3UGFLREFmQmdOVkhTTUVHREFXZ0JUYjc0VmpjSXZDaDFqQVVubEZXM2d2UWRybnBUQUtCZ2dxaGtqT1BRUURBZ05JQURCRkFpRUFpajlJUkRqVmJTWnpPTXBXOUl3UHRpaTBxQ2taOW14TEFNRGJ5LVVHQzNvQ0lEOFBQRUMwaEtzeTJ2eUQtb1dKODBqWkt3UWhaYkF4VmJiNGo5YURSazJrIiwiTUlJQi1qQ0NBWi1nQXdJQkFnSUZCTEhYQWhrd0NnWUlLb1pJemowRUF3SXdUekVMTUFrR0ExVUVCaE1DU1VReEl6QWhCZ05WQkFvTUdsQlVJRU52Ym5SdmFDQlFaWEpoYm1kcllYUWdTM0pwY0hSdk1Sc3dHUVlEVlFRRERCSkRiMjUwYjJnZ1NGTk5JRkp2YjNRZ1EwRXdIaGNOTWpVd05qQXhNREF3TURBd1doY05ORFV3TmpBeE1EQXdNREF3V2pCUk1Rc3dDUVlEVlFRR0V3SkpSREVqTUNFR0ExVUVDZ3dhVUZRZ1EyOXVkRzlvSUZCbGNtRnVaMnRoZENCTGNtbHdkRzh4SFRBYkJnTlZCQU1NRkVOdmJuUnZhQ0JJVTAwZ04xRTBTeTB3TWpFNU1Ga3dFd1lIS29aSXpqMENBUVlJS29aSXpqMERBUWNEUWdBRW4yZl9lTG85bWkzZUcyUDd6UktIMGd0Sm1uQndTdmF2c1g3RmpPUWw4Qm9hMWpzSllzd2d2QUFpclhqeTBlT056Skdrb0o1dThUWGw0TWllbmJfZWdhTm1NR1F3RWdZRFZSMFRBUUhfQkFnd0JnRUJfd0lCQURBT0JnTlZIUThCQWY4RUJBTUNBZ1F3SFFZRFZSME9CQllFRk52dmhXTndpOEtIV01CU2VVVmJlQzlCMnVlbE1COEdBMVVkSXdRWU1CYUFGS2M3RmlGVXprOS03NEVIN0Z2c1JMTEdpdWhoTUFvR0NDcUdTTTQ5QkFNQ0Ewa0FNRVlDSVFEUGNLTF9PdDI2aENBOXdJR2JyOFhPNzZCVkgxTUdCM2NXamp2eHhJVktqQUloQU9BbE1sOTZORUoyOEpXX0NmUWI1Y29IZXM2Q0E3dzNpYkR3cVZKV3BzMWoiXX19XSwiY2VydGlmaWNhdGlvblJlcXVlc3RzIjpbeyJwdXJwb3NlIjoiaXNzdWFuY2UtY29zZSIsImNzciI6Ik1JSUJPRENCM2dJQkFEQjhNUXN3Q1FZRFZRUUdFd0pKUkRFLU1Ed0dBMVVFQ2d3MVJHbHlaV3QwYjNKaGRDQktaVzVrWlhKaGJDQkxaWEJsYm1SMVpIVnJZVzRnWkdGdUlGQmxibU5oZEdGMFlXNGdVMmx3YVd3eExUQXJCZ05WQkFNTUpFUjFhMk5oY0dsc0lHMWtiMk1nUkc5amRXMWxiblFnVTJsbmJtVnlJREl3TWpZdE1EQlpNQk1HQnlxR1NNNDlBZ0VHQ0NxR1NNNDlBd0VIQTBJQUJFM3FIeVJPWjBIVzNPTTQzZm9TY0d5V3ZYb1NnaFp3d1E2MUhPa09mNDZfWEtSLVRCYzdZWmlOS0dkcjdJYWFMZ09FdGh0UEpzblhaeXd0X08tRWl2Q2dBREFLQmdncWhrak9QUVFEQWdOSkFEQkdBaUVBLTJRSlpVdjlsTHBUX2V2LXpsZUM2YUxueURtRHJTUWdsUTdFdWxERl9VMENJUUMwY2JReHFBMXRweFE2RjlxNGtwMGlReTlSeE9TTjdSV2owTXc1bHkyWG1RIn1dLCJyZWdpc3RyYXRpb25CaW5kaW5nIjoiZXlKaGJHY2lPaUpJVXpJMU5pSXNJbXRwWkNJNklsSXlNREkyTFRBd01ERXhOeUlzSW5WeWJDSTZJbWgwZEhCek9pOHZaVzUwYVhScFpYTXVkSEoxYzNRdVoyOHVhV1F2Wlc1MGFYUnBaWE12YldVdmEyVjVjeUo5LlpHbGtPbXRsZVRwNk5rMXJhRVJZV25SQ1NFeFZTMHN5TjBjeFpEVnpOVU5PTkVvMlpXdEtkMEpvVW5KbWJXdENTMDFMUkRWRVZsZ2plalpOYTJoRVdGcDBRa2hNVlV0TE1qZEhNV1ExY3pWRFRqUktObVZyU25kQ2FGSnlabTFyUWt0TlMwUTFSRlpZLmM5UDc0MDhjbDNjOGpUU0xTdEJkQVlfZVJPXzRZSEFGM0RTQjFGS1R6QmcifQ.0KGfI8NVrNK5pZLH0KGZz6CxQy9of7fR7aGGvBeOtDmaGmIPaU70bo6ya2FSzNx1l1jiMbNIPKZOkIcvoAlXCw
```

Decoded, its protected header names the update key the entry carries, the
nonce, and the address; its payload carries the entry, three proofs of
possession, the storage evidence of three transaction keys, the request for
the Document Signer Certificate of the `issuance-cose` key, which the log
does not carry, and the binding:

``` { .json title="The first entry request, decoded" data-format="JSON" }
{
  "protected": {
    "alg": "EdDSA",
    "kid": "did:key:z6MkhDXZtBHLUKK27G1d5s5CN4J6ekJwBhRrfmkBKMKD5DVX#z6MkhDXZtBHLUKK27G1d5s5CN4J6ekJwBhRrfmkBKMKD5DVX",
    "nonce": "Stz075TjIIctkvRXPDYW0T2Lr1Ru8ud3",
    "url": "https://entities.trust.go.id/entities/me/keys"
  },
  "payload": {
    "logEntry": {
      "versionId": "1-QmVKY1B6GfgWufkmEJ8NWR83QbYUjgcFrx1VJaFrqLrsje",
      "versionTime": "2026-02-01T00:00:00Z",
      "parameters": {
        "method": "did:webvh:1.0",
        "scid": "QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4",
        "updateKeys": [
          "z6MkhDXZtBHLUKK27G1d5s5CN4J6ekJwBhRrfmkBKMKD5DVX"
        ],
        "nextKeyHashes": [
          "QmVC43PqjprVjnkqf8nEKScSwBE8BvJqrfhBW23BBaMj7s"
        ],
        "witness": {
          "threshold": 1,
          "witnesses": [
            {
              "id": "did:key:z6MkrGRs1p2FjsQsxJtKwmaUotzGtjmjcvM7uKcnXU7ffLKe"
            }
          ]
        },
        "watchers": [
          "https://did.trust.go.id"
        ],
        "portable": false
      },
      "state": {
        "@context": [
          "https://www.w3.org/ns/did/v1",
          "https://w3id.org/security/multikey/v1"
        ],
        "id": "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id",
        "verificationMethod": [
          {
            "id": "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id#issuance-jose-1",
            "type": "Multikey",
            "controller": "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id",
            "publicKeyMultibase": "zDnaeWSwJDrKLraHe5w4vA39xFW2TnZaDDNEGGWSyHYSC9Nfp"
          },
          {
            "id": "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id#status-list-1",
            "type": "Multikey",
            "controller": "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id",
            "publicKeyMultibase": "zDnaeamPEKdV4VYmsDaPr9f3LyENGRFTwHRpoNvRLyi2gznvD"
          }
        ],
        "assertionMethod": [
          "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id#issuance-jose-1",
          "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id#status-list-1"
        ]
      },
      "proof": [
        {
          "type": "DataIntegrityProof",
          "cryptosuite": "eddsa-jcs-2022",
          "verificationMethod": "did:key:z6MkhDXZtBHLUKK27G1d5s5CN4J6ekJwBhRrfmkBKMKD5DVX#z6MkhDXZtBHLUKK27G1d5s5CN4J6ekJwBhRrfmkBKMKD5DVX",
          "proofPurpose": "assertionMethod",
          "proofValue": "z67gL2PpK1JnCw3C5MNyX9xxEqGb628bSe6AT1PnED54jbryYqAGw4VXMZDaY1GhqXbMGPXfybXAAnb811UmeEbah"
        }
      ]
    },
    "proofOfPossession": [
      "eyJ0eXAiOiJ2bmQuaWQuaWRjdGYua2V5LXBvcCtqd3QiLCJhbGciOiJFZERTQSIsImtpZCI6ImRpZDprZXk6ejZNa2hEWFp0QkhMVUtLMjdHMWQ1czVDTjRKNmVrSndCaFJyZm1rQktNS0Q1RFZYI3o2TWtoRFhadEJITFVLSzI3RzFkNXM1Q040SjZla0p3QmhScmZta0JLTUtENURWWCJ9.eyJhdWQiOiJkaWQ6d2Vidmg6UW1aankxdDlvRmlhRmpoWDJlMzh1TXVSN21ndGRMakhQTUdmakVmdnJzbWFpcTp0cnVzdC5nby5pZCIsIm5vbmNlIjoiU3R6MDc1VGpJSWN0a3ZSWFBEWVcwVDJMcjFSdTh1ZDMiLCJpYXQiOjE3Njk5MDQwNjB9.B89Shr5krpDqVpwVBniEePHw1prvK_WFnnJGTsZhP096iiGb2A42BHybXZWmqyp95IkZLDGMMnndpfZ5IfMECw",
      "eyJ0eXAiOiJ2bmQuaWQuaWRjdGYua2V5LXBvcCtqd3QiLCJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDp3ZWJ2aDpRbWNFVlQyaUpTcnNzNWhnd2lNRnNNVXhLa1JvemdGRjQ1OFJjZ2dUNE1GMkw0OmR1a2NhcGlsLmdvLmlkI2lzc3VhbmNlLWpvc2UtMSJ9.eyJhdWQiOiJkaWQ6d2Vidmg6UW1aankxdDlvRmlhRmpoWDJlMzh1TXVSN21ndGRMakhQTUdmakVmdnJzbWFpcTp0cnVzdC5nby5pZCIsIm5vbmNlIjoiU3R6MDc1VGpJSWN0a3ZSWFBEWVcwVDJMcjFSdTh1ZDMiLCJpYXQiOjE3Njk5MDQwNjB9.Jzq5Mj3LZNuVHxsNiq8NtsyrEuJkcfQbtZEaRTTkGVlzsXhSMdyZdoLFp9S4NHQno3PE5SXp7EfXyDwWgKWCLg",
      "eyJ0eXAiOiJ2bmQuaWQuaWRjdGYua2V5LXBvcCtqd3QiLCJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDp3ZWJ2aDpRbWNFVlQyaUpTcnNzNWhnd2lNRnNNVXhLa1JvemdGRjQ1OFJjZ2dUNE1GMkw0OmR1a2NhcGlsLmdvLmlkI3N0YXR1cy1saXN0LTEifQ.eyJhdWQiOiJkaWQ6d2Vidmg6UW1aankxdDlvRmlhRmpoWDJlMzh1TXVSN21ndGRMakhQTUdmakVmdnJzbWFpcTp0cnVzdC5nby5pZCIsIm5vbmNlIjoiU3R6MDc1VGpJSWN0a3ZSWFBEWVcwVDJMcjFSdTh1ZDMiLCJpYXQiOjE3Njk5MDQwNjB9.KXt0YBQKzAZJ8PQj-I5DkEl3qeHZGPuJlQTTgzREkEEHFtKzcpyUjWJy3HwlRWSgoZt6KZNeHh2ET1CIuRV7sQ"
    ],
    "keyStorage": [
      {
        "key": "zDnaeWSwJDrKLraHe5w4vA39xFW2TnZaDDNEGGWSyHYSC9Nfp",
        "storage": "hsm",
        "evidence": {
          "format": "x509-chain",
          "certs": [
            "MIIB5TCCAYugAwIBAgIBQTAKBggqhkjOPQQDAjBRMQswCQYDVQQGEwJJRDEjMCEGA1UECgwaUFQgQ29udG9oIFBlcmFuZ2thdCBLcmlwdG8xHTAbBgNVBAMMFENvbnRvaCBIU00gN1E0Sy0wMjE5MB4XDTI2MDEzMDAwMDAwMFoXDTQ1MDYwMTAwMDAwMFowRTELMAkGA1UEBhMCSUQxIzAhBgNVBAoMGlBUIENvbnRvaCBQZXJhbmdrYXQgS3JpcHRvMREwDwYDVQQDDAhLZXkgMDA0MTBZMBMGByqGSM49AgEGCCqGSM49AwEHA0IABFllubOndYRftLX5FPLZGZdeGS7kJG0mFxMCR-X4jEIPRVGRu4yPJY-pv33Ax8XXl1lCmpKlpy_KM1tWZNw3CdqjYDBeMAwGA1UdEwEB_wQCMAAwDgYDVR0PAQH_BAQDAgeAMB0GA1UdDgQWBBQuO4Y7IETrU7Z_Yxeu-pKWaCoq6jAfBgNVHSMEGDAWgBTb74VjcIvCh1jAUnlFW3gvQdrnpTAKBggqhkjOPQQDAgNIADBFAiEAh48Gd6vX7TOKu1FUI63MOyp5HiOxyWZsQmqsjzcysFECICAdSQADwAvq0-rmhLz2SbQ7O4M9d2Enc0KfGeC0gkTD",
            "MIIB-jCCAZ-gAwIBAgIFBLHXAhkwCgYIKoZIzj0EAwIwTzELMAkGA1UEBhMCSUQxIzAhBgNVBAoMGlBUIENvbnRvaCBQZXJhbmdrYXQgS3JpcHRvMRswGQYDVQQDDBJDb250b2ggSFNNIFJvb3QgQ0EwHhcNMjUwNjAxMDAwMDAwWhcNNDUwNjAxMDAwMDAwWjBRMQswCQYDVQQGEwJJRDEjMCEGA1UECgwaUFQgQ29udG9oIFBlcmFuZ2thdCBLcmlwdG8xHTAbBgNVBAMMFENvbnRvaCBIU00gN1E0Sy0wMjE5MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEn2f_eLo9mi3eG2P7zRKH0gtJmnBwSvavsX7FjOQl8Boa1jsJYswgvAAirXjy0eONzJGkoJ5u8TXl4Mienb_egaNmMGQwEgYDVR0TAQH_BAgwBgEB_wIBADAOBgNVHQ8BAf8EBAMCAgQwHQYDVR0OBBYEFNvvhWNwi8KHWMBSeUVbeC9B2uelMB8GA1UdIwQYMBaAFKc7FiFUzk9-74EH7FvsRLLGiuhhMAoGCCqGSM49BAMCA0kAMEYCIQDPcKL_Ot26hCA9wIGbr8XO76BVH1MGB3cWjjvxxIVKjAIhAOAlMl96NEJ28JW_CfQb5coHes6CA7w3ibDwqVJWps1j"
          ]
        }
      },
      {
        "key": "zDnaeamPEKdV4VYmsDaPr9f3LyENGRFTwHRpoNvRLyi2gznvD",
        "storage": "hsm",
        "evidence": {
          "format": "x509-chain",
          "certs": [
            "MIIB5TCCAYugAwIBAgIBQjAKBggqhkjOPQQDAjBRMQswCQYDVQQGEwJJRDEjMCEGA1UECgwaUFQgQ29udG9oIFBlcmFuZ2thdCBLcmlwdG8xHTAbBgNVBAMMFENvbnRvaCBIU00gN1E0Sy0wMjE5MB4XDTI2MDEzMDAwMDAwMFoXDTQ1MDYwMTAwMDAwMFowRTELMAkGA1UEBhMCSUQxIzAhBgNVBAoMGlBUIENvbnRvaCBQZXJhbmdrYXQgS3JpcHRvMREwDwYDVQQDDAhLZXkgMDA0MjBZMBMGByqGSM49AgEGCCqGSM49AwEHA0IABJmOP_rxO8ku_q14SfTNiSPwrKXfwVjcyrRF2vq0bOyaXPft9vxqVGJzvXCrwjl3Yfg1XcFTxYbdva-bKRdcXayjYDBeMAwGA1UdEwEB_wQCMAAwDgYDVR0PAQH_BAQDAgeAMB0GA1UdDgQWBBSFxQa7Z1eDnXWvx12b7JrwKeZ9gDAfBgNVHSMEGDAWgBTb74VjcIvCh1jAUnlFW3gvQdrnpTAKBggqhkjOPQQDAgNIADBFAiBr1YgtspVwFN1OwTihXIMAp6JxdTXoejnYZmwncdLq2gIhAIlwQcu-vVc4JaB1IV2h4DXLtjvrCcBglQqBtS8DuWO1",
            "MIIB-jCCAZ-gAwIBAgIFBLHXAhkwCgYIKoZIzj0EAwIwTzELMAkGA1UEBhMCSUQxIzAhBgNVBAoMGlBUIENvbnRvaCBQZXJhbmdrYXQgS3JpcHRvMRswGQYDVQQDDBJDb250b2ggSFNNIFJvb3QgQ0EwHhcNMjUwNjAxMDAwMDAwWhcNNDUwNjAxMDAwMDAwWjBRMQswCQYDVQQGEwJJRDEjMCEGA1UECgwaUFQgQ29udG9oIFBlcmFuZ2thdCBLcmlwdG8xHTAbBgNVBAMMFENvbnRvaCBIU00gN1E0Sy0wMjE5MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEn2f_eLo9mi3eG2P7zRKH0gtJmnBwSvavsX7FjOQl8Boa1jsJYswgvAAirXjy0eONzJGkoJ5u8TXl4Mienb_egaNmMGQwEgYDVR0TAQH_BAgwBgEB_wIBADAOBgNVHQ8BAf8EBAMCAgQwHQYDVR0OBBYEFNvvhWNwi8KHWMBSeUVbeC9B2uelMB8GA1UdIwQYMBaAFKc7FiFUzk9-74EH7FvsRLLGiuhhMAoGCCqGSM49BAMCA0kAMEYCIQDPcKL_Ot26hCA9wIGbr8XO76BVH1MGB3cWjjvxxIVKjAIhAOAlMl96NEJ28JW_CfQb5coHes6CA7w3ibDwqVJWps1j"
          ]
        }
      },
      {
        "key": "zDnaeVg7Vo7J9E7wQaXAo34XMQcsnPWPh4LRfxHQB1k6zbCsY",
        "storage": "hsm",
        "evidence": {
          "format": "x509-chain",
          "certs": [
            "MIIB5TCCAYugAwIBAgIBQzAKBggqhkjOPQQDAjBRMQswCQYDVQQGEwJJRDEjMCEGA1UECgwaUFQgQ29udG9oIFBlcmFuZ2thdCBLcmlwdG8xHTAbBgNVBAMMFENvbnRvaCBIU00gN1E0Sy0wMjE5MB4XDTI2MDEzMDAwMDAwMFoXDTQ1MDYwMTAwMDAwMFowRTELMAkGA1UEBhMCSUQxIzAhBgNVBAoMGlBUIENvbnRvaCBQZXJhbmdrYXQgS3JpcHRvMREwDwYDVQQDDAhLZXkgMDA0MzBZMBMGByqGSM49AgEGCCqGSM49AwEHA0IABE3qHyROZ0HW3OM43foScGyWvXoSghZwwQ61HOkOf46_XKR-TBc7YZiNKGdr7IaaLgOEthtPJsnXZywt_O-EivCjYDBeMAwGA1UdEwEB_wQCMAAwDgYDVR0PAQH_BAQDAgeAMB0GA1UdDgQWBBTVDKpltGDhBALTly9zuDDbiwPaKDAfBgNVHSMEGDAWgBTb74VjcIvCh1jAUnlFW3gvQdrnpTAKBggqhkjOPQQDAgNIADBFAiEAij9IRDjVbSZzOMpW9IwPtii0qCkZ9mxLAMDby-UGC3oCID8PPEC0hKsy2vyD-oWJ80jZKwQhZbAxVbb4j9aDRk2k",
            "MIIB-jCCAZ-gAwIBAgIFBLHXAhkwCgYIKoZIzj0EAwIwTzELMAkGA1UEBhMCSUQxIzAhBgNVBAoMGlBUIENvbnRvaCBQZXJhbmdrYXQgS3JpcHRvMRswGQYDVQQDDBJDb250b2ggSFNNIFJvb3QgQ0EwHhcNMjUwNjAxMDAwMDAwWhcNNDUwNjAxMDAwMDAwWjBRMQswCQYDVQQGEwJJRDEjMCEGA1UECgwaUFQgQ29udG9oIFBlcmFuZ2thdCBLcmlwdG8xHTAbBgNVBAMMFENvbnRvaCBIU00gN1E0Sy0wMjE5MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEn2f_eLo9mi3eG2P7zRKH0gtJmnBwSvavsX7FjOQl8Boa1jsJYswgvAAirXjy0eONzJGkoJ5u8TXl4Mienb_egaNmMGQwEgYDVR0TAQH_BAgwBgEB_wIBADAOBgNVHQ8BAf8EBAMCAgQwHQYDVR0OBBYEFNvvhWNwi8KHWMBSeUVbeC9B2uelMB8GA1UdIwQYMBaAFKc7FiFUzk9-74EH7FvsRLLGiuhhMAoGCCqGSM49BAMCA0kAMEYCIQDPcKL_Ot26hCA9wIGbr8XO76BVH1MGB3cWjjvxxIVKjAIhAOAlMl96NEJ28JW_CfQb5coHes6CA7w3ibDwqVJWps1j"
          ]
        }
      }
    ],
    "certificationRequests": [
      {
        "purpose": "issuance-cose",
        "csr": "MIIBODCB3gIBADB8MQswCQYDVQQGEwJJRDE-MDwGA1UECgw1RGlyZWt0b3JhdCBKZW5kZXJhbCBLZXBlbmR1ZHVrYW4gZGFuIFBlbmNhdGF0YW4gU2lwaWwxLTArBgNVBAMMJER1a2NhcGlsIG1kb2MgRG9jdW1lbnQgU2lnbmVyIDIwMjYtMDBZMBMGByqGSM49AgEGCCqGSM49AwEHA0IABE3qHyROZ0HW3OM43foScGyWvXoSghZwwQ61HOkOf46_XKR-TBc7YZiNKGdr7IaaLgOEthtPJsnXZywt_O-EivCgADAKBggqhkjOPQQDAgNJADBGAiEA-2QJZUv9lLpT_ev-zleC6aLnyDmDrSQglQ7EulDF_U0CIQC0cbQxqA1tpxQ6F9q4kp0iQy9RxOSN7RWj0Mw5ly2XmQ"
      }
    ],
    "registrationBinding": "eyJhbGciOiJIUzI1NiIsImtpZCI6IlIyMDI2LTAwMDExNyIsInVybCI6Imh0dHBzOi8vZW50aXRpZXMudHJ1c3QuZ28uaWQvZW50aXRpZXMvbWUva2V5cyJ9.ZGlkOmtleTp6Nk1raERYWnRCSExVS0syN0cxZDVzNUNONEo2ZWtKd0JoUnJmbWtCS01LRDVEVlgjejZNa2hEWFp0QkhMVUtLMjdHMWQ1czVDTjRKNmVrSndCaFJyZm1rQktNS0Q1RFZY.c9P7408cl3c8jTSLStBdAY_eRO_4YHAF3DSB1FKTzBg"
  }
}
```

Trust Authority answers with the witness proof, the Document Signer
Certificate, and the Accreditation Credential, and with the nonce the next
request takes. The certificate is the one the trusted list later names
revoked by its subject key identifier, and whose serial number is on
[the Issuer Root CA revocation list][ts-5-04-revocation]:

``` { .http title="200, the answer to the first entry" data-format="HTTP" }
HTTP/1.1 200 OK
Replay-Nonce: 2DWd3RDvhnHWQ5rCpbZLzTV-CEcXEeiI
Cache-Control: no-store
Content-Type: application/json

{
  "witness": {
    "versionId": "1-QmVKY1B6GfgWufkmEJ8NWR83QbYUjgcFrx1VJaFrqLrsje",
    "proof": [
      {
        "type": "DataIntegrityProof",
        "cryptosuite": "eddsa-jcs-2022",
        "verificationMethod": "did:key:z6MkrGRs1p2FjsQsxJtKwmaUotzGtjmjcvM7uKcnXU7ffLKe#z6MkrGRs1p2FjsQsxJtKwmaUotzGtjmjcvM7uKcnXU7ffLKe",
        "proofPurpose": "assertionMethod",
        "proofValue": "z4A7yGKW2NGVnwNn1pTYfFErb5qqtUTtNkGKkos3hgNWmvQxyi9iWBw9GpbnXMPs6nL3Aezptjs7gxjW3jkEiRTUN"
      }
    ]
  },
  "certificates": [
    {
      "purpose": "issuance-cose",
      "certificate": "MIICqzCCAlGgAwIBAgINAPkhi90QexsE_B8W5TAKBggqhkjOPQQDAjBZMQswCQYDVQQGEwJJRDErMCkGA1UECgwiVHJ1c3QgQXV0aG9yaXR5IFJlcHVibGlrIEluZG9uZXNpYTEdMBsGA1UEAwwUSURDVEYgSXNzdWVyIFJvb3QgQ0EwHhcNMjYwMjAxMDAwMDAwWhcNMjcwNTAyMDAwMDAwWjB8MQswCQYDVQQGEwJJRDE-MDwGA1UECgw1RGlyZWt0b3JhdCBKZW5kZXJhbCBLZXBlbmR1ZHVrYW4gZGFuIFBlbmNhdGF0YW4gU2lwaWwxLTArBgNVBAMMJER1a2NhcGlsIG1kb2MgRG9jdW1lbnQgU2lnbmVyIDIwMjYtMDBZMBMGByqGSM49AgEGCCqGSM49AwEHA0IABE3qHyROZ0HW3OM43foScGyWvXoSghZwwQ61HOkOf46_XKR-TBc7YZiNKGdr7IaaLgOEthtPJsnXZywt_O-EivCjgdowgdcwDAYDVR0TAQH_BAIwADAOBgNVHQ8BAf8EBAMCB4AwFQYDVR0lAQH_BAswCQYHKIGMXQUBAjAfBgNVHSMEGDAWgBT78NVqsL_agEoy7d0zzMnd0oN5mjAdBgNVHQ4EFgQU1QyqZbRg4QQC05cvc7gw24sD2igwHgYDVR0SBBcwFYYTaHR0cHM6Ly90cnVzdC5nby5pZDBABgNVHR8EOTA3MDWgM6Axhi9odHRwczovL3JlZ2lzdHJ5LnRydXN0LmdvLmlkL2NybC9pc3N1ZXItcm9vdC1jYTAKBggqhkjOPQQDAgNIADBFAiBxyh5io28JaIG1nndZKpMfliOZK1XGrjUEWBa99v8yRAIhAJARWhB8NbKGeLI-opvhk1SUZtHsE0hn9CEQgdwK2V1z"
    }
  ],
  "accreditationCredential": "eyJ0eXAiOiJkYytzZC1qd3QiLCJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDp3ZWJ2aDpRbVpqeTF0OW9GaWFGamhYMmUzOHVNdVI3bWd0ZExqSFBNR2ZqRWZ2cnNtYWlxOnRydXN0LmdvLmlkI2FjY3JlZGl0YXRpb24tY3JlZGVudGlhbC0xIn0.eyJpc3MiOiJkaWQ6d2Vidmg6UW1aankxdDlvRmlhRmpoWDJlMzh1TXVSN21ndGRMakhQTUdmakVmdnJzbWFpcTp0cnVzdC5nby5pZCIsInZjdCI6ImlkLmlkY3RmLmFjY3JlZGl0YXRpb24uMSIsInN1YiI6ImRpZDp3ZWJ2aDpRbWNFVlQyaUpTcnNzNWhnd2lNRnNNVXhLa1JvemdGRjQ1OFJjZ2dUNE1GMkw0OmR1a2NhcGlsLmdvLmlkIiwiZW50aXR5X25hbWUiOiJEaXJla3RvcmF0IEplbmRlcmFsIEtlcGVuZHVkdWthbiBkYW4gUGVuY2F0YXRhbiBTaXBpbCIsImVudGl0eV90eXBlIjpbImh0dHBzOi8vaWRjdGYuaWQvbnMvMTk2MDIvU3ZjVHlwZS9JZGVudGl0eUlzc3VlciJdLCJzY29wZSI6W3siYWN0aW9uIjoiaXNzdWUiLCJyZXNvdXJjZSI6ImlkLmlkY3RmLmt0cC4xIn1dLCJzdGF0dXMiOnsic3RhdHVzX2xpc3QiOnsiaWR4IjoxNywidXJpIjoiaHR0cHM6Ly9yZWdpc3RyeS50cnVzdC5nby5pZC9zdGF0dXMvYWNjcmVkaXRhdGlvbnMtMSJ9fSwiaWF0IjoxNzY5OTA0MDAwLCJleHAiOjE4MzI5NzYwMDB9.kQVtLszmfPhVBfSdumMGFHCV7GB9y1QWmaScMCn_f8tHbHW6kjTw5qmR4B9A2DZBmNtlQxtH3W1j3eRSS_f3vA~"
}
```

The host is an illustration; the Governance Profile publishes the address
of the endpoint in force.

## The portal {#ts-4-03-the-portal}

The portal is a web application for people, and it is not a protocol: this
specification fixes what Trust Authority takes in it, checks, keeps and
shows, and not how it looks. Everything a person does there is done under
an account, and every account acts for the registrations the person
answerable for each of them names.

### Accounts {#ts-4-03-accounts}

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-4-03-003 }**REQ-TS-4-03-003** Trust Authority MUST serve the portal over HTTP with Transport Layer Security (TLS) only, at the address the Governance Profile publishes.
- [](){ #req-ts-4-03-004 }**REQ-TS-4-03-004** Trust Authority MUST require, at every sign-in to the portal, a second factor of a kind the Governance Profile accepts.
- [](){ #req-ts-4-03-005 }**REQ-TS-4-03-005** Trust Authority MUST bind each portal account to one natural person.
- [](){ #req-ts-4-03-006 }**REQ-TS-4-03-006** Trust Authority MUST take the holder of the account that registers a body as the person answerable the registration names.
- [](){ #req-ts-4-03-007 }**REQ-TS-4-03-007** Trust Authority MUST let an account act for a registration only when the person answerable for that registration has named its holder.
- [](){ #req-ts-4-03-008 }**REQ-TS-4-03-008** Trust Authority MUST NOT give a portal account any operation of its back office.
- [](){ #req-ts-4-03-009 }**REQ-TS-4-03-009** Trust Authority MUST record each action taken in the portal with the account that took it.
- [](){ #req-ts-4-03-010 }**REQ-TS-4-03-010** Trust Authority MUST limit the rate of requests from one network address at the portal to the limit the Governance Profile sets.
- [](){ #req-ts-4-03-122 }**REQ-TS-4-03-122** Trust Authority MUST lock a portal account after the number of consecutive failed sign-ins the Governance Profile sets.

</div>

### Registration {#ts-4-03-registration}

A registration carries what the trusted list will say about the body, what
the body asks to be, and the documents the Root Authority reads before it
decides. [The table of registration items][tbl-ts-4-03-registration-items]
gives each item.

[](){ #tbl-ts-4-03-registration-items }

<figure markdown="1" class="ekdn-table">

| Item | Presence | Value |
|---|---|---|
| Legal name | Present | The legal name of the body, in Indonesian and in English |
| Legal identifier | Present | `BKN:` and the institution code, or `NIB:` and the Nomor Induk Berusaha (NIB) |
| Operating name | Optional | The name the body operates under, where it differs from the legal name |
| Address | Present | The postal address, the e-mail address, and the website |
| Domain | Present | The domain the body's `did:webvh` will name |
| Roles | Present | The role service types the body asks for |
| Permissions | Present | Each permission the body asks for, as an `action` and a `resource` |
| Person answerable | Present | The name and e-mail address of the person answerable for the body |
| Documents | Present | Each document, of a kind [the table of document kinds][tbl-ts-4-03-document-kinds] gives |

</figure>

A body that holds neither a BKN institution code nor an NIB has no legal identifier. Its registration then lacks an item the table marks present, and Trust Authority does not open it ([REQ-TS-4-03-011][req-ts-4-03-011]).

[](){ #tbl-ts-4-03-document-kinds }

<figure markdown="1" class="ekdn-table">

| Kind | What it establishes | Presence |
|---|---|---|
| Legal body | That the body exists as a legal body | At least one |
| Person answerable | That the person named answers for the body | At least one |
| Sector license | The license of the regulator of the body's sector, as evidence | Where the sector is licensed |
| Conformance test | The result of the body's conformance test | At least one |
| Key storage evaluation | The certificate of an evaluation that a Key Attestation's `certification` will name, which an Assessment Body checks in its assessment, with the device models the Wallet Provider maps to it | Where the body asks for the Wallet Provider role and its Key Attestations will report a value above `iso_18045_enhanced-basic` |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-4-03-011 }**REQ-TS-4-03-011** Trust Authority MUST NOT open a registration that lacks an item [the table of registration items][tbl-ts-4-03-registration-items] marks present.
- [](){ #req-ts-4-03-012 }**REQ-TS-4-03-012** Trust Authority MUST take the legal name and the legal identifier in the forms [REQ-TS-5-01-018][req-ts-5-01-018] and [REQ-TS-5-01-019][req-ts-5-01-019] fix for the trusted list.
- [](){ #req-ts-4-03-013 }**REQ-TS-4-03-013** Trust Authority MUST take each role as a role service type of [the table of service types][tbl-ts-5-01-service-types].
- [](){ #req-ts-4-03-014 }**REQ-TS-4-03-014** Trust Authority MUST take each permission in the forms [What a permission names][ts-5-05-what-a-permission-names] fixes.
- [](){ #req-ts-4-03-015 }**REQ-TS-4-03-015** Trust Authority MUST NOT open a registration that lacks a document of a kind [the table of document kinds][tbl-ts-4-03-document-kinds] marks at least one.
- [](){ #req-ts-4-03-016 }**REQ-TS-4-03-016** Trust Authority MUST NOT allocate a registration identifier it has allocated before.
- [](){ #req-ts-4-03-017 }**REQ-TS-4-03-017** Trust Authority MUST record the decision the Root Authority takes on a registration, and the time it took it.
- [](){ #req-ts-4-03-018 }**REQ-TS-4-03-018** Trust Authority MUST show that decision in the portal to every account that acts for the registration.
- [](){ #req-ts-4-03-126 }**REQ-TS-4-03-126** Trust Authority MUST NOT open a registration that asks for the Wallet Provider role and lacks a document of the kind Key storage evaluation, where its Key Attestations will report a value above `iso_18045_enhanced-basic`.
- [](){ #req-ts-4-03-127 }**REQ-TS-4-03-127** Trust Authority MUST accept through the portal a further document of the kind Key storage evaluation from an account of a Wallet Provider's registration, and MUST hand it to an Assessment Body for assessment, so that the Root Authority decides on the report of the Assessment Body.

</div>

### The registration code {#ts-4-03-the-registration-code}

An approved registration has no identifier yet, so Trust Authority cannot
recognize the key that will sign its first entry. The registration code
ties the two together: the portal shows it once, and the first entry
carries a binding made with it, as External Account Binding does in
[RFC 8555][ref-rfc8555]. Knowing the registration identifier is not enough
to claim a registration; holding the code is.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-4-03-019 }**REQ-TS-4-03-019** When the Root Authority approves a registration, Trust Authority MUST generate a registration code of 256 bits drawn from a cryptographically secure random source.
- [](){ #req-ts-4-03-020 }**REQ-TS-4-03-020** Trust Authority MUST show the code, encoded in base64url without padding as [RFC 4648][ref-rfc4648] defines it, and the registration identifier, once, in the portal, to an account that acts for the registration.
- [](){ #req-ts-4-03-021 }**REQ-TS-4-03-021** Trust Authority MUST accept a code for the lifetime the Governance Profile sets, counted from when it generated the code.
- [](){ #req-ts-4-03-022 }**REQ-TS-4-03-022** Trust Authority MUST discard a code once it has bound a first entry, or once that lifetime has passed.
- [](){ #req-ts-4-03-023 }**REQ-TS-4-03-023** Trust Authority MUST NOT set a registration granted before its first entry has been witnessed.

</div>

A code that expires unused, or that an account lost before it was used, is
replaced by a new one on the Root Authority's word, and the registration
stays pending until a first entry is bound. The Root Authority's approval
takes effect as the grant of the accreditation at that moment, which is
when [Issuing and carrying an Accreditation
Credential](issuing-and-carrying-an-accreditation-credential.md)
issues the credential and [Publishing and reading the trusted
list](publishing-and-reading-the-trusted-list.md)
lists the registration as granted.

### Uses and further permissions {#ts-4-03-uses-and-further-permissions}

A Relying Party submits each use it wants to run, and collects the Use
Statement once the Root Authority approves it, as
[Registering, renewing, and withdrawing a use][ts-5-06-registering-renewing-and-withdrawing-a-use]
sets out. The submission names what the statement will carry, its purpose,
its legal basis and its attributes, in the forms
[What a use names][ts-5-06-what-a-use-names] fixes; Trust Authority
allocates the `use_id` when the use is approved, not when it is submitted.
An accredited registration also asks here for a permission it does not yet
hold, which the Root Authority grants one at a time through the approval
tier the permission falls in, as [authorization][authorization] sets out.

[](){ #tbl-ts-4-03-use-statuses }

<figure markdown="1" class="ekdn-table">

| Status | What it means |
|---|---|
| `pending` | Submitted, not yet decided |
| `approved` | Approved; the Use Statement in force can be collected |
| `refused` | Refused by the Root Authority |
| `withdrawn` | Withdrawn by the Root Authority, on its own decision or at the registration's request |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-4-03-024 }**REQ-TS-4-03-024** Trust Authority MUST take a use's purpose, legal basis and attributes in the forms [What a use names][ts-5-06-what-a-use-names] fixes.
- [](){ #req-ts-4-03-025 }**REQ-TS-4-03-025** Trust Authority MUST NOT accept a use from a registration that does not hold the Relying Party role.
- [](){ #req-ts-4-03-026 }**REQ-TS-4-03-026** Trust Authority MUST NOT accept a use from a registration that is suspended.
- [](){ #req-ts-4-03-027 }**REQ-TS-4-03-027** Trust Authority MUST NOT accept a request for a further permission from a registration that is suspended.
- [](){ #req-ts-4-03-028 }**REQ-TS-4-03-028** Trust Authority MUST show each use a registration submitted with its status, as [the table of use statuses][tbl-ts-4-03-use-statuses] gives it, and its `use_id` once approved.
- [](){ #req-ts-4-03-029 }**REQ-TS-4-03-029** Trust Authority MUST offer, for each approved use, the last Use Statement it issued for it, renewals included.
- [](){ #req-ts-4-03-030 }**REQ-TS-4-03-030** Trust Authority MUST let an account ask for the withdrawal of a use of its registration.
- [](){ #req-ts-4-03-031 }**REQ-TS-4-03-031** Trust Authority MUST hand each request to withdraw a use to the Root Authority.
- [](){ #req-ts-4-03-032 }**REQ-TS-4-03-032** Trust Authority MUST let an account of a granted registration ask for a further permission, in the forms [What a permission names][ts-5-05-what-a-permission-names] fixes.
- [](){ #req-ts-4-03-033 }**REQ-TS-4-03-033** Trust Authority MUST hand each request for a further permission to the Root Authority.
- [](){ #req-ts-4-03-034 }**REQ-TS-4-03-034** Verifier Core MUST NOT load a Use Statement it is given unless its signature verifies as [Signature][ts-5-06-signature] fixes and its `sub` is the registration's `did:webvh`.

</div>

### Incidents and post-mortems {#ts-4-03-incidents-and-post-mortems}

An entity that learns one of its keys is compromised or lost reports it
here, without waiting for a scheduled rotation, and files its post-mortem
here once the incident is over. The report revokes nothing on its own: the
Root Authority revokes the key through Trust Authority, within the hour
[entity key revocation][entity-key-revocation] counts from the moment the
compromise is confirmed, and the report is what sets that going. Because the
portal needs no key of the entity, the
update key is reported the same way as any other.
[The table of report items][tbl-ts-4-03-report-items] gives each item.

[](){ #tbl-ts-4-03-report-items }

<figure markdown="1" class="ekdn-table">

| Item | Presence | Value |
|---|---|---|
| Kind | Present | Compromised, lost, or post-mortem |
| Key | Present unless the kind is post-mortem | The public key, as a Multikey |
| Noticed | Present unless the kind is post-mortem | When the entity learned of it |
| Description | Optional | What the entity knows of it, for the Root Authority to read |
| Incident | Present when the kind is post-mortem | The incident the post-mortem closes |
| Document | Present when the kind is post-mortem | The post-mortem |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-4-03-035 }**REQ-TS-4-03-035** Trust Authority MUST accept a report from a registration whatever its status.
- [](){ #req-ts-4-03-036 }**REQ-TS-4-03-036** Trust Authority MUST NOT accept a report naming a key the Public Key Registry does not record for the registration.
- [](){ #req-ts-4-03-037 }**REQ-TS-4-03-037** Trust Authority MUST hand each report it accepts to the Root Authority as an incident, through its Incident Service Component.
- [](){ #req-ts-4-03-038 }**REQ-TS-4-03-038** Trust Authority MUST show the account that reported an incident the identifier it allocated to it.
- [](){ #req-ts-4-03-039 }**REQ-TS-4-03-039** Trust Authority MUST NOT accept a post-mortem naming an incident it does not hold for the registration.
- [](){ #req-ts-4-03-040 }**REQ-TS-4-03-040** Trust Authority MUST write each post-mortem it accepts into the Transparency Log.

</div>

An incident the Root Authority opened itself has an identifier the Root
Authority gives the body with its notice, and the post-mortem names that
one.

### Withdrawing the registration {#ts-4-03-withdrawing-the-registration}

A body may leave. Its staff ask in the portal; the Root Authority decides
and withdraws the accreditation, and the trusted list and the Accreditation
Credential status list carry the withdrawal as
[Publishing and reading the trusted list](publishing-and-reading-the-trusted-list.md)
and [Issuing and carrying an Accreditation
Credential](issuing-and-carrying-an-accreditation-credential.md)
fix. Withdrawal revokes no key: what the body signed while accredited still
verifies, because its log stays resolvable and its entry stays on the list
at status `withdrawn`.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-4-03-041 }**REQ-TS-4-03-041** Trust Authority MUST let an account of a granted or suspended registration ask for the registration to be withdrawn.
- [](){ #req-ts-4-03-042 }**REQ-TS-4-03-042** Trust Authority MUST hand each request to withdraw a registration to the Root Authority.
- [](){ #req-ts-4-03-043 }**REQ-TS-4-03-043** Trust Authority MUST NOT record a key of a registration as revoked because its accreditation was withdrawn.

</div>

### The record and the audit trail {#ts-4-03-the-record-and-the-audit-trail}

A registration's accounts read its record, the certificates in force, and
its history in the portal. The record is where an entity collects a later
copy of its Accreditation Credential.
[The table of events][tbl-ts-4-03-events] gives every event the audit trail
carries.

The audit trail is the registration's share of the Transparency Log, the
append-only record Trust Authority keeps of every entity event. The portal
is the only place outside Trust Authority where the log is read, and each
registration reads its own events there and no other's. A party that checks
an entity from outside reads the entity's `did:webvh` log, which DID Service
witnessed, and the trusted list, never the Transparency Log.

[](){ #tbl-ts-4-03-events }

<figure markdown="1" class="ekdn-table">

| Event | What happened |
|---|---|
| Registered | The registration was opened |
| Approved, rejected | The Root Authority decided on the registration |
| Granted | The first entry was witnessed and the accreditation took effect |
| Suspended, restored, withdrawn | The Root Authority changed the registration's status |
| Withdrawal requested | An account asked for the registration to be withdrawn |
| Key registered, key revoked | A key was recorded in the Public Key Registry, or the Root Authority revoked it |
| Certificate issued, certificate revoked | A certificate was issued, or placed on a revocation list |
| Accreditation Credential issued | An Accreditation Credential was issued |
| Permission requested, granted, refused, withdrawn | A permission changed |
| Use submitted, approved, refused, withdrawn, withdrawal requested | A use changed |
| Incident reported, post-mortem filed | A report was received |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-4-03-044 }**REQ-TS-4-03-044** Trust Authority MUST show each account the registration's identifier, its `did:webvh`, its status, its roles, and every permission in force.
- [](){ #req-ts-4-03-045 }**REQ-TS-4-03-045** Trust Authority MUST offer, while the registration is granted or suspended, the Accreditation Credential [REQ-TS-5-07-077][req-ts-5-07-077] treats as in force.
- [](){ #req-ts-4-03-046 }**REQ-TS-4-03-046** Trust Authority MUST offer every certificate it issued to the registration that has neither expired nor been revoked.
- [](){ #req-ts-4-03-047 }**REQ-TS-4-03-047** Trust Authority MUST show every event of the registration, in the order it happened, with its time, the key, certificate, use, permission or incident it concerns, and the account that caused it where one did.
- [](){ #req-ts-4-03-048 }**REQ-TS-4-03-048** Trust Authority MUST NOT show an event of another registration.
- [](){ #req-ts-4-03-120 }**REQ-TS-4-03-120** Trust Authority MUST write every event [the table of events][tbl-ts-4-03-events] lists into the Transparency Log when it happens.
- [](){ #req-ts-4-03-121 }**REQ-TS-4-03-121** Trust Authority MUST NOT change or remove an entry of the Transparency Log.

</div>

## The entity endpoint {#ts-4-03-the-entity-endpoint}

The entity endpoint takes two operations, and both come from a Key Manager.
[The table of operations][tbl-ts-4-03-operations] gives them.

### The HTTPS binding {#ts-4-03-the-https-binding}

The endpoint is public, because the Modules that call it run at each
entity, outside Trust Infrastructure, as
[network zones and placement][network-zones-and-placement] sets out.

[](){ #tbl-ts-4-03-operations }

<figure markdown="1" class="ekdn-table">

| Operation | Request | Answer | Clause |
|---|---|---|---|
| `GET <endpoint>/nonce` | None | `204` | [Nonce][ts-4-03-nonce] |
| `POST <endpoint>/entities/me/keys` | A signed submission | `200` | [Registering keys][ts-4-03-registering-keys] |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-4-03-049 }**REQ-TS-4-03-049** Trust Authority MUST serve the entity endpoint over HTTP with TLS only.
- [](){ #req-ts-4-03-050 }**REQ-TS-4-03-050** Trust Authority MUST serve the two operations [the table of operations][tbl-ts-4-03-operations] lists, at the address the Governance Profile publishes as `<endpoint>`.
- [](){ #req-ts-4-03-051 }**REQ-TS-4-03-051** Trust Authority MUST NOT serve any other operation at the entity endpoint.
- [](){ #req-ts-4-03-052 }**REQ-TS-4-03-052** Trust Authority MUST carry a `Cache-Control: no-store` header on every answer of the entity endpoint.
- [](){ #req-ts-4-03-053 }**REQ-TS-4-03-053** Trust Authority MUST limit the rate of requests from one network address at the entity endpoint to the limit the Governance Profile sets.

</div>

### Nonce {#ts-4-03-nonce}

A nonce is what makes a signed request impossible to replay. Trust
Authority issues one at its nonce operation and a fresh one on every
answer, in the `Replay-Nonce` header [RFC 8555][ref-rfc8555] defines, so
that a Module sending several requests asks for a nonce only once.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-4-03-054 }**REQ-TS-4-03-054** Trust Authority MUST answer `GET <endpoint>/nonce` with `204` and a `Replay-Nonce` header carrying a nonce.
- [](){ #req-ts-4-03-055 }**REQ-TS-4-03-055** Trust Authority MUST carry a `Replay-Nonce` header with a fresh nonce on every answer of the entity endpoint, a problem document included.
- [](){ #req-ts-4-03-056 }**REQ-TS-4-03-056** A nonce MUST carry at least 128 bits drawn from a cryptographically secure random source, encoded in base64url without padding.
- [](){ #req-ts-4-03-057 }**REQ-TS-4-03-057** Trust Authority MUST accept a nonce for the lifetime the Governance Profile sets, counted from when it issued the nonce.
- [](){ #req-ts-4-03-058 }**REQ-TS-4-03-058** Trust Authority MUST accept each nonce in one request only.
- [](){ #req-ts-4-03-059 }**REQ-TS-4-03-059** Trust Authority MUST refuse with `bad-nonce` a request whose nonce it did not issue, has already accepted, or issued longer ago than that lifetime.
- [](){ #req-ts-4-03-060 }**REQ-TS-4-03-060** The calling Module MUST send each nonce in one request only.

</div>

### The signed request {#ts-4-03-the-signed-request}

A submission is a POST whose body is one JWS in the compact serialization
of [RFC 7515][ref-rfc7515], with media type `application/jose`, and whose
payload is a JSON object. [RFC 8555][ref-rfc8555] sends the flattened JSON
serialization; this endpoint takes the compact one, the form every other
JWS in the ecosystem takes.
[The table of protected header members][tbl-ts-4-03-protected-header] gives
each member of the protected header.

[](){ #tbl-ts-4-03-protected-header }

<figure markdown="1" class="ekdn-table">

| Member | Type | Presence | Value |
|---|---|---|---|
| `alg` | string | Present | `EdDSA` |
| `kid` | string | Present | The update key, as `did:key:<multikey>#<multikey>` |
| `nonce` | string | Present | A nonce Trust Authority issued |
| `url` | string | Present | The full address the request is sent to, `https://` included |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-4-03-061 }**REQ-TS-4-03-061** The calling Module MUST send a submission as a JWS in compact serialization whose payload is a JSON object.
- [](){ #req-ts-4-03-062 }**REQ-TS-4-03-062** The calling Module MUST send a submission with the header `Content-Type: application/jose`.
- [](){ #req-ts-4-03-063 }**REQ-TS-4-03-063** The protected header MUST carry the four members [the table of protected header members][tbl-ts-4-03-protected-header] gives, and no other.
- [](){ #req-ts-4-03-064 }**REQ-TS-4-03-064** The calling Module MUST sign a submission with the update key that the latest log entry Trust Authority witnessed for the registration carries in `updateKeys`, except for a first entry, which [REQ-TS-4-03-065][req-ts-4-03-065] covers, and where [After a revoked update key][ts-4-03-after-a-revoked-update-key] applies.
- [](){ #req-ts-4-03-065 }**REQ-TS-4-03-065** The calling Module MUST sign the submission that carries a registration's first log entry with the update key that entry carries.
- [](){ #req-ts-4-03-066 }**REQ-TS-4-03-066** Trust Authority MUST refuse with `malformed-request` a request whose protected header carries a member [the table of protected header members][tbl-ts-4-03-protected-header] does not give, or lacks one it gives.
- [](){ #req-ts-4-03-067 }**REQ-TS-4-03-067** Trust Authority MUST find the registration a request comes from by the key `kid` names, among the update keys the latest witnessed entry of each registration carries.
- [](){ #req-ts-4-03-068 }**REQ-TS-4-03-068** Trust Authority MUST refuse with `unauthorized` a request whose `kid` names no such key, unless the request carries a first log entry as [The first entry][ts-4-03-the-first-entry] fixes, or the next entry after a revoked update key as [After a revoked update key][ts-4-03-after-a-revoked-update-key] fixes.
- [](){ #req-ts-4-03-069 }**REQ-TS-4-03-069** Trust Authority MUST refuse with `unauthorized` a request whose signature does not verify under the key `kid` names.
- [](){ #req-ts-4-03-070 }**REQ-TS-4-03-070** Trust Authority MUST refuse with `unauthorized` a request whose `url` differs from the address it was received at.
- [](){ #req-ts-4-03-071 }**REQ-TS-4-03-071** Trust Authority MUST refuse with `unauthorized` a request signed with a key the Public Key Registry records as revoked.
- [](){ #req-ts-4-03-072 }**REQ-TS-4-03-072** Trust Authority MUST refuse with `registration-withdrawn` every request from a registration whose accreditation is withdrawn.

</div>

A withdrawn registration's log stays resolvable, so that what it signed
while accredited still verifies, and its update key may still sign; the
endpoint refuses it all the same. A suspended registration may still
rotate its keys; what it may not do is ask for a certificate.

### Registering keys {#ts-4-03-registering-keys}

`POST <endpoint>/entities/me/keys` is the one operation through which a key
enters the ecosystem. One submission carries a log entry, a certificate
signing request, or both, and everything Trust Authority checks about them,
as [the table of submission members][tbl-ts-4-03-submission-members] gives.

1. The calling Module signs the submission, as [The signed
request][ts-4-03-the-signed-request]
   fixes.
2. Trust Authority checks the signature, the nonce, and, for a first
   entry, the binding, or, for a certificate request without an entry, the
   countersignature.
3. It checks that the entry belongs to the registration.
4. It checks the storage evidence of each new transaction key against the
   grade the registration's permissions demand.
5. It checks each certificate signing request against the profile of the
   certificate it asks for, and that it can reach every key the answer
   will be signed with.
6. It hands the entry to DID Service, with the proofs of possession and the
   request's nonce, and receives the witness proof or a refusal.
7. It issues each certificate and records each key in the Public Key
   Registry and the event in the Transparency Log.
8. For a first entry, it sets the registration granted and issues the
   Accreditation Credential.
9. It records each key against the registration's entry in Trust Registry,
   and answers.
10. Trust Registry publishes a new trusted list where the entry changed.

[](){ #tbl-ts-4-03-submission-members }

<figure markdown="1" class="ekdn-table">

| Member | Type | Presence | Value |
|---|---|---|---|
| `logEntry` | object | Present when the submission carries a log entry | The entry, as [The log][ts-5-02-the-log] fixes it |
| `proofOfPossession` | array of string | Present when `logEntry` publishes a key for the first time | One proof for each such key, as [REQ-TS-4-01-032][req-ts-4-01-032] and [REQ-TS-4-01-033][req-ts-4-01-033] fix it |
| `keyStorage` | array of object | Present when the submission introduces a transaction key | One item for each such key, as [the table of storage members][tbl-ts-4-03-storage-members] gives |
| `certificationRequests` | array of object | Present when the submission asks for a certificate | One item for each certificate, as [the table of certification request members][tbl-ts-4-03-certification-request-members] gives |
| `countersignature` | string | Present when the submission carries `certificationRequests` and no `logEntry` | A proof of possession over the request's nonce by a transaction key the registration already holds |
| `registrationBinding` | string | Present on the first entry only | The binding [The first entry][ts-4-03-the-first-entry] fixes |

</figure>

A transaction key is any key but the update key: one the entry publishes
for the first time, or the key of a certificate signing request that the
Public Key Registry does not hold. The update key carries no storage item,
because [the update key][the-update-key] may stay in the software keystore
whatever driver holds the others.

[](){ #tbl-ts-4-03-storage-members }

<figure markdown="1" class="ekdn-table">

| Member | Type | Presence | Value |
|---|---|---|---|
| `key` | string | Present | The public key, as a Multikey |
| `storage` | string | Present | The driver that holds the key: `software`, `cloudkms`, or `hsm` |
| `evidence` | object | Present unless `storage` is `software` | What the storage is taken on, as [the table of evidence members][tbl-ts-4-03-evidence-members] gives |

</figure>

The evidence is what [two assurance levels][issuer-assurance] takes the
storage on: a statement the device that holds the key signs, under a root
its manufacturer or provider placed in it, or, where the device gives none
this specification reads, the report of an Assessment Body covering the
key ceremony, which reaches Trust Authority outside this interface.
Devices sign that statement in several forms, and only some as a
certificate over the key, so `format` names the form.
[The table of evidence members][tbl-ts-4-03-evidence-members] gives the
two forms this version reads. A key in the software keystore carries no
evidence, as the Relying Party of the Verifier Issuing CA example below
declared its Request Object key:

``` { .json title="A storage item for a key in the software keystore" data-format="JSON" }
{
  "key": "zDnaeZ5itwE2JdeopSYt95LLYAFMCgRneASH35Yc7bQHAocpB",
  "storage": "software"
}
```

[](){ #tbl-ts-4-03-evidence-members }

<figure markdown="1" class="ekdn-table">

| Member | Type | Presence | Value |
|---|---|---|---|
| `format` | string | Present | `x509-chain`, the device's certificate over the key, or `assessment-report`, an Assessment Body report |
| `certs` | array of string | Present when `format` is `x509-chain` | The certificate the device issued over the key, then each certificate up to and excluding the root, each DER in base64url without padding |
| `report` | string | Present when `format` is `assessment-report` | The identifier of the report Trust Authority holds |

</figure>

[](){ #tbl-ts-4-03-certification-request-members }

<figure markdown="1" class="ekdn-table">

| Member | Type | Presence | Value |
|---|---|---|---|
| `purpose` | string | Present | `issuance-cose` for a Document Signer Certificate, `status-list` for a status list signer certificate, `verifier-issuing-ca` for a Verifier Issuing CA certificate |
| `csr` | string | Present | The request under [RFC 2986][ref-rfc2986], DER in base64url without padding |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-4-03-073 }**REQ-TS-4-03-073** A submission MUST carry `logEntry`, `certificationRequests`, or both.
- [](){ #req-ts-4-03-074 }**REQ-TS-4-03-074** A submission MUST carry every other member [the table of submission members][tbl-ts-4-03-submission-members] marks present for what it carries.
- [](){ #req-ts-4-03-075 }**REQ-TS-4-03-075** Trust Authority MUST refuse with `did-mismatch` a `logEntry` whose `state.id` is not the registration's `did:webvh`, or, for a first entry, whose domain is not the domain of the registration.
- [](){ #req-ts-4-03-076 }**REQ-TS-4-03-076** The calling Module MUST sign each proof of possession over the nonce of the request that carries it.
- [](){ #req-ts-4-03-077 }**REQ-TS-4-03-077** The submission MUST carry one `keyStorage` item for each transaction key it introduces.
- [](){ #req-ts-4-03-078 }**REQ-TS-4-03-078** The submission MUST NOT carry a `keyStorage` item for the update key.
- [](){ #req-ts-4-03-079 }**REQ-TS-4-03-079** A `keyStorage` item MUST carry `evidence` unless its `storage` is `software`.
- [](){ #req-ts-4-03-080 }**REQ-TS-4-03-080** `countersignature` MUST be a JWS in compact serialization whose protected header carries `typ` `vnd.id.idctf.key-pop+jwt`, `alg` the algorithm of the signing key, and `kid` the identifier of a key the registration's latest witnessed DID Document lists under `assertionMethod`, and whose payload carries `aud`, Trust Authority's identifier, `nonce`, the request's nonce, and `iat`.
- [](){ #req-ts-4-03-081 }**REQ-TS-4-03-081** Trust Authority MUST refuse with `malformed-request` a submission that breaks [REQ-TS-4-03-061][req-ts-4-03-061], [REQ-TS-4-03-073][req-ts-4-03-073], [REQ-TS-4-03-074][req-ts-4-03-074], [REQ-TS-4-03-077][req-ts-4-03-077], [REQ-TS-4-03-078][req-ts-4-03-078], [REQ-TS-4-03-079][req-ts-4-03-079], or [REQ-TS-4-03-080][req-ts-4-03-080].
- [](){ #req-ts-4-03-082 }**REQ-TS-4-03-082** Trust Authority MUST refuse with `unauthorized` a submission whose `countersignature` does not verify under the key its `kid` names, or names a key the Public Key Registry does not record Active for the registration.
- [](){ #req-ts-4-03-083 }**REQ-TS-4-03-083** Trust Authority MUST refuse with `key-storage-rejected` an `x509-chain` evidence whose `certs` do not chain to a root the Governance Profile accepts for the `storage` the item names.
- [](){ #req-ts-4-03-084 }**REQ-TS-4-03-084** Trust Authority MUST refuse with `key-storage-rejected` an `x509-chain` evidence whose first certificate certifies a key other than the one `key` names.
- [](){ #req-ts-4-03-085 }**REQ-TS-4-03-085** Trust Authority MUST refuse with `key-storage-rejected` an `assessment-report` evidence that names no report it holds on the ceremony of that key.
- [](){ #req-ts-4-03-086 }**REQ-TS-4-03-086** Trust Authority MUST refuse with `key-storage-rejected` a key whose `storage` gives a lower `issuer_assurance`, through the mapping the Governance Profile sets, than a permission of the registration demands.
- [](){ #req-ts-4-03-087 }**REQ-TS-4-03-087** Trust Authority MUST refuse with `key-storage-rejected` a `verifier-issuing-ca` request over a key whose `storage` is `software`.
- [](){ #req-ts-4-03-088 }**REQ-TS-4-03-088** Trust Authority MUST refuse with `role-not-held` a certificate signing request whose `purpose` the registration's role and permissions do not admit, as [REQ-TS-5-04-047][req-ts-5-04-047] admits a Verifier Issuing CA.
- [](){ #req-ts-4-03-089 }**REQ-TS-4-03-089** Trust Authority MUST refuse with `certification-request-rejected` a certificate signing request that fails a check of [Issuing and validating the X.509 certificates and the VICAL](issuing-and-validating-the-x509-certificates-and-the-vical.md) for the certificate it asks for.
- [](){ #req-ts-4-03-090 }**REQ-TS-4-03-090** Trust Authority MUST refuse with `certification-request-rejected` a certificate signing request over a key any log entry of the registration lists in `updateKeys`.
- [](){ #req-ts-4-03-091 }**REQ-TS-4-03-091** Trust Authority MUST refuse with `registration-suspended` a submission carrying `certificationRequests` from a registration that is suspended.
- [](){ #req-ts-4-03-092 }**REQ-TS-4-03-092** Trust Authority MUST complete every check this specification sets on a submission that does not depend on the witness proof before it hands the entry to DID Service.
- [](){ #req-ts-4-03-093 }**REQ-TS-4-03-093** Trust Authority MUST confirm that it can reach every key the answer will be signed with before it hands the entry to DID Service.
- [](){ #req-ts-4-03-094 }**REQ-TS-4-03-094** Trust Authority MUST hand DID Service the entry and the proofs of possession unchanged, with the request's nonce as `nonce`, as [The hand-off to the Publisher endpoint][ts-4-01-the-hand-off-to-the-publisher-endpoint] fixes.
- [](){ #req-ts-4-03-095 }**REQ-TS-4-03-095** Trust Authority MUST relay a refusal DID Service answers with `422` as the problem type of the same name as its `reason`.
- [](){ #req-ts-4-03-096 }**REQ-TS-4-03-096** Trust Authority MUST NOT issue a certificate for a submission whose entry DID Service refused.
- [](){ #req-ts-4-03-097 }**REQ-TS-4-03-097** Trust Authority MUST record each key it accepts in the Public Key Registry, with its purpose, its storage and evidence, its validity, and the status Active, before it answers.
- [](){ #req-ts-4-03-098 }**REQ-TS-4-03-098** Trust Authority MUST write each key it accepts and each certificate it issues into the Transparency Log.
- [](){ #req-ts-4-03-099 }**REQ-TS-4-03-099** Trust Authority MUST answer a submission it accepts with `200`, media type `application/json`, and an object carrying every member [the table of answer members][tbl-ts-4-03-answer-members] marks present for what the submission carried.

</div>

[](){ #tbl-ts-4-03-answer-members }

<figure markdown="1" class="ekdn-table">

| Member | Type | Presence | Value |
|---|---|---|---|
| `witness` | object | Present when the submission carried `logEntry` | The witness proof DID Service returned, as [The witness proof as returned][ts-4-01-the-witness-proof-as-returned] shows it |
| `certificates` | array of object | Present when the submission carried `certificationRequests` | One item per request, in the same order, each carrying `purpose` and `certificate`, the certificate DER in base64url without padding |
| `accreditationCredential` | string | Present when the submission carried a first entry | The Accreditation Credential issued at that moment |

</figure>

The checks run before the hand-off, and the keys the answer needs are
reached before it too, so that an entry is witnessed only when everything
its answer carries can be signed. Once it holds the answer, the calling
Module publishes the entry as [REQ-TS-5-02-034][req-ts-5-02-034] and its
neighbors require, and when the witness cannot be reached it keeps the
signed entry and submits it again, as [REQ-TS-5-02-041][req-ts-5-02-041]
requires.

A submission that carries a certificate signing request and no entry
renews a certificate over a key the registration holds, or certifies a key
that is not in the log. Its countersignature is what keeps the update key
from being enough on its own: a key that signs nothing a wallet or a
verifier sees cannot get a certificate over a key of its holder's choosing
without a transaction key that the registration already holds, as
[the update key][the-update-key] promises. Below, the issuer of the example
above asks for a Document Signer Certificate over a new `issuance-cose` key
held in its HSM, and for a status list signer certificate over the
`status-list` key its first entry published, countersigned with its
`issuance-jose` key. The first request is the one
[Issuing and validating the X.509 certificates and the VICAL](issuing-and-validating-the-x509-certificates-and-the-vical.md)
shows, and the two certificates in the answer are the ones it shows.

``` { .http title="POST /entities/me/keys, a certificate request" data-format="HTTP" }
POST /entities/me/keys HTTP/1.1
Host: entities.trust.go.id
Content-Type: application/jose

eyJhbGciOiJFZERTQSIsImtpZCI6ImRpZDprZXk6ejZNa2hEWFp0QkhMVUtLMjdHMWQ1czVDTjRKNmVrSndCaFJyZm1rQktNS0Q1RFZYI3o2TWtoRFhadEJITFVLSzI3RzFkNXM1Q040SjZla0p3QmhScmZta0JLTUtENURWWCIsIm5vbmNlIjoibDYzcVVlWFBUUXVGQjhnSGE5VFBOOGgwNjhxUW9fd0UiLCJ1cmwiOiJodHRwczovL2VudGl0aWVzLnRydXN0LmdvLmlkL2VudGl0aWVzL21lL2tleXMifQ.eyJjb3VudGVyc2lnbmF0dXJlIjoiZXlKMGVYQWlPaUoyYm1RdWFXUXVhV1JqZEdZdWEyVjVMWEJ2Y0N0cWQzUWlMQ0poYkdjaU9pSkZVekkxTmlJc0ltdHBaQ0k2SW1ScFpEcDNaV0oyYURwUmJXTkZWbFF5YVVwVGNuTnpOV2huZDJsTlJuTk5WWGhMYTFKdmVtZEdSalExT0ZKaloyZFVORTFHTWt3ME9tUjFhMk5oY0dsc0xtZHZMbWxrSTJsemMzVmhibU5sTFdwdmMyVXRNU0o5LmV5SmhkV1FpT2lKa2FXUTZkMlZpZG1nNlVXMWFhbmt4ZERsdlJtbGhSbXBvV0RKbE16aDFUWFZTTjIxbmRHUk1ha2hRVFVkbWFrVm1kbkp6YldGcGNUcDBjblZ6ZEM1bmJ5NXBaQ0lzSW01dmJtTmxJam9pYkRZemNWVmxXRkJVVVhWR1FqaG5TR0U1VkZCT09HZ3dOamh4VVc5ZmQwVWlMQ0pwWVhRaU9qRTNPRGd5TWpBMU1EQjkuQmwxaW5TVWY3dFR5TXdZRjh6NGpOSk02ZW9xNG5iNjNVakxMM0szcUliUDNONGJXTVJDM0h6MzF0b2J1RTlJTjQ1MVFvdVJydDZFbkV2R2xXTHZEU1EiLCJrZXlTdG9yYWdlIjpbeyJrZXkiOiJ6RG5hZWVYc1VKMldZOVNlVFNmOWM2SGUzU2NRSGVUMTg0Y1U0Z1NLWmM4UXFZbkRZIiwic3RvcmFnZSI6ImhzbSIsImV2aWRlbmNlIjp7ImZvcm1hdCI6Ing1MDktY2hhaW4iLCJjZXJ0cyI6WyJNSUlCNVRDQ0FZdWdBd0lCQWdJQlZ6QUtCZ2dxaGtqT1BRUURBakJSTVFzd0NRWURWUVFHRXdKSlJERWpNQ0VHQTFVRUNnd2FVRlFnUTI5dWRHOW9JRkJsY21GdVoydGhkQ0JMY21sd2RHOHhIVEFiQmdOVkJBTU1GRU52Ym5SdmFDQklVMDBnTjFFMFN5MHdNakU1TUI0WERUSTJNRGd5T0RBd01EQXdNRm9YRFRRMU1EWXdNVEF3TURBd01Gb3dSVEVMTUFrR0ExVUVCaE1DU1VReEl6QWhCZ05WQkFvTUdsQlVJRU52Ym5SdmFDQlFaWEpoYm1kcllYUWdTM0pwY0hSdk1SRXdEd1lEVlFRRERBaExaWGtnTURBMU56QlpNQk1HQnlxR1NNNDlBZ0VHQ0NxR1NNNDlBd0VIQTBJQUJOR0d6R05uTjlOQmlDVjY0ekIwNm9zZlFLT09NU2RyNmI5VTZCb21ORnlqQk1mWXJmQ0M2N2V3VUFRWGVPd000WjhVUGtCMkdYd0Nhak1mVXktbmcyU2pZREJlTUF3R0ExVWRFd0VCX3dRQ01BQXdEZ1lEVlIwUEFRSF9CQVFEQWdlQU1CMEdBMVVkRGdRV0JCVHVyZEItYVY1cWFKVUJpUExQa3ViRlpzbW8zVEFmQmdOVkhTTUVHREFXZ0JUYjc0VmpjSXZDaDFqQVVubEZXM2d2UWRybnBUQUtCZ2dxaGtqT1BRUURBZ05JQURCRkFpRUFnWVZNV2VDN1gyX0NTakFmTHEzUHM5RHlRc3B0UnVIbE9id3Y2dVpEa2owQ0lBWUdXT3o1N3N6ZnRpYmt6dU9SSmFONkIyY3lObVlVQVNhQ3ZSdHhYSjZSIiwiTUlJQi1qQ0NBWi1nQXdJQkFnSUZCTEhYQWhrd0NnWUlLb1pJemowRUF3SXdUekVMTUFrR0ExVUVCaE1DU1VReEl6QWhCZ05WQkFvTUdsQlVJRU52Ym5SdmFDQlFaWEpoYm1kcllYUWdTM0pwY0hSdk1Sc3dHUVlEVlFRRERCSkRiMjUwYjJnZ1NGTk5JRkp2YjNRZ1EwRXdIaGNOTWpVd05qQXhNREF3TURBd1doY05ORFV3TmpBeE1EQXdNREF3V2pCUk1Rc3dDUVlEVlFRR0V3SkpSREVqTUNFR0ExVUVDZ3dhVUZRZ1EyOXVkRzlvSUZCbGNtRnVaMnRoZENCTGNtbHdkRzh4SFRBYkJnTlZCQU1NRkVOdmJuUnZhQ0JJVTAwZ04xRTBTeTB3TWpFNU1Ga3dFd1lIS29aSXpqMENBUVlJS29aSXpqMERBUWNEUWdBRW4yZl9lTG85bWkzZUcyUDd6UktIMGd0Sm1uQndTdmF2c1g3RmpPUWw4Qm9hMWpzSllzd2d2QUFpclhqeTBlT056Skdrb0o1dThUWGw0TWllbmJfZWdhTm1NR1F3RWdZRFZSMFRBUUhfQkFnd0JnRUJfd0lCQURBT0JnTlZIUThCQWY4RUJBTUNBZ1F3SFFZRFZSME9CQllFRk52dmhXTndpOEtIV01CU2VVVmJlQzlCMnVlbE1COEdBMVVkSXdRWU1CYUFGS2M3RmlGVXprOS03NEVIN0Z2c1JMTEdpdWhoTUFvR0NDcUdTTTQ5QkFNQ0Ewa0FNRVlDSVFEUGNLTF9PdDI2aENBOXdJR2JyOFhPNzZCVkgxTUdCM2NXamp2eHhJVktqQUloQU9BbE1sOTZORUoyOEpXX0NmUWI1Y29IZXM2Q0E3dzNpYkR3cVZKV3BzMWoiXX19XSwiY2VydGlmaWNhdGlvblJlcXVlc3RzIjpbeyJwdXJwb3NlIjoiaXNzdWFuY2UtY29zZSIsImNzciI6Ik1JSUJOekNCM2dJQkFEQjhNUXN3Q1FZRFZRUUdFd0pKUkRFLU1Ed0dBMVVFQ2d3MVJHbHlaV3QwYjNKaGRDQktaVzVrWlhKaGJDQkxaWEJsYm1SMVpIVnJZVzRnWkdGdUlGQmxibU5oZEdGMFlXNGdVMmx3YVd3eExUQXJCZ05WQkFNTUpFUjFhMk5oY0dsc0lHMWtiMk1nUkc5amRXMWxiblFnVTJsbmJtVnlJREl3TWpZdFFUQlpNQk1HQnlxR1NNNDlBZ0VHQ0NxR1NNNDlBd0VIQTBJQUJOR0d6R05uTjlOQmlDVjY0ekIwNm9zZlFLT09NU2RyNmI5VTZCb21ORnlqQk1mWXJmQ0M2N2V3VUFRWGVPd000WjhVUGtCMkdYd0Nhak1mVXktbmcyU2dBREFLQmdncWhrak9QUVFEQWdOSUFEQkZBaUVBdWs4Qy1GNkxvOW02WjdFNVc1OWoyWmNiMzJRY0tfZUE0ZHV6YXNLNU11c0NJQU5YYXZKVXVYSmo2c2wxT3FHa0pPOVFVS3pOeDRLcU9ySnM3c1RMMnpMNCJ9LHsicHVycG9zZSI6InN0YXR1cy1saXN0IiwiY3NyIjoiTUlJQk5qQ0IzQUlCQURCNk1Rc3dDUVlEVlFRR0V3SkpSREUtTUR3R0ExVUVDZ3cxUkdseVpXdDBiM0poZENCS1pXNWtaWEpoYkNCTFpYQmxibVIxWkhWcllXNGdaR0Z1SUZCbGJtTmhkR0YwWVc0Z1UybHdhV3d4S3pBcEJnTlZCQU1NSWtSMWEyTmhjR2xzSUZOMFlYUjFjeUJNYVhOMElGTnBaMjVsY2lBeU1ESTJMVUV3V1RBVEJnY3Foa2pPUFFJQkJnZ3Foa2pPUFFNQkJ3TkNBQVNaampfNjhUdkpMdjZ0ZUVuMHpZa2o4S3lsMzhGWTNNcTBSZHI2dEd6c21sejM3ZmI4YWxSaWM3MXdxOEk1ZDJINE5WM0JVOFdHM2Iydm15a1hYRjJzb0FBd0NnWUlLb1pJemowRUF3SURTUUF3UmdJaEFMSHlfZ1BWUUhLMEtRMkpZeUcxYy1QdWE2WnFvTTcwNklJdHFhd0g3d0JhQWlFQXROekgzSXk5Y0tDdndWRWNyRXZBMUNGT2U3VVZDbjU5Z3hYS3hkNXpzcFUifV19.p3k5PfDqDGFAKjTfNNqUbePfV3wwrgs5k7wk5W-nMowmdX5p3KPnxnYwcR7rv7qE7cgw1uSO4C-bUQJjIET_BA
```

``` { .json title="The certificate request, decoded" data-format="JSON" }
{
  "protected": {
    "alg": "EdDSA",
    "kid": "did:key:z6MkhDXZtBHLUKK27G1d5s5CN4J6ekJwBhRrfmkBKMKD5DVX#z6MkhDXZtBHLUKK27G1d5s5CN4J6ekJwBhRrfmkBKMKD5DVX",
    "nonce": "l63qUeXPTQuFB8gHa9TPN8h068qQo_wE",
    "url": "https://entities.trust.go.id/entities/me/keys"
  },
  "payload": {
    "countersignature": "eyJ0eXAiOiJ2bmQuaWQuaWRjdGYua2V5LXBvcCtqd3QiLCJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDp3ZWJ2aDpRbWNFVlQyaUpTcnNzNWhnd2lNRnNNVXhLa1JvemdGRjQ1OFJjZ2dUNE1GMkw0OmR1a2NhcGlsLmdvLmlkI2lzc3VhbmNlLWpvc2UtMSJ9.eyJhdWQiOiJkaWQ6d2Vidmg6UW1aankxdDlvRmlhRmpoWDJlMzh1TXVSN21ndGRMakhQTUdmakVmdnJzbWFpcTp0cnVzdC5nby5pZCIsIm5vbmNlIjoibDYzcVVlWFBUUXVGQjhnSGE5VFBOOGgwNjhxUW9fd0UiLCJpYXQiOjE3ODgyMjA1MDB9.Bl1inSUf7tTyMwYF8z4jNJM6eoq4nb63UjLL3K3qIbP3N4bWMRC3Hz31tobuE9IN451QouRrt6EnEvGlWLvDSQ",
    "keyStorage": [
      {
        "key": "zDnaeeXsUJ2WY9SeTSf9c6He3ScQHeT184cU4gSKZc8QqYnDY",
        "storage": "hsm",
        "evidence": {
          "format": "x509-chain",
          "certs": [
            "MIIB5TCCAYugAwIBAgIBVzAKBggqhkjOPQQDAjBRMQswCQYDVQQGEwJJRDEjMCEGA1UECgwaUFQgQ29udG9oIFBlcmFuZ2thdCBLcmlwdG8xHTAbBgNVBAMMFENvbnRvaCBIU00gN1E0Sy0wMjE5MB4XDTI2MDgyODAwMDAwMFoXDTQ1MDYwMTAwMDAwMFowRTELMAkGA1UEBhMCSUQxIzAhBgNVBAoMGlBUIENvbnRvaCBQZXJhbmdrYXQgS3JpcHRvMREwDwYDVQQDDAhLZXkgMDA1NzBZMBMGByqGSM49AgEGCCqGSM49AwEHA0IABNGGzGNnN9NBiCV64zB06osfQKOOMSdr6b9U6BomNFyjBMfYrfCC67ewUAQXeOwM4Z8UPkB2GXwCajMfUy-ng2SjYDBeMAwGA1UdEwEB_wQCMAAwDgYDVR0PAQH_BAQDAgeAMB0GA1UdDgQWBBTurdB-aV5qaJUBiPLPkubFZsmo3TAfBgNVHSMEGDAWgBTb74VjcIvCh1jAUnlFW3gvQdrnpTAKBggqhkjOPQQDAgNIADBFAiEAgYVMWeC7X2_CSjAfLq3Ps9DyQsptRuHlObwv6uZDkj0CIAYGWOz57szftibkzuORJaN6B2cyNmYUASaCvRtxXJ6R",
            "MIIB-jCCAZ-gAwIBAgIFBLHXAhkwCgYIKoZIzj0EAwIwTzELMAkGA1UEBhMCSUQxIzAhBgNVBAoMGlBUIENvbnRvaCBQZXJhbmdrYXQgS3JpcHRvMRswGQYDVQQDDBJDb250b2ggSFNNIFJvb3QgQ0EwHhcNMjUwNjAxMDAwMDAwWhcNNDUwNjAxMDAwMDAwWjBRMQswCQYDVQQGEwJJRDEjMCEGA1UECgwaUFQgQ29udG9oIFBlcmFuZ2thdCBLcmlwdG8xHTAbBgNVBAMMFENvbnRvaCBIU00gN1E0Sy0wMjE5MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEn2f_eLo9mi3eG2P7zRKH0gtJmnBwSvavsX7FjOQl8Boa1jsJYswgvAAirXjy0eONzJGkoJ5u8TXl4Mienb_egaNmMGQwEgYDVR0TAQH_BAgwBgEB_wIBADAOBgNVHQ8BAf8EBAMCAgQwHQYDVR0OBBYEFNvvhWNwi8KHWMBSeUVbeC9B2uelMB8GA1UdIwQYMBaAFKc7FiFUzk9-74EH7FvsRLLGiuhhMAoGCCqGSM49BAMCA0kAMEYCIQDPcKL_Ot26hCA9wIGbr8XO76BVH1MGB3cWjjvxxIVKjAIhAOAlMl96NEJ28JW_CfQb5coHes6CA7w3ibDwqVJWps1j"
          ]
        }
      }
    ],
    "certificationRequests": [
      {
        "purpose": "issuance-cose",
        "csr": "MIIBNzCB3gIBADB8MQswCQYDVQQGEwJJRDE-MDwGA1UECgw1RGlyZWt0b3JhdCBKZW5kZXJhbCBLZXBlbmR1ZHVrYW4gZGFuIFBlbmNhdGF0YW4gU2lwaWwxLTArBgNVBAMMJER1a2NhcGlsIG1kb2MgRG9jdW1lbnQgU2lnbmVyIDIwMjYtQTBZMBMGByqGSM49AgEGCCqGSM49AwEHA0IABNGGzGNnN9NBiCV64zB06osfQKOOMSdr6b9U6BomNFyjBMfYrfCC67ewUAQXeOwM4Z8UPkB2GXwCajMfUy-ng2SgADAKBggqhkjOPQQDAgNIADBFAiEAuk8C-F6Lo9m6Z7E5W59j2Zcb32QcK_eA4duzasK5MusCIANXavJUuXJj6sl1OqGkJO9QUKzNx4KqOrJs7sTL2zL4"
      },
      {
        "purpose": "status-list",
        "csr": "MIIBNjCB3AIBADB6MQswCQYDVQQGEwJJRDE-MDwGA1UECgw1RGlyZWt0b3JhdCBKZW5kZXJhbCBLZXBlbmR1ZHVrYW4gZGFuIFBlbmNhdGF0YW4gU2lwaWwxKzApBgNVBAMMIkR1a2NhcGlsIFN0YXR1cyBMaXN0IFNpZ25lciAyMDI2LUEwWTATBgcqhkjOPQIBBggqhkjOPQMBBwNCAASZjj_68TvJLv6teEn0zYkj8Kyl38FY3Mq0Rdr6tGzsmlz37fb8alRic71wq8I5d2H4NV3BU8WG3b2vmykXXF2soAAwCgYIKoZIzj0EAwIDSQAwRgIhALHy_gPVQHK0KQ2JYyG1c-Pua6ZqoM706IItqawH7wBaAiEAtNzH3Iy9cKCvwVEcrEvA1CFOe7UVCn59gxXKxd5zspU"
      }
    ]
  }
}
```

``` { .http title="200, the answer to a certificate request" data-format="HTTP" }
HTTP/1.1 200 OK
Replay-Nonce: z2hGd6L3_gsvLDG_2XP82xxmAw2wuKO3
Cache-Control: no-store
Content-Type: application/json

{
  "certificates": [
    {
      "purpose": "issuance-cose",
      "certificate": "MIICqjCCAlCgAwIBAgIMFqmFNGJqaLIdEMCbMAoGCCqGSM49BAMCMFkxCzAJBgNVBAYTAklEMSswKQYDVQQKDCJUcnVzdCBBdXRob3JpdHkgUmVwdWJsaWsgSW5kb25lc2lhMR0wGwYDVQQDDBRJRENURiBJc3N1ZXIgUm9vdCBDQTAeFw0yNjA5MDEwMDAwMDBaFw0yNzExMDEwMDAwMDBaMHwxCzAJBgNVBAYTAklEMT4wPAYDVQQKDDVEaXJla3RvcmF0IEplbmRlcmFsIEtlcGVuZHVkdWthbiBkYW4gUGVuY2F0YXRhbiBTaXBpbDEtMCsGA1UEAwwkRHVrY2FwaWwgbWRvYyBEb2N1bWVudCBTaWduZXIgMjAyNi1BMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE0YbMY2c300GIJXrjMHTqix9Ao44xJ2vpv1ToGiY0XKMEx9it8ILrt7BQBBd47AzhnxQ-QHYZfAJqMx9TL6eDZKOB2jCB1zAMBgNVHRMBAf8EAjAAMA4GA1UdDwEB_wQEAwIHgDAVBgNVHSUBAf8ECzAJBgcogYxdBQECMB8GA1UdIwQYMBaAFPvw1Wqwv9qASjLt3TPMyd3Sg3maMB0GA1UdDgQWBBTurdB-aV5qaJUBiPLPkubFZsmo3TAeBgNVHRIEFzAVhhNodHRwczovL3RydXN0LmdvLmlkMEAGA1UdHwQ5MDcwNaAzoDGGL2h0dHBzOi8vcmVnaXN0cnkudHJ1c3QuZ28uaWQvY3JsL2lzc3Vlci1yb290LWNhMAoGCCqGSM49BAMCA0gAMEUCIB7a47XayNlMAd68To0wXzx-OpBwHYci_FWqKKm-kMppAiEA4fMeNqaylzA-OovL4A05fUWrdfb5eyKg7MXTU90r2O8"
    },
    {
      "purpose": "status-list",
      "certificate": "MIICkDCCAjegAwIBAgIMOT87A0UqrARSSWmjMAoGCCqGSM49BAMCMFkxCzAJBgNVBAYTAklEMSswKQYDVQQKDCJUcnVzdCBBdXRob3JpdHkgUmVwdWJsaWsgSW5kb25lc2lhMR0wGwYDVQQDDBRJRENURiBJc3N1ZXIgUm9vdCBDQTAeFw0yNjA5MDEwMDAwMDBaFw0yOTA5MDEwMDAwMDBaMHoxCzAJBgNVBAYTAklEMT4wPAYDVQQKDDVEaXJla3RvcmF0IEplbmRlcmFsIEtlcGVuZHVkdWthbiBkYW4gUGVuY2F0YXRhbiBTaXBpbDErMCkGA1UEAwwiRHVrY2FwaWwgU3RhdHVzIExpc3QgU2lnbmVyIDIwMjYtQTBZMBMGByqGSM49AgEGCCqGSM49AwEHA0IABJmOP_rxO8ku_q14SfTNiSPwrKXfwVjcyrRF2vq0bOyaXPft9vxqVGJzvXCrwjl3Yfg1XcFTxYbdva-bKRdcXayjgcMwgcAwDAYDVR0TAQH_BAIwADAOBgNVHQ8BAf8EBAMCB4AwHwYDVR0jBBgwFoAU-_DVarC_2oBKMu3dM8zJ3dKDeZowHQYDVR0OBBYEFIXFBrtnV4Odda_HXZvsmvAp5n2AMB4GA1UdEgQXMBWGE2h0dHBzOi8vdHJ1c3QuZ28uaWQwQAYDVR0fBDkwNzA1oDOgMYYvaHR0cHM6Ly9yZWdpc3RyeS50cnVzdC5nby5pZC9jcmwvaXNzdWVyLXJvb3QtY2EwCgYIKoZIzj0EAwIDRwAwRAIgOyA_D0tKOX0VLFgnzP9FM5r6PRYbiJnqVglVv5MDl0sCIBUVE0N58jwFGeU7hLCHckCj1BC5WC9LDs3iwF8SKn_P"
    }
  ]
}
```

A Relying Party that registers merchants asks for its Verifier Issuing CA
the same way. The key lives in a cloud key service whose statement over a
key this specification does not read, so its evidence is the Assessment
Body report on the key ceremony; the request is countersigned with the
Relying Party's Request Object key, and the certificate in the answer is
the one
[Issuing and validating the X.509 certificates and the VICAL](issuing-and-validating-the-x509-certificates-and-the-vical.md)
shows.

``` { .http title="POST /entities/me/keys, a Verifier Issuing CA request" data-format="HTTP" }
POST /entities/me/keys HTTP/1.1
Host: entities.trust.go.id
Content-Type: application/jose

eyJhbGciOiJFZERTQSIsImtpZCI6ImRpZDprZXk6ejZNa3R2OHNOOVpIeFV6UnJvWmpQVWRiY1BGOThkQjZOQ2o3VzZmMWFEa1Bpd3E0I3o2TWt0djhzTjlaSHhVelJyb1pqUFVkYmNQRjk4ZEI2TkNqN1c2ZjFhRGtQaXdxNCIsIm5vbmNlIjoiejVISFJvNzdDN2NZTmFXckh3OUxUV0hwMF9iZlJPeTAiLCJ1cmwiOiJodHRwczovL2VudGl0aWVzLnRydXN0LmdvLmlkL2VudGl0aWVzL21lL2tleXMifQ.eyJjb3VudGVyc2lnbmF0dXJlIjoiZXlKMGVYQWlPaUoyYm1RdWFXUXVhV1JqZEdZdWEyVjVMWEJ2Y0N0cWQzUWlMQ0poYkdjaU9pSkZVekkxTmlJc0ltdHBaQ0k2SW1ScFpEcDNaV0oyYURwUmJWVkJWRU0xYW5sbU5YbFdlVGN5UjFsQmNEaHVVM1oxZDNOb2VrUjVObmRaV0RkWGJVNVpOVlZLZEZoVU9uUmxjbTFwYm1Gc0xXNTFjMkZ1ZEdGeVlTNWpieTVwWkNOeVpYRjFaWE4wTFc5aWFtVmpkQzB4SW4wLmV5SmhkV1FpT2lKa2FXUTZkMlZpZG1nNlVXMWFhbmt4ZERsdlJtbGhSbXBvV0RKbE16aDFUWFZTTjIxbmRHUk1ha2hRVFVkbWFrVm1kbkp6YldGcGNUcDBjblZ6ZEM1bmJ5NXBaQ0lzSW01dmJtTmxJam9pZWpWSVNGSnZOemRETjJOWlRtRlhja2gzT1V4VVYwaHdNRjlpWmxKUGVUQWlMQ0pwWVhRaU9qRTNPREF5TnpFM01EQjkucGUxZEQ4bXVrMEFWaXNXTVhvaV9xSS1CWjY2dXJ0cWQ4ODYtVkJMc1NGeGVEMDhVT3pZcWRwdW5iSzlvanpBeDJIUHVvWVlJcDBKNURnbW5qZi1HQkEiLCJrZXlTdG9yYWdlIjpbeyJrZXkiOiJ6RG5hZXNodjRENEMyN3NQRGdHSmNMV3d6UHBDZTc0WHR0NEQzUFg2Mll6czhxMzZxIiwic3RvcmFnZSI6ImNsb3Vka21zIiwiZXZpZGVuY2UiOnsiZm9ybWF0IjoiYXNzZXNzbWVudC1yZXBvcnQiLCJyZXBvcnQiOiJBQi0yMDI2LTA0MTIifX1dLCJjZXJ0aWZpY2F0aW9uUmVxdWVzdHMiOlt7InB1cnBvc2UiOiJ2ZXJpZmllci1pc3N1aW5nLWNhIiwiY3NyIjoiTUlJQkZqQ0J2UUlCQURCYk1Rc3dDUVlEVlFRR0V3SkpSREViTUJrR0ExVUVDZ3dTVkdWeWJXbHVZV3dnVG5WellXNTBZWEpoTVM4d0xRWURWUVFERENaVVpYSnRhVzVoYkNCT2RYTmhiblJoY21FZ1ZtVnlhV1pwWlhJZ1NYTnpkV2x1WnlCRFFUQlpNQk1HQnlxR1NNNDlBZ0VHQ0NxR1NNNDlBd0VIQTBJQUJKVkJkWWJGcmdZQ0s3VW5fZHhmZHpmY1hOTlNHRUJ1emJNX3ZBUGhGZXlLOFlGbU16TkJqMmsyREF2cy10TEFWbzFiN29EUWRHN3Jkcl9QWjBVUGYzMmdBREFLQmdncWhrak9QUVFEQWdOSUFEQkZBaUFPZEZlTFM0aE1oSTd1WlRzWXdkdE50dEtTZ1NLeFlOOC1RaS14d0c5clRnSWhBSjlvNHJ6X1R5N3VnQWhMSm9TWGRtVTcwb1hFRGk5Q2hTcHBwOW05dlZNYSJ9XX0.lp4An4YDu3X_wrCFD-GuRtc3sEEU1ZvAwXbsI0J48w-RQXgJb0h62ucFwLDAsX_i6AUPJPBSO-eTVcRPJkKCAg
```

``` { .json title="The Verifier Issuing CA request, decoded" data-format="JSON" }
{
  "protected": {
    "alg": "EdDSA",
    "kid": "did:key:z6Mktv8sN9ZHxUzRroZjPUdbcPF98dB6NCj7W6f1aDkPiwq4#z6Mktv8sN9ZHxUzRroZjPUdbcPF98dB6NCj7W6f1aDkPiwq4",
    "nonce": "z5HHRo77C7cYNaWrHw9LTWHp0_bfROy0",
    "url": "https://entities.trust.go.id/entities/me/keys"
  },
  "payload": {
    "countersignature": "eyJ0eXAiOiJ2bmQuaWQuaWRjdGYua2V5LXBvcCtqd3QiLCJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDp3ZWJ2aDpRbVVBVEM1anlmNXlWeTcyR1lBcDhuU3Z1d3NoekR5NndZWDdXbU5ZNVVKdFhUOnRlcm1pbmFsLW51c2FudGFyYS5jby5pZCNyZXF1ZXN0LW9iamVjdC0xIn0.eyJhdWQiOiJkaWQ6d2Vidmg6UW1aankxdDlvRmlhRmpoWDJlMzh1TXVSN21ndGRMakhQTUdmakVmdnJzbWFpcTp0cnVzdC5nby5pZCIsIm5vbmNlIjoiejVISFJvNzdDN2NZTmFXckh3OUxUV0hwMF9iZlJPeTAiLCJpYXQiOjE3ODAyNzE3MDB9.pe1dD8muk0AVisWMXoi_qI-BZ66urtqd886-VBLsSFxeD08UOzYqdpunbK9ojzAx2HPuoYYIp0J5Dgmnjf-GBA",
    "keyStorage": [
      {
        "key": "zDnaeshv4D4C27sPDgGJcLWwzPpCe74Xtt4D3PX62Yzs8q36q",
        "storage": "cloudkms",
        "evidence": {
          "format": "assessment-report",
          "report": "AB-2026-0412"
        }
      }
    ],
    "certificationRequests": [
      {
        "purpose": "verifier-issuing-ca",
        "csr": "MIIBFjCBvQIBADBbMQswCQYDVQQGEwJJRDEbMBkGA1UECgwSVGVybWluYWwgTnVzYW50YXJhMS8wLQYDVQQDDCZUZXJtaW5hbCBOdXNhbnRhcmEgVmVyaWZpZXIgSXNzdWluZyBDQTBZMBMGByqGSM49AgEGCCqGSM49AwEHA0IABJVBdYbFrgYCK7Un_dxfdzfcXNNSGEBuzbM_vAPhFeyK8YFmMzNBj2k2DAvs-tLAVo1b7oDQdG7rdr_PZ0UPf32gADAKBggqhkjOPQQDAgNIADBFAiAOdFeLS4hMhI7uZTsYwdtNttKSgSKxYN8-Qi-xwG9rTgIhAJ9o4rz_Ty7ugAhLJoSXdmU70oXEDi9ChSppp9m9vVMa"
      }
    ]
  }
}
```

``` { .http title="200, the answer to a Verifier Issuing CA request" data-format="HTTP" }
HTTP/1.1 200 OK
Replay-Nonce: F0GA3bAHUAwgU5QeIAyzZGjd390HGa_G
Cache-Control: no-store
Content-Type: application/json

{
  "certificates": [
    {
      "purpose": "verifier-issuing-ca",
      "certificate": "MIICcDCCAhegAwIBAgINALWJzfYbiJ6_CpzOBTAKBggqhkjOPQQDAjBbMQswCQYDVQQGEwJJRDErMCkGA1UECgwiVHJ1c3QgQXV0aG9yaXR5IFJlcHVibGlrIEluZG9uZXNpYTEfMB0GA1UEAwwWSURDVEYgVmVyaWZpZXIgUm9vdCBDQTAeFw0yNjA2MDEwMDAwMDBaFw0zMTA2MDEwMDAwMDBaMFsxCzAJBgNVBAYTAklEMRswGQYDVQQKDBJUZXJtaW5hbCBOdXNhbnRhcmExLzAtBgNVBAMMJlRlcm1pbmFsIE51c2FudGFyYSBWZXJpZmllciBJc3N1aW5nIENBMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAElUF1hsWuBgIrtSf93F93N9xc01IYQG7Nsz-8A-EV7IrxgWYzM0GPaTYMC-z60sBWjVvugNB0but2v89nRQ9_faOBvzCBvDASBgNVHRMBAf8ECDAGAQH_AgEAMA4GA1UdDwEB_wQEAwIBBjASBgNVHSUECzAJBgcogYxdBQEGMB8GA1UdIwQYMBaAFFnF8EN4aHfG4uKhJUSkMD1K7gTzMB0GA1UdDgQWBBQuo7b1odPn9_kgYF7_6ICgWYF5MzBCBgNVHR8EOzA5MDegNaAzhjFodHRwczovL3JlZ2lzdHJ5LnRydXN0LmdvLmlkL2NybC92ZXJpZmllci1yb290LWNhMAoGCCqGSM49BAMCA0cAMEQCICG2iSLIuvM1F8n0ZjzNVRBhsY_aWRe6s9BMBmhN7PNGAiASz3-SCPOvuVg4P8-qIfaeGtkuO4Mv13sfZgKZz6rlrQ"
    }
  ]
}
```

A rotation carries the next log entry. Below is the one
[Witnessing a log entry and serving its copy](witnessing-a-log-entry-and-serving-its-copy.md)
shows Trust Authority handing on, as the entity sent it: the same entry,
the same two proofs of possession over the same nonce, and the storage
evidence of the new `issuance-jose` key. The request is signed with the
update key of the first entry, because that is the latest entry witnessed
when it is sent.

``` { .http title="POST /entities/me/keys, a rotation" data-format="HTTP" }
POST /entities/me/keys HTTP/1.1
Host: entities.trust.go.id
Content-Type: application/jose

eyJhbGciOiJFZERTQSIsImtpZCI6ImRpZDprZXk6ejZNa2hEWFp0QkhMVUtLMjdHMWQ1czVDTjRKNmVrSndCaFJyZm1rQktNS0Q1RFZYI3o2TWtoRFhadEJITFVLSzI3RzFkNXM1Q040SjZla0p3QmhScmZta0JLTUtENURWWCIsIm5vbmNlIjoiZ3BrRi0zaW1MOVRfLVVNZlRDbzVwZmE2elJOUXUxc0oiLCJ1cmwiOiJodHRwczovL2VudGl0aWVzLnRydXN0LmdvLmlkL2VudGl0aWVzL21lL2tleXMifQ.eyJsb2dFbnRyeSI6eyJ2ZXJzaW9uSWQiOiIyLVFtTnI3dkhQQ25TQThHVmVRcGVCWmRqMXZOaGVadml5VmpSd2lKeTNndDF6SkUiLCJ2ZXJzaW9uVGltZSI6IjIwMjYtMDktMTVUMDk6MDA6MDBaIiwicGFyYW1ldGVycyI6eyJ1cGRhdGVLZXlzIjpbIno2TWtnbmVHcnhlTmRpMm1pNnN3aWRwMzhpcXRrazZyMmlhRWdmMjVLdWZiN3JSTCJdLCJuZXh0S2V5SGFzaGVzIjpbIlFtWFZxRXlHd3pRSGZMUTFTRzRNQ0tBNUdITnZ1SlJEVjIyWFg1Q0NRcnNqY3ciXSwid2l0bmVzcyI6eyJ0aHJlc2hvbGQiOjEsIndpdG5lc3NlcyI6W3siaWQiOiJkaWQ6a2V5Ono2TWtyR1JzMXAyRmpzUXN4SnRLd21hVW90ekd0am1qY3ZNN3VLY25YVTdmZkxLZSJ9LHsiaWQiOiJkaWQ6a2V5Ono2TWt0cWpFVksxUDFIZ01TSllHcFBZanVMakVhMTN1MjZXRWhmN2R2Q1dQWVpqMSJ9XX19LCJzdGF0ZSI6eyJAY29udGV4dCI6WyJodHRwczovL3d3dy53My5vcmcvbnMvZGlkL3YxIiwiaHR0cHM6Ly93M2lkLm9yZy9zZWN1cml0eS9tdWx0aWtleS92MSJdLCJpZCI6ImRpZDp3ZWJ2aDpRbWNFVlQyaUpTcnNzNWhnd2lNRnNNVXhLa1JvemdGRjQ1OFJjZ2dUNE1GMkw0OmR1a2NhcGlsLmdvLmlkIiwidmVyaWZpY2F0aW9uTWV0aG9kIjpbeyJpZCI6ImRpZDp3ZWJ2aDpRbWNFVlQyaUpTcnNzNWhnd2lNRnNNVXhLa1JvemdGRjQ1OFJjZ2dUNE1GMkw0OmR1a2NhcGlsLmdvLmlkI2lzc3VhbmNlLWpvc2UtMSIsInR5cGUiOiJNdWx0aWtleSIsImNvbnRyb2xsZXIiOiJkaWQ6d2Vidmg6UW1jRVZUMmlKU3JzczVoZ3dpTUZzTVV4S2tSb3pnRkY0NThSY2dnVDRNRjJMNDpkdWtjYXBpbC5nby5pZCIsInB1YmxpY0tleU11bHRpYmFzZSI6InpEbmFlV1N3SkRyS0xyYUhlNXc0dkEzOXhGVzJUblphRERORUdHV1N5SFlTQzlOZnAifSx7ImlkIjoiZGlkOndlYnZoOlFtY0VWVDJpSlNyc3M1aGd3aU1Gc01VeEtrUm96Z0ZGNDU4UmNnZ1Q0TUYyTDQ6ZHVrY2FwaWwuZ28uaWQjc3RhdHVzLWxpc3QtMSIsInR5cGUiOiJNdWx0aWtleSIsImNvbnRyb2xsZXIiOiJkaWQ6d2Vidmg6UW1jRVZUMmlKU3JzczVoZ3dpTUZzTVV4S2tSb3pnRkY0NThSY2dnVDRNRjJMNDpkdWtjYXBpbC5nby5pZCIsInB1YmxpY0tleU11bHRpYmFzZSI6InpEbmFlYW1QRUtkVjRWWW1zRGFQcjlmM0x5RU5HUkZUd0hScG9OdlJMeWkyZ3pudkQifSx7ImlkIjoiZGlkOndlYnZoOlFtY0VWVDJpSlNyc3M1aGd3aU1Gc01VeEtrUm96Z0ZGNDU4UmNnZ1Q0TUYyTDQ6ZHVrY2FwaWwuZ28uaWQjaXNzdWFuY2Utam9zZS0yIiwidHlwZSI6Ik11bHRpa2V5IiwiY29udHJvbGxlciI6ImRpZDp3ZWJ2aDpRbWNFVlQyaUpTcnNzNWhnd2lNRnNNVXhLa1JvemdGRjQ1OFJjZ2dUNE1GMkw0OmR1a2NhcGlsLmdvLmlkIiwicHVibGljS2V5TXVsdGliYXNlIjoiekRuYWVnbXZqUDV5TXluWWRRRHNEeVJBdENLSG9vVDdQdWhxVmF4TjdSU0FnQlo2RSJ9XSwiYXNzZXJ0aW9uTWV0aG9kIjpbImRpZDp3ZWJ2aDpRbWNFVlQyaUpTcnNzNWhnd2lNRnNNVXhLa1JvemdGRjQ1OFJjZ2dUNE1GMkw0OmR1a2NhcGlsLmdvLmlkI2lzc3VhbmNlLWpvc2UtMiIsImRpZDp3ZWJ2aDpRbWNFVlQyaUpTcnNzNWhnd2lNRnNNVXhLa1JvemdGRjQ1OFJjZ2dUNE1GMkw0OmR1a2NhcGlsLmdvLmlkI3N0YXR1cy1saXN0LTEiXX0sInByb29mIjpbeyJ0eXBlIjoiRGF0YUludGVncml0eVByb29mIiwiY3J5cHRvc3VpdGUiOiJlZGRzYS1qY3MtMjAyMiIsInZlcmlmaWNhdGlvbk1ldGhvZCI6ImRpZDprZXk6ejZNa2duZUdyeGVOZGkybWk2c3dpZHAzOGlxdGtrNnIyaWFFZ2YyNUt1ZmI3clJMI3o2TWtnbmVHcnhlTmRpMm1pNnN3aWRwMzhpcXRrazZyMmlhRWdmMjVLdWZiN3JSTCIsInByb29mUHVycG9zZSI6ImFzc2VydGlvbk1ldGhvZCIsInByb29mVmFsdWUiOiJ6Mm11ZEUxSlZFaFpRZ3hlTjVkdXkxUG1lQ2htbzlyOW1SelpycEVjUFZXSkE5SnA2blo5MlBDM3Q4U2ZlTUdzY0dDTWZkRGh3UGcxM0Y5Q3lXd0paeUFMViJ9XX0sInByb29mT2ZQb3NzZXNzaW9uIjpbImV5SjBlWEFpT2lKMmJtUXVhV1F1YVdSamRHWXVhMlY1TFhCdmNDdHFkM1FpTENKaGJHY2lPaUpGWkVSVFFTSXNJbXRwWkNJNkltUnBaRHByWlhrNmVqWk5hMmR1WlVkeWVHVk9aR2t5YldrMmMzZHBaSEF6T0dseGRHdHJObkl5YVdGRloyWXlOVXQxWm1JM2NsSk1JM28yVFd0bmJtVkhjbmhsVG1ScE1tMXBObk4zYVdSd016aHBjWFJyYXpaeU1tbGhSV2RtTWpWTGRXWmlOM0pTVENKOS5leUpoZFdRaU9pSmthV1E2ZDJWaWRtZzZVVzFhYW5reGREbHZSbWxoUm1wb1dESmxNemgxVFhWU04yMW5kR1JNYWtoUVRVZG1ha1ZtZG5KemJXRnBjVHAwY25WemRDNW5ieTVwWkNJc0ltNXZibU5sSWpvaVozQnJSaTB6YVcxTU9WUmZMVlZOWmxSRGJ6VndabUUyZWxKT1VYVXhjMG9pTENKcFlYUWlPakUzT0RrME5qSTROakI5LjN1ZWJCT0dWdkZISkprbXRwV25hNGFudmtiYTVoNWFUekpJM2NDVG1sNG9Vd1djdU5PeGxjMFlJQUJpWlpHWDFwbVFDQ3FsOFQyOVlXYWlkZWsxWURRIiwiZXlKMGVYQWlPaUoyYm1RdWFXUXVhV1JqZEdZdWEyVjVMWEJ2Y0N0cWQzUWlMQ0poYkdjaU9pSkZVekkxTmlJc0ltdHBaQ0k2SW1ScFpEcDNaV0oyYURwUmJXTkZWbFF5YVVwVGNuTnpOV2huZDJsTlJuTk5WWGhMYTFKdmVtZEdSalExT0ZKaloyZFVORTFHTWt3ME9tUjFhMk5oY0dsc0xtZHZMbWxrSTJsemMzVmhibU5sTFdwdmMyVXRNaUo5LmV5SmhkV1FpT2lKa2FXUTZkMlZpZG1nNlVXMWFhbmt4ZERsdlJtbGhSbXBvV0RKbE16aDFUWFZTTjIxbmRHUk1ha2hRVFVkbWFrVm1kbkp6YldGcGNUcDBjblZ6ZEM1bmJ5NXBaQ0lzSW01dmJtTmxJam9pWjNCclJpMHphVzFNT1ZSZkxWVk5abFJEYnpWd1ptRTJlbEpPVVhVeGMwb2lMQ0pwWVhRaU9qRTNPRGswTmpJNE5qQjkudGhtSkVxSDNUQzU5MExGakxpdHhEYWtNLWNPbHkxR25QdjEzbE1CZHFXWjRjelkxVkFUang1N2hIWlZxYW1HalNSd2ZsVWNnOEdKSDY5RVhYdEJSdGciXSwia2V5U3RvcmFnZSI6W3sia2V5IjoiekRuYWVnbXZqUDV5TXluWWRRRHNEeVJBdENLSG9vVDdQdWhxVmF4TjdSU0FnQlo2RSIsInN0b3JhZ2UiOiJoc20iLCJldmlkZW5jZSI6eyJmb3JtYXQiOiJ4NTA5LWNoYWluIiwiY2VydHMiOlsiTUlJQjVEQ0NBWXVnQXdJQkFnSUJZekFLQmdncWhrak9QUVFEQWpCUk1Rc3dDUVlEVlFRR0V3SkpSREVqTUNFR0ExVUVDZ3dhVUZRZ1EyOXVkRzlvSUZCbGNtRnVaMnRoZENCTGNtbHdkRzh4SFRBYkJnTlZCQU1NRkVOdmJuUnZhQ0JJVTAwZ04xRTBTeTB3TWpFNU1CNFhEVEkyTURreE5EQXdNREF3TUZvWERUUTFNRFl3TVRBd01EQXdNRm93UlRFTE1Ba0dBMVVFQmhNQ1NVUXhJekFoQmdOVkJBb01HbEJVSUVOdmJuUnZhQ0JRWlhKaGJtZHJZWFFnUzNKcGNIUnZNUkV3RHdZRFZRUUREQWhMWlhrZ01EQTJNekJaTUJNR0J5cUdTTTQ5QWdFR0NDcUdTTTQ5QXdFSEEwSUFCUExYX1dQeTVHemN2eWFfcDZocTVwS1dPTXNTd1JiVzZvazVtWmhfZ0UtUDJaTjZaSk9hampYVENyemthQkZEbWVwdjlIN0xGUUVLbG51S0R0QVY4aGlqWURCZU1Bd0dBMVVkRXdFQl93UUNNQUF3RGdZRFZSMFBBUUhfQkFRREFnZUFNQjBHQTFVZERnUVdCQlNjRjBaM01xRjk5N3hNLWlQUjdrcXozMFRuVERBZkJnTlZIU01FR0RBV2dCVGI3NFZqY0l2Q2gxakFVbmxGVzNndlFkcm5wVEFLQmdncWhrak9QUVFEQWdOSEFEQkVBaUI3LTAxN0wxbzR2VTA3dllpSmFCWHVOQmNnQzF5Zkc4OFFHQk1VTmpOamFnSWdINzl5bzdKLS1RYXFMdWt1Z0lXdGgxZGQ0dFRuc0hXbllOa3NPNUhrZEdvIiwiTUlJQi1qQ0NBWi1nQXdJQkFnSUZCTEhYQWhrd0NnWUlLb1pJemowRUF3SXdUekVMTUFrR0ExVUVCaE1DU1VReEl6QWhCZ05WQkFvTUdsQlVJRU52Ym5SdmFDQlFaWEpoYm1kcllYUWdTM0pwY0hSdk1Sc3dHUVlEVlFRRERCSkRiMjUwYjJnZ1NGTk5JRkp2YjNRZ1EwRXdIaGNOTWpVd05qQXhNREF3TURBd1doY05ORFV3TmpBeE1EQXdNREF3V2pCUk1Rc3dDUVlEVlFRR0V3SkpSREVqTUNFR0ExVUVDZ3dhVUZRZ1EyOXVkRzlvSUZCbGNtRnVaMnRoZENCTGNtbHdkRzh4SFRBYkJnTlZCQU1NRkVOdmJuUnZhQ0JJVTAwZ04xRTBTeTB3TWpFNU1Ga3dFd1lIS29aSXpqMENBUVlJS29aSXpqMERBUWNEUWdBRW4yZl9lTG85bWkzZUcyUDd6UktIMGd0Sm1uQndTdmF2c1g3RmpPUWw4Qm9hMWpzSllzd2d2QUFpclhqeTBlT056Skdrb0o1dThUWGw0TWllbmJfZWdhTm1NR1F3RWdZRFZSMFRBUUhfQkFnd0JnRUJfd0lCQURBT0JnTlZIUThCQWY4RUJBTUNBZ1F3SFFZRFZSME9CQllFRk52dmhXTndpOEtIV01CU2VVVmJlQzlCMnVlbE1COEdBMVVkSXdRWU1CYUFGS2M3RmlGVXprOS03NEVIN0Z2c1JMTEdpdWhoTUFvR0NDcUdTTTQ5QkFNQ0Ewa0FNRVlDSVFEUGNLTF9PdDI2aENBOXdJR2JyOFhPNzZCVkgxTUdCM2NXamp2eHhJVktqQUloQU9BbE1sOTZORUoyOEpXX0NmUWI1Y29IZXM2Q0E3dzNpYkR3cVZKV3BzMWoiXX19XX0.BxTEz63vHfETQ7pz_4OiuytdD2AF1iI9Ga2wvCSYCnsCCcV8EGHyVgVeVHzq6D8L0H5kf-gT5Gjgk1Teo9oADw
```

``` { .json title="The rotation request, decoded" data-format="JSON" }
{
  "protected": {
    "alg": "EdDSA",
    "kid": "did:key:z6MkhDXZtBHLUKK27G1d5s5CN4J6ekJwBhRrfmkBKMKD5DVX#z6MkhDXZtBHLUKK27G1d5s5CN4J6ekJwBhRrfmkBKMKD5DVX",
    "nonce": "gpkF-3imL9T_-UMfTCo5pfa6zRNQu1sJ",
    "url": "https://entities.trust.go.id/entities/me/keys"
  },
  "payload": {
    "logEntry": {
      "versionId": "2-QmNr7vHPCnSA8GVeQpeBZdj1vNheZviyVjRwiJy3gt1zJE",
      "versionTime": "2026-09-15T09:00:00Z",
      "parameters": {
        "updateKeys": [
          "z6MkgneGrxeNdi2mi6swidp38iqtkk6r2iaEgf25Kufb7rRL"
        ],
        "nextKeyHashes": [
          "QmXVqEyGwzQHfLQ1SG4MCKA5GHNvuJRDV22XX5CCQrsjcw"
        ],
        "witness": {
          "threshold": 1,
          "witnesses": [
            {
              "id": "did:key:z6MkrGRs1p2FjsQsxJtKwmaUotzGtjmjcvM7uKcnXU7ffLKe"
            },
            {
              "id": "did:key:z6MktqjEVK1P1HgMSJYGpPYjuLjEa13u26WEhf7dvCWPYZj1"
            }
          ]
        }
      },
      "state": {
        "@context": [
          "https://www.w3.org/ns/did/v1",
          "https://w3id.org/security/multikey/v1"
        ],
        "id": "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id",
        "verificationMethod": [
          {
            "id": "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id#issuance-jose-1",
            "type": "Multikey",
            "controller": "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id",
            "publicKeyMultibase": "zDnaeWSwJDrKLraHe5w4vA39xFW2TnZaDDNEGGWSyHYSC9Nfp"
          },
          {
            "id": "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id#status-list-1",
            "type": "Multikey",
            "controller": "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id",
            "publicKeyMultibase": "zDnaeamPEKdV4VYmsDaPr9f3LyENGRFTwHRpoNvRLyi2gznvD"
          },
          {
            "id": "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id#issuance-jose-2",
            "type": "Multikey",
            "controller": "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id",
            "publicKeyMultibase": "zDnaegmvjP5yMynYdQDsDyRAtCKHooT7PuhqVaxN7RSAgBZ6E"
          }
        ],
        "assertionMethod": [
          "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id#issuance-jose-2",
          "did:webvh:QmcEVT2iJSrss5hgwiMFsMUxKkRozgFF458RcggT4MF2L4:dukcapil.go.id#status-list-1"
        ]
      },
      "proof": [
        {
          "type": "DataIntegrityProof",
          "cryptosuite": "eddsa-jcs-2022",
          "verificationMethod": "did:key:z6MkgneGrxeNdi2mi6swidp38iqtkk6r2iaEgf25Kufb7rRL#z6MkgneGrxeNdi2mi6swidp38iqtkk6r2iaEgf25Kufb7rRL",
          "proofPurpose": "assertionMethod",
          "proofValue": "z2mudE1JVEhZQgxeN5duy1PmeChmo9r9mRzZrpEcPVWJA9Jp6nZ92PC3t8SfeMGscGCMfdDhwPg13F9CyWwJZyALV"
        }
      ]
    },
    "proofOfPossession": [
      "eyJ0eXAiOiJ2bmQuaWQuaWRjdGYua2V5LXBvcCtqd3QiLCJhbGciOiJFZERTQSIsImtpZCI6ImRpZDprZXk6ejZNa2duZUdyeGVOZGkybWk2c3dpZHAzOGlxdGtrNnIyaWFFZ2YyNUt1ZmI3clJMI3o2TWtnbmVHcnhlTmRpMm1pNnN3aWRwMzhpcXRrazZyMmlhRWdmMjVLdWZiN3JSTCJ9.eyJhdWQiOiJkaWQ6d2Vidmg6UW1aankxdDlvRmlhRmpoWDJlMzh1TXVSN21ndGRMakhQTUdmakVmdnJzbWFpcTp0cnVzdC5nby5pZCIsIm5vbmNlIjoiZ3BrRi0zaW1MOVRfLVVNZlRDbzVwZmE2elJOUXUxc0oiLCJpYXQiOjE3ODk0NjI4NjB9.3uebBOGVvFHJJkmtpWna4anvkba5h5aTzJI3cCTml4oUwWcuNOxlc0YIABiZZGX1pmQCCql8T29YWaidek1YDQ",
      "eyJ0eXAiOiJ2bmQuaWQuaWRjdGYua2V5LXBvcCtqd3QiLCJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDp3ZWJ2aDpRbWNFVlQyaUpTcnNzNWhnd2lNRnNNVXhLa1JvemdGRjQ1OFJjZ2dUNE1GMkw0OmR1a2NhcGlsLmdvLmlkI2lzc3VhbmNlLWpvc2UtMiJ9.eyJhdWQiOiJkaWQ6d2Vidmg6UW1aankxdDlvRmlhRmpoWDJlMzh1TXVSN21ndGRMakhQTUdmakVmdnJzbWFpcTp0cnVzdC5nby5pZCIsIm5vbmNlIjoiZ3BrRi0zaW1MOVRfLVVNZlRDbzVwZmE2elJOUXUxc0oiLCJpYXQiOjE3ODk0NjI4NjB9.thmJEqH3TC590LFjLitxDakM-cOly1GnPv13lMBdqWZ4czY1VATjx57hHZVqamGjSRwflUcg8GJH69EXXtBRtg"
    ],
    "keyStorage": [
      {
        "key": "zDnaegmvjP5yMynYdQDsDyRAtCKHooT7PuhqVaxN7RSAgBZ6E",
        "storage": "hsm",
        "evidence": {
          "format": "x509-chain",
          "certs": [
            "MIIB5DCCAYugAwIBAgIBYzAKBggqhkjOPQQDAjBRMQswCQYDVQQGEwJJRDEjMCEGA1UECgwaUFQgQ29udG9oIFBlcmFuZ2thdCBLcmlwdG8xHTAbBgNVBAMMFENvbnRvaCBIU00gN1E0Sy0wMjE5MB4XDTI2MDkxNDAwMDAwMFoXDTQ1MDYwMTAwMDAwMFowRTELMAkGA1UEBhMCSUQxIzAhBgNVBAoMGlBUIENvbnRvaCBQZXJhbmdrYXQgS3JpcHRvMREwDwYDVQQDDAhLZXkgMDA2MzBZMBMGByqGSM49AgEGCCqGSM49AwEHA0IABPLX_WPy5Gzcvya_p6hq5pKWOMsSwRbW6ok5mZh_gE-P2ZN6ZJOajjXTCrzkaBFDmepv9H7LFQEKlnuKDtAV8hijYDBeMAwGA1UdEwEB_wQCMAAwDgYDVR0PAQH_BAQDAgeAMB0GA1UdDgQWBBScF0Z3MqF997xM-iPR7kqz30TnTDAfBgNVHSMEGDAWgBTb74VjcIvCh1jAUnlFW3gvQdrnpTAKBggqhkjOPQQDAgNHADBEAiB7-017L1o4vU07vYiJaBXuNBcgC1yfG88QGBMUNjNjagIgH79yo7J--QaqLukugIWth1dd4tTnsHWnYNksO5HkdGo",
            "MIIB-jCCAZ-gAwIBAgIFBLHXAhkwCgYIKoZIzj0EAwIwTzELMAkGA1UEBhMCSUQxIzAhBgNVBAoMGlBUIENvbnRvaCBQZXJhbmdrYXQgS3JpcHRvMRswGQYDVQQDDBJDb250b2ggSFNNIFJvb3QgQ0EwHhcNMjUwNjAxMDAwMDAwWhcNNDUwNjAxMDAwMDAwWjBRMQswCQYDVQQGEwJJRDEjMCEGA1UECgwaUFQgQ29udG9oIFBlcmFuZ2thdCBLcmlwdG8xHTAbBgNVBAMMFENvbnRvaCBIU00gN1E0Sy0wMjE5MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEn2f_eLo9mi3eG2P7zRKH0gtJmnBwSvavsX7FjOQl8Boa1jsJYswgvAAirXjy0eONzJGkoJ5u8TXl4Mienb_egaNmMGQwEgYDVR0TAQH_BAgwBgEB_wIBADAOBgNVHQ8BAf8EBAMCAgQwHQYDVR0OBBYEFNvvhWNwi8KHWMBSeUVbeC9B2uelMB8GA1UdIwQYMBaAFKc7FiFUzk9-74EH7FvsRLLGiuhhMAoGCCqGSM49BAMCA0kAMEYCIQDPcKL_Ot26hCA9wIGbr8XO76BVH1MGB3cWjjvxxIVKjAIhAOAlMl96NEJ28JW_CfQb5coHes6CA7w3ibDwqVJWps1j"
          ]
        }
      }
    ]
  }
}
```

``` { .http title="200, the answer to a rotation" data-format="HTTP" }
HTTP/1.1 200 OK
Replay-Nonce: FE5zEeu1SOjoDFUiwyfpvQ8lqzslFKyc
Cache-Control: no-store
Content-Type: application/json

{
  "witness": {
    "versionId": "2-QmNr7vHPCnSA8GVeQpeBZdj1vNheZviyVjRwiJy3gt1zJE",
    "proof": [
      {
        "type": "DataIntegrityProof",
        "cryptosuite": "eddsa-jcs-2022",
        "verificationMethod": "did:key:z6MkrGRs1p2FjsQsxJtKwmaUotzGtjmjcvM7uKcnXU7ffLKe#z6MkrGRs1p2FjsQsxJtKwmaUotzGtjmjcvM7uKcnXU7ffLKe",
        "proofPurpose": "assertionMethod",
        "proofValue": "z5tQ7npYT9Hhe59U4oXarFcq7kYJmP2yR5AdGQT67R6oPgpypgktjZEPX9SPwc89h2XDtMnk6PJuuneNGgUn2wMZL"
      }
    ]
  }
}
```

### The first entry {#ts-4-03-the-first-entry}

A registration's first entry is the only one whose update key Trust
Authority has never seen. It is bound to the registration by a second JWS,
inside the payload, keyed with the 32 octets the registration code
encodes, under Hash-based Message Authentication Code (HMAC) with SHA-256,
`HS256` as [RFC 7518][ref-rfc7518] defines it.
[The table of binding members][tbl-ts-4-03-binding-members] gives its
protected header and its payload.

[](){ #tbl-ts-4-03-binding-members }

<figure markdown="1" class="ekdn-table">

| Member | Type | Presence | Value |
|---|---|---|---|
| `alg` | string | Present | `HS256` |
| `kid` | string | Present | The registration identifier |
| `url` | string | Present | The `url` of the request that carries it |
| Payload | octets | Present | The `kid` of the request that carries it, as UTF-8 octets |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-4-03-100 }**REQ-TS-4-03-100** The calling Module MUST carry the binding in `registrationBinding` of the submission that carries the registration's first entry, and in no other.
- [](){ #req-ts-4-03-101 }**REQ-TS-4-03-101** The binding MUST be a JWS in compact serialization, keyed with the 32 octets the registration code encodes, whose protected header and payload are as [the table of binding members][tbl-ts-4-03-binding-members] gives them.
- [](){ #req-ts-4-03-102 }**REQ-TS-4-03-102** Trust Authority MUST refuse with `binding-invalid` a first entry whose binding names no registration with a code it still accepts.
- [](){ #req-ts-4-03-103 }**REQ-TS-4-03-103** Trust Authority MUST refuse with `binding-invalid` a first entry whose binding does not verify under that code.
- [](){ #req-ts-4-03-104 }**REQ-TS-4-03-104** Trust Authority MUST refuse with `binding-invalid` a first entry whose binding carries a `url` or a payload other than the request's `url` and `kid`.
- [](){ #req-ts-4-03-105 }**REQ-TS-4-03-105** Trust Authority MUST refuse with `binding-invalid` a first entry whose `updateKeys` holds any key but the one the request's `kid` names.
- [](){ #req-ts-4-03-106 }**REQ-TS-4-03-106** When it accepts a first entry, Trust Authority MUST set the registration granted, with the time of the answer as the time it took effect.
- [](){ #req-ts-4-03-107 }**REQ-TS-4-03-107** When it accepts a first entry, Trust Authority MUST issue the Accreditation Credential as [Issuing, reissuing, and withdrawing][ts-5-07-issuing-reissuing-and-withdrawing] fixes.
- [](){ #req-ts-4-03-108 }**REQ-TS-4-03-108** Trust Authority MUST carry that credential in the answer to the first entry.
- [](){ #req-ts-4-03-109 }**REQ-TS-4-03-109** When it accepts a first entry, Trust Authority MUST have Trust Registry publish a trusted list carrying the registration's entry.

</div>

The payload ties the code to the key: a binding copied from one request
cannot vouch for another key, and a code learned without the key that
signs the request cannot claim the registration.

### After a revoked update key {#ts-4-03-after-a-revoked-update-key}

A registration whose update key is recorded revoked has no key Trust
Authority accepts a request from, and the way out is the key pre-rotation
held back for this: the next update key, whose hash the latest entry
announced and which nobody has seen. The request that carries the next
entry is signed with that key, as the first entry is, and DID Service
checks that it is the key the hash committed to.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-4-03-110 }**REQ-TS-4-03-110** When the Public Key Registry records the update key of the registration's latest witnessed entry as revoked, the calling Module MUST sign the request that carries the next entry with the update key that entry carries.
- [](){ #req-ts-4-03-111 }**REQ-TS-4-03-111** Trust Authority MUST accept a request signed that way only when its `logEntry` names the registration's DID and the update key of the latest witnessed entry is recorded revoked.

</div>

### Errors {#ts-4-03-errors}

A request the entity endpoint does not carry out is answered with a
problem document as [RFC 9457][ref-rfc9457] defines one, in the form Trust
Registry uses in [Errors][ts-4-02-errors]: the `type` is the IDCTF root
`https://idctf.id/ns/problems/` followed by the code, and names one entry
of a closed list. [The table of problem types][tbl-ts-4-03-problem-types]
gives each entry.

[](){ #tbl-ts-4-03-problem-types }

<figure markdown="1" class="ekdn-table">

| Code | Status | Title | Raised when |
|---|---|---|---|
| `malformed-request` | `400` | `Malformed request` | [REQ-TS-4-03-066][req-ts-4-03-066], [REQ-TS-4-03-081][req-ts-4-03-081] |
| `bad-nonce` | `400` | `Bad nonce` | [REQ-TS-4-03-059][req-ts-4-03-059] |
| `unauthorized` | `403` | `Unauthorized` | [REQ-TS-4-03-068][req-ts-4-03-068] to [REQ-TS-4-03-071][req-ts-4-03-071], [REQ-TS-4-03-082][req-ts-4-03-082] |
| `registration-withdrawn` | `403` | `Registration withdrawn` | [REQ-TS-4-03-072][req-ts-4-03-072] |
| `binding-invalid` | `403` | `Binding invalid` | [REQ-TS-4-03-102][req-ts-4-03-102] to [REQ-TS-4-03-105][req-ts-4-03-105] |
| `role-not-held` | `403` | `Role not held` | [REQ-TS-4-03-088][req-ts-4-03-088] |
| `registration-suspended` | `403` | `Registration suspended` | [REQ-TS-4-03-091][req-ts-4-03-091] |
| `unknown-operation` | `404` | `Unknown operation` | The method or the path is not one of the operations of the entity endpoint |
| `did-mismatch` | `422` | `DID mismatch` | [REQ-TS-4-03-075][req-ts-4-03-075] |
| `key-storage-rejected` | `422` | `Key storage rejected` | [REQ-TS-4-03-083][req-ts-4-03-083] to [REQ-TS-4-03-087][req-ts-4-03-087] |
| `certification-request-rejected` | `422` | `Certification request rejected` | [REQ-TS-4-03-089][req-ts-4-03-089], [REQ-TS-4-03-090][req-ts-4-03-090] |
| `log-unknown`, `not-next-entry`, `proof-of-possession-invalid`, `parameters-rejected`, `did-document-rejected`, `update-key-revoked` | `422` | `Log unknown`, `Not next entry`, `Proof of possession invalid`, `Parameters rejected`, `DID Document rejected`, `Update key revoked` | DID Service refused the entry with the reason of the same name, [REQ-TS-4-03-095][req-ts-4-03-095] |
| `rate-limited` | `429` | `Rate limited` | [REQ-TS-4-03-053][req-ts-4-03-053] |
| `server-error` | `500` | `Server error` | Trust Authority failed for a reason no other code names, DID Service answering `malformed-request` included |
| `witness-unavailable` | `503` | `Witness unavailable` | DID Service answered `503` or could not be reached |
| `signer-unavailable` | `503` | `Signer unavailable` | Trust Authority cannot reach a key it would sign the answer's certificate or credential with |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-4-03-112 }**REQ-TS-4-03-112** Trust Authority MUST answer a request it does not carry out with the status [the table of problem types][tbl-ts-4-03-problem-types] gives, media type `application/problem+json`, and a problem document carrying `type`, `title`, and `status` as that table gives them.
- [](){ #req-ts-4-03-113 }**REQ-TS-4-03-113** Trust Authority MUST NOT answer with a `type` that table does not hold.
- [](){ #req-ts-4-03-114 }**REQ-TS-4-03-114** Trust Authority MUST NOT carry in a problem document anything about another registration.
- [](){ #req-ts-4-03-115 }**REQ-TS-4-03-115** The calling Module MUST read the code from `type`, compared byte for byte.
- [](){ #req-ts-4-03-116 }**REQ-TS-4-03-116** The calling Module MUST NOT dereference `type`.
- [](){ #req-ts-4-03-117 }**REQ-TS-4-03-117** The calling Module MUST NOT treat an entry answered with `witness-unavailable` or `signer-unavailable` as refused.

</div>

A request that reuses a nonce, answered with the nonce the next request
takes:

``` { .http title="400, the answer to a request whose nonce was used" data-format="HTTP" }
HTTP/1.1 400 Bad Request
Replay-Nonce: s_2nyjg8HvhTZGUvXwEFbCk3xaJksY-C
Cache-Control: no-store
Content-Type: application/problem+json

{
  "type": "https://idctf.id/ns/problems/bad-nonce",
  "title": "Bad nonce",
  "status": 400
}
```

## Security considerations {#ts-4-03-security-considerations}

Each threat below is answered by the requirement named with it.

- **A stolen portal password.** Every sign-in asks for a second factor,
  [REQ-TS-4-03-004][req-ts-4-03-004], and an account acts only for the registrations its
  holder was named for, [REQ-TS-4-03-007][req-ts-4-03-007].
- **A replayed request.** Each nonce is accepted once and for a short
  time, [REQ-TS-4-03-058][req-ts-4-03-058] and [REQ-TS-4-03-059][req-ts-4-03-059], and each request names
  the address it was signed for, [REQ-TS-4-03-070][req-ts-4-03-070], so a captured request works
  neither again nor elsewhere.
- **A registration claimed by someone else.** The first entry needs the
  registration code, which the portal shows once to an account of the
  registration, [REQ-TS-4-03-020][req-ts-4-03-020], and accepts once, [REQ-TS-4-03-022][req-ts-4-03-022], and
  the binding ties it to one update key, [REQ-TS-4-03-104][req-ts-4-03-104] and
  [REQ-TS-4-03-105][req-ts-4-03-105].
- **A stolen update key.** The update key opens the entity endpoint and
  nothing in the portal. Pre-rotation keeps the thief from rotating to a
  key of its own, as [the update key][the-update-key] sets out, and a
  certificate over a key of the thief's choosing needs a countersignature
  by a transaction key the update key does not reach,
  [REQ-TS-4-03-082][req-ts-4-03-082]. Once the key is recorded revoked, a request it
  signs is refused, [REQ-TS-4-03-071][req-ts-4-03-071], and so is any entry,
  [REQ-TS-4-01-008][req-ts-4-01-008].
- **A key claimed to be stronger than it is.** Storage is taken on
  evidence the device signs, or on an Assessment Body report,
  [REQ-TS-4-03-083][req-ts-4-03-083] to [REQ-TS-4-03-085][req-ts-4-03-085], and checked against the grade the
  permissions demand, [REQ-TS-4-03-086][req-ts-4-03-086].
- **A key that never reached Trust Authority.** No resolver accepts an
  entry DID Service did not witness, and DID Service takes entries from
  Trust Authority only, [REQ-TS-4-01-002][req-ts-4-01-002]; an entry that
  appears on a domain all the same is what the conformance crawler finds,
  as [why nobody can rotate quietly][why-nobody-can-rotate-quietly] sets out.
- **An entry witnessed without its certificate.** Every check runs, and
  every key the answer needs is reached, before the hand-off,
  [REQ-TS-4-03-092][req-ts-4-03-092] and [REQ-TS-4-03-093][req-ts-4-03-093], and nothing is issued for a
  refused entry, [REQ-TS-4-03-096][req-ts-4-03-096].

## Privacy considerations {#ts-4-03-privacy-considerations}

Neither door handles a citizen. What Trust Authority holds about a person
is the name and e-mail address of the person answerable for each body, the
holder of each portal account, and the documents a body sent; these serve
the Root Authority's decision and are published nowhere, because the
trusted list carries the body and not the person, as
[Publishing and reading the trusted list](publishing-and-reading-the-trusted-list.md)
fixes.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-4-03-118 }**REQ-TS-4-03-118** Trust Authority MUST NOT publish the person answerable, an account holder, or any document a registration carried.
- [](){ #req-ts-4-03-119 }**REQ-TS-4-03-119** Trust Authority MUST NOT carry a citizen's data at either door or in the audit trail.

</div>

## Changelog {#ts-4-03-changelog}

<figure markdown="1" class="ekdn-table">

| Version | Date | Change |
|---|---|---|
| 1.0 draft | 19 October 2026 | First draft |

</figure>
