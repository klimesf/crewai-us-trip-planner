from crewai.tools import BaseTool
from typing import Type
import os
import json
import requests
from pydantic import BaseModel, Field


class SearchToolInput(BaseModel):
    """Input schema for SearchTool."""
    query: str = Field(..., description="The search query to send to Google")


class SearchTool(BaseTool):
    name: str = "Search Google"
    description: str = (
        "A tool that performs Google searches using the Serper.dev API. "
        "Useful for finding up-to-date information about any topic. "
        "Input should be a search query string."
    )
    args_schema: Type[BaseModel] = SearchToolInput

    def _run(self, query: str) -> str:
        try:
            api_key = os.getenv("SERPER_API_KEY")
            if not api_key:
                return "Error: SERPER_API_KEY not found in environment variables"

            headers = {
                "X-API-KEY": api_key,
                "Content-Type": "application/json"
            }

            url = "https://google.serper.dev/search"
            payload = json.dumps({"q": query})

            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()  # Raise exception for bad status codes

            search_results = response.json()

            # Format the results into a readable string
            formatted_results = []
            if "organic" in search_results:
                for result in search_results["organic"][:5]:  # Get top 5 results
                    title = result.get("title", "No title")
                    snippet = result.get("snippet", "No snippet")
                    link = result.get("link", "No link")
                    formatted_results.append(
                        f"Title: {title}\nSnippet: {snippet}\nLink: {link}\n")

            return "\n".join(formatted_results) if formatted_results else "No results found"

        except requests.exceptions.RequestException as e:
            return f"Error performing search: {str(e)}"
        except json.JSONDecodeError:
            return "Error parsing search results"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
