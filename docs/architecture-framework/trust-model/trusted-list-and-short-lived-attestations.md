---
title: "Trusted list and short-lived attestations"
description: What the trusted list answers and how a cached copy of it is trusted, and the four attestations whose limited lifetime does the work of a revocation list.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §5.4, §5.5, §8.6, Kep. 7, 23, 25, 26; Bentuk Data Attestation (Kapan attestation diperlukan, Empat lapis, §3, Kenapa umurnya dibatasi); Rincian Module dan Operasi §2.3, §2.5, §7.4; tracks/0169 (fallback log DID ke DID Service, tidak ada di sumber) -->

# Trusted list and short-lived attestations {#trusted-list-and-short-lived-attestations}

Two mechanisms carry the trust model between transactions. The first is a
list: the trusted list that every verifying party downloads, caches, and
checks a counterpart against. The second is a set of signed statements with a
limited life, which a vouching party issues to a device or an entity that
cannot be found on that list. The list answers for the entities the ecosystem
accredited. The attestations answer for everything one level below them.

## Trusted list and cache {#trusted-list-and-cache}

The trusted list is an index, not a keystore. Each entry names an entity by its
Decentralized Identifier (DID), its name, its status, its role, and the legal
identifier of the body behind it, and for an entity that holds a certificate
authority (CA), the Verifier Issuing CA it issues from. The legal identifier is
the institution code of the Badan Kepegawaian Negara (BKN) for a government body
and the Nomor Induk Berusaha (NIB) for a private one. Every registration of one
legal body carries the same value, so the list shows which entries one body
holds, and the DID still tells them apart. The entity's keys are not in it: a
verifier resolves them from the entity's [DID Document][did-document] instead.

The keys the list does name are of two kinds. One is Trust Authority's own: its
witness key, which Trust SDK checks a witness proof against, and the key the
list is signed with, each as a `did:key`. The other is any key of an entity
revoked early, named in that entity's entry with the time from which it is
revoked. No key of an entity in good standing is listed.
[The trusted list][trusted-list]
records what the list carries, who publishes it, and in what encoding.

### A bulk download, cached {#a-bulk-download-cached}

A wallet and a verifier work from a bulk download of the whole list, cached on
the device or the server, and never from a lookup made during a transaction.
Nothing on the transaction path asks Trust Infrastructure anything while a
transaction runs, which is the principle
[the two paths never cross][the-two-paths-never-cross], and the cache is what
holds that principle up.

The reason is privacy before it is availability. A lookup made once per
transaction would tell Trust Infrastructure exactly which citizen was dealing with which
bank, and when. One download a day covers every transaction the citizen makes
that day and tells Trust Infrastructure nothing about any of them. Availability follows
from the same choice: a verification that starts while Trust Infrastructure is
unreachable completes from the copy already held.

A cached copy is filled and refreshed outside any transaction by
[the scheduled sync][trust-cache-sync], which names everything it pulls and
runs on a jittered timer, so that every device does not reach
Trust Infrastructure in the same second.

An entity missing from the cached copy is not looked up on the spot: the copy
is refreshed on its schedule, never in the middle of a transaction. An
emergency trusted list does not break that rule, because what reaches a
Relying Party between syncs is the notice that goes with it, and the list
itself reaches each cache at its next sync. The hour within which both go out
is the first phase of [entity key revocation][entity-key-revocation].

The same list and notice go out when the Root Authority suspends a whole
entity for misconduct. That suspension stops at the one registration, unless
the Root Authority extends it to every registration of the same legal body,
which all carry one legal identifier on the list.

### Three rules for reading the copy {#three-rules-for-reading-the-copy}

Trust SDK applies these rules in every Module that holds a copy.

1. **The signature is checked every time the copy is read**, not only when it
   was fetched. A copy that was poisoned on disk after download is caught at
   the next read rather than trusted for the rest of its life.
2. **The copy is valid until the `NextUpdate` it carries and is discarded after
   it**, with no grace period. ETSI TS 119 602 V1.1.1 requires it: a
   List of Trusted Entities (LoTE) whose `NextUpdate` has passed is discarded as
   expired, so that an attacker cannot substitute an old list. The room an
   offline device needs sits inside `NextUpdate` instead. Trust Registry sets
   `NextUpdate` to the staleness it is willing to accept from a device with no
   network, within the six-month ceiling the standard allows, and reissues the
   list on the sync schedule regardless, which the standard also permits. A
   Verifier Core that is online refreshes well before the date; a device with no
   network reads its copy up to the date and refuses after.
3. **The other cached artifacts have a tolerance limit.** Each carries a Time to
   Live (TTL) of its own, and past it the last-known-good copy is still used, up
   to the tolerance limit, and refused after. The Governance Profile names every
   copy that has a tolerance and sets one value for each, which serves every
   reader of that copy, online or not. The list is in
   [Tolerances][ts-02-tolerances] and covers:

    - the status list and the CRL;
    - the VICAL;
    - a cached Trust Registry Query Protocol (TRQP) v2.0 answer and an
      Authority Statement;
    - the catalog list;
    - an entity's `did:webvh` log.

    A Status List Token also carries an `exp`, and a copy past it is refused
    whatever the tolerance limit allows. The others name no date at which a
    verifier must discard them, which is why they are treated differently from
    the list. [What connects the two planes][what-connects-the-two-planes]
    states the same bound from the other side.

