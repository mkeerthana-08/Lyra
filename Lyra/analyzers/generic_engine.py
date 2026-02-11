import ast
import re


LOOP_TOKENS = [r"\bfor\b", r"\bwhile\b", r"\bforeach\b"]
SORT_TOKENS = [r"\bsort\s*\(", r"std::sort", r"Collections\.sort", r"Arrays\.sort"]
DS_TOKENS = [
    r"std::vector", r"std::map", r"std::unordered_map", r"std::set", r"std::unordered_set",
    r"HashMap", r"HashSet", r"ArrayList", r"List<", r"Map<",
    r"\bdict\b", r"\bset\s*\(", r"\blist\s*\(", r"\{\s*\}"  # empty dicts
]


CONTROL_KEYWORDS = {"if", "else", "for", "while", "switch", "case", "do", "try", "catch", "finally"}


def check_basic_syntax(code: str, language: str = ""):
    """Lightweight heuristic syntax checks for C/CPP/Java/JS-like languages."""
    issues = []
    brace = paren = bracket = 0
    in_block_comment = False

    lines = code.splitlines()
    for idx, raw in enumerate(lines, start=1):
        line = raw.strip()

        # look ahead to skip headers that put '{' on the next line
        next_meaningful = ""
        for j in range(idx, len(lines)):
            candidate = lines[j].strip()
            if not candidate or candidate.startswith("//"):
                continue
            next_meaningful = candidate
            break
        if not line:
            continue

        # crude block comment handling
        if in_block_comment:
            if "*/" in line:
                in_block_comment = False
            continue
        if line.startswith("/*") and "*/" not in line:
            in_block_comment = True
            continue

        # balance tracking
        brace += line.count("{") - line.count("}")
        paren += line.count("(") - line.count(")")
        bracket += line.count("[") - line.count("]")

        if brace < 0:
            issues.append(f"Line {idx}: Extra closing brace '}}'.")
            brace = 0
        if paren < 0:
            issues.append(f"Line {idx}: Extra closing parenthesis ')'.")
            paren = 0
        if bracket < 0:
            issues.append(f"Line {idx}: Extra closing bracket ']'.")
            bracket = 0

        # missing semicolon heuristic for statement lines
        if language.lower() in {"c", "cpp", "c++", "java", "js", "javascript"}:
            if line.endswith((";", "{", "}", ":")):
                continue
            token = line.split()[0] if line.split() else ""
            if token in CONTROL_KEYWORDS:
                continue
            # lines like function declarations / definitions can end with )
            if line.endswith(")") and ("(" in line and "{" in line):
                continue
            if line.endswith(")") and next_meaningful.startswith("{"):
                continue
            # preprocessor or labels
            if line.startswith("#") or line.endswith(":"):
                continue
            issues.append(f"Line {idx}: Possible missing semicolon.")

    if brace != 0:
        issues.append("Unbalanced braces '{ }'.")
    if paren != 0:
        issues.append("Unbalanced parentheses '( )'.")
    if bracket != 0:
        issues.append("Unbalanced brackets '[ ]'.")

    return issues


def count_nested_loops_text(code: str):
    depth = 0
    max_depth = 0
    brace_stack = []
    for line in code.splitlines():
        l = line.strip()
        if any(re.search(tok, l) for tok in LOOP_TOKENS):
            depth += 1
            max_depth = max(max_depth, depth)
            brace_stack.append('{')
        # crude closing detection
        closes = l.count('}') + len(re.findall(r"\bend\b", l))
        for _ in range(closes):
            if brace_stack:
                brace_stack.pop()
                depth = max(0, depth - 1)
    return max_depth


def _has_recursion_text(code: str):
    # heuristic: function name appears calling itself
    func_defs = re.findall(r"(\w+)\s*\([^)]*\)\s*\{", code)
    for name in set(func_defs):
        if re.search(rf"\b{name}\s*\(", code.split('{', 1)[-1]):
            return True
    return False


def estimate_time_complexity(code: str):
    depth = count_nested_loops_text(code)
    has_sort = any(re.search(tok, code) for tok in SORT_TOKENS)
    has_rec = _has_recursion_text(code)

    label = "O(1)"
    klass = "complexity-o1"
    notes = []

    if has_sort:
        label = "O(n log n)"
        klass = "complexity-onlogn"
        notes.append("Sorting detected; typical O(n log n).")

    if depth >= 3:
        label = "O(n^3)"
        klass = "complexity-on3"
        notes.append("Triple-nested loops detected.")
    elif depth == 2:
        label = "O(n^2)"
        klass = "complexity-on2"
        notes.append("Double-nested loops detected.")
    elif depth == 1 or has_rec:
        if not has_sort:
            label = "O(n)"
            klass = "complexity-on"
            notes.append("Single loop or recursion detected.")

    return label, klass, notes


def _estimate_space_python(code: str):
    # AST-based detection to avoid undercounting list/dict/set usage
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None

    dynamic_alloc = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.List, ast.Dict, ast.Set, ast.ListComp, ast.SetComp, ast.DictComp)):
            dynamic_alloc += 1
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in {"append", "extend", "insert", "add", "update"}:
                dynamic_alloc += 1

    label = "O(1)"
    klass = "complexity-o1"
    notes = []
    if dynamic_alloc >= 2:
        label = "O(n)"
        klass = "complexity-on"
        notes.append("Multiple dynamic collections or growth operations detected (likely O(n) space).")
    elif dynamic_alloc == 1:
        label = "O(n)"
        klass = "complexity-on"
        notes.append("Dynamic collection detected; may grow with input size.")
    return label, klass, notes


def estimate_space_complexity(code: str, language: str = ""):
    lang = (language or "").lower()
    if lang == "python":
        python_estimate = _estimate_space_python(code)
        if python_estimate:
            return python_estimate

    ds_hits = sum(1 for tok in DS_TOKENS if re.search(tok, code))
    label = "O(1)"
    klass = "complexity-o1"
    notes = []
    if ds_hits >= 2:
        label = "O(n)"
        klass = "complexity-on"
        notes.append("Multiple dynamic data structures detected (likely O(n) space).")
    elif ds_hits == 1:
        label = "O(n)"
        klass = "complexity-on"
        notes.append("Data structure detected; may grow with input size.")
    return label, klass, notes
