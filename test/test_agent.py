import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ensure the repository root is on sys.path so `from src...` imports work
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Add the 'src' directory to the Python path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from src.agent.agent import run_agent

# --- ❗️ CONFIGURATION ❗️ ---
# IMPORTANT: Replace this with the actual, absolute path to YOUR Spring Boot project.
PATH_TO_YOUR_SPRING_BOOT_PROJECT = "/home/souhaib/Projects/modelService" 
# Example for Windows: "C:\\Users\\Souhaib\\Projects\\my-spring-project"
# --- END CONFIGURATION ---


def main():
    print("--- Loading environment variables from .env ---")
    load_dotenv()

    if not os.path.exists(PATH_TO_YOUR_SPRING_BOOT_PROJECT):
        print(f"❌ ERROR: The project path specified does not exist: {PATH_TO_YOUR_SPRING_BOOT_PROJECT}")
        print("Please update the PATH_TO_YOUR_SPRING_BOOT_PROJECT variable in test_agent.py")
        return

    print(f"--- 🚀 Starting Multi-Agent System on project: {PATH_TO_YOUR_SPRING_BOOT_PROJECT} ---")
    final_doc, report = run_agent(PATH_TO_YOUR_SPRING_BOOT_PROJECT)

    print("\n" + "="*50)
    print("✅ AGENT RUN COMPLETE")
    print("="*50 + "\n")

    print("--- Final Report ---")
    print(report)

    print("\n--- Final Generated Documentation ---")
    print(final_doc)

    # Save the final output to a file for easy review
    output_filename = "FINAL_DOCUMENTATION.md"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(final_doc)
    print(f"\n📄 Documentation saved to {output_filename}")


if __name__ == "__main__":
    main()