import os
import subprocess

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
    # ROLE: Strict Minimalist Reviewer
    # GOAL: Identify critical bugs or project violations with MINIMAL footprint.

    ## PRINCIPLES:
    - Only flag issues that are BUGS, SECURITY RISKS, or BLATANT project style violations.
    - Do NOT suggest refactors.
    - Do NOT suggest formatting changes.
    - Do NOT suggest adding comments/docs unless the surrounding code already has them.
    - If the code is functional and follows existing patterns, output 'LGTM'.

    ## STAGED DIFF:
    {diff}
    
    Output a concise list of critical concerns or 'LGTM'.
    """

    print("Gemini CLI is reviewing your local changes (Minimalist Mode)...")
    try:
        # Using gemini CLI with -o text for pure output
        result = subprocess.run(["gemini", "-o", "text", prompt], capture_output=True, text=True)
        review_output = result.stdout
    except Exception as e:
        print(f"Error running gemini CLI: {e}")
        return
    
    with open("local_review.md", "w") as f:
        f.write(review_output)
    
    print("Local review generated in local_review.md")

if __name__ == "__main__":
    main()
