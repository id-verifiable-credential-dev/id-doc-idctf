---
title: "[TS-3-02] Verifying a credential in proximity via ISO/IEC 18013-5"
description: The ISO/IEC 18013-5 profile Mobile Verifier and Mobile Wallet run face to face, from device engagement over a QR code or NFC, through the encrypted BLE session and the signed request, to the response and the end of the session.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §3.4, §4.5, §4.7, §7.4, §9.3, Kep. 19, Kep. 28, Kep. 30; Panduan mdoc §0, §3, §5, §9; Peta Alur Penerbitan dan Presentasi §4.1, §6; ISO/IEC 18013-5:2021 §6.3, §8.2, §8.3, §9.1, Annex D.5; tracks/0078, tracks/0172, tracks/0182, tracks/0362, tracks/0363, tracks/0348, tracks/0349, tracks/0350 -->

<p class="ekdn-docid">TS-3-02</p>

# Verifying a credential in proximity via ISO/IEC 18013-5 {#ts-3-02-verifying-a-credential-in-proximity-via-iso-iec-18013-5}

<p class="ekdn-lead" markdown="span">
A proximity check runs between two phones at a counter, with no network on
either side. This specification fixes how Mobile Verifier and Mobile Wallet
find each other, open the encrypted session, and carry one signed request and
one answer across it.
</p>

Every sentence on this page binds Mobile Verifier, which reads, and
Mobile Wallet, which answers, and an Assessment Body tests them against it in
the version the Governance Profile puts in force. The key words and the
identifier `REQ-TS-3-02-nnn` follow [Common provisions](common-provisions.md).

## Who runs this and what it needs {#ts-3-02-who-runs-this-and-what-it-needs}

This specification fixes the profile of device retrieval under
[ISO/IEC 18013-5:2021][ref-iso-18013-5] that IDCTF runs:

- Device engagement by QR code and by Near Field Communication (NFC).
- The Bluetooth Low Energy (BLE) transport.
- Session establishment and session encryption.
- The handover the SessionTranscript ends in.
- The DeviceRequest and its ReaderAuth.
- The checks Mobile Wallet runs on a request.
- When a DeviceResponse is sent and what it leaves out.
- How the session ends.

Its conformance targets are Mobile Verifier, which is the mdoc reader, and
Mobile Wallet, which is the mdoc. A Relying Party's own application built on
Reader SDK runs the exchange through that library, and the requirements
addressed to Mobile Verifier bind the application as well, except where a
requirement names the application itself.

It leaves to other documents:

- The documents a DeviceResponse carries, its DeviceAuth, the structure of the
  SessionTranscript both are taken over, and the checks a verifier runs on the
  answer, which
  [Building and verifying a presentation](building-and-verifying-a-presentation.md)
  holds.
- The mdoc itself and the checks that reach it, which
  [Issuing a credential in SD-JWT VC, mdoc, and `ldp_vc`](issuing-a-credential-in-sd-jwt-vc-mdoc-and-ldp-vc.md)
  holds.
- The Use Statement in `requestInfo` and the checks Mobile Wallet runs on it,
  which
  [Registering and carrying a Use Statement](registering-and-carrying-a-use-statement.md)
  holds.
- The Verifier Device Certificate, its `ReaderAuthRole`, and the validation of
  the reader chain and of the issuer chain against the Verified Issuer
  Certificate Authority List (VICAL), which
  [Issuing and validating the X.509 certificates and the VICAL](issuing-and-validating-the-x509-certificates-and-the-vical.md)
  holds.
- The trusted list, which
  [Publishing and reading the trusted list](publishing-and-reading-the-trusted-list.md)
  holds.
- The status list form an mdoc reader reads, which
  [Publishing and reading a status list](publishing-and-reading-a-status-list.md)
  holds.
- How stale a cached status list, certificate revocation list (CRL), or VICAL
  may be before a device with no network stops accepting it, which the
  Governance Profile holds.
- [What a merchant may do with what it was shown][gf-what-a-merchant-does-with-what-it-is-shown],
  which the Governance Framework holds.

The profile narrows the standard where it lets an mdoc or a reader choose, and
each narrowing is a requirement below.

Reader authentication, which the standard leaves optional, is required:
Mobile Wallet answers no request that a Verifier Device Certificate did not
sign, because the certificate is where the bound on a merchant lives, as
[a central Relying Party vouching for a small one][verifier-device-certificate-for-a-small-verifier]
sets out. Mobile Wallet always offers engagement by QR code, because an app
on an iOS device in Indonesia cannot act as an NFC tag. It offers device
retrieval over BLE alone and never through a server, because a check in
proximity makes no network call. One session carries one request, so that the
citizen consents to one request whole.

On the reader side the profile asks for what an IDCTF wallet uses:
Mobile Verifier supports both engagement methods, Static Handover, both BLE modes, and
P-256. It recommends the rest of what the standard asks of a mobile driving
license (mDL) reader. Negotiated Handover, NFC device retrieval, and the other
key agreement curves are recommended rather than required,
[REQ-TS-3-02-074][req-ts-3-02-074] among them, because only a wallet outside
IDCTF uses them.

Before the first exchange, each target holds what the rules below assume:

- **Mobile Verifier** holds:
    - Its device key, in the secure element that generated it.
    - The Verifier Device Certificate over that key.
    - The Verifier Issuing CA certificate that issued it.
    - The Use Statements of the uses bound to the device.
    - The Issuer Root CA, from build time.
    - What its [trust cache sync][trust-cache-sync] fetched: the trusted list,
      the VICAL, the Issuer Root CA CRL, and the status lists in Concise Binary
      Object Representation (CBOR) Web Token (CWT) form.
- **Mobile Wallet** holds:
    - Each credential it presents as an mdoc.
    - The credential key, in the device's secure element.
    - The Verifier Root CA, from build time.
    - Trust Authority's self-certifying identifier (SCID), from build time.
    - What its trust cache sync fetched: the trusted list, Trust Authority's
      Decentralized Identifier (DID) log, the Authority Statements on what each
      Relying Party may ask for, the CRL of each Verifier Issuing CA, and the
      Use Statement status list.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-3-02-001 }**REQ-TS-3-02-001** Mobile Verifier MUST meet every requirement on this page that names Mobile Verifier, and every requirement on what Mobile Verifier sends: its request and its session messages.
