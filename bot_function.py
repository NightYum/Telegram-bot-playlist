import os.path
import json


class File:  #Класс FILE
    def __init__(self, name: str):
        self.name = name

    def read(self):
        with open(self.name, mode='r') as document:
            text = document.read().split()
        return text

    def append(self, text: str, mode='a'):  #Добавить проверку файлов
        if mode == 'a':
            with open(self.name, mode='a') as document:
                document.write(text+'\n')
        else:
            with open(self.name, mode='w') as document:
                document.write(text+'\n')

    def delete_value(self, text: int):
        with open(self.name, mode='r') as document:
            list_text = document.read().split()
        text = str(text)
        list_text = [user_id for user_id in list_text if user_id != text]
        with open(self.name, mode='w') as document:
            for user_id in list_text:
                document.write(user_id + '\n')

    def clear(self):
        with open(self.name, mode='w') as document:
            document.write('')


class JsonDb:
    def __init__(self, name: str = "DATABASE"):
        self.db_name = name + ".json"
        structure_database = {
            "user": {
            }
        }
        if not os.path.exists(self.db_name):
            with open(self.db_name, mode="w") as file:
                json.dump(structure_database, file, indent="\t")
            print("db created")
        print("db exists")

    def read(self) -> dict:
        with open(self.db_name, mode="r") as file:
            db = json.load(file)
        return db

    def append(self, data):
        with open(self.db_name, mode="w") as file:
            json.dump(data, file, indent="\t")

    def verify_user(self, user_id: str) -> bool:
        db = self.read()
        if user_id not in db["user"]:
            return True
        return False

    def add_user_info(self, user_id: str, first_name: str, last_name: str, user_name: str):
        db = self.read()
        db["user"][user_id] = {
            "first_name": None,
            "last_name": None,
            "user_name": None,
        }
        self.append(data=db)
        db["user"][user_id]["first_name"] = first_name
        db["user"][user_id]["last_name"] = last_name
        db["user"][user_id]["user_name"] = user_name
        db["user"][user_id]["playlist"] = []
        self.append(data=db)

    def add_playlist(self, user_id: str, playlist_name: str, count_video: str, count_viewed: str, count_vid_in_day: str, count_left_video: str, count_day: str):
        db = self.read()
        playlist = {
            "playlist_name": playlist_name,
            "count_video": count_video,
            "count_viewed": count_viewed,
            "count_vid_in_day": count_vid_in_day,
            "count_left_video": count_left_video,
            "count_day": count_day
        }
        db["user"][user_id]["playlist"].append(playlist)
        self.append(data=db)

    def view_playlist(self, user_id: str, playlist_id: int) -> dict:
        db = self.read()
        playlist = db["user"][user_id]["playlist"][playlist_id]
        return playlist

    def delete_playlist(self, user_id: str, playlist_id: int) -> None:
        db = self.read()
        db["user"][user_id]["playlist"].pop(playlist_id)
        self.append(data=db)

    def update_playlist(self, user_id: str, playlist_id: int, count_viewed_today: int) -> None:
        db = self.read()
        count_viewed = db["user"][user_id]["playlist"][playlist_id]["count_viewed"] + count_viewed_today
        count_left_video = db["user"][user_id]["playlist"][playlist_id]["count_left_video"] - count_viewed_today
        db["user"][user_id]["playlist"][playlist_id]["count_viewed"] = count_viewed
        db["user"][user_id]["playlist"][playlist_id]["count_left_video"] = count_left_video
        db["user"][user_id]["playlist"][playlist_id]["count_day"] = count_left_video / db["user"][user_id]["playlist"][playlist_id]["count_vid_in_day"]
        self.append(data=db)

    def get_len_playlist(self, user_id: str) -> int:
        db = self.read()
        len_playlist = len(db["user"][user_id]["playlist"])
        return len_playlist

    def get_playlist_names(self, user_id: str) -> list:
        db = self.read()
        playlist_names = []
        for sub_playlist in db["user"][user_id]["playlist"]:
            playlist_names.append(sub_playlist["playlist_name"])
        return playlist_names
# mode = "a" if os.path.exists(db_name) else "m"



