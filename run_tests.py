import unittest
import coverage
import webbrowser
import os

def run_all_tests():
    # Start coverage collection
    cov = coverage.Coverage()
    cov.start()

    # Discover and run all tests in tests/ folder
    loader = unittest.TestLoader()
    suite = loader.discover('tests')

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Stop coverage and save report
    cov.stop()
    cov.save()

    # Generate HTML coverage report
    cov.html_report(directory='htmlcov')
    index_path = os.path.abspath('htmlcov/index.html')

    print(f"\nCoverage report generated at: {index_path}")

    # Open coverage report in default browser
    webbrowser.open(f'file://{index_path}')

if __name__ == "__main__":
    run_all_tests()