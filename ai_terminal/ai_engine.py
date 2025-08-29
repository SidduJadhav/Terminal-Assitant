"""AI engine coordinator for command generation."""

from typing import Optional, Dict, Type
from enum import Enum

from .config import Config
from .models import Command, ShellContext
from .providers.base import AIProvider
from .providers.gemini import GeminiProvider
from .fallback import FallbackHandler


class AIProviderType(Enum):
    """Available AI provider types."""
    GEMINI = "gemini"
    OPENAI = "openai"
    CLAUDE = "claude"


class AIEngine:
    """Manages AI providers and command generation."""
 
    PROVIDERS: Dict[AIProviderType, Type[AIProvider]] = {
        AIProviderType.GEMINI: GeminiProvider,
        
    }
    
    def __init__(self, config: Config):
        """
        Initialize AI engine with configuration.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.fallback_handler = FallbackHandler()
        self.provider = self._initialize_provider()
    
    def _initialize_provider(self) -> Optional[AIProvider]:
        """Initialize the configured AI provider."""
        try:
            provider_type = AIProviderType(self.config.ai_provider)
            provider_class = self.PROVIDERS.get(provider_type)
            
            if not provider_class:
                print(f"⚠️ Provider '{self.config.ai_provider}' not implemented yet")
                return None
            
           
            api_key = self._get_api_key(provider_type)
            if not api_key:
                print(f"⚠️ No API key found for {provider_type.value}")
                return None
            
           
            provider = provider_class(api_key, self.config.model_name)
            
         
            if not provider.is_available():
                print(f"⚠️ Provider {provider_type.value} is not available")
                return None
            
            return provider
            
        except Exception as e:
            print(f"⚠️ Failed to initialize AI provider: {e}")
            return None
    
    def _get_api_key(self, provider_type: AIProviderType) -> Optional[str]:
        """Get API key for the specified provider."""
        key_mapping = {
            AIProviderType.GEMINI: self.config.gemini_api_key,
            AIProviderType.OPENAI: self.config.openai_api_key,
            AIProviderType.CLAUDE: self.config.claude_api_key,
        }
        return key_mapping.get(provider_type)
    
    def generate_command(
        self,
        query: str,
        context: ShellContext
    ) -> Optional[Command]:
        """
        Generate a shell command from natural language.
        
        Args:
            query: Natural language query
            context: Shell context information
        
        Returns:
            Command object or None
        """
        command = None
        
        
        if self.provider:
            if self.config.verbose:
                print(f"🤖 Using {self.config.ai_provider} provider...")
            
            command = self.provider.generate_command(query, context)
            
            if command and self.config.verbose:
                print(f"✅ AI generated: {command.raw_command}")
        
       
        if not command:
            if self.config.verbose:
                print("🔄 Trying fallback patterns...")
            
            command = self.fallback_handler.generate_command(query, context)
            
            if command and self.config.verbose:
                print(f"✅ Fallback generated: {command.raw_command}")
        
        return command
    
    def switch_provider(self, provider_name: str) -> bool:
        """
        Switch to a different AI provider.
        
        Args:
            provider_name: Name of the provider to switch to
        
        Returns:
            True if switch was successful
        """
        self.config.ai_provider = provider_name
        new_provider = self._initialize_provider()
        
        if new_provider:
            self.provider = new_provider
            return True
        
        return False