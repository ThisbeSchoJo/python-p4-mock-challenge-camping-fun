#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

@app.route('/campers')
def get_campers():
    all_campers = Camper.query.all()
    camper_dictionary = [camper.to_dict(rules=('-signups',)) for camper in all_campers]
    return make_response(jsonify(camper_dictionary), 200)

@app.route('/campers/<int:id>')
def get_camper(id):
    camper = db.session.get(Camper, id)

    if camper:
        return make_response(jsonify(camper.to_dict()), 200)
    else:
        response_body = {
            "error": "Camper not found"
        }
        return make_response(jsonify(response_body), 404)

@app.route('/campers/<int:id>', methods=['PATCH'])
def update_camper(id):
    camper = db.session.get(Camper, id)

    if not camper:
        response_body = {
            "error" : "Camper not found"
        }
        return make_response(jsonify(response_body), 404)
    else:
        try:
            for attr in request.json:
                setattr(camper, attr, request.json.get(attr))
            db.session.commit()
            response_body = camper.to_dict(rules=('-signups',))
            return make_response(jsonify(response_body), 202)
        except ValueError:
            response_body= {
                "errors": ["validation errors"]
            }
            return make_response(jsonify(response_body), 400)

@app.route('/campers', methods = ['POST'])
def create_camper():
    name = request.json.get('name')
    age = request.json.get('age')
    try:
        new_camper = Camper(name=name, age=age)
        db.session.add(new_camper)
        db.session.commit()
        response_body = new_camper.to_dict(rules=('-signups',))
        return make_response(jsonify(response_body), 201)
    except:
        response_body = {
            "errors":["validation errors"]
        }
        return make_response(jsonify(response_body), 400)

@app.route('/activities')
def get_activities():
    all_activities = Activity.query.all()
    all_activities_dictionaries_list = [activity.to_dict(only=('id', 'name', 'difficulty')) for activity in all_activities]
    return make_response(jsonify(all_activities_dictionaries_list),200)

@app.route('/activities/<int:id>', methods=['DELETE'])
def delete_activity(id):
    activity = db.session.get(Activity, id)
    if activity:
        db.session.delete(activity)
        db.session.commit()
        return make_response({}, 204)
    else:
        response_body = {
            "error": "Activity not found"
        }
        return make_response(jsonify(response_body), 404)

@app.route('/signups', methods = ['POST'])
def add_signup():
    time = request.json.get('time')
    activity_id = request.json.get('activity_id')
    camper_id = request.json.get('camper_id')
    try:
        new_signup = Signup(time=time, activity_id=activity_id, camper_id=camper_id)
        db.session.add(new_signup)
        db.session.commit()
        response_body = new_signup.to_dict()
        return make_response(jsonify(response_body), 201)
    except:
        response_body = {
            "errors": ["validation errors"]
        }
        return make_response(jsonify(response_body), 400)

if __name__ == '__main__':
    app.run(port=5555, debug=True)
