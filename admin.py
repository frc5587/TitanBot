# This is for admin based commands


def clear():
    """
    Clears channels.txt of any extra \n's and return a list of channel IDs

    :return: list (str)
    """
    with open('Xtras/channels.txt', 'r') as f:
        lines = f.read()
    with open('Xtras/channels.txt', 'w') as f:
        lines_list = lines.split('\n')
        final_list = []
        for line in lines_list:
            if line != '':
                final_list.append(line)
        f.writelines(final_list)
    return final_list


async def channels(bot, ctx):
    """
    Just for debugging, sends a list of the channel IDs and names stored in channels.txt

    :param bot: connection to discord
    :return: None
    """
    channel_list = clear()
    chan_lst = []
    for channel in channel_list:
        channel_ = bot.get_channel(int(channel))
        chan_lst.append(f"#{str(channel_)} ({channel_.id})")
    await ctx.channel.send('\n'.join(chan_lst))
