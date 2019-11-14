"""
This is for administrator commands
"""
from typing import List
import os


def make_channel_cache() -> bool:
    """
    Creates the file and folder for caching the channels used in the auto announcement system.
    Returns `True` if it created the file, and `False` if it didn't

    :return: whether it created the file
    :rtype: bool
    """
    if not os.path.exists('cache/channels.txt'):
        try:
            os.mkdir('cache')
        except FileExistsError:
            pass
        with open('cache/channels.txt', 'a+'):
            pass
        return True
    return False


def clear_and_find_channels() -> List[int]:
    """
    Clears channels.txt of any extra \n's and return a list of channel IDs

    :raises ValueError: if channels.txt is empty
    :return: list of all of the channel IDs
    :rtype: List[int]
    """
    make_channel_cache()

    with open('cache/channels.txt', 'r+') as channels_file:
        lines = channels_file.readlines()
        final_list = []
        for line in lines:
            if line not in ['', '\n']:
                final_list.append(line)
        channels_file.seek(0)  # sets pointer to the beginning of the file
        channels_file.writelines(final_list)

        if lines == list():
            raise ValueError

    return [int(channel) for channel in final_list]


async def channels(bot, ctx) -> None:
    """
    Just for debugging, sends a list of the channel IDs and names stored in channels.txt

    :param bot: connection to discord
    :type bot: Object
    :param ctx: context for message
    :type ctx: Object
    """
    try:
        channel_list_int = clear_and_find_channels()
        chan_lst = []

        if channel_list_int == list():
            await ctx.channel.send("No channels are subscribed to announcements")
            return

        for channel_int in channel_list_int:
            channel = bot.get_channel(channel_int)
            chan_lst.append(f"#{str(channel)} ({channel.id})")

        await ctx.channel.send('\n'.join(chan_lst))

    except ValueError:
        await ctx.channel.send("No channels are subscribed to the announcements")
