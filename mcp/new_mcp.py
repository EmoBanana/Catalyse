from mcp.server.fastmcp import FastMCP, Context
from dotenv import load_dotenv
import os
from langchain_community.tools import BraveSearch
import httpx 
import re
import asyncio
from bs4 import BeautifulSoup
from pydantic import BaseModel
import json
#playwright 
#captcha solver
from dataclasses import dataclass
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
import asyncio
import sys
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import base64
from langchain_core.messages import HumanMessage
from langchain_core.messages import AIMessage
from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime
from langchain.chains import LLMChain
import pickle

# Path to your service account credentials
SERVICE_ACCOUNT_FILE = 'GCC_account.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Authenticate the service account
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

# Build the Calendar API client
service = build('calendar', 'v3', credentials=credentials)

# Your shared calendar ID
calendar_id = '1fcbaedeedb15f25a1c8e71ad79eded5f1a118c95cf4c32f091ce736c140e41d@group.calendar.google.com'


if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

path = os.getcwd()


@dataclass
class AppContext:
    db: MongoClient

class DateTimeField(BaseModel):
    dateTime: str
    timeZone: str

class GoogleCalendarEvent(BaseModel):
    summary: str
    location: str
    description: str 
    start: DateTimeField
    end: DateTimeField

class GoogleEventList(BaseModel):
    event_list: list[GoogleCalendarEvent]

class Prediction(BaseModel):
    model: str = None
    num_months: int = None

