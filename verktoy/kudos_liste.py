"""Skriver ut dokumenter fra Kudos-eksporten som passer et søk, uten å lagre noe.

Bruk: python3 -I verktoy/kudos_liste.py --typer "NOU,Melding til Stortinget" [--eier REGEX] [--sok REGEX] [--fra ÅR]

Hver rad begynner med RAD og har tabulator mellom feltene: dato, type, id, tittel, eiere,
dokumentside, originalfil (Word/PDF fra regjeringen.no), PDF i Kudos og starten av sammendraget.
Brukes til å finne dokumenter og lenker før de legges inn i dokumenter.json.
"""
import csv, io, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kudos_hent import EKSPORT, hent, liste  # noqa: E402


def arg(navn, standard=""):
    return sys.argv[sys.argv.index(navn) + 1] if navn in sys.argv else standard


def main():
    typer = [t.strip() for t in arg("--typer").split(",") if t.strip()]
    eier, sok, fra = arg("--eier"), arg("--sok"), int(arg("--fra", "0") or 0)
    data = hent(EKSPORT)
    if not data:
        print("Fikk ikke hentet eksporten fra Kudos")
        return 1
    alle = list(csv.DictReader(io.StringIO(data.decode("utf-8-sig", "replace")), delimiter=";"))
    print(f"{len(alle)} dokumenter i eksporten")
    n = 0
    for r in sorted(alle, key=lambda r: r.get("publish_date") or "", reverse=True):
        if typer and r.get("type") not in typer:
            continue
        if int((r.get("publish_date") or "0")[:4] or 0) < fra:
            continue
        if eier and not re.search(eier, r.get("owners") or "", re.I):
            continue
        if sok and not re.search(sok, " ".join([r.get("title") or "", r.get("abstract") or ""]), re.I):
            continue
        pdf = next((f for f in liste(r.get("file_urls")) if f.lower().endswith(".pdf")), "")
        felt = [(r.get("publish_date") or "")[:10], r.get("type") or "", "KU-" + r["uuid"], (r.get("title") or "").strip(),
                ",".join(liste(r.get("owners"))), (r.get("external_public_url") or "").strip(),
                (liste(r.get("source_file_urls")) or [""])[0], pdf, re.sub(r"\s+", " ", r.get("abstract") or "")[:200]]
        print("RAD\t" + "\t".join(f.replace("\t", " ") for f in felt))
        n += 1
    print(f"{n} dokumenter passer")
    return 0


if __name__ == "__main__":
    sys.exit(main())
