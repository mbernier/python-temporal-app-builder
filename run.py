import os
from pydantic import validate_arguments
from enum import Enum

WORKFLOW_CLASS      = "{{WORKFLOW_CLASS}}"
WORKFLOW_ID         = "{{WORKFLOW_ID}}"
WORKFLOW_TASK_QUEUE = "{{WORKFLOW_TASK_QUEUE}}"
WORKFLOW_ACTIVITIES = "{{WORKFLOW_ACTIVITIES}}"
WORKFLOW_NAMESPACE  = "{{WORKFLOW_NAME_SPACE}}"
SERVER_LOCATION_KEY = "{{SERVER_LOCATION}}"
SERVER_LOCATION     = "localhost:7233"
WORKFLOW_NAMESPACE_KEY = "{{WORKFLOW_NAMESPACE}}"
WORKFLOW_NAMESPACE = "background-check"
WORKFLOW_TASK_QUEUE_KEY = "{{WORKFLOW_TASK_QUEUE}}"
WORKFLOW_TASK_QUEUE = "poker-game-task-queue"

def read_file(filepath):
    f = open(filepath, "r")
    output = f.read()
    f.close()
    return output

class FileActionEnum(str, Enum):
    append  = "append"
    write   = "write"

class Builder_Exception(Exception):
    def __init__(self, message:str="Builder_Exception raised"):
            self.message = message
            super().__init__(self.message)

class Builder_File_Exception(Builder_Exception):
    def __init__(self, message:str="Builder_Exception raised"):
            self.message = message
            super().__init__(self.message)

class File_Base():
    @validate_arguments
    def __init__(self, source_files:list=[]):
        self.source_files:list = []
        self.replace_keys:dict = {}
        self.content:str = ""
        if source_files != []:
            for source_file in source_files:
                self.add_source(source_file)

    @validate_arguments
    def add_source(self, filename):
        if not self.file_exists(filename):
            raise Builder_File_Exception(f"{filename} does not exist")
        self.source_files.append(filename)
        self.read_source_content()
    
    @validate_arguments
    def read_source_content(self):
        output = ""

        for source in self.source_files:
            output += self.read_from_disk(source) + "\n\n"

        self.content = output

    @validate_arguments
    def read_from_disk(self, filename):
        f = open(filename, "r")
        content = f.read()
        f.close()
        return content

    @validate_arguments
    def file_exists(self, file_path:str):
        if not os.path.isfile(file_path):
            return False
        return True

    @validate_arguments
    def directory_exists(self, directory:str):
        """Check if the directory passed exists"""
        #if file DNE then fail
        if not os.path.exists(os.path.dirname(directory)):
            return False
        return True

    @validate_arguments
    def content(self, content:str, action:FileActionEnum = "write"):
        if action == "append":
            self.content += content

        if action == "write":
            self.content = content

    @validate_arguments
    def get_content(self):
        return self.content

