
from flask import Flask, request
import uuid
import json
import milvus_model
from pymilvus import MilvusClient, DataType, Collection

import boto3

client = MilvusClient(
    uri="http://my-release-milvus.default.svc:19530"
)

s3 = boto3.client(
    "s3",
    aws_access_key_id="SLQ4WM6AFASUJ4PEW2QU",
    aws_secret_access_key="vfsbYAppm4dAvQMHZPAUAZefOZuatjMhiDT3M4UX",
    endpoint_url="http://rook-ceph-rgw-my-store.rook-ceph.svc:80",
    use_ssl=False,
    verify=False,
)
# Store bucket name
bucket_name = "ceph-bkt-a238d69b-bb95-4687-8ed5-da3039e0177b"

i = 0

app = Flask(__name__)

@app.route('/', methods=['POST'])
def hello_world():
    app.logger.warning(request.data)
    event_data = json.loads(request.data)
    object_key = event_data['Records'][0]['s3']['object']['key']
    app.logger.warning(object_key)
    if not client.has_collection(collection_name="demo_collection"):
        client.create_collection(
            collection_name="demo_collection",
            dimension=768,  # The vectors we will use in this demo has 768 dimensions
            )
    object_data = s3.get_object(Bucket=bucket_name, Key=object_key)

    object_content = object_data["Body"].read().decode("utf-8")
    app.logger.warning(object_content)
    # Load the collection into memory
    client.load_collection("demo_collection")
    objectlist = []

    objectlist.append(object_content)

    embedding_fn = milvus_model.DefaultEmbeddingFunction()

    vectors = embedding_fn.encode_documents(objectlist)

    app.logger.warning(vectors)
    global i
    i = i + 1

    data = [ {"id": i, "vector": vectors[0], "object_name": object_key} ]

    res = client.insert(collection_name="demo_collection", data=data)
    app.logger.warning(res)

    return

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)

