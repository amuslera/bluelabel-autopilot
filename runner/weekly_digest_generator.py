#!/usr/bin/env python3
"""
Weekly Digest Generator
Reads run_archive.json and generates markdown digests for a specified date range.
"""

import argparse
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('weekly_digest')


class WeeklyDigestGenerator:
    """Generates weekly digests from workflow run archives."""
    
    def __init__(self, archive_path: str = "data/workflows/run_archive.json",
                 output_dir: str = "data/digests"):
        """Initialize the digest generator.
        
        Args:
            archive_path: Path to run_archive.json
            output_dir: Directory to save digest files
        """
        self.archive_path = Path(archive_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def load_archive(self) -> List[Dict]:
        """Load the run archive file.
        
        Returns:
            List of workflow run entries
        """
        if not self.archive_path.exists():
            logger.warning(f"Archive file not found: {self.archive_path}")
            return []
            
        try:
            with open(self.archive_path) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading archive: {e}")
            return []
    
    def filter_by_date_range(self, entries: List[Dict], 
                           start_date: datetime, 
                           end_date: datetime) -> List[Dict]:
        """Filter entries by date range.
        
        Args:
            entries: List of archive entries
            start_date: Start of date range (inclusive)
            end_date: End of date range (inclusive)
            
        Returns:
            Filtered list of entries
        """
        filtered = []
        
        for entry in entries:
            try:
                # Parse timestamp
                timestamp_str = entry.get('timestamp', '')
                if timestamp_str:
                    # Handle various timestamp formats
                    if 'T' in timestamp_str:
                        entry_date = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    else:
                        entry_date = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    
                    # Check if in range (convert to date for comparison)
                    if start_date.date() <= entry_date.date() <= end_date.date():
                        filtered.append(entry)
            except Exception as e:
                logger.warning(f"Error parsing timestamp for entry {entry.get('run_id', 'unknown')}: {e}")
                
        return filtered
    
    def generate_digest(self, entries: List[Dict], 
                       start_date: datetime, 
                       end_date: datetime) -> str:
        """Generate markdown digest from entries.
        
        Args:
            entries: List of workflow entries
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            Formatted markdown content
        """
        # Calculate statistics
        total_runs = len(entries)
        successful_runs = len([e for e in entries if e.get('status') == 'success'])
        failed_runs = len([e for e in entries if e.get('status') in ['failed', 'error']])
        
        # Group by workflow
        by_workflow = defaultdict(list)
        for entry in entries:
            workflow_name = entry.get('workflow_name', 'Unknown')
            by_workflow[workflow_name].append(entry)
        
        # Group by tags
        by_tag = defaultdict(list)
        for entry in entries:
            tags = entry.get('tags', [])
            if not tags:
                by_tag['untagged'].append(entry)
            else:
                for tag in tags:
                    by_tag[tag].append(entry)
        
        # Extract sources
        sources = defaultdict(int)
        for entry in entries:
            source = entry.get('source', {})
            if isinstance(source, dict):
                source_type = source.get('type', 'unknown')
                sources[source_type] += 1
            else:
                sources['unknown'] += 1
        
        # Build markdown
        lines = []
        lines.append(f"# Weekly Digest ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})")
        lines.append("")
        lines.append(f"*Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC*")
        lines.append("")
        
        # Summary statistics
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- **Total Runs:** {total_runs}")
        lines.append(f"- **Successful:** {successful_runs} ({successful_runs/total_runs*100:.1f}%)" if total_runs > 0 else "- **Successful:** 0")
        lines.append(f"- **Failed:** {failed_runs}")
        lines.append(f"- **Workflows:** {len(by_workflow)}")
        lines.append("")
        
        # Workflows breakdown
        lines.append("## Workflows")
        lines.append("")
        for workflow, runs in sorted(by_workflow.items(), key=lambda x: len(x[1]), reverse=True):
            success_count = len([r for r in runs if r.get('status') == 'success'])
            lines.append(f"### {workflow}")
            lines.append(f"- Runs: {len(runs)}")
            lines.append(f"- Success Rate: {success_count/len(runs)*100:.1f}%")
            
            # Average duration
            durations = [r.get('duration_ms', 0) for r in runs if r.get('duration_ms')]
            if durations:
                avg_duration = sum(durations) / len(durations)
                lines.append(f"- Avg Duration: {avg_duration:.0f}ms")
            lines.append("")
        
        # Tags breakdown
        lines.append("## Tags")
        lines.append("")
        for tag, runs in sorted(by_tag.items(), key=lambda x: len(x[1]), reverse=True):
            lines.append(f"- **{tag}:** {len(runs)} runs")
        lines.append("")
        
        # Sources breakdown
        if sources:
            lines.append("## Sources")
            lines.append("")
            for source_type, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"- **{source_type}:** {count}")
            lines.append("")
        
        # Recent summaries
        lines.append("## Recent Summaries")
        lines.append("")
        
        # Get last 10 entries with summaries
        recent_with_summary = [e for e in sorted(entries, 
                                               key=lambda x: x.get('timestamp', ''), 
                                               reverse=True) 
                             if e.get('summary')][:10]
        
        for i, entry in enumerate(recent_with_summary, 1):
            lines.append(f"### {i}. {entry.get('workflow_name', 'Unknown')}")
            lines.append(f"*{entry.get('timestamp', 'Unknown time')}*")
            lines.append("")
            
            # Truncate summary if too long
            summary = entry.get('summary', '')
            if len(summary) > 500:
                summary = summary[:497] + "..."
            lines.append(summary)
            lines.append("")
        
        # Failed runs (if any)
        failed_entries = [e for e in entries if e.get('status') in ['failed', 'error']]
        if failed_entries:
            lines.append("## Failed Runs")
            lines.append("")
            for entry in failed_entries[-5:]:  # Last 5 failures
                lines.append(f"- **{entry.get('workflow_name', 'Unknown')}** ({entry.get('run_id', 'unknown')[:8]}...)")
                lines.append(f"  - Time: {entry.get('timestamp', 'unknown')}")
                lines.append(f"  - Status: {entry.get('status', 'unknown')}")
            lines.append("")
        
        return "\n".join(lines)
    
    def save_digest(self, content: str, start_date: datetime, end_date: datetime) -> Path:
        """Save digest to file.
        
        Args:
            content: Markdown content
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            Path to saved file
        """
        filename = f"weekly_digest_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.md"
        output_path = self.output_dir / filename
        
        with open(output_path, 'w') as f:
            f.write(content)
            
        return output_path
    
    def generate(self, start_date: Optional[str] = None, 
                end_date: Optional[str] = None) -> Optional[Path]:
        """Generate weekly digest for date range.
        
        Args:
            start_date: Start date (YYYY-MM-DD) or None for 7 days ago
            end_date: End date (YYYY-MM-DD) or None for today
            
        Returns:
            Path to generated digest file or None if error
        """
        # Parse dates
        if end_date:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        else:
            end_dt = datetime.now()
            
        if start_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        else:
            start_dt = end_dt - timedelta(days=7)
        
        logger.info(f"Generating digest for {start_dt.date()} to {end_dt.date()}")
        
        # Load archive
        entries = self.load_archive()
        if not entries:
            logger.error("No archive entries found")
            return None
        
        # Filter by date
        filtered = self.filter_by_date_range(entries, start_dt, end_dt)
        logger.info(f"Found {len(filtered)} entries in date range")
        
        if not filtered:
            logger.warning("No entries found in specified date range")
            # Generate empty digest
            content = f"# Weekly Digest ({start_dt.strftime('%Y-%m-%d')} to {end_dt.strftime('%Y-%m-%d')})\n\n"
            content += "*No workflow runs found in this period.*\n"
        else:
            # Generate digest
            content = self.generate_digest(filtered, start_dt, end_dt)
        
        # Save to file
        output_path = self.save_digest(content, start_dt, end_dt)
        logger.info(f"Digest saved to: {output_path}")
        
        return output_path


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Generate weekly digest from workflow run archive'
    )
    parser.add_argument(
        '--start', '-s',
        help='Start date (YYYY-MM-DD). Default: 7 days ago',
        type=str
    )
    parser.add_argument(
        '--end', '-e',
        help='End date (YYYY-MM-DD). Default: today',
        type=str
    )
    parser.add_argument(
        '--archive', '-a',
        help='Path to run_archive.json. Default: data/workflows/run_archive.json',
        default='data/workflows/run_archive.json'
    )
    parser.add_argument(
        '--output-dir', '-o',
        help='Output directory. Default: data/digests',
        default='data/digests'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create generator
    generator = WeeklyDigestGenerator(
        archive_path=args.archive,
        output_dir=args.output_dir
    )
    
    # Generate digest
    try:
        output_path = generator.generate(args.start, args.end)
        if output_path:
            print(f"✅ Digest generated successfully: {output_path}")
            
            # Show preview
            with open(output_path) as f:
                content = f.read()
                if len(content) > 1000:
                    print(f"\nPreview (first 1000 chars):\n{'-'*50}")
                    print(content[:1000])
                    print(f"{'-'*50}\n")
                else:
                    print(f"\nContent:\n{'-'*50}")
                    print(content)
                    print(f"{'-'*50}\n")
        else:
            print("❌ Failed to generate digest")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error generating digest: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()