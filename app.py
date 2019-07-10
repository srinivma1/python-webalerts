from flask import Flask, request

import json, os

app = Flask(__name__)



@app.route('/webalerts', methods=['POST'])
def handle_alert():
    data = json.loads(request.data)
    alertname = data['commonLabels']['alertname']
    severity = data['commonLabels']['severity']
    alerts = data['alerts']
    labels = alerts[0]["labels"]
    instanceName = labels["app"]
    annotations = alerts[0]["annotations"]
    namespace = labels["kubernetes_namespace"]
    if alertname == 'InstanceDown' and instanceName == 'infytraveltwo':

        sendToKafkaTopic(alertname,instanceName,namespace,severity)
    return "OK"

def sendToKafkaTopic(alertname,instanceName,namespace,severity):
    kafka_host = os.environ["KAFKA_HOST"]
    producer = KafkaProducer(value_serializer=lambda v:json.dumps(v).encode('utf-8'),bootstrap_servers=kafka_host)
    gmail_user = os.environ["GMAIL_USERNAME"]
    gmail_password = os.environ["GMAIL_PASSWORD"]
    sent_from = gmail_user
    to = os.environ["TO_GMAIL"]
    clusterName = os.environ["CLUSTER_NAME"]
    kafka_topic = os.environ["KAFKA_TOPIC"]
    data = {}
    data['gmailUserName'] = gmail_user
    data['gmailPassword'] = gmail_password
    data['gmailRecipient'] = to
    data['clusterName'] = clusterName
    data['alertName'] = alertname
    data['instanceName'] = instanceName
    data['namespace'] = namespace
    data['severity'] = severity
    json_data = json.dumps(data)
    print(json_data)
    ack = producer.send(kafka_topic, json_data)
    metadata = ack.get()
    print(metadata.topic)
    print(metadata.partition)
    producer.flush()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)
