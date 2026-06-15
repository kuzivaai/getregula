# Blind Subset Code Context

Extracted 2026-06-15T12:24:36+01:00

## frigate/frigate/config/classification.py (lines 1-60)
```python
from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import ConfigDict, Field, field_validator

from .base import FrigateBaseModel

__all__ = [
    "CameraFaceRecognitionConfig",
    "CameraLicensePlateRecognitionConfig",
    "CameraAudioTranscriptionConfig",
    "FaceRecognitionConfig",
    "SemanticSearchConfig",
    "CameraSemanticSearchConfig",
    "LicensePlateRecognitionConfig",
]


class SemanticSearchModelEnum(str, Enum):
    jinav1 = "jinav1"
    jinav2 = "jinav2"


class EnrichmentsDeviceEnum(str, Enum):
    GPU = "GPU"
    CPU = "CPU"


class ModelSizeEnum(str, Enum):
    small = "small"
    large = "large"


class TriggerType(str, Enum):
    THUMBNAIL = "thumbnail"
    DESCRIPTION = "description"


class TriggerAction(str, Enum):
    NOTIFICATION = "notification"
    SUB_LABEL = "sub_label"
    ATTRIBUTE = "attribute"


class ObjectClassificationType(str, Enum):
    sub_label = "sub_label"
    attribute = "attribute"


class AudioTranscriptionConfig(FrigateBaseModel):
    enabled: bool = Field(
        default=False,
        title="Enable audio transcription",
        description="Enable or disable automatic audio transcription for all cameras; can be overridden per-camera.",
    )
    language: str = Field(
        default="en",
        title="Transcription language",
        description="Language code used for transcription/translation (for example 'en' for English). See https://whisper-api.com/docs/languages/ for supported language codes.",
    )
```

## frigate/frigate/comms/embeddings_updater.py (lines 1-60)
```python
"""Facilitates communication between processes."""

import logging
from enum import Enum
from typing import Any, Callable

import zmq

logger = logging.getLogger(__name__)


SOCKET_REP_REQ = "ipc:///tmp/cache/embeddings"


class EmbeddingsRequestEnum(Enum):
    # audio
    transcribe_audio = "transcribe_audio"
    # custom classification
    reload_classification_model = "reload_classification_model"
    # face
    clear_face_classifier = "clear_face_classifier"
    recognize_face = "recognize_face"
    register_face = "register_face"
    reprocess_face = "reprocess_face"
    # semantic search
    embed_description = "embed_description"
    embed_thumbnail = "embed_thumbnail"
    generate_search = "generate_search"
    reindex = "reindex"
    # LPR
    reprocess_plate = "reprocess_plate"
    # Review Descriptions
    summarize_review = "summarize_review"


class EmbeddingsResponder:
    def __init__(self) -> None:
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(SOCKET_REP_REQ)

    def check_for_request(self, process: Callable) -> None:
        while True:  # load all messages that are queued
            has_message, _, _ = zmq.select([self.socket], [], [], 0.01)

            if not has_message:
                break

            try:
                raw = self.socket.recv_json(flags=zmq.NOBLOCK)

                if isinstance(raw, list):
                    (topic, value) = raw
                    response = process(topic, value)
                else:
                    logging.warning(
                        f"Received unexpected data type in ZMQ recv_json: {type(raw)}"
                    )
                    response = None

```

## crewai/lib/crewai-tools/tests/rag/test_mdx_loader.py (lines 20-40)
```python
        try:
            loader = MDXLoader()
            return loader.load(SourceContent(path)), path
        finally:
            os.unlink(path)

    def test_load_basic_mdx_file(self):
        content = """
import Component from './Component'
export const meta = { title: 'Test' }

# Test MDX File

This is a **markdown** file with JSX.

<Component prop="value" />

Some more content.

<div className="container">
    <p>Nested content</p>
```

## crewai/lib/crewai-tools/src/crewai_tools/tools/oxylabs_google_search_scraper_tool/oxylabs_google_search_scraper_tool.py (lines 120-145)
```python
                sdk_type=sdk_type,
            )
        else:
            import click

            if click.confirm(
                "You are missing the 'oxylabs' package. Would you like to install it?"
            ):
                import subprocess

                try:
                    subprocess.run(["uv", "add", "oxylabs"], check=True)  # noqa: S607
                    from oxylabs import RealtimeClient

                    kwargs["oxylabs_api"] = RealtimeClient(
                        username=username,
                        password=password,
                        sdk_type=sdk_type,
                    )
                except subprocess.CalledProcessError as e:
                    raise ImportError("Failed to install oxylabs package") from e
            else:
                raise ImportError(
                    "`oxylabs` package not found, please run `uv add oxylabs`"
                )

```

