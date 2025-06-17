def run_all_tests():
    cov = coverage.Coverage()
    cov.start()

    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')
    print(f"Discovered {suite.countTestCases()} tests.")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    cov.stop()
    cov.save()
    cov.html_report(directory='htmlcov')
    webbrowser.open(f'file://{os.path.abspath("htmlcov/index.html")}')