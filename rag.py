import pymupdf
import psycopg2
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Document
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import TextNode
from llama_index.llms.llama_cpp import LlamaCPP
from llama_index.core.query_engine import RetrieverQueryEngine

from retriever import VectorDBRetriever

# sentence transformers
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en")

db_name = "vectordb"
host = "localhost"
port = "5432"
user = "llama"
password = "llama"

text_parser = SentenceSplitter(
    chunk_size=1024,
    # separator=" ",
)

vector_store = PGVectorStore.from_params(
    database=db_name,
    host=host,
    password=password,
    port=port,
    user=user,
    table_name="sansar_contract",
    embed_dim=384,  # openai embedding dimension
)

llm = LlamaCPP(
    model_path="./model/llama-2-13b-chat.Q4_0.gguf",
    temperature=0.1,
    max_new_tokens=256,
    # llama2 has a context window of 4096 tokens, but we set it lower to allow for some wiggle room
    context_window=3900,
    # kwargs to pass to __call__()
    generate_kwargs={},
    # kwargs to pass to __init__()
    # set to at least 1 to use GPU
    model_kwargs={"n_gpu_layers": 1},
    verbose=True,
)

retriever = VectorDBRetriever(
    vector_store, embed_model, query_mode="default", similarity_top_k=5
)
query_engine = RetrieverQueryEngine.from_args(retriever, llm=llm)

def _init_db():
    pass
    # conn = psycopg2.connect(connection_string)
    # conn = psycopg2.connect(
    #     dbname="postgres",
    #     host=host,
    #     password=password,
    #     port=port,
    #     user=user,
    # )
    # conn.autocommit = True

    # with conn.cursor() as c:
    #     c.execute(f"DROP DATABASE IF EXISTS {db_name}")
    #     c.execute(f"CREATE DATABASE {db_name}")


def init():
    _init_db()


def ingest_pdf(file_path):
    documents =  [
        Document(text=page.get_text().encode("utf-8"), extra_info={})
        for page in pymupdf.open(file_path)
    ]

    text_chunks = []
    # maintain relationship with source doc index, to help inject doc metadata in (3)
    doc_idxs = []
    for doc_idx, doc in enumerate(documents):
        cur_text_chunks = text_parser.split_text(doc.text)
        text_chunks.extend(cur_text_chunks)
        doc_idxs.extend([doc_idx] * len(cur_text_chunks))

    nodes = []
    for idx, text_chunk in enumerate(text_chunks):
        node = TextNode(
            text=text_chunk,
        )
        src_doc = documents[doc_idxs[idx]]
        node.metadata = src_doc.metadata
        nodes.append(node)

    # generate embeddings
    for node in nodes:
        node_embedding = embed_model.get_text_embedding(
            node.get_content(metadata_mode="all")
        )
        node.embedding = node_embedding

    # add the llama index nodes into postgres vector db
    vector_store.add(nodes)

def query(prompt):
    response = query_engine.query(prompt)
    return str(response)
