from plaid import Client


class PlaidClient:

    __instance = None

    @staticmethod
    def get_instance():
        if PlaidClient.__instance is None:
            PlaidClient()
        return PlaidClient.__instance

    def __init__(self):
        if PlaidClient.__instance is not None:
            raise Exception("Object already instantiated!")
        else:
            PlaidClient.__instance = Client(
                client_id="6077aff00b1c9e00111702d8",
                secret="842032c8317c41824f993a2c23d81f",
                environment="sandbox",
                api_version="2020-09-14"
            )
