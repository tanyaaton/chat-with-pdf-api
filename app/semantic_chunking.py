import os
from dotenv import load_dotenv
from langchain_community.document_loaders import AzureAIDocumentIntelligenceLoader
from langchain.text_splitter import MarkdownHeaderTextSplitter


class SemanticChunker:
    def __init__(self):
        load_dotenv()
        self.doc_intelligence_endpoint = os.getenv("AZURE_DOC_ENDPOINT")
        self.doc_intelligence_key = os.getenv("AZURE_DOC_KEY")
        self.headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
            ]
        
    def process_with_loader(self, file_path):
        loader = AzureAIDocumentIntelligenceLoader(
            file_path=file_path,
            api_key= self.doc_intelligence_key,
            api_endpoint= self.doc_intelligence_endpoint,
            api_model="prebuilt-layout"  # or another model, based on your needs
        )
        docs = loader.load()  # Load the document using AzureAIDocumentIntelligenceLoader
        return docs

    def split_using_markdown(self, docs):
        text_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=self.headers_to_split_on)
        docs_string = docs[0].page_content
        splits = text_splitter.split_text(docs_string)
        return splits

    def adjust_chunk_size(slef, splits):
        i=0
        chunk_list = []
        while i < len(splits):
            metadata = splits[i].metadata
            content = splits[i].page_content
            while len(content) <500 and i<len(splits)-1:
                if len(content+splits[i+1].page_content)>1000:  
                    break
                else: 
                    i +=1
                    content = content+splits[i].page_content
            if '<table>' in content:
                table = '{Table}\n'
            else: table =''
            if '<figure>' in content:
                figure = '{Figure}\n' 
            else: figure =''
            chunk = str(metadata)+'\n'+table+figure+content
            i+=1
            chunk_list.append(chunk)
        return chunk_list
    
    def process_file(self, file_path):
        docs = self.process_with_loader(file_path)
        splits = self.split_using_markdown(docs)
        chunks = self.adjust_chunk_size(splits)
        return chunks