import random

from core.commands import get_leaders, upload_music, start_game
from core.methods import send_message, send_audio
from core.models import Player, Music

DEFAULT_MSG = (
    'Чтобы начать игру, выберите команду /game\n'
    'Посмотреть список лидеров: /leaderboard'
)


COMMANDS = dict(
    leaderboard=get_leaders,
    upload_sudo_zx=upload_music,
    game=start_game
)


async def process_response(chat, message):
    chat_id = chat['id']
    if message.startswith('/'):
        return await execute_command(chat, message)

    else:
        # Пришла не команда, значит либо ответ, либо какая-то ерунда
        player = await Player.get_player_by_chat(chat_id)
        if not player or not player.active:
            return await send_message(chat_id, DEFAULT_MSG)

        if player.progress.current == message:
            return await promote_player(player, chat_id)
        else:
            return await deactivate_player(player, chat_id)


async def execute_command(chat, message):
    command = message.lstrip('/')
    if command not in COMMANDS:
        return await send_message(chat['id'], DEFAULT_MSG)

    return await COMMANDS[command](chat)


async def promote_player(player, chat_id):
    player.inc_score()
    # Получение нового неповторяющегося трека
    track = await Music.get_random_track(player.get_passed_tracks_ids())
    if not track:
        msg = (
            'Вы абсолютный чемпион! Весь музыкальный репертуар кончился.\n'
            f'Ваши очки: {player.score}\n'
            'Посмотреть список лидеров: /leaderboard\n\n'
            'Сыграем снова?? /game'
        )
        await player.deactivate()
        return await send_message(chat_id, msg)

    player.progress.current = track.right
    player.progress.passed.append(str(track._id))
    await player.save()
    random.shuffle(track.answers)

    msg = f'Верно! Ваши очки: {player.progress.score}.  Играем дальше!!'
    await send_message(chat_id, msg)
    return await send_audio(chat_id, track.file, track.answers)


async def deactivate_player(player, chat_id):
    session_score = player.progress.score if player.progress else 0
    await player.deactivate()
    msg = (
        f'Вы не угадали. Набранные очки: {session_score}!\n'
        f'Ваш лучший счёт: {player.score}!\n'
        f'Но возможно Вы новый чемпион! Посмотрим?: /leaderboard\n\n'
        f'Сыграем снова?? /game'
    )
    return await send_message(chat_id, msg)
