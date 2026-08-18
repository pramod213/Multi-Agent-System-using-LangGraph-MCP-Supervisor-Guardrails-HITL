

# import sys
# import os
# import asyncio
# import certifi
# from dotenv import load_dotenv
# from pydantic import SecretStr
# from langchain_mcp_adapters.client import MultiServerMCPClient
# from langchain_groq import ChatGroq


# # Prevent SSL certificate issues on Windows
# os.environ["SSL_CERT_FILE"] = certifi.where()
# os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

# load_dotenv()

# TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
# AVIATIONSTACK_API_KEY = os.getenv("AVIATION_STACK_API_KEY")
# OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# if not GROQ_API_KEY:
#     raise ValueError("GROQ_API_KEY is not set in the .env file")

# # Initializing the LLM
# llm = ChatGroq(
#     model="llama-3.3-70b-versatile",
#     api_key=SecretStr(GROQ_API_KEY)
# )


# server_config = {
#     "tavily": {
#         "transport": "streamable_http",
#         "url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}",
#     },

#     "aviationstack": {
#         "transport": "stdio",
#         "command": "uvx",
#         "args": [
#             "--python",
#             "3.13",
#             "--with",
#             "mcp<2",
#             "aviationstack-mcp",
#         ],
#         "env": {
#             "AVIATION_STACK_API_KEY": AVIATIONSTACK_API_KEY,
#         },
#     },
    
#     "weather": {
#             "transport": "stdio",
            
#             "command": r"D:\Projects\Agentic AI Projects\Multi-Agent-System-using-LangGraph-MCP-Supervisor-Guardrails-HITL\tripenv\Scripts\python.exe",
#             "args": [
#                 r"D:\Projects\Agentic AI Projects\Multi-Agent-System-using-LangGraph-MCP-Supervisor-Guardrails-HITL\weather_mcp_server.py"
#             ],

#             "env": {
#                 "OPENWEATHER_API_KEY": OPENWEATHER_API_KEY
#             }
#         }
# }


# client = MultiServerMCPClient(server_config)


# # Check if the client is connected to all servers
# async def get_all_tools():
#     tools = await client.get_tools()

#     print("\nAvailable MCP Tools:\n")

#     for tool in tools:
#         print(tool.name)




# ###############################################
# # Tavily and Aviation Tools
# ###############################################

# from typing import Any


# search_tool = None
# aviation_tools = {}


# async def initialize_mcp():

#     global search_tool
#     global aviation_tools

#     if search_tool is not None and aviation_tools:
#         return

#     tools = await client.get_tools()

#     print("\nAvailable MCP Tools:\n")

#     for tool in tools:
#         print(tool.name)

#     search_tool = next(
#         (
#             tool
#             for tool in tools
#             if tool.name == "tavily_search"
#         ),
#         None,
#     )

#     aviation_tools = {
#         tool.name: tool
#         for tool in tools
#         if tool.name != "tavily_search"
#     }


# async def tavily_mcp_search(query: str) -> Any:
#     await initialize_mcp()

#     if search_tool is None:
#         raise RuntimeError(
#             "Tavily search tool could not be initialized."
#         )

#     result = await search_tool.ainvoke(
#         {
#             "query": query
#         }
#     )

#     return result


# async def aviation_mcp_call(
#     tool_name: str,
#     tool_args: dict[str, Any] | None = None,
# ) -> Any:

#     await initialize_mcp()

#     tool = aviation_tools.get(tool_name)

#     if tool is None:
#         raise ValueError(
#             f"Aviation MCP tool '{tool_name}' was not found."
#         )

#     result = await tool.ainvoke(
#         tool_args or {}
#     )

#     return result



# # ==========================================
# # Weather MCP tools
# # ==========================================

# weather_tool = None
# forecast_tool = None


# async def initialize_weather_tools():
#     global weather_tool
#     global forecast_tool

#     if (
#         weather_tool is not None
#         and forecast_tool is not None
#     ):
#         return

#     tools = await client.get_tools()

#     weather_tool = next(
#         t for t in tools
#         if t.name == "get_current_weather"
#     )

#     forecast_tool = next(
#         t for t in tools
#         if t.name == "get_forecast"
#     )


# async def weather_mcp_search(city: str):
    
#     await initialize_weather_tools()
    
#     if weather_tool is None:
#         raise RuntimeError("Weather tool was not initialized.")

#     result = await weather_tool.ainvoke(
#         {
#             "city": city
#         }
#     )

#     return result


# async def forecast_mcp_search(city: str):
    
#     await initialize_weather_tools()
    
#     if forecast_tool is None:
#         raise RuntimeError("Forecast tool was not initialized.")

#     result = await forecast_tool.ainvoke(
#         {
#             "city": city
#         }
#     )

#     return result


# ########################################################
# # Destination Extractor
# ########################################################

# def extract_destination(query: str) -> str:
    
#     prompt = f"""
#     Extract only the destination city or country.
    
#     Query:
#     {query}
    
#     Return only destination name.
    
#     """
    
#     response = llm.invoke(prompt)
    
#     return str(response.content).strip()












import os
import shutil
import sys
from pathlib import Path
from typing import Any
from pydantic import SecretStr

import certifi
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.runnables import RunnableConfig


# =========================================================
# Environment setup
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Support both environment-variable names.
AVIATION_STACK_API_KEY = (
    os.getenv("AVIATION_STACK_API_KEY")
    or os.getenv("AVIATIONSTACK_API_KEY")
)

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

