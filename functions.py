""" @bot.command()
@has_permissions(Administrator=True)
async def isAdmin():

@isAdmin.error
async def admin_error(error, ctx):
       await ctx.send("You don't have permission to do that!") """