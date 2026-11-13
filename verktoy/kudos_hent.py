"""Henter offentlige dokumenter fra Kudos (DFØ, kudos.dfo.no) og lagrer dem som tekst.

Bruk: python3 -I verktoy/kudos_hent.py [--maks N] [--diagnose]

Laster ned DFØs åpne CSV-eksport (ett kall), velger dokumentene i dokumenter.json
(dokumenttype, eier og første år), henter PDF-en fra Kudos og gjør den om til tekst med
pdftotext. Hvert dokument blir én fil: dokumenter/<mappe>/<år>/<kort-id>-<tittel>.md (tildelingsbrev under budsjettåret), med
tittel, år, eiere, utførere og lenker øverst. dokumenter.tsv er oversikten over alt som er lagret.
Dokumenter som er lagret fra før, hentes ikke på nytt. --diagnose skriver ut hva eksporten
inneholder for de valgte typene, uten å lagre noe.
"""
import csv, gzip, io, json, os, re, subprocess, sys, tempfile, time, unicodedata, urllib.request
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import deling  # noqa: E402

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EKSPORT = "https://kudos.dfo.no/api/v0/documents/download/csv"
UA = "Mozilla/5.0 (offentlige dokumenter)"
OVERSIKT = os.path.join(ROT, "dokumenter.tsv")
START = time.time()
MINUTTER = 140
FELT = ["id", "type", "ar", "tittel", "sammendrag", "eiere", "mottakere", "utforere", "fil", "side", "kudos", "kilde", "ord", "tekstkilde", "tabeller", "figurer", "tall_linjer", "hentet"]
VEIVISER = os.path.join(ROT, "VEIVISER.md")


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


def sammendrag(r, n=300):
    t = re.sub(r"\s+", " ", r.get("abstract") or "").strip()
    return t if len(t) <= n else t[:n].rsplit(" ", 1)[0] + " …"


def kvalitet(tekst):
    """Tegn på at tabeller og figurer kan være lest feil: tabell- og figurtitler, budsjettabeller
    og linjer som bare har tall (tall som er revet løs fra tabellen eller figuren de hørte til)."""
    tabeller = len(re.findall(r"(?m)^\s*Tabell\s+\d+(\.\d+)*\s+[A-ZÆØÅ«]", tekst))
    tabeller += 1 if re.search(r"(?m)^\s*(Kap\.|Post)\s*$", tekst) else 0   # budsjettabell der kolonnene er splittet
    figurer = len(re.findall(r"(?m)^\s*Figur\s+\d+(\.\d+)*\s+[A-ZÆØÅ«]", tekst))
    # Linjer med bare tall: beløp med tusenskille, desimaltall, prosent eller flere tall etter hverandre.
    # Et enkelt heltall er oftest et sidetall.
    # Kapittelnumre (9.4.2) og sesjoner (2022–2023) telles ikke.
    tall = sum(1 for x in re.findall(r"(?m)^[ \t]*[-–]?\d[\d.,% \t–-]*$", tekst)
               if re.search(r"\d \d{3}|\d,\d|%|\d\s+[-–]?\d", x.strip()) and not re.fullmatch(r"\d{4}\s*[–-]\s*\d{4}", x.strip()))
    return tabeller, figurer, tall


def varsel(tabeller, figurer, tall):
    """Linja øverst i fila som sier om tabeller og figurer kan være lest feil."""
    if tabeller == 0 and figurer == 0 and tall < 10:
        return "- Tekst: hentet fra PDF. Ingen tegn til tabeller eller figurer som kan være lest feil."
    deler = []
    if tabeller:
        deler.append(f"{tabeller} {'tabell' if tabeller == 1 else 'tabeller'}")
    if figurer:
        deler.append(f"{figurer} {'figur' if figurer == 1 else 'figurer'}")
    if tall >= 10:
        deler.append(f"{tall} linjer med løsrevne tall")
    return (f"- Tekst: hentet fra PDF. OBS: {', '.join(deler)}. Tall i tabeller og figurer kan være forskjøvet eller mangle. "
            "Kontroller mot originalen før du bruker dem.")


def merk_kvalitet(rad):
    """Teller og skriver varsellinja i en lagret fil som har tekst fra PDF (gjøres på nytt hver kjøring, billig)."""
    p = os.path.join(ROT, rad["fil"])
    if not os.path.exists(p) or (rad.get("tekstkilde") or "pdf") != "pdf":
        return
    hode, kropp = deling.les(rad["fil"])
    t, f, n = kvalitet(kropp)
    rad.update(tekstkilde="pdf", tabeller=str(t), figurer=str(f), tall_linjer=str(n))
    linje = varsel(t, f, n)
    linjer = [x for x in hode.split("\n") if not x.startswith("- Tekst:")]
    i = next((k for k, x in enumerate(linjer) if x.startswith("- Kudos:")), len(linjer))
    linjer.insert(i, linje)
    linjer = [x for x in linjer if not x.startswith("Teksten er hentet automatisk fra PDF-en")]
    deling.skriv(rad["fil"], "\n".join(linjer), kropp)


