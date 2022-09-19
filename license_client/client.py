import asyncio
import base64
import collections
import json
from logging import getLogger
import time

from Crypto import Random
from Crypto.Cipher import AES
from aiohttp import ClientSession

from .config import KEY, IV


logging = getLogger('docr.license')


class InvalidLicense(Exception):
    pass


class NoConfigs(Exception):
    pass


class ClientV3:
    OFFLINE_TIMEOUT = 10 * 86400  # 10 days
    CHECK_INTERVAL = 30  # 30 sec

    def __init__(self, url: str, license: str, key: bytes = KEY, iv: bytes = IV):
        self.url = url
        self.license = license
        self.key = key
        self.iv = iv
        self.last_success = dict()
        self.counters = collections.defaultdict(int)

    async def check(
            self,
            label: str,
            name: str,
            count: int = 1,
            force: bool = False
    ) -> bool:
        self.counters[name] += count
        logging.debug(f'inc_counter[label={label}, name={name}]: {count}, result={self.counters[name]}')
        if label in self.last_success and not force:
            diff = int(time.monotonic()) - self.last_success[label]
            if diff < self.CHECK_INTERVAL:
                return True
        counters = json.dumps(dict(self.counters)).encode()
        counters = base64.b64encode(counters)
        lcn = self.license.encode() + b':' + label.encode() + b':' + counters
        salt = Random.get_random_bytes(32)
        lcn += b':' + salt
        lcn += b'=' * ((16 - len(lcn) % 16) % 16)

        lcn = AES.new(self.key, AES.MODE_CBC, self.iv).encrypt(lcn)
        try:
            async with ClientSession(trust_env=True) as session:
                async with session.post(self.url, data=lcn) as resp:
                    status = resp.status
                    content = await resp.read()
                    logging.info(f'inc_counter request: counters={dict(self.counters)}')
            # print(content)
            if status != 200:
                return False
            resp = AES.new(self.key, AES.MODE_CBC, self.iv).decrypt(content)
            logging.debug(f'inc_counter response: {resp}')
            status, s = resp.split(b':', 1)
            if status != b'success':
                return False
            if s.rstrip(b'=') != salt.rstrip(b'='):
                return False
            self.counters = collections.defaultdict(int)
            self.last_success[label] = int(time.monotonic())
            return True
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logging.exception(e)
            diff = int(time.monotonic()) - self.last_success.get(label, -self.OFFLINE_TIMEOUT)
            return diff < self.OFFLINE_TIMEOUT


class MultiCheckerV3:
    def __init__(self, url: str, key: bytes = KEY, iv: bytes = IV):
        self._url = url
        self._key = key
        self._iv = iv
        self._clients = {}

    async def inc_counter(
            self,
            license: str,
            label: str,
            name: str,
            count: int = 1,
            force: bool = False,
    ):
        if self._key == b'' or self._iv == b'':
            raise NoConfigs('No LICENSE_CRYPTO_KEY or LICENSE_CRYPTO_IV envs found')
        if not license:
            raise InvalidLicense()
        if license.startswith('Token '):
            license = license.split('Token ', 1)[1].strip()
        client = self._clients.get(license, ClientV3(self._url, license, key=self._key, iv=self._iv))
        self._clients[license] = client
        if not await client.check(label, name, count=count, force=force):
            raise InvalidLicense()
