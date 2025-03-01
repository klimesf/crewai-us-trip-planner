import json
import os

import requests
from crewai import Agent, Task
from langchain.tools import tool
from unstructured.partition.html import partition_html
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field


class BrowserToolInput(BaseModel):
    """Input schema for BrowserTool."""
    url: str = Field(...,
                     description="URL of the website to scrape you found in Google search")


class BrowserTool(BaseTool):
    name: str = "Browser"
    description: str = "Useful to scrape and summarize a website content"
    args_schema: Type[BaseModel] = BrowserToolInput

    def _run(self, url: str) -> str:
        """Useful to scrape and summarize a website content"""
        # Store the original URL
        target_url = url

        # Create the browserless API URL
        browserless_url = f"https://chrome.browserless.io/content?token={os.environ['BROWSERLESS_API_KEY']}"

        # Use the target URL in the payload
        payload = json.dumps({"url": target_url})
        headers = {'cache-control': 'no-cache',
                   'content-type': 'application/json'}

        # Use browserless_url instead of overwriting the url parameter
        response = requests.request(
            "POST", browserless_url, headers=headers, data=payload)

        # Rest of the code remains the same
        elements = partition_html(text=response.text)
        content = "\n\n".join([str(el) for el in elements])
        content = [content[i:i + 8000] for i in range(0, len(content), 8000)]
        summaries = []
        for chunk in content:
            agent = Agent(
                config={
                    "role": "Principal Researcher",
                    "goal": "Do amazing researches and summaries based on the content you are working with",
                    "backstory": "You're a Principal Researcher at a big company and you need to do a research about a given topic.",
                },
                tools=[],
                verbose=True,
                allow_delegation=False)
            task = Task(
                agent=agent,
                description=f'Analyze and summarize the content bellow, make sure to include the most relevant information in the summary, return only the summary nothing else.\n\nCONTENT\n----------\n{chunk}',
                expected_output="A summary of the content"
            )
            summary = task.execute_sync()
            summaries.append(summary)
        return "\n\n".join(summaries)
