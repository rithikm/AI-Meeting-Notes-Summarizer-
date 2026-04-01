#Refrences
#Get_Mime_Type Function: https://www.geeksforgeeks.org/python/find-the-mime-type-of-a-file-in-python/



#Imported the required libraries that will be used to handle the Flask backend of the application
import os 
from crewai import Agent, Task, Process, LLM, Crew
from dotenv import load_dotenv
import google.generativeai as genai


load_dotenv()
#Aquring the Google API Key from the enviorment file created through Google AI Studio
api_key = os.getenv("GOOGLE_API_KEY")

#Intializing the Crew AI agents to utilize Gemini 2.5 Pro as the LLM 
llm = LLM(
    api_key=api_key,
    model="gemini/gemini-2.5-pro",
    temperature=0.2
)

# ------ Crew AI Agents ---------
transcriber_agent = Agent(
    role = "AI Meeting Transcriber",
    goal = "Convert meeting audio into accurate text transcripts.",
    backstory = "An expert in speech-to-text conversion using LLMs.",
    verbose=True,
    llm=llm
)

analyzer_agent = Agent(
    role = "AI Meeting Analyzer",
    goal = "Summarize transcripts and extract key decisions and action items",
    backstory = "A detail-oriented analyst specializing in structured meeting notes.",
    verbose = True,
    llm=llm
)

# ------ Agent Tasks ---------
transcriber_task = Task(
    description=( 
        "You are provided with a raw transcript extracted from an audio file: {transcript_text}. "
        "Your job is NOT to transcribe audio, but to clean, organize, and refine the transcript. "
        "You MUST preserve timestamps if they exist. If timestamps are missing or incomplete, "
        "insert timestamps every 10 seconds in the format [MM:SS]. "
        "Ensure speaker turns are separated, filler noise is minimized, and the transcript is easy to read."
        ),
    expected_output=(
        "Return the transcription as clean text with speaker labels and timestamps."
    ),
    agent=transcriber_agent
)

analyzer_task = Task(
    description=(
        "Given the meeting transcript : {transcript_text}, analyze it carefully."
        "Extract a concise meeting summary, key decisions, and action items."
    ),
    expected_output=(
        "Return ONLY valid JSON using double quotes. Do not use single quotes. "
        "Format:\n"
        "{\n"
        '  "summary": "...",\n'
        '  "decisions": ["...", "..."],\n'
        '  "action_items": ["...", "..."]\n'
        "}"
    ),
    agent=analyzer_agent
)

#Created a crew which takes in the agents created, tasks, and preforms them in a sequential order.
meeting_crew = Crew(
    agents=[transcriber_agent,analyzer_agent],
    tasks=[transcriber_task,analyzer_task],
    process=Process.sequential
)

def extract_Text(audio_path):
    """
    The extract_Text function transcribes an audio file using Gemini 2.5 Pro and returns the structure
    expected by the CrewAI pipeline.
    """

    # Acquring the Gemini API Key to have Gemini 2.5 Pro preform transcription.
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    # Loading in the audio file to be processed by Gemini 2.5 Pro for transcription 
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()

    # Prepare audio for Gemini 2.5 pro to be transcribed.
    audio_part = {
        "mime_type": get_mime_type(audio_path),
        "data": audio_bytes
    }

    # Calling Gemini 2.5 pro LLM model for audio transcription. 
    model = genai.GenerativeModel("gemini-2.5-pro")

    response = model.generate_content([
        "Transcribe the FULL audio from start to finish. Do not skip any sections. "
        "Follow this EXACT formatting template for every spoken line:\n\n"
        "[MM:SS] Speaker Name: spoken text...\n\n"
        "Rules:\n"
        "- The timestamp MUST ALWAYS appear at the very beginning of each line.\n"
        "- NEVER place timestamps in the middle or end of sentences.\n"
        "- EVERY speaker turn must begin with a timestamp.\n"
        "- Estimate timestamps if exact timing metadata is unavailable.\n"
        "- Combine long utterances into a single line rather than multiple timestamps inside the text.",
        audio_part
    ])

    transcript = response.text

    # MUST return these keys because they match {transcript_text} in the Tasks
    return {
        "audio_path": audio_path,
        "transcript_text": transcript
    }

#Created the get_mime_type function which verfies the type of audio file by extracting the extension. 
def get_mime_type(path):
    ext = path.split(".")[-1].lower()
    if ext == "mp3":
        return "audio/mpeg"
    if ext == "wav":
        return "audio/wav"
    if ext == "m4a":
        return "audio/mp4"
    return "audio/mpeg"   


#Created a function called process_audio which takes in the audio path as a parameter. 
#Inside the function the extract_Tect function is being called to handle transcription of the audio file and stored by a text variable
#After the transcription is complete it is taken in as a form of input as the text variable then the Crew AI agents are called to preform their assigned tasks 
#Then the fucntion returns transcription output and analysis output which will be sent to the Frontend to be displayed to the user on the webpage of the application.

def process_audio(audio_path) :

    text=extract_Text(audio_path)

    result = meeting_crew.kickoff(inputs=text)

    transcription_output = result.tasks_output[0].raw

    analysis_output = result.tasks_output[1].raw

    return {
        "transcript": transcription_output,
        "analysis": analysis_output
    }






