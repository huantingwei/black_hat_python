from urllib.request import urlopen, Request
import sys

ex = int(sys.argv[1])

if ex == 0:
    # ex0: GET request
    body = urlopen("https://github.com/huantingwei/black_hat_python")
    print(body.read())

elif ex == 1:
    # ex1: GET request with headers
    url = "https://github.com/huantingwei/black_hat_python"
    headers = {}
    headers['User-Agent'] = 'Googlebot'

    request = Request(url, headers=headers)
    response = urlopen(request)

    print(response.read())
    response.close()

