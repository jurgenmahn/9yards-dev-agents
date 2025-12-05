#!/usr/bin/env python3
"""
Index GitLab repositories (code, commits, MRs) into Chroma
Run: source .venv/bin/activate && python scripts/index-gitlab-repos.py
"""

import os
import sys
from pathlib import Path
import requests

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import chromadb
    import git
except ImportError:
    print("❌ Missing dependencies. Run: pip install chromadb gitpython")
    sys.exit(1)

# Configuration
GITLAB_TOKEN = os.getenv('GITLAB_PERSONAL_ACCESS_TOKEN')
GITLAB_URL = os.getenv('GITLAB_API_URL', 'https://git.9yards.nl/api/v4')
CHROMA_PATH = os.path.expanduser(os.getenv('CHROMA_DATA_DIR', '~/claude-code-data/chroma'))
CLONE_DIR = '/tmp/gitlab-index'
REPOS = os.getenv('GITLAB_REPOS', '').split(',')

if not GITLAB_TOKEN:
    print("❌ GITLAB_PERSONAL_ACCESS_TOKEN not set")
    sys.exit(1)

if not REPOS or REPOS == ['']:
    print("❌ GITLAB_REPOS not set (comma-separated list like: group/project1,group/project2)")
    sys.exit(1)

def get_project_id(repo_path):
    """Get GitLab project ID from path"""
    encoded_path = repo_path.replace('/', '%2F')
    resp = requests.get(
        f'{GITLAB_URL}/projects/{encoded_path}',
        headers={'PRIVATE-TOKEN': GITLAB_TOKEN}
    )
    
    if resp.ok:
        return resp.json()['id']
    else:
        print(f"  ❌ Failed to get project ID: {resp.json().get('message')}")
        return None

def clone_or_pull_repo(repo_path):
    """Clone repository or pull if exists"""
    local_path = Path(CLONE_DIR) / repo_path
    git_url = f"https://oauth2:{GITLAB_TOKEN}@{GITLAB_URL.replace('/api/v4', '')}/{repo_path}.git"
    
    if local_path.exists():
        print(f"  📥 Pulling latest changes...")
        repo = git.Repo(local_path)
        repo.remotes.origin.pull()
    else:
        print(f"  📥 Cloning repository...")
        local_path.parent.mkdir(parents=True, exist_ok=True)
        git.Repo.clone_from(git_url, local_path)
    
    return local_path

def index_code_files(repo_path, local_path):
    """Index code files with meaningful content"""
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection(
        name="codebase_knowledge",
        metadata={"description": "Indexed code, commits, and MRs"}
    )
    
    extensions = {'.php', '.js', '.vue', '.py', '.md', '.xml', '.json'}
    excluded_dirs = {'vendor', 'node_modules', '.git', 'var', 'pub/static'}
    
    indexed = 0
    skipped = 0
    
    print(f"  📄 Indexing code files...", end='', flush=True)
    
    for file_path in Path(local_path).rglob('*'):
        # Skip if in excluded directory
        if any(excluded in file_path.parts for excluded in excluded_dirs):
            continue
        
        if file_path.suffix not in extensions:
            continue
        
        if not file_path.is_file():
            continue
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Skip very small or very large files
            if len(content) < 100 or len(content) > 100000:
                skipped += 1
                continue
            
            relative_path = file_path.relative_to(local_path)
            doc_id = f"code_{repo_path}_{relative_path}".replace('/', '_')
            
            # Check if already indexed
            try:
                existing = collection.get(ids=[doc_id])
                if existing and existing['ids']:
                    skipped += 1
                    continue
            except:
                pass
            
            metadata = {
                'type': 'code',
                'source': 'gitlab',
                'repo': repo_path,
                'file': str(relative_path),
                'language': file_path.suffix[1:]
            }
            
            collection.add(
                documents=[content],
                metadatas=[metadata],
                ids=[doc_id]
            )
            indexed += 1
            
        except Exception as e:
            skipped += 1
            continue
    
    print(f" indexed {indexed}, skipped {skipped}")

