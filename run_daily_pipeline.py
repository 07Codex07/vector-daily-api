import os
import subprocess

def run_step(name, command):
    print(f"\n🚀 Running: {name}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"❌ Step '{name}' failed.")
    else:
        print(f"✅ Step '{name}' completed.")

def main():
    steps = [
        ("Scrape Articles", "python main.py"),
        ("Generate Digests", "python generate_digests_groq.py"),
        ("Generate Newsletter", "python generate_newsletter_grok.py"),
        ("Send Newsletter", "python send_newsletter.py"),
    ]
    for name, cmd in steps:
        run_step(name, cmd)

if __name__ == "__main__":
    main()
