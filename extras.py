import discord


class Commands:
    """
    This is just an easy way to keep track of commands and it generates the string used in the help
    function
    """
    command_list = []
    command_count = 0
    command_str = ""
    command_list_name = []

    def __init__(self, name: str, description: str, syntax: str, permissions: str):
        """
        Creates the command object (duh) and generates the comma separated string of commands used
        by the help function to list commands

        :param name: name of command
        :type name: str
        :param description: description of what the command does
        :type description: str
        :param syntax: syntax example of how the command is used
        :type syntax: str
        :param permissions: comma separated list of roles/permissions needed to use the command
        :type permissions: str
        """
        self.name = name
        self.description = description
        self.syntax = syntax
        self.permissions = permissions
        Commands.command_list.append(self)
        Commands.command_list_name.append(self.name)
        Commands.command_count += 1
        Commands.command_str = ", ".join(Commands.command_list_name)


async def command_error(ctx,
                        error_code: str,
                        reason: str,
                        missing_args: str = None,
                        command: str = None) -> None:
    """
    This send out an error message (embed) according to the error codes below

    404: Command doesn't exist
    505: Missing args
    606: Complexity error
    707: Incorrect args

    :param ctx: context object of message
    :type ctx: Object
    :param error_code: error type
    :type error_code: str
    :param reason: Direct reason of error
    :type reason: str
    :param missing_args: comma separated list
    :type missing_args: List[str]
    :param command: the unfound command
    :type command: str
    """
    error_codes = {
        '404': f'The command `{command}` is not found, check -help if that command even exists, if '
               f'it does then please notify Johnny Wobble#1085 or Brendan Doney#2365 of this',
        '505': f'You are missing arg(s): {missing_args}, without this arg(s) the function will not '
               f'work, refer to -help if this error keeps popping up',
        '606': 'The expression/equation that you imputed could not be solved due to a complexity '
               'error',
        '707': 'Check your args, one or more may not be correct',
        '808': 'Incorrect number of args'}
    error_embed = discord.Embed(
        title=f'Error {error_code}: {reason}',
        description=error_codes.get(error_code),
        color=discord.Color.from_rgb(255, 0, 0)
    )
    await ctx.channel.send(content=None, embed=error_embed)


async def specific_help(ctx, help_command: str) -> None:
    """
    This will retrieve and send data about a specific command when it is askes, e.g. `-help math`,
    then it will give all of the helpful things about the math function: syntax, permissions needed,
    name

    :param ctx: context object for the message
    :type ctx: Object
    :param help_command: the command to get help for
    :type help_command: str
    """
    for command in Commands.command_list:
        if help_command == command.name.lower():
            help_command_embed = discord.Embed(
                title=command.name,
                description=command.description,
                color=discord.Color.from_rgb(67, 0, 255))

            help_command_embed.add_field(name="Syntax", value=command.syntax)
            help_command_embed.add_field(name="Permissions needed",
                                         value=command.permissions)
            help_command_embed.set_footer(text='O: means that the arg is optional')
            await ctx.channel.send(content=None, embed=help_command_embed)
            return

    await command_error(ctx, '404', 'Command not found', command=help_command)


async def helper(ctx, user_arg):
    """
    Sends the help embed, can also give specific help of a given command

    :param ctx: context object of the message
    :type ctx: Object
    :param user_arg: the args that the user passes through
    :type user_arg: List[str]
    """
    if len(user_arg) > 0:
        await specific_help(ctx, user_arg[0].lower())
    else:
        embed = discord.Embed(
            title='Help',
            description='prefix: -\ngeneral format: -<command>  <O: additional argument(s)>\n',
            color=discord.Color.from_rgb(67, 0, 255)
        )
        embed.set_footer(text='O: means that the arg is optional')
        embed.add_field(name="Commands", value=Commands.command_str, inline=True)
        await ctx.channel.send(content=None, embed=embed)
