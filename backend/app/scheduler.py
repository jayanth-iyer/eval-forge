import asyncio
import logging
from datetime import datetime, timedelta
from typing import List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import SyntheticTest
from .synthetic_monitoring import synthetic_service

logger = logging.getLogger(__name__)

class SyntheticTestScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.running = False
    
    async def start(self):
        """Start the scheduler and schedule all active tests"""
        if self.running:
            return
        
        self.scheduler.start()
        self.running = True
        
        # Schedule all active tests
        await self.schedule_all_active_tests()
        
        # Schedule periodic rescheduling (every 5 minutes)
        self.scheduler.add_job(
            self.reschedule_tests,
            IntervalTrigger(minutes=5),
            id="reschedule_tests",
            replace_existing=True
        )
        
        logger.info("Synthetic test scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        if not self.running:
            return
        
        self.scheduler.shutdown()
        self.running = False
        logger.info("Synthetic test scheduler stopped")
    
    async def schedule_all_active_tests(self):
        """Schedule all active synthetic tests"""
        db = SessionLocal()
        try:
            active_tests = db.query(SyntheticTest).filter(SyntheticTest.is_active == True).all()
            
            for test in active_tests:
                self.schedule_test(test)
                
            logger.info(f"Scheduled {len(active_tests)} active tests")
        except Exception as e:
            logger.error(f"Error scheduling tests: {e}")
        finally:
            db.close()
    
    def schedule_test(self, test: SyntheticTest):
        """Schedule a single test for periodic execution"""
        job_id = f"test_{test.id}"
        
        # Remove existing job if it exists
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
        
        # Only schedule if test is active and has valid interval
        if not test.is_active or test.interval <= 0:
            return
        
        # Add new job
        self.scheduler.add_job(
            self.execute_scheduled_test,
            IntervalTrigger(seconds=test.interval),
            args=[test.id],
            id=job_id,
            replace_existing=True,
            next_run_time=datetime.now() + timedelta(seconds=10)  # Start in 10 seconds
        )
        
        logger.info(f"Scheduled test '{test.name}' (ID: {test.id}) to run every {test.interval} seconds")
    
    def unschedule_test(self, test_id: int):
        """Remove a test from the schedule"""
        job_id = f"test_{test_id}"
        
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
            logger.info(f"Unscheduled test ID: {test_id}")
    
    async def execute_scheduled_test(self, test_id: int):
        """Execute a scheduled test"""
        db = SessionLocal()
        try:
            test = db.query(SyntheticTest).filter(SyntheticTest.id == test_id).first()
            
            if not test:
                logger.warning(f"Test ID {test_id} not found, removing from schedule")
                await self.unschedule_test(test_id)
                return
            
            if not test.is_active:
                logger.info(f"Test '{test.name}' is inactive, removing from schedule")
                await self.unschedule_test(test_id)
                return
            
            # Execute the test
            logger.info(f"Executing scheduled test: {test.name}")
            execution = await synthetic_service.execute_test(test, db)
            logger.info(f"Test '{test.name}' completed with status: {execution.status}")
            
        except Exception as e:
            logger.error(f"Error executing scheduled test {test_id}: {e}")
        finally:
            db.close()
    
    async def reschedule_tests(self):
        """Periodically check for new/updated tests and reschedule as needed"""
        try:
            db = SessionLocal()
            active_tests = db.query(SyntheticTest).filter(SyntheticTest.is_active == True).all()
            
            # Get currently scheduled job IDs
            scheduled_job_ids = {job.id for job in self.scheduler.get_jobs() if job.id.startswith("test_")}
            active_test_ids = {f"test_{test.id}" for test in active_tests}
            
            # Remove jobs for tests that are no longer active
            for job_id in scheduled_job_ids - active_test_ids:
                if job_id != "reschedule_tests":  # Don't remove the reschedule job
                    self.scheduler.remove_job(job_id)
                    logger.info(f"Removed job for inactive test: {job_id}")
            
            # Add/update jobs for active tests
            for test in active_tests:
                job_id = f"test_{test.id}"
                existing_job = self.scheduler.get_job(job_id)
                
                if not existing_job:
                    # New test, schedule it
                    await self.schedule_test(test)
                else:
                    # Check if interval has changed
                    current_interval = existing_job.trigger.interval.total_seconds()
                    if current_interval != test.interval:
                        # Reschedule with new interval
                        self.schedule_test(test)
                        logger.info(f"Rescheduled test '{test.name}' with new interval: {test.interval}s")
            
            db.close()
            
        except Exception as e:
            logger.error(f"Error in reschedule_tests: {e}")

# Global scheduler instance
scheduler = SyntheticTestScheduler()
