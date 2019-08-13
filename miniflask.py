import time
from flask import Flask, Response, stream_with_context

app = Flask(__name__)


@app.route("/stream")
def stream():
    def gen():
        try:
            i = 0
            while True:
                data = "this is line {}".format(i)
                print(data)
                yield data + "<br>"
                i += 1
                time.sleep(5)
        except GeneratorExit:
            print("closed")

    return Response(stream_with_context(gen()))
