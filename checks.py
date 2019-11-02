import discord
from discord.ext.commands import check
from typing import List, Union, Any
import functools

import extras

with open("cache/devs.txt", "r") as file:
    dev_list = file.readlines()

devs = []

for dev_str in dev_list:
    devs.append(int(dev_str))

# 359794541257162753  # Max Gordon
# 248914785888894976  # Brendan Doney


async def bad_permissions(ctx, permissions: List[str]) -> None:
    """
    Error for when people try and use a command that needs permissions that they don't have, send out an embed

    :param ctx: context object of message
    :type ctx: Object
    :param permissions: list of roles needed to run a command
    :type permissions: List[str]
    """
    bad_permissions_embed = discord.Embed(
        title=f"Missing permission(s): {', '.join(permissions)}",
        description="",
        color=discord.Color.from_rgb(255, 0, 0)
    )
    bad_permissions_embed.set_footer(text="Well... I guess it was worth a try?")
    await ctx.channel.send(content=None, embed=bad_permissions_embed)


def is_admin(*roles: List[str]) -> check:
    """
    Checks if the person is an admin, dev, **OR** if they have any of the roles passed through *roles

    :param roles: List roles that a person needs any of them to use the command
    :type roles: List[str]
    :return: whether they are allowed to use the command
    :rtype: check()
    """

    roles = list(roles)
    # adds administrator so they know what they need on the error message, it does not change the execution
    if roles is None:
        roles = ["Administer"]
    else:
        roles.append("Administrator")  # just for te visuals, does not effect function

    async def decorator(ctx) -> bool:
        """
        Returns a bool that is True if they are an admin, dev, or have a role in *roles

        :param ctx: context object for the message
        :type ctx: Object
        :return: if they are an admin, dev, or have a role in *roles
        :rtype: bool
        """
        # are not they and admin, dev or have a role in roles
        if not (ctx.message.author.guild_permissions.administrator or ctx.message.author.id in devs or
                any([role.name in roles for role in ctx.message.author.roles])):
            await bad_permissions(ctx, [i for i in roles])

        # are they and admin, dev or have a role in roles
        return ctx.message.author.guild_permissions.administrator or ctx.message.author.id in devs or\
            any([role.name in roles for role in ctx.message.author.roles])
    return check(decorator)


def is_dev() -> check:
    """
    Checks is a person is a dev (Max and Brendan), used for developer commands

    :return: if they are admin
    :rtype: check()
    """
    async def decorator(ctx):
        if ctx.message.author.id not in devs:
            await bad_permissions(ctx, ["being a dev"])
        return ctx.message.author.id in devs
    return check(decorator)

# Union[str, int, float
class GetArgs:
    def __init__(self, num_args, arg_type):
        print("***")
        self.num_args = num_args
        self.arg_type = arg_type

    def __call__(self, func):
        print("******")
        async def wrapper(ctx, *args, **kwargs):
            print("**************************")
            return await func(ctx, None)
        return wrapper




# def get_args(func, numb_args:int, arg_type: List[type]):
#
#     @functools.wraps(func)
#     def decorator(ctx):
#         print("test")
#         func(ctx)
#     return decorator

#
# def get_args(num_args: int, arg_type: List[Any]):
#     def get_func(func):
#         @functools.wraps(func)
#         async def wrapper(ctx):
#             return await func(ctx, [])
#
#         return wrapper
#     return get_func
#
#     open_str = False
#
#     arg_list = []
#     sub_arg_list = []
#
#     for word in ctx.message.content.split():
#         if word.startswith("\"") or word.endwith("\""):
#             if open_str:
#                 open_str = False
#                 arg_list.append(" ".join(sub_arg_list))
#                 sub_arg_list = []
#             if not open_str:
#                 open_str = True
#                 sub_arg_list.append(word[1:])
#         elif open_str:
#             sub_arg_list.append(word)
#         else:
#             arg_list.append(word)
#
#     if open_str:
#         await
#         extras.command_error(ctx, '707', "Arg was never closed with \"")
#         return None
#     await
#     func(ctx)
#
#     print(arg_list)








































        # print("3")
        # open_str = False
        #
        # arg_list = []
        # sub_arg_list = []
        #
        # for word in ctx.message.content.split():
        #     if word.startswith("\"") or word.endwith("\""):
        #         if open_str:
        #             open_str = False
        #             arg_list.append(" ".join(sub_arg_list))
        #             sub_arg_list = []
        #         if not open_str:
        #             open_str = True
        #             sub_arg_list.append(word[1:])
        #     elif open_str:
        #         sub_arg_list.append(word)
        #     else:
        #         arg_list.append(word)
        #
        # if open_str:
        #     await extras.command_error(ctx, '707', "Arg was never closed with \"")
        #     return None
        # print(arg_list + "\n" + sub_arg_list)
        # await ctx.channel.send(arg_list + "\n" + sub_arg_list)
        # print(arg_list)
