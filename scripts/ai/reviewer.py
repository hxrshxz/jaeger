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
    You are a Senior Reviewer. Analyze the following staged git diff for GSoC/LFX quality standards.
    Identify any bugs, anti-patterns, or missing tests.
    
    DIFF:
    {diff}
    
    Output a list of critical concerns or 'LGTM' if it's perfect.
    """

    print("Gemini CLI is reviewing your local changes...")
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
