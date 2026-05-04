import os

from openai import OpenAI


client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

for model in client.models.list().data:
    print(model.id)
