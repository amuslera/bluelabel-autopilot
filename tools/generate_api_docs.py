#!/usr/bin/env python3
"""
API Documentation Generator

Automatically generates comprehensive API documentation from Python files,
extracting function signatures, docstrings, and usage examples from tests.
"""

import ast
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import argparse
import json


@dataclass
class FunctionDoc:
    """Documentation for a single function"""
    name: str
    signature: str
    docstring: str
    file_path: str
    line_number: int
    decorators: List[str]
    is_method: bool = False
    class_name: str = ""
    examples: List[str] = None
    
    def __post_init__(self):
        if self.examples is None:
            self.examples = []


@dataclass
class ClassDoc:
    """Documentation for a class"""
    name: str
    docstring: str
    file_path: str
    line_number: int
    methods: List[FunctionDoc]
    decorators: List[str]


class APIDocGenerator:
    """Generates API documentation from Python source files"""
    
    def __init__(self, base_path: str = "/Users/arielmuslera/Development/Projects/bluelabel-autopilot"):
        self.base_path = Path(base_path)
        self.functions: Dict[str, List[FunctionDoc]] = {}
        self.classes: Dict[str, List[ClassDoc]] = {}
        self.examples: Dict[str, List[str]] = {}
        
    def extract_docs_from_file(self, file_path: Path) -> Tuple[List[FunctionDoc], List[ClassDoc]]:
        """Extract documentation from a Python file"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            tree = ast.parse(content)
            functions = []
            classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Skip if it's a method inside a class (we'll handle those separately)
                    parent = self._get_parent_class(tree, node)
                    if parent is None:
                        func_doc = self._extract_function_doc(node, file_path, parent_class=None)
                        functions.append(func_doc)
                        
                elif isinstance(node, ast.ClassDef):
                    class_doc = self._extract_class_doc(node, file_path)
                    classes.append(class_doc)
                    
            return functions, classes
            
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return [], []
            
    def _get_parent_class(self, tree: ast.AST, node: ast.FunctionDef) -> Optional[ast.ClassDef]:
        """Find the parent class of a function node"""
        for potential_parent in ast.walk(tree):
            if isinstance(potential_parent, ast.ClassDef):
                for child in potential_parent.body:
                    if child == node:
                        return potential_parent
        return None
        
    def _extract_function_doc(self, node: ast.FunctionDef, file_path: Path, parent_class: Optional[ast.ClassDef]) -> FunctionDoc:
        """Extract documentation from a function node"""
        # Get function signature
        args = []
        for arg in node.args.args:
            arg_str = arg.arg
            # Add type annotation if available
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"
            args.append(arg_str)
            
        # Handle *args and **kwargs
        if node.args.vararg:
            args.append(f"*{node.args.vararg.arg}")
        if node.args.kwarg:
            args.append(f"**{node.args.kwarg.arg}")
            
        signature = f"{node.name}({', '.join(args)})"
        
        # Add return type if available
        if node.returns:
            signature += f" -> {ast.unparse(node.returns)}"
            
        # Get decorators
        decorators = [f"@{ast.unparse(d)}" for d in node.decorator_list]
        
        # Get docstring
        docstring = ast.get_docstring(node) or ""
        
        return FunctionDoc(
            name=node.name,
            signature=signature,
            docstring=docstring,
            file_path=str(file_path.relative_to(self.base_path)),
            line_number=node.lineno,
            decorators=decorators,
            is_method=parent_class is not None,
            class_name=parent_class.name if parent_class else ""
        )
        
    def _extract_class_doc(self, node: ast.ClassDef, file_path: Path) -> ClassDoc:
        """Extract documentation from a class node"""
        # Get class methods
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_doc = self._extract_function_doc(item, file_path, parent_class=node)
                methods.append(method_doc)
                
        # Get decorators
        decorators = [f"@{ast.unparse(d)}" for d in node.decorator_list]
        
        # Get docstring
        docstring = ast.get_docstring(node) or ""
        
        return ClassDoc(
            name=node.name,
            docstring=docstring,
            file_path=str(file_path.relative_to(self.base_path)),
            line_number=node.lineno,
            methods=methods,
            decorators=decorators
        )
        
    def extract_examples_from_tests(self, test_dir: Path):
        """Extract usage examples from test files"""
        if not test_dir.exists():
            return
            
        for test_file in test_dir.rglob("test_*.py"):
            try:
                with open(test_file, 'r') as f:
                    content = f.read()
                    
                # Extract function calls and their context
                # Look for patterns like: function_name(...) or module.function_name(...)
                pattern = r'(\w+(?:\.\w+)*)\s*\([^)]*\)'
                matches = re.findall(pattern, content)
                
                for match in matches:
                    func_name = match.split('.')[-1]
                    if func_name not in self.examples:
                        self.examples[func_name] = []
                        
                    # Extract the line containing the example
                    for line in content.split('\n'):
                        if match in line and line.strip():
                            self.examples[func_name].append(line.strip())
                            
            except Exception as e:
                print(f"Error extracting examples from {test_file}: {e}")
                
    def scan_directory(self, directory: Path, pattern: str = "*.py"):
        """Scan a directory for Python files and extract documentation"""
        for py_file in directory.rglob(pattern):
            # Skip test files and __pycache__
            if '__pycache__' in str(py_file) or 'test_' in py_file.name:
                continue
                
            functions, classes = self.extract_docs_from_file(py_file)
            
            # Group by module
            module_name = str(py_file.relative_to(self.base_path)).replace('/', '.').replace('.py', '')
            
            if functions:
                if module_name not in self.functions:
                    self.functions[module_name] = []
                self.functions[module_name].extend(functions)
                
            if classes:
                if module_name not in self.classes:
                    self.classes[module_name] = []
                self.classes[module_name].extend(classes)
                
    def generate_markdown(self) -> str:
        """Generate markdown documentation"""
        md_lines = ["# API Reference", ""]
        md_lines.append("This document provides a comprehensive API reference for all tools and utilities in the BlueLabelAutopilot orchestration system.")
        md_lines.append("")
        md_lines.append("## Table of Contents")
        md_lines.append("")
        
        # Generate TOC
        all_modules = sorted(set(list(self.functions.keys()) + list(self.classes.keys())))
        for module in all_modules:
            module_title = module.replace('_', ' ').title()
            anchor = module.replace('.', '-').lower()
            md_lines.append(f"- [{module_title}](#{anchor})")
            
        md_lines.append("")
        
        # Generate documentation for each module
        for module in all_modules:
            module_title = module.replace('_', ' ').title()
            anchor = module.replace('.', '-').lower()
            md_lines.append(f"## {module_title}")
            md_lines.append("")
            
            # Add module file path
            if module in self.functions and self.functions[module]:
                file_path = self.functions[module][0].file_path
                md_lines.append(f"**File**: `{file_path}`")
                md_lines.append("")
                
            # Document classes
            if module in self.classes:
                for class_doc in sorted(self.classes[module], key=lambda x: x.name):
                    md_lines.extend(self._format_class_doc(class_doc))
                    
            # Document standalone functions
            if module in self.functions:
                standalone_funcs = [f for f in self.functions[module] if not f.is_method]
                if standalone_funcs:
                    md_lines.append("### Functions")
                    md_lines.append("")
                    for func_doc in sorted(standalone_funcs, key=lambda x: x.name):
                        md_lines.extend(self._format_function_doc(func_doc))
                        
            md_lines.append("---")
            md_lines.append("")
            
        return '\n'.join(md_lines)
        
    def _format_class_doc(self, class_doc: ClassDoc) -> List[str]:
        """Format class documentation as markdown"""
        lines = []
        lines.append(f"### class {class_doc.name}")
        lines.append("")
        
        # Add decorators
        if class_doc.decorators:
            for decorator in class_doc.decorators:
                lines.append(f"`{decorator}`")
            lines.append("")
            
        # Add docstring
        if class_doc.docstring:
            lines.append(class_doc.docstring)
            lines.append("")
            
        # Add source location
        lines.append(f"*Source: {class_doc.file_path}:{class_doc.line_number}*")
        lines.append("")
        
        # Document methods
        if class_doc.methods:
            lines.append("#### Methods")
            lines.append("")
            for method in sorted(class_doc.methods, key=lambda x: x.name):
                lines.extend(self._format_function_doc(method, indent="##### "))
                
        return lines
        
    def _format_function_doc(self, func_doc: FunctionDoc, indent: str = "#### ") -> List[str]:
        """Format function documentation as markdown"""
        lines = []
        lines.append(f"{indent}{func_doc.signature}")
        lines.append("")
        
        # Add decorators
        if func_doc.decorators:
            for decorator in func_doc.decorators:
                lines.append(f"`{decorator}`")
            lines.append("")
            
        # Add docstring
        if func_doc.docstring:
            # Properly indent multi-line docstrings
            docstring_lines = func_doc.docstring.split('\n')
            for line in docstring_lines:
                lines.append(line)
            lines.append("")
            
        # Add examples if available
        if func_doc.name in self.examples and self.examples[func_doc.name]:
            lines.append("**Examples:**")
            lines.append("```python")
            # Show up to 3 unique examples
            unique_examples = list(set(self.examples[func_doc.name]))[:3]
            for example in unique_examples:
                lines.append(example)
            lines.append("```")
            lines.append("")
            
        # Add source location
        lines.append(f"*Source: {func_doc.file_path}:{func_doc.line_number}*")
        lines.append("")
        
        return lines
        
    def generate_tools_reference(self) -> str:
        """Generate specific reference for tools/ directory"""
        tools_dir = self.base_path / "tools"
        
        # Clear existing data
        self.functions.clear()
        self.classes.clear()
        
        # Scan tools directory
        self.scan_directory(tools_dir)
        
        # Extract examples from tests
        self.extract_examples_from_tests(self.base_path / "tests")
        
        # Generate markdown
        return self.generate_markdown()


def main():
    """CLI interface for API documentation generator"""
    parser = argparse.ArgumentParser(description="Generate API documentation from Python source files")
    parser.add_argument("--dir", default="tools", help="Directory to scan (default: tools)")
    parser.add_argument("--output", default="docs/api/API_REFERENCE.md", help="Output file path")
    parser.add_argument("--base-path", default="/Users/arielmuslera/Development/Projects/bluelabel-autopilot",
                       help="Base path for the project")
    
    args = parser.parse_args()
    
    # Create generator
    generator = APIDocGenerator(args.base_path)
    
    # Create output directory if needed
    output_path = Path(args.base_path) / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if args.dir == "tools":
        # Generate specific tools reference
        markdown = generator.generate_tools_reference()
    else:
        # Scan specified directory
        scan_dir = Path(args.base_path) / args.dir
        generator.scan_directory(scan_dir)
        generator.extract_examples_from_tests(Path(args.base_path) / "tests")
        markdown = generator.generate_markdown()
        
    # Write output
    with open(output_path, 'w') as f:
        f.write(markdown)
        
    print(f"✅ API documentation generated: {output_path}")
    print(f"📊 Documented {sum(len(funcs) for funcs in generator.functions.values())} functions")
    print(f"📦 Documented {sum(len(classes) for classes in generator.classes.values())} classes")


if __name__ == "__main__":
    main()