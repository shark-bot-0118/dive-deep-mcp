import dotenv
import json
import os
import sys
from mcp.server.fastmcp import FastMCP
from typing import List, TypedDict
import google.genai as genai
from google.genai.types import GenerateContentConfig
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

# Gemini clientの初期化
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# デフォルトのモデルを環境変数から読み込む
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

logger.info("Initializing MCP server...")
mcp = FastMCP(
    'Deep Thinking Assistant - MCP server for enhanced reasoning and analysis',
    dependencies=[
        'loguru',
        'google-genai',
    ],
)


@mcp.tool(name='deep_thinking_agent',
           description=DEEP_THINKING_AGENT_DESCRIPTION)
def deep_thinking_agent(
    instructions: str,
    context: str,
    model: str = DEFAULT_MODEL
) -> McpResponse:
    """deep_thinking_agentを実行し、着眼点を提示し思考範囲を拡大します。

    Args:
        context: 思考プロセスのコンテキスト
        model: 使用するモデル名（デフォルト: "gemini-2.0-flash"）
    """
    logger.info(f"Starting deep_thinking_agent with model: {model}")
    logger.debug(f"Instructions: {instructions}")
    logger.debug(f"Context length: {len(context)} characters")
    
    try:
        # システムプロンプトの設定
        content = f"instructions from user: {instructions}\nthinking process: {context}"

        logger.debug("Sending request to Gemini API")
        response = client.models.generate_content(
            model=model,
            contents=content,
            config=GenerateContentConfig(
                system_instruction=DEEP_THINKING_PROMPT,
            ),
        )
        
        logger.info("Successfully received response from deep_thinking_agent")
        return {
            'content': [
                {
                    'type': 'text',
                    'text': response.text,
                }
            ]
        }
    except Exception as e:
        logger.error(f'Error in deep_thinking_agent: {str(e)}', exc_info=True)
        return {
            'content': [{'type': 'text', 'text': f'Error in content generation: {e}'}],
            'isError': True,
        }


@mcp.tool(name='enhancement_agent',
           description=ENHANCEMENT_AGENT_DESCRIPTION)
def enhancement_agent(
    instructions: str,
    code: list[str],
    model: str = DEFAULT_MODEL,
    temperature: float = 0.7
) -> McpResponse:
    """enhancement_agentを実行し、深い思考と分析を提供します。

    Args:
        instructions: レビュー対象のコードに対する指示
        code: コードのリスト
        model: 使用するモデル名（デフォルト: "gemini-2.0-flash"）
        temperature: 生成時の温度パラメータ（デフォルト: 0.7）
    """
    logger.info(f"Starting enhancement_agent with model: {model}")
    logger.debug(f"Instructions: {instructions}")
    logger.debug(f"Number of code files: {len(code)}")
    
    try:
        # コンテンツの準備
        content = f"instructions: {instructions}\ncode: {json.dumps(code, ensure_ascii=False)}"

        logger.debug("Sending request to Gemini API")
        response = client.models.generate_content(
            model=model,
            contents=content,
            config=GenerateContentConfig(
                system_instruction=ADVANCED_ANALYSIS_PROMPT,
                temperature=temperature,
            ),
        )
        
        logger.info("Successfully received response from enhancement_agent")
        return {
            'content': [
                {
                    'type': 'text',
                    'text': response.text,
                }
            ]
        }
    except Exception as e:
        logger.error(f'Error in enhancement_agent: {str(e)}', exc_info=True)
        return {
            'content': [{'type': 'text', 'text': f'Error in content generation: {e}'}],
            'isError': True,
        }


@mcp.tool(name='final_review_agent',
           description=FINAL_REVIEW_AGENT_DESCRIPTION)
def final_review_agent(
    instructions: str,
    code: list[str],
    model: str = DEFAULT_MODEL,
    temperature: float = 0.7
) -> McpResponse:
    """提案された回答や解決策を批判的に分析し、改善点を提示します。

    Args:
        instructions: レビュー対象のコードに対する指示
        code: コードのリスト
        model: 使用するモデル名（デフォルト: "gemini-2.0-flash"）
        temperature: 生成時の温度パラメータ（デフォルト: 0.7）
    """
    logger.info(f"Starting final_review_agent with model: {model}")
    logger.debug(f"Instructions: {instructions}")
    logger.debug(f"Number of code files: {len(code)}")
    
    try:
        # コンテンツの準備
        content = f"instructions: {instructions}\ncode: {json.dumps(code, ensure_ascii=False)}"

        logger.debug("Sending request to Gemini API")
        response = client.models.generate_content(
            model=model,
            contents=content,
            config=GenerateContentConfig(
                system_instruction=DEEP_REVIEW_PROMPT,
                temperature=temperature,
            ),
        )
        
        logger.info("Successfully received response from final_review_agent")
        return {
            'content': [
                {
                    'type': 'text',
                    'text': response.text,
                }
            ]
        }
    except Exception as e:
        logger.error(f'Error in final_review_agent: {str(e)}', exc_info=True)
        return {
            'content': [{'type': 'text', 'text': f'Error in content generation: {e}'}],
            'isError': True,
        }


def main() -> None:
    """Run Dive Deep MCP server."""

    logger.info("Starting Dive Deep MCP server")

    # Run server with default transport (stdio)
    try:
        logger.info("Running server with stdio transport")
        mcp.run()
    except Exception as e:
        logger.critical(f"Failed to start server: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main() 