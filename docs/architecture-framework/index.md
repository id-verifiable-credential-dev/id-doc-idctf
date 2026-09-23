---
title: "Architecture Framework"
description: "IDCTF-AF, the architecture document: system boundary, roles and entities, module map, data model, trust model, use case flows, and software architecture."
---

# Architecture Framework

<p class="ekdn-lead" markdown="span">
The architecture document for the ecosystem. It draws the line between what is
inside the system and what is outside, names the roles and entities involved,
maps the modules and their dependencies, then works down to components, the
tech stack, and implementation guidance for each module.
</p>

The software architecture that once stood on its own as an SA document is now
part of this one, running from
[Software Architecture](software-architecture/index.md) through
[Module Guides](module-guides/index.md). Rules that bind implementations are
not written here but in
[Technical Specifications](../technical-specifications/index.md); the rules for
joining the ecosystem and what each participant owes are in
[Governance Framework](../governance-framework/index.md).

## Document Standing

This document is IDCTF-AF, the first of the five IDCTF documents to be written.
It declares what gets built: the roles and the institutions that hold them, the
four Services that group their functions, the eleven Modules that implement
those Services, which roles are accredited and which are only registered, the
trust model, and one flow per use case. Architects change it, and rarely.

Software Architecture, Tech Stack and Deployment and Module Guides are on loan.
They describe software rather than architecture, and move to a document of their
own once they are stable. A version of this document is written
`IDCTF-AF-1.0`.

## System boundary

Inside the boundary are the roles on the transaction path and the trust path,
and the software they run. It is a boundary of the system and not of an
organization: one institution may hold several roles, and one role may be held
by many institutions.

Outside it are the four external systems the ecosystem depends on and does not
govern: the source systems an issuer copies from, CONNECTIDN, the device
platforms, and the KMS providers. Each is reached through a fixed
interface, and each is described in
[Section 1.3.1, External systems](roles/role-map.md#131-external-systems).

!!! note "Partly written"
    The Roles and High-Level Architecture chapters carry prose. Every other
    chapter below is a skeleton marked `(soon)`.

## Chapters

- [Roles](roles/index.md)
- [High-Level Architecture](high-level-architecture/index.md)
- [Data Model and Protocols (Overview)](data-model-and-protocols/index.md)
- [Trust Model (Conceptual)](trust-model/index.md)
- [Software Architecture](software-architecture/index.md)
- [Tech Stack and Deployment](tech-stack-and-deployment/index.md)
- [Module Guides](module-guides/index.md)
- [Open Decisions and Technical Debt](open-decisions-and-technical-debt.md)
- [References](references.md)
