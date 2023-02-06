import numpy as np
import pandas as pd
from flask import Flask, jsonify, request
from PIL import Image, ImageDraw
from collections import defaultdict
from rssi import RSSI_Localizer
from sqlalchemy import text, MetaData, create_engine, Table, Column, Integer, String
from sqlalchemy.sql import text
app = Flask(__name__)



# SQL Alchemy

metadata = MetaData()
books = Table('book', metadata,
              Column('id', Integer, primary_key=True),
              Column('book_name', String),
              Column('author_name', String),
              Column('rack_number', Integer),
              )
engine = create_engine('sqlite:///db.sqlite3')
metadata.create_all(engine)

# dataset
#         {"id":1, "book_name":"Anna Karenina", "author_name":"Leo Tolstoy", "rack_number":1},
#         {"id":2, "book_name":"Madame Bovary", "author_name":"Gustave Flaubert", "rack_number":1},
#         {"id":3, "book_name":"War and Peace", "author_name":"Leo Tolstoy", "rack_number":2},
#         {"id":4, "book_name":"The Great Gatsby", "author_name":"F. Scott Fitzgerald", "rack_number":2},
#         {"id":5, "book_name":"Lolita", "author_name": "Vladimir Nabokov", "rack_number":3},
#         {"id":6, "book_name":"The Adventures of Huckleberry Finn", "author_name": "Mark Twain", "rack_number":3},
#         {"id":7, "book_name":"The Stories of Anton Chekhov", "author_name": "Anton Chekhov", "rack_number":4},
#         {"id":8, "book_name":"Middlemarch", "author_name":"George Eliot", "rack_number":4}


def buildGraph():
    edges = [
        [1, 2], [2, 8],
        [8, 4], [7, 6],
        [4, 7], [5, 8],
        [3, 4]
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


def displayLocation(x, y, r=10):
    mapImage = Image.open(
        'C:\Projects\App development\IndoorNavigationSystemBackend\static\FloorMapHostel.png')
    drawImage = ImageDraw.Draw(mapImage)
    twoPointList = [(x - r, y - r), (x + r, y + r)]
    drawImage.ellipse(twoPointList, fill=(255, 0, 0, 255))
    mapImage.save(
        'C:/Projects/App development/IndoorNavigationSystemBackend/static/FloorMapUpdated.png')
    return


def displayPath(vertexList):
    mapImage = Image.open(
        'C:/Projects/App development/IndoorNavigationSystemBackend/static/FloorMapHostel.png')
    drawImage = ImageDraw.Draw(mapImage)
    RSSITable = pd.read_csv('RSSITable.csv')
    for i in range(len(vertexList) - 1):
        x1 = RSSITable.iloc[vertexList[i] - 1]['x']
        y1 = RSSITable.iloc[vertexList[i] - 1]['y']
        x2 = RSSITable.iloc[vertexList[i + 1] - 1]['x']
        y2 = RSSITable.iloc[vertexList[i + 1] - 1]['y']
        drawImage.line([(x1, y1), (x2, y2)], fill="red", width=5)

    twoPointList = [(RSSITable.iloc[vertexList[0] - 1]['x'] - 10, RSSITable.iloc[vertexList[0] - 1]['y'] - 10),
                    (RSSITable.iloc[vertexList[0] - 1]['x'] + 10, RSSITable.iloc[vertexList[0] - 1]['y'] + 10)]
    drawImage.ellipse(twoPointList, fill=(255, 0, 0, 255))

    twoPointList = [(RSSITable.iloc[vertexList[-1] - 1]['x'] - 10, RSSITable.iloc[vertexList[-1] - 1]['y'] - 10),
                    (RSSITable.iloc[vertexList[-1] - 1]['x'] + 10, RSSITable.iloc[vertexList[-1] - 1]['y'] + 10)]
    drawImage.ellipse(twoPointList, fill=(255, 0, 0, 255))

    mapImage.save('C:/Projects/App development/IndoorNavigationSystemBackend/static/FloorMapUpdated.png')


def generateCleanDictionary(rawData):
    RSSIDict = {'84:EB:18:08:BB:2E': 0,
                '84:EB:18:08:BD:2E': 0, '84:EB:18:08:BF:30': 0}
    keyList = list(RSSIDict.keys())
    for i in rawData:
        if i == 'ChoiceValue':
            continue
        if rawData[i]['name'] == 'Ghostyu' and (rawData[i]['id'] in keyList):
            RSSIDict[rawData[i]['id']] = rawData[i]['rssi']
    return RSSIDict


def getLocationCoordinates(RSSIDict):
    RSSITable = pd.read_csv('RSSITable.csv')

    targetAP1 = RSSIDict['84:EB:18:08:BB:2E']
    targetAP2 = RSSIDict['84:EB:18:08:BD:2E']
    targetAP3 = RSSIDict['84:EB:18:08:BF:30']

    def applicationFun(row):
        xDist = abs(row['ap1'] - targetAP1)
        yDist = abs(row['ap2'] - targetAP2)
        zDist = abs(row['ap3'] - targetAP3)
        return xDist**2 + yDist**2 + zDist**2

    RSSITable['result'] = RSSITable.apply(applicationFun, axis=1)
    resultant = RSSITable[RSSITable['result'] == RSSITable['result'].min()]
    return resultant.head(1)['x'], resultant.head(1)['y']


def generatePath(x, y, choice):
    RSSITable = pd.read_csv('RSSITable.csv')
    query = 'x == ' + str(int(x)) + ' & y == ' + str(int(y))
    start = RSSITable.query(query).index[0] + 1
    graph = buildGraph()

    displayPath(shortestPath(graph, start, choice))

    return


@app.route('/getLocation', methods=['POST'])
def getLocation():
    data = request.get_json()
    RSSIDict = generateCleanDictionary(data)
    print(RSSIDict)
    x, y = getLocationCoordinates(RSSIDict)
    displayLocation(x, y)

    return jsonify({"Yes": "Worked"})


@app.route('/getPath', methods=['POST'])
def getPath():
    data = request.get_json()
    RSSIDict = generateCleanDictionary(data)
    print(RSSIDict)
    x, y = getLocationCoordinates(RSSIDict)
    generatePath(x, y, data['ChoiceValue'])

    return jsonify({"Yes": "Worked for this too"})


@app.route("/getBook", methods=['POST'])
def search():
    data = request.get_json()
    query = 'SELECT * FROM book WHERE book_name LIKE "'+data.strip()+ '";'
    sql = text(query)
    with engine.connect() as conn:
        result = conn.execute(sql)
    df = pd.DataFrame(result)
    booksDict = df.to_dict(orient='records')
    return booksDict


if (__name__ == '__main__'):
    print('The server is running...')
    app.run(port=4000, debug=False)