WEATHER_SERVER_PATH = BASE_DIR / "custom_weather_mcp_server.py"
UVX_COMMAND = shutil.which("uvx") or "uvx"


def _require_env(name: str, value: str | None) -> str:
    """Return an environment value or raise a readable setup error."""

    if not value:
        raise RuntimeError(
            f"{name} is missing. "
            f"Add {name}=your_key to the project .env file."
        )

    return value


def _subprocess_env(**updates: str | None) -> dict[str, str]:
    """
    Preserve the current Windows/Conda environment and add MCP API keys.
    """

    env = os.environ.copy()

    for key, value in updates.items():
        if value:
            env[key] = value

    return env


# =========================================================
# LLM
# =========================================================

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=SecretStr(GROQ_API_KEY) if GROQ_API_KEY else None,
)


# =========================================================
# MCP client
# =========================================================

client = MultiServerMCPClient(
    {
        "tavily": {
            "transport": "streamable_http",
            "url": (
                "https://mcp.tavily.com/mcp/"
                f"?tavilyApiKey={TAVILY_API_KEY or ''}"
            ),
        },

        "aviationstack": {
            "transport": "stdio",
            "command": UVX_COMMAND,
            "args": [
                "aviationstack-mcp",
            ],
            "env": _subprocess_env(
                AVIATION_STACK_API_KEY=AVIATION_STACK_API_KEY,
            ),
        },

        "weather": {
            "transport": "stdio",

            # Uses the Python executable from the active Conda environment.
            "command": sys.executable,

            # Uses the weather server inside the current project folder.
            "args": [
                str(WEATHER_SERVER_PATH),
            ],

            "env": _subprocess_env(
                OPENWEATHER_API_KEY=OPENWEATHER_API_KEY,
            ),
        },
    }
)


async def _get_server_tool(
    server_name: str,
    tool_name: str,
):
    """
    Load one tool from one MCP server.

    This prevents a broken weather or AviationStack server from
    crashing an unrelated Tavily request.
    """

    if server_name == "tavily":
        _require_env(
            "TAVILY_API_KEY",
            TAVILY_API_KEY,
        )

    elif server_name == "aviationstack":
        _require_env(
            "AVIATION_STACK_API_KEY",
            AVIATION_STACK_API_KEY,
        )

        if shutil.which("uvx") is None:
            raise RuntimeError(
                "uvx was not found. Install uv, reopen the terminal, "
                "activate the travel environment, and run "
                "`uvx --version`."
            )

    elif server_name == "weather":
        _require_env(
            "OPENWEATHER_API_KEY",
            OPENWEATHER_API_KEY,
        )

        if not WEATHER_SERVER_PATH.is_file():
            raise FileNotFoundError(
                f"Weather MCP server not found: "
                f"{WEATHER_SERVER_PATH}"
            )

    # Important: load only the requested MCP server.
    tools = await client.get_tools(
        server_name=server_name,
    )

    tool = next(
        (
            item
            for item in tools
            if item.name == tool_name
        ),
        None,
    )

    if tool is None:
        available_tools = (
            ", ".join(
                sorted(item.name for item in tools)
            )
            or "none"
        )

        raise RuntimeError(
            f"MCP tool '{tool_name}' was not found "
            f"on server '{server_name}'. "
            f"Available tools: {available_tools}"
        )

    return tool


# =========================================================
# MCP connection test
# =========================================================

async def get_all_tools() -> None:
    """
    Test every MCP server independently.

    One failed server will not stop the remaining tests.
    """

    for server_name in (
        "tavily",
        "aviationstack",
        "weather",
    ):
        try:
            tools = await client.get_tools(
                server_name=server_name,
            )

            tool_names = (
                ", ".join(
                    tool.name
                    for tool in tools
                )
                or "no tools"
            )

            print(
                f"{server_name}: OK -> {tool_names}"
            )

        except Exception as exc:
            print(
                f"{server_name}: FAILED -> "
                f"{type(exc).__name__}: {exc}"
            )


# =========================================================
# Tavily MCP
# =========================================================

async def tavily_mcp_search(query: str):
    search_tool = await _get_server_tool(
        "tavily",
        "tavily_search",
    )

    return await search_tool.ainvoke(
        {
            "query": query,
        }
    )


# =========================================================
# AviationStack MCP
# =========================================================

async def aviation_mcp_call(
    tool_name: str,
    tool_args: dict[str, Any] | None = None,
):
    aviation_tool = await _get_server_tool(
        "aviationstack",
        tool_name,
    )

    return await aviation_tool.ainvoke(
        tool_args or {}
    )


# =========================================================
# Weather MCP
# =========================================================

async def weather_mcp_search(city: str):
    weather_tool = await _get_server_tool(
        "weather",
        "get_current_weather",
    )

    return await weather_tool.ainvoke(
        {
            "city": city,
        }
    )


async def forecast_mcp_search(city: str):
    forecast_tool = await _get_server_tool(
        "weather",
        "get_forecast",
    )

    return await forecast_tool.ainvoke(
        {
            "city": city,
        }
    )


# =========================================================
# Destination extractor
# =========================================================

def extract_destination(query: str) -> str:
    prompt = f"""
Extract only the destination city or country from the travel request.

Travel request:
{query}

Return only the destination name.
Do not add any explanation.
"""

    response = llm.invoke(prompt)

    destination = str(
        response.content
    ).strip()

    if not destination:
        raise ValueError(
            "The destination could not be extracted."
        )

    return destination