import discord
from discord.ext import commands
from discord import app_commands


class Calculos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot



    #Lista de comandos sobre Calculos

    @commands.command()
    async def somar(self, ctx: commands.Context, num1: float, num2: float):
        resultado = num1 + num2
        await ctx.reply(f'O resultado da sua soma de `{num1}` + `{num2}` é: `{resultado}`')
           

    @commands.command()
    async def multiplicar(self, ctx: commands.Context, num1: float, num2: float):
        resultado = num1 * num2
        await ctx.reply(f'O resultado da sua multiplicação de `{num1}` x `{num2}` é: `{resultado}`')

    @commands.command()
    async def subtrair(self, ctx: commands.Context, num1: float, num2: float):
        resultado = num1 - num2
        await ctx.reply(f'O resultado da sua subtração de `{num1}` - `{num2}` é: `{resultado}`')    

    @commands.command()
    async def dividir(self, ctx: commands.Context, num1: float, num2: float):
        resultado = num1 / num2
        await ctx.reply(f'O resultado da sua divisão de `{num1}` / `{num2}` é: `{resultado}`')        

    #Slash em cogs 
    
    @app_commands.command()
    async def soma(self, interaction: discord.Interaction, num1: float, num2: float):
        resultado = num1 + num2
        await interaction.response.send_message(f'O resultado da sua soma de `{num1}` + `{num2}` é: `{resultado}`')

    @app_commands.command()
    async def subtrair(self, interaction: discord.Interaction, num1:float,num2:float):
        resultado = num1 - num2
        await interaction.response.send_message(f'O resultado da sua subtração de `{num1}` - `{num2}` é: `{resultado}`')    

    
    





#Iniciar o sistema de cogs

async def setup(bot):
    await bot.add_cog(Calculos(bot))
