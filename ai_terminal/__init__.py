"""AI Terminal Assistant - Natural language shell command interface."""

__version__ = "2.0.0"
__author__ = "AI Terminal Team"

from .assistant import AITerminalAssistant
from .config import Config

__all__ = ["AITerminalAssistant", "Config"]