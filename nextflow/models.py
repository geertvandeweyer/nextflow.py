import re
import os
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from nextflow.io import get_file_text, get_directory_contents

@dataclass
class Execution:
    """A class to represent the execution of a Nextflow pipeline."""

    identifier: str
    stdout: str
    stderr: str
    return_code: str
    started: datetime
    finished: datetime
    command: str
    log: str
    path: str
    remote: str
    process_executions: list

    def __repr__(self):
        return f"<Execution: {self.identifier}>"
    

    @property
    def duration(self):
        return self.finished - self.started
    

    @property
    def status(self):
        if self.return_code == "0": return "OK"
        if self.return_code == "": return "-"
        return "ERROR"



@dataclass
class ProcessExecution:
    """A class to represent the execution of a single Nextflow process."""

    identifier: str
    name: str
    process: str
    path: str
    stdout: str
    stderr: str
    return_code: str
    bash: str
    started: datetime
    finished: datetime
    status: str

    def __repr__(self):
        return f"<ProcessExecution: {self.identifier}>"
    

    @property
    def duration(self):
        return self.finished - self.started


    @property
    def full_path(self):
        if not self.path: return ""
        return Path(self.execution.path, "work", self.path)
    

    def input_data(self, include_path=True):
        """A list of files passed to the process execution as inputs.
        
        :param bool include_path: if ``False``, only filenames returned.
        :type: ``list``"""
        
        inputs = []
        run = get_file_text(self.full_path / ".command.run", self.execution.remote)
        stage = re.search(r"nxf_stage\(\)((.|\n|\r)+?)}", run)
        if not stage: return []
        contents = stage[1]
        inputs = re.findall(r"ln -s (.+?) ", contents)
        if include_path:
            return inputs
        else:
            return [os.path.basename(f) for f in inputs]
    

    def all_output_data(self, include_path=True):
        """A list of all output data produced by the process execution,
        including unpublished staging files.

        :param bool include_path: if ``False``, only filenames returned.
        :type: ``list``"""

        outputs = []
        if not self.path: return []
        inputs = self.input_data(include_path=False)
        for f in get_directory_contents(self.full_path, self.execution.remote):
            full_path = Path(f"{self.full_path}/{f}")
            if not f.startswith(".command") and f != ".exitcode":
                if f not in inputs:
                    outputs.append(str(full_path) if include_path else f)
        return outputs
