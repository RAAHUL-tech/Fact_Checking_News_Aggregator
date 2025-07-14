import subprocess
import time
import signal
import sys
import os

AGENT_PATHS = [
    "mcp_server.py",  # Start MCP server first
    "agents/crawler_agent/agent_base.py",
    "agents/extractor_agent/extractor_agent.py",
    "agents/fact_checker_agent/fact_checker_agent.py",
    "agents/publisher_agent/publisher_agent.py"
]

processes = []

def start_process(cmd, name):
    print(f"Starting {name}...")
    process = subprocess.Popen(
        cmd, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        text=True
    )
    processes.append((process, name))
    print(f"Started {name} with PID {process.pid}")
    return process

def check_environment():
    """Check if required environment variables are set"""
    if not os.getenv("GROQ_API_KEY"):
        print("Warning: GROQ_API_KEY environment variable not set.")
        print("The MCP server may not work properly for claim extraction.")
        print("Please set GROQ_API_KEY in your environment or create a .env file.")

def main():
    try:
        check_environment()
        
        # Start each agent Python file
        for agent_script in AGENT_PATHS:
            if agent_script == "mcp_server.py":
                name = "MCP Server"
            else:
                name = agent_script.split('/')[-1].replace('.py', '')
            
            process = start_process(["python", agent_script], name)
            
            # Give MCP server a moment to start up
            if agent_script == "mcp_server.py":
                print("Waiting for MCP server to start...")
                time.sleep(3)

        print("\nAll services started:")
        for _, name in processes:
            print(f"  - {name}")
        print("\nPress Ctrl+C to stop all services.")

        # Keep the script running
        while True:
            time.sleep(1)
            
            # Check if any process has died
            for process, name in processes:
                if process.poll() is not None:
                    print(f"Warning: {name} has stopped unexpectedly (exit code: {process.returncode})")

    except KeyboardInterrupt:
        print("\nTerminating all processes...")
        for process, name in processes:
            try:
                process.send_signal(signal.SIGINT)
                print(f"Sent SIGINT to {name}")
            except Exception as e:
                print(f"Error terminating {name}: {e}")
        
        # Wait a moment for graceful shutdown
        time.sleep(2)
        
        # Force kill any remaining processes
        for process, name in processes:
            if process.poll() is None:
                try:
                    process.terminate()
                    print(f"Force terminated {name}")
                except Exception as e:
                    print(f"Error force terminating {name}: {e}")
        
        sys.exit(0)

if __name__ == "__main__":
    main()
