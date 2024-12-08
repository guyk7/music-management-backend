from pymongo import MongoClient
from bson.objectid import ObjectId

class Database:
    def __init__(self, host='localhost', port=27017):  # Updated to 'localhost'
        self.client = MongoClient(host, port)
        self.db = self.client['music_db']
        self.singers_collection = self.db['singers']
        self.songs_collection = self.db['songs']

    def add_singer(self, name, genre):
        singer = {'name': name, 'genre': genre, 'songs': []}
        return self.singers_collection.insert_one(singer).inserted_id

    def get_all_singers(self):
        return list(self.singers_collection.find())

    def get_singer_by_id(self, singer_id):
        return self.singers_collection.find_one({'_id': ObjectId(singer_id)})

    def add_song_to_singer(self, singer_id, title, year, album):
        song = {'title': title, 'year': year, 'album': album, 'singer_id': ObjectId(singer_id)}
        song_id = self.songs_collection.insert_one(song).inserted_id
        self.singers_collection.update_one({'_id': ObjectId(singer_id)}, {'$push': {'songs': song_id}})
        return song_id

    def get_songs_by_singer(self, singer_id):
        return list(self.songs_collection.find({'singer_id': ObjectId(singer_id)}))

    def delete_singer(self, singer_id):
        self.singers_collection.delete_one({'_id': ObjectId(singer_id)})
        self.songs_collection.delete_many({'singer_id': ObjectId(singer_id)})

    def delete_song(self, song_id):
        self.songs_collection.delete_one({'_id': ObjectId(song_id)})
        self.singers_collection.update_many({}, {'$pull': {'songs': ObjectId(song_id)}})
