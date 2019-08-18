
async def is_russian(word: str):
    """ Проверка: является ли слово русским """
    rus_alphabet = {
        'а', 'б', 'в', 'г', 'д', 'е', 'ж', 'з',
        'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п',
        'р', 'с', 'т', 'у', 'ф', 'х', 'ц', 'ч',
        'ш', 'щ', 'ъ', 'э', 'ю', 'я'
    }
    pattern = word.lower()
    for alpha in rus_alphabet:
        if alpha in pattern:
            return True
    return False


async def get_chat(request):
    return request['message']['chat']


async def get_message(request):
    return request['message']['text']
