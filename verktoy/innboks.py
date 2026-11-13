"""Erstatter PDF-teksten i et dokument med tekst fra en Word-, epub- eller HTML-fil som er lagt i innboks/.

Bruk: python3 -I verktoy/innboks.py

Filen kobles til dokumentet i dokumenter.tsv på filnavnet fra regjeringen.no (som følger PDF-navnet), id-en (de åtte tegnene foran tittelen i filnavnet
i dokumenter/, eller hele KU-id-en) eller på tittelen (for eksempel «NOU 2019 2.docx» eller
«Meld. St. 14 (2022–2023).epub»). Teksten gjøres om med pandoc, med tabeller. Ordtallet kontrolleres
mot PDF-teksten, så en feil fil ikke erstatter riktig dokument. Toppen av dokumentfilen med lenkene
beholdes. Filer som er lest inn, slettes fra innboksen. Resultatet står i innboks/rapport.md.
"""
import csv, os, re, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kudos_hent import FELT, OVERSIKT, ROT, les_oversikt, skriv_oversikt, slug  # noqa: E402

INNBOKS = os.path.join(ROT, "innboks")
FORMATER = {".docx": "docx", ".epub": "epub", ".html": "html", ".htm": "html", ".odt": "odt"}
GRENSE = (0.7, 1.5)   # ordtall i ny tekst delt på ordtall i PDF-teksten


def finn(navn, rader):
    """Dokumentet filnavnet passer med, eller en forklaring på hvorfor det ikke ble funnet."""
    stamme = os.path.splitext(navn)[0]
    m = re.search(r"KU-[0-9a-f-]{36}", stamme)
    if m:
        r = rader.get(m.group(0))
        return (r, "") if r else (None, f"fant ingen dokument med id {m.group(0)}")
    m = re.match(r"([0-9a-f]{8})(?:-|$)", stamme)
    if m:
        treff = [r for r in rader.values() if os.path.basename(r["fil"]).startswith(m.group(1) + "-")]
        if len(treff) == 1:
            return treff[0], ""
    # Filnavnet fra regjeringen.no: Word-filen heter som PDF-filen, med docx i stedet for pdfs
    # (…/pdfs/nou202520250001_kddddpdfs.pdf og …/docx/nou202520250001_kdddddocx.docx).
    kjerne = re.sub(r"(docx|epub|html?|odt|pdfs)$", "", stamme.lower())
    if len(kjerne) >= 8:
        treff = [r for r in rader.values()
                 if re.sub(r"pdfs$", "", os.path.splitext(os.path.basename(r.get("kilde") or ""))[0].lower()) == kjerne]
        if len(treff) == 1:
            return treff[0], ""
    s = slug(stamme, 200)
    treff = [r for r in rader.values() if slug(r["tittel"], 200) == s]
    if len(treff) == 1:
        return treff[0], ""
    if len(treff) > 1:
        return None, "flere dokumenter har denne tittelen; gi filen navn etter id-en (de åtte tegnene foran tittelen i filnavnet)"
    return None, "fant ikke dokumentet; gi filen samme navn som tittelen (for eksempel «NOU 2019 2.docx») eller id-en"


def til_tekst(sti, fra):
    r = subprocess.run(["pandoc", "-f", fra, "-t", "gfm", "--wrap=none", sti], capture_output=True, timeout=600)
    if r.returncode:
        raise RuntimeError(r.stderr.decode("utf-8", "replace")[:300])
    tekst = r.stdout.decode("utf-8", "replace")
    tekst = re.sub(r"!\[[^\]]*\]\([^)]*\)(\{[^}]*\})?", "", tekst)   # bilder: bare figurtitlene blir igjen
    tekst = re.sub(r"<img[^>]*>", "", tekst)
    tekst = re.sub(r"[ \t]+\n", "\n", tekst)
    return re.sub(r"\n{3,}", "\n\n", tekst).strip()


def tellbare_ord(tekst):
    return len(re.sub(r"<[^>]+>|[|#*_`-]{2,}", " ", tekst).split())


def main():
    if not os.path.isdir(INNBOKS):
        return 0
    # Filer som er lastet opp i rotmappa ved en feil, flyttes inn i innboksen.
    for f in os.listdir(ROT):
        if os.path.splitext(f)[1].lower() in FORMATER and os.path.isfile(os.path.join(ROT, f)):
            os.replace(os.path.join(ROT, f), os.path.join(INNBOKS, f))
    rader = les_oversikt()
    filer = sorted(f for f in os.listdir(INNBOKS) if os.path.splitext(f)[1].lower() in FORMATER)
    if not filer:
        print("Ingen filer i innboksen")
        return 0
    rapport, lest = [], 0
    for navn in filer:
        sti = os.path.join(INNBOKS, navn)
        r, grunn = finn(navn, rader)
        if not r:
            rapport.append(f"- **{navn}**: ikke lest inn – {grunn}.")
            continue
        try:
            tekst = til_tekst(sti, FORMATER[os.path.splitext(navn)[1].lower()])
        except Exception as e:
            rapport.append(f"- **{navn}**: ikke lest inn – filen kunne ikke gjøres om til tekst ({e}).")
            continue
        ny, gml = tellbare_ord(tekst), int(r.get("ord") or 0)
        forhold = ny / gml if gml else 1
        if gml and not GRENSE[0] <= forhold <= GRENSE[1] and "--tving" not in sys.argv:
            rapport.append(f"- **{navn}**: ikke lest inn – {ny} ord mot {gml} i PDF-teksten til «{r['tittel']}». "
                           "Er det riktig fil? Er den det, kjør jobben med «tving».")
            continue
        p = os.path.join(ROT, r["fil"])
        hode = open(p, encoding="utf-8").read().partition("\n---\n")[0]
        fra = FORMATER[os.path.splitext(navn)[1].lower()]
        kilde = {"docx": "Word-fil", "odt": "ODT-fil", "epub": "epub-fil", "html": "HTML-side"}[fra]
        linjer = [x for x in hode.split("\n") if not x.startswith("- Tekst:")]
        i = next((k for k, x in enumerate(linjer) if x.startswith("- Kudos:")), len(linjer))
        linjer.insert(i, f"- Tekst: fra {kilde} lastet opp {time.strftime('%Y-%m-%d')}, ikke fra PDF. Tabellene er med. "
                         "Figurer er bare med som titler, så tall som bare finnes i en figur, må leses i originalen.")
        with open(p, "w", encoding="utf-8") as f:
            f.write("\n".join(linjer).rstrip("\n") + "\n\n---\n\n" + tekst + "\n")
        r.update(tekstkilde=fra, ord=str(ny), tabeller=str(len(re.findall(r"(?m)^\|.*\|$\n^\|[ :|-]+\|$", tekst))
                                                          + tekst.count("<table")), figurer="", tall_linjer="")
        os.remove(sti)
        lest += 1
        rapport.append(f"- **{navn}**: lest inn i «{r['tittel']}» ({ny} ord, PDF-teksten hadde {gml}).")
    skriv_oversikt(rader)
    with open(os.path.join(INNBOKS, "rapport.md"), "w", encoding="utf-8") as f:
        f.write(f"# Siste kjøring av innboksen ({time.strftime('%Y-%m-%d %H:%M')})\n\n" + "\n".join(rapport) + "\n")
    with open(os.path.join(ROT, "innboks-melding.txt"), "w", encoding="utf-8") as f:
        f.write(f"Innboks: {lest} dokumenter lest inn, {len(filer) - lest} ikke\n")
    print("\n".join(rapport))
    return 0


if __name__ == "__main__":
    sys.exit(main())
