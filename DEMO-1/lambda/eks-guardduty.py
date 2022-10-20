from __future__ import print_function
import json
import urllib3
import logging
import boto3
from botocore.exceptions import ClientError
import os

http = urllib3.PoolManager()
# Slack channel: pso-security
url = 'https://hooks.slack.com/services/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'


def lambda_handler(event, context):
    message = event['Records'][0]['Sns']['Message']
    message = json.loads(message)
    print(message)
    account = message['account']
    time = message['time']
    type = message['detail']['type']
    cluster = message['detail']['resource']['eksClusterDetails']['name']
    object = message['detail']['resource']['kubernetesDetails']['kubernetesWorkloadDetails']['type']
    pod = message['detail']['resource']['kubernetesDetails']['kubernetesWorkloadDetails']['name']
    print(account)
    print(time)
    print(type)
    print(cluster)
    print(object)
    print(pod)

    messg = 'GuardDuty Finding\nAccount: '+account+'\nTime: '+time+'\nType: '+type+'\nCluster: '+cluster+'\nObject type: '+object+'\nName: '+pod
    try:
        message = {
            'text': messg,
            'username': 'GuardDuty',
            'icon_emoji': ':no_entry:'
        }
        encoded_message = json.dumps(message).encode('utf-8')
        resp = http.request('POST',url, body=encoded_message)
        #print(presignUrl)
    except ClientError as e:
        logging.error(e)
        return None

# Emoji cheat sheet: https://www.webfx.com/tools/emoji-cheat-sheet/