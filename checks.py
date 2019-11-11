import discord
import json
import extras
from discord.ext.commands import check
from typing import List, Type, Callable, Union


DEVS = []


def load_devs_config():
    """
    It parses config.json for the list of devs, then it updates the global constant DEVS with the list of IDs
    """
    global DEVS
    with open("config.json", "a+") as file:
        file.seek(0)  # set pointer to the beginning
        devs_dict = json.load(file)
        dev_list = devs_dict.get("devs")
        DEVS = dev_list if dev_list is not None else []


async def bad_permissions(ctx, permissions: List[str]):
    """
    Sends the error embed for when people try and use a command that needs permissions
    they don't have.

    :param ctx: context object of message
    :type ctx: Object
    :param permissions: list of roles needed to run a command
    :type permissions: List[str]
    """
    bad_permissions_embed = discord.Embed(
        title=f"Missing permission(s): {', '.join(permissions)}",
        description="",
        color=discord.Color.from_rgb(255, 0, 0))
    bad_permissions_embed.set_footer(text="Well... I guess it was worth a try?")
    await ctx.channel.send(content=None, embed=bad_permissions_embed)


def is_admin(*roles: List[str]) -> Callable:
    """
    Checks if the person is an admin, dev, **OR** if they have any of the roles passed
    through *roles.

    :param roles: List roles that a person needs any of them to use the command
    :type roles: List[str]
    :return: whether they are allowed to use the command
    :rtype: check()
    """

    roles = list(roles)
    # add administrator to the list of required roles so it is seen in error embed
    if roles is None:
        roles = ["Administer"]
    else:
        roles.append(
            "Administrator")  # just for te visuals, does not effect function

    async def decorator(ctx) -> bool:
        """
        Returns a bool that is True if they are an admin, dev, or have a role in *roles

        :param ctx: context object for the message
        :type ctx: Object
        :return: if they are an admin, dev, or have a role in *roles
        :rtype: bool
        """
        # are not they and admin, dev or have a role in roles
        if not (ctx.message.author.guild_permissions.administrator or
                ctx.message.author.id in DEVS or
                any([role.name in roles for role in ctx.message.author.roles])):
            await bad_permissions(ctx, [i for i in roles])

        # are they and admin, dev or have a role in roles
        return ctx.message.author.guild_permissions.administrator or ctx.message.author.id in DEVS \
            or any([role.name in roles for role in ctx.message.author.roles])

    return check(decorator)


def is_dev() -> Callable:
    """
    Checks is a person is a dev (Max and Brendan, or any else in cache/devs.txt), used for developer commands

    :return: if they are admin
    :rtype: check()
    """

    async def decorator(ctx):
        if ctx.message.author.id not in DEVS:
            await bad_permissions(ctx, ["being a dev"])
        return ctx.message.author.id in DEVS

    return check(decorator)


async def get_arg_list(message: str, ctx) -> List[str]:
    """
    Splits the other args that the user sends with tho command, e.g. if the send `-test 1 2 "foo bar"` it will return
    [1, 2, "foo bar"], because it looks for quotation marks to signify an arg that has spaces in it

    :param message: the message that the user sends
    :type message: str
    :param ctx: context for the message
    :type ctx: Object
    :return: the list of all of the args
    :rtype: List[Any]
    """
    open_str = False

    arg_list = []
    sub_arg_list = []

    for word in message.split():
        if word.startswith("\"") or word.endswith("\""):  # looks for " to signify a longer arg

            if open_str:  # if the long arg is currently "open"
                open_str = False
                arg_list.append(" ".join(sub_arg_list))
                sub_arg_list = []
            if not open_str:  # if the long arg is not open
                open_str = True
                sub_arg_list.append(word[1:]
                                    )
        elif open_str:
            sub_arg_list.append(word)
        else:
            arg_list.append(word)

    if open_str:  # User didn't send a second "
        await extras.command_error(ctx, '707', "Arg was never closed with \"")
        raise ValueError
    arg_list.pop(0)  # pops the command (e.g. `-test`) from the list
    return arg_list


async def check_args(arg_list: List[str],
                     min_args: int,
                     max_args: int,
                     types: Union[List[Type], Type],
                     ctx) -> List[Union[int, float, str]]:
    """
    This first checks to see if there are too many or too little args, in that case it sends out an error message. Then
    it iterates through all of the args checking that they are the right type

    str: includes, all
    float: includes, int and float
    int: includes, int

    :param arg_list: list of the user inputed args
    :type arg_list: List[str]
    :param min_args: minimum amount of args
    :type min_args: int
    :param max_args: maximum amount of args
    :type max_args: int
    :param types: list of the types of args expected
    :type types: List[Type]
    :param ctx: context object for message
    :type ctx: Object
    :return: the list of parsed args
    :rtype: List[Union[int, str, float]]
    """
    if not (min_args <= len(arg_list) <= max_args):
        await extras.command_error(ctx, '808',
                                   f"Expected between {min_args} and {max_args} args, got {len(arg_list)} args ")
        raise ValueError
    for num, arg in enumerate(arg_list):

        if not isinstance(types, list):  # if there is only one type for all of
            arg_type = types             # the args to be, then it just make all of checks do that

        else:
            arg_type = types[num]

        if isinstance(arg_type, str):  # everything is a string, so if it wants a str, then it can just continue
            continue

        elif arg.isdigit():  # parse arg, if it can
            arg_list[num] = eval(arg)
            arg = eval(arg)

        if isinstance(arg_type, float):  # ints are included in floats
            if not (isinstance(arg, float) or isinstance(arg, int)):
                await extras.command_error(ctx, '707',
                                           f"Expected arg number {num} to be float or int, got {type(arg)}")
                raise ValueError
            continue

        elif isinstance(arg_type, int):
            if not (isinstance(arg, int)):
                await extras.command_error(ctx, '707',
                                           f"Expected arg number {num} to be int, got {type(arg)}")
                raise ValueError
            continue

    return arg_list


def get_args_in_message(min_args: int = 0,
                        max_args: int = 0,
                        arg_types: Union[List[Type], Type] = None) -> Callable:
    """
    This should decorate every command function on the bot. It will parse the user's message, then if the args that it
    finds don't match up with the expect types, or there are too few/many, it will send an error message saying so,
    otherwise, it will pass the list of args into the command function. For the types, putting str, basically means the
    type doesn't matter, and any time a float is asked for, an int will be accepted in the arg as well. If just one type
    is passed into `arg_types`, then it will assum all of the args are supposed to be that type.

    :param min_args: minimum amount of args allowed
    :type min_args: int
    :param max_args: maximum amount of args allowed
    :type max_args: int
    :param arg_types: A list of the classes that the arg should be, really only, int, float, or str
    :type arg_types: Union[List[Type], Type]
    :return: This is a decorator so it returns the function
    :rtype: Callable
    """
    def get_func(func: Callable) -> Callable:
        async def wrapper(ctx) -> Union[discord.Message, None]:
            try:
                arg_list = await get_arg_list(ctx.message.content, ctx)

                arg_list = await check_args(arg_list, min_args, max_args, arg_types, ctx)

                return await func(ctx, arg_list)
            except ValueError:
                return None
        return wrapper
    return get_func
