from rag_engine import CyberCareerRAG

TESTS = [
    ("What does a SOC analyst do?", "soc_analyst.md"),
    ("Which skills should I learn for SIEM and log analysis?", "soc_analyst.md"),
    ("What is authorized penetration testing?", "penetration_tester.md"),
    ("Which tools and concepts help a beginner in web security?", "penetration_tester.md"),
    ("What does a digital forensics investigator examine?", "digital_forensics.md"),
    ("Why are hashes useful in digital evidence?", "digital_forensics.md"),
    ("What is IAM in cloud security?", "cloud_security.md"),
    ("How can I learn to secure a web application?", "application_security.md"),
    ("Suggest a Python project for security automation.", "beginner_projects.md"),
    ("What is today's cafeteria menu?", None),
]

def main():
    rag = CyberCareerRAG()
    passed = 0
    for question, expected in TESTS:
        sources = rag.retrieve(question, top_k=4)
        best_path = sources[0]["path"].split("/")[-1] if sources else None
        # For intentionally unsupported content, require the public answer to abstain.
        if expected is None:
            ok = not rag.answer(question)["sources"]
        else:
            ok = best_path == expected
        passed += int(ok)
        print(f'{"PASS" if ok else "CHECK"} | {question} | expected={expected} | got={best_path}')
    print(f"\nTop-1 retrieval checks: {passed}/{len(TESTS)}")
    print("Review CHECK cases manually. This small set is a smoke test, not a complete benchmark.")

if __name__ == "__main__":
    main()
