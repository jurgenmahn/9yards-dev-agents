#!/usr/bin/env python3
"""
Index GitLab repositories (code, commits, MRs) into Chroma
Run: source .venv/bin/activate && python scripts/index-gitlab-repos.py

Supports incremental updates by default (only indexes changed files since last run).
Use --full-reindex to force complete reindexing from scratch.
"""

import os
import sys
from pathlib import Path
import requests
import argparse
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import chromadb
    import git
except ImportError:
    print("❌ Missing dependencies. Run: pip install chromadb gitpython")
    sys.exit(1)

from scripts.indexer_state import IndexerState

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

def get_changed_files(local_path, last_commit_sha=None):
    """Get list of changed files since last commit

    Args:
        local_path: Local repository path
        last_commit_sha: Last indexed commit SHA, or None for all files

    Returns:
        tuple: (changed_files list, deleted_files list, latest_commit_sha)
    """
    repo = git.Repo(local_path)
    latest_sha = repo.head.commit.hexsha

    if not last_commit_sha:
        # First run - index all files
        return ([], [], latest_sha)

    try:
        # Get diff between last indexed commit and current HEAD
        diff = repo.git.diff(
            '--name-status',
            last_commit_sha,
            'HEAD'
        )

        changed_files = []
        deleted_files = []

        for line in diff.split('\n'):
            if not line.strip():
                continue

            parts = line.split('\t')
            if len(parts) < 2:
                continue

            status = parts[0]
            file_path = parts[1]

            if status == 'D':  # Deleted
                deleted_files.append(file_path)
            else:  # Added, Modified, Renamed, etc.
                changed_files.append(file_path)

        return (changed_files, deleted_files, latest_sha)

    except git.exc.GitCommandError as e:
        print(f"\n⚠️  Git diff failed (possibly force-pushed?): {e}")
        # Fallback to full reindex if git history changed
        return ([], [], latest_sha)


def index_code_files(repo_path, local_path, changed_files=None, full_reindex=False):
    """Index code files with meaningful content

    Args:
        repo_path: GitLab repo path (e.g., 'group/project')
        local_path: Local clone path
        changed_files: List of changed files to index (None = all files)
        full_reindex: Whether this is a full reindex

    Returns:
        list: Paths of all indexed files
    """
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection(
        name="codebase_knowledge",
        metadata={"description": "Indexed code, commits, and MRs"}
    )

    extensions = {'.php', '.js', '.vue', '.py', '.md', '.xml', '.json'}
    excluded_dirs = {'vendor', 'node_modules', '.git', 'var', 'pub/static'}

    indexed = 0
    skipped = 0
    indexed_files = []

    if changed_files is not None and len(changed_files) > 0:
        print(f"  📄 Indexing {len(changed_files)} changed files...", end='', flush=True)
        files_to_process = [Path(local_path) / f for f in changed_files]
    elif changed_files is not None:
        print(f"  📄 No changed files to index")
        return []
    else:
        print(f"  📄 Indexing all code files...", end='', flush=True)
        files_to_process = Path(local_path).rglob('*')

    for file_path in files_to_process:
        # Skip if in excluded directory
        if any(excluded in file_path.parts for excluded in excluded_dirs):
            continue

        if file_path.suffix not in extensions:
            continue

        if not file_path.is_file() or not file_path.exists():
            continue

        try:
            content = file_path.read_text(encoding='utf-8')

            # Skip very small or very large files
            if len(content) < 100 or len(content) > 100000:
                skipped += 1
                continue

            relative_path = file_path.relative_to(local_path)
            doc_id = f"code_{repo_path}_{relative_path}".replace('/', '_')

            # Only skip if full reindex is false and already indexed
            if not full_reindex:
                try:
                    existing = collection.get(ids=[doc_id])
                    if existing and existing['ids']:
                        indexed_files.append(str(relative_path))
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
            indexed_files.append(str(relative_path))

        except Exception as e:
            skipped += 1
            continue

    print(f" indexed {indexed}, skipped {skipped}")
    return indexed_files


def remove_deleted_files(repo_path, deleted_files):
    """Remove deleted files from Chroma collection

    Args:
        repo_path: GitLab repo path
        deleted_files: List of deleted file paths
    """
    if not deleted_files:
        return

    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection(name="codebase_knowledge")

    removed = 0
    print(f"  🗑️  Removing {len(deleted_files)} deleted files...", end='', flush=True)

    for file_path in deleted_files:
        doc_id = f"code_{repo_path}_{file_path}".replace('/', '_')
        try:
            collection.delete(ids=[doc_id])
            removed += 1
        except Exception as e:
            # File might not have been indexed, ignore
            pass

    print(f" removed {removed}")

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
    # Parse CLI arguments
    parser = argparse.ArgumentParser(
        description='Index GitLab repositories into Chroma (incremental by default)'
    )
    parser.add_argument(
        '--full-reindex',
        action='store_true',
        help='Force full reindexing from scratch (ignores previous state)'
    )
    args = parser.parse_args()

    # Initialize state
    state = IndexerState()

    # Handle full reindex
    if args.full_reindex:
        print("🔄 Full reindex requested - resetting state...")
        state.reset()
        mode = "FULL reindex"
    else:
        mode = "incremental update"

    print("=" * 60)
    print("🔍 GitLab Codebase Indexing")
    print("=" * 60)
    print(f"📅 Mode: {mode}")
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

        # Get last indexed commit SHA for incremental updates
        last_commit_sha = None
        if not args.full_reindex:
            repo_state = state.get_gitlab_repo_state(repo_path)
            if repo_state:
                last_commit_sha = repo_state.get('last_commit_sha')

        # Determine what changed since last run
        changed_files, deleted_files, latest_sha = get_changed_files(
            local_path,
            last_commit_sha
        )

        # Handle file deletions
        if deleted_files:
            remove_deleted_files(repo_path, deleted_files)

        # Index changed files (or all files on first run / full reindex)
        indexed_files = index_code_files(
            repo_path,
            local_path,
            changed_files=changed_files if not args.full_reindex and last_commit_sha else None,
            full_reindex=args.full_reindex
        )

        # Only index commits and MRs on full reindex (they're less frequently changing)
        if args.full_reindex or not last_commit_sha:
            index_commits(local_path, repo_path)
            index_merge_requests(project_id, repo_path)
        else:
            print(f"  ℹ️  Skipping commits/MRs (incremental mode)")

        # Update state with latest commit SHA
        state.update_gitlab_repo(repo_path, latest_sha, indexed_files)

        print()

    # Save state
    state.save()

    print("=" * 60)
    print("✅ GitLab indexing complete!")
    print("=" * 60)

if __name__ == '__main__':
    main()
