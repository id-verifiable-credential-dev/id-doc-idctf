---
title: Issuers
description: "What an Identity Issuer or Attribute Issuer owes while it is accredited: a reachable endpoint, a sector license in force, a published validity policy, and a channel for a citizen's loss report."
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §2.2, §4.4; tracks/0018, tracks/0135, tracks/0157, tracks/0175, tracks/0178, tracks/0183, tracks/0197, tracks/0367, tracks/0389, tracks/0414; debt/0064, debt/0072, debt/0083, debt/0089 -->

# Issuers {#gf-issuers}

<p class="ekdn-lead" markdown="span">
An Identity Issuer and an Attribute Issuer are accredited once and keep their
place by meeting four duties: staying reachable, keeping the sector license
they registered with in force, publishing how long their credentials last, and
taking a citizen's loss report.
</p>

!!! info "Normative page"

    The rules on this page bind. A participant holding the role a rule names
    is compliant only when it meets it, and an Assessment Body tests it
    against them. The capitalized key words carry the meaning given in
    [RFC 2119][ref-rfc2119] and [RFC 8174][ref-rfc8174]. Each requirement
    carries an identifier, `REQ-GF-nnn`, numbered across the document. A
    number is never reused, and a withdrawn requirement keeps its number,
    marked withdrawn.

## Reachability {#gf-issuer-reachability}

Every issuer runs its own public endpoint for Issuer Core, and an issuer that
cannot expose one does not meet the condition for being an issuer. The
status list is hosted on the issuer's own domain as well, and a reader stops
trusting a copy once its tolerance limit has run out. An issuer whose
status list stays unreachable therefore stops every credential it issued from
verifying, whether or not anyone can still reach its issuance endpoint.

