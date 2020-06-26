import discord

from math_equ import math_main
from extras import SYSTEM_CONFIG
import classes.reaction_role_poll as rrp


async def channels(ctx, bot):
    """
    Just for debugging, sends a list of the channel IDs and names stored in channels.txt

    :param ctx: context for message
    :type ctx: Object
    :param bot: connection to discord
    :type bot: Object
    """
    if SYSTEM_CONFIG['channels']:
        await ctx.channel.send(
            "\n".join([bot.get_channel(c).mention for c in SYSTEM_CONFIG['channels']]))

    else:
        await ctx.channel.send("No channels are subscribed to announcements")


async def makepoll(ctx, bot):
    bot_msg = await ctx.channel.send('Name your poll, then list out the options, one per message, '
                                     'send `done` when you are finished')

    def message_check(m) -> bool:
        return m.channel == ctx.channel and m.author == ctx.message.author

    title_msg = await bot.wait_for('message', check=message_check)  # blocking

    role_emoji_list = await rrp.get_roles(bot, ctx, message_check)
    poll = rrp.ReactionRolePoll(bot,
                                [emoji for role, emoji in role_emoji_list],
                                [role for role, emoji in role_emoji_list],
                                title_msg.author, title_msg.content)
    await ctx.message.delete()
    await bot_msg.delete()
    await title_msg.delete()

    await poll.start(ctx.channel)
    await poll.loop()


async def math(ctx, user_args):

    await ctx.channel.trigger_typing()
    try:
        answers, equ = math_main(user_args)
        math_embed = discord.Embed(
            title=f"`{equ}`",
            color=discord.Color.from_rgb(67, 0, 255),
            description=f"```\n{''.join(answers)}\n```"
        )
        await ctx.channel.send(content=None, embed=math_embed)
    except Exception as e:
        await ctx.channel.send(f"Well, You did something wrong\n`{e}`")