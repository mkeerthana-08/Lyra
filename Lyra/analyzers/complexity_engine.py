import ast
from radon.complexity import cc_visit


def get_cyclomatic_complexity(code: str):
    results = cc_visit(code)
    return [(block.name, block.complexity) for block in results]


def get_nested_loop_depth(tree: ast.AST):
    max_depth = 0

    def visit(node, depth=0):
        nonlocal max_depth
        if isinstance(node, (ast.For, ast.While)):
            depth += 1
            max_depth = max(max_depth, depth)
        for child in ast.iter_child_nodes(node):
            visit(child, depth)

    visit(tree)
    return max_depth
