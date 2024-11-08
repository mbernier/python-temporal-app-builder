
from config import config
from temporalio.client import Client

async def temporal_client():
    """Get the client and return it"""

    temporalServer = config('server_location')
    namespace = config('workflow_namespace')
    print(temporalServer)
    print(namespace)
    return await Client.connect(temporalServer, namespace=namespace)

