---
title: "Software Architecture"
description: How each Module is built, what it divides into, what every implementation is held to, and the technology it runs on.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §6 (SA), §8 (SA), §8.1 -->

# Software Architecture {#software-architecture}

<p class="ekdn-lead" markdown="span">
The earlier chapters say which Modules exist and who runs them. This one opens
a Module and says how it is built: what it divides into, what it may and may
not do, and what it runs on.
</p>

The chapter works at the last of the three tiers the
[Services](../high-level-architecture/services.md) page defines.
A Service groups Modules, and a Module groups Components; here the unit is the
Component. A layer is not a fourth tier. It names what a Component is
responsible for, and one rule orders the layers: each calls only the layer
beneath it, never upward and never skipping one.

This chapter describes software rather than architecture, and it moves to a
document of its own once it is stable, as
[Document Standing][document-standing] records.

## Chapter contents {#sa-chapter-contents}

1. [Layers inside a Module](layers-inside-a-module.md), the four layers of a
   server Module and the pair a console or application Module uses instead,
   what each layer knows, and one request traced through them
2. [Components inside a Module](components-inside-a-module.md), the
   Components of each of the ten Modules and of Trust SDK, grouped by Service,
   with the layer and the standards each one carries
3. [Constraints, decisions, and targets](constraints-decisions-and-targets.md),
   the rules every implementation is held to and why, where data is kept and for
   how long, how each Module scales, and the targets the system is measured
   against
4. [Technology stack](technology-stack.md), the language, database, cache, key
   store, and policy engine behind each building block, how each Module is
   packaged and shipped, and the three risks the stack carries
