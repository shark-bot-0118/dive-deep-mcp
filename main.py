#!/usr/bin/env python3
"""
Think MCP - An implementation of a "think" tool using OpenAI's o3-mini model.
The tool implements a multi-step thinking capability through an MCP interface.
With enhanced security features and robust failure detection.
"""

import os
import sys
import json
import time
import signal
import logging
import re
import hashlib
import requests
from typing import Dict, Any, Optional, Union, List, Tuple
from datetime import datetime, timedelta
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("think-mcp")

# Load environment variables
load_dotenv()

# Configuration
DEFAULT_MODEL = "o3-mini"  # Default to o3-mini model
DEFAULT_MAX_TOKENS = 1000
DEFAULT_TEMPERATURE = 0.7
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
TIMEOUT = 25  # seconds
MAX_QUERY_LENGTH = 8000  # Maximum allowed query length
ALLOWED_MODELS = ["o3-mini"]
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Security features
UNSAFE_PATTERN = re.compile(r'(sudo|rm\s+-rf|/etc/passwd|/etc/shadow|eval\(|exec\(|system\()')
API_KEY_HASH = hashlib.sha256(OPENAI_API_KEY.encode()).hexdigest()[:8] if OPENAI_API_KEY else None

# Rate limiting
class RateLimiter:
    def __init__(self, max_calls: int = 10, time_frame: int = 60):
        self.max_calls = max_calls  # Maximum calls allowed in time_frame
        self.time_frame = time_frame  # Time frame in seconds
        self.calls: List[datetime] = []
    
    def is_allowed(self) -> bool:
        """Check if a new call is allowed based on rate limiting rules."""
        now = datetime.now()
        # Remove calls outside the time frame
        self.calls = [call for call in self.calls if now - call < timedelta(seconds=self.time_frame)]
        # Check if we're under the limit
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        return False

# Create rate limiter - 5 calls per minute
rate_limiter = RateLimiter(max_calls=5, time_frame=60)

# Custom exceptions for better error handling
class ThinkMCPError(Exception):
    """Base exception for Think MCP errors."""
    pass

class RateLimitExceededError(ThinkMCPError):
    """Exception raised when rate limit is exceeded."""
    pass

class SecurityViolationError(ThinkMCPError):
    """Exception raised when a security violation is detected."""
    pass

class ModelUnavailableError(ThinkMCPError):
    """Exception raised when a requested model is unavailable."""
    pass

# Handle SIGINT (Ctrl+C) gracefully
def signal_handler(sig, frame):
    logger.info("Received signal %s. Shutting down think MCP gracefully...", sig)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)  # Also handle SIGTERM

# Utility functions
def sanitize_input(text: str) -> str:
    """Sanitize input to prevent injection attacks."""
    # Remove any potentially harmful code patterns
    return re.sub(r'[^\w\s.,?!;:()\[\]{}\'"`-]', '', text)

def validate_model(model: str) -> bool:
    """Validate that the requested model is allowed."""
    return model in ALLOWED_MODELS

def check_query_safety(query: str) -> Tuple[bool, str]:
    """Check if a query contains potentially unsafe content."""
    if UNSAFE_PATTERN.search(query):
        return False, "Query contains potentially unsafe patterns"
    return True, ""

# Utility functions for API parameter consistency
def get_model_parameters(model: str, max_tokens: Optional[int], temperature: Optional[float]) -> Dict[str, Any]:
    """Get the correct parameters for a specific model to handle API differences."""
    params = {}
    
    # Add token limit parameter using the correct name based on model
    if max_tokens is not None:
        params["max_completion_tokens"] = max_tokens
    
    # o3-mini doesn't support temperature parameter
    if temperature is not None and model != "o3-mini":
        params["temperature"] = temperature
        
    return params

