import datetime
import os
import subprocess

import discord
from discord import app_commands
from discord.ext import commands

from file_manager import get_todos, make_todo, save_todos


class TodoHandler(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Bot = bot

    @app_commands.command(name="addtodo", description="Add a todo")
    @app_commands.describe(
        contents="The contents of the todo",
        target="Who to target with command",
        notify="Give a time that is compatible with the command 'at'\nIf not, then get fucked",
    )
    async def add_todo(
        self,
        interaction: discord.Interaction,
        contents: str,
        target: discord.Member | None,
        notify: str | None,
    ):
        todos = get_todos()
        if not target:
            target = interaction.user
        todo = make_todo(
            contents,
            interaction.user.name,
            interaction.user.id,
            target.name,
            target.id,
            interaction.guild_id,
        )
        todos["incomplete"].append(todo)
        save_todos(todos)
        await interaction.response.send_message(
            f"Todo for **{todo['target']}**: {todo['contents']}",
            silent=True,
        )

    @commands.command(name="gettodo")
    async def get_todo(self, ctx: commands.Context):
        todos = get_todos()
        string = "You have the following incomplete todos\n"
        index = 0
        for todo in todos["incomplete"]:
            if todo["target"] != str(ctx.message.author):
                continue
            string += (
                f"{index} Submitted by **{todo["sender"]}**: " + todo["contents"] + "\n"
            )
            index += 1
        string.strip()
        if index == 0:
            string = "You have no remaining todos to complete!"
        await ctx.send(string)

    @commands.command(name="fintodo")
    async def finish_todo(self, ctx: commands.Context, *args):
        todos = get_todos()
        my_todos = [
            t for t in todos["incomplete"] if t["target"] == str(ctx.message.author)
        ]

        for arg in args:
            if arg.isdigit() and int(arg) < len(my_todos):
                tod = my_todos.pop(int(arg))
                todos["incomplete"].remove(tod)
                todos["complete"].append(tod)
        save_todos(todos)
        await ctx.send(f"Marked **{tod['contents']}** As Finished")

    # Get Todos
    @app_commands.command(
        name="gettodos", description="Get all todos associated with given user"
    )
    @app_commands.describe(
        user="User to reveal todos of", state="Which category should the todos be in"
    )
    @app_commands.choices(
        state=[
            app_commands.Choice(name="InComplete", value="incomplete"),
            app_commands.Choice(name="All", value="all"),
            app_commands.Choice(name="Completed", value="complete"),
        ]
    )
    async def get_todos(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        state: app_commands.Choice[str],
    ):
        todos = get_todos()
        if user.name == "FishIn":
            string = f"The group has the following todos\n"
        else:
            string = f"User: **{user.name}** has the following todos:\n"

        in_todos = (
            todos[state.value]
            if state.value != "all"
            else todos["complete"] + todos["incomplete"]
        )
        for todo in filter(lambda d: user.name in (d["target"], "FishIn"), in_todos):
            if user.name == "FishIn":
                string += f"Submitted by **{todo['sender']}**, intended for **{todo['target']}**: {todo['contents']}\n"
            else:
                string += f"Submitted by **{todo["sender"]}**: {todo["contents"]}\n"
        string.strip()
        await interaction.response.send_message(string, silent=True)


from utils import get_guilds


async def setup(bot):
    await bot.add_cog(TodoHandler(bot), guilds=get_guilds())
