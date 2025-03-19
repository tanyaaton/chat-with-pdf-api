import os
from google import genai
from dotenv import load_dotenv
from pymilvus import Collection, connections, DataType, FieldSchema, CollectionSchema
from langchain_openai import OpenAIEmbeddings

load_dotenv()
GEMINI_KEY= os.getenv("GEMINI_KEY")
OPENAI_API_KEY= os.getenv("OPENAI_API_KEY")

client = genai.Client(api_key=GEMINI_KEY)
# collection = Collection(name='ahB8Qym2dsGjzoNI')

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


def generate_prompt_gemini(question, context, conversation_history):
    output = f"""You are a helpful, respectful assistant that helps answer questions about research paper. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature. If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.

You will receive in the following section, information from research papers, a QUESTION from user, and PREVIOUS CONVERSATION which contain past user's questions and your generated answers. You will need to answer the QUESTION using the information from the RESEARCH PAPERS. Explain your reasoning. If the question is not within the provided research paper, please answer answer with your knowleadge but also specify that it is not part of the provided documents.

RESEARCH PAPERS:
{context}

PREVIOUS CONVERSATION:
{conversation_history}

QUESTION: {question}

ANSWER: """
    return output

def generate_answer(gemini_client, prompt):
    response = gemini_client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )
    return response.text

def get_answer_from_docs(question, collection_name, conversation_history=None):
    collection = Collection(name=collection_name)
    hits = find_answer(question, collection, embeddings)
    top_5_chunks = [hits[0][i].text for i in range(5)]
    prompt = generate_prompt_gemini(question, top_5_chunks, conversation_history)
    response = generate_answer(client, prompt)
    return response, top_5_chunks

if __name__ == "__main__":
    get_answer_from_docs()