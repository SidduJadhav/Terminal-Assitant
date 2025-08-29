"""Shell detection and utility functions."""

import os
import platform
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import getpass


from .models import ShellType, ShellContext


def detect_shell() -> ShellType:
    """
    Detect the current shell type.
    
    Returns:
        ShellType enum value
    """
    system = platform.system()
    
    if system == "Windows":
       
        if os.getenv("PSModulePath"):
            return ShellType.POWERSHELL
        elif os.getenv("PROMPT"):
            prompt = os.getenv("PROMPT", "")
            if "PS" in prompt:
                return ShellType.POWERSHELL
            return ShellType.CMD
        else:
            return ShellType.CMD
    else:
      
        shell_env = os.getenv("SHELL", "").lower()
        if "zsh" in shell_env:
            return ShellType.ZSH
        elif "fish" in shell_env:
            return ShellType.FISH
        elif "bash" in shell_env:
            return ShellType.BASH
        else:
          
            return ShellType.BASH


def get_shell_executable(shell_type: ShellType) -> List[str]:
    """
    Get the shell executable command for a given shell type.
    
    Args:
        shell_type: Type of shell
    
    Returns:
        List of command parts for subprocess
    """
    executables = {
        ShellType.POWERSHELL: ["powershell.exe", "-Command"],
        ShellType.CMD: ["cmd.exe", "/c"],
        ShellType.BASH: ["/bin/bash", "-c"],
        ShellType.ZSH: ["/bin/zsh", "-c"],
        ShellType.FISH: ["/usr/bin/fish", "-c"],
    }
    
    return executables.get(shell_type, ["/bin/bash", "-c"])


def detect_python_environment() -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Detect Python virtual environment information.
    
    Returns:
        Tuple of (is_venv, venv_name, package_manager)
    """
   
    if venv_path := os.getenv("VIRTUAL_ENV"):
        return True, Path(venv_path).name, "pip"
    
   
    if conda_env := os.getenv("CONDA_DEFAULT_ENV"):
        return True, conda_env, "conda"
    
  
    if os.getenv("POETRY_ACTIVE"):
        return True, "poetry", "poetry"
    
   
    if os.getenv("PIPENV_ACTIVE"):
        return True, "pipenv", "pipenv"
    
    return False, None, "pip"


def is_admin() -> bool:
    """
    Check if running with administrative privileges.
    
    Returns:
        True if running as admin/root
    """
    if platform.system() == "Windows":
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
    else:
        return os.getuid() == 0


def get_shell_context() -> ShellContext:
    """
    Get comprehensive shell context information.
    
    Returns:
        ShellContext object with environment details
    """
    shell_type = detect_shell()
    is_venv, venv_name, pkg_manager = detect_python_environment()
    
    return ShellContext(
        shell_type=shell_type,
        os_name=platform.system(),
        is_admin=is_admin(),
        is_virtual_env=is_venv,
        virtual_env_name=venv_name,
        package_manager=pkg_manager,
        current_directory=os.getcwd(),
        environment_vars=dict(os.environ),
    )


def get_basic_commands(shell_type: ShellType) -> Dict[str, str]:
    """
    Get basic command mappings for a shell type.
    
    Args:
        shell_type: Type of shell
    
    Returns:
        Dictionary of common command descriptions to actual commands
    """
    if shell_type == ShellType.POWERSHELL:
        return {
            "list files": "Get-ChildItem",
            "show current directory": "Get-Location",
            "clear screen": "Clear-Host",
            "list processes": "Get-Process",
            "create file": "New-Item -ItemType File -Name",
            "create directory": "New-Item -ItemType Directory -Name",
            "remove file": "Remove-Item",
            "copy file": "Copy-Item",
            "move file": "Move-Item",
            "show file content": "Get-Content",
            "search text": "Select-String",
            "system info": "Get-ComputerInfo",
        }
    elif shell_type == ShellType.CMD:
        return {
            "list files": "dir",
            "show current directory": "cd",
            "clear screen": "cls",
            "list processes": "tasklist",
            "create file": "type nul >",
            "create directory": "mkdir",
            "remove file": "del",
            "copy file": "copy",
            "move file": "move",
            "show file content": "type",
            "search text": "findstr",
            "system info": "systeminfo",
        }
    else:  # Unix-like shells
        return {
            "list files": "ls -la",
            "show current directory": "pwd",
            "clear screen": "clear",
            "list processes": "ps aux",
            "create file": "touch",
            "create directory": "mkdir -p",
            "remove file": "rm",
            "copy file": "cp",
            "move file": "mv",
            "show file content": "cat",
            "search text": "grep",
            "system info": "uname -a",
            "disk usage": "df -h",
            "memory usage": "free -h",
        }