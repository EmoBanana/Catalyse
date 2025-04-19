from pymongo import MongoClient, DESCENDING
from datetime import datetime, timedelta
from pymongo.server_api import ServerApi
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import gridfs
from pydantic import BaseModel
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
import asyncio
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import base64
from langchain_core.messages import HumanMessage
from langchain_core.messages import AIMessage
from langchain_core.messages import SystemMessage
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import MemorySaver
from langmem import create_manage_memory_tool, create_search_memory_tool
import time
import sys
import io
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from starlette.requests import Request
from starlette.responses import Response
import re
import glob
from pathlib import Path



app = FastAPI()



app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=['POST', 'OPTIONS'],
	allow_headers=["*"],
)



class AskRequest(BaseModel):
    query: str
    merchant_id: str

# Ensure all stdout/stderr is UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

merchant_id = '0c2d7'


class GraphContainer(BaseModel):
    title: str
    image_path: str
    current_data: str
    description: str
    
class NormalContainer(BaseModel):
    title: str
    current_data: str
    description: str

class QueryRequest(BaseModel):
    query: str
    merchant_id: str

class TextAnalytics(BaseModel):
    title: str
    image: str

message = []

model = ChatOpenAI(model="gpt-4.1-mini", 
    api_key="")

embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=""
)

store = InMemoryStore(
    index={
        "dims": 1536,
        "embed": embedding_model,
    }
) 

base = Path(__file__).resolve().parents[1] 
json_repository = os.path.join(base, 'src/components')

checkpointer = MemorySaver()

server_params = StdioServerParameters(
    command="python",  # Executable
    args=["new_mcp.py"],  # Optional command line arguments
    env=None,  # Optional environment variables
)

def check_cache(query: str):
    cached = db["query_cache"].find_one({"query": query}, {"_id": 0, "response": 1})
    return cached["response"] if cached else None

def save_to_cache(query: str, response: str):
    db["query_cache"].insert_one({
        "query": query,
        "response": response,
        "timestamp": datetime.now()
    })

async def run(messages):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # Get tools
            tools = await load_mcp_tools(session) + [
                create_manage_memory_tool(namespace=("memories",)),
                create_search_memory_tool(namespace=("memories",)),
            ]
            # Create and run the agent
            agent = create_react_agent(model, tools, store= store, checkpointer = checkpointer)
            agent_response = await agent.ainvoke({"messages": messages}, config = {"configurable":{"thread_id":1}})
            response = agent_response['messages'][-1].content
            return response

async def run_without_reasoning(messages):
    response = await model.ainvoke(messages, config = {"configurable":{"thread_id":1}})
    return response.content


ML_EXPLANATION_PROMPT = f'''
🧠 Role
You are a friendly and intelligent AI assistant who helps food stall owners understand prediction graphs from machine learning models. Your user is an experienced food seller (20+ years), but not tech-savvy. You explain what the future numbers (like from Prophet’s yhat) mean in the simplest way.

🎯 Task
When given a forecast graph (e.g., Prophet or ML model with yhat), explain what’s happening and what it means for the seller’s future sales or customer flow. No technical terms. Keep it practical and friendly, like chatting with a stall owner curious about what to expect next week.

📋 Format
📈 Summary: One clear sentence about the main trend (e.g., “Sales are likely to rise next month” or “Expect a slower week ahead”).
🔍 Key Observations:
Point out the highest and lowest predicted days or items.
Mention any big changes (spikes/drops) and possible reasons (e.g., weekend, rainy season, holiday).
Compare predictions if there are different items or customer types.
✅ Tip for Action: End with one helpful thing the seller can do next (e.g., “Get more chicken ready for the weekend” or “Consider a small discount midweek”).

⚠️ Important
Use only 4 simple sentences.
Avoid tech words like “model,” “forecast,” “dataframe,” etc.
Focus only on what helps the seller run their business better.
Never mention code or chart tools.
'''

GRAPH_EXPLANATION_PROMPT = f'''
🧠 Role
You are a friendly and intelligent AI assistant specialized in helping food business owners understand visual charts and business data. Your user is a food merchant with over 20 years of experience in selling food, but has little experience with computers or data analysis.

🎯 Task
When provided with a bar or line chart (e.g., from matplotlib or Plotly), analyze it and explain the insight in the simplest and most practical language. Focus on what the business owner needs to know. Do not use technical or computer terms. Speak as if you're chatting with a friend who runs a food stall and wants to know what’s happening in the numbers. And, lastly, save this convo in your memory.
Whenever the user provides JSON data or analysis results, use the 'manage_memory' tool to store the data under the 'memories' namespace.

📋 Format
1. 📈 Summary: Start with one sentence about the overall trend (e.g., "Sales went up in July" or "Customer visits dropped last week").
2. 🔍 Key Observations:
   - Say which food item or time period did best or worst.
   - Mention any spikes or drops, and suggest a simple reason (e.g., holiday, slow day).
   - Compare lines/bars clearly if there are multiple (e.g., “New customers came more often than returning ones.”)
3. ✅ Tip for Action: End with one clear suggestion the seller can try next (e.g., “Prepare more stock in the evenings” or “Try a promotion on quiet days”).

Important Notes:
- Use only 4 short sentences total.
- Use simple and friendly words.
- Focus only on what the seller needs to do better.
- Never include code or chart details.
- Remember this data for later use.

'''


NON_GRAPH_EXPLANATION_PROMPT = '''
🧠 Role
You are a smart and patient AI assistant helping a food merchant who has over 20 years of experience but limited computer skills. Your job is to review business data provided in JSON format (including sales numbers, customer activity, food performance, etc.) and explain what it means in clear and simple language.

🎯 Task
Using only the JSON data provided (no charts or images), give a short and easy-to-understand explanation of key business insights. Focus on helping the merchant make smarter decisions without using technical jargon. Each explanation must follow the exact format below.And, lastly, save this convo in your memory.
Whenever the user provides JSON data or analysis results, use the 'manage_memory' tool to store the data under the 'memories' namespace.

📋 Format
1. 📈 Summary: One line to say if business is doing well, poorly, or mixed based on the numbers.
2. 🔍 Observations:
   - Mention any increase or drop in key metrics (like income, customer count, price, etc.).
   - Clearly say whether there were more new or returning customers.
   - Point out any sharp spike or drop and suggest why (e.g., promotion, slow week, new item).
3. ✅ Recommendation: End with one clear and friendly tip the merchant could use to improve next month.

Important:
- Keep all explanations very simple and short.
- Do not include raw JSON unless it helps the explanation.
- Use emojis to make each section stand out and easier to follow.
- Use bullet points under "Observations" to keep it neat.
- Stick to a maximum of 5 sentences total.
- Remember this data for later use
'''

BOTTLENECK_OPPORTUNITY_PROMPT = '''
Role
You are a smart, memory-enabled AI assistant helping a food merchant with over 20 years of experience. Throughout past conversations, you’ve received various types of business data such as sales charts, customer behavior insights, and JSON statistics. Your job is to reflect on all of that data and give a concise summary that helps the merchant take action. And, lastly, save this convo in your memory.

Task
Using all the business data you’ve seen so far, do two things:
Identify the single most critical operational bottleneck (something hurting the merchant’s performance).
Identify one clear sales opportunity (something that could boost performance or earnings).

📋 Format
Only return valid JSON matching the schema:
{
  "bottleneck": "One simple sentence explaining the biggest operational issue.",
  "opportunity": "One simple sentence suggesting a sales opportunity the merchant should try."
}
IMPORTANT: Do not include other text, only json format
'''

message_non_graph = [
        SystemMessage(content=NON_GRAPH_EXPLANATION_PROMPT),
        HumanMessage(
            content=[
                {"type": "text", "text": "Please explain this json in simple terms."},
            ]
        )
    ]

