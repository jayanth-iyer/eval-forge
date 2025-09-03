import httpx
import time
import json
import ssl
import socket
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models, schemas

class SyntheticMonitoringService:
    
    async def execute_api_test(self, test: models.SyntheticTest) -> Dict:
        """Execute API/HTTP test with authentication and enhanced validation"""
        start_time = time.time()
        
        try:
            headers = json.loads(test.headers) if test.headers else {}
            body = json.loads(test.body) if test.body else None
            
            # Add authentication headers
            if test.auth_type == "api_key" and test.auth_credentials:
                auth_data = json.loads(test.auth_credentials)
                headers[auth_data.get("header_name", "X-API-Key")] = auth_data.get("key")
            elif test.auth_type == "bearer_token" and test.auth_credentials:
                auth_data = json.loads(test.auth_credentials)
                headers["Authorization"] = f"Bearer {auth_data.get('token')}"
            
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
    
    def execute_browser_test(self, test: models.SyntheticTest) -> Dict:
        """Execute browser automation test - Placeholder for now"""
        # Browser automation will be implemented with Playwright in future phase
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
        """Execute uptime test with SSL certificate checking"""
        start_time = time.time()
        
        try:
            # SSL certificate check if enabled
            ssl_info = None
            if test.ssl_check_enabled and test.url.startswith('https://'):
                ssl_info = self._check_ssl_certificate(test.url)
            
            async with httpx.AsyncClient(timeout=test.timeout) as client:
                response = await client.get(test.url)
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                
                # For uptime tests, we just check if we get any 2xx response
                success = 200 <= response.status_code < 300
                
                # Check SSL certificate expiry if enabled
                if ssl_info and ssl_info.get("days_until_expiry", 365) < 30:
                    success = False
                
                error_msg = None
                if not success:
                    if ssl_info and ssl_info.get("days_until_expiry", 365) < 30:
                        error_msg = f"SSL certificate expires in {ssl_info['days_until_expiry']} days"
                    else:
                        error_msg = f"HTTP {response.status_code}"
                
                return {
                    "status": "success" if success else "failure",
                    "response_time": response_time,
                    "status_code": response.status_code,
                    "response_body": f"HTTP {response.status_code}",
                    "error_message": error_msg,
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
    
    def _check_ssl_certificate(self, url: str) -> Dict:
        """Check SSL certificate expiry for HTTPS URLs"""
        try:
            from urllib.parse import urlparse
            parsed_url = urlparse(url)
            hostname = parsed_url.hostname
            port = parsed_url.port or 443
            
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
            # Parse expiry date
            expiry_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
            days_until_expiry = (expiry_date - datetime.now()).days
            
            return {
                "days_until_expiry": days_until_expiry,
                "expiry_date": expiry_date.isoformat(),
                "issuer": cert.get('issuer', [{}])[0].get('organizationName', 'Unknown')
            }
        except Exception as e:
            return {
                "days_until_expiry": 0,
                "error": str(e)
            }
    
    def get_monitoring_metrics(self, db: Session, test_type: str = None) -> Dict:
        """Calculate real metrics for monitoring types"""
        try:
            # Base query for executions
            query = db.query(models.SyntheticExecution).join(models.SyntheticTest)
            
            if test_type:
                query = query.filter(models.SyntheticTest.test_type == test_type)
            
            # Get executions from last 24 hours
            since = datetime.now() - timedelta(hours=24)
            recent_executions = query.filter(models.SyntheticExecution.executed_at >= since).all()
            
            if not recent_executions:
                return {
                    "success_rate": 0.0,
                    "avg_response_time": 0.0,
                    "total_tests": 0,
                    "successful_tests": 0
                }
            
            total_tests = len(recent_executions)
            successful_tests = len([e for e in recent_executions if e.status == "success"])
            success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0.0
            
            # Calculate average response time for successful tests only
            successful_response_times = [e.response_time for e in recent_executions if e.status == "success" and e.response_time]
            avg_response_time = sum(successful_response_times) / len(successful_response_times) if successful_response_times else 0.0
            
            return {
                "success_rate": round(success_rate, 1),
                "avg_response_time": round(avg_response_time, 0),
                "total_tests": total_tests,
                "successful_tests": successful_tests
            }
        except Exception:
            # Return default values on error
            return {
                "success_rate": 0.0,
                "avg_response_time": 0.0,
                "total_tests": 0,
                "successful_tests": 0
            }

# Global service instance
synthetic_service = SyntheticMonitoringService()
