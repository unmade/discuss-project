import argparse
import asyncio

import requests
from centrifuge import Client, Credentials


async def run(username, token_url, ws_url, content_type_id, object_id):
    data = {'username': username, 'email': f'{username}@example.com'}
    response = requests.post(token_url, data=data)
    content = response.json()

    credentials = Credentials(username, content['timestamp'], '', content['token'])

    async def connect_handler(**kwargs):
        print(f'Connected {kwargs}')

    async def disconnect_handler(**kwargs):
        print(f'Disconnected: {kwargs}')

    async def connect_error_handler(**kwargs):
        print(f'Error: {kwargs}')

    client = Client(
        ws_url,
        credentials,
        on_connect=connect_handler,
        on_disconnect=disconnect_handler,
        on_error=connect_error_handler
    )

    await client.connect()

    async def message_handler(**kwargs):
        print(f'Message: {kwargs}')

    async def join_handler(**kwargs):
        print(f'Join: {kwargs}',)

    async def leave_handler(**kwargs):
        print(f'Leave: {kwargs}')

    async def error_handler(**kwargs):
        print(f'Sub error: {kwargs}')

    channel = await client.subscribe(
        f'thread:{content_type_id}_{object_id}',
        on_message=message_handler,
        on_join=join_handler,
        on_leave=leave_handler,
        on_error=error_handler
    )

    print('History:', await channel.history())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--username', type=str, default='fdooch')
    parser.add_argument('--token_url', type=str, default='http://localhost/users/token/')
    parser.add_argument('--ws_url', type=str, default='ws://localhost/centrifugo/connection/websocket')
    parser.add_argument('--content_type_id', type=int, default=1)
    parser.add_argument('--object_id', type=int, default=1)
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    asyncio.ensure_future(run(args.username, args.token_url, args.ws_url, args.content_type_id, args.object_id))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print('interrupted')
    finally:
        loop.close()
