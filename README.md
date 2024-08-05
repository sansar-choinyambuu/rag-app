# RAG AI assistant
Upload your pdf's as augmented context for your AI prompts.

- built with streamlit: https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps
- built with llamaindex: https://docs.llamaindex.ai/en/stable/examples/low_level/oss_ingestion_retrieval/

Main components:
- vector db (postgresql with pgvector)
- llm [llama-2-chat-13b-ggml model](https://huggingface.co/TheBloke/Llama-2-13B-chat-GGML)

## Postgres as vector database
`brew install postgresql`
```
vi ~/.bashrc
export LDFLAGS="-L/opt/homebrew/opt/postgresql@16/lib"
export CPPFLAGS="-I/opt/homebrew/opt/postgresql@16/include"
export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH
```

install pgvector https://github.com/pgvector/pgvector
```
cd /tmp
git clone --branch v0.7.3 https://github.com/pgvector/pgvector.git
cd pgvector
make
make install # may need sudo
```

create role
```
psql
CREATE ROLE <user> WITH LOGIN PASSWORD '<password>';
ALTER ROLE <user> SUPERUSER;
```

## pending
- packaging with Docker and docker-compose is not complete
- llm model path is local, needs to be downloaded