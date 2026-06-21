import re

class EnterpriseGuardrail:
    """
    Security and Compliance Engine for Advanced RAG.
    Handles real-time PII anonymization and adversarial prompt injection detection.
    """
    
    # Pre-compiled high-performance regex signatures for standard enterprise PII
    PII_PATTERNS = {
        "EMAIL": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "PHONE_NUMBER": r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b",
        "CREDIT_CARD": r"\b\d{4}[-.\s]?\d{4}[-.\s]?\d{4}[-.\s]?\d{4}\b",
        "API_KEY": r"\b(sk-[a-zA-Z0-9]{32,48}|AIzaSy[a-zA-Z0-9-_]{33})\b",
        "IP_ADDRESS": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"
    }

    # Common malicious prompt injection vectors used to jailbreak enterprise RAG setups
    INJECTION_SIGNATURES = [
        r"ignore\s+(any|previous)\s+instructions",
        r"system\s+prompt\s+override",
        r"you\s+are\s+now\s+an\s+unrestricted",
        r"reveal\s+(your|the)\s+hidden\s+instructions",
        r"bypass\s+all\s+guardrails",
        r"output\s+the\s+system\s+prompt"
    ]

    @classmethod
    def mask_sensitive_data(cls, text: str) -> str:
        """
        Scans and masks matching PII vectors with clean corporate compliance tags.
        """
        sanitized_text = text
        for pii_type, pattern in cls.PII_PATTERNS.items():
            sanitized_text = re.sub(pattern, f"[{pii_type}_MASKED]", sanitized_text)
        return sanitized_text

    @classmethod
    def check_prompt_injection(cls, text: str) -> bool:
        """
        Evaluates incoming prompt matrices against known injection patterns.
        Returns True if a threat pattern matches.
        """
        normalized_text = text.lower()
        for signature in cls.INJECTION_SIGNATURES:
            if re.search(signature, normalized_text):
                return True
        return False

    @classmethod
    def process_incoming_query(cls, raw_query: str):
        """
        Main routing validator wrapper block.
        
        :return: Tuple[bool, str] -> (is_safe, processed_or_error_text)
        """
        # 1. Audit against adversarial injections
        if cls.check_prompt_injection(raw_query):
            return False, "🔒 Security Alert: Malicious interaction matrix signatures detected. Query dropped."
        
        # 2. Sanitize and anonymize raw PII leak variants
        clean_query = cls.mask_sensitive_data(raw_query)
        return True, clean_query