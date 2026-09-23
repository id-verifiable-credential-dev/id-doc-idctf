---
title: Network zones and placement
description: The five zones each Module is placed in, who is admitted to each, and why public endpoints and the Admin API never share a door.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §3.3 -->

# 5. Network zones and placement

Every Module sits in one of five network zones, and the zone is what decides
who can reach it. The zones are ordered by exposure. The two applications sit
in the open Internet, and each step inward admits fewer callers, ending in a
zone that admits exactly one.

Read the third column first. It is the one that carries the design, because a
zone is defined by who is let in rather than by where the hardware is.

| Zone | What is in it | Who reaches it |
|---|---|---|
| Internet | Mobile Wallet, Mobile Verifier | Citizens, merchants |
| Public | Issuer Core's OpenID4VCI endpoint, Verifier Core's OpenID4VP endpoint, Trust Registry's TRQP endpoint, Wallet Backend Service's endpoint, the CDN for static artifacts, each issuer's status list | Mobile Wallet, Mobile Verifier, other Core Modules |
| Internal | Issuer Console, Verifier Console, Admin API, Trust Authority (back office and portal), PostgreSQL, Redis, Claims Provider | An operator, over VPN or the office network |
| Secure | KMS, HSM, both offline CA roots | Trust Authority only |
| Closed agency network | Source systems | Claims Provider only, and read-only |

Only protocol endpoints are public. Nothing is placed in the public zone for
convenience, which is why the databases, the Consoles, and the Admin API all
sit one zone further in, and why Trust Authority's portal is internal even
though the entities that use it are not.

The last zone is not the ecosystem's at all. A source system belongs to the
agency that runs it, and the architecture reaches into that network at exactly
one point: Claims Provider, reading and never writing. That is the only
component in the ecosystem that crosses an organisational boundary.

## 5.1 One application, two doors

A Core Module answers two kinds of caller that have nothing in common. A wallet
arrives from the Internet with no credentials of its own; an operator arrives
from the office network already authenticated. Issuer Core and Verifier Core
therefore expose their public protocol endpoint on one ingress and their Admin
API on a separate one.

The separation is what makes the placement enforceable. Without it, the Admin
API would be reachable from wherever the protocol endpoint is reachable, and a
zone boundary that exists only in a diagram is not a boundary.
