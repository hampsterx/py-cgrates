from datetime import time
from typing import List
from cgrates.schemas import models
from cgrates.client.base import BaseClient, TPNotFoundException
import logging

log = logging.getLogger()


class ClientV1(BaseClient):

    def reload_cache(self):

        method = "ApierV1.ReloadCache"

        params = {

        }

        data, error = self.call_api(method, params=[params])

        if error:
            if error == "NOT_FOUND":
                return None
            else:
                raise Exception("{} returned error: {}".format(method, error))

    def get_timing(self, timing_id):

        self.ensure_valid_tag(name="timing_id", value=timing_id)

        method = "ApierV1.GetTPTiming"

        params = {
            'TPid': self.tenant,
            'ID': timing_id
        }

        data, error = self.call_api(method, params=[params])

        if error:
            raise Exception("{} returned error: {}".format(method, error))

        data.pop("TPid")

        return models.Timing(data)


    def add_timing(self, timing_id, week_days: List[int] = None, time: time = None):

        self.ensure_valid_tag(name="timing_id", value=timing_id)

        method = "ApierV1.SetTPTiming"

        timing = models.Timing({'timing_id' : timing_id})

        if week_days:
            timing.week_days = week_days
        if time:
            timing.time = time

        params = timing.to_dict()
        params['TPid'] = self.tenant

        data, error = self.call_api(method, params=[params])

        if error:
            raise Exception("{} returned error: {}".format(method, error))

        return self.get_timing(timing_id)


    def get_destination(self, destination_id: str):

        self.ensure_valid_tag(name="destination_id", value=destination_id, prefix="DST")

        method = "ApierV1.GetDestination"

        data, error = self.call_api(method, params=[destination_id])

        if error:
            if error == "NOT_FOUND":
                return None
            else:
                raise Exception("{} returned error: {}".format(method, error))

        return models.Destination(data)

    def add_destination(self, destination_id: str, prefixes):

        self.ensure_valid_tag(name="destination_id", value=destination_id, prefix="DST")

        method = "ApierV1.SetTPDestination"

        params = {
            "id": destination_id,
            "Prefixes": prefixes,
            "TPid": self.tenant
        }

        data, error = self.call_api(method, params=[params])

        if error:
            raise Exception("{} returned error: {}".format(method, error))

        # Refresh data_db
        method = "ApierV1.LoadDestination"

        params = {
            "id": destination_id,
            "TPid": self.tenant,
        }

        data, error = self.call_api(method, params=[params])

        if error:
            raise Exception("{} returned error: {}".format(method, error))

        return self.get_destination(destination_id=destination_id)

    def get_rates(self, rate_id: str):

        self.ensure_valid_tag(name="rate_id", value=rate_id, prefix="RT")

        method = "ApierV1.GetTPRate"

        params = {
            "Id": rate_id,
            "TPid": self.tenant
        }

        data, error = self.call_api(method, params=[params])

        if error:
            if error == "NOT_FOUND":
                return None
            else:
                raise Exception("{} returned error: {}".format(method, error))

        return [models.Rate(r) for r in data['RateSlots']]

    def add_rates(self, rate_id: str, rates: List[models.Rate]):

        self.ensure_valid_tag(name="rate_id", value=rate_id, prefix="RT")

        method = "ApierV1.SetTPRate"

        params = {
            "Id": rate_id,
            "RateSlots": [r.to_primitive() for r in rates],
            "TPid": self.tenant
        }

        data, error = self.call_api(method, params=[params])

        if error:
            raise Exception("{} returned error: {}".format(method, error))

        return self.get_rates(rate_id=rate_id)


    def get_destination_rates(self, dest_rate_id: str):

        self.ensure_valid_tag(name="dest_rate_id", value=dest_rate_id, prefix="DR")

        method = "ApierV1.GetTPDestinationRate"

        params = {
            "TPid": self.tenant,
            "ID": dest_rate_id
        }

        data, error = self.call_api(method, params=[params])

        if error:
            if error == "NOT_FOUND":
                return None
            else:
                raise Exception("{} returned error: {}".format(method, error))

        return [models.DestinationRate(dr) for dr in data['DestinationRates']]

    def add_destination_rates(self, dest_rate_id: str, dest_rates: List[models.DestinationRate]):

        self.ensure_valid_tag(name="dest_rate_id", value=dest_rate_id, prefix="DR")

        for dr in dest_rates:
            rates = self.get_rates(rate_id=dr.rate_id)
            if not rates:
                raise TPNotFoundException("Rate {} Not found. Cannot add destination rate {}".format(dr.rate_id, dest_rate_id))
            dest = self.get_destination(destination_id=dr.dest_id)
            if not dest:
                raise TPNotFoundException("Destination {} Not found. Cannot add destination rate {}".format(dr.dest_id, dest_rate_id))


        # todo: confirm rates and destinations first?

        method = "ApierV1.SetTPDestinationRate"

        params = {
            "Id": dest_rate_id,
            "DestinationRates": [dr.to_dict() for dr in dest_rates],
            "TPid": self.tenant
        }

        data, error = self.call_api(method, params=[params])

        if error:
            raise Exception("{} returned error: {}".format(method, error))

        if data != "OK":
            raise Exception("{} returned {}".format(method, data))


        #
        #method = "ApierV1.LoadDestinationRates"

        #data, error = self.call_api(method, params=[])

        #if error:
        #    raise Exception("{} returned error: {}".format(method, error))


        return self.get_destination_rates(dest_rate_id=dest_rate_id)

    def get_rating_plans(self, rating_plan_id: str):

        self.ensure_valid_tag(name="rating_plan_id", value=rating_plan_id, prefix="RPL")

        method = "ApierV1.GetTPRatingPlan"

        params = {
                    "Id": rating_plan_id,
                    "TPid": self.tenant
        }

        data, error = self.call_api(method, params=[params])

        if error:
            if error == "NOT_FOUND":
                return None

            raise Exception("{} returned error: {}".format(method, error))

        return [models.RatingPlan(rp) for rp in data['RatingPlanBindings']]


    def add_rating_plans(self, rating_plan_id: str, rating_plans: List[models.RatingPlan]):

        self.ensure_valid_tag(name="rating_plan_id", value=rating_plan_id, prefix="RPL")

        # Verify child deps exist. Eg destination rates/destinations/rates
        for rp in rating_plans:
            dr = self.get_destination_rates(dest_rate_id=rp.dest_rate_id)
            if not dr:
                raise Exception("Destination Rate {} Not found. Cannot add rating plan {}".format(rp.dest_rate_id, rating_plan_id))

            # todo: verify timing tag

        method = "ApierV1.SetTPRatingPlan"

        params = {
            "Id": rating_plan_id,
            "RatingPlanBindings": [rp.to_dict() for rp in rating_plans],
            "TPid": self.tenant
        }

        data, error = self.call_api(method, params=[params])

        if error:
            raise Exception("{} returned error: {}".format(method, error))

        method = "ApierV1.LoadRatingPlan"

        params = {
            "RatingPlanId": rating_plan_id,
            "TPid": self.tenant
        }

        data, error = self.call_api(method, params=[params])

        if error:
            raise Exception("{} returned error: {}".format(method, error))


        return self.get_rating_plans(rating_plan_id=rating_plan_id)

    def get_rating_profile(self, rating_profile_id: str):

        self.ensure_valid_tag(name="rating_profile_id", value=rating_profile_id, prefix="RPF")

        method = "ApierV1.GetTPRatingProfilesByLoadId"

        params = {
            "LoadId": rating_profile_id,
            "TPid": self.tenant,
        }

        data, error = self.call_api(method, params=[params])

        if error:
            raise Exception("{} returned error: {}".format(method, error))

        # https://github.com/cgrates/cgrates/issues/1353
        # todo
        return None

        return [models.RatingPlanActivation(rp) for rp in data['RatingPlanActivations']]


    def add_rating_profiles(self, rating_profile_id: str, subject: str, rating_plan_activations: List[models.RatingPlanActivation]):

        self.ensure_valid_tag(name="rating_profile_id", value=rating_profile_id, prefix="RPF")

        for rpa in rating_plan_activations:
            rp = self.get_rating_plans(rating_plan_id=rpa.rating_plan_id)
            if not rp:
                raise Exception("Rating Plan {} Not found. Cannot add rating profile {}".format(rpa.rating_plan_id, rating_profile_id))

        method = "ApierV1.SetTPRatingProfile"

        params = {
            "LoadId": rating_profile_id,
            "TPid": self.tenant,
            "Category": "call",
            "Direction": "*out",
            "Subject": subject,
            "Tenant": self.tenant,
            "RatingPlanActivations": [rpa.to_dict() for rpa in rating_plan_activations]
        }

        data, error = self.call_api(method, params=[params])

        if error:
            raise Exception("{} returned error: {}".format(method, error))

        method = "ApierV1.LoadRatingProfile"

        params = {
            "TPid": self.tenant,
            "LoadId": rating_profile_id
        }

        data, error = self.call_api(method, params=[params])

        if error:
            raise Exception("{} returned error: {}".format(method, error))

        return self.get_rating_profile(rating_profile_id=rating_profile_id)


    def get_cost(self, subject, destination, answer_time, usage, category="call"):

        method = "ApierV1.GetCost"

        answer_time_str = answer_time.replace(microsecond=0).isoformat()

        params = {
            "Tenant": self.tenant,
            "Category": category,
            "Subject": subject,
            "AnswerTime": answer_time_str,
            "Destination": destination,
            "Usage": usage

        }

        data, error = self.call_api(method, params=[params])

        if error:
            if error == "SERVER_ERROR: UNAUTHORIZED_DESTINATION":
                log.warn("Failed to cost call: {}".format(destination))
                return None

            raise Exception("{} returned error: {}".format(method, error))

        def format_s(num):
            return "{}s".format(round(num / (1000*1000*1000)))

        return {
            'cost' : data["Cost"],
            'usage': format_s(data["Usage"]),
            'charges': [[{'cost': i["Cost"], 'usage': format_s(i['Usage'])} for i in c["Increments"]] for c in data['Charges']],
            'rating_filters': [{'dest_id': rf['DestinationID'], 'prefix': rf['DestinationPrefix'], 'rating_plan_id': rf['RatingPlanID'], 'subject': rf['Subject']} for rf in data['RatingFilters'].values()],
            'rates': [[{'value': i['Value'], 'group_interval_start': i['GroupIntervalStart'], 'rate_increment': format_s(i['RateIncrement']), 'rate_unit': format_s(i['RateUnit'])} for i in rf] for rf in data['Rates'].values()],

        }


    def add_action(self, action):

        method = "ApierV1.SetTPActions"

        params = {
            "TPid": self.tenant,
            "Id": "test",
            "Actions": [a.to_dict() for a in action]
        }

        data, error = self.call_api(method, params=[params])

        if error:
            raise Exception("{} returned error: {}".format(method, error))

        return data

    def add_action_plan(self, action_plan_id, action_plan):

        method = "ApierV1.SetTPActionPlan"

        params = {
            "TPid": self.tenant,
            "Id": action_plan_id,
            "ActionPlan": [a.to_dict() for a in action_plan]
        }

        data, error = self.call_api(method, params=[params])

        if error:
            raise Exception("{} returned error: {}".format(method, error))

        print(data)
        # todo: format data

        return data

    def add_action_trigger(self, action_trigger_id, action_trigger):

        method = "ApierV1.SetTPActionTriggers"

        params = {
            "TPid": self.tenant,
            "Id": action_trigger_id,
            "ActionTriggers": [a.to_dict() for a in action_trigger]
        }

        data, error = self.call_api(method, params=[params])

        if error:
            raise Exception("{} returned error: {}".format(method, error))

        print(data)
        # todo: format data

        return data

    def add_account_action(self, account, action_plan_id, action_triggers_id):

        method = "ApierV1.SetTPAccountActions"

        params = {
            "TPid": self.tenant,
            "Tenant": self.tenant,
            "LoadId": "test",
            "Account": account,
            "ActionPlanId": action_plan_id,
            "ActionTriggersId": action_triggers_id,
            "AllowNegative": True,
            "Disabled": False
        }

        data, error = self.call_api(method, params=[params])

        if error:
            raise Exception("{} returned error: {}".format(method, error))

        print(data)
        # todo: format data

        return data

    def add_balance(self, account, value, balance_id, balance_type="*monetary"):

        method = "ApierV1.AddBalance"

        params = {
            "Tenant": self.tenant,
            "Account": account,
            "value": value,
            "BalanceId": balance_id,
            "BalanceType": balance_type
        }

        data, error = self.call_api(method, params=[params])

        if error:
            raise Exception("{} returned error: {}".format(method, error))

        print(data)
        # todo: format data

        return data


    def rate_cdrs(self):

        method = "CdrsV1.RateCDRs"

        # todo
        params = {
        }

        data, error = self.call_api(method, params=[params])

        if error:
            raise Exception("{} returned error: {}".format(method, error))

        # todo: check response
        return data

