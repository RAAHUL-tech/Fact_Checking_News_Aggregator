from python_a2a.mcp import FastMCP
from dotenv import load_dotenv
from groq import Groq
import subprocess
import requests
import logging
import json
import os
import re

# Load environment variables
load_dotenv()

# Initialize MCP Server
factcheck_mcp = FastMCP(
    name="FactCheckTools",
    version="1.0",
    description="MCP for verifying factual claims and generating Jekyll posts."
)

@factcheck_mcp.tool()
def extract_claims(text: str) -> list:
    """
    Extracts standalone factual claims using LLaMA-3 (Groq).
    """
    print("[extract_claims] Received input:", text)
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return ["GROQ_API_KEY not found in environment"]

    client = Groq(api_key=api_key)
    prompt = f"""
    Extract a list of concise, standalone factual claims from the following article. 
    Return only the claims in JSON array format.

    Article:
    \"\"\"
    {text}
    \"\"\"
    """

    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "You are a helpful assistant trained to extract factual claims from news articles."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        output = response.choices[0].message.content
        print("[extract_claims] Raw output from LLM:", output)
        return json.loads(output)

    except Exception as e:
        print("[extract_claims] ERROR:", str(e))
        return [f"Error parsing claims: {str(e)}", output if 'output' in locals() else ""]

@factcheck_mcp.tool()
def check_wikidata(statement: str) -> dict:
    """
    Checks if a statement is supported by Wikidata.
    """
    print("[check_wikidata] Checking:", statement)
    try:
        resp = requests.get("https://www.wikidata.org/w/api.php", params={
            "action": "wbsearchentities",
            "search": statement,
            "language": "en",
            "format": "json"
        })

        data = resp.json()
        results = data.get("search", [])
        if results:
            source_url = f"https://www.wikidata.org/wiki/{results[0]['id']}"
            return {"verified": True, "source": source_url}

        return {"verified": False, "source": ""}
    except Exception as e:
        print("[check_wikidata] ERROR:", str(e))
        return {"error": str(e)}

@factcheck_mcp.tool()
def generate_jekyll_post(statement: str, verified: bool, source: str) -> str:
    """
    Generates a Markdown blog post for a fact-check result.
    """
    fname = f"{int(abs(hash(statement)))}.md"
    content = f"""---
title: "Claim {fname}"
verified: {verified}
source: "{source}"
---

{statement}
"""
    filepath = os.path.join("jekyll_site/_posts", fname)
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            f.write(content)
        return_code = subprocess.run(["jekyll", "build"], cwd="jekyll_site").returncode
        return f"Generated Jekyll post with code {return_code}"
    except Exception as e:
        return f"Error generating Jekyll post: {str(e)}"

# Run the MCP Server
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Registered tools:", list(factcheck_mcp.tools.keys()))
    factcheck_mcp.run(host="0.0.0.0", port=8000)
