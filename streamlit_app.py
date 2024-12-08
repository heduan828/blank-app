__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import sqlite3
import platform
import streamlit as st
from openai import OpenAI
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from IPython.display import display
import os

os.system("sudo apt-get update && sudo apt-get install -y sqlite3")

#import keys
my_openaikey = st.secrets["my_openaikey"]
my_serperkey = st.secrets["my_serperkey"]

os.environ['OPENAI_API_KEY'] = my_openaikey
os.environ["SERPER_API_KEY"] = my_serperkey

#Agents definitions
planner = Agent(
    role="Car Searcher",
    goal="Identify a suitable car to purchase based on user preferences",
			tools=[SerperDevTool(), ScrapeWebsiteTool()],
    backstory="You excel at finding the perfect new car for sale in the USA for the user "
              "to purchase that fits the user's budget and bodystyle preferences. "
              "Your work is the basis for "
              "the Content Writer to write an article on this car.",
    allow_delegation=False,
	verbose=True
)
writer = Agent(
    role="Content Writer",
    goal="Write factually accurate and convincing "
         "article about the vehicle",
			tools=[],
    backstory="You're working on a writing "
              "an article about the car the Car Searcher has chosen. "
              "You base your writing on the work of "
              "the Car Searcher, who provides details "
              "of the make and model, key features, price and year of the vehicle. "
              "You write an article on the car, emphasizing "
              "the vehicle's key features and why it is a good fit "
              "for the user's requirements. ",
    allow_delegation=False,
    verbose=True
)
editor = Agent(
    role="Editor",
    goal="Edit a given article about vehicle to align with "
         "user requirements. ",
			tools=[],
    backstory="You are an editor who receives an article about a vehicle "
              "from the Content Writer. "
              "Your goal is to review the article "
              "to ensure that it aligns with the user's requirments,"
              "provides balanced viewpoints "
              "when providing opinions or assertions, "
              "and also avoids major controversial topics "
              "or opinions when possible.",
    allow_delegation=False,
    verbose=True
)
#Task definitions
plan = Task(
    description=(
        "1. Find three new car models with {bodystyle} bodystyle "
            "that costs less than {budget}.\n"
        "2. Do not find car models that are priced more than 15 percent below the {budget}.\n"
        "3. Base your search on at most 3 websites to ensure fast response "
            "and do not read from edmunds.com and cars.com.\n"
        "4. Try to be as fast as possible and do not take more than 25 seconds in formulating your answer.\n"
        "5. Move on to another website if a website is not responding or providing any information for more than 5 seconds.\n"
    ),
    expected_output="The year, make, model, price and key features "
        "of each chosen vehicle "
        " and URL link to a website with details of the vehicle. ",
    agent=planner,
)
write = Task(
    description=(
        "1. Use the details of the three car models provided by the planner "
            "to write an article including all three cars.\n"
        "2. Highlight the key features of each particular vehicle "
            "and why it is a good fit for the user's {priorities}.\n"
        "3. At the end of the article provide a recommendation of which "
            "of the three vehicles is the best match for the user.\n"
		"4. Sections/Subtitles are properly named "
            "in an engaging manner.\n"
        "5. Ensure the post is structured with an "
            "engaging introduction, insightful body, "
            "and a summarizing conclusion.\n"
        "6. Try to be as quick as possible in formulating your answer.\n"
    ),
    expected_output="A well-written article, "
        "about the three vehicles provided by the planner, "
        "each section should have 2 or 3 paragraphs. "
        "At the top of the article, provide the year, make, model, price, sale location "
        "of the three vehicles and URL links to the vehicle listings.",
    agent=writer,
)
edit = Task(
    description=("Proofread the article written by the writer for "
                 "grammatical errors and "
                 "alignment with the user's {priorities} and is well formatted in markdown."),
    expected_output="A well-written article, "
                    "ready for publication formatted in markdown, "
                    "each section should have 2 or 3 paragraphs.",
    agent=editor
)
#Crew Kickoff
crew = Crew(
    agents=[planner, writer, editor],
    tasks=[plan, write, edit],
    verbose=True
)
def generate_article(user_input):
  """Generates the article based on user input."""
  result = crew.kickoff(inputs=user_input)
  return result.raw

# Streamlit app

st.title("Petrolhead Podcasts Car Recommender")

image_url = "https://yt3.googleusercontent.com/bfm8RFQfV-9xbSZ4SAjwthXCa03fH0UALMDRQWjKovcW9mVmQYywij-NuI21YHIDyF2EzFCG0HU=w1060-fcrop64=1,00005a57ffffa5a8-k-c0xffffffff-no-nd-rj"  # Replace with the actual URL
st.image(image_url, caption="", use_container_width=True)

# Embed the video
video_url = "https://youtu.be/3exJ9hD5ERQ?si=eat0UMiA_4_CeVCs"
st.video(video_url)

# User input
user_input = {
    'budget': st.number_input("Budget", min_value=20000, max_value=100000, value=30000, step=1000),
    'bodystyle': st.selectbox("Bodystyle", ["SUV", "Sedan", "Truck"]),
    'priorities': st.multiselect("Priorities", ["Quality", "Affordability", "Fun to drive", "Classiness", "Sportiness", "Practicality", "Youthfulness"],
                                 default=["Quality", "Affordability", "Fun to drive", "Classiness", "Sportiness", "Practicality", "Youthfulness"],),
}
# Join priorities to a string
user_input['priorities'] = ', '.join(user_input['priorities'])

# Generate and display the article
if st.button("Generate Recommendation"):
    try:
        article = generate_article(user_input)
        st.markdown(article)
    except Exception as e:
        st.error(f"An error occurred: {e}")

