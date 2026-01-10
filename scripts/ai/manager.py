import subprocess
import os
import time

MAX_ITERATIONS = 5

def run_script(script_name, args=[]):
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    cmd = ["python3", script_path] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"Error in {script_name}: {result.stderr}")
    return result.returncode

def main():
    print("🚀 Starting AI Minimal-Change Automation Loop...")
    
    # Check if we are in a PR environment
    pr_id = os.environ.get("PR_ID", "0")
    repo = os.environ.get("GITHUB_REPOSITORY", "local/local")

    for i in range(MAX_ITERATIONS):
        print(f"\n--- Iteration {i+1} ---")
        
        # 1. Review
        print("🔍 Step 1: Reviewing staged changes (Minimalist Mode)...")
        run_script("reviewer.py")
        
        if os.path.exists("local_review.md"):
            with open("local_review.md", "r") as f:
                review_content = f.read().upper()
                if "LGTM" in review_content and len(review_content) < 50:
                    print("✅ AI Review: LGTM. Code meets project standards.")
                    break
        else:
            print("No review generated. Staging might be empty.")
            break

        # 2. Architect
        print("🧠 Step 2: Architecting minimal fix plan (3-Phase Reasoning)...")
        run_script("architect.py", ["--pr", pr_id, "--repo", repo])
        
        if not os.path.exists("FIX_PLAN.md"):
            print("✅ Architect found no valid fixes or rejected suggestions. Loop complete.")
            break

        # 3. Laborer
        print("👷 Step 3: Laborer applying minimal fixes...")
        run_script("laborer.py")
        
        # 4. Re-stage
        print("🔄 Re-staging changes for next iteration...")
        subprocess.run(["git", "add", "."], capture_output=True)
        
        # Cleanup
        if os.path.exists("FIX_PLAN.md"):
            os.remove("FIX_PLAN.md")
        # Keep PR_DETAILS.md for the end

    if os.path.exists("PR_DETAILS.md"):
        print("\n📝 Proposed PR Details:")
        with open("PR_DETAILS.md", "r") as f:
            print(f.read())
    
    print("\n✅ AI Automation completed.")

if __name__ == "__main__":
    main()
