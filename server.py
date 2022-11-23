import numpy as np
import pandas as pd
from flask import Flask, jsonify, request
from PIL import Image, ImageDraw
from collections import defaultdict
from rssi import RSSI_Localizer

app = Flask(__name__)

def buildGraph():
    edges = [
        [1, 2], [2, 3],
        [3, 4], [4, 5],
        [5, 6], [6, 7],
        [7, 8]
    ]
    graph = defaultdict(list)
    
    for edge in edges:
        a, b = edge[0], edge[1]
        graph[a].append(b)
        graph[b].append(a)
    
    return graph

def shortestPath(graph, start, goal):
    explored = []
    queue = [[start]]
    
    if start == goal:
        return [start]
    
    while queue:
        path = queue.pop(0)
        node = path[-1]

        if node not in explored:
            neighbours = graph[node]
            
            for neighbour in neighbours:
                new_path = list(path)
                new_path.append(neighbour)
                queue.append(new_path)
                
                if neighbour == goal:
                    return new_path
            explored.append(node)
    return []

def displayLocation(x, y, r = 10):
    mapImage = Image.open('BLEAppMap.png')
    drawImage = ImageDraw.Draw(mapImage)  
    twoPointList = [(x - r, y - r), (x + r, y + r)]
    drawImage.ellipse(twoPointList, fill = (255, 0, 0, 255))
    mapImage.save('/Users/nimitbhatia/Projects/BLECentralAppBackend/static/BLEAppMapUpdated.png')
    return

def displayPath(vertexList):
    mapImage = Image.open('BLEAppMap.png')
    drawImage = ImageDraw.Draw(mapImage)
    RSSITable = pd.read_csv('RSSITable.csv') 
    for i in range(len(vertexList) - 1):
        x1 = RSSITable.iloc[vertexList[i] - 1]['x']
        y1 = RSSITable.iloc[vertexList[i] - 1]['y']
        x2 = RSSITable.iloc[vertexList[i + 1] - 1]['x']
        y2 = RSSITable.iloc[vertexList[i + 1] - 1]['y']
        drawImage.line([(x1, y1), (x2, y2)], fill ="blue", width = 5)

    twoPointList = [(RSSITable.iloc[vertexList[0] - 1]['x'] - 10, RSSITable.iloc[vertexList[0] - 1]['y'] - 10), (RSSITable.iloc[vertexList[0] - 1]['x'] + 10, RSSITable.iloc[vertexList[0] - 1]['y'] + 10)]
    drawImage.ellipse(twoPointList, fill = (255, 0, 0, 255))

    twoPointList = [(RSSITable.iloc[vertexList[-1] - 1]['x'] - 10, RSSITable.iloc[vertexList[-1] - 1]['y'] - 10), (RSSITable.iloc[vertexList[-1] - 1]['x'] + 10, RSSITable.iloc[vertexList[-1] - 1]['y'] + 10)]
    drawImage.ellipse(twoPointList, fill = (255, 0, 0, 255))

    mapImage.save('/Users/nimitbhatia/Projects/BLECentralAppBackend/static/BLEAppMapUpdated.png')

def generateCleanDictionary(rawData):
    RSSIDict = {'OnePlus Buds Z2': 0, 'Nothing ear (1)': 0, '7D:35:CE:88:FE:92': 0, '6F:B6:B4:D2:8E:63': 0}
    keyList = list(RSSIDict.keys())
    for i in rawData:
        if i == 'ChoiceValue':
            continue
        if rawData[i]['name'] == keyList[0] or rawData[i]['name'] == keyList[1]:
            RSSIDict[rawData[i]['name']] = rawData[i]['rssi']
        elif rawData[i]['id'] == keyList[-2] or rawData[i]['id'] == keyList[-1]:
            RSSIDict[rawData[i]['id']] = rawData[i]['rssi']
    return RSSIDict

def getLocationCoordinates(RSSIDict):
    RSSITable = pd.read_csv('RSSITable.csv')

    targetAP1 = RSSIDict['Nothing ear (1)']
    targetAP2 = RSSIDict['OnePlus Buds Z2']
    # targetAP3 = RSSIDict['7D:35:CE:88:FE:92']
    # targetAP4 = RSSIDict['OnePlus Buds Z2']

    def applicationFun(row):
        xDist = abs(row['ap1'] - targetAP1)
        yDist = abs(row['ap2'] - targetAP2)
        # zDist = abs(row['ap3'] - targetAP3)
        return xDist**2 + yDist**2

    RSSITable['result'] = RSSITable.apply(applicationFun, axis = 1)
    resultant = RSSITable[RSSITable['result'] == RSSITable['result'].min()]

    return resultant.head(1)['x'], resultant.head(1)['y']

def generatePath(x, y, choice):
    RSSITable = pd.read_csv('RSSITable.csv')
    query = 'x == ' + str(int(x)) + ' & y == ' + str(int(y))
    start = RSSITable.query(query).index[0] + 1
    graph = buildGraph()

    displayPath(shortestPath(graph, start, choice))

    return

@app.route('/getLocation', methods = ['POST'])
def getLocation():
    data = request.get_json()
    RSSIDict = generateCleanDictionary(data)
    print(RSSIDict)
    x, y = getLocationCoordinates(RSSIDict)
    displayLocation(x, y)

    return jsonify({"Yes": "Worked"})

@app.route('/getPath', methods = ['POST'])
def getPath():
    data = request.get_json()
    RSSIDict = generateCleanDictionary(data)
    print(RSSIDict)
    x, y = getLocationCoordinates(RSSIDict)
    generatePath(x, y, data['ChoiceValue'])

    return jsonify({"Yes": "Worked for this too"})

if(__name__ == '__main__'):
    print('The server is running...')
    app.run(port = 4000, debug = False)