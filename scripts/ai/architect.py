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
    reviews = pr.get_reviews()
    comments = []
    for review in reviews:
        if review.body:
             comments.append(f"Review by {review.user.login}: {review.body}")
        # Note: In a real implementation, you'd also fetch path-specific comments
        
    if not comments:
        print("No comments found.")
        return

    prompt = f"""
    You are a Senior Architect. Analyze these PR review comments and create a FIX_PLAN.md.
    
    PR Context: {pr.title}
    Comments:
    {"/n".join(comments)}
    
    Format FIX_PLAN.md as:
    #### [FILE_PATH]
    - Action: REPLACE/ADD/DELETE
    - Logic: "Exact code change"
    - Verification: "command"
    """

    response = model.generate_content(prompt)
    
    with open("FIX_PLAN.md", "w") as f:
        f.write(response.text)
    
    print("Architect plan generated.")

if __name__ == "__main__":
    main()
