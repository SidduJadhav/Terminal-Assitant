"""Core assistant orchestration logic."""

from typing import Optional

from .config import Config
from .models import ShellContext, Command
from .shell_utils import get_shell_context
from .safety import SafetyFilter
from .ai_engine import AIEngine
from .executor import CommandExecutor
from pathlib import Path



class AITerminalAssistant:
    """Main assistant that orchestrates all components."""
    
    def __init__(self, config: Config):
        """
        Initialize the AI Terminal Assistant.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.context = get_shell_context()
        self.safety_filter = SafetyFilter(strict_mode=config.enable_safety_filter)
        self.ai_engine = AIEngine(config)
        self.executor = CommandExecutor(
            timeout=config.default_timeout,
            verbose=config.verbose
        )
    
    def process_query(
        self,
        query: str,
        suggest_only: bool = False,
        skip_confirmation: bool = False
    ) -> bool:
        """
        Process a natural language query and execute the resulting command.
        
        Args:
            query: Natural language query
            suggest_only: If True, only suggest commands without executing
            skip_confirmation: If True, skip user confirmation
        
        Returns:
            True if successful, False otherwise
        """
        # Display query and context
        print(f"\n🔸 Query: {query}")
        if self.config.verbose:
            self._display_context()
        
        # Generate command
        command = self.ai_engine.generate_command(query, self.context)
        
        if not command:
            print("❌ Could not generate a command for this query.")
            self._suggest_help(query)
            return False
        
        # Safety check
        is_safe, safety_message = self.safety_filter.validate_command(command)
        
        if not is_safe:
            print(f"🛡️ {safety_message}")
            
            
            alternative = self.safety_filter.suggest_safer_alternative(
                command.raw_command
            )
            if alternative:
                print(f"💡 Safer alternative: {alternative}")
            
            return False
        
        
        if suggest_only or self.executor.should_suggest_only(command):
            self.executor.suggest_command(command)
            return True
        
       
        if not skip_confirmation and self.config.require_confirmation:
            if not self.executor.confirm_execution(command):
                print("❌ Command execution cancelled.")
                return False
        
        
        print("⚡ Executing command...\n")
        result = self.executor.execute_command(
            command,
            self.context.shell_type,
            working_dir=Path(self.context.current_directory)
        )
        
       
        self.executor.format_result(result)
        
        return result.success
    
    def _display_context(self) -> None:
        """Display current shell context."""
        print(f"🔹 Shell: {self.context.shell_type.value}")
        print(f"🔹 OS: {self.context.os_name}")
        print(f"🔹 Directory: {self.context.current_directory}")
        
        if self.context.is_virtual_env:
            print(f"🐍 Python environment: {self.context.virtual_env_name}")
            print(f"   Package manager: {self.context.package_manager}")
        
        if self.context.is_admin:
            print("⚠️ Running with administrative privileges")
    
    def _suggest_help(self, query: str) -> None:
        """Suggest help for failed queries."""
        print("\n💡 Suggestions:")
        print("   • Try rephrasing your request")
        print("   • Be more specific about what you want to do")
        print("   • Check if the operation is supported on your system")
        
       
        examples = [
            "list all files",
            "create a file named test.txt",
            "install pandas package",
            "show current directory",
            "clear the screen",
        ]
        
        print("\n📝 Example queries:")
        for example in examples:
            print(f"   • {example}")