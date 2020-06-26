from typing import List

from classes.poll import PollBase
from extras import SYSTEM_CONFIG


class SetupPoll(PollBase):
    def __init__(self, author, bot):
        super(SetupPoll, self).__init__(["✅", "❌"], [], author, "Subscribe to Auto-Announcements",
                                        bot)
        self.stop_emoji = ""
        self.stop = False

    async def unsubscribe(self):
        """
        It removes the channel from the config, if it hasn't been already
        """
        if self.message.channel.id not in SYSTEM_CONFIG['channels']:
            await self.message.channel.send("This channel is not subscribed to the announcements")

        else:
            for index, channel_id in enumerate(SYSTEM_CONFIG['channels']):
                if channel_id == self.message.channel.id:
                    del SYSTEM_CONFIG['channels'][index]
                    SYSTEM_CONFIG.write()
                    await self.message.channel.send("This channel has now been unsubscribed from "
                                                    "the announcements")
        self.stop = True

    async def subscribe(self):
        """
        This adds the channel to config if it isn't on already
        """
        if self.message.channel.id in SYSTEM_CONFIG['channels']:
            await self.message.channel.send(
                "This channel is already subscribed to the announcements")
        else:
            SYSTEM_CONFIG['channels'].append(self.message.channel.id)
            SYSTEM_CONFIG.write()
            await self.message.channel.send("This channel is now subscribed to the announcements")
        self.stop = True

    async def on_reaction_add(self, emoji: str, user_id: id):
        if user_id == self.author.id and emoji in self.emoji_list:
            if emoji == "✅":
                await self.subscribe()
            elif emoji == "❌":
                await self.unsubscribe()
            else:
                raise RuntimeError(f"Somehow got reaction {emoji}")
        else:
            await self.message.remove_reaction(emoji, self.bot.ge)

    @property
    def text(self) -> str:
        return "Do you want to subscribe (✅) or unsubscribe (❌) from the auto-announcements?"

    def stop_condition(self, emoji: str, user_id: int):
        return self.stop

    @property
    def emoji_list(self) -> List[str]:
        return self.raw_emoji_list
