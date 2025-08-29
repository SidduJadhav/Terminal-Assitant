"""Command execution and suggestion logic."""

import subprocess
import time
from typing import Optional, Tuple
from pathlib import Path

from .models import Command, CommandCategory, ExecutionResult, ShellType
from .shell_utils import get_shell_executable


class CommandExecutor:
    """Handles command execution and suggestion."""

    def __init__(self, timeout: int = 15, verbose: bool = False):
        """
        Initialize command executor.
        
        Args:
            timeout: Default timeout for commands in seconds
            verbose: Enable verbose output
        """
        self.timeout = timeout
        self.verbose = verbose

    def should_suggest_only(self, command: Command) -> bool:
        """
        Determine if a command should only be suggested, not executed.
        
        Args:
            command: Command to check
        
        Returns:
            True if command should only be suggested
        """
        return command.category in [
            CommandCategory.INTERACTIVE,
            CommandCategory.DIRECTORY_CHANGE,
            CommandCategory.LONG_RUNNING,
        ]

    def suggest_command(self, command: Command) -> None:
        """
        Display command suggestion to user.
        
        Args:
            command: Command to suggest
        """
        print("\nCommand Suggestion:")
        print("=" * 60)
        print(f"Command: {command.raw_command}")
        print("=" * 60)

        if command.explanation:
            print(f"Details: {command.explanation}")

        if command.category == CommandCategory.DIRECTORY_CHANGE:
            print("Note: Directory changes must be executed directly in your shell to persist.")
        elif command.category == CommandCategory.INTERACTIVE:
            print("Note: Interactive commands should be executed directly in your shell.")
        elif command.category == CommandCategory.LONG_RUNNING:
            print("Note: This command may run for an extended period (Ctrl+C to stop).")

        if command.alternatives:
            print("\nAlternative commands:")
            for alt in command.alternatives:
                print(f"  - {alt}")

    def execute_command(
        self,
        command: Command,
        shell_type: ShellType,
        working_dir: Optional[Path] = None
    ) -> ExecutionResult:
        """
        Execute a shell command.
        
        Args:
            command: Command to execute
            shell_type: Type of shell to use
            working_dir: Optional working directory
        
        Returns:
            ExecutionResult with execution details
        """
        start_time = time.time()

        try:
            shell_exec = get_shell_executable(shell_type)

            subprocess_args = {
                "capture_output": True,
                "text": True,
                "timeout": self.timeout,
            }

            if working_dir:
                subprocess_args["cwd"] = str(working_dir)

            if self.verbose:
                print(f"Executing: {command.raw_command}")
                print(f"Shell: {shell_type.value}")
                print(f"Timeout: {self.timeout}s")

            result = subprocess.run(
                shell_exec + [command.raw_command],
                **subprocess_args
            )

            execution_time = time.time() - start_time

            return ExecutionResult(
                success=(result.returncode == 0),
                stdout=result.stdout.strip(),
                stderr=result.stderr.strip(),
                return_code=result.returncode,
                execution_time=execution_time
            )

        except subprocess.TimeoutExpired:
            return ExecutionResult(
                success=False,
                error_message=f"Command timed out after {self.timeout} seconds",
                execution_time=self.timeout
            )
        except FileNotFoundError as e:
            return ExecutionResult(
                success=False,
                error_message=f"Shell executable not found: {e}"
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                error_message=f"Execution failed: {str(e)}",
                execution_time=time.time() - start_time
            )

    def format_result(self, result: ExecutionResult) -> None:
        """
        Format and display execution result.
        
        Args:
            result: Execution result to display
        """
        print("\nExecution Result:")
        print("=" * 60)

        if result.success:
            if result.stdout:
                print(result.stdout)
            if self.verbose and result.execution_time:
                print(f"\nCompleted in {result.execution_time:.2f} seconds")
        else:
            if result.stderr:
                print(f"Error Output:\n{result.stderr}")
            if result.error_message:
                print(f"Error: {result.error_message}")
            if result.return_code is not None:
                print(f"Return Code: {result.return_code}")

    def confirm_execution(self, command: Command) -> bool:
        """
        Ask user for confirmation before executing command.
        
        Args:
            command: Command to confirm
        
        Returns:
            True if user confirms execution
        """
        print(f"\nProposed Command: {command.raw_command}")

        if command.explanation:
            print(f"Details: {command.explanation}")

        if command.confidence < 0.7:
            print(f"Warning: Low confidence ({command.confidence:.0%})")

        response = input("\nExecute this command? (y/n): ").strip().lower()
        return response in ['y', 'yes']
