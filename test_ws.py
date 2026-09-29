import asyncio, websockets, json

async def test():
    try:
        async with websockets.connect('ws://localhost:8000/ws/test123') as ws:
            print('Connected!')
            msg = await ws.recv()
            print('Welcome:', json.loads(msg)['content'][:80])
            await ws.send(json.dumps({'type': 'message', 'content': 'Hey Kurumi, did you finish your homework?'}))
            for i in range(3):
                msg = await ws.recv()
                data = json.loads(msg)
                print(f'Turn {i+1}: {data["content"][:120]}')
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

asyncio.run(test())