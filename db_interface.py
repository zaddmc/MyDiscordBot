import logging
import sqlite3
import uuid
from enum import Enum
from typing import Optional

lg = logging.getLogger(__name__)

con = None
if not con:
    con = sqlite3.connect("main.db", autocommit=True)
    cur = con.cursor()
    try:
        if "todo" not in cur.execute("SELECT name FROM sqlite_master").fetchone():
            raise Exception("I am too lazy, table will be created")
    except Exception as e:
        lg.error(f"Failed to instantiate table: {e}")
        cur.execute("CREATE TABLE todo(target, sender, content, priority, state, uuid)")


class TodoStateEnum(Enum):
    NOT_BEGUN = "NotBegun"
    IN_PROGRESS = "InProgress"
    FAILED = "Failed"
    SUCCES = "Succes"


class Todo:
    def __init__(
        self,
        target: str,
        sender: str,
        content: str,
        priority: int = 0,
        state: TodoStateEnum | str = TodoStateEnum.NOT_BEGUN,
        l_uuid: Optional[str] = None,
    ):
        self.Target = target
        self.Sender = sender
        self.Content = content
        self.Priority = priority
        self.State = state if isinstance(state, TodoStateEnum) else TodoStateEnum(state)
        self.Uuid = l_uuid if l_uuid else str(uuid.uuid4())

    def to_sql(self) -> dict[str, str | int]:
        return {
            "target": self.Target,
            "sender": self.Sender,
            "content": self.Content,
            "priority": self.Priority,
            "state": self.State.value,
            "uuid": self.Uuid,
        }

    def __str__(self) -> str:
        return f"<Todo: {self.Target=}, {self.Sender=}, {self.Content=}, {self.Priority=}, {self.State=}, {self.Uuid=}>"


def get_todos(
    target: Optional[str] = None,
    sender: Optional[str] = None,
    state: Optional[TodoStateEnum | list[TodoStateEnum]] = None,
    min_priority: Optional[int] = None,
) -> list[Todo]:
    query = "SELECT * FROM todo"
    conditions = []
    params: dict[str, str | int] = {}
    if target:
        conditions.append("target = :target")
        params["target"] = target
    if sender:
        conditions.append("sender = :sender")
        params["sender"] = sender
    if state:
        states = state if isinstance(state, list) else [state]
        state_keys = []
        for i, s in enumerate(states):
            key = f"state{i}"
            state_keys.append(f":{key}")
            params[key] = s.value
        conditions.append(f"state IN ({', '.join(state_keys)})")
    if min_priority:
        conditions.append("priority >= :priority")
        params["priority"] = min_priority
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    res = cur.execute(query, params)
    return [Todo(*row) for row in res.fetchall()]


def get_todo(l_uuid: str) -> Optional[Todo]:
    res = cur.execute("SELECT * FROM todo WHERE uuid=?", (l_uuid,)).fetchone()
    return Todo(*res)


def add_todo(todo: Todo):
    cur.execute("INSERT INTO todo VALUES(:target, :sender, :content, :priority, :state, :uuid)", todo.to_sql())


def save_modded_todo(todo: Todo):
    cur.execute("UPDATE todo SET content=:content, priority=:priority, state=:state WHERE uuid=:uuid", todo.to_sql())
