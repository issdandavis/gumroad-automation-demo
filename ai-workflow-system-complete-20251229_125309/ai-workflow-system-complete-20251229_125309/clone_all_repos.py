#!/usr/bin/env python3
"""
Clone all high-potential repositories for review
"""

import os
import subprocess
import json

def run_command(cmd, cwd=None):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def clone_repo(repo_url, folder_name):
    """Clone a repository"""
    print(f"📥 Cloning {folder_name}...")
    
    if os.path.exists(folder_name):
        print(f"   ⚠️  {folder_name} already exists, pulling latest...")
        success, stdout, stderr = run_command("git pull", cwd=folder_name)
        if success:
            print(f"   ✅ Updated {folder_name}")
        else:
            print(f"   ❌ Failed to update {folder_name}: {stderr}")
    else:
        success, stdout, stderr = run_command(f"git clone {repo_url} {folder_name}")
        if success:
            print(f"   ✅ Cloned {folder_name}")
        else:
            print(f"   ❌ Failed to clone {folder_name}: {stderr}")
    
    return success

def main():
    # High-potential repositories to clone
    high_potential_repos = [
        {
            "name": "AI-Workflow-Architect",
            "url": "https://github.com/issdandavis/AI-Workflow-Architect.git",
            "priority": 1
        },
        {
            "name": "AI-Workflow-Architect.01.01.02", 
            "url": "https://github.com/issdandavis/AI-Workflow-Architect.01.01.02.git",
            "priority": 1
        },
        {
            "name": "gumroad-automation-demo",
            "url": "https://github.com/issdandavis/gumroad-automation-demo.git", 
            "priority": 1
        },
        {
            "name": "morewritings",
            "url": "https://github.com/issdandavis/morewritings.git",
            "priority": 2
        },
        {
            "name": "ai-orchestration-hub",
            "url": "https://github.com/issdandavis/ai-orchestration-hub.git",
            "priority": 2
        },
        {
            "name": "chat-archive-system", 
            "url": "https://github.com/issdandavis/chat-archive-system.git",
            "priority": 2
        },
        {
            "name": "Shopify",
            "url": "https://github.com/issdandavis/Shopify.git",
            "priority": 3
        }
    ]
    
    print("🚀 CodeVoyager's Repository Cloning Mission")
    print("=" * 50)
    
    # Create projects directory
    projects_dir = "projects_review"
    if not os.path.exists(projects_dir):
        os.makedirs(projects_dir)
        print(f"📁 Created {projects_dir} directory")
    
    os.chdir(projects_dir)
    
    successful_clones = []
    failed_clones = []
    
    for repo in high_potential_repos:
        success = clone_repo(repo["url"], repo["name"])
        if success:
            successful_clones.append(repo["name"])
        else:
            failed_clones.append(repo["name"])
    
    print("\n" + "=" * 50)
    print("📊 CLONING SUMMARY")
    print("=" * 50)
    print(f"✅ Successfully cloned: {len(successful_clones)}")
    for repo in successful_clones:
        print(f"   • {repo}")
    
    if failed_clones:
        print(f"\n❌ Failed to clone: {len(failed_clones)}")
        for repo in failed_clones:
            print(f"   • {repo}")
    
    print(f"\n📁 All repositories are in: {os.path.abspath('.')}")
    print("\n🎯 Ready for CodeVoyager's deep dive review!")

if __name__ == "__main__":
    main()