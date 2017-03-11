
from flask import Flask
from redis import Redis
from flask import request, redirect
import tempfile
import os
from  blob_api import blob_api
import base64

app = Flask(__name__)
redis = Redis(host='redis', port=6379)

base_url = "http://192.168.15.198:8080"


@app.route('/blob/v1/count')
def hello():
    redis.incr('hits')
    return 'This was called %s times.' % redis.get('hits')

@app.route('/blob/v1/exist/<url>', methods = ['GET'])
@app.route('/blob/v1/exist/<url>/<idx>',  methods = ['GET'])
def obj_exist(url, idx='1'):
    url = url.encode('ascii')
    ln = len(url) % 4
    if ln != 0:
        url += (4 - ln) * '='
    if redis.exists(url) == 1:
        return "True"
    else:
        return "False"

@app.route('/blob/v1/obj/<url>', methods=['GET', 'POST'])
@app.route('/blob/v1/obj/<url>/<idx>', methods=['GET', 'POST'])
def get_obj(url, idx='1'):
    url = url.encode('ascii')
    ln = len(url) % 4
    if ln != 0:
        url += (4 - ln) * '='
    d_url = base64.b64decode(url, '-_')
    app.logger.debug('Request method ' + request.method)

    if request.method == 'GET':
        app.logger.debug('Obj URL' + url)
        obj_location = redis.get(url)
        if obj_location is None:
            return redirect(d_url, 302)
        else:
            app.logger.debug('Rdir Obj ' + obj_location)
            return redirect(base_url + obj_location, 301)
    elif request.method == 'POST':
        accept_incoming_file(url)
        return 'OK. Received'
    else:
        return 'Hmm.. wrong method'


def accept_incoming_file(url):
    files = request.files.items()
    app.logger.debug('File :' + str(files))

    for name, file in files:
        app.logger.debug('File :' + name)

        (hndl, tmpname) = tempfile.mkstemp(prefix='/store/tmp/')
        app.logger.debug('TmpFile  %s hndl %d ' % (name, hndl))
        os.close(hndl)
        file.save(tmpname)

        file_sum = blob_api.sha1_of_file(tmpname)
        stored_file_prefix = blob_api.prefix_from_sum(file_sum)

        app.logger.debug('Received file hashed :' + file_sum + ' will be saved to ' + stored_file_prefix)

        blob_api.make_store_dirs('/store', stored_file_prefix)
        dest_file = os.path.join('/store', stored_file_prefix, file_sum + ".jpeg")
        app.logger.debug('Dest file :' + dest_file)

        os.rename(tmpname, dest_file)
        os.chmod(dest_file, 0666 )
        redis.set(url, dest_file)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
