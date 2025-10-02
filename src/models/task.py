from dataclasses import dataclass
from typing import Optional

@dataclass
class Task:
    id: Optional[int]
    title: str
    completed: bool = False
    category: str = "Общее"
    due_date: Optional[str] = None  # формат: "YYYY-MM-DD HH:MM"
    section: str = "Сегодня"
    parent_id: Optional[int] = None  # если задача — подзадача
    notified: bool = False
    description: str = ""  # новое поле