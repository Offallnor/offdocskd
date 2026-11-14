# Innboks for bedre tekst

Legg en Word-fil (`.docx`), epub, ODT, RTF (også zip-fila med RTF som regjeringen.no har for eldre dokumenter, `…rtfz.zip`) eller en lagret HTML-side her når et dokument i basen har rotete tabeller fra PDF-en. En jobb gjør filen om til tekst med tabeller, erstatter PDF-teksten i dokumentet og sletter filen fra innboksen. Toppen av dokumentet med lenkene beholdes.

**Filnavn.** Behold navnet filen har fra regjeringen.no, for eksempel `nou202520250001_kdddddocx.docx`. Det følger navnet på PDF-filen, så jobben finner riktig dokument. Har filen et annet navn, gi den tittelen i basen (for eksempel `NOU 2019 2.docx`) eller id-en: de åtte tegnene foran tittelen i filnavnet under `dokumenter/`.

**Kontroll.** Ordtallet sammenlignes med PDF-teksten. Avviker det mye (under 70 eller over 150 prosent), leses filen ikke inn, fordi det kan være feil fil. Er den riktig, kjør jobben «Les inn filer fra innboksen» for hånd med «tving».

**Resultat** står i `rapport.md` i denne mappen. Filer som ikke ble lest inn, blir liggende her.

Last opp som offallnor-bot. Repoet er åpent, så legg bare inn offentlige dokumenter. Filen blir liggende i historikken selv om den slettes, så unngå filer over 20 MB.
