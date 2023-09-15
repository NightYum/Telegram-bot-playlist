from aiogram import Bot, executor, types
from aiogram.dispatcher import Dispatcher, FSMContext
from datetime import datetime
import asyncio


from bot_function import *
from bot_keyboard import *
from bot_config import *
from bot_state import *

bot = Bot(TOKEN_API)
dp = Dispatcher(bot, storage=storage)
DATABASE = JsonDb(name="DATABASE")


# Старт
@dp.message_handler(commands=["start"])
async def cmd_start(msg: types.Message):
    await msg.delete()
    await msg.answer(text="Добро пожаловать! Здесь вы сможете отслеживать прогресс по плейлистам в YouTube. Удачи! - /help", reply_markup=start_kb())
    user_id = msg.from_user.id
    if DATABASE.verify_user(user_id=user_id):
        first_name = msg.from_user.first_name
        last_name = msg.from_user.last_name
        user_name = msg.from_user.username
        DATABASE.add_user_info(user_id=user_id,
                               first_name=first_name,
                               last_name=last_name,
                               user_name=user_name)
    while True:
        await asyncio.sleep(1)
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        if current_time == '08:00:00':
            await msg.answer(text="Доброе утро! Сегодня вы должны посмотреть 4 видео, удачи!")
        elif current_time == '12:00:00':
            await msg.answer(text="Уже половина дня, сколько видео вы успели посмотреть? - /update")
        elif current_time == '21:00:00':
            await msg.answer(text="Ночь, сколько видео вы успели посмотреть? - /update")


# Помощь
@dp.message_handler(commands=["help"])
async def cmd_help(msg: types.Message):
    await msg.answer(text=HELP_COMMAND)


# Создание
@dp.message_handler(commands=["add"])
async def cmd_test_set(msg: types.Message):
    await msg.delete()
    await msg.answer(text="Первым делом введите название плейлиста", reply_markup=types.ReplyKeyboardRemove())
    await CreatePlaylist.playlist_name.set()


@dp.message_handler(state=CreatePlaylist.playlist_name)
async def cmd_create_playlist_next(msg: types.Message, state: FSMContext):
    user_text = str(msg.text)
    if len(user_text) > 25:
        await msg.answer(text="Максимальная длина названия 25, введите данные снова - /add")
        await state.finish()
    else:
        await state.update_data(playlist_name=msg.text)
        await msg.answer(text="Сколько видео в плейлисте?")
        await CreatePlaylist.next()


@dp.message_handler(state=CreatePlaylist.count_video)
async def cmd_test_hand(msg: types.Message, state: FSMContext):
    try:
        user_text = int(msg.text)
        await state.update_data(count_video=user_text)
        await msg.reply(text=f"Сколько видео вы посмотрели?")
        await CreatePlaylist.next()
    except ValueError:
        await msg.answer(text="Вы ввели неверные данные")
        await state.finish()


@dp.message_handler(state=CreatePlaylist.count_viewed)
async def cmd_test_hand(msg: types.Message, state: FSMContext):
    try:
        user_text = int(msg.text)
        await state.update_data(count_viewed=user_text)
        await msg.reply(text=f"Сколько видео нужно смотреть в день?")
        await CreatePlaylist.next()
    except ValueError:
        await msg.answer(text="Вы ввели неверные данные")
        await state.finish()


