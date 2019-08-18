import asyncio

from aiohttp import web
from aiomotorengine import connect

from core.methods import reload_web_hook
from core.processing import process_response
from settings import APPLICATION_SECRET, DB_NAME, DB_HOST
from utils.logic import get_chat, get_message

routes = web.RouteTableDef()
loop = asyncio.get_event_loop()
connect(DB_NAME, host=DB_HOST, io_loop=loop)


@routes.post(f'/{APPLICATION_SECRET}')
async def handler(request):
    request_json = await request.json()
    return await process_response(
        chat=await get_chat(request_json),
        message=await get_message(request_json)
    )

app = web.Application()
app.add_routes(routes)


if __name__ == '__main__':
    asyncio.run(reload_web_hook())
    web.run_app(app)
