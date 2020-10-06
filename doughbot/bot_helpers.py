from pyfp import Option

def has_role(user, role: str) -> bool:
    for r in user.roles:
        if r.name == role:
            return True
    
    return False

def get_role(guild, role: str) -> Option:
    for r in guild.roles:
        if r.name == role:
            return Option.some(r)
    
    return Option.empty()

def command_prefix(prefix):
    def wrapper(func):
        def inner(bot, message):
            if message.content.startswith(prefix):
                message.content = message.content[1:]
                return func(bot, message)
            else:
                async def foo():
                    pass
                
                return foo()
        
        return inner
    return wrapper

async def incorrect_permissions_response(message):
    await message.channel.send(f"{message.author.mention} you do not have permission to use this command")

def restrict_to(role):
    def wrapper(func):
        def inner(bot, message):
            if has_role(message.author, role):
                return func(bot, message)
            else:
                return incorrect_permissions_response(message)
        
        return inner
    return wrapper

def log(x):
    print(x)
    return(x)