class MenuItem(BaseModel):
    price: float 
    title: str


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with type-safe context"""
    uri = "mongodb+srv://haohong0127:Hongwork123@cluster.xlxyiby.mongodb.net/?retryWrites=true&w=majority&appName=Cluster"
    client = MongoClient(uri, server_api=ServerApi('1'))
    try:
        yield AppContext(db=client)
    finally:
        client.close()



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

@mcp.tool()
async def description_database(ctx:Context) -> str:
    """Tools to get the description of database related to the user/merchant business"""
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

async def querying_llm(template:str, model_name:str, input_variables:list[str], input_dict:dict, partial_variables: dict= {}):
    prompt_template = PromptTemplate(
        template = template,
        input_variables = input_variables,
        partial_variables = partial_variables
    )

    model = ChatOpenAI(model=model_name, 
    api_key="")

    chain = prompt_template | model

    result =  await chain.ainvoke(input_dict)

    if isinstance(result, AIMessage):
        return result.content  # returns the actual string message from the LLM

    return str(result)


@mcp.tool()
async def timeline_scheduling(plan_before_elaboration:str, duration_in_days:str):
    '''
    Generates a strategic calendar event from a vague business context.

    This tool takes an unstructured input (e.g., a business issue or goal), a time bound to perform two steps:
    1. It analyzes the context and provides a concise, implementation-ready business recommendation.
    2. It then  converts that recommendation into a structured Google Calendar event in JSON format, ready for scheduling.

    The event includes:
    - Summary
    - Description
    - Start & end time (ISO format)
    - Location
    - Timezone

    Use this tool to translate business intent into actionable, time-bound plans. OR
    Use this tool when user ask to generate schedule for them.
    '''
    recommendation_prompt = '''
    🧠 Role–Task–Format Prompt: Strategic Business Plan with Campaign-Centric Milestones
    👤 Role:
    You are a senior business strategist with over two decades of experience advising C-level executives across industries.
    Your strength lies in translating vague business intent into concrete, time-bound, and campaign-driven execution plans. You think holistically across departments — but treat marketing campaigns as a core business driver, not a side function.

    🎯 Task:
    Analyze the following unstructured business context and create a professional, comprehensive execution roadmap that the organization can begin implementing immediately.

    Your plan should:

    Be rational, outcome-driven, and implementation-ready

    Include a logical sequence of phases or milestones — not limited to 5 — structure as many as needed for effective execution

    Blend internal strategic activities (e.g., alignment, planning, resource deployment) with external marketing campaign milestones (e.g., content creation, channel launches, performance reviews)

    Be written as a succinct, well-structured narrative — not a bullet list — that clearly flows from initial intent to measurable outcomes

    📌 Specific Instructions:

    Do not restate the original context — jump straight into the strategic plan

    Treat marketing campaign events as fundamental to success — include them as key milestones (e.g., "Social rollout", "Go-live teaser", "Ad creative approval", "Campaign analytics review")

    Make each phase time-bound, logically connected, and actionable across teams

    The structure should make it easy to convert each step into a calendar event if needed

    ✍️ Input Format:
    📄 Business Context:
    "{plan_before_elaboration}"

    📅 Execution Start Date:
    "{date}"
    📆 Strategic Timeframe or Window:
    "{time}"

    📌 Strategic Execution Plan (Marketing-Led & Milestone-Based):
    '''
    
    description = await querying_llm(recommendation_prompt, "o4-mini", ['plan_before_elaboration', 'time', 'date'], {'plan_before_elaboration': plan_before_elaboration, 'time' :duration_in_days, 'date':datetime.datetime.today()})
    
    event_generation_prompt = '''You are an elite AI scheduling assistant trained to build a full event timeline from a business plan.

    Based on the input description, break it into 3–5 key events that need to be scheduled (e.g., kickoff meeting, review session, final launch).

    For each event, return the following fields:
    - summary
    - location
    - description
    - start (in ISO 8601 format)
    - end (in ISO 8601 format)
    - timeZone ("Asia/Kuala_Lumpur" by default)

    Return the full output as a JSON object with the format:

    {format_instructions}

    ---

    📋 Plan description:
    "{plan_before_elaboration}"

    💡 Output only the structured event list in JSON format.
    '''
    
    parser = PydanticOutputParser(pydantic_object=GoogleEventList)

    events_list = parser.parse(await querying_llm(event_generation_prompt, "gpt-4.1-mini", ["plan_before_elaboration"], {"plan_before_elaboration": description}, {"format_instructions": parser.get_format_instructions()})).event_list

    for event in events_list:
        created_event = service.events().insert(calendarId=calendar_id, body=event.model_dump()).execute()
        print("✅ Event created:", created_event['htmlLink'])
    return description + "Here's the timeline generated, show them and tell them the calendar is ready to view  and stop the iteration."

@mcp.tool()
async def prediction(predict:Prediction):
    '''
    Generates future predictions using a pre-trained time series forecasting model.

    This tool loads a saved Prophet model based on the input category (e.g., sales, customer types, or menu items),
    forecasts future values for the specified number of months, and returns a structured prediction output.

    Model available:
    "order", "new_customer", "rec_customer", "income", "4_piece", "chicken_waffles", "potato","spicy_chicken" 

    Input:
    - model: str — the type of model to load (e.g., 'order', 'income', 'spicy_chicken')
    - num_months: int — number of months into the future to forecast

    Process:
    1. Loads the corresponding model from disk
    2. Generates a future time range
    3. Uses the model to predict future values
    4. Extracts and returns a list of date-value pairs in the format: [{'ds': 'YYYY-MM-DD', 'yhat': prediction}, ...]

    Output:
    - model: name of the model used
    - predictions: list of forecasted values per month

    Use this tool to support demand planning, inventory decisions, and campaign timing using data-driven forecasts.
    '''
    model_paths = {
        "order" : "order_forecast.pkl",
        "new_customer" : "new_customer_forecast.pkl",
        "rec_customer" : "recc_customer_forecast.pkl",
        "income" : "income_forecast.pkl",
        "4_piece" : "4-Piece_Chicken_Meal_Fried_Chicken.pkl",
        "chicken_waffles" : "Chicken_&_Waffles_Fried_Chicken.pkl",
        "potato" : "Potato_Wedges_Side.pkl",
        "spicy_chicken" : "Spicy_Chicken_Tenders_Fried_Chicken.pkl"
    }

    model_file = os.path.join(path, "ML_model", model_paths[predict.model])

    with open(model_file, 'rb') as f:
        loaded_model = pickle.load(f)

    future = loaded_model.make_future_dataframe(periods=predict.num_months, freq='M')
    forecast = loaded_model.predict(future)
    new_forecast = forecast.tail(predict.num_months)
    filtered = new_forecast[['ds', 'yhat']].round()
    result = filtered.to_dict(orient='records')
    return {"model":predict.model,"predictions": result}




@mcp.tool()
async def query_database(ctx:Context, collection:str, query:dict, limit: int=2) -> str:
    """
    Query documents from a MongoDB collection that comprises the merchant business data.
    Such as transport, ranking, monthly sales summary, and customer growth and etc.
    Use if user ask something related to their business which does not require web search.
    
    📂 Collection: order_forecast
    - _id: ObjectId → 6800722ea1654ee8b13e53e5
    - ds: datetime → 2023-01-01 00:00:00
    - trend: float → 3034.791968
    - yhat_lower: float → 2935.2166948058693
    - yhat_upper: float → 3136.062449316533
    - trend_lower: float → 3034.791968
    - trend_upper: float → 3034.791968
    - additive_terms: float → 0.0
    - additive_terms_lower: float → 0.0
    - additive_terms_upper: float → 0.0
    - multiplicative_terms: float → 0.0
    - multiplicative_terms_lower: float → 0.0
    - multiplicative_terms_upper: float → 0.0
    - yhat: float → 3034.791968

    📂 Collection: customer_forecast_new
    - _id: ObjectId → 6800722da1654ee8b13e53c4
    - ds: datetime → 2023-01-01 00:00:00
    - trend: float → 3000.620324
    - yhat_lower: float → 2899.125074182523
    - yhat_upper: float → 3114.8126568306566
    - trend_lower: float → 3000.620324
    - trend_upper: float → 3000.620324
    - additive_terms: float → 0.0
    - additive_terms_lower: float → 0.0
    - additive_terms_upper: float → 0.0
    - multiplicative_terms: float → 0.0
    - multiplicative_terms_lower: float → 0.0
    - multiplicative_terms_upper: float → 0.0
    - yhat: float → 3000.620324
    - pct_change: float → nan

    📂 Collection: cuisine_merchant_summary
    - _id: ObjectId → 68006af9d71dc1fe5ff878b7
    - cuisine_tag: str → Fried Chicken
    - merchant_name: str → Fried Chicken Express
    - num_items: int → 3
    - avg_price_per_item: float → 9.17
    - items: list → ['4-Piece Chicken Meal', 'Chicken & Waffles', 'Spicy Chicken Tenders']
    - type: str → merchant_summary

    📂 Collection: keywords
    - _id: ObjectId → 68006787d9ddb7fdee9c10f6
    - Unnamed: 0: int → 0
    - keyword: str → fried spring rolls
    - view: int → 37816
    - menu: int → 11185
    - checkout: int → 3882
    - order: int → 153

    📂 Collection: golden_hour
    - _id: ObjectId → 680067cc3bb1e8224ce20ddd
    - order_hour: int → 6
    - total_delivery_mins: float → 38.5163139329806

    📂 Collection: order_by_hour
    - _id: ObjectId → 680067ca3bb1e8224ce20d4f
    - order_hour: int → 6
    - order_count: int → 2268

    📂 Collection: delivery_outliers
    - _id: ObjectId → 68006b00d71dc1fe5ff908ed
    - order_id: str → 9332e40b7
    - item_id: int → 286
    - merchant_id: str → 0c2d7
    - order_time: datetime → 2023-01-24 21:00:00
    - driver_arrival_time: datetime → 2023-01-24 21:15:00
    - driver_pickup_time: datetime → 2023-01-24 21:21:00
    - delivery_time: datetime → 2023-01-24 21:51:00
    - order_value: float → 197.99
    - eater_id: int → 1000417022
    - cuisine_tag: str → Fried Chicken
    - item_name: str → Spicy Chicken Tenders
    - item_price: float → 8.0
    - merchant_name: str → Fried Chicken Express
    - join_date: int → 2032017
    - city_id: int → 4
    - estimated_quantity: int → 24
    - customer_type: str → New
    - order_month: datetime → 2023-01-01 00:00:00
    - order_to_arrival_mins: float → 15.0
    - arrival_to_pickup_mins: float → 6.0
    - pickup_to_delivery_mins: float → 30.0
    - total_delivery_mins: float → 51.0
    - outlier_columns: list → ['order_value_outlier', 'estimated_quantity_outlier']

    📂 Collection: fs.files
    - _id: ObjectId → 680067ca3bb1e8224ce20d41
    - filename: str → new_old_ratio.png
    - contentType: str → image/png
    - chunkSize: int → 261120
    - length: Int64 → 55129
    - uploadDate: datetime → 2025-04-17 02:30:34.237000

    📂 Collection: ranking
    - _id: ObjectId → 68006af9d71dc1fe5ff878b9
    - cuisine_tag: str → Fried Chicken
    - merchant_id: str → 0c2d7
    - merchant_name: str → Fried Chicken Express
    - total_sales: float → 3885334.67
    - city_area: str → 4
    - rank_in_cuisine: int → 1
    - highlight: bool → True

    📂 Collection: new_old_ratio
    - _id: ObjectId → 680067ca3bb1e8224ce20d43
    - order_month: str → 2023-01-01
    - New: int → 3079
    - Recurring: int → 38
    - New_Change_%: float → nan
    - Recurring_Change_%: float → nan

    📂 Collection: item_order_perhour
    - _id: ObjectId → 680067cb3bb1e8224ce20d64
    - order_day: str → Friday
    - order_hour: int → 6
    - order_count: int → 319

    📂 Collection: monthly_income
    - _id: ObjectId → 6800722fa1654ee8b13e53f6
    - ds: datetime → 2023-01-01 00:00:00
    - trend: float → 393356.25445824
    - yhat_lower: float → 368492.0609294877
    - yhat_upper: float → 415148.80157850136
    - trend_lower: float → 393356.25445824
    - trend_upper: float → 393356.25445824
    - additive_terms: float → 0.0
    - additive_terms_lower: float → 0.0
    - additive_terms_upper: float → 0.0
    - multiplicative_terms: float → 0.0
    - multiplicative_terms_lower: float → 0.0
    - multiplicative_terms_upper: float → 0.0
    - yhat: float → 393356.25445824

    📂 Collection: master_merchant
    - _id: ObjectId → 67ffe4b8402c58c4cea375a8
    - order_id: str → 8f1ef0988
    - item_id: int → 242
    - merchant_id: str → 0c2d7
    - order_time: datetime → 2023-08-11 10:12:00
    - driver_arrival_time: str → 2023-08-11 10:19:00
    - driver_pickup_time: str → 2023-08-11 10:24:00
    - delivery_time: str → 2023-08-11 10:46:00
    - order_value: float → 33.1
    - eater_id: int → 1000067003
    - cuisine_tag: str → Fried Chicken
    - item_name: str → 4-Piece Chicken Meal
    - item_price: float → 9.5
    - merchant_name: str → Fried Chicken Express
    - join_date: int → 2032017
    - city_id: int → 4
    - estimated_quantity: int → 3
    - customer_type: str → New
    - order_month: datetime → 2023-08-01 00:00:00

    📂 Collection: customer_forecast_recc
    - _id: ObjectId → 6800722ea1654ee8b13e53d5
    - ds: datetime → 2023-01-01 00:00:00
    - trend: float → 35.150322
    - yhat_lower: float → 25.99257344955633
    - yhat_upper: float → 44.68873377194271
    - trend_lower: float → 35.150322
    - trend_upper: float → 35.150322
    - additive_terms: float → 0.0
    - additive_terms_lower: float → 0.0
    - additive_terms_upper: float → 0.0
    - multiplicative_terms: float → 0.0
    - multiplicative_terms_lower: float → 0.0
    - multiplicative_terms_upper: float → 0.0
    - yhat: float → 35.150322
    - pct_change: float → nan

    📂 Collection: transport
    - _id: ObjectId → 68006af9d71dc1fe5ff878c7
    - order_to_arrival_mins: float → 7.0
    - arrival_to_pickup_mins: float → 5.0
    - pickup_to_delivery_mins: float → 22.0
    - total_delivery_mins: float → 34.0

    📂 Collection: item_sales_breakdown
    - _id: ObjectId → 680067cd3bb1e8224ce20dfe
    - cuisine_tag: str → Fried Chicken
    - item_name: str → 4-Piece Chicken Meal
    - order_month: datetime → 2023-01-01 00:00:00
    - monthly_quantity: int → 18598

    📂 Collection: monthly_summary
    - _id: ObjectId → 68006af9d71dc1fe5ff878bb
    - order_month: str → 2023-01-01
    - total_earnings: float → 379151.72
    - total_quantity_sold: int → 49963
    - earnings_growth_%: float → nan
    - quantity_growth_%: float → nan

    📂 Collection: keyword_funnel
    - _id: ObjectId → 680067cd3bb1e8224ce20e30
    - keyword: str → potato wedges
    - stage: str → menu
    - percent: float → 19.469399213924763
    ⛔ Skipping fs.chunks collection

    📂 Collection: foodforecast
    - _id: ObjectId → 6800722fa1654ee8b13e5407
    - ds: datetime → 2023-12-31 00:00:00
    - yhat: float → 17928.18
    - yhat_lower: float → 16372.77
    - yhat_upper: float → 19568.27
    - pct_change: float → -0.94
    - pct_change_lower: float → -0.04
    - pct_change_upper: float → -0.81
    - cuisine_tag: str → Fried Chicken
    - item_name: str → 4-Piece Chicken Meal

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

