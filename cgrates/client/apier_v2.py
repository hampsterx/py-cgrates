from cgrates.schemas import models
from cgrates.client.base import BaseClient
import logging

log = logging.getLogger()


class ClientV2(BaseClient):

    def _create_account_from_data(self, item):
        balance_map = item.pop('BalanceMap')

        account = models.Account(item)
        account.balance_map = {}

        if balance_map:
            for k, balances in balance_map.items():
                account.balance_map[k] = []
                for balance in balances:
                    account.balance_map[k].append(models.Balance(balance))

        return account

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

        result = []

        for item in data:
            result.append(self._create_account_from_data(item))

        return result


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

        return self._create_account_from_data(data)

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

