"""Fixed read-only CloudWatch aggregate query. No shell or caller-controlled arguments."""
import json
import os
from pathlib import Path
import subprocess
from agentjam.modules.tools.public import ToolFailure

class MockAlarmTool:
    id = "mock.alarm-count"
    def collect(self):
        return 0

class AwsAlarmTool:
    id = "aws.cloudwatch.alarm-count"
    def __init__(self, executable: Path, profile: str, region: str, account: str):
        self.executable, self.profile, self.region, self.account = executable, profile, region, account

    def collect(self):
        identity = self._query(["sts", "get-caller-identity", "--query", "Account"])
        if identity != self.account:
            raise ToolFailure("aws_account_mismatch")
        data = self._query(["cloudwatch", "describe-alarms",
                "--state-value", "ALARM", "--alarm-types", "CompositeAlarm", "MetricAlarm",
                "--query", "{metric:length(MetricAlarms),composite:length(CompositeAlarms)}"])
        try:
            values = [data["metric"], data["composite"]]
            if any(type(v) is not int or v < 0 for v in values):
                raise ValueError()
            return sum(values)
        except (ValueError, TypeError, KeyError):
            raise ToolFailure("invalid_result") from None

    def _query(self, command):
        args = [str(self.executable), *command,
                "--profile", self.profile, "--region", self.region,
                "--output", "json", "--no-cli-pager", "--no-cli-auto-prompt",
                "--cli-connect-timeout", "5", "--cli-read-timeout", "10"]
        # Do not pass explicit access keys or alternate AWS endpoint configuration.
        env = {k: v for k,v in os.environ.items()
               if not k.startswith("AWS_") and k != "AGENTJAM_API_TOKEN"}
        env["AWS_PAGER"] = ""
        env["AWS_IGNORE_CONFIGURED_ENDPOINT_URLS"] = "true"
        env["AWS_EC2_METADATA_DISABLED"] = "true"
        try:
            result = subprocess.run(args, shell=False, capture_output=True, timeout=30,
                                    env=env, check=False)
        except subprocess.TimeoutExpired:
            raise ToolFailure("timeout") from None
        except OSError:
            raise ToolFailure("cli_unavailable") from None
        if result.returncode != 0:
            # No raw stderr; do not infer authentication state from every failure.
            raise ToolFailure("aws_query_failed_check_session_or_permissions")
        if len(result.stdout) > 4096:
            raise ToolFailure("invalid_result")
        try:
            return json.loads(result.stdout)
        except (ValueError, TypeError, KeyError):
            raise ToolFailure("invalid_result") from None
