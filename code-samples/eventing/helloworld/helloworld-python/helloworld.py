
from flask import Flask, request, make_response
import uuid
import json

app = Flask(__name__)

@app.route('/', methods=['POST'])
def hello_world():
    app.logger.warning(request.data)
    event_data = json.loads(request.data)
    object_key = event_data['Records'][0]['s3']['object']['key']
    app.logger.warning(object_key)
    # Respond with another event (optional)
    response = make_response({
        "msg": "Hi from helloworld-python app!"
    })
    response.headers["Ce-Id"] = str(uuid.uuid4())
    response.headers["Ce-specversion"] = "0.3"
    response.headers["Ce-Source"] = "knative/eventing/samples/hello-world"
    response.headers["Ce-Type"] = "dev.knative.samples.hifromknative"
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)

