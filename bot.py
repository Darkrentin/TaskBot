import discord
from discord.ext import commands
from discord import app_commands
import json
import time
from datetime import datetime

path = "data.json"

def get_json_data(path):
    with open(path,"r",encoding="utf-8") as f:
        data = json.load(f)
    return data
def save_json_data(data,path):
    with open(path,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=4)
def create_task(data,name,priority,responsable,state,deadline,description):
    data["last_id"]+=1
    date = datetime.now().strftime("%d/%m/%Y")
    ldata={'name':name,'priority':priority,'responsable':responsable,'state':state,'date':date,'deadline':deadline,'description':description}
    data[data['last_id']]=ldata
    save_json_data(data,path)
def suppr_task(data,id):
    del data[str(id)]
    save_json_data(data,path)
def show():
    data = get_json_data(path)
    afaire=""
    encours=""
    terminer=""
    for key in data:
        if key!="last_id" and key!="setup_id":
            d=data[key]
            mes=f"> [ **{key}** ]| **{d['name']}** | *Priorité:* **{d['priority']}** | *Atribuée à:* **{d['responsable']}**\n"
            if d["state"]=="A faire":
                afaire+=mes
            elif d["state"]=="En cours":
                encours+=mes
            else:
                terminer+=mes
    embedd=discord.Embed(
        title = "Liste des tâches",
        description = "## - Tâches à faire:\n"+afaire+"## - Tâches en cours:\n"+encours+"## - Tâches terminées:\n"+terminer,
        color=discord.Color.dark_blue()
    )
    return embedd


data = get_json_data(path)

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())

    async def setup_hook(self) -> None:
        await self.tree.sync()

    async def on_ready(self):
        print("je suis en ligne")

bot = MyBot()

async def prio_autocomplete(
    interaction: discord.Interaction,
    current: str,
):
    priority = ['Optionnel','Bas', 'Moyen', 'Haut', 'Urgent!']
    return [
        app_commands.Choice(name=prio, value=prio)
        for prio in priority if current.lower() in prio.lower()
    ]
async def state_autocomplete(
    interaction: discord.Interaction,
    current: str,
):
    state = ['A faire','En cours','Terminée']
    return [
        app_commands.Choice(name=st, value=st)
        for st in state if current.lower() in st.lower()
    ]
async def name_autocomplete(
    interaction: discord.Interaction,
    current: str,
):
    state = ['name','responsable','deadline','description']
    return [
        app_commands.Choice(name=st, value=st)
        for st in state if current.lower() in st.lower()
    ]

@bot.hybrid_command(name="add_task")
@app_commands.autocomplete(priority=prio_autocomplete)
async def hadd(ctx : commands.Context,name,priority,responsable="Non attribué",deadline="Non défini",description="") -> discord.Message:
    data = get_json_data(path)
    state="A faire"
    create_task(data,name,priority,responsable,state,deadline,description)
    #-----------
    id = data["setup_id"]
    try:
        message = await ctx.fetch_message(id)
        await message.edit(embed=show())
        #-----------
        return await ctx.send(f"Task **{name}** ajoutée !",ephemeral=True)
    except:
        return await ctx.send("[ERROR]: il se peut que vous ne soyer pas dans le bon channel",ephemeral=True)

@bot.hybrid_command(name="suppr_task")
async def hsuppr(ctx : commands.Context,id) -> discord.Message:
    data=get_json_data(path)
    try:
        suppr_task(data,id)
        #-----------
        data = get_json_data(path)
        ID = data["setup_id"]
        try:
            if ID==-1:
                pass
            else:
                message = await ctx.fetch_message(ID)
                await message.edit(embed=show())
            #-----------
            return await ctx.send(f"Task **{id}** supprimée !",ephemeral=True)
        except:
            return await ctx.send("[ERROR]: il se peut que vous ne soyer pas dans le bon channel",ephemeral=True)
    except:
        return await ctx.send("[ERROR]: Cette task n'existe pas",ephemeral=True)

@bot.hybrid_command(name="modif")
@app_commands.autocomplete(name=name_autocomplete)
async def modif(ctx: commands.Context,id,name,value) -> discord.Message:
    data = get_json_data(path)
    try:
        data[id][name]=value
        save_json_data(data,path)
        data=get_json_data(path)
        ID = data["setup_id"]
        if ID==-1:
            pass
        else:
            message = await ctx.fetch_message(ID)
            await message.edit(embed=show())
        return await ctx.send("Modification effectuée !",ephemeral=True)
    except:
        return await ctx.send("[ERROR]: Aucun message ne correspond à cette ID",ephemeral=True)

@bot.hybrid_command(name="set_state")
@app_commands.autocomplete(value=state_autocomplete)
async def modifstate(ctx: commands.Context,id,value) -> discord.Message:
    data = get_json_data(path)
    try:
        data[id]["state"]=value
        save_json_data(data,path)
        data=get_json_data(path)
        ID = data["setup_id"]
        if ID==-1:
            pass
        else:
            message = await ctx.fetch_message(ID)
            await message.edit(embed=show())
        return await ctx.send("Modification effectuée !",ephemeral=True)
    except:
        return await ctx.send("[ERROR]: Aucun message ne correspond à cette ID",ephemeral=True)
@bot.hybrid_command(name="set_priority")
@app_commands.autocomplete(value=prio_autocomplete)
async def modifstate(ctx: commands.Context,id,value) -> discord.Message:
    data = get_json_data(path)
    try:
        data[id]["priority"]=value
        save_json_data(data,path)
        data=get_json_data(path)
        ID = data["setup_id"]
        if ID==-1:
            pass
        else:
            message = await ctx.fetch_message(ID)
            await message.edit(embed=show())
        return await ctx.send("Modification effectuée !",ephemeral=True)
    except:
        return await ctx.send("[ERROR]: Aucun message ne correspond à cette ID",ephemeral=True)

@bot.hybrid_command(name="task_help")
async def help(ctx: commands.Context):
    mes=""
    with open("help.txt","r") as f:
        mes=f.read()
    embedd=discord.Embed(
        title="Liste des commandes:",
        description=mes,
        color=discord.Color.dark_blue()
    )
    return await ctx.send(embed=embedd,ephemeral=True)

@bot.hybrid_command(name="update")
async def update(ctx: commands.Context):
    data = get_json_data(path)
    id = data["setup_id"]
    if id==-1:
        pass
    else:
        message = await ctx.fetch_message(id)
        await message.edit(embed=show())
    return await ctx.send("updated !",ephemeral=True)


@bot.hybrid_command(name="show_task")
async def showt(ctx: commands.Context,id):
    try:
        data=get_json_data(path)
        d=data[str(id)]
        mes=""
        for key in d:
            if key!="name":
                mes+=f"- **{key}**: {d[key]}\n"
        embedd=discord.Embed(
            title=f"{d['name']}",
            description=mes,
            color=discord.Color.dark_blue()
        )
        return await ctx.send(embed=embedd,ephemeral=True)
    except:
        return await ctx.send("[ERROR]: Aucune Task ne correspond à cette ID",ephemeral=True)

@bot.command()
async def setup(ctx: commands.Context) -> discord.Message:
    mes=show()
    message=await ctx.send(embed=mes)
    data["setup_id"]=message.id
    save_json_data(data,path)
    await ctx.message.delete()
    return message



if __name__ == "__main__":
    bot.run("TOKEN")


