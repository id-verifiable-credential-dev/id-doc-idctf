---
title: Governance Framework
description: "IDCTF-GF: who decides, what participants owe, and what happens when they fall short."
---

<!-- Sumber: IDCTF-AF — Architecture Framework, §0, §2.2, §2.4; Glosarium dan Konvensi IDCTF, D.2, D.4, E, F; tracks/0013, tracks/0135, tracks/0288, tracks/0305, tracks/0421 -->

# Governance Framework {#gf-governance-framework}

<p class="ekdn-lead" markdown="span">
<code>IDCTF-GF</code>. Who may recognize whom, what each role owes, and what
follows when those obligations go unmet. Changed by the Root Authority through
a formal process.
</p>

The Governance Framework holds the rules for institutions and people. It says
who decides each question about a participant, what a participant has to show
to join, what it owes for as long as it holds a role, how an Assessment Body
tests it, what happens when it falls short, and on what terms another ecosystem
is recognized. The architecture these rules rest on is in
[Architecture Framework](../architecture-framework/index.md), and the technical
rules each Module meets are in
[Technical Specifications](../technical-specifications/index.md).

**The Governance Framework holds no value of its own.** Every number a rule
needs, a period, a limit, a list of algorithms, an address, is a member of the
Governance Profile, the signed file
[Publishing and reading the Governance Profile](../technical-specifications/publishing-and-reading-the-governance-profile.md)
binds. A rule here says "within the period the Governance Profile sets" and
names the member; the Root Authority sets the value, and
[amendment][gf-amendment] says how. The rules of one credential type are in its
Credential Rulebook, in
[Credential Rulebook Catalog](../credential-rulebook/index.md). Where the three
sit beside each other is in
[The Credential Rulebook][the-credential-rulebook].

Every page of this document is normative. A participant is compliant with
IDCTF only when it meets the obligations of its role here, as
[Common provisions](../technical-specifications/common-provisions.md) states,
and an Assessment Body tests it against them. Each requirement carries an
identifier, `REQ-GF-nnn`, numbered across the document; a number is never
reused, and a withdrawn requirement keeps its number, marked withdrawn. The
capitalized key words carry the meaning given in [RFC 2119][ref-rfc2119] and
[RFC 8174][ref-rfc8174].

The Root Authority is the state institution the regulation establishing IDCTF
designates, and none has been designated yet;
[the Root Authority][gf-the-root-authority] says what follows from that.

## Contents {#gf-contents}

1. [Who decides](who-decides.md)
2. [Assessment and supervision](assessment-and-supervision.md)
3. [Obligations of every participant](obligations/index.md)
    1. [Issuers](obligations/issuers.md)
    2. [Wallet Providers](obligations/wallet-providers.md)
    3. [Relying Parties and merchants](obligations/relying-parties-and-merchants.md)
4. [Incidents and sanctions](incidents-and-sanctions.md)
5. [Recognition](recognition.md)
