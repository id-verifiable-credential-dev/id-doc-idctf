---
title: Roles
description: Who takes part in the ecosystem, what each is responsible for, and what makes each one trusted.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §2 -->

# Roles

<p class="ekdn-lead" markdown="span">
A role is a set of responsibilities. One institution may hold several roles,
and one role may be held by many institutions. This chapter names the roles and
says what each is answerable for; the software behind them is a separate
question.
</p>

The chapter runs on three words that are easy to mistake for one another.
**Institution** is the legal body, and it exists before it ever approaches the
ecosystem. **Entity** is what accreditation produces: a DID, keys and
certificates, a status, and a row in the trusted list. **Role** is the
authority granted to that entity, and one entity may hold several at once.
Section 1 opens with them, because most questions about who may do what turn
out to be questions about which of the three is meant.

There are ten roles. Three of them govern: they decide who may take part and
what they may then do, and they never touch a citizen's transaction. Seven sit
on the path a credential travels, and one of those seven, the Holder, is held
by a person rather than an institution. Two kinds of box are drawn beside them
without being roles at all: four external systems the ecosystem depends on and
does not govern, and one Module, the wallet a citizen installs.

Three questions separate the pages below, and mixing them causes most of the
confusion about this ecosystem. *What is this party responsible for* is the
role. *What may it issue or request* is the scope of its accreditation. *Does
it answer for itself, or does someone answer for it* is the difference between
an accredited entity and a registered merchant. A single bank can be a Relying
Party, an RP Intermediary for the merchants it acquires, and an Attribute
Issuer for its account credentials at the same time without any contradiction.

The Services that group these responsibilities, and the software that
implements them, are described in
[High-Level Architecture](../high-level-architecture/index.md).

## Chapter contents

1. [Section 1, Role map](role-map.md), the ten roles, what each is answerable
   for, and the external systems and Module drawn beside them
2. [Section 2, Three stages of authority](three-stages-of-authority.md),
   registration, accreditation and authorization, and what each one produces
3. [Section 3, RP Intermediary and merchant](rp-intermediary-and-merchant.md),
   how a business too small to be accredited still verifies a credential
