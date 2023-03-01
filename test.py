import json
import boto3

if __name__ == '__main__':
    client = boto3.client('ec2', region_name='ap-south-1')
    instances_array = client.describe_instances()['Reservations']
    
    instances = []
    for instance in instances_array:
        for tag in instance['Instaces'][0]['Tags']:
            if tag['Key'] == 'Name':
                
    
    for x in instances:
        for y in x['Tags']:
            if y['Key'] == 'Name' and y['Value'] == 'jenkins-server':
                print(x['PublicDnsName'])