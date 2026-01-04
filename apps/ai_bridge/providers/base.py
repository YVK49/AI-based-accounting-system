from abc import ABC, abstractmethod

class AIProvider(ABC):
    """
    Abstract Interface for AI Providers.
    Allows swapping between OpenAI, Anthropic, or Local LLMs.
    """
    
    @abstractmethod
    def extract_invoice_data(self, file_path):
        """
        Extracts accounting metadata from an invoice image/pdf.
        """
        pass

    @abstractmethod
    def classify_transaction(self, narration):
        """
        Suggests Ledger Account based on narration.
        """
        pass

    @abstractmethod
    def generate_compliance_explanation(self, context_data):
        """
        Explains "Why is tax high?" etc in plain language.
        """
        pass
