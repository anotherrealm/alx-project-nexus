import base64
import json
import os
import sys
import requests
from pathlib import Path

def encode_mermaid_to_url(mermaid_code):
    """Encode Mermaid code to a URL-safe string."""
    # Convert to base64
    message_bytes = mermaid_code.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    
    # Make URL safe
    return base64_message.replace('+', '-').replace('/', '_')

def render_mermaid_to_png(mermaid_code, output_path):
    """Render Mermaid code to PNG using Mermaid Live Editor API."""
    # Prepare the request
    url = "https://mermaid.ink/img/"
    encoded = encode_mermaid_to_url(mermaid_code)
    
    try:
        # Make the request
        response = requests.get(f"{url}{encoded}")
        response.raise_for_status()
        
        # Save the image
        with open(output_path, 'wb') as f:
            f.write(response.content)
            
        print(f"Successfully saved diagram to {output_path}")
        return True
    except Exception as e:
        print(f"Error rendering diagram: {e}")
        return False

def main():
    # Create output directory if it doesn't exist
    output_dir = Path("docs/diagrams")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process each .mmd file
    for file_path in Path("docs/diagrams").glob("*.mmd"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                mermaid_code = f.read()
                
            output_path = file_path.with_suffix('.png')
            print(f"Rendering {file_path} to {output_path}...")
            
            if render_mermaid_to_png(mermaid_code, output_path):
                print(f"Successfully created {output_path}")
            else:
                print(f"Failed to render {file_path}")
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    main()
