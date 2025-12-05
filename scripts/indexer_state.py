#!/usr/bin/env python3
"""
State management for incremental indexing
Tracks progress and last indexed items to enable delta updates
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any


class IndexerState:
    """Manages persistent state for incremental indexing"""

    def __init__(self, state_file: str = ".indexer-state.json"):
        self.state_file = Path(__file__).parent / state_file
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        """Load state from file or create new"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Failed to load state file: {e}")
                return self._default_state()
        return self._default_state()

    def _default_state(self) -> Dict[str, Any]:
        """Return default empty state structure"""
        return {
            "slack": {
                "channels": {}
            },
            "gitlab": {
                "repos": {}
            }
        }

    def save(self):
        """Save current state to file"""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            print(f"⚠️  Failed to save state: {e}")

    def reset(self):
        """Reset state (for full reindex)"""
        self.state = self._default_state()
        if self.state_file.exists():
            self.state_file.unlink()

    # Slack state management

    def get_slack_channel_timestamp(self, channel_name: str) -> Optional[str]:
        """Get last indexed timestamp for Slack channel"""
        channels = self.state.get("slack", {}).get("channels", {})
        channel_data = channels.get(channel_name, {})
        return channel_data.get("last_timestamp")

    def update_slack_channel(self, channel_name: str, last_timestamp: str):
        """Update last indexed timestamp for Slack channel"""
        if "slack" not in self.state:
            self.state["slack"] = {"channels": {}}
        if "channels" not in self.state["slack"]:
            self.state["slack"]["channels"] = {}

        self.state["slack"]["channels"][channel_name] = {
            "last_timestamp": last_timestamp,
            "last_run": datetime.now().isoformat()
        }

    # GitLab state management

    def get_gitlab_repo_state(self, repo_path: str) -> Optional[Dict[str, Any]]:
        """Get last indexed state for GitLab repo"""
        repos = self.state.get("gitlab", {}).get("repos", {})
        return repos.get(repo_path)

    def update_gitlab_repo(
        self,
        repo_path: str,
        last_commit_sha: str,
        indexed_files: list[str]
    ):
        """Update last indexed commit and files for GitLab repo"""
        if "gitlab" not in self.state:
            self.state["gitlab"] = {"repos": {}}
        if "repos" not in self.state["gitlab"]:
            self.state["gitlab"]["repos"] = {}

        self.state["gitlab"]["repos"][repo_path] = {
            "last_commit_sha": last_commit_sha,
            "last_run": datetime.now().isoformat(),
            "indexed_files": indexed_files
        }

    def get_gitlab_indexed_files(self, repo_path: str) -> list[str]:
        """Get list of previously indexed files for a repo"""
        repo_state = self.get_gitlab_repo_state(repo_path)
        if repo_state:
            return repo_state.get("indexed_files", [])
        return []
