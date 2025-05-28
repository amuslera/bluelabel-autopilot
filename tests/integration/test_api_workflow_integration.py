"""
Integration tests for API workflow execution.

Tests the full stack: API -> UnifiedWorkflowEngine -> Agents -> Results
"""

import pytest
import asyncio
import json
from pathlib import Path
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocketDisconnect
import tempfile
import yaml
from datetime import datetime
from unittest.mock import patch

from apps.api.main import app, active_runs, ws_manager
from core.agent_registry import registry
from agents.ingestion_agent import IngestionAgent
from agents.digest_agent import DigestAgent


class TestAPIWorkflowIntegration:
    """Integration tests for the API."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup before each test."""
        # Clear active runs
        active_runs.clear()
        # Clear registry and re-register agents
        registry.clear()
        registry.register('ingestion_agent', IngestionAgent)
        registry.register('digest_agent', DigestAgent)
        
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def test_workflow(self):
        """Create a test workflow file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            workflow = {
                'workflow': {
                    'name': 'Test Integration Workflow',
                    'version': '1.0.0',
                    'description': 'Integration test workflow'
                },
                'steps': [
                    {
                        'id': 'ingest',
                        'name': 'Ingest Test Data',
                        'agent': 'ingestion_agent',
                        'input_file': 'test_input.json'
                    },
                    {
                        'id': 'digest',
                        'name': 'Create Digest',
                        'agent': 'digest_agent',
                        'input_from': 'ingest'
                    }
                ]
            }
            yaml.dump(workflow, f)
            temp_path = f.name
        
        # Create test input file
        test_input = {
            'task_id': 'test-integration',
            'source': 'test',
            'content': {
                'type': 'url',
                'url': 'https://example.com',
                'text': 'Test content for integration testing'
            }
        }
        input_path = Path(temp_path).parent / 'test_input.json'
        with open(input_path, 'w') as f:
            json.dump(test_input, f)
        
        yield temp_path
        
        # Cleanup
        Path(temp_path).unlink()
        input_path.unlink()
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["active_runs"] == 0
    
    def test_list_dag_runs_empty(self, client):
        """Test listing DAG runs when empty."""
        response = client.get("/api/dag-runs")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["limit"] == 20
        assert data["offset"] == 0
    
    def test_create_dag_run(self, client, test_workflow):
        """Test creating a new DAG run."""
        response = client.post("/api/dag-runs", json={
            "workflow_path": test_workflow,
            "persist": False,
            "engine_type": "sequential"
        })
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert data["status"] == "running"
        assert data["workflow_name"] == Path(test_workflow).name
        assert "started_at" in data
    
    def test_get_dag_run(self, client, test_workflow):
        """Test getting a specific DAG run."""
        # Create a run
        create_response = client.post("/api/dag-runs", json={
            "workflow_path": test_workflow,
            "persist": False
        })
        run_id = create_response.json()["id"]
        
        # Wait a bit for execution to start
        import time
        time.sleep(0.5)
        
        # Get the run
        response = client.get(f"/api/dag-runs/{run_id}")
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == run_id
        assert data["workflow_name"] == Path(test_workflow).name
        assert "status" in data
        assert "started_at" in data
    
    def test_get_nonexistent_dag_run(self, client):
        """Test getting a DAG run that doesn't exist."""
        response = client.get("/api/dag-runs/nonexistent-id")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_list_dag_runs_with_pagination(self, client, test_workflow):
        """Test pagination in DAG run listing."""
        # Create multiple runs
        run_ids = []
        for i in range(5):
            response = client.post("/api/dag-runs", json={
                "workflow_path": test_workflow,
                "persist": False
            })
            run_ids.append(response.json()["id"])
        
        # Test pagination
        response = client.get("/api/dag-runs?limit=2&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["limit"] == 2
        assert data["offset"] == 0
        
        # Test second page
        response = client.get("/api/dag-runs?limit=2&offset=2")
        data = response.json()
        assert len(data["items"]) == 2
        assert data["offset"] == 2
    
    def test_filter_dag_runs_by_status(self, client, test_workflow):
        """Test filtering DAG runs by status."""
        # Create a run
        client.post("/api/dag-runs", json={
            "workflow_path": test_workflow,
            "persist": False
        })
        
        # Filter by running status
        response = client.get("/api/dag-runs?status=running")
        assert response.status_code == 200
        data = response.json()
        # Should have at least one running
        assert len([r for r in data["items"] if r["status"] == "running"]) > 0
        
        # Filter by invalid status
        response = client.get("/api/dag-runs?status=invalid")
        assert response.status_code == 400
    
    def test_cancel_dag_run(self, client, test_workflow):
        """Test cancelling a DAG run."""
        # Create a run
        create_response = client.post("/api/dag-runs", json={
            "workflow_path": test_workflow,
            "persist": False
        })
        run_id = create_response.json()["id"]
        
        # Cancel it
        response = client.patch(f"/api/dag-runs/{run_id}/status", json={
            "status": "cancelled",
            "message": "Test cancellation"
        })
        assert response.status_code == 200
        assert response.json()["status"] == "cancelled"
    
    def test_websocket_connection(self, client):
        """Test WebSocket connection."""
        with client.websocket_connect("/ws") as websocket:
            data = websocket.receive_json()
            assert data["event"] == "connection.established"
            
            # Test ping/pong
            websocket.send_text("ping")
            response = websocket.receive_text()
            assert response == "pong"
    
    def test_websocket_dag_events(self, client, test_workflow):
        """Test WebSocket events during DAG execution."""
        events_received = []
        
        with client.websocket_connect("/ws") as websocket:
            # Receive connection message
            websocket.receive_json()
            
            # Create a DAG run in another thread
            def create_run():
                response = client.post("/api/dag-runs", json={
                    "workflow_path": test_workflow,
                    "persist": False
                })
                return response.json()["id"]
            
            import threading
            thread = threading.Thread(target=create_run)
            thread.start()
            
            # Collect events for a short time
            import time
            start_time = time.time()
            while time.time() - start_time < 2:
                try:
                    websocket.settimeout(0.1)
                    data = websocket.receive_json()
                    events_received.append(data)
                except:
                    pass
            
            thread.join()
        
        # Verify we received DAG events
        event_types = [e["event"] for e in events_received]
        assert "dag.run.created" in event_types
    
    def test_workflow_error_handling(self, client):
        """Test error handling for invalid workflow."""
        response = client.post("/api/dag-runs", json={
            "workflow_path": "/nonexistent/workflow.yaml",
            "persist": False
        })
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_concurrent_workflow_detection(self, client, test_workflow):
        """Test detection of concurrent workflow runs."""
        # Start first run
        response1 = client.post("/api/dag-runs", json={
            "workflow_path": test_workflow,
            "persist": False
        })
        assert response1.status_code == 200
        
        # Try to start second run without force
        response2 = client.post("/api/dag-runs", json={
            "workflow_path": test_workflow,
            "persist": False
        })
        assert response2.status_code == 409
        assert "already running" in response2.json()["detail"]
        
        # Start with force flag
        response3 = client.post("/api/dag-runs", json={
            "workflow_path": test_workflow,
            "persist": False,
            "force": True
        })
        assert response3.status_code == 200
    
    @pytest.mark.asyncio
    async def test_full_workflow_execution(self, client, test_workflow):
        """Test complete workflow execution through API."""
        # Create a run
        response = client.post("/api/dag-runs", json={
            "workflow_path": test_workflow,
            "persist": False,
            "engine_type": "sequential"
        })
        run_id = response.json()["id"]
        
        # Wait for completion (with timeout)
        max_wait = 5  # seconds
        start = datetime.utcnow()
        
        while (datetime.utcnow() - start).total_seconds() < max_wait:
            response = client.get(f"/api/dag-runs/{run_id}")
            data = response.json()
            
            if data["status"] in ["success", "failed"]:
                break
            
            await asyncio.sleep(0.1)
        
        # Verify completion
        final_response = client.get(f"/api/dag-runs/{run_id}")
        final_data = final_response.json()
        
        # Should have completed
        assert final_data["status"] in ["success", "failed"]
        assert final_data["completed_at"] is not None
        assert final_data["duration_ms"] > 0
        
        # Should have step information
        if "steps" in final_data and final_data["steps"]:
            assert len(final_data["steps"]) > 0
            # Verify step structure
            for step in final_data["steps"]:
                assert "id" in step
                assert "status" in step
                assert "duration_ms" in step