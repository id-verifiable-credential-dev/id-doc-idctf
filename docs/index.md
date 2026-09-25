---
title: Indonesia Digital Credential Trust Framework
description: What IDCTF is, the five documents it consists of, and how much of each is written.
hide:
  - navigation
  - toc
---

<!-- Sumber: IDCTF-AF — Architecture Framework, §0 -->

<div class="ekdn-home" markdown="1">

<div class="ekdn-banner" markdown="1">

<div class="ekdn-hero" markdown="1">

# Indonesia Digital Credential Trust Framework

A digital credential issued by one institution, accepted by another. Five
documents say what gets built, how it is specified, who may join, what each
credential type requires, and which decisions are already closed.

[Read the Architecture Framework](architecture-framework/index.md){ .md-button .md-button--primary }
[See what is written](#progress){ .md-button }

<div class="ekdn-verstrip" markdown="span">
<span class="dot"></span> Version **0.0.1** &nbsp;·&nbsp; Status: early draft, structure and terminology may still change
</div>

</div>

<div class="ekdn-banner__art" aria-hidden="true">
  <svg class="ekdn-graph" viewBox="0 0 400 130" role="presentation" focusable="false">
    <line class="ekdn-graph__edge" style="--i: 1" x1="88" y1="56" x2="172" y2="56" />
    <line class="ekdn-graph__edge" style="--i: 3" x1="228" y1="56" x2="312" y2="56" />

    <circle class="ekdn-graph__node" style="--i: 0" cx="60" cy="56" r="26" />
    <circle class="ekdn-graph__node" style="--i: 2" cx="200" cy="56" r="26" />
    <circle class="ekdn-graph__node" style="--i: 4" cx="340" cy="56" r="26" />

    <g class="ekdn-graph__glyph">
      <rect x="51" y="45" width="18" height="22" rx="3" />
      <path d="M 56 52 h 8 M 56 58 h 8" />
      <rect x="192" y="43" width="16" height="26" rx="4" />
      <path d="M 197 65 h 6" />
      <path d="M 331 56 l 6 7 l 12 -14" />
    </g>

    <g class="ekdn-graph__card">
      <rect x="77" y="49" width="22" height="14" rx="3" />
      <path d="M 82 54 h 9 M 82 58 h 5" />
    </g>

    <text class="ekdn-graph__label" x="60" y="102">Identity Issuer</text>
    <text class="ekdn-graph__label" x="200" y="102">Mobile Wallet</text>
    <text class="ekdn-graph__label" x="340" y="102">Relying Party</text>
  </svg>
</div>

</div>

<div class="ekdn-sections" markdown="1">

## What IDCTF is

IDCTF is the name of the framework as a whole: the rules, the accreditation,
the architecture, and the technical specifications that let a digital
credential issued by one institution be trusted by another.

The word *ecosystem* is used throughout these documents as an ordinary noun,
as in the IDCTF ecosystem or an ecosystem participant. It is not a name.

Three names are fixed and used consistently across all five documents.

- The wallet on the citizen's phone is a Module called **Mobile Wallet**.
- Credential types are named in the `id.go.credential.<Type>.v<N>` namespace.
- The technical profile that applies across credential types is called the
  **Governance Profile**.

## What the five documents hold

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

## Progress

Only the Architecture Framework is being written. Roles and Data Model and
Protocols are done; High-Level Architecture and Software Architecture are part
written. 17 of 57 pages carry prose. A page whose prose is unwritten carries a
`(soon)` marker and holds section headings only.

| Document | Chapter | Status |
| --- | --- | --- |
| `IDCTF-AF` | [Roles](architecture-framework/roles/index.md) | <span class="ekdn-status ekdn-status--written"><span class="dot"></span>Written</span> |
| `IDCTF-AF` | [High-Level Architecture](architecture-framework/high-level-architecture/index.md) | <span class="ekdn-status ekdn-status--drafting"><span class="dot"></span>Drafting</span> |
| `IDCTF-AF` | [Software Architecture](architecture-framework/software-architecture/index.md) | <span class="ekdn-status ekdn-status--drafting"><span class="dot"></span>Drafting</span> |
| `IDCTF-AF` | [Data Model and Protocols](architecture-framework/data-model-and-protocols/index.md) | <span class="ekdn-status ekdn-status--written"><span class="dot"></span>Written</span> |
| `IDCTF-AF` | [Trust Model](architecture-framework/trust-model/index.md) | <span class="ekdn-status ekdn-status--todo"><span class="dot"></span>Not started</span> |
| `IDCTF-AF` | [Module Guides](architecture-framework/module-guides/index.md) | <span class="ekdn-status ekdn-status--todo"><span class="dot"></span>Not started</span> |
| `IDCTF-AF` | [Open Decisions and Technical Debt](architecture-framework/open-decisions-and-technical-debt.md) | <span class="ekdn-status ekdn-status--todo"><span class="dot"></span>Not started</span> |
| `IDCTF-AF` | [References](architecture-framework/references.md) | <span class="ekdn-status ekdn-status--todo"><span class="dot"></span>Not started</span> |
| `IDCTF-TS-nn` | [Technical Specifications](technical-specifications/index.md) | <span class="ekdn-status ekdn-status--todo"><span class="dot"></span>Not started</span> |
| `IDCTF-GF` | [Governance Framework](governance-framework/index.md) | <span class="ekdn-status ekdn-status--todo"><span class="dot"></span>Not started</span> |
| `IDCTF-CR` | [Credential Rulebook Catalog](credential-rulebook/index.md) | <span class="ekdn-status ekdn-status--todo"><span class="dot"></span>Not started</span> |
| `IDCTF-DL` | [Decision Log](decision-log/index.md) | <span class="ekdn-status ekdn-status--todo"><span class="dot"></span>Not started</span> |

<p class="ekdn-legend">
<span class="ekdn-status ekdn-status--written"><span class="dot"></span>Written</span> every page has prose &nbsp;·&nbsp;
<span class="ekdn-status ekdn-status--drafting"><span class="dot"></span>Drafting</span> some pages still <code>(soon)</code> &nbsp;·&nbsp;
<span class="ekdn-status ekdn-status--todo"><span class="dot"></span>Not started</span> every page <code>(soon)</code>
</p>

</div>

</div>