uri = "mongodb+srv://haohong0127:Hongwork123@cluster.xlxyiby.mongodb.net/?retryWrites=true&w=majority&appName=Cluster"
db = MongoClient(uri, server_api=ServerApi('1'))["Umhack"]
fs = gridfs.GridFS(db)
graph_containers = []


def get_transport_average(collection):

    numeric_fields = [k for k, v in collection.find_one().items() if isinstance(v, (int, float)) and k != "_id"]


    group_stage = {
        "_id": None
    }
    for field in numeric_fields:
        group_stage[f"avg_{field}"] = {"$avg": f"${field}"}

    pipeline = [{"$group": group_stage}]
    context = json.dumps(list(collection.aggregate(pipeline)))
    message_non_graph[1].content.append({"type": "text", "text": context})
    description = asyncio.run(run_without_reasoning(message_non_graph))
    return NormalContainer(
    title= 'Transport',
    current_data= context,
    description=description)


def get_ranking(collection,merchant_id):
    context = list(collection.find({"merchant_id": merchant_id}, {"cuisine_tag":2,"rank_in_cuisine": 1, "_id": 0}).sort('rank_in_cuisine',DESCENDING))
    context_json = json.dumps(context)
    data = {}
    for i in context:
        data[i['cuisine_tag']] = i['rank_in_cuisine']
    message_non_graph[1].content.append({"type": "text", "text": context_json})
    description = asyncio.run(run_without_reasoning(message_non_graph))
    return NormalContainer(
    title= 'Ranking',
    current_data = json.dumps(data),
    description=description)
    

def get_monthly_income(collection, target_date):
    
    context = collection.find_one({"order_month": target_date},{"_id": 0, "total_earnings":1,'earning_growth_%':2})
    context_json = json.dumps(context)
    message_non_graph[1].content.append({"type": "text", "text": context_json})
    description = asyncio.run(run_without_reasoning(message_non_graph))
    return NormalContainer(
    title= 'Total Sales',
    current_data= f"\"RM {round(float(context['total_earnings']),2)}\"",
    description=description)

    

def get_cuisine_price(collection, merchant_id, db):
    # Get merchant name using merchant ID
    merchant_doc = db['delivery_outliers'].find_one(
        {"merchant_id": merchant_id},
        {"_id": 0, "merchant_name": 1}
    )

    if not merchant_doc:
        return json.dumps({"error": "Merchant not found"})

    merchant_name = merchant_doc['merchant_name']

    # Get merchant's cuisine tag and average price
    merchant_info = list(collection.find(
        {"merchant_name": merchant_name},
        {"_id": 0, "avg_price_per_item": 1, "cuisine_tag": 1}
    ))

    if not merchant_info:
        return json.dumps({"error": "Merchant cuisine data not found"})

    cuisine = [doc["cuisine_tag"] for doc in merchant_info]
    print(cuisine)
    merchant_price = [round(float(doc["avg_price_per_item"]),2) for doc in merchant_info]

    # Get all prices for this cuisine tag and compute average
    cursor = []
    other_prices = []
    cuisine_avg_price = []
    for i in cuisine:
        other_entries = collection.find(
            {"cuisine_tag": i},
            {"_id": 0, "avg_price_per_item": 1}
        )
        cursor.append(other_entries)
        prices = [round(float(doc["avg_price_per_item"]),2) for doc in other_entries if "avg_price_per_item" in doc]
        other_prices.append(prices)
        cuisine_avg_price.append(sum(prices) / len(prices))



    

    # Compute price difference
    valid_differences = [
    (mprice - aprice) / aprice * 100
    for mprice, aprice in zip(merchant_price, cuisine_avg_price)
    if aprice != 0
    ]

    difference = sum(valid_differences) / len(valid_differences) if valid_differences else 0
    context = json.dumps({
        "merchant_name": merchant_name,
        "merchant_price": merchant_price,
        "cuisine_avg_price": cuisine_avg_price,
        "price_difference_percentage": round(difference, 2),
    })
    message_non_graph[1].content.append({"type": "text", "text": context})
    description = asyncio.run(run_without_reasoning(message_non_graph))
     # 2. Add the generated description
    return NormalContainer(
    title= 'Market Price',
    current_data= context,
    description=description)
    
