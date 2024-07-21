import discord
import re
import random
from discord.ext import commands

class Mensagens(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mention_count = {}
        self.waiting_for_soma = False
        self.waiting_for_dado = False

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        
        # Check if bot is mentioned
        if self.bot.user.mentioned_in(message):
            author_id = message.author.id

            if author_id not in self.mention_count:
                self.mention_count[author_id] = 0

            # Increment mention count
            self.mention_count[author_id] += 1

            # Define responses
            responses = [
                "Oi! Posso te ajudar? Digite `!botinfo` para ter algumas informações!",
                "Okok você não entendeu? Digite `!botinfo` se quiser saber mais sobre.",
                "Cara eu sou um Bot eu não vou te responder diferente se voce ficar me marcando toda hora...",
                "Ok, agora você passou dos limites. Estou ficando bravo!",
                "Chega! Não vou mais responder.",
            ]

            # Get response index based on mention count
            response_index = min(self.mention_count[author_id], len(responses)) - 1

            embed = discord.Embed(
                title="Você me marcou...",
                description=responses[response_index],
                color=discord.Color.red()
            )

            await message.reply(embed=embed, mention_author=False)

    @commands.command()
    async def hsoma(self, ctx):
        if self.waiting_for_soma:
            self.waiting_for_soma = False
            await ctx.send("Desativei a espera por um cálculo matemático!")
        else:
            self.waiting_for_soma = True
            await ctx.send("Agora estou esperando um cálculo matemático!")

    @commands.command()
    async def hdado(self, ctx):
        if self.waiting_for_dado:
            self.waiting_for_dado = False
            await ctx.send("Desativei a espera por uma rolagem de dado!")
        else:
            self.waiting_for_dado = True
            await ctx.send("Agora estou esperando uma rolagem de dado!")

    @commands.command()
    async def botinfo(self, ctx):
        embed = discord.Embed(
            title=f"Informações sobre {self.bot.user.name}",
            description="Digite `!comandos` para ver os comandos, aqui estão algumas informações sobre o bot:",
            color=discord.Color.blurple()
        )

        embed.set_thumbnail(url=self.bot.user.avatar)

        # Bot info
        embed.add_field(name="Nome do Bot", value=self.bot.user.name, inline=False)
        embed.add_field(name="ID do Bot", value=self.bot.user.id, inline=False)

        # Server info
        embed.add_field(name="Servidores", value=len(self.bot.guilds), inline=False)
        embed.add_field(name="Usuários", value=len(set(self.bot.get_all_members())), inline=False)

        # Development info
        embed.add_field(name="Desenvolvedor", value="sr.dark", inline=False)
        embed.add_field(name="Versão do Bot", value="0.1", inline=False)

        # Description
        embed.add_field(name="Descrição", value="Hey! Sou o DarkRpg, uma extensão do DarkBot porém focado apenas no Rpg!", inline=False)

        # Support and links
        embed.add_field(name="Convite", value=f"[Clique aqui para me adicionar ao seu servidor]({discord.utils.oauth_url(self.bot.user.id)})")

        embed.set_footer(text=f"Comando executado por {ctx.author.name}", icon_url=ctx.author.avatar)

        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        
        # Check if bot is mentioned
        if self.bot.user.mentioned_in(message):
            author_id = message.author.id

            if author_id not in self.mention_count:
                self.mention_count[author_id] = 0

            # Increment mention count
            self.mention_count[author_id] += 1

            # Define responses
            responses = [
                "Oi! Posso te ajudar? Digite `!botinfo` para ter algumas informações!",
                "Okok você não entendeu? Digite `!botinfo` se quiser saber mais sobre.",
                "Cara eu sou um Bot eu não vou te responder diferente se voce ficar me marcando toda hora...",
                "Ok, agora você passou dos limites. Estou ficando bravo!",
                "Chega! Não vou mais responder.",
            ]

            # Get response index based on mention count
            response_index = min(self.mention_count[author_id], len(responses)) - 1

            embed = discord.Embed(
                title="Você me marcou...",
                description=responses[response_index],
                color=discord.Color.red()
            )

            await message.reply(embed=embed, mention_author=False)

        # Check for calculations or dice rolls if waiting for them
        if self.waiting_for_soma or self.waiting_for_dado:
            pattern_calc = re.compile(r'^[0-9+\-*/\s()]+$')
            pattern_roll = re.compile(r'^(\d+)d(\d+)([+-]\d+)?$')

            if pattern_calc.match(message.content):
                try:
                    resultado = eval(message.content)
                    await message.channel.send(f'**🧮 Resultado:**\n `{message.content} = {resultado}`')
                except Exception as e:
                    await message.channel.send(f'Erro ao calcular a expressão: {str(e)}')

            elif pattern_roll.match(message.content.lower()):
                match = pattern_roll.match(message.content.lower())
                X = int(match.group(1))
                Y = int(match.group(2))
                modifier = int(match.group(3)) if match.group(3) else 0

                resultados = []
                for _ in range(X):
                    sorteado = random.randint(1, Y)
                    resultados.append(sorteado)

                resultados_soma = sum(resultados) + modifier

                resultado_str = ", ".join(map(str, resultados))
                if modifier >= 0:
                    await message.channel.send(f'**🎲 Resultado da rolagem de {X}d{Y} + {modifier}:**\n `{resultado_str} + {modifier} = {resultados_soma}`')
                else:
                    await message.channel.send(f'**🎲 Resultado da rolagem de {X}d{Y} - {-modifier}:**\n `{resultado_str} - {-modifier} = {resultados_soma}`')

                # Reset waiting flags after using the command
                if self.waiting_for_soma:
                    self.waiting_for_soma = False
                elif self.waiting_for_dado:
                    self.waiting_for_dado = False

async def setup(bot):
    cog = Mensagens(bot)
    await bot.add_cog(cog)
