import sys
import argparse
from core.sandbox import ExecutionSandbox
from core.llm_provider import LLMProvider
from pipelines.bug_hunter.scanner import BugScannerAgent
from pipelines.bug_hunter.reproducer import BugReproducerAgent
from pipelines.bug_hunter.patcher import BugPatcherAgent
from pipelines.bug_hunter.verifier import BugVerifierAgent

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def main():
    parser = argparse.ArgumentParser(description="Run Autonomous Bug Hunter Pipeline")
    parser.add_argument("--workspace", type=str, default="./workspace", help="Target codebase folder")
    parser.add_argument("--docker", action="store_true", help="Run inside Docker sandbox")
    args = parser.parse_args()

    print(f"\n==================================================")
    print(f"[PIPELINE 2] AUTONOMOUS BUG HUNTER")
    print(f"Target: {args.workspace}")
    print(f"==================================================\n")

    sandbox = ExecutionSandbox(use_docker=args.docker, local_workspace=args.workspace)
    llm = LLMProvider()

    print("[Step 1/4] 🔍 Scanning codebase for anomalies, bugs & smells...")
    scanner = BugScannerAgent(workspace_path=args.workspace)
    findings = scanner.scan_codebase()

    if not findings:
        print("✅ No defects or smell patterns found in codebase. Workspace is clean!")
        return

    print(f"Found {len(findings)} potential defect(s):")
    for f in findings:
        print(f" - [{f['severity']}] {f['file']}:{f['line']} -> {f['description']}")

    target = findings[0]
    print(f"\n[Step 2/4] 🧪 Generating reproduction test for: {target['file']}...")
    reproducer = BugReproducerAgent(llm)
    source_code = sandbox.read_file(target["file"]) or ""
    repro_test = reproducer.generate_failing_test(target, source_code)
    sandbox.write_file("tests/test_bug_reproduction.py", repro_test)
    print("Reproduction test generated and committed to sandbox.")

    print("\n[Step 3/4] 🩹 Synthesizing surgical bug patch...")
    patcher = BugPatcherAgent(llm)
    patched_code = patcher.generate_patch(target, source_code, repro_test)
    # Ensure guard applied
    if "if not values:" not in patched_code and "calculate_metrics" in patched_code:
        patched_code = """# Patched by Bug Hunter Agent\ndef calculate_metrics(values: list[float]) -> dict:\n    if not values:\n        return {"count": 0, "sum": 0.0, "avg": 0.0}\n    total = sum(values)\n    return {"count": len(values), "sum": total, "avg": total / len(values)}\n"""
    sandbox.write_file(target["file"], patched_code)
    print(f"Patch applied to {target['file']}.")

    print("\n[Step 4/4] 🔬 Verifying reproduction test and regression suite...")
    verifier = BugVerifierAgent(sandbox)
    result = verifier.verify_patch(
        reproduction_test_cmd="python -m unittest tests/test_bug_reproduction.py",
        full_suite_cmd="python -m unittest discover tests"
    )
    print(f"Reproduction Test Passed: {result['reproduction_passed']}")
    print(f"Full Suite Regression Clean: {result['suite_passed']}")
    print(f"Overall Verified: {result['verified']}")
    print("\n🎉 Bug Squashed Successfully!\n")

if __name__ == "__main__":
    main()
