CAREER_RULES = {
    "SOC Analyst": {
        "signals": ["Investigating alerts and incidents", "Automating tasks with Python"],
        "reason": "A good path to explore if you like investigating events, interpreting logs, and understanding how attacks are detected.",
        "next": "Learn networking fundamentals, Linux commands, log analysis, and the purpose of a SIEM; then analyze a sample authentication log."
    },
    "Penetration Tester": {
        "signals": ["Ethical hands-on testing", "Automating tasks with Python"],
        "reason": "Worth exploring if you enjoy hands-on problem solving, web technologies, and authorized security testing.",
        "next": "Study HTTP, Linux, networking, and common web vulnerabilities in a legal training lab; write a clear findings report."
    },
    "Digital Forensics Investigator": {
        "signals": ["Investigating digital evidence", "Investigating alerts and incidents"],
        "reason": "Worth exploring if you enjoy careful investigation, timelines, evidence handling, and reconstructing events.",
        "next": "Learn operating-system artefacts, file systems, hashes, evidence integrity, and basic incident timelines."
    },
    "Cloud Security Engineer": {
        "signals": ["Cloud and infrastructure"],
        "reason": "Worth exploring if cloud platforms, identity permissions, networks, and infrastructure configuration interest you.",
        "next": "Learn cloud fundamentals, IAM, networking, logging, and least privilege using a free-tier or local learning lab."
    },
    "Application Security Engineer": {
        "signals": ["Building secure software"],
        "reason": "Worth exploring if you enjoy programming and want to prevent vulnerabilities in applications and APIs.",
        "next": "Build a small web app, learn input validation and authentication basics, and practice identifying and fixing OWASP-style vulnerabilities in a lab."
    },
    "Security Automation": {
        "signals": ["Automating tasks with Python", "Investigating alerts and incidents"],
        "reason": "Worth exploring if you like scripting repetitive tasks and connecting security tools and data.",
        "next": "Use Python to parse a sample log file, flag suspicious patterns, and output a short report."
    }
}

def recommend_paths(interests, programming, networking, work_style):
    ranked = []
    for career, info in CAREER_RULES.items():
        score = sum(1 for signal in info["signals"] if signal in interests)
        if career == "Application Security Engineer" and programming in ["Intermediate", "Strong"]:
            score += 1
        if career in ["SOC Analyst", "Penetration Tester"] and networking in ["Intermediate", "Strong"]:
            score += 1
        if work_style == "Programming and building" and career in ["Application Security Engineer", "Security Automation"]:
            score += 2
        if work_style == "Investigative and analytical" and career in ["SOC Analyst", "Digital Forensics Investigator"]:
            score += 2
        if work_style == "Hands-on testing" and career == "Penetration Tester":
            score += 2
        if work_style == "Infrastructure and configuration" and career == "Cloud Security Engineer":
            score += 2
        ranked.append((score, career, info))
    ranked.sort(key=lambda x: (-x[0], x[1]))
    selected = ranked[:3]
    return [{"career": career, "reason": info["reason"], "next_step": info["next"]} for score, career, info in selected]

def build_roadmap(career, weeks, rag):
    result = rag.answer(f"{career} required skills beginner projects learning roadmap certifications", top_k=5)
    milestones = {
        4: ["Week 1: foundations and terminology", "Week 2: guided hands-on exercises", "Week 3: one small beginner project", "Week 4: document findings and review gaps"],
        8: ["Weeks 1–2: foundations", "Weeks 3–4: core tools and guided labs", "Weeks 5–6: build a portfolio project", "Weeks 7–8: write a report, review gaps, and plan next steps"],
        12: ["Weeks 1–3: foundations", "Weeks 4–6: tools and guided labs", "Weeks 7–9: build and improve a portfolio project", "Weeks 10–12: document results, revise fundamentals, and plan next steps"]
    }
    plan = "\n".join(f"- {item}" for item in milestones[weeks])
    result["answer"] = f"## {weeks}-week starter roadmap: {career}\n\n{plan}\n\n### Career-specific knowledge to use\n{result['answer']}\n\nAdjust the pace to your current experience. This is a starter plan, not a guarantee of job readiness."
    return result
