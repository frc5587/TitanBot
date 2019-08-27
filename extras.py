import discord


class Commands:
    """
    This is just an easy way to keep track of commands and it generates the string used in the help function
    """
    command_list = []
    command_count = 0
    command_str = ""
    command_list_name = []

    def __init__(self, name, description, syntax, permissions):
        """
        Creates the command object (duh) and generates the comma separated string of commands used by the help function

        :param name: str; name of command
        :param description: str; description of what the command does
        :param syntax: str; syntax example of how the command is used
        """
        self.name = name
        self.description = description
        self.syntax = syntax
        self.permissions = permissions
        Commands.command_list.append(self)
        Commands.command_list_name.append(self.name)
        Commands.command_count += 1
        Commands.command_str = ", ".join(Commands.command_list_name)


async def command_error(ctx, error, reason, missing_args=None):
    """
    This send out an error message (embed) according to the error codes below

    404: Command doesn't exist
    505: Missing args
    606: Complexity error
    707: Incorrect args

    :param ctx: context object
    :param error: str
    :param reason: str
    :param missing_args: str
    :return: None
    """
    error_codes = {
        '404': f'The command {ctx.message.content[1:]} is not found, check -help if that command even exists, if it '
            f'does then please notify Johnny Wobble#1085 of this',
        '505': f'You are missing arg(s): {missing_args}, without this arg(s) the function will not work, refer to -help'
            f' if this error keeps popping up',
        '606': 'The expression/equation that you imputed could not be solved due to a complexity error',
        '707': 'Check your args, one or more may not be correct'}
    error_embed = discord.Embed(
        title=f'Error {error}: {reason}',
        description=error_codes.get(error),
        color=discord.Color.from_rgb(255, 0, 0)
    )
    await ctx.channel.send(content=None, embed=error_embed)


async def helper(ctx):
    """
    Sends the help embed, can also give specific help of a given command

    :param ctx: command object
    :return: None
    """
    if len(ctx.message.content.split()) > 1:
        help_command = ctx.message.content.split()[1].lower()
        for i in Commands.command_list:
            if help_command == i.name.lower():
                help_command_embed = discord.Embed(
                    title=i.name,
                    description=i.description,
                    color=discord.Color.from_rgb(67, 0, 255)
                )
                help_command_embed.add_field(name="Syntax", value=i.syntax)
                help_command_embed.add_field(name="Permissions needed", value=f"You need any one of these to use the command\n{i.permissions}")
                help_command_embed.set_footer(text='O: means that the arg is optional')
                await ctx.channel.send(content=None, embed=help_command_embed)
                return
        error_embed = discord.Embed(
            title='Error 404: command not found',
            description=f'The command {ctx.message.content.split()[1]} is not found, check -help if that command exist, '
            f'if it does then please notify Johnny Wobble#1085 of this',
            color=discord.Color.from_rgb(255, 0, 0)
        )
        await ctx.channel.send(content=None, embed=error_embed)
    else:
        embed = discord.Embed(
            title='Help',
            description='- is the prefix,\ngeneral format: -<command>  <O: conditional statement(s)>\n',
            color=discord.Color.from_rgb(67, 0, 255)
        )
        embed.set_footer(text='O: means that the arg is optional')
        embed.add_field(name="list of commands", value=Commands.command_str, inline=True)
        await ctx.channel.send(content=None, embed=embed)