import os
import subprocess
from github import Github
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("GITHUB_TOKEN")
if not TOKEN:
    raise RuntimeError("GITHUB_TOKEN not found in .env")

gh = Github(TOKEN)

TOP_N = 20
MIN_STARS = 5000
OUTPUT_DIR = "repos"
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "repos", "top_repos_java.txt")

os.makedirs(OUTPUT_DIR, exist_ok=True)


def get_top_python_repos(top_n=TOP_N, min_stars=MIN_STARS):
    q = f"language:Java stars:>={min_stars}"
    repos = []
    for idx, repo in enumerate(gh.search_repositories(q, sort="stars", order="desc")):
        if idx >= top_n:
            break
        repos.append(repo.clone_url)
    return repos


def clone_repos(repo_urls, base_dir=OUTPUT_DIR):
    for url in repo_urls:
        name = url.split("/")[-1].replace(".git", "")
        path = os.path.join(base_dir, name)
        if os.path.exists(path):
            print(f"[skip] {name} already exists")
            continue
        print(f"[clone] {url} -> {path}")
        subprocess.run(["git", "clone", url, path], check=False)


def clone_repos_from_file(file_path=OUTPUT_FILE, base_dir=OUTPUT_DIR):
    if not os.path.exists(file_path):
        raise FileNotFoundError(file_path)
    with open(file_path, "r", encoding="utf-8") as f:
        repo_urls = [line.strip() for line in f if line.strip()]
    clone_repos(repo_urls, base_dir)


if __name__ == "__main__":
    # repos = get_top_python_repos()
    # print(f"Found {len(repos)} repos")
    #
    # # Save to text file in root
    # with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    #     for url in repos:
    #         f.write(url + "\n")
    # print(f"Saved repo list to {OUTPUT_FILE}")
    #
    # #clone_repos(repos)
    clone_repos_from_file()
