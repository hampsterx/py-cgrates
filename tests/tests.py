import time
import json
import pprint
import logging
import uuid
from datetime import datetime
from unittest import TestCase
from cgrates import Client
from cgrates import models
from cgrates import TPNotFoundException

logging.getLogger("urllib3").setLevel(logging.WARNING)

class BaseTests(TestCase):

    def get_id(self, prefix):
        return "{}_TEST_{}".format(prefix, str(uuid.uuid4())[0:8]).upper()

    @staticmethod
    def dump(data):
        pprint.pprint(data, indent=2)
        raise

    def get_fixture(self, name):
        with open('tests/fixtures/{}'.format(name)) as f:
            return json.loads(f.read())

    def save_fixture(self, path, fixture):
        open("tests/fixtures/{}".format(path), 'w').write(json.dumps(fixture, indent=True))


class TPManagementHelpers(BaseTests):

    def get_rate_model(self, rate=0, connect_fee=0, rate_unit=60, rate_increment=60):

        model = models.Rate()
        model.connect_fee = connect_fee
        model.rate = rate
        model.rate_unit = rate_unit
        model.rate_increment = rate_increment

        return model

    def create_destination_rate(self, dest_rate_id):
        rate_id = self.get_id("RT")
        dest_id = self.get_id("DST")

        self.client.add_rates(rate_id=rate_id, rates=[self.get_rate_model()])
        self.client.add_destination(destination_id=dest_id, prefixes=["00"])

        dest_rate = models.DestinationRate()

        dest_rate.rate_id = rate_id
        dest_rate.dest_id = dest_id

        return self.client.add_destination_rates(dest_rate_id=dest_rate_id, dest_rates=[dest_rate])

    def create_rating_plan(self, dest_rate_id, rating_plan_id, timing_id):

        rating_plan = models.RatingPlan()

        rating_plan.dest_rate_id = dest_rate_id
        rating_plan.timing_id = timing_id

        return self.client.add_rating_plans(rating_plan_id=rating_plan_id, rating_plans=[rating_plan])

    def create_timing(self, timing_id):
        return self.client.add_timing(timing_id=timing_id)


