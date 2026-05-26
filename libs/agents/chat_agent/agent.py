from google.antigravity import Agent as AGYAgent, LocalAgentConfig
from typing import AsyncGenerator, Optional, List

class HiqonisChatAgent:
    """Wrapper class around Google Antigravity SDK for Hiqonis AI Agents."""
    
    def __init__(
        self, 
        system_instructions: str, 
        model_name: str = "gemini-2.5-flash", 
        api_key: Optional[str] = None
    ):
        self.system_instructions = system_instructions
        self.model_name = model_name
        self.api_key = api_key
        
    async def chat(self, prompt: str) -> str:
        """Send a standard turn-based prompt to the agent and receive a full response."""
        config = LocalAgentConfig(
            system_instructions=self.system_instructions,
            model=self.model_name,
            api_key=self.api_key
        )
        async with AGYAgent(config=config) as agent:
            response = await agent.chat(prompt)
            return await response.text()
            
    async def chat_stream(self, prompt: str) -> AsyncGenerator[str, None]:
        """Send a turn prompt and yield tokens as they stream from the Google GenAI backend."""
        config = LocalAgentConfig(
            system_instructions=self.system_instructions,
            model=self.model_name,
            api_key=self.api_key
        )
        async with AGYAgent(config=config) as agent:
            response = await agent.chat(prompt)
            async for token in response:
                yield token
                
    async def chat_thoughts_stream(self, prompt: str) -> AsyncGenerator[str, None]:
        """Send a prompt and yield internal model thoughts (reasoning process) as they stream."""
        config = LocalAgentConfig(
            system_instructions=self.system_instructions,
            model=self.model_name,
            api_key=self.api_key
        )
        async with AGYAgent(config=config) as agent:
            response = await agent.chat(prompt)
            async for thought in response.thoughts:
                yield thought
