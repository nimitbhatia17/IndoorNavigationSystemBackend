from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)

@app.route('/getUUIDList', methods = ['POST'])
def getUUIDList():
    data = request.get_json()
    print(data)
    return jsonify({"Yes": "Worked"})

if(__name__ == '__main__'):
    print('The server is running...')
    app.run(port = 4000, debug = False)