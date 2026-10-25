import html
import json
from pathlib import Path
import subprocess

OWNER = "dejotaerre"
README = Path(__file__).resolve().parents[1] / "README.md"
START, END = "<!-- RECENT:START -->", "<!-- RECENT:END -->"


def render(repos):
    repos = [r for r in repos if not r["private"] and not r["fork"] and r["name"] != OWNER]
    repos.sort(key=lambda r: (r["created_at"], r["name"]), reverse=True)
    rows = ["| Proyecto | Descripción | Creado |", "| --- | --- | --- |"]
    for repo in repos[:6]:
        description = html.escape(" ".join((repo["description"] or "—").split())).replace("|", "&#124;")
        name = html.escape(repo["name"]).replace("|", "&#124;")
        rows.append(f'| <a href="{html.escape(repo["html_url"], quote=True)}">{name}</a> | {description} | {repo["created_at"][:10]} |')
    return "\n".join(rows)


def main():
    result = subprocess.run(
        ["gh", "api", "--paginate", "--slurp", f"users/{OWNER}/repos?type=owner&per_page=100"],
        check=True, text=True, capture_output=True,
    )
    repos = [repo for page in json.loads(result.stdout) for repo in page]
    text = README.read_text()
    if text.count(START) != 1 or text.count(END) != 1:
        raise ValueError("No se encontraron los marcadores únicos de proyectos recientes")
    before, rest = text.split(START)
    _, after = rest.split(END)
    README.write_text(before + START + "\n" + render(repos) + "\n" + END + after)


if __name__ == "__main__":
    main()
