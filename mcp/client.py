from pymongo import MongoClient, DESCENDING
from datetime import datetime
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
from openai import OpenAI
from langchain_core.tools import tool
import asyncio
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import base64
from langchain_core.messages import HumanMessage
from langchain_core.messages import AIMessage
from langchain_core.messages import SystemMessage
from langgraph.store.memory import InMemoryStore
from langmem import create_manage_memory_tool, create_search_memory_tool

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


model = ChatOpenAI(model="gpt-4o", 
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

server_params = StdioServerParameters(
    command="python",  # Executable
    args=["new_mcp.py"],  # Optional command line arguments
    env=None,  # Optional environment variables
)

async def run(message):
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
            agent = create_react_agent(model, tools, store=store)
            agent_response = await agent.ainvoke({"messages": message})
            response = agent_response['messages'][-1].content
            print(response)
            return response



#asyncio.run(run())

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
    description = asyncio.run(run(message_non_graph))
    context_dict = json.loads(context) 
    return NormalContainer(
    title= 'Transport',
    current_data= context,
    description=description)


def get_ranking(collection,merchant_id):
    context = json.dumps(list(collection.find({"merchant_id": merchant_id}, {"cuisine_tag":2,"rank_in_cuisine": 1, "_id": 0}).sort('rank_in_cuisine',DESCENDING)))
    message_non_graph[1].content.append({"type": "text", "text": context})
    description = asyncio.run(run(message_non_graph))
    context_dict = json.loads(context) 
    return NormalContainer(
    title= 'Ranking',
    current_data= context,
    description=description)
    

def get_monthly_income(collection, target_date):
    context = json.dumps(collection.find_one({"order_month": target_date},{"_id": 0, "total_earnings":1,'earning_growth_%':2}))
    message_non_graph[1].content.append({"type": "text", "text": context})
    description = asyncio.run(run(message_non_graph))
    context_dict = json.loads(context) 
    return NormalContainer(
    title= 'Total Sales',
    current_data= context,
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
    merchant_info = collection.find_one(
        {"merchant_name": merchant_name},
        {"_id": 0, "avg_price_per_item": 1, "cuisine_tag": 1}
    )

    if not merchant_info:
        return json.dumps({"error": "Merchant cuisine data not found"})

    cuisine = merchant_info["cuisine_tag"]
    merchant_price = merchant_info["avg_price_per_item"]

    # Get all prices for this cuisine tag and compute average
    cursor = collection.find(
        {"cuisine_tag": cuisine},
        {"_id": 0, "avg_price_per_item": 1}
    )

    prices = [doc["avg_price_per_item"] for doc in cursor if "avg_price_per_item" in doc]

    if not prices:
        return json.dumps({"error": "No other prices found for this cuisine"})

    cuisine_avg_price = sum(prices) / len(prices)

    # Compute price difference
    difference = merchant_price - cuisine_avg_price
    percentage = (difference / cuisine_avg_price) * 100

    context = json.dumps({
        "merchant_name": merchant_name,
        "merchant_price": round(merchant_price, 2),
        "cuisine_avg_price": round(cuisine_avg_price, 2),
        "price_difference": round(difference, 2),
        "percentage_difference": f"{round(percentage, 2)}%"
    })
    message_non_graph[1].content.append({"type": "text", "text": context})
    description = asyncio.run(run(message_non_graph))
    context_dict = json.loads(context) 
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
    return asyncio.run(run(bottleneck_opportunity_message ))


def initial_analysis():
    
    target_date = datetime(2023, 12, 1)

    images_mapping = {'img2.png':['hourly_order', 'collection.find_one({"order_hour": 16}, {"order_count": 1, "_id": 0})'], 'img3.png': ['multi_day_hourly','collection.find_one({"order_day": "Sunday", "order_hour": 16},{"_id": 0, "order_count": 1})'], 'img5.png': ['food_breakdown', 'list(collection.find({"order_month": target_date},{"_id": 0, "item_name":1, "monthly_quantity": 2}))'], 'imj_4.png': ['monthly_income', 'collection.find_one({"order_month": target_date},{"_id": 0, "order_value": 1} )'], 'monthly_customers.png':['customer_growth','collection.find_one({"order_month": target_date},{"_id": 0, "New": 1,"Recurring":2,"New_change_%":3,"Recurring_Change_%":4})']}
    non_graph_collections = [i for i in db.list_collection_names() if i not in [j[0] for j in images_mapping.values()] + ['fs.chunks', 'fs.files']]
    non_graph_container = [get_monthly_income(db['monthly_summary'], target_date), get_ranking(db['ranking'],merchant_id),get_transport_average(db['transport']),get_cuisine_price(db['monthly_cuisine_items'], merchant_id, db)]

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
            with open(file.filename, "wb") as f:
                f.write(file.read())
            graph_containers.append(GraphContainer(
                    title= title,
                    image_path= path,
                    current_data= current_data,
                    description= description
            ))
        except Exception as e:
            continue

    json_data = json.dumps([graph.model_dump() for graph in graph_containers], indent=2)
    json_data2 = json.dumps([text.model_dump() for text in non_graph_container], indent=2)

    with open("graph_text_data.json", 'w') as f:
        f.write(json_data)

    with open("text_data.json", 'w') as f:
        f.write(json_data2)

    with open("bottleneck_opportunity.json", "w") as w:
        suggestions = identify_bottleneck_opportunity()
        w.write(suggestions)


def normal_run(query):
    ORDINARY_PROMPT = f'''
🧠 Role  
You are a memory-enabled AI assistant designed to support a food merchant with over 20 years of experience in the industry. Your core responsibility is to help analyze business performance and operational efficiency using real data. You have access to both tools and memory, and you can query databases when needed.

🎯 Task  
When a question is asked, first identify whether it's related to business operations, performance metrics, or sales analytics. If it is, automatically query the relevant database or use tools to retrieve up-to-date insights. Then provide the clearest and most practical answer based on the results. Use memory when it adds helpful context or improves the accuracy of your response.

Information:
- Your user's merchant id = {merchant_id}
- If users ask for recommendation, you are highly suggested to browse real-time information with Internet tools.
- Always ensure the information provided to user is up-to-date, by using internet surfing, or querying database.
- Remember to save the conversation each time you had with user, and retrieve whenever you need.

📋 Format  
1. Understand the user's question and determine if it's business/sales-related.  
2. If yes, query the database to retrieve the necessary data before answering.  
3. Present a clear and business-friendly answer in 2–4 sentences.  
4. Optionally offer a helpful suggestion or ask if the merchant wants a deeper breakdown.

🛠️ Notes  
- Prioritize real-time data over assumptions when answering performance or analytics questions.  
- Use memory only to enrich context or compare past performance.  
- Avoid technical jargon—speak clearly and practically.  
- Always aim to help the merchant act, decide, or understand quickly.
- Leverage between efficiency and quality of answers, be smart while choosing tools to save time.
'''
    message= [
                SystemMessage(content=ORDINARY_PROMPT),
                HumanMessage(
                    content=[
                        {"type": "text", "text":  query},
                        
                    ]
                )
            ]
    asyncio.run(run(message))