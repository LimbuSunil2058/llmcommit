"""Test git operations."""

import subprocess
from unittest.mock import patch, MagicMock
import pytest

from llmcommit.git_handler import GitHandler


class TestGitHandler:
    """Test GitHandler class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.git_handler = GitHandler()
    
    @patch('llmcommit.git_handler.subprocess.run')
    def test_get_staged_diff_success(self, mock_run):
        """Test successful staged diff retrieval."""
        mock_result = MagicMock()
        mock_result.stdout = "diff --git a/file.py b/file.py\n+added line"
        mock_run.return_value = mock_result
        
        diff = self.git_handler.get_staged_diff()
        
        assert diff == "diff --git a/file.py b/file.py\n+added line"
        mock_run.assert_called_once_with(
            ["git", "diff", "--cached"],
            capture_output=True,
            text=True,
            check=True
        )
    
    @patch('llmcommit.git_handler.subprocess.run')
    def test_get_staged_diff_empty(self, mock_run):
        """Test empty staged diff."""
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_run.return_value = mock_result
        
        diff = self.git_handler.get_staged_diff()
        
        assert diff is None
    
    @patch('llmcommit.git_handler.subprocess.run')
    def test_get_staged_diff_error(self, mock_run):
        """Test git diff error handling."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "git diff")
        
        diff = self.git_handler.get_staged_diff()
        
        assert diff is None
    
    @patch('llmcommit.git_handler.subprocess.run')
    def test_commit_success(self, mock_run):
        """Test successful commit."""
        mock_run.return_value = MagicMock()
        
        result = self.git_handler.commit("Test commit message")
        
        assert result is True
        mock_run.assert_called_once_with(
            ["git", "commit", "-m", "Test commit message"],
            check=True,
            capture_output=True,
            text=True
        )
    
    @patch('llmcommit.git_handler.subprocess.run')
    def test_commit_error(self, mock_run):
        """Test commit error handling."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "git commit")
        
        result = self.git_handler.commit("Test commit message")
        
        assert result is False