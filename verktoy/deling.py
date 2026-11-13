"""Deler store dokumentfiler i deler, så de kan leses av verktøy som kutter lange tekster.

Et dokument på over GRENSE tegn blir en hovedfil med toppen (lenker, tekstkilde) og en innholdsfortegnelse,
og en mappe med samme navn som hovedfilen, med del-01.md, del-02.md osv. Tekst fra Word, epub og HTML deles
ved kapitteloverskriftene, PDF-tekst ved sidemerkene ([Side N]). Hver del har lenkene og tekstlinja øverst.

les(fil) gir (topp, tekst) for hele dokumentet, delt eller ikke. skriv(fil, topp, tekst) lagrer og deler på nytt.

Bruk alene: python3 -I verktoy/deling.py  (deler alle dokumenter i dokumenter.tsv på nytt)
"""
import csv, os, re, shutil, sys

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRENSE = 100_000   # tegn; mindre dokumenter blir liggende i én fil
MAL = 50_000       # omtrentlig størrelse på en del
MAKS_DEL = 75_000  # større enkeltkapitler deles videre
MERKE = "<!-- DELT -->"
SIDE = re.compile(r"^\[Side (\d+)\]$", re.M)


def mappe(fil):
    return fil[:-3] if fil.endswith(".md") else fil + "-deler"


def les(fil):
    p = os.path.join(ROT, fil)
    tekst = open(p, encoding="utf-8").read()
    topp, _, kropp = tekst.partition("\n---\n")
    if MERKE not in kropp:
        return topp, kropp.strip("\n")
    m = os.path.join(ROT, mappe(fil))
    deler = sorted(f for f in os.listdir(m) if re.fullmatch(r"del-\d+\.md", f))
    return topp, "\n\n".join(open(os.path.join(m, f), encoding="utf-8").read().partition("\n---\n")[2].strip("\n") for f in deler)


def _seksjoner(tekst):
    """Deler tekst i enheter med (overskrift-eller-side, tekst). Word-tekst ved #-overskrifter, PDF-tekst ved sidemerker."""
    if SIDE.search(tekst):
        biter = SIDE.split(tekst)   # [før, n1, tekst1, n2, tekst2, ...]
        enheter = [("", biter[0])] if biter[0].strip() else []
        for i in range(1, len(biter), 2):
            enheter.append((int(biter[i]), f"[Side {biter[i]}]" + biter[i + 1]))
        return "pdf", enheter
    for niva in ("# ", "## ", "### "):
        biter = re.split(rf"(?m)^(?={re.escape(niva)})", tekst)
        if len(biter) > 2:
            return "word", [(b.split("\n", 1)[0].lstrip("# ").strip() if b.startswith("#") else "", b) for b in biter if b.strip()]
    return "word", [("", tekst)]


def _for_stor(enhet):
    """Deler en enkelt enhet som er for stor: ved underoverskrifter, ellers ved avsnitt."""
    navn, tekst = enhet
    for niva in ("## ", "### ", "#### "):
        biter = re.split(rf"(?m)^(?={re.escape(niva)})", tekst)
        if len(biter) > 2:
            return [(navn if i == 0 else b.split("\n", 1)[0].lstrip("# ").strip(), b) for i, b in enumerate(biter) if b.strip()]
    ut, buf = [], ""
    for avsnitt in re.split(r"(?<=\n\n)", tekst):
        if len(buf) + len(avsnitt) > MAL and buf:
            ut.append((navn if not ut else "", buf))
            buf = ""
        buf += avsnitt
    if buf:
        ut.append((navn if not ut else "", buf))
    return ut


def _grupper(enheter):
    ut, gruppe, storrelse = [], [], 0
    ko = list(enheter)
    while ko:
        e = ko.pop(0)
        if len(e[1]) > MAKS_DEL:
            mindre = _for_stor(e)
            if len(mindre) > 1:
                ko[:0] = mindre
                continue
        if gruppe and storrelse + len(e[1]) > MAL:
            ut.append(gruppe)
            gruppe, storrelse = [], 0
        gruppe.append(e)
        storrelse += len(e[1])
    if gruppe:
        ut.append(gruppe)
    return ut


