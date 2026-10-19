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

# Indonesia Digital Credential Trust Framework {#idctf}

A digital credential issued by one institution, accepted by another. Five
documents say what gets built, how it is specified, who may join, what each
credential type requires, and which decisions are already closed.

[Architecture Framework](architecture-framework/index.md){ .md-button .md-button--primary }
[See what is written][what-the-five-documents-hold]{ .md-button }

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

## What IDCTF is {#what-idctf-is}

The Indonesia Digital Credential Trust Framework (IDCTF) is the name of the
framework as a whole: the rules, the accreditation,
the architecture, and the technical specifications that let a digital
credential issued by one institution be trusted by another.

The word *ecosystem* is used throughout these documents as an ordinary noun,
as in the IDCTF ecosystem or an ecosystem participant. It is not a name.

## What the five documents hold {#what-the-five-documents-hold}

IDCTF is five documents. They are split by the kind of question each answers
and by who is allowed to change it.

<figure markdown="1" class="ekdn-table">

| Code | Document | Answers | Who changes it | Progress |
| --- | --- | --- | --- | --- |
| `IDCTF-AF` | [Architecture Framework](architecture-framework/index.md) | What and why: roles, Services, Modules, tenancy, trust model, flows | Architects, rarely | <span class="ekdn-status ekdn-status--written"><span class="dot"></span>Done</span> |
| `IDCTF-TS-g-nn` | [Technical Specifications](technical-specifications/index.md) | How exactly, in a form that can be tested | The technical team, per version | <span class="ekdn-status ekdn-status--written"><span class="dot"></span>Done</span> |
| `IDCTF-GF` | [Governance Framework](governance-framework/index.md) | Who decides, what participants owe, what the sanctions are | The Root Authority, through a formal process | <span class="ekdn-status ekdn-status--written"><span class="dot"></span>Done</span> |
| `IDCTF-CR` | [Credential Rulebook Catalog](credential-rulebook/index.md) | The rules for each credential type | The Credential Rulebook Provider for that type | <span class="ekdn-status ekdn-status--written"><span class="dot"></span>Done</span> |
| `IDCTF-DL` | [Decision Log](decision-log/index.md) | Numbered decisions and their status | The architecture committee | <span class="ekdn-status ekdn-status--todo"><span class="dot"></span>Not started</span> |

</figure>

A version is written with its document code, so `IDCTF-AF-1.0` is a version of
the Architecture Framework and `IDCTF-TS-5-01-1.0` is a version of one technical
specification.

The Architecture Framework, the Technical Specifications, the Governance
Framework and the Credential Rulebook Catalog are done: every page of each
carries prose. The Decision Log is not started. 70 of 71 pages carry prose. A page whose prose is unwritten carries a
`(soon)` marker and holds section headings only.

<p class="ekdn-legend">
<span class="ekdn-status ekdn-status--written"><span class="dot"></span>Done</span> every page has prose and nothing owed is open &nbsp;·&nbsp;
<span class="ekdn-status ekdn-status--drafting"><span class="dot"></span>Drafting</span> pages still being written, or still <code>(soon)</code> &nbsp;·&nbsp;
<span class="ekdn-status ekdn-status--todo"><span class="dot"></span>Not started</span> every page <code>(soon)</code>
</p>

</div>

</div>
