
from flask import Flask
from redis import Redis
from flask import request, redirect
import tempfile
import os
from  blob_api import blob_api
import base64

app = Flask(__name__)
redis = Redis(host='redis', port=6379)

base_url = "http://172.16.2.170:8080"


@app.route('/blob/v1/count')
def hello():
    redis.incr('hits')
    return 'This was called %s times.' % redis.get('hits')


@app.route('/blob/v1/obj/<url>', methods=['GET', 'POST'])
@app.route('/blob/v1/obj/<url>/<idx>', methods=['GET', 'POST'])
def get_obj(url, idx='1'):
    d_url = base64.b64decode(url)
    app.logger.debug('URL ' + d_url + " IDX " + idx)
    app.logger.debug('Request method ' + request.method)

    if request.method == 'GET':
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
        redis.set(url, dest_file)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
