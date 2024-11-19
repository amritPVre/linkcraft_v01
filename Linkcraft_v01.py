import streamlit as st
import datetime
from newsapi import NewsApiClient
from langchain.chat_models import ChatOpenAI


def linkcraft():
    #st.title("LinkCraft - AI-Powered LinkedIn & Slide Content Generator")
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
        insightful LinkedIn posts and now also creates slides! 📊 Select an industry, choose a headline, 
        and receive both a LinkedIn post and slides tailored to the LinkedIn audience. 🚀
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

    # Ensure session state variables exist
    if "news_headlines" not in st.session_state:
        st.session_state.news_headlines = []
    if "selected_news" not in st.session_state:
        st.session_state.selected_news = None
    if "generated_post" not in st.session_state:
        st.session_state.generated_post = ""
    if "slide_content" not in st.session_state:
        st.session_state.slide_content = []

    # Industry selection
    industries = [
        'automobile', 'e-vehicle', 'renewable energy', 'technology',
        'environment', 'global affairs', 'healthcare', 'finance',
        'entertainment', 'sports', 'real estate', 'education',
        'agriculture', 'fashion', 'travel', 'food & beverages',
    ]
    selected_industry = st.selectbox('Select a News Segment:', industries)
    
    # Date range selection
    today = datetime.date.today()
    start_date = st.date_input('Start Date', min_value=today - datetime.timedelta(days=7), value=today - datetime.timedelta(days=7))
    end_date = st.date_input('End Date', min_value=start_date)
    if start_date > end_date:
        st.error("Start date must be earlier than or equal to the end date.")
        return

    # Fetch headlines
    if st.button("Fetch Headlines"):
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
        except Exception as e:
            st.error(f"Error fetching headlines: {e}")

    # Display headlines
    if st.session_state.news_headlines:
        st.session_state.selected_news = st.radio("Select a news headline:", st.session_state.news_headlines)

    # Generate LinkedIn post
    if st.session_state.selected_news and st.button("Generate LinkedIn Post"):
        try:
            linkedin_prompt = f"""
            Create a professional LinkedIn post based on the headline: "{st.session_state.selected_news}".
            Include insights, trends, and industry-specific points in an engaging style.
            """
            response = llm.predict(linkedin_prompt)
            st.session_state.generated_post = response
        except Exception as e:
            st.error(f"Error generating LinkedIn post: {e}")

    # Display the generated post
    if st.session_state.generated_post:
        st.text_area("Generated LinkedIn Post:", st.session_state.generated_post, height=400)

    # Generate slide content and image prompts
    if st.session_state.generated_post and st.button("Generate Slide Content and Image Prompts"):
        try:
            slide_prompt = f"""
            Break the following LinkedIn post into structured slides. Each slide should include:
            - Title
            - Bullet points summarizing the content
            - A descriptive image prompt for generating a suitable image
            Ensure the format is consistent and clear. Here's the LinkedIn post:
            {st.session_state.generated_post}
            """
            slide_response = llm.predict(slide_prompt)

            # Parse slide content
            slides = []
            for slide in slide_response.split("\n\n"):
                if "Image Prompt:" in slide:
                    title_and_content, image_prompt = slide.split("Image Prompt:")
                    title, *points = title_and_content.strip().split("\n")
                    slides.append({
                        "title": title.strip(),
                        "points": [point.strip() for point in points if point.strip()],
                        "image_prompt": image_prompt.strip()
                    })
            st.session_state.slide_content = slides
        except Exception as e:
            st.error(f"Error generating slide content and prompts: {e}")

    # Display slides and prompts
    if st.session_state.slide_content:
        for i, slide in enumerate(st.session_state.slide_content, start=1):
            st.subheader(f"Slide {i}: {slide['title']}")
            for point in slide["points"]:
                st.write(f"- {point}")
            st.markdown(f"**Image Prompt:** {slide['image_prompt']}")


# Run the app
if __name__ == "__main__":
    linkcraft()
