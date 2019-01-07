from cgrates.client.base import BaseClient
from cgrates.schemas.models import CDR
import logging

log = logging.getLogger()

class ClientCdrsV1(BaseClient):

    def process_cdr(self, cdr: CDR):

        method = "CdrsV1.ProcessExternalCDR"

        cdr.tenant = self.tenant

        params = cdr.to_dict()

        data, error = self.call_api(method, params=[params])

        if error:
            raise Exception("{} returned error: {}".format(method, error))

        return data

    def get_cdrs(self, account_id=None, last_order_id=None, limit=1000):

        method = "CdrsV1.GetCDRs"

        params = {
          #  "OrderIDStart": last_order_id,
            "Limit": limit,
         #   "Offset": 1 if last_order_id else 0
        }

        if account_id:
            params['Accounts'] = [account_id]

        print(params)

        data, error = self.call_api(method, params=[params])

        if error:
            if error == "SERVER_ERROR: NOT_FOUND":
                return []

            raise Exception("{} returned error: {}".format(method, error))

        return data
