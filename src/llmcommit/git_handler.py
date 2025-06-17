"""Git operations handler."""

import subprocess
from typing import Optional


class GitHandler:
    """Handle git operations."""
    
    def get_staged_diff(self) -> Optional[str]:
        """Get the staged changes diff."""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip() if result.stdout.strip() else None
        except subprocess.CalledProcessError:
            return None
    
    def get_unstaged_diff(self) -> Optional[str]:
        """Get the unstaged changes diff."""
        try:
            result = subprocess.run(
                ["git", "diff"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip() if result.stdout.strip() else None
        except subprocess.CalledProcessError:
            return None
    
    def add_all(self) -> bool:
        """Stage all modified and new files."""
        try:
            subprocess.run(
                ["git", "add", "-A"],
                check=True,
                capture_output=True,
                text=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
    
    def commit(self, message: str, no_verify: bool = False) -> bool:
        """Commit with the given message."""
        try:
            cmd = ["git", "commit", "-m", message]
            if no_verify:
                cmd.append("--no-verify")
            
            subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
    
    def push(self, force: bool = False) -> bool:
        """Push to remote repository."""
        try:
            # First check if there's a remote configured
            result = subprocess.run(
                ["git", "remote"],
                capture_output=True,
                text=True,
                check=True
            )
            if not result.stdout.strip():
                print("No remote repository configured.")
                return False
            
            # Get current branch
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                check=True
            )
            current_branch = result.stdout.strip()
            
            # Push to remote
            cmd = ["git", "push"]
            if force:
                cmd.append("--force")
            cmd.extend(["origin", current_branch])
            
            subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            return True
        except subprocess.CalledProcessError as e:
            if e.stderr and "no upstream branch" in e.stderr:
                # Try to push with --set-upstream
                try:
                    cmd = ["git", "push", "--set-upstream", "origin", current_branch]
                    if force:
                        cmd.insert(2, "--force")
                    subprocess.run(
                        cmd,
                        check=True,
                        capture_output=True,
                        text=True
                    )
                    return True
                except subprocess.CalledProcessError:
                    return False
            return False
    
    def is_git_repo(self) -> bool:
        """Check if current directory is a git repository."""
        try:
            subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                check=True,
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError:
            return False