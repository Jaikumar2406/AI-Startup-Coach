from langchain.tools import tool
import time
import os
from groq import Groq
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from selenium import webdriver

load_dotenv()
groq = os.getenv('GROQ')

URLS = ["https://devfolio.co/hackathons",]
def get_page_text(url: str) -> str:
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    return ' '.join(
        tag.get_text(strip=True)
        for tag in soup.find_all(['p', 'li', 'h1', 'h2', 'h3'])
    )


@tool
def ask_question(question: str) -> str:
    """this tool provide all the information about the hackathons like how to apply what are theam of the hackathon how can apply.
    """
    combined_content = ""
    for url in URLS:
        print(f"Scraping: {url}")
        try:
            text = get_page_text(url)
            combined_content += text + "\n\n"
        except Exception as e:
            print(f"Error scraping {url}: {e}")

    context = combined_content[:12000]

    prompt = f"""You are an assistant that answers questions using only the following website content.
    provide information in this formare 
    hackathone name 
    eligiblity critria
    and also how to apply for the hackathon
Website Content:
{context}

Question:
{question}

Answer:"""

    client = Groq(api_key=groq)
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": "Answer only using the provided website content."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content