## crewai/lib/crewai/src/crewai/utilities/evaluators/crew_evaluator_handler.py (lines 1-60)
```python
from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field
from rich.box import HEAVY_EDGE
from rich.console import Console
from rich.table import Table

from crewai.agent import Agent
from crewai.events.event_bus import crewai_event_bus
from crewai.events.types.crew_events import CrewTestResultEvent
from crewai.llms.base_llm import BaseLLM
from crewai.task import Task
from crewai.tasks.task_output import TaskOutput


if TYPE_CHECKING:
    from crewai.crew import Crew


class TaskEvaluationPydanticOutput(BaseModel):
    quality: float = Field(
        description="A score from 1 to 10 evaluating on completion, quality, and overall performance from the task_description and task_expected_output to the actual Task Output."
    )


class CrewEvaluator:
    """A class to evaluate the performance of the agents in the crew based on the tasks they have performed.

    Attributes:
        crew: The crew of agents to evaluate.
        tasks_scores: A dictionary to store the scores of the agents for each task.
        run_execution_times: A dictionary to store execution times for each run.
        iteration: The current iteration of the evaluation.
    """

    def __init__(
        self,
        crew: Crew,
        eval_llm: BaseLLM | str | None = None,
        openai_model_name: str | None = None,
        llm: BaseLLM | str | None = None,
    ) -> None:
        self.crew = crew
        self.llm = eval_llm
        self.tasks_scores: defaultdict[int, list[float]] = defaultdict(list)
        self.run_execution_times: defaultdict[int, list[float]] = defaultdict(list)
        self.iteration: int = 0
        self._setup_for_evaluating()

    def _setup_for_evaluating(self) -> None:
        """Sets up the crew for evaluating."""
        for task in self.crew.tasks:
            task.callback = self.evaluate

    def _evaluator_agent(self) -> Agent:
        return Agent(
            role="Task Execution Evaluator",
```

## crewai/lib/crewai/tests/utilities/evaluators/test_crew_evaluator_handler.py (lines 1-40)
```python
from unittest import mock

import pytest
from crewai.agent import Agent
from crewai.crew import Crew
from crewai.task import Task
from crewai.tasks.task_output import TaskOutput
from crewai.utilities.evaluators.crew_evaluator_handler import (
    CrewEvaluator,
    TaskEvaluationPydanticOutput,
)


class InternalCrewEvaluator:
    @pytest.fixture
    def crew_planner(self):
        agent = Agent(role="Agent 1", goal="Goal 1", backstory="Backstory 1")
        task = Task(
            description="Task 1",
            expected_output="Output 1",
            agent=agent,
        )
        crew = Crew(agents=[agent], tasks=[task])

        return CrewEvaluator(crew, openai_model_name="gpt-4o-mini")

    def test_setup_for_evaluating(self, crew_planner):
        crew_planner._setup_for_evaluating()
        assert crew_planner.crew.tasks[0].callback == crew_planner.evaluate

    def test_set_iteration(self, crew_planner):
        crew_planner.set_iteration(1)
        assert crew_planner.iteration == 1

    def test_evaluator_agent(self, crew_planner):
        agent = crew_planner._evaluator_agent()
        assert agent.role == "Task Execution Evaluator"
        assert (
            agent.goal
            == "Your goal is to evaluate the performance of the agents in the crew based on the tasks they have performed using score from 1 to 10 evaluating on completion, quality, and overall performance."
```

## crewai/lib/crewai-tools/src/crewai_tools/tools/singlestore_search_tool/singlestore_search_tool.py (lines 1-40)
```python
from collections.abc import Callable
from typing import Any

from crewai.tools import BaseTool, EnvVar
from pydantic import BaseModel, Field


try:
    from singlestoredb import connect  # type: ignore[attr-defined]
    from sqlalchemy.pool import QueuePool

    SINGLSTORE_AVAILABLE = True

except ImportError:
    SINGLSTORE_AVAILABLE = False


class SingleStoreSearchToolSchema(BaseModel):
    """Input schema for SingleStoreSearchTool.

    This schema defines the expected input format for the search tool,
    ensuring that only valid SELECT and SHOW queries are accepted.
    """

    search_query: str = Field(
        ...,
        description=(
            "Mandatory semantic search query you want to use to search the database's content. "
            "Only SELECT and SHOW queries are supported."
        ),
    )


class SingleStoreSearchTool(BaseTool):
    """A tool for performing semantic searches on SingleStore database tables.

    This tool provides a safe interface for executing SELECT and SHOW queries
    against a SingleStore database with connection pooling for optimal performance.
    """

```

