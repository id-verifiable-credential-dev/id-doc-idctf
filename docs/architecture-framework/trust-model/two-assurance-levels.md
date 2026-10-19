---
title: "Two assurance levels"
description: The one assurance scale the ecosystem uses and the two unrelated questions it answers, one about the issuer's signing key and one about the key on a citizen's device.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §5.6, §10 butir 15, Kep. 9, 13, 26; Bentuk Data Attestation §2; Rincian Module dan Operasi §4.1, §7 (issuance_record); JWT di OpenID4VCI dan OpenID4VP §0; tracks/0229, tracks/0325, tracks/0386 -->

# Two assurance levels {#two-assurance-levels}

The words `low`, `substantial`, and `high` are the levels of Implementing
Regulation (EU) 2015/1502, which is a legal text rather than a technical
specification. The ecosystem uses the scale in two places that have nothing to do with each other. One grades the key an issuer
signs credentials with. The other grades the key on a citizen's phone that a
credential will be bound to. The two share three words and nothing else, and
anyone who mixes them will read a rule about an issuer's hardware security
module (HSM) as if it were a rule about a citizen's phone.
[The two scales side by side][tbl-two-assurance-scales] sets them apart.

[](){ #tbl-two-assurance-scales }

<figure markdown="1" class="ekdn-table">

| | `issuer_assurance` | `min_assurance` |
|---|---|---|
| Grades | The issuer's signing key | The credential key on the citizen's device |
| The question | How well protected is the key that signs this credential | How well protected must the key be that will hold this credential |
| Set in | The Credential Rulebook demands the level; the Public Key Registry records the `keyStorage` value the issuer's grade follows from | The Credential Rulebook, proposed by the Credential Rulebook Provider and approved by the Root Authority |
| Enforced by | Trust Authority, which writes no Authority Statement for an issuer below it and checks it again at every key registration and rotation | Issuer Core, when it receives a credential request |
| Carried by the protocol as | Nothing; it is a governance matter | `key_attestations_required` in the issuer's metadata |

</figure>

## `issuer_assurance`: the issuer signing key {#issuer-assurance}

An issuer's grade follows from where its signing key lives, and nowhere else.
Key Manager generates every entity key in one of three drivers, and the
driver's `keyStorage` value is submitted with the key and recorded in the
Public Key Registry when the key is registered through the `did:webvh`
witness. [Where an entity key lives][where-an-entity-key-lives] describes the
three drivers, and the Governance Profile sets the grade each one earns in
its [mappings][ts-02-mappings].

<figure markdown="1" class="ekdn-table">

| Grade | Minimum for the issuer's key |
|---|---|
| `low` | `software`, the encrypted keystore built into Key Manager |
| `substantial` | `cloudkms`, a cloud Key Management Service (KMS) |
| `high` | `hsm`, an HSM over PKCS#11 |

</figure>

The `keyStorage` value is not taken on the entity's word. For `hsm`, the
evidence is a statement the HSM signs with a key its manufacturer placed in
it, saying the key was generated inside the device and cannot be exported, and
Trust Authority verifies it against the manufacturer's chain. For `cloudkms`,
it is the same kind of statement where the provider issues one. Where neither
exists, an [Assessment Body][assessment-body] report covering the key ceremony
stands in for it. `software` needs no evidence, because it is the lowest
grade. Whatever the driver, the Assessment Body audits the issuer's key
management at accreditation, since a statement about where a key lives says
nothing about who can reach it.

The grade is read by Trust Authority when it writes an Authority Statement.
A Credential Rulebook names the `issuer_assurance` its type demands. Trust
Authority writes no Authority Statement for an issuer whose driver gives it
less, and Trust Registry answers a permission query for that type
accordingly, so the refusal reaches a wallet from cache like every other
answer. KTP Digital demands `high`, so only an issuer whose key sits in an
HSM can be authorized to issue it. The check
runs again at every key registration and rotation: Trust Authority compares
the `keyStorage` evidence against the grade the entity holds, as the
[rotation flow][how-an-entity-rotates-a-key] shows.

An entity may start on the software driver and move up. The move is an
ordinary rotation, a new key born in the stronger driver, a new log entry,
and a new Document Signer Certificate, and nothing in Issuer Core changes
because the driver sits behind one interface. One key is exempt from the
grade: the `did:webvh` update key may stay in the software driver whatever
driver the signing keys use, for the reason
[where an entity key lives][where-an-entity-key-lives] gives. `keyStorage` is graded for the keys
that sign credentials.

## `min_assurance`: the credential key on a citizen's device {#min-assurance}

A credential type's Rulebook says how well the credential key has to be
protected before a credential of that type may be bound to it. Issuer Core
turns that demand into the standard OpenID for Verifiable Credential Issuance (OpenID4VCI) 1.0 metadata field
`key_attestations_required`, so a wallet reads what proof to send rather
than guessing. The field carries attack-resistance values named after
ISO/IEC 18045:2022, the `iso_18045_*` values of OpenID4VCI Appendix D.2. No
standard says what `substantial` means in those values, so the Governance
Profile sets the mapping, and [the mapping][tbl-min-assurance-mapping] holds
the values it carries. It
follows the attack potential Implementing Regulation (EU) 2015/1502 sets for
each level's authentication mechanism: enhanced-basic for `low`, moderate for
`substantial`, high for `high`. `iso_18045_basic` falls below `low` and is
accepted at no level. At `high` the two values part: key storage has to reach
high, and user authentication moderate or above. A secure element can be
certified against an attacker of high attack potential, but no evaluation has
reached the path a citizen authenticates by, so a demand for high on both
would leave no device able to hold the credential.

[](){ #tbl-min-assurance-mapping }

<figure markdown="1" class="ekdn-table">

| `min_assurance` | `key_attestations_required` the issuer announces | Proof type accepted | Example |
|---|---|---|---|
| `high` | `key_storage: [iso_18045_high]`, `user_authentication: [iso_18045_moderate, iso_18045_high]` | `attestation` only | KTP Digital, SIM |
| `substantial` | `key_storage: [iso_18045_moderate, iso_18045_high]`, `user_authentication` the same | `attestation`, or `jwt` with a `key_attestation` header | A degree certificate, a professional license |
| `low` | `key_storage: [iso_18045_enhanced-basic, iso_18045_moderate, iso_18045_high]`, `user_authentication` the same | `attestation`, or `jwt` with a `key_attestation` header | A membership card, a ticket |

</figure>

At every level the proof the wallet sends carries a
[Key Attestation][key-attestation] from its Wallet Backend Service, either
as the proof itself, the `attestation` proof type of Appendix F.3, or inside
the header of an ordinary proof JSON Web Token (JWT), the `jwt` proof type of
Appendix F.1. Issuer Core checks that the attestation's signer is a Wallet
Provider granted on the trusted list, that its signature verifies against
the key its `kid` names in the Wallet Provider's Decentralized Identifier
(DID) Document and is not named revoked in the provider's trusted list entry,
that the nonce matches and the
attestation has not expired, that the key in the proof is among the
`attested_keys`, and that its `key_storage` and `user_authentication` meet [the mapping][tbl-min-assurance-mapping]. What a
wallet installation may report is a claim about an evaluation rather than
about a brand: a Wallet Provider establishes it per key storage component and
per device model, against a certification under a scheme the Governance
Profile recognizes, and the Key Attestation carries the address of that evaluation.
For high, that certification is a Common Criteria one that includes
`AVA_VAN.5` and whose evaluated scope covers the secure element the key
is generated and held in. The key management software on it need not be in
scope where the platform attests that the key lives there, which a secure
element such as StrongBox or an embedded Universal Integrated Circuit Card (eUICC) holding the key can show
today and a phone's general key store cannot.
The name of a chip or of a key storage interface establishes nothing, and a
certification of key storage does not reach the path a citizen authenticates
by. At `low` any storage
the device platform vouches for at enhanced-basic or above passes, so the
Rulebook lowers the bar without dropping the check that the installation is
genuine. The exchange is
shown in [wallet enrollment and attestation][wallet-enrollment-and-attestation]
and in [the Authorization Code flow][authorization-code-flow].

## One credential, two grades {#one-credential-two-grades}

Two credential types that both demand `high` of the holder may be issued
under different `issuer_assurance`, and two types issued from the same HSM
may demand different things of the holder. The grades are independent, so
Issuer Core records them separately in the `issuance_record` of each
credential: the `key_storage` the Key Attestation reported for the credential
key, and the reference to the signing key, whose `keyStorage` the Public Key
Registry holds. A dispute years later can ask either question on its own.

Both mappings are the Governance Profile's, carried as `issuer_assurance`
and `min_assurance` in its [mappings][ts-02-mappings], and the two tables on
this page hold the values it carries. The issuer of KTP Digital runs an HSM
from the pilot onward, with no exemption while the pilot lasts: a credential
keeps the grade of the key that signed it, and a later move to an HSM would
not raise the grade of what was issued before it.
