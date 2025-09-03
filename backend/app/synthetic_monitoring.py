import httpx
import time
import json
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from . import models, schemas

class SyntheticMonitoringService:
    
    async def execute_api_test(self, test: models.SyntheticTest) -> Dict:
        """Execute API/HTTP test"""
        start_time = time.time()
        
        try:
            headers = json.loads(test.headers) if test.headers else {}
            body = json.loads(test.body) if test.body else None
            
            async with httpx.AsyncClient(timeout=test.timeout) as client:
                response = await client.request(
                    method=test.method,
                    url=test.url,
                    headers=headers,
                    json=body if body else None
                )
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                
                # Check if response meets expectations
                status_ok = response.status_code == test.expected_status
                content_ok = True
                
                if test.expected_response_contains:
                    content_ok = test.expected_response_contains in response.text
                
                success = status_ok and content_ok
                
                return {
                    "status": "success" if success else "failure",
                    "response_time": response_time,
                    "status_code": response.status_code,
                    "response_body": response.text[:1000],  # Limit response body size
                    "error_message": None if success else f"Status: {response.status_code}, Content check: {content_ok}",
                    "dns_time": None,  # Could be enhanced with detailed timing
                    "connect_time": None,
                    "ssl_time": None,
                    "first_byte_time": None
                }
                
        except httpx.TimeoutException:
            return {
                "status": "timeout",
                "response_time": test.timeout * 1000,
                "status_code": None,
                "response_body": None,
                "error_message": f"Request timeout after {test.timeout} seconds",
                "dns_time": None,
                "connect_time": None,
                "ssl_time": None,
                "first_byte_time": None
            }
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            return {
                "status": "error",
                "response_time": response_time,
                "status_code": None,
                "response_body": None,
                "error_message": str(e),
                "dns_time": None,
                "connect_time": None,
                "ssl_time": None,
                "first_byte_time": None
            }
    
    async def execute_browser_test(self, test: models.SyntheticTest) -> Dict:
        """Execute browser automation test - Placeholder for now"""
        # TODO: Implement browser automation when Playwright is available
        return {
            "status": "error",
            "response_time": 0,
            "status_code": None,
            "response_body": None,
            "error_message": "Browser automation not available - Playwright not installed",
            "dns_time": None,
            "connect_time": None,
            "ssl_time": None,
            "first_byte_time": None
        }
    
    async def execute_uptime_test(self, test: models.SyntheticTest) -> Dict:
        """Execute simple uptime/availability test"""
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=test.timeout) as client:
                response = await client.get(test.url)
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                
                # For uptime tests, we just check if we get any 2xx response
                success = 200 <= response.status_code < 300
                
                return {
                    "status": "success" if success else "failure",
                    "response_time": response_time,
                    "status_code": response.status_code,
                    "response_body": f"HTTP {response.status_code}",
                    "error_message": None if success else f"HTTP {response.status_code}",
                    "dns_time": None,
                    "connect_time": None,
                    "ssl_time": None,
                    "first_byte_time": None
                }
                
        except httpx.TimeoutException:
            return {
                "status": "timeout",
                "response_time": test.timeout * 1000,
                "status_code": None,
                "response_body": None,
                "error_message": f"Request timeout after {test.timeout} seconds",
                "dns_time": None,
                "connect_time": None,
                "ssl_time": None,
                "first_byte_time": None
            }
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            return {
                "status": "error",
                "response_time": response_time,
                "status_code": None,
                "response_body": None,
                "error_message": str(e),
                "dns_time": None,
                "connect_time": None,
                "ssl_time": None,
                "first_byte_time": None
            }
    
    async def execute_test(self, test: models.SyntheticTest, db: Session) -> models.SyntheticExecution:
        """Execute a synthetic test and save results"""
        
        # Execute the appropriate test type
        if test.test_type == "api":
            result = await self.execute_api_test(test)
        elif test.test_type == "browser":
            result = await self.execute_browser_test(test)
        elif test.test_type == "uptime":
            result = await self.execute_uptime_test(test)
        else:
            result = {
                "status": "error",
                "response_time": 0,
                "status_code": None,
                "response_body": None,
                "error_message": f"Unknown test type: {test.test_type}",
                "dns_time": None,
                "connect_time": None,
                "ssl_time": None,
                "first_byte_time": None
            }
        
        # Save execution result to database
        execution = models.SyntheticExecution(
            test_id=test.id,
            status=result["status"],
            response_time=result["response_time"],
            status_code=result["status_code"],
            response_body=result["response_body"],
            error_message=result["error_message"],
            dns_time=result["dns_time"],
            connect_time=result["connect_time"],
            ssl_time=result["ssl_time"],
            first_byte_time=result["first_byte_time"],
            executed_at=datetime.now()
        )
        
        db.add(execution)
        db.commit()
        db.refresh(execution)
        
        return execution

# Global service instance
synthetic_service = SyntheticMonitoringService()