## crewai/lib/crewai-tools/src/crewai_tools/tools/patronus_eval_tool/patronus_predefined_criteria_eval_tool.py (lines 85-110)
```python
                if isinstance(evaluated_model_gold_answer, str)
                else evaluated_model_gold_answer.get("description")  # type: ignore[union-attr]
            ),
            "evaluators": (
                evaluators
                if isinstance(evaluators, list)
                else evaluators.get("description")
            ),
        }

        response = requests.post(
            self.evaluate_url,
            headers=headers,
            data=json.dumps(data),
            timeout=30,
        )
        if response.status_code != 200:
            raise Exception(
                f"Failed to evaluate model input and output. Status code: {response.status_code}. Reason: {response.text}"
            )

        return response.json()
```

## crewai/lib/crewai-tools/src/crewai_tools/tools/patronus_eval_tool/patronus_eval_tool.py (lines 135-160)
```python
            "evaluators": evals,
        }

        api_key = os.getenv("PATRONUS_API_KEY", "")
        headers = {
            "X-API-KEY": api_key,
            "accept": "application/json",
            "content-type": "application/json",
        }

        response = requests.post(
            self.evaluate_url,
            headers=headers,
            data=json.dumps(data),
            timeout=30,
        )
        if response.status_code != 200:
            raise Exception(
                f"Failed to evaluate model input and output. Response status code: {response.status_code}. Reason: {response.text}"
            )

        return response.json()
```

## crewai/lib/crewai-tools/src/crewai_tools/aws/bedrock/agents/invoke_agent_tool.py (lines 160-185)
```python

            return completion

        except ClientError as e:
            error_code = "Unknown"
            error_message = str(e)

            # Try to extract error code if available
            if hasattr(e, "response") and "Error" in e.response:
                error_code = e.response["Error"].get("Code", "Unknown")
                error_message = e.response["Error"].get("Message", str(e))

            raise BedrockAgentError(f"Error ({error_code}): {error_message}") from e
        except BedrockAgentError:
            # Re-raise BedrockAgentError exceptions
            raise
        except Exception as e:
            raise BedrockAgentError(f"Unexpected error: {e!s}") from e
```

## crewai/lib/crewai-tools/src/crewai_tools/tools/selenium_scraping_tool/selenium_scraping_tool.py (lines 1-40)
```python
import re
import time
from typing import Any
from urllib.parse import urlparse

from crewai.tools import BaseTool
from pydantic import BaseModel, Field, field_validator


class FixedSeleniumScrapingToolSchema(BaseModel):
    """Input for SeleniumScrapingTool."""


class SeleniumScrapingToolSchema(FixedSeleniumScrapingToolSchema):
    """Input for SeleniumScrapingTool."""

    website_url: str = Field(
        ...,
        description="Mandatory website url to read the file. Must start with http:// or https://",
    )
    css_element: str = Field(
        ...,
        description="Mandatory css reference for element to scrape from the website",
    )

    @field_validator("website_url")
    @classmethod
    def validate_website_url(cls, v: str) -> str:
        if not v:
            raise ValueError("Website URL cannot be empty")

        if len(v) > 2048:  # Common maximum URL length
            raise ValueError("URL is too long (max 2048 characters)")

        if not re.match(r"^https?://", v):
            raise ValueError("URL must start with http:// or https://")

        try:
            result = urlparse(v)
            if not all([result.scheme, result.netloc]):
```

## crewai/lib/crewai-tools/src/crewai_tools/tools/selenium_scraping_tool/selenium_scraping_tool.py (lines 80-100)
```python
                By,
            )
        except ImportError:
            import click

            if click.confirm(
                "You are missing the 'selenium' and 'webdriver-manager' packages. Would you like to install it?"
            ):
                import subprocess

                subprocess.run(
                    ["uv", "pip", "install", "selenium", "webdriver-manager"],  # noqa: S607
                    check=True,
                )
                from selenium import webdriver
                from selenium.webdriver.chrome.options import (
                    Options,
                )
                from selenium.webdriver.common.by import (
                    By,
                )
```

