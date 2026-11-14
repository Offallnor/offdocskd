"""Hovedtittel og kortnavn for dokumentene i dokumenter.tsv.

Kudos oppgir bare nummeret («Meld. St. 17 (2023–2024)»), mens brukerne spør etter tittelen
(«Om integreringspolitikken») eller kortnavnet («integreringsmeldingen», «Lavlønnsutvalget»).

- hovedtittel: leses fra forsiden i dokumentteksten og lagres i dokumenter.tsv. «-» betyr at den
  ikke ble funnet; da prøves det igjen ved neste kjøring (for eksempel etter at teksten er byttet ut
  med tekst fra Word). Dokumentsiden på regjeringen.no kan ikke brukes: den gir 403 også fra GitHub
  (test 14.11.2026).
- kortnavn: utvalgsnavnet leses fra NOU-teksten («Lavlønnsutvalget ble oppnevnt …»). Andre kortnavn
  (for eksempel «integreringsmeldingen») står for hånd under «kortnavn» i dokumenter.json. En tom liste
  der betyr at dokumentet bevisst ikke har kortnavn. Nye meldinger og NOU-er uten kortnavn listes i
  kudos-rapport.txt, så de kan legges til.

Bruk: python3 -I verktoy/titler.py [--alle] [--vis]
  --alle  les hovedtittelen på nytt for alle dokumentene
  --vis   skriv ut tittel og kortnavn for alle, uten å lagre
"""
import json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import deling  # noqa: E402

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TYPER = ("NOU", "Melding til Stortinget", "Proposisjon til Stortinget")
STOPP = re.compile(r"^(Utredning fra|Utgreiing frå|Tilråding|Tilråding frå|Det kongelige|Avgitt til|Til .*departementet|\(Regjeringen|\[Side|Innstilling|Meld\. St|Prop\. |NOU \d|\(\d{4}|Melding til Stortinget|Proposisjon til Stortinget|Omslag|Offentlige institusjoner|Departementenes sikkerhets|Bestilling|Internett|Telefon|E-post|.*www\.)", re.I)
HOPP = re.compile(r"^(\(\d{4}\s*[–-]\s*\d{4}\)|Melding til Stortinget|Proposisjon til Stortinget.*|Norges offentlige utredninger|\d{4}: ?\d+)$", re.I)
UTVALG = re.compile(r"\b([A-ZÆØÅ][a-zæøå-]+(?:utvalget|kommisjonen|ekspertgruppen|gruppen))\b(?: \([^)]*\))? (?:ble|vart|blei) oppnevnt")


def rens(linje):
    linje = re.sub(r"<[^>]+>", "", linje)
    linje = re.sub(r"^(Brø)+", "", linje)   # rest fra Word-konverteringen i noen eldre dokumenter
    linje = re.sub(r"[*_#]+", "", linje)
    return re.sub(r"\s+", " ", linje).strip(" |")


def nummer(tittel):
    """«Meld. St. 17 (2023–2024)» → «Meld. St. 17», «Prop. 98 L (2023–2024)» → «Prop. 98 L»."""
    return re.sub(r"\s*\(.*$", "", tittel).strip()


def forside(rad, n=400):
    fil = rad["fil"]
    del1 = os.path.join(deling.mappe(fil), "del-01.md")
    _, kropp = deling.les(del1 if os.path.exists(os.path.join(ROT, del1)) else fil)
    return [rens(x) for x in kropp.split("\n")[:n]]


def fra_tekst(rad):
    """Tittelen står på forsiden etter nummeret (og sesjon/dokumenttype), fram til første stopplinje."""
    linjer = forside(rad)
    num = nummer(rad["tittel"])
    for i, l in enumerate(linjer):
        if l.replace(" ", "") != num.replace(" ", ""):
            continue
        ut = []
        for m in linjer[i + 1:i + 16]:
            if not m:
                if ut:
                    break
                continue
            if HOPP.match(m) and not ut:
                continue
            if STOPP.match(m) or len(m) > 400:
                break
            ut.append(m)
        if ut:
            t = re.sub(r"\s+:", ":", " ".join(ut)).strip()
            t = re.sub(r"(?<=\S)– ", " – ", t)
            t = re.sub(r":(?=\S)", ": ", t)
            if 3 <= len(t) <= 500 and not re.fullmatch(r"[\d\s:().–-]+", t):
                return t
    if rad["type"] == "NOU":   # forsiden uten nummer: tittelen står rett over «Utredning fra …»
        for i, l in enumerate(linjer[:60]):
            if re.match(r"^(Utredning fra|Utgreiing frå)", l):
                ut = []
                for m in reversed(linjer[max(0, i - 6):i]):
                    if not m:
                        continue
                    if STOPP.match(m) or HOPP.match(m) or len(m) > 160 or m.replace(" ", "") == num.replace(" ", ""):
                        break
                    ut.insert(0, m)
                if ut:
                    return " – ".join(ut[:3])
    return ""


def kortnavn(rad, hand):
    navn = list(hand.get(rad["tittel"], []))
    if rad["type"] == "NOU":
        m = UTVALG.search("\n".join(forside(rad, 400)))
        if m and m.group(1) not in navn and m.group(1) != rad.get("hovedtittel"):
            navn.append(m.group(1))
    return "|".join(navn)


def oppdater(rader, alle=False):
    """Fyller hovedtittel og kortnavn i radene (dict id → rad). Returnerer meldinger og NOU-er uten kortnavn."""
    oppsett = json.load(open(os.path.join(ROT, "dokumenter.json"), encoding="utf-8"))
    hand = oppsett.get("kortnavn", {})
    for t in hand:
        if t not in {r["tittel"] for r in rader.values()}:
            print(f"Kortnavn for et dokument som ikke er i basen: {t}")
    mangler = []
    for r in rader.values():
        if r["type"] not in TYPER or not os.path.exists(os.path.join(ROT, r["fil"])):
            continue
        if not r.get("hovedtittel") or r["hovedtittel"] == "-" or alle:
            r["hovedtittel"] = fra_tekst(r) or "-"
        r["kortnavn"] = kortnavn(r, hand)
        if r["type"] in ("NOU", "Melding til Stortinget") and not r["kortnavn"] and r["tittel"] not in hand:
            mangler.append(r["tittel"])
    return mangler


def visningstittel(r):
    """Tittelen slik den står i lista i veiviseren."""
    t = r["tittel"]
    if r.get("hovedtittel") and r["hovedtittel"] != "-":
        t += " " + r["hovedtittel"]
    if r.get("kortnavn"):
        t += " (" + ", ".join(r["kortnavn"].split("|")) + ")"
    return t


def main():
    import kudos_hent
    rader = kudos_hent.les_oversikt()
    mangler = oppdater(rader, alle="--alle" in sys.argv)
    if "--vis" in sys.argv:
        for r in sorted(rader.values(), key=lambda r: (r["type"], r["ar"])):
            if r["type"] in TYPER:
                print(f"{r['type'][:5]}\t{visningstittel(r)}")
        print(f"\nUten kortnavn ({len(mangler)}): " + "; ".join(mangler))
        return 0
    kudos_hent.skriv_oversikt(rader)
    kudos_hent.skriv_veiviser(rader, json.load(open(os.path.join(ROT, "dokumenter.json"), encoding="utf-8"))["typer"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
