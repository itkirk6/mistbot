import os
import openai
from dotenv import load_dotenv


#   Load Environment Variables
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')


def respond(msg):
    completion = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "user", "content": msg}
      ]
    )

    response = completion.choices[0].message.content
    return response
        
        
def writeRap(msg):
    completion = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "user", "content": f"Make a short rap relating to this topic: {msg}"}
      ]
    )
    
    response = completion.choices[0].message.content
    
    if "\n" in response:
        return response
    else:
        return ""