import discord
from discord.ext import commands
import os
from pymongo import MongoClient
import asyncio

# Conectar ao MongoDB
con = MongoClient('mongodb+srv:meuuserdomongodb')
db = con.get_database('BotDb')
colecao = db.get_collection('items')

class Form(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    

# -----------------------------------Seção de Adição de Itens------------------------------------- #
    
    @commands.command()
    async def additem(self, ctx: commands.Context, item: str, quantity: int = 1):
        if quantity <= 0:
            await ctx.send("A quantidade precisa ser maior que zero.")
            return
        if item == '':
            await ctx.send("Digite o nome do item.")
            return
        
        item = item.capitalize()
        
        try:
            result = colecao.find_one_and_update(
                {'_id': ctx.author.id},
                {'$inc': {item: quantity}},
                upsert=True,
                return_document=True
            )
            
            embed = discord.Embed(title='Item Adicionado!', color=discord.Color.green())
            embed.set_thumbnail(url=ctx.author.avatar)
            embed.add_field(name='Item', value=item, inline=False)
            embed.add_field(name='Quantidade', value=quantity, inline=False)
            embed.set_author(name=ctx.guild.me.name, icon_url=ctx.guild.me.avatar)
            embed.set_footer(text=f'Comando executado por: {ctx.author.name}')

            
            await ctx.reply(embed=embed)
        
        except Exception as e:
            await ctx.send(f"Ocorreu um erro: `{e}`")

# -----------------------------------Seção de Remover  Itens------------------------------------- #
    @commands.command()
    async def removeitem(self, ctx: commands.Context, item: str, quantity: int = 1):
        if quantity <= 0:
            await ctx.send("A quantidade precisa ser maior que zero.")
            return
        if item == '':
            await ctx.send("Digite o nome do item.")
            return
        
        item = item.capitalize()
        
        try:
            # Verificar a quantidade atual do item do usuário
            user_data = colecao.find_one({'_id': ctx.author.id})
            if not user_data or item not in user_data:
                await ctx.send(f"Você não possui `{item}` suficiente para remover.")
                return
            
            current_quantity = user_data.get(item, 0)
            if current_quantity < quantity:
                await ctx.send(f"❌ Você não possui `{quantity}` de `{item}` para remover.")
                return
            
            # Calcular a quantidade a ser removida (máximo até zero)
            remove_quantity = min(quantity, current_quantity)
            
            result = colecao.find_one_and_update(
                {'_id': ctx.author.id},
                {'$inc': {item: -remove_quantity}},
                return_document=True
            )
            
            embed = discord.Embed(title='Item Removido!', color=discord.Color.red())
            embed.set_thumbnail(url=ctx.author.avatar)
            embed.add_field(name='Item', value=item, inline=False)
            embed.add_field(name='Quantidade', value=quantity, inline=False)
            embed.set_author(name=ctx.guild.me.name, icon_url=ctx.guild.me.avatar)
            embed.set_footer(text=f'Comando executado por: {ctx.author.name}')
            
            await ctx.reply(embed=embed)
        
        except Exception as e:
            await ctx.send(f"Ocorreu um erro: `{e}`")

    @removeitem.error
    async def removeitem_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Ocorreu um erro de valor. Por favor não utilize espaços no nome do seu item! Ex: `Espada_Vermelha`")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Por favor utilize: **!removeitem** `nome do item` `quantidade`")
        elif isinstance(error, commands.CommandInvokeError):
            original = error.original
            if isinstance(original, ValueError):
                await ctx.send("Ocorreu um erro de valor. Por favor não utilize espaços no nome do seu item! Ex: `Espada_Vermelha`.")
            elif isinstance(original, KeyError):
                await ctx.send("Ocorreu um erro de chave. Verifique seus argumentos.")
        elif isinstance(error, commands.CommandError):
            await ctx.send(f"Ocorreu um erro: `{error}`")

