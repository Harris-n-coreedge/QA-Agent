"""
Safety policies and anti-detection measures.
"""
import asyncio
import random
from typing import Dict, Any
from dataclasses import dataclass

from qa_agent.core.config import settings


@dataclass
class PolicyConfig:
    """Configuration for simulation policies."""
    human_like: bool = True
    min_delay_ms: int = 100
    max_delay_ms: int = 1000
    typing_delay_ms: int = 50
    max_step_timeout_ms: int = 15000
    retry_attempts: int = 3


class PolicyManager:
    """Manages safety and anti-detection policies."""
    
    def __init__(self):
        self.config = PolicyConfig()
    
    async def apply_step_policies(self, step: Dict[str, Any]) -> None:
        """Apply policies after step execution."""
        if not self.config.human_like:
            return
        
        # Random delay between steps
        delay = random.randint(
            self.config.min_delay_ms,
            self.config.max_delay_ms
        )
        await asyncio.sleep(delay / 1000)
    
    async def apply_typing_policy(self, text: str) -> None:
        """Apply human-like typing delays."""
        if not self.config.human_like:
            return
        
        for char in text:
            await asyncio.sleep(self.config.typing_delay_ms / 1000)
            
            # Occasional longer pauses (thinking)
            if random.random() < 0.1:
                await asyncio.sleep(random.randint(200, 800) / 1000)
    
    def get_step_timeout(self, step: Dict[str, Any]) -> int:
        """Get timeout for a step."""
        return step.get("timeout", self.config.max_step_timeout_ms)
    
    def get_retry_attempts(self, step: Dict[str, Any]) -> int:
        """Get retry attempts for a step."""
        return step.get("retry_attempts", self.config.retry_attempts)
    
    def is_destructive_action(self, step: Dict[str, Any]) -> bool:
        """Check if step is potentially destructive."""
        destructive_types = ["delete", "remove", "clear"]
        step_type = step.get("type", "")
        
        return step_type in destructive_types
    
    def should_skip_step(self, step: Dict[str, Any]) -> bool:
        """Check if step should be skipped based on policies."""
        # Skip destructive actions in safe mode
        if settings.ENV != "prod" and self.is_destructive_action(step):
            return True
        
        return False