- [](){ #req-ts-3-02-002 }**REQ-TS-3-02-002** Mobile Wallet MUST meet every requirement on this page that names Mobile Wallet, and every requirement on what Mobile Wallet sends: its engagement, its response, and its session messages.

</div>

## What a proximity check does {#ts-3-02-what-a-proximity-check-does}

The mdoc representation exists for this check, as
[online and offline][online-and-offline] sets out. Everything either side needs
to judge the other is already on the device: Mobile Wallet checks the reader
against the Verifier Root CA and its cached trusted list, and Mobile Verifier
checks the issuer against the Issuer Root CA or its cached VICAL.
[Offline verification][offline-verification] walks the exchange through.

Both signatures of the exchange, ReaderAuth over the request and DeviceAuth
over the answer, are taken over the SessionTranscript, the record of the
engagement and the reader key, so neither can be lifted into another
session.

What the reader may ask for is bounded three times before the citizen sees a
screen: by the permission of the entity that vouches for the device, by the
Use Statement the request carries, and by the `ReaderAuthRole` of the
certificate that signed it.

## The exchange {#ts-3-02-the-exchange}

A proximity check runs in eleven steps.

1. The cashier picks the use the transaction falls under, and Mobile Verifier
   loads its Use Statement.
2. Mobile Wallet generates an ephemeral key pair and shows the
   DeviceEngagement as a QR code, or holds it in a Handover Select message
   for an NFC tap.
3. Mobile Verifier reads the engagement and opens the BLE link in a mode the
   engagement offers. In mdoc central client mode it advertises the
   Universally Unique Identifier (UUID) of the engagement, Mobile Wallet
   connects to it and checks the Ident characteristic it serves; in mdoc
   peripheral server mode Mobile Wallet advertises and Mobile Verifier
   connects.
4. Mobile Verifier generates its own ephemeral key pair on the same curve,
   builds the SessionTranscript, and derives the session keys.
5. Mobile Verifier builds the DeviceRequest, with the Use Statement in each
   `ItemsRequest` and a ReaderAuth over each, and sends it encrypted in the
   SessionEstablishment.
6. Mobile Wallet derives the same session keys from its own SessionTranscript
   and decrypts the request.
7. Mobile Wallet checks each ReaderAuth, the reader chain, the entity's
   permission, the Use Statement, and the `ReaderAuthRole`, and ends the
   session when any document asks for something outside them.
8. Mobile Wallet asks the citizen to approve the request, naming the
   requester from the certificate and the purpose from the Use Statement.
9. Mobile Wallet sends the DeviceResponse encrypted in a SessionData, or, if
   the citizen refused, ends the session without one.
10. Mobile Verifier decrypts the response and checks the credential, the
    issuer chain, DeviceAuth, and the status, all from its cache.
11. Mobile Verifier ends the session, and both sides destroy the ephemeral
    keys and the session keys.

## A proximity check, as exchanged {#ts-3-02-a-proximity-check-as-exchanged}

The citizen, the merchant, the session, and every key are invented, and no
transaction has taken place. Every field is exact.

The examples agree with the pages that show the same parties and artifacts:

- The reader is the phone at Warung Bu Ani, a merchant Terminal Nusantara
  registered, whose Verifier Device Certificate is the one
  [Verifier Device Certificate][ts-5-04-verifier-device-certificate-as-issued]
  shows in TS-5-04.
- The cashier picked the tobacco category, so the request is the age check
  [carrying it in proximity][ts-5-06-carrying-it-in-proximity] publishes in
  TS-5-06.
- The answer is the DeviceResponse
  [an mdoc presentation in proximity][ts-5-11-an-mdoc-presentation-in-proximity]
  shows in TS-5-11, under the SessionTranscript shown there.
- ReaderAuth verifies under the device key that certificate names.
- Both encrypted messages decrypt under
  [the session keys][ts-3-02-the-session-keys], and the ephemeral keys behind
  them are kept with the other keys of the examples.

### Engagement by QR code {#ts-3-02-engagement-by-qr-code}

The citizen opens the wallet and chooses to show a credential. The wallet
draws its ephemeral key and shows this QR code:

``` { .text title="The QR code of the engagement" data-format="URI" }
mdoc:owBjMS4wAYIB2BhYS6QBAiABIVggoyVd9AqbDDyWABXVvTAnoHzPeZLbWl3UkBXRJKuFB1AiWCAgZIcKoEGngJ3pAdfZEtbeUhcSJJKurcOXPQLMODVdLgKBgwIBowD0AfULUEXv73QrLEg3qaOw4dBaaRc
```

The DeviceEngagement it carries offers BLE in mdoc central client mode alone,
with the UUID of the service the reader advertises:

``` { .text title="The DeviceEngagement, in CBOR diagnostic notation" data-format="CBOR diag" }
{
  0: "1.0",
  1: [
    1,
    24(<< {
      1: 2,
      -1: 1,
      -2: h'a3255df40a9b0c3c960015d5bd3027a07ccf7992db5a5dd49015d124ab850750',
      -3: h'2064870aa041a7809de901d7d912d6de5217122492aeadc3973d02cc38355d2e'
    } >>)
  ],
  2: [
    [
      2,
      1,
      {
        0: false,
        1: true,
        11: h'45efef742b2c4837a9a3b0e1d05a6917'
      }
    ]
  ]
}
```

A wallet that also offers mdoc peripheral server mode writes both flags, a
UUID for each mode, and no device address:

``` { .text title="The BleOptions of an engagement offering both BLE modes, in CBOR diagnostic notation" data-format="CBOR diag" }
{
  0: true,
  1: true,
  10: h'c3a6e1f0b2d94f7e8a51d07e6b4f2c19',
  11: h'5f0e9b72a4c84d3a9e17b2c6d8f40a85'
}
```

### The session keys {#ts-3-02-the-session-keys}

The reader draws its own ephemeral key, the `eReaderKey` the SessionEstablishment
carries, and both sides derive the session keys. The shared secret, the salt,
which is the SHA-256 digest of the `SessionTranscriptBytes`, and the two keys:

``` { .text title="The session keys of that session" data-format="hex" }
ZAB       e290fda99502223cc2cedf77c9b6833a2c55f79644e0ca098d7cc6bb18d5161a
salt      c8354e64586d455978b4c2366f8113f55144b4b303c9e28c457a8d1c84f02d7d
SKReader  af5402c2e9f6637487e80756937a2eb833b103a6a3aed6fcb22786aaa8f8b3b8
SKDevice  0f40a856760e685d4e34a384a47dd65d1a740474c6e68acd2ff509912b3e90e7
```

### The DeviceRequest and the SessionEstablishment {#ts-3-02-the-devicerequest-and-the-sessionestablishment}

The DeviceRequest, before encryption. Its one DocRequest carries the
`ItemsRequest` of TS-5-06 byte for byte, and a ReaderAuth whose `x5chain` holds
the Verifier Device Certificate and the Verifier Issuing CA certificate:

``` { .text title="The DeviceRequest, in CBOR diagnostic notation" data-format="CBOR diag" }
{
  "version": "1.0",
  "docRequests": [
    {
      "readerAuth": [
        h'a10126',
        {
          33: [
            h'308202e73082028da003020102020c598bdb20342f8d4489ab2c0f300a06082a8648ce3d040302305b310b3009060355040613024944311b3019060355040a0c125465726d696e616c204e7573616e74617261312f302d06035504030c265465726d696e616c204e7573616e746172612056657269666965722049737375696e67204341301e170d3236303932303030303030305a170d3238303931393030303030305a3042310b3009060355040613024944311b3019060355040a0c125465726d696e616c204e7573616e746172613116301406035504030c0d576172756e6720427520416e693059301306072a8648ce3d020106082a8648ce3d030107034200049ce7b03cec1efb9ed931d6c49125510513596b638aa2c415fdc5b9ebaaa3f5790a37f7e45ae6f792c94eaa3e55e4e52281d4ad740e27f350e6292692793204afa382014e3082014a300c0603551d130101ff04023000300e0603551d0f0101ff04040302078030150603551d250101ff040b3009060728818c5d050106301f0603551d230418301680142ea3b6f5a1d3e7f7f920605effe880a059817933301d0603551d0e041604144b80b91cb6ff7cf1bd5459679a7a0bf748a8bc3a308187060a2b0601040181fd5901010479307730230c0e69642e69646374662e6b74702e3130110c0f757369615f64695f617461735f313730260c156f72672e69736f2e31383031332e352e312e6d444c300d0c0b6167655f6f7665725f313830280c1469642e69646374662e6b617274752d61736e2e3130100c046e616d610c08696e7374616e736930490603551d1f04423040303ea03ca03a863868747470733a2f2f7465726d696e616c2d6e7573616e746172612e636f2e69642f63726c2f76657269666965722d69737375696e672d6361300a06082a8648ce3d0403020348003045022100e141f6697986692fdf2362552c386240a96c730260a26ac6d5618c2b1e09b444022042c8667cd0b56bb733c573071812ab68355aea3f95eec998cb878c53f0022e85',
            h'3082027030820217a003020102020d00b589cdf61b889ebf0a9cce05300a06082a8648ce3d040302305b310b3009060355040613024944312b3029060355040a0c22547275737420417574686f726974792052657075626c696b20496e646f6e65736961311f301d06035504030c16494443544620566572696669657220526f6f74204341301e170d3236303630313030303030305a170d3331303630313030303030305a305b310b3009060355040613024944311b3019060355040a0c125465726d696e616c204e7573616e74617261312f302d06035504030c265465726d696e616c204e7573616e746172612056657269666965722049737375696e672043413059301306072a8648ce3d020106082a8648ce3d0301070342000495417586c5ae06022bb527fddc5f7737dc5cd35218406ecdb33fbc03e115ec8af181663333418f69360c0becfad2c0568d5bee80d0746eeb76bfcf67450f7f7da381bf3081bc30120603551d130101ff040830060101ff020100300e0603551d0f0101ff04040302010630120603551d25040b3009060728818c5d050106301f0603551d2304183016801459c5f043786877c6e2e2a12544a4303d4aee04f3301d0603551d0e041604142ea3b6f5a1d3e7f7f920605effe880a05981793330420603551d1f043b30393037a035a033863168747470733a2f2f72656769737472792e74727573742e676f2e69642f63726c2f76657269666965722d726f6f742d6361300a06082a8648ce3d0403020347003044022021b68922c8baf33517c9f4663ccd551061b18fda5917bab3d04c06684decf346022012cf7f9208f3afb958383fcfaa21f69e1ad92e3b832fd77b1f660299cfaae5ad'
          ]
        },
        null,
        h'7b2856abb1cafe4a1c3916e440d608427b13da9ac64378fd5439fa80be0c9864935599021867a041171aa479a46ba3a3359477159f1c33fa1b7c8a2cfd7fe407'
      ],
      "itemsRequest": 24(<< {
        "docType": "id.idctf.ktp.1",
        "nameSpaces": {
          "id.idctf.ktp.1": {
            "usia_di_atas_17": false
          }
        },
        "requestInfo": {
          "idUseStatement": 'eyJ0eXAiOiJ2bmQuaWQuaWRjdGYudXNlLXN0YXRlbWVudCtqd3QiLCJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDp3ZWJ2aDpRbVpqeTF0OW9GaWFGamhYMmUzOHVNdVI3bWd0ZExqSFBNR2ZqRWZ2cnNtYWlxOnRydXN0LmdvLmlkI3VzZS1zdGF0ZW1lbnQtMSJ9.eyJpc3MiOiJkaWQ6d2Vidmg6UW1aankxdDlvRmlhRmpoWDJlMzh1TXVSN21ndGRMakhQTUdmakVmdnJzbWFpcTp0cnVzdC5nby5pZCIsInN1YiI6ImRpZDp3ZWJ2aDpRbVVBVEM1anlmNXlWeTcyR1lBcDhuU3Z1d3NoekR5NndZWDdXbU5ZNVVKdFhUOnRlcm1pbmFsLW51c2FudGFyYS5jby5pZCIsInVzZV9pZCI6ImthdGVnb3JpLXRlbWJha2F1IiwicHVycG9zZSI6eyJpZCI6IlZlcmlmaWthc2kgdXNpYSBwZW1iZWxpIHByb2R1ayB0ZW1iYWthdSIsImVuIjoiQWdlIHZlcmlmaWNhdGlvbiBmb3IgdGhlIHB1cmNoYXNlIG9mIHRvYmFjY28gcHJvZHVjdHMifSwibGVnYWxfYmFzaXMiOiJQUCAxMDkvMjAxMiBQYXNhbCAyNSBodXJ1ZiBiIiwiY2xhaW1zIjpbImlkLmlkY3RmLmt0cC4xI3VzaWFfZGlfYXRhc18xNyIsIm9yZy5pc28uMTgwMTMuNS4xLm1ETC4xI2FnZV9vdmVyXzE4Il0sInN0YXR1cyI6eyJzdGF0dXNfbGlzdCI6eyJpZHgiOjgxMiwidXJpIjoiaHR0cHM6Ly9yZWdpc3RyeS50cnVzdC5nby5pZC9zdGF0dXMvdXNlLXN0YXRlbWVudHMtMSJ9fSwiaWF0IjoxNzc2NDcwNDAwLCJleHAiOjE4MDgwMDY0MDB9.Jji2ue0AO4C-NpZbZ8ttzs7DsqWLTZbm2JGAsDw7Utb_ctPZUVZxFXeH-xTm0e7LxrSfq0Mhw24vHfu3yFcDzA'
        }
      } >>)
    }
  ]
}
```

It travels encrypted under `SKReader` with the reader's first counter, inside
the SessionEstablishment:

``` { .text title="The SessionEstablishment, as sent" data-format="CBOR hex" }
a26464617461590a79b5982a9df2ce2e4b027533f2339923fdd9136de8d32eae14394cdca30b
a971996de2aa9e2df52a7d0cf92eec275f895da014757c80d464f5e8acc8a6c164e2990bbc8f
621061c4decdf984e0df51d1be5f023956420a5f8462ff651c50cc5f5ca7738b95fb3894fa79
4c09cefd32181ee30c7e56447d4ec5e407196f8a606efb1c0ee9f29f4fb1880ad547869ffc49
a5fbe19454b1fefd8d4509652aeaf0b29ca610d2f40635815aa9393bcef828abdae33168d152
8d025aa8d18b891f7d2f15296ffc47906abc57d0703a0844ecf816a17eb854f0b9166a56bcb9
e3c436370c30c52bdf3dc1f07d46e8d051665322f065dda6c044679883835dcd5014274d76da
bf5dafd3d1a56a638aa72db9b44a9fef76cffa2782ded3f5def7e80046fc22229781cffc0fe4
c95c4a9c6fe852177c1c894064224b9edc92d2d283079e4ccf3c0431726d48ba1ed5ff9e89f2
be0299c42bfe35e6c8ae1dda5e263f7b22d239fc17461c36ca7aa010cdf6cfcd418d59ff10c3
2a53f8f389b96085cf22ada939524231ef42ccf5738b1c86f395063de1f5a119d571386c1248
85c645492ee6fac0404aea8a6c5212287b46094d46ec18d8ea5956c7393c8463cf8b04375449
25d0021033b9f0e7264502ae425fcb753142102fb25fae50aef85b53fd8436bc53d83577655f
dc1c843a3498c212742f9cbc6d8eafde84a259bf7b74ac741233bc9079762953620516c0815e
4e3ebfaeb1dda97c411c07c7d3015abcdc3cc8aad7011fc7cd6e51a130056c43a2f0fb593df8
433f1fd5f05eebba1f2fbc9841ed7c8cc16b7bbdb97dbc1aeba42c3ae17f70325c1b9fe12417
0eb9c6120704801173a625d06962a4f358ad7ac77b169926bb5b2731db88bc54fb2af81ca7da
6fc631ebf425ce59e767218f31245777be3fbc3c4054a4a7b1e7997bbaa66a22db5529855420
114c1d0142c9554ffb36610fa3d63a866c5ba011b991698b94ae07b6e7da3e550a964a5eb698
f8d3e8ca67a3747530eb32eaa2577b1c0a6d1c42d4df106e6fef02291cbe9551a9ca4915e8e4
a6be4d1ee8a99a37672143e2716d46152eb81c8503c726e70ebdf8f2658ac8a2fbbc2da1e16e
fac075ba5f942ead016680f50aa1a31202cc9c23e3b4c0efd6e640dda33c4db6e384b54e4865
32239be1b9b1b8a342f146997752ee4386a74c418aafff61f47fdf57f6a58df0444d3b837d15
681858a9630d3102598868986d06bd37d39cd7cb188a7e694da156b3acbe1edfe40f411d0410
3ceed86f11b1971f53ece9d85e86bc010e81264acf71c9b5f6830f0db5d60162667c8bb38c2b
6463a2df2a146a8fea2aa4397b2b1c5a5eb9908cd328796a66e15e6852790a6808b4aa6e7f11
f98c489626aaa5d57fca825a6f69f1766702779da7b7bc4ded363127666f51f531237a390f2f
90384cf0471a19b13a3fd2855d27724ceeb706cbd1b307d724dafbdeb2481864ff40b02b244d
a71be46552eb290fc0382741c46ca1f77cd4088d4948006f73df1076e08ab398fc5e4271c141
1b3a8b3bb33431be8049f3284a4cba8c0e5b1d5c2f81773e27528b3d9598591a2cd0934a263b
1e9aac971fd0011959039786313ae8f109a9be01e095f0b3b5e554ca5b1153876a1c61333687
69fd5769d6991f8302bdb180bae9cf438c83f1f9112c891565ef1e4db9e6b6113c33a65b734b
ff5df78bdeb8f4e570648d5919037bd262ff97941b9bb73d8880306b20e97fd8c1653b40aedf
1eaecada7f1579b9697a3dae200310ef9be35e7280392c1ed713b6c93d22b618725171760cf0
bc079dd7e05802aa3e7b9cd0f071502f697226cade2836adc10c764117579f600d2b88a83b73
ae1fd73f2c77bb60661ee797f9071644b04ebe69797b1a23a212da50fc666a28981731addb1e
c54c9f43dc2591f0de0859b6fca39bd296349513a012b42452a5bea93da221ef9ac67aee0976
ae5a9a337e1316eb7b852f04b370c4520cf86617410a8fb71a44fadf6f68e561283ff83de521
68c33c10eb7f59c82b88493c5e99e0edb7a48fdc76ca320cb29bfd34b9789f8fbefa6dabfe00
193cbce3927416bc81408bdfafdd46fbac700bb33d5ac04901950e8eb95aa249f2bf0be36b9f
8f14d2eb4b47dc3bfe45cd62a4b0b337f9d2171a6e459a66e3ed131b4b69421a34de0c162727
d0b9c8a82ff7c84a21766e787f19a5ee6ecffac4b2b4b9939d47a0d547a0c626f3b7fc108617
1d866231fcd3752cc0cfc4fc0c91ffaa61158708b8622a90cbef6318843e535939d8c6849543
790e68248edca6bee24d4f38c4e6a6cade4bf0146b292862cadc84b8661aa04a21e15f1844f7
f4c51fda035ec861d61f1d17366c528306628973f2151658844b905a09b4f0b8094ddffb7fa5
c9857e356b8d42a8fab1ab1a234fe8ace6db7aaf4de17bae68e0e2498421f9d9957e8a11d520
5f2648acbe21d6556e1b5a7e7463a8b8b2c0e4ab1df3fb712a41f91f833ca8b3d2994a5ce11f
d879065be795925fb894555ddf1e530d78f6728c4f4672b46ea3ec7dcd5064ed5df178b44d5e
eb614fe4272011964b20edfc52627aed02b6e9a371fd136c164b1edde07554b6bf3b45c439ce
c4746b645a7edbcd78467fb3a5a194775b1728fd0c6305610faba2149604f9ae7d59fe134984
23d35a019208482eca7d41bccdc72e5fcc9a24932875ffc1db69b82b59c101ecd966a708de9c
15fa79f70f081808a91e92bdac8eb56883912b0ab33f09cee1d31ba5a8d988dfbe429cf8c988
a8cd7b5ae73b6ef5de413fc8b6e32055afb63eac8628850c16af71d5caa3cf31ed2da1b66c33
032005036a72dd099f0e5564b7d9c6e54ace8ca0c3e02498727b5712aedecce981b6c6f4aac8
9378a10c6c3523a0ac1d011eee6e1d9ebd7fcb3a3d976ec5f51065478eb201ffce34ede31aa9
ec2893914987cb3cb8098af245ac0d79722c3d76bc0c47f43524ff43a01d19b6f563a0f6b80b
454c764b4ad61e6fc580c100f3dfd3d172b93e5444a2995f23e43c9355982879d81306e5e45d
75df69a11191fc7420270dfaf79c3b75058001d8fb0a93cc048fa9f2200e97006e694c7fd7e4
e110e1f5f75a9a7c28ae689484bc7549b95a6826812138d17e622aeb38dd7301f1949b94d6d2
76585324b21b37e9e0d436b88746c4c072a1c7f3c0d47a8cbce984b664f9a92f86c3b5671c8a
e3fbfc23a24cd2fdc37feaa1a6758ea5a85580ae17587bbe366f10d7cfe3720d163312075d1c
6bbad8939a2c07989e2d1da075521fa3db77586f4383020392cb14503f14326a1b70ffda2a91
71ee2838e729bf2346ce763d73ef0a41465b3398778e0d5024cf95acc853b7679bebb1e8020c
fe4c3ea26a4e1bc7dbafe120757c7046d7a6f770789832edfc9374143579e9887ed2a362a1e4
a4ea33691185b079870b8e427fc7375191615172c9b2591b8d0daff003f1da9b320b6c54bbc9
9e2f9b4b3ab2d24c9b15157b789bccea193b57483f6dd33f3aa92e472ebadd8a74302814c1ef
205d7af8bb4eb687861e1d6c614c5a1839b9a690e40a763ddd69b1151a56830eaae2e31c5fe4
af9966ca62abc48e674c03a4cfbced4917ad3fc6e13e7e98bb8faeac1a3899141a716521a44a
2a01dbf1eaebf7b5c61681537e1956ff1b7957d8e34793137cc09c0ad0829ddda28b72959745
efbeb71f4e1734dc6979a3fdd2b0497d30714817cd3112066a6f466f8db95c565e26a80fcea5
858c05ca27ef08ffb25cd3484e0b4a45836cfd6a83821a681963e2bbf21e6a65526561646572
4b6579d818584ba40102200121582060ed1de1facf2443f8f4d2e3692ee956e4956034f71223
8ffaa5a6017534a279225820d0d3ab6943faa692262db0f90c2218a8fa4cce2c521fae0a54c5
6b8b1b7a928a
```

``` { .text title="The SessionEstablishment, in CBOR diagnostic notation" data-format="CBOR diag" }
{
  "data": h'b5982a9df2ce2e4b027533f2339923fdd9136de8d32eae14394cdca30ba971996de2aa9e2df52a7d0cf92eec275f895da014757c80d464f5e8acc8a6c164e2990bbc8f621061c4decdf984e0df51d1be5f023956420a5f8462ff651c50cc5f5ca7738b95fb3894fa794c09cefd32181ee30c7e56447d4ec5e407196f8a606efb1c0ee9f29f4fb1880ad547869ffc49a5fbe19454b1fefd8d4509652aeaf0b29ca610d2f40635815aa9393bcef828abdae33168d1528d025aa8d18b891f7d2f15296ffc47906abc57d0703a0844ecf816a17eb854f0b9166a56bcb9e3c436370c30c52bdf3dc1f07d46e8d051665322f065dda6c044679883835dcd5014274d76dabf5dafd3d1a56a638aa72db9b44a9fef76cffa2782ded3f5def7e80046fc22229781cffc0fe4c95c4a9c6fe852177c1c894064224b9edc92d2d283079e4ccf3c0431726d48ba1ed5ff9e89f2be0299c42bfe35e6c8ae1dda5e263f7b22d239fc17461c36ca7aa010cdf6cfcd418d59ff10c32a53f8f389b96085cf22ada939524231ef42ccf5738b1c86f395063de1f5a119d571386c124885c645492ee6fac0404aea8a6c5212287b46094d46ec18d8ea5956c7393c8463cf8b0437544925d0021033b9f0e7264502ae425fcb753142102fb25fae50aef85b53fd8436bc53d83577655fdc1c843a3498c212742f9cbc6d8eafde84a259bf7b74ac741233bc9079762953620516c0815e4e3ebfaeb1dda97c411c07c7d3015abcdc3cc8aad7011fc7cd6e51a130056c43a2f0fb593df8433f1fd5f05eebba1f2fbc9841ed7c8cc16b7bbdb97dbc1aeba42c3ae17f70325c1b9fe124170eb9c6120704801173a625d06962a4f358ad7ac77b169926bb5b2731db88bc54fb2af81ca7da6fc631ebf425ce59e767218f31245777be3fbc3c4054a4a7b1e7997bbaa66a22db5529855420114c1d0142c9554ffb36610fa3d63a866c5ba011b991698b94ae07b6e7da3e550a964a5eb698f8d3e8ca67a3747530eb32eaa2577b1c0a6d1c42d4df106e6fef02291cbe9551a9ca4915e8e4a6be4d1ee8a99a37672143e2716d46152eb81c8503c726e70ebdf8f2658ac8a2fbbc2da1e16efac075ba5f942ead016680f50aa1a31202cc9c23e3b4c0efd6e640dda33c4db6e384b54e486532239be1b9b1b8a342f146997752ee4386a74c418aafff61f47fdf57f6a58df0444d3b837d15681858a9630d3102598868986d06bd37d39cd7cb188a7e694da156b3acbe1edfe40f411d04103ceed86f11b1971f53ece9d85e86bc010e81264acf71c9b5f6830f0db5d60162667c8bb38c2b6463a2df2a146a8fea2aa4397b2b1c5a5eb9908cd328796a66e15e6852790a6808b4aa6e7f11f98c489626aaa5d57fca825a6f69f1766702779da7b7bc4ded363127666f51f531237a390f2f90384cf0471a19b13a3fd2855d27724ceeb706cbd1b307d724dafbdeb2481864ff40b02b244da71be46552eb290fc0382741c46ca1f77cd4088d4948006f73df1076e08ab398fc5e4271c1411b3a8b3bb33431be8049f3284a4cba8c0e5b1d5c2f81773e27528b3d9598591a2cd0934a263b1e9aac971fd0011959039786313ae8f109a9be01e095f0b3b5e554ca5b1153876a1c6133368769fd5769d6991f8302bdb180bae9cf438c83f1f9112c891565ef1e4db9e6b6113c33a65b734bff5df78bdeb8f4e570648d5919037bd262ff97941b9bb73d8880306b20e97fd8c1653b40aedf1eaecada7f1579b9697a3dae200310ef9be35e7280392c1ed713b6c93d22b618725171760cf0bc079dd7e05802aa3e7b9cd0f071502f697226cade2836adc10c764117579f600d2b88a83b73ae1fd73f2c77bb60661ee797f9071644b04ebe69797b1a23a212da50fc666a28981731addb1ec54c9f43dc2591f0de0859b6fca39bd296349513a012b42452a5bea93da221ef9ac67aee0976ae5a9a337e1316eb7b852f04b370c4520cf86617410a8fb71a44fadf6f68e561283ff83de52168c33c10eb7f59c82b88493c5e99e0edb7a48fdc76ca320cb29bfd34b9789f8fbefa6dabfe00193cbce3927416bc81408bdfafdd46fbac700bb33d5ac04901950e8eb95aa249f2bf0be36b9f8f14d2eb4b47dc3bfe45cd62a4b0b337f9d2171a6e459a66e3ed131b4b69421a34de0c162727d0b9c8a82ff7c84a21766e787f19a5ee6ecffac4b2b4b9939d47a0d547a0c626f3b7fc1086171d866231fcd3752cc0cfc4fc0c91ffaa61158708b8622a90cbef6318843e535939d8c6849543790e68248edca6bee24d4f38c4e6a6cade4bf0146b292862cadc84b8661aa04a21e15f1844f7f4c51fda035ec861d61f1d17366c528306628973f2151658844b905a09b4f0b8094ddffb7fa5c9857e356b8d42a8fab1ab1a234fe8ace6db7aaf4de17bae68e0e2498421f9d9957e8a11d5205f2648acbe21d6556e1b5a7e7463a8b8b2c0e4ab1df3fb712a41f91f833ca8b3d2994a5ce11fd879065be795925fb894555ddf1e530d78f6728c4f4672b46ea3ec7dcd5064ed5df178b44d5eeb614fe4272011964b20edfc52627aed02b6e9a371fd136c164b1edde07554b6bf3b45c439cec4746b645a7edbcd78467fb3a5a194775b1728fd0c6305610faba2149604f9ae7d59fe13498423d35a019208482eca7d41bccdc72e5fcc9a24932875ffc1db69b82b59c101ecd966a708de9c15fa79f70f081808a91e92bdac8eb56883912b0ab33f09cee1d31ba5a8d988dfbe429cf8c988a8cd7b5ae73b6ef5de413fc8b6e32055afb63eac8628850c16af71d5caa3cf31ed2da1b66c33032005036a72dd099f0e5564b7d9c6e54ace8ca0c3e02498727b5712aedecce981b6c6f4aac89378a10c6c3523a0ac1d011eee6e1d9ebd7fcb3a3d976ec5f51065478eb201ffce34ede31aa9ec2893914987cb3cb8098af245ac0d79722c3d76bc0c47f43524ff43a01d19b6f563a0f6b80b454c764b4ad61e6fc580c100f3dfd3d172b93e5444a2995f23e43c9355982879d81306e5e45d75df69a11191fc7420270dfaf79c3b75058001d8fb0a93cc048fa9f2200e97006e694c7fd7e4e110e1f5f75a9a7c28ae689484bc7549b95a6826812138d17e622aeb38dd7301f1949b94d6d276585324b21b37e9e0d436b88746c4c072a1c7f3c0d47a8cbce984b664f9a92f86c3b5671c8ae3fbfc23a24cd2fdc37feaa1a6758ea5a85580ae17587bbe366f10d7cfe3720d163312075d1c6bbad8939a2c07989e2d1da075521fa3db77586f4383020392cb14503f14326a1b70ffda2a9171ee2838e729bf2346ce763d73ef0a41465b3398778e0d5024cf95acc853b7679bebb1e8020cfe4c3ea26a4e1bc7dbafe120757c7046d7a6f770789832edfc9374143579e9887ed2a362a1e4a4ea33691185b079870b8e427fc7375191615172c9b2591b8d0daff003f1da9b320b6c54bbc99e2f9b4b3ab2d24c9b15157b789bccea193b57483f6dd33f3aa92e472ebadd8a74302814c1ef205d7af8bb4eb687861e1d6c614c5a1839b9a690e40a763ddd69b1151a56830eaae2e31c5fe4af9966ca62abc48e674c03a4cfbced4917ad3fc6e13e7e98bb8faeac1a3899141a716521a44a2a01dbf1eaebf7b5c61681537e1956ff1b7957d8e34793137cc09c0ad0829ddda28b72959745efbeb71f4e1734dc6979a3fdd2b0497d30714817cd3112066a6f466f8db95c565e26a80fcea5858c05ca27ef08ffb25cd3484e0b4a45836cfd6a83821a681963e2bbf21e',
  "eReaderKey": 24(<< {
    1: 2,
    -1: 1,
    -2: h'60ed1de1facf2443f8f4d2e3692ee956e4956034f712238ffaa5a6017534a279',
    -3: h'd0d3ab6943faa692262db0f90c2218a8fa4cce2c521fae0a54c56b8b1b7a928a'
  } >>)
}
```

### The response and the end of the session {#ts-3-02-the-response-and-the-end-of-the-session}

The citizen approved. The wallet answers with the DeviceResponse of TS-5-11,
encrypted under `SKDevice` with the wallet's first counter:

``` { .text title="The SessionData carrying the DeviceResponse, as sent" data-format="CBOR hex" }
a164646174615908da6ee4ce1806753ef1fd780fd845ffdb77f04d146f1539ab89fe9ce1954f
500f5b320b2c293b14ce05d26323a3753d949a4dd3f664ca13550ff92f6adbd6d8c61549d876
cd34d0e4d536478d98f3cf0393876d0c55494e6d79ecad8f0e4a926eccd261132396e507b2fc
e1d760ea2ca1bdc5226c95cd54f52cc686bdc721a11add8638a6b60f7ca7ff57b5b448d1ec25
26a16777ec1eb99bf4046c942ab3a92d234880194e2c8147fc4c8f3872e409b8b462b72031c6
7294099fdc885e25198d141c37b09137669df9fb3198a7049ce740c2fa8de70957a043db2ef9
269f1669bb46cbe1ba33a08b98966b2c158212cd95c9f94b60c1777b17f7b2df01a4018cd7a0
2adf1b391c523cb36a321181b1ae43e84c61e4d52561dec07d6c6d9bfa57a35627e3bb13b3bc
b9991bec368a19580b761cf369c9e91479fc3dadfc132a7fdd638e1230231e993d071a8f1673
ce4f3477b4af6e32374b2f62c3b7bdaf228598d7c676f7ac952989fb82f442032eded89b70de
38f57f9bc3aa140e86489c217c0efb54d24563ed0f807d046b8115be5d46e05e84821935c23c
8b461d49b28bef69ecf273ab9eec0a143d3169f1e5f0f58988413c4a3efde48567f5c3243a22
2a8324d3137b66f5fd9906b29b50399f68880e9485d05b96a1b50e8a5bddfee1ff845c2634af
c5d16ea6ee6b7efe4a89de40892422d0f9402efeb99959b5db091d077041627be72d5dc92795
130d7841f1725722bab3a89aacf03eb8b5598907a40f6a4d8ffeb7b857ddc8266f5f9b00ba1d
ee9eb869ce529411ffd9baec5f9906d93d02cd6e9a00eb431e19501fa5feb6371d92897c3d7f
33e42e4ef95f044ac581bf0e3df4ae97fafad84a44ba9d5c069e44a04e79c0ad4c38c978a644
eae08908b9c8f2930bd73b8113a6572a3ed216d70a024c218fb651b044157c37017415a7033c
c850c3dfe0dcc131c581d5297ce7af1717a9c50f89d2b98ac5f100f30627ea76dc304b042894
ff1f8823493cbf0cee425170e679d1b2da192ca4696b3872aa4a9fabba8429424b7d9d9c71e7
f42c503f9eda28b36f2da19bd5bae5f8f76e63519e20189918c70a16ec36dd018be3f9772060
63eed1bcf7e922631d526254afc8e6d5d8e24d94fbaa07af0ee65b70b15a631b684a707d1a72
86336c0057b4b6b49225826f1068ac12c8ab88c807b827c1e0f4806b638b222dbe741c1e4736
e2f9b3e3f921d8a82c0839f5b1774fec9e979f395be4dc7ba719a94e6783476c53160560811d
0b533f0e80bc4363d812bb8b23fc426000afade13089573c15a0a085570fbf7f8ee7fabb01f1
fdc7fd9db9be345958fccc3029e96cd03049289ef0f1428cc0ad0f3d4b7d280d29b045878fba
da0d7a7c576e17000ecddd052eda251d2fcebc2ec40085e559a44ecae8252c17b20e5ff5ad78
964621c713abb72760458edc8b432d7559bf3c3506e4d54bafbc2dc069d42647b3bb014e1cd5
7c7aa235c0e28bbe6bde722626291f3fc166bda20481ebcc7fb5e16129275f1e494a4cfd1c43
3da2f32644903591ce2e7e5b074aff5f71b008852860ef9e40533d1185fc3d9ae774a7f9b98e
a32d6273e93bc08645029d68b80bbdd1aafd03e6fa6a77a447eb2bf810265ce2ce5ef171f0ac
f2f2bbcb9c04a202aaec1a8a708a5bd041a7d6567358c24c98bbc2178576ef32213e99d288cf
ad5acb3220819277c6b725eddcd926853d09ffa5402f872c4f0c629b997ce3d13f6ab7f06fd7
26522560f6710c8e7c79d7ad6bf5929b3039f41eccd95119da3372bffb2b53c7b3fb2413f421
7c96f0c2f3ab8d6e84bde1a9f0796899420a6e9ce2b3cc4e75a051f8523432096f3e1110d402
2c1782b1d8014f0cebbf50d023689d008e50a2bae2b37223938903bbb7db067c1660c4881db7
6dbe74f44ff10d9ea6b97b49e54b08f21afa697761d7d62142d87cf57de41cd2d470cae13d38
c289921f13533b60208abba58adddc849fdcca708295b9df6a0fbb3f0aa52159d5b62e1514ce
73379c1ca9bc465cf0d42ef5aa26cc55104f45d04870226e64ac43b0575f883bdbb387cad6d9
2d531cee67a176d174f9af8fc9a36e2ac940b2d8ff2b1a307f2f566dca9d4baeeaed3c3f2534
dd54f4c92cee41f62591123657db8d2b016916d28b82a17ae336e601bae7255bac38fccad355
3cb66b0ba4efa3e01edd25510fac0b638f14c7fa5e4a71e47b6c9c75f55cd5a1d4d05d28c686
6e11f37b8eb2f9b3ca98936ee377e68a26ebcd8d897f384b965fc75b7485a5b779425f086014
87ce2ea6a192b1e2c2e86d0157c19c3e5527d5fc276eefedcd712fb4daf4d1c3941bbf74c4fa
5902bf3f091b5198d63792f9738796e2f3f8edec50c1204ea3868afd894c3678cd56cec1eb25
a73396f6217e4fa5fdf5d4f97df4716097256a9a3cc107e8277750f6b4d9e52f9677121417a9
89f94f0b3c999340369503387bf2359045576015dde3231419840da9bcbbaa8784282d2ff9b7
69b155424d8ee682070047d9b1a1ca08f7f5967c4e47b699709c8d61247ece9464b23b213408
534b271aab318cd6af5632dc7b07469447ca75e9158c9957ab083d487c15a134b9c1d9bf2a62
5c8f6a23910c279d9f69968cf0957202f28f51fba6b9db188868f5b423219c4f439bf8233bae
98b403dca52ea475409707e953c4229be752dcd862e574946bb1ad839f87efc31b61e2ab40d9
159ea5ca5a572f55ab613c706f7f9e10220b4b3b8150deed0e9636ac775ff5e2226b3479752a
2e256dd4c096d550f798d0e88eb460caae8ceedfd81ced9c3ae5bddd714c12317a4bbee6f04b
83fda8051054556d8011df6f6bafbf2fd24a7ac79724a1cae4087ac756765b4eb830e59464af
87030ba5ee79b171bebe849d0d2a12770433f50c438f9b33cd8d044897986e399e0fcd347f62
d11f15131ad55179223c1f89a4912cf4a1b7c83d91a75eb01487c5ba70dd825dad1e4226c991
42e5448138776e6e24d8c00a359c8093e0df98d04fc283fe6f496503374738a80b4ec853910f
038a2bfbde54230d8916a057a5e6905320f9da20d4a839f90784f98d376e49a250aef6a4749d
76e0b67b15e8757bcccebcf9239f450e81c402f3af4ad9a714479ba8c23c708bcc714cfc21d8
a4aacced0dd54b6ae1487b08e6b541f6436c4162a7663313d7b2077be1e2c448a8
```

The reader has its answer and ends the session:

``` { .text title="The SessionData that ends the session, as sent" data-format="CBOR hex" }
a16673746174757314
```

``` { .text title="The SessionData that ends the session, in CBOR diagnostic notation" data-format="CBOR diag" }
{
  "status": 20
}
```

A side that cannot decrypt a message ends the session with status `10`
instead, and one that cannot decode it with status `11`:

``` { .text title="The SessionData of the two error statuses, as sent" data-format="CBOR hex" }
a1667374617475730a
a1667374617475730b
```

### Engagement by NFC {#ts-3-02-engagement-by-nfc}

A second citizen taps the phone instead. The wallet holds a Handover Select
message for Static Handover, with one alternative carrier: BLE in mdoc central
client mode, its UUID in the out-of-band (OOB) data of the carrier
configuration record. The DeviceEngagement rides in an auxiliary record and
names no retrieval method, because the carrier record does:

``` { .text title="The Handover Select message of an NFC engagement, as the tag holds it" data-format="NDEF hex" }
91020f487315d10209616301013001046d646f631a2015016170706c69636174696f6e2f766e
642e626c7565746f6f74682e6c652e6f6f6230021c01110793b6c4f0e2517d9a0b4e3ec61f4a
2b8d5c1e580469736f2e6f72673a31383031333a646576696365656e676167656d656e746d64
6f63a20063312e30018201d818584ba4010220012158209793e94e05bdee925bdfa3281dd237
93d3d3f0da0914a7cde3b05c6fbafb643b225820cd88eb4a47578d61d057f321373666076d4a
c44eb9f0166c812f48705e301c9e
```

``` { .text title="The same Handover Select message, record by record" data-format="NDEF hex" }
Handover Select record
91020f487315d10209616301013001046d646f63
BLE carrier configuration record
1a2015016170706c69636174696f6e2f766e642e626c7565746f6f74682e6c65
2e6f6f6230021c01110793b6c4f0e2517d9a0b4e3ec61f4a2b8d
DeviceEngagement record
5c1e580469736f2e6f72673a31383031333a646576696365656e676167656d65
6e746d646f63a20063312e30018201d818584ba4010220012158209793e94e05
bdee925bdfa3281dd23793d3d3f0da0914a7cde3b05c6fbafb643b225820cd88
eb4a47578d61d057f321373666076d4ac44eb9f0166c812f48705e301c9e
```

Its SessionTranscript ends in the Handover Select message as the reader read
it, and `null` where a Handover Request would sit under Negotiated Handover:

``` { .text title="The SessionTranscript of the NFC engagement" data-format="CBOR diag" }
[
  24(<< {
    0: "1.0",
    1: [
      1,
      24(<< {
        1: 2,
        -1: 1,
        -2: h'9793e94e05bdee925bdfa3281dd23793d3d3f0da0914a7cde3b05c6fbafb643b',
        -3: h'cd88eb4a47578d61d057f321373666076d4ac44eb9f0166c812f48705e301c9e'
      } >>)
    ]
  } >>),
  24(<< {
    1: 2,
    -1: 1,
    -2: h'04940d3b3a845ba9276dfa1267669150f0ea37a76485dc45698c1c3d65eac7f2',
    -3: h'a7c94412b539e1994d2a54a0990aad6d49d63ebee71ef62b0313f748c21fb1dd'
  } >>),
  [
    h'91020f487315d10209616301013001046d646f631a2015016170706c69636174696f6e2f766e642e626c7565746f6f74682e6c652e6f6f6230021c01110793b6c4f0e2517d9a0b4e3ec61f4a2b8d5c1e580469736f2e6f72673a31383031333a646576696365656e676167656d656e746d646f63a20063312e30018201d818584ba4010220012158209793e94e05bdee925bdfa3281dd23793d3d3f0da0914a7cde3b05c6fbafb643b225820cd88eb4a47578d61d057f321373666076d4ac44eb9f0166c812f48705e301c9e',
    null
  ]
]
```

## Device engagement {#ts-3-02-device-engagement}

Mobile Wallet starts every check. It shows the DeviceEngagement as a QR code
or holds it on an NFC tag the reader taps, and the reader reads it; nothing
reaches the wallet before that. The engagement carries the wallet's ephemeral
public key and the ways to reach it, and nothing about the citizen.

[](){ #tbl-ts-3-02-device-engagement }

<figure markdown="1" class="ekdn-table">

| Key | Member | Type | Presence | Value |
|---|---|---|---|---|
| `0` | Version | `tstr` | Present | `1.0` |
| `1` | Security | array | Present | Cipher suite `1`, then the `EDeviceKey` as a COSE_Key wrapped in CBOR tag 24 |
| `2` | DeviceRetrievalMethods | array | Present after a QR code, absent after NFC | One entry, `[2, 1, BleOptions]`, BLE |
| `3` | ServerRetrievalMethods | map | Absent | Absent |
| `4` | ProtocolInfo | any | Absent | Absent |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-3-02-003 }**REQ-TS-3-02-003** Mobile Wallet MUST offer device engagement by QR code.
- [](){ #req-ts-3-02-004 }**REQ-TS-3-02-004** Mobile Wallet MAY offer device engagement by NFC.
- [](){ #req-ts-3-02-005 }**REQ-TS-3-02-005** Mobile Wallet MUST use Static Handover when it offers device engagement by NFC.
- [](){ #req-ts-3-02-006 }**REQ-TS-3-02-006** Mobile Verifier MUST support device engagement by QR code and by NFC under Static Handover.
- [](){ #req-ts-3-02-074 }**REQ-TS-3-02-074** Mobile Verifier SHOULD support Negotiated Handover, which [ISO/IEC 18013-5][ref-iso-18013-5] clause 6.3.2.3 requires of an mDL reader, for a wallet outside IDCTF.
- [](){ #req-ts-3-02-007 }**REQ-TS-3-02-007** Mobile Wallet MUST generate a new ephemeral key pair for every engagement.
- [](){ #req-ts-3-02-008 }**REQ-TS-3-02-008** Mobile Wallet MUST generate its ephemeral key on P-256, curve `1` of the CBOR Object Signing and Encryption (COSE) registry.
- [](){ #req-ts-3-02-009 }**REQ-TS-3-02-009** Mobile Wallet MUST write each member of the DeviceEngagement as [the table of DeviceEngagement members][tbl-ts-3-02-device-engagement] gives it.
- [](){ #req-ts-3-02-010 }**REQ-TS-3-02-010** Mobile Wallet MUST NOT carry ServerRetrievalMethods, because a check in proximity makes no network call.
- [](){ #req-ts-3-02-011 }**REQ-TS-3-02-011** A QR code engagement MUST hold `mdoc:` followed by the DeviceEngagement bytes in base64url without padding, as [RFC 4648][ref-rfc4648] defines it.
- [](){ #req-ts-3-02-012 }**REQ-TS-3-02-012** An NFC engagement MUST carry the DeviceEngagement in an NFC Forum external type record of type `iso.org:18013:deviceengagement` with the identifier `mdoc`, which each alternative carrier record names as its auxiliary data reference.

</div>

## The BLE transport {#ts-3-02-the-ble-transport}

BLE is the only device retrieval method Mobile Wallet offers, so every check
between two IDCTF applications runs on it. A wallet offers either mode or
both, and a reader supports both, so that a wallet built on a library that
runs one mode at a time still reaches every counter.

In mdoc central client mode the reader is the Generic Attribute Profile
(GATT) server and advertises the UUID the engagement names; in mdoc
peripheral server mode the wallet is. Either way the client subscribes to
State and Server2Client and writes Start to State. Each side then sends a
message in parts of three bytes less than the negotiated maximum transmission
unit, each part opening with `0x01` when more follow and `0x00` on the
last.

[](){ #tbl-ts-3-02-gatt }

<figure markdown="1" class="ekdn-table">

| Characteristic | mdoc central client mode, served by the reader | mdoc peripheral server mode, served by the wallet |
|---|---|---|
| State | `00000005-A123-48CE-896B-4C76973373E6` | `00000001-A123-48CE-896B-4C76973373E6` |
| Client2Server | `00000006-A123-48CE-896B-4C76973373E6` | `00000002-A123-48CE-896B-4C76973373E6` |
| Server2Client | `00000007-A123-48CE-896B-4C76973373E6` | `00000003-A123-48CE-896B-4C76973373E6` |
| Ident | `00000008-A123-48CE-896B-4C76973373E6` | None |

</figure>

The Ident characteristic tells a wallet in mdoc central client mode that it
connected to the reader that read its own engagement, and not to another one
advertising at the next counter. Its value is the 16 bytes the HMAC-based Key
Derivation Function (HKDF) derives from the `EDeviceKeyBytes`, with SHA-256
as the hash of its Hash-based Message Authentication Code (HMAC), no salt, and
the info string `BLEIdent`. Anyone who saw the engagement can compute it, so it proves which
session the reader belongs to and nothing about who the reader is; ReaderAuth
proves that.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-3-02-013 }**REQ-TS-3-02-013** Mobile Wallet MUST offer BLE device retrieval, in mdoc central client mode, in mdoc peripheral server mode, or in both, in every engagement.
- [](){ #req-ts-3-02-014 }**REQ-TS-3-02-014** Mobile Wallet MAY offer both BLE modes in one engagement.
- [](){ #req-ts-3-02-015 }**REQ-TS-3-02-015** Mobile Wallet MUST NOT offer NFC device retrieval.
- [](){ #req-ts-3-02-016 }**REQ-TS-3-02-016** Mobile Wallet MUST NOT offer Wi-Fi Aware device retrieval.
- [](){ #req-ts-3-02-017 }**REQ-TS-3-02-017** Mobile Verifier MUST support BLE device retrieval in mdoc central client mode and in mdoc peripheral server mode.
- [](){ #req-ts-3-02-018 }**REQ-TS-3-02-018** Mobile Verifier SHOULD support NFC device retrieval as ISO/IEC 18013-5 clause 8.3.3.1.2 fixes it, for a wallet outside IDCTF.
- [](){ #req-ts-3-02-019 }**REQ-TS-3-02-019** Mobile Verifier SHOULD choose mdoc central client mode where an engagement offers both BLE modes, as ISO/IEC 18013-5 clause 8.3.3.1.1.1 advises.
- [](){ #req-ts-3-02-020 }**REQ-TS-3-02-020** Mobile Wallet MUST draw a new UUID for every engagement.
- [](){ #req-ts-3-02-070 }**REQ-TS-3-02-070** Mobile Wallet MUST NOT carry a BLE device address in BleOptions, key `20`.
- [](){ #req-ts-3-02-071 }**REQ-TS-3-02-071** Mobile Wallet MUST NOT carry the LE Device Address data type, `0x1B`, in the BLE carrier configuration record of an NFC engagement.
- [](){ #req-ts-3-02-021 }**REQ-TS-3-02-021** In mdoc central client mode, Mobile Verifier MUST serve the Ident characteristic with the value derived from the `EDeviceKeyBytes` of the engagement it read.
- [](){ #req-ts-3-02-022 }**REQ-TS-3-02-022** In mdoc central client mode, Mobile Wallet MUST read the Ident characteristic and compare it with the value it derives itself before it writes Start.
- [](){ #req-ts-3-02-023 }**REQ-TS-3-02-023** Mobile Wallet MUST disconnect from a reader whose Ident differs.

</div>

## Session establishment and encryption {#ts-3-02-session-establishment-and-encryption}

The session is set up in five steps, from the engagement the reader read.

1. Mobile Verifier generates its ephemeral key pair, `EReaderKey`, on the curve
   the `EDeviceKey` names.
2. Each side builds the SessionTranscript from what it observed, as
   [DeviceAuth and the SessionTranscript][ts-5-11-deviceauth-and-the-sessiontranscript]
   fixes: the DeviceEngagement bytes, the `EReaderKey` bytes, and the handover
   [REQ-TS-3-02-069][req-ts-3-02-069] names, `null` after a QR code and the
   NFC handover after a tap.
3. Each side computes the shared secret by Elliptic Curve Diffie-Hellman
   (ECDH) and derives `SKReader` and `SKDevice` with HKDF and SHA-256, 32 bytes
   each, as ISO/IEC 18013-5 clause 9.1.1.5 fixes. The salt is the SHA-256 digest
   of the `SessionTranscriptBytes`, and the info string is `SKReader` or
   `SKDevice`.
4. Mobile Verifier sends the SessionEstablishment, carrying `EReaderKey` and the
   DeviceRequest encrypted under `SKReader`.
5. Every later message is a SessionData, encrypted under `SKReader` when the
   reader sends it and under `SKDevice` when the wallet does.

Encryption is Advanced Encryption Standard (AES) with a 256-bit key in
Galois/Counter Mode (GCM), with empty additional authenticated data. The
initialization vector is an eight-byte identifier, all zero for the reader and
`0x0000000000000001` for the wallet, followed by a four-byte big-endian counter
that starts at 1 and grows by one for each message that key encrypts. The
encrypted value is the ciphertext followed by its 16-byte tag.

[](){ #tbl-ts-3-02-session-messages }

<figure markdown="1" class="ekdn-table">

| Message | Member | Type | Presence | Value |
|---|---|---|---|---|
| SessionEstablishment | `eReaderKey` | `bstr`, tag 24 | Present | `EReaderKey` as a COSE_Key, uncompressed, carrying `kty`, `crv`, `x`, and `y` alone |
| SessionEstablishment | `data` | `bstr` | Present | The DeviceRequest, encrypted under `SKReader` |
| SessionData | `data` | `bstr` | Conditional | The DeviceResponse encrypted under `SKDevice`; absent with status `10`, `11`, or `20` |
| SessionData | `status` | `uint` | Conditional | `10` when a message does not decrypt, `11` when it does not decode as CBOR, `20` to end the session; absent otherwise |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-3-02-024 }**REQ-TS-3-02-024** Mobile Verifier MUST generate a new `EReaderKey` for every session.
- [](){ #req-ts-3-02-025 }**REQ-TS-3-02-025** Mobile Verifier MUST generate `EReaderKey` on the curve the `EDeviceKey` of the engagement names.
- [](){ #req-ts-3-02-026 }**REQ-TS-3-02-026** Mobile Verifier MUST support P-256 for `EReaderKey`.
- [](){ #req-ts-3-02-027 }**REQ-TS-3-02-027** Mobile Verifier SHOULD support every other curve [ISO/IEC 18013-5][ref-iso-18013-5] Table 22 gives the purpose ECDH, which clause 9.1.5.2 requires of an mdoc reader, for a wallet outside IDCTF.
- [](){ #req-ts-3-02-028 }**REQ-TS-3-02-028** Mobile Verifier and Mobile Wallet MUST derive `SKReader` and `SKDevice` as ISO/IEC 18013-5 clause 9.1.1.5 fixes, each from the SessionTranscript it built itself.
- [](){ #req-ts-3-02-069 }**REQ-TS-3-02-069** Mobile Verifier and Mobile Wallet MUST each end the SessionTranscript in `null` after an engagement by QR code, and after an engagement by NFC in the array of the Handover Select message as the reader read it and the Handover Request message, or `null` under Static Handover.
- [](){ #req-ts-3-02-029 }**REQ-TS-3-02-029** Mobile Verifier MUST send the DeviceRequest in the `data` of the SessionEstablishment, encrypted under `SKReader`.
- [](){ #req-ts-3-02-030 }**REQ-TS-3-02-030** Mobile Wallet MUST send the DeviceResponse in the `data` of a SessionData, encrypted under `SKDevice`.
- [](){ #req-ts-3-02-031 }**REQ-TS-3-02-031** Mobile Verifier and Mobile Wallet MUST each start the counter of the key they encrypt with at 1 and raise it by one for every message that key encrypts.
- [](){ #req-ts-3-02-032 }**REQ-TS-3-02-032** Mobile Verifier and Mobile Wallet MUST end the session with status `10` when a message does not decrypt.
- [](){ #req-ts-3-02-033 }**REQ-TS-3-02-033** Mobile Verifier and Mobile Wallet MUST end the session with status `11` when a decrypted message does not decode as CBOR.
- [](){ #req-ts-3-02-034 }**REQ-TS-3-02-034** Mobile Verifier and Mobile Wallet MUST destroy their ephemeral private key and both session keys when the session ends.
- [](){ #req-ts-3-02-035 }**REQ-TS-3-02-035** Mobile Verifier and Mobile Wallet MUST NOT use an ephemeral key or a session key in a second session.

</div>

## The request {#ts-3-02-the-request}

A DeviceRequest holds one DocRequest per document type it asks for. Each
DocRequest carries its `ItemsRequest`, wrapped in CBOR tag 24, and a ReaderAuth
over it. The `ItemsRequest` names the document type, the data elements under
their namespace, and in `requestInfo` the Use Statement, as
[carrying it in proximity][ts-5-06-carrying-it-in-proximity] fixes.

[](){ #tbl-ts-3-02-device-request }

<figure markdown="1" class="ekdn-table">

| Structure | Member | Type | Presence | Value |
|---|---|---|---|---|
| DeviceRequest | `version` | `tstr` | Present | `1.0` |
| DeviceRequest | `docRequests` | array | Present | One DocRequest per document type asked for |
| DocRequest | `itemsRequest` | `bstr`, tag 24 | Present | The `ItemsRequest` |
| DocRequest | `readerAuth` | `COSE_Sign1` | Present | ReaderAuth over this `ItemsRequest` |
| `ItemsRequest` | `docType` | `tstr` | Present | The document type, as the issuer wrote it |
| `ItemsRequest` | `nameSpaces` | map | Present | Each data element asked for, under its namespace, mapped to its `IntentToRetain` |
| `ItemsRequest` | `requestInfo` | map | Present | `idUseStatement` and no other key |

</figure>

Every DocRequest carries a ReaderAuth, as
[REQ-TS-5-06-056][req-ts-5-06-056] requires. ReaderAuth is a `COSE_Sign1` as
[RFC 9052][ref-rfc9052] defines it. The detached content is
`ReaderAuthenticationBytes`: the array of the string `ReaderAuthentication`,
the SessionTranscript, and the `ItemsRequest` bytes as sent, encoded and
wrapped in CBOR tag 24. The device key signs it, which is the reader key a
Mobile Verifier holds, as [the device key][the-device-key] sets out.

[](){ #tbl-ts-3-02-reader-auth }

<figure markdown="1" class="ekdn-table">

| Header | Label | Presence | Value |
|---|---|---|---|
| Protected | `1`, `alg` | Present | `-7`, ES256 |
| Unprotected | `33`, `x5chain` | Present | An array of the Verifier Device Certificate, then the Verifier Issuing CA certificate that issued it, each in DER |

</figure>

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-3-02-036 }**REQ-TS-3-02-036** `version` of a DeviceRequest MUST be `1.0`.
- [](){ #req-ts-3-02-037 }**REQ-TS-3-02-037** Mobile Verifier MUST carry one DocRequest per document type it asks for.
- [](){ #req-ts-3-02-038 }**REQ-TS-3-02-038** Mobile Verifier MUST set every `IntentToRetain` to `false`, because it keeps no value it was shown, as [REQ-TS-5-11-092][req-ts-5-11-092] and [REQ-TS-5-11-096][req-ts-5-11-096] require.
- [](){ #req-ts-3-02-075 }**REQ-TS-3-02-075** A Relying Party's own application built on Reader SDK MUST set `IntentToRetain` to `true` for exactly the data elements its business system keeps beyond the transaction.
- [](){ #req-ts-3-02-039 }**REQ-TS-3-02-039** Mobile Verifier MUST NOT carry a key in `requestInfo` other than `idUseStatement`.
- [](){ #req-ts-3-02-040 }**REQ-TS-3-02-040** ReaderAuth MUST be an untagged `COSE_Sign1` whose payload is `null` and whose detached content is `ReaderAuthenticationBytes`.
- [](){ #req-ts-3-02-041 }**REQ-TS-3-02-041** `ReaderAuthentication` MUST be the array of the string `ReaderAuthentication`, the SessionTranscript Mobile Verifier built, and the `ItemsRequest` bytes as the DocRequest carries them.
- [](){ #req-ts-3-02-042 }**REQ-TS-3-02-042** The protected header of ReaderAuth MUST carry label `1` set to `-7` and no other label.
- [](){ #req-ts-3-02-043 }**REQ-TS-3-02-043** The unprotected header of ReaderAuth MUST carry label `33` and no other label.
- [](){ #req-ts-3-02-044 }**REQ-TS-3-02-044** `x5chain` MUST be an array of the Verifier Device Certificate followed by the Verifier Issuing CA certificate that issued it.
- [](){ #req-ts-3-02-045 }**REQ-TS-3-02-045** `x5chain` MUST NOT carry the Verifier Root CA certificate, because a wallet takes the root from its own build and never from a request.
- [](){ #req-ts-3-02-046 }**REQ-TS-3-02-046** The external additional authenticated data of ReaderAuth MUST be empty.
- [](){ #req-ts-3-02-047 }**REQ-TS-3-02-047** Mobile Verifier MUST send one DeviceRequest in a session.

</div>

## Checking the request {#ts-3-02-checking-the-request}

Mobile Wallet checks the request in seven steps, from its own cache, before
the citizen sees anything.

1. **Decrypt it.** The SessionEstablishment decrypts under `SKReader`, and the
   DeviceRequest decodes.
2. **Check each ReaderAuth.** Take the first certificate of `x5chain`, build
   `ReaderAuthentication` from the SessionTranscript the wallet built itself
   and the `ItemsRequest` bytes as received, and verify the signature with the
   key of that certificate.
3. **Check the reader.** Validate the chain to the Verifier Root CA, confirm
   that the Verifier Issuing CA is granted, and check the CRL, as
   [Validating a chain][ts-5-04-validating-a-chain] fixes.
4. **Check the permission.** Read from the cached Authority Statements whether
   the entity holding the Verifier Issuing CA may `request` each document type
   asked for, as [Reading the answer][ts-5-05-reading-the-answer] fixes and
   [REQ-TS-5-06-077][req-ts-5-06-077] requires. Refuse the request whole when a
   statement is missing, past its tolerance limit, or answers `false`, as the
   online check does.
5. **Check the Use Statement**, as [Reading it][ts-5-06-reading-it] fixes,
   with `sub` matched against the entity holding the Verifier Issuing CA. A
   request that carries none is served or refused as that clause sets out for
   the transition, [REQ-TS-5-06-075][req-ts-5-06-075] to
   [REQ-TS-5-06-076][req-ts-5-06-076].
6. **Apply the bounds.** Refuse every data element outside the Use Statement
   or outside the `ReaderAuthRole` of the certificate, and return no document
   of the request when one was refused, as
   [REQ-TS-5-06-112][req-ts-5-06-112] and
   [REQ-TS-5-04-101][req-ts-5-04-101] require.
7. **Ask the citizen.** The consent screen names the requester by the
   `commonName` of the certificate's subject, shows the purpose of the
   Use Statement and which data elements the requester keeps, and the citizen
   approves the whole of what is left, or refuses.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-3-02-048 }**REQ-TS-3-02-048** Mobile Wallet MUST refuse a DeviceRequest in which any DocRequest carries no `readerAuth`.
- [](){ #req-ts-3-02-049 }**REQ-TS-3-02-049** Mobile Wallet MUST verify each ReaderAuth over `ReaderAuthentication` built from the SessionTranscript it built itself and the `ItemsRequest` bytes as it received them.
- [](){ #req-ts-3-02-050 }**REQ-TS-3-02-050** Mobile Wallet MUST verify ReaderAuth with the public key of the first certificate of its `x5chain`.
- [](){ #req-ts-3-02-051 }**REQ-TS-3-02-051** Mobile Wallet MUST refuse a DeviceRequest in which any ReaderAuth does not verify.
- [](){ #req-ts-3-02-052 }**REQ-TS-3-02-052** Mobile Wallet MUST refuse a DeviceRequest whose DocRequests are not all signed under the same Verifier Device Certificate.
- [](){ #req-ts-3-02-053 }**REQ-TS-3-02-053** Mobile Wallet MUST show the citizen, on the consent screen, every data element whose `IntentToRetain` is `true` as one the requester keeps.
- [](){ #req-ts-3-02-054 }**REQ-TS-3-02-054** Mobile Wallet MUST name the requester on the consent screen by the `commonName` of the subject of the Verifier Device Certificate.
- [](){ #req-ts-3-02-055 }**REQ-TS-3-02-055** Mobile Wallet MUST NOT show the `organizationName` of that subject on the consent screen.
- [](){ #req-ts-3-02-056 }**REQ-TS-3-02-056** Mobile Wallet MUST NOT show the consent screen before every check of this clause has passed.

</div>

## The response {#ts-3-02-the-response}

Mobile Wallet answers once. A citizen who approves gets every document of
the request sent in one DeviceResponse, built as
[the mdoc presentation][ts-5-11-the-mdoc-presentation] fixes. A citizen who
refuses, or a request of which any document fell outside the bounds, gets no
DeviceResponse at all: the wallet ends the session, and the reader learns only
that nothing came. A partial answer would hand a verifier data it is bound to
refuse under [REQ-TS-5-11-088][req-ts-5-11-088].

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-3-02-057 }**REQ-TS-3-02-057** Mobile Wallet MUST send at most one DeviceResponse in a session.
- [](){ #req-ts-3-02-058 }**REQ-TS-3-02-058** `status` of a DeviceResponse MUST be `0`.
- [](){ #req-ts-3-02-059 }**REQ-TS-3-02-059** Mobile Wallet MUST NOT carry `documentErrors` in a DeviceResponse, because naming a document it did not return tells the reader what the citizen holds or refused.
- [](){ #req-ts-3-02-060 }**REQ-TS-3-02-060** Mobile Wallet MUST NOT carry `errors` in a document of a DeviceResponse.
- [](){ #req-ts-3-02-061 }**REQ-TS-3-02-061** Mobile Wallet MUST end the session with status `20` and no DeviceResponse when the citizen refuses or when any document of the request cannot be returned under [REQ-TS-5-06-112][req-ts-5-06-112].
- [](){ #req-ts-3-02-062 }**REQ-TS-3-02-062** Mobile Wallet MUST NOT answer a second DeviceRequest in a session.

</div>

## Checking the response {#ts-3-02-checking-the-response}

Mobile Verifier checks the response in five steps, from its own cache.

1. **Decrypt it.** The SessionData decrypts under `SKDevice`, and the
   DeviceResponse decodes.
2. **Check the credential**, as
   [Reading a credential][ts-5-10-reading-a-credential] fixes: IssuerAuth, the
   digests, the type, and the validity period.
3. **Check the issuer**, from `x5chain` to the Issuer Root CA or to a root its
   cached VICAL carries for the document type, as
   [Validating a chain][ts-5-04-validating-a-chain] fixes.
4. **Check the presentation**, as
   [Verifying a presentation][ts-5-11-verifying-a-presentation] fixes:
   DeviceAuth over the SessionTranscript Mobile Verifier built, and nothing
   more and nothing less than the request asked for.
5. **Check the status** in the CWT form of the issuer's status list.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-3-02-063 }**REQ-TS-3-02-063** Mobile Verifier MUST refuse a DeviceResponse whose `status` is not `0`.
- [](){ #req-ts-3-02-064 }**REQ-TS-3-02-064** Mobile Verifier MUST treat a session the wallet ends without a DeviceResponse as a refusal.
- [](){ #req-ts-3-02-065 }**REQ-TS-3-02-065** Mobile Verifier MUST NOT open a network connection between reading an engagement and the end of the session that engagement started.

</div>

## Ending the session {#ts-3-02-ending-the-session}

A session ends after one answer, after a refusal, on an error, or after 300
seconds without a message, the floor ISO/IEC 18013-5 clause 9.1.1.4 sets for
that time-out.

<div class="ekdn-reqs" markdown="1">

- [](){ #req-ts-3-02-066 }**REQ-TS-3-02-066** Mobile Verifier MUST end the session with status `20` once it has received the DeviceResponse.
- [](){ #req-ts-3-02-067 }**REQ-TS-3-02-067** On BLE, Mobile Verifier MUST signal End, `0x02`, on the State characteristic after the SessionData that ends the session, by a notification in mdoc central client mode and by a write in mdoc peripheral server mode.
- [](){ #req-ts-3-02-072 }**REQ-TS-3-02-072** On BLE, the side that is the GATT client MUST unsubscribe from State and Server2Client and disconnect once End is signaled.
- [](){ #req-ts-3-02-073 }**REQ-TS-3-02-073** Mobile Verifier and Mobile Wallet MUST end a session in which no message has arrived for 300 seconds.
- [](){ #req-ts-3-02-068 }**REQ-TS-3-02-068** Mobile Verifier and Mobile Wallet MUST NOT reconnect a session that has ended.

</div>

## Security considerations {#ts-3-02-security-considerations}

- **A reader that asks without a certificate.** The standard lets an mdoc
  answer an anonymous reader. Under this profile the wallet answers no
  DocRequest that a Verifier Device Certificate did not sign, so every request
  carries the bound its certificate sets,
  [REQ-TS-3-02-037][req-ts-3-02-037] and
  [REQ-TS-3-02-048][req-ts-3-02-048].
- **A signature lifted from another session.** ReaderAuth is taken over the
  SessionTranscript the wallet built itself, so a ReaderAuth recorded in one
  session fails in any other,
  [REQ-TS-3-02-041][req-ts-3-02-041] and
  [REQ-TS-3-02-049][req-ts-3-02-049]. The same holds for DeviceAuth in the
  other direction, as
  [REQ-TS-5-11-084][req-ts-5-11-084] fixes.
- **A replayed session.** Freshness comes from the ephemeral keys and not from
  a nonce: both sides draw new ones for every engagement and every session,
  and destroy them after,
  [REQ-TS-3-02-007][req-ts-3-02-007],
  [REQ-TS-3-02-024][req-ts-3-02-024],
  [REQ-TS-3-02-034][req-ts-3-02-034], and
  [REQ-TS-3-02-035][req-ts-3-02-035].
- **A second reader nearby.** In mdoc central client mode the wallet connects
  to whichever device advertises the UUID. The Ident check keeps it from
  talking to the wrong counter by mistake,
  [REQ-TS-3-02-022][req-ts-3-02-022] and
  [REQ-TS-3-02-023][req-ts-3-02-023], but any device that saw the QR code can
  compute Ident. ReaderAuth stops a device that copied the engagement:
  without the device key of a certified reader it gets no answer,
  [REQ-TS-3-02-048][req-ts-3-02-048] and
  [REQ-TS-3-02-051][req-ts-3-02-051]. A reader that relays the engagement to
  a far device and the messages back can still carry a session between two
  places; it gains an answer to a request that a certified device signed, with
  the bounds of that device.
- **Two readers in one request.** A DeviceRequest whose DocRequests are signed
  under different certificates would let one reader borrow another's bound,
  so the wallet refuses it,
  [REQ-TS-3-02-052][req-ts-3-02-052].
- **A message read off the air.** The request and the response are
  encrypted under keys derived from an ECDH exchange no bystander takes part
  in, [REQ-TS-3-02-028][req-ts-3-02-028] to
  [REQ-TS-3-02-030][req-ts-3-02-030]. What travels in the clear is the
  engagement, an ephemeral public key, and a UUID, and the status code that
  ends the session.
- **A counter used twice.** Under one key it breaks GCM, so each side counts
  from 1 and never reuses a key in a second
  session,
  [REQ-TS-3-02-031][req-ts-3-02-031] and
  [REQ-TS-3-02-035][req-ts-3-02-035].

## Privacy considerations {#ts-3-02-privacy-considerations}

- **The engagement says nothing about the citizen.** A QR code or an NFC tap
  hands over an ephemeral key, a transport, and a UUID, all new for each
  engagement, and no fixed device address, so a reader cannot recognize the
  same wallet twice from them,
  [REQ-TS-3-02-007][req-ts-3-02-007],
  [REQ-TS-3-02-020][req-ts-3-02-020],
  [REQ-TS-3-02-070][req-ts-3-02-070], and
  [REQ-TS-3-02-071][req-ts-3-02-071].
- **Nothing leaves the wallet before consent.** The reader sends its request
  first and learns nothing until the citizen approves,
  [REQ-TS-3-02-056][req-ts-3-02-056].
- **A refusal is one bit.** The wallet names no document and no data element
  it did not return, and a refusal reaches the reader as an ended session,
  [REQ-TS-3-02-059][req-ts-3-02-059] to
  [REQ-TS-3-02-061][req-ts-3-02-061].
- **The citizen sees what will be kept.** Mobile Verifier keeps nothing and
  says so with every `IntentToRetain` at `false`; a Relying Party's own
  application marks what its business system keeps, and the wallet shows it
  before the citizen approves,
  [REQ-TS-3-02-038][req-ts-3-02-038],
  [REQ-TS-3-02-075][req-ts-3-02-075], and
  [REQ-TS-3-02-053][req-ts-3-02-053]. What a merchant does with what it saw
  on the screen [is the Governance Framework's to bound][gf-what-a-merchant-does-with-what-it-is-shown].
- **The RP Intermediary stays off the screen.** The citizen sees the merchant's
  name and the purpose, not the RP Intermediary that vouches for it, as
  [how the intermediated group works][how-the-intermediated-group-works] sets
  out, [REQ-TS-3-02-054][req-ts-3-02-054] and
  [REQ-TS-3-02-055][req-ts-3-02-055].
- **No network means no trace elsewhere.** Neither side calls anyone during
  the check, so no Trust Registry, issuer, or RP Intermediary learns that it happened,
  [REQ-TS-3-02-065][req-ts-3-02-065].

## Changelog {#ts-3-02-changelog}

<figure markdown="1" class="ekdn-table">

| Version | Date | Change |
|---|---|---|
| 1.0 draft | 21 October 2026 | First draft |

</figure>
