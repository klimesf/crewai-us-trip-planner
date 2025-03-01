from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field


class CalculatorToolInput(BaseModel):
    """Input schema for CalculatorTool."""
    expression: str = Field(
        ..., description="Mathematical expression to evaluate (e.g. '2 + 2', '5 * 3')")


class CalculatorTool(BaseTool):
    name: str = "Calculator"
    description: str = (
        "A calculator tool that can perform basic mathematical operations. "
        "Input should be a valid mathematical expression like '2 + 2' or '5 * 3'."
    )
    args_schema: Type[BaseModel] = CalculatorToolInput

    def _run(self, expression: str) -> str:
        try:
            result = eval(expression)
            return str(result)
        except Exception as e:
            return f"Error evaluating expression: {str(e)}"
