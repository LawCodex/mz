# Moçambique (MZ) — legislação em Markdown

Part of [LawCodex](https://github.com/LawCodex): the legislation of every country as plain Markdown in git.

**Partial / minimal corpus.** Legislation of the Republic of Mozambique in **Portuguese** (official language):
the **Constitution** (2004, as revised in 2018) and the basic parliamentary laws from the Assembleia da República,
plus a set of laws, codes, decrees and ministerial diplomas that the former Government portal published
(1991–2009 texts, recovered from the Internet Archive). Retrieved 2026-10-13.

| Category | Files |
|---|---|
| Constituição (2004 rev. 2018; 1990 historical) | 2 |
| Leis (Regimento da AR, Estatuto do Deputado, Lei Orgânica da AR, Lei de Imprensa, Lei de Terras, Boletim with Lei do Trabalho) | 6 |
| Códigos (Código Comercial 2005; Código de Processo Penal — pre-2019 version) | 2 |
| Decretos (tax codes IRPS/IRPC 2002, Benefícios Fiscais, investment, IVA, ...) | 9 |
| Diplomas ministeriais (7) / despachos (1) | 8 |
| Regulamentos | 2 |
| **Total** | **29** |

## Structure

```
constituicao/constituicao-da-republica.md          Constituição de 2004, revista pela Lei n.º 1/2018
constituicao/constituicao-1990.md                  Constituição de 1990 (historical, status: repealed)
leis/<year>/<slug>.md                              Leis
codigos/<slug>.md                                  Códigos
decretos/<year>/  diplomas-ministeriais/<year>/  despachos/  regulamentos/   (sem-data = date not known)
```

Front matter: `identifier` (e.g. `Lei n.º 19/97`, `Decreto n.º 21/2002`), `date` (publication date when known),
`status` (`in_force` for the Assembleia da República texts; `unknown` for the archived sectoral texts, several of
which have since been amended or replaced — e.g. the Lei de Terras and the tax codes), `source`, and for archived
files `archived_source` (Wayback Machine URL). Articles become `Artigo N.º — <epígrafe>` headings; TÍTULO /
CAPÍTULO / SECÇÃO become headings. Text extracted with poppler `pdftotext`; texts copied from the Boletim da
República keep the gazette's cover/summary text.

## Sources

| Source | URL |
|---|---|
| Assembleia da República — "Legislação Básica" compilation (Constituição, Regimento, Estatuto do Deputado, Lei Orgânica) | https://www.parlamento.mz/wp-content/uploads/2022/08/Legislacao_Basica.pdf |
| Assembleia da República — Constituição de 1990 | https://www.parlamento.mz/wp-content/uploads/2022/06/Constituicao-da-Republica.pdf |
| Portal do Governo de Moçambique — "Legislação sectorial" (offline; Internet Archive copies) | http://www.portaldogoverno.gov.mz/Legisla/legisSectores/... (each file's `archived_source`) |

The Parliament's robots.txt places no restriction; requests were made with an identifying User-Agent. The archived
Government portal pages were public official publications with no terms forbidding copying.

## Not covered / known gaps

* **Most legislation is missing.** The official gazette (*Boletim da República*, Imprensa Nacional de Moçambique)
  is not freely available online (imprensanac.gov.mz unreachable; it is a paid publication), and no official
  consolidated legislation database exists. The current Government portal no longer publishes legislation.
* Skipped archived files: electronic editions marked "© Pandora Box Lda. — todos os direitos reservados" (a
  commercial publisher's edition: Código de Estrada, Estatuto Geral dos Funcionários, Lei das Telecomunicações,
  etc.), drafts and explanatory documents (Código Penal with "Notas Explicativas", "Fundamentos do Processo
  Penal", the Lei de Bases da Organização Judiciária proposal), a brochure on the tax system, a 2007 thematic
  compilation of the Ministry of Science and Technology, and ~20 scanned PDFs without a text layer (no OCR) —
  among them the Lei da Família, Código do Registo Civil, Lei do Ambiente, Lei de Petróleos, Lei de Electricidade,
  Lei de Investimentos, Lei dos Partidos Políticos.
* The standalone Parliament PDF of the 2018 Constitution is a scan; the compilation text was used instead.

## Regenerate

```
pip install -r scripts/requirements.txt     # plus poppler (pdftotext, pdfinfo)
python scripts/mz_fetch.py                  # downloads into ../_raw/mz/
python scripts/mz_convert.py .
```
