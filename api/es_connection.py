from elasticsearch import Elasticsearch
import os
from dotenv import load_dotenv

load_dotenv()


def connect_elastic():
    client = Elasticsearch(
        hosts=[os.getenv("ELASTICSEARCH_URL")],
        basic_auth=(
            os.getenv("ELASTICSEARCH_USERNAME"),
            os.getenv("ELASTICSEARCH_PASSWORD"),
        ),
        verify_certs=False,
        request_timeout=30,
    )
    if client.ping():
        print("Elastic Search Connected Sucessfully!!")
        return client
    else:
        print("Couldnot Connect to Elastic Search")
        return None
