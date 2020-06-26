from typing import List, Union, Type, Callable, Tuple, Any
from pathlib import Path
import os
import json

import discord


class Colors:
    white = discord.Color.from_rgb(252, 252, 252)
    purple = discord.Color.from_rgb(67, 0, 255)
    red = discord.Color.from_rgb(255, 0, 0)
    green = discord.Color.from_rgb(9, 227, 100)


class JSONConfig:
    def __init__(self, path: Union[Path, str] = '.', file: Union[Path, str] = "config.json"):
        self.path = Path('.') / path
        self.file = self.path / file
        self.dict_, self.last_read = None, None
        self.dict_ = self.refresh()
        self.last_read = self.dict_.copy()
        self.written = False

    def write(self):
        with open(self.file, 'w') as f:
            json.dump(self.dict_, f)
        self.dict_, self.last_read = None, None
        self.written = True
        self.refresh()

    def has_written(self):
        written = self.written
        self.written = False
        return written

    def refresh(self) -> dict:
        if not self.edited():
            with open(self.file, 'r') as f:
                self.dict_ = json.load(f)
                self.last_read = self.dict_.copy()
                return self.dict_
        else:
            raise RuntimeError("Contains local changes that have not been written yet")

    def edited(self) -> bool:
        return self.last_read != self.dict_

    def update(self, item):
        return self.dict_.update(item)

    def __getitem__(self, item):
        return self.dict_.__getitem__(item)

    def __setitem__(self, key, value):
        return self.dict_.__setitem__(key, value)

    def __repr__(self):
        return self.dict_.__repr__()


class Command:
    """
    This is just an easy way to keep track of commands and it generates the string used in the help
    function
    """

    def __init__(self, name: str, description: str, syntax: str, min_args: int = 0,
                 max_args: int = 100, dm_only: bool = False,
                 dev_command: bool = False):
        """
        Creates the command object (duh) and generates the comma separated string of commands used
        by the help function to list commands

        :param name: name of command
        :type name: str
        :param description: description of what the command does
        :type description: str
        :param syntax: syntax example of how the command is used
        :type syntax: str
        :param dev_command: whether the command is for devs only
        :type dev_command: bool
        """
        self.name = name
        self.description = description
        self.syntax = syntax
        self.dev_command = dev_command
        self.min_args = min_args
        self.max_args = max_args
        self.dm_only = dm_only


class CommandGroup:
    def __init__(self, bot):
        self._commands: List[Command] = []
        self.bot = bot

    def new_command(self, name: str, description: str, syntax: str, min_args: int = 0,
                    max_args: int = 100, dm_only: bool = False,
                    dev_command: bool = False, frc_leadership_command: bool = False,
                    types: Union[List[Type], Type] = str):
        """
        Decorator to enforce various policies on commands and keep track of all commands for the
        help/lookup functions. This enforce DM commands, arg counts/limits, dev commands, and arg
        typing. This also holds the names, descriptions, and syntax examples for commands.

        :param name: name of commands
        :type name: str
        :param description: description of purpose for the command, NOT syntax
        :type description: str
        :param syntax: simple example of how to use command
        :type syntax: str
        :param min_args: min args the user can pass in
        :type min_args: int
        :param max_args: max args the user can pass in
        :type max_args: int
        :param dm_only: whether the command should only be used in DMs
        :type dm_only: bool
        :param dev_command: whether only devs can use the command
        :type dev_command: bool
        :param types: the types that the decorator should try and turn the args to, these should
        only really be `int`, `float`, and `str` (maybe `bool` too)
        :type types: Union[List[Type], Type]
        :return: the decorated function
        :rtype: Callable
        """
        self._commands.append(
            Command(name, description, syntax, min_args, max_args, dm_only, dev_command))

        def wrapper(func: Callable) -> Callable:
            """
            Wraps `decorator()` and because `decorator()` is coroutine and needs another wrapper to
            work properly as a decorator

            :param func: function being decorated
            :type func: Callable
            :return: the decorated function
            :rtype: Callable
            """

            @self.bot.command(name=name)
            async def decorator(ctx):
                """
                Decorates all of the discord commands. It will check and enforce if its a DM, it
                will also count and enforce arg limits, and finally it will try and convert the args
                to any types specified with `types`

                :param ctx: Context object of message
                :type ctx: discord.ext.commands.Context
                :return: output of `func`
                :rtype: Any
                """
                try:
                    user_args = arg_parser(ctx.message.content.split()[1:], types)
                except ValueError:
                    return await command_error(ctx, '707')

                if frc_leadership_command and isinstance(ctx.author, discord.User):
                    return await command_error(ctx, '303', missing_permissions="FRC Leadership",
                                               extra="This only works on a server channel, not in "
                                                     "DMs")
                
                if frc_leadership_command and "FRC Leadership" not in [str(r) for r in ctx.author.roles]:
                    return await command_error(ctx, '303', missing_permissions="FRC Leadership")

                if dm_only and not isinstance(ctx.channel, discord.DMChannel):
                    return await command_error(ctx, '909')

                if dev_command and ctx.message.author.id not in SYSTEM_CONFIG["devs"].values():
                    return await command_error(ctx, '303', missing_permissions="dev")

                if min_args > len(user_args) or max_args < len(user_args):
                    return await command_error(ctx, '808',
                                               num_args=(min_args, max_args, len(user_args)))

                return await func(ctx, user_args)

            return decorator

        return wrapper

    @property
    def command_str(self) -> str:
        return ', '.join([c.name for c in self.commands])

    @property
    def commands(self) -> List[Command]:
        return sorted(self._commands, key=lambda x: x.name)


