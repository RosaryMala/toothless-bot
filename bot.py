import discord
import asyncio
import logging
import os
import re
import sqlite3

logging.basicConfig(level=logging.INFO)
client = discord.Client()


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)


MODSTATE_STRING = "Please acknowledge (if appropriate to do so)."
async def parse_message(message):
    if message.content.startswith('/state '):
        target_channel = message.channel
        statecontent = message.content[7:].strip()
        maybematch = re.match(r'<#(\d+)>', statecontent)
        if maybematch:
            targetchannelid = maybematch.group(1)
            target_channel = client.get_channel(targetchannelid)
            statecontent = statecontent[maybematch.end():]

        pings = set(re.findall(r'<@!*\d+>', statecontent))
        separator = ' - ' if pings else ''
        content = f'{" ".join(pings)}{separator}{MODSTATE_STRING}'
        embed = discord.Embed(
            title='MOD STATEMENT',
            timestamp=message.timestamp,
            type='rich',
            description=statecontent,
            color=discord.Color.dark_red()
        )
        username = message.author.nick
        if not username:
            username = message.author.name
        avatarurl = message.author.avatar_url
        embed.set_footer(text=username, icon_url=avatarurl)
        await client.send_message(target_channel, content=content, embed=embed)


@client.event
async def on_message(message):
    for role in message.author.roles:
        if role.name == 'Protectorate':
            await parse_message(message)
            break

client.run(os.environ['BOTTOKEN'])
