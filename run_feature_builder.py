import sys
import argparse
from core.sandbox import ExecutionSandbox
from core.llm_provider import LLMProvider
from pipelines.feature_builder.planner import FeaturePlannerAgent
from pipelines.feature_builder.coder import FeatureCoderAgent
from pipelines.feature_builder.tester import FeatureTesterAgent
from pipelines.feature_builder.reviewer import FeatureReviewerAgent

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def main():
    parser = argparse.ArgumentParser(description="Run Feature Builder Pipeline")
    parser.add_argument("--spec", type=str, default="Add metrics aggregation function with empty list safeguard", help="Feature description")
    parser.add_argument("--docker", action="store_true", help="Run inside Docker sandbox")
    args = parser.parse_args()

    print(f"\n==================================================")
    print(f"[PIPELINE 1] FEATURE BUILDER")

    print(f"Spec: {args.spec}")
    print(f"Sandbox Mode: {'Docker' if args.docker else 'Local Process'}")
    print(f"==================================================\n")

    sandbox = ExecutionSandbox(use_docker=args.docker, local_workspace="./workspace")
    llm = LLMProvider()

    print("[Step 1/4] 🧠 Planning architecture...")
    planner = FeaturePlannerAgent(llm)
    plan = planner.plan_feature(args.spec)
    print(f"Plan Generated: {plan.get('feature_name')} ({plan.get('architecture_summary')})")

    print("\n[Step 2/4] 💻 Generating code & test suites...")
    coder = FeatureCoderAgent(llm)
    files = coder.generate_code(plan)
    for path, code in files.items():
        print(f" -> Writing file: {path}")
        sandbox.write_file(path, code)

    print("\n[Step 3/4] 🧪 Executing automated test suite in sandbox...")
    tester = FeatureTesterAgent(sandbox)
    test_result = tester.run_tests()
    print(f"Tests Passed: {test_result['passed']}")
    if not test_result['passed']:
        print(f"Errors:\n{test_result['stderr']}")

    print("\n[Step 4/4] 🔍 Generating PR summary & review notes...")
    reviewer = FeatureReviewerAgent(llm)
    pr_notes = reviewer.generate_pr_summary(plan, files, test_result)
    print(f"\n--- PULL REQUEST SUMMARY ---\n{pr_notes}\n")
    print("✅ Feature Builder Pipeline Finished Successfully!\n")

if __name__ == "__main__":
    main()
