"""Mozambique: convert the downloaded PDFs to Markdown (Portuguese).

* "Legislação Básica" (Assembleia da República compilation) is split into its four texts: Constituição da
  República (2004, revised 2018), Regimento da AR (Lei n.º 17/2013 as republished by Lei n.º 12/2016),
  Estatuto, Segurança e Previdência do Deputado (Lei n.º 31/2014), Lei Orgânica da AR (Lei n.º 13/2013).
* Constituição de 1990 (historical).
* Archived Portal do Governo sectoral legislation: only official texts are kept; electronic editions marked
  "© Pandora Box Lda. — todos os direitos reservados" (a commercial publisher's edition), explanatory/draft
  documents and brochures are excluded; scans without a text layer are skipped (no OCR).
Usage: python mz_convert.py <repo_dir>"""
import datetime
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mz_text import pdf_text, clean_pages, structure, write_md, slug, text_quality  # noqa: E402

RAW = os.environ.get("MZ_RAW", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_raw", "mz"))
TODAY = datetime.date.today().isoformat()

# archived sectoral files: key -> (type, identifier, title, date)
SECTORAL = {
    "agricultura-lei-de-terras": ("lei", "Lei n.º 19/97", "Lei de Terras", "1997-10-01"),
    "imprensa-lei-de-imprensa": ("lei", "Lei n.º 18/91", "Lei de Imprensa", "1991-08-10"),
    "trabalho-lei-do-trabalho": ("lei", "Lei n.º 23/2007", "Boletim da República, I Série, n.º 31, de 1 de Agosto de 2007: Leis n.º 21/2007, 22/2007 e 23/2007 (Lei do Trabalho)", "2007-08-01"),
    "indust-comerc-codigo-comercial": ("codigo", "Decreto-Lei n.º 2/2005", "Código Comercial de Moçambique", "2005-12-27"),
    "judiciaria-codigo-de-processo-penal": ("codigo", "", "Código de Processo Penal (versão anterior à reforma de 2019)", ""),
    "adminest-regfae": ("decreto", "Boletim da República, I Série, n.º 35, 8 de Setembro de 2009",
                        "Regulamento — Boletim da República n.º 35 (2009)", "2009-09-08"),
    "adminest-sistemas-de-carreiras": ("decreto", "Boletim da República, I Série, n.º 35, 5.º Suplemento, 8 de Setembro de 2009",
                                       "Sistemas de Carreiras e Remuneração — Boletim da República n.º 35 (2009)", "2009-09-08"),
    "alfandegas-aluguer-de-viaturas": ("diploma-ministerial", "Diploma Ministerial n.º 74/99", "Diploma Ministerial n.º 74/99 — aluguer de viaturas ligeiras sem condutor (rent-a-car)", "1999-06-02"),
    "alfandegas-comercio-externo": ("diploma-ministerial", "Diploma Ministerial n.º 202/98", "Diploma Ministerial n.º 202/98 — normas do comércio externo", "1998-11-12"),
    "alfandegas-imposto-em-projectos-de-investimentos": ("diploma-ministerial", "Diploma Ministerial n.º 213/98", "Diploma Ministerial n.º 213/98 — importação de bens para projectos de investimento", "1998-12-16"),
    "alfandegas-incricao-como-importador-taxas": ("diploma-ministerial", "Diploma Ministerial n.º 203/98", "Diploma Ministerial n.º 203/98 — taxas de inscrição como importador e exportador", "1998-11-12"),
    "alfandegas-isencao-fabrica-acucar": ("despacho", "", "Despacho do Ministro do Plano e Finanças — isenção para fábricas de açúcar", ""),
    "alfandegas-regulamento-de-desembaraco-aduaneiro": ("diploma-ministerial", "Diploma Ministerial n.º 262/2004", "Diploma Ministerial n.º 262/2004 — Regulamento de desembaraço aduaneiro", "2004-12-22"),
    "alfandegas-sobre-mineiros": ("diploma-ministerial", "Diploma Ministerial n.º 62/98", "Diploma Ministerial n.º 62/98 — trabalhadores mineiros", "1998-05-20"),
    "impostos-iva-regbens2mao": ("decreto", "Decreto n.º 79/98", "Regime especial do IVA aplicável aos bens em segunda mão", "1998-12-29"),
    "impostos-iva-regcompensacao": ("decreto", "", "Regime transitório de compensação do imposto de circulação suportado nas existências (IVA)", ""),
    "indust-comerc-regmademoz-aprovado": ("regulamento", "", "Regulamento sobre os critérios de concessão do direito de uso da marca «Orgulho Moçambicano. Made in Mozambique»", ""),
    "invest-leg-benfiscais": ("decreto", "Decreto n.º 16/2002", "Decreto n.º 16/2002 — Código dos Benefícios Fiscais", "2002-06-27"),
    "invest-leg-irpcolectivas": ("decreto", "Decreto n.º 21/2002", "Decreto n.º 21/2002 — Código do Imposto sobre o Rendimento das Pessoas Colectivas", "2002-07-30"),
    "invest-leg-irpsingulares": ("decreto", "Decreto n.º 20/2002", "Decreto n.º 20/2002 — Código do Imposto sobre o Rendimento das Pessoas Singulares", "2002-07-30"),
    "invest-leg-regulamento-leiinvest": ("decreto", "Decreto n.º 14/93", "Decreto n.º 14/93 — Regulamento da Lei de Investimentos", "1993-07-21"),
    "invest-leg-regulamento-zonaindus": ("decreto", "Decreto n.º 62/99", "Decreto n.º 62/99 — Regulamento das Zonas Francas Industriais", "1999-09-21"),
    "sistema-fiscal-embarque-ipe": ("regulamento", "", "Regulamento da Inspecção Pré-Embarque (IPE)", ""),
    "sistema-fiscal-regras-gerais-de-desembaraco-aduaneiro": ("diploma-ministerial", "Diploma Ministerial n.º 262/2004", "Diploma Ministerial n.º 262/2004 — Regras Gerais de Desembaraço Aduaneiro", "2004-12-22"),
}
DIRS = {"lei": "leis", "codigo": "codigos", "decreto": "decretos", "diploma-ministerial": "diplomas-ministeriais",
        "despacho": "despachos", "regulamento": "regulamentos", "constitution": "constituicao"}
COMPILATION = [  # (cover title regex, key, title, identifier, date, type)
    (r"^CONSTITUIÇÃO DA REPÚBLICA\s*$", "constituicao-da-republica", "Constituição da República de Moçambique",
     "Constituição de 2004, revista pela Lei n.º 1/2018, de 12 de Junho", "2004-11-16", "constitution"),
    (r"^REGIMENTO DA ASSEMBLEIA DA REPÚBLICA\s*$", "regimento-da-assembleia-da-republica",
     "Regimento da Assembleia da República", "Lei n.º 17/2013, republicada pela Lei n.º 12/2016", "2016-12-30", "lei"),
    (r"^ESTATUTO, SEGURANÇA E\s+PREVIDÊNCIA DO DEPUTADO", "estatuto-seguranca-e-previdencia-do-deputado",
     "Estatuto, Segurança e Previdência do Deputado", "Lei n.º 31/2014", "2014-12-30", "lei"),
    (r"^LEI ORGÂNICA DA\s+ASSEMBLEIA DA REPÚBLICA", "lei-organica-da-assembleia-da-republica",
     "Lei Orgânica da Assembleia da República", "Lei n.º 13/2013", "2013-08-12", "lei"),
]


def usable(pages):
    full = re.sub(r"(\.\s?){4,}", " ", "\n".join(pages))
    return len(re.sub(r"\s", "", full)) > 1500 and text_quality(full) >= 0.7


def body_of(pages):
    lines = [x for x in clean_pages(pages) if not re.search(r"(\.\s?){6,}\s*\d*$", x)]
    return structure(lines, "pt")


def out_path(repo, typ, date, name):
    d = DIRS.get(typ, "outros")
    y = date[:4] if date else "sem-data"
    return os.path.join(repo, d, name + ".md") if typ in ("constitution", "codigo") else os.path.join(repo, d, y, name + ".md")


def main(repo):
    items = json.load(open(os.path.join(RAW, "index.json")))
    n = 0
    hashes = set()
    for it in items:
        f = it.get("file")
        if not f:
            continue
        pages, _ = pdf_text(f)
        if it["key"] == "legislacao-basica":
            covers = []
            for i, p in enumerate(pages):
                t = p.strip()
                if len(t) < 200:
                    for k, c in enumerate(COMPILATION):
                        if re.match(c[0], t, re.S) and k not in [x[1] for x in covers]:
                            covers.append((i, k))
            covers.sort()
            for j, (i, k) in enumerate(covers):
                end = covers[j + 1][0] if j + 1 < len(covers) else len(pages)
                _, key, title, ident, date, typ = COMPILATION[k]
                meta = {"title": title, "identifier": ident, "type": typ, "jurisdiction": "mz", "language": "pt",
                        "date": date, "status": "in_force", "source": it["url"], "retrieved": TODAY,
                        "note": "Extraído da compilação «Legislação Básica» do Secretariado Geral da Assembleia da República (2022)"}
                write_md(out_path(repo, typ, date, key), meta, title, body_of(pages[i + 1:end]))
                n += 1
            continue
        if it["origin"] == "parlamento":
            if it["key"] != "constituicao-1990" or not usable(pages):
                print("skip (covered by the compilation, or scanned):", it["key"])
                continue
            title = "Constituição da República de Moçambique (1990)"
            meta = {"title": title, "identifier": "Constituição de 1990", "type": "constitution", "jurisdiction": "mz",
                    "language": "pt", "date": "1990-11-02", "status": "repealed", "source": it["url"], "retrieved": TODAY,
                    "note": "Constituição anterior, substituída pela Constituição de 2004"}
            write_md(os.path.join(repo, "constituicao", "constituicao-1990.md"), meta, title, body_of(pages))
            n += 1
            continue
        key = re.sub(r"^ia-", "", os.path.basename(f))[:-4]
        if key not in SECTORAL:
            print("skip (not an official text, publisher edition, draft or scan):", key)
            continue
        if not usable(pages):
            print("skip (no usable text layer):", key)
            continue
        h = hashlib.sha1("".join(pages).encode()).hexdigest()
        if h in hashes:
            continue
        hashes.add(h)
        typ, ident, title, date = SECTORAL[key]
        meta = {"title": title, "identifier": ident, "type": typ, "jurisdiction": "mz", "language": "pt", "date": date,
                "status": "unknown", "source": it["url"], "archived_source": it["archived"], "retrieved": TODAY,
                "note": "Portal do Governo de Moçambique (legislação sectorial), cópia do Internet Archive"}
        write_md(out_path(repo, typ, date, slug(title)[:90]), meta, title, body_of(pages))
        n += 1
    print("written", n)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
