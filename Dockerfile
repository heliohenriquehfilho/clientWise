# Base image
ARG PYTHON_IMAGE=python:3.x-slim
FROM python:3.12-slim

WORKDIR /app

# Instale dependências
COPY requirements.txt .
RUN python -m pip install -r requirements.txt --no-cache-dir

# Copie o código da aplicação e o index.html
COPY . .
COPY index.html /usr/local/lib/python3.x/site-packages/streamlit/static/index.html

# Exponha a porta
EXPOSE 8501

# Execute a aplicação Streamlit
CMD ["streamlit", "run", "app.py"]
