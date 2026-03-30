from transformers import pipeline

# Use text-generation instead of summarization
generator = pipeline("text-generation", model="gpt2")

def summarize_text(text):
    text = text[:1000]

    prompt = f"Summarize this text:\n{text}"

    result = generator(prompt, max_length=200, num_return_sequences=1)

    return result[0]['generated_text']