import boto3

def get_region_name():
    region_name = input('Enter region name: ')
    print()

    if len(region_name) == 0:
      region_name = 'ap-south-1'
      print(f"Taking default region: {region_name}\n")

    return region_name


def get_all_asg(client):
    response = client.describe_auto_scaling_groups()

    return response['AutoScalingGroups']


def print_all_asg_groups(auto_scaling_groups):
    for asg in auto_scaling_groups:
        print(f"{asg['AutoScalingGroupName']}")
        print(f"    Min Size: {asg['MinSize']}")
        print(f"    Max Size: {asg['MaxSize']}")
        print(f"    Desired Capacity: {asg['DesiredCapacity']}")
        print(f"    ARN: {asg['AutoScalingGroupARN']}\n")


def get_asg_selection(auto_scaling_groups):
    selected_asg = input('Enter asg name: ')
    print()

    if len(selected_asg) == 0:
        print("No asg selected")
        exit()

    try:
      existing_desired_capacity = [x['DesiredCapacity'] for x in auto_scaling_groups if x['AutoScalingGroupName'] == selected_asg][0]
      minimum_size = [x['MinSize'] for x in auto_scaling_groups if x['AutoScalingGroupName'] == selected_asg][0]
      maximum_size = [x['MaxSize'] for x in auto_scaling_groups if x['AutoScalingGroupName'] == selected_asg][0]

    except IndexError:
      print("The selected asg is not in the list")
      exit()

    return selected_asg, minimum_size, existing_desired_capacity, maximum_size


def change_size(client, selected_asg, minimum_size, existing_desired_capacity, maximum_size):
    try:
        new_minimum_size = input(f'New minimum size [Blank = DEFAULT][{minimum_size}]: ')
        new_maximum_size = input(f'New maximum size [Blank = DEFAULT][{maximum_size}]: ')
        new_desired_capacity = input(f'New desired capacity [Blank = DEFAULT][{existing_desired_capacity}]: ')
        print()

        if len(new_minimum_size) == 0 and len(new_desired_capacity) == 0 and len(new_maximum_size) == 0:
            print("All default values")
            exit()

        if len(new_minimum_size) == 0:
            new_minimum_size = minimum_size
        else:
            new_minimum_size = int(new_minimum_size)

        if len(new_maximum_size) == 0:
            new_maximum_size = maximum_size
        else:
            new_maximum_size = int(new_maximum_size)

        if len(new_desired_capacity) == 0:
            new_desired_capacity = existing_desired_capacity
        else:
            new_desired_capacity = int(new_desired_capacity)

        if new_minimum_size > new_desired_capacity or new_desired_capacity > new_maximum_size:
            print("Not within limits")
            exit()

    except ValueError:
        print("Not an integer")
        exit()

    response = client.update_auto_scaling_group(
        AutoScalingGroupName = selected_asg,
        MinSize = new_minimum_size,
        MaxSize = new_maximum_size,
        DesiredCapacity = new_desired_capacity
    )

    return response


if __name__ == '__main__':
    region_name = get_region_name()
    client = boto3.client('autoscaling', region_name=region_name)

    auto_scaling_groups = get_all_asg(client)
    print_all_asg_groups(auto_scaling_groups)
    selected_asg, minimum_size, existing_desired_capacity, maximum_size = get_asg_selection(auto_scaling_groups)

    result = change_size(client, selected_asg, minimum_size, existing_desired_capacity, maximum_size)
    print(result)