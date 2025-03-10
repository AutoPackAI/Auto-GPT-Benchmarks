import glob
import inspect
import os
import subprocess
import types
from abc import ABC, ABCMeta
from typing import Any, Dict, List, Optional, Tuple, Type, cast

import pytest
from dotenv import load_dotenv

from agbenchmark.challenges.define_task_types import ChallengeData, Ground

load_dotenv()

mock_test_str = os.getenv("MOCK_TEST")
MOCK_TEST = mock_test_str.lower() == "true" if mock_test_str else False


class ChallengeMeta(ABCMeta):
    def __init__(self, name: str, bases: Tuple[Type, ...], dct: Dict[str, Any]) -> None:

        super().__init__(name, bases, dct)
        try:
            frame = cast(types.FrameType, inspect.currentframe())
            assert frame.f_back is not None
            self.CHALLENGE_LOCATION = os.path.dirname(inspect.getfile(frame.f_back))
        except Exception as e:
            print(f"Unable to get the file from 8 frames back due to: {str(e)}")
            raise e


class Challenge(ABC, metaclass=ChallengeMeta):
    """The parent class to all specific challenges classes.
    Defines helper methods for running a challenge"""

    _data_cache: Dict[str, ChallengeData] = {}
    CHALLENGE_LOCATION: str

    @property
    def data(self) -> ChallengeData:
        file_path = f"{self.CHALLENGE_LOCATION}/data.json"
        Challenge._data_cache[file_path] = ChallengeData.deserialize(file_path)
        return Challenge._data_cache[file_path]

    @property
    def mock(self) -> Optional[str]:
        return self.data.mock.mock_func if self.data.mock else None

    @property
    def task(self) -> Optional[str]:
        return (
            self.data.mock.mock_task if self.data.mock and MOCK_TEST else self.data.task
        )

    @property
    def dependencies(self) -> list:
        return self.data.dependencies

    def setup_challenge(self, config: Dict[str, Any]) -> None:
        from agbenchmark.agent_interface import copy_artifacts_into_workspace, run_agent

        copy_artifacts_into_workspace(
            config["workspace"], "artifacts_in", self.__class__.CHALLENGE_LOCATION
        )

        run_agent(self.task, self.mock, config, self.__class__.CHALLENGE_LOCATION)

    @property
    def name(self) -> str:
        return self.data.name

    @pytest.mark.parametrize(
        "challenge_data",
        [data],
        indirect=True,
    )
    def test_method(self, config: Dict[str, Any]) -> None:
        raise NotImplementedError

    @staticmethod
    def open_file(workspace: str, filename: str) -> str:
        script_dir = os.path.abspath(workspace)
        workspace_dir = os.path.join(script_dir, filename)
        with open(workspace_dir, "r") as f:
            return f.read()

    def get_artifacts_out(self, workspace: str, file_patterns: list) -> List[str]:
        script_dir = os.path.abspath(workspace)
        files_contents = []

        for file_pattern in file_patterns:
            # Check if it is a file extension
            if file_pattern.startswith("."):
                # Find all files with the given extension in the workspace
                matching_files = glob.glob(os.path.join(script_dir, "*" + file_pattern))
            else:
                # Otherwise, it is a specific file
                matching_files = [os.path.join(script_dir, file_pattern)]

            for file_path in matching_files:
                if self.data.ground.type == "execute_python_code":
                    result = subprocess.run(
                        ["python3", file_path],
                        cwd=os.path.abspath(workspace),
                        capture_output=True,
                        text=True,
                    )
                    files_contents.append(result.stdout)
                else:
                    with open(file_path, "r") as f:
                        files_contents.append(f.read())

        return files_contents

    @staticmethod
    def write_to_file(workspace: str, filename: str, content: str) -> None:
        script_dir = os.path.abspath(workspace)
        print("Writing file at", script_dir)
        workspace_dir = os.path.join(script_dir, filename)

        # Open the file in write mode.
        with open(workspace_dir, "w") as f:
            # Write the content to the file.
            f.write(content)

    def get_filenames_in_workspace(self, workspace: str) -> List[str]:
        return [
            filename
            for filename in os.listdir(workspace)
            if os.path.isfile(os.path.join(workspace, filename))
        ]

    def scoring(self, content: str, ground: Ground) -> float:
        if ground.should_contain:
            for should_contain_word in ground.should_contain:
                if should_contain_word not in content:
                    return 0.0
                else:
                    print(
                        f"Word that should exist: {should_contain_word} exists in the content"
                    )

        if ground.should_not_contain:
            for should_not_contain_word in ground.should_not_contain:
                if should_not_contain_word in content:
                    return 0.0
                else:
                    print(
                        f"Word that should not exist: {should_not_contain_word} does not exist in the content"
                    )

        return 1.0
