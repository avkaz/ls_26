"""
OpenAI agent using structured tool calling with a Pydantic-derived JSON schema.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from loguru import logger
from openai import OpenAI

from config.configuration import TOOL_NAME
from config.parameters import MODEL, TEMPERATURE
from config.prompts import SYSTEM_PROMPT
from schemas import MatchReport


@dataclass(frozen=True)
class MatchReportAgent:
    """
    Agent wrapper for calling OpenAI with required tool calling.
    """

    api_key: str | None
    model: str = MODEL

    def __post_init__(self) -> None:
        logger.debug("Initializing MatchReportAgent")

        # --- Validate API key ---
        if not self.api_key or not self.api_key.strip():
            logger.error("API key validation failed (empty or missing)")
            raise ValueError("api_key is empty.")

        logger.debug("API key validation passed")

        # --- Configuration summary ---
        logger.info("MatchReportAgent configuration")
        logger.info(f"Model: {self.model}")

        # --- Success ---
        logger.success("MatchReportAgent initialized successfully")

    def _language_instruction(self, language: str) -> str:
        if language == "cs":
            return "Generate the report in Czech language."
        return "Generate the report in English language."

    def analyze(self, cleaned_text: str, language: str = "en") -> MatchReport:
        """
        Analyze cleaned page text and return a validated MatchReport.
        """
        logger.info("Starting analysis with OpenAI agent")

        if not cleaned_text.strip():
            logger.error("cleaned_text is empty")
            raise ValueError("cleaned_text is empty.")

        logger.debug(f"Input text length: {len(cleaned_text)} characters")

        # --- OpenAI client ---
        logger.debug("Creating OpenAI client")
        client = OpenAI(api_key=self.api_key)

        # --- Tool schema ---
        logger.debug("Generating JSON schema from MatchReport")
        raw_schema = MatchReport.model_json_schema()

        logger.debug(f"Tool name: {TOOL_NAME}")
        logger.debug(f"Tool schema keys: {list(raw_schema.keys())}")

        tool_schema = {
            "type": "object",
            "properties": raw_schema["properties"],
            "required": raw_schema["required"],
        }

        tools = [
            {
                "type": "function",
                "name": TOOL_NAME,
                "description": "Submit extracted match statistics and a 300-word match report.",
                "parameters": tool_schema,
            }
        ]
        # --- OpenAI call ---
        logger.info("Sending request to OpenAI (tool_choice=required)")
        try:
            language_instruction = self._language_instruction(language)

            resp = client.responses.create(  # type: ignore
                model=self.model,
                input=cleaned_text,
                temperature=TEMPERATURE,
                instructions=f"{SYSTEM_PROMPT}\n\n{language_instruction}",
                tool_choice="required",
                tools=tools,
            )

        except Exception:
            logger.exception("OpenAI API call failed")
            raise

        logger.success("OpenAI response received")

        # --- Extract tool arguments ---
        logger.debug("Extracting tool call arguments from OpenAI response")
        arguments_json = _extract_required_tool_arguments(resp, tool_name=TOOL_NAME)

        logger.debug(f"Tool arguments JSON length: {len(arguments_json)}")

        # --- Validate schema ---
        logger.info("Validating AI output with Pydantic schema")
        try:
            result = MatchReport.model_validate_json(arguments_json)
        except Exception:
            logger.exception("Schema validation failed")
            raise

        logger.success("AI output validated successfully")
        return result


def _extract_required_tool_arguments(response: Any, tool_name: str) -> str:
    """
    Extract the arguments JSON string from a required tool call in a Responses API response.
    """
    logger.debug("Inspecting OpenAI response output items")

    output_items = getattr(response, "output", None)
    if not output_items:
        logger.error("OpenAI response has no output items")
        raise RuntimeError("OpenAI response has no output items; expected a tool call.")

    logger.debug(f"Number of output items: {len(output_items)}")

    for idx, item in enumerate(output_items):
        item_type = getattr(item, "type", None)
        logger.debug(f"Output item {idx}: type={item_type}")

        if item_type != "function_call":
            continue

        name = getattr(item, "name", None)
        logger.debug(f"Function call name: {name}")

        if name != tool_name:
            logger.debug("Function call name does not match required tool")
            continue

        arguments = getattr(item, "arguments", None)
        if not arguments or not isinstance(arguments, str):
            logger.error("Tool call found but arguments are missing or invalid")
            raise RuntimeError(
                "Tool call found, but arguments are missing or not a string."
            )

        logger.success("Required tool call extracted successfully")
        return arguments

    logger.error(f"Required tool call '{tool_name}' not found in OpenAI response")
    raise RuntimeError(f"No required tool call found with name='{tool_name}'.")
