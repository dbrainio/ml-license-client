import os

KEY: str = os.getenv('LICENSE_CRYPTO_KEY', '').encode('ascii')
IV: str = os.getenv('LICENSE_CRYPTO_IV', '').encode('ascii')
