from fastapi import FastAPI
from api.es_connection import connect_elastic
import pandas as pd
import regex as re
from langchain_openai import OpenAIEmbeddings
import os, json
from api.utils import convert_gglsht_url, generate_embedding, gendata
from elasticsearch.helpers import bulk
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain_core.prompts.prompt import PromptTemplate
from api.scripts import hybrid_search
import os
from dotenv import load_dotenv

app = FastAPI()

load_dotenv()


@app.get("/")
def main():
    return {
        "message": "Hello! Find answers about Nepali government services and procedures here."
    }


@app.post("/ingestion")
def ingest_data():
    try:
        client = connect_elastic()
        url = os.getenv("GOOGLE_SHEETS_URL")
        index_name = os.getenv("ELASTICSEARCH_INDEX_NAME")
        new_url = convert_gglsht_url(url)
        df = pd.read_csv(new_url)
        # Apply embedding function and add new columns
        df["question_embeddings"] = df["Question"].apply(generate_embedding)
        df["answer_embeddings"] = df["Answer"].apply(generate_embedding)
        # Convert DataFrame to JSON
        result_json = df.to_json(orient="records", indent=4)
        # Save JSON to a file
        output_file = "output.json"
        with open(output_file, "w") as f:
            f.write(result_json)

        ##to delete the index if it already exists
        if client.indices.exists(index=index_name):
            resp = client.indices.delete(index=index_name)

        # create index with custom mappings
        resp = client.indices.create(
            index=index_name,
            body={
                "mappings": {
                    "properties": {
                        "Question": {"type": "text"},
                        "Answer": {"type": "text"},
                        "question_embeddings": {"type": "dense_vector", "dims": 3072},
                        "answer_embeddings": {"type": "dense_vector", "dims": 3072},
                    }
                },
            },
        )
        # Load json data

        with open(output_file, "r") as f:
            json_data = json.load(f)
        bulk(client, gendata(json_data))
        return {"message": "Successfully ingested data in elasticsearch."}

    except Exception as e:
        print("Exception: ", e)
        return {"message": "Error occured during data ingestion."}


@app.get("/fetch_answer")
def search_answer(user_query):
    try:
        template = """You are an assistant for question-answering tasks. 
            Use the following pieces of retrieved context to answer the question. 
            If you don't know the answer, just say that you don't know. 
            Use three sentences maximum and keep the answer concise.
            Question: {question} 
            Context: {context} 
            Answer:
            """

        llm = ChatOpenAI(
            model_name=os.getenv("OPENAI_CHAT_MODEL_NAME"),
            temperature=os.getenv("TEMPERATURE"),
            api_key=os.getenv("OPENAI_API_KEY"),
        )

        prompt = PromptTemplate.from_template(template)

        chain = LLMChain(llm=llm, prompt=prompt)
        context = hybrid_search(user_query)
        response = chain.invoke(input={"question": user_query, "context": context})
        answer = response["text"]
        return answer

    except Exception as e:
        print("Exception: ", e)
        return {"message": "Error occured while fetching answer."}
