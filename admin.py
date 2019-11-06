"""
This is for admin based commands
"""
from typing import List


def clear_and_find_channels() -> List[int]:
    """
    Clears channels.txt of any extra \n's and return a list of channel IDs

    :return: list of all of the channel IDs
    :rtype: List[int]
    """
    with open('cache/channels.txt', 'r+') as channels_file:
        lines = channels_file.readlines()
        final_list = []
        for line in lines:
            if line not in ['', '\n']:
                final_list.append(line)
        channels_file.seek(0)  # sets pointer to the beginning of the file
        channels_file.writelines(final_list)
    return [int(channel) for channel in final_list]


async def channels(bot, ctx) -> None:
    """
    Just for debugging, sends a list of the channel IDs and names stored in channels.txt

    :param bot: connection to discord
    :type bot: Object
    :param ctx: context for message
    :type ctx: Object
    """
    channel_list_int = clear_and_find_channels()
    chan_lst = []

    if channel_list_int == list():
        await ctx.channel.send("No channels are subscribed to announcements")
        return

    for channel_int in channel_list_int:
        channel = bot.get_channel(channel_int)
        chan_lst.append(f"#{str(channel)} ({channel.id})")

    await ctx.channel.send('\n'.join(chan_lst))