# -----------------------------------Seção de Transferir de Itens------------------------------------- #

    @commands.command()
    async def transferitem(self, ctx: commands.Context, recipient: discord.Member, item: str, quantity: int = 1):
        if quantity <= 0:
            await ctx.send("A quantidade precisa ser maior que zero.")
            return
        if item == '':
            await ctx.send("Digite o nome do item.")
            return
        
        item = item.capitalize()
        
        try:
            # Verificar se o remetente possui o item suficiente
            sender_data = colecao.find_one({'_id': ctx.author.id})
            if not sender_data or item not in sender_data:
                await ctx.send(f"Você não possui `{item}` suficiente para transferir.")
                return
            
            sender_quantity = sender_data.get(item, 0)
            if sender_quantity < quantity:
                await ctx.send(f"❌ Você não possui `{quantity}` de `{item}` para transferir.")
                return
            
            # Atualizar a coleção para o remetente
            sender_update = colecao.find_one_and_update(
                {'_id': ctx.author.id},
                {'$inc': {item: -quantity}},
                return_document=True
            )
            
            # Atualizar a coleção para o destinatário
            recipient_data = colecao.find_one_and_update(
                {'_id': recipient.id},
                {'$inc': {item: quantity}},
                upsert=True,
                return_document=True
            )
            
            embed = discord.Embed(title='Item Transferido!', color=discord.Color.blue())
            embed.add_field(name='Item', value=item, inline=False)
            embed.add_field(name='Quantidade', value=quantity, inline=False)
            embed.add_field(name='Remetente', value=ctx.author.display_name, inline=False)
            embed.add_field(name='Destinatário', value=recipient.display_name, inline=False)
            embed.set_thumbnail(url=ctx.author.avatar)
            embed.set_author(name=ctx.guild.me.name, icon_url=ctx.guild.me.avatar)
            embed.set_footer(text=f'Comando executado por: {ctx.author.name}')
            
            await ctx.reply(embed=embed)
        
        except Exception as e:
            await ctx.send(f"Ocorreu um erro: `{e}`")

    @transferitem.error
    async def transferitem_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Por favor utilize: **!transferitem** `@usuário` `nome do item` `quantidade`")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Por favor utilize: **!transferitem** `@usuário` `nome do item` `quantidade`")
        elif isinstance(error, commands.CommandInvokeError):
            original = error.original
            if isinstance(original, ValueError):
                await ctx.send("Ocorreu um erro de valor. Por favor não utilize espaços no nome do seu item! Ex: `Espada_Vermelha`.")
            elif isinstance(original, KeyError):
                await ctx.send("Ocorreu um erro de chave. Verifique seus argumentos.")
        elif isinstance(error, commands.CommandError):
            await ctx.send(f"Ocorreu um erro: `{error}`")

# -----------------------------------Seção de Listar Itens------------------------------------- #

    @commands.command()
    async def list(self, ctx: commands.Context, member: discord.Member = None):
        try:
            # Use the mentioned member's ID or the author's ID if no member is mentioned
            user_id = member.id if member else ctx.author.id
            
            # Obter os dados do usuário
            user_data = colecao.find_one({'_id': user_id})
            
            if not user_data or len(user_data) == 1:
                await ctx.send("Você não possui nenhum item.")
                return
            
            user_name = member.name if member else ctx.author.name
            user_avatar = member.avatar if member else ctx.author.avatar
            
            embed = discord.Embed(
                title='📜 Lista de Itens',
                description='Aqui estão todos os seus itens:',
                color=discord.Color.blue(),
                timestamp=ctx.message.created_at
            )
            
            embed.set_author(
                name=f'Inventário de: {user_name}',
                icon_url=user_avatar
            )
            
            embed.set_footer(
                text=f'Comando executado por: {ctx.author.name}',
                icon_url=ctx.author.avatar
            )
            
            # Dicionário de itens e seus emojis correspondentes
            item_emojis = {
                'Ouro': '💰',
                'Espada': '⚔️',
                'Escudo': '🛡️',
                'Poção': '🧪',
                'Armadura': '🛡️',
                'Martelo': '🔨',
                'Prata': '🥈'
            }
            
            for item, quantity in user_data.items():
                if item == '_id':
                    continue
                
                # Substitui underscores por espaços
                item_name = item.replace('_', ' ')
                
                # Identifica o emoji apropriado
                emoji = ''
                for keyword in item_emojis:
                    if keyword.lower() in item_name.lower():
                        emoji = item_emojis[keyword]
                        break
                else:
                    emoji = '📦'
                
                embed.add_field(name=f'{emoji} {item_name}', value=quantity, inline=False)
            
            await ctx.reply(embed=embed)
        
        except Exception as e:
            await ctx.send(f"Ocorreu um erro: `{e}`")

 # -----------------------------------Seção de Remoção de Itens Direcionada------------------------------------- #

    @commands.command()
    async def removefrom(self, ctx: commands.Context, target: discord.Member, item: str, quantity: int = 1):
        admin_ids = [468470557457776641,844517813338112010]
        if ctx.author.id not in admin_ids:
            await ctx.send("❌ Hey espertinho! Você não tem permissão para usar este comando.")
            return
        if quantity <= 0:
            await ctx.send("A quantidade precisa ser maior que zero.")
            return
        if item == '':
            await ctx.send("Digite o nome do item.")
            return
        
        item = item.capitalize()
        
        try:
            # Verificar a quantidade atual do item do usuário alvo
            user_data = colecao.find_one({'_id': target.id})
            if not user_data or item not in user_data:
                await ctx.send(f"O usuário `{target.display_name}` não possui `{item}` suficiente para remover.")
                return
            
            current_quantity = user_data.get(item, 0)
            if current_quantity < quantity:
                await ctx.send(f"❌ O usuário `{target.display_name}` não possui `{quantity}` de `{item}` para remover.")
                return
            
            # Calcular a quantidade a ser removida (máximo até zero)
            remove_quantity = min(quantity, current_quantity)
            
            result = colecao.find_one_and_update(
                {'_id': target.id},
                {'$inc': {item: -remove_quantity}},
                return_document=True
            )
            
            embed = discord.Embed(title='Item Removido!', color=discord.Color.red())
            embed.set_thumbnail(url=ctx.author.avatar)
            embed.add_field(name='Item', value=item, inline=False)
            embed.add_field(name='Quantidade', value=quantity, inline=False)
            embed.add_field(name='Usuário', value=target.display_name, inline=False)
            embed.set_author(name=ctx.guild.me.name, icon_url=ctx.guild.me.avatar)
            embed.set_footer(text=f'Comando executado por: {ctx.author.name}')
            
            await ctx.reply(embed=embed)
        
        except Exception as e:
            await ctx.send(f"Ocorreu um erro: `{e}`")

