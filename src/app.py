from os import name
from flask import Flask, jsonify, request, Response
from flask_pymongo import PyMongo
from bson import json_util
from bson.objectid import ObjectId
import json

from werkzeug.wrappers import response
from config import _secret_key, _db_mongo_uri


from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = _secret_key

app.config["MONGO_URI"] = _db_mongo_uri

mongo = PyMongo(app)


@app.route("/users", methods=["GET"])
def get_users():
    users = mongo.db.users.find()
    response = json_util.dumps(users)
    return Response(response, mimetype="application/json")


@app.route('/users/<id>', methods=['GET'])
def get_user(id):
    user = mongo.db.users.find_one({'_id': ObjectId(id), })
    response = json_util.dumps(user)
    return Response(response, mimetype="application/json")


@app.route('/users/<id>', methods=['DELETE'])
def delete_user(id):
    mongo.db.users.delete_one({'_id': ObjectId(id), })
    response = jsonify({"message": "User with id: " +
                       id + " deleted successfully"})
    response.status_code = 200
    return response


@app.route("/users", methods=["POST"])
def create_user():
    # Receiving data
    username = request.json['username']
    email = request.json["email"]
    password = request.json["password"]

    if username and email and password:
        hashed_password = generate_password_hash(password)
        id = mongo.db.users.insert(
            {
                "username": username, "email": email, "password": hashed_password
            }
        )
        response = jsonify({
            "id": str(id),
            "username": username,
            "email": email,
            "password": password
        })
        response.status_code = 201
        return response
    else:
        return not_found()


@app.route('/users/<_id>', methods=['PUT'])
def update_user(_id):
    username = request.json["username"]
    email = request.json["email"]
    password = request.json["password"]
    if username and email and password and _id:
        hashed_password = generate_password_hash(password)
        mongo.db.users.update_one(
            {'_id': ObjectId(_id['$oid']) if '$oid' in _id else ObjectId(_id)}, {'$set': {'username': username, 'email': email, 'password': hashed_password}})
        response = jsonify({'message': 'User' + _id + 'Updated Successfuly'})
        response.status_code = 200
        return response
    else:
        return not_found()


@app.errorhandler(404)
def not_found(error=None):
    message = {
        "message": "Resource Not Found" + request.url,
        "status": 404
    }
    response = jsonify(message)
    response.status_code = 404
    return 404


if __name__ == '__main__':
    app.run(debug=True)
