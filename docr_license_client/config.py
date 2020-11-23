import os

KEY: str = os.getenv('DOCR_LICENSE_CRYPTO_KEY', '').encode('ascii')
IV: str = os.getenv('DOCR_LICENSE_CRYPTO_IV').encode('ascii')
