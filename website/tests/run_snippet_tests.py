#!/usr/bin/env python
"""
Test runner script specifically for snippet moderation workflow tests.

This script runs all the snippet-related tests and provides a summary
of the test coverage for the draft and moderation workflow functionality.
"""

import subprocess
import sys
import os


def run_snippet_tests():
    """Run all snippet workflow tests and display results."""

    print("=" * 80)
    print("SNIPPET DRAFT & MODERATION WORKFLOW TESTS")
    print("=" * 80)
    print()

    # Test files to run
    test_files = [
        "tests/test_snippet_moderation_core.py",
        "tests/test_snippet_workflow_scenarios.py",
        "tests/test_snippet_admin_integration.py",
    ]

    # Build pytest command
    cmd = [
        "pytest",
        "-v",
        "--tb=short",
        "--no-header",
        "--disable-warnings",
    ] + test_files

    print("Running snippet workflow tests...")
    print("Test files:")
    for test_file in test_files:
        print(f"  - {test_file}")
    print()

    # Run tests
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())

        # Display results
        print("TEST RESULTS:")
        print("=" * 40)
        print(result.stdout)

        if result.stderr:
            print("STDERR:")
            print(result.stderr)

        # Summary
        if result.returncode == 0:
            print("✅ ALL SNIPPET WORKFLOW TESTS PASSED!")
            print()
            print("The following functionality has been verified:")
            print("• Draft creation and management for all snippet types")
            print("• Moderation workflow (submit/approve/reject)")
            print("• Scheduled publishing and expiry")
            print("• Revision tracking capabilities")
            print("• Admin panel integration with PublishingPanel")
            print("• Real-world administrator scenarios")
            print("• Judge profile language review workflow")
            print("• Multi-snippet independence")
            return True
        else:
            print("❌ SOME TESTS FAILED")
            print(f"Exit code: {result.returncode}")
            return False

    except FileNotFoundError:
        print(
            "❌ ERROR: pytest not found. Make sure you're in the virtual environment."
        )
        print("Run: source ../.venv/bin/activate")
        return False
    except Exception as e:
        print(f"❌ ERROR running tests: {e}")
        return False


if __name__ == "__main__":
    success = run_snippet_tests()
    sys.exit(0 if success else 1)
