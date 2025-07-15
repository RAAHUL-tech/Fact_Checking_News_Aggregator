# Fact Checking News Aggregator

A multi-agent system that crawls news sources, extracts factual claims, verifies them against Wikipedia/Wikidata, and publishes verified facts to a Jekyll site.

## Architecture

The system consists of 5 main components:

1. **MCP Server** (Port 8000) - Provides tools for claim extraction and verification
2. **Crawler Agent** (Port 5001) - Crawls RSS feeds and extracts news articles
3. **Extractor Agent** (Port 5002) - Extracts factual claims from articles using LLM
4. **Checker Agent** (Port 5003) - Verifies claims against Wikipedia/Wikidata
5. **Publisher Agent** (Port 5004) - Publishes verified facts to Jekyll site

## Setup

### 1. Install Dependencies

```bash
# Using pip
pip install -r requirements.txt

# Or using uv (recommended)
uv sync
```

### 2. Environment Variables

Create a `.env` file in the project root:

```bash
# Required: Groq API Key for LLM-based claim extraction
# Get your API key from: https://console.groq.com/
GROQ_API_KEY=your_groq_api_key_here

# Optional: Override default ports
# MCP_SERVER_PORT=8000
# CRAWLER_PORT=5001
# EXTRACTOR_PORT=5002
# CHECKER_PORT=5003
# PUBLISHER_PORT=5004
```

### 3. Start All Services

```bash
# Start all agents and MCP server
python run_all_agents.py
```

### 4. Run the Orchestrator

In a separate terminal:

```bash
python orchestrator.py
```

## Troubleshooting

### Common Issues

1. **"Expecting value: line 1 column 1 (char 0)" Error**
   - This usually means the MCP server isn't running
   - Make sure to start all services with `python run_all_agents.py`
   - Check that port 8000 is available for the MCP server

2. **"GROQ_API_KEY not found" Error**
   - Set the GROQ_API_KEY environment variable
   - Create a `.env` file with your API key

3. **Agent Communication Errors**
   - Ensure all agents are running on their expected ports
   - Check that no other services are using ports 5001-5004 and 8000
   - Restart all services if needed

4. **Jekyll Build Errors**
   - Make sure Jekyll is installed: `gem install jekyll`
   - The publisher agent will create posts in `jekyll_site/_posts/`

### Manual Testing

To test individual components:

```bash
# Test MCP server
python mcp_server.py

# Test individual agents
python agents/crawler_agent/agent_base.py
python agents/extractor_agent/extractor_agent.py
python agents/fact_checker_agent/fact_checker_agent.py
python agents/publisher_agent/publisher_agent.py
```

### Logs and Debugging

- Each agent runs on its own port and can be accessed directly
- Check the terminal output for each service for error messages
- The orchestrator will show the chain of communication between agents

## Configuration

Each agent has its own `config.yaml` file in its directory:

- `agents/crawler_agent/config.yaml` - RSS feeds and filtering rules
- `agents/extractor_agent/config.yaml` - MCP server connection
- `agents/fact_checker_agent/config.yaml` - MCP server connection
- `agents/publisher_agent/config.yaml` - MCP server connection

## Output

Verified facts are published to the Jekyll site in `jekyll_site/_posts/` as markdown files. The site can be built and served with:

```bash
cd jekyll_site
jekyll build
jekyll serve
```