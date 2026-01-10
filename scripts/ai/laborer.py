import os
import re
import google.generativeai as genai

def main():
    if not os.path.exists("FIX_PLAN.md"):
        print("No plan to execute.")
        return

    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-pro')

    with open("FIX_PLAN.md", "r") as f:
        plan = f.read()

    # Simple regex to extract file paths and instructions
    # Format expected: #### [FILE_PATH] followed by instructions
    sections = re.split(r'####\s+', plan)[1:]
    
    for section in sections:
        lines = section.strip().split('\n')
        file_path = lines[0].strip('[] ')
        instructions = '\n'.join(lines[1:])
        
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue

        print(f"Laborer fixing: {file_path}")
        
        with open(file_path, "r") as f:
            original_content = f.read()

        prompt = f"""
        # ROLE: Laborer Agent
        # TASK: Execute the Architect's Blueprint exactly.
        
        ## BLUEPRINT INSTRUCTIONS:
        {instructions}
        
        ## TARGET FILE: {file_path}
        
        ## ORIGINAL CONTENT:
        {original_content}
        
        ## MANDATORY RULES:
        1. Follow instructions EXACTLY.
        2. Maintain existing indentation and style.
        3. Output ONLY the new file content. No markdown wrappers unless they are part of the code.
        """

        response = model.generate_content(prompt)
        new_content = response.text.strip()
        
        # Strip potential markdown code blocks if the model included them
        if new_content.startswith("```"):
            new_content = re.sub(r'^```[a-z]*\n', '', new_content)
            new_content = re.sub(r'\n```$', '', new_content)

        with open(file_path, "w") as f:
            f.write(new_content)
        
        print(f"Successfully updated {file_path}")

if __name__ == "__main__":
    main()
