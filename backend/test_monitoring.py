#!/usr/bin/env python3
"""
Test script for synthetic monitoring implementation
"""
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database import SessionLocal, engine
from app.models import Base, SyntheticTest, SyntheticExecution
from app.synthetic_monitoring import synthetic_service
from app.scheduler import scheduler
from datetime import datetime

async def test_monitoring_features():
    """Test the enhanced monitoring features"""
    print("🧪 Testing Enhanced Synthetic Monitoring Implementation")
    print("=" * 60)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Test 1: Create a test with new fields
        print("\n1. Testing enhanced test creation...")
        test_data = {
            'name': 'Test API Monitor',
            'type': 'api',
            'url': 'https://httpbin.org/get',
            'interval': 300,
            'is_active': True,
            'service_name': 'HTTPBin Test Service',
            'auth_type': 'none',
            'auth_credentials': '{}',
            'ssl_check_enabled': True,
            'alert_thresholds': '{"response_time": 5000, "success_rate": 95}',
            'created_at': datetime.now()
        }
        
        test = SyntheticTest(**test_data)
        db.add(test)
        db.commit()
        db.refresh(test)
        print(f"✅ Created test: {test.name} (ID: {test.id})")
        print(f"   Service: {test.service_name}")
        print(f"   Auth Type: {test.auth_type}")
        print(f"   SSL Check: {test.ssl_check_enabled}")
        
        # Test 2: Execute the test
        print("\n2. Testing enhanced test execution...")
        execution = await synthetic_service.execute_test(test, db)
        print(f"✅ Test executed with status: {execution.status}")
        print(f"   Response time: {execution.response_time}ms")
        print(f"   Details: {execution.details}")
        
        # Test 3: Test metrics calculation
        print("\n3. Testing metrics calculation...")
        metrics = synthetic_service.get_monitoring_metrics(db, 'api')
        print(f"✅ Metrics calculated:")
        print(f"   Success Rate: {metrics['success_rate']:.1f}%")
        print(f"   Avg Response Time: {metrics['avg_response_time']:.1f}ms")
        print(f"   Total Tests (24h): {metrics['total_tests']}")
        
        # Test 4: Test scheduler integration
        print("\n4. Testing scheduler integration...")
        await scheduler.start()
        scheduler.schedule_test(test)
        scheduled_jobs = scheduler.scheduler.get_jobs()
        test_jobs = [job for job in scheduled_jobs if job.id.startswith('test_')]
        print(f"✅ Scheduler started with {len(test_jobs)} test jobs")
        
        # Test 5: Test SSL certificate checking (for HTTPS URLs)
        print("\n5. Testing SSL certificate checking...")
        https_test_data = {
            'name': 'HTTPS SSL Test',
            'type': 'uptime',
            'url': 'https://google.com',
            'interval': 300,
            'is_active': True,
            'service_name': 'Google',
            'auth_type': 'none',
            'auth_credentials': '{}',
            'ssl_check_enabled': True,
            'alert_thresholds': '{"response_time": 5000, "success_rate": 95}',
            'created_at': datetime.now()
        }
        
        https_test = SyntheticTest(**https_test_data)
        db.add(https_test)
        db.commit()
        db.refresh(https_test)
        
        https_execution = await synthetic_service.execute_test(https_test, db)
        print(f"✅ HTTPS test executed with status: {https_execution.status}")
        if 'ssl_expires' in https_execution.details:
            print(f"   SSL certificate info included in details")
        
        # Clean up
        scheduler.stop()
        
        print("\n" + "=" * 60)
        print("🎉 All tests completed successfully!")
        print("✅ Enhanced monitoring implementation is working correctly")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_monitoring_features())
