# This is for admin based commands


async def channels(bot, ctx):
    """
    Just for debugging, sends "Is this right?" to every channel saved in channels.txt

    :param bot: connection to discord
    :return: None
    """
    with open('Xtras/channels.txt', 'r') as f:
        channel_list = f.readlines()
        static = channel_list
    with open('Xtras/channels.txt', 'w') as f:
        write_line = []
        for line in channel_list:
            if line != '\n':
                write_line.append(line)
        f.writelines(write_line)
    chan_lst = []
    for channel in write_line:
        channel_ = bot.get_channel(int(channel))
        chan_lst.append(f"#{str(channel_)} ({channel_.id})")
    await ctx.channel.send('\n'.join(chan_lst))
    await ctx.channel.send(static)
