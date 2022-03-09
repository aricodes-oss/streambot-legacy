import discord
from streambot.db import MemberReservation, MemberStream
from streambot.discord import client
from streambot.logging import logger


async def reconcile_presence(member):
    logger.info(member)
    existing_messages = MemberStream.select().where(MemberStream.member_id == member.id)

    # If the user is not streaming, we want to clear any mention of that
    if not member.status == discord.Status.streaming:
        for message in existing_messages:
            reservation = message.reservation

            guild = await client.fetch_guild(reservation.guild_id)
            channel = await guild.fetch_channel(reservation.channel_id)
            dmessage = await channel.fetch_message(message.message_id)

            await dmessage.delete()
