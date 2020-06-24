# tgfilestream - A Telegram bot that can stream Telegram files to users over HTTP.
# Copyright (C) 2019 Tulir Asokan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.'
import logging

from telethon import TelegramClient, events

from .paralleltransfer import ParallelTransferrer
from .config import (
    session_name,
    api_id,
    api_hash,
    public_url,
    start_message,
    group_chat_message
)
from .util import pack_id, get_file_name

log = logging.getLogger(__name__)

client = TelegramClient(session_name, api_id, api_hash)
transfer = ParallelTransferrer(client)


@client.on(events.NewMessage)
async def handle_message(evt: events.NewMessage.Event) -> None:
    if not evt.is_private:
        await evt.reply(group_chat_message)
        return
    if not evt.file:
        if evt.message.message.startswith("/start "):
            file_id = evt.message.message.split(" ", maxsplit=1)[1]
            peer, msg_id = unpack_id(int(file_id))
            if not peer or not msg_id:
                await evt.reply(start_message)
            else:
                message = cast(Message, await client.get_messages(entity=peer, ids=msg_id))
                await evt.reply(message)
        else:
            await evt.reply(start_message)
        return
    file_id = str(pack_id(evt))
    url = public_url / file_id / get_file_name(evt)
    rep_message = ""
    rep_message += f"Link to download file: {url}\n\n"
    my_username_e = await evt.client.get_me()
    my_username = my_username_e.username
    rep_message += f"Shareable Telegram Link: https://t.me/{my_username}?start={file_id}"
    await evt.reply(rep_message)
    log.info(f"Replied with link for {evt.id} to {evt.from_id} in {evt.chat_id}")
    log.debug(f"Link to {evt.id} in {evt.chat_id}: {url}")
