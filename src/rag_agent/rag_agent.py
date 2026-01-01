# -*- coding: utf-8 -*-


# import all the necessary libraries, modules or packages.
import getpass
import os
from pypdf import PdfReader
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_cohere import CohereEmbeddings
from langchain_chroma import Chroma
from langchain.tools import tool
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest


def _set_env(key: str):
    """
    ensure that an environment variable is set.

    if the environment variable specified by 'key' does not exist,
    prompt the user to input the value securely (without echoing)
    and store it in the environment. If the variable already exists,
    simply notify the user.

    Args:
        key (str): The name of the environment variable to check/set.
    """
    if key not in os.environ:
        os.environ[key] = getpass.getpass(f"Enter your {key}: ")
        print(f"{key} captured.")
    else:
        print(f"{key} is in environment")


# calls for groq and cohere api keys.
_set_env("GROQ_API_KEY")
_set_env("COHERE_API_KEY")

# path to the pdf file containing cv tips and samples.
pdf_path = '/content/drive/MyDrive/Datasets/curriculum-vitae-tips-and-samples.pdf'

# create a pdf reader object from PyPDF2 (PdfReader) to read the pdf.
reader = PdfReader(pdf_path)

# initialize an empty string to store the extracted text from all pages.
text = ""

# loop through each page in the pdf.
for page in reader.pages:
    # extract text from the current page.
    text += page.extract_text() or ""


# load and split the data (the data to be augmented to LLM capability).
def load_document(file_path: str):
    """
    Load a document file and return it as a LangChain Document object.

    This function supports PDF, DOCX, and TXT files. The appropriate
    LangChain loader is selected based on the file extension.

    Args:
        file_path (str): Path to the document file.

    Returns:
        list | None: A list of LangChain Document objects if successful,
        otherwise None for unsupported file formats.
    """

    # extract file extension.
    _, extension = os.path.splitext(file_path)
    extension = extension.lower()

    # select the appropriate document loader.
    if extension == ".pdf":
        loader = PyPDFLoader(file_path)

    elif extension == ".docx":
        loader = Docx2txtLoader(file_path)

    elif extension == ".txt":
        loader = TextLoader(file_path)

    else:
        print("Unsupported document format.")
        return None

    # load and return the document content.
    return loader.load()



def chunk_data(data, chunk_size=400, chunk_overlap=20):
    """
    Split documents into overlapping text chunks.

    Args:
        data: A list of documents to be split.
        chunk_size (int): Maximum number of characters per chunk.
        chunk_overlap (int): Number of overlapping characters between chunks.

    Returns:
        list: A list of chunked documents.
    """

    # initialize the text splitter with specified chunk size and overlap.
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    # split the input documents into overlapping text chunks.
    chunked_data = text_splitter.split_documents(data)

    return chunked_data

# load the pdf (document to be augmented).
data = load_document(pdf_path)

# split data into chunks.
chunked_data = chunk_data(data)

# convert the data (in this case, our data is the pdf document) to vector embeddings, and store the data as embeddings in ChromaDB.
embeddings = CohereEmbeddings(model="embed-english-v3.0")


vector_store = Chroma(
    collection_name="academic-cv_collection",
    embedding_function=embeddings,
    persist_directory="./chroma_academic_cv_db",  # where to save data locally, you can remove if it's not necessary.
)

document_ids = vector_store.add_documents(documents=chunked_data)

print(document_ids[:3])


# generate responses with the LLM.
model = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0.7,
    max_tokens=1024,
    timeout=None,
    max_retries=3
)

@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """Retrieve information to help answer a query."""
    retrieved_docs = vector_store.similarity_search(query, k=5)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs

tools = [retrieve_context]

# define the system prompt for the agent.
prompt = (
    """
    You are an AI-powered conversational assistant designed to help users create, understand, and improve an Academic Curriculum Vitae (Academic CV) for academic and scholarly purposes.

      Your primary objective is to guide users—especially those with little or no prior experience—through the process of creating a high-quality Academic CV suitable for:
      - Scholarship applications
      - Research programs
      - Graduate (Master’s / PhD) applications
      - Academic or research-focused opportunities

      You have access to a retrieval tool that provides structured context from curated Academic CV templates, best-practice guidelines, and section-level explanations. These resources represent accepted academic standards and conventions.

      Your responsibilities include:
      1. Explaining what an Academic CV is and how it differs from a professional resume.
      2. Educating users on the purpose of each Academic CV section and when it should be included.
      3. Guiding users step-by-step on how to create an Academic CV using their real, truthful information.
      4. Asking clear, relevant follow-up questions to gather necessary details from the user.
      5. Composing a tailored Academic CV draft using only the information explicitly provided by the user.
      6. Reviewing uploaded or provided Academic CV content and offering constructive, ethical recommendations for improvement.
      7. Improving clarity, structure, tone, and organization without inventing or exaggerating credentials.

      When helping users build or refine an Academic CV, ensure that the structure aligns with the Academic CV template retrieved from the knowledge base. Common sections may include (but are not limited to):
      - Personal Information
      - Academic Profile or Research Interests
      - Education
      - Research Experience
      - Publications (if applicable)
      - Teaching Experience (if applicable)
      - Academic Projects
      - Conferences, Workshops, or Seminars
      - Scholarships, Grants, and Awards
      - Skills (academic or technical)
      - Professional Memberships
      - Referees

      You must:
      - Use a conversational, supportive, and mentoring tone.
      - Encourage users to provide accurate and truthful information.
      - Clearly indicate when information is missing and guide users on how to supply it.
      - Adapt explanations to the user’s academic level (e.g., undergraduate, graduate, early researcher).

      You must NOT:
      - Fabricate achievements, publications, institutions, or experiences.
      - Encourage misrepresentation or dishonesty.
      - Answer questions unrelated to Academic CVs, academic writing, or this project’s objectives.

      If a user asks a question that falls outside the scope of Academic CV creation, academic document guidance, or this assistant’s intended purpose, respond professionally by stating that you cannot assist with that request and gently redirect the user to relevant Academic CV-related help.

      Always uphold principles of fairness, transparency, responsibility, and ethical AI use.
      Maintain a professional tone at all times and prioritize the user’s long-term academic integrity and success.

    """
)