@mcp.tool()
def add_new_menu_items(item:MenuItem):
    """
    Inserts a new JSX component representing a menu item into the `action.js` frontend component file.

    This tool takes structured input representing a new menu item (title, price), and:
    1. Constructs a formatted JSX <div> block using the provided data.
    2. Searches for a placeholder comment `/* Replace */` in the specified React file.
    3. Replaces that placeholder with the generated JSX snippet, preserving the rest of the file.

    The generated JSX includes:
    - Title
    - Price

    This tool helps dynamically inject visual UI elements based on backend logic or content-driven updates.

    Example use case: Adding new unapproved items to a review dashboard in real time.
    """
    template = f'''
            <div key= "1" className="newmenu-card">
                <img
                  src= "customer.jpg"
                  alt="{item.title}"
                  className="menu-image"
                  onClick={{() => handleImageClick("customer.jpg")}}
                />
                <h2 className="menu-title">{item.title}</h2>
                <div className="menu-details">
                  <p className="menu-price">
                    RM {item.price}
                  </p>
                  <button className="menu-status">Approve</button>
                </div>
            </div>'''
    
    file_path = "/home/haoho/projects/new_mcp/UMHack/Catalyse/src/components/action.js"

    # 1. Read the file
    with open(file_path, "r") as f:
        lines = f.readlines()

    # 2. Modify the lines
    text = []
    for line in lines:
        if re.search(r"\{?/\* Replace \*/\}?", line):  
            text.append(template + "\n")        
            continue
        text.append(line)

    # 3. Write the modified content back
    with open(file_path, "w") as w:
        w.writelines(text)
    return "File changes, you may now revert back to the menu."


        



if __name__ == "__main__":
    mcp.run(transport="stdio")
