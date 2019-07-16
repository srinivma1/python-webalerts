from flask import Flask, request
from kafka import KafkaProducer
import json, os

app = Flask(__name__)



@app.route('/webalerts', methods=['POST'])
def handle_alert():
    data = json.loads(request.data)
    alertname = data['commonLabels']['alertname']
    print(alertname)
    severity = data['commonLabels']['severity']
    instanceDown = os.environ[alertname.upper()]
    instanceDownArr = instanceDown.split(',')
    print(severity)
    alerts = data['alerts']
    for i in alerts:
        labels = i["labels"]
        if "app" in labels:
            instanceName = labels["app"]
            print(instanceName)
            if alertname == labels["alertname"] and instanceName in instanceDownArr:
                namespace = labels["kubernetes_namespace"]
                print(namespace)
                sendToKafkaTopic(alertname, instanceName, namespace, severity)

    return "OK"

def sendToKafkaTopic(alertname,instanceName,namespace,severity):
    kafka_host = os.environ["KAFKA_HOST"]
    kafka_topic = os.environ["KAFKA_TOPIC"]
    clusterName = os.environ["CLUSTER_NAME"]
    data = {}
    data['alertName'] = alertname
    data['instanceName'] = instanceName
    data['namespace'] = namespace
    data['severity'] = severity
    data['clusterName'] = clusterName
    json_data = json.dumps(data)
    print(json_data)
    producer = KafkaProducer(value_serializer=lambda v: json.dumps(v).encode('utf-8'), bootstrap_servers=kafka_host)
    ack = producer.send(kafka_topic, json_data)
    metadata = ack.get()
    print(metadata.topic)
    print(metadata.partition)
    producer.flush()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)
