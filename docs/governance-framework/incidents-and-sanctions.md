---
title: Incidents and sanctions
description: How a participant reports an incident, what follows a compromised key, and on what grounds, in what order and with what notice and appeal the Root Authority warns, suspends or withdraws a registration.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §2.2, §6; Rincian Module dan Operasi, §2.4; tracks/0018, tracks/0135, tracks/0136, tracks/0159, tracks/0178, tracks/0304, tracks/0305, tracks/0367, tracks/0389, tracks/0414; debt/0064, debt/0080, debt/0089, debt/0091, debt/0194 -->

# Incidents and sanctions {#gf-incidents-and-sanctions}

<p class="ekdn-lead" markdown="span">
An entity that loses a key tells the Root Authority, and a compromised key costs
the entity that key and not its accreditation. An entity that breaks an obligation
meets a ladder of sanctions, each step narrower than the next, with notice,
a way back, and a right to object.
</p>

!!! info "Normative page"

    The rules on this page bind. A participant holding the role a rule names
    is compliant only when it meets it, and an Assessment Body tests it
    against them. The capitalized key words carry the meaning given in
    [RFC 2119][ref-rfc2119] and [RFC 8174][ref-rfc8174]. Each requirement
    carries an identifier, `REQ-GF-nnn`, numbered across the document. A
    number is never reused, and a withdrawn requirement keeps its number,
    marked withdrawn.

## Reporting an incident {#gf-reporting-an-incident}

