import pickle
from typing import List
from queue import Queue
import os
import asyncio

import discord

from extras import Colors, SYSTEM_CONFIG


class PollBase:
    EMOJI_LIST = ['🍇', '🍈', '🍉', '🍊', '🍋', '🍌', '🍍', '🍎', '🍏', '🍐', '🥝', '🍒', '🥭', '🍓',
                  '🍅', '🥑', '🍑', '🥥', '🌶', '🌽', '🥔']

    def __init__(self, emoji_list: List[str], text_list: List[str], author: discord.Member,
                 title: str, bot):
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
        self.raw_emoji_list = emoji_list
        self.raw_text_list = text_list
        self.author = author
        self.title = title
        self.message = None
        self.bot = bot
        self.add_reaction_q = None
        self.remove_reaction_q = None
        self.stop_emoji = "❌"
        self.save_data = {}
        self.file_number = None

    async def end(self):
        """
        Ends the poll by deleting all of the the roles, then edits the poll message to say poll has
        ended
        """
        os.remove(f'cache/polls/poll{self.file_number}.pickle')  # delete cache
        await self.clean_up()
        embed = self.embed.set_footer(text="Poll has ended")
        embed.description = self.end_text
        await self.message.edit(embed=embed)
        return self

    async def save(self):
        """
        This writes all the IDs for the context objects down to some files in cache/polls/ then it
        removes the context objects from the object and pickles the object to another file. Once
        that is done, it get the context object back by reading the file with the IDs
        """
        self.file_number = 0
        while os.path.exists(f'cache/polls/poll{self.file_number}.pickle'):
            self.file_number += 1  # counts up till it finds and unused number

        self.remove_context_data()
        bot, self.bot = self.bot, None

        with open(f'cache/polls/poll{self.file_number}.pickle', 'wb+') as pickle_file:
            pickle.dump(self, pickle_file)

        self.bot = bot
        await self.load_context_data()

    async def start(self, channel):
        await self.init()

        self.message = await channel.send(embed=self.embed)
        for emoji in self.emoji_list:
            await self.message.add_reaction(emoji)

        await self.set_up()
        await self.save()

    async def loop(self):
        """
        Loop, when someone reacts to the message it removes all of their other reactions and gives
        them the corresponding role
        """
        self.bot.add_listener(self.reaction_add_listener, name="on_raw_reaction_add")
        self.bot.add_listener(self.reaction_remove_listener, name="on_raw_reaction_remove")

        while True:
            await asyncio.sleep(0.1)
            if not self.add_reaction_q.empty():
                emoji, user_id = self.add_reaction_q.get()
                if self.stop_condition(emoji, user_id):
                    break
                else:
                    await self.on_reaction_add(emoji, user_id)

            if not self.remove_reaction_q.empty():
                emoji, user_id = self.remove_reaction_q.get()
                await self.on_reaction_remove(emoji, user_id)

        self.bot.remove_listener(self.reaction_add_listener, name="on_raw_reaction_add")
        self.bot.remove_listener(self.reaction_remove_listener, name="on_raw_reaction_remove")
        await self.end()

    async def add_reactions(self):
        """
        Adds the appropriate reactions to the poll message, and the cancel emoji to the emoji list,
        also names the general reaction role (role you get from reacting to anything after the title
        """
        for emoji in self.emoji_list:
            await self.message.add_reaction(emoji)
        return self

    @property
    def embed(self):
        embed = discord.Embed(
            title=f"**{self.title}**",
            description=self.text,
            color=Colors.purple
        )
        embed.set_footer(text='React with the corresponding emoji!')

        return embed

    def stop_condition(self, emoji: str, user_id: int):
        return (emoji == self.stop_emoji) and (user_id in [self.author.id, *SYSTEM_CONFIG['devs'].values()])

    async def reaction_add_listener(self, payload: discord.RawReactionActionEvent):  # listener
        if payload.message_id == self.message.id and payload.user_id != self.message.author.id:
            self.add_reaction_q.put((str(payload.emoji), payload.user_id))

    async def reaction_remove_listener(self, payload: discord.RawReactionActionEvent):  # listener
        if payload.message_id == self.message.id and payload.user_id != self.message.author.id:
            self.remove_reaction_q.put((str(payload.emoji), payload.user_id))

    @staticmethod
    async def loadall(bot) -> List["PollBase"]:
        """
        This iterates through all of the cached polls in `cache/polls`, un-pickles them, and adds
        back the context attributes. Then it returns the list of polls to be run

        :param bot: Client connection to discord
        :type bot: Object
        :return: A list of the cached polls
        :rtype: List[ReactionRolePoll]
        """
        # try:
        await bot.wait_until_ready()
        poll_list = []
        file_list = sorted(os.listdir('cache/polls'))

        for num, file in enumerate(file_list):
            with open('cache/polls/' + file, 'rb') as pickle_file:
                poll_list.append(pickle.load(pickle_file))

            poll_list[num].bot = bot
            await poll_list[num].load_context_data()
        return poll_list

    @classmethod
    async def runall(cls, bot):
        """
        Runs all of the cached polls. This should be called on startup, by creating a task with
        `bot`. It will unpickle all of the polls, then run them and they will behave like normal.

        :param bot: Client connection to discord
        :type bot: Object
        """
        await bot.wait_until_ready()
        poll_list = await cls.loadall(bot)
        for poll in poll_list:
            await poll.on_bot_start()
            bot.loop.create_task(poll.loop())
            print("running poll: ", poll.title)

    @property
    def emoji_list(self) -> List[str]:
        return self.raw_emoji_list + [self.stop_emoji]

    @property
    def text_list(self) -> List[str]:
        return self.raw_text_list + [f"End poll ({self.author.mention})"]

    @property
    def end_text(self) -> str:
        return self.text

    @property
    def text(self) -> str:
        return "\n".join([f"{e} - {t}" for e, t in zip(self.emoji_list, self.text_list)])

    async def on_bot_start(self):
        for reaction in self.message.reactions:
            async for user in reaction.users():
                if user.id != SYSTEM_CONFIG['self']:
                    await self.on_reaction_add(str(reaction), user.id)

    async def clean_up(self):
        pass

    async def set_up(self):
        pass

    async def on_reaction_add(self, emoji: str, user_id: id):
        pass

    async def on_reaction_remove(self, emoji: str, user_id: int):
        pass

    async def load_context_data(self):
        self.remove_reaction_q = Queue()
        self.add_reaction_q = Queue()

        channel = self.bot.get_channel(self.save_data["channel_id"])
        self.message = await channel.fetch_message(self.save_data["message_id"])
        self.author = channel.guild.get_member(self.save_data["author_id"])

    def remove_context_data(self):
        self.save_data.update({
            "channel_id": self.message.channel.id,
            "author_id": self.author.id,
            "message_id": self.message.id
        })
        self.message = None
        self.author = None

    async def init(self):
        pass
