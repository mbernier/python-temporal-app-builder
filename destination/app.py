import asyncio
from client import temporal_client
from datetime import timedelta
from temporalio import service
from temporalio.common import RetryPolicy
from poker import PokerWorkflow

async def main():
    # logging.basicConfig(level=logging.CRITICAL)

    client = await temporal_client()

    try:
        retry_policy = RetryPolicy()

        # logging.info('in try')
        result = await client.start_workflow(
            PokerWorkflow.run,
            id="poker-workflow-id",
            task_queue="poker-task-queue",
            run_timeout=timedelta(seconds=300),
            retry_policy=retry_policy
        )
    except service.RPCError as err:
        if err.grpc_status.code != 6: #@todo is there a constant for this?
            raise
        
        result = client.get_workflow_handle_for(
            PokerWorkflow.run,
            "poker-workflow-id"
        )

    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())

