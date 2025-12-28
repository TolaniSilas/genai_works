import os
import getpass
import pathlib
import requests
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command



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


# calls for google and langsmith api keys.
_set_env("GOOGLE_API_KEY")
_set_env("LANGSMITH_API_KEY")


# initialize a google gemini chat model to be used as the LLM.
model = ChatGoogleGenerativeAI(model="gemini-3-flash-preview")

# model = ChatGoogleGenerativeAI(model="gemini-3-pro-preview")


# url of the Chinook SQLite database to download.
url = "https://storage.googleapis.com/benchmarks-artifacts/chinook/Chinook.db"

# local path where the database will be saved.
local_path = pathlib.Path("Chinook.db")

# check if the file already exists locally.
if local_path.exists():
    print("chinook database already exists! skip downloading.")

else:
    # download the file from the url.
    response = requests.get(url)

    # if the download is successful, save the binary file locally.
    if response.status_code == 200:
        local_path.write_bytes(response.content)
        print(f"file downloaded and saved as {local_path}")

    else:
        # print an error message if the download failed.
        print(f"failed to download the file. Status code: {response.status_code}")


# create a connection to the SQLite database using its uri.
db = SQLDatabase.from_uri("sqlite:///Chinook.db")

# print the SQL dialect used by the connected database.
print(f"dialect: {db.dialect}")

# retrieve and display the list of usable tables in the chinook database.
print(f"available tables: {db.get_usable_table_names()}")

# execute a sample SQL query to fetch a few rows from the Artist table, and print the output to verify database access.
print(f"sample Output: {db.run('SELECT * FROM Artist LIMIT 5;')}")


# initialize the SQL database toolkit by combining the connected database with the LLM that will reason about SQL queries.
toolkit = SQLDatabaseToolkit(db=db, llm=model)

# Extract the list of SQL-related tools provided by the toolkit. these tools define the actions the agent can perform on the database.
tools = toolkit.get_tools()

# iterate through each tool and display its name and description for inspection and understanding of the agent's available capabilities.
for tool in tools:
    print(f"{tool.name}: {tool.description}\n")


# set the maximum number of results to return unless the user specifies otherwise.
top_k=5

# define the system prompt to customize the agent's behavior and instructs it on how to interact with the SQL database.
system_prompt = f"""
You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct {db.dialect} query to run, then look at the results of the query and return the answer.
Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most {top_k} results.

You can order the results by a relevant column to return the most interesting examples in the database. Never query for all the columns from a specific table,
only ask for the relevant columns given the question.

You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the
database.

To start you should ALWAYS look at the tables in the database to see what you
can query. Do NOT skip this step.

Then you should query the schema of the most relevant tables.

Once the query executes successfully, **use the results to generate a clear, concise, and conversational response** to the user.
Make sure your response reflects only the information obtained from the executed query.
"""

# create the ai agent with the specified model, tools, and system prompt.
agent = create_agent(
    model,
    tools,
    system_prompt=system_prompt
)

# define the user question to ask the agent.
question = "Which genre on average has the longest tracks?"

# stream the agent's responses step by step.
for step in agent.stream(
    {"messages": [{"role": "user", "content": question}]},
    stream_mode="values",
):

    # print the latest message from the agent in a readable format.
    step["messages"][-1].pretty_print()