class TPManagementTests(TPManagementHelpers, BaseTests):
    """
    TP Management Tests
    """

    def setUp(self):
        self.client = Client(tenant="test")

    def test_add_timing(self):

        timing_id = self.get_id("ALWAYS")

        timing = self.client.add_timing(timing_id=timing_id, week_days=[1,2,3,4,5])

        self.assertIsInstance(timing, models.Timing)

        data = timing.to_dict()

        # self.dump(data)

        self.assertEquals(
            {'ID': timing_id,
             'MonthDays': '*any',
             'Months': '*any',
             'Time': '00:00:00',
             'WeekDays': '1;2;3;4;5',
             'Years': '*any'},
            data
        )


    def test_get_destination_unknown(self):

        self.assertIsNone(self.client.get_destination(destination_id=self.get_id("DST")))

    def test_add_destination(self):

        dest_id = self.get_id("DST")

        destination = self.client.add_destination(dest_id, prefixes=["64"])

        self.assertIsInstance(destination, models.Destination)

        data = destination.to_dict()

        # self.dump(data)

        self.assertEquals(
            {'Id': dest_id, 'Prefixes': ['64']},
            data
        )

    def test_get_rate_unknown(self):

        self.assertIsNone(self.client.get_rates(rate_id=self.get_id("RT")))


    def test_add_rate(self):

        rate = self.get_rate_model(rate=0.05)

        rate_id = self.get_id("RT")

        rates = self.client.add_rates(rate_id=rate_id, rates=[rate])

        self.assertIsInstance(rates, list)
        self.assertEqual(len(rates), 1)

        data = rates[0].to_dict()

        # self.dump(data)

        self.assertEquals(
            {'ConnectFee': 0.0,
             'GroupIntervalStart': None,
             'Rate': 0.05,
             'RateIncrement': '60s',
             'RateUnit': '60s'
             }, data
        )

    def test_get_destination_rate_unknown(self):

        self.assertIsNone(self.client.get_destination_rates(dest_rate_id=self.get_id("DR")))


    def test_add_destination_rate(self):

        rate_id = self.get_id("RT")
        dest_id = self.get_id("DST")

        self.client.add_rates(rate_id=rate_id, rates=[self.get_rate_model()])
        self.client.add_destination(dest_id, prefixes=["65"])

        dest_rate = models.DestinationRate()

        dest_rate.rate_id = rate_id
        dest_rate.dest_id = dest_id

        dest_rate_id = self.get_id("DR")

        dest_rates = self.client.add_destination_rates(dest_rate_id=dest_rate_id, dest_rates=[dest_rate])

        self.assertIsInstance(dest_rates, list)
        self.assertEqual(len(dest_rates), 1)

        data = dest_rates[0].to_dict()

        # self.dump(data)

        self.assertEquals(
            {'DestinationId': dest_id,
             'MaxCost': 0.0,
             'MaxCostStrategy': None,
             'Rate': None,
             'RateId': rate_id,
             'RoundingDecimals': 4,
             'RoundingMethod': '*up'
             }, data
        )

    def test_add_destination_rate_missing_rate(self):

        rate_id = self.get_id("RT")
        dest_id = self.get_id("DST")

        self.client.add_rates(rate_id=rate_id, rates=[self.get_rate_model()])

        dest_rate = models.DestinationRate()

        dest_rate.rate_id = rate_id
        dest_rate.dest_id = dest_id

        dest_rate_id = self.get_id("DR")

        with self.assertRaises(TPNotFoundException):
            self.client.add_destination_rates(dest_rate_id=dest_rate_id, dest_rates=[dest_rate])

    def test_add_destination_rate_missing_dest(self):

        rate_id = self.get_id("RT")
        dest_id = self.get_id("DST")

        self.client.add_destination(destination_id=dest_id, prefixes=["00"])

        dest_rate = models.DestinationRate()

        dest_rate.rate_id = rate_id
        dest_rate.dest_id = dest_id

        dest_rate_id = self.get_id("DR")

        with self.assertRaises(TPNotFoundException):
            self.client.add_destination_rates(dest_rate_id=dest_rate_id, dest_rates=[dest_rate])



    def test_get_rating_plan_unknown(self):

        self.assertIsNone(self.client.get_rating_plans(rating_plan_id=self.get_id("RPL")))

    def test_add_rating_plan(self):

        dest_rate_id = self.get_id("DR")
        self.create_destination_rate(dest_rate_id=dest_rate_id)

        timing_id = self.get_id("TP")
        self.create_timing(timing_id=timing_id)

        rating_plan_id = self.get_id("RPL")
        rating_plans = self.create_rating_plan(dest_rate_id=dest_rate_id, rating_plan_id=rating_plan_id, timing_id=timing_id)

        self.assertIsInstance(rating_plans, list)
        self.assertEqual(len(rating_plans), 1)

        data = rating_plans[0].to_dict()

        #self.dump(data)

        self.assertEquals(
            {'DestinationRatesId': dest_rate_id,
             'TimingId': timing_id,
             'Weight': 10
             }, data
        )

    def test_get_rating_profile_unknown(self):
        pass
        #self.client.get_rating_profile(rating_profile_id="RP_TEST")

    def test_add_rating_profile(self):

        dest_rate_id = self.get_id("DR")
        self.create_destination_rate(dest_rate_id=dest_rate_id)

        timing_id = self.get_id("TP")
        self.create_timing(timing_id=timing_id)

        rating_plan_id = self.get_id("RPL")
        self.create_rating_plan(dest_rate_id=dest_rate_id, rating_plan_id=rating_plan_id, timing_id=timing_id)

        rating_plan_activation = models.RatingPlanActivation()
        rating_plan_activation.rating_plan_id = rating_plan_id

        rating_plan_activation.activation_time = datetime.now()

        rating_profile_id = self.get_id("RPF")

        rating_profiles = self.client.add_rating_profiles(rating_profile_id=rating_profile_id, subject="*any",rating_plan_activations=[rating_plan_activation])

        # todo:

        #self.assertIsInstance(rating_plans, list)
        #self.assertEqual(len(rating_plans), 1)

