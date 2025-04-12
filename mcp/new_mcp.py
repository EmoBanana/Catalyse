# server.py
from mcp.server.fastmcp import FastMCP, Context
from dotenv import load_dotenv
import os
from langchain_community.tools import BraveSearch
import httpx 
import asyncio
from bs4 import BeautifulSoup
import json
#playwright 
#captcha solver
from dataclasses import dataclass
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator


@dataclass
class AppContext:
    db: MongoClient


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with type-safe context"""
    uri = "mongodb+srv://haohong0127:Hongwork123@cluster.xlxyiby.mongodb.net/?retryWrites=true&w=majority&appName=Cluster"
    client = MongoClient(uri, server_api=ServerApi('1'))
    try:
        yield AppContext(db=client)
    finally:
        client.close()



load_dotenv(dotenv_path="secret.env")

brave_search_api = "BSAuaNApqhevBk3yppJtcPmITC2VR6s"
# Create an MCP server
mcp = FastMCP("Browser", lifespan=app_lifespan)

search_tool = BraveSearch.from_api_key(api_key = brave_search_api, search_kwargs={"count":3})

async def fetch_pages(url):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            body = soup.find("body")
            if body:
                return body.get_text(separator="\n", strip=True)
            else:
                return f"[No <body> tag found for {url}]"
        except Exception as e:
            return f"[Error fetching {url}]: {str(e)}"
    

async def main(urls):
    tasks = [fetch_pages(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return results

@mcp.tool()
async def browse_internet(query: str) -> str:
    """
    Searches the internet in real-time to retrieve information not present in the LLM's training data.

    This tool:
    - Uses a live search engine to find relevant web pages for the given query.
    - Fetches and parses the HTML content of each result.
    - Returns the raw or structured content (e.g., page body text) from those pages.

    Useful for answering up-to-date questions about recent events, facts, or topics the LLM may not know.

    Args:
        query (str): The user's search question or topic.

    Returns:
        str: Combined text or HTML from the <body> of top search result pages.
    """
    result = json.loads(search_tool.run(query))
    urls = [i['link'] for i in result]
    contents = await main(urls)
    return contents

# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b
        

@mcp.tool()
def multiply(a: float, b:float) -> float:
    """multiply two numbers"""
    return a*b

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

@mcp.tool()
async def description_database(ctx:Context) -> str:
    """Tools to get the description of database"""
    try:
        db = ctx.request_context.lifespan_context.db['Umhack']
        collections = db.list_collection_names()
        descriptions = {}
        print(collections)
        for c in collections:
            c = db[c]
            doc = c.find_one()
            if doc:
                descriptions[c] = [f"- {key}: {type(value).__name__}" for key, value in doc.items()]
            else:
                descriptions[c] = ["(No documents found)"]
        output = ""
        for name, fields in descriptions.items():
            output += f"\n📂 Collection: {name}"
            for line in fields:
                output += "\n" + line + "\n"
        return output
    except Exception as e:
        print(e)

@mcp.tool()
async def query_database(ctx:Context, collection:str, query:dict, limit: int=2) -> str:
    """
    Query documents from a MongoDB collection.
    
    Args:
        collection_name: The name of the collection
        query: MongoDB query filter in JSON format (default: empty query that matches all documents)
        limit: Maximum number of documents to return (default: 10)
        
    Returns:
        List of documents matching the query
    """
    try:
        db = ctx.request_context.lifespan_context.db['Umhack']
        result = list(db[collection].find(query).limit(limit))
        
        return (result)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    mcp.run()
