import discord
import asyncio
from typing import List

from classes.PollBaseClass import PollBaseClass


class Poll(PollBaseClass):
    """
    This cass has all the methods needed to run a discord reaction based poll, except for the data collection, given
    the proper loops on the calls
    """
    model_perms = discord.Permissions(0)

    def __init__(self, emoji_list: List[str], role_list: List[str], author: discord.Member, title: str):
        """
        This should be called once the data is obtained

        :param emoji_list: all emojis being used in the poll, except for the reset and end emojis
        :type emoji_list: List[str]
        :param role_list: list of strings to be converted to discord roles
        :type role_list: List[str]
        :param author: the author of the poll
        :type author: discord.Member
        :param title: Name of the poll
        :type title: str
        """
        self.emoji_list = emoji_list
        self.role_list = role_list
        self.author = author
        self.title = title
        self.emoji_role_paired_list = []
        self.roles = []
        self.text = ""
        self.message = None
        self.embed = None
        self.general_role = None

    async def create_roles(self):
        """
        Creates all the roles needed for the poll

        :return: self
        """
        for i in self.role_list:
            self.roles.append([await self.author.guild.create_role(name=i,
                                                                   mentionable=True,
                                                                   permissions=Poll.model_perms)])
        # not really sure why it indexes '0', but its important
        self.emoji_role_paired_list = [[self.emoji_list[i],
                                        self.roles[i][0]] for i in range(len(self.emoji_list))]
        return self

    def make_body_text(self):
        """
        Formats all of the roles and emojis so they can look nice and orderly on the embed, basically makes them all one
        big str
        """
        self.text += '\n'.join((f"{emoji} - {role.mention}" for emoji, role in self.emoji_role_paired_list))
        return self

    def get_role(self, emoji_unicode: str) -> (discord.Role, List[str, discord.Role]):
        """
        Gets the role associated with the unicode of an emoji, and returns a list of the rest of the emoji role pair
        without the emoji role pair that was asked for

        :param emoji_unicode: the string literal of the emoji
        :type emoji_unicode: str
        :return: the role that corresponds to emoji_unicode and the rest of the pairs
        :rtype: discord.Role, List[str, discord.Role]
        """
        rest = []
        return_role = None
        for emoji, role in self.emoji_role_paired_list:
            if emoji == emoji_unicode:
                return_role = role
            else:
                rest.append([emoji, role])
        if return_role is None:
            raise ValueError("Emoji is not in 'emoji_role_paired_list'")
        return return_role, rest

    async def end_poll(self):
        """
        Ends the poll by deleting all of the the roles, then edits the poll message to say poll has ended
        TODO replace the roles on the message with their string literal so it doesn't say '@role-deleted'
        """
        for role in self.roles:
            await role[0].delete()
        embed_edit = self.embed.set_footer(text="Poll has ended")
        await self.message.edit(embed=embed_edit)
        await self.general_role.delete()
        return self

    async def reaction_watch_loop(self, bot) -> None:
        """
        Loop, when someone reacts to the message it removes all of their other reactions and gives them the
        corresponding role, if they pick the ⛔ it removes all of their roles, and if the author picks ❌ then it will
        close the poll with poll.end_poll()

        :param bot: client connection to discord
        :type bot: Object
        """

        def reaction_check(reaction_, user):
            """
            Is a check method so that bot.wait_for() only returns valid reactions, it deletes incorrect reations and
            ignores ones from the wrong message

            :param reaction_: Reaction that this is called for
            :type reaction_: discord.Reaction
            :param user: The user that reacts with reaction_
            :type user: discord.User
            :return: Whether if is a valid reaction for the poll, if False it just ignore its (and remove it)
            :rtype: bool
            """
            # if valid message and real user
            if reaction_.message.id == self.message.id and user != self.message.author:
                loop = asyncio.get_event_loop()

                if str(reaction_.emoji) == '⛔':
                    if user == self.author:
                        return True

                elif str(reaction_.emoji) == '❌':
                    return True

                elif str(reaction_.emoji) in self.emoji_list:  # if the reaction is one of the choices for the poll
                    return True

                loop.run_until_complete(self.message.remove_reaction(reaction_, user))
                loop.close()
            return False

        while True:
            try:
                reaction, member = await bot.wait_for('reaction_add', check=reaction_check)  # blocking

                if str(reaction.emoji) == '⛔':  # ends poll
                    await self.end_poll()
                    return

                elif str(reaction.emoji) == '❌':  # removes all of the users reactions and roles
                    for emoji, role in self.emoji_role_paired_list:
                        await member.remove_roles(role)
                        await self.message.remove_reaction(emoji, member)
                    await self.message.remove_reaction('❌', member)
                    await member.remove_roles(self.general_role)
                    continue

                role, not_roles = self.get_role(str(reaction.emoji))
                await member.add_roles(role)
                await member.add_roles(self.general_role)

            except Exception as eEe:
                print(f"Reaction watch loop error: {eEe}")

    async def add_reactions(self):
        """
        Adds the appropriate reactions to the poll message, and the cancel emoji to the emoji list, also names the
        general reaction role (role you get from reacting to anything) after the title
        """
        for emoji in self.emoji_list:
            await self.message.add_reaction(emoji)
        await self.message.add_reaction('❌')
        await self.message.add_reaction('⛔')
        self.emoji_list.append('❌')
        self.emoji_list.append('⛔')

        self.general_role = await self.author.guild.create_role(name=self.title,
                                                                mentionable=True,
                                                                permissions=Poll.model_perms)
        return self


async def get_roles(bot, ctx, check):
    """
    Interacts with the user to get the options for the poll and return the appropriate emojis as well

    :param bot: client connection to discord
    :type bot: Object
    :param ctx: context for the message
    :type ctx: Object
    :param check: check method that gets called on every message sent
    :type check: function
    :return: list
    """
    action_list = []
    emoji_list = ['🍇', '🍈', '🍉', '🍊', '🍋', '🍌', '🍍', '🍎', '🍏', '🍐']  # TODO make emoji list longer
    while True:
        msg = await bot.wait_for('message', check=check)
        if msg.content.lower() == 'done':
            if action_list == list():  # empty list
                await ctx.channel.send('Ok, poll cancelled')
                raise ValueError("Poll cancelled")
            break
        action_list.append([msg.content, emoji_list.pop(0)])

    return action_list


async def create_poll_embed(poll: Poll) -> (discord.Embed, Poll):
    """
    Creates the embed of the poll, collects the role information from the user, runs most of the higher level Poll class
    methods to organize the poll to be sent

    :param poll: the poll being acted on
    :type poll: Poll
    :return: the embed that will be sent and the poll with all of the data
    :rtype: discord.Embed, Poll
    """
    await poll.create_roles()  # interacts with user to get role information
    poll.make_body_text()
    poll.embed = discord.Embed(
        title=f"**{poll.title}**",
        description=f"{poll.text}\n❌ - Nevermind (removes reaction roles)\n⛔ - To end poll (Author only)",
        color=discord.Color.from_rgb(67, 0, 255)
    )
    poll.embed.set_footer(text='React with the corresponding emoji!')

    return poll.embed, poll
