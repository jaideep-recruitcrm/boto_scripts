import json
import time
import boto3


def extract_values(event):
    region_name = ''
    asg_name = ''
    
    if 'region_name' in event:
        region_name = event['region_name']
    else:
        region_name = 'ap-south-1'
    
    if 'asg_name' in event:
        asg_name = event['asg_name']
    else:
        asg_name = 'fluid-attack-asg'

    return region_name, asg_name


def verify_asg_name(client, all_asg, asg_name):
    present = False
    minimum_size = ''
    current_desired_capacity = ''
    maximum_size = ''
    asg_name_list = []

    for x in all_asg:
        asg_name_list += [
            {
                'asg_name': x['AutoScalingGroupName'],
                'minimum_size': str(x['MinSize']),
                'maximum_size': str(x['MaxSize']),
                'desired_capacity': str(x['DesiredCapacity'])
            }
        ]

        if x['AutoScalingGroupName'] == asg_name:
            present = True
            minimum_size = x['MinSize']
            current_desired_capacity = x['DesiredCapacity']
            maximum_size = x['MaxSize']

    return present, minimum_size, current_desired_capacity, maximum_size, asg_name_list


def verify_scale_request(scale):
    if scale != 'up' and scale != 'down':
        return False
    else:
        return scale


def scale_asg(client, all_asg, asg_name, scale, minimum_size, current_desired_capacity, maximum_size):
    if scale == 'up':
        if current_desired_capacity == 1:
            return 500
        else:
            return client.set_desired_capacity(
                AutoScalingGroupName=asg_name,
                DesiredCapacity=1,
                HonorCooldown=False
            )['ResponseMetadata']['HTTPStatusCode']
    elif scale == 'down':
        if current_desired_capacity == 0:
            return 500
        else:
            return client.set_desired_capacity(
                AutoScalingGroupName=asg_name,
                DesiredCapacity=0,
                HonorCooldown=False
            )['ResponseMetadata']['HTTPStatusCode']


def get_ip_address(client, region_name, asg_name):
    ip_address = ''
    while ip_address == '':
        time.sleep(15)
        ec2 = boto3.resource('ec2')
        response= client.describe_auto_scaling_groups(AutoScalingGroupNames=[asg_name])
        groups=response.get("AutoScalingGroups")
        instances=(groups[0].get('Instances'))
        for instance in instances:
            ip_address = ec2.Instance(instance.get('InstanceId')).public_dns_name
        
    return ip_address


def lambda_handler(event, context):
    # Extracting Json values
    event = json.loads(event['body'])
    region_name, asg_name = extract_values(event)
    scale = verify_scale_request(event['scale'])

    # Boto3
    client = boto3.client('autoscaling', region_name=region_name)
    all_asg = client.describe_auto_scaling_groups()['AutoScalingGroups']

    # Verifications
    present, minimum_size, current_desired_capacity, maximum_size, asg_name_list = verify_asg_name(
        client,
        all_asg,
        asg_name
    )

    if present and scale:
        status_code = scale_asg(
            client,
            all_asg,
            asg_name,
            scale,
            minimum_size,
            current_desired_capacity,
            maximum_size
        )

        if status_code == 500:
            response = {
                'message': "Already scaled " + scale
            }
            return {
                'statusCode': status_code,
                'body': json.dumps(response)
            }
        elif status_code == 200:
            if scale == 'up':
                ip_address = get_ip_address(client, region_name, asg_name)

                response = {
                    'message': "Successfully scaled " + scale,
                    'connection_string': 'ssh -i katia.pem ubuntu@' + ip_address
                }
                return {
                    'statusCode': status_code,
                    'body': json.dumps(response)
                }
            else:
                response = {
                    'message': "Successfully scaled " + scale
                }
                return {
                    'statusCode': status_code,
                    'body': json.dumps(response)
                }
        else:
            response = {
                'message': "Unexpected response"
            }
            return {
                'statusCode': status_code,
                'body': json.dumps(response)
            }

    elif not present:
        response = {
            'message': 'Please select asg from the following',
            'asg_list': asg_name_list,
            'user_selected': asg_name
        }
        return {
            'statusCode': 404,
            'body': json.dumps(response)
        }

    elif not scale:
        response = {
            'message': 'Please select scale [\'up\'] or [\'down\']',
            'user_selected': str(event['scale'])
        }
        return {
            'statusCode': 500,
            'body': json.dumps(response)
        }