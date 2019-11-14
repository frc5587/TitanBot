import asyncio
from typing import List

import discord


class PollBaseClass:
    def __init__(self, emoji_list: List[str], author: discord.Member, title: str):
        """
        This gets inherited into any poll-based class whether or not all of the methods get
        overridden. This contains all the functionality to run a reaction poll, albeit a basic one,
        it doesn't do anything if there is a reaction,but that can be overridden when necessary,
        just copy and paste the code and edit to your heart's content

        :param emoji_list: The list of emojis used in the poll
        :type emoji_list: List[str]
        :param author: the user that initiates the poll
        :type author: discord.Member
        :param title: title of the poll
        :type title: str
        """
        self.emoji_list = emoji_list
        self.author = author
        self.title = title
        self.text = ""
        self.message = None
        self.embed = None

    async def end_poll(self):
        """
        Ends the poll by deleting all of the the roles, then edits the poll message to say poll has
        ended
        """
        embed_edit = self.embed.set_footer(text="Poll has ended")
        await self.message.edit(embed=embed_edit)
        return self

    async def reaction_watch_loop(self, bot):
        """
        Loop, when someone reacts to the message it removes all of their other reactions and gives
        them the corresponding role

        :param bot: client connection to discord
        :type bot: Object
        """

        def reaction_check(reaction_, user) -> bool:
            """
            Is a check method so that bot.wait_for() only returns valid reactions, it deletes
            incorrect reactions and ignores ones from the wrong message

            :param reaction_: the reaction that the user reacted with
            :type reaction_: discord.Reaction
            :param user: user that reacted
            :type user: discord.User
            :return: if its a valid reaction or not
            :rtype: bool
            """
            # if valid message and real user
            if reaction_.message.id == self.message.id and user != self.message.author:
                loop = asyncio.get_event_loop()

                if str(reaction_.emoji) in self.emoji_list:  # if the reaction is one of the choices
                    return True

                else:
                    loop.run_until_complete(self.message.remove_reaction(reaction_, user))

                loop.close()
            return False

        while True:
            try:
                # blocking
                reaction, member = await bot.wait_for('reaction_add', check=reaction_check)
                return str(reaction.emoji), member

            except Exception as e:
                print(e)

    async def add_reactions(self):
        """
        Adds the appropriate reactions to the poll message, and the cancel emoji to the emoji list,
        also names the general reaction role (role you get from reacting to anything after the title
        """
        for emoji in self.emoji_list:
            await self.message.add_reaction(emoji)
        return self
