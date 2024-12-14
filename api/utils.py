import pandas as pd
import regex as re
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

embeddings = OpenAIEmbeddings(
    api_key=os.getenv("OPENAI_API_KEY"),
    model=os.getenv("OPENAI_EMBEDDING_MODEL"),
    dimensions=os.getenv("OPENAI_EMBEDDING_DIMENSION"),
)


def convert_gglsht_url(url):

    pattern = r"https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)(/edit#gid=(\d+)|/edit.*)?"

    replacement = (
        lambda m: f"https://docs.google.com/spreadsheets/d/{m.group(1)}/export?"
        + (f"gid={m.group(3)}&" if m.group(3) else "")
        + "format=csv"
    )

    new_url = re.sub(pattern, replacement, url)

    return new_url


def generate_embedding(user_input):
    return embeddings.embed_query(user_input)


def gendata(data):
    for record in data:
        yield {
            "_index": os.getenv("ELASTICSEARCH_INDEX_NAME"),
            "_source": {
                "Question": record["Question"],
                "Answer": record["Answer"],
                "question_embeddings": record["question_embeddings"],
                "answer_embeddings": record["answer_embeddings"],
            },
        }
