from flask import Flask
from flask import jsonify
app = Flask(__name__)

@app.route('/getUUIDList', methods = ['GET'])
def getUUIDList():
    print('Inside getUUIDList')
    return jsonify({"Hello": "World"})

if(__name__ == '__main__'):
    print('The server is running...')
    app.run(debug = False)