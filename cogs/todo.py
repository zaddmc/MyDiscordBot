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

    @ac.command(name="addtodo", description="Add a todo")
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
        add_todo(todo)
        await interaction.response.send_message(
            f"Todo for **{todo.Target}**: {todo.Content}",
            silent=True,
        )

    async def m_todo_autocomplete(self, intr: discord.Interaction, current: str) -> List[ac.Choice[str]]:
        todos = get_todos(target=intr.user.name, state=TodoStateEnum.IN_COMPLETE)
        return [
            ac.Choice(name=todo.Content[:100], value=todo.Uuid)
            for todo in todos
            if current.lower() in todo.Content.lower()
        ]

    @ac.command(name="fintodo", description="Mark Todo as Finished")
    @ac.describe(todo_mark="The Todo of yours to mark as finished", mark_as="Mark as succes or failure")
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

    @ac.command(name="gettodos", description="Get all todos associated with given user")
    @ac.describe(
        user="User to reveal todos of, FishIn is everyone",
        state="Which category should the todos be in, Leave empty for all",
    )
    @ac.choices(
        state=[
            ac.Choice(name="InProgress", value=TodoStateEnum.IN_PROGRESS.value),
            ac.Choice(name="InComplete", value=TodoStateEnum.IN_PROGRESS.value),
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
        if user.name == "FishIn":
            string = f"The group has the following todos:\n"
            todos = get_todos(state=e_state)
        else:
            string = f"User: **{user.name}** has the following todos:\n"
            todos = get_todos(target=user.name, state=e_state)

        for todo in todos:
            if user.name == "FishIn":
                string += f"Sent by **{todo.Sender}**, targeted for **{todo.Target}**, Cur State **{todo.State}**:  {todo.Content}\n"
            else:
                string += f"Sent by **{todo.Sender}**, Cur State **{todo.State}**:  {todo.Content}\n"

        if len(todos) == 0:
            if user.name == "FishIn":
                string = "The group has finished all todos!\nNow make some new and bet back to work you slackers"
            else:
                string = "You have nothing to do\nGet serious and do some work you coward"
        string.strip()
        await interaction.response.send_message(string, silent=True)


from utils import get_guilds


async def setup(bot):
    await bot.add_cog(TodoHandler(bot), guilds=get_guilds())
