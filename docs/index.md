---
title: Introduction
description: What IDCTF is, the five documents it consists of, and the names already settled.
---

<!-- Sumber: IDCTF-AF — Architecture Framework, §0 -->

# Indonesia Digital Credential Trust Framework

<p class="ekdn-lead" markdown="span">
IDCTF is the name of the framework as a whole: the rules, the accreditation,
the architecture, and the technical specifications that let a digital
credential issued by one institution be trusted by another.
</p>

<div class="ekdn-verstrip" markdown="span">
<span class="dot"></span> Version **0.0.1** &nbsp;·&nbsp; Status: early draft, structure and terminology may still change
</div>

The word *ecosystem* is used throughout these documents as an ordinary noun,
as in the IDCTF ecosystem or an ecosystem participant. It is not a name.

## The five documents

IDCTF is five documents. They are split by the kind of question each answers
and by who is allowed to change it.

| Code | Document | Answers | Who changes it |
| --- | --- | --- | --- |
| `IDCTF-AF` | [Architecture Framework](architecture-framework/index.md) | What and why: roles, Services, Modules, levels, tenancy, trust model, flows | Architects, rarely |
| `IDCTF-TS-nn` | [Technical Specifications](technical-specifications/index.md) | How exactly, in a form that can be tested | The technical team, per version |
| `IDCTF-GF` | [Governance Framework](governance-framework/index.md) | Who decides, what participants owe, what the sanctions are | The Root Authority, through a formal process |
| `IDCTF-CR` | [Credential Rulebook Catalog](credential-rulebook/index.md) | The rules for each credential type | The owner of that credential type |
| `IDCTF-DL` | [Decision Log](decision-log/index.md) | Numbered decisions and their status | The architecture committee |

A version is written with its document code, so `IDCTF-AF-1.0` is a version of
the Architecture Framework and `IDCTF-TS-06-1.2` is a version of one technical
specification.

## Names already settled

Four names are fixed and used consistently across all five documents.

- The wallet on the citizen's phone is a Module called **Mobile Wallet**.
- Credential types are named in the `id.go.credential.<Type>.v<N>` namespace.
- The technical profile that applies across credential types is called the
  **Governance Profile**.
- The three depths of review an authorization request can receive are called
  **Approval Tier A**, **B** and **C**. A tier grades one request and not the
  party that made it. Nobody is a tier A or a tier C participant, and what a
  participant may ask for is set by its accreditation scope alone.

## What is written so far

Only the Architecture Framework is being written. The other four documents
carry their titles and their place in this set, and each page is marked
`(soon)` until its prose exists.
