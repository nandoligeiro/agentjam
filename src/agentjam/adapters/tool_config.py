import os
from pathlib import Path
import re
from agentjam.adapters.tool_aws_cli import AwsAlarmTool, MockAlarmTool
from agentjam.adapters.tool_sqlite import SQLiteObservationStore
from agentjam.modules.tools.public import Registry

def configured_registry(store):
    tools = [MockAlarmTool()]
    if os.getenv("AGENTJAM_ENABLE_AWS_TOOL") == "true":
        executable = Path(os.environ["AGENTJAM_AWS_CLI"])
        profile = os.environ["AGENTJAM_AWS_PROFILE"]
        region = os.environ["AGENTJAM_AWS_REGION"]
        if not executable.is_absolute() or not executable.is_file():
            raise ValueError("Provide an absolute trusted AWS CLI executable path")
        if executable.suffix.lower() in (".cmd", ".bat"):
            raise ValueError("Use a native AWS CLI executable, not a shell wrapper")
        if not re.fullmatch(r"[A-Za-z0-9_.-]{1,100}",profile):
            raise ValueError("Invalid AWS profile")
        if not re.fullmatch(r"[a-z]{2}(?:-[a-z0-9]+)+-[0-9]+",region):
            raise ValueError("Invalid AWS region")
        tools.append(AwsAlarmTool(executable.resolve(),profile,region))
    return Registry(tools,SQLiteObservationStore(store))
