## Установить:

```shell
pip install git+https://github.com/dbrainio/ml-license-client.git
```

## Запустить:

Установить перменные окружения LICENSE_CRYPTO_KEY, LICENSE_CRYPTO_IV

```python
from license_client import MultiCheckerV3, InvalidLicense, NoConfigs

LICENSE_URL='http://license.ml.dbrain.io/check/v2'
inc_counter = MultiCheckerV3(LICENSE_URL).inc_counter

await inc_counter(TOKEN, 'recognize', 'entrypoint.total.recognize')
```
