---
title: Relying Parties and merchants
description: What a Relying Party, an RP Intermediary and a merchant owe, how a merchant is registered, scoped and withdrawn, and what the relay and the merchant may keep.
---

<!-- Sumber: IDCTF-AF — Architecture Framework, §2.2, §2.4; tracks/0024, tracks/0096, tracks/0162, tracks/0177, tracks/0334, tracks/0374, tracks/0410, tracks/0411; debt/0004, debt/0033, debt/0090, debt/0194 -->

# Relying Parties and merchants {#gf-relying-parties-and-merchants}

<p class="ekdn-lead" markdown="span">
A Relying Party asks for credentials under the permissions it was granted. An RP Intermediary does the same on behalf of small businesses, and answers to the Root Authority for each business it registers. This page sets what each of them owes, and what a merchant may do with what it is shown.
</p>

!!! info "Normative page"

    The rules on this page bind. A participant holding the role a rule names
    is compliant only when it meets it, and an Assessment Body tests it
    against them. The capitalized key words carry the meaning given in
    [RFC 2119][ref-rfc2119] and [RFC 8174][ref-rfc8174]. Each requirement
    carries an identifier, `REQ-GF-nnn`, numbered across the document. A
    number is never reused, and a withdrawn requirement keeps its number,
    marked withdrawn.

## Relying Parties {#gf-relying-parties}

A Relying Party is accredited, and its [registered use][registered-use] fixes what it may ask for and why. [Registering and carrying a Use Statement](../../technical-specifications/registering-and-carrying-a-use-statement.md) binds how the use is carried and checked. The Technical Specifications bind how a verifier keeps its verification record and consent receipt. This section adds the organizational duties: a Relying Party stays inside its use, and what it was shown serves that use and the legal duties of its business system.

