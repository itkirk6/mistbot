# bot.py

#system imports
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
#from colorama import init, Back, Fore, Style
import datetime
import platform
    #import random

#custom imports
from discordInfo import channels, users     #dicts in the form of name:ID
import sheetsInterface
    #import GPT

#copyright disney 2000


#   Global Variables
RESPONSE_CHANCE = 0.05     #chance that bot sends something in general thread per interaction (1=100%, 0.5=50%)


#   Load Environment Variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')      #Discord Token
apiKey = os.getenv('GOOGLE_API_KEY')    #Google API Key
GUILD_ID = discord.Object(id=int(os.getenv('GUILD_ID')))
#init(convert=True)                      #colorama
#def prfx(): return f'{Back.BLACK} {Fore.GREEN} {datetime.datetime.now()} {Back.RESET} {Fore.WHITE} {Style.BRIGHT}'  # Style for Console



#client = discord.Client(intents=discord.Intents.all())
client = commands.Bot(command_prefix=".", intents=discord.Intents.all())

@client.event
async def on_ready():

    print(" Logging in...")
    print(" Logged in : " + f'{client.user}')
            
    synced = await client.tree.sync(guild=GUILD_ID)
    print(" Slash Commands Synced : " + str(len(synced)) + " Commands ")
    print(" Discord Version : " + discord.__version__)
    print(" Python Version : "f'{platform.python_version()}')
    



@client.tree.command(name="bill", description="Add a bill to the list", guild=GUILD_ID)
@discord.app_commands.describe(split = "How many ways to split the bill? [5 or 3]", amount = "How much the bill was", description = "What you bought")
async def bill(interaction: discord.Interaction, split: int, amount: discord.app_commands.Range[float, 0], description: str):
    # /bill [number] [amount] [multiple word description]
    #example commands
    # /bill 5 100 walmart groceries          -> splits a $100 walmart purchase between all 5 people
    # /bill 3 20 ifixit                      -> splits a $20 purchase between the boys

    if split not in [3, 5]:
        await interaction.response.send_message("Invalid value for split. Please enter either 3 or 5.", ephemeral=True)
        return

    response = sheetsInterface.bill(interaction.user.id, split, amount, description)
    if response:
        response = addPings(response)
        await interaction.response.send_message(response)
        print(interaction.user.nick + " executed command : "+ f"/bill {split} {amount} {description}")




@client.tree.command(name="money", description="Check who owes what", guild=GUILD_ID)
#@discord.app_commands.guilds(GUILD_ID)
async def money(interaction: discord.Interaction):
    response = sheetsInterface.checkMoney()
    if response:
        response = addPings(response)
        await interaction.response.send_message(response)
        print(interaction.user.nick + " executed command : " + f"/money")

    

@client.tree.command(name="split", description="Add a bill to the list, split between you and another person.", guild=GUILD_ID)
@discord.app_commands.choices(member=[
    discord.app_commands.Choice(name="Ivan", value=1),
    discord.app_commands.Choice(name="Jesse", value=2),
    discord.app_commands.Choice(name="Nico", value=3)
])
@discord.app_commands.describe(member = "Who you are splitting it with", amount = "How much the bill was", description = "What you bought")
async def split(interaction: discord.Interaction, member: discord.app_commands.Choice[int], amount: discord.app_commands.Range[float, 0], description: str):
    memberID = users[member.name.lower()]
    response = sheetsInterface.splitBill(interaction.user.id, memberID, amount, description)
    if response:
        response = addPings(response)
        await interaction.response.send_message(response)
        print(interaction.user.nick +  " executed command : " + f"/split {member.name} {amount} {description}")




@client.tree.command(name="paid", description="Document the fact you paid someone a balance you owe them", guild=GUILD_ID)
@discord.app_commands.choices(member=[
    discord.app_commands.Choice(name="Ivan", value=1),
    discord.app_commands.Choice(name="Jesse", value=2),
    discord.app_commands.Choice(name="Nico", value=3)
])
@discord.app_commands.describe(member = "Who you paid", amount = "How much you paid")
async def paid(interaction: discord.Interaction, member: discord.app_commands.Choice[int], amount: discord.app_commands.Range[float, 0]):
    memberID = users[member.name.lower()]
    response = sheetsInterface.paid(interaction.user.id, memberID, amount)
    if response:
        response = addPings(response)
        await interaction.response.send_message(response)
        print(interaction.user.nick +  " executed command : " + f"/paid {member.name} {amount}")




@client.tree.command(name="charge", description="Charge a user some money", guild=GUILD_ID)
@discord.app_commands.choices(member=[
    discord.app_commands.Choice(name="Ivan", value=1),
    discord.app_commands.Choice(name="Jesse", value=2),
    discord.app_commands.Choice(name="Nico", value=3)
])
@discord.app_commands.describe(member = "Who owes you", amount = "How much they owe you", description = "What it is for")
async def paid(interaction: discord.Interaction, member: discord.app_commands.Choice[int], amount: discord.app_commands.Range[float, 0], description: str):
    memberID = users[member.name.lower()]
    response = sheetsInterface.charge(interaction.user.id, memberID, amount, description)
    if response:
        response = addPings(response)
        await interaction.response.send_message(response)
        print(interaction.user.nick +  " executed command : " + f"/charge {member.name} {amount} {description}")



#async def GPT():
    #send a random response sometimes if there's interactions in the general channel
    #turned off for now due to GPT errors
    """
    if interaction.channel.id == channels["general"]:
    
        if interaction.content.lower().startswith("mistbot"):
            question = " ".join(interaction.content.split(" ")[1:])
            response = GPT.respond(question)
            if response:
                await interaction.channel.send(response)
                print("sent a response")
            else:
                await interaction.channel.send("That was a confusing interaction dude")
                    
        elif random.random() < RESPONSE_CHANCE:
            if interaction.content:
                response = GPT.writeRap(interaction.content)
                if response:
                    await interaction.channel.send(response)
                    print("sent a rap")
                else:
                    await interaction.channel.send("That was a confusing interaction dude")
    """


def addPings(msg):
    newMsg = []
    for line in msg.split("\n"):
        newLine = []
        for word in line.split(" "):
            if word[0] == "@":
                if word[1:] in users.keys():
                    newLine.append(f'<@{users[word[1:]]}>')
            else:
                newLine.append(word)
        newMsg.append(" ".join(newLine))
    
    return "\n".join(newMsg)

client.run(TOKEN)
