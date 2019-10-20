import discord

from Classes.PollBaseClass import PollBaseClass


class SetupPoll(PollBaseClass):

    @staticmethod
    async def unsubscribe(ctx):
        """
        It removes the channel from channels.txt, if it hasn't been already

        :param ctx: context
        :return: None
        """
        with open('cache/channels.txt', 'r') as f:  # reads all current ids on the text file (list)
            channel_id_list = f.readlines()

        if str(ctx.channel.id) not in channel_id_list:  # checks if channels is already in the list
            await ctx.channel.send("This channel is not subscribed to the announcements")
            return

        else:
            for index, channel_id in enumerate(channel_id_list):
                if channel_id == str(ctx.channel.id):
                    channel_id_list.pop(index)
                    channel_str = '\n'.join(channel_id_list)

                    with open('cache/channels.txt', 'w') as f:  # deletes the channel id from text file
                        f.write(channel_str)

                    await ctx.channel.send("This channel has now been unsubscribed from the announcements")

    @staticmethod
    async def subscribe(ctx):
        """
        This adds the channel to channels.txt if it isn't on already

        :param ctx: context
        :return: None
        """
        with open('cache/channels.txt', 'r') as f:  # reads all current ids on the text file (list)
            channel_id_list = f.readlines()

        if str(ctx.channel.id) in channel_id_list:  # checks if channels is already in the list
            await ctx.channel.send("This channel is already subscribed to the announcements")
            return

        else:
            with open('cache/channels.txt', 'a') as f:  # writes the channels id to text file
                f.write("\n" + str(ctx.channel.id))
            await ctx.channel.send("This channel is now subscribed to the announcements")

    async def sub_to_auto_announcements(self, bot, ctx):
        """
        Waits for a reaction (either ✅ or ❌) then it acts accordingly, if it is a check it adds it to channels.txt if
        it isn't on already, if it is the X then it removes it from channels.txt, if it hasn't been already

        :param bot: connection
        :param ctx: context
        :return: None
        """
        emoji, member = await self.reaction_watch_loop(bot)
        while member != self.author:
            emoji, member = await self.reaction_watch_loop(bot)
        if emoji == '✅':
            await self.subscribe(ctx)

        else:
            await self.unsubscribe(ctx)

    async def create_poll_embed(self):
        """
        Creates the embed of the poll, collects the role information from the user

        :return: discord.Embed, Poll
        """

        self.embed = discord.Embed(
            title=f"**{self.title}**",
            description=f"Do you want to subscribe (✅) or unsubscribe (❌) from the auto-announcements?",
            color=discord.Color.from_rgb(67, 0, 255)
        )
        self.embed.set_footer(text='React with the corresponding emoji!')
