"""Henter offentlige dokumenter fra Kudos (DFØ, kudos.dfo.no) og lagrer dem som tekst.

Bruk: python3 -I verktoy/kudos_hent.py [--maks N] [--diagnose]

Laster ned DFØs åpne CSV-eksport (ett kall), velger dokumentene i dokumenter.json
(dokumenttype, eier og første år), henter PDF-en fra Kudos og gjør den om til tekst med
pdftotext. Hvert dokument blir én fil: dokumenter/<mappe>/<år>/<kort-id>-<tittel>.md, med
tittel, år, eiere, utførere og lenker øverst. dokumenter.tsv er oversikten over alt som er lagret.
Dokumenter som er lagret fra før, hentes ikke på nytt. --diagnose skriver ut hva eksporten
inneholder for de valgte typene, uten å lagre noe.
"""
import csv, gzip, io, json, os, re, subprocess, sys, tempfile, time, unicodedata, urllib.request
from collections import Counter

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EKSPORT = "https://kudos.dfo.no/api/v0/documents/download/csv"
UA = "Mozilla/5.0 (offentlige dokumenter)"
OVERSIKT = os.path.join(ROT, "dokumenter.tsv")
FELT = ["id", "type", "ar", "tittel", "eiere", "utforere", "fil", "kudos", "kilde", "ord", "hentet"]


def hent(url, forsok=4, pause=40):
    for i in range(forsok):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=300) as r:
                data = r.read()
            return gzip.decompress(data) if data[:2] == b"\x1f\x8b" else data
        except Exception as e:
            print(f"  {type(e).__name__} {getattr(e, 'code', '')}: {url}", flush=True)
            if getattr(e, "code", None) == 404:
                return b""
            time.sleep(pause * (i + 1))
    return b""


def liste(s):
    return [x.strip() for x in (s or "").split("|") if x.strip()]


def slug(s, n=60):
    s = unicodedata.normalize("NFKD", s.lower().replace("ø", "o").replace("æ", "ae").replace("å", "a"))
    s = re.sub(r"[^a-z0-9]+", "-", s.encode("ascii", "ignore").decode()).strip("-")
    return s[:n].rstrip("-") or "dokument"


def les_oversikt():
    if not os.path.exists(OVERSIKT):
        return {}
    with open(OVERSIKT, encoding="utf-8") as f:
        return {r["id"]: r for r in csv.DictReader(f, delimiter="\t")}


def skriv_oversikt(rader):
    with open(OVERSIKT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, FELT, delimiter="\t", lineterminator="\n")
        w.writeheader()
        for r in sorted(rader.values(), key=lambda r: (r["type"], r["ar"], r["tittel"])):
            w.writerow(r)


def pdf_til_tekst(data):
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "f.pdf")
        open(p, "wb").write(data)
        r = subprocess.run(["pdftotext", "-enc", "UTF-8", p, "-"], capture_output=True, timeout=300)
        tekst = r.stdout.decode("utf-8", "replace")
    tekst = re.sub(r"\f", "\n\n", tekst)
    tekst = re.sub(r"[ \t]+\n", "\n", tekst)
    return re.sub(r"\n{3,}", "\n\n", tekst).strip()


