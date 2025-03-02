from math import gcd
import re
from typing import Any


# TODO: list of dicts syntax


def parse(file_name: str) -> dict | list:
    with open(file_name) as f:
        lines = [
            l.replace("\n", "")
            for l in f.readlines()
            if not (l.startswith("#") or l.isspace())
        ]

        document_indentation = gcd(*[indentation(l) for l in lines])

        tree = build_tree(lines, document_indentation)

        print("------")
        print(tree)

        return serialize(tree)


def build_tree(lines: list[str], indent: int) -> list:
    # Assumes the root object is not a list???
    # TODO: account for array items
    # TODO: don't allow for mixed key-value pairs and array elements
    # TODO: validate string quotes
    base_indent = indentation(lines[0] if lines else "")
    layer = []
    for i, line in enumerate(lines):
        if is_nested(line, base_indent):
            continue

        if is_inline(line):
            layer.append(line)
        else:
            layer.append(
                {line: build_tree(lines[i + 1 : find_next_block_end(lines)], indent)}
            )

    return layer


def is_nested(line: str, indent: int) -> bool:
    return indentation(line) > indent


def is_inline(line) -> bool:
    return re.search(r"(:\s?\S+$)|(^\s*-)", line) is not None


def find_next_block_end(lines: list[str]) -> int:
    base = indentation(lines[0])
    for i, line in enumerate(lines[1:], 1):
        if indentation(line) < base:
            return i

    return len(lines)


def indentation(line: str) -> int:
    return len(re.search(r"^\s*", line).group())  # type: ignore


def serialize(tree: list[str | dict]) -> dict[str, Any] | list:
    if any(b.strip().startswith("-") for b in tree if type(b) == str):
        return serialize_list(tree)

    obj = {}

    for branch in tree:
        # inline value
        if type(branch) == str:
            key = re.search(r"(?!^\s)\w+(?=:)", branch).group()  # type: ignore
            value = re.search(r'(?!:\s?)[\w|"|\']+$', branch).group()  # type: ignore
            obj[key] = value
        elif type(branch) == dict:
            k, v = list(branch.items())[0]
            print("[dict]", k, v)
            obj[k] = serialize(v)

    return obj


def serialize_list(tree: list[str | dict]) -> list[Any]:
    arr = []
    for branch in tree:
        if type(branch) == str:
            arr.append(branch.strip()[2:])
        elif type(branch) == dict:
            print("TODO: dict array ->", branch)
            # arr.append(serialize(branch))

    return arr