class Builder_File(File_Base):

    @validate_arguments
    def __init__(self, destination_file:str, source_files:list=[], imports:dict[str,list]=None):
        self.imports:dict = {"python": []}
        self.source_files:list = []
        self.replace_keys:dict = {}
        self.content:str = ""
        
        if not self.directory_exists(os.path.dirname(destination_file)):
            raise Builder_File_Exception(f"The destination dir '{destination_file}' does not exist")

        self.destination = destination_file
        
        if source_files != []:
            for source_file in source_files:
                self.add_source(source_file)
        
        if None != imports:
            for source, importItems in imports.items():
                for item in importItems:
                    self.add_import(source=source, name=item)
    
    @validate_arguments
    def add_import(self, name:str, source:str="python"):
        if not source in self.imports.keys():
            self.imports[source] = []

        self.imports[source].append(name)

    @validate_arguments
    def add_replace_key(self, find_key:str, replace_key:str, filename=None):
        if find_key in self.replace_keys.keys():
            raise Builder_File_Exception(f"{find_key} is already in replace_keys for {self.destination}")
        self.replace_keys[find_key] = replace_key

    def __find_replace(self) -> str:
        for findstr, replacestr in self.replace_keys.items():
            if findstr in self.content:
                self.content = self.content.replace(findstr, replacestr)
        return self.content

    def __create_imports(self) -> str:
        output = ""
        for source, importItems in self.imports.items():
            
            itemsString = ", ".join(importItems)

            if len(importItems) > 0:
                if source == "python":
                    output += f"import {itemsString}\n"
                else:
                    output += f"from {source} import {itemsString}\n"
        
        return output + "\n"

    def __write(self):
        if not os.path.exists(os.path.dirname(self.destination)):
            os.mkdir(os.path.dirname(self.destination))

        f = open(self.destination, "w")
        imports = self.__create_imports()
        info = imports + self.__find_replace()
        f.write(f"{info}")
        f.close()

    def commit(self):
        self.__write()

class Builder():
    @validate_arguments
    def __init__(self, program_name:str, destination_dir:str):
        program_name = program_name.lower()
        self.files = {}
        self.replace_keys:dict = {'all':{}}
        self.destination_dir = destination_dir
        self.activities = {}
    
    @validate_arguments
    def add_replace_key(self, find_key:str, replace_key:str, filename=None):
        
        if None == filename:
            self.replace_keys['all'][find_key] = replace_key
        else:
            if len(self.replace_keys[filename]) > 0:
                self.replace_keys[filename][find_key] = replace_key
            else:
                self.replace_keys[filename] = {find_key: replace_key}

    @validate_arguments
    def __process_replace_keys(self):
        for file, replace_keys in self.replace_keys.items():
            if "all" == file:
                """Run through all the files and do this find/replace"""
                for findstr, replacestr in replace_keys.items():
                    for filename, fileobj in self.files.items():
                        self.files[filename].add_replace_key(findstr, replacestr)
            else: 
                """This is a find/replace for a specific file, do it there only"""
                for findstr, replacestr in replace_keys.items():
                    self.files[file].add_replace_key(findstr, replacestr)

    @validate_arguments
    def workflow_class(self, class_name:str):
        self.workflow_class = class_name
    
    @validate_arguments
    def workflow_id(self, workflow_id:str):
        self.workflow_id = workflow_id
    
    @validate_arguments
    def add_activity(self, name:str, source_files:list=None):
        self.activities[name] = source_files
    
    def get_activities(self):
        return self.activities
    
    @validate_arguments
    def add_file(self, filename:str, destination_file:str, source_files:list=None, imports:dict=None):
        self.files[filename] = Builder_File(
                source_files=source_files, 
                destination_file=destination_file, 
                imports=imports
            )
    
    def __make_activity_methods(self) -> str:
        output:str = ""
        if len(self.activities) > 0:
            for activity, source_files in self.activities.items():
                file_content = File_Base(source_files)
                activity_replace = file_content.get_content()
                output += f"""
@activity.defn
async def {activity}() -> None:
    {activity_replace}
""" 
                output += "\n\n"

        return output

    def __make_execute_activities(self) -> str:
        output:str = ""
        
        if len(self.activities) > 0:
            for activity, files in self.activities.items():
                output += """return await workflow.execute_activity(
                    {{WORKFLOW_ACTIVITY}},
                    start_to_close_timeout=timedelta(seconds=10),
                )
                """.replace("{{WORKFLOW_ACTIVITY}}", activity)
                output += "\n\n"
        
        return output

    @validate_arguments
    def commit(self):
        self.__process_replace_keys()
        for filename, fileobj in self.files.items():
            if filename == "program_file":
                self.files[filename].add_replace_key("{{ACTIVITY_METHODS}}", self.__make_activity_methods())
                self.files[filename].add_replace_key("{{EXECUTE_ACTIVITIES}}", self.__make_execute_activities())
            fileobj.commit()
        print(f"Application created in {self.destination_dir}")

