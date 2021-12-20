from flask import Flask, render_template, request
import json
from typing import Collection
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from bson.objectid import ObjectId

imgWidth = 2704
imgHeight = 1520

# load_dotenv() # Se toman las variables de entorno del archivo .env. Alli estan el usuario y la clave de la base de datos
dbUser = os.environ['DBUSER']
dbPass = os.environ['DBPASS']

# Ahora se hace la conexión a la base de datos
client = MongoClient(f"mongodb+srv://{dbUser}:{dbPass}@cluster0.hlrki.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client.trafficLights
# Esta colección corresponde a los datos de entrenamiento
collection = db.trainData

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home.html', title = "Traffic lights detection")

@app.route('/lights')
def table():
    lights = collection.find()
    lightsForTable = []
    # The list of ids will allow navigation
    idsList = []
    for light in lights:
        newLight = parseLight(light)
        lightsForTable.append(newLight)
        idsList.append(newLight["_id"])

    return render_template('table.html', title = "Traffic lights table", lights=lightsForTable)

@app.route('/light/<id>')
def details(id):
    ids = collection.find({"ignore":0}, {"_id":1})
    idPrev = None
    idNext = None
    found = False
    for elem in ids:
        if found:
            idNext = elem["_id"]
            break
        if elem["_id"] == ObjectId(id):
            found = True
            continue
        idPrev = elem["_id"]
    
    light = collection.find_one({"_id":ObjectId(id)})
    try:
        processedLight = parseLight(light)
    except TypeError:
        processedLight = None

    if light != None:
        title = f"Details {light['imgname']}"
    else:
        title = "Error"
    return render_template('details.html', title = title, light=processedLight, rawLight = light, imgWidth = imgWidth, imgHeight = imgHeight, idNext = idNext, idPrev = idPrev)

def parseLight(light):
    try:
        newLight = light["inbox"][0]
        newLight["xmin"] = newLight["bndbox"]["xmin"]
        newLight["xmax"] = newLight["bndbox"]["xmax"]
        newLight["ymin"] = newLight["bndbox"]["ymin"]
        newLight["ymax"] = newLight["bndbox"]["ymax"]
        del newLight["bndbox"]
    except:
        newLight = {"color":None, "shape":None, "xmax":None, "ymax":None, "xmin":None, "ymin":None, "occluded":None, "truncated":None, "difficult":None, "value":None}
    newLight["ignore"] = light["ignore"]
    newLight["imgname"] = light["imgname"]
    newLight["url"] = light["url"]
    newLight["_id"] = light["_id"]
    return newLight



