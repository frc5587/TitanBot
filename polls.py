import random
from typing import List, Tuple
import pickle
import os

import discord

from classes.PollBaseClass import PollBaseClass


class Poll(PollBaseClass):
    """
    This cass has all the methods needed to run a discord reaction based poll, except for the data
    collection, given the proper loops on the calls
    """
    model_perms = discord.Permissions(0)

    def __init__(self,
                 emoji_list: List[str],
                 role_list: List[str],
                 author: discord.Member,
                 title: str):
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
        self.file_number = None

    async def create_roles(self):
        """
        Creates all the roles needed for the poll
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
        Formats all of the roles and emojis so they can look nice and orderly on the embed,
        basically makes them all one big str
        """
        self.text += '\n'.join((f"{emoji} - "
                                f"{role.mention}" for emoji, role in self.emoji_role_paired_list))
        return self

    def get_role(self, emoji_unicode: str) -> (discord.Role, List[Tuple[str, discord.Role]]):
        """
        Gets the role associated with the unicode of an emoji, and returns a list of the rest of the
        emoji role pair without the emoji role pair that was asked for

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
        Ends the poll by deleting all of the the roles, then edits the poll message to say poll has
        ended
        TODO replace the roles on the message so it doesn't say '@role-deleted'
        """
        os.remove(f'cache/polls/poll{self.file_number}.pickle')  # delete cache
        os.remove(f'cache/polls/poll{self.file_number}.poTaTo')

        for role in self.roles:
            await role.delete()
        embed_edit = self.embed.set_footer(text="Poll has ended")
        await self.message.edit(embed=embed_edit)
        await self.general_role.delete()
        return self

    async def add_reactions(self):
        """
        Adds the appropriate reactions to the poll message, and the cancel emoji to the emoji list,
        also names the general reaction role (role you get from reacting to anything) after the
        title
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

    async def get_compare_reactions(self):
        """
        First this gets the newest instance of the object representing the message, then it iterates
        through any users that have added a reaction that is not on the list, and removes the
        reaction. Finally, it will add the roles necessary for the reactions that the users choose.
        Note: this takes about 20 - 45 seconds to iterate once
        """
        try:
            while True:
                self.message = await self.message.channel.fetch_message(self.message.id)
                await self.remove_wrong_reactions(self.message.reactions)
                await self.add_remove_roles(self.message.reactions)
        except RuntimeError:
            return

    async def add_remove_roles(self, reaction_list: List[discord.Reaction]):
        """
        This iterates through all of the reactions on the message, and it adds the roles necessary
        and removes all of their roles and reactions if they reacted with the :x:, a

        :param reaction_list: A list of the reactions on the message
        :type reaction_list: List[discord.Reaction]
        """
        try:
            for reaction in reaction_list:
                async for member in reaction.users():
                    if member == self.message.author:
                        continue
                    if str(reaction.emoji) == '❌':  # removes all of the user's reactions and roles
                        for emoji, role in self.emoji_role_paired_list:
                            await member.remove_roles(role)
                            await self.message.remove_reaction(emoji, member)
                        await self.message.remove_reaction('❌', member)
                        await member.remove_roles(self.general_role)
                        continue

                    elif str(reaction.emoji) in self.emoji_list:
                        role, not_roles = self.get_role(str(reaction.emoji))
                        await member.add_roles(role)
                        await member.add_roles(self.general_role)
        except Exception as e:
            print(e)

    async def remove_wrong_reactions(self, reaction_list: List[discord.Reaction]):
        """
        This will iterate through all of the reactions on a message and if one is not an option,
        it removes that reaction. If someone who is not the author reacts with ⛔ then it will remove
        it. Otherwise it will delete the poll and returns out of the loop

        :param reaction_list: A list of the reactions on the message
        :type reaction_list: List[discord.Reaction]
        """
        try:
            for reaction in reaction_list:
                if str(reaction.emoji) == '⛔':
                    async for member in reaction.users():
                        if member != self.message.author:
                            if member == self.author:
                                await self.end_poll()
                                raise RuntimeError("Poll has been deleted")
                            else:
                                await self.message.remove_reaction(reaction.emoji, member)

                if str(reaction.emoji) not in self.emoji_list and \
                        str(reaction.emoji) != '❌' and str(reaction.emoji) != '⛔':

                    async for member in reaction.users():
                        self.message.remove_reaction(reaction.emoji, member)

        except RuntimeError:
            raise RuntimeError("Poll has been deleted")
        except Exception as e:
            print(f"**{e}**")

    def write_important_stuff(self):
        """
        This writes all the IDs for the context objects down to some files in cache/polls/ and adds
        the file "number" that contains the data, to the object
        """
        counter = 0
        while os.path.exists(f'cache/polls/poll{counter}.pickle'):
            counter += 1

        with open(f'cache/polls/poll{counter}.poTaTo', 'w+') as file:
            file.write(f"{str(self.message.channel.id)}\n"
                       f"{str(self.message.id)}\n"
                       f"{str(self.general_role.id)}\n"
                       f"{str(self.author.id)}\n")

            for emoji, role in self.emoji_role_paired_list:
                file.write(emoji + str(role.id) + "\n")
        self.file_number = counter
        return self

    async def save(self, bot):
        """
        This writes all the IDs for the context objects down to some files in cache/polls/ then it
        removes the context objects from the object and pickles the object to another file. Once
        that is done, it get the context object back by reading the file with the IDs

        :param bot: client connection to discord
        :type bot: Object
        """
        self.write_important_stuff()

        # clear data
        self.emoji_role_paired_list = []
        self.general_role = None
        self.roles = []
        self.message = None
        self.author = None

        with open(f'cache/polls/poll{self.file_number}.pickle', 'wb+') as file:
            pickle.dump(self, file)

        with open(f"cache/polls/poll{self.file_number}.poTaTo", "r") as file:
            lines = file.readlines()

        # get context objects back
        channel = bot.get_channel(eval(lines.pop(0)))
        self.message = await channel.fetch_message(eval(lines.pop(0)))
        self.general_role = channel.guild.get_role(eval(lines.pop(0)))
        self.author = channel.guild.get_member(eval(lines.pop(0)))

        for line in lines:  # add roles back to lists
            self.emoji_role_paired_list.append([line[0], channel.guild.get_role(eval(line[1:]))])
            self.roles.append(channel.guild.get_role(eval(line[1:])))
        return self

    @staticmethod
    async def loadall(bot) -> List:
        """
        This iterates through all of the cached polls in `cache/polls`, un-pickles them, and adds
        back the context attributes. Then it returns the list of polls to be run

        :param bot: Client connection to discord
        :type bot: Object
        :return: A list of the cached polls
        :rtype: List[Poll]
        """
        try:
            await bot.wait_until_ready()
            poll_list = []
            pickle_file_list = sorted(os.listdir('cache/polls'))[::2]
            potato_file_list = sorted(os.listdir('cache/polls'))[1::2]

            for num, file in enumerate(pickle_file_list):
                with open('cache/polls/' + file, 'rb') as read_file:
                    poll_list.append(pickle.load(read_file))

                with open('cache/polls/' + potato_file_list[num], 'r') as read_file2:
                    lines = read_file2.readlines()

                channel: discord.TextChannel = bot.get_channel(eval(lines.pop(0)))
                poll_list[num].message = await channel.fetch_message(eval(lines.pop(0)))
                poll_list[num].general_role = channel.guild.get_role(eval(lines.pop(0)))
                poll_list[num].author = channel.guild.get_member(eval(lines.pop(0)))

                for line in lines:  # add roles back to lists
                    poll_list[num].emoji_role_paired_list\
                        .append([line[0], channel.guild.get_role(eval(line[1:]))])

                    poll_list[num].roles.append(channel.guild.get_role(eval(line[1:])))
            return poll_list
        except Exception as ee:
            print(ee)

    @staticmethod
    async def runall(bot):
        """
        Runs all of the cached polls. This should be called on startup, by creating a task with
        `bot`. It will unpickle all of the polls, then run them and they will behave like normal.

        :param bot: Client connection to discord
        :type bot: Object
        """
        try:
            await bot.wait_until_ready()
            poll_list = await Poll.loadall(bot)
            for poll in poll_list:
                bot.loop.create_task(poll.get_compare_reactions())
                print("running poll: ", poll.title)
        except Exception as ee:
            print(ee)


async def get_roles(bot, ctx, check):
    """
    Interacts with the user to get the options for the poll and return the appropriate emojis as
    well

    :param bot: client connection to discord
    :type bot: Object
    :param ctx: context for the message
    :type ctx: Object
    :param check: check method that gets called on every message sent
    :type check: function
    :return: list
    """
    action_list = []
    emoji_list = ['🍇', '🍈', '🍉', '🍊', '🍋', '🍌', '🍍', '🍎', '🍏', '🍐', '🥝', '🍒']
    random.shuffle(emoji_list)
    # TODO make emoji_list longer
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
    Creates the embed of the poll, collects the role information from the user, runs most of the
    higher level Poll class methods to organize the poll to be sent

    :param poll: the poll being acted on
    :type poll: Poll
    :return: the embed that will be sent and the poll with all of the data
    :rtype: discord.Embed, Poll
    """
    await poll.create_roles()  # interacts with user to get role information
    poll.make_body_text()
    poll.embed = discord.Embed(
        title=f"**{poll.title}**",
        description=f"{poll.text}\n❌ - Nevermind (removes reaction roles)"
                    f"\n⛔ - To end poll (Author only)",
        color=discord.Color.from_rgb(67, 0, 255)
    )
    poll.embed.set_footer(text='React with the corresponding emoji!')

    return poll.embed, poll
