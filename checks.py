import discord
from discord.ext.commands import check

devs = [359794541257162753,  # Max Gordon
        248914785888894976]  # Brendan Doney


async def bad_permissions(ctx, permissions):
    """
    Error for when people try and use a command that needs permissions that they don't have, send out an embed

    :param ctx: context object
    :param premissions: list (str)
    :return: None
    """
    bad_permissions_embed = discord.Embed(
        title=f"Missing permission(s): {', '.join(permissions)}",
        description="",
        color=discord.Color.from_rgb(255, 0, 0)
    )
    bad_permissions_embed.set_footer(text="Well... I guess it was worth a try?")
    await ctx.channel.send(content=None, embed=bad_permissions_embed)


def is_admin(*roles):
    """
    Checks if the person is an admin, dev, **OR** if they have any of the roles passed through *roles

    :param roles: list (str)
    :return: bool
    """

    roles = list(roles)
    if roles is None:  # adds administrator so they know what they need on the error message, it does not change the execution
        roles = ["Administer"]
    else:
        roles.append("Administrator")

    async def decorator(ctx):
        """
        Returns a bool that is True

        :param ctx:
        :return:
        """
        if not (ctx.message.author.guild_permissions.administrator or ctx.message.author.id in devs or\
        any([i.name in [roles] for i in ctx.message.author.roles])):  # are not they and admin, dev or have a role in roles
            await bad_permissions(ctx, [i for i in roles])

        return ctx.message.author.guild_permissions.administrator or ctx.message.author.id in devs or\
            any([i.name in [roles] for i in ctx.message.author.roles])  # are they and admin, dev or have a role in roles
    return check(decorator)


def is_dev():
    """
    Checks is a person is a dev (Max and Brendan), used for developer commands

    :return: bool
    """
    async def decorator(ctx):
        if ctx.message.author.id not in devs:
            await bad_permissions(ctx, ["being a dev"])
        return ctx.message.author.id in devs
    return check(decorator)

