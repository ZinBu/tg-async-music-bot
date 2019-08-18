import asyncio

from core.methods import reload_web_hook


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(reload_web_hook())
    loop.close()
