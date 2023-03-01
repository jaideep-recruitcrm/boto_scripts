import requests
import json

def get_scale():
    scale = input("Scale ['up'] or ['down']: ")
    if scale != 'up' and scale != 'down':
        print("Enter scale ['up'] or ['down']")
        exit(1)
    return scale


URL = 'redacted'
if __name__ == '__main__':
    scale = get_scale()

    data = {
        'region_name': 'ap-south-1',
        'instance_name': 'fluid-attack-security',
        'asg_name': 'fluid-attack-asg',
        'scale': scale
    }

    response = requests.post(URL, json=data)
    print(f'Status Code: {response.status_code}')
    print(json.loads(response._content))