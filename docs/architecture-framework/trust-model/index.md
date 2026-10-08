---
title: "Trust Model"
description: Who trusts whom in the ecosystem, through which artifact, and which questions the trust model answers and which it leaves to somebody else.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §5 (pengantar, gambar cakupan, tabel pertanyaan kepercayaan) -->

# Trust Model {#trust-model}

<p class="ekdn-lead" markdown="span">
A credential is only worth what the party reading it can establish about the
party that signed it, the party asking for it, and the device holding it. This
chapter is how each of those is established, by whom, through which artifact,
and for how long an answer stays good.
</p>

The previous chapters named the parties, the Modules, and the artifacts that
pass between them. This one puts them to work on a single job: letting a
wallet or a verifier that has never met the other side decide, from material
it already holds, whether to proceed. Two things carry that decision and
neither stands in for the other. A Decentralized Identifier (DID) Document
proves that a signature belongs to the entity that claims it; Trust Registry
proves that the entity is allowed to have made it. Everything in the chapter
is one or the other of those two proofs, or a statement one party signs about
another because that other is not in the registry at all.

## What the trust model covers and what it leaves out {#trust-model-scope}

The trust model establishes six facts in every transaction, and
[what the trust model establishes][tbl-what-the-trust-model-establishes]
names, for each one, the party that establishes it, the artifact it rests on,
and how the check runs online and in proximity. The chain codes are those of
[the entity chain and the transaction chain][entity-chain-and-transaction-chain].

[](){ #tbl-what-the-trust-model-establishes }

<figure markdown="1" class="ekdn-table">

| Established | By | Through | Online | In proximity |
|---|---|---|---|---|
| The issuer's identity and its authority to issue this type | Trust Registry and DID Service | Trusted list, Authority Statement, DID Document | E1 to E3 | The next row instead |
| The issuer's signing certificate for an mdoc | The certificate authority at Trust Authority | Document Signer Certificate chained to the Issuer Root CA, the VICAL, the CRL | E4 | E4 |
| The verifier's identity and the attributes it may request | Trust Registry, for an accredited verifier; the RP Intermediary, itself on the trusted list, for a merchant | `did:webvh` plus the trusted list for a Relying Party and an RP Intermediary; the Verifier Device Certificate for a merchant; the Use Statement for the use in hand | T5, in Mobile Wallet | Verifier Device Certificate chained to the Verifier Root CA; the Use Statement in `requestInfo` |
| The wallet installation and the storage of its key | The Wallet Provider | Key Attestation, when `min_assurance` demands one | Checked by Issuer Core at issuance | Not checked; issuance is always online |
| The credential's current validity | The issuer itself | Status list | Read from cache, on a short TTL | Read from cache, up to the tolerance limit |
| The holder's possession of the credential key | The citizen's device | Key Binding JWT (KB-JWT), or DeviceAuth | T3 | T3 |

</figure>

Three things sit outside this trust model, each because somebody else is
answerable for it.

- **Whether the contents of a credential are true.** The trust model proves
  who signed a credential and that the signature holds. Whether the claims
  inside it are correct is the business of the source system the issuer
  copied them from, which the ecosystem depends on and does not govern.
- **Whether a Relying Party's own service trusts its own Verifier Core.** That
  is an internal matter of the Relying Party, settled inside its own systems
  once the Verifier Core has handed over a result.
- **Who the citizen is at the identity provider behind a Mobile Wallet.**
  Identity proofing at sign-in belongs to that provider, and for CONNECTIDN to
  the Badan Siber dan Sandi Negara (BSSN) behind it. The trust model takes
  the authenticated session as given; what it checks is the wallet and its
  key, not the person at the identity provider.

## Chapter contents {#tm-chapter-contents}

1. [Chain of trust](chain-of-trust.md), who accredits whom with no authority
   in between, the two routes a verifier takes to a trust anchor, and the two
   chains every verification has to evaluate
2. [Trusted list and short-lived attestations](trusted-list-and-short-lived-attestations.md),
   what the trusted list answers and how a cached copy of it is trusted, and
   the four signed statements whose limited lifetime does the work of a
   revocation list
3. [Two assurance levels](two-assurance-levels.md), the one scale borrowed
   from eIDAS and the two unrelated questions it answers, about the issuer's
   signing key and about the key on a citizen's device
4. [Keys: who creates, who signs](keys-who-creates-who-signs.md), every key
   in the ecosystem, where it is born, who signs with it, how it is rotated,
   and how each is replaced
