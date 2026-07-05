import os
import re
import shutil
import tempfile
import subprocess
from typing import Tuple, Optional
from gitingest import ingest

class GitService:
    @staticmethod
    def validate_url(url: str) -> bool:
        """Checks if a URL is a valid GitHub URL."""
        github_regex = r"^(https?://)?(www\.)?github\.com/[\w\-]+/[\w\-]+(/?.*)?$"
        return bool(re.match(github_regex, url))

    @staticmethod
    def extract_repo_info(url: str) -> Tuple[str, str]:
        """
        Extracts the owner and repository name from a GitHub URL.
        Allows additional path segments (e.g., /tree/main, /blob/...).
        """
        from urllib.parse import urlparse

        parsed = urlparse(url)
        # Must be a github.com URL
        if parsed.netloc.lower() != "github.com":
            raise ValueError("Invalid URL: not a github.com URL")

        # Split the path and keep only the first two components (owner/repo)
        parts = parsed.path.strip("/").split("/")
        if len(parts) < 2:
            raise ValueError("Invalid URL: expected at least owner/repo")

        owner, repo = parts[0], parts[1]
        return owner, repo


    @staticmethod
    def clone_and_ingest(
        url: str, 
        token: Optional[str] = None, 
        temp_dir: Optional[str] = None
    ) -> Tuple[str, str, str, str]:
        """
        Clones a repository (using token if private) and digests it using gitingest.
        Returns:
            summary (str): The high level summary of the codebase.
            tree (str): The file structure tree.
            content (str): The aggregated codebase content.
            local_path (str): The local path where the files were cloned.
        """
        if not GitService.validate_url(url):
            raise ValueError("Please provide a valid GitHub repository URL.")

        owner, repo_name = GitService.extract_repo_info(url)
        
        # Prepare target clone URL
        if token:
            # Inject token for authentication
            clone_url = f"https://{token}@github.com/{owner}/{repo_name}.git"
        else:
            clone_url = f"https://github.com/{owner}/{repo_name}.git"

        # If no temp_dir was provided, create one
        if not temp_dir:
            temp_dir = tempfile.mkdtemp(prefix=f"gitchat_{repo_name}_")

        # Clone repository
        try:
            # Clean directory first if it exists and has content
            if os.path.exists(temp_dir) and os.listdir(temp_dir):
                shutil.rmtree(temp_dir)
            os.makedirs(temp_dir, exist_ok=True)
                
            # Perform a shallow clone to save time/bandwidth
            cmd = ["git", "clone", "--depth", "1", clone_url, temp_dir]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        except FileNotFoundError:
            # Git is not installed! Fall back to downloading ZIP
            import urllib.request
            import zipfile
            import io
            
            zip_downloaded = False
            # Try to fetch default branches: main, then master
            for branch in ["main", "master"]:
                try:
                    zip_url = f"https://github.com/{owner}/{repo_name}/archive/refs/heads/{branch}.zip"
                    req = urllib.request.Request(
                        zip_url, 
                        headers={'User-Agent': 'Mozilla/5.0'}
                    )
                    with urllib.request.urlopen(req) as response:
                        zip_data = response.read()
                        with zipfile.ZipFile(io.BytesIO(zip_data)) as z:
                            extract_temp = tempfile.mkdtemp()
                            z.extractall(extract_temp)
                            extracted_dirs = os.listdir(extract_temp)
                            if extracted_dirs:
                                inner_dir = os.path.join(extract_temp, extracted_dirs[0])
                                for item in os.listdir(inner_dir):
                                    shutil.move(os.path.join(inner_dir, item), os.path.join(temp_dir, item))
                                zip_downloaded = True
                                shutil.rmtree(extract_temp)
                                break
                except Exception:
                    continue
            
            if not zip_downloaded:
                raise RuntimeError(
                    "Git executable ('git') was not found on this system, "
                    "and the fallback ZIP download failed. Please install Git and add it to your PATH."
                )
        except subprocess.CalledProcessError as e:
            # Cleanup on failure
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            error_msg = e.stderr or e.stdout
            if "Authentication failed" in error_msg or "Repository not found" in error_msg:
                raise PermissionError("Access denied. Please check your GitHub URL or Personal Access Token (PAT).")
            raise RuntimeError(f"Failed to clone repository: {error_msg}")

        # Run GitIngest on the cloned local directory
        try:
            summary, tree, content = ingest(temp_dir)
            return summary, tree, content, temp_dir
        except Exception as e:
            # Cleanup on failure
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            raise RuntimeError(f"Failed to analyze code structure with GitIngest: {str(e)}")
