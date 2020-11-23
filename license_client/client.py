import base64
import collections
import json
import logging
import time

from Crypto import Random
from Crypto.Cipher import AES
from aiohttp import ClientSession

from .config import KEY, IV


class InvalidLicense(Exception):
    pass

class NoConfigs(Exception):
    pass


class ClientV3:
    OFFLINE_TIMEOUT = 10 * 86400  # 10 days
    CHECK_INTERVAL = 30  # 30 sec

    def __init__(self, url: str, license: str):
        self.url = url
        self.license = license
        self.last_success = dict()
        self.counters = collections.Counter()

    async def check(
            self,
            label: str,
            name: str,
            count: int = 1,
            force: bool = False
    ) -> bool:
        self.counters[name] += count
        if label in self.last_success and not force:
            diff = int(time.monotonic()) - self.last_success[label]
            if diff < self.CHECK_INTERVAL:
                return True
        counters = json.dumps(self.counters).encode()
        counters = base64.b64encode(counters)
        lcn = self.license.encode() + b':' + label.encode() + b':' + counters
        salt = Random.get_random_bytes(32)
        lcn += b':' + salt
        lcn += b'=' * ((16 - len(lcn) % 16) % 16)
        # print(lcn)
        lcn = AES.new(KEY, AES.MODE_CBC, IV).encrypt(lcn)
        try:
            async with ClientSession(trust_env=True) as session:
                async with session.post(self.url, data=lcn) as resp:
                    status = resp.status
                    content = await resp.read()
                    logging.info('license sent')
            # print(content)
            if status != 200:
                return False
            resp = AES.new(KEY, AES.MODE_CBC, IV).decrypt(content)
            # print(resp)
            status, s = resp.split(b':', 1)
            if status != b'success':
                return False
            if s.rstrip(b'=') != salt.rstrip(b'='):
                return False
            self.counters = collections.Counter()
            self.last_success[label] = int(time.monotonic())
            return True
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logging.exception(e)
            diff = int(time.monotonic()) - self.last_success.get(label, 0)
            return diff < self.OFFLINE_TIMEOUT


class MultiCheckerV3:
    def __init__(self, url: str):
        self._url = url
        self._clients = {}

    async def inc_counter(
            self,
            license: str,
            label: str,
            name: str,
            count: int = 1,
            force: bool = False,
    ):
        if KEY == b'' or IV == b'':
            raise NoConfigs('No LICENSE_CRYPTO_KEY or LICENSE_CRYPTO_IV envs found')
        if not license:
            raise InvalidLicense()
        if license.startswith('Token '):
            license = license.split('Token ', 1)[1].strip()
        client = self._clients.get(license, ClientV3(self._url, license))
        self._clients[license] = client
        if not await client.check(label, name, count=count, force=force):
            raise InvalidLicense()
