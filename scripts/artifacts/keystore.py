"""Key material for the example artifacts the Technical Specifications carry.

These are illustration keys for documentation, never production trust anchors:
TS-5-04 requires a production root to be generated in an offline hardware
security module. The private keys live outside the repository, under
``IDCTF_KEYSTORE`` or ``.secrets/idctf-example-keys`` by default, and are
created on first use.
"""

from __future__ import annotations

import os
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DIR = REPO_ROOT / ".secrets" / "idctf-example-keys"

README = """# IDCTF example keys

Private keys for the artifacts the Technical Specifications show. They sign
illustrations, not production credentials: every organization, domain and key
in `docs/` is invented, and no production authority has issued anything.

Do not promote a key in this folder to a production root. TS-5-04 requires a
root key to be generated and kept in an offline hardware security module.

Written by `scripts/artifacts/build.py`. Move the folder anywhere and point
`IDCTF_KEYSTORE` at it.
"""


def keystore_dir() -> Path:
    return Path(os.environ.get("IDCTF_KEYSTORE", DEFAULT_DIR))


def load_or_create(name: str) -> ec.EllipticCurvePrivateKey:
    """Return the P-256 key called ``name``, generating it on first use."""
    directory = keystore_dir()
    directory.mkdir(parents=True, exist_ok=True)
    readme = directory / "README.md"
    if not readme.exists():
        readme.write_text(README)
    path = directory / f"{name}.pem"
    if path.exists():
        return serialization.load_pem_private_key(path.read_bytes(), password=None)
    key = ec.generate_private_key(ec.SECP256R1())
    path.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    path.chmod(0o600)
    return key


def load_or_create_ed25519(name: str) -> Ed25519PrivateKey:
    """Return the Ed25519 key called ``name``, generating it on first use."""
    directory = keystore_dir()
    directory.mkdir(parents=True, exist_ok=True)
    readme = directory / "README.md"
    if not readme.exists():
        readme.write_text(README)
    path = directory / f"{name}.pem"
    if path.exists():
        return serialization.load_pem_private_key(path.read_bytes(), password=None)
    key = Ed25519PrivateKey.generate()
    path.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    path.chmod(0o600)
    return key
