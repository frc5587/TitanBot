from typing import List

import discord
from discord.ext.commands import check
from typing import List


DEVS = []
with open("cache/devs.txt", "r") as file:
    for dev_str in file.readlines():
        DEVS.append(int(dev_str))


async def bad_permissions(ctx, permissions: List[str]) -> None:
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


def is_admin(*roles: List[str]) -> check:
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


def is_dev() -> check:
    """
    Checks is a person is a dev (Max and Brendan), used for developer commands

    :return: if they are admin
    :rtype: check()
    """

    async def decorator(ctx):
        if ctx.message.author.id not in DEVS:
            await bad_permissions(ctx, ["being a dev"])
        return ctx.message.author.id in DEVS

    return check(decorator)
