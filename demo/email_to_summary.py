#!/usr/bin/env python3
"""
End-to-end demo: Email with PDF → Summary

This script demonstrates the complete workflow:
1. Simulate receiving an email with PDF attachment
2. Call the API to process it
3. Show real-time progress via WebSocket
4. Display the final summary

Run this after starting the API server:
    python apps/api/main.py
"""

import asyncio
import requests
import websockets
import json
import base64
from pathlib import Path
from datetime import datetime
import sys
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel
from rich.markdown import Markdown
from rich.live import Live
from rich.table import Table
import time

console = Console()


class EmailDemo:
    """Demonstrates email to summary workflow."""
    
    def __init__(self, api_base_url="http://localhost:8000"):
        self.api_base_url = api_base_url
        self.ws_url = "ws://localhost:8000/ws"
        self.console = console
        
    def create_sample_email_with_pdf(self) -> dict:
        """Create a sample email with PDF attachment."""
        # Check for sample PDF
        sample_pdfs = [
            Path("tests/sample.pdf"),
            Path("data/samples/research_paper.pdf"),
            Path("workflows/templates/sample.pdf")
        ]
        
        pdf_path = None
        for path in sample_pdfs:
            if path.exists():
                pdf_path = path
                break
        
        if not pdf_path:
            # Create a simple test PDF
            self.console.print("[yellow]No sample PDF found, creating one...[/yellow]")
            pdf_path = self.create_test_pdf()
        
        # Read PDF content
        with open(pdf_path, 'rb') as f:
            pdf_content = f.read()
        
        # Create email data
        email_data = {
            "subject": "Q2 Financial Report for Review",
            "sender": "cfo@example.com",
            "body": "Please review the attached Q2 financial report and provide a summary of key findings.",
            "attachments": [{
                "name": pdf_path.name,
                "content": base64.b64encode(pdf_content).decode()
            }]
        }
        
        return email_data, len(pdf_content)
    
    def create_test_pdf(self) -> Path:
        """Create a simple test PDF."""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
        except ImportError:
            self.console.print("[red]reportlab not installed. Using existing PDF.[/red]")
            # Return a placeholder path
            return Path("test.pdf")
        
        pdf_path = Path("demo/test_financial_report.pdf")
        pdf_path.parent.mkdir(exist_ok=True)
        
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        
        # Add content
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 750, "Q2 2025 Financial Report")
        
        c.setFont("Helvetica", 12)
        y = 700
        content = [
            "Executive Summary:",
            "Total Revenue: $12.5M (+15% YoY)",
            "Operating Expenses: $8.2M (+10% YoY)",
            "Net Profit: $4.3M (+25% YoY)",
            "",
            "Key Highlights:",
            "- Strong growth in cloud services division",
            "- International expansion showing positive results",
            "- R&D investments increased by 20%",
            "- Customer retention rate at 95%",
            "",
            "Recommendations:",
            "- Continue investment in cloud infrastructure",
            "- Expand sales team in APAC region",
            "- Focus on AI/ML product development"
        ]
        
        for line in content:
            c.drawString(100, y, line)
            y -= 20
        
        c.save()
        return pdf_path
    
    async def monitor_progress(self, run_id: str, progress_table: Table):
        """Monitor workflow progress via WebSocket."""
        try:
            async with websockets.connect(self.ws_url) as websocket:
                self.console.print("[green]Connected to WebSocket[/green]")
                
                while True:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=30)
                        data = json.loads(message)
                        
                        if data.get("event") == "email.processing.started":
                            progress_table.add_row(
                                datetime.now().strftime("%H:%M:%S"),
                                "Started",
                                f"Processing {data['data'].get('pdf_name', 'PDF')}"
                            )
                        
                        elif data.get("event") == "email.processing.progress":
                            progress_table.add_row(
                                datetime.now().strftime("%H:%M:%S"),
                                "Progress",
                                data['data'].get('progress', 'Processing...')
                            )
                        
                        elif data.get("event") == "email.processing.completed":
                            progress_table.add_row(
                                datetime.now().strftime("%H:%M:%S"),
                                "✅ Complete",
                                f"Processed in {data['data'].get('processing_time_ms', 0)}ms"
                            )
                            return data['data'].get('summary')
                        
                        elif data.get("event") == "email.processing.error":
                            progress_table.add_row(
                                datetime.now().strftime("%H:%M:%S"),
                                "❌ Error",
                                data['data'].get('error', 'Unknown error')
                            )
                            return None
                            
                    except asyncio.TimeoutError:
                        # Keep connection alive
                        await websocket.send("ping")
                        
        except Exception as e:
            self.console.print(f"[red]WebSocket error: {e}[/red]")
            return None
    
    async def run_demo(self):
        """Run the complete demo."""
        self.console.clear()
        
        # Header
        self.console.print(Panel.fit(
            "[bold blue]Email to Summary Demo[/bold blue]\n"
            "Demonstrating PDF processing through email workflow",
            padding=(1, 2)
        ))
        
        # Step 1: Create sample email
        with self.console.status("[bold green]Creating sample email..."):
            email_data, pdf_size = self.create_sample_email_with_pdf()
            time.sleep(0.5)
        
        self.console.print("\n📧 [bold]Sample Email Created:[/bold]")
        email_table = Table(show_header=False, box=None)
        email_table.add_column(style="cyan", width=12)
        email_table.add_column()
        email_table.add_row("From:", email_data["sender"])
        email_table.add_row("Subject:", email_data["subject"])
        email_table.add_row("Attachment:", f"{email_data['attachments'][0]['name']} ({pdf_size:,} bytes)")
        self.console.print(email_table)
        
        # Step 2: Send to API
        self.console.print("\n🚀 [bold]Sending to API...[/bold]")
        
        try:
            response = requests.post(
                f"{self.api_base_url}/api/process-email",
                json=email_data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            result = response.json()
            run_id = result["run_id"]
            
            self.console.print(f"[green]✓ Email accepted[/green] - Run ID: {run_id}")
            
        except Exception as e:
            self.console.print(f"[red]Failed to send email: {e}[/red]")
            return
        
        # Step 3: Monitor progress
        self.console.print("\n📊 [bold]Processing Progress:[/bold]")
        
        progress_table = Table(show_header=True, box=None)
        progress_table.add_column("Time", style="dim", width=10)
        progress_table.add_column("Status", width=15)
        progress_table.add_column("Details")
        
        # Start WebSocket monitoring in background
        summary_task = asyncio.create_task(
            self.monitor_progress(run_id, progress_table)
        )
        
        # Show live progress
        with Live(progress_table, refresh_per_second=4) as live:
            summary = await summary_task
        
        # Step 4: Display results
        if summary:
            self.console.print("\n📄 [bold]Generated Summary:[/bold]")
            self.console.print(Panel(
                Markdown(summary),
                title="Executive Summary",
                border_style="green"
            ))
            
            # Performance stats
            self.console.print("\n📈 [bold]Performance Metrics:[/bold]")
            stats_table = Table(show_header=False, box=None)
            stats_table.add_column(style="cyan", width=20)
            stats_table.add_column()
            
            # Get final status
            status_response = requests.get(f"{self.api_base_url}/api/email-status/{run_id}")
            if status_response.ok:
                status_data = status_response.json()
                stats_table.add_row("Processing Time:", f"{status_data.get('processing_time_ms', 0)}ms")
                stats_table.add_row("Status:", status_data.get('status', 'unknown'))
                
            self.console.print(stats_table)
            
            self.console.print("\n[bold green]✅ Demo completed successfully![/bold green]")
        else:
            self.console.print("\n[bold red]❌ Demo failed - no summary generated[/bold red]")
    
    def check_api_health(self):
        """Check if API is running."""
        try:
            response = requests.get(f"{self.api_base_url}/health")
            return response.ok
        except:
            return False


async def main():
    """Main demo entry point."""
    demo = EmailDemo()
    
    # Check API health
    if not demo.check_api_health():
        console.print("[bold red]❌ API is not running![/bold red]")
        console.print("\nPlease start the API first:")
        console.print("  cd apps/api")
        console.print("  python main.py")
        sys.exit(1)
    
    # Run demo
    try:
        await demo.run_demo()
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Demo error: {e}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Install rich if not available
    try:
        import rich
    except ImportError:
        print("Installing required package: rich")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "rich"])
    
    asyncio.run(main())