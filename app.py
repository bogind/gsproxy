# a simple proxy, taking incoming requests, passing them on with authetication and returning the result
import os
from flask import Flask,request,Response
import requests
from requests import get
from requests.auth import HTTPBasicAuth

app = Flask('__main__')

GEOSERVER_USER = os.environ['GEOSERVER_USER']
GEOSERVER_PWD = os.environ['GEOSERVER_PWD']

@app.route('/')
def proxy():
    url = request.query_string.decode('ascii')
    res = requests.request(  # ref. https://stackoverflow.com/a/36601467/248616
        method          = request.method,
        url             = url,
        auth=HTTPBasicAuth(GEOSERVER_USER,GEOSERVER_PWD),
        headers         = {k:v for k,v in request.headers if k.lower() != 'host'}, # exclude 'host' header
        data            = request.get_data(),
        cookies         = request.cookies,
        allow_redirects = False,
    )

    #region exlcude some keys in :res response
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']  #NOTE we here exclude all "hop-by-hop headers" defined by RFC 2616 section 13.5.1 ref. https://www.rfc-editor.org/rfc/rfc2616#section-13.5.1
    headers          = [
        (k,v) for k,v in res.raw.headers.items()
        if k.lower() not in excluded_headers
    ]
    #endregion exlcude some keys in :res response

    response = Response(res.content, res.status_code, headers)
    return response

app.run(host='0.0.0.0', port=8089)