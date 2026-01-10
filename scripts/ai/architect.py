import os
import argparse
import google.generativeai as genai
from github import Github

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pr", type=int, required=True)
    parser.add_argument("--repo", type=str, required=True)
    args = parser.parse_args()

    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-pro')

    gh = Github(os.environ["GITHUB_TOKEN"])
    repo = gh.get_repo(args.repo)
    pr = repo.get_pull(args.pr)

    # Get reviews and comments
    comments = []
    
    # Try local review first
    if os.path.exists("local_review.md"):
        with open("local_review.md", "r") as f:
            comments.append(f"Local AI Review: {f.read()}")
    
    # Then get remote reviews from GitHub
    reviews = pr.get_reviews()
    for review in reviews:
        if review.body:
             comments.append(f"GitHub Review by {review.user.login}: {review.body}")
        
    if not comments:
        print("No comments to process.")
        return

    prompt = f"""
    # ROLE: Senior Architect / Mentor
    # TASK: Validate code reviews and generate a Technical Blueprint for the Laborer.

    ## INPUTS
    - PR Context: {pr.title}
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

    response = model.generate_content(prompt)
    with open("FIX_PLAN.md", "w") as f:
        f.write(response.text)
    
    print("FIX_PLAN.md generated.")

if __name__ == "__main__":
    main()
