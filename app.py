import asyncio
import sqlite3
import ollama
import faiss
import numpy as np
import gradio as gr
from crawl4ai import AsyncWebCrawler
from sentence_transformers import SentenceTransformer
import re

# Load embedding model
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize FAISS index
dimension = 384
faiss_index = faiss.IndexFlatL2(dimension)

# Database path
DB_PATH = "vector_store.db"

# Create DB Table if not exists
def create_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS seo_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            original_text TEXT,
            rewritten_text TEXT
        )
    """)
    conn.commit()
    conn.close()

create_db()  # Ensure DB exists

# Crawl & store content
async def crawl_and_store(url):
    """Crawls a webpage, extracts content, embeds it, and stores it in FAISS."""
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        content = result.markdown.strip()

    if content:
        embedding = embed_model.encode([content], convert_to_numpy=True)
        faiss_index.add(embedding)  # Store in FAISS
        return content
    return None

# Retrieve website knowledge from FAISS
def retrieve_website_knowledge(query):
    """Retrieves the most relevant content from FAISS."""
    query_embedding = embed_model.encode([query], convert_to_numpy=True)
    if query_embedding is None or query_embedding.size == 0:
        return ""
   
    _, indices = faiss_index.search(query_embedding, 1)
    if indices[0][0] == -1:
        return ""
   
    return query

# Generate structured prompt
def generate_prompt(original_content, keyword, stored_content):
    """Generates a structured prompt."""
    return f"""
    Use the following website knowledge to rewrite the content with SEO improvements:
    - Optimize keyword placement for '{keyword}'.
    - Improve readability while maintaining factual accuracy.

    Website Knowledge:
    {stored_content}

    Strictly format the output as follows:
    Before: {original_content}
    After (LLM-generated): <Optimized Content>
    """

# Strip unnecessary sections like <think> from the content
def clean_rewritten_content(content):
    """Cleans and removes any system-generated sections like <think> from content."""
    content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL)  # Remove <think> tags
    return content.strip()

# Rewrite content using AI
async def rewrite_content(url, input_text):
    """Crawls, stores content, and rewrites user input using website knowledge."""
    stored_content = await crawl_and_store(url)
   
    if not stored_content:
        return "No relevant website knowledge found.", ""

    prompt = generate_prompt(input_text, input_text, stored_content)
    response = await asyncio.to_thread(ollama.chat, model="deepseek-r1", messages=[{"role": "user", "content": prompt}])

    optimized_content = response["message"]["content"].strip()

    # Clean the rewritten content to remove <think> sections
    cleaned_content = clean_rewritten_content(optimized_content)

    # Limit to 3 lines of rewritten content
    optimized_lines = cleaned_content.split("\n")
    optimized_summary = " ".join(optimized_lines[:3])

    # Store in SQLite Database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO seo_content (url, original_text, rewritten_text) VALUES (?, ?, ?)",
                   (url, input_text, optimized_summary))
    conn.commit()
    conn.close()

    return input_text, optimized_summary

# View stored content history
def view_faiss_vectors():
    """Fetches stored SEO content history from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT url, original_text, rewritten_text FROM seo_content ORDER BY id DESC")
    results = cursor.fetchall()
    conn.close()

    if not results:
        return "No stored content available."

    formatted_results = "\n📜 **Stored Content History:**\n\n"
    for url, original_text, rewritten_text in results:
        formatted_results += f"🔗 **URL:** {url}\n📝 **Original:** {original_text}\n✅ **Rewritten:** {rewritten_text}\n" + "-" * 80 + "\n"

    return formatted_results

# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("# 🚀 AI-Powered SEO Content Rewriter")

    # Inputs
    url_input = gr.Textbox(label="Enter the URL to extract knowledge from")
    text_input = gr.Textbox(label="Enter the content to rewrite")
   
    # Outputs
    original_output = gr.Textbox(label="Original Content")
    rewritten_output = gr.Textbox(label="Rewritten Content")
   
    # Buttons
    rewrite_button = gr.Button("Rewrite Content")
    history_button = gr.Button("View History")

    # History output
    history_output = gr.Textbox(label="Stored Content History", interactive=False)

    # Click Events
    rewrite_button.click(fn=rewrite_content, inputs=[url_input, text_input], outputs=[original_output, rewritten_output])
    history_button.click(fn=view_faiss_vectors, inputs=[], outputs=history_output)

# Launch Gradio UI
if __name__ == "__main__":
    demo.launch()
