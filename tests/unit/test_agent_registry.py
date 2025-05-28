"""
Unit tests for AgentRegistry dependency injection system.

Tests registration, discovery, health checks, and thread safety.
"""

import pytest
import asyncio
import threading
from unittest.mock import Mock, AsyncMock, MagicMock
from datetime import datetime

from core.agent_registry import (
    AgentRegistry, AgentStatus, AgentMetadata,
    register_agent, get_agent, discover_agents
)
from agents.base_agent import BaseAgent
from agents.base_agent_v2 import BaseAgentV2
from interfaces.agent_models import AgentCapabilities, AgentInput, AgentOutput


# Test agent implementations
class TestAgent(BaseAgent):
    """Simple test agent."""
    
    def __init__(self):
        super().__init__("Test Agent", "A test agent")
        
    async def initialize(self):
        self._initialized = True
        
    async def process(self, input_data: AgentInput) -> AgentOutput:
        return AgentOutput(
            task_id=input_data.task_id,
            agent_id=self.agent_id,
            status="success",
            result={"processed": True}
        )
    
    def get_capabilities(self):
        return []


class TestAgentV2(BaseAgentV2):
    """Test agent with v2 features."""
    
    def __init__(self):
        super().__init__(
            "Test Agent V2", 
            "An enhanced test agent",
            tags=["test", "v2"],
            auto_register=False  # Disable for controlled testing
        )
        
    async def initialize(self):
        self._initialized = True
        
    async def process(self, input_data: AgentInput) -> AgentOutput:
        return self.create_output(
            task_id=input_data.task_id,
            result={"enhanced": True}
        )
    
    def get_capabilities(self):
        return []
    
    def _build_capabilities(self):
        return AgentCapabilities(
            can_process_files=True,
            supported_formats=["txt", "json"]
        )


class UnhealthyAgent(BaseAgent):
    """Agent that fails health checks."""
    
    def __init__(self):
        super().__init__("Unhealthy Agent", "Always fails")
        
    async def initialize(self):
        raise RuntimeError("Initialization failed")
        
    async def process(self, input_data: AgentInput) -> AgentOutput:
        raise RuntimeError("Processing failed")
    
    def get_capabilities(self):
        return []
    
    async def health_check(self):
        return False


class TestAgentRegistry:
    """Test cases for AgentRegistry."""
    
    @pytest.fixture
    def registry(self):
        """Create a fresh registry for each test."""
        # Create new instance and clear it
        reg = AgentRegistry()
        reg.clear()
        return reg
    
    def test_singleton_pattern(self):
        """Test that AgentRegistry is a singleton."""
        reg1 = AgentRegistry()
        reg2 = AgentRegistry()
        assert reg1 is reg2
    
    def test_register_agent(self, registry):
        """Test basic agent registration."""
        registry.register(
            agent_id="test_agent",
            agent_class=TestAgent,
            version="1.0.0",
            description="Test agent"
        )
        
        # Verify registration
        metadata = registry.get_metadata("test_agent")
        assert metadata is not None
        assert metadata.agent_id == "test_agent"
        assert metadata.agent_class == TestAgent
        assert metadata.version == "1.0.0"
        assert metadata.status == AgentStatus.REGISTERED
    
    def test_register_duplicate_agent(self, registry):
        """Test registering duplicate agent without replace flag."""
        registry.register("test_agent", TestAgent)
        
        # Should raise error without replace=True
        with pytest.raises(ValueError, match="already registered"):
            registry.register("test_agent", TestAgent)
    
    def test_register_replace_agent(self, registry):
        """Test replacing an existing agent registration."""
        registry.register("test_agent", TestAgent, version="1.0.0")
        registry.register("test_agent", TestAgentV2, version="2.0.0", replace=True)
        
        metadata = registry.get_metadata("test_agent")
        assert metadata.agent_class == TestAgentV2
        assert metadata.version == "2.0.0"
    
    def test_register_invalid_agent_class(self, registry):
        """Test registering a non-agent class."""
        class NotAnAgent:
            pass
        
        with pytest.raises(TypeError, match="must be a subclass of BaseAgent"):
            registry.register("invalid", NotAnAgent)
    
    def test_get_agent(self, registry):
        """Test getting an agent instance."""
        registry.register("test_agent", TestAgent)
        
        agent = registry.get("test_agent")
        assert agent is not None
        assert isinstance(agent, TestAgent)
        assert registry.get_metadata("test_agent").status == AgentStatus.INITIALIZED
        
        # Getting again should return same instance
        agent2 = registry.get("test_agent")
        assert agent is agent2
    
    def test_get_nonexistent_agent(self, registry):
        """Test getting an agent that doesn't exist."""
        agent = registry.get("nonexistent")
        assert agent is None
    
    def test_get_agent_initialization_failure(self, registry):
        """Test getting an agent that fails to initialize."""
        registry.register("unhealthy", UnhealthyAgent)
        
        agent = registry.get("unhealthy")
        assert agent is None
        
        metadata = registry.get_metadata("unhealthy")
        assert metadata.status == AgentStatus.UNHEALTHY
        assert len(metadata.health_check_errors) > 0
    
    def test_discover_agents_by_tags(self, registry):
        """Test discovering agents by tags."""
        registry.register("agent1", TestAgent, tags=["test", "v1"])
        registry.register("agent2", TestAgentV2, tags=["test", "v2"])
        registry.register("agent3", TestAgent, tags=["production"])
        
        # Find all test agents
        test_agents = registry.discover(tags=["test"])
        assert set(test_agents) == {"agent1", "agent2"}
        
        # Find v2 agents
        v2_agents = registry.discover(tags=["v2"])
        assert v2_agents == ["agent2"]
    
    def test_discover_agents_by_status(self, registry):
        """Test discovering agents by status."""
        registry.register("agent1", TestAgent)
        registry.register("agent2", UnhealthyAgent)
        
        # Initialize agent1
        registry.get("agent1")
        
        # Find initialized agents
        initialized = registry.discover(status=AgentStatus.INITIALIZED)
        assert initialized == ["agent1"]
        
        # Find registered (not initialized) agents
        registered = registry.discover(status=AgentStatus.REGISTERED)
        assert registered == ["agent2"]
    
    def test_discover_agents_by_capabilities(self, registry):
        """Test discovering agents by capabilities."""
        registry.register("agent1", TestAgentV2)
        registry.register("agent2", TestAgent)
        
        # Create instances to populate capabilities
        agent1 = registry.get("agent1")
        metadata1 = registry.get_metadata("agent1")
        metadata1.capabilities = agent1._build_capabilities()
        
        # Find agents that can process files
        file_processors = registry.discover(capabilities={"can_process_files": True})
        assert file_processors == ["agent1"]
    
    def test_list_agents(self, registry):
        """Test listing all agents."""
        registry.register("agent1", TestAgent, version="1.0.0")
        registry.register("agent2", TestAgentV2, version="2.0.0")
        
        agents = registry.list_agents()
        assert len(agents) == 2
        assert "agent1" in agents
        assert "agent2" in agents
        assert agents["agent1"]["version"] == "1.0.0"
        assert agents["agent2"]["version"] == "2.0.0"
    
    @pytest.mark.asyncio
    async def test_health_check(self, registry):
        """Test health checking an agent."""
        registry.register("healthy", TestAgent)
        registry.register("unhealthy", UnhealthyAgent)
        
        # Initialize healthy agent
        agent = registry.get("healthy")
        await agent.initialize()
        
        # Check healthy agent
        is_healthy = await registry.health_check("healthy")
        assert is_healthy is True
        
        metadata = registry.get_metadata("healthy")
        assert metadata.status == AgentStatus.HEALTHY
        assert metadata.last_health_check is not None
        
        # Check unhealthy agent
        is_unhealthy = await registry.health_check("unhealthy")
        assert is_unhealthy is False
        
        metadata = registry.get_metadata("unhealthy")
        assert metadata.status == AgentStatus.UNHEALTHY
    
    @pytest.mark.asyncio
    async def test_health_check_all(self, registry):
        """Test health checking all agents."""
        registry.register("agent1", TestAgent)
        registry.register("agent2", TestAgent)
        registry.register("unhealthy", UnhealthyAgent)
        
        # Initialize first two agents
        for agent_id in ["agent1", "agent2"]:
            agent = registry.get(agent_id)
            await agent.initialize()
        
        results = await registry.health_check_all()
        
        assert results["agent1"] is True
        assert results["agent2"] is True
        assert results["unhealthy"] is False
    
    def test_disable_enable_agent(self, registry):
        """Test disabling and enabling agents."""
        registry.register("test_agent", TestAgent)
        
        # Disable agent
        registry.disable("test_agent")
        metadata = registry.get_metadata("test_agent")
        assert metadata.status == AgentStatus.DISABLED
        
        # Enable agent
        registry.enable("test_agent")
        metadata = registry.get_metadata("test_agent")
        assert metadata.status == AgentStatus.REGISTERED
    
    def test_observer_pattern(self, registry):
        """Test observer notifications."""
        events = []
        
        def observer(event, agent_id, metadata):
            events.append((event, agent_id))
        
        registry.add_observer(observer)
        
        # Register agent
        registry.register("test_agent", TestAgent)
        assert ("register", "test_agent") in events
        
        # Initialize agent
        registry.get("test_agent")
        assert ("initialize", "test_agent") in events
        
        # Disable agent
        registry.disable("test_agent")
        assert ("disable", "test_agent") in events
        
        # Remove observer
        registry.remove_observer(observer)
        registry.enable("test_agent")
        # Should not receive enable event
        assert ("enable", "test_agent") not in events
    
    def test_thread_safety(self, registry):
        """Test thread-safe operations."""
        errors = []
        
        def register_agents():
            try:
                for i in range(100):
                    registry.register(
                        f"agent_{threading.current_thread().name}_{i}",
                        TestAgent,
                        replace=True
                    )
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for i in range(5):
            t = threading.Thread(target=register_agents, name=f"thread_{i}")
            threads.append(t)
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join()
        
        # Check no errors occurred
        assert len(errors) == 0
        
        # Verify all agents registered
        agents = registry.list_agents()
        assert len(agents) == 500  # 5 threads * 100 agents each
    
    def test_global_functions(self, registry):
        """Test global convenience functions."""
        # Clear global registry
        from core.agent_registry import registry as global_registry
        global_registry.clear()
        
        # Test registration
        register_agent("global_test", TestAgent, version="1.5.0")
        
        # Test retrieval
        agent = get_agent("global_test")
        assert isinstance(agent, TestAgent)
        
        # Test discovery
        register_agent("global_test2", TestAgent, tags=["global"])
        agents = discover_agents(tags=["global"])
        assert "global_test2" in agents
    
    def test_auto_registration(self):
        """Test BaseAgentV2 auto-registration."""
        # Clear global registry
        from core.agent_registry import registry as global_registry
        global_registry.clear()
        
        # Enable auto-registration
        TestAgentV2.enable_auto_registration()
        
        # Create agent (should auto-register)
        agent = TestAgentV2()
        
        # Verify registration
        metadata = global_registry.get_metadata(agent.agent_id)
        assert metadata is not None
        assert metadata.agent_class == TestAgentV2
        
        # Disable for cleanup
        TestAgentV2.disable_auto_registration()