# Import necessary libraries
import streamlit as st
import datetime
from newsapi import NewsApiClient
from langchain.chat_models import ChatOpenAI

def linkcraft():
    # Set up the Streamlit app
    col1, col2, col3 = st.columns(3)
    col2.title("LinkCraft")
    st.markdown(
        "<h1 style='text-align: center; color: black; font-size: 38px;'>AI-Powered LinkedIn Content Composer</h1>",
        unsafe_allow_html=True,
    )
    st.write(
        """
        Welcome to 🌐 LinkCraft, your premier AI-driven tool for crafting LinkedIn content. 
        Designed for professionals and thought leaders, LinkCraft transforms trending news headlines into 
        insightful LinkedIn posts. 📊 Select an industry, choose a headline, and receive a post tailored for the LinkedIn audience, 
        echoing the styles of industry influencers. 🚀
        """
    )
    
    # Initialize API clients
    try:
        NEWS_API_KEY = st.secrets["NEWS_API"]["api_key"]
        OPENAI_API_KEY = st.secrets["OPENAI_API"]["chatgpt_api"]
        newsapi = NewsApiClient(api_key=NEWS_API_KEY)
        llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=OPENAI_API_KEY, temperature=0.7)
    except KeyError as e:
        st.error(f"Missing API key: {e}")
        return

    # Industry selection
    industries = [
        'automobile', 'e-vehicle', 'renewable energy', 'technology',
        'environment', 'global affairs', 'healthcare', 'finance',
        'entertainment', 'sports', 'real estate', 'education',
        'agriculture', 'fashion', 'travel', 'food & beverages',
    ]
    col1, col2, col3 = st.columns([0.5, 1.5, 0.5])
    col2.subheader('Select a News Segment')
    selected_industry = col2.selectbox('', industries)

    # Date range selection
    st.subheader('Select a Date Range for the Top 10 Trending News Headlines')
    today = datetime.date.today()
    col1, col2 = st.columns(2)
    start_date = col1.date_input('Start Date', min_value=today - datetime.timedelta(days=7), value=today - datetime.timedelta(days=7))
    end_date = col2.date_input('End Date', min_value=start_date)
    if start_date > end_date:
        st.error("Start date must be earlier than or equal to the end date.")
        return

    # Initialize session states
    if 'selected_news' not in st.session_state:
        st.session_state.selected_news = None
    if 'news_headlines' not in st.session_state:
        st.session_state.news_headlines = []

    # Fetch headlines
    col1, col2, col3 = st.columns(3)
    if col2.button("Fetch Headlines"):
        try:
            news_articles = newsapi.get_everything(
                q=selected_industry,
                from_param=start_date,
                to=end_date,
                sort_by='relevancy',
                language='en',
                page_size=10
            )
            st.session_state.news_headlines = [article['title'] for article in news_articles['articles']]
            if not st.session_state.news_headlines:
                st.warning("No headlines found for the selected industry and date range.")
        except Exception as e:
            st.error(f"Error fetching headlines: {e}")

    # Display headlines
    if st.session_state.news_headlines:
        st.session_state.selected_news = st.radio("Select a news headline:", st.session_state.news_headlines)

    # Generate LinkedIn post
    if st.session_state.selected_news and st.button("Generate LinkedIn Post"):
        try:
            linkedin_prompt = f"""
            Craft an engaging LinkedIn post within 1000 words based on the provided news headline:
            "{st.session_state.selected_news}". The post should target {selected_industry} professionals. 
            Use statistical data, bullet points, and a captivating hook. Incorporate emojis where appropriate.
            """
            response = llm.predict(linkedin_prompt)
            st.text_area("Generated LinkedIn Post:", response, height=400)
        except Exception as e:
            st.error(f"Error generating LinkedIn post: {e}")

# Run the app
if __name__ == "__main__":
    linkcraft()
