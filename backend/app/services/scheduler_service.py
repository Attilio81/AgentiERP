"""
Scheduler service for managing automated tasks.
"""
import logging
from typing import Optional, Callable
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.base import JobLookupError
import json

logger = logging.getLogger(__name__)


class SchedulerService:
    """
    Service for scheduling and managing automated tasks using APScheduler.
    Singleton pattern to ensure only one scheduler instance.
    """

    _instance: Optional["SchedulerService"] = None
    _scheduler: Optional[BackgroundScheduler] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the scheduler if not already initialized."""
        if self._scheduler is None:
            self._scheduler = BackgroundScheduler(
                timezone="Europe/Rome",
                job_defaults={
                    "coalesce": True,  # Combine multiple missed executions into one
                    "max_instances": 1,  # Only one instance of a job at a time
                    "misfire_grace_time": 3600,  # 1 hour grace period for missed jobs
                },
            )
            logger.info("SchedulerService initialized")

    def start(self):
        """Start the scheduler."""
        if self._scheduler and not self._scheduler.running:
            self._scheduler.start()
            logger.info("Scheduler started")

    def shutdown(self):
        """Shutdown the scheduler."""
        if self._scheduler and self._scheduler.running:
            self._scheduler.shutdown(wait=False)
            logger.info("Scheduler shut down")

    def add_task(
        self,
        task_id: str,
        cron_expression: str,
        callback: Callable,
        task_name: str = "",
        **callback_kwargs,
    ) -> bool:
        """
        Add a scheduled task.

        Args:
            task_id: Unique identifier for the task (use database ID)
            cron_expression: Cron expression for scheduling
            callback: Function to call when task is triggered
            task_name: Human-readable task name (for logging)
            **callback_kwargs: Additional keyword arguments for the callback

        Returns:
            True if task was added successfully, False otherwise
        """
        try:
            # Parse cron expression
            trigger = self._parse_cron_expression(cron_expression)

            # Remove existing job if present
            self.remove_task(task_id)

            # Add new job
            job_id = f"scheduled_task_{task_id}"
            self._scheduler.add_job(
                func=callback,
                trigger=trigger,
                id=job_id,
                name=task_name or f"Task {task_id}",
                kwargs=callback_kwargs,
                replace_existing=True,
            )

            logger.info(
                f"Added scheduled task '{task_name}' (ID: {task_id}) with cron: {cron_expression}"
            )
            return True

        except Exception as e:
            logger.error(
                f"Failed to add scheduled task '{task_name}' (ID: {task_id}): {str(e)}"
            )
            return False

    def remove_task(self, task_id: str) -> bool:
        """
        Remove a scheduled task.

        Args:
            task_id: Task ID to remove

        Returns:
            True if task was removed, False if not found
        """
        try:
            job_id = f"scheduled_task_{task_id}"
            self._scheduler.remove_job(job_id)
            logger.info(f"Removed scheduled task ID: {task_id}")
            return True
        except JobLookupError:
            logger.warning(f"Task ID {task_id} not found in scheduler")
            return False
        except Exception as e:
            logger.error(f"Failed to remove task ID {task_id}: {str(e)}")
            return False

    def get_next_run_time(self, task_id: str) -> Optional[datetime]:
        """
        Get the next scheduled run time for a task.

        Args:
            task_id: Task ID

        Returns:
            Next run time as datetime, or None if not found
        """
        try:
            job_id = f"scheduled_task_{task_id}"
            job = self._scheduler.get_job(job_id)
            if job:
                return job.next_run_time
            return None
        except Exception as e:
            logger.error(f"Failed to get next run time for task {task_id}: {str(e)}")
            return None

    def _parse_cron_expression(self, cron_expression: str) -> CronTrigger:
        """
        Parse a cron expression into an APScheduler CronTrigger.

        Supports both standard cron format and preset shortcuts:
        - "@daily" or "@midnight" -> 0 0 * * *
        - "@weekly" -> 0 0 * * 0
        - "@monthly" -> 0 0 1 * *
        - "#1" in day_of_week for "first Monday" etc.

        Args:
            cron_expression: Cron expression string

        Returns:
            CronTrigger object

        Raises:
            ValueError: If cron expression is invalid
        """
        # Handle preset shortcuts
        presets = {
            "@daily": "0 0 * * *",
            "@midnight": "0 0 * * *",
            "@weekly": "0 0 * * 0",
            "@monthly": "0 0 1 * *",
        }

        if cron_expression in presets:
            cron_expression = presets[cron_expression]

        # Parse standard cron format: minute hour day month day_of_week
        parts = cron_expression.strip().split()

        if len(parts) != 5:
            raise ValueError(
                f"Invalid cron expression '{cron_expression}'. "
                "Expected format: 'minute hour day month day_of_week'"
            )

        minute, hour, day, month, day_of_week = parts

        # Handle nth weekday (e.g., "1#1" for first Monday)
        # APScheduler format: day_of_week='mon-fri', week='1-5'
        week = None
        if "#" in day_of_week:
            dow, week_num = day_of_week.split("#")
            day_of_week = dow
            week = week_num

        return CronTrigger(
            minute=minute,
            hour=hour,
            day=day,
            month=month,
            day_of_week=day_of_week,
            week=week,
            timezone="Europe/Rome",
        )

    def list_jobs(self):
        """List all scheduled jobs (for debugging)."""
        if self._scheduler:
            return self._scheduler.get_jobs()
        return []


# Global singleton instance
_scheduler_service = None


def get_scheduler_service() -> SchedulerService:
    """Get the global scheduler service instance."""
    global _scheduler_service
    if _scheduler_service is None:
        _scheduler_service = SchedulerService()
    return _scheduler_service