def index_commits(local_path, repo_path):
    """Index meaningful commit messages"""
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection(name="codebase_knowledge")
    
    repo = git.Repo(local_path)
    
    indexed = 0
    skipped = 0
    
    print(f"  📝 Indexing commits...", end='', flush=True)
    
    # Last 500 commits
    for commit in list(repo.iter_commits('main', max_count=500)):
        message = commit.message.strip()
        
        # Skip merge commits and trivial messages
        if message.startswith('Merge') or len(message) < 20:
            skipped += 1
            continue
        
        doc_id = f"commit_{repo_path}_{commit.hexsha}".replace('/', '_')
        
        # Check if already indexed
        try:
            existing = collection.get(ids=[doc_id])
            if existing and existing['ids']:
                skipped += 1
                continue
        except:
            pass
        
        metadata = {
            'type': 'commit',
            'source': 'gitlab',
            'repo': repo_path,
            'sha': commit.hexsha[:8],
            'author': commit.author.name,
            'date': commit.committed_datetime.isoformat()
        }
        
        try:
            collection.add(
                documents=[message],
                metadatas=[metadata],
                ids=[doc_id]
            )
            indexed += 1
        except Exception as e:
            skipped += 1
    
    print(f" indexed {indexed}, skipped {skipped}")

def index_merge_requests(project_id, repo_path):
    """Index MR descriptions and discussions"""
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection(name="codebase_knowledge")
    
    indexed = 0
    skipped = 0
    
    print(f"  🔀 Indexing merge requests...", end='', flush=True)
    
    # Get last 100 merged MRs
    resp = requests.get(
        f'{GITLAB_URL}/projects/{project_id}/merge_requests',
        headers={'PRIVATE-TOKEN': GITLAB_TOKEN},
        params={'state': 'merged', 'per_page': 100, 'order_by': 'updated_at'}
    )
    
    if not resp.ok:
        print(f" ❌ Failed to fetch MRs")
        return
    
    for mr in resp.json():
        # Combine title + description
        content = f"{mr['title']}\n\n{mr.get('description', '')}"
        
        if len(content) < 30:
            skipped += 1
            continue
        
        doc_id = f"mr_{project_id}_{mr['iid']}"
        
        # Check if already indexed
        try:
            existing = collection.get(ids=[doc_id])
            if existing and existing['ids']:
                skipped += 1
                continue
        except:
            pass
        
        metadata = {
            'type': 'merge_request',
            'source': 'gitlab',
            'repo': repo_path,
            'mr_id': mr['iid'],
            'author': mr['author']['username'],
            'merged_at': mr.get('merged_at', ''),
            'web_url': mr['web_url']
        }
        
        try:
            collection.add(
                documents=[content],
                metadatas=[metadata],
                ids=[doc_id]
            )
            indexed += 1
        except Exception as e:
            skipped += 1
    
    print(f" indexed {indexed}, skipped {skipped}")

def main():
    print("=" * 60)
    print("🔍 GitLab Codebase Indexing")
    print("=" * 60)
    print(f"📂 Chroma path: {CHROMA_PATH}")
    print(f"📦 Repositories: {len(REPOS)}")
    print()
    
    Path(CLONE_DIR).mkdir(parents=True, exist_ok=True)
    
    for repo_path in REPOS:
        repo_path = repo_path.strip()
        if not repo_path:
            continue
            
        print(f"📦 Processing {repo_path}...")
        
        project_id = get_project_id(repo_path)
        if not project_id:
            continue
        
        local_path = clone_or_pull_repo(repo_path)
        
        index_code_files(repo_path, local_path)
        index_commits(local_path, repo_path)
        index_merge_requests(project_id, repo_path)
        
        print()
    
    print("=" * 60)
    print("✅ GitLab indexing complete!")
    print("=" * 60)

if __name__ == '__main__':
    main()
