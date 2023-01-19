import asyncio
from config import config
from client import temporal_client
from datetime import timedelta
from temporalio.worker import Worker
from poker import PokerWorkflow, poker_activity

interrupt_event = asyncio.Event()

async def main():
    # Connect client
    client = await temporal_client()

    # Run a worker for the workflow
    async with Worker(
        client,
        task_queue=config('WORKFLOW_TASK_QUEUE'),
        workflows=[PokerWorkflow], # needs a workflow class name
        activities=[poker_activity], # activity method names
        graceful_shutdown_timeout=timedelta(seconds=int(config('worker_graceful_shutdown_timeout')))
    ):
        # Wait until interrupted
        print("Temporal worker started, ctrl+c to exit")
        await interrupt_event.wait()
        print("Shutting down")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        interrupt_event.set()
        loop.run_until_complete(loop.shutdown_asyncgens())