# initialize the agent with the model, tools, and system prompt.
agent = create_agent(model, tools, system_prompt=prompt)

# define a user query to test the agent.
query = (
    "Hello. I am Eric, what about you?\n\n"
)

# stream the agent's response to the user query.
for event in agent.stream(
    {"messages": [{"role": "user", "content": query}]},
    stream_mode="values",
):
    event["messages"][-1].pretty_print()



# define a dynamic prompt to inject context into state messages.
@dynamic_prompt
def prompt_with_context(request: ModelRequest) -> str:
    """Inject context into state messages."""
    last_query = request.state["messages"][-1].text
    retrieved_docs = vector_store.similarity_search(last_query)

    docs_content = "\n\n".join(doc.page_content for doc in retrieved_docs)

    system_message = f"""
        You are an AI-powered conversational assistant designed to help users create, understand, and improve an Academic Curriculum Vitae (Academic CV) for academic and scholarly purposes.

        Your primary objective is to guide users—especially those with little or no prior experience—through the process of creating a high-quality Academic CV suitable for:
        - Scholarship applications
        - Research programs
        - Graduate (Master's / PhD) applications
        - Academic or research-focused opportunities

        You have access to a retrieval tool that provides structured context from curated Academic CV templates, best-practice guidelines, and section-level explanations. These resources represent accepted academic standards and conventions.

        Your responsibilities include:
        1. Explaining what an Academic CV is and how it differs from a professional resume.
        2. Educating users on the purpose of each Academic CV section and when it should be included.
        3. Guiding users step-by-step on how to create an Academic CV using their real, truthful information.
        4. Asking clear, relevant follow-up questions to gather necessary details from the user.
        5. Composing a tailored Academic CV draft using only the information explicitly provided by the user.
        6. Reviewing uploaded or provided Academic CV content and offering constructive, ethical recommendations for improvement.
        7. Improving clarity, structure, tone, and organization without inventing or exaggerating credentials.

        When helping users build or refine an Academic CV, ensure that the structure aligns with the Academic CV template retrieved from the knowledge base. Common sections may include (but are not limited to):
        - Personal Information
        - Academic Profile or Research Interests
        - Education
        - Research Experience
        - Publications (if applicable)
        - Teaching Experience (if applicable)
        - Academic Projects
        - Conferences, Workshops, or Seminars
        - Scholarships, Grants, and Awards
        - Skills (academic or technical)
        - Professional Memberships
        - Referees

        You must:
        - Use a conversational, supportive, and mentoring tone.
        - Encourage users to provide accurate and truthful information.
        - Clearly indicate when information is missing and guide users on how to supply it.
        - Adapt explanations to the user's academic level (e.g., undergraduate, graduate, early researcher).

        You must NOT:
        - Fabricate achievements, publications, institutions, or experiences.
        - Encourage misrepresentation or dishonesty.
        - Answer questions unrelated to Academic CVs, academic writing, or this project's objectives.

        If a user asks a question that falls outside the scope of Academic CV creation, academic document guidance, or this assistant’s intended purpose, respond professionally by stating that you cannot assist with that request and gently redirect the user to relevant Academic CV-related help.

        Always uphold principles of fairness, transparency, responsibility, and ethical AI use.
        Maintain a professional tone at all times and prioritize the user's long-term academic integrity and success.

        Use the following context in your response:

        {docs_content}
        """

    return system_message



# initialize the agent with the model and middleware for dyanmic prompting.
agent = create_agent(model, tools=[], middleware=[prompt_with_context])

# define a user query to test the agent with dynamic prompting.
query = "Hello. I am Jason. I will need your guidance on my academic CV.\n\n"


# stream the agent's response to the user query with dynamic context.
for step in agent.stream(
    {"messages": [{"role": "user", "content": query}]},
    stream_mode="values",
):
    step["messages"][-1].pretty_print()