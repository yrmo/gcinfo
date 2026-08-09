import requests

url = "https://open.canada.ca/data/dataset/a35cf382-690c-4221-a971-cf0fd189a46f/resource/64774bc1-c90a-4ae2-a3ac-d9b50673a895/download/rbpo_rppo_en.csv"

r = requests.head(url, allow_redirects=True)
print(r.status_code)
print(r.headers)