import json
import boto3


def get_region(region_name):
    if len(region_name) == 0:
        return 'ap-south-1'
    else:
        return region_name


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
        if current_desired_capacity == 2:
            return 500
        else:
            return client.set_desired_capacity(
                AutoScalingGroupName=asg_name,
                DesiredCapacity=2,
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


def lambda_handler(event, context):
    # Extracting Json values
    event = json.loads(event['body'])
    region_name = get_region(event['region_name'])
    asg_name = event['asg_name']
    scale = verify_scale_request(event['scale'])

    # Boto3
    client = boto3.client('autoscaling', region_name=region_name)
    all_asg = client.describe_auto_scaling_groups()['AutoScalingGroups']

    # Verifications
    present, minimum_size, current_desired_capacity, maximum_size, asg_name_list = verify_asg_name(
        client, all_asg, asg_name)

    if present and scale:
        status_code = scale_asg(client, all_asg, asg_name, scale,
                                minimum_size, current_desired_capacity, maximum_size)

        if status_code == 500:
            response = {
                'message': "Already scaled " + scale
            }
            return {
                'statusCode': status_code,
                'body': json.dumps(response)
            }
        elif status_code == 200:
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
