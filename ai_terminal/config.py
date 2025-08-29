"""Configuration management for AI Terminal Assistant."""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
import json


@dataclass
class Config:
    """Application configuration."""
    
   
    ai_provider: str = "gemini"
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    claude_api_key: Optional[str] = None
    model_name: Optional[str] = None
    
   
    default_timeout: int = 15
    require_confirmation: bool = True
    verbose: bool = False
    
    
    enable_safety_filter: bool = True
    allow_sudo: bool = False
    
   
    force_shell: Optional[str] = None  
    
    def __post_init__(self):
        """Load API keys from environment if not set."""
        if not self.gemini_api_key:
            self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not self.openai_api_key:
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.claude_api_key:
            self.claude_api_key = os.getenv("ANTHROPIC_API_KEY")
    
    def validate(self) -> None:
        """Validate configuration."""
        if self.ai_provider == "gemini" and not self.gemini_api_key:
            raise ValueError(
                "Gemini API key not found. "
                "Please set GEMINI_API_KEY environment variable or provide in config."
            )
        elif self.ai_provider == "openai" and not self.openai_api_key:
            raise ValueError(
                "OpenAI API key not found. "
                "Please set OPENAI_API_KEY environment variable."
            )
        elif self.ai_provider == "claude" and not self.claude_api_key:
            raise ValueError(
                "Claude API key not found. "
                "Please set ANTHROPIC_API_KEY environment variable."
            )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            k: v for k, v in self.__dict__.items()
            if not k.endswith("_key")  # Don't export API keys
        }


def load_config(config_path: Optional[Path] = None) -> Config:
    """
    Load configuration from file or use defaults.
    
    Args:
        config_path: Optional path to configuration file
    
    Returns:
        Config object
    """
    config_data = {}
    
   
    if not config_path:
        default_paths = [
            Path.home() / ".ai_terminal" / "config.json",
            Path.home() / ".config" / "ai_terminal" / "config.json",
            Path("config.json"),
        ]
        
        for path in default_paths:
            if path.exists():
                config_path = path
                break
    
   
    if config_path and config_path.exists():
        with open(config_path, "r") as f:
            config_data = json.load(f)
    
    
    config = Config(**config_data)
    config.validate()
    
    return config