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

## Chapter contents {#sa-chapter-contents}

1. [Layers inside a Module](layers-inside-a-module.md)
2. [Components inside a Module](components-inside-a-module.md)
3. [Constraints, decisions, and targets](constraints-decisions-and-targets.md)
4. [Technology stack](technology-stack.md)