def arstall(tittel, publisert, o):
    """Året dokumentet legges under: publiseringsåret, eller året i tittelen når typen har "ar": "tittel"
    (tildelingsbrev ligger under budsjettåret de gjelder, ikke året de ble publisert)."""
    if o.get("ar") == "tittel":
        m = re.search(r"(?<!\d)(19|20)\d\d(?!\d)", tittel or "")
        if m:
            return m.group(0)
    return (publisert or "0000")[:4]


def filsti(o, ar, uuid, tittel):
    # Slutten av uuid-en skiller dokumentene; begynnelsen er lik for dokumenter lagt inn samtidig.
    return os.path.join("dokumenter", o["mappe"], ar, f"{uuid[-8:]}-{slug(tittel or '')}.md")


def flytt_til_riktig_ar(rader, typer):
    """Flytter lagrede filer som har fått ny plass, for eksempel etter at regelen for året eller filnavnet er endret."""
    flytt = []
    for r in rader.values():
        o = typer.get(r["type"])
        if not o:
            continue
        ar = arstall(r["tittel"], r["ar"], o)
        ny = filsti(o, ar, r["id"][3:], r["tittel"])
        if ny != r["fil"]:
            flytt.append((r, ar, ny))
    nye = [ny for _, _, ny in flytt]
    if len(set(nye)) != len(nye) or set(nye) & ({r["fil"] for r in rader.values()} - {r["fil"] for r, _, _ in flytt}):
        print("Flytting stoppet: to dokumenter ville fått samme filnavn")
        return
    for r, ar, ny in flytt:
        if os.path.exists(os.path.join(ROT, r["fil"])):
            os.makedirs(os.path.join(ROT, os.path.dirname(ny)), exist_ok=True)
            os.replace(os.path.join(ROT, r["fil"]), os.path.join(ROT, ny))
            if os.path.isdir(os.path.join(ROT, deling.mappe(r["fil"]))):
                os.replace(os.path.join(ROT, deling.mappe(r["fil"])), os.path.join(ROT, deling.mappe(ny)))
            gml = os.path.join(ROT, os.path.dirname(r["fil"]))
            if os.path.isdir(gml) and not os.listdir(gml):
                os.rmdir(gml)
        r["ar"], r["fil"] = ar, ny


def skriv_veiviser(rader, typer):
    """Skriver lista over dokumentene mellom AUTO-START og AUTO-SLUTT i VEIVISER.md."""
    if not os.path.exists(VEIVISER):
        return
    ut = ["<!-- AUTO-START: lages av verktoy/kudos_hent.py, rediger ikke for hånd -->", ""]
    for t, o in typer.items():
        av = [r for r in rader.values() if r["type"] == t]
        if not av:
            continue
        ut += [f"### {t} ({len(av)})", ""]
        if t == "Tildelingsbrev":
            per = {}
            for r in av:
                for m in liste(r.get("mottakere")) or ["(ukjent mottaker)"]:
                    per.setdefault(m, Counter())[r["ar"]] += 1
            ut += [f"Mappe: `dokumenter/{o['mappe']}/<år>/`. Søk i `dokumenter.tsv` (kolonnen `mottakere`) for å finne brevene til én mottaker. Brev og tillegg per mottaker og budsjettår:", "",
                   "| Mottaker | Brev | År |", "|---|---|---|"]
            for m, c in sorted(per.items(), key=lambda x: (-sum(x[1].values()), x[0])):
                ut.append(f"| {m} | {sum(c.values())} | {', '.join(f'{a} ({n})' for a, n in sorted(c.items()))} |")
        else:
            ut += ["| År | Tittel | Innhold | Fil |", "|---|---|---|---|"]
            for r in sorted(av, key=lambda r: (r["ar"], r["tittel"]), reverse=True):
                inn = (r.get("sammendrag") or "").replace("|", "/")[:220]
                ut.append(f"| {r['ar']} | {r['tittel'].replace('|', '/')} | {inn} | `{r['fil']}` |")
        ut.append("")
    ut.append("<!-- AUTO-SLUTT -->")
    tekst = open(VEIVISER, encoding="utf-8").read()
    a, b = tekst.find("<!-- AUTO-START"), tekst.find("<!-- AUTO-SLUTT -->")
    if a < 0 or b < 0:
        return
    open(VEIVISER, "w", encoding="utf-8").write(tekst[:a] + "\n".join(ut) + tekst[b + len("<!-- AUTO-SLUTT -->"):])


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


def pdf_til_tekst(data, valg=()):
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "f.pdf")
        open(p, "wb").write(data)
        r = subprocess.run(["pdftotext", "-enc", "UTF-8", *valg, p, "-"], capture_output=True, timeout=300)
        tekst = r.stdout.decode("utf-8", "replace")
    # Hver side i PDF-en får et merke, [Side N], så svar kan lenke til riktig side (PDF-lenke + #page=N).
    sider = tekst.split("\f")
    while sider and not sider[-1].strip():
        sider.pop()
    tekst = "".join(f"\n\n[Side {i}]\n\n{side}" for i, side in enumerate(sider, 1))
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
    if "--test" in sys.argv:   # lagre teksten fra pdftotext med og uten -layout for noen id-er, til sammenligning
        ids = sys.argv[sys.argv.index("--test") + 1].split()
        os.makedirs(os.path.join(ROT, "tester"), exist_ok=True)
        for r in alle:
            if "KU-" + r["uuid"] not in ids:
                continue
            pdf = next((f for f in liste(r.get("file_urls")) if f.lower().endswith(".pdf")), "")
            fil = hent(pdf, forsok=3, pause=20) if pdf else b""
            for navn, valg in (("vanlig", []), ("layout", ["-layout"])):
                tekst = pdf_til_tekst(fil, valg) if fil else ""
                with open(os.path.join(ROT, "tester", f"{r['uuid'][-8:]}-{slug(r.get('title') or '')}-{navn}.txt"), "w", encoding="utf-8") as f:
                    f.write(tekst + "\n")
            print(r.get("title"), len(fil), "byte")
        return 0
    if "--liste" in sys.argv:   # skriv ut alle dokumenter av én type fra et år, uten å lagre noe
        t = sys.argv[sys.argv.index("--liste") + 1]
        if t == "typer":   # skriv ut hvilke dokumenttyper eksporten har
            for k, n in Counter(r.get("type") for r in alle).most_common():
                print(f"{n}\t{k}")
            return 0
        fra = int(sys.argv[sys.argv.index("--fra") + 1]) if "--fra" in sys.argv else 0
        for r in sorted(alle, key=lambda r: r.get("publish_date") or "", reverse=True):
            sok = sys.argv[sys.argv.index("--sok") + 1] if "--sok" in sys.argv else ""
            tekst = " ".join([r.get("title") or "", r.get("abstract") or "", r.get("owners") or ""])
            if sok and not re.search(sok, tekst, re.I):
                continue
            if r.get("type") in t.split(",") and int((r.get("publish_date") or "0")[:4] or 0) >= fra:
                print("|".join([(r.get("publish_date") or "")[:10], r.get("type") or "", "KU-" + r["uuid"], (r.get("title") or "").strip(), ",".join(liste(r.get("owners"))),
                                re.sub(r"\s+", " ", r.get("abstract") or "")[:200]]))
        return 0
    valgte = []
    for t, o in typer.items():
        av_type = [r for r in alle if r.get("type") == t]
        egne = set(o.get("eiere", eiere))   # typen kan ha egne eiere; tom liste betyr alle eiere
        mine = [r for r in av_type if (not egne or egne & set(liste(r.get("owners"))))
                and int((r.get("publish_date") or "0")[:4] or 0) >= o.get("fra_ar", 0)]
        if o.get("ta_med") or o.get("ta_med_start"):
            # ta_med: nøyaktig tittel (for eksempel «NOU 2025: 1»); ta_med_start: tittelen begynner slik
            def nokkel(r):
                t_ = (r.get("title") or "").strip()
                if t_ in set(o.get("ta_med", [])):
                    return t_
                return next((s for s in o.get("ta_med_start", []) if t_.lower().startswith(s.lower())), None)
            mine = [r for r in mine if nokkel(r)]
            # Samme tittel kan stå flere ganger (engelsk utgave, kopi uten sammendrag): behold én,
            # helst norsk, med sammendrag og PDF.
            beste = {}
            for r in mine:
                t_ = nokkel(r)
                poeng = ((r.get("language") or "").lower() not in ("en", "eng", "engelsk", "english"),
                         bool(r.get("abstract")), any(f.lower().endswith(".pdf") for f in liste(r.get("file_urls"))),
                         r.get("publish_date") or "")
                if t_ not in beste or poeng > beste[t_][0]:
                    beste[t_] = (poeng, r)
            mine = [r for _, r in beste.values()]
        print(f"{t}: {len(av_type)} i alt, {len(mine)} valgt")
        if diagnose:
            print("  Vanligste eiere:", Counter(e for r in av_type for e in liste(r.get("owners"))).most_common(15))
            print("  Mottakere blant de valgte:", Counter(e for r in mine for e in liste(r.get("recipients"))).most_common(60))
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
        ny_tekst = rid in oversikt and "--ny-tekst" in sys.argv and (oversikt[rid].get("tekstkilde") or "pdf") == "pdf" \
            and not re.search(r"(?m)^\[Side 1\]$", deling.les(oversikt[rid]["fil"])[1])
        if rid in oversikt and not ny_tekst:   # lagret fra før: fyll inn felt som kom til senere, uten å hente på nytt
            gml = oversikt[rid]
            side = (r.get("external_public_url") or "").strip()
            if side and not gml.get("side"):
                gml["side"] = side
                p = os.path.join(ROT, gml["fil"])
                if os.path.exists(p):
                    topp, kropp = deling.les(gml["fil"])
                    if "- Les hele dokumentet:" not in topp:
                        deling.skriv(gml["fil"], topp.replace("\n- Type:", f"\n- Les hele dokumentet: {side}\n- Type:", 1), kropp)
            if not gml.get("sammendrag"):
                gml["sammendrag"] = sammendrag(r)
            if not gml.get("mottakere"):
                gml["mottakere"] = "|".join(liste(r.get("recipients")))
            continue
        if nye >= maks or time.time() - START > MINUTTER * 60:   # stopp i tide, så det som er hentet blir lagret
            break
        ar = arstall(r.get("title"), r.get("publish_date"), o)
        pdf = next((f for f in liste(r.get("file_urls")) if f.lower().endswith(".pdf")), "")
        if not pdf:
            feil.append(f"Ingen PDF: {r.get('title')} ({rid})")
            continue
        fil = hent(pdf, forsok=3, pause=20)
        time.sleep(2)
        # Sidelayout holder tabellradene samlet, men blander spaltene i dokumenter med to spalter.
        tekst = pdf_til_tekst(fil, ["-layout"] if o.get("layout") else []) if fil else ""
        if len(tekst) < 200:
            feil.append(f"Ingen tekst ({len(fil)} byte): {r.get('title')} ({rid})")
            continue
        sti = filsti(o, ar, r["uuid"], r.get("title"))
        os.makedirs(os.path.join(ROT, os.path.dirname(sti)), exist_ok=True)
        kudos = "https://kudos.dfo.no/dokument/" + r["uuid"]
        kilde = (liste(r.get("source_file_urls")) or [""])[0]
        side = (r.get("external_public_url") or "").strip()
        hode = [f"# {r.get('title') or ''}", "", f"- Type: {t}", f"- Publisert: {r.get('publish_date') or ''}",
                f"- Eier: {', '.join(liste(r.get('owners')))}"]
        if liste(r.get("recipients")):
            hode.append(f"- Mottaker: {', '.join(liste(r.get('recipients')))}")
        if liste(r.get("authoring_actors")):
            hode.append(f"- Utført av: {', '.join(liste(r.get('authoring_actors')))}")
        hode += [f"- Les hele dokumentet: {side}" if side else "", f"- Original-PDF: {kilde}" if kilde else f"- PDF: {pdf}", f"- Kudos: {kudos}", f"- Hentet: {time.strftime('%Y-%m-%d')}",
                 "", "---", ""]
        deling.skriv(sti, "\n".join(x for x in hode[:-3] if x is not None), tekst)
        oversikt[rid] = {"id": rid, "type": t, "ar": ar, "tittel": (r.get("title") or "").replace("\t", " "), "sammendrag": sammendrag(r),
                         "eiere": "|".join(liste(r.get("owners"))), "mottakere": "|".join(liste(r.get("recipients"))), "utforere": "|".join(liste(r.get("authoring_actors"))),
                         "fil": sti, "kudos": kudos, "side": side, "kilde": kilde, "ord": str(len(tekst.split())), "hentet": time.strftime("%Y-%m-%d")}
        nye += 1
        print(f"  {sti} ({len(tekst.split())} ord)", flush=True)
    flytt_til_riktig_ar(oversikt, typer)
    for rad in oversikt.values():
        merk_kvalitet(rad)
        deling.ordne(rad["fil"])
    skriv_oversikt(oversikt)
    skriv_veiviser(oversikt, typer)
    gjenstar = sum(1 for _, _, r in valgte if "KU-" + r["uuid"] not in oversikt) - len(feil)
    with open(os.path.join(ROT, "kudos-rapport.txt"), "w", encoding="utf-8") as f:
        f.write(f"Dokumenter fra Kudos: {nye} nye, {len(oversikt)} i alt\n\n")
        f.write("\n".join(f"- {x}" for x in feil[:50]) + ("\n" if feil else ""))
    print(f"{nye} nye, {len(oversikt)} i alt, {len(feil)} uten tekst, om lag {max(gjenstar, 0)} gjenstår")
    return 0


if __name__ == "__main__":
    sys.exit(main())
