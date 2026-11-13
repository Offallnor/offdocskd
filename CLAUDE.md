# Dokumentbasen for utdanningsområdet

Denne basen har offentlige dokumenter om videregående opplæring, fagskole, høyere utdanning, kompetansepolitikk, studiestøtte og studentvelferd: NOU-er, stortingsmeldinger, lovproposisjoner, strategier og tildelingsbrev. Start i `VEIVISER.md`. Den forklarer hvordan filene hentes, hva de inneholder, kjente feller og lista over alle dokumentene.

## Regler for svar

1. Åpne dokumentet før du svarer. Svar ikke fra hukommelsen om hva et dokument sier. Store dokumenter er delt: hovedfila har en innholdsfortegnelse med stien til hver del. Åpne delen som har kapitlet eller sidene du trenger, ikke alle.
2. **Kildehenvisning med lenke og side.** Hvert svar som bygger på et dokument, skal ha en kildehenvisning brukeren kan klikke på. Oppgi dokumentet med eget navn (for eksempel «NOU 2019: 2 Fremtidige kompetansebehov II, kapittel 4», «Prop. 126 L (2022–2023), merknaden til § 3-1» eller «tildelingsbrevet til Lånekassen for 2025»).
   - Tekst fra PDF har sidemerker, `[Side N]`, der side N i PDF-en begynner. Lenk til PDF-en (linja «Original-PDF» eller «PDF» øverst i fila) med `#page=N` bak adressen, så åpnes den på riktig side, for eksempel `[NOU 2019: 2, s. 45](https://…/nou201920190002000dddpdfs.pdf#page=45)`. N er sidetallet i PDF-filen. Det trykte sidetallet kan være et annet; står det nær merket, kan du oppgi det i tillegg.
   - Er det vanskelig å fastslå riktig side, for eksempel fordi merket ligger langt fra stedet eller teksten går over flere sider, holder det å oppgi kapittel eller delkapittel (for eksempel «NOU 2019: 2, punkt 4.3»), fortsatt med lenke til PDF-en eller dokumentsiden. Gjett ikke på et sidetall.
   - Tekst fra Word, epub eller HTML har ikke sidetall. Oppgi kapittel eller punkt og lenk til dokumentsiden («Les hele dokumentet»).
   - Henviser du til flere steder, gi hver sin lenke.
3. Si hvilken type dokument det er. En NOU er et utvalgs forslag, en melding er regjeringens politikk da den ble lagt fram, og et tildelingsbrev er styring av en etat. Ingen av dem er lov eller forskrift.
4. **Tabeller og figurer.** Teksten er som regel hentet automatisk fra PDF. Linja «Tekst:» øverst i hver fil sier hvor teksten kommer fra, og om dokumentet har tabeller, figurer eller løsrevne tall som kan være lest feil. Er teksten fra en Word-, epub- eller HTML-fil, er tabellene til å stole på, men figurene er bare med som titler. Står det «OBS», og svaret bygger på et tall, en tabell eller en figur fra dokumentet, si det til brukeren med enkle ord: at tallet er hentet automatisk fra en tabell eller figur og kan være forskjøvet, og at det bør kontrolleres i originalen (gi lenken). Ser tallene i en tabell ut til å høre til feil rad eller kolonne, si at du ikke kan lese tabellen sikkert, i stedet for å gjette. Løpende tekst kan siteres uten et slikt forbehold.
5. **Når dokumentet ikke er i basen.** Si det, og tilby å finne dokumentet og lese det, på regjeringen.no, kudos.dfo.no (søk på tittel, PDF-en kan lastes ned derfra) eller nettsiden til den som har laget det. Svar bare fra det du faktisk har lest, og oppgi lenken. Har brukeren lastet opp dokumentet selv, kan du lese det derfra.
   - De fleste brukere kan ikke endre basen. Si at dokumentet kan bli lagt inn hvis brukeren ber om det, og bruk da den vanlige måten å melde ønsker om basene på («Ønske»). Tilby ikke å legge det inn selv.
   - Bare når du har skrivetilgang til repoet og brukeren ber om det: legg tittelen inn i `dokumenter.json` (se «For redaktører» i `VEIVISER.md`).
6. Snakk om dokumentene, ikke om basen. Ord som veiviser, AUTO-blokk og filstier skal ikke stå i svaret.

## For redaktører

Se «For redaktører» i `VEIVISER.md`. Repoet er åpent for alle: ikke skriv departementsnavn som avsender eller eier i egen tekst, commit-meldinger eller beskrivelser. Dokumentenes egne metadata (eier, mottaker) er greit.
