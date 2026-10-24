"""MCP Server for GenPark Aho-Corasick Multi-Pattern Matcher.
100% Python Standard Library.
"""

import json
import sys
from client import AhoCorasickMatcher

matcher = AhoCorasickMatcher()

def handle_request(req):
    method = req.get("method")
    params = req.get("params", {})
    req_id = req.get("id")

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "add_keywords",
                        "description": "Add keywords or forbidden terms to the Aho-Corasick dictionary",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "keywords": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of keywords to index"
                                }
                            },
                            "required": ["keywords"]
                        }
                    },
                    {
                        "name": "search_patterns",
                        "description": "Search text simultaneously for all indexed keywords in O(n) time",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "text": {"type": "string", "description": "Target string to scan"}
                            },
                            "required": ["text"]
                        }
                    },
                    {
                        "name": "redact_patterns",
                        "description": "Redact matched keywords from text using a replacement string",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "text": {"type": "string", "description": "Target string to redact"},
                                "replacement": {"type": "string", "description": "Masking string, default '***'"}
                            },
                            "required": ["text"]
                        }
                    }
                ]
            }
        }
    elif method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {})
        if name == "add_keywords":
            kws = args.get("keywords", [])
            for kw in kws:
                matcher.add_keyword(kw)
            matcher.build()
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": f"Indexed {len(kws)} keywords into automaton."}]}
            }
        elif name == "search_patterns":
            text = args.get("text", "")
            matches = matcher.search(text)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps(matches, indent=2)}]}
            }
        elif name == "redact_patterns":
            text = args.get("text", "")
            rep = args.get("replacement", "***")
            redacted = matcher.redact(text, replacement=rep)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": redacted}]}
            }

    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            res = handle_request(req)
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err = {"jsonrpc": "2.0", "id": None, "error": {"code": -32000, "message": str(e)}}
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
