import os
import re
import subprocess

def make_whitespace_insensitive(text):
    # Escape special regex characters
    text = re.escape(text)
    # Replace escaped spaces/tabs with a matcher for any amount of horizontal whitespace
    # we use \s+ for actual newlines or spaces to be safe
    # But often we just want to ignore indentation differences
    # Let's replace ' ' with '[ \t]*' and keep newlines fixed for precision
    text = text.replace(r'\ ', r'[ \t]*')
    return text

def main():
    if not os.path.exists("FIX_PLAN.md"):
        print("No plan to execute.")
        return

    with open("FIX_PLAN.md", "r") as f:
        plan = f.read()

    # Split by file
    file_sections = re.split(r'####\s+', plan)[1:]
    
    for section in file_sections:
        lines = section.split('\n')
        if not lines:
            continue
            
        file_path = lines[0].strip('`[] ')
        
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue

        print(f"Laborer applying minimal fixes for: {file_path}")
        
        with open(file_path, "r") as f:
            content = f.read()

        # Extract Search/Replace blocks
        # Pattern: <<<< SEARCH ... ==== ... >>>> REPLACE
        blocks = re.findall(r'<<<< SEARCH\n(.*?)\n====\n(.*?)\n>>>> REPLACE', section, re.DOTALL)
        
        if not blocks:
            print(f"No valid Search/Replace blocks found for {file_path}")
            continue

        for search, replace in blocks:
            # Try exact match first
            if search in content:
                print(f"  Applying Search/Replace block (exact)...")
                content = content.replace(search, replace)
                continue
            
            # Try whitespace-insensitive match (per line)
            search_lines = search.split('\n')
            content_lines = content.split('\n')
            
            found = False
            for i in range(len(content_lines) - len(search_lines) + 1):
                match = True
                for j in range(len(search_lines)):
                    if search_lines[j].strip() != content_lines[i+j].strip():
                        match = False
                        break
                if match:
                    print(f"  Applying Search/Replace block (whitespace-insensitive)...")
                    # Replace the lines while preserving content around them
                    content_lines[i:i+len(search_lines)] = replace.split('\n')
                    content = '\n'.join(content_lines)
                    found = True
                    break
            
            if not found:
                print(f"  ⚠️ Could not find search block in {file_path}. Skipping.")
                print(f"  Looking for: {search[:100]}...")

        with open(file_path, "w") as f:
            f.write(content)
        
        print(f"Successfully updated {file_path}")

if __name__ == "__main__":
    main()
