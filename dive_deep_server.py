import argparse
import dotenv
import json
import os
import sys
from mcp.server.fastmcp import FastMCP
from typing import List, TypedDict
from openai import OpenAI
from logger_config import get_logger
from prompts import (
    DEEP_THINKING_AGENT_DESCRIPTION,
    ENHANCEMENT_AGENT_DESCRIPTION,
    FINAL_REVIEW_AGENT_DESCRIPTION,
    DEEP_THINKING_PROMPT,
    ADVANCED_ANALYSIS_PROMPT,
    DEEP_REVIEW_PROMPT
)


class ContentItem(TypedDict):
    """A TypedDict representing a single content item in an MCP response."""
    type: str
    text: str


class McpResponse(TypedDict, total=False):
    """A TypedDict representing an MCP server response."""
    content: List[ContentItem]
    isError: bool


# ロガーの初期化
logger = get_logger("dive_deep_server")

dotenv.load_dotenv()

# OpenAI clientの初期化
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

logger.info("Initializing MCP server...")
mcp = FastMCP(
    'Deep Thinking Assistant - MCP server for enhanced reasoning and analysis',
    dependencies=[
        'loguru',
        'openai',
    ],
)


@mcp.tool(name='deep_thinking_agent',
           description=DEEP_THINKING_AGENT_DESCRIPTION)
def deep_thinking_agent(
    instructions: str,
    context: str,
    model: str = "o3-mini",
    reasoning_effort: str = "medium" 
) -> McpResponse:
    """deep_thinking_agentを実行し、着眼点を提示し思考範囲を拡大します。

    Args:
        context: 思考プロセスのコンテキスト
        model: 使用するモデル名（デフォルト: "o3-mini"）
        reasoning_effort: medium 
    """
    logger.info(f"Starting deep_thinking_agent with model: {model}")
    logger.debug(f"Instructions: {instructions}")
    logger.debug(f"Context length: {len(context)} characters")
    
    try:
        # システムプロンプトの設定
        final_messages = []
        final_messages.append({"role": "system", "content": DEEP_THINKING_PROMPT})
        prompt = {
            "role": "user",
            "content": f"instructions from user: {instructions}\nthinking process: {context}"
        }
        final_messages.append(prompt)

        logger.debug("Sending request to OpenAI API")
        response = client.chat.completions.create(
            model=model,
            messages=final_messages,
            reasoning_effort=reasoning_effort
        )
        
        logger.info("Successfully received response from deep_thinking_agent")
        return {
            'content': [
                {
                    'type': 'text',
                    'text': response.choices[0].message.content,
                }
            ]
        }
    except Exception as e:
        logger.error(f'Error in deep_thinking_agent: {str(e)}', exc_info=True)
        return {
            'content': [{'type': 'text', 'text': f'Error in chat completion: {e}'}],
            'isError': True,
        }


@mcp.tool(name='enhancement_agent',
           description=ENHANCEMENT_AGENT_DESCRIPTION)
def enhancement_agent(
    instructions: str,
    code: list[str],
    model: str = "gpt-4",
    temperature: float = 0.7
) -> McpResponse:
    """enhancement_agentを実行し、深い思考と分析を提供します。

    Args:
        instructions: レビュー対象のコードに対する指示
        code: コードのリスト
        model: 使用するモデル名（デフォルト: "gpt-4"）
        temperature: 生成時の温度パラメータ（デフォルト: 0.7）
        """
    logger.info(f"Starting enhancement_agent with model: {model}")
    logger.debug(f"Instructions: {instructions}")
    logger.debug(f"Number of code files: {len(code)}")
    
    try:
        # システムプロンプトの設定
        final_messages = []
        final_messages.append({"role": "system", "content": ADVANCED_ANALYSIS_PROMPT})
        prompt = {
            "role": "user",
            "content": f"instructions: {instructions}\ncode: {json.dumps(code, ensure_ascii=False)}"
        }
        final_messages.append(prompt)

        logger.debug("Sending request to OpenAI API")
        response = client.chat.completions.create(
            model=model,
            messages=final_messages,
            temperature=temperature,
        )
        
        logger.info("Successfully received response from enhancement_agent")
        return {
            'content': [
                {
                    'type': 'text',
                    'text': response.choices[0].message.content,
                }
            ]
        }
    except Exception as e:
        logger.error(f'Error in enhancement_agent: {str(e)}', exc_info=True)
        return {
            'content': [{'type': 'text', 'text': f'Error in chat completion: {e}'}],
            'isError': True,
        }


@mcp.tool(name='final_review_agent',
           description=FINAL_REVIEW_AGENT_DESCRIPTION)
def final_review_agent(
    instructions: str,
    code: list[str],
    model: str = "gpt-4",
    temperature: float = 0.7
) -> McpResponse:
    """提案された回答や解決策を批判的に分析し、改善点を提示します。

    Args:
        instructions: レビュー対象のコードに対する指示
        code: コードのリスト
        model: 使用するモデル名（デフォルト: "gpt-4"）
        temperature: 生成時の温度パラメータ（デフォルト: 0.7）
    """
    logger.info(f"Starting final_review_agent with model: {model}")
    logger.debug(f"Instructions: {instructions}")
    logger.debug(f"Number of code files: {len(code)}")
    
    try:
        # 分析用のプロンプトを構築
        final_messages = []
        final_messages.append({"role": "system", "content": DEEP_REVIEW_PROMPT})
        prompt = {
            "role": "user",
            "content": f"instructions: {instructions}\ncode: {json.dumps(code, ensure_ascii=False)}"
        }
        final_messages.append(prompt)

        logger.debug("Sending request to OpenAI API")
        response = client.chat.completions.create(
            model=model,
            messages=final_messages,
            temperature=temperature,
        )
        
        logger.info("Successfully received response from final_review_agent")
        return {
            'content': [
                {
                    'type': 'text',
                    'text': response.choices[0].message.content,
                }
            ]
        }
    except Exception as e:
        logger.error(f'Error in final_review_agent: {str(e)}', exc_info=True)
        return {
            'content': [{'type': 'text', 'text': f'Error in response analysis: {e}'}],
            'isError': True,
        }


def main() -> None:
    """Run Dive Deep MCP server."""
    parser = argparse.ArgumentParser(
        description='A Deep Thinking Assistant - MCP server for enhanced reasoning and analysis'
    )
    parser.add_argument('--sse', action='store_true', help='Use SSE transport')
    parser.add_argument('--port', type=int, default=8889, help='Port to run the server on')
    args = parser.parse_args()

    logger.info("Starting Dive Deep MCP server")
    logger.debug(f"Arguments: SSE={args.sse}, Port={args.port}")

    # Set up logging
    logger.remove()
    logger.add(sys.stderr, level='DEBUG')

    # Run server with appropriate transport
    try:
        if args.sse:
            logger.info(f"Running server with SSE transport on port {args.port}")
            mcp.settings.port = args.port
            mcp.run(transport='sse')
        else:
            logger.info("Running server with default transport")
            mcp.run()
    except Exception as e:
        logger.critical(f"Failed to start server: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main() 