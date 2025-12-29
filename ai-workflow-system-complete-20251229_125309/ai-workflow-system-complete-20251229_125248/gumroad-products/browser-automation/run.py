#!/usr/bin/env python3
"""
Browser Automation Tool - Recipe Runner
Automate Any Web Task Locally – No Code, No Cloud, Just Results
"""

import click
import yaml
import json
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table

console = Console()

class RecipeRunner:
    """Execute browser automation recipes."""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.results = []
        
    def _load_config(self, path: str) -> dict:
        """Load configuration file."""
        config_file = Path(path)
        if config_file.exists():
            with open(config_file) as f:
                return yaml.safe_load(f)
        return {}
    
    def load_recipe(self, recipe_path: str) -> dict:
        """Load and parse a recipe YAML file."""
        with open(recipe_path) as f:
            recipe = yaml.safe_load(f)
        console.print(f"[green]✓[/green] Loaded recipe: {recipe.get('name', 'Unknown')}")
        return recipe
    
    def validate_recipe(self, recipe: dict) -> bool:
        """Validate recipe structure."""
        required_fields = ['name', 'steps']
        for field in required_fields:
            if field not in recipe:
                console.print(f"[red]✗[/red] Missing required field: {field}")
                return False
        return True
    
    def execute(self, recipe: dict, dry_run: bool = False) -> dict:
        """Execute a recipe."""
        if dry_run:
            console.print("[yellow]DRY RUN MODE[/yellow] - No actions will be performed")
            return self._dry_run(recipe)
        
        # Import Playwright only when needed
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            console.print("[red]Error:[/red] Playwright not installed. Run: pip install playwright && playwright install")
            return {"status": "error", "message": "Playwright not installed"}
        
        results = {
            "recipe": recipe.get("name"),
            "started_at": datetime.now().isoformat(),
            "steps_completed": 0,
            "steps_total": len(recipe.get("steps", [])),
            "status": "running"
        }
        
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=self.config.get("browser", {}).get("headless", False)
            )
            page = browser.new_page()
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Executing recipe...", total=len(recipe["steps"]))
                
                for i, step in enumerate(recipe["steps"]):
                    action = step.get("action")
                    progress.update(task, description=f"Step {i+1}: {action}")
                    
                    try:
                        self._execute_step(page, step)
                        results["steps_completed"] += 1
                    except Exception as e:
                        console.print(f"[red]Error in step {i+1}:[/red] {str(e)}")
                        if self.config.get("automation", {}).get("screenshot_on_error", True):
                            screenshot_path = f"output/error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                            page.screenshot(path=screenshot_path)
                            console.print(f"[yellow]Screenshot saved:[/yellow] {screenshot_path}")
                        break
                    
                    progress.advance(task)
            
            browser.close()
        
        results["completed_at"] = datetime.now().isoformat()
        results["status"] = "completed" if results["steps_completed"] == results["steps_total"] else "partial"
        
        return results
    
    def _execute_step(self, page, step: dict):
        """Execute a single step."""
        action = step.get("action")
        
        if action == "navigate":
            page.goto(step["url"])
            if "wait_for" in step:
                page.wait_for_selector(step["wait_for"])
                
        elif action == "click":
            page.click(step["selector"])
            if "wait_for" in step:
                page.wait_for_selector(step["wait_for"])
                
        elif action == "type":
            page.fill(step["selector"], step["value"])
            
        elif action == "clear":
            page.fill(step["selector"], "")
            
        elif action == "wait":
            page.wait_for_timeout(step.get("duration_ms", 1000))
            
        elif action == "extract":
            # Extract data from page
            elements = page.query_selector_all(step["selector"])
            return [el.inner_text() for el in elements]
            
        elif action == "keyboard":
            for key in step.get("keys", []):
                page.keyboard.press(key)
    
    def _dry_run(self, recipe: dict) -> dict:
        """Simulate recipe execution without performing actions."""
        table = Table(title=f"Recipe: {recipe.get('name')}")
        table.add_column("Step", style="cyan")
        table.add_column("Action", style="green")
        table.add_column("Details", style="white")
        
        for i, step in enumerate(recipe.get("steps", []), 1):
            action = step.get("action", "unknown")
            details = step.get("url") or step.get("selector") or step.get("value") or ""
            if len(details) > 50:
                details = details[:47] + "..."
            table.add_row(str(i), action, details)
        
        console.print(table)
        return {"status": "dry_run", "steps": len(recipe.get("steps", []))}


@click.command()
@click.option("--recipe", "-r", required=True, help="Path to recipe YAML file")
@click.option("--config", "-c", default="config.yaml", help="Path to config file")
@click.option("--dry-run", is_flag=True, help="Preview recipe without executing")
@click.option("--output", "-o", default="output", help="Output directory")
def main(recipe: str, config: str, dry_run: bool, output: str):
    """
    Browser Automation Tool - Execute automation recipes.
    
    Example:
        python run.py --recipe recipes/shopify-price-updater.yaml
        python run.py --recipe recipes/linkedin-connector.yaml --dry-run
    """
    console.print(Panel.fit(
        "[bold blue]Browser Automation Tool[/bold blue]\n"
        "Automate Any Web Task Locally",
        border_style="blue"
    ))
    
    runner = RecipeRunner(config)
    
    # Load and validate recipe
    recipe_data = runner.load_recipe(recipe)
    if not runner.validate_recipe(recipe_data):
        raise click.Abort()
    
    # Execute
    results = runner.execute(recipe_data, dry_run=dry_run)
    
    # Save results
    if not dry_run:
        output_path = Path(output)
        output_path.mkdir(exist_ok=True)
        results_file = output_path / f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)
        console.print(f"\n[green]Results saved:[/green] {results_file}")
    
    # Summary
    console.print(f"\n[bold]Status:[/bold] {results['status']}")
    if "steps_completed" in results:
        console.print(f"[bold]Steps:[/bold] {results['steps_completed']}/{results['steps_total']}")


if __name__ == "__main__":
    main()
