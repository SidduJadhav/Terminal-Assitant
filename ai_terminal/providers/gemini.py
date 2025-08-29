"""Google Gemini AI provider implementation."""

from typing import Optional
import google.generativeai as genai

from .base import AIProvider
from ..models import ShellContext, Command, CommandCategory


class GeminiProvider(AIProvider):
    """Google Gemini AI provider."""
    
    def __init__(self, api_key: str, model_name: Optional[str] = None):
        """
        Initialize Gemini provider.
        
        Args:
            api_key: Gemini API key
            model_name: Model name (default: gemini-1.5-flash)
        """
        self.api_key = api_key
        self.model_name = model_name or "gemini-1.5-flash"
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
    
    def generate_command(
        self,
        query: str,
        context: ShellContext,
        examples: Optional[list] = None
    ) -> Optional[Command]:
        """
        Generate command using Gemini.
        
        Args:
            query: Natural language query
            context: Shell context
            examples: Optional examples
        
        Returns:
            Command object or None
        """
        try:
            prompt = self.format_prompt(query, context, examples)
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                return None
            
            # Clean up the response
            command_text = response.text.strip()
            
            # Remove markdown formatting if present
            command_text = command_text.replace("```bash", "")
            command_text = command_text.replace("```powershell", "")
            command_text = command_text.replace("```cmd", "")
            command_text = command_text.replace("```", "")
            command_text = command_text.strip()
            
            # Take only first line if multiple
            if "\n" in command_text:
                command_text = command_text.split("\n")[0].strip()
            
            return Command(
                raw_command=command_text,
                confidence=0.8,  # Default confidence for Gemini
                explanation=f"Generated from: {query}"
            )
            
        except Exception as e:
            print(f"Gemini generation failed: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if Gemini is available."""
        try:
            # Try a simple generation to test availability
            test_response = self.model.generate_content("echo test")
            return test_response is not None
        except:
            return False