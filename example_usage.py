"""Example usage for GenPark Aho-Corasick Multi-Pattern Matcher.
100% Python Standard Library.
"""

from client import AhoCorasickMatcher

def main():
    matcher = AhoCorasickMatcher()
    
    # Register sensitive terms
    sensitive_terms = ["api_key", "bearer_token", "private_secret", "admin_root"]
    for term in sensitive_terms:
        matcher.add_keyword(term, metadata={"severity": "HIGH"})
    
    matcher.build()
    
    prompt = "Client prompt contains api_key and bearer_token alongside private_secret configuration."
    print("Original Text:", prompt)
    
    matches = matcher.search(prompt)
    print("\nFound Matches:")
    for m in matches:
        print(f"- Keyword: {m['keyword']} (offset {m['start']} to {m['end']})")
        
    redacted = matcher.redact(prompt, replacement="[REDACTED]")
    print("\nRedacted Text:", redacted)

if __name__ == "__main__":
    main()
