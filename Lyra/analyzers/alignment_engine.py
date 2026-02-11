import ast


def _recursive_functions(tree: ast.AST):
    funcs = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            name = node.name
            calls_self = any(isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id == name for c in ast.walk(node))
            if calls_self:
                funcs.append(node)
    return funcs


def _has_base_case(func_node):
    for node in func_node.body:
        if hasattr(node, 'body') and any(isinstance(n, ast.Return) for n in ast.walk(node)):
            return True
    return False


def analyze_problem_alignment(problem_statement: str, strategy_list):
    insights = []
    text = (problem_statement or "").lower()
    wants_efficiency = any(k in text for k in ["efficient", "optimize", "performance", "large input", "scalable", "time complexity"])
    mentions_recursion = "recurs" in text
    memory_focus = any(k in text for k in ["memory", "space", "low memory", "optimize space"]) 

    has_bruteforce = any("Brute Force" in s for s in strategy_list)
    has_recursion = any("Recursive" in s for s in strategy_list)
    uses_hash = any("Hash" in s for s in strategy_list)

    if wants_efficiency and has_bruteforce:
        insights.append("❗ Problem emphasizes efficiency, but code appears brute-force. Consider algorithmic optimization.")
    elif wants_efficiency and not has_bruteforce:
        insights.append("✅ Efficiency requested; current strategy avoids deep nesting.")

    if mentions_recursion:
        if has_recursion:
            insights.append("✅ Recursion requested and detected.")
        else:
            insights.append("ℹ️ Problem mentions recursion, but code is iterative.")

    if memory_focus:
        if uses_hash:
            insights.append("ℹ️ Hash-based structures used; check memory trade-offs.")
        else:
            insights.append("✅ Memory focus noted; minimal heavy structures detected.")

    if not insights:
        insights.append("ℹ️ No specific alignment cues detected from problem statement.")
    return insights


def generate_optimization_suggestions(tree: ast.AST, complexity_list, nested_depth, strategy_list):
    suggestions = []
    if nested_depth >= 2:
        suggestions.append("Use dictionary/set for O(1) lookups to avoid nested loops.")
        suggestions.append("Pre-index or pre-sort inputs to reduce inner loop scanning.")
    high_complex = [(n, c) for (n, c) in complexity_list if c > 5]
    if high_complex:
        suggestions.append("Refactor high-complexity functions into smaller helpers with clear responsibilities.")
        suggestions.append("Apply guard clauses to reduce branching depth.")
    if tree is not None:
        for f in _recursive_functions(tree):
            if not _has_base_case(f):
                suggestions.append(f"Add explicit base-case checks in recursive function '{f.name}'.")
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
                suggestions.append("Guard against division-by-zero before division operations.")
                break
    if not suggestions:
        suggestions.append("Code appears straightforward; consider input validation and early exits for performance.")
    return list(dict.fromkeys(suggestions))


def compute_quality_score(complexity_list, nested_depth, risks, alignment_insights):
    score = 100
    if complexity_list:
        avg_complex = sum(c for (_, c) in complexity_list) / max(1, len(complexity_list))
        score -= min(40, avg_complex * 4)
        high_count = sum(1 for (_, c) in complexity_list if c > 5)
        score -= min(20, high_count * 6)
    score -= min(20, max(0, (nested_depth - 1) * 8))
    score -= min(25, len(risks) * 5)
    misalign_penalty = sum(6 for i in alignment_insights if i.startswith("❗"))
    score -= min(18, misalign_penalty)
    score = max(0, min(100, round(score)))
    return score
