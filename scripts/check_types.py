#!/usr/bin/env python3
"""Script to check type hints coverage in the codebase."""

import ast
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Set


def check_function_type_hints(node: ast.FunctionDef) -> Tuple[bool, List[str]]:
    """Check if a function has type hints for all parameters and return type."""
    issues = []
    
    # Check parameters
    for arg in node.args.args:
        if arg.arg != 'self' and arg.arg != 'cls' and arg.annotation is None:
            issues.append(f"Parameter '{arg.arg}' missing type hint")
    
    # Check return type (except for __init__)
    if node.name != '__init__' and node.returns is None:
        # Check if it's a property or has decorators that might affect return
        decorator_names = [d.id if isinstance(d, ast.Name) else 
                          (d.attr if isinstance(d, ast.Attribute) else None) 
                          for d in node.decorator_list]
        
        if 'property' not in decorator_names:
            issues.append("Missing return type hint")
    
    return len(issues) == 0, issues


def analyze_file(file_path: Path) -> Dict[str, List[str]]:
    """Analyze a Python file for missing type hints."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                # Skip test functions and private functions
                if node.name.startswith('test_') or node.name.startswith('_'):
                    continue
                    
                has_hints, func_issues = check_function_type_hints(node)
                if not has_hints:
                    for issue in func_issues:
                        issues.append(f"Line {node.lineno}, {node.name}(): {issue}")
        
        return {str(file_path): issues} if issues else {}
        
    except SyntaxError as e:
        return {str(file_path): [f"Syntax error in file: {e}"]}
    except (IOError, OSError) as e:
        return {str(file_path): [f"Error reading file: {e}"]}
    except Exception as e:
        # Log unexpected errors but don't mask them
        return {str(file_path): [f"Unexpected error analyzing file: {type(e).__name__}: {e}"]}


def main():
    """Main function to check type hints across the codebase."""
    src_path = Path(__file__).parent.parent / "src"
    
    if not src_path.exists():
        print(f"Source directory not found: {src_path}")
        sys.exit(1)
    
    all_issues = {}
    total_files = 0
    files_with_issues = 0
    
    # Find all Python files
    python_files = list(src_path.rglob("*.py"))
    
    for file_path in python_files:
        # Skip __pycache__ and test files
        if "__pycache__" in str(file_path) or "test_" in file_path.name:
            continue
            
        total_files += 1
        issues = analyze_file(file_path)
        
        if issues:
            files_with_issues += 1
            all_issues.update(issues)
    
    # Report results
    if all_issues:
        print("Type hint issues found:\n")
        for file_path, issues in sorted(all_issues.items()):
            print(f"\n{file_path}:")
            for issue in issues:
                print(f"  - {issue}")
        
        print(f"\n\nSummary: {files_with_issues}/{total_files} files have missing type hints")
        sys.exit(1)
    else:
        print(f"✓ All {total_files} files have proper type hints!")
        sys.exit(0)


if __name__ == "__main__":
    main()