def arg_parser(args: List[str], types: Union[List[Type], Type]) -> List[Any]:
    if not isinstance(types, list):
        types = [types]
    while len(types) < len(args):
        types.append(types[-1])

    new_args = []
    for typ, arg in list(zip(types, args)):
        new_args.append(typ(arg))

    return new_args


async def command_error(ctx,
                        error_code: str,
                        extra: str = '',
                        missing_args: str = None,
                        command: str = None,
                        num_args: Tuple[int, int, int] = (0, 0, 1),
                        missing_permissions: str = 'dev'):
    """
    This send out an error message (embed) according to the error codes below

    404: Command doesn't exist
    505: Missing args
    606: Complexity error
    707: Incorrect args
    808: Wrong number of args
    909: DM command

    :param ctx: context object of message
    :type ctx: Object
    :param error_code: error type
    :type error_code: str
    :param extra: extra info about the problem
    :type extra: str
    :param missing_args: comma separated list
    :type missing_args: List[str]
    :param command: the unfound command
    :type command: str
    :param num_args: (min args #, max args #, received args #)
    :type num_args: Tuple[int, int, int]
    :param missing_permissions: comma separated permissions that are missing
    :type missing_permissions: str
    """
    extra_info = {
        '303': f"You are missing permission(s) {missing_permissions}",
        '404': f'The command `{command}` is not found, check -help if that command even exists, if '
               f'it does then please notify Johnny Wobble#1085 of this',
        '505': f'You are missing arg(s): {missing_args}, without this arg(s) the function will not '
               f'work, refer to -help if this error keeps popping up',
        '606': 'The expression/equation that you imputed could not be solved due to a complexity '
               'error',
        '707': 'Check your args, one or more may not be correct',
        '808': f'Incorrect number of args, expected between {num_args[0]} and {num_args[1]} args,'
               f' got {num_args[2]}',
        '909': 'This command only works in DMs'}
    error_codes = {
        '303': "Missing Permissions",
        '404': "Command Not Found",
        '505': "Missing arg",
        '606': "Complexity Error",
        '707': "Incorrect or Bad Args",
        '808': "Incorrect Number of Args",
        '909': "DM Command"
    }
    error_embed = discord.Embed(
        title=f'Error {error_code}: {error_codes.get(error_code)}',
        description=extra_info.get(error_code) + "\n" + extra,
        color=Colors.red
    )
    await ctx.channel.send(content=None, embed=error_embed)


async def specific_help(ctx, help_command: str, command_group: CommandGroup) -> None:
    """
    This will retrieve and send data about a specific command when it is asks, e.g. `-help math`,
    then it will give all of the helpful things about the math function: syntax, permissions needed,
    name

    :param ctx: context object for the message
    :type ctx: Context Object
    :param help_command: the command to get help for
    :type help_command: str
    :param command_group: The group of commands
    :type command_group: CommandGroup
    """
    for command in command_group.commands:
        if help_command == command.name.lower():
            help_command_embed = discord.Embed(
                title=command.name,
                description=command.description,
                color=Colors.purple
            )

            help_command_embed.add_field(name="Syntax", value=command.syntax)
            help_command_embed.add_field(name="Args", value=f"Minimum args: {command.min_args}"
                                                            f"\nMaximum args: {command.max_args}")
            help_command_embed.add_field(name="DM only", value=str(command.dm_only))
            help_command_embed.add_field(name="Developer Command",
                                         value=str(command.dev_command))
            help_command_embed.set_footer(text='O: means that the arg is optional')
            await ctx.channel.send(content=None, embed=help_command_embed)
            return

    await command_error(ctx, '404', command=help_command)


async def helper(ctx, user_arg, command_group: CommandGroup):
    """
    Sends the help embed, can also give specific help of a given command

    :param ctx: context object of the message
    :type ctx: Object
    :param user_arg: the args that the user passes through
    :type user_arg: List[str]
    :param command_group: The group of all commands
    :type command_group: CommandGroup
    """
    if len(user_arg) > 0:
        await specific_help(ctx, user_arg[0].lower(), command_group)
    else:
        embed = discord.Embed(
            title='Help',
            description='prefix: -\ngeneral format: -<command>  <O: additional argument(s)>\n'
                        '`O:` means that the arg is optional and `...` means the arg can be '
                        'repeated infinite times',
            color=Colors.purple
        )
        embed.set_footer(text='')
        embed.add_field(name="Command", value=command_group.command_str, inline=True)
        await ctx.channel.send(content=None, embed=embed)


class Restart(SystemExit):
    pass


class Shutdown(SystemExit):
    pass


def is_number(string: str) -> bool:
    try:
        eval(string)
        return True
    except SyntaxError:
        return False


def make_cache():
    """
    Creates the cache/ folder and the polls/ folder that reside within it, if they don't already
    exist.
    """
    if not os.path.exists('cache/polls'):
        try:
            os.mkdir('cache')
        except FileExistsError:
            pass
        try:
            os.mkdir('cache/polls')
        except FileExistsError:
            pass
    open("cache/discord.log", 'a+').close()


SYSTEM_CONFIG = JSONConfig()