@dp.message_handler(state=CreatePlaylist.count_vid_in_day)
async def cmd_test_hand(msg: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data["count_vid_in_day"] = int(msg.text)
            data["count_left_video"] = data["count_video"] - data["count_viewed"]
            data["count_day"] = data["count_left_video"] / data["count_vid_in_day"]
            DATABASE.add_playlist(
                user_id=str(msg.from_user.id),
                playlist_name=data["playlist_name"],
                count_video=data["count_video"],
                count_viewed=data["count_viewed"],
                count_vid_in_day=data["count_vid_in_day"],
                count_left_video=data["count_left_video"],
                count_day=data["count_day"]
            )
        await msg.answer(text="Вы создали новую статистику по плейлисту. /view - чтобы увидеть ее", reply_markup=start_kb())
        await state.finish()
    except ValueError:
        await msg.answer(text="Вы ввели неверные данные")
        await state.finish()


# Удаление
@dp.message_handler(commands=["delete"])
async def cmd_delete_playlist_set(msg: types.Message):
    user_id = msg.from_user.id
    if DATABASE.get_len_playlist(user_id=user_id) == 0:
        await msg.answer(text="У вас нет плейлистов, создайте его - /add")
    elif DATABASE.get_len_playlist(user_id=user_id) == 1:
        DATABASE.delete_playlist(user_id=user_id, playlist_id=0)
        await msg.answer(text="Удаление завершено удачно, чтобы это проверить - /view")
    else:
        playlist_names = DATABASE.get_playlist_names(user_id=user_id)
        await msg.answer(text=f"Ваши плейлисты:\n" + '\n'.join(playlist_names) + "\nВведите номер, чтобы удалить :/")
        await DeletePlaylist.delete_playlist.set()


@dp.message_handler(state=DeletePlaylist.delete_playlist)
async def cmd_delete_playlist_hand(msg: types.Message, state: FSMContext):
    try:
        user_id = msg.from_user.id
        user_text = int(msg.text) - 1
        len_playlist = DATABASE.get_len_playlist(user_id=user_id)
        if user_text <= len_playlist:
            playlist_id = int(msg.text)-1
            DATABASE.delete_playlist(user_id=user_id, playlist_id=playlist_id)
            await msg.answer(text="Удаление завершено удачно, чтобы это проверить - /view")
            await state.finish()
        else:
            await msg.answer(text="У вас не так много плейлистов, введите заново - /delete")
            await state.finish()
    except ValueError:
        await msg.answer(text="Вы ввели неверные данные")
        await state.finish()


# Просмотр
@dp.message_handler(commands=["view"])
async def cmd_view_playlist_set(msg: types.Message):
    user_id = msg.from_user.id
    playlist_names = DATABASE.get_playlist_names(user_id=user_id)
    len_playlist = DATABASE.get_len_playlist(user_id=user_id)
    if len_playlist == 0:
        await msg.answer(text="У вас нет плейлистов, чтобы создать - /add")
    elif len_playlist == 1:
        await msg.answer(text=f"Ваш плейлист: " + playlist_names[0])
    else:
        await msg.answer(text=f"Ваши плейлисты:\n" + '\n'.join(playlist_names))


# Детальный просмотр
@dp.message_handler(commands=["view_detail"])
async def cmd_view_detail_static_set(msg: types.Message):
    user_id = msg.from_user.id
    len_playlist = DATABASE.get_len_playlist(user_id=user_id)
    if len_playlist == 0:
        await msg.answer(text="У вас нет плейлистов, создайте его - /add")
    elif len_playlist == 1:
        playlist = DATABASE.view_playlist(user_id=user_id, playlist_id=0)
        await msg.answer(text=f"У вас один плейлист {playlist['playlist_name']}, его данные:\n"
                              f"Всего видео:  {playlist['count_video']}\n"
                              f"Просмотрено:  {playlist['count_viewed']}\n"
                              f"Видео в день:  {playlist['count_vid_in_day']}\n"
                              f"Осталось посмотреть:  {playlist['count_left_video']}\n"
                              f"Осталось дней смотреть:  {playlist['count_day']}"
                         )
    else:
        playlist_names = DATABASE.get_playlist_names(user_id=user_id)
        await msg.answer(text=f"Ваши плейлисты:\n" + '\n'.join(
            playlist_names) + "\nВведите номер, чтобы посмотреть его статистику :)")
        await ChoosePlaylist.choose_playlist.set()


@dp.message_handler(state=ChoosePlaylist.choose_playlist)
async def cmd_view_detail_static_hand(msg: types.Message, state: FSMContext):
    try:
        user_id = msg.from_user.id
        user_text = int(msg.text) - 1
        len_playlist = DATABASE.get_len_playlist(user_id=user_id)
        if user_text <= len_playlist:
            playlist = DATABASE.view_playlist(user_id=user_id, playlist_id=user_text)
            await msg.answer(text=f"Вы выбрали плейлист {playlist['playlist_name']}, его данные:\n"
                                  f"Всего видео:  {playlist['count_video']}\n"
                                  f"Просмотрено:  {playlist['count_viewed']}\n"
                                  f"Видео в день:  {playlist['count_vid_in_day']}\n"
                                  f"Осталось посмотреть:  {playlist['count_left_video']}\n"
                                  f"Осталось дней смотреть:  {playlist['count_day']}")
            await state.finish()
        else:
            await msg.answer(text="У вас не так много плейлистов, введите заново - /delete")
            await state.finish()
    except ValueError:
        await msg.answer(text="Вы ввели неверные данные")
        await state.finish()


#  Обновление
@dp.message_handler(commands=["update"])
async def cmd_update_data_set(msg: types.Message):
    user_id = msg.from_user.id
    playlist_names = DATABASE.get_playlist_names(user_id=user_id)
    await msg.answer(text=f"Ваши плейлисты:\n" + '\n'.join(playlist_names) + "\nКакой из них вы хотите обновить?")
    await UpdatePlaylist.choose_playlist.set()


@dp.message_handler(state=UpdatePlaylist.choose_playlist)
async def cmd_update_playlist_hand_set(msg: types.Message, state: FSMContext):
    try:
        user_id = msg.from_user.id
        user_text = int(msg.text) - 1
        len_playlist = DATABASE.get_len_playlist(user_id=user_id)
        if user_text <= len_playlist:
            playlist_id = int(msg.text) - 1
            await msg.answer(text="Сколько видео вы сегодня посмотрели?")
            async with state.proxy() as data:
                data["playlist_id"] = playlist_id
            await UpdatePlaylist.next()
    except ValueError:
        await msg.answer(text="Вы ввели неверные данные, начните заново - /update")
        await state.finish()


@dp.message_handler(state=UpdatePlaylist.update_playlist)
async def cmd_update_data_hand(msg: types.Message, state: FSMContext):
    try:
        user_id = msg.from_user.id
        count_viewed_today = int(msg.text)
        async with state.proxy() as data:
           DATABASE.update_playlist(user_id=user_id, playlist_id=data["playlist_id"], count_viewed_today=count_viewed_today)
        await state.update_data(upadate_playlist=count_viewed_today)
        await state.finish()
        await msg.answer(text="Вы обновили статистику, чтобы ее проверить - /view_detail")
    except ValueError:
        await msg.answer(text="Вы ввели неверные данные, начните заново - /update")
        await state.finish()

if __name__ == "__main__":
    executor.start_polling(dp,
                           on_startup=print("BOT STARTED"),
                           skip_updates=True
                           )

# Запись файлов пользователя, статистика, рейнтинг получение по ссылке сколько осталось в процентах
# улучшить вывод данных, красоту в чате, улучшить сохранение статистики и её проверку, при state подготовить выходы и проверку данных
# Обновление данных
