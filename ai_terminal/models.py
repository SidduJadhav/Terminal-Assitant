"""Data models for AI Terminal Assistant."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Dict, Any


class ShellType(Enum):
    """Supported shell types."""
    POWERSHELL = "powershell"
    CMD = "cmd"
    BASH = "bash"
    ZSH = "zsh"
    FISH = "fish"


class CommandCategory(Enum):
    """Command categories for handling."""
    SAFE = "safe"
    DANGEROUS = "dangerous"
    INTERACTIVE = "interactive"
    DIRECTORY_CHANGE = "directory_change"
    LONG_RUNNING = "long_running"


@dataclass
class ShellContext:
    """Context information about the current shell environment."""
    shell_type: ShellType
    os_name: str
    is_admin: bool = False
    is_virtual_env: bool = False
    virtual_env_name: Optional[str] = None
    package_manager: Optional[str] = None
    current_directory: Optional[str] = None
    environment_vars: Dict[str, str] = None
    
    def __post_init__(self):
        if self.environment_vars is None:
            self.environment_vars = {}


@dataclass
class Command:
    """Represents a shell command."""
    raw_command: str
    category: CommandCategory = CommandCategory.SAFE
    confidence: float = 1.0
    explanation: Optional[str] = None
    alternatives: List[str] = None
    requires_sudo: bool = False
    estimated_duration: Optional[float] = None  # seconds
    
    def __post_init__(self):
        if self.alternatives is None:
            self.alternatives = []
    
    @property
    def is_safe(self) -> bool:
        """Check if command is safe to execute."""
        return self.category == CommandCategory.SAFE
    
    @property
    def requires_interaction(self) -> bool:
        """Check if command requires user interaction."""
        return self.category in [
            CommandCategory.INTERACTIVE,
            CommandCategory.DIRECTORY_CHANGE
        ]


@dataclass
class ExecutionResult:
    """Result of command execution."""
    success: bool
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    return_code: Optional[int] = None
    execution_time: Optional[float] = None
    error_message: Optional[str] = None