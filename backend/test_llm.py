import os
import asyncio
import time
from app.ai.llm_client import create_llm_client

def load_env():
    with open(".env", "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                key, val = line.split("=", 1)
                os.environ[key] = val


async def main():
    load_env()
    provider = os.getenv("LLM_PROVIDER", "gemini")
    api_key = os.getenv("GEMINI_API_KEY", "")
    model = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
    
    print(f"1. Model loaded: {model}")
    masked_key = api_key[:4] + "*" * (len(api_key)-8) + api_key[-4:] if len(api_key) > 8 else "***"
    print(f"2. API Key: {masked_key}")
    print(f"3. Provider: {provider}")
    
    client = create_llm_client(
        provider=provider,
        api_key=api_key,
        model=model,
        max_tokens=100,
        temperature=0.2,
        timeout=30
    )
    
    system_prompt = "You are a test bot."
    messages = [{"role": "user", "content": "Hello Gemini, reply with 'I am contacted'"}]
    
    print("\n4. Exact Request:")
    print(f"   System: {system_prompt}")
    print(f"   Messages: {messages}")
    
    try:
        start = time.time()
        response = await client.generate(
            system=system_prompt,
            messages=messages
        )
        latency = time.time() - start
        
        print("\n5. Exact Response:")
        print(f"   Content: {response.content}")
        print(f"\n6. Token Usage: Input: {response.input_tokens}, Output: {response.output_tokens}")
        print(f"7. Latency: {latency:.4f} seconds")
        print("8. Cost: Not available via standard Gemini API without Vertex pricing info.")
    except Exception as e:
        print(f"\nFailed to contact Gemini:")
        print(f"Exception: {type(e).__name__}: {str(e)}")
        print("\nIf Gemini is not actually called, here is exactly why:")
        print("The API Key might be invalid, or the provider network might be unreachable.")

if __name__ == "__main__":
    asyncio.run(main())
