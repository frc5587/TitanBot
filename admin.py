"""
This is for admin based commands
"""
from typing import List


def clear_and_find_channels() -> List[str]:
    """
    Clears channels.txt of any extra \n's and return a list of channel IDs

    :return: list of all of the channel IDs
    :rtype: List[str]
    """
    with open('cache/channels.txt', 'rw') as channels_file:
        lines = channels_file.readlines()
        final_list = []
        for line in lines:
            if line != '':
                final_list.append(line)
        channels_file.writelines(final_list)
    return final_list


async def channels(bot, ctx) -> None:
    """
    Just for debugging, sends a list of the channel IDs and names stored in channels.txt

    :param bot: connection to discord
    :type bot: Object
    :param ctx: context for message
    :type ctx: Object
    """
    channel_list = clear_and_find_channels()
    chan_lst = []
    for channel in channel_list:
        channel_ = bot.get_channel(int(channel))
        chan_lst.append(f"#{str(channel_)} ({channel_.id})")
    await ctx.channel.send('\n'.join(chan_lst))
