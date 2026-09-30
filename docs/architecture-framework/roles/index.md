---
title: Roles
description: The eight roles of the ecosystem, what each is responsible for, and the test that decides whether something counts as a role at all.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §2 -->

# Roles {#roles}

<p class="ekdn-lead" markdown="span">
A role is a set of responsibilities. One institution may hold several roles,
and one role may be held by many institutions. This chapter names the roles and
says what each is answerable for; the software behind them is a separate
question.
</p>

Something is a role only if the Root Authority can accredit it, register it,
or recognize it. Measured against that test, there are eight roles. Three of
them govern: they decide who may take part and what they may then do, and they
never touch a citizen's transaction. Five sit on the path a credential
travels, and one of those five, the holder, is held by a person rather than an
institution. Two kinds of box are drawn beside them without being roles at
all: four external systems the ecosystem depends on and does not govern, and
the wallet on the citizen's phone, drawn because every credential passes
through it.

The verifying side is one role and not three. An RP Intermediary and a
merchant are subtypes of Relying Party rather than roles of their own: a
merchant fails the role test, since the Root Authority neither accredits,
registers, nor recognizes it, and an intermediary is accredited as a Relying
Party and nothing further.

Three questions separate the three pages of this chapter, and mixing them
causes most of the confusion about this ecosystem. *What is this party
responsible for* is the role. *What may it issue or request* is the scope of
its accreditation. *Does it answer for itself, or does someone answer for it*
is the difference between a party the Root Authority accredited directly and a
merchant somebody else answers for. A single bank can be a Relying Party, an RP
Intermediary for the merchants it acquires, and an Attribute Issuer for its
account credentials. That is two roles rather than three, because the second
is a subtype of the first, and holding both at once is no contradiction.

The Services that group these responsibilities, and the software that
implements them, are described in
[High-Level Architecture](../high-level-architecture/index.md).

## Chapter contents {#roles-chapter-contents}

1. [Role map](role-map.md), the eight roles, what each is answerable
   for, and the external systems and the citizen's wallet drawn beside them
2. [Three stages of authority](three-stages-of-authority.md),
   registration, accreditation and authorization, and what each one produces
3. [RP Intermediary and merchant](rp-intermediary-and-merchant.md),
   how a business too small to be accredited still verifies a credential
