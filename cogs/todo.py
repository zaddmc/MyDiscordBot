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
    )
    async def m_add_todo(
        self,
        interaction: discord.Interaction,
        contents: str,
        target: discord.Member | None,
    ):
        if not target and isinstance(interaction.user, discord.Member):
            target = interaction.user
        if target and interaction.guild_id:
            todo = Todo(
                target.name,
                interaction.user.name,
                contents,
            )
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
        todos = get_todos(target=target, state=[TodoStateEnum.IN_COMPLETE, TodoStateEnum.IN_PROGRESS])
        return [
            ac.Choice(name=todo.Content[:100], value=todo.Uuid)
            for todo in todos
            if current.lower() in todo.Content.lower()
        ]

    @ac.command(name="todo_cstate", description="Change the state of a Todo")
    @ac.describe(todo_mark="The Todo of yours to change state of", mark_as="The state to mark the todo as")
    @ac.autocomplete(todo_mark=m_todo_autocomplete)
    @ac.choices(
        mark_as=[
            ac.Choice(name="InProgress", value=TodoStateEnum.IN_PROGRESS.value),
            ac.Choice(name="Succes", value=TodoStateEnum.SUCCES.value),
            ac.Choice(name="Failed", value=TodoStateEnum.FAILED.value),
            ac.Choice(name="InComplete", value=TodoStateEnum.IN_PROGRESS.value),
        ]
    )
    async def m_fin_todo(self, intr: discord.Interaction, todo_mark: str, mark_as: ac.Choice[str] | None):
        respond = intr.response.send_message
        todo = get_todo(todo_mark)
        if not todo:
            await respond("Failed to find Todo", ephemeral=True)
            return
        todo.State = TodoStateEnum(mark_as.value) if mark_as else TodoStateEnum.SUCCES
        save_modded_todo(todo)
        await respond(f"Marked **{todo.Content}** As **{todo.State.value}**")

    @ac.command(name="todo_get", description="Get all todos associated with given user or group")
    @ac.describe(
        user="User to reveal todos of, FishIn is everyone",
        state="Which state should the retreived todos be in, Leave empty for all",
    )
    @ac.choices(
        state=[
            ac.Choice(name="InProgress", value=TodoStateEnum.IN_PROGRESS.value),
            ac.Choice(name="InComplete", value=TodoStateEnum.IN_COMPLETE.value),
            ac.Choice(name="Succes", value=TodoStateEnum.SUCCES.value),
            ac.Choice(name="Failed", value=TodoStateEnum.FAILED.value),
        ]
    )
    async def m_get_todos(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        state: ac.Choice[str] | None,
    ):
        e_state = TodoStateEnum(state.value) if state else None
        is_group = user.name == "FishIn"
        target = None if is_group else user.name

        target_text = "The group" if is_group else f"User: **{target}**"
        state_text = f" with state **{e_state.value}**" if e_state else ""
        string = f"{target_text} has the following todos{state_text}:\n"
        todos = get_todos(state=e_state, target=target)

        for todo in todos:
            cur_state = f", Cur State **{todo.State.value}**" if not e_state else ""
            todo_target = f", Target is **{todo.Target}**" if is_group else ""
            string += f"Sent by **{todo.Sender}**{todo_target}{cur_state}:  {todo.Content}\n"

        string.strip()
        await interaction.response.send_message(string, silent=True)

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
