import aiohttp
from aiohttp import web

from settings import APPLICATION_SECRET, APP_DOMAIN, TG_BOT_TOKEN


API_URL = f'https://api.telegram.org/bot{TG_BOT_TOKEN}/'


async def send_message(chat_id, text, remove_markup=True):
    url = API_URL + 'sendMessage'
    data = dict(chat_id=chat_id, text=text)
    if remove_markup:
        data.update(reply_markup=dict(remove_keyboard=True))

    response = await _post(url, data)
    return await _process_response(response)


async def send_audio(chat_id, file_id, reply_markup):
    url = API_URL + 'sendAudio'
    data = dict(
        chat_id=chat_id,
        audio=file_id,
        reply_markup=dict(
            one_time_keyboard=True,
            keyboard=[[x] for x in reply_markup]
        ),
        **(await _add_audio_meta())
    )
    response = await _post(url, data)
    return await _process_response(response)


async def load_audio(chat_id, file):
    url = API_URL + 'sendAudio'
    data = dict(
        chat_id=chat_id,
        audio=file,
        **(await _add_audio_meta())
    )
    return await _post(url=url, json=None, data=data, to_json=True)


async def reload_web_hook():
    await _remove_web_hook()
    await _set_web_hook()


async def _process_response(response):
    if response.status != 200:
        return web.Response(status=500)

    return web.Response(status=200)


async def _add_audio_meta():
    return dict(
        caption='Sample',
        performer='Sample',
        title='Sample'
    )


async def _post(url, json, data=None, to_json=False):
    body = dict(data=_prepare_form_data(data)) if data else dict(json=json)
    async with aiohttp.ClientSession(conn_timeout=30.) as session:
        async with session.post(url, **body) as response:
            return response if not to_json else await response.json()


def _prepare_form_data(params):
    data = aiohttp.formdata.FormData(quote_fields=False)
    for key, value in params.items():
        if key == 'audio':
            data.add_field(key, value, filename='sample.mp3')
        else:
            data.add_field(key, str(value))

    return data


async def _set_web_hook():
    url = API_URL + 'setWebhook'
    data = dict(url=f'{APP_DOMAIN}/{APPLICATION_SECRET}')
    return await _post(url, data)


async def _remove_web_hook():
    url = API_URL + 'deleteWebhook'
    return await _post(url, None)
