import traceback
import json
import urllib3
import urllib.parse

def get_data_from_url(url):
    try:
        if "github.com" in url:
            parsed = urllib.parse.urlsplit(url)
            path = parsed.path # Getting path from url
            path = path.removesuffix("/") # Remove potential leading /
            path = path.removesuffix(".git") # Remove potential .git suffix
            api_url = "https://api.github.com/repos" + path + "/contents" # Convert into Git REST API URL
            api_response = http.request('GET', api_url)
            data_raw = api_response.data
            data = json.loads(data_raw)
            return data
        else:
            print("Invalid URL - please enter a GitHub repository URL.")
        return None
    except Exception:
        traceback.print_exc()
        return None


http = urllib3.PoolManager()

url = input("Enter a GitHub repo link: ")
data = get_data_from_url(url)

if not data is None: # Use recursion, so it checks an entry to see if its a file or directory. If it's a directory, recall on the directory.
    for i in range(len(data)):
        print(data[i]['name'], "\n")