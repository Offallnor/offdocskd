# Innboks for bedre tekst

Legg en Word-fil (`.docx`), epub, ODT eller en lagret HTML-side her når et dokument i basen har rotete tabeller fra PDF-en. En jobb gjør filen om til tekst med tabeller, erstatter PDF-teksten i dokumentet og sletter filen fra innboksen. Toppen av dokumentet med lenkene beholdes.

**Filnavn.** Gi filen samme navn som tittelen i basen, for eksempel `NOU 2019 2.docx` eller `Meld. St. 14 (2022–2023).epub` (tegn som kolon kan sløyfes). Har flere dokumenter samme tittel, som tildelingsbrev, bruk id-en: de åtte tegnene foran tittelen i filnavnet under `dokumenter/`, for eksempel `94749193.docx`.

**Kontroll.** Ordtallet sammenlignes med PDF-teksten. Avviker det mye (under 70 eller over 150 prosent), leses filen ikke inn, fordi det kan være feil fil. Er den riktig, kjør jobben «Les inn filer fra innboksen» for hånd med «tving».

**Resultat** står i `rapport.md` i denne mappen. Filer som ikke ble lest inn, blir liggende her.

Last opp som offallnor-bot. Repoet er åpent, så legg bare inn offentlige dokumenter. Filen blir liggende i historikken selv om den slettes, så unngå filer over 20 MB.
