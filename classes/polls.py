import discord
import asyncio
from typing import List, Tuple
import pickle
from os import path, listdir, remove

from classes.PollBaseClass import PollBaseClass


class Poll(PollBaseClass):
    """
    This cass has all the methods needed to run a discord reaction based poll, except for the data collection, given
    the proper loops on the calls
    """
    model_perms = discord.Permissions(0)

    def __init__(self, emoji_list: List[str], str_role_list: List[str], author: discord.Member, title: str):
        """
        This should be called once the data is obtained

        :param emoji_list: all emojis being used in the poll, except for the reset and end emojis
        :type emoji_list: List[str]
        :param str_role_list: list of strings to be converted to discord roles
        :type str_role_list: List[str]
        :param author: the author of the poll
        :type author: discord.Member
        :param title: Name of the poll
        :type title: str
        """
        self.emoji_list = emoji_list
        self.str_role_list = str_role_list
        self.author = author
        self.title = title
        self.emoji_role_paired_list = []
        self.roles = []
        self.text = ""
        self.message = None
        self.embed = None
        self.general_role = None
        self.file_no = None

    async def run(self, ctx, bot):
        await self.create_poll_embed()
        self.message = await ctx.channel.send(content=None, embed=self.embed)
        await self.add_reactions()
        try:
            await self.save(bot)
        except Exception as e:
            await ctx.channel.send(e)
        await self.reaction_watch_loop(bot)

    async def create_roles(self):
        """
        Creates all the roles needed for the poll

        :return: self
        """
        for i in self.str_role_list:
            self.roles.append([await self.author.guild.create_role(name=i,
                                                                   mentionable=True,
                                                                   permissions=Poll.model_perms)])
        # not really sure why it indexes '0', but its important
        self.emoji_role_paired_list = [[self.emoji_list[i],
                                        self.roles[i][0]] for i in range(len(self.emoji_list))]
        return self

    async def create_poll_embed(self):
        """
        Creates the embed of the poll, collects the role information from the user, runs most of the higher level Poll class
        methods to organize the poll to be sent

        :return: the embed that will be sent and the poll with all of the data
        :rtype: discord.Embed, Poll
        """
        await self.create_roles()  # interacts with user to get role information
        self.make_body_text()
        self.embed = discord.Embed(
            title=f"**{self.title}**",
            description=f"{self.text}\n❌ - Nevermind (removes reaction roles)\n⛔ - To end poll (Author only)",
            color=discord.Color.from_rgb(67, 0, 255)
        )
        self.embed.set_footer(text='React with the corresponding emoji!')

        return self

    def make_body_text(self):
        """
        Formats all of the roles and emojis so they can look nice and orderly on the embed, basically makes them all one
        big str
        """
        self.text += '\n'.join((f"{emoji} - {role.mention}" for emoji, role in self.emoji_role_paired_list))
        return self

    def get_role(self, emoji_unicode: str) -> (discord.Role, List[Tuple[str, discord.Role]]):
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
        remove(f"cache/polls/poll{str(self.file_no)}.pickle")
        remove(f"cache/polls/poll{str(self.file_no)}.poTaTo")
        for role in self.roles:
            await role.delete()
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
        loop = asyncio.get_event_loop()

        async def reaction_check(reaction_, user) -> bool:
            """
            Is a check method so that bot.wait_for() only returns valid reactions, it deletes incorrect reactions and
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

                if str(reaction_.emoji) == '⛔':
                    if user == self.author:
                        return True

                elif str(reaction_.emoji) == '❌':
                    return True

                elif str(reaction_.emoji) in self.emoji_list:  # if the reaction is one of the choices for the poll
                    return True

                coro = self.message.remove_reaction(reaction_, user)

                asyncio.run_coroutine_threadsafe(coro, loop)
            return False

        while True:  # event loop
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

    def write_important_stuff(self):
        """
        This writes all the IDs for the context objects down to some files in cache/polls/ and adds the file "number"
        that contains the data, to the object
        """
        counter = 0
        while path.exists(f'cache/polls/poll{counter}.pickle'):
            counter += 1
        with open(f'cache/polls/poll{counter}.poTaTo', 'w+') as file:
            file.write(f"{str(self.message.channel.id)}\n{str(self.message.id)}\n{str(self.general_role.id)}\n")
            for emoji, role in self.emoji_role_paired_list:
                file.write(emoji + str(role.id) + "\n")
        self.file_no = counter
        return self

    async def save(self, bot):
        """
        This writes all the IDs for the context objects down to some files in cache/polls/ then it removes the context
        objects from the object and pickles the object to another file. Once that is done, it get the context object
        back by reading the file with the IDs

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
        # self.embed = None

        with open(f'cache/polls/poll{self.file_no}.pickle', 'wb+') as file:
            pickle.dump(self, file)

        with open(f"cache/polls/poll{self.file_no}.poTaTo", "r") as file:
            lines = file.readlines()

        # get context objects back
        channel = bot.get_channel(int(lines.pop(0)))
        self.message = await channel.fetch_message(int(lines.pop(0)))
        self.general_role = channel.guild.get_role(int(lines.pop(0)))
        self.author = self.message.author

        for line in lines:  # add roles back to lists
            self.emoji_role_paired_list.append([line[0], channel.guild.get_role(int(line[1:]))])
            self.roles.append(channel.guild.get_role(int(line[1:])))
        return self

    @staticmethod
    async def loadall(bot):
        try:
            await bot.wait_until_ready()
            poll_list = []
            pickle_file_list = sorted(listdir('cache/polls'))[::2]
            potato_file_list = sorted(listdir('cache/polls'))[1::2]

            for num, file in enumerate(pickle_file_list):
                with open('cache/polls/' + file, 'rb') as read_file:
                    poll_list.append(pickle.load(read_file))

                with open('cache/polls/' + potato_file_list[num], 'r') as read_file2:
                    lines = read_file2.readlines()

                channel = bot.get_channel(int(lines.pop(0)))
                poll_list[num].message = await channel.fetch_message(int(lines.pop(0)))
                poll_list[num].general_role = channel.guild.get_role(int(lines.pop(0)))
                poll_list[num].author = poll_list[num].message.author

                for line in lines:  # add roles back to lists
                    poll_list[num].emoji_role_paired_list.append([line[0], channel.guild.get_role(int(line[1:]))])
                    poll_list[num].roles.append(channel.guild.get_role(int(line[1:])))
            return poll_list
        except Exception as ee:
            print(ee)

    @staticmethod
    async def runall(bot):
        """
        Runs all of the saved polls, should be called upon startup

        :param bot:
        :type bot:
        """
        try:
            await bot.wait_until_ready()
            poll_list = await Poll.loadall(bot)
            for poll in poll_list:
                bot.loop.create_task(poll.reaction_watch_loop(bot))
                print("running: ", poll.title)
        except Exception as ee:
            print(ee)


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