def identify_bottleneck_opportunity():
    bottleneck_opportunity_message = [
            SystemMessage(content=BOTTLENECK_OPPORTUNITY_PROMPT),
            HumanMessage(
                content=[
                    {"type": "text", "text": "Please inform me."},
                ]
            )
        ]
    return asyncio.run(run_without_reasoning(bottleneck_opportunity_message))

def analyse_content():
        target_date = datetime(2023, 12, 1)

        images_mapping = {'order_by_hour.png':['order_by_hour', 'collection.find_one({"order_hour": 9}, {"order_count": 1, "_id": 0})'], 'multi_day_hourly.png': ['item_order_perhour','collection.find_one({"order_day": "Sunday", "order_hour": 9},{"_id": 0, "order_count": 1})'], 'item_sales_breakdown.png': ['item_sales_breakdown', 'list(collection.find({"order_month": target_date},{"_id": 0, "item_name":1, "monthly_quantity": 2}))'], 'monthly_income.png': ['monthly_summary', 'collection.find_one({"order_month": target_date.strftime("%Y-%m-%d")},{"_id": 0, "total_earnings": 1} )'], 'new_old_ratio.png':['new_old_ratio','collection.find_one({"order_month": target_date},{"_id": 0, "New": 1,"Recurring":2,"New_change_%":3,"Recurring_Change_%":4})']}
        non_graph_container = [get_monthly_income(db['monthly_summary'], target_date.strftime('%Y-%m-%d')), get_ranking(db['ranking'],merchant_id),get_transport_average(db['transport']),get_cuisine_price(db['cuisine_merchant_summary'], merchant_id, db)]

        # Find by filename or ID
        for file in fs.find():
            try:
                print("Stored File:", file.filename, "| Upload Date:", file.upload_date)
                title = images_mapping[file.filename][0]
                collection = db[title]
                path = file.filename
                current_data = json.dumps(eval(images_mapping[file.filename][1]))
                image_data = base64.b64encode(file.read()).decode("utf-8")
                message = [
                    SystemMessage(content=GRAPH_EXPLANATION_PROMPT),
                    HumanMessage(
                        content=[
                            {"type": "text", "text": "Please explain this chart in simple terms."},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_data}"
                                }
                            }
                        ]
                    )
                ]
                description = asyncio.run(run(message))
                file.seek(0)
                with open(os.path.abspath(os.path.join(os.getcwd(), "../public", file.filename)), "wb") as f:
                    f.write(file.read())
                graph_containers.append(GraphContainer(
                        title= title,
                        image_path= path,
                        current_data= current_data,
                        description= description
                ))
            except Exception as e:
                continue

        json_data = [graph.model_dump() for graph in graph_containers]
        json_data2 = [text.model_dump() for text in non_graph_container]
        suggestions = identify_bottleneck_opportunity()
        file_name = f"Analysis_{merchant_id}_{datetime.today().isoformat()}.json"
        with open(os.path.join(json_repository, file_name), "w") as f:
            f.write(json.dumps({"graph_text_data":json_data,"text_data":json_data2, 'bottleneck_opportunity': suggestions}))
        return file_name

@app.get("/dashboard")
def initial_analysis():
    pattern = os.path.join(json_repository, f"Analysis_{merchant_id}_*.json")
    files = glob.glob(pattern)  
    if files:
        now = datetime.now()
        difference = now - datetime.fromisoformat(os.path.basename(files[0]).split("_")[-1].replace(".json", ""))
        if difference <= timedelta(hours=1):
            return JSONResponse(content={"file_name": os.path.basename(files[0])}) 
        else:
            os.remove(files[0])
            return JSONResponse(content={"file_name": analyse_content()})

    else:
        return JSONResponse(content={"file_name": analyse_content()})

