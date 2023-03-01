import requests


def get_scale():
    scale = input("Scale ['up'] or ['down']: ")
    if scale != 'up' and scale != 'down':
        print("Enter scale ['up'] or ['down']")
        exit(1)


URL = ''
if __name__ == '__main__':
    scale = get_scale()

    data = {
        'region_name': 'ap-south-1',
        'asg_name': 'fluid-attack-asg',
        'scale': str(scale)
    }

    response = requests.post(URL, json=data)
    print(response)