from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from django.conf import settings

api_key = settings.OPENAI_API_KEY

class EmergencyRAGChainer:
    def __init__(self, db_path):
        self.db_path = db_path
        self.embedding_model = OpenAIEmbeddings(api_key=api_key)
        template = '''Answer the question in korean, based only on the following context:

        context :
        {context}

        Question: {question}
        '''
        self.prompt = ChatPromptTemplate.from_template(template)
        self.model = ChatOpenAI(
            # model='gpt-4o-mini',
            model='ft:gpt-4o-mini-2024-07-18:personal:fine-tune-qadataset-model:AY0P3YLq',
            temperature=0,
            max_tokens=500,
            api_key=api_key
        )

    def load_vectorstore(self):
        return Chroma(
            persist_directory=self.db_path,
            embedding_function=self.embedding_model,
            collection_metadata={'hnsw:space': 'cosine'}
        )

    def create_retriever(self, vector_store):
        return vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 20, "alpha": 0.5},
        )

    def format_docs(self, docs):
        return '\n\n'.join([d.page_content for d in docs])

    def create_rag_chain(self):
        vector_store = self.load_vectorstore()
        retriever = self.create_retriever(vector_store)
        return {'context': retriever | self.format_docs, 'question': RunnablePassthrough()} | self.prompt | self.model | StrOutputParser()


def get_chain():
    chainer = EmergencyRAGChainer(db_path='./db/chromadb_1')
    return chainer.create_rag_chain()