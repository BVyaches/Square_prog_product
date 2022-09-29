from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from main import translate_to_users_lang, auto_check_type, set_accuracy, database, LANGCODES


async def main_keyboard(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                         one_time_keyboard=True, row_width=1)

    buttons = [translate_to_users_lang('Посчитать с заданной точностью', message) + '.', '🌎⚙️']
    keyboard.add(*buttons)
    return keyboard


async def language_keyboard(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ['Русский', 'English', '汉语', 'Español ', 'हिन्दी', translate_to_users_lang('Другой', message)]
    keyboard.add(*buttons)
    return keyboard


async def start_bot(message: types.Message):
    keyboard = await main_keyboard(message)
    await message.answer(
        translate_to_users_lang(
            'Добро пожаловать в бот-калькулятор корней! '
            'Я умею вычислять квадратный корень из практически любого выражения или числа.\n'
            'Чтобы посчитать любое выражение, просто отравьте его ответным сообщением, '
            'или нажмите на предложенную слева кнопку на клавиатуре, '
            'чтобы задать точность вычислений количеством знаков после запятой.\n'
            'Чтобы поменять язык нажмите кнопку "🌎⚙️".'
            'Техническая поддержка:\n@Vyaches_s\n8-992-224-70-47\nvsbolshagin@edu.hse.\n'
            'Техническая поддержка работает круглосуточно и на всех доступных языках.\n'
            'Приятного пользования!\n'
            'Для получения списка команд отправьте /commands',
            message),
        reply_markup=keyboard)


async def cancel_operation(message: types.Message, state: FSMContext):
    await state.finish()
    keyboard = await main_keyboard(message)
    await message.answer(translate_to_users_lang('Операция отменена', message), reply_markup=keyboard)


async def commands_list(message: types.Message, state: FSMContext):
    keyboard = await main_keyboard(message)
    await message.answer(
        translate_to_users_lang(
            'Список команд, доступных в программе:\n'
            '/start - начать общение с ботом\n'
            '/help - узнать возможности бота\n'
            '/commands - узнать список доступных команд\n'
            '/cancel - отменить текущую операцию, вернуться в главное меню\n'
            '/menu - вернуться в главное меню',
            message),
        reply_markup=keyboard)
    await state.finish()


async def get_menu(message: types.Message, state: FSMContext):
    await state.finish()
    keyboard = await main_keyboard(message)
    await message.answer(translate_to_users_lang('Вы вернулись в меню', message), reply_markup=keyboard)


async def help_list(message: types.Message, state: FSMContext):
    await state.finish()
    keyboard = await main_keyboard(message)
    await message.answer(translate_to_users_lang('Выражения, из который программа умеет извлекать корни:\n'
                                                 '1. Целые и вещественные числа\n2. Числа в экспоненциальной записи\n'
                                                 '3. Комплексные и отрицательные числа\n4. Выражения вида a**b, '
                                                 'где a - любое число или переменная, b-четный показатель степени\n'
                                                 '5. Аналитические выражения, например формула полного квадрата или '
                                                 'следствие основного тригонометрического тождества\n'
                                                 '6. Выражения вида a**b, где а - число, из которого нацело выделяется '
                                                 'квадратный корень, b - любое число или переменная\n'
                                                 'Для показа всех команд нажмите', message)+ ' /commands', reply_markup=keyboard)


class CalculateWithAccuracy(StatesGroup):
    waiting_for_accuracy = State()
    waiting_for_formula = State()


async def calculate_acccurate_first(message: types.Message):
    await message.answer(
        translate_to_users_lang('Введите желаемое количество знаков после запятой', message),
        reply_markup=types.ReplyKeyboardRemove())
    await CalculateWithAccuracy.waiting_for_accuracy.set()


async def calculate_acccurate_second(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer(translate_to_users_lang('Пожалуйста, введите целое число', message)
                             )
        return True
    accuracy = int(message.text)
    await state.update_data(waiting_for_accuracy=accuracy)

    await message.answer(translate_to_users_lang('Введите выражение', message),
                         reply_markup=types.ReplyKeyboardRemove())
    await CalculateWithAccuracy.waiting_for_formula.set()


async def calculate_acccurate_third(message: types.Message, state=FSMContext):
    result = auto_check_type(message.html_text.replace('<b>', '**').replace('</b>', '**'))
    if not result:
        await message.answer(translate_to_users_lang(
            'Похоже, Вы ошиблись при вводе, или калькулятор пока не умееет такое считать.'
            ' Попробуйте ввести ещё раз\n'
            'Для пожеланий пишите сюда: @Vyaches\nДля отмены нажмите', message) + ' /cancel',
                             reply_markup=types.ReplyKeyboardRemove())
        return True
    keyboard = await main_keyboard(message)
    if await state.get_state() is None:
        await message.answer(result, reply_markup=keyboard)
    else:
        data = await state.get_data()
        await message.answer(set_accuracy(result, data.get('waiting_for_accuracy')), reply_markup=keyboard)
    await state.finish()


class ChangingLanguage(StatesGroup):
    waiting_for_new_lang = State()
    setting_another_lang = State()


# Инициализация процесса смены языка
async def change_language_first(message: types.Message):
    keyboard = await language_keyboard(message)
    await message.answer(
        translate_to_users_lang('На клавиатуре выберите язык, на который хотите перевести программу\n'
                                'Если нужного языка нет, добавьте его, введя код языка, нажав на кнопку "Другой"',
                                message), reply_markup=keyboard)
    await ChangingLanguage.waiting_for_new_lang.set()


async def change_language_second(message: types.Message, state: FSMContext):
    langs = {'Русский': 'ru', 'English': 'en', '汉语': 'zh-cn', 'Español': 'es', 'हिन्दी': 'hi'}
    lang_code = langs.get(message.text)
    if lang_code == database.get(message.from_user.id):
        keyboard = await main_keyboard(message)
        await message.answer(translate_to_users_lang('Данный язык и так используется', message), reply_markup=keyboard)
        await state.finish()
    else:
        if lang_code:
            database[message.from_user.id] = lang_code
            keyboard = await main_keyboard(message)
            await message.answer(translate_to_users_lang('Вы успешно поменяли язык', message), reply_markup=keyboard)
            await state.finish()
        elif message.text == translate_to_users_lang('Другой', message):
            await message.answer(translate_to_users_lang('Введите код нужного языка в формате "en" или "ru".\n'
                                                         'Для отмены нажмите ', message) + ' /cancel')
            await ChangingLanguage.setting_another_lang.set()
        else:
            keyboard = await language_keyboard(message)
            await message.answer(
                translate_to_users_lang('Выберите на клавиатуре нужный язык или добавьте свой нажатием кнопки "Другой"',
                                        message),
                reply_markup=keyboard)
            return True


async def change_language_third(message: types.Message, state: FSMContext):
    if message.text.lower() not in LANGCODES.values():
        await message.answer(translate_to_users_lang(
            'Похоже, Вы ошиблись при вводе кода страны или данный код неверен.'
            ' Попробуйте ввести ещё раз код языка в формате по типу "en" или "ru".\n'
            'Для пожеланий пишите сюда: @Vyaches\nДля отмены нажмите ', message) + ' /cancel')
        return True

    new_lang_code = message.text.lower()
    if new_lang_code in [database.get(message.from_user.id), message.from_user.language_code]:
        keyboard = await main_keyboard(message)
        await message.answer(translate_to_users_lang('Данный язык и так используется', message), reply_markup=keyboard)

    else:
        database[message.from_user.id] = new_lang_code
        keyboard = await main_keyboard(message)
        await message.answer(translate_to_users_lang('Вы успешно поменяли язык', message), reply_markup=keyboard)
    await state.finish()


# Регистрация всех команд и состояний вызова функций
def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(start_bot, commands='start', state='*')
    dp.register_message_handler(commands_list, commands='commands', state='*')
    dp.register_message_handler(help_list, commands='help', state='*')
    dp.register_message_handler(get_menu, commands='menu', state='*')
    dp.register_message_handler(cancel_operation, commands='cancel', state='*')
    dp.register_message_handler(cancel_operation, Text(equals='Отмена',
                                                       ignore_case=True),
                                state='*'),

    dp.register_message_handler(calculate_acccurate_first, Text(endswith='.', ignore_case=True), state='*'),
    dp.register_message_handler(calculate_acccurate_second, state=CalculateWithAccuracy.waiting_for_accuracy),
    dp.register_message_handler(calculate_acccurate_third, state=CalculateWithAccuracy.waiting_for_formula),

    dp.register_message_handler(change_language_first, Text(equals='🌎⚙️')),
    dp.register_message_handler(change_language_second, state=ChangingLanguage.waiting_for_new_lang),
    dp.register_message_handler(change_language_third, state=ChangingLanguage.setting_another_lang)
    dp.register_message_handler(calculate_acccurate_third, state=None),
