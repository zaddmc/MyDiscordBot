import datetime
import logging
import os
import subprocess
import uuid
from typing import List

import discord
from discord import app_commands as ac
from discord.ext import commands

# from file_manager import Todo, get_todo, get_todos, save_todos
from db_interface import Todo, TodoStateEnum, add_todo, get_todo, get_todos, save_modded_todo

lg = logging.getLogger(__name__)


class TodoHandler(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @ac.command(name="todo_add", description="Add a todo")
    @ac.describe(
        contents="The contents of the todo",
        target="Who to target with command",
        priority="How important it is, where higher is higher",
    )
    async def m_add_todo(
        self,
        interaction: discord.Interaction,
        contents: str,
        target: discord.Member | None,
        priority: int = 0,
    ):
        if not target and isinstance(interaction.user, discord.Member):
            target = interaction.user
        if target:
            todo = Todo(target.name, interaction.user.name, contents, priority)
        if not todo:
            await interaction.response.send_message(f"Failed to make Todo", silent=True)
            return
        add_todo(todo)
        await interaction.response.send_message(
            f"Todo for **{todo.Target}**: {todo.Content}",
            silent=True,
        )

    async def m_todo_autocomplete(self, intr: discord.Interaction, current: str) -> List[ac.Choice[str]]:
        cmd_name = intr.command.name if isinstance(intr.command, ac.Command) else "todo_cstate"
        target = "FishIn" if cmd_name == "todo_take" else intr.user.name
        todos = get_todos(target=target, state=[TodoStateEnum.NOT_BEGUN, TodoStateEnum.IN_PROGRESS])
        return [
            ac.Choice(name=todo.Content.split("\n")[0][:100], value=todo.Uuid)
            for todo in todos
            if current.lower() in todo.Content.lower()
        ]

    @ac.command(name="todo_cstate", description="Change the state of a Todo")
    @ac.describe(
        todo_mark="The Todo of yours to change state of",
        mark_as="The state to mark the todo as",
        priority="Change to another priority",
    )
    @ac.autocomplete(todo_mark=m_todo_autocomplete)
    @ac.choices(
        mark_as=[
            ac.Choice(name="InProgress", value=TodoStateEnum.IN_PROGRESS.value),
            ac.Choice(name="Succes", value=TodoStateEnum.SUCCES.value),
            ac.Choice(name="Failed", value=TodoStateEnum.FAILED.value),
            ac.Choice(name="NotBegun", value=TodoStateEnum.NOT_BEGUN.value),
        ]
    )
    async def m_fin_todo(
        self, intr: discord.Interaction, todo_mark: str, mark_as: ac.Choice[str] | None, priority: int | None
    ):
        respond = intr.response.send_message
        todo = get_todo(todo_mark)
        if not todo:
            await respond("Failed to find Todo", ephemeral=True)
            return
        if mark_as:
            todo.State = TodoStateEnum(mark_as.value)
        if priority:
            todo.Priority = priority
        if not mark_as and not priority:
            todo.State = TodoStateEnum.SUCCES
        if todo.State == TodoStateEnum.SUCCES:
            todo.Priority = -1000
        save_modded_todo(todo)
        state_text = f" As **{todo.State.value}**" if mark_as or (not priority and not mark_as) else ""
        priority_text = f" With priority {priority}" if priority else ""
        content_text = todo.Content.split("\n")[0]
        await respond(f"Marked **{content_text}**{state_text}{priority_text}", silent=True)

    @ac.command(name="todo_get", description="Get all todos associated with given user or group")
    @ac.describe(
        user="User to reveal todos of, FishIn is everyone",
        state="Which state should the retreived todos be in, Leave empty for all",
    )
    @ac.choices(
        state=[
            ac.Choice(name="NotFinished", value="NotFinished"),
            ac.Choice(name="InProgress", value=TodoStateEnum.IN_PROGRESS.value),
            ac.Choice(name="NotBegun", value=TodoStateEnum.NOT_BEGUN.value),
            ac.Choice(name="Finished", value="Finished"),
            ac.Choice(name="Succes", value=TodoStateEnum.SUCCES.value),
            ac.Choice(name="Failed", value=TodoStateEnum.FAILED.value),
        ]
    )
    async def m_get_todos(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        state: ac.Choice[str] | None,
        min_priority: int | None,
    ):
        if not state or state.value == "NotFinished":
            e_state = [TodoStateEnum.IN_PROGRESS, TodoStateEnum.NOT_BEGUN]
        elif state.value in TodoStateEnum:
            e_state = TodoStateEnum(state.value)
        else:
            e_state = [TodoStateEnum.SUCCES, TodoStateEnum.FAILED]
        is_group = user.name == "FishIn"
        target = None if is_group else user.name

        target_text = "The group" if is_group else f"User: **{target}**"
        state_text = f" with state **{e_state.value}**" if isinstance(e_state, TodoStateEnum) else ""
        priority_text = f" with at minimum {min_priority} priority" if min_priority else ""
        string = f"{target_text} has the following todos{state_text}{priority_text}:\n"
        todos = get_todos(state=e_state, target=target)
        todos = sorted(todos, key=lambda t: t.Priority, reverse=True)

        for todo in todos:
            todo_target = f", Target is **{todo.Target}**" if is_group else ""
            cur_state = f", Cur State **{todo.State.value}**" if isinstance(e_state, TodoStateEnum) else ""
            todo_priority = f", Priority is {todo.Priority}" if min_priority else ""
            todo_cont = " **Truncated**" if "\n" in todo.Content else ""
            string += f"Sent by **{todo.Sender}**{todo_target}{cur_state}{todo_priority}{todo_cont}:  {todo.Content.split('\n')[0]}\n"

        string.strip()
        await interaction.response.send_message(string, silent=True)

    @ac.command(name="todo_extend", description="Append more to a todo or show the full form")
    @ac.describe(todo_id="The Todo you want to extend", new_content="The new content you want to add")
    @ac.autocomplete(todo_id=m_todo_autocomplete)
    async def m_extend_todo(self, intr: discord.Interaction, todo_id: str, new_content: str | None):
        todo = get_todo(todo_id)
        if not todo:
            await intr.response.send_message("Failed to find todo", ephemeral=True)
            return
        if new_content:
            todo.Content += "\n- " + new_content
            save_modded_todo(todo)
        string = "The todo looks like:\n" + todo.Content
        await intr.response.send_message(string, silent=True)

    @ac.command(name="todo_take", description="Take a freed todo from Fish")
    @ac.describe(free_todo="The todo to take that is free")
    @ac.autocomplete(free_todo=m_todo_autocomplete)
    async def m_take_todo(self, intr: discord.Interaction, free_todo: str, new_target: discord.Member | None):
        todo = get_todo(free_todo)
        if not todo:
            await intr.response.send_message("Failed to find todo", ephemeral=True)
            return

        if new_target:
            todo.Target = new_target.name
            await intr.response.send_message(f"Todo has been assigned to **{new_target.name}**")
        else:
            todo.Target = intr.user.name
            await intr.response.send_message("Todo has been assigned to you", silent=True)
        save_modded_todo(todo)

    @ac.command(name="todo_free", description="Free one of you todos")
    @ac.describe(your_todo="The todo you dont want")
    @ac.autocomplete(your_todo=m_todo_autocomplete)
    async def m_free_todo(self, intr: discord.Interaction, your_todo: str):
        todo = get_todo(your_todo)
        if not todo:
            await intr.response.send_message("Failed to find todo", ephemeral=True)
            return
        todo.Target = "FishIn"
        save_modded_todo(todo)
        await intr.response.send_message("Todo has been freed, and is available to take", silent=True)


from utils import get_guilds


async def setup(bot):
    await bot.add_cog(TodoHandler(bot), guilds=get_guilds())
