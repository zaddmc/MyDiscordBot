import datetime

import discord
from discord import app_commands
from discord.ext import commands

from file_manager import get_todos, make_todo, save_todos


class TodoHandler(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Bot = bot

    @app_commands.command(name="addtodo", description="Add a todo")
    @app_commands.describe(
        contents="The contents of the todo", target="Who to target with command"
    )
    async def add_todo(
        self,
        interaction: discord.Interaction,
        contents: str,
        target: discord.Member,
    ):
        todos = get_todos()
        todo = make_todo(contents, interaction.user.name, target.name)
        todos["incomplete"].append(todo)
        save_todos(todos)
        await interaction.response.send_message(f"Was succesfully added")

    @commands.command(name="gettodo")
    async def get_todo(self, ctx: commands.Context):
        todos = get_todos()
        string = "You have the following incomplete todos\n"
        index = 0
        for todo in todos["incomplete"]:
            string += (
                f"{index} Submitted by **{todo["sender"]}**: " + todo["contents"] + "\n"
            )
        string.strip()
        await ctx.send(string)

    @commands.command(name="fintodo")
    async def finish_todo(self, ctx: commands.Context, args):
        todos = get_todos()
        print(args)
        for arg in args:
            if arg.isdigit():
                pass

        await ctx.send("Fuck you, aka not implemented")

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
        string = f"User: **{user.name}** has the following todos:\n"
        if state.value in ("all", "incomplete"):
            for todo in todos["incomplete"]:
                string += (
                    f"Submitted by **{todo["sender"]}**: " + todo["contents"] + "\n"
                )
        elif state.value in ("all", "complete"):
            for todo in todos["complete"]:
                string += (
                    f"Submitted by **{todo["sender"]}**: " + todo["contents"] + "\n"
                )
        string.strip()
        await interaction.response.send_message(string)


from utils import get_guilds


async def setup(bot):
    test_server_id = 593152900063297557
    await bot.add_cog(TodoHandler(bot), guilds=get_guilds())