The `NextUpdate` horizon and the tolerance limit both bind participants and
are checked by assessment, so they belong to the Governance Profile. For the
pilot the Profile sets the horizon at seven days and one tolerance limit for
each other cached artifact, none longer than that horizon.

### The DID Document is not on the central CDN {#the-did-document-is-not-on-the-central-cdn}

The trusted list sits behind the central content delivery network (CDN). The
DID Document does not. `did:webvh` derives the
address of its log from the identifier itself, so
`did:webvh:<scid>:kampus.ac.id` resolves to a `did.jsonl` file at that
university's own domain. The entity signs its own log and serves its own file;
DID Service adds a witness proof to each new entry and keeps a copy of the log,
which [the scheduled sync][trust-cache-sync] reads only when the entity's domain
cannot be reached. An entity's identity is therefore attached to the entity
rather than to Trust Registry, and an outage of the central CDN stops no key
from being resolved. How the log is formed is in
[entities: did:webvh][entities-didwebvh].

### Three questions, three answers {#three-questions-three-answers}

Membership in the ecosystem is never answered by a DID Document.

- **Is this entity accredited?** The trusted list, published by Trust
  Registry to the central CDN.
- **What is it authorized to do?** The Authority Statement, asked for over
  TRQP and answered by Trust Registry, which [Authorization][authorization]
  sets out.
- **Is this signing key its own?** The DID Document, and nothing else.
  The entity's entry in the trusted list adds only whether that key was revoked
  early.

The DID Document is checked last, after the first two have passed. A DID that
is absent from the trusted list is rejected however perfectly its DID Document
resolves, because anyone can mint a DID in five minutes and the list is the
only thing that tells an accredited entity from a forger.

## Short-lived attestations {#short-lived-attestations}

An attestation is a signed statement by one party about another. The rule for
when one is needed is a single sentence: an attestation is required only where
trust cannot be settled through the trusted list. An accredited entity is on
the list, so it introduces itself by its DID and needs no further statement.
A device held by a party that is not on the list, or a key that no list could
vouch for, needs a party that is on the list to speak for it. Three
statements do that. A fourth, the Accreditation Credential, is about an entity
that is on the list: the entity carries it as evidence about itself, and nobody
in the ecosystem relies on it, because the list already answers.
[The four attestations][tbl-four-attestations] names all four.

