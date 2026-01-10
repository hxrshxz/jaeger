import os
import re
import subprocess

def main():
    if not os.path.exists("FIX_PLAN.md"):
        print("No plan to execute.")
        return

    with open("FIX_PLAN.md", "r") as f:
        plan = f.read()

    # Simple regex to extract file paths and instructions
    # Format expected: #### [FILE_PATH] followed by instructions
    sections = re.split(r'####\s+', plan)[1:]
    
    for section in sections:
        lines = section.strip().split('\n')
        if not lines:
            continue
            
        # Clean up file path (strip backticks, brackets, spaces)
        file_path = lines[0].strip('`[] ')
        instructions = '\n'.join(lines[1:])
        
        if not file_path or not os.path.exists(file_path):
            print(f"File not found or invalid: '{file_path}'")
            continue

        print(f"Laborer fixing: {file_path}")
        
        with open(file_path, "r") as f:
            original_content = f.read()

        prompt = f"""
        # ROLE: Laborer Agent
        # TASK: Execute the Architect's Blueprint exactly.
        # OUTPUT: Return ONLY the new content of the file. DO NOT include any explanations, markdown markers, or chatter.
        
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

        try:
            print(f"Gemini CLI is fixing: {file_path}")
            result = subprocess.run(["gemini", "-o", "text", prompt], capture_output=True, text=True)
            new_content = result.stdout.strip()
        except Exception as e:
            print(f"Error running gemini CLI for {file_path}: {e}")
            continue
        
        # SAFETY CHECK: If the output is dangerously short or chatty, skip it
        if "Sure" in new_content[:50] or "I will" in new_content[:50] or "Certainly" in new_content[:50]:
             print(f"⚠️ Warning: Gemini output for {file_path} contains conversational markers. Skipping.")
             continue
        if len(new_content) < len(original_content) * 0.2 and len(original_content) > 100:
             print(f"⚠️ Warning: Gemini output for {file_path} is too short compared to original. Skipping.")
             continue

        # Strip potential markdown code blocks
        if new_content.startswith("```"):
            new_content = re.sub(r'^```[a-z]*\n', '', new_content, flags=re.MULTILINE)
            new_content = re.sub(r'\n```$', '', new_content, flags=re.MULTILINE)

        with open(file_path, "w") as f:
            f.write(new_content)
        
        print(f"Successfully updated {file_path}")

if __name__ == "__main__":
    main()
