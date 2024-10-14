
from flask import Flask, request, make_response
import uuid
import json
from pymilvus import MilvusClient, DataType, Collection, model

client = MilvusClient(
    uri="http://my-release-milvus.default.svc:19530"
)

objectlist = []

app = Flask(__name__)

@app.route('/', methods=['POST'])
def hello_world():
    app.logger.warning(request.data)
    event_data = json.loads(request.data)
    object_key = event_data['Records'][0]['s3']['object']['key']
    app.logger.warning(object_key)
    if client.has_collection(collection_name="demo_collection"):
        client.drop_collection(collection_name="demo_collection")
        print("collectiop dropped")
        client.create_collection(
            collection_name="demo_collection",
            dimension=768,  # The vectors we will use in this demo has 768 dimensions
            )
        # Load the collection into memory
    client.load_collection("demo_collection")
    objectlist.append(object_key)

    embedding_fn = model.DefaultEmbeddingFunction()

    vectors = embedding_fn.encode_documents(objectlist)

    data = [ {"id": 0, "vector": vectors[0], "object_name": object_key} ]

    res = client.insert(collection_name="demo_collection", data=data)
    print(res)

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

