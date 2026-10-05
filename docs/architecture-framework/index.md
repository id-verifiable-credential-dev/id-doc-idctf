---
title: "Architecture Framework"
description: "IDCTF-AF, the architecture document: system boundary, roles and entities, module map, data model, trust model, use case flows, and software architecture."
---

# Architecture Framework {#architecture-framework}

<p class="ekdn-lead" markdown="span">
The architecture document for the ecosystem. It draws the line between what is
inside the system and what is outside, names the roles and entities involved,
maps the modules and their dependencies, then works down to components and
the tech stack.
</p>

The software architecture that once stood on its own as an SA document is now
part of this one, as
[Software Architecture](software-architecture/index.md). Rules that bind implementations are
not written here but in
[Technical Specifications](../technical-specifications/index.md); the rules for
joining the ecosystem and what each participant owes are in
[Governance Framework](../governance-framework/index.md).

## Document Standing {#document-standing}

This document is IDCTF-AF, the first of the five IDCTF documents to be written.
It declares what gets built: the roles and the institutions that hold them, the
four Services that group their functions, the ten Modules that implement
those Services, which roles are accredited and which are only registered, the
trust model, and one flow per use case. Architects change it, and rarely.

Software Architecture is on loan. It describes software rather than
architecture, and moves to a document of its own once it is stable. A version of this document is written
`IDCTF-AF-1.0`.

## System boundary {#system-boundary}

Inside the boundary are the roles on the transaction path and the trust path,
and the software they run. It is a boundary of the system and not of an
organization: one institution may hold several roles, and one role may be held
by many institutions.

Outside it are the four external systems the ecosystem depends on and does not
govern: the source systems an issuer copies from, CONNECTIDN, the device
platforms, and the key management service (KMS) providers. Each is reached
through a fixed interface, and each is described in
[External systems][external-systems].

!!! note "Partly written"
    The Roles, High-Level Architecture, and Data Model and Protocols chapters
    carry prose, and so do the Glossary, References, and two sections of
    Software Architecture. The rest of Software Architecture and the whole of
    the Trust Model are skeletons marked `(soon)`.

## Chapters {#chapters}

- [Roles](roles/index.md)
- [High-Level Architecture](high-level-architecture/index.md)
- [Software Architecture](software-architecture/index.md)
- [Data Model and Protocols](data-model-and-protocols/index.md)
- [Trust Model](trust-model/index.md)
- [Glossary](glossary.md)
- [References](references.md)
