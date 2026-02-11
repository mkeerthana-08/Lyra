import ast


def detect_risk_patterns(tree: ast.AST, complexity_list, nested_depth):
    risks = []
    for name, complexity in complexity_list:
        if complexity > 5:
            risks.append(f"⚠️ High complexity in function '{name}' (Complexity: {complexity})")
    if nested_depth >= 2:
        risks.append(f"⚠️ Deep nested loops detected (Depth: {nested_depth})")
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if len(node.body) > 20:
                risks.append(f"⚠️ Large function '{node.name}' may reduce readability")
    return risks


def detect_edge_case_issues(tree: ast.AST):
    issues = []
    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            issues.append("⚠️ Possible division operation detected (check for zero division)")
        if isinstance(node, ast.FunctionDef):
            has_if = any(isinstance(child, ast.If) for child in node.body)
            if not has_if:
                issues.append(f"⚠️ Function '{node.name}' has no input validation")
        if isinstance(node, ast.Subscript):
            issues.append("⚠️ Direct indexing detected (ensure bounds checking)")
    return list(set(issues))
