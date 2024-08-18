# run.py
import os
from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    extra_dirs = ['web/templates', 'web/static',]
    extra_files = extra_dirs[:]
    for extra_dir in extra_dirs:
        for dirname, dirs, files in os.walk(extra_dir):
            for filename in files:
                filename = os.path.join(dirname, filename)
                if os.path.isfile(filename):
                    extra_files.append(filename)

    #app.run(debug=True, extra_files=extra_files)
    socketio.run(app, host='localhost', port=6969, debug=True, extra_files=extra_files)