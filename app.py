import os
from flask import Flask, render_template, jsonify, request
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_cors import CORS
from models import db
from myqueue import Queue
import queue

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.url_map.strict_slashes = False 
app.config['DEBUG'] = True
app.config['ENV'] = 'development'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db.init_app(app)
migrate = Migrate(app, db)


manager = Manager(app)
manager.add_command("db", MigrateCommand)

CORS(app)

receiver = Queue()

@app.route('/')
def main():
    return render_template('index.html', name ='main')


@app.route('/new', methods=['POST'])
def new_element():
    if request.method == 'POST':
        if not request.json.get('name'):
                return jsonify({"name":"Is required"}),422
        if not request.json.get('phone'):
                return jsonify({"phone":"Is required"}),422
        item = {
            "name":request.json.get('name'),
            "phone":request.json.get('phone')
        }
        receiver.enqueue(item)
        return jsonify({'OK':'Contacto agregado'}), 200

@app.route('/next')
def next_element():
    if receiver.size() > 0:
        receiver.dequeue()
        return jsonify({'msg':'En turno'})
    else:
        return jsonify({'msg':'Lista vacia'})
@app.route('/all')
def all_element():
    return jsonify(receiver.get_queue())

if __name__ == '__main__':
    manager.run()