from complexity_analyzer import ComplexityAnalyzer


def load_code(path):
    with open(path, "r") as file:
        return file.read()


def main():
    print("\n🌌 LYRA ANALYSIS REPORT")
    print("-" * 40)

    code = load_code("sample_codes/example1.py")

    analyzer = ComplexityAnalyzer(code)
    result = analyzer.analyze()

    print("\n📊 Cyclomatic Complexity:")
    for name, complexity in result["complexity"]:
        print(f"{name} → {complexity}")

    print(f"\n🔁 Nested Loop Depth: {result['nested_loops']}")

    print("\n🚨 Risk Analysis:")
    if result["risks"]:
        for risk in result["risks"]:
            print(risk)
    else:
        print("✅ No major risk patterns detected.")

    print("\n🧪 Edge Case Analysis:")
    if result["edge_cases"]:
        for issue in result["edge_cases"]:
            print(issue)
    else:
        print("✅ No obvious edge case risks detected.")


if __name__ == "__main__":
    main()
