import os
import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pr", type=int, required=True)
    parser.add_argument("--repo", type=str, required=True)
    args = parser.parse_args()

    pr_context = "Local Development"
    comments = []

    # Get remote reviews from GitHub if PR is provided
    if args.pr != 0:
        try:
            from github import Github
            gh = Github(os.environ["GITHUB_TOKEN"])
            repo = gh.get_repo(args.repo)
            pr = repo.get_pull(args.pr)
            pr_context = f"PR #{pr.number}: {pr.title}\nDescription: {pr.body}"
            
            reviews = pr.get_reviews()
            for review in reviews:
                if review.body:
                     comments.append(f"GitHub Review by {review.user.login}: {review.body}")
        except Exception as e:
            print(f"Warning: Could not fetch GitHub reviews: {e}")

    # Try local review first
    if os.path.exists("local_review.md"):
        with open("local_review.md", "r") as f:
            comments.append(f"AI Review Comments: {f.read()}")
        
    if not comments:
        print("No comments to process.")
        return

    prompt = f"""
    # ROLE: Senior Project Maintainer (Minimalist)
    # TASK: Solve the review comments using a Unified 3-Phase approach.

    ## CORE PRINCIPLES:
    - Minimal changes only — don’t modify unrelated code.
    - Reuse existing patterns and structure.
    - No new abstractions unless strictly required.
    - No comments unless the surrounding code already has them.
    - No formatting/style refactors.
    - Don’t add explanatory comments or TODOs.

    ## INPUTS:
    - Context: {pr_context}
    - Review Comments: {"\n".join(comments)}

    ---

    ## PHASE 1: Act as an Experienced Project Maintainer
    Draft the technical solution. Touch as little code as possible. Preserving existing style.

    ## PHASE 2: Act as a Strict Project Reviewer
    Critique Phase 1. Ensure it is MINIMAL and directly addresses the issue without noise.
    Identify any unnecessary changes.

    ## PHASE 3: Write the Machine Blueprint & PR Summary
    1. Output the technical blueprint in SEARCH/REPLACE format.
    2. Output a concise PR title and description.

    ## OUTPUT FORMAT (MANDATORY STRUCTURE)
    
    ### [ARCHITECT_REASONING]
    (Include Phase 1 and Phase 2 thinking here)

    ### [BLUEPRINT]
    #### [FILE_PATH]
    <<<< SEARCH
    [exact unique code block to find]
    ====
    [exact replacement code block]
    >>>> REPLACE

    ### [PR_SUMMARY]
    Title: [Short title]
    Description: [Concise summary of changes]
    """

    print("Gemini CLI is architecting (3-Phase Unified Mode)...")
    try:
        result = subprocess.run(["gemini", "-o", "text", prompt], capture_output=True, text=True)
        full_output = result.stdout
    except Exception as e:
        print(f"Error running gemini CLI: {e}")
        return

    # Extract Blueprint for Laborer
    blueprint_match = full_output.split("### [BLUEPRINT]")
    if len(blueprint_match) > 1:
        blueprint_content = blueprint_match[1].split("### [PR_SUMMARY]")[0]
        with open("FIX_PLAN.md", "w") as f:
            f.write(blueprint_content.strip())
        print("FIX_PLAN.md generated.")

    # Extract PR Summary for Manager
    pr_match = full_output.split("### [PR_SUMMARY]")
    if len(pr_match) > 1:
        pr_content = pr_match[1]
        with open("PR_DETAILS.md", "w") as f:
            f.write(pr_content.strip())
        print("PR_DETAILS.md generated.")

if __name__ == "__main__":
    main()