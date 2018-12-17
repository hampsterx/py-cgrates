import json
import pprint
import logging

from unittest import TestCase
from cgrates import Client
from cgrates import models

logging.getLogger("urllib3").setLevel(logging.WARNING)

class BaseTests(TestCase):

    @staticmethod
    def dump(data):
        pprint.pprint(data, indent=2)
        raise

    def get_fixture(self, name):
        with open('tests/fixtures/{}'.format(name)) as f:
            return json.loads(f.read())

    def save_fixture(self, path, fixture):
        open("tests/fixtures/{}".format(path), 'w').write(json.dumps(fixture, indent=True))


class ClientTests(BaseTests):
    """
    Client Tests
    """

    def setUp(self):
        self.client = Client(tenant="1")

    def test_destination(self):

        destination = self.client.add_destination("DST_45", prefixes=["45"])

        self.assertIsInstance(destination, models.Destination)

        data = destination.to_dict()

        # self.dump(data)

        self.assertEquals(
            {'Id': 'DST_45', 'Prefixes': ['45']},
            data
        )

        self.assertEquals(destination.to_dict(), models.Destination.from_result(data).to_dict())


