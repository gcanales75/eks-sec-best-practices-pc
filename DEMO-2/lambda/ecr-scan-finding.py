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
    time = event['time']
    account = event['account']
    region = event['region']
    critical_findings = event['detail']['finding-severity-counts']['CRITICAL']
    high_findings = event['detail']['finding-severity-counts']['HIGH']
    repo_arn = event['detail']['repository-name']
    image_tag = event['detail']['image-tags'][0]
    
    print(account)
    print(time)
    print(region)
    print(critical_findings)
    print(high_findings)
    print(repo_arn)
    print(image_tag)

    repo_name = (repo_arn.split('/'))
    repo_name = repo_name[1]
    critical_findings = str(critical_findings)
    high_findings = str(high_findings)
    
    print(repo_name)

    messg = 'Inspector2 Image Scan Findings\nAccount: '+account+'\nTime: '+time+'\nRegion: '+region+'\nRepo: '+repo_name+'\nImage tag: '+image_tag+'\nCRITICAL: '+critical_findings+'\nHIGH: '+high_findings
    print(messg)

    try:
        message = {
            'text': messg,
            'username': 'Inspector2',
            'icon_emoji': ':mag:'
        }
        encoded_message = json.dumps(message).encode('utf-8')
        resp = http.request('POST',url, body=encoded_message)
        #print(presignUrl)
    except ClientError as e:
        logging.error(e)
        return None


# Emoji cheat sheet: https://www.webfx.com/tools/emoji-cheat-sheet/