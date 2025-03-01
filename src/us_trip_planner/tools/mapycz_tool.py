from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import requests
import json
import os


class MapyCzToolInput(BaseModel):
    """Input schema for MapyCzTool."""
    start_point: str = Field(...,
                             description="Starting point coordinates in format 'lat,lon'")
    end_point: str = Field(...,
                           description="Ending point coordinates in format 'lat,lon'")
    mode: str = Field(
        default="car_fast_traffic", description="Transportation mode: car_fast, car_fast_traffic, car_short")


class MapyCzTool(BaseTool):
    name: str = "MapyCz Route Planner"
    description: str = (
        "A tool that uses the Mapy.cz API to plan a route between two points, returning distance and duration."
        "Input should be start and end coordinates in 'lat,lon' format and optionally a mode of transport."
    )
    args_schema: Type[BaseModel] = MapyCzToolInput

    def _run(self, start_point: str, end_point: str, mode: str = "car") -> str:
        try:
            # Parse coordinates
            start_lat, start_lon = map(float, start_point.split(","))
            end_lat, end_lon = map(float, end_point.split(","))

            # API endpoint

            # Get API key from environment
            api_key = os.getenv('MAPYCZ_API_KEY')
            if not api_key:
                raise ValueError("MAPYCZ_API_KEY environment variable not set")

            # Add API key to headers
            headers = {
                "accept": "application/json",
                "X-Mapy-Api-Key": api_key
            }

            url = f"https://api.mapy.cz/v1/routing/route?start={start_lon}&start={start_lat}&end={end_lon}&end={end_lat}&routeType={mode}&apikey={api_key}"
            print(f"Debug mapycz URL: {url}")

            response = requests.get(url, headers=headers)
            response.raise_for_status()

            route_data = response.json()

            # Format response
            if "length" in route_data:
                distance = route_data.get("length", 0) / 1000  # Convert to km
                duration = route_data.get(
                    "duration", 0) / 60  # Convert to minutes

                return (
                    f"Route found:\n"
                    f"Distance: {distance:.1f} km\n"
                    f"Duration: {duration:.1f} minutes"
                )
            else:
                return "No route found"

        except ValueError as e:
            return f"Error parsing coordinates or missing API key: {str(e)}"
        except requests.exceptions.RequestException as e:
            return f"Error making request: {str(e)}"
        except json.JSONDecodeError:
            return "Error parsing response from API"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