@app.post("/ask")
async def normal_run(data: AskRequest):
    validate = check_cache(data.query)
    if validate == None:
        ORDINARY_PROMPT = f'''
        🧠 Role  
        You are a smart, memory-enabled assistant helping a veteran food merchant (20+ years experience). Your job is to analyze real-time business performance and operations using tools, memory, and live databases when needed.

        🎯 Task  
        When the user asks a question:
    -   1.. Use namespace = 'memories' when calling the tool.
        2. Check if it’s about business, operations, sales, or performance.
        3. If yes, query the database or use tools to get updated info.
        4. Give a clear, helpful answer — short, simple, and practical.
        5. Save the insight to memory for future reference.

        📌 Info  
        - User’s merchant ID: {data.merchant_id}  
        - User's merchant Name: Fried Chicken Express
        - Always prefer real-time data over assumptions.  
        - Use memory if it adds helpful context.  
        - Save all valuable insights using memory tools.  
        - For recommendations, browse external sources if needed.

        📋 Output Format  
        - 2–4 clear sentences: what’s happening, what to do, and why it matters.  
        - Speak in simple, business-friendly language — avoid technical terms.  
        - Optionally end with: “Want a deeper breakdown?”

        🛠️ Notes for Efficiency  
        - Respond in a maximum of 25 steps or fewer.  
        - Be direct — skip long intros or filler.  
        - Use tools/memory only when they improve accuracy.  
        - Avoid repetition or unnecessary chaining — stay lean and useful.
        '''
        global message
        message = [
                    SystemMessage(content=ORDINARY_PROMPT),
                    HumanMessage(
                        content=[
                            {"type": "text", "text": data.query + ""},
                        ]
                    )
                ]
        response =  await (run(message))
        save_to_cache(data.query, response)
        return JSONResponse(content={"response":response})
    else:
        time.sleep(1.5)
        return JSONResponse(content={"response":validate})

def retrieve_content_menu():
    existing_items = list(db['item_price'].find({},{'_id':0, "title": 1, 'price':1, 'image':1}))
    new_items = list(db['new_items'].find({},{'_id':0, "title": 1, 'price':1, 'image':1}))
    json_file = {}
    filenames = list(set([doc['image'] for doc in existing_items] + [doc['image'] for doc in new_items]))
    for file in fs.find({"filename": {'$in': filenames}}):
        with open(os.path.abspath(os.path.join(os.getcwd(), "../public", file.filename)), 'wb') as f:
            f.write(file.read())
    json_file['ExistingMenu'] = existing_items 
    json_file['newMenu'] = new_items 
    file_name = f"menu_{merchant_id}_{datetime.now().isoformat()}.json"
    with open(os.path.join(json_repository, file_name), "w") as f:
        f.write(json.dumps(json_file))
    return file_name

@app.get("/menu")
def retrieve_menu():
    pattern = os.path.join(json_repository, f"menu_{merchant_id}_*.json")
    files = glob.glob(pattern)  
    if files:
        now = datetime.now()
        difference = now - datetime.fromisoformat(os.path.basename(files[0]).split("_")[-1].replace(".json", ""))
        if difference <= timedelta(hours=1):
            return JSONResponse(content={'file_name':os.path.basename(files[0])})
        else:
            os.remove(files[0])
            return JSONResponse(content={'file_name':retrieve_content_menu()})

    else:
        return JSONResponse(content={'file_name':retrieve_content_menu()})