def _pdf_overskrifter(tekst):
    """Nummererte overskrifter i PDF-tekst (1, 1.2, 1.2.3 fulgt av tekst med stor forbokstav på egen, kort linje)."""
    funnet = []
    for m in re.finditer(r"(?m)^ *(\d{1,2}(?:\.\d{1,2})?) {1,3}([A-ZÆØÅ][^\n]{2,70})$", tekst):
        nr, tittel = m.group(1), m.group(2).strip()
        if re.search(r"\d{3,}|  {2,}|\.{3}", tittel) or (nr.isdigit() and int(nr) > 40):
            continue
        funnet.append(f"{nr} {tittel}")
    return funnet


def skriv(fil, topp, tekst):
    """Lagrer dokumentet, delt hvis det er stort. Skriver bare filer som endres."""
    p = os.path.join(ROT, fil)
    m = os.path.join(ROT, mappe(fil))
    tekst = tekst.strip("\n")
    topp = topp.rstrip("\n")
    if len(tekst) <= GRENSE:
        _skriv(p, topp + "\n\n---\n\n" + tekst + "\n")
        if os.path.isdir(m):
            shutil.rmtree(m)
        return 1
    art, enheter = _seksjoner(tekst)
    grupper = _grupper(enheter)
    tittel = topp.split("\n", 1)[0].lstrip("# ").strip()
    lenker = [x for x in topp.split("\n") if re.match(r"- (Les hele dokumentet|Original-PDF|PDF|Tekst):", x)]
    rader, filer = [], []
    for i, g in enumerate(grupper, 1):
        navn = f"del-{i:02d}.md"
        filer.append(navn)
        innhold = "".join(t for _, t in g).strip("\n")
        sider = [n for n, _ in g if isinstance(n, int)]
        if art == "pdf":
            omfang = f"side {sider[0]}–{sider[-1]}" if sider else "forside"
            kapitler = _pdf_overskrifter(innhold)
        else:
            omfang = ""
            kapitler = [re.sub(r"^#+ *", "", x).strip() for x in re.findall(r"(?m)^#{1,2} [^\n]+", innhold)] or [n for n, _ in g if n]
        delsti = f"{mappe(fil)}/{navn}"
        hode = [f"# {tittel}, del {i} av {len(grupper)}" + (f" ({omfang})" if omfang else ""), "",
                f"- Hele dokumentet med innholdsfortegnelse: {fil}"] + lenker
        _skriv(os.path.join(m, navn), "\n".join(hode) + "\n\n---\n\n" + innhold + "\n")
        vis = "; ".join(kapitler[:10]) + (" …" if len(kapitler) > 10 else "")
        rader.append(f"| {i} | {omfang or '–'} | {vis.replace('|', '/') or '–'} | `{delsti}` |")
    if os.path.isdir(m):
        for f in os.listdir(m):
            if f not in filer:
                os.remove(os.path.join(m, f))
    forklaring = ("Teksten er delt i sider fra PDF-en. Kapitlene er funnet automatisk og kan mangle eller være ufullstendige; "
                  "sidetallene er sikre." if art == "pdf" else "Teksten er delt ved kapitlene.")
    kropp = [MERKE, "", f"Dokumentet er langt og er delt i {len(grupper)} deler. Åpne delen du trenger. {forklaring}", "",
             "| Del | Sider | Kapitler | Fil |", "|---|---|---|---|"] + rader
    _skriv(p, topp + "\n\n---\n\n" + "\n".join(kropp) + "\n")
    return len(grupper)


def _skriv(p, innhold):
    if os.path.exists(p) and open(p, encoding="utf-8").read() == innhold:
        return
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(innhold)


def ordne(fil):
    """Deler (eller samler) en lagret fil etter gjeldende regler."""
    if not os.path.exists(os.path.join(ROT, fil)):
        return 0
    return skriv(fil, *les(fil))


def main():
    with open(os.path.join(ROT, "dokumenter.tsv"), encoding="utf-8") as f:
        rader = list(csv.DictReader(f, delimiter="\t"))
    delt = sum(1 for r in rader if ordne(r["fil"]) > 1)
    print(f"{delt} av {len(rader)} dokumenter er delt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
