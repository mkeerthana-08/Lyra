import ast


def detect_strategy_pattern(tree: ast.AST, nested_depth: int):
    strategies = []
    has_nested_loops = nested_depth >= 2
    func_names = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    has_recursion = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in func_names:
            has_recursion = True
            break
    uses_dictionary = any(isinstance(n, ast.Dict) for n in ast.walk(tree))
    uses_set = any(isinstance(n, ast.Set) for n in ast.walk(tree))
    uses_sort = any(isinstance(n, ast.Call) and getattr(getattr(n, 'func', None), 'attr', '') == 'sort' for n in ast.walk(tree))

    if has_nested_loops:
        strategies.append("🧠 Brute Force pattern detected (nested iteration)")
    if has_recursion:
        strategies.append("🔁 Recursive strategy detected")
    if uses_dictionary or uses_set:
        strategies.append("📦 Hash-based optimization pattern detected")
    if uses_sort:
        strategies.append("↕️ Sorting utilized")
    if not strategies:
        strategies.append("📈 Linear / simple iteration strategy")
    return strategies
