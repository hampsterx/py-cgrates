from cgrates.client.base import BaseClient
from cgrates.models import CDR

class ClientCdrsV2(BaseClient):

    def rate_call(self, cdr: CDR):

        method = "CdrsV2.ProcessExternalCDR"

        cdr.tenant = self.tenant

        params = cdr.to_dict()

        data, error = self.call_api(method, params=[params])

        if error:
            raise Exception("{} returned error: {}".format(method, error))
