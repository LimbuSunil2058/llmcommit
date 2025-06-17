#!/usr/bin/env python3
"""Model server for persistent model caching."""

import os
import sys
import json
import time
import socket
import pickle
import signal
import argparse
from pathlib import Path
from multiprocessing import Process, Queue
from threading import Thread

# Set environment variable before importing transformers
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from .llm_client import LLMClient
from .config import load_config


class ModelServer:
    """Server that keeps model in memory."""
    
    def __init__(self, config_path=None):
        self.config = load_config(config_path)
        self.socket_path = "/tmp/llmcommit.sock"
        self.model_client = None
        self.running = True
        
    def start(self):
        """Start the model server."""
        # Remove existing socket
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)
            
        # Load model once
        print(f"Loading model {self.config['model']}...")
        start_time = time.time()
        self.model_client = LLMClient(self.config)
        print(f"Model loaded in {time.time() - start_time:.1f}s")
        
        # Create Unix socket
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(self.socket_path)
        server.listen(1)
        
        print(f"Server listening on {self.socket_path}")
        
        # Handle shutdown
        signal.signal(signal.SIGINT, self._shutdown)
        signal.signal(signal.SIGTERM, self._shutdown)
        
        while self.running:
            try:
                conn, _ = server.accept()
                self._handle_request(conn)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Server error: {e}")
                
        server.close()
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)
            
    def _handle_request(self, conn):
        """Handle a single request."""
        try:
            # Receive data
            data = b""
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                data += chunk
                if b"\n\n" in data:  # End marker
                    break
                    
            # Process request
            request = json.loads(data.decode().strip())
            diff = request.get("diff", "")
            
            # Generate message
            start_time = time.time()
            message = self.model_client.generate_commit_message(diff)
            elapsed = time.time() - start_time
            
            # Send response
            response = {
                "message": message,
                "elapsed": elapsed
            }
            conn.send(json.dumps(response).encode() + b"\n")
            
        except Exception as e:
            error_response = {"error": str(e)}
            conn.send(json.dumps(error_response).encode() + b"\n")
        finally:
            conn.close()
            
    def _shutdown(self, signum, frame):
        """Graceful shutdown."""
        print("\nShutting down server...")
        self.running = False


class ModelClient:
    """Client for communicating with model server."""
    
    def __init__(self):
        self.socket_path = "/tmp/llmcommit.sock"
        
    def is_server_running(self):
        """Check if server is running."""
        return os.path.exists(self.socket_path)
        
    def generate_commit_message(self, diff):
        """Generate message via server."""
        if not self.is_server_running():
            raise Exception("Model server not running. Start with: llmcommit-server")
            
        # Connect to server
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(self.socket_path)
        
        try:
            # Send request
            request = {"diff": diff}
            client.send(json.dumps(request).encode() + b"\n\n")
            
            # Receive response
            data = b""
            while True:
                chunk = client.recv(4096)
                if not chunk:
                    break
                data += chunk
                if b"\n" in data:
                    break
                    
            response = json.loads(data.decode().strip())
            
            if "error" in response:
                raise Exception(response["error"])
                
            return response["message"]
            
        finally:
            client.close()


def start_server_daemon():
    """Start server as daemon process."""
    pid_file = Path.home() / ".llmcommit" / "server.pid"
    pid_file.parent.mkdir(exist_ok=True)
    
    # Check if already running
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text())
            os.kill(pid, 0)  # Check if process exists
            print("Server already running")
            return
        except (OSError, ValueError):
            # Process doesn't exist, remove stale pid file
            pid_file.unlink()
    
    # Fork daemon
    pid = os.fork()
    if pid > 0:
        # Parent process
        pid_file.write_text(str(pid))
        print(f"Server started (PID: {pid})")
        return
        
    # Child process - become daemon
    os.setsid()
    os.umask(0)
    
    # Redirect stdout/stderr to log
    log_file = pid_file.parent / "server.log"
    sys.stdout = open(log_file, 'a')
    sys.stderr = sys.stdout
    
    # Start server
    server = ModelServer()
    server.start()


def stop_server_daemon():
    """Stop the daemon server."""
    pid_file = Path.home() / ".llmcommit" / "server.pid"
    
    if not pid_file.exists():
        print("Server not running")
        return
        
    try:
        pid = int(pid_file.read_text())
        os.kill(pid, signal.SIGTERM)
        pid_file.unlink()
        
        # Clean up socket
        socket_path = "/tmp/llmcommit.sock"
        if os.path.exists(socket_path):
            os.unlink(socket_path)
            
        print("Server stopped")
    except Exception as e:
        print(f"Error stopping server: {e}")


def main():
    """Server CLI."""
    parser = argparse.ArgumentParser(description="LLMCommit Model Server")
    parser.add_argument("command", choices=["start", "stop", "status", "foreground"],
                       help="Server command")
    parser.add_argument("--config", help="Config file path")
    
    args = parser.parse_args()
    
    if args.command == "start":
        start_server_daemon()
    elif args.command == "stop":
        stop_server_daemon()
    elif args.command == "status":
        pid_file = Path.home() / ".llmcommit" / "server.pid"
        if pid_file.exists():
            try:
                pid = int(pid_file.read_text())
                os.kill(pid, 0)
                print(f"Server running (PID: {pid})")
            except OSError:
                print("Server not running (stale PID file)")
        else:
            print("Server not running")
    elif args.command == "foreground":
        # Run in foreground (for debugging)
        server = ModelServer(args.config)
        server.start()


if __name__ == "__main__":
    main()