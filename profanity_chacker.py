import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

async_openai = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def check_for_profanity(content: str) -> bool:
    response = await async_openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that checks text for obscene language."
                                          " Respond with Yes or No."},
            {"role": "user", "content": f"Check the following text for obscene language: '{content}'"}
        ]
    )
    result = response.choices[0].message.content.strip()
    return result.lower() == "yes"
