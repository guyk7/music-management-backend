from flask import Flask, request, jsonify
from database import Database
from bson.objectid import ObjectId

app = Flask(__name__)
db = Database()

@app.route('/singers', methods=['GET', 'POST'])
def manage_singers():
    if request.method == 'POST':
        data = request.json
        singer_id = db.add_singer(data['name'], data['genre'])
        return jsonify({'id': str(singer_id)})
    elif request.method == 'GET':
        singers = db.get_all_singers()
        return jsonify([
            {
                '_id': str(singer['_id']),
                'name': singer['name'],
                'genre': singer['genre'],
                'songs': [str(song_id) for song_id in singer['songs']]
            }
            for singer in singers
        ])

@app.route('/singers/<singer_id>/songs', methods=['GET', 'POST'])
def manage_songs(singer_id):
    if request.method == 'POST':
        data = request.json
        song_id = db.add_song_to_singer(
            singer_id, data['title'], data['year'], data['album']
        )
        return jsonify({'id': str(song_id)})
    elif request.method == 'GET':
        songs = db.get_songs_by_singer(singer_id)
        return jsonify([
            {
                '_id': str(song['_id']),
                'title': song['title'],
                'year': song['year'],
                'album': song['album']
            }
            for song in songs
        ])

@app.route('/singers/<singer_id>', methods=['DELETE'])
def delete_singer(singer_id):
    result = db.singers_collection.delete_one({"_id": ObjectId(singer_id)})
    db.songs_collection.delete_many({"singer_id": ObjectId(singer_id)})
    if result.deleted_count == 1:
        return jsonify({'message': 'Singer deleted successfully'}), 200
    else:
        return jsonify({'error': 'Singer not found'}), 404

@app.route('/singers/<singer_id>/songs/<song_id>', methods=['DELETE'])
def delete_song(singer_id, song_id):
    result = db.songs_collection.delete_one({"_id": ObjectId(song_id)})
    if result.deleted_count == 1:
        db.singers_collection.update_one(
            {"_id": ObjectId(singer_id)},
            {"$pull": {"songs": ObjectId(song_id)}}
        )
        return jsonify({'message': 'Song deleted successfully'}), 200
    else:
        return jsonify({'error': 'Song not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
