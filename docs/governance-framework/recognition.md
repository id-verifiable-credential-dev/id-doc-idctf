---
title: Recognition
description: How the Root Authority recognizes a foreign authority, what IDCTF hands over and receives under the terms, how a replaced anchor is announced, and why the pilot recognizes nobody.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §2.2, §6; tracks/0108, tracks/0135, tracks/0296, tracks/0353, tracks/0305; debt/0051, debt/0109, debt/0115, debt/0174, debt/0208 -->

# Recognition {#gf-recognition}

<p class="ekdn-lead" markdown="span">
Recognition is the Root Authority's decision to let credentials of a foreign
authority be read in IDCTF, for one credential type and one action. What that
authority's ecosystem accepts from IDCTF in return is its own act under the
terms both sign.
</p>

!!! info "Normative page"

    The rules on this page bind. A participant holding the role a rule names
    is compliant only when it meets it, and an Assessment Body tests it
    against them. The capitalized key words carry the meaning given in
    [RFC 2119][ref-rfc2119] and [RFC 8174][ref-rfc8174]. Each requirement
    carries an identifier, `REQ-GF-nnn`, numbered across the document. A
    number is never reused, and a withdrawn requirement keeps its number,
    marked withdrawn.

## What recognition is {#gf-what-recognition-is}

