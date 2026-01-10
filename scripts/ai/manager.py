import subprocess
import time
import os

MAX_ITERATIONS = 5

def run_script(script_name, args=[]):
    try:
        cmd = ["python", f"scripts/ai/{script_name}"] + args
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running {script_name}: {e}")
        return False

def main():
    print("🚀 Starting AI Automation Loop...")
    
    for i in range(MAX_ITERATIONS):
        print(f"\n--- Iteration {i+1} ---")
        
        # 1. Review
        print("🔍 Step 1: Reviewing staged changes...")
        run_script("reviewer.py")
        
        if os.path.exists("local_review.md"):
            with open("local_review.md", "r") as f:
                review_content = f.read().upper()
                if "LGTM" in review_content and len(review_content) < 50:
                    print("✅ AI Reviewer says LGTM! Loop complete.")
                    break
        
        # 2. Architect
        print("🧠 Step 2: Architecting fix plan...")
        # Passing a dummy PR/Repo since we are working locally on staged changes
        run_script("architect.py", ["--pr", "0", "--repo", "local/local"])
        
        if not os.path.exists("FIX_PLAN.md"):
            print("✅ Architect found no valid fixes. Loop complete.")
            break

        # 3. Laborer
        print("👷 Step 3: Laborer applying fixes...")
        run_script("laborer.py")
        
        # 4. Clean up and Re-stage
        print("🔄 Re-staging changes for next iteration...")
        subprocess.run(["git", "add", "-A"])
        
        # Wait a bit to avoid hitting rate limits too fast
        time.sleep(2)
    else:
        print("⚠️ Reached max iterations. Please check the code manually.")

if __name__ == "__main__":
    main()
