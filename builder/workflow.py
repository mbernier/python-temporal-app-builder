"""Builds the Workflow File"""

class Workflow_Builder():
    imports:list = []



    
    def forever_workflow(self):
        self.imports.append("asyncio")
        output = """
            event = asyncio.Event()
            await event.wait()
        """
        return output
