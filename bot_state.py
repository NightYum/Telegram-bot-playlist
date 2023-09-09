from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage

storage = MemoryStorage()


class CreatePlaylist(StatesGroup):
    playlist_name = State()
    count_video = State()
    count_viewed = State()
    count_vid_in_day = State()


class ChoosePlaylist(StatesGroup):
    choose_playlist = State()


class DeletePlaylist(StatesGroup):
    delete_playlist = State()


class UpdatePlaylist(StatesGroup):
    choose_playlist = State()
    update_playlist = State()

