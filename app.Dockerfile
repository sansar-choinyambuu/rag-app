FROM python:3.10
RUN apt update && apt install -y gcc clang clang-tools cmake

WORKDIR /app

COPY ./requirements.txt .
RUN pip3 install -r requirements.txt

# copy llm model
COPY ./model/llama-2-13b-chat.Q4_0.gguf .

# copy python code
COPY ./streamlit_app.py .
COPY ./rag.py .
COPY ./retriever.py .

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]