import re
import openai
import streamlit as st
from metaphor_python import Metaphor

# OpenAI API key
openai.api_key = st.sidebar.text_input("API-KEY",type="password")

# Metaphor API key
metaphor = Metaphor(st.sidebar.text_input("METAPHOR-KEY",type="password"))

# image_url = 'https://assets.website-files.com/60afacf3bc3bf37dd0ad97c5/617ab3cd027d61b4591da3f9_job-search.jpg'

# st.markdown(f"<div style='display: flex; justify-content: center;'><img src='{image_url}' alt='Job Image' width='200' /></div>", unsafe_allow_html=True) 

# App title
st.markdown("<h2 style='text-align: center;'> Job Search Assistant 🔍 </h2><p style='text-align: center; font-size: 18px;'>Goodbye to Experience-Level Uncertainity with LLMs and Metaphor API 👋</p>", unsafe_allow_html=True)

st.write("") 
st.write("")

# User input for the question
USER_QUESTION = st.text_input("Enter the job title:")

st.markdown("Sample Search: 'Job Title' Listings (e.g., New Data Scientist Positions / Data Scientist Jobs)")

num_postings = st.sidebar.slider("Number of Job Postings:", 5, 20, 10, step=5)

# Button to perform the search
if st.button("Search"):
    if USER_QUESTION:
        SYSTEM_MESSAGE = "You are a helpful assistant that generates search queries based on user questions. Only generate one search query."

        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_MESSAGE},
                {"role": "user", "content": USER_QUESTION},
            ],
        )

        query = completion.choices[0].message.content
        search_response = metaphor.search(
            query, num_results=num_postings, use_autoprompt=True, start_published_date="2023-06-01"
        )

        SYSTEM_MESSAGE = "Just give me the Company Name, Job Title, Years of Experience Required for the job"

        contents_result = search_response.get_contents()

        pattern = r"(\d+\.?\d*) (years|year)"

        # Iterate through each job link in the search results of Metaphor API
        for i, link in enumerate(contents_result.contents):
            
            # Extracting the content of the link
            link_content = link.extract

            if "linkedin.com" in link.url:
            # Skip LinkedIn
                continue

            if "twitter.com" in link.url:
            # Skip twitter 
                continue

            # Use the link content as user input for OpenAI API
            messages = [
                {"role": "system", "content": SYSTEM_MESSAGE},
                {"role": "user", "content": link_content},
            ]

            # Make an API request for the current link
            completion = openai.ChatCompletion.create(
                model="gpt-4",
                messages=messages,
            )

            # Display the response for the link
            summary = completion.choices[0].message.content
            
            lines = summary.split('\n')
            
            # Extract and display URL, company, title, and years of experience
            url = link.url
            company = lines[0] if len(lines) > 0 else ""
            title = lines[1] if len(lines) > 1 else ""
            experience = lines[2] if len(lines) > 2 else ""

            experience = re.sub(pattern, r'**\1 \2**', experience)
            
            job_id = i + 1
            st.write(f"**Job ID: {job_id}**")
            st.write(f"{company}")
            st.write(f"Job Posting Link: {url}")
            st.write(f"{title}")
            st.write(f"{experience}")
            
            if i < num_postings - 1:
                st.markdown("---") # Seperating each job from one another.
