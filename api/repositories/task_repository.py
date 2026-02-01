from sqlmodel import Session, select
from typing import List, Optional
from models.task import Task, TaskCreate


class TaskRepository:
    def create_task(self, session: Session, task: TaskCreate, user_id: str) -> Task:
        """Create a new task linked to the authenticated user."""
        db_task = Task(
            description=task.description,
            completed=task.completed,
            category=task.category,
            priority=task.priority,
            user_id=user_id  # Link task to the authenticated user
        )
        session.add(db_task)
        session.commit()
        session.refresh(db_task)
        return db_task

    def get_task(self, session: Session, task_id: int, user_id: str) -> Optional[Task]:
        """Get a task by ID, but only if it belongs to the user."""
        task = session.get(Task, task_id)
        if task and task.user_id == user_id:
            return task
        return None  # Return None if task doesn't exist or doesn't belong to user

    def get_tasks(self, session: Session, user_id: str) -> List[Task]:
        """Get all tasks belonging to the authenticated user ONLY."""
        return list(session.exec(
            select(Task).where(Task.user_id == user_id)
        ).all())

    def update_task(self, session: Session, task_id: int, user_id: str, task_data: dict) -> Optional[Task]:
        """Update a task, but only if it belongs to the user."""
        db_task = self.get_task(session, task_id, user_id)
        if db_task:
            for key, value in task_data.items():
                setattr(db_task, key, value)
            session.add(db_task)
            session.commit()
            session.refresh(db_task)
        return db_task

    def delete_task(self, session: Session, task_id: int, user_id: str) -> bool:
        """Delete a task, but only if it belongs to the user."""
        db_task = self.get_task(session, task_id, user_id)
        if db_task:
            session.delete(db_task)
            session.commit()
            return True
        return False

    def search_tasks(self, session: Session, query: str, user_id: str) -> List[Task]:
        """Search tasks by description or category containing the query."""
        # Fetch all users tasks and filter in Python for robustness across DBs (Case-insensitive)
        user_tasks = self.get_tasks(session, user_id)
        query_lower = query.lower()
        return [
            t for t in user_tasks 
            if query_lower in t.description.lower() or query_lower in t.category.lower()
        ]