# -----------------------------------Seção de Adição de Itens Direcionada------------------------------------- #


    @commands.command()
    async def addfrom(self, ctx: commands.Context, target: discord.Member, item: str, quantity: int = 1):
        admin_ids = [468470557457776641, 844517813338112010]
        if ctx.author.id not in admin_ids:
            await ctx.send("❌ Hey espertinho! Você não tem permissão para usar este comando.")
            return
        if quantity <= 0:
            await ctx.send("A quantidade precisa ser maior que zero.")
            return
        if item == '':
            await ctx.send("Digite o nome do item.")
            return
        
        item = item.capitalize()
        
        try:
            result = colecao.find_one_and_update(
                {'_id': target.id},
                {'$inc': {item: quantity}},
                upsert=True,
                return_document=True
            )
            
            embed = discord.Embed(title='Item Adicionado!', color=discord.Color.green())
            embed.set_thumbnail(url=ctx.author.avatar)
            embed.add_field(name='Item', value=item, inline=False)
            embed.add_field(name='Quantidade', value=quantity, inline=False)
            embed.add_field(name='Usuário', value=target.display_name, inline=False)
            embed.set_author(name=ctx.guild.me.name, icon_url=ctx.guild.me.avatar)
            embed.set_footer(text=f'Comando executado por: {ctx.author.name}')
            
            await ctx.reply(embed=embed)
        
        except Exception as e:
            await ctx.send(f"Ocorreu um erro: `{e}`")


            
# -----------------------------------Seção de Restartar bot------------------------------------- #

    @commands.command()
    @commands.is_owner() 
    async def restart(self, ctx):
        await ctx.send("Reiniciando o bot...")
        await self.bot.close()
        os._exit(0)

# -----------------------------------Seção de Lista de comandos------------------------------------- #

#Comando de Comandos
    @commands.command()
    async def comandos(self, ctx):
        # Construção do embed
        embed = discord.Embed(
            title='Comandos do Bot',
            description='Aqui estão os comandos disponíveis:',
            color=discord.Color.blue()
        )
        embed.set_author(name=ctx.guild.me.name, icon_url=ctx.guild.me.avatar)
        
        # Adicionando os comandos, suas descrições, sintaxe e uso
        embed.add_field(
            name='!additem',
            value='Adiciona um item ao inventário.\n'
                  'Sintaxe: `!additem <nome do item> [quantidade]`\n'
                  'Exemplo: `!additem Espada 1`\n',
            inline=False
        )
        embed.add_field(
            name='!removeitem',
            value='Remove um item do inventário.\n'
                  'Sintaxe: `!removeitem <nome do item> [quantidade]`\n'
                  'Exemplo: `!removeitem Espada 1`\n',
            inline=False
        )
        embed.add_field(
            name='!transferitem',
            value='Transfere um item para outro usuário.\n'
                  'Sintaxe: `!transferitem <@usuário> <nome do item> [quantidade]`\n'
                  'Exemplo: `!transferitem @Amigo Espada 1`\n',
            inline=False
        )
        embed.add_field(
            name='!ask',
            value='Pergunte algo ao Gemini ia PRO.\n'
                  'Sintaxe: `!ask <sua pergunta>`\n'
                  'Exemplo: `!ask Como mando um pix pro meu amigo Yuri?`\n',
            inline=False
        )
        embed.add_field(
            name='!hsoma',
            value='Habilita a calculadora automatica pra quando você cansar do Rolle.\n'
                  'Sintaxe: `!hsoma`\n',
            inline=False
        )
        embed.add_field(
            name='1 + 1',
            value='Mande qualquer calculo no chat após habilitar que ele calcula na hora!.\n'
                  'Sintaxe: `5 * 5 - (10 * 2)`\n',
            inline=False
        )

        embed.add_field(
            name='!list',
            value='Mostra todos os itens do seu inventário ou de um outro usuario.\n'
                  'Sintaxe: `!list @Amigo`\nOu `!list`\n'
                  'Exemplo: `!list`\n',
            inline=False
        )
        embed.add_field(
            name='!removefrom',
            value='Remove um item do inventário de outro usuário (apenas mestre do RPG).\n'
                  'Sintaxe: `!removefrom <@usuário> <nome do item> [quantidade]`\n'
                  'Exemplo: `!removefrom @Amigo Espada 1`\n',
            inline=False
        )
        embed.add_field(
            name='!addfrom',
            value='Adicione um item ao inventário de outro usuário (apenas mestre do RPG).\n'
                  'Sintaxe: `!addfrom <@usuário> <nome do item> [quantidade]`\n'
                  'Exemplo: `!addfrom @Amigo Espada 1`\n',
            inline=False
        )
        embed.add_field(
            name='!status',
            value='Veja e edite os status!\n'
                  'Sintaxe: `!status`\n'
                  'Exemplo: `!status @Amigo`\n',
            inline=False
        )
        embed.add_field(
            name='!comandos',
            value='Mostra todos os comandos disponíveis.\n'
                  'Sintaxe: `!comandos`\n'
                  'Exemplo: `!comandos`\n',
            inline=False
        )
        embed.add_field(
            name='!restart',
            value='Reinicia o bot (apenas o dono do bot).\n'
                  'Sintaxe: `!restart`\n'
                  'Exemplo: `!restart`\n',
            inline=False
        )

        embed.add_field(
            name='!invite',
            value='Pega o Invite do bot!\n'
                  'Sintaxe: `!invite`\n'
                  'Exemplo: `!invite`\n',
            inline=False
        )

        embed.set_footer(text=f'Comando executado por: {ctx.author.name}', icon_url=ctx.author.avatar)

        await ctx.send(embed=embed)

# --------------------------------- Equip --------------------------------- #


    @commands.command()
    async def equip(self, ctx: commands.Context, item: str = None):
        try:
            # Obtém os dados do usuário
            user_data = colecao.find_one({'_id': ctx.author.id})
            
            if not user_data:
                await ctx.send("Você não possui itens no seu inventário.")
                return

            if not item:
     
                items_list = [f"{key}: {value}" for key, value in user_data.items() if key != '_id' and key != 'Equipado' and value > 0]
                
                if items_list:
                    items_message = "\n".join(items_list)
                    await ctx.reply(f"Seus itens disponíveis são:\n```{items_message}```\nDigite o comando novamente com o nome do item que deseja equipar.")
                else:
                    await ctx.send("Você não possui itens disponíveis no seu inventário.")
                return
            
            item = item.capitalize()
            
           
            if item in user_data and user_data[item] > 0:
               
                result = colecao.find_one_and_update(
                    {'_id': ctx.author.id},
                    {'$set': {'Equipado': item}},
                    return_document=True
                )

                embed = discord.Embed(title='Item Equipado!', color=discord.Color.green())
                embed.set_thumbnail(url=ctx.author.avatar.url)
                embed.add_field(name='Item Equipado', value=item, inline=False)
                embed.set_author(name=ctx.guild.me.name, icon_url=ctx.guild.me.avatar.url)
                embed.set_footer(text=f'Comando executado por: {ctx.author.name}')

                await ctx.reply(embed=embed)
            else:
                await ctx.send(f"Você não possui o item '{item}' no seu inventário.")
        
        except Exception as e:
            await ctx.send(f"Ocorreu um erro: `{e}`")

