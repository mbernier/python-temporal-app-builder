


class Workflow_Activity():

    def __init__(name:str):
        pass

    def call_activity_code():
        output = """self.data.round:str = await workflow.execute_activity(
            {{activity_method}},
            {{activity_data}},
            start_to_close_timeout=timedelta(seconds={{activity_start_to_close_timeout}}),
        )"""