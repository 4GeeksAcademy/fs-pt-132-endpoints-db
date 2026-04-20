"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planets, Posts, Profile, Favorites
from sqlalchemy import select

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200


#endpoints con db

@app.route("/people", methods=["GET"])
def get_people():
    people = db.session.execute(select(People)).scalars().all()
    #pasamos de objeto a diccionario
    transformed = [p.serialize() for p in people]
  
    return jsonify({"success": True, "data": transformed}), 200

@app.route("/people", methods=["POST"])
def add_people():
    #extraemos del pedido la info
    body = request.get_json() #lo pasamos a diccionario
    #verificamos que tengamos toda la informacion
    if not body["name"] or not body["hair_color"]:
        return jsonify({"success": False, "msg": "missing data"}), 403

    #generamos registro
    new_people = People( #referencia a la tabla donde vamos a crear
        name=body["name"],
        hair_color= body["hair_color"]
    )
    #add para añadir los cambios
    db.session.add(new_people)
    #commit para guardar
    db.session.commit()

    return jsonify({"success": True, "data": new_people.serialize()}), 201

#un solo registro
@app.route("/people/byId/<int:id>", methods=["GET"])
def get_one_people(id):
    person = db.session.get(People, id)
   
    
  #como devuelve un solo objeto, porque estamos buscando UN id, podemos aplicar directamente serialize()
    return jsonify({"success": True, "data": person.serialize()}), 200

#modificar registro
@app.route("/people/update/<int:id>", methods=["PUT"])
def mod_people(id):
    person = db.session.get(People, id)
    if not person: 
        return jsonify({"success": False, "data": "not found"}), 404
    body = request.get_json() #lo pasamos a diccionario
    
    #verificamos que tengamos toda la informacion
    #person es un objeto
    #body es un diccionario
    person.name = body["name"] if body["name"] else person.name
    if body['hair_color']:
        person.hair_color = body['hair_color'] 
    
    #almacenamos cambios
    db.session.commit()

  #como devuelve un solo objeto, porque estamos buscando UN id, podemos aplicar directamente serialize()
    return jsonify({"success": True, "data": person.serialize()}), 200



#delete  registro
@app.route("/people/delete/<int:id>", methods=["DELETE"])
def delete_people(id):
    person = db.session.get(People, id)

    db.session.delete(person)
    db.session.commit()
   
    
  #como devuelve un solo objeto, porque estamos buscando UN id, podemos aplicar directamente serialize()
    return jsonify({"success": True, "data": "deleted user " + str(id)}), 200

#prioridad 
#responde a princpio RESTful
#la info va cifrada
@app.route("/fav/new_by_body", methods=["POST"])
def new_fav_body():
    body = request.get_json()
    new_fav = Favorites(
        user_id =  body["user_id"],
        planet_id = body["planet_id"],
        people_id= body["people_id"]
        )

    db.session.add(new_fav)
    db.session.commit()

    return jsonify({'msg': "created"})

#no se usa para post, mas bien se usa en GET
@app.route('/fav/new/<int:user_id>/<int:planet_id>/<int:people_id>', methods=["POST"])
def new_fav_dynamic(user_id, planet_id, people_id):

    new_fav = Favorites(
        user_id =  user_id,
        planet_id = planet_id,
        people_id= people_id
    )

    db.session.add(new_fav)
    db.session.commit()

    return jsonify(new_fav.serialize())



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
