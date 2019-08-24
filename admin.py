# This is for admin based commands


async def channels(bot):
    """
    Just for debugging, sends "Is this right?" to every channel saved in channels.txt

    :param bot: connection to discord
    :return: None
    """
    with open('Xtras/channels.txt', 'r') as f:
        channel_list = f.readlines()
        channel_list.pop(0)
    for channel in channel_list:
        chan_id = int(channel)
        channel = bot.get_channel(chan_id)
        await channel.send("Is this right?")
