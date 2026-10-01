import sys
import argparse
from core.sandbox import ExecutionSandbox
from core.llm_provider import LLMProvider
from pipelines.app_generator.architect import AppArchitectAgent
from pipelines.app_generator.scaffolder import AppScaffolderAgent
from pipelines.app_generator.validator import AppValidatorAgent

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def main():
    parser = argparse.ArgumentParser(description="Run Full-Stack App Generator Pipeline")
    parser.add_argument("--spec", type=str, default="Lightweight IoT sensor telemetry API with SQLite and Dockerfile", help="App brief")
    parser.add_argument("--output", type=str, default="./workspace/generated_app", help="Output directory")
    args = parser.parse_args()

    print(f"\n==================================================")
    print(f"[PIPELINE 3] FULL-STACK APP GENERATOR")
    print(f"Spec: {args.spec}")
    print(f"Target Output: {args.output}")
    print(f"==================================================\n")

    sandbox = ExecutionSandbox(local_workspace=args.output)
    llm = LLMProvider()

    print("[Step 1/3] 📐 Designing system architecture, OpenAPI & schemas...")
    architect = AppArchitectAgent(llm)
    arch_spec = architect.design_architecture(args.spec)
    print(f"App: {arch_spec.get('app_name')} | Stack: {arch_spec.get('stack')}")

    print("\n[Step 2/3] 🏗️ Scaffolding full-stack application source tree...")
    scaffolder = AppScaffolderAgent(llm)
    files = scaffolder.scaffold_application(arch_spec)
    for path, code in files.items():
        print(f" -> Generated: {path}")
        sandbox.write_file(path, code)

    print("\n[Step 3/3] 🔬 Validating syntax and test harnesses...")
    validator = AppValidatorAgent(sandbox)
    val_res = validator.validate_scaffold()
    print(f"Compilation Check: {val_res['syntax_check']['passed']}")
    print(f"Unit Tests Check:  {val_res['tests_check']['passed']}")
    print(f"\n✅ Full-Stack Microservice Generated Successfully at: {args.output}!\n")

if __name__ == "__main__":
    main()
