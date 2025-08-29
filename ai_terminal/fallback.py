"""Fallback command generation when AI is unavailable."""

import re
from typing import Optional, Dict, List

from .models import Command, CommandCategory, ShellContext, ShellType
from .shell_utils import get_basic_commands


class FallbackHandler:
    """Handles fallback command generation."""
    
    def __init__(self):
        """Initialize fallback handler."""
        self.python_packages = self._load_python_packages()
        self.command_patterns = self._load_command_patterns()
    
    def _load_python_packages(self) -> List[str]:
        """Load list of common Python packages."""
        return [
            "pandas", "numpy", "requests", "flask", "django",
            "tensorflow", "torch", "scikit-learn", "matplotlib",
            "pytest", "black", "mypy", "ruff", "poetry",
            "fastapi", "streamlit", "gradio", "jupyterlab",
            "google-generativeai", "openai", "anthropic",
            "langchain", "transformers", "pillow", "opencv-python",
        ]
    
    def _load_command_patterns(self) -> Dict[str, str]:
        """Load command patterns for common operations."""
        return {
           
            r"create (?:a )?file (?:named |called )?(.+)": "touch {0}",
            r"make (?:a )?(?:new )?directory (?:named |called )?(.+)": "mkdir -p {0}",
            r"delete (?:the )?file (.+)": "rm {0}",
            r"copy (.+) to (.+)": "cp {0} {1}",
            r"move (.+) to (.+)": "mv {0} {1}",
            r"rename (.+) to (.+)": "mv {0} {1}",
            
           
            r"show (?:me )?(?:the )?current (?:working )?directory": "pwd",
            r"list (?:all )?files?": "ls -la",
            r"clear (?:the )?(?:terminal|screen)": "clear",
            r"show (?:running )?processes": "ps aux",
            r"kill process (?:with )?(?:pid |id )?(\d+)": "kill {0}",
            
           
            r"ping (.+)": "ping -c 4 {0}",
            r"check (?:the )?port (\d+)": "netstat -an | grep {0}",
            r"download (?:from )?(.+)": "wget {0}",
            
           
            r"git status": "git status",
            r"git add (?:all|everything)": "git add .",
            r"git commit (?:with message )?(.+)": 'git commit -m "{0}"',
            r"git push": "git push",
            r"git pull": "git pull",
        }
    
    def generate_command(
        self,
        query: str,
        context: ShellContext
    ) -> Optional[Command]:
        """
        Generate fallback command based on patterns.
        
        Args:
            query: Natural language query
            context: Shell context
        
        Returns:
            Command object or None
        """
        query_lower = query.lower().strip()
        
       
        if self._is_package_install(query_lower):
            return self._handle_package_install(query_lower, context)
        
       
        basic_commands = get_basic_commands(context.shell_type)
        for key, cmd in basic_commands.items():
            if key in query_lower:
                return Command(
                    raw_command=cmd,
                    confidence=0.6,
                    explanation=f"Basic command for: {key}"
                )
        
       
        for pattern, template in self.command_patterns.items():
            match = re.search(pattern, query_lower)
            if match:
                
                cmd = template.format(*match.groups()) if match.groups() else template
                
               
                cmd = self._adjust_for_shell(cmd, context.shell_type)
                
                return Command(
                    raw_command=cmd,
                    confidence=0.7,
                    explanation=f"Pattern match for: {query}"
                )
        
        return None
    
    def _is_package_install(self, query: str) -> bool:
        """Check if query is about package installation."""
        install_keywords = ["install", "add", "get", "setup", "pip", "conda"]
        package_keywords = ["package", "module", "library", "dependency"]
        
        has_install = any(kw in query for kw in install_keywords)
        has_package = any(kw in query for kw in package_keywords)
        
       
        has_known_package = any(pkg in query for pkg in self.python_packages)
        
        return (has_install and has_package) or (has_install and has_known_package)
    
    def _handle_package_install(
        self,
        query: str,
        context: ShellContext
    ) -> Optional[Command]:
        """Handle package installation requests."""
       
        package_name = None
        
       
        for pkg in self.python_packages:
            if pkg in query:
                package_name = pkg
                break
        
       
        if not package_name:
            patterns = [
                r"install\s+([a-z0-9_-]+)",
                r"add\s+([a-z0-9_-]+)",
                r"get\s+([a-z0-9_-]+)",
            ]
            
            for pattern in patterns:
                match = re.search(pattern, query)
                if match:
                    package_name = match.group(1)
                    break
        
        if not package_name:
            return None
        
      
        if context.is_virtual_env:
            if context.package_manager == "conda":
                cmd = f"conda install -y {package_name}"
            elif context.package_manager == "poetry":
                cmd = f"poetry add {package_name}"
            elif context.package_manager == "pipenv":
                cmd = f"pipenv install {package_name}"
            else:
                cmd = f"pip install {package_name}"
        else:
            cmd = f"pip install {package_name}"
        
        return Command(
            raw_command=cmd,
            confidence=0.8,
            explanation=f"Install Python package: {package_name}"
        )
    
    def _adjust_for_shell(self, cmd: str, shell_type: ShellType) -> str:
        """Adjust command for specific shell type."""
        if shell_type == ShellType.POWERSHELL:
            replacements = {
                "touch": "New-Item -ItemType File -Name",
                "rm": "Remove-Item",
                "cp": "Copy-Item",
                "mv": "Move-Item",
                "cat": "Get-Content",
                "grep": "Select-String",
                "ls -la": "Get-ChildItem -Force",
                "ps aux": "Get-Process",
                "clear": "Clear-Host",
                "pwd": "Get-Location",
                "mkdir -p": "New-Item -ItemType Directory -Force -Path",
            }
        elif shell_type == ShellType.CMD:
            replacements = {
                "touch": "type nul >",
                "rm": "del",
                "cp": "copy",
                "mv": "move",
                "cat": "type",
                "grep": "findstr",
                "ls -la": "dir /a",
                "ps aux": "tasklist",
                "clear": "cls",
                "pwd": "cd",
                "mkdir -p": "mkdir",
            }
        else:
            return cmd  # No adjustment needed for Unix shells
        
        for unix_cmd, win_cmd in replacements.items():
            if cmd.startswith(unix_cmd):
                cmd = cmd.replace(unix_cmd, win_cmd, 1)
                break
        
        return cmd