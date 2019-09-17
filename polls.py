import discord
import asyncio

from PollBaseClass import PollBaseClass


class Poll(PollBaseClass):
    model_perms = discord.Permissions(70769729)

    def __init__(self, emoji_list, role_list, author, title):
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
            self.roles.append([await self.author.guild.create_role(name=i, mentionable=True, permissions=Poll.model_perms)])
        self.emoji_role_paired_list = [[self.emoji_list[i], self.roles[i][0]] for i in range(len(self.emoji_list))]
        return self

    def make_body_text(self):
        """
        Formats all of the roles and emojis so they can look nice on the embed

        :return: self
        """
        self.text += '\n'.join((f"{emoji} - {role.mention}" for emoji, role in self.emoji_role_paired_list))
        return self

    def get_role(self, emoji_unicode):
        """
        Gets the role associated with the unicode of an emoji

        :param emoji_unicode: str
        :return: discord.Role, list
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

        :return: self
        """
        for role in self.roles:
            await role[0].delete()
        embed_edit = self.embed.set_footer(text="Poll has ended")
        await self.message.edit(embed=embed_edit)
        await self.general_role.delete()
        return self

    async def reaction_watch_loop(self, bot):
        """
        Loop, when someone reacts to the message it removes all of their other reactions and gives them the
        corresponding role

        :param bot: connection to discord
        :param bot_message: discord.Message
        :return: None
        """

        def reaction_check(reaction_, user):
            """
            Is a check method so that bot.wait_for() only returns valid reactions, it deletes incorrect reations and
            ignores ones from the wrong message

            :param reaction_: discord.Reaction
            :param user: discord.User
            :return: bool
            """
            if reaction_.message.id == self.message.id and user != self.message.author:  # if valid message and real user
                loop = asyncio.get_event_loop()

                if str(reaction_.emoji) == '⛔':
                    if user == self.author:
                        return True

                elif str(reaction_.emoji) == '❌':
                    return True

                elif str(reaction_.emoji) in self.emoji_list:  # if the reaction is one of the choices
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

            except Exception as e:
                print(12, e)

    async def add_reactions(self):
        """
        Adds the appropriate reactions to the poll message, and the cancel emoji to the emoji list, also names the
        general reaction role (role you get from reacting to anything after the title

        :return: self
        """
        for emoji in self.emoji_list:
            await self.message.add_reaction(emoji)
        await self.message.add_reaction('❌')
        await self.message.add_reaction('⛔')
        self.emoji_list.append('❌')
        self.emoji_list.append('⛔')

        self.general_role = await self.author.guild.create_role(name=self.title, mentionable=True, permissions=Poll.model_perms)
        return self


async def get_roles(bot, ctx, check):
    """
    Interacts with the user to get the options for the poll and return the appropriate emojis as well

    :param bot: connection
    :param ctx: context
    :param check: check method
    :return: list
    """
    action_list = []
    emoji_list = ['🍇', '🍈', '🍉', '🍊', '🍋', '🍌', '🍍', '🍎', '🍏', '🍐']
    while True:
        msg = await bot.wait_for('message', check=check)
        if msg.content.lower() == 'done':
            if action_list == []:
                await ctx.channel.send('Ok, poll cancelled')
                raise ValueError("Poll cancelled")
            break
        action_list.append([msg.content, emoji_list.pop(0)])

    return action_list


async def create_poll_embed(poll):
    """
    Creates the embed of the poll, collects the role information from the user

    :param poll: Poll
    :return: discord.Embed, Poll
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