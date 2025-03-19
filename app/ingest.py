import os
import string
import random
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility, has_collection
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from semantic_chunking import SemanticChunker


load_dotenv()
OPENAI_API_KEY= os.getenv("OPENAI_API_KEY")

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large",
    api_key=OPENAI_API_KEY,
)

chunker = SemanticChunker()

text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=300,
        length_function=len,
        is_separator_regex=False,
        )

def create_milvus_db(collection_name):
    item_id    = FieldSchema( name="id",         dtype=DataType.INT64,    is_primary=True, auto_id=True )
    text       = FieldSchema( name="text",       dtype=DataType.VARCHAR,  max_length= 50000             )
    embeddings = FieldSchema( name="embeddings", dtype=DataType.FLOAT_VECTOR,    dim= 3072             )
    source_pdf = FieldSchema(name="source",      dtype=DataType.VARCHAR, max_length=255)
    schema     = CollectionSchema( fields=[item_id, text, embeddings, source_pdf], description="research document", enable_dynamic_field=True )
    collection = Collection( name=collection_name, schema=schema, using='default' )
    return collection

def load_and_split_pdfs(directory, filename, text_splitter):
    all_chunks = []
    if filename.endswith(".pdf"):
        pdf_path = os.path.join(directory, filename)
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()

        for page in pages:
            cleaned_text = page.page_content.replace("\n", " ")
            chunks = text_splitter.split_text(cleaned_text)
            all_chunks.extend(chunks)

    return all_chunks

def embedding_and_store_data(chunks_list, collection_name, filename, model_emb):
    vector_list  = model_emb.embed_documents(chunks_list)
    if not has_collection(collection_name):
        collection = create_milvus_db(collection_name)
    else:
        collection = Collection(name=collection_name)
    collection.insert([chunks_list,vector_list,[filename]* len(chunks_list) ])
    collection.create_index(field_name="embeddings",
                            index_params={"metric_type":"IP","index_type":"IVF_FLAT","params":{"nlist":16384}})
    return collection

def initiate_collection_name():
    characters = string.ascii_letters + string.digits + '_'
    collection_name = 'a'+''.join(random.choice(characters) for _ in range(random.randint(5, 32)))
    print('collection_name: ', collection_name)
    return collection_name

def ingest_directory(directory, collection_name=None, semantic_chunking=True):
    if collection_name is None:
        collection_name = initiate_collection_name()
    create_milvus_db(collection_name)
    print('collection name: ', collection_name)

    file_count = 0
    total_chunks = 0
    for filename in os.listdir(directory):
        print('filename: ', filename)
        if filename.endswith(".pdf"):
            if semantic_chunking:
                chunks = chunker.process_file(directory + '/' + filename)
            else:
                chunks = load_and_split_pdfs(directory, filename, text_splitter)
            collection = embedding_and_store_data(chunks, collection_name, filename, embeddings)
            file_count += 1
            total_chunks += len(chunks)
    return collection_name, file_count, total_chunks