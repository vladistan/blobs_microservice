from flask import Flask
from redis import Redis
from flask import request, redirect
from werkzeug import secure_filename
import tempfile
import base64
import os
from  blob_api import blob_api

app = Flask(__name__)
redis = Redis(host='redis', port=6379)


@app.route('/blob/v1/count')
def hello():
    redis.incr('hits')
    return 'This was called %s times.' % redis.get('hits')


@app.route('/blob/v1/obj/<url>/<idx>', methods=['GET', 'POST'])
def get_obj(url, idx=1):
    d_url = base64.b64decode(url)
    app.logger.debug('URL ' + d_url + " IDX " + idx)
    app.logger.debug('Request method ' + request.method)

    if request.method == 'GET':
        return redirect(d_url, 301)
    elif request.method == 'POST':
        accept_incoming_file()
        return 'OK. Received'
    else:
        return 'Hmm.. wrong method'


def accept_incoming_file():
    files = request.files.items()
    for name, file in files:
        app.logger.debug('File :' + name)
        save_file = secure_filename(name)
        app.logger.debug('Secure file :' + save_file)
        (hndl, tmpname) = tempfile.mkstemp(prefix='/store/tmp/')
        app.logger.debug('TmpFile  %s hndl %d ' % (name, hndl))
        os.close(hndl)
        file.save(tmpname)

        file_sum = blob_api.sha1_of_file(tmpname)
        stored_file_prefix = blob_api.prefix_from_sum(file_sum)

        app.logger.debug('Received file hashed :' + file_sum + ' will be saved to ' + stored_file_prefix)

        blob_api.make_store_dirs('/store', stored_file_prefix)
        dest_file = os.path.join('/store', stored_file_prefix, file_sum + ".jpeg")
        app.logger.debug('Dest file :' + dest_file )
        os.rename(tmpname, dest_file)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
