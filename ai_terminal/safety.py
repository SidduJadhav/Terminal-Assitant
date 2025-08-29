"""Safety filters and validation for commands."""

import re
from typing import List, Pattern, Optional
from dataclasses import dataclass

from .models import Command, CommandCategory


@dataclass
class SafetyRule:
    """Represents a safety rule for command filtering."""
    pattern: Pattern
    category: CommandCategory
    description: str
    severity: str  # "critical", "high", "medium", "low"


class SafetyFilter:
    """Manages safety filtering for shell commands."""
    
    def __init__(self, strict_mode: bool = True):
        """
        Initialize safety filter.
        
        Args:
            strict_mode: If True, be more restrictive with commands
        """
        self.strict_mode = strict_mode
        self.rules = self._initialize_rules()
    
    def _initialize_rules(self) -> List[SafetyRule]:
        """Initialize safety rules."""
        return [
            # Critical - System destruction
            SafetyRule(
                pattern=re.compile(r"rm\s+-rf\s+/?(?:\s|$)", re.IGNORECASE),
                category=CommandCategory.DANGEROUS,
                description="Recursive force delete from root",
                severity="critical"
            ),
            SafetyRule(
                pattern=re.compile(r":(){ :|:& };:", re.IGNORECASE),
                category=CommandCategory.DANGEROUS,
                description="Fork bomb",
                severity="critical"
            ),
            SafetyRule(
                pattern=re.compile(r"mkfs\.", re.IGNORECASE),
                category=CommandCategory.DANGEROUS,
                description="Format filesystem",
                severity="critical"
            ),
            SafetyRule(
                pattern=re.compile(r"dd\s+if=.*of=/dev/[sh]d", re.IGNORECASE),
                category=CommandCategory.DANGEROUS,
                description="Direct disk write",
                severity="critical"
            ),
            
            # High - System control
            SafetyRule(
                pattern=re.compile(r"shutdown|poweroff|reboot|init\s+[06]", re.IGNORECASE),
                category=CommandCategory.DANGEROUS,
                description="System shutdown/reboot",
                severity="high"
            ),
            SafetyRule(
                pattern=re.compile(r"Stop-Computer|Restart-Computer", re.IGNORECASE),
                category=CommandCategory.DANGEROUS,
                description="PowerShell system control",
                severity="high"
            ),
            
            # Medium - Potentially destructive
            SafetyRule(
                pattern=re.compile(r"del\s+/[sf]|Remove-Item.*-Recurse", re.IGNORECASE),
                category=CommandCategory.DANGEROUS,
                description="Recursive deletion",
                severity="medium"
            ),
            SafetyRule(
                pattern=re.compile(r"format\s+[a-z]:", re.IGNORECASE),
                category=CommandCategory.DANGEROUS,
                description="Format drive",
                severity="medium"
            ),
            
            # Interactive commands
            SafetyRule(
                pattern=re.compile(r"^(nano|vim?|emacs|code|notepad)", re.IGNORECASE),
                category=CommandCategory.INTERACTIVE,
                description="Text editor",
                severity="low"
            ),
            SafetyRule(
                pattern=re.compile(r"^(cd|pushd|popd|Set-Location)", re.IGNORECASE),
                category=CommandCategory.DIRECTORY_CHANGE,
                description="Directory navigation",
                severity="low"
            ),
            
            # Long-running commands
            SafetyRule(
                pattern=re.compile(r"^(ping|tracert|traceroute|tail\s+-f)", re.IGNORECASE),
                category=CommandCategory.LONG_RUNNING,
                description="Long-running process",
                severity="low"
            ),
        ]
    
    def check_command(self, command_str: str) -> Optional[SafetyRule]:
        """
        Check if a command matches any safety rule.
        
        Args:
            command_str: Command string to check
        
        Returns:
            Matching SafetyRule if found, None otherwise
        """
        for rule in self.rules:
            if rule.pattern.search(command_str):
                return rule
        return None
    
    def validate_command(self, command: Command) -> tuple[bool, Optional[str]]:
        """
        Validate a command for safety.
        
        Args:
            command: Command object to validate
        
        Returns:
            Tuple of (is_safe, error_message)
        """
        rule = self.check_command(command.raw_command)
        
        if not rule:
            command.category = CommandCategory.SAFE
            return True, None
        
        command.category = rule.category
        
        # Block critical and high severity in strict mode
        if self.strict_mode and rule.severity in ["critical", "high"]:
            return False, f"Command blocked: {rule.description} (severity: {rule.severity})"
        
        # Block all dangerous commands
        if rule.category == CommandCategory.DANGEROUS:
            return False, f"Dangerous command blocked: {rule.description}"
        
        # Allow but categorize other commands
        return True, None
    
    def suggest_safer_alternative(self, command: str) -> Optional[str]:
        """
        Suggest a safer alternative for a dangerous command.
        
        Args:
            command: Original command
        
        Returns:
            Safer alternative if available
        """
        alternatives = {
            r"rm\s+-rf": "rm -i",  # Interactive deletion
            r"dd\s+if=": "Use 'cp' or 'rsync' for file copying",
            r"shutdown": "Use 'logout' to end session",
            r"format": "Use disk management tools with GUI",
        }
        
        for pattern, suggestion in alternatives.items():
            if re.search(pattern, command, re.IGNORECASE):
                return suggestion
        
        return None