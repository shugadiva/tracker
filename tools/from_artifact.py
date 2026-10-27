"""Снимок трекера из артефакта claude.ai в data/<project>.json.

Выгрузка: ArtifactData list коллекций items и meta с out_dir=<dump>,
картинки /_blob/<id> скачать в img/<project>/ (Artifact read path=<id>).
Запуск: python -X utf8 tools/from_artifact.py <dump> <project> "<Название>" "<Клиент>"
"""
import json, re, sys, glob, os, datetime

dump, pid, title, client = sys.argv[1:5]
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
imgs = {os.path.splitext(f)[0]: f for f in os.listdir(os.path.join(root, "src", "img", pid))}


def load(path):
    d = json.load(open(path, encoding="utf8"))
    return d.get("data", d)


def blob(m):
    return f"img/{pid}/{imgs.get(m.group(1), m.group(1))}"


items = []
for f in sorted(glob.glob(os.path.join(dump, "items", "*.json"))):
    d = load(f)
    d["_id"] = os.path.splitext(os.path.basename(f))[0]
    items.append(d)
meta = {os.path.splitext(os.path.basename(f))[0]: load(f) for f in glob.glob(os.path.join(dump, "meta", "*.json"))}
out = {
    "id": pid,
    "title": title,
    "client": client,
    "updated": datetime.date.today().isoformat(),
    "areas": [{"name": "Отзывы", "slug": "reviews"}, {"name": "Бронирования", "slug": "bookings"}],
    "briefs": {k[6:]: v for k, v in meta.items() if k.startswith("brief-")},
    "rules": meta.get("rules"),
    "items": items,
}
text = re.sub(r"/_blob/([0-9a-f]{32})", blob, json.dumps(out, ensure_ascii=False, indent=1))
open(os.path.join(root, "src", "data", pid + ".json"), "w", encoding="utf8").write(text)
print("items:", len(items), "briefs:", list(out["briefs"]))
