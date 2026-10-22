---
title: Wallet Providers
description: What a Wallet Provider files to be accredited, what it owes while it holds the role, how it may disown a wallet installation, and what it owes citizens when it is suspended or withdrawn.
---

<!-- Sumber: Rincian Module dan Operasi, §2.4; Arsitektur Ekosistem Identitas Digital v0.2, §2.2, §2.4; tracks/0018, tracks/0094, tracks/0135, tracks/0157, tracks/0159, tracks/0288, tracks/0305, tracks/0367, tracks/0414; debt/0030, debt/0031, debt/0194 -->

# Wallet Providers {#gf-wallet-providers}

<p class="ekdn-lead" markdown="span">
A Wallet Provider publishes a wallet and vouches that a device and its keys are
genuine.
</p>

!!! info "Normative page"

    The rules on this page bind. A participant holding the role a rule names
    is compliant only when it meets it, and an Assessment Body tests it
    against them. The capitalized key words carry the meaning given in
    [RFC 2119][ref-rfc2119] and [RFC 8174][ref-rfc8174]. Each requirement
    carries an identifier, `REQ-GF-nnn`, numbered across the document. A
    number is never reused, and a withdrawn requirement keeps its number,
    marked withdrawn.

## What a Wallet Provider files {#gf-what-a-wallet-provider-files}

A Wallet Provider is [registered][registration] and [accredited][accreditation]
like any other entity, and files what the [Wallet Provider][wallet-provider]
role adds to that. The attestation roots are not filed: the Technical
Specifications fix them for every Wallet Provider, so one test serves all of
them.

