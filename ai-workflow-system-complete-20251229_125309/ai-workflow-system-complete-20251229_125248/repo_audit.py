#!/usr/bin/env python3
"""
GitHub Repository Audit Tool
Helps review all repositories and organize them for product development
"""

import requests
import json
from datetime import datetime

def get_github_repos(username):
    """Get all repositories for a GitHub user"""
    url = f"https://api.github.com/users/{username}/repos"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            repos = response.json()
            return repos
        else:
            print(f"Error: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching repos: {e}")
        return []

def analyze_repo(repo):
    """Analyze a single repository"""
    analysis = {
        'name': repo['name'],
        'description': repo.get('description', 'No description'),
        'language': repo.get('language', 'Unknown'),
        'private': repo['private'],
        'updated': repo['updated_at'],
        'size': repo['size'],
        'stars': repo['stargazers_count'],
        'forks': repo['forks_count'],
        'url': repo['html_url'],
        'clone_url': repo['clone_url'],
        'topics': repo.get('topics', []),
        'has_issues': repo['has_issues'],
        'open_issues': repo['open_issues_count']
    }
    
    # Determine potential for Gumroad
    sellable_indicators = []
    name_lower = repo['name'].lower()
    desc_lower = (analysis['description'] or '').lower()
    
    if 'automation' in name_lower or 'automation' in desc_lower:
        sellable_indicators.append('automation-tool')
    if 'ai' in name_lower or 'ai' in desc_lower:
        sellable_indicators.append('ai-tool')
    if 'book' in name_lower or 'writing' in name_lower:
        sellable_indicators.append('content-product')
    if analysis['language'] in ['Python', 'JavaScript', 'TypeScript']:
        sellable_indicators.append('script-tool')
    
    analysis['gumroad_potential'] = sellable_indicators
    analysis['sellability_score'] = len(sellable_indicators)
    
    return analysis

def main():
    username = "issdandavis"
    print(f"🔍 Auditing GitHub repositories for {username}...")
    
    repos = get_github_repos(username)
    
    if not repos:
        print("No repositories found or error occurred")
        return
    
    print(f"📊 Found {len(repos)} repositories\n")
    
    # Analyze all repos
    analyses = []
    for repo in repos:
        analysis = analyze_repo(repo)
        analyses.append(analysis)
    
    # Sort by sellability score (highest first)
    analyses.sort(key=lambda x: x['sellability_score'], reverse=True)
    
    # Generate report
    print("=" * 80)
    print("🎯 GUMROAD PRODUCT POTENTIAL RANKING")
    print("=" * 80)
    
    for i, analysis in enumerate(analyses, 1):
        print(f"\n{i}. {analysis['name']}")
        print(f"   Description: {analysis['description']}")
        print(f"   Language: {analysis['language']}")
        print(f"   Private: {analysis['private']}")
        print(f"   Last Updated: {analysis['updated'][:10]}")
        print(f"   Sellability Score: {analysis['sellability_score']}/4")
        if analysis['gumroad_potential']:
            print(f"   Potential Categories: {', '.join(analysis['gumroad_potential'])}")
        print(f"   URL: {analysis['url']}")
        
        if analysis['sellability_score'] >= 2:
            print("   🟢 HIGH POTENTIAL FOR GUMROAD")
        elif analysis['sellability_score'] == 1:
            print("   🟡 MEDIUM POTENTIAL")
        else:
            print("   🔴 LOW POTENTIAL")
    
    # Save detailed report
    with open('github_audit_report.json', 'w') as f:
        json.dump(analyses, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: github_audit_report.json")
    
    # Quick recommendations
    print("\n" + "=" * 80)
    print("🚀 QUICK RECOMMENDATIONS")
    print("=" * 80)
    
    high_potential = [a for a in analyses if a['sellability_score'] >= 2]
    if high_potential:
        print(f"\n✅ Focus on these {len(high_potential)} high-potential repos first:")
        for repo in high_potential[:3]:  # Top 3
            print(f"   • {repo['name']} - {', '.join(repo['gumroad_potential'])}")
    
    print(f"\n📋 Next steps:")
    print(f"   1. Clone and review top 3 repositories")
    print(f"   2. Create product documentation for each")
    print(f"   3. Set up automated build/package workflows")
    print(f"   4. Create Gumroad listings")

if __name__ == "__main__":
    main()