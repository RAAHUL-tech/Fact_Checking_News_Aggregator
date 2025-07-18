# Fact-Checking News Aggregator

A multi-agent system that automatically crawls news sources, extracts factual claims, verifies them against reliable sources, and publishes verified results to a Jekyll website.

## 🎯 Project Description

This project implements an automated fact-checking pipeline using multiple AI agents that work together to:
1. **Crawl** news sources for articles
2. **Extract** factual claims from articles
3. **Verify** claims against reliable sources
4. **Publish** verified results to a Jekyll website

The system uses the **A2A (Agent-to-Agent) protocol** for inter-agent communication and **MCP (Model Context Protocol)** for external tool integration, creating a robust and scalable fact-checking infrastructure.

## 🏗️ Architecture

### Multi-Agent System
- **Orchestrator Agent**: Coordinates the entire pipeline and manages agent communication
- **Crawler Agent**: Fetches news articles from various sources
- **Extractor Agent**: Extracts factual claims from articles using LLM analysis
- **Fact Checker Agent**: Verifies claims against reliable sources
- **Publisher Agent**: Publishes verified results to the Jekyll website

### Communication Protocol
- **A2A Protocol**: Enables asynchronous communication between agents
- **MCP Integration**: Provides external tools for claim extraction, verification, and publishing

## 🛠️ Tools & Technologies

### Core Technologies
- **Python 3.11+**: Main programming language
- **Jekyll**: Static site generator for the fact-checking website
- **A2A Protocol**: Agent-to-agent communication framework
- **MCP (Model Context Protocol)**: External tool integration

### AI/ML Components
- **Large Language Models**: For claim extraction and verification
- **Semantic Analysis**: For understanding and processing news content
- **Fact Verification**: Against reliable databases and sources

### Web Technologies
- **Jekyll**: Static site generation
- **Markdown**: Content formatting
- **CSS/HTML**: Website styling and structure

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- Ruby and Jekyll (for website generation)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Fact_Checking_News_Aggregator
   ```

2. **Set up Python environment**
   ```bash
   # Using uv (recommended)
   uv sync
   
   # Or using pip
   pip install -r requirements.txt
   ```

3. **Install Jekyll** (for website generation)
   ```bash
   gem install jekyll jekyll-feed
   ```

### Running the System

1. **Run the complete pipeline**
   ```bash
   python run_all_agents.py
   ```
   This will:
   - Start the mcp server
   - Initialize all agents

2. **Start the Orchestrator** 
   ```bash
   python orchestrator.py
   ```
   This will:
   - Start the Orchestrator Agent.

2. **Start the Orchestrator Client**
   ```bash
   python orchestrator_client.py
   ```
   This will:
   - Start the client interface
   - Type 'start' to run the pipeline and 'end' to stop the flow.

3. **Serve the Jekyll website**
   ```bash
   cd jekyll_site
   jekyll serve --host 0.0.0.0 --port 4000
   ```
   Visit `http://localhost:4000` to see the fact-checked results.

## 🔧 MCP-A2A Integration

### MCP Server Tools
The MCP server provides three main tools that agents can call:

1. **`extract_claims`**: Extracts factual claims from news articles
   - Input: Article text
   - Output: JSON array of claims

2. **`verify_claim`**: Verifies a claim against reliable sources
   - Input: Claim statement
   - Output: Verification result (True/False) and source

3. **`generate_jekyll_post`**: Creates Jekyll blog posts for verified claims
   - Input: Statement, verification status, source
   - Output: Generated Markdown file with proper Jekyll format

### A2A Protocol Integration
- **Asynchronous Communication**: Agents communicate asynchronously using `handle_message_async`
- **Message Routing**: Orchestrator routes messages between agents
- **Error Handling**: Robust error handling for failed agent communications
- **State Management**: Each agent maintains its own state and processing logic

### Agent Workflow
1. **Orchestrator** → **Crawler**: Request news articles
2. **Crawler** → **Orchestrator**: Return article URLs and content
3. **Orchestrator** → **Extractor**: Send articles for claim extraction
4. **Extractor** → **MCP**: Call `extract_claims` tool
5. **Extractor** → **Orchestrator**: Return extracted claims
6. **Orchestrator** → **Fact Checker**: Send claims for verification
7. **Fact Checker** → **MCP**: Call `verify_claim` tool
8. **Fact Checker** → **Orchestrator**: Return verification results
9. **Orchestrator** → **Publisher**: Send verified claims for publishing
10. **Publisher** → **MCP**: Call `generate_jekyll_post` tool

## 📁 Project Structure

```
Fact_Checking_News_Aggregator/
├── agents/                    # Agent implementations
│   ├── crawler_agent/        # News crawling agent
│   ├── extractor_agent/      # Claim extraction agent
│   ├── fact_checker_agent/   # Fact verification agent
│   └── publisher_agent/      # Publishing agent
├── jekyll_site/              # Jekyll website
│   ├── _posts/              # Generated fact-check posts
│   ├── _layouts/            # Jekyll layouts
│   ├── assets/              # CSS and styling
│   └── _config.yml          # Jekyll configuration
├── mcp_server.py            # MCP server with external tools
├── orchestrator.py          # Main orchestrator agent
├── run_all_agents.py        # Pipeline execution script
└── requirements.txt         # Python dependencies
```

## 🔍 How It Works

### 1. News Crawling
The crawler agent fetches news articles from configured sources and extracts relevant content.

### 2. Claim Extraction
The extractor agent uses LLM analysis to identify factual claims within articles, calling the MCP `extract_claims` tool.

### 3. Fact Verification
The fact checker agent verifies each claim against reliable sources using the MCP `verify_claim` tool.

### 4. Publishing
The publisher agent generates Jekyll blog posts for verified claims using the MCP `generate_jekyll_post` tool.

### 5. Website Generation
Jekyll automatically builds the website with the new fact-checked posts, making them available at the configured URL.

## 🎨 Customization

### Adding News Sources
Modify the crawler agent configuration to add new news sources.

### Custom Verification Sources
Update the fact checker agent to use different verification databases or APIs.

### Website Styling
Customize the Jekyll theme and styling in the `jekyll_site/assets/` directory.

### Agent Behavior
Modify individual agent configurations to adjust their behavior and processing logic.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


**Note**: This system is designed for educational and research purposes. Always verify fact-checking results independently for critical applications.
