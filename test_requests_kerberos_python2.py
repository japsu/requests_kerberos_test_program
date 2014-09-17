# encoding: utf-8

from contextlib import contextmanager
import json
from tempfile import NamedTemporaryFile

import ldap
import ldap.sasl
import requests
from requests_kerberos import HTTPKerberosAuth


class Settings(object):
    """
    Fake django.conf.settings
    """

    USERNAME = 'japsu'
    KOMPASSI_IPA_JSONRPC = 'https://moukari.tracon.fi/ipa/json'
    KOMPASSI_IPA_CACERT_PATH = './ca.crt'

settings = Settings()


class IPAError(RuntimeError):
    pass


def json_rpc(method_name, *args, **kwargs):
    headers = {
        "Referer": settings.KOMPASSI_IPA_JSONRPC,
        "Content-Type": "application/json",
    }

    payload = {
        "params": [args, kwargs],
        "method": method_name,
        "id": 0,
    }

    response = requests.post(settings.KOMPASSI_IPA_JSONRPC,
        auth=HTTPKerberosAuth(),
        data=json.dumps(payload),
        headers=headers,
        verify=settings.KOMPASSI_IPA_CACERT_PATH,
    )

    try:
        response.raise_for_status()
    except requests.HTTPError, e:
        raise IPAError(e)

    result = response.json()

    error = result.get('error', None)
    if error:
        raise IPAError(error)

    return result


def main():
    print json_rpc('user_show', 'japsu', dict(
        raw=False,
        all=False,
        version='2.46',
        rights=False,
    ))


if __name__ == '__main__':
    main()