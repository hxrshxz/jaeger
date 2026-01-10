import os
import re
import subprocess

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
            # Strip trailing/leading newlines that might cause mismatch
            search_stripped = search.strip('\n')
            
            # Look for exact match first
            if search in content:
                print(f"  Applying Search/Replace block...")
                content = content.replace(search, replace)
            elif search_stripped in content:
                 print(f"  Applying Search/Replace block (fuzzy newline)...")
                 content = content.replace(search_stripped, replace.strip('\n'))
            else:
                print(f"  ⚠️ Could not find search block in {file_path}. Skipping.")
                print(f"  Looking for: {search[:100]}...")

        with open(file_path, "w") as f:
            f.write(content)
        
        print(f"Successfully updated {file_path}")

if __name__ == "__main__":
    main()
