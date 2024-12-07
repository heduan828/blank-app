import streamlit as st
import os

from langchain.chat_models import ChatOpenAI
my_openaikey = os.environ.get("OPENAI_API_KEY")
my_serperkey = os.environ.get("SERPER_API_KEY")
llm = ChatOpenAI(model='gpt-3.5') # Loading GPT-3.5

planner = Agent(
    role="Car Searcher",
    goal="Identify a suitable car to purchase based on user requirements",
    llm = llm
    tools=[
        SearchTools.search_internet,
        BrowserTools.scrape_and_summarize_kwebsite
    ],
    backstory="You excel at finding the perfect new car for sale in the USA for the user "
              "to purchase that fits the user's budget, bodystyle, priorities "
              "Your work is the basis for "
              "the Content Writer to write an article on this car.",
    allow_delegation=False,
	verbose=True
)
writer = Agent(
    role="Content Writer",
    goal="Write factually accurate and convincing "
         "article about the vehicle",
    llm = llm
    tools=[
        SearchTools.search_internet,
        BrowserTools.scrape_and_summarize_kwebsite
    ],
    backstory="You're working on a writing "
              "an article about the car the Car Searcher has chosen. "
              "You base your writing on the work of "
              "the Car Searcher, who provides details "
              "of the make and model, price and year of the vehicle. "
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
    llm = llm
    tools=[
        SearchTools.search_internet,
        BrowserTools.scrape_and_summarize_kwebsite
    ],
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
plan = Task(
    description=(
        "1. Find three new car models with {bodystyle} bodystyle "
            "that costs less than {budget}.\n"
        "2. Ensure the chosen car's features and characteristics "
            "matches the user's {priorities}.\n"
    ),
    expected_output="The year, make, model, price "
        "of each chosen vehicle and URL link to a website with details of the vehicle. ",
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
        "6. Proofread for grammatical errors and "
            "alignment with the brand's voice.\n"
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
                 "alignment with the user's {priorities}."),
    expected_output="A well-written article, "
                    "ready for publication formatted in markdown, "
                    "each section should have 2 or 3 paragraphs.",
    agent=editor
)
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
st.title("Car Recommendation App")

# Embed the video
video_url = "https://youtu.be/aChue7Fn35M?si=8-o2dVxw2zpkS4TJ"  # Replace with your URL
st.video(video_url)

# User input
user_input = {
    'budget': st.number_input("Budget", min_value=20000, max_value=100000, value=30000, step=1000),
    'bodystyle': st.selectbox("Bodystyle", ["SUV", "Sedan", "Truck", "Hatchback"]),
    'priorities': st.multiselect("Priorities", ["Quality", "Affordability", "Fun to drive", "Classiness", "Sportiness", "Practicality", "Youthfulness"],
                                 default=["Quality", "Affordability", "Fun to drive", "Classiness", "Sportiness", "Practicality", "Youthfulness"],),
}
# Join priorities to a string
user_input['priorities'] = ', '.join(user_input['priorities'])

# Generate and display the article
if st.button("Generate Article"):
    try:
        article = generate_article(user_input)
        st.markdown(article)
    except Exception as e:
        st.error(f"An error occurred: {e}")

