"""
Base agent class for all Bank Marketing AI agents.
Uses Azure OpenAI with function-calling (tool use) pattern.
Each subclass defines its own tools and system prompt.
"""

import json
import logging
import os
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Callable, Optional

from openai import AzureOpenAI

from config.settings import settings

logger = logging.getLogger(__name__)


class AgentTool:
    """Descriptor for a tool available to an agent."""

    def __init__(
        self,
        name: str,
        description: str,
        parameters: dict,
        handler: Callable,
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.handler = handler

    def to_openai_schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    def execute(self, **kwargs) -> Any:
        try:
            result = self.handler(**kwargs)
            return result
        except Exception as exc:
            logger.exception("Tool %s failed: %s", self.name, exc)
            return {"error": str(exc)}


class BaseAgent(ABC):
    """
    Abstract base for all marketing AI agents.
    Wraps Azure OpenAI with multi-turn conversation + tool execution.
    """

    def __init__(self):
        self._client = AzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
        )
        self._tools: dict[str, AgentTool] = {}
        self._conversation_history: list[dict] = []
        self._session_id = str(uuid.uuid4())
        self._register_tools()

    @property
    @abstractmethod
    def name(self) -> str:
        """Agent display name."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Short description of this agent's role."""

    @property
    @abstractmethod
    def phase(self) -> str:
        """Which marketing phase this agent covers."""

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """System prompt / instructions for this agent."""

    @abstractmethod
    def _register_tools(self):
        """Register all tools this agent can use."""

    def register_tool(self, tool: AgentTool):
        self._tools[tool.name] = tool

    def get_tools_schema(self) -> list[dict]:
        return [t.to_openai_schema() for t in self._tools.values()]

    def reset_conversation(self):
        self._conversation_history = []
        self._session_id = str(uuid.uuid4())

    def run(self, user_message: str, context: Optional[dict] = None) -> dict:
        """
        Run the agent with a user message.
        Handles multi-turn conversation and tool execution loops.
        Returns the final response dict.
        """
        # Inject context into first message if provided
        if context:
            context_str = "\n\nContext:\n" + json.dumps(context, indent=2)
            full_message = user_message + context_str
        else:
            full_message = user_message

        self._conversation_history.append({"role": "user", "content": full_message})

        messages = [
            {"role": "system", "content": self.system_prompt},
            *self._conversation_history,
        ]

        tool_calls_made = []
        final_response = ""
        iterations = 0
        max_iterations = 10  # Prevent infinite loops

        while iterations < max_iterations:
            iterations += 1
            try:
                response = self._client.chat.completions.create(
                    model=settings.azure_openai_deployment,
                    messages=messages,
                    tools=self.get_tools_schema() if self._tools else None,
                    tool_choice="auto" if self._tools else None,
                    temperature=0.3,
                    max_tokens=4096,
                )
            except Exception as exc:
                logger.exception("Azure OpenAI call failed: %s", exc)
                # Return mock response for development/demo
                return self._mock_response(user_message)

            choice = response.choices[0]
            message = choice.message

            # Append assistant message to history
            messages.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                    }
                    for tc in (message.tool_calls or [])
                ] or None,
            })

            # If no tool calls, we have the final answer
            if not message.tool_calls:
                final_response = message.content or ""
                break

            # Execute tool calls
            for tool_call in message.tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments or "{}")

                tool = self._tools.get(fn_name)
                if tool:
                    tool_result = tool.execute(**fn_args)
                else:
                    tool_result = {"error": f"Unknown tool: {fn_name}"}

                tool_calls_made.append({
                    "tool": fn_name,
                    "args": fn_args,
                    "result": tool_result,
                })

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result),
                })

        # Update conversation history with assistant response
        self._conversation_history.append({"role": "assistant", "content": final_response})

        return {
            "agent": self.name,
            "session_id": self._session_id,
            "response": final_response,
            "tool_calls": tool_calls_made,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _mock_response(self, user_message: str) -> dict:
        """
        Returns a rich mock response when Azure OpenAI is not configured.
        Used for local development and demos.
        """
        return {
            "agent": self.name,
            "session_id": self._session_id,
            "response": (
                f"[{self.name}] Received: '{user_message[:100]}...'\n\n"
                f"Phase: {self.phase}\n"
                f"Available tools: {', '.join(self._tools.keys())}\n\n"
                "Note: Connect Azure OpenAI to get AI-powered responses. "
                "This is a demo response showing the agent structure."
            ),
            "tool_calls": [],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "demo_mode": True,
        }

    def get_capabilities(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "phase": self.phase,
            "tools": [
                {"name": t.name, "description": t.description}
                for t in self._tools.values()
            ],
        }
