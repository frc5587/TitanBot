import discord
from discord.ext.commands import check

devs = ['Johnny Wobble#1085', 'Brendan Doney#2365']


async def bad_premissions(ctx, premissions):
    """
    Error for when people try and use a command that needs permissions that they don't have, send out an embed

    :param ctx: context object
    :param premissions: list (str)
    :return: None
    """
    bad_premissions_embed = discord.Embed(
        title=f"Missing permission(s): {', '.join(premissions)}",
        description="",
        color=discord.Color.from_rgb(255, 0, 0)
    )
    bad_premissions_embed.set_footer(text="Well... I guess it was worth a try?")
    await ctx.channel.send(content=None, embed=bad_premissions_embed)


def is_admin(*roles):
    """
    Checks if the person is an admin **OR** if they have any of the roles passed through *roles

    :param roles: list (str)
    :return: bool
    """
    roles = list(roles)
    if roles is None:
        roles = ["administer"]
    else:
        roles.append("administer")

    async def decorator(ctx):
        """
        Returns a bool that is True

        :param ctx:
        :return:
        """
        if not ctx.message.author.guild_permissions.administrator:
            await bad_premissions(ctx, [i for i in roles])
        return ctx.message.author.guild_permissions.administrator or str(ctx.message.author) in devs or\
            any([i.name in [roles] for i in ctx.message.author.roles])
    return check(decorator)


def is_dev():
    """
    Checks is a person is a dev (Max and Brendan), used for developer commands

    :return: bool
    """
    async def decorator(ctx):
        if str(ctx.message.author) not in devs:
            await bad_premissions(ctx, ["being a dev"])
        return str(ctx.message.author) in devs
    return check(decorator)

