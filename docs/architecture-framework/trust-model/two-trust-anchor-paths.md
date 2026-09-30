---
title: "Two trust anchor paths: DID and X.509"
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §5 (pengantar), §5.2, Kep. 8 -->

# Two trust anchor paths: DID and X.509 {#two-trust-anchor-paths}

Three questions get three different answers, and nothing answers more than one
of them.

- **The trusted list** answers whether an entity is recognized at all.
- **The Authority Statement**, answered over TRQP, answers what that entity may
  do, which is the subject of [Authorization][authorization].
- **The DID Document** answers only whether a signing key really belongs to it.

A DID that is absent from the trusted list is rejected however well its DID
Document resolves. Anyone can make a DID in five minutes; what stops them is
the list. Keeping the three separate, and keeping all of them cacheable, is
what lets verification continue when the parties that publish them are
unreachable.

The third question has two answers rather than one, because a verifier reaches
an anchor by one of two routes. This page sets out both: the DID route, and the
X.509 route that proximity reading obliges every reader to hold as well.

## The issuer side: Issuer Root CA and Document Signer Certificate {#the-issuer-side}

<p class="ekdn-soon">(soon)</p>

## The reader side: Verifier Root CA, Verifier Issuing CA, Verifier Device Certificate {#the-reader-side}

<p class="ekdn-soon">(soon)</p>

## Two parallel roots that never sign each other {#two-parallel-roots-that-never-sign-each-other}

<p class="ekdn-soon">(soon)</p>

## Naming and its ISO/IEC 18013-5 equivalents {#naming-and-its-isoiec-18013-5-equivalents}

<p class="ekdn-soon">(soon)</p>