def call_openai_api(prompt: str, model: str, max_completion_tokens: Optional[int], temperature: Optional[float] = None) -> Dict[str, Any]:
    """Make a call to the OpenAI API with retry logic and failure detection."""
    if not OPENAI_API_KEY:
        raise ThinkMCPError("OPENAI_API_KEY not configured in environment")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    system_prompt = """You are an analytical thinking assistant designed to help users explore complex topics. When a user shares their thoughts, your role is to:

1. Break down the problem into clear, manageable components
2. Provide valuable context that enriches their understanding
3. Identify connections or implications they may have missed
4. Ask thoughtful questions that deepen their analysis
5. Suggest alternative perspectives when appropriate

Your goal is not to solve problems for users, but to enhance their thinking process by offering structured analysis and relevant insights. Respond in a clear, thoughtful manner that respects the user's level of expertise while adding substantive value to their exploration."""
    
    # Build API request with correct parameters
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    }
    
    # Add model-specific parameters
    model_params = get_model_parameters(model, max_completion_tokens, temperature)
    data.update(model_params)
    
    logger.info(f"Sending request to OpenAI API: {json.dumps(data)}")
    
    # Implement retry logic with exponential backoff
    for attempt in range(MAX_RETRIES):
        try:
            # Use the OpenAI API endpoint
            api_url = "https://api.openai.com/v1/chat/completions"
            
            response = requests.post(
                api_url,
                headers=headers,
                json=data,
                timeout=TIMEOUT
            )
            
            # Log response status
            logger.info(f"API response status: {response.status_code}")
            
            # Check for various error conditions
            if response.status_code == 429:
                logger.warning(f"Rate limit exceeded (attempt {attempt+1}/{MAX_RETRIES})")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY * (2 ** attempt))  # Exponential backoff
                    continue
                else:
                    raise ThinkMCPError("Rate limit exceeded after maximum retries")
                    
            elif response.status_code == 401:
                raise ThinkMCPError("API key is invalid or expired")
                
            elif response.status_code == 404:
                raise ModelUnavailableError(f"Model '{model}' not found")
                
            elif response.status_code != 200:
                error_message = f"API request failed with status code {response.status_code}"
                try:
                    error_detail = response.json()
                    logger.error(f"API error response: {json.dumps(error_detail)}")
                    error_message += f": {json.dumps(error_detail)}"
                except:
                    error_message += f": {response.text}"
                    logger.error(f"API error response text: {response.text}")
                
                if attempt < MAX_RETRIES - 1:
                    logger.warning(f"{error_message} (attempt {attempt+1}/{MAX_RETRIES})")
                    time.sleep(RETRY_DELAY * (2 ** attempt))
                    continue
                else:
                    raise ThinkMCPError(error_message)
            
            # Success case
            result = response.json()
            
            # Verify response structure
            if "choices" not in result or not result["choices"] or "message" not in result["choices"][0]:
                raise ThinkMCPError("Invalid response structure from API")
                
            return result
            
        except requests.exceptions.Timeout:
            logger.warning(f"Request to OpenAI API timed out (attempt {attempt+1}/{MAX_RETRIES})")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (2 ** attempt))
            else:
                raise ThinkMCPError("Request to AI model timed out after maximum retries")
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"Network error: {str(e)} (attempt {attempt+1}/{MAX_RETRIES})")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (2 ** attempt))
            else:
                raise ThinkMCPError(f"Network error after maximum retries: {str(e)}")
    
    # This should not be reached due to the raises in the loop, but adding as fallback
    raise ThinkMCPError("Failed to get response after maximum retries")

# Create an MCP instance with appropriate configuration
mcp = FastMCP(
    name="think",
    timeout=45  # Increased timeout to accommodate retry logic
)

