import asyncio


class PollBaseClass:
    def __init__(self, emoji_list, author, title):
        self.emoji_list = emoji_list
        self.author = author
        self.title = title
        self.text = ""
        self.message = None
        self.embed = None

    async def end_poll(self):
        """
        Ends the poll by deleting all of the the roles, then edits the poll message to say poll has ended

        :return: self
        """
        embed_edit = self.embed.set_footer(text="Poll has ended")
        await self.message.edit(embed=embed_edit)
        return self

    async def reaction_watch_loop(self, bot):
        """
        Loop, when someone reacts to the message it removes all of their other reactions and gives them the
        corresponding role

        :param bot: connection to discord
        :return: None
        """

        def reaction_check(reaction_, user):
            """
            Is a check method so that bot.wait_for() only returns valid reactions, it deletes incorrect reactions and
            ignores ones from the wrong message

            :param reaction_: discord.Reaction
            :param user: discord.User
            :return: bool
            """

            if reaction_.message.id == self.message.id and user != self.message.author:  # if valid message and real user
                loop = asyncio.get_event_loop()

                if str(reaction_.emoji) in self.emoji_list:  # if the reaction is one of the choices
                    return True

                else:
                    loop.run_until_complete(self.message.remove_reaction(reaction_, user))

                loop.close()
            return False

        while True:
            try:
                reaction, member = await bot.wait_for('reaction_add', check=reaction_check)  # blocking
                return str(reaction.emoji), member

            except Exception as e:
                print(e)

    async def add_reactions(self):
        """
        Adds the appropriate reactions to the poll message, and the cancel emoji to the emoji list, also names the
        general reaction role (role you get from reacting to anything after the title

        :return: self
        """
        for emoji in self.emoji_list:
            await self.message.add_reaction(emoji)
        return self
