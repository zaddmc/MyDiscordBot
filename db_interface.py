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
            cur.execute("CREATE TABLE todo(target, sender, content, state, uuid)")
    except Exception as e:
        lg.error(f"Failed to instantiate table: {e}")
        cur.execute("CREATE TABLE todo(target, sender, content, state, uuid)")


class TodoStateEnum(Enum):
    IN_COMPLETE = "InComplete"
    IN_PROGRESS = "InProgress"
    FAILED = "Failed"
    SUCCES = "Succes"


class Todo:
    def __init__(
        self,
        target: str,
        sender: str,
        content: str,
        state: TodoStateEnum | str = TodoStateEnum.IN_COMPLETE,
        l_uuid: str | None = None,
    ):
        self.Target = target
        self.Sender = sender
        self.Content = content
        self.State = state if isinstance(state, TodoStateEnum) else TodoStateEnum(state)
        self.Uuid = l_uuid if l_uuid else str(uuid.uuid4())

    def to_sql(self) -> dict[str, str]:
        return {
            "target": self.Target,
            "sender": self.Sender,
            "content": self.Content,
            "state": self.State.value,
            "uuid": self.Uuid,
        }

    def __str__(self) -> str:
        return f"<Todo: {self.Target=}, {self.Sender=}, {self.Content=}, {self.State=}, {self.Uuid=}>"


def get_todos(
    target: Optional[str] = None, sender: Optional[str] = None, state: Optional[TodoStateEnum] = None
) -> list[Todo]:
    query = "SELECT * FROM todo"
    conditions = []
    params = {}
    if target:
        conditions.append("target = :target")
        params["target"] = target
    if sender:
        conditions.append("sender = :sender")
        params["sender"] = sender
    if state:
        conditions.append("state = :state")
        params["state"] = state.value
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    res = cur.execute(query, params)
    return [Todo(*row) for row in res.fetchall()]


def get_todo(l_uuid: str) -> Optional[Todo]:
    res = cur.execute("SELECT * FROM todo WHERE uuid=?", (l_uuid,)).fetchone()
    return Todo(*res)


def add_todo(todo: Todo):
    cur.execute("INSERT INTO todo VALUES(:target, :sender, :content, :state, :uuid)", todo.to_sql())


def save_modded_todo(todo: Todo):
    cur.execute("UPDATE todo SET content=:content, state=:state WHERE uuid=:uuid", todo.to_sql())


if __name__ == "__main__":
    todoes = Todo("aw", "me", "Testing")
    print(todoes)
    add_todo(todoes)
    print("Getting it back", get_todo(todoes.Uuid))
    todoes.Content = "New testing"
    todoes.State = TodoStateEnum.FAILED
    save_modded_todo(todoes)
    print("Getting cahges back", get_todo(todoes.Uuid))
    print()
    for tod in get_todos(state=TodoStateEnum.IN_COMPLETE):
        print(tod)