# --------------------------------- Qual equipei --------------------------------- #
    @commands.command()
    async def equipado(self, ctx: commands.Context, item: str = None):
        try:
            user_data = colecao.find_one({'_id': ctx.author.id})
            
            if not user_data:
                await ctx.send("Você não possui itens equipados e nem no seu inventário!")
                return
            
            equipped_item = user_data.get('Equipado', 'nenhum item equipado')
            await ctx.send(f"Você está atualmente utilizando uma: {equipped_item}")
        
        except Exception as e:
            await ctx.send(f"Ocorreu um erro ao buscar os dados: {e}")
    
        





# --------------------------------- Status --------------------------------- #


    @commands.command()
    async def status(self, ctx: commands.Context, member: discord.Member = None):
        try:
           
            user_id = member.id if member else ctx.author.id

            # Obter os dados do usuário da coleção 'status'
            status_collection = db.get_collection('status')
            user_data = status_collection.find_one({'_id': user_id})

     
            if not user_data:
                initial_data = {
                    '_id': user_id,
                    'vida': 100,
                    'efeitos': ['Saudável'],
                    'status': 'Normal',
                    'level': 1
                }
                status_collection.insert_one(initial_data)
                user_data = initial_data

            user_name = member.name if member else ctx.author.name
            user_avatar = member.avatar.url if member else ctx.author.avatar.url

            embed = discord.Embed(
                title=f'Status de {user_name}',
                description='Aqui estão os status do usuário:',
                color=discord.Color.blue(),
                timestamp=ctx.message.created_at
            )

            embed.set_author(
                name=f'Status de: {user_name}',
                icon_url=user_avatar
            )

            embed.set_footer(
                text=f'Comando executado por: {ctx.author.name}',
                icon_url=ctx.author.avatar.url
            )
# -------- Emojis
            embed.add_field(name='🩸 Vida', value=f"{user_data['vida']} HP", inline=False)
            embed.add_field(name='🌀 Efeitos', value=', '.join(user_data['efeitos']), inline=False)
            embed.add_field(name='⚡ Status', value=user_data['status'], inline=False)
            embed.add_field(name='🎚️ Level', value=user_data['level'], inline=False)

      
            reactions = {
                '1️⃣': 'Vida',
                '2️⃣': 'Efeitos',
                '3️⃣': 'Status',
                '4️⃣': 'Level'
            }

            msg = await ctx.reply(embed=embed)

            for emoji in reactions.keys():
                await msg.add_reaction(emoji)

# ----- Checa emojis

            def check(reaction, user):
                return user == ctx.author and reaction.message.id == msg.id and str(reaction.emoji) in reactions

            reaction, _ = await self.bot.wait_for('reaction_add', check=check)


            response = reactions[str(reaction.emoji)]


            await msg.clear_reactions()

#-------- Verifica resposta de acordo com o coiso la
            await msg.edit(content=f"Você escolheu editar: ``{response}``. Qual informação você deseja inserir?")

         
            def check_new_message(message):
                return message.author == ctx.author and message.channel == ctx.channel

            if response == 'Vida':
                message = await self.bot.wait_for('message', check=check_new_message)
                try:
                    new_value = int(message.content)
                    user_data['vida'] = new_value
                    await ctx.send(f"Informação atualizada com sucesso em {response}. Vida foi ajustada para {user_data['vida']} HP.")
                except ValueError:
                    await ctx.send("Por favor, insira um valor numérico válido para Vida. \n Digite !status para recomeçar")
                    return
            else:
                message = await self.bot.wait_for('message', check=check_new_message)
                new_info = message.content

            
                if response == 'Efeitos':
                    user_data['efeitos'] = new_info.split(',')
                    await ctx.send(f"Informação atualizada com sucesso em {response}: {new_info}")
                elif response == 'Status':
                    user_data['status'] = new_info
                    await ctx.send(f"Informação atualizada com sucesso em {response}: {new_info}")
                elif response == 'Level':
                    try:
                        user_data['level'] = int(new_info)
                        await ctx.send(f"Informação atualizada com sucesso em {response}: {new_info}")
                    except ValueError:
                        await ctx.send("Por favor, insira um valor numérico válido para o Level.")
                        return

   
            status_collection.update_one({'_id': user_id}, {'$set': user_data})

     
            await self.status(ctx, member)

        except Exception as e:
            await ctx.send(f"Ocorreu um erro: `{e}`")








async def setup(bot):
    await bot.add_cog(Form(bot))
