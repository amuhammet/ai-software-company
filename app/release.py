import os
from github import Github, GithubException
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

class ReleaseManager:
    def __init__(self):
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            raise ValueError("GITHUB_TOKEN not found in environment variables.")
        
        self.gh = Github(token)
        # Assumes the token has access to the current repository
        # In a real scenario, you might pass the repo name as an env var
        self.repo_name = os.getenv("GITHUB_REPOSITORY") # Provided by GH Actions or .env

    def create_production_release(self, version: str, description: str, files: Optional[List[str]] = None) -> str:
        """
        Creates a Git tag and a GitHub Release with optional artifacts.
        """
        try:
            repo = self.gh.get_repo(self.repo_name)
            
            # 1. Create the Git Tag
            # Note: In a real flow, the tag is often created by the git commit 
            # but we ensure it exists here for the release.
            repo.create_git_ref(ref=f"refs/tags/{version}")

            # 2. Create the GitHub Release
            release = repo.create_git_release(
                tag=version,
                name=f"Release {version}",
                message=description,
                draft=False,
                prerelease=False
            )

            # 3. Upload Artifacts if provided
            if files:
                for file_path in files:
                    if os.path.exists(file_path):
                        release.upload_asset(path=file_path)

            return f"Successfully released {version}. URL: {release.html_url}"

        except GithubException as e:
            return f"GitHub API Error: {e.data.get('message', str(e))}"
        except Exception as e:
            return f"Unexpected error during release: {str(e)}"

if __name__ == "__main__":
    # Example usage for testing
    manager = ReleaseManager()
    print(manager.create_production_release(
        version="v0.1.0", 
        description="Initial production-ready foundation", 
        files=["requirements.txt"]
    ))