The Mobile Wallet build and Wallet Backend Service are tested by an
Assessment Body before accreditation and at each renewal. Who books the test,
when a changed build needs a new one, and what follows from skipping it are set
under [wallet releases][gf-wallet-releases].

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-154 }**REQ-GF-154** A Wallet Provider MUST name, in its registration, the official build of its Mobile Wallet: the Android package name with its signing certificate digest, and the iOS App ID.
- [](){ #req-gf-155 }**REQ-GF-155** A Wallet Provider MUST name, in its registration, the identity provider its citizens enroll through.
- [](){ #req-gf-156 }**REQ-GF-156** A Wallet Provider MUST file a Key storage evaluation for every key storage component and device model whose Key Attestations will report a value above the floor, as [REQ-TS-4-03-126][req-ts-4-03-126] requires.
- [](){ #req-gf-157 }**REQ-GF-157** A Wallet Provider MUST publish, before it is accredited, its policy for revoking installations, with the content [revoking an installation][gf-revoking-an-installation] sets.
- [](){ #req-gf-158 }**REQ-GF-158** A Wallet Provider MUST publish, before it is accredited, its policy for the personal data it processes under [UU No. 27 Tahun 2022 tentang Pelindungan Data Pribadi][ref-uu-27-2022].
- [](){ #req-gf-159 }**REQ-GF-159** A Wallet Provider MUST distribute the official build only under the developer account its registration names.

</div>

## Obligations while accredited {#gf-wallet-provider-obligations}

Wallet Backend Service is never called by an issuer and publishes no list of
installations ([REQ-TS-2-01-075][req-ts-2-01-075]). A lost phone therefore stops
new issuance to that installation and nothing already on the device.
[REQ-GF-162][req-gf-162] requires the Wallet Provider to tell the citizen this,
because it cannot reach the issuers on the citizen's behalf.

A device may be lost together with its phone number, so the channel to report
the loss cannot depend on either.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-160 }**REQ-GF-160** A Wallet Provider MUST offer every citizen, at all times, a way to report a device lost that needs neither the device nor the phone number held on it.
- [](){ #req-gf-161 }**REQ-GF-161** A Wallet Provider MUST revoke the installation when it accepts a loss report, as [REQ-TS-2-01-072][req-ts-2-01-072] and [REQ-TS-2-01-073][req-ts-2-01-073] require.
- [](){ #req-gf-162 }**REQ-GF-162** A Wallet Provider MUST tell a citizen who reports a loss that the credentials already on the device go on being presented until each issuer is told, and that the Wallet Provider cannot tell the issuers.
- [](){ #req-gf-163 }**REQ-GF-163** A Wallet Provider MUST NOT use the account, the device model, or the moments of enrollment and attestation for anything other than enrolling the installation and attesting its key.
- [](){ #req-gf-164 }**REQ-GF-164** A Wallet Provider MUST report a security breach of a build or of Wallet Backend Service to the Root Authority through the portal within the period the Governance Profile sets as `intervals.incident_report`, which [Intervals][ts-02-intervals] lists and [reporting an incident][gf-reporting-an-incident] applies.

</div>

## Revoking an installation {#gf-revoking-an-installation}

Three kinds of revocation exist and they are kept apart. The citizen's own act,
a loss report or a new enrollment, revokes automatically under the Technical
Specifications and needs no review. The Wallet Provider's own decision is
allowed only on the closed grounds below. A competent authority's order under
Indonesian law is the third.

A revoked installation never returns ([REQ-TS-2-01-074][req-ts-2-01-074]), and
revocation reaches issuance only. A failed check refuses that one request and is
never a ground ([REQ-TS-2-01-070][req-ts-2-01-070]). The Wallet Provider gives
no prior notice, because a compromised key has to stop at once; the notice
follows, within the period the Governance Profile sets as
`intervals.citizen_notice` ([Intervals][ts-02-intervals]). A Key Attestation is
minted for one issuance and not on a schedule, so an installation that asks for
nothing holds none, and the deadline cannot hang on it.

Revocation ends one installation and never the account. A new installation is
enrolled with new keys in the secure element, as a compromised key calls for.
The Technical Specifications give Wallet Backend Service no state in which an
account is barred ([REQ-TS-2-01-009][req-ts-2-01-009]).

The objection below is open against the Wallet Provider's own decision alone. A
Wallet Provider cannot undo a competent authority's order, so a citizen who
disputes one turns to the authority that gave it or to the courts. A citizen
who is not satisfied after the objection below turns to the personal data
protection authority or to the courts. The Root Authority is not an appeal
body: it gives a citizen no account and no access, sees only the aggregate
counts, and acts on the Wallet Provider as an entity. How a
citizen moves to a new installation is described under
[device migration and reissuance][device-migration-and-reissuance].

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-165 }**REQ-GF-165** A Wallet Provider MUST revoke an installation on its own decision only where evidence shows the installation's key or the device's attestation compromised.
- [](){ #req-gf-294 }**REQ-GF-294** A Wallet Provider MUST revoke an installation where a competent authority orders it under Indonesian law, and that revocation is not a decision of its own.
- [](){ #req-gf-166 }**REQ-GF-166** A Wallet Provider MUST NOT revoke an installation on a failed check of a request, on suspicion alone, or on an automated result that no person of the Wallet Provider has reviewed against the evidence.
- [](){ #req-gf-167 }**REQ-GF-167** A Wallet Provider MUST tell the citizen of a revocation on its own decision or on an order, with the ground and its consequence, within the period the Governance Profile sets as `intervals.citizen_notice` from the decision or the order, unless the order forbids it.
- [](){ #req-gf-168 }**REQ-GF-168** A Wallet Provider MUST tell that citizen that the credentials already on the device go on being presented, and that a new installation obtains credentials again from each issuer.
- [](){ #req-gf-169 }**REQ-GF-169** A Wallet Provider MUST let the citizen object to a revocation on its own decision.
- [](){ #req-gf-170 }**REQ-GF-170** A Wallet Provider MUST have a person who did not take the decision review the objection.
- [](){ #req-gf-171 }**REQ-GF-171** A Wallet Provider MUST NOT refuse an account a new installation on the ground of a revocation it made or an order it carried out.
- [](){ #req-gf-172 }**REQ-GF-172** A Wallet Provider MUST record the ground and the decider of each revocation, and the outcome of each objection to it.
- [](){ #req-gf-173 }**REQ-GF-173** A Wallet Provider MUST keep the record of [REQ-GF-172][req-gf-172] with the installation record, for the period [retention][gf-retention] sets for it.
- [](){ #req-gf-174 }**REQ-GF-174** A Wallet Provider MUST report to the Root Authority, at each renewal, the number of revocations it made on each ground, and nothing that identifies a citizen.

</div>

## Suspension of a Wallet Provider {#gf-wallet-provider-suspension}

How a registration comes to be suspended, and what notice that carries, is set
under [the ladder of sanctions][gf-ladder-of-sanctions] and
[notice of a sanction][gf-notice-of-a-sanction]. For a Wallet Provider the
suspended entry stops issuance and renewal to its installations at the issuers'
next sync, and nothing else. Credentials already held keep presenting until
their own expiry or status says otherwise. No verifier sees a Key Attestation,
so a suspension that locked presentation would break offline use.

A citizen therefore needs to know that the wallet will obtain nothing new, and
that another Wallet Provider's wallet is open to them.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-175 }**REQ-GF-175** A suspended Wallet Provider MUST tell every citizen with an active installation, within the period the Governance Profile sets as `intervals.citizen_notice` from the start of the suspension, that the wallet obtains no new credential while the suspension lasts.
- [](){ #req-gf-176 }**REQ-GF-176** A suspended Wallet Provider MUST tell those citizens in the same notice that they may enroll a wallet of another Wallet Provider.
- [](){ #req-gf-177 }**REQ-GF-177** A suspended Wallet Provider MUST keep revoking installations on loss reports.

</div>

## Withdrawal of a Wallet Provider {#gf-wallet-provider-withdrawal}

Withdrawal sets the entry to `withdrawn`. Nothing the Wallet Provider signed
stops verifying, and credentials keep presenting until their own expiry. A
citizen needs time to enroll another wallet and have each issuer issue again.
The citizen also needs the presentation history, which sits as ciphertext in
the backup that Wallet Backend Service runs and that the citizen alone holds
the key to. A departing Wallet Provider owes that export; reading it into
another Wallet Provider's wallet waits on a format no specification fixes yet.

A Wallet Provider that will not renew knows it by the time the accreditation
renewal is prepared, so the same lead is its notice. An accreditation that runs
out without renewal ends the same way a withdrawal on request does
([REQ-GF-078][req-gf-078]). Where the Root Authority withdraws the
accreditation, the Wallet Provider cannot give that notice, and
`intervals.citizen_notice` sets the limit instead.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-178 }**REQ-GF-178** A Wallet Provider that asks to withdraw, or that will not renew its accreditation, MUST tell every citizen with an active installation no later than the period the Governance Profile sets as `intervals.accreditation_renewal_lead` before the withdrawal or the lapse takes effect ([Intervals][ts-02-intervals]).
- [](){ #req-gf-179 }**REQ-GF-179** A Wallet Provider MUST keep attesting active installations until its withdrawal or its lapse takes effect.
- [](){ #req-gf-180 }**REQ-GF-180** A Wallet Provider MUST let each citizen export the encrypted presentation history, with the key that opens it, until its withdrawal or its lapse takes effect.
- [](){ #req-gf-181 }**REQ-GF-181** A Wallet Provider whose accreditation the Root Authority withdraws MUST tell every citizen with an active installation within the period the Governance Profile sets as `intervals.citizen_notice` from the decision.

</div>
