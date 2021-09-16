import discord
from discord.ext import commands, tasks
import os
import time
from datetime import date
import io
from itertools import cycle
from discord.ext.commands.bot import Bot
import json
import requests
from github import Github

g = Github("github token")

repo = g.get_repo("KAMKAZEMARCI/Tesla-Blacklist") #resp
token = "token here"
prefix = "<"


client = discord.Client()
client = commands.AutoShardedBot(shard_count=10, command_prefix="<")
intents = discord.Intents.all()
intents.members = True
intents = discord.Intents(messages=True, guilds=True, members=True) #some random stuff, i was testing sum
client = commands.Bot(
    description="Tesla Blacklist",
    command_prefix=prefix,
    self_bot=False,
    guild_subscriptions=True, 
    intents=intents
)
client.remove_command('help')

@client.event
async def on_message(message):
  await client.process_commands(message)

@client.event
async def on_message_edit(before, after):
    await client.process_commands(after)


@client.command()
async def findrblx(ctx, *, user:discord.User=None): # b'\xfc'
    await ctx.message.delete()
    if user is None:
        user = ctx.author
    rbx = f"https://verify.eryn.io/api/user/{user.id}"
    output = requests.get(rbx).text
    embed = discord.Embed(title="Roblox Username:", description=f"```\n{output}\n```")
    embed.add_field(name="API:", value="verify.eryn.io", inline=False)
    embed.set_footer(text="Tesla Blacklist")
    await ctx.send(embed=embed)


@client.command()
@commands.has_permissions(administrator=True)
async def blacklist(ctx):
    contents = repo.get_contents("blacklist.lua")
    q_list = ['Please send roblox user ID that you want to blacklist.']
    submit_channel = ctx.channel
    channel = ctx.channel

    def check(m):
        return m.content is not None and m.channel == channel

    for question in q_list:
            await channel.send(question)
            msg = await client.wait_for('message', check=check)
            ans = msg.content

    submit_wait = True
    while submit_wait:
        await channel.send('Are you sure you want to blacklist the user? type ``submit`` to confirm')
        msg = await client.wait_for('message', check=check)
        if "submit" in msg.content.lower():
          submit_wait = False
          answers = f"\n{ans}"
          submit_msg = f'''Blacklisted user {answers}'''
          await submit_channel.send(submit_msg)
          data = f"{answers}"
          with open('blacklist.txt', 'a', encoding = 'UTF-8') as f:
              f.write(data)
          with open('blacklist.txt', 'r', encoding = 'UTF-8') as f:
              fixed = f.read()[:-1]
          with open('blacklist.txt', 'w', encoding = 'UTF-8') as f:
              f.write(fixed)
          time.sleep(1)
          with open('blacklist.txt', 'r') as file:
            datas = file.read()
            print(datas)
          repo.update_file("blacklist.lua", "Updated", f"{datas}", contents.sha)

@client.event
async def on_command_error(ctx, error): # b'\xfc
  error_str = str(error)
  error = getattr(error, 'original', error)
  if isinstance(error, commands.CommandNotFound):
    return
  elif isinstance(error, commands.CheckFailure):
    print(f"[ERROR]: You're missing permission to execute this command")           
  else:
    print(f"[ERROR]: {error_str}")

@client.event
async def on_ready():
    print("Bot is ready!")

client.run("token here")