[](){ #tbl-four-attestations }

<figure markdown="1" class="ekdn-table">

| Attestation | Issued by | About | Vouches that | Lifetime |
|---|---|---|---|---|
| Attestation platform | The phone's chip, Google's or Apple's | On Android each key the keystore generated: a wallet's device key or credential key, or a reader's device key. On iOS the App Attest key alone, which commits to the credential key beside it | The key sits in hardware, and the application holding it is genuine. On iOS what vouches for the credential key is that official application rather than the chip | As long as the key |
| Key Attestation | Wallet Backend Service, for its Wallet Provider | A wallet installation's credential key | The key sits in secure storage of the strength it states, and the installation is still entitled | A day at most, one per issuance |
| Verifier Device Certificate | Verifier Core, from its own Verifier Issuing CA: an RP Intermediary's for a merchant's device, a Relying Party's own for its counter device | A reader on a device: Mobile Verifier, or a Relying Party's own application built on the Reader SDK | The device is genuine and may ask for the attributes in `ReaderAuthRole` | Limited, set by the Governance Profile, plus a CRL |
| Accreditation Credential | Trust Authority | An entity | The entity was accredited | The accreditation period |

</figure>

The attestation platform, the Key Attestation, and the
Verifier Device Certificate each check the one before them, then issue their
own statement in a form the next party understands. The attestation platform is read only by the party that vouches for
the device, Wallet Backend Service or Verifier Core, and never travels further.
The Key Attestation travels with the credential key to the issuer's credential
endpoint at every issuance, and the Credential Rulebook sets the storage it must
report, as [`min_assurance`][min-assurance] sets out. The
Verifier Device Certificate travels with every request a reader device sends.
The Accreditation Credential is carried by the entity it was issued to. Because
it lives as long as the accreditation, it carries a `status` reference to a
status list,
so that it can be revoked before it expires. What each one carries is in
[Key Attestation][key-attestation],
[Verifier Device Certificate][verifier-device-certificate], and
[Accreditation Credential][accreditation-credential].

A limited lifetime makes the attestation platform, the Key Attestation, and
the Verifier Device Certificate revocable without a list that has to reach
everyone. A wallet installation that is disowned is refused its
next attestation, and the issuers that would have read one never have to
be told. A merchant device that stops being renewed reaches the end of its
certificate and nothing more needs to be said. Only a withdrawal made in the
middle of a certificate's life needs announcing, which is the CRL's job: it
carries the certificates revoked
before their expiry and nothing else, so it stays short, and a stale copy of
it on an offline device carries a small risk because the window it covers is
short.

Two of [the four attestations][tbl-four-attestations] do this at different
speeds, and the difference follows from what each one is for. A
Key Attestation is minted for one issuance, lives a day at most, and is never
revoked: it expires. Its expiry
reaches issuance alone, because no verifier ever reads one, and a credential
already on the device goes on being presented until the issuer's status list
says otherwise. A Verifier Device Certificate lives longer than a day, so it is
withdrawn the ordinary X.509 way, through the CRL its issuer publishes and the
wallet reads from cache. How long it lives, how often the CRL is published, and
how stale a CRL may be before an offline wallet refuses it are three numbers the
Governance Profile sets, and the operation may loosen them later.

An attestation vouches for the container, never for the contents. A
Key Attestation says nothing about whether the data in a credential is true, and
a Verifier Device Certificate says nothing about how a merchant treats the data
it receives. Whether the data is true is the issuer's business and its source
system's; how a merchant treats it is set by
[what a merchant does with what it is shown][gf-what-a-merchant-does-with-what-it-is-shown].

### Verifier Device Certificate: a central Relying Party vouching for a small one {#verifier-device-certificate-for-a-small-verifier}

A Relying Party and an RP Intermediary are on the trusted list. Online they
introduce themselves with a `client_id` that is their `did:webvh` and sign
the Request Object with a key from their DID Document. The wallet settles
trust through the cached trusted list and a cached TRQP answer, with no
further artifact.

A merchant is different. A citizen's wallet cannot validate a corner shop's key
against the trusted list, because the shop is not on it and should not be:
[RP Intermediary and merchant][rp-intermediary-and-merchant] says why. No form
of identifier helps here. A shop could hold a `did:key`, and the wallet would
still not know what that key is entitled to ask. The RP Intermediary signs a
statement that the device is its own and may ask for these attributes.

The statement takes the form of a Verifier Device Certificate because
ISO/IEC 18013-5:2021 knows only X.509, so a merchant needs the certificate for
proximity reading anyway. Used online as well, carried in `x5c` behind a
`client_id` of the form `x509_hash`, it leaves the merchant holding one
certificate rather than two, with one validation path and one revocation
mechanism.
[How a verifier introduces itself][tbl-how-a-verifier-introduces-itself] sets
the two cases side by side.

[](){ #tbl-how-a-verifier-introduces-itself }

<figure markdown="1" class="ekdn-table">

| Who | Online | Offline | A certificate online? |
|---|---|---|---|
| Relying Party, RP Intermediary | `client_id` as `did:webvh`; the Request Object signed with a key in the DID Document | Verifier Device Certificate, because ISO/IEC 18013-5 requires X.509 | No: already on the trusted list |
| Merchant | `client_id` as `x509_hash`; the Verifier Device Certificate in `x5c` | Verifier Device Certificate in `x5chain` | Yes: the only route it has |

</figure>

The shape mirrors the wallet side. Mobile Wallet is vouched for by Wallet
Backend Service with a Key Attestation at every issuance; Mobile Verifier is vouched for
by Verifier Core with a Verifier Device Certificate.
[The comparison of the two applications][tbl-wallet-verifier-comparison] takes
the two side by side.

The wallet runs four checks on the certificate, in both channels, and all
four from cache.

1. The chain validates from the Verifier Device Certificate, through the
   Verifier Issuing CA, to the Verifier Root CA the wallet carries from build
   time, and the Verifier Issuing CA belongs to an entity whose status is
   granted on the trusted list, with the entry not naming that CA as revoked.
   [The reader side][the-reader-side] sets out the chain.
2. The certificate has not expired and is not on the CRL.
3. The signature on the request matches the key in the certificate, so the
   certificate is not being used by a different device.
4. The attributes requested are a subset of `ReaderAuthRole`, and the
   difference is refused on the spot rather than left to an audit.

The scope is enforced by the wallet at the moment of the request. A fifth check runs beside these in
both channels and belongs to a different artifact: the requested attributes
are also a subset of the [Use Statement][use-statement] the request carries.

Three keys sit behind a merchant's device, held by two different parties.

<figure markdown="1" class="ekdn-table">

| Function | Key held by |
|---|---|
| Signing the Request Object and the ReaderAuth | The merchant's device key, in its secure element, the key its Verifier Device Certificate certifies |
| Decrypting the response | A key pair the merchant's device draws for one request, keeps on the device, and discards once it has decrypted the response |
| Issuing the Verifier Device Certificate and its CRL | The RP Intermediary, through its Verifier Issuing CA, one certificate per device with a limited lifetime |

</figure>

The `ReaderAuthRole` of a merchant's certificate is always a subset of the
union of the Use Statements of the categories its device is bound to, each
of which sits inside the RP Intermediary's own accreditation scope. Legal responsibility sits with the RP
Intermediary; a citizen's data is never readable by it, because the response
is encrypted to the key the merchant's device drew for that request, and the
relay that carries it holds only ciphertext, briefly.
