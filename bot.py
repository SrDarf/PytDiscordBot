import os
from dotenv import load_dotenv
import datetime,pytz
import discord;
import random;
from discord.ext import commands,tasks
from discord import app_commands
import google.generativeai as genai
import os 
import google.generativeai as genai
from discord import SelectOption
import aiohttp
import requests
load_dotenv()
token = os.getenv('token')
prefix = os.getenv('prefix')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix=prefix,intents=intents)

#Definição de tempo!

atime = datetime.datetime.now(tz=pytz.timezone ('America/Sao_Paulo'))
fuso_horario = atime.tzinfo

#horario = datetime.time(23,32,tzinfo=fuso_horario)

#Cogs que puxam os comandos

async def carregar_cogs():
    carregados = []
    for arquivo in os.listdir('cogs'):
        if arquivo.endswith('.py'):
            await bot.load_extension(f"cogs.{arquivo[:-3]}")
            carregados.append(arquivo)

    print("Arquivos carregados:")
    for arquivo in carregados:
        print(arquivo)
    return carregados

#Ready event

@bot.event
async def on_ready():
    print(f'O {bot.user.name} está pronto para o uso!')

#System command

@bot.command()

async def sync(ctx:commands.Context):

    if ctx.author.id == 468470557457776641:
        await ctx.reply('Modo administrador? Ok comandos slash sincronizados com sucesso!')
        sinc = await bot.tree.sync()
        await ctx.reply(f'Foram sincronizados {sinc} comandos!')
    else:   
        await ctx.reply('Você precisa ser um administrador do bot para executar este comando')

#Invite system command
@bot.command()
async def invite(ctx):
    try:
     
        invite_link = discord.utils.oauth_url(bot.user.id, permissions=discord.Permissions(permissions=379968))


        async def response(interact: discord.Interaction):
            await interact.response.send_message('O que você achou que fosse acontecer?', ephemeral=True)
            await interact.followup.send_message(f'Aqui está o link de convite para adicionar o bot ao seu servidor: {invite_link}')

  
        view = discord.ui.View()
        button_invite = discord.ui.Button(label='Clique para convidar', style=discord.ButtonStyle.link, url=invite_link)
        button_brabo = discord.ui.Button(label='Botão brabo', style=discord.ButtonStyle.green)
        button_brabo.callback = response

        view.add_item(button_invite)
        view.add_item(button_brabo)

     
        await ctx.send('Pressione o botão para convidar o bot ou clique no botão brabo!', view=view)
    
    except discord.Forbidden:
        await ctx.send("Eu não tenho permissão para criar convites neste servidor.")
    except discord.HTTPException:
        await ctx.send("Ocorreu um erro ao criar o convite.")



genai.configure(api_key="minhakey")

model = genai.GenerativeModel('gemini-pro',
	safety_settings = [
    {
        "category": "HARM_CATEGORY_DANGEROUS",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
	]
	)


@bot.command(name = "ask")
async def ask(ctx: commands.Context, *, prompt: str):
	response = model.generate_content(prompt)


	await ctx.reply(response.text)



stats = ['⁉️ Precisa de ajuda? !botinfo', '🎶 8 bit songs on top!']

@tasks.loop(seconds=5)
async def stuffurich():
    ctype = random.choice([discord.ActivityType.playing, discord.ActivityType.watching])
    cstats = random.choice(stats)


    if random.random() < 0.5:
        aatv = discord.Activity
    else:
        aatv = discord.CustomActivity

 
    if aatv == discord.CustomActivity:
        cstats = random.choice(stats)
    else:  
        if ctype == discord.ActivityType.watching:
            cstats = random.choice(['Rpg do Cellbit', 'Hentai'])
        else:
            cstats = random.choice(['Minecraft'])

    await bot.change_presence(
        status=discord.Status.idle,
        activity=aatv(
            type=ctype,
            name=cstats,
            url='https://www.youtube.com/watch?v=IkrVNH0uy0w'
        )
    )







 #Start 
@bot.event
async def on_ready():
    print(f'O {bot.user.name} está pronto para o uso!')
    await carregar_cogs()
    await stuffurich.start()

bot.run(token=token)