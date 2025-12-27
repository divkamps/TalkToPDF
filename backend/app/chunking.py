import tiktoken

# Use a tokenizer compatible with modern LLMs
tokenizer = tiktoken.get_encoding("cl100k_base")


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 100
):
    tokens = tokenizer.encode(text)

    chunks = []
    start = 0

    while start < len(tokens):
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        chunk_text = tokenizer.decode(chunk_tokens)
        chunks.append(chunk_text)

        start += chunk_size - overlap

    return chunks
