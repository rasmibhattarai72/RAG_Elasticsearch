from utils import generate_embedding
from es_connection import connect_elastic
import os
from dotenv import load_dotenv

load_dotenv()


def hybrid_search(user_input):
    token_vector = generate_embedding(user_input)
    client = connect_elastic()

    es_query = {
        "query": {"match": {"answer": {"query": user_input, "boost": 0.6}}},
        "knn": {
            "field": "answer_embeddings",
            "query_vector": token_vector,
            "k": 7,
            "num_candidates": 100,
            "boost": 0.4,
        },
    }
    response = client.search(index=os.getenv("ELASTICSEARCH_INDEX_NAME"), body=es_query)

    # Extract the desired fields
    data = []
    for hit in response["hits"]["hits"]:
        extracted_data = {
            "id": hit["_id"],
            "Question": hit["_source"]["Question"],
            "Answer": hit["_source"]["Answer"],
            "question_embeddings": hit["_source"]["question_embeddings"],
            "answer_embeddings": hit["_source"]["answer_embeddings"],
        }
        data.append(extracted_data)

    # return the Answer of first hit , it will be passed to LLM as context
    context = data[0]["Answer"]
    return context
