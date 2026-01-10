import os
import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pr", type=int, required=True)
    parser.add_argument("--repo", type=str, required=True)
    args = parser.parse_args()

    pr_title = "Local Development"
    comments = []

    # Get remote reviews from GitHub if PR is provided
    if args.pr != 0:
        try:
            from github import Github
            gh = Github(os.environ["GITHUB_TOKEN"])
            repo = gh.get_repo(args.repo)
            pr = repo.get_pull(args.pr)
            pr_title = pr.title
            
            reviews = pr.get_reviews()
            for review in reviews:
                if review.body:
                     comments.append(f"GitHub Review by {review.user.login}: {review.body}")
        except Exception as e:
            print(f"Warning: Could not fetch GitHub reviews: {e}")

    # Try local review first
    if os.path.exists("local_review.md"):
        with open("local_review.md", "r") as f:
            comments.append(f"Local AI Review: {f.read()}")
        
    if not comments:
        print("No comments to process.")
        return

    prompt = f"""
    # ROLE: Senior Architect / Mentor
    # TASK: Validate code reviews and generate a Technical Blueprint for the Laborer.

    ## INPUTS
    - PR Context: {pr_title}
    - Review Comments: {"\n".join(comments)}

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
        # Using gemini CLI with -o text for pure output
        result = subprocess.run(["gemini", "-o", "text", prompt], capture_output=True, text=True)
        blueprint = result.stdout
    except Exception as e:
        print(f"Error running gemini CLI: {e}")
        return

    with open("FIX_PLAN.md", "w") as f:
        f.write(blueprint)
    
    print("FIX_PLAN.md generated.")

if __name__ == "__main__":
    main()