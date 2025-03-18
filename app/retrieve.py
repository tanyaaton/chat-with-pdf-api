import os
from google import genai
from dotenv import load_dotenv
from pymilvus import Collection, connections, DataType, FieldSchema, CollectionSchema
from langchain_openai import OpenAIEmbeddings

load_dotenv()
GEMINI_KEY= os.getenv("GEMINI_KEY")
OPENAI_API_KEY= os.getenv("OPENAI_API_KEY")

connections.connect("default", host="localhost", port="19530")
client = genai.Client(api_key=GEMINI_KEY)
collection = Collection(name='ahB8Qym2dsGjzoNI')

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large",
    api_key=OPENAI_API_KEY,
    # dimensions=1024
)

def find_answer(question, collection, embeddings):
    embedded_vector  = embeddings.embed_documents([question])
    collection.load()
    hits = collection.search(data=embedded_vector, 
                             anns_field="embeddings", 
                             param={"metric_type": "IP", "top_k": 5}, 
                             output_fields=["text"], 
                             limit=10)   
    return hits


def generate_prompt_gemini(question, context):
    output = f"""You are a helpful, respectful assistant. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature. If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.

You will receive information from research papers anout SQL, and a QUESTION from user in the following section. Answer the question in English.

RESEARCH PAPER INFORMATION:
{context}

QUESTION: {question}

Answer the QUESTION using details about HR Policy from HR POLICY DETAILS. Explain your reasoning if the question is not related to the provided HR Policy. If the question is not within the provided HR Policy, please answer "I don't know the answer, it is not part of the provided HR Policy."

ANSWER: """
    return output

def generate_answer(gemini_client, prompt):
    response = gemini_client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )
    return response.text

def get_answer_from_docs(question):
    hits = find_answer(question, collection, embeddings)
    prompt = generate_prompt_gemini(question, [hits[0][i].text for i in range(4)])
    response = generate_answer(client, prompt)
    print(response)
    return response

if __name__ == "__main__":
    get_answer_from_docs()