A Relying Party's own application can keep an attribute value beyond the transaction. Mobile Verifier keeps only the transaction record [REQ-TS-5-11-096][req-ts-5-11-096] lists and no attribute value ([REQ-TS-5-11-092][req-ts-5-11-092]), so the declaration of what is kept belongs to the Relying Party alone, and the citizen's consent screen shows it.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-182 }**REQ-GF-182** A Relying Party MUST ask only for the attributes its permissions and a registered use of its own allow.
- [](){ #req-gf-183 }**REQ-GF-183** A Relying Party MUST keep and delete its verification record and its consent receipt as [REQ-TS-5-11-099][req-ts-5-11-099] requires.
- [](){ #req-gf-184 }**REQ-GF-184** A Relying Party MUST use what it was shown only for the purpose of the registered use under which it asked, and for the legal duties of its business system.
- [](){ #req-gf-185 }**REQ-GF-185** A Relying Party whose own application keeps a data element beyond the transaction MUST declare that element as [REQ-TS-3-02-075][req-ts-3-02-075] requires.

</div>

## RP Intermediary and its merchants {#gf-rp-intermediary-and-merchants}

An RP Intermediary holds the authority of a Relying Party and lends a subset of it to merchants. [What the intermediary takes on][what-the-intermediary-takes-on] describes the role. A merchant is never accredited and never registered by the Root Authority, so the Root Authority holds the intermediary to every rule below, and the intermediary holds each merchant through a written agreement. A breach by a merchant is a breach by the intermediary that registered it.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-186 }**REQ-GF-186** An RP Intermediary MUST answer to the Root Authority for each breach of this section by a merchant it registered, as for a breach of its own.

</div>

### Registering a merchant {#gf-registering-a-merchant}

A merchant is a business with a legal identity: a private business holds a Nomor Induk Berusaha (NIB), and a public body such as a village clinic holds an institution code from the Badan Kepegawaian Negara (BKN), as the same identifiers name any legal body in the [trusted list](../../architecture-framework/trust-model/trusted-list-and-short-lived-attestations.md). A body with neither is not registered. A natural person answers for the merchant, so a citizen who is harmed has someone to turn to, and the agreement carries the duties of [what a merchant does with what it is shown][gf-what-a-merchant-does-with-what-it-is-shown].

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-187 }**REQ-GF-187** Before it registers a merchant, an RP Intermediary MUST establish the merchant's legal identity from its NIB or, for a public body, its BKN institution code.
- [](){ #req-gf-188 }**REQ-GF-188** An RP Intermediary MUST check that identifier against the register that issued it.
- [](){ #req-gf-189 }**REQ-GF-189** An RP Intermediary MUST NOT register a merchant that holds neither identifier.
- [](){ #req-gf-190 }**REQ-GF-190** An RP Intermediary MUST record a natural person answerable for each merchant.
- [](){ #req-gf-191 }**REQ-GF-191** An RP Intermediary MUST establish that the person answerable holds the NIB or is authorized by the body that holds it.
- [](){ #req-gf-192 }**REQ-GF-192** An RP Intermediary MUST bind each merchant to a written agreement before the merchant's first device is activated.

</div>

### A merchant's scope {#gf-merchant-scope}

A merchant asks for less than its intermediary may. The rule has two homes: this section holds the intermediary to it, and the Verifier Device Certificate carries it as a bound a wallet enforces on sight. A use is registered per business category, so one Use Statement serves every merchant of that kind and none is written for a single merchant.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-193 }**REQ-GF-193** An RP Intermediary MUST set each merchant's attribute scope as a subset of the attributes its own permissions and the Use Statements of the merchant's categories allow.
- [](){ #req-gf-194 }**REQ-GF-194** An RP Intermediary MUST NOT give a merchant a scope that carries an attribute of class `restricted`, whatever its own accreditation covers.
- [](){ #req-gf-195 }**REQ-GF-195** An RP Intermediary MUST register a use for each business category it serves.
- [](){ #req-gf-196 }**REQ-GF-196** An RP Intermediary MUST NOT register a use that names a single merchant.
- [](){ #req-gf-197 }**REQ-GF-197** An RP Intermediary MUST bind a merchant device only to categories whose purpose matches the merchant's business.

</div>

### What a merchant does with what it is shown {#gf-what-a-merchant-does-with-what-it-is-shown}

Mobile Verifier sets every `IntentToRetain` to `false` because it keeps no attribute value, only its transaction record, and the citizen's screen says so. A certificate cannot say what a merchant does afterward, so the agreement does. A merchant that has to keep a value, by law or for its business, needs the consent screen that says "kept", which only a Relying Party's own application can raise. Such a business is therefore served as a Relying Party and not as a merchant.

This Framework does not decide who is the personal data controller under [UU No. 27 Tahun 2022 tentang Pelindungan Data Pribadi][ref-uu-27-2022]; the law decides that. What this section settles is that inside IDCTF the intermediary answers for the merchant, whatever the merchant's standing under the law.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-198 }**REQ-GF-198** A merchant MUST use what Mobile Verifier shows only for the purpose of the category under which the request was made.
- [](){ #req-gf-199 }**REQ-GF-199** A merchant MUST NOT copy, photograph, transcribe or otherwise record an attribute value Mobile Verifier shows, into any system, on paper or on another device.
- [](){ #req-gf-200 }**REQ-GF-200** A merchant MUST NOT keep an attribute value once the transaction it was shown for has ended.
- [](){ #req-gf-201 }**REQ-GF-201** A merchant MUST NOT run Mobile Verifier on a device it has modified to capture the screen or the data, or alongside software that does.
- [](){ #req-gf-202 }**REQ-GF-202** A merchant that has to keep an attribute value beyond the transaction MUST NOT serve that need as a merchant.
- [](){ #req-gf-203 }**REQ-GF-203** A merchant MUST tell its RP Intermediary of the loss, theft or misuse of a Mobile Verifier device within the period its agreement sets, which is no longer than the period the Governance Profile sets as `intervals.merchant_withdrawal`, listed in [Intervals][ts-02-intervals].
- [](){ #req-gf-204 }**REQ-GF-204** An RP Intermediary MUST write [REQ-GF-198][req-gf-198] to [REQ-GF-203][req-gf-203] into every merchant agreement.
- [](){ #req-gf-205 }**REQ-GF-205** An RP Intermediary MUST publish a contact through which a citizen can report a merchant it registered.

</div>

### Withdrawing a merchant {#gf-withdrawing-a-merchant}

A merchant's place in the system is its Verifier Device Certificates, so withdrawing a merchant means withdrawing them, as [withdrawing a merchant's certificate][merchant-certificate-withdrawal] shows. The clock runs from the moment the intermediary learns of a ground and not from the first refused request, because one refusal can be a misconfigured template. What keeps knowledge from being put off is the duty to look at the refusals in the relay record.

The Governance Profile sets the period as `intervals.merchant_withdrawal` ([Intervals][ts-02-intervals]). The end-to-end exposure at an offline wallet adds the tolerance for the certificate revocation list, so the intermediary's share is the part it controls.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-206 }**REQ-GF-206** An RP Intermediary MUST withdraw every Verifier Device Certificate of a merchant that asks for an attribute beyond its categories.
- [](){ #req-gf-207 }**REQ-GF-207** An RP Intermediary MUST withdraw every Verifier Device Certificate of a merchant that breaches its agreement.
- [](){ #req-gf-208 }**REQ-GF-208** An RP Intermediary MUST withdraw every Verifier Device Certificate of a merchant that loses its NIB or BKN institution code or ceases business.
- [](){ #req-gf-209 }**REQ-GF-209** An RP Intermediary MUST withdraw every Verifier Device Certificate of a merchant when the Root Authority orders it.
- [](){ #req-gf-210 }**REQ-GF-210** An RP Intermediary MUST have each withdrawn certificate on a published certificate revocation list within the period the Governance Profile sets as `intervals.merchant_withdrawal`, counted from the moment it learns of the ground.
- [](){ #req-gf-211 }**REQ-GF-211** An RP Intermediary MUST examine the refused requests in its relay record at least as often as the Governance Profile's `intervals.crl_publication` ([Intervals][ts-02-intervals]) to decide whether any of them is a ground under this section.
- [](){ #req-gf-212 }**REQ-GF-212** An RP Intermediary MUST report to the Root Authority each withdrawal on a ground other than the merchant's own request, with the ground.

</div>

### The relay record and transport logs {#gf-relay-record}

When a merchant's check goes online, Verifier Core relays it and writes the record [the relay record fields][tbl-ts-3-01-relay-record] list. [REQ-TS-3-01-112][req-ts-3-01-112] allows no other value. A billing field would be the first value not taken from the signed request: the merchant instance, the time and the outcome already let the intermediary count checks per merchant per period. Proximity checks never pass through the relay, so the intermediary bills those by device or by subscription.

The record holds no citizen identifier, but the wallet's network address would link two transactions to one wallet, which [REQ-TS-3-01-098][req-ts-3-01-098] forbids. The address is written by whatever ends the connection in front of Verifier Core, often a hosting or firewall provider, and a Module requirement cannot reach that provider. An organizational duty can, through the intermediary's contract with it. How long the relay keeps the record is the Governance Profile's `lifetimes.relay_record` ([Lifetimes][ts-02-lifetimes]).

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-213 }**REQ-GF-213** An RP Intermediary MUST NOT add a field to the relay record, a billing field included.
- [](){ #req-gf-214 }**REQ-GF-214** An RP Intermediary MUST NOT write a wallet's network address to persistent storage, at its relay endpoints or at any party that carries their traffic for it.
- [](){ #req-gf-215 }**REQ-GF-215** An RP Intermediary MAY hold a wallet's network address in memory for as long as a rate limit or a connection needs it.
- [](){ #req-gf-216 }**REQ-GF-216** An RP Intermediary MUST bind every party that carries relay traffic for it to [REQ-GF-214][req-gf-214] by contract.

</div>

### The merchant inventory {#gf-merchant-inventory}

The Root Authority can see who acts under an intermediary's name only if the intermediary keeps the list. The inventory is the merchant's place in the intermediary's tenant, which the Root Authority may ask for at any time. The Root Authority names the period in which it wants the answer, because that is a decision and not a technical value. An entry outlives the merchant's last certificate for the period the Governance Profile sets as `lifetimes.dispute_period` ([Lifetimes][ts-02-lifetimes]), so a later complaint still finds it.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-gf-217 }**REQ-GF-217** An RP Intermediary MUST keep an inventory of every merchant it registered.
- [](){ #req-gf-218 }**REQ-GF-218** An RP Intermediary MUST record in each inventory entry the merchant's legal name, its NIB or BKN institution code, the person answerable, its categories and scope, each device with the serial number and status of its certificate, and the dates of registration and withdrawal.
- [](){ #req-gf-219 }**REQ-GF-219** An RP Intermediary MUST hand the inventory to the Root Authority on request, within the period the request names.
- [](){ #req-gf-220 }**REQ-GF-220** An RP Intermediary MUST keep an inventory entry for the period the Governance Profile sets as `lifetimes.dispute_period`, counted from the day the merchant's last certificate expired or was withdrawn.

</div>
