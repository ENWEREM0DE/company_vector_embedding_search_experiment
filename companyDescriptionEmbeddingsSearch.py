import streamlit as st
import pandas as pd
from openai import OpenAI
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import os
from dotenv import load_dotenv

load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="Company Vector Search",
    page_icon="🏢",
    layout="wide",
)

# --- Initialize Session State ---
# This holds the search results across reruns
if 'search_results_df' not in st.session_state:
    st.session_state.search_results_df = None


# --- API Keys and Configuration ---
# WARNING: It is not recommended to hardcode secrets in your code.
# Use Streamlit's secrets management for better security in production.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = "marovi_db_prod"


# --- Initialize Clients ---
# Initialize OpenAI client
try:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
except Exception as e:
    st.error(f"Failed to initialize OpenAI client. Please check your API key. Error: {e}", icon="🔑")
    st.stop()

# Caching the database connection is a best practice for performance.
# It prevents reconnecting and re-authenticating on every interaction.
@st.cache_resource
def get_mongo_client():
    """Establishes and returns a connection to MongoDB."""
    try:
        client = MongoClient(MONGO_URI)
        # The ismaster command is cheap and does not require auth.
        client.admin.command('ismaster')
        return client
    except ConnectionFailure as e:
        st.error(f"MongoDB Connection Error: Could not connect to MongoDB. Please check your URI. Details: {e}", icon="🚨")
        st.stop()
    except Exception as e:
        st.error(f"An unexpected error occurred during MongoDB connection: {e}", icon="🚨")
        st.stop()

client = get_mongo_client()
db = client[DATABASE_NAME]
collection = db["companies_new_data_load"]


# --- Core Functions ---
# Caching the embedding function saves API calls and money if the exact
# same text is submitted twice. It will always re-run for new text.
@st.cache_data(show_spinner="Generating embedding for your description...")
def get_embedding(text, model="text-embedding-ada-002"):
    """Generates an embedding for the given text using OpenAI."""
    try:
        text = text.replace("\n", " ")
        response = openai_client.embeddings.create(input=[text], model=model)
        return response.data[0].embedding
    except Exception as e:
        st.error(f"OpenAI Error: Failed to generate embedding. {e}", icon="🤖")
        return None

def vector_search(query_vector, num_candidates, limit, industries_list):
    """Performs a vector search on the MongoDB collection with filters."""
    if query_vector is None:
        return None

    # MongoDB vector search stage with corrected filter syntax
    search_stage = {
        "index": "vector_index_for_company_search",
        "path": "company_description_embedding",
        "queryVector": query_vector,
        "numCandidates": num_candidates,
        "limit": limit,
        "filter": {
            "company_headquarters_country": "USA",
            **({"industry": {"$in": industries_list}} if industries_list else {})
        }
    }

    pipeline = [
        {"$vectorSearch": search_stage},
        {
            "$project": {
                "score": {"$meta": "vectorSearchScore"},
                "company_name": 1,
                "company_description": 1,
                "company_headquarters_country": 1,
                "industry": 1,
                "_id": 0,
            }
        }
    ]
    try:
        results = list(collection.aggregate(pipeline))
        return results
    except OperationFailure as e:
        st.error(f"MongoDB Operation Error: The search failed. Check index and filters. Details: {e}", icon="💾")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred during the search: {e}", icon="💥")
        return None


# --- Streamlit UI ---
st.title("🏢 MongoDB Vector Search for Companies")
st.markdown("Enter a description to find similar companies. All searches are filtered for companies in the **USA**.")

# --- Search Form ---
with st.form("search_form"):
    description_input = st.text_area(
        "Enter company description here:",
        height=150,
        placeholder="e.g., 'A cutting-edge artificial intelligence startup specializing in natural language processing...'"
    )
    
    st.markdown("### Filters")
    industry_input = st.text_input("Industries (optional, comma-separated)", placeholder="e.g., Artificial Intelligence, SaaS")

    st.markdown("### Search Parameters")
    col1_params, col2_params = st.columns(2)
    with col1_params:
        limit_input = st.number_input("Max results to fetch from database", min_value=1, max_value=10000, value=1000, step=100)
    with col2_params:
        candidates_input = st.number_input("Candidates to search", min_value=limit_input, max_value=20000, value=10000, step=100)

    submit_button = st.form_submit_button("Search for Similar Companies")

# --- Search Logic ---
if submit_button:
    # CORRECTED: Immediately clear old results to prevent showing stale data
    st.session_state.search_results_df = None 
    
    if not description_input:
        st.warning("Please enter a description to search for.", icon="⚠️")
    else:
        query_vector = get_embedding(description_input)
        if query_vector:
            industries_list = [ind.strip() for ind in industry_input.split(',') if ind.strip()] if industry_input else []

            with st.spinner(f"Searching for the top {limit_input} companies..."):
                search_results = vector_search(query_vector, candidates_input, limit_input, industries_list)
            
            if search_results:
                st.session_state.search_results_df = pd.DataFrame(search_results)
            else:
                # Set to empty df to indicate search was run but found nothing
                st.session_state.search_results_df = pd.DataFrame()
        # If get_embedding fails, state remains None, so nothing is displayed.

# --- Results Display ---
if st.session_state.search_results_df is not None:
    total_results = len(st.session_state.search_results_df)

    if total_results == 0:
        st.info("The search did not return any results from the database. Try broadening your criteria.", icon="🤷")
    else:
        st.markdown("---")
        st.subheader(f"Search Results: {total_results} Companies Found")
        
        # The full dataframe from the search is now displayed directly.
        df_to_display = st.session_state.search_results_df.copy()
        
        st.write(f"Displaying all **{total_results}** fetched companies.")
        st.dataframe(df_to_display, use_container_width=True)