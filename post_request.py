import requests
import json

def get_scale():
    scale = input("Scale ['up'] or ['down']: ")
    if scale != 'up' and scale != 'down':
        print("Enter scale ['up'] or ['down']")
        exit(1)
    return scale


url = "FUNCTION_URL"
if __name__ == '__main__':
    scale = get_scale()

    headers = {
        'Content-Type': 'application/json'
    }

    payload = json.dumps({
        "scale": scale
    })

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)