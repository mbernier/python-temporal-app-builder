import asyncio
from client import temporal_client
from poker import PokerWorkflow

async def main():
    # logging.basicConfig(level=logging.CRITICAL)

    client = await temporal_client

    result = await client.execute_workflow(
        PokerWorkflow.run,
        id="poker-workflow-id",
        WORKFLOW_TASK_QUEUE="pokerWORKFLOW_TASK_QUEUE",
    )

    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())

