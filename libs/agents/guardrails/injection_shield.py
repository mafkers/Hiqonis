import logging
import re
from typing import Tuple

logger = logging.getLogger("hiqonis.guardrails")

class HiqonisInjectionShield:
    """Security guardrail shielding AI agents from prompt injection and leakage attacks."""

    def __init__(self):
        # 1. Regex patterns representing jailbreak signatures and override attempts
        self.injection_patterns = [
            r"ignore\s+(?:all\s+)?(?:previous|prior)\s+(?:rules|instructions|directives|prompts)",
            r"forget\s+(?:your\s+)?(?:rules|instructions|directives|system|context)",
            r"you\s+are\s+now\s+(?:an?\s+)?(?:developer|unrestricted|unbound|jailbroken|system\s+admin)",
            r"DAN\s+(?:mode|do\s+anything\s+now)",
            r"system\s+override\s+initiated",
            r"(?:disable|bypass|deactivate)\s+(?:your\s+)?(?:filters|safety|guardrails|moderation)",
            r"ignore\s+what\s+was\s+written\s+above"
        ]
        
        # 2. System prompt leakage indicator patterns
        self.leakage_patterns = [
            r"output\s+(?:your\s+)?(?:system\s+)?(?:instructions|prompt|rules|directives)",
            r"show\s+(?:your\s+)?(?:system\s+)?(?:instructions|prompt|rules|directives)",
            r"reveal\s+(?:your\s+)?(?:system\s+)?(?:instructions|prompt|rules|directives)",
            r"what\s+is\s+your\s+(?:system\s+)?(?:prompt|instruction|rule)",
            r"copy\s+and\s+paste\s+(?:your\s+)?(?:system\s+)?(?:prompt|rules)"
        ]

        # Compile for speed
        self.rx_injections = [re.compile(p, re.IGNORECASE) for p in self.injection_patterns]
        self.rx_leakages = [re.compile(p, re.IGNORECASE) for p in self.leakage_patterns]

    async def verify_prompt_safety(self, prompt: str) -> Tuple[bool, str]:
        """Analyzes a customer prompt to identify prompt injection attacks.

        Returns:
            Tuple[bool, str]: (is_safe, explanation_reason)
        """
        if not prompt or not isinstance(prompt, str):
            return True, ""

        clean_prompt = prompt.strip()

        # A. Check Jailbreak / Override Injections
        for rx in self.rx_injections:
            if rx.search(clean_prompt):
                logger.warning(f"Adversarial prompt injection signature detected matching pattern: {rx.pattern}")
                return False, "Adversarial override signature detected."

        # B. Check System Prompt Leakage attempts
        for rx in self.rx_leakages:
            if rx.search(clean_prompt):
                logger.warning(f"System leakage attempt signature detected matching pattern: {rx.pattern}")
                return False, "Prompt leakage attempt signature detected."

        # C. Check for unusual command shells/system escape sequences
        if any(keyword in clean_prompt.lower() for keyword in ["sudo rm -rf", "/bin/bash", "cmd.exe", "powershell"]):
            logger.warning("System escape instruction indicators detected.")
            return False, "System escape indicators detected."

        return True, ""
