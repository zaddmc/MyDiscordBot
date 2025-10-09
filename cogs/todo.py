import discord
from discord.ext import commands

from file_manager import get_todos, save_todos


class Todo(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Bot = bot

    @commands.command(name="addtodo")
    async def add_todo(self, ctx: commands.Context, header: str, *task):
        todos = get_todos()
        if header in todos.keys():
            await ctx.channel.send(
                f"Title is already in todos\nTitle: {header}, content: {todos[header]}"
            )
            return
        todos[header] = " ".join(task)
        save_todos(todos)
        await ctx.channel.send("Todo was succesfully added")

    @commands.command(name="gettodo")
    async def get_todo(self, ctx: commands.Context, *header: str):
        todos = get_todos()
        if header == ():  # Empty tuples are cursed
            await ctx.channel.send(
                f"**The Available Todos are:** {', '.join(todos.keys())}"
            )
            return
        header = " ".join(header)
        if header in todos.keys():
            await ctx.channel.send(f"**{header}:** {todos[header]}")
            return
        await ctx.channel.send("Todo was not found :(")


async def setup(bot):
    await bot.add_cog(Todo(bot))