Recognition is an act of the Root Authority, carried out by Trust Authority.
It rests on an agreement between two authorities, because
neither can bind the other's participants alone. IDCTF's side of that
agreement is a one-way statement: for one credential type and one action,
[Trust Registry's recognition answer][ts-4-02-recognition-lifecycle] says the
foreign authority is recognized.

Recognition is per credential type and per action, and a record is never
widened or narrowed ([REQ-TS-4-02-051][req-ts-4-02-051]).

A credential type reaches recognition through the Credential Rulebook Catalog
first. Trust Registry answers `recognized: false` for a type the Catalog does
not register ([REQ-TS-4-02-033][req-ts-4-02-033]), so terms naming a type
nobody has admitted take effect nowhere. The type is admitted the way
[Admission and versions](../credential-rulebook/admission-and-versions.md)
sets out, on a Rulebook a Credential Rulebook Provider proposes, before
Trust Authority records the recognition.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-271 }**REQ-GF-271** The Root Authority MUST decide every recognition of a foreign authority.
- [](){ #req-gf-272 }**REQ-GF-272** The Root Authority MUST NOT recognize a foreign authority except under written terms of recognition agreed with that authority.
- [](){ #req-gf-273 }**REQ-GF-273** The Root Authority MUST name in the terms of recognition the foreign authority, each credential type and each action recognized, and the date the recognition takes effect.
- [](){ #req-gf-274 }**REQ-GF-274** The Root Authority MUST have Trust Authority record one recognition for each authority, action, and credential type the terms name, as [REQ-TS-4-02-049][req-ts-4-02-049] requires.
- [](){ #req-gf-275 }**REQ-GF-275** The Root Authority MUST NOT recognize an action that the `recognition_actions` member of the Governance Profile does not list, which [Closed lists][ts-02-closed-lists] defines.
- [](){ #req-gf-292 }**REQ-GF-292** The Root Authority MUST NOT recognize a foreign authority for a credential type the Credential Rulebook Catalog does not register.

</div>

## What IDCTF hands over {#gf-what-idctf-hands-over}

A foreign wallet trusts an IDCTF reader through the trusted list, and for that
it needs a pointer to the list and the Verifier Root CA to validate the chain
against ([the reader side][the-reader-side]). A foreign reader checks an IDCTF
credential against the Issuer Root CA it takes from the Verified Issuer
Certificate Authority List (VICAL) ([the issuer side][the-issuer-side]). Both
are handed over under recognition, and
[the table of the hand-over][tbl-gf-hand-over] lists what the terms carry.

The statement about the trusted list's signature form closes a gap the list
itself leaves: a foreign reader that expects the form
[ETSI TS 119 602][ref-etsi-ts-119602] V1.1.1 asks for is told that IDCTF signs
a JSON Web Signature (JWS) in the compact serialization instead
([REQ-TS-5-01-049][req-ts-5-01-049]). The Verifier Root CA is handed over as a
certificate and not only as a fingerprint, because nothing publishes it. The
VICAL is handed over as a full address, because the Governance Profile carries
no address for it.

[](){ #tbl-gf-hand-over }

<figure markdown="1" class="ekdn-table">

| Item | What the terms hand over |
|---|---|
| 1 | The `did:webvh` of Trust Authority, which is IDCTF's `authority_id` |
| 2 | The address of the Governance Framework |
| 3 | The address of the Governance Profile |
| 4 | Every distribution point of the trusted list |
| 5 | The statement that the trusted list is a JWS in the compact serialization of [RFC 7515][ref-rfc7515] whose payload is the LoTE JSON document of ETSI TS 119 602, and not the signature form that standard's clause 6.8 asks for |
| 6 | The `did:key` of each trusted list signing key in force |
| 7 | The Verifier Root CA certificate and its SHA-256 fingerprint |
| 8 | The full address of the VICAL |
| 9 | The SHA-256 fingerprint of the Issuer Root CA |

</figure>

Later signing keys of the trusted list follow in the list itself
([REQ-TS-5-01-056][req-ts-5-01-056]), so the terms carry only the keys in
force at the date of effect.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-276 }**REQ-GF-276** The Root Authority MUST hand over in the terms of recognition every item of [the table of the hand-over][tbl-gf-hand-over].
- [](){ #req-gf-277 }**REQ-GF-277** The Root Authority MUST state in the terms of recognition that a reader treats the Issuer Root CA it takes out of the VICAL as a trust anchor only once its SHA-256 fingerprint matches the one handed over.

</div>

## What IDCTF receives {#gf-what-idctf-receives}

IDCTF asks the foreign authority for the same kind of material. A recognition
query names the foreign authority in `entity_id`, by the identifier the terms
fix for it, as a URI. That identifier is the `authority_id` its own ecosystem
publishes as its globally unique identifier under
[Trust Registry Query Protocol (TRQP) v2.0][ref-trqp] section 5.1, which is a
Decentralized Identifier (DID) where that ecosystem uses DIDs. A reader ties a foreign credential to that
authority through the anchor handed over, and through no second identifier
that IDCTF invents ([REQ-TS-4-02-024][req-ts-4-02-024]).

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-278 }**REQ-GF-278** The Root Authority MUST obtain in the terms of recognition the `authority_id` of the foreign authority and the address of the document that governs its ecosystem.
- [](){ #req-gf-279 }**REQ-GF-279** The Root Authority MUST obtain in the terms of recognition the trust anchor to which the foreign authority's issuers of each recognized credential type chain, with its SHA-256 fingerprint delivered through a channel that does not rest on the foreign authority's own signature.
- [](){ #req-gf-280 }**REQ-GF-280** The Root Authority MUST obtain in the terms of recognition the address of the list in which those issuers are published and a contact for incident notices in both directions.
- [](){ #req-gf-281 }**REQ-GF-281** The Root Authority MUST have Trust Authority record each recognition under the `authority_id` the terms name, so that a recognition query for that authority carries it as `entity_id`.
- [](){ #req-gf-282 }**REQ-GF-282** The Root Authority MUST tell each recognized authority, through that contact and within the time the terms set, of a withdrawn issuer, a compromised anchor, and a withdrawn recognition.

</div>

## The channel and a replaced anchor {#gf-the-channel-and-a-replaced-anchor}

An anchor that arrives only inside an IDCTF signature proves nothing, because
the signature is what the anchor exists to check. The hand-over therefore
travels outside anything Trust Authority signs: in the signed terms
themselves, or in the Root Authority's own official publication.

A new fingerprint goes the same way when a root is replaced, and a
Verifier Root CA also needs its new certificate, because no one else publishes
it. Replacement runs by link certificate, and
[how the keys are replaced][how-trust-authoritys-keys-are-replaced] says when
each root changes. The foreign side needs to hold the new anchor before the new
root signs anything that side reads.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-283 }**REQ-GF-283** The Root Authority MUST deliver the items of [the table of the hand-over][tbl-gf-hand-over] in the signed terms of recognition or in its own official publication.
- [](){ #req-gf-284 }**REQ-GF-284** The Root Authority MUST NOT rely on an artifact that Trust Authority signs as the only means of delivering an anchor or a fingerprint.
- [](){ #req-gf-285 }**REQ-GF-285** When a root is to be replaced, the Root Authority MUST announce the fingerprint of the new root to every recognized authority through the channel of the terms, and for the Verifier Root CA the new certificate with it.
- [](){ #req-gf-286 }**REQ-GF-286** The Root Authority MUST make that announcement before the new root signs anything a recognized ecosystem reads, and no later than the start of the lead time the Governance Profile sets as `roots.<root>.lead_time`, which [Roots][ts-02-roots] defines.

</div>

## Withdrawing a recognition {#gf-withdrawing-a-recognition}

A withdrawal reaches readers through the lifecycle
[Recognition lifecycle][ts-4-02-recognition-lifecycle] fixes.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-287 }**REQ-GF-287** The Root Authority MUST withdraw a recognition when the terms end, when the foreign authority's anchor is compromised, or when the foreign authority stops meeting the terms.
- [](){ #req-gf-288 }**REQ-GF-288** The Root Authority MUST have the VICAL drop the root of a withdrawn authority within the time [REQ-TS-5-04-083][req-ts-5-04-083] sets.

</div>

## Scope for the pilot {#gf-recognition-scope-for-the-pilot}

The pilot recognizes nobody. IDCTF publishes the trusted list without a
pointer to another list, as [the scheme
information][ts-5-01-scheme-information] of the trusted list already has it.
[The hand-over][gf-what-idctf-hands-over] is the pointer, and joining a
List of Trusted Lists (LoTL) later is an amendment to this Framework.

An IDCTF reader is required to read in proximity only a credential presented
from a wallet of an IDCTF Wallet Provider.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-289 }**REQ-GF-289** For the pilot, the Root Authority MUST NOT publish a pointer to another list in the trusted list or enter the trusted list in a LoTL of another body.
- [](){ #req-gf-290 }**REQ-GF-290** The Root Authority MUST name, in terms of recognition that require an IDCTF reader to read a wallet of another ecosystem in proximity, that ecosystem and the version of the Technical Specification that requires it.

</div>
