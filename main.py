from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message
from responses import getResponse

load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

intents: Intents = Intents.default()
intents.message_content() = True
client: Client = Client(intents=intents)

async def sendMessage(message: Message, userMessage: str) -> None:
    if not userMessage:
        print("The message was empty because intents were not enable properly")
        return

    if isPrivate :=userMessage[0] == '?':
        userMessage = userMessage[1:]
        
    try:
        response: str = getResponse(userMessage)
        await message.author.send(response) if isPrivate else message.channel.send(response)
    except Exception as e:
        print(e)