def main():
    maks = int(sys.argv[sys.argv.index("--maks") + 1]) if "--maks" in sys.argv else 300
    diagnose = "--diagnose" in sys.argv
    oppsett = json.load(open(os.path.join(ROT, "dokumenter.json"), encoding="utf-8"))
    eiere, typer = set(oppsett["eiere"]), oppsett["typer"]

    data = hent(EKSPORT)
    if not data:
        print("Fikk ikke hentet eksporten fra Kudos")
        return 1
    alle = list(csv.DictReader(io.StringIO(data.decode("utf-8-sig", "replace")), delimiter=";"))
    print(f"{len(alle)} dokumenter i eksporten")
    valgte = []
    for t, o in typer.items():
        av_type = [r for r in alle if r.get("type") == t]
        mine = [r for r in av_type if eiere & set(liste(r.get("owners")))
                and int((r.get("publish_date") or "0")[:4] or 0) >= o.get("fra_ar", 0)]
        print(f"{t}: {len(av_type)} i alt, {len(mine)} valgt")
        if diagnose:
            print("  Vanligste eiere:", Counter(e for r in av_type for e in liste(r.get("owners"))).most_common(15))
            print("  Utførere blant de valgte:", Counter(e for r in mine for e in liste(r.get("authoring_actors"))).most_common(40))
            print("  År blant de valgte:", sorted(Counter((r.get("publish_date") or "")[:4] for r in mine).items()))
            for r in mine[:8]:
                print("  -", r.get("publish_date"), "|", r.get("title"), "|", r.get("owners"), "|", r.get("authoring_actors"),
                      "|", len(liste(r.get("file_urls"))), "filer")
        valgte += [(t, o, r) for r in mine]
    if diagnose:
        print("Kolonner:", list(alle[0].keys()))
        return 0

    oversikt = les_oversikt()
    nye, feil = 0, []
    for t, o, r in valgte:
        rid = "KU-" + r["uuid"]
        if rid in oversikt:
            continue
        if nye >= maks:
            break
        ar = (r.get("publish_date") or "0000")[:4]
        pdf = next((f for f in liste(r.get("file_urls")) if f.lower().endswith(".pdf")), "")
        if not pdf:
            feil.append(f"Ingen PDF: {r.get('title')} ({rid})")
            continue
        fil = hent(pdf, forsok=3, pause=20)
        time.sleep(2)
        tekst = pdf_til_tekst(fil) if fil else ""
        if len(tekst) < 200:
            feil.append(f"Ingen tekst ({len(fil)} byte): {r.get('title')} ({rid})")
            continue
        sti = os.path.join("dokumenter", o["mappe"], ar, f"{r['uuid'][:8]}-{slug(r.get('title') or '')}.md")
        os.makedirs(os.path.join(ROT, os.path.dirname(sti)), exist_ok=True)
        kudos = "https://kudos.dfo.no/dokument/" + r["uuid"]
        kilde = (liste(r.get("source_file_urls")) or [r.get("external_public_url") or ""])[0]
        hode = [f"# {r.get('title') or ''}", "", f"- Type: {t}", f"- Publisert: {r.get('publish_date') or ''}",
                f"- Eier: {', '.join(liste(r.get('owners')))}"]
        if liste(r.get("authoring_actors")):
            hode.append(f"- Utført av: {', '.join(liste(r.get('authoring_actors')))}")
        hode += [f"- Kudos: {kudos}", f"- Original: {kilde}" if kilde else "", f"- Hentet: {time.strftime('%Y-%m-%d')}",
                 "", "Teksten er hentet automatisk fra PDF-en og kan ha feil i tabeller og oppsett. Kontroller sitater mot originalen.", "", "---", ""]
        with open(os.path.join(ROT, sti), "w", encoding="utf-8") as f:
            f.write("\n".join(x for x in hode if x is not None) + "\n" + tekst + "\n")
        oversikt[rid] = {"id": rid, "type": t, "ar": ar, "tittel": (r.get("title") or "").replace("\t", " "),
                         "eiere": "|".join(liste(r.get("owners"))), "utforere": "|".join(liste(r.get("authoring_actors"))),
                         "fil": sti, "kudos": kudos, "kilde": kilde, "ord": str(len(tekst.split())), "hentet": time.strftime("%Y-%m-%d")}
        nye += 1
        print(f"  {sti} ({len(tekst.split())} ord)", flush=True)
    skriv_oversikt(oversikt)
    gjenstar = sum(1 for _, _, r in valgte if "KU-" + r["uuid"] not in oversikt) - len(feil)
    with open(os.path.join(ROT, "kudos-rapport.txt"), "w", encoding="utf-8") as f:
        f.write(f"Dokumenter fra Kudos: {nye} nye, {len(oversikt)} i alt\n\n")
        f.write("\n".join(f"- {x}" for x in feil[:50]) + ("\n" if feil else ""))
    print(f"{nye} nye, {len(oversikt)} i alt, {len(feil)} uten tekst, om lag {max(gjenstar, 0)} gjenstår")
    return 0


if __name__ == "__main__":
    sys.exit(main())
