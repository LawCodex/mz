"""Mozambique: download legislation PDFs from
  * the Assembleia da República (https://www.parlamento.mz): Constituição da República (in force, and the
    previous one), Regimento, Estatuto do Deputado, Lei Orgânica da AR;
  * the former Portal do Governo de Moçambique "Legislação sectorial" pages
    (http://www.portaldogoverno.gov.mz/Legisla/legisSectores/...), no longer online, via their Internet Archive
    (Wayback Machine) captures — the archived URL is recorded.
Cache: _raw/mz/. Usage: python mz_fetch.py
"""
import json
import os
import re
import sys
import time
from urllib.parse import unquote

import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mz_text import fetch, UA  # noqa: E402

RAW = os.environ.get("MZ_RAW", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_raw", "mz"))
PARL = [
    ("legislacao-basica", "Legislação Básica (Secretariado Geral da Assembleia da República): Constituição, Regimento, "
     "Estatuto do Deputado, Lei Orgânica da AR", "compilation",
     "https://www.parlamento.mz/wp-content/uploads/2022/08/Legislacao_Basica.pdf"),
    ("constituicao", "Constituição da República de Moçambique (2004, revista pela Lei n.º 1/2018)", "constitution",
     "https://www.parlamento.mz/wp-content/uploads/2022/06/Constituicao-da-Republica-Mocambicana-2018.pdf"),
    ("constituicao-1990", "Constituição da República de Moçambique (1990)", "constitution",
     "https://www.parlamento.mz/wp-content/uploads/2022/06/Constituicao-da-Republica.pdf"),
    ("regimento-ar", "Regimento da Assembleia da República", "lei",
     "https://www.parlamento.mz/wp-content/uploads/2022/02/Regimento-da-Assembleia-da-Republica.pdf"),
    ("estatuto-deputado", "Estatuto, Segurança e Previdência do Deputado", "lei",
     "https://www.parlamento.mz/wp-content/uploads/2022/02/Estatuto-do-Deputado.pdf"),
    ("lei-organica-ar", "Lei Orgânica da Assembleia da República", "lei",
     "https://www.parlamento.mz/wp-content/uploads/2022/06/Lei-Organica-da-Assembleia-da-Republica.pdf"),
]
CDX = ("https://web.archive.org/cdx/search/cdx?url=portaldogoverno.gov.mz/Legisla/legisSectores/*"
       "&output=json&fl=original,timestamp,statuscode,mimetype&filter=statuscode:200&collapse=urlkey&limit=5000")


def main():
    items = []
    for key, title, typ, url in PARL:
        f = fetch(url, os.path.join(RAW, "pdf", key + ".pdf"), delay=3, check_pdf=True, timeout=300)
        items.append({"key": key, "title": title, "type": typ, "url": url, "file": f, "origin": "parlamento"})
    rows = []
    for k in range(5):
        try:
            rows = requests.get(CDX, headers={"User-Agent": UA}, timeout=300).json()[1:]
            break
        except Exception as e:  # noqa
            print("cdx retry", k + 1, e)
            time.sleep(30)
    best = {}
    for orig, ts, st, mt in rows:
        if not orig.lower().endswith(".pdf"):
            continue
        path = re.sub(r"^https?://(www\.)?portaldogoverno\.gov\.mz(:80)?/", "", orig)
        if path not in best or ts > best[path][1]:
            best[path] = (orig, ts)
    for path, (orig, ts) in sorted(best.items()):
        key = re.sub(r"[^A-Za-z0-9]+", "-", unquote(path.split("legisSectores/")[1]))[:-4].strip("-").lower()
        arch = "https://web.archive.org/web/%sid_/%s" % (ts, orig)
        f = fetch(arch, os.path.join(RAW, "pdf", "ia-" + key + ".pdf"), delay=4, check_pdf=True, timeout=300)
        items.append({"key": key, "url": orig.replace(":80/", "/"), "archived": "https://web.archive.org/web/%s/%s" % (ts, orig),
                      "sector": path.split("/")[2], "file": f, "origin": "portaldogoverno"})
        if not f:
            print("FAILED", arch)
    json.dump(items, open(os.path.join(RAW, "index.json"), "w"), indent=1, ensure_ascii=False)
    print("items", len(items), "ok", sum(1 for i in items if i["file"]))


if __name__ == "__main__":
    os.makedirs(RAW, exist_ok=True)
    main()