class RatingHelpers:

    def create_standard_rating(self):

        # Destination
        self.dest_id = self.get_id("DST")
        self.client.add_destination(destination_id=self.dest_id, prefixes=["00"])

        # Rate
        rate_id = self.get_id("RT")

        rate = models.Rate()
        rate.rate = 0.1
        rate.rate_unit = 60
        rate.rate_increment = 60

        self.client.add_rates(rate_id=rate_id, rates=[rate])

        # Destination Rate
        dest_rate = models.DestinationRate()

        dest_rate.rate_id = rate_id
        dest_rate.dest_id = self.dest_id

        dest_rate_id = self.get_id("DR")

        self.client.add_destination_rates(dest_rate_id=dest_rate_id, dest_rates=[dest_rate])

        # Timing
        timing_id = self.get_id("ALWAYS")
        self.client.add_timing(timing_id=timing_id)

        # Rating Plan

        rating_plan = models.RatingPlan()

        rating_plan.dest_rate_id = dest_rate_id
        rating_plan.timing_id = timing_id

        self.rating_plan_id = self.get_id("RPL")
        self.client.add_rating_plans(rating_plan_id=self.rating_plan_id, rating_plans=[rating_plan])

        # Rating Profile
        rating_plan_activation = models.RatingPlanActivation()
        rating_plan_activation.rating_plan_id = self.rating_plan_id
        rating_plan_activation.activation_time = datetime.now()

        rating_profile_id = self.get_id("RPF")

        self.client.add_rating_profiles(rating_profile_id=rating_profile_id, subject="*any",
                                        rating_plan_activations=[rating_plan_activation])

        self.client.reload_cache()


class CDRTests(TPManagementHelpers, RatingHelpers, BaseTests):
    """
    CDR Tests
    """

    def setUp(self):
        self.client = Client(tenant="test")

    def test_cost(self):

        self.create_standard_rating()

        result = self.client.get_cost(destination="0000000", subject="1001", answer_time=datetime.now() , usage="30s")

        # self.dump(result)

        self.assertDictEqual(
            {'charges': [[{'cost': 0.1, 'usage': '60s'}]],
             'cost': 0.1,
             'rates': [[{'group_interval_start': 0,
                         'rate_increment': '60s',
                         'rate_unit': '60s',
                         'value': 0.1}]],
             'rating_filters': [{'dest_id': self.dest_id,
                                 'prefix': '00',
                                 'rating_plan_id': self.rating_plan_id,
                                 'subject': '*out:test:call:*any'}],
             'usage': '60s'},
            result
        )



class AccountTests(TPManagementHelpers, RatingHelpers, BaseTests):
    """
    Account Tests
    """

    def setUp(self):
        self.client = Client(tenant=self.get_id("TENANT"))

    def test_account(self):

        account_id = self.get_id("ACC")

        result = self.client.add_account(account_id)

        self.assertDictEqual(
            {'ActionTriggers': None,
             'AllowNegative': False,
             'BalanceMap': {},
             'Disabled': False,
             'ID': account_id,
             'UnitCounters': None
             },
            result.to_dict()
        )

        result = self.client.add_balance(account_id, balance_id="MainBalance", value=10)

        data = result.to_dict()
        balance_map = data.pop('BalanceMap')

        self.assertDictEqual(
            {'ActionTriggers': None,
             'AllowNegative': False,
             'Disabled': False,
             'ID': account_id,
             'UnitCounters': None
             },
            data
        )

        self.assertListEqual(list(balance_map.keys()), ['*monetary'])

        balance = balance_map['*monetary'][0]
        balance.pop("Uuid")

        self.assertDictEqual(
            {'Blocker': False,
             'Categories': {},
             'DestinationIDs': {},
             'Directions': None,
             'Disabled': False,
             'ExpirationDate': '0001-01-01T00:00:00+00:00',
             'Factor': None,
             'ID': 'MainBalance',
             'RatingSubject': None,
             'SharedGroups': {},
             'TimingIDs': {},
             'Timings': None,
             'Value': 10.0,
             'Weight': 0
             },
            balance
        )

    def test_account_balance(self):

        # Add Account and set balance
        account_id = self.get_id("ACC")

        self.client.add_account(account_id)

        self.client.add_balance(account_id, balance_id="MainBalance", value=10)

        self.create_standard_rating()

        cdr = models.CDR()

        cdr.destination = "0000000"
        cdr.answer_time = datetime.now()
        cdr.usage = "30s"
        cdr.subject = account_id
        cdr.account = account_id

        cdr.request_type = "postpaid"
        cdr.origin_id = self.get_id("ORIGIN")

        self.client.process_cdr(cdr)

        # Need to wait, seems ProcessExternalCDR is async?
        time.sleep(0.1)

        result = self.client.get_account(account_id)

        # self.dump(result.to_dict())

        self.assertEqual(result.balance_map['*monetary'][0].value, 9.9)

        result = self.client.get_cdrs(account_id=account_id)

        self.assertEqual(len(result), 2)

        self.assertEqual(result[1]['Cost'], 0.1)
