import ast
from executor.code_runner import run_python_code
from .complexity_engine import get_cyclomatic_complexity, get_nested_loop_depth
from .risk_engine import detect_risk_patterns, detect_edge_case_issues
from .strategy_engine import detect_strategy_pattern
from .alignment_engine import analyze_problem_alignment, generate_optimization_suggestions
from .generic_engine import estimate_time_complexity, estimate_space_complexity, count_nested_loops_text, check_basic_syntax


def analyze_all(code: str, problem_statement: str = "", language: str = "python"):
    result = {}
    execution_result = {}

    if (language or "").lower() == "python":
        tree = ast.parse(code)
        complexity = get_cyclomatic_complexity(code)
        nested = get_nested_loop_depth(tree)
        risks = detect_risk_patterns(tree, complexity, nested)
        edges = detect_edge_case_issues(tree)
        strategy = detect_strategy_pattern(tree, nested)
        alignment = analyze_problem_alignment(problem_statement, strategy)
        suggestions = generate_optimization_suggestions(tree, complexity, nested, strategy)
        execution_result = run_python_code(code)
    else:
        # Generic fallback for non-Python languages
        complexity = []
        nested = count_nested_loops_text(code)
        risks = check_basic_syntax(code, language)
        edges = []
        strategy = ["📈 Linear / simple iteration strategy"]
        alignment = analyze_problem_alignment(problem_statement, strategy)
        suggestions = generate_optimization_suggestions(None, complexity, nested, strategy)

    # Language-agnostic time/space complexity estimation
    time_label, time_class, time_notes = estimate_time_complexity(code)
    space_label, space_class, space_notes = estimate_space_complexity(code, language)

    result.update({
        "complexity": complexity,
        "nested_loops": nested,
        "risks": risks,
        "edge_cases": edges,
        "strategy": strategy,
        "alignment_insights": alignment,
        "optimization_suggestions": suggestions,
        "time_complexity": time_label,
        "time_class": time_class,
        "time_notes": time_notes,
        "space_complexity": space_label,
        "space_class": space_class,
        "space_notes": space_notes,
    })

    result["execution"] = execution_result

    return result
