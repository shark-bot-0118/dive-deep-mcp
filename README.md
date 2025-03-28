# Think MCP

An implementation of Anthropic's "think" tool using the Model Context Protocol (MCP). This tool uses OpenAI's o3-mini model to provide deep thinking capabilities through a standardized MCP interface.

## Features

- Implements the MCP protocol for the "think" capability
- Uses OpenAI's o3-mini model for deep thinking analysis
- Runs using stdio transport for seamless integration with other tools
- Comprehensive error handling and logging

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set up your OpenAI API key:

Create or edit the `.env` file in the root directory with:

```
OPENAI_API_KEY=your_api_key_here
```
3. Configure Claude Desktop to use the MCP server:

   Open your Claude Desktop configuration file:
   
   **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
   **Windows**: `C:\Users\YourUsername\AppData\Roaming\Claude\claude_desktop_config.json`

   Add the following configuration:
   ```json
   {
     "mcpServers": {
       "think": {
         "command": "/full/path/to/python",
         "args": [
           "/full/path/to/main.py"
         ]
       }
     }
   }
   ```
   
   Be sure to replace the paths with the actual locations on your system.

4. Restart Claude Desktop
