"""Aho-Corasick Multi-Pattern Matcher Engine.
100% Python Standard Library.
"""

from collections import deque
from typing import Dict, List, Any, Optional, Tuple

class AhoCorasickNode:
    def __init__(self):
        self.children: Dict[str, "AhoCorasickNode"] = {}
        self.fail: Optional["AhoCorasickNode"] = None
        self.outputs: List[Tuple[str, Any]] = []

class AhoCorasickMatcher:
    """Deterministic Finite Automaton for simultaneous linear-time multi-pattern matching."""

    def __init__(self):
        self.root = AhoCorasickNode()
        self._is_built = False
        self._pattern_count = 0

    def add_keyword(self, keyword: str, metadata: Any = None):
        if not keyword:
            return
        curr = self.root
        for char in keyword:
            if char not in curr.children:
                curr.children[char] = AhoCorasickNode()
            curr = curr.children[char]
        curr.outputs.append((keyword, metadata))
        self._pattern_count += 1
        self._is_built = False

    def build(self):
        queue = deque()
        for char, child in self.root.children.items():
            child.fail = self.root
            queue.append(child)

        while queue:
            curr = queue.popleft()
            for char, child in curr.children.items():
                fail_state = curr.fail
                while fail_state and char not in fail_state.children:
                    fail_state = fail_state.fail
                child.fail = fail_state.children[char] if fail_state else self.root
                child.outputs.extend(child.fail.outputs)
                queue.append(child)
        self._is_built = True

    def search(self, text: str) -> List[Dict[str, Any]]:
        if not self._is_built:
            self.build()
        matches = []
        curr = self.root
        for i, char in enumerate(text):
            while curr and char not in curr.children:
                curr = curr.fail
            curr = curr.children[char] if curr else self.root
            if curr.outputs:
                for kw, meta in curr.outputs:
                    matches.append({
                        "keyword": kw,
                        "start": i - len(kw) + 1,
                        "end": i + 1,
                        "metadata": meta
                    })
        return matches

    def redact(self, text: str, replacement: str = "***") -> str:
        matches = self.search(text)
        if not matches:
            return text
        intervals = sorted([(m["start"], m["end"]) for m in matches], key=lambda x: (x[0], -x[1]))
        merged = []
        for start, end in intervals:
            if not merged:
                merged.append([start, end])
            else:
                last_start, last_end = merged[-1]
                if start <= last_end:
                    merged[-1][1] = max(last_end, end)
                else:
                    merged.append([start, end])

        res = []
        last_idx = 0
        for start, end in merged:
            res.append(text[last_idx:start])
            res.append(replacement)
            last_idx = end
        res.append(text[last_idx:])
        return "".join(res)
