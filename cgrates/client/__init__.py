from cgrates.client.apier_v1 import ClientV1
from cgrates.client.apier_v2 import ClientV2
from cgrates.client.cdrs_v1 import ClientCdrsV1

class Client(ClientV1, ClientV2, ClientCdrsV1):

    def __init__(self, tenant, host="localhost", port=2080):
        self.host = host
        self.port = port
        self.tenant = tenant
