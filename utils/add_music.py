import os
import asyncio
import random

from aiomotorengine import connect

from core.models import Storage
from settings import DB_NAME, DB_HOST
from utils.logic import is_russian

MUSIC_PATH = 'music'


async def add_music_to_db():
    tracks = []
    for file in os.listdir(MUSIC_PATH):
        if file.split('.')[-1] == 'mp3':
            file_path = os.path.join(MUSIC_PATH, file)
            with open(file_path, 'rb') as f:
                track = Storage(
                    right=file[:-4],
                    binary=f.read()
                )
                tracks.append(track)

    await _generate_wrong_answers(tracks)
    await Storage.objects.bulk_insert(tracks)


async def _generate_wrong_answers(tracks):
    all_answers = [x.right for x in tracks]
    random.shuffle(all_answers)

    # Русские варианты
    answers_rus = [x for x in all_answers if await is_russian(x)]
    # Зарубежные
    answers_eng = [x for x in all_answers if not await is_russian(x)]

    # Добавление по 3 неверных ответа к каждой записи
    for track in tracks:
        wrong_answers = await _get_variants(track, answers_rus, answers_eng)
        track.answers = wrong_answers + [track.right]


async def _get_variants(track, answers_rus, answers_eng):
    wrong_answers = []
    # Определяем язык названия и исполнителя трека
    rus_lang = True if (await is_russian(track.right)) else False
    while len(wrong_answers) != 3:
        # Выбираем вариант случайным образом среди треков языка
        wrong_answer = (
            random.choice(answers_rus)
            if rus_lang
            else random.choice(answers_eng)
        )
        # Если ответ не совпадает с правильным
        # ответом текущей песни - записываем
        if wrong_answer != track.right and wrong_answer not in wrong_answers:
            wrong_answers.append(wrong_answer)

    return wrong_answers


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    connect(DB_NAME, host=DB_HOST, io_loop=loop)
    loop.run_until_complete(add_music_to_db())
    loop.close()
