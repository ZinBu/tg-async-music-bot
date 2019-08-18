import random

from core.methods import send_message, send_audio, load_audio
from core.models import Player, Music, ProgressEmbedded, Storage


async def start_game(chat):
    player = await Player.get_player_by_chat(chat['id'])
    if not player:
        player = await Player.create_player(chat)

    if player.active:
        return await send_message(chat['id'], 'Уже в игре!', False)

    track = await Music.get_random_track()
    player.active = True
    player.progress = ProgressEmbedded(
        current=track.right,
        passed=[str(track._id)]
    )
    await player.save()
    random.shuffle(track.answers)
    return await send_audio(chat['id'], track.file, track.answers)


async def get_leaders(chat):
    board = await Player.show_leader_board()
    msg = board or 'Пока таблица пуста!'
    return await send_message(chat['id'], msg, remove_markup=False)


async def upload_music(chat):
    exists_music = {x.right: x for x in await Music.objects.find_all()}
    storage = await Storage.objects.find_all()
    if not storage:
        return await send_message(chat['id'], 'Нечего загружать.')

    music = []
    for track in storage:
        result = await load_audio(chat['id'], track.binary)
        exists_track = exists_music.get(track.right)
        if exists_track:
            exists_track.file = result['result']['audio']['file_id']
            await exists_track.save()
        else:
            music.append(
                Music(
                    right=track.right,
                    answers=track.answers,
                    file=result['result']['audio']['file_id']
                )
            )
        await track.delete()

    await Music.objects.bulk_insert(music)
    return await send_message(chat['id'], f'Все загружено. {len(music)}')