Trust Authority's portal already takes a report from a registration whatever
its status ([REQ-TS-4-03-035][req-ts-4-03-035]), and a report revokes nothing
on its own ([incidents and post-mortems][ts-4-03-incidents-and-post-mortems]).
The portal leaves open the clock and the duty to use it. An entity
knows its keys best, so its own report that a key is compromised needs no
further confirmation.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-221 }**REQ-GF-221** An entity MUST report to the Root Authority, through Trust Authority's portal, every key of its own that it learns is compromised or lost, without undue delay and within the period the Governance Profile sets as `intervals.incident_report`, listed in [Intervals][ts-02-intervals].
- [](){ #req-gf-222 }**REQ-GF-222** An entity MUST report in the same way and within the same period any security incident that affects what it issues, presents, or verifies.
- [](){ #req-gf-223 }**REQ-GF-223** The Root Authority MUST treat an entity's report that its own key is compromised as a confirmed compromise on receipt.
- [](){ #req-gf-224 }**REQ-GF-224** An entity MUST NOT rely on a report under this Framework to meet a notification that [UU No. 27 Tahun 2022 tentang Pelindungan Data Pribadi][ref-uu-27-2022] Pasal 46 requires of it.

</div>

## The response to a compromised key {#gf-response-to-a-compromised-key}

A compromised key revokes that key, and the entity stays accredited. The steps,
their order and the time within which the first phase ends belong to
[entity key revocation][entity-key-revocation] and are not restated here. This
section binds the two parties the flow names. Phases that have no fixed target
in the flow stay without one.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-225 }**REQ-GF-225** The Root Authority, through Trust Authority, MUST complete the first phase of [entity key revocation][entity-key-revocation] within the time that flow sets, counted from the confirmation of the compromise.
- [](){ #req-gf-226 }**REQ-GF-226** An entity MUST rotate a revoked key and submit a new certificate signing request on the day the flow sets.
- [](){ #req-gf-227 }**REQ-GF-227** An issuer MUST revoke every credential that a revoked key signed and reissue it as the flow describes.
- [](){ #req-gf-228 }**REQ-GF-228** The Root Authority MUST NOT treat the revocation of a compromised key, or a key incident alone, as a sanction or as a ground for suspension or withdrawal.
- [](){ #req-gf-229 }**REQ-GF-229** The Root Authority MUST handle an unwitnessed log entry as [what a finding starts][gf-what-a-finding-starts] provides.

</div>

## Post-mortem {#gf-post-mortem}

A post-mortem is written to the Transparency Log ([REQ-TS-4-03-040][req-ts-4-03-040]),
so the record outlives the people who wrote it. The clock runs from the
revocation, because the end of an incident is not an event Trust Authority
records.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-230 }**REQ-GF-230** An entity MUST file the post-mortem of an incident that led to a key revocation within the period the Governance Profile sets as `intervals.post_mortem`, counted from the revocation, listed in [Intervals][ts-02-intervals].
- [](){ #req-gf-231 }**REQ-GF-231** The Root Authority MUST treat a failure to report under [reporting an incident][gf-reporting-an-incident] or to file a post-mortem as a ground for a warning.
- [](){ #req-gf-232 }**REQ-GF-232** The Root Authority MUST suspend without a prior warning an entity that conceals a compromise from it.

</div>

## Grounds {#gf-grounds}

A sector regulator's act is evidence for a ground and never a ground itself.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-233 }**REQ-GF-233** The Root Authority MUST decide every warning, suspension, withdrawal, and restoration of a registration.
- [](){ #req-gf-234 }**REQ-GF-234** The Root Authority MUST treat a finding of Conformance Crawler, a signing request that Trust Authority refused, and a report from a participant as an incident to decide on, never as a decision.
- [](){ #req-gf-235 }**REQ-GF-235** The Root Authority MAY ask an Assessment Body for a special assessment of an entity before it decides.

</div>

### Grounds for a warning {#gf-grounds-for-a-warning}

A warning covers breaches that a reader already refuses, so no citizen is
exposed while the entity corrects. The obligations behind each ground live on
the page that binds the role.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-236 }**REQ-GF-236** The Root Authority MUST warn a registration that publishes metadata offering more than its granted scope, as [what is watched][gf-what-is-watched] describes.
- [](){ #req-gf-237 }**REQ-GF-237** The Root Authority MUST warn an issuer whose Issuer Core endpoint stays unreachable as [reachability][gf-issuer-reachability] requires.
- [](){ #req-gf-238 }**REQ-GF-238** The Root Authority MUST warn an entity that does not file or report its sector license as [sector license][gf-sector-license] requires.
- [](){ #req-gf-239 }**REQ-GF-239** The Root Authority MUST warn an RP Intermediary that has not withdrawn a merchant as [withdrawing a merchant][gf-withdrawing-a-merchant] requires.
- [](){ #req-gf-240 }**REQ-GF-240** The Root Authority MUST warn a Wallet Provider that released a build changing code a specification binds before it had filed the report [wallet releases][gf-wallet-releases] requires and had it accepted.
- [](){ #req-gf-241 }**REQ-GF-241** The Root Authority MUST warn a participant that displays a mark, name, or wording against [publishing no more than was granted][gf-publishing-no-more-than-was-granted].
- [](){ #req-gf-242 }**REQ-GF-242** The Root Authority MUST warn a registration that breaches any other obligation this Framework places on its role, unless the breach is a ground for suspension.
- [](){ #req-gf-243 }**REQ-GF-243** The Root Authority MUST name in a warning the ground, the evidence, the correction the Root Authority requires, and the end of the correction period.
- [](){ #req-gf-244 }**REQ-GF-244** The Root Authority MUST set the correction period of a warning to the period the Governance Profile sets as `intervals.correction_period`, listed in [Intervals][ts-02-intervals], counted from the notice.

</div>

### Grounds for suspension {#gf-grounds-for-suspension}

A suspension answers a warning left uncorrected, and the misconduct that
reaches citizens directly. It is a holding state. A suspension left open
would become a sanction by neglect, so it ends in a restoration or a
withdrawal, in the same way that a credential's suspension ends.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-245 }**REQ-GF-245** The Root Authority MUST suspend a registration whose warning was not corrected within the correction period.
- [](){ #req-gf-246 }**REQ-GF-246** The Root Authority MUST suspend a registration without a prior warning when it issued a credential of a type, or asked for an attribute, outside its granted scope or registered uses.
- [](){ #req-gf-247 }**REQ-GF-247** The Root Authority MUST suspend a registration without a prior warning when it breached a data obligation of this Framework or of UU No. 27 Tahun 2022 in a way that exposed citizens' personal data.
- [](){ #req-gf-248 }**REQ-GF-248** The Root Authority MUST suspend a registration without a prior warning when it failed its conformance test at renewal or after a binding change.
- [](){ #req-gf-249 }**REQ-GF-249** The Root Authority MUST suspend a registration without a prior warning when it received a second warning on the same ground within one accreditation period.
- [](){ #req-gf-250 }**REQ-GF-250** The Root Authority MUST suspend a registration without a prior warning when the entity gave false information at registration or since.
- [](){ #req-gf-251 }**REQ-GF-251** The Root Authority MUST suspend a registration when the entity that holds it asks in writing, signed by the person answerable for it.
- [](){ #req-gf-252 }**REQ-GF-252** The Root Authority MUST suspend a registration when a court order, or an order of an authority with legal power over the entity, requires it.
- [](){ #req-gf-253 }**REQ-GF-253** The Root Authority MUST restore or withdraw a suspended registration before the period the Governance Profile sets as `lifetimes.registration_suspension`, listed in [Lifetimes][ts-02-lifetimes], ends.

</div>

### Grounds for withdrawal {#gf-grounds-for-withdrawal}

Withdrawal revokes no key, so what the entity signed while accredited still
verifies ([REQ-TS-4-03-043][req-ts-4-03-043]), unless the Root Authority has
reason to fear backdated credentials, the risk that the trusted list page
names.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-254 }**REQ-GF-254** The Root Authority MUST withdraw an accreditation when the entity asks for it ([REQ-TS-4-03-041][req-ts-4-03-041]), when the entity loses legal standing, or when a suspension reaches its end uncorrected.
- [](){ #req-gf-255 }**REQ-GF-255** The Root Authority MAY withdraw an accreditation without a prior suspension for fraud, or for a ground that repeats after a restoration.
- [](){ #req-gf-256 }**REQ-GF-256** The Root Authority MUST also revoke the keys of an entity whose accreditation it withdraws for misconduct when it has reason to believe the entity may backdate credentials.

</div>

## The ladder of sanctions {#gf-ladder-of-sanctions}

The Architecture Framework's own example of the narrowest sanction is a campus
that mishandles one credential type and loses that one permission, with its
standing untouched. From narrowest to widest the steps are a warning, the
withdrawal of one permission or registered use, suspension of the
registration, suspension of every registration of the legal body, and
withdrawal of the accreditation.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-257 }**REQ-GF-257** The Root Authority MUST choose the narrowest sanction on the ladder that answers the ground.
- [](){ #req-gf-258 }**REQ-GF-258** The Root Authority MUST NOT suspend a registration before the correction period of a warning on the same ground has passed, except on [a ground that allows suspension without a warning][gf-grounds-for-suspension].

</div>

## Suspending every registration of one legal body {#gf-body-wide-suspension}

A suspension reaches one registration, and the Root Authority may extend it
to every registration that carries the same legal identifier. Always doing so would collapse separate
registrations, so the extension needs evidence that the problem is not
confined to one of them.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-259 }**REQ-GF-259** The Root Authority MAY extend a suspension to every registration with the same legal identifier when the entity has lost control over its registrations, through a compromise of the accounts or update keys of more than one of them or of the systems they share.
- [](){ #req-gf-260 }**REQ-GF-260** The Root Authority MAY extend a suspension to every registration with the same legal identifier when the entity has committed fraud.
- [](){ #req-gf-261 }**REQ-GF-261** The Root Authority MAY extend a suspension to every registration with the same legal identifier when an order under [grounds for suspension][gf-grounds-for-suspension] names the entity rather than one registration, or the entity asks for it in writing.
- [](){ #req-gf-262 }**REQ-GF-262** The Root Authority MAY extend a suspension to every registration with the same legal identifier when the misconduct that grounds it shows in a second registration of the same entity.
- [](){ #req-gf-263 }**REQ-GF-263** The Root Authority MUST NOT extend a suspension to every registration with the same legal identifier on a ground other than those of [REQ-GF-259][req-gf-259] to [REQ-GF-262][req-gf-262].

</div>

## Notice of a sanction {#gf-notice-of-a-sanction}

Prior notice is the warning itself, so the Root Authority adds no hearing
step before a suspension.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-264 }**REQ-GF-264** The Root Authority MUST notify the entity of a warning, suspension, withdrawal, or restoration no later than when it takes effect, stating the ground, the evidence, the start, the scope, what ends it, and the objection and appeal available.
- [](){ #req-gf-265 }**REQ-GF-265** The Root Authority, through Trust Authority's Incident Service Component, MUST give notice of a suspension or withdrawal to Relying Parties as organizations, with the emergency trusted list.

</div>

## What each status does to what the entity signed {#gf-effect-of-each-status}

A suspension sets every role service and Verifier Issuing CA service
of the entry to `suspended` ([REQ-TS-5-01-035][req-ts-5-01-035]), turns its
Authority Statement answers to `false` ([REQ-TS-5-05-009][req-ts-5-05-009]) and
sets its accreditation status list entry to suspended
([REQ-TS-5-07-062][req-ts-5-07-062]). A reader then refuses the issuer, so a
suspension in force stops every credential of the issuer, those signed
earlier included. Withdrawal sets the services to `withdrawn` and the entry
to invalid ([REQ-TS-5-07-063][req-ts-5-07-063]), and its Use Statements end
([REQ-TS-5-06-083][req-ts-5-06-083]). For an RP Intermediary, the suspended
Verifier Issuing CA stops every merchant device under it
([REQ-TS-5-01-076][req-ts-5-01-076]).

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-266 }**REQ-GF-266** An RP Intermediary whose registration is suspended MUST NOT issue or renew a Verifier Device Certificate.
- [](){ #req-gf-267 }**REQ-GF-267** The Root Authority MUST say in the notice to an RP Intermediary that its merchants stop with it.

</div>

## Restoration {#gf-restoration}

A restoration sets the status list entry back to valid at the same index and
reissues nothing ([REQ-TS-5-07-064][req-ts-5-07-064]).

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-268 }**REQ-GF-268** The Root Authority MUST restore a suspended registration once the entity has corrected the ground and, where it asked for a special assessment, an Assessment Body report confirms the correction.
- [](){ #req-gf-269 }**REQ-GF-269** An entity whose accreditation was withdrawn for misconduct MUST apply again as a new entity, reviewed at [Approval Tier C][authorization], with an Assessment Body report that addresses the ground of the withdrawal.

</div>

## Objection and appeal {#gf-objection-and-appeal}

The Root Authority is a designated state institution, so its decisions are
government administrative decisions, and
[UU No. 30 Tahun 2014 tentang Administrasi Pemerintahan][ref-uu-30-2014] applies
whether this Framework says so or not. It sets the objection (*keberatan*) and
the appeal (*banding*), with their periods in Pasal 75 to
78. This Framework writes no period of its own, because a second set of days
would sit beside the statute and could contradict it. An Assessment Body's
report is not a decision, so only the Root Authority's decision on it can be
objected to.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-270 }**REQ-GF-270** The Root Authority MUST accept and decide an entity's objection and appeal against a warning, suspension, withdrawal, or restoration decision within the periods and in the form UU No. 30 Tahun 2014 sets.
- [](){ #req-gf-295 }**REQ-GF-295** The Root Authority MUST keep the sanction in force while it decides an objection or appeal, unless it suspends the sanction's effect.

</div>