## crewai/lib/crewai-tools/src/crewai_tools/tools/weaviate_tool/vector_search.py (lines 85-115)
```python

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if WEAVIATE_AVAILABLE:
            openai_api_key = os.environ.get("OPENAI_API_KEY")
            if not openai_api_key:
                raise ValueError(
                    "OPENAI_API_KEY environment variable is required for WeaviateVectorSearchTool and it is mandatory to use the tool."
                )
            self.headers = {"X-OpenAI-Api-Key": openai_api_key}
        else:
            if click.confirm(
                "You are missing the 'weaviate-client' package. Would you like to install it?"
            ):
                subprocess.run(["uv", "pip", "install", "weaviate-client"], check=True)  # noqa: S607

            else:
                raise ImportError(
                    "You are missing the 'weaviate-client' package. Would you like to install it?"
                )

    def _run(self, query: str) -> str:
        if not WEAVIATE_AVAILABLE:
            raise ImportError(
                "You are missing the 'weaviate-client' package. Would you like to install it?"
            )

        if not self.weaviate_cluster_url or not self.weaviate_api_key:
            raise ValueError("WEAVIATE_URL or WEAVIATE_API_KEY is not set")

        client = weaviate.connect_to_weaviate_cloud(
```

## crewai/lib/crewai/tests/cli/tools/test_main.py (lines 385-405)
```python
# FILE NOT FOUND: /tmp/regula-repos/crewai/lib/crewai/tests/cli/tools/test_main.py
```

## crewai/lib/crewai/src/crewai/utilities/file_handler.py (lines 170-195)
```python
```

## aider/aider/commands.py (lines 965-990)
```python
                    self.io.tool_output(f"Removed {matched_file} from the chat")

    def cmd_git(self, args):
        "Run a git command (output excluded from chat)"
        combined_output = None
        try:
            args = "git " + args
            env = dict(subprocess.os.environ)
            env["GIT_EDITOR"] = "true"
            result = subprocess.run(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=env,
                shell=True,
                encoding=self.io.encoding,
                errors="replace",
            )
            combined_output = result.stdout
        except Exception as e:
            self.io.tool_error(f"Error running /git command: {e}")

        if combined_output is None:
            return

```

## aider/tests/basic/test_linter.py (lines 55-75)
```python
        mock_popen.return_value = mock_process

        result = self.linter.run_cmd("test_cmd", "test_file.py", "code")
        self.assertIsNotNone(result)
        self.assertIn("Error message", result.text)

    def test_run_cmd_with_special_chars(self):
        with patch("subprocess.Popen") as mock_popen:
            mock_process = MagicMock()
            mock_process.returncode = 1
            mock_process.stdout.read.side_effect = ("Error message", None)
            mock_popen.return_value = mock_process

            # Test with a file path containing special characters
            special_path = "src/(main)/product/[id]/page.tsx"
            result = self.linter.run_cmd("eslint", special_path, "code")

            # Verify that the command was constructed correctly
            mock_popen.assert_called_once()
            call_args = mock_popen.call_args[0][0]

```

## monai/README.md (lines 1-20)
```markdown
<p align="center">
<img src="https://raw.githubusercontent.com/Project-MONAI/MONAI/dev/docs/images/MONAI-logo-color.png" width="50%" alt='project-monai'>
</p>

**M**edical **O**pen **N**etwork for **AI**

![Supported Python versions](https://raw.githubusercontent.com/Project-MONAI/MONAI/dev/docs/images/python.svg)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)
[![auto-commit-msg](https://img.shields.io/badge/dynamic/json?label=citations&query=%24.citationCount&url=https%3A%2F%2Fapi.semanticscholar.org%2Fgraph%2Fv1%2Fpaper%2FDOI%3A10.48550%2FarXiv.2211.02701%3Ffields%3DcitationCount)](https://arxiv.org/abs/2211.02701)
[![PyPI version](https://badge.fury.io/py/monai.svg)](https://badge.fury.io/py/monai)
[![docker](https://img.shields.io/badge/docker-pull-green.svg?logo=docker&logoColor=white)](https://hub.docker.com/r/projectmonai/monai)
[![conda](https://img.shields.io/conda/vn/conda-forge/monai?color=green)](https://anaconda.org/conda-forge/monai)

[![premerge](https://github.com/Project-MONAI/MONAI/actions/workflows/pythonapp.yml/badge.svg?branch=dev)](https://github.com/Project-MONAI/MONAI/actions/workflows/pythonapp.yml)
[![postmerge](https://img.shields.io/github/checks-status/project-monai/monai/dev?label=postmerge)](https://github.com/Project-MONAI/MONAI/actions?query=branch%3Adev)
[![Documentation Status](https://readthedocs.org/projects/monai/badge/?version=latest)](https://monai.readthedocs.io/en/latest/)
[![codecov](https://codecov.io/gh/Project-MONAI/MONAI/branch/dev/graph/badge.svg?token=6FTC7U1JJ4)](https://codecov.io/gh/Project-MONAI/MONAI)
[![monai Downloads Last Month](https://assets.piptrends.com/get-last-month-downloads-badge/monai.svg 'monai Downloads Last Month by pip Trends')](https://piptrends.com/package/monai)

MONAI is a [PyTorch](https://pytorch.org/)-based, [open-source](https://github.com/Project-MONAI/MONAI/blob/dev/LICENSE) framework for deep learning in healthcare imaging, part of the [PyTorch Ecosystem](https://pytorch.org/ecosystem/).
```