@mcp.tool("think",
description="""
The Deep Thinking Tool enables LLMs to perform extended reasoning processes on complex problems within their existing knowledge base, creating a dedicated computational space for multi-step analysis without retrieving new external information. It excels at breaking down intricate concepts, exploring competing hypotheses, recognizing subtle patterns, and maintaining multiple variables simultaneously throughout extended reasoning chains. This tool is ideal for mathematical proofs, complex system analysis, ethical deliberations, and creative problem-solving that requires connecting disparate knowledge domains. While powerful for reasoning through available information, it operates within the model's pre-existing knowledge boundaries and cannot compensate for fundamental knowledge gaps.
Use it when you need to perform a multi-step analysis on a complex problem.
""")
def think(query: Union[str, Dict[str, Any]], model: Optional[str] = DEFAULT_MODEL, 
          max_tokens: Optional[int] = DEFAULT_MAX_TOKENS, 
          temperature: Optional[float] = DEFAULT_TEMPERATURE) -> Dict[str, Any]:
    """
    Generate deep analytical thinking on a given query using a language model.
    
    This tool uses OpenAI's o3-mini model to generate
    thoughtful analysis, reasoning, and insights about the provided query.
    
    Args:
        query: The question or topic to think deeply about (can be string or dict)
        model: The model to use for thinking (default: "o3-mini")
        max_tokens: Maximum tokens in the response (default: 1000)
        temperature: Temperature for response generation (not used with o3-mini)
        
    Returns:
        A dictionary containing the thinking result and metadata
    """
    start_time = time.time()
    
    try:
        # Handle dict input for query
        if isinstance(query, dict):
            # Check for 'query' field
            if 'query' in query:
                query_text = query['query']
                
                # Check for optional parameters in the dict
                if 'model' in query and query['model'] is not None:
                    model = query['model']
                if 'max_tokens' in query and query['max_tokens'] is not None:
                    max_tokens = query['max_tokens']
                # Ignore temperature if model is o3-mini
                if 'temperature' in query and query['temperature'] is not None:
                    temperature = query['temperature']
            else:
                return {
                    "status": "error",
                    "message": "Query dict must contain a 'query' key"
                }
        else:
            query_text = query
                
        # Generate a request ID after processing the query
        request_id = hashlib.md5(f"{query_text}:{time.time()}".encode()).hexdigest()[:8]
        
        # Rate limiting check
        if not rate_limiter.is_allowed():
            logger.warning(f"[{request_id}] Rate limit exceeded")
            return {
                "status": "error",
                "message": "Rate limit exceeded. Please try again later.",
                "request_id": request_id
            }
        
        # Validate and sanitize input
        if not query_text or not isinstance(query_text, str):
            return {
                "status": "error", 
                "message": "Query must be a non-empty string",
                "request_id": request_id
            }
        
        if len(query_text) > MAX_QUERY_LENGTH:
            return {
                "status": "error",
                "message": f"Query exceeds maximum length of {MAX_QUERY_LENGTH} characters",
                "request_id": request_id
            }
        
        # Sanitize the query
        sanitized_query = sanitize_input(query_text)
        
        # Security check
        is_safe, safety_message = check_query_safety(query_text)
        if not is_safe:
            logger.warning(f"[{request_id}] Security violation: {safety_message}")
            return {
                "status": "error",
                "message": "Your query contains potentially unsafe content and was rejected",
                "request_id": request_id
            }
        
        # Validate model
        if not validate_model(model):
            available_models = ", ".join(ALLOWED_MODELS)
            return {
                "status": "error",
                "message": f"Invalid model specified. Allowed models: {available_models}",
                "request_id": request_id
            }
            
        # Check for API key
        if not OPENAI_API_KEY:
            logger.error(f"[{request_id}] API key not configured")
            return {
                "status": "error", 
                "message": "API key not configured. Please set OPENAI_API_KEY in environment.",
                "request_id": request_id
            }
        
        # Log the operation (without sensitive data)
        logger.info(f"[{request_id}] Generating thoughts using model: {model}")
        
        # Make the API request with retry logic
        try:
            result = call_openai_api(
                sanitized_query, 
                model, 
                max_tokens,
                temperature
            )
            
            thinking = result["choices"][0]["message"]["content"]
            token_usage = result.get("usage", {})
            
            # Calculate metrics
            elapsed_time = time.time() - start_time
            
            return {
                "status": "success",
                "thinking": thinking,
                "model_used": model,
                "token_usage": token_usage,
                "request_id": request_id,
                "elapsed_time": round(elapsed_time, 2)
            }
            
        except ModelUnavailableError as e:
            logger.error(f"[{request_id}] Model error: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "request_id": request_id
            }
            
        except ThinkMCPError as e:
            logger.error(f"[{request_id}] API error: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "request_id": request_id
            }
            
    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.exception(f"[{request_id}] Unexpected error: {str(e)}")
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}",
            "request_id": request_id,
            "elapsed_time": round(elapsed_time, 2)
        }

@mcp.tool()
def query_thinking(query_json: Dict[str, Any], model: Optional[str] = DEFAULT_MODEL,
                   max_tokens: Optional[int] = DEFAULT_MAX_TOKENS, 
                   temperature: Optional[float] = None) -> Dict[str, Any]:
    """
    Process a query from a JSON object and return thinking results.
    
    This is a specialized version of the think tool that handles queries sent as JSON objects
    with a 'query' field.
    
    Args:
        query_json: A JSON object with a 'query' field containing the question to analyze
        model: The model to use for thinking (default: "o3-mini")
        max_tokens: Maximum tokens in the response (default: 1000)
        temperature: Temperature for response generation (not used with o3-mini)
        
    Returns:
        A dictionary containing the thinking result and metadata
    """
    # Simply pass the entire JSON object to the think function which will handle extracting the query
    # and any optional parameters
    return think(query_json, model, max_tokens, temperature)

def main() -> None:
    """Main entry point for the MCP"""
    # Check if API key is configured
    if not OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY is not configured. The MCP will run but API calls will fail.")
        logger.warning("Set the API key in the .env file or environment variables.")
    else:
        logger.info(f"API key configured (hash: {API_KEY_HASH})")
    
    try:
        logger.info("Starting Think MCP with stdio transport")
        logger.info(f"Allowed models: {', '.join(ALLOWED_MODELS)}")
        logger.info(f"Rate limiting: {rate_limiter.max_calls} calls per {rate_limiter.time_frame} seconds")
        
        # Run with stdio transport for integration with other tools
        mcp.run(transport='stdio')
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down...")
    except Exception as e:
        logger.exception("Error in Think MCP: %s", str(e))
    finally:
        logger.info("Think MCP shutdown complete")

if __name__ == "__main__":
    main()
