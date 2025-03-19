# Use an official Python image
FROM python:3.10

# Set the working directory
WORKDIR /app/app

# Copy all files
COPY . /app

# Install dependencies without unnecessary flags
RUN pip install --no-cache-dir \
    chromadb==0.6.3 \
    pandas==2.2.3 \
    pymilvus==2.5.5 \
    langchain_openai==0.3.8 \
    langchain==0.3.20 \
    pypdf==5.3.1 \
    google-genai==1.5.0 \
    langchain-community==0.3.19 \
    azure-ai-documentintelligence==1.0.1 \
    azure-ai-formrecognizer==3.3.3
    

# Expose FastAPI port
EXPOSE 7777

# Run the FastAPI app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7777", "--reload"]
