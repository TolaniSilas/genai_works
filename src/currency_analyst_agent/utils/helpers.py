# helper functions.

def load_markdown_report(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

report = load_markdown_report("output/report.md")