The Root Authority does not measure availability as a percentage. The
Conformance Crawler of Trust Registry fetches the issuer metadata, and
[what is watched][gf-what-is-watched] says when a failed fetch opens an
incident. A breach of this rule is not a suspension by itself, because
suspending an unreachable issuer harms its citizens and adds no protection: its
credentials stop verifying when the status list ages out. The Root Authority
applies the [ladder of sanctions][gf-ladder-of-sanctions] instead.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-127 }**REQ-GF-127** An issuer MUST keep its Issuer Core endpoint reachable from the internet for as long as it is accredited.
- [](){ #req-gf-128 }**REQ-GF-128** An issuer MUST keep the address of each of its status lists reachable from the internet for as long as it is accredited and, after that, until every credential that points into the list has expired, as [REQ-TS-5-09-036][req-ts-5-09-036] requires of a publisher.
- [](){ #req-gf-129 }**REQ-GF-129** An issuer MUST name its Issuer Core endpoint in its [registration][registration].
- [](){ #req-gf-130 }**REQ-GF-130** An issuer MUST file a [post-mortem][gf-post-mortem] for an incident of reachability.
- [](){ #req-gf-131 }**REQ-GF-131** The Root Authority MAY suspend an issuer that leaves an incident of reachability uncorrected, or repeats it, under the [ladder of sanctions][gf-ladder-of-sanctions].
- [](){ #req-gf-132 }**REQ-GF-132** The Root Authority MUST NOT suspend an issuer on the ground of an outage alone.

</div>

## Sector license {#gf-sector-license}

A sector regulator's license is evidence of an Attribute Issuer's standing,
never authority in itself, as the [Attribute Issuer][attribute-issuer] role
sets out. Left alone, that rule has a gap: the license is read once at
registration and nobody learns when the regulator later withdraws it. The gap
closes through the entity. The regulator never suspends anyone. Its act
reaches the trusted list only through the entity's report and a decision of
the Root Authority.

A regulator may narrow a license instead of withdrawing it, for instance by
ending one study program of a university. The Root Authority then withdraws
the permission for the affected credential type and leaves the rest of the
[accreditation][accreditation] standing.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-133 }**REQ-GF-133** An entity that registered with a sector license MUST file a license in force at each renewal of its accreditation.
- [](){ #req-gf-134 }**REQ-GF-134** An entity MUST file a renewed sector license before the one it filed expires, where that license has an end date.
- [](){ #req-gf-135 }**REQ-GF-135** An entity MUST report to the Root Authority, through the Trust Authority portal, that its sector regulator withdrew, suspended, or narrowed its license, within the period the Governance Profile sets as `intervals.license_change_report`, counted from the day the entity is told.
- [](){ #req-gf-136 }**REQ-GF-136** The Root Authority, through Trust Authority, MUST suspend the registration of an entity whose filed license has expired or been withdrawn and that has filed no license in force, until it files one.
- [](){ #req-gf-137 }**REQ-GF-137** The Root Authority MUST withdraw the permission for each credential type a narrowed license no longer covers.
- [](){ #req-gf-138 }**REQ-GF-138** The Root Authority MAY act on a notice from a sector regulator as evidence, in the same way as on the entity's own report.

</div>

## Validity policy {#gf-validity-policy}

How long a credential lasts has two parts. The administrative period comes
from the legal basis in the Credential Rulebook. The technical period, how
long one signed copy verifies, is chosen by the issuer within a ceiling the
Governance Profile sets for each credential type, as [expiry and validity
periods][expiry-and-validity-periods] explains. A Rulebook carries no
technical period ([what a Rulebook does not
carry][what-a-rulebook-does-not-carry]), so [REQ-GF-140][req-gf-140] has the
issuer write its own choice down in its validity policy, where a citizen and
an Assessment Body can read it.

IDCTF issues no batch of credentials, and one credential is presented with
the same key and the same signature each time. The only lever against
linking two presentations is therefore the length of the period, and the
policy says so openly.

Every credential carries a status list entry, whatever its technical period
and whatever its type, as [REQ-TS-5-10-087][req-ts-5-10-087] already
requires. No short-lived exception exists. A loss report works through
suspension, which needs an entry. A leaked signing key is answered by revoking
every credential it signed, and a credential without an entry can only wait
that out.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-139 }**REQ-GF-139** An issuer MUST publish, at the website its registration names, a validity policy for each credential type it issues.
- [](){ #req-gf-140 }**REQ-GF-140** An issuer MUST state in its validity policy, for each credential type it issues, the technical validity period the issuer chooses, within the ceiling the Governance Profile sets for the type as `credential_types.<type>.validity_ceiling`.
- [](){ #req-gf-141 }**REQ-GF-141** An issuer MUST state in its validity policy when the technical period ends at the administrative period instead.
- [](){ #req-gf-142 }**REQ-GF-142** An issuer MUST state in its validity policy the grounds on which the issuer suspends and revokes a credential, and the channels of its [loss reports][gf-loss-reports].
- [](){ #req-gf-143 }**REQ-GF-143** An issuer MUST state in its validity policy that one credential is presented with the same key and signature each time, and which verifiers could link two presentations of it during its technical period.
- [](){ #req-gf-144 }**REQ-GF-144** An Assessment Body MUST check, at accreditation and at each renewal, that the credentials of an issuer carry the periods its validity policy states.
- [](){ #req-gf-145 }**REQ-GF-145** *Withdrawn: stated by [REQ-TS-5-10-087][req-ts-5-10-087].*

</div>

## Loss reports {#gf-loss-reports}

A citizen who loses a phone reports it to the Wallet Provider, which revokes
the installation so that it obtains no further Key Attestation. That stops
new issuance only. A credential already on the lost phone keeps verifying
until its issuer acts, so the citizen has to tell each issuer too, as
[citizen-initiated revocation][citizen-initiated-revocation] shows. The
report runs outside Mobile Wallet, because the phone is gone. It cannot depend
on the phone number held on the device either, because a lost phone usually
takes the SIM card with it and with it any one-time code.

One channel may meet both duties. An in-person counter that closes at night
does not accept a report at all times, and a call center that proves identity
by the phone number held on the device asks for what the citizen no longer has.

Issuer Core keeps the subject pseudonym of each credential in its issuance
record, so an issuer that has established who the citizen is can recompute the
pseudonym and find every credential it issued to that person. The rule needs
no new record.

The first action is suspension, not revocation. Only the issuer suspends a
credential, and a loss report is one of the grounds
[REQ-TS-5-09-123][req-ts-5-09-123] lists. Suspension is the reversible step
while a report is checked: a citizen who finds the phone again has every
suspended credential back and can present it until it expires. The wallet
installation does not come back, because the Wallet Provider revoked it on
the same report and [REQ-TS-2-01-074][req-ts-2-01-074] never returns a revoked
installation to `active`. A credential issued after that comes from a new
installation.

A suspension has an end, though, and [REQ-TS-5-09-124][req-ts-5-09-124]
already caps it at `lifetimes.credential_suspension`. A citizen who has the
credential on a new installation no longer needs the old one.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-146 }**REQ-GF-146** An issuer MUST offer at least one channel for a loss report that needs neither the device that held the credential nor the phone number held on it.
- [](){ #req-gf-147 }**REQ-GF-147** An issuer MUST offer a channel that accepts a loss report at all times.
- [](){ #req-gf-148 }**REQ-GF-148** An issuer MUST establish who the citizen is, on a loss report, by the same means it uses before issuance, or in person against the physical document.
- [](){ #req-gf-149 }**REQ-GF-149** An issuer MUST NOT accept a loss report that it cannot tie to the subject of the credential.
- [](){ #req-gf-150 }**REQ-GF-150** An issuer MUST publish its loss report channels at the website its registration names.
- [](){ #req-gf-151 }**REQ-GF-151** An issuer MUST have Issuer Core set to suspended the entry of every credential it issued to the citizen on the reported installation, or refuse the report and state its reason to the citizen, within the period the Governance Profile sets as `intervals.loss_report_action`, counted from receipt of the report.
- [](){ #req-gf-152 }**REQ-GF-152** An issuer MUST set an entry suspended on a loss report to invalid when the citizen obtains the credential on another installation, or when the time `lifetimes.credential_suspension` fixes runs out, whichever comes first.
- [](){ #req-gf-153 }**REQ-GF-153** An issuer MUST set an entry suspended on a loss report back to valid only when the citizen reports the device found before either of those events.

</div>
