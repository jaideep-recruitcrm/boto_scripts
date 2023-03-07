import boto3


"""
Get region name
"""


def get_region_name():
    region_list = [
        # North Virginia
        "us-east-1",
        # Ohio
        "us-east-2",
        # North California
        "us-west-1",
        # Oregon
        "us-west-2",
        # Mumbai
        "ap-south-1",
        # Oska
        "ap-northeast-3"
        # Seaoul
        "ap-northeast-2",
        # Singapore
        "ap-southeast-1",
        # Sydney
        "ap-southeast-2",
        # Tokyo
        "ap-northeast-1",
        # Central
        "ap-ca-central-1",
        # Frankfurt
        "eu-central-1",
        # Ireland
        "eu-west-1",
        # London
        "eu-west-2",
        # Paris
        "eu-west-3",
        # Stockhold
        "eu-north-1",
        # Sao Paulo
        "sa-east-1"
    ]

    region = input("Enter region code: ")

    if region not in region_list:
        print("Invalid Region Code")
        exit()
    print()
    return region


"""
Get all AMI IDs
"""


def get_all_amis(ec2_client):
    amis = ec2_client.describe_images(Owners=['self'])['Images']
    all_amis = []
    for ami in amis:
        if ami['ImageId'] not in all_amis:
            all_amis += [ami['ImageId']]
    return all_amis


"""
Get AMI IDs by instance
"""


def get_used_amis_by_instance(ec2_client):
    reservations = ec2_client.describe_instances()['Reservations']
    amis_used_list = []
    for reservation in reservations:
        ec2_instances = reservation['Instances']
        for ec2 in ec2_instances:
            ImageId = ec2['ImageId']
            if ImageId not in amis_used_list:
                amis_used_list += [ImageId]

    amis_used_list = list(set(amis_used_list))
    return amis_used_list


"""
Get unused AMIs
"""


def get_unused_amis(all_amis, all_used):
    unused_amis_list = []
    for ami_id in all_amis:
        if ami_id not in all_used:
            unused_amis_list += [ami_id]

    return unused_amis_list


if __name__ == '__main__':
    region_name = get_region_name()
    ec2_client = boto3.client('ec2', region_name=region_name)

    all_amis = get_all_amis(ec2_client)
    print(f"All AMIs: {len(all_amis)}")

    all_used = get_used_amis_by_instance(ec2_client)
    print(f'All used AMIs: {len(all_used)}')

    all_unused = get_unused_amis(all_amis, all_used)
    print(f'All unused AMIs: {len(all_unused)}\n')

    count = 0
    for unused in all_unused:
        count += 1
        print(f'{count}:\t{unused}')
