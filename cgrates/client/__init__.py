from cgrates.client.apier_v1 import ClientV1
from cgrates.client.apier_v2 import ClientV2
from cgrates.client.cdrs_v2 import ClientCdrsV2

class Client(ClientV1, ClientV2, ClientCdrsV2):

    def __init__(self, tenant, host="localhost", port=2080):
        self.host = host
        self.port = port
        self.tenant = tenant
