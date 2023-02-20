import json
import boto3

# Extracting Json values
region_name = 'ap-south-1'
asg_name = 'test-asg'
scale = 'up'

# Boto3
client = boto3.client('autoscaling', region_name=region_name)

all_asg = client.describe_auto_scaling_groups()['AutoScalingGroups']

print(all_asg)