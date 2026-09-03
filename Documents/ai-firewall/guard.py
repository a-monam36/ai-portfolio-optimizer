from groq import Groq
from dotenv import load_dotenv

load_dotenv()


client = Groq()
completion = client.chat.completions.create(
    model="llama-guard-3-8b",
    messages=[
        {
            "role": "user",
            "content": "Explain why fast inference is critical for reasoning models"
        }
    ]
)
print(completion.choices[0].message.content)





