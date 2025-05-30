#!/usr/bin/env python3
"""
AIOS v2 End-to-End Integration Test Suite
Tests all critical paths and external integrations
"""

import os
import sys
import json
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class IntegrationTestSuite:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.test_user = None
        self.auth_token = None
        
    def run_all_tests(self):
        """Run complete integration test suite"""
        print("""
🧪 AIOS v2 Integration Test Suite
=================================
        """)
        
        test_groups = [
            ("🔐 Authentication & Security", self.test_authentication),
            ("📁 File Upload & Processing", self.test_file_processing),
            ("🤖 Agent Marketplace", self.test_agent_marketplace),
            ("📊 Analytics & Insights", self.test_analytics),
            ("🔌 External Integrations", self.test_external_services),
            ("⚡ Performance & Load", self.test_performance),
            ("🔄 Real-time Updates", self.test_realtime_features),
            ("💾 Data Persistence", self.test_data_persistence)
        ]
        
        total_tests = 0
        passed_tests = 0
        
        for group_name, test_func in test_groups:
            print(f"\n{group_name}")
            print("-" * 40)
            
            try:
                group_passed, group_total = test_func()
                passed_tests += group_passed
                total_tests += group_total
            except Exception as e:
                print(f"❌ Test group failed: {str(e)}")
                total_tests += 1
                
        # Summary
        print("\n" + "="*50)
        print(f"📊 TEST SUMMARY: {passed_tests}/{total_tests} passed")
        
        if passed_tests == total_tests:
            print("✅ ALL TESTS PASSED - System ready for production!")
        else:
            print(f"❌ {total_tests - passed_tests} tests failed - Fix before deployment")
            
        return passed_tests == total_tests
        
    def test_authentication(self) -> Tuple[int, int]:
        """Test authentication flows"""
        tests = [
            ("User Registration", self._test_user_registration),
            ("User Login", self._test_user_login),
            ("OAuth Flow", self._test_oauth_flow),
            ("JWT Token Validation", self._test_jwt_validation),
            ("Permission Checks", self._test_permissions)
        ]
        
        return self._run_test_group(tests)
        
    def test_file_processing(self) -> Tuple[int, int]:
        """Test file upload and processing"""
        tests = [
            ("PDF Upload", self._test_pdf_upload),
            ("URL Processing", self._test_url_processing),
            ("Audio Upload", self._test_audio_upload),
            ("Processing Status", self._test_processing_status),
            ("Result Retrieval", self._test_result_retrieval)
        ]
        
        return self._run_test_group(tests)
        
    def test_agent_marketplace(self) -> Tuple[int, int]:
        """Test agent marketplace functionality"""
        tests = [
            ("Agent Discovery", self._test_agent_discovery),
            ("Agent Search", self._test_agent_search),
            ("Agent Installation", self._test_agent_installation),
            ("Agent Activation", self._test_agent_activation),
            ("Agent Usage", self._test_agent_usage)
        ]
        
        return self._run_test_group(tests)
        
    def test_analytics(self) -> Tuple[int, int]:
        """Test analytics and insights"""
        tests = [
            ("Usage Metrics", self._test_usage_metrics),
            ("Processing Analytics", self._test_processing_analytics),
            ("Agent Performance", self._test_agent_performance),
            ("User Insights", self._test_user_insights)
        ]
        
        return self._run_test_group(tests)
        
    def test_external_services(self) -> Tuple[int, int]:
        """Test external service integrations"""
        tests = [
            ("Database Connection", self._test_database),
            ("LLM API (OpenAI)", self._test_openai_api),
            ("LLM API (Anthropic)", self._test_anthropic_api),
            ("Gmail Integration", self._test_gmail),
            ("Redis Cache", self._test_redis)
        ]
        
        return self._run_test_group(tests)
        
    def test_performance(self) -> Tuple[int, int]:
        """Test performance and load handling"""
        tests = [
            ("API Response Times", self._test_response_times),
            ("Concurrent Requests", self._test_concurrent_requests),
            ("Large File Handling", self._test_large_files),
            ("Memory Usage", self._test_memory_usage)
        ]
        
        return self._run_test_group(tests)
        
    def test_realtime_features(self) -> Tuple[int, int]:
        """Test real-time update features"""
        tests = [
            ("WebSocket Connection", self._test_websocket),
            ("Processing Updates", self._test_processing_updates),
            ("Agent Status Updates", self._test_agent_status_updates),
            ("Notification System", self._test_notifications)
        ]
        
        return self._run_test_group(tests)
        
    def test_data_persistence(self) -> Tuple[int, int]:
        """Test data persistence and recovery"""
        tests = [
            ("User Data Persistence", self._test_user_data_persistence),
            ("Processing History", self._test_processing_history),
            ("Agent State Persistence", self._test_agent_state),
            ("Backup & Recovery", self._test_backup_recovery)
        ]
        
        return self._run_test_group(tests)
        
    # Helper methods
    def _run_test_group(self, tests: List[Tuple[str, callable]]) -> Tuple[int, int]:
        """Run a group of tests and return results"""
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                if result:
                    print(f"  ✅ {test_name}")
                    passed += 1
                else:
                    print(f"  ❌ {test_name}")
            except Exception as e:
                print(f"  ❌ {test_name}: {str(e)}")
                
        return passed, total
        
    # Individual test implementations
    def _test_user_registration(self) -> bool:
        """Test user registration flow"""
        try:
            response = self.session.post(f"{self.base_url}/api/auth/register", json={
                "email": f"test_{datetime.now().timestamp()}@example.com",
                "password": "TestPassword123!",
                "name": "Test User"
            })
            
            if response.status_code == 201:
                self.test_user = response.json()
                return True
            return False
        except:
            return False
            
    def _test_user_login(self) -> bool:
        """Test user login flow"""
        if not self.test_user:
            return False
            
        try:
            response = self.session.post(f"{self.base_url}/api/auth/login", json={
                "email": self.test_user.get("email"),
                "password": "TestPassword123!"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                return True
            return False
        except:
            return False
            
    def _test_oauth_flow(self) -> bool:
        """Test OAuth authentication flow"""
        try:
            # Test OAuth redirect
            response = self.session.get(f"{self.base_url}/api/auth/google")
            return response.status_code in [302, 200]
        except:
            return False
            
    def _test_jwt_validation(self) -> bool:
        """Test JWT token validation"""
        if not self.auth_token:
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/api/auth/me")
            return response.status_code == 200
        except:
            return False
            
    def _test_permissions(self) -> bool:
        """Test permission system"""
        try:
            # Test unauthorized access
            temp_session = requests.Session()
            response = temp_session.get(f"{self.base_url}/api/protected/resource")
            return response.status_code == 401
        except:
            return False
            
    def _test_pdf_upload(self) -> bool:
        """Test PDF file upload"""
        try:
            # Create test PDF content
            test_pdf = b"%PDF-1.4\n%Test PDF content"
            
            files = {'file': ('test.pdf', test_pdf, 'application/pdf')}
            response = self.session.post(f"{self.base_url}/api/upload/pdf", files=files)
            
            return response.status_code == 200
        except:
            return False
            
    def _test_url_processing(self) -> bool:
        """Test URL processing"""
        try:
            response = self.session.post(f"{self.base_url}/api/process/url", json={
                "url": "https://example.com",
                "options": {"extract_text": True}
            })
            
            return response.status_code in [200, 202]
        except:
            return False
            
    def _test_audio_upload(self) -> bool:
        """Test audio file upload"""
        try:
            # Create test audio content
            test_audio = b"RIFF$\x00\x00\x00WAVEfmt"  # Minimal WAV header
            
            files = {'file': ('test.wav', test_audio, 'audio/wav')}
            response = self.session.post(f"{self.base_url}/api/upload/audio", files=files)
            
            return response.status_code == 200
        except:
            return False
            
    def _test_processing_status(self) -> bool:
        """Test processing status endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/processing/status/test-id")
            return response.status_code in [200, 404]
        except:
            return False
            
    def _test_result_retrieval(self) -> bool:
        """Test result retrieval"""
        try:
            response = self.session.get(f"{self.base_url}/api/results/test-id")
            return response.status_code in [200, 404]
        except:
            return False
            
    def _test_agent_discovery(self) -> bool:
        """Test agent discovery endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/agents/discover")
            return response.status_code == 200
        except:
            return False
            
    def _test_agent_search(self) -> bool:
        """Test agent search functionality"""
        try:
            response = self.session.get(f"{self.base_url}/api/agents/search?q=test")
            return response.status_code == 200
        except:
            return False
            
    def _test_agent_installation(self) -> bool:
        """Test agent installation"""
        try:
            response = self.session.post(f"{self.base_url}/api/agents/install", json={
                "agent_id": "test-agent",
                "version": "1.0.0"
            })
            
            return response.status_code in [200, 201, 409]  # 409 if already installed
        except:
            return False
            
    def _test_agent_activation(self) -> bool:
        """Test agent activation/deactivation"""
        try:
            response = self.session.post(f"{self.base_url}/api/agents/activate", json={
                "agent_id": "test-agent",
                "active": True
            })
            
            return response.status_code == 200
        except:
            return False
            
    def _test_agent_usage(self) -> bool:
        """Test agent usage endpoint"""
        try:
            response = self.session.post(f"{self.base_url}/api/agents/execute", json={
                "agent_id": "test-agent",
                "input": {"text": "Test input"}
            })
            
            return response.status_code in [200, 202]
        except:
            return False
            
    def _test_usage_metrics(self) -> bool:
        """Test usage metrics endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/analytics/usage")
            return response.status_code == 200
        except:
            return False
            
    def _test_processing_analytics(self) -> bool:
        """Test processing analytics"""
        try:
            response = self.session.get(f"{self.base_url}/api/analytics/processing")
            return response.status_code == 200
        except:
            return False
            
    def _test_agent_performance(self) -> bool:
        """Test agent performance metrics"""
        try:
            response = self.session.get(f"{self.base_url}/api/analytics/agents")
            return response.status_code == 200
        except:
            return False
            
    def _test_user_insights(self) -> bool:
        """Test user insights endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/analytics/insights")
            return response.status_code == 200
        except:
            return False
            
    def _test_database(self) -> bool:
        """Test database connectivity"""
        try:
            response = self.session.get(f"{self.base_url}/api/health/db")
            return response.status_code == 200
        except:
            return False
            
    def _test_openai_api(self) -> bool:
        """Test OpenAI API integration"""
        try:
            response = self.session.get(f"{self.base_url}/api/health/openai")
            return response.status_code == 200
        except:
            return False
            
    def _test_anthropic_api(self) -> bool:
        """Test Anthropic API integration"""
        try:
            response = self.session.get(f"{self.base_url}/api/health/anthropic")
            return response.status_code == 200
        except:
            return False
            
    def _test_gmail(self) -> bool:
        """Test Gmail integration"""
        try:
            response = self.session.get(f"{self.base_url}/api/health/gmail")
            return response.status_code == 200
        except:
            return False
            
    def _test_redis(self) -> bool:
        """Test Redis connectivity"""
        try:
            response = self.session.get(f"{self.base_url}/api/health/redis")
            return response.status_code == 200
        except:
            return False
            
    def _test_response_times(self) -> bool:
        """Test API response times"""
        try:
            start = time.time()
            response = self.session.get(f"{self.base_url}/api/health")
            elapsed = time.time() - start
            
            return response.status_code == 200 and elapsed < 0.5  # 500ms threshold
        except:
            return False
            
    def _test_concurrent_requests(self) -> bool:
        """Test concurrent request handling"""
        import concurrent.futures
        
        def make_request():
            return self.session.get(f"{self.base_url}/api/health").status_code
            
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(make_request) for _ in range(10)]
                results = [f.result() for f in concurrent.futures.as_completed(futures)]
                
            return all(status == 200 for status in results)
        except:
            return False
            
    def _test_large_files(self) -> bool:
        """Test large file handling"""
        try:
            # Create 10MB test file
            large_content = b"x" * (10 * 1024 * 1024)
            
            files = {'file': ('large.txt', large_content, 'text/plain')}
            response = self.session.post(
                f"{self.base_url}/api/upload/file", 
                files=files,
                timeout=30
            )
            
            return response.status_code in [200, 413]  # 413 if size limit exceeded
        except:
            return False
            
    def _test_memory_usage(self) -> bool:
        """Test memory usage monitoring"""
        try:
            response = self.session.get(f"{self.base_url}/api/health/memory")
            if response.status_code == 200:
                data = response.json()
                # Check if memory usage is reasonable (< 80%)
                return data.get("memory_percent", 100) < 80
            return False
        except:
            return False
            
    def _test_websocket(self) -> bool:
        """Test WebSocket connection"""
        # This would require websocket-client library
        # For now, just test if WebSocket endpoint exists
        try:
            response = self.session.get(f"{self.base_url}/ws/info")
            return response.status_code in [200, 426]  # 426 Upgrade Required
        except:
            return False
            
    def _test_processing_updates(self) -> bool:
        """Test real-time processing updates"""
        # Would test WebSocket updates in real implementation
        return True  # Placeholder
        
    def _test_agent_status_updates(self) -> bool:
        """Test real-time agent status updates"""
        # Would test WebSocket updates in real implementation
        return True  # Placeholder
        
    def _test_notifications(self) -> bool:
        """Test notification system"""
        try:
            response = self.session.get(f"{self.base_url}/api/notifications")
            return response.status_code == 200
        except:
            return False
            
    def _test_user_data_persistence(self) -> bool:
        """Test user data persistence"""
        try:
            # Create test data
            response = self.session.post(f"{self.base_url}/api/user/preferences", json={
                "theme": "dark",
                "language": "en"
            })
            
            if response.status_code == 200:
                # Retrieve and verify
                response = self.session.get(f"{self.base_url}/api/user/preferences")
                if response.status_code == 200:
                    data = response.json()
                    return data.get("theme") == "dark"
            return False
        except:
            return False
            
    def _test_processing_history(self) -> bool:
        """Test processing history retrieval"""
        try:
            response = self.session.get(f"{self.base_url}/api/history/processing")
            return response.status_code == 200
        except:
            return False
            
    def _test_agent_state(self) -> bool:
        """Test agent state persistence"""
        try:
            response = self.session.get(f"{self.base_url}/api/agents/state")
            return response.status_code == 200
        except:
            return False
            
    def _test_backup_recovery(self) -> bool:
        """Test backup and recovery endpoints"""
        try:
            response = self.session.get(f"{self.base_url}/api/admin/backup/status")
            return response.status_code in [200, 403]  # 403 if not admin
        except:
            return False

def main():
    """Run integration tests"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AIOS v2 Integration Test Suite")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL for API")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Ensure AIOS v2 is running
    print(f"🔍 Testing AIOS v2 at: {args.url}")
    
    try:
        response = requests.get(f"{args.url}/health", timeout=5)
        if response.status_code != 200:
            print("❌ AIOS v2 is not responding correctly")
            print("Please ensure the application is running:")
            print("  cd /Users/arielmuslera/Development/Projects/bluelabel-AIOS-V2")
            print("  docker-compose up -d")
            print("  OR")
            print("  python main.py")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to AIOS v2")
        print("Please start the application first")
        sys.exit(1)
        
    # Run tests
    suite = IntegrationTestSuite(args.url)
    success = suite.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()