import requests
import re
import logging

log = logging.getLogger()

class TPNotFoundException(Exception):
    pass


class BaseClient:

    def call_api(self, method, params):
        body = {

            "method": method,
            "params": params
        }

        log.debug("Calling {}".format(method), extra={"params": params})

        response = requests.post('http://{}:{}/jsonrpc'.format(self.host, self.port), timeout=5, json=body)

        if response.status_code != 200:
            log.error("Received {} response".format(response.status_code), extra={"response": response.text})
            raise Exception("Received {} calling {}".format(response.status_code, method))

        result = response.json()

        return result['result'], result.get('error', None)

    def ensure_valid_tag(self, name, value, prefix=None):
        if prefix and not value.startswith("{}_".format(prefix)):
            raise Exception("{} must begin with prefix {}_ found: {}".format(name, prefix, value))

        if not re.match("^[A-Z0-9\_]+$", value):
            raise Exception("{} must be upper case/alpha or underscore only".format(name))