from pathlib import Path

def main():

    path_dir            = Path(os.path.dirname(__file__))
    current_dir         = str(path_dir)
    destination_dir     = str(path_dir.parent) + "/poker-destination/"
    # destination_dir     = str(path_dir) + "/destination/"
    program_name        = "poker"
    builder             = Builder(program_name, destination_dir)
    workflow_class_name = f"{program_name.capitalize()}Workflow"
    activity_name       = f"{program_name}_activity"

    builder.add_activity(
        activity_name, 
        source_files = [current_dir + "/sources/poker-activity-code.py.txt"]
    )

    builder.add_file(
        filename="gitignore", 
        source_files = [
            current_dir + "/templates/gitignore.txt"
        ],
        destination_file=f"{destination_dir}.gitignore"
    )

    builder.add_file(
        filename="dataclasses", 
        source_files = [
            current_dir + "/sources/classes.py"
        ],
        imports = {
            "python": ["random"]
        },
        destination_file=f"{destination_dir}dataobjs.py"
    )
    
    program_file_name = "program_file"
    builder.add_file(
        filename=program_file_name, 
        source_files = [
            current_dir + "/templates/workflow.py.txt"
        ],
        imports = {
            "dataobjs": ["StandardDeck", "Player", "PokerScorer"],
            "datetime": ["timedelta"],
            "temporalio": ["activity", "workflow"]
        },
        destination_file=f"{destination_dir}{program_name}.py"
    )

    workflow_class_imports_list = [workflow_class_name]

    builder.add_file(
        filename='app',
        source_files = [
            current_dir + "/templates/app.py.txt"
        ],
        imports = {
            "python": ["asyncio"],
            "client": ["temporal_client"],
            "datetime": ["timedelta"],
            "temporalio": ["service"],
            "temporalio.common": ["RetryPolicy"],
            program_name: workflow_class_imports_list
        },
        destination_file = f"{destination_dir}/app.py"
    )

    builder.add_file(
        filename='client',
        source_files = [
            current_dir + "/templates/client.py.txt"
        ],
        destination_file = f"{destination_dir}/client.py"
    )

    builder.add_file(
        filename='worker',
        source_files = [
            current_dir + "/templates/worker.py.txt"
        ],
        imports = {
            "python": ["asyncio"],
            "config": ["config"],
            "client": ["temporal_client"],
            "datetime": ["timedelta"],
            "temporalio.worker": ["Worker"],
            program_name: workflow_class_imports_list  + [activity_name] 
        },
        destination_file = f"{destination_dir}/worker.py"
    )
    
    builder.add_file(
            filename = 'config.ini', 
            source_files = [current_dir + "/templates/config.ini.txt"],
            destination_file = destination_dir + "/config.ini"
    )

    builder.add_file(
        filename = 'config.py',
        source_files = [current_dir + "/templates/config.py.txt"],
        destination_file = destination_dir + "/config.py"
    )
    
    builder.add_replace_key(WORKFLOW_TASK_QUEUE_KEY, WORKFLOW_TASK_QUEUE)
    builder.add_replace_key(WORKFLOW_NAMESPACE_KEY, WORKFLOW_NAMESPACE)
    builder.add_replace_key(SERVER_LOCATION_KEY, SERVER_LOCATION)
    builder.add_replace_key(WORKFLOW_CLASS,         workflow_class_name)
    builder.add_replace_key(WORKFLOW_ID,            f"{program_name}-workflow-id")
    builder.add_replace_key(WORKFLOW_TASK_QUEUE,    f"{program_name}-task-queue")
    builder.add_replace_key(WORKFLOW_ACTIVITIES,    ", ".join(builder.get_activities().keys()))

    builder.commit()

if __name__ == "__main__":
    main()