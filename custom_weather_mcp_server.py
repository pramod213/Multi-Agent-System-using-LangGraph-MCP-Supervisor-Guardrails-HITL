# from mcp.server.fastmcp import FastMCP
# import requests
# import os
# from dotenv import load_dotenv

# load_dotenv()

# mcp = FastMCP("Weather MCP Server")

# OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")



# @mcp.tool()
# def get_current_weather(city: str):

#     response = requests.get(
#         "https://api.openweathermap.org/data/2.5/weather",
#         params={
#             "q": city,
#             "appid": OPENWEATHER_API_KEY,
#             "units": "metric"
#         }
#     )

#     data = response.json()

#     if response.status_code != 200:
#         return data

#     return {
#         "city": data["name"],
#         "temperature_c": data["main"]["temp"],
#         "feels_like_c": data["main"]["feels_like"],
#         "humidity": data["main"]["humidity"],
#         "condition": data["weather"][0]["description"],
#         "wind_speed": data["wind"]["speed"]
#     }




# @mcp.tool()
# def get_forecast(city: str):

#     url = (
#         "https://api.openweathermap.org/data/2.5/forecast"
#     )

#     params = {
#         "q": city,
#         "appid": OPENWEATHER_API_KEY,
#         "units": "metric"
#     }

#     response = requests.get(
#         url,
#         params=params
#     )

#     data = response.json()

#     forecast = []

#     # Return first 5 forecast entries
#     for item in data["list"][:5]:

#         forecast.append(
#             {
#                 "datetime": item["dt_txt"],
#                 "temperature": item["main"]["temp"],
#                 "weather": item["weather"][0]["description"]
#             }
#         )

#     return {
#         "city": city,
#         "forecast": forecast
#     }



# # This mcp server is not running in any remote server it is running in local.
# # So to run it use:

# if __name__ == "__main__":
#     mcp.run()










import os
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

mcp = FastMCP("Weather MCP Server")

OPENWEATHER_API_KEY = os.getenv(
    "OPENWEATHER_API_KEY"
)

REQUEST_TIMEOUT_SECONDS = 20


def _get_api_key() -> str:
    if not OPENWEATHER_API_KEY:
        raise RuntimeError(
            "OPENWEATHER_API_KEY is missing "
            "from the project .env file."
        )

    return OPENWEATHER_API_KEY


def _request_json(
    url: str,
    params: dict[str, Any],
) -> dict[str, Any]:
    try:
        response = requests.get(
            url,
            params=params,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as exc:
        details = ""

        failed_response = getattr(
            exc,
            "response",
            None,
        )

        if failed_response is not None:
            details = (
                f" Response: "
                f"{failed_response.text[:500]}"
            )

        raise RuntimeError(
            f"OpenWeather request failed: "
            f"{exc}.{details}"
        ) from exc


@mcp.tool()
def get_current_weather(
    city: str,
) -> dict[str, Any]:
    """Return the current weather for a city."""

    city = city.strip()

    if not city:
        raise ValueError(
            "city cannot be empty"
        )

    data = _request_json(
        "https://api.openweathermap.org/data/2.5/weather",
        {
            "q": city,
            "appid": _get_api_key(),
            "units": "metric",
        },
    )

    return {
        "city": data["name"],
        "temperature_c": data["main"]["temp"],
        "feels_like_c": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "condition": data["weather"][0]["description"],
        "wind_speed": data["wind"]["speed"],
    }


@mcp.tool()
def get_forecast(
    city: str,
) -> dict[str, Any]:
    """
    Return the first five three-hour
    forecast entries for a city.
    """

    city = city.strip()

    if not city:
        raise ValueError(
            "city cannot be empty"
        )

    data = _request_json(
        "https://api.openweathermap.org/data/2.5/forecast",
        {
            "q": city,
            "appid": _get_api_key(),
            "units": "metric",
        },
    )

    forecast = [
        {
            "datetime": item["dt_txt"],
            "temperature_c": item["main"]["temp"],
            "condition": item["weather"][0]["description"],
        }
        for item in data.get("list", [])[:5]
    ]

    return {
        "city": data.get(
            "city",
            {},
        ).get(
            "name",
            city,
        ),
        "forecast": forecast,
    }


if __name__ == "__main__":
    # mcp_client.py launches this as a stdio subprocess.
    mcp.run(
        transport="stdio",
    )