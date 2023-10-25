import asyncio
import time
from discord.ext import commands
import discord
import random
from collections import defaultdict
import urllib.request
import json
import os
from dotenv import load_dotenv

# Dictionary to hold timestamps of user messages
user_messages = defaultdict(list)

# Toggle for the flood command
flood_active = False

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(
    command_prefix="!",  # Change to desired prefix
    case_insensitive=True, # Commands aren't case-sensitive
    intents = intents # Set up basic permissions
)

bot.author_id = 187517861923782657  # Change to your discord id

@bot.event
async def on_ready():  # When the bot is ready
    print("I'm in")
    print(bot.user)  # Prints the bot's username and identifier

@bot.command()
async def pong(ctx):
    await ctx.send('pong')

# When typing `!name` the bot should write back the name of the user typing the command
@bot.command()
async def name(ctx):
    await ctx.send(ctx.author.name)

@bot.command()
async def d6(ctx):
    await ctx.send(random.randint(1,6))

# When typing "Salut tout le monde" (without the command sign), the bot should say "Salut tout seul" and ping the original author of the message
@bot.event
async def on_message(message):
    if message.content == "Salut tout le monde":
        await message.channel.send("Salut tout seul")
        await message.channel.send(message.author.mention)
    await bot.process_commands(message)

# When typing `!admin <A member nickname>`, your bot should create an Admin role (if it doesn't exists) on your server, allowing them to manage channels, kick and ban members, and give it to the member in parameter

@bot.command()
async def admin(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name="Admin")
    if role is None:
        await ctx.guild.create_role(name="Admin", permissions=discord.Permissions(22))
        role = discord.utils.get(ctx.guild.roles, name="Admin")
    await member.add_roles(role)

# When typing `!ban <A member nickname> <ban reason?>`, your bot should ban that member from the server (**Test with caution**) displaying the input reason for the ban. If no ban reason is input, your bot should display a funny catchphrase picked at random in a given list of catchphrases de Cyril Hanouna

@bot.command()
async def ban(ctx, member: discord.Member, reason=None):
    if reason is None:
        reasons = ["C'est un fdp", "Il est trop moche", "Il est trop con", "Il est trop nul", "Il est trop bête", "Il est trop méchant"]
        reason = random.choice(reasons)
    await ctx.guild.ban(member, reason=reason)
    await ctx.send(f"{member} a été banni pour la raison suivante : {reason}")

# The command `!flood` should activate (or deactivate) a moderation workflow. When activated, your bot should monitor the messages and display a warning to any user posting more than X messages in the last Y minutes. The (de)activation should be confirmed using a custom message

@bot.command()
async def flood(ctx):
    #state flood
    global flood_active
    flood_active = not flood_active

    if flood_active:
        await ctx.send("Flood moderation is now **activated**!")
    else:
        await ctx.send("Flood moderation is now **deactivated**!")

@bot.event
async def on_message(message):
    await bot.process_commands(message)

    if flood_active and not message.author.bot:
        user_messages[message.author.id].append(time.time())
        
        # Define your X and Y here
        X = 5  # e.g., 5 messages
        Y = 60  # e.g., in 60 seconds

        # Filter out messages older than Y seconds
        user_messages[message.author.id] = [t for t in user_messages[message.author.id] if time.time() - t <= Y]

        if len(user_messages[message.author.id]) > X:
            await message.channel.send(f"{message.author.mention}, you're sending messages too quickly! Please slow down.")

#When typing `!xkcd`, your post should post a random comic from https://xkcd.com using urllib and the JSON API. The bot should display the title of the comic as well as the image itself and a message to the one who typed the command
@bot.command()
async def xkcd(ctx):
    #latest comic number
    url = "https://xkcd.com/info.0.json"
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    # random comic number
    random_comic = random.randint(1, data["num"])
    url = f"https://xkcd.com/{random_comic}/info.0.json"
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    await ctx.send(data["img"])
    await ctx.send(data["title"])
    await ctx.send(ctx.author.mention)
# When typing `!poll <q[uestion>`, your bot should post a @here mention followed by a Yes/No question. The bost will then write the question again in another message and add one :thumbsup: and one :thumbsdown: emoji reaction to its message .Define a time-limit for the poll. When the limit has been reached, bot will bot a message with the final result and delete the original poll message
@bot.command()
async def poll(ctx, question):
    await ctx.send("@here")
    # create a message object
    message = await ctx.send(question)
    # destroy the original message
    await ctx.message.delete()
    # add reactions to the message
    await message.add_reaction('👍')
    await message.add_reaction('👎')
    # add a timer
    timer = 10 # seconds
    await asyncio.sleep(timer)
    # get the message agains
    message = await ctx.fetch_message(message.id)
    # get the reactions
    reactions = message.reactions
    # count the reactions
    yes = 0
    no = 0
    for reaction in reactions:
        if reaction.emoji == '👍':
            yes = reaction.count
        elif reaction.emoji == '👎':
            no = reaction.count
    # delete the message
    await message.delete()
    # send the result
    await ctx.send(f"Result: {yes - 1} yes and {no - 1} no")

# play a sound from the file sound.mp3
@bot.command()
async def play(ctx):

    channel = ctx.author.voice.channel
    vc = await channel.connect()
    
    # Play the music.mp3 file
    vc.play(discord.FFmpegPCMAudio(executable="/usr/bin/ffmpeg", source="sound.mp3"))
    
    # Wait until audio is played
    while vc.is_playing():
        await asyncio.sleep(1)
    
    await vc.disconnect()
        
#  Create a chat-GPT integration with the command `!prompt <prompt to be processed>`
@bot.command()
async def prompt(ctx, *, prompt):
    url = "none"
    data = {
        "prompt": prompt,
        "length": prompt.length + 10,
        "num_samples": 1,
    }
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(url, json.dumps(data).encode(), headers)
    response = urllib.request.urlopen(req)
    data = json.loads(response.read())
    await ctx.send(data["replies"][0])


load_dotenv()
token = os.getenv('DISCORD_TOKEN')
bot.run(token)  # Starts the bot