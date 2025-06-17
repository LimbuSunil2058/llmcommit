"""Simple rule-based commit message generator for fast operation."""

import re
from typing import Dict, Any


class SimpleLLMClient:
    """Fast rule-based commit message generator."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize simple client."""
        self.config = config
        
    def generate_commit_message(self, diff: str) -> str:
        """Generate commit message using simple rules."""
        # Parse the diff
        lines = diff.split('\n')
        
        # Count changes
        added_lines = [l for l in lines if l.startswith('+') and not l.startswith('+++')]
        removed_lines = [l for l in lines if l.startswith('-') and not l.startswith('---')]
        modified_files = set()
        
        # Extract file names
        for line in lines:
            if line.startswith('diff --git'):
                # Extract file path from "diff --git a/file b/file"
                match = re.search(r'diff --git a/(.*?) b/', line)
                if match:
                    modified_files.add(match.group(1))
            elif line.startswith('+++') or line.startswith('---'):
                # Extract from +++ b/file or --- a/file
                match = re.search(r'[+-]{3} [ab]/(.*)', line)
                if match:
                    modified_files.add(match.group(1))
        
        # Determine action
        added_count = len(added_lines)
        removed_count = len(removed_lines)
        
        # Generate message based on pattern
        if len(modified_files) == 1:
            filename = list(modified_files)[0]
            if added_count > removed_count * 2:
                return f"Add content to {filename}"
            elif removed_count > added_count * 2:
                return f"Remove content from {filename}"
            else:
                return f"Update {filename}"
        
        elif len(modified_files) > 1:
            if added_count > removed_count * 2:
                return f"Add content to {len(modified_files)} files"
            elif removed_count > added_count * 2:
                return f"Remove content from {len(modified_files)} files"
            else:
                return f"Update {len(modified_files)} files"
        
        # Fallback patterns
        total_changes = added_count + removed_count
        if total_changes == 0:
            return "Minor changes"
        elif total_changes < 10:
            return "Small updates"
        elif total_changes < 50:
            return "Medium updates"
        else:
            return "Major changes"


class FastCommitClient:
    """Ultra-fast commit message generator with better quality."""
    
    KEYWORDS = {
        'config': ['.json', 'config', 'settings', '.env', 'dockerfile', 'makefile'],
        'test': ['test', 'spec', '__test__', '.test.', '_test.'],
        'docs': ['readme', 'doc', 'docs', '.md', 'changelog'],
        'fix': ['fix', 'bug', 'error', 'issue'],
        'feat': ['add', 'new', 'create', 'implement'],
        'refactor': ['refactor', 'cleanup', 'organize', 'restructure'],
        'style': ['format', 'lint', 'style', 'prettier'],
        'deps': ['package.json', 'requirements.txt', 'pip', 'npm']
    }
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize fast client."""
        self.config = config
        
    def _detect_change_type(self, diff: str, files: list) -> str:
        """Detect the type of change based on files and diff content."""
        files_str = ' '.join(files).lower()
        
        # Check file-based patterns first (more reliable)
        for change_type, keywords in self.KEYWORDS.items():
            if any(keyword in files_str for keyword in keywords):
                return change_type
        
        # Check diff content for specific patterns only if no file match
        diff_lower = diff.lower()
        
        # Look for configuration patterns - check for actual config changes
        if '.json' in files_str and ('config' in diff_lower or 'setting' in diff_lower):
            return 'config'
        elif any(word in diff_lower for word in ['fix', 'bug', 'error', 'issue']):
            return 'fix'
        # Only detect test if it's in test files, not content
        elif any('.test.' in f or '_test.' in f or '/test/' in f for f in files):
            return 'test'
                
        # Default based on diff patterns
        added_lines = len([l for l in diff.split('\n') if l.startswith('+') and not l.startswith('+++')])
        removed_lines = len([l for l in diff.split('\n') if l.startswith('-') and not l.startswith('---')])
        
        if added_lines > removed_lines * 2:
            return 'feat'
        elif removed_lines > added_lines * 2:
            return 'remove'
        else:
            return 'update'
    
    def _get_primary_file(self, files: list) -> str:
        """Get the most important file from the list."""
        if not files:
            return "files"
            
        # Prioritize certain file types
        priority_extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c']
        
        for ext in priority_extensions:
            for file in files:
                if file.endswith(ext):
                    return file
                    
        # Return first file if no priority match
        return files[0]
    
    def generate_commit_message(self, diff: str) -> str:
        """Generate high-quality commit message quickly."""
        lines = diff.split('\n')
        
        # Extract modified files
        files = []
        for line in lines:
            if line.startswith('diff --git'):
                match = re.search(r'diff --git a/(.*?) b/', line)
                if match:
                    files.append(match.group(1))
        
        # Detect change type
        change_type = self._detect_change_type(diff, files)
        primary_file = self._get_primary_file(files)
        
        # Generate contextual messages
        if change_type == 'test':
            if len(files) == 1:
                return f"Add tests for {primary_file.replace('.test', '').replace('_test', '')}"
            return f"Add tests for {len(files)} modules"
            
        elif change_type == 'config':
            return "Update configuration"
            
        elif change_type == 'docs':
            return "Update documentation"
            
        elif change_type == 'fix':
            if len(files) == 1:
                return f"Fix issue in {primary_file}"
            return "Fix multiple issues"
            
        elif change_type == 'feat':
            if len(files) == 1:
                return f"Add feature to {primary_file}"
            return f"Add new features ({len(files)} files)"
            
        elif change_type == 'refactor':
            if len(files) == 1:
                return f"Refactor {primary_file}"
            return f"Refactor codebase ({len(files)} files)"
            
        elif change_type == 'style':
            return "Format code"
            
        elif change_type == 'deps':
            return "Update dependencies"
            
        else:  # 'update' or fallback
            if len(files) == 1:
                return f"Update {primary_file}"
            elif len(files) <= 3:
                return f"Update {', '.join(files[:2])}{'...' if len(files) > 2 else ''}"
            else:
                return f"Update {len(files)} files"