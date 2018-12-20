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

        return self.client.add_rating_plan(rating_plan_id=rating_plan_id, rating_plans=[rating_plan])

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

        self.assertIsNone(self.client.get_rating_plan(rating_plan_id=self.get_id("RP")))

    def test_add_rating_plan(self):

        dest_rate_id = self.get_id("DR")
        self.create_destination_rate(dest_rate_id=dest_rate_id)

        timing_id = self.get_id("TP")
        self.create_timing(timing_id=timing_id)

        rating_plan_id = self.get_id("RP")
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

        rating_plan_id = self.get_id("RP")
        self.create_rating_plan(dest_rate_id=dest_rate_id, rating_plan_id=rating_plan_id, timing_id=timing_id)

        rating_plan_activation = models.RatingPlanActivation()
        rating_plan_activation.rating_plan_id = rating_plan_id
        rating_plan_activation.activation_time = datetime.now()

        rating_profile_id = self.get_id("RP")

        rating_profiles = self.client.add_rating_profiles(rating_profile_id=rating_profile_id, subject="*any",rating_plan_activations=[rating_plan_activation])

        # todo:

        #self.assertIsInstance(rating_plans, list)
        #self.assertEqual(len(rating_plans), 1)
