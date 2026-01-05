from django.conf import settings
from .providers.base import AIProvider
import import_module_logic # Placeholder for dynamic import

class AIService:
    _provider = None

    @classmethod
    def get_provider(cls) -> AIProvider:
        if cls._provider is None:
            # In a real app, we'd load this from settings.AI_PROVIDER
            # e.g., 'apps.ai_bridge.providers.openai_provider.OpenAIProvider'
            from .providers.mock_provider import MockAIProvider
            cls._provider = MockAIProvider()
        return cls._provider

    @classmethod
    def process_document(cls, document):
        """
        Main entry point for AI processing of an uploaded document.
        """
        provider = cls.get_provider()
        
        # 1. Extraction
        try:
            extraction_result = provider.extract_invoice_data(document.file.path)
            document.ai_metadata = extraction_result
            document.save()
            return extraction_result
        except Exception as e:
            # Handle AI failure gracefully
            raise e
