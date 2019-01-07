from cgrates.schemas import models
from cgrates.client.base import BaseClient
import logging

log = logging.getLogger()


class ClientV2(BaseClient):

    def get_accounts(self):
        """
        Get Accounts
        Note: This uses data_db
        :return:
        """

        method = "ApierV2.GetAccounts"

        params = {
            "Tenant": self.tenant,
        }

        data, error = self.call_api(method, params=[params])

        if error:
            raise Exception("{} returned error: {}".format(method, error))

        return [models.Account(x) for x in data]

    def get_account(self, account: str):
        """
        Get Account
        Note: This uses data_db
        :return:
        """

        method = "ApierV2.GetAccount"

        params = {
            "Tenant": self.tenant,
            "Account": account
        }

        data, error = self.call_api(method, params=[params])

        if error:
            raise Exception("{} returned error: {}".format(method, error))

        # Strip off tenant
        data['ID'] = data['ID'].split(":")[1]

        return models.Account(data, strict=False) # todo: remove this and implement balance_map

    def add_account(self, account: str, action_plan_id: str ="", action_trigger_id: str="", allow_negative=False):
        """
        Add Account
        Note: This uses data_db
        :return:
        """

        method = "ApierV2.SetAccount"

        params = {
            "tenant": self.tenant,
            "Account": account,
            "ActionPlanID": action_plan_id,
            "ActionPlansOverwrite": True,
            "ActionTriggerID": action_trigger_id,
            "ActionTriggerOverwrite": True,
            "AllowNegative": allow_negative,
            "Disabled": False,
            "ReloadScheduler": True
        }

        data, error = self.call_api(method, params=[params])

        if error:
            raise Exception("{} returned error: {}".format(method, error))

        if data != "OK":
            raise Exception("{} returned {}".format(method, data))

        return self.get_account(account)

