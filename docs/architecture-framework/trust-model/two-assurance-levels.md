---
title: "Two assurance levels"
description: The one scale the ecosystem borrows from eIDAS and the two unrelated questions it answers, one about the issuer's signing key and one about the key on a citizen's device.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §5.6, §10 butir 15, Kep. 9, 13, 26; Bentuk Data Attestation §2; Rincian Module dan Operasi §4.1, §7 (issuance_record); JWT di OpenID4VCI dan OpenID4VP §0 -->

# Two assurance levels {#two-assurance-levels}

The words `low`, `substantial`, and `high` come from eIDAS, through
Implementing Regulation (EU) 2015/1502, which is a legal text rather than a
technical specification. The ecosystem borrows the scale and uses it in two
places that have nothing to do with each other. One grades the key an issuer
signs credentials with. The other grades the key on a citizen's phone that a
credential will be bound to. The two share three words and nothing else, and
a reader who mixes them will read a rule about an issuer's hardware security
module (HSM) as if it were a rule about a citizen's phone.
[The two scales side by side][tbl-two-assurance-scales] sets them apart.

[](){ #tbl-two-assurance-scales }

<figure markdown="1" class="ekdn-table">

| | `issuer_assurance` | `min_assurance` |
|---|---|---|
| Grades | The issuer's signing key | The holder's key on the citizen's device |
| The question | How well protected is the key that signs this credential | How well protected must the key be that will hold this credential |
| Set in | The Authority Statement, by Trust Authority | The Credential Rulebook, proposed by the Credential Rulebook Provider and approved by Trust Authority |
| Enforced by | Trust Authority, at accreditation and authorization | Issuer Core, when it receives a credential request |
| Carried by the protocol as | Nothing; it is a governance matter | `key_attestations_required` in the issuer's metadata |

</figure>

## `issuer_assurance`: the issuer signing key {#issuer-assurance}

An issuer's grade follows from where its signing key lives, and nowhere else.
Key Manager generates every entity key in one of three drivers, and the
driver's `keyStorage` value is submitted with the key and recorded in the
Public Key Registry when the key is registered through the `did:webvh`
witness. [Where an entity key lives][where-an-entity-key-lives] describes the
three drivers; the grade each one earns is a candidate for the Governance
Profile, which sets the final mapping.

<figure markdown="1" class="ekdn-table">

| Grade | Minimum for the issuer's key |
|---|---|
| `low` | `software`, the encrypted keystore built into Key Manager |
| `substantial` | `cloudkms`, a cloud Key Management Service (KMS) |
| `high` | `pkcs11`, an HSM |

</figure>

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
[the update key][the-update-key] gives. `keyStorage` is graded for the keys
that sign credentials.

## `min_assurance`: the holder key on a citizen's device {#min-assurance}

A credential type's Rulebook says how well the citizen's key has to be
protected before a credential of that type may be bound to it. Issuer Core
turns that demand into the standard OpenID4VCI metadata field
`key_attestations_required`, so a wallet reads what proof to send rather
than guessing. The field carries attack-resistance values named after
ISO/IEC 18045, the `iso_18045_*` values of OpenID4VCI 1.0 Appendix D.1. No
standard says what `substantial` means in those values, so the mapping is a
candidate for the Governance Profile, and
[the mapping][tbl-min-assurance-mapping] is what the ecosystem proposes.

[](){ #tbl-min-assurance-mapping }

<figure markdown="1" class="ekdn-table">

| `min_assurance` | `key_attestations_required` the issuer announces | Proof type accepted | Example |
|---|---|---|---|
| `high` | `key_storage: [iso_18045_high]`, `user_authentication: [iso_18045_high]` | `attestation` only | KTP Digital |
| `substantial` | `key_storage: [iso_18045_moderate, iso_18045_high]`, `user_authentication` the same | `attestation`, or `jwt` with a `key_attestation` header | A degree certificate, a professional license |
| `low` | Not announced | A plain `jwt` | A membership card, a ticket |

</figure>

At `substantial` and `high` the proof the wallet sends carries a
[Key Attestation][key-attestation] from its Wallet Backend Service, either
as the proof itself, the `attestation` proof type of Appendix F.3, or inside
the header of an ordinary proof JSON Web Token (JWT), the `jwt` proof type of
Appendix F.1. Issuer Core checks that the attestation's signer is a Wallet
Provider granted on the trusted list, that the nonce matches and the
attestation has not expired, that the key in the proof is among the
`attested_keys`, and that its `key_storage` meets the mapping above. A phone
with StrongBox or Secure Enclave meets `iso_18045_high`. At `low` nothing
is announced, the wallet sends a plain proof JWT signed with its credential
key, and Wallet Backend Service is never contacted, which is why issuing a
membership card costs no more ceremony than it is worth. The exchange is
shown in [wallet registration and attestation][wallet-registration-and-attestation]
and in [the Authorization Code flow][authorization-code-flow].

## One credential, two grades {#one-credential-two-grades}

Two credential types that both demand `high` of the holder may be issued
under different `issuer_assurance`, and two types issued from the same HSM
may demand different things of the holder. The grades are independent, so
Issuer Core records them separately in the `issuance_record` of each
credential: the `key_storage` the Key Attestation reported for the holder's
key, and the reference to the signing key, whose `keyStorage` the Public Key
Registry holds. A dispute years later can ask either question on its own.

Neither mapping is final. Which driver earns which grade, and which
`iso_18045_*` values each `min_assurance` announces, are the Governance
Profile's to set, and so is whether the issuer of KTP Digital runs an HSM
from the pilot onward. Read both tables as proposed rather than as settled.
