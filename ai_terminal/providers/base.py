"""Base AI provider interface."""

from abc import ABC, abstractmethod
from typing import Optional

from ..models import ShellContext, Command


class AIProvider(ABC):
    """Abstract base class for AI providers."""
    
    @abstractmethod
    def __init__(self, api_key: str, model_name: Optional[str] = None):
        """
        Initialize the AI provider.
        
        Args:
            api_key: API key for the provider
            model_name: Optional specific model to use
        """
        pass
    
    @abstractmethod
    def generate_command(
        self,
        query: str,
        context: ShellContext,
        examples: Optional[list] = None
    ) -> Optional[Command]:
        """
        Generate a shell command from natural language query.
        
        Args:
            query: Natural language query
            context: Shell context information
            examples: Optional few-shot examples
        
        Returns:
            Command object or None if generation fails
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the provider is available and configured.
        
        Returns:
            True if provider can be used
        """
        pass
    
    def format_prompt(
        self,
        query: str,
        context: ShellContext,
        examples: Optional[list] = None
    ) -> str:
        """
        Format the prompt for the AI model.
        
        Args:
            query: Natural language query
            context: Shell context information
            examples: Optional few-shot examples
        
        Returns:
            Formatted prompt string
        """
        shell_name = {
            "powershell": "Windows PowerShell",
            "cmd": "Windows Command Prompt",
            "bash": "Linux/Unix Bash",
            "zsh": "Z Shell (zsh)",
            "fish": "Fish Shell",
        }.get(context.shell_type.value, context.shell_type.value)
        
        prompt = f"""
You are a shell command expert. Convert the following natural language request into a valid shell command.

Context:
- Shell: {shell_name}
- Operating System: {context.os_name}
- Current Directory: {context.current_directory}
"""
        
        if context.is_virtual_env:
            prompt += f"""
- Python Environment: {context.virtual_env_name} (active)
- Package Manager: {context.package_manager}
"""
        
        if examples:
            prompt += "\nExamples:\n"
            for ex in examples:
                prompt += f"- Request: '{ex['request']}' -> Command: `{ex['command']}`\n"
        
        prompt += f"""
Instructions:
1. Output ONLY the shell command, nothing else
2. Do not include markdown formatting or backticks
3. Ensure the command is valid for {shell_name}
4. If the request involves Python packages and a virtual environment is active, use {context.package_manager}
5. Prefer simple, safe commands over complex ones

Request: {query}
Command:"""
        
        return prompt