import discord
from discord.ext import commands, tasks
import logging
import os
import datetime
import webserver
from dotenv import load_dotenv

load_dotenv()
token = os.environ['TOKEN']

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot_guilds = list()
guild_channels = dict()
role_name = 'RNG Enjoyer'
guildchannelfilename = 'guildchanneldata.txt'

bot = commands.Bot(command_prefix='rng!', intents=intents)

utc = datetime.timezone.utc
time = datetime.time(hour=0, minute=0, tzinfo=utc)

with open(guildchannelfilename, 'r') as f:
    data = f.readlines()

async def check_setup(ctx, setup):
    if ctx.guild.id in guild_channels.keys():
        return True
    else:
        if not setup:
            await ctx.channel.send(f"Setup not yet complete! Please type rng!setup first!")
        return False

@bot.event
async def on_ready():
    print(f"We are ready to go, {bot.user.name}")
    for guildchanneldata in data:
        guildchannel = guildchanneldata.split(':')
        guild_channels.update({int(guildchannel[0]):int(guildchannel[1].replace('\n', ''))})
    print(guild_channels)
    if not send_reminder.is_running():
        send_reminder.start()
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await bot.process_commands(message)

@bot.command()
async def setup(ctx):
    if await check_setup(ctx, True):
        await ctx.channel.send(f"Setup already complete")
    else:
        await ctx.guild.create_role(name=role_name)
        guild_channels.update({ctx.guild.id: ctx.channel.id})
        channel = bot.get_channel(guild_channels[ctx.guild.id])
        await channel.send(f"Setup complete for this channel (to set a new channel, type rng!set_channel)")
        channel_output = open(guildchannelfilename, "a")
        channel_output.write(f"{ctx.guild.id}:{ctx.channel.id}\n")
        channel_output.close()

@bot.command()
async def set_channel(ctx):
    if await check_setup(ctx, False):
        guild_channels.update({ctx.guild.id: ctx.channel.id})
        channel = bot.get_channel(guild_channels[ctx.guild.id])
        with open(guildchannelfilename, 'r') as fr:
            data = fr.readlines()

        with open(guildchannelfilename, 'w') as file:
            for line in data:
                if(str(ctx.guild.id) in line):
                    print("found current guild")
                    file.write(f"{ctx.guild.id}:{ctx.channel.id}\n")
                else:
                    print("not current guild")
                    file.write(line)
        await channel.send(f"Set channel for reminders to #{channel.name}")

@bot.command()
async def get_reminders(ctx):
    if await check_setup(ctx, False):
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role:
            await ctx.author.add_roles(role)
            await ctx.channel.send(f"Successfully added reminder role to {ctx.author.name}")
        else:
            await ctx.channel.send(f"Please don't delete the RNG Reminders role, type rng!create_role to recreate it.")

@bot.command()
async def stop_reminders(ctx):
    if await check_setup(ctx, False):
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role:
            await ctx.author.remove_roles(role)
            await ctx.channel.send(f"Successfully removed reminder role from {ctx.author.name}")
        else:
            await ctx.channel.send(f"Please don't delete the RNG Reminders role, type rng!create_role to recreate it.")

@bot.command()
async def send_reminders(ctx):
    for guild_id in guild_channels.keys():
        print(guild_id)
        guild = bot.get_guild(guild_id)
        channel = bot.get_channel(guild_channels[guild_id])
        role = discord.utils.get(guild.roles, name=role_name)
        await channel.send(f"{role.mention} it is time to roll a new number!")

@tasks.loop(time=time)
async def send_reminder():
    print("time reached")
    for guild_id in guild_channels.keys():
        print(guild_id)
        guild = bot.get_guild(guild_id)
        channel = bot.get_channel(guild_channels[guild_id])
        role = discord.utils.get(guild.roles, name=role_name)
        await channel.send(f"{role.mention} it is time to roll a new number!")
        

    
webserver.keep_alive()
bot.run(token)