def retrieve_content_analytics():
    target_date = datetime(2024, 2, 29)
    images_mapping = {'customer_forecast_new.png':['customer_forecast_new', 'collection.find_one({"ds": target_date}, {"yhat": 1, "_id": 0})'], 'customer_forecast_rec.png': ['customer_forecast_recc','collection.find_one({"ds": target_date},{"_id": 0, "yhat": 1})'], 'forecast_orders.png': ['order_forecast', 'collection.find_one({"ds": target_date},{"_id": 0, "yhat":1})'], 'forecast_income.png': ['monthly_income', 'collection.find_one({"ds": target_date},{"_id": 0, "yhat": 1} )']}
    for item in list(db['foodforecast'].find({'ds':target_date})):
        title = item['item_name'] + " Forecast"
        path = f"forecast_{item['item_name'].replace(" ", "_")}_{item['cuisine_tag'].replace(" ", "_")}.png"
        current_data = f"RM {item['yhat']}"
        print(path)
        image = fs.find_one({"filename": path})
        image_data = base64.b64encode(image.read()).decode("utf-8")
        message = [
            SystemMessage(content= ML_EXPLANATION_PROMPT), #need a change
                HumanMessage(
                    content=[
                        {"type": "text", "text": "Please explain this forecast chart in simple terms."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_data}"
                            }
                        }
                    ]
            )
        ]
        description = asyncio.run(run_without_reasoning(message))
        image.seek(0)
        with open(os.path.abspath(os.path.join(os.getcwd(), "../public", image.filename)), "wb") as f:
            f.write(image.read())
        graph_containers.append(GraphContainer(
                    title= title,
                    image_path= path,
                    current_data= current_data,
                    description= description
        ))

    # Find by filename or ID
    for file in fs.find({"filename": {'$in': list(images_mapping.keys())}}):
            print("Stored File:", file.filename, "| Upload Date:", file.upload_date)
            title = images_mapping[file.filename][0]
            collection = db[title]
            path = file.filename
            current_data = json.dumps(eval(images_mapping[file.filename][1]))
            image_data = base64.b64encode(file.read()).decode("utf-8")
            message = [
                SystemMessage(content=ML_EXPLANATION_PROMPT),
                HumanMessage(
                    content=[
                        {"type": "text", "text": "Please explain this chart in simple terms."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_data}"
                            }
                        }
                    ]
                )
            ]
            description = asyncio.run(run_without_reasoning(message))
            file.seek(0)
            with open(os.path.abspath(os.path.join(os.getcwd(), "../public", file.filename)), "wb") as f:
                f.write(file.read())
            graph_containers.append(GraphContainer(
                    title= title,
                    image_path= path,
                    current_data= current_data,
                    description= description
            ))


    json_data = [graph.model_dump() for graph in graph_containers]

    text_analytics = [('Sentiment Distribution','sentiment_distribution.png'), ('Wordcloud Positve', 'wordcloud_positive.png'), ('Wordcloud Negative', 'wordcloud_negative.png')]
    TA_container = []

    output_dir = os.path.join(os.getcwd(), "catalyse/public")
    os.makedirs(output_dir, exist_ok=True)

    for name, col in text_analytics:
        file = fs.find_one({"filename":col})
        title = name
        with open(os.path.join(os.getcwd(), "catalyse/public", col), "wb") as f:
            f.write(file.read())
        TA_container.append(TextAnalytics(title = name, image = col).model_dump())

    json_file = {"MachineLearning":json_data, "TextAnalytics": TA_container}
    file_name = f"analytics_{merchant_id}_{datetime.now().isoformat()}.json"

    with open(os.path.join(json_repository, file_name), "w") as f:
        f.write(json.dumps(json_file))
    return file_name

@app.get("/analytics")
def Analytics():
    pattern = os.path.join(json_repository, f"analytics_{merchant_id}_*.json")
    files = glob.glob(pattern)  
    if files:
        now = datetime.now()
        difference = now - datetime.fromisoformat(os.path.basename(files[0]).split("_")[-1].replace(".json", ""))
        if difference <= timedelta(hours=1):
            return JSONResponse(content={"file_name":os.path.basename(files[0])})
        else:
            os.remove(files[0])
            return JSONResponse(content={"file_name":retrieve_content_analytics()})

    else:
        return JSONResponse(content={"file_name":retrieve_content_analytics()})