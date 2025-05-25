#!/usr/bin/env python3
"""
Archive Integrity Validator
Scans run_archive.json and validates the integrity of archived workflow runs.
"""

import argparse
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import sys
from collections import defaultdict

# Set up logging
def setup_logging(log_file: Optional[str] = None, verbose: bool = False):
    """Set up logging configuration."""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_level = logging.DEBUG if verbose else logging.INFO
    
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_file:
        # Create logs directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=handlers
    )
    
    return logging.getLogger('archive_validator')


class ArchiveValidator:
    """Validates the integrity of workflow run archives."""
    
    def __init__(self, archive_path: str = "data/workflows/run_archive.json",
                 workflow_base: str = "data/workflows",
                 log_file: Optional[str] = None):
        """Initialize the validator.
        
        Args:
            archive_path: Path to run_archive.json
            workflow_base: Base directory for workflow outputs
            log_file: Optional path to log file
        """
        self.archive_path = Path(archive_path)
        self.workflow_base = Path(workflow_base)
        self.logger = setup_logging(log_file)
        self.validation_errors = []
        self.validation_warnings = []
        
    def load_archive(self) -> List[Dict]:
        """Load the run archive file.
        
        Returns:
            List of workflow run entries
        """
        if not self.archive_path.exists():
            self.logger.error(f"Archive file not found: {self.archive_path}")
            return []
            
        try:
            with open(self.archive_path) as f:
                data = json.load(f)
                self.logger.info(f"Loaded {len(data)} entries from archive")
                return data
        except (json.JSONDecodeError, IOError) as e:
            self.logger.error(f"Error loading archive: {e}")
            return []
    
    def validate_entry(self, entry: Dict) -> Dict[str, Any]:
        """Validate a single archive entry.
        
        Args:
            entry: Archive entry to validate
            
        Returns:
            Dictionary of validation results
        """
        errors = []
        warnings = []
        
        # Extract basic info
        workflow_id = entry.get('workflow_id', 'unknown')
        run_id = entry.get('run_id', 'unknown')
        entry_id = f"{workflow_id}/{run_id}"
        
        # 1. Validate required fields
        required_fields = ['workflow_id', 'run_id', 'timestamp', 'workflow_name', 'status']
        for field in required_fields:
            if not entry.get(field):
                errors.append(f"Missing required field: {field}")
        
        # 2. Validate timestamp format
        timestamp = entry.get('timestamp')
        if timestamp:
            try:
                # Try various timestamp formats
                if 'T' in str(timestamp):
                    datetime.fromisoformat(str(timestamp).replace('Z', '+00:00'))
                else:
                    datetime.strptime(str(timestamp), '%Y-%m-%d %H:%M:%S')
            except Exception as e:
                errors.append(f"Invalid timestamp format: {timestamp} ({e})")
        
        # 3. Check workflow directory exists
        if workflow_id != 'unknown' and run_id != 'unknown':
            run_path = self.workflow_base / workflow_id / run_id
            
            if not run_path.exists():
                errors.append(f"Run directory not found: {run_path}")
            else:
                # 4. Check for expected files in run directory
                expected_files = {
                    'workflow.yaml': 'Workflow definition',
                    'run_metadata.json': 'Run metadata'
                }
                
                for filename, description in expected_files.items():
                    file_path = run_path / filename
                    if not file_path.exists():
                        warnings.append(f"Missing {description}: {file_path}")
                
                # 5. Validate run_metadata.json if exists
                metadata_path = run_path / 'run_metadata.json'
                if metadata_path.exists():
                    try:
                        with open(metadata_path) as f:
                            metadata = json.load(f)
                            
                        # Check metadata consistency
                        if metadata.get('run_id') != run_id:
                            errors.append(f"Run ID mismatch in metadata: {metadata.get('run_id')} != {run_id}")
                        
                        if metadata.get('workflow_name') != entry.get('workflow_name'):
                            warnings.append(f"Workflow name mismatch: {metadata.get('workflow_name')} != {entry.get('workflow_name')}")
                            
                    except Exception as e:
                        errors.append(f"Error reading metadata file: {e}")
                
                # 6. Check for step output files
                step_files = list(run_path.glob('*_output.json'))
                if not step_files and entry.get('status') == 'success':
                    warnings.append("No step output files found for successful run")
                
                # 7. Validate step output files
                for step_file in step_files:
                    try:
                        with open(step_file) as f:
                            step_data = json.load(f)
                            if not step_data:
                                warnings.append(f"Empty step output: {step_file.name}")
                    except Exception as e:
                        errors.append(f"Error reading step output {step_file.name}: {e}")
        
        # 8. Validate status value
        valid_statuses = ['success', 'failed', 'error', 'cancelled', 'running', 'pending']
        status = entry.get('status', '')
        if status and status not in valid_statuses:
            warnings.append(f"Invalid status value: {status}")
        
        # 9. Validate duration
        duration = entry.get('duration_ms')
        if duration is not None:
            if not isinstance(duration, (int, float)) or duration < 0:
                warnings.append(f"Invalid duration value: {duration}")
        
        # 10. Check source structure
        source = entry.get('source', {})
        if source and not isinstance(source, dict):
            warnings.append(f"Source should be a dictionary, got: {type(source).__name__}")
        
        return {
            'entry_id': entry_id,
            'errors': errors,
            'warnings': warnings,
            'valid': len(errors) == 0
        }
    
    def filter_by_date_range(self, entries: List[Dict], 
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> List[Dict]:
        """Filter entries by date range.
        
        Args:
            entries: List of archive entries
            start_date: Start of date range (inclusive)
            end_date: End of date range (inclusive)
            
        Returns:
            Filtered list of entries
        """
        if not start_date and not end_date:
            return entries
            
        filtered = []
        
        for entry in entries:
            try:
                timestamp_str = entry.get('timestamp', '')
                if timestamp_str:
                    if 'T' in timestamp_str:
                        entry_date = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    else:
                        entry_date = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    
                    # Check if in range
                    if start_date and entry_date.date() < start_date.date():
                        continue
                    if end_date and entry_date.date() > end_date.date():
                        continue
                        
                    filtered.append(entry)
            except Exception:
                # Include entries with invalid timestamps for validation
                filtered.append(entry)
                
        return filtered
    
    def generate_summary(self, validation_results: List[Dict]) -> Dict:
        """Generate a summary of validation results.
        
        Args:
            validation_results: List of validation result dictionaries
            
        Returns:
            Summary dictionary
        """
        total = len(validation_results)
        valid = len([r for r in validation_results if r['valid']])
        invalid = total - valid
        
        # Group errors by type
        error_types = defaultdict(int)
        warning_types = defaultdict(int)
        
        for result in validation_results:
            for error in result['errors']:
                # Extract error type from message
                if 'Missing required field' in error:
                    error_types['missing_fields'] += 1
                elif 'Run directory not found' in error:
                    error_types['missing_directory'] += 1
                elif 'Invalid timestamp' in error:
                    error_types['invalid_timestamp'] += 1
                elif 'Error reading' in error:
                    error_types['corrupt_files'] += 1
                else:
                    error_types['other'] += 1
            
            for warning in result['warnings']:
                if 'Missing' in warning and '.json' in warning:
                    warning_types['missing_metadata'] += 1
                elif 'No step output' in warning:
                    warning_types['missing_outputs'] += 1
                elif 'mismatch' in warning:
                    warning_types['data_mismatch'] += 1
                else:
                    warning_types['other'] += 1
        
        # Find patterns
        failed_workflows = defaultdict(list)
        for result in validation_results:
            if not result['valid']:
                workflow_id = result['entry_id'].split('/')[0]
                failed_workflows[workflow_id].append(result['entry_id'])
        
        return {
            'total_entries': total,
            'valid_entries': valid,
            'invalid_entries': invalid,
            'validation_rate': f"{(valid/total)*100:.1f}%" if total > 0 else "0%",
            'error_types': dict(error_types),
            'warning_types': dict(warning_types),
            'failed_workflows': dict(failed_workflows),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def save_results(self, validation_results: List[Dict], 
                    summary: Dict,
                    output_file: Optional[str] = None) -> Path:
        """Save validation results to JSON file.
        
        Args:
            validation_results: List of validation results
            summary: Summary dictionary
            output_file: Optional output file path
            
        Returns:
            Path to saved file
        """
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"logs/archive_validation_{timestamp}.json"
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Only include entries with issues
        issues_only = [r for r in validation_results if not r['valid'] or r['warnings']]
        
        output_data = {
            'summary': summary,
            'validation_issues': issues_only,
            'full_results_count': len(validation_results)
        }
        
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)
            
        return output_path
    
    def validate(self, start_date: Optional[str] = None,
                end_date: Optional[str] = None,
                output_file: Optional[str] = None) -> Tuple[bool, Path]:
        """Run validation on the archive.
        
        Args:
            start_date: Optional start date filter (YYYY-MM-DD)
            end_date: Optional end date filter (YYYY-MM-DD)
            output_file: Optional output file path
            
        Returns:
            Tuple of (success, output_path)
        """
        self.logger.info("Starting archive validation...")
        
        # Load archive
        entries = self.load_archive()
        if not entries:
            self.logger.error("No entries to validate")
            return False, None
        
        # Apply date filter if provided
        if start_date or end_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
            end_dt = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
            entries = self.filter_by_date_range(entries, start_dt, end_dt)
            self.logger.info(f"Filtered to {len(entries)} entries in date range")
        
        # Validate each entry
        validation_results = []
        for i, entry in enumerate(entries):
            self.logger.debug(f"Validating entry {i+1}/{len(entries)}")
            result = self.validate_entry(entry)
            validation_results.append(result)
            
            # Log errors immediately
            if result['errors']:
                self.logger.error(f"{result['entry_id']}: {len(result['errors'])} errors")
                for error in result['errors']:
                    self.logger.error(f"  - {error}")
            
            if result['warnings']:
                self.logger.warning(f"{result['entry_id']}: {len(result['warnings'])} warnings")
                for warning in result['warnings']:
                    self.logger.warning(f"  - {warning}")
        
        # Generate summary
        summary = self.generate_summary(validation_results)
        
        # Log summary
        self.logger.info("="*50)
        self.logger.info("VALIDATION SUMMARY")
        self.logger.info("="*50)
        self.logger.info(f"Total entries validated: {summary['total_entries']}")
        self.logger.info(f"Valid entries: {summary['valid_entries']}")
        self.logger.info(f"Invalid entries: {summary['invalid_entries']}")
        self.logger.info(f"Validation rate: {summary['validation_rate']}")
        
        if summary['error_types']:
            self.logger.info("\nError breakdown:")
            for error_type, count in summary['error_types'].items():
                self.logger.info(f"  - {error_type}: {count}")
        
        if summary['warning_types']:
            self.logger.info("\nWarning breakdown:")
            for warning_type, count in summary['warning_types'].items():
                self.logger.info(f"  - {warning_type}: {count}")
        
        # Save results
        output_path = self.save_results(validation_results, summary, output_file)
        self.logger.info(f"\nDetailed results saved to: {output_path}")
        
        return summary['invalid_entries'] == 0, output_path


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Validate integrity of workflow run archive'
    )
    parser.add_argument(
        '--archive', '-a',
        help='Path to run_archive.json. Default: data/workflows/run_archive.json',
        default='data/workflows/run_archive.json'
    )
    parser.add_argument(
        '--start', '-s',
        help='Start date filter (YYYY-MM-DD)',
        type=str
    )
    parser.add_argument(
        '--end', '-e',
        help='End date filter (YYYY-MM-DD)',
        type=str
    )
    parser.add_argument(
        '--log', '-l',
        help='Log file path. Default: logs/archive_validation.log',
        default='logs/archive_validation.log'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output JSON file for results',
        type=str
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Create validator
    validator = ArchiveValidator(
        archive_path=args.archive,
        log_file=args.log
    )
    
    # Set verbose logging if requested
    if args.verbose:
        validator.logger.setLevel(logging.DEBUG)
    
    # Run validation
    try:
        success, output_path = validator.validate(
            start_date=args.start,
            end_date=args.end,
            output_file=args.output
        )
        
        if success:
            print(f"\n✅ Archive validation passed! Results: {output_path}")
            sys.exit(0)
        else:
            print(f"\n❌ Archive validation found issues. See: {output_path}")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Validation error: {e}")
        sys.exit(2)


if __name__ == "__main__":
    main()