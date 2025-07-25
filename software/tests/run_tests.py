#!/usr/bin/env python3
"""
Test runner script for the game show application.

This script provides an easy way to run different types of tests
and generate coverage reports.
"""

import sys
import subprocess
import argparse


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    try:
        subprocess.run(cmd, check=True, capture_output=False)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run tests for the game show application")
    parser.add_argument(
        "--type", 
        choices=["unit", "integration", "gui", "hardware", "all"],
        default="unit",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true",
        help="Generate coverage report"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--parallel", "-n",
        type=int,
        default=1,
        help="Number of parallel processes"
    )
    parser.add_argument(
        "--no-cov",
        action="store_true",
        help="Disable coverage reporting (useful when coverage is enabled by default)"
    )
    
    args = parser.parse_args()
    
    # Base pytest command using the current Python executable
    base_cmd = [sys.executable, "-m", "pytest"]
    
    if args.verbose:
        base_cmd.append("-v")
    
    # Handle coverage options
    if args.coverage and not args.no_cov:
        base_cmd.extend([
            "--cov=.",
            "--cov-report=html",
            "--cov-report=term-missing"
        ])
    elif args.no_cov:
        # Explicitly disable coverage if requested
        base_cmd.extend(["--no-cov"])
    
    if args.parallel > 1:
        base_cmd.extend(["-n", str(args.parallel)])
    
    # Determine test path based on type
    if args.type == "all":
        test_path = "tests/"
    else:
        test_path = f"tests/{args.type}/"
    
    base_cmd.append(test_path)
    
    # Run tests
    success = run_command(base_cmd, f"{args.type.title()} tests")
    
    if success:
        print(f"\n🎉 All {args.type} tests passed!")
        if args.coverage and not args.no_cov:
            print("📊 Coverage report generated in htmlcov/")
            print("   Open htmlcov/index.html to view the report")
    else:
        print(f"\n💥 Some {args.type} tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main() 