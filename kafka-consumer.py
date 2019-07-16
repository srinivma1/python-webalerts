from kafka import KafkaConsumer
import json, os
import smtplib
import os
import sys

with open("instance_down_email_template.txt") as f:
    email_template = f.read()

def sendGmail():
    kafka_host = os.environ["KAFKA_HOST"]
    topicName = os.environ["KAFKA_TOPIC"]
    consumer = KafkaConsumer(topicName, bootstrap_servers=kafka_host,
                             auto_offset_reset='earliest',
                             value_deserializer=lambda m: json.loads(m.decode('utf-8')))
    try:
        for message in consumer:
            data = json.loads(message.value)
            print(data)
            gmail_user = data['emailUserName']
            print(gmail_user)
            gmail_password = data['emailPassword']
            sent_from = gmail_user
            to = data['emailRecipient']
            clusterName = data['clusterName']
            alertname = data['alertName']
            severity = data['severity']
            instanceName = data['instanceName']
            namespace = data['namespace']
            subject = 'Alert : {} Severity : {}'.format(alertname, severity)
            body = email_template.format(instance_name=instanceName, namespace=namespace, cluster_name=clusterName)
            message = 'Subject: {}\n\n{}'.format(subject, body)
            emailHostName = os.environ["EMAIL_HOST_NAME"]
            emailHostPort = os.environ["EMAIL_HOST_PORT"]
            server = smtplib.SMTP(emailHostName, emailHostPort)
            server.ehlo()
            server.starttls()
            server.login(gmail_user, gmail_password)
            server.sendmail(sent_from, to, message)


    except KeyboardInterrupt:
        sys.exit()


if __name__ == '__main__':
    sendGmail()