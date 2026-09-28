---
title: "Identifier"
description: How the ecosystem identifies an entity, a holder, a credential type, an attribute, and a device, and why each identifier takes a different shape.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §4.2, §4.3 (Kep. 4, 5, 14), §9.2; Rincian Module dan Operasi, DID Service; Bentuk Data Attestation, §3 -->

# 2. Identifier

Five different things in the ecosystem carry an identifier: an entity, a
holder, a credential type, an attribute inside that type, and a device. Each
gets a different shape, because each is asked to do a different job. An
entity's identifier has to resolve to a full history of keys. A holder's
identifier has to bind every credential to the phone that holds it. A
credential type's identifier has to stay fixed for one version and change only
by becoming a new one. A device's identifier has to name a piece of hardware
without ever exposing the key that hardware holds.

| Object | Identifier | Why this shape |
|---|---|---|
| Entity (issuer, verifier, Wallet Provider) | [did:webvh](../references.md#identifiers-and-keys) | An append-only `did.jsonl` log with pre-rotation, so a resolver can walk a key through its full history |
| Holder | One [did:key](../references.md#identifiers-and-keys) per wallet installation, shared by every credential | The simplest binding to run in this phase; presentations can be linked, a cost accepted until the decision is revisited |
| Credential type | `id.go.credential.<TypeName>.v<N>` | A name that stays fixed for one version, and changes only by becoming a new version |
| Attribute in scope | `<type>#<attribute>`, for example `id.go.credential.KTPDigital.v1#usia_di_atas_17` | Names one attribute wherever a rule needs to point at it without pointing at the whole credential |
| Wallet or merchant device | JWK thumbprint of the device key ([RFC 7638](../references.md#identifiers-and-keys)) | Identifies the device without transmitting the key it names |

## 2.1 Entities: did:webvh

Every issuer, verifier, and Wallet Provider identifies itself with did:webvh.
Its address is not looked up in a directory: `did:webvh:<scid>:<domain>`
resolves at the entity's own domain, backed by a signed, append-only log
called `did.jsonl`. The self-certifying identifier inside the address is
derived from that log's own first entry, so the identifier and the log
backing it cannot be pulled apart. What the log holds and how a verifier
reads it is in
[Section 4.2.1, DID Document](artifacts-exchanged.md#421-did-document).

The log being append-only, with pre-rotation, is what makes the identifier
survive a key rotation. An entity that rotates its signing key still needs
every past signature to verify against whichever key was active when that
signature was made, so a resolver has to walk the entity's full key history
rather than trust only the current key. Pre-rotation lets the entity commit to
its next key before that key is ever used, so a thief who steals the current
key cannot also claim the one coming after it.

The identifier proves only that a signature belongs to the entity claiming
it. Whether that entity is allowed to issue or verify at all is a separate
question, answered by the trusted list and by the Authority Statement it can
be asked for, not by did:webvh itself.

## 2.2 Holder: one did:key per wallet installation

did:key needs nothing did:webvh needs. It is derived entirely from a public
key, so there is no log to sign, no domain to host it on, and no resolver
call beyond decoding the identifier itself. The wallet generates one key pair
in the secure element at its first issuance, and the identifier falls out of
it for free.

In this phase that one key serves every credential on the installation, and it
is not created again per issuance. The decision is marked temporary because it
has a known cost. A holder who presents the same identifier to a grocery store
and to a bank can be recognized by the two of them comparing notes, even
without either one reading a single disclosed attribute.

<figure markdown="1" id="figure-2-1">
  ![One citizen holding three credentials that share one did:key, presented to three different verifiers](../../images/architecture-framework/data-model-and-protocols/holder-identifier.svg){ loading=lazy }
  <figcaption><span class="ekdn-fignum">Figure 2.1</span> One citizen, three credentials, one holder identifier.</figcaption>
</figure>

- **Every credential** carries the same did:key, so the wallet holds one holder
  identifier however many credentials it holds.
- **Each verifier** sees that identifier.
- **Comparing notes** lets two verifiers match the holder, which is the exposure
  this phase accepts.

The way out is prepared. Each stored credential records which key binds it, so
a later move to a key per credential, or to the batch issuance OpenID4VCI 1.0
already defines, changes the wallet's key handling and no credential format.

This key is what the rest of the ecosystem calls the credential key: one key
per wallet installation, used for holder binding and for presentation, kept separate
from the device key that identifies the hardware itself (covered in
[Section 2.4](#24-devices)). Each credential format asserts the same holder binding
differently. [SD-JWT VC](../references.md#credential-formats-and-their-signatures) carries it in the `cnf` claim. [ISO mdoc](../references.md#credential-formats-and-their-signatures) carries the same
key as the `DeviceKey` field inside the MSO, a name that belongs to the mdoc
specification's own vocabulary rather than to the physical device. [W3C VCDM 2.0](../references.md#credential-formats-and-their-signatures)
(`ldp_vc`) has no claim to carry it in at all, so it proves possession with a
[Data Integrity](../references.md#credential-formats-and-their-signatures) proof at the presentation level, signed over a `challenge` and a
`domain` the verifier supplies.

Because the credential key is shared across formats as well, a
credential type that ships as both SD-JWT VC and ISO mdoc, per
[Section 1.3, One credential, two representations](credential-formats.md#13-one-credential-two-representations),
binds both representations to the same did:key. The wallet does not mint a
second identifier just because a Credential Rulebook demands a second format.

## 2.3 Credential types and attributes

A credential type is named `id.go.credential.<TypeName>.v<N>`. `TypeName`
capitalizes the start of each word and drops every separator, so a national
ID digital credential type is written `KTPDigital`, and the version number is
never left implicit. The `id.go` namespace is not open for anyone to mint
into: Trust Authority holds it, so a credential type name cannot come
from whoever happens to write a Credential Rulebook.

This identifier anchors the Credential Rulebook that governs the type: it is
the value of the Rulebook's own `id` field, for example
`"id.go.credential.KTPDigital.v1"`. A version is frozen once its Rulebook is
published, so `.v1` never changes meaning underneath a party that already
checked it. A schema change, a new attribute, or a different assurance
requirement is published as `.v2` instead. What else a Rulebook freezes under
that same version is in
[Section 1.6, The Credential Rulebook](credential-formats.md#16-the-credential-rulebook).

An attribute inside a credential type gets its own identifier, built by
appending `#<attribute>` to the type's own:
`id.go.credential.KTPDigital.v1#usia_di_atas_17` names one derived attribute
rather than the whole credential. This is what lets a rule point at a single
attribute instead of at the credential that carries it. An Authority Statement
can grant a role permission over one attribute, and the `ReaderAuthRole`
extension can bound a reader's certificate to that same attribute. Neither has
to enumerate the whole credential type.

## 2.4 Devices

The wallet installation on a citizen's phone and the reader on a merchant's
device are each identified the same way: the JWK thumbprint of their device
key, computed the way RFC 7638 defines it. A thumbprint is a hash over the
public key's own JSON fields, so anyone holding the public key can compute
the identical identifier without asking a registry for it.

This device key is not the credential key from
[Section 2.2](#22-holder-one-didkey-per-wallet-installation). One belongs to the
hardware and is minted once, held in the device's secure element from
provisioning onward. The other is minted at the first issuance, binds every
credential, and never touches the device's own identity. A phone carrying ten
credentials has one credential key beside one device key, and the two are
never the same key.

Publishing only the thumbprint, and never the key, is deliberate: the
identifier is safe to carry inside a request or write to a log, because it
gives an attacker nothing to impersonate the device with, while the private
key stays wherever it was generated. The identifier surfaces in two places: in
registering a wallet installation, and in the messages that ask for a Key
Attestation. Both follow the same protocol paths as everything else a wallet
exchanges with its backend, covered in
[Section 3.1, Protocols per interaction](protocols-and-modes.md#31-protocols-per-interaction).
