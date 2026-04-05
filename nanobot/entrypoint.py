#!/usr/bin/env python3
"""
Entrypoint script for nanobot Docker container.

Reads config.json, injects environment variable values, writes config.resolved.json,
then execs into nanobot gateway.
"""

import json
import os
import sys


def main():
    config_path = "/app/nanobot/config.json"
    resolved_path = "/tmp/nanobot/config.resolved.json"
    workspace = "/app/nanobot/workspace"

    os.makedirs(os.path.dirname(resolved_path), exist_ok=True)

    with open(config_path, "r") as f:
        config = json.load(f)

    # Override provider settings from env vars
    if llm_api_key := os.environ.get("LLM_API_KEY"):
        config["providers"]["custom"]["apiKey"] = llm_api_key

    if llm_api_base_url := os.environ.get("LLM_API_BASE_URL"):
        config["providers"]["custom"]["apiBase"] = llm_api_base_url

    if llm_api_model := os.environ.get("LLM_API_MODEL"):
        config["agents"]["defaults"]["model"] = llm_api_model

    # Override gateway settings
    if nanobot_gateway_host := os.environ.get("NANOBOT_GATEWAY_HOST"):
        config["gateway"]["host"] = nanobot_gateway_host

    if nanobot_gateway_port := os.environ.get("NANOBOT_GATEWAY_PORT"):
        config["gateway"]["port"] = int(nanobot_gateway_port)

    # Configure movie MCP server
    config["tools"]["mcpServers"]["movies"] = {
        "command": "/usr/local/bin/python",
        "args": ["-m", "mcp_movies"],
        "env": {
            "MOVIE_BACKEND_URL": os.environ.get(
                "MOVIE_BACKEND_URL", "http://backend:8000"
            ),
        },
    }

    with open(resolved_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Using config: {resolved_path}", file=sys.stderr)

    os.execvp(
        "nanobot",
        [
            "nanobot",
            "gateway",
            "--config",
            resolved_path,
            "--workspace",
            workspace,
        ],
    )


if __name__ == "__main__":
    main()