## monai/monai/networks/nets/resnet.py (lines 660-680)
```python
                logger.info(f"Trying with {filename}")
                pretrained_path = hf_hub_download(
                    repo_id=f"{medicalnet_huggingface_repo_basename}{resnet_depth}", filename=filename
                )
            else:
                raise EntryNotFoundError(
                    f"{filename} not found on {medicalnet_huggingface_repo_basename}{resnet_depth}"
                ) from None
        checkpoint = torch.load(pretrained_path, map_location=torch.device(device), weights_only=True)
    else:
        raise NotImplementedError("Supported resnet_depth are: [10, 18, 34, 50, 101, 152, 200]")
    logger.info(f"{filename} downloaded")
    return checkpoint.get("state_dict")


def get_medicalnet_pretrained_resnet_args(resnet_depth: int):
    """
    Return correct shortcut_type and bias_downsample
    for pretrained MedicalNet weights according to resnet depth.
    """
    # After testing
```

## monai/monai/networks/utils.py (lines 1-40)
```python
# Copyright (c) MONAI Consortium
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Utilities and types for defining networks, these depend on PyTorch.
"""

from __future__ import annotations

import io
import re
import tempfile
import warnings
from collections import OrderedDict
from collections.abc import Callable, Iterable, Mapping, Sequence
from contextlib import contextmanager
from copy import deepcopy
from typing import Any

import numpy as np
import torch
import torch.nn as nn

from monai.apps.utils import get_logger
from monai.config import PathLike
from monai.utils.misc import ensure_tuple, save_obj, set_determinism
from monai.utils.module import look_up_option, optional_import
from monai.utils.type_conversion import convert_to_dst_type, convert_to_tensor

onnx, _ = optional_import("onnx")
onnxreference, _ = optional_import("onnx.reference")
onnxruntime, _ = optional_import("onnxruntime")
polygraphy, polygraphy_imported = optional_import("polygraphy")
```

## rasa/tests/conftest.py (lines 515-535)
```python
@pytest.fixture
def rasa_server_secured(default_agent: Agent) -> Sanic:
    app = server.create_app(agent=default_agent, auth_token="rasa", jwt_secret="core")
    channel.register([RestInput()], app, "/webhooks/")
    return app


@pytest.fixture
def test_public_key() -> Text:
    test_public_key = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC34ht9inqGq79HecpyOAnu2Cgv
jvgcpFifpFLPmCNdiomAgE48tfUAXJRoOGlVtrqc8KgQWjTFLjqDjUh1sBFF69Fl
wQGt7pgH10ZbERWpMTAbpjI9EoH74gDcmZ6Fy1VgQPbAwty3liw5Q5zqZLj7JhuX
Sa0EqvZQP+Hnayab7QIDAQAB
-----END PUBLIC KEY-----"""

    return test_public_key


@pytest.fixture
def test_private_key() -> Text:
```

## crewai/lib/cli/tests/tools/test_main.py (lines 385-405) [corrected path from lib/crewai/tests/cli/tools/]
```python
    with raises(SystemExit):
        tool_command.publish(is_public=True)
    output = capsys.readouterr().out
    assert "Request to Enterprise API failed" in output

    mock_publish.assert_called_once()


@patch("crewai_cli.tools.main.get_project_name", return_value="sample-tool")
@patch("crewai_cli.tools.main.get_project_version", return_value="1.0.0")
@patch("crewai_cli.tools.main.get_project_description", return_value="A sample tool")
@patch("crewai_cli.tools.main.subprocess.run")
@patch("crewai_cli.tools.main.os.listdir", return_value=["sample-tool-1.0.0.tar.gz"])
@patch(
    "crewai_cli.tools.main.open",
    new_callable=unittest.mock.mock_open,
    read_data=b"sample tarball content",
)
@patch("crewai_cli.plus_api.PlusAPI.publish_tool")
@patch("crewai_cli.tools.main.git.Repository.is_synced", return_value=True)
@patch(
```

