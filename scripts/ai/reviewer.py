import os
import subprocess
import google.generativeai as genai

def main():
    # Get staged changes
    try:
        diff = subprocess.check_output(["git", "diff", "--staged"]).decode("utf-8")
    except subprocess.CalledProcessError:
        print("Error getting git diff.")
        return

    if not diff:
        print("No staged changes to review.")
        return

    prompt = f"""
    # ROLE: Senior Architect / Mentor
    # TASK: Validate code reviews and generate a Technical Blueprint for the Laborer.

    ## INPUTS
    - PR Context: {pr_title}
    - Review Comments: {"/n".join(comments)}

    ## OBJECTIVE
    1. VALIDATE: Reject hallucinations or suggestions that break project patterns.
    2. BLUEPRINT: For accepted suggestions, provide exact, step-by-step instructions.

    ## OUTPUT FORMAT (MANDATORY)
    #### [FILE_PATH]
    - Action: [REPLACE/ADD/DELETE]
    - Logic: "Detailed code snippet or instruction"
    - Verification: "Instruction on how to test this change"
    """

    print("Gemini CLI is architecting the plan...")
    try:
        result = subprocess.run(["gemini", prompt], capture_output=True, text=True)
        blueprint = result.stdout
    except Exception as e:
        print(f"Error running gemini CLI: {e}")
        return

    with open("FIX_PLAN.md", "w") as f:
        f.write(blueprint)
    
    print("FIX_PLAN.md generated.")

if __name__ == "__main__":
    main()
