import numpy as np
import pandas as pd
from flask import Flask, jsonify, request
from PIL import Image, ImageDraw
from rssi import RSSI_Localizer

app = Flask(__name__)

def displayLocation(x, y, r = 10):
    mapImage = Image.open('BLEAppMap.png')
    drawImage = ImageDraw.Draw(mapImage)  
    twoPointList = [(x - r, y - r), (x + r, y + r)]
    drawImage.ellipse(twoPointList, fill = (255, 0, 0, 255))
    mapImage.show()
    return mapImage

def getLocationCoordinates(RSSIDict):
    RSSITable = pd.read_csv('RSSITable.csv')
    x = 0 # read value by using logic from the csv
    y = 0 # read value by using logic from csv

    # implement logic by RSSI Values obtained in the Dictionary and closest from csv

    return x, y

@app.route('/getLocation', methods = ['POST'])
def getLocation():
    data = request.get_json()
    print(data)
    return jsonify({"Yes": "Worked"})

@app.route('/getPath', methods = ['POST'])
def getPath():
    data = request.get_json()
    print(data)
    return jsonify({"Yes": "Worked for this too"})

if(__name__ == '__main__'):
    print('The server is running...')
    app.run(port = 4000, debug = False)