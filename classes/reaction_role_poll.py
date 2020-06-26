import random
from typing import List

import discord

from classes.poll import PollBase


class ReactionRolePoll(PollBase):
    model_perms = discord.Permissions(0)

    def __init__(self,
                 bot: discord.Client,
                 emoji_list: List[str],
                 role_list: List[str],
                 author: discord.Member,
                 title: str):
        """
        This should be called once the data is obtained

        :param bot: client connection to discord
        :type bot: discord.Bot
        :param emoji_list: all emojis being used in the poll, except for the reset and end emojis
        :type emoji_list: List[str]
        :param role_list: list of strings to be converted to discord roles
        :type role_list: List[str]
        :param author: the author of the poll
        :type author: discord.Member
        :param title: Name of the poll
        :type title: str
        """
        super(ReactionRolePoll, self).__init__(emoji_list, role_list, author, title, bot)
        self.roles = []
        self.general_role = None

    async def init(self):
        for i in self.raw_text_list:
            self.roles.append(await self.author.guild.create_role(name=i,
                                                                  mentionable=True,
                                                                  permissions=ReactionRolePoll.model_perms))
        self.general_role = await self.author.guild.create_role(name=self.title,
                                                                mentionable=True,
                                                                permissions=ReactionRolePoll.model_perms)

    @property
    def text_list(self) -> List[str]:
        """
        Formats all of the roles and emojis so they can look nice and orderly on the embed,
        basically makes them all one big str
        """
        return [r.mention for r in self.roles] + [f"End poll ({self.author.mention})"]

    @property
    def end_text(self) -> str:
        return "\n".join([f"{e} - {t}" for e, t in
                          zip(self.emoji_list,
                              self.raw_text_list + [f"End poll ({self.author.mention})"])])

    @property
    def emoji_role_dict(self) -> dict:
        return dict(zip(self.emoji_list[:-1], self.roles))

    async def clean_up(self):
        """
        Ends the poll by deleting all of the the roles, then edits the poll message to say poll has
        ended
        """
        for role in self.roles:
            await role.delete()
        await self.general_role.delete()

    async def on_reaction_add(self, emoji: str, user_id: id):
        if (emoji not in self.emoji_list) or (
                emoji == self.stop_emoji and user_id != self.author.id):
            await self.message.remove_reaction(emoji, self.message.guild.get_member(user_id))

        else:
            await self.message.guild.get_member(user_id).add_roles(self.emoji_role_dict[emoji],
                                                                   self.general_role)

    async def on_reaction_remove(self, emoji: str, user_id: int):
        if emoji in self.emoji_list[:-1]:
            await self.message.guild.get_member(user_id).remove_roles(self.emoji_role_dict[emoji])

    def remove_context_data(self):
        super(ReactionRolePoll, self).remove_context_data()
        self.save_data.update({
            "general_role_id": self.general_role.id,
            "role_ids": [role.id for role in self.roles]
        })
        self.general_role = None
        self.roles = []

    async def load_context_data(self):
        await super(ReactionRolePoll, self).load_context_data()

        channel = self.bot.get_channel(self.save_data["channel_id"])
        self.general_role = channel.guild.get_role(self.save_data["general_role_id"])
        self.roles = [channel.guild.get_role(role_id) for role_id in self.save_data['role_ids']]


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
    emoji_list = random.sample(PollBase.EMOJI_LIST, len(PollBase.EMOJI_LIST))
    while True:
        msg = await bot.wait_for('message', check=check)
        await msg.delete()
        if msg.content.lower().strip() == 'done':
            if action_list == list():  # empty list
                await ctx.channel.send('Ok, poll cancelled')
                raise RuntimeError("ReactionRolePoll cancelled")
            break
        action_list.append((msg.content, emoji_list.pop(0)))

    return action_list
