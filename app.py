from flask import Flask, request

import json, os

app = Flask(__name__)



@app.route('/webalerts', methods=['POST'])
def handle_alert():
    data = json.loads(request.data)
    print(data)
    alerts = data['alerts']['labels']
    alertname = alerts['alertname']
    print(alertname)
    description = data['commonAnnotations']['description']
    severity = int(data['commonAnnotations']['severity'])
    scope = ''
    for key in data['commonAnnotations']:
        if key == "description" or key == "severity":
            continue
        newname = key.replace('_', '.')
        scope += newname + ' = "' + data['commonAnnotations'][key] + '" and '
    tags = data['commonLabels']
    return "OK"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)
