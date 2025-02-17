# AI-Powered SEO Content Rewriter

This project provides an AI-powered SEO content rewriting tool that extracts knowledge from a given webpage and rewrites user-provided content by optimizing it for SEO, improving readability, and maintaining factual accuracy.

## Key Features
- **Web Crawling**: The tool crawls a webpage and extracts its content using `crawl4ai`.
- **SEO Content Rewriting**: The extracted website content is used to optimize and rewrite input content for SEO improvements, keyword placement, and readability.
- **Fast Execution**: The tool leverages `FAISS` for fast semantic content retrieval and `SentenceTransformer` for embedding and encoding text.
- **Generative AI**: `Ollama (DeepSeek)` is used to generate the SEO-optimized content based on the extracted website knowledge.

## Tech Stack
- **Python**: Backend programming language
- **Gradio**: User interface for easy interaction
- **Ollama (DeepSeek)**: LLM for content generation
- **FAISS**: Vector search library for efficient content retrieval
- **SentenceTransformers**: Embedding model for text-to-vector conversion
- **crawl4ai**: Web crawling tool to extract content from webpages
- **asyncio**: For asynchronous execution of web crawling and content rewriting tasks

## Requirements
To run this project, ensure the following libraries are installed:

- `gradio`
- `asyncio`
- `ollama`
- `faiss-cpu` (or `faiss-gpu` if you have a GPU setup)
- `numpy`
- `sentence-transformers`
- `crawl4ai`

You can install the required packages using `pip`:

```bash
pip install gradio ollama faiss-cpu numpy sentence-transformers crawl4ai
