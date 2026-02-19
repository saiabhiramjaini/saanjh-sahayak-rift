from src.services.test_runner import TestRunner

runner = TestRunner()

def run_ci(repo_url: str, session_id: str):
    response = runner.run_tests(
        repo_url=repo_url,
        session_id=session_id,
        language="python"
    )
    return response
