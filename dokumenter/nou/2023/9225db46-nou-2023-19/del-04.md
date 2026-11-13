# NOU 2023: 19, del 4 av 15

- Hele dokumentet med innholdsfortegnelse: dokumenter/nou/2023/9225db46-nou-2023-19.md
- Les hele dokumentet: https://www.regjeringen.no/no/dokumenter/nou-2023-19/id2982722/
- Original-PDF: https://www.regjeringen.no/contentassets/c0471fcd36e8481a92b627f54a702c7e/no/pdfs/nou202320230019000dddpdfs.pdf
- Tekst: fra Word-fil lastet opp 2026-11-13, ikke fra PDF. Tabellene er med. Figurer er bare med som titler, så tall som bare finnes i en figur, må leses i originalen.

---

# Datatyper og datakvalitet i læringsanalyse

En forutsetning for all læringsanalyse er å ha tilgang til relevante data som har potensiale til å gi oss innsikt i læringen og undervisningen. Kvaliteten på dataene er alltid avgjørende for kvaliteten på innsikten dataene kan gi. I dette kapitlet vil vi se nærmere på hva slags datatyper som er relevant for læringsanalyse og hva som menes med god datakvalitet i forbindelse med læringsanalyse.

## Hva er data?

Det finnes mange ulike definisjoner av data avhengig av hvilket perspektiv en har. Ofte oppfattes *data* som «en måte å lagre, overføre og prosessere informasjon i form av et bestemt dataformat»[^15].

I denne sammenhengen er vi først og fremst opptatt av data som kan inngå i læringsanalyse. I løpet av en vanlig dag bruker mange elever og studenter digitale læringsplattformer, apper og programmer. Slike interaksjoner med digitale enheter skaper *digitale data.* Så å si alt vi gjør på digitale enheter, etterlater spor og genererer data. For eksempel skapes digitale data hver gang en elev trykker på skjermen i en språkapp, eller hver gang en student ser på en instruksjonsvideo. I tillegg til slike spor kan digitale data være basert på analoge signaler fra for eksempel sensorer, som så blir digitalisert. Når denne typen data inkluderes i analysen, kalles det en *multimodal* læringsanalyse (Giannakos mfl., 2022).

For å få et best mulig utgangspunkt for å tolke dataene er vi avhengige av informasjon om selve dataene og måten de ble samlet inn på. *Metadata* blir ofte beskrevet som «data om data» og gir beskrivende informasjon om de dataene vi har. Et eksempel på metadata kan være datoen et digitalt bilde er tatt, når et bestemt dokument ble opprettet eller sist ble endret. *Konteksten* dataene ble samlet i, er også viktig for å tolke dataene. For læringsanalyse vil den pedagogiske konteksten være relevant, for eksempel om en oppgave elevene har skrevet, var en samarbeidsoppgave, eller hva slags undervisning studentene hadde rett før de tok en bestemt flervalgstest.

### Data sett fra ulike perspektiver

Fra et *teknisk perspektiv* må ulike datatyper lagres i en database eller i et filsystem for å kunne analyseres av statistisk programvare eller algoritmer. Dataene lagres da i et *dataformat* som er lesbart og forståelig for programvaren i en datamaskin. Dataformater kan eksempelvis være

- numeriske (heltall eller desimaltall)

- tekst (for eksempel ren tekst, html, xml)

- lyd (for eksempel wav, aiff)

- visuelle (for eksempel bilder som jpeg, png, tiff eller video som mpv4)

- instrumentspesifikke (for eksempel biosensor, blikksporing, bevegelsessensor)

Fra et *teknisk perspektiv* er også disse fagtermene om data viktige:

- *Metadata* er data om data, eller data som definerer eller beskriver andre data (for eksempel tidspunktet dataene ble registrert, hva slags kamera som er brukt for å ta et bilde eller hvilket læreverk de aktuelle dataene kommer fra).

- *Multimodale data* er kombinasjoner av forskjellige modaliteter (for eksempel tekst, bilde, sensordata, blikksporingsdata).

- *Datasett* er en strukturert samling av data (for eksempel bestående av studentnummer, karakter og tid brukt) eller en organisert samling ustrukturerte data.

Fra et *analytisk perspektiv* kan vi kategorisere data som

- *rådata* (ubehandlede data som er registrert og samlet inn, men ikke gjort noe med) eller *bearbeidede data* (data som er bearbeidet, for eksempel ved at de er gjort om til et format som tillater visualisering, sammenstilling og sammenligning med andre data)

- *sanntidsdata* (data som presenteres for brukeren med en gang de er registrert) eller *historiske data* (data som er registrert på et tidligere tidspunkt)

- *strukturerte data* (data som er organisert og definert etter bestemte regler, noe som er nødvendig for utveksling og samhandling), *ustrukturerte data* (uorganiserte data) eller *semistrukturerte data* (en blanding av strukturerte og ustrukturerte data)

Fra et *praktisk perspektiv* kan vi snakke om:

- *rådata,* for eksempel

  - *innholdsdata* (skapes bevisst av mennesker, for eksempel når en oppgir personlige opplysninger for å opprette en konto for å bruke en app eller laste opp en video på en plattform) eller

  - *sensordata* (data registrert av en sensor, for eksempel når bevegelsene dine registreres av en smartklokke)

- *analytiske data* (behandlet data opprettet av maskiner etter menneske-maskin-interaksjon)

- *funksjonelle data* (data opprettet av en maskin for å muliggjøre kommunikasjon mellom maskin og maskin)

Fra et *læringsanalyseperspektiv* bruker vi ofte begrepet *aktivitetsdata* (Kay og Harmelen, 2014). Denne typen data er definert som spor av menneskelige handlinger i den elektroniske eller fysiske verden som kan fanges opp av en datamaskin eller digital enhet. Termen aktivitetsdata rommer både synlige rådata og analytiske data og usynlige funksjonelle data. De ulike typene av data gjenspeiles også i definisjonen fra rapporten *Å lykkes med åpenhet* der aktivitetsdata fra adaptive læremidler beskrives som «de opplysningene som skapes når en elev gjør oppgaver i et læremiddel. Dette kan være svaret som en elev gir på en oppgave, opplysninger om hvilken oppgave eleven har løst, hvor lang tid eleven brukte på oppgaven, og om eleven besvarte oppgaven korrekt eller feil» (Datatilsynet, 2022c, s. 3). Det genereres også metadata om situasjonen hvor dataene er samlet inn, for eksempel hva slags digital enhet som er brukt, eller hvilken Feide-ID[^16] som er pålogget.

Fra et *personvernperspektiv* betegnes data som *personopplysninger* når de kan brukes til å identifisere en person, enten direkte eller indirekte. Dette omfatter data som navn, adresse, fødselsdato, telefonnummer, e-postadresse, personnummer, passnummer eller andre identifikatorer som er unike hver for seg eller sammensatt med andre data. I læringsanalyse kan personopplysninger samles inn fra elever, studenter eller andre for å analysere og fremme læring og forbedre undervisning. Det er imidlertid viktig å sikre at personopplysningene blir behandlet på en lovlig, ansvarlig og etisk måte, og at det finnes egnede tekniske, administrative eller rettighetsfremmende tiltak for å etterleve kravene i personvernforordningen for å beskytte enkeltpersoners rettigheter og interesser.

Det er på langt nær slik at alle former for læringsanalyse har behov for å kunne identifisere ett enkelt individ. Data blir ofte aggregert på gruppe- eller organisasjonsnivå. *Aggregerte data* er data på et høyere nivå som man får ved å kombinere data fra et individnivå. Blant annet bruker ledelsesnivået, administratorer og forskere aggregerte data til en rekke ulike formål. For eksempel bruker de dem til å vurdere konsekvenser av tiltak, gjenkjenne trender og mønstre i prosesser og få relevant innsikt for å kunne ta strategiske beslutninger. Når data aggregeres til et gruppe- eller organisasjonsnivå, blir identiteten til det enkelte individet bare brukt når data sammenstilles til større datasett for analyse. Identiteten er ikke tilgjengelig ved de analysene som gjøres i ettertid.

## Data brukt i læringsanalyse

Dataene fra utdanningssektoren skapes fra et bredt spekter av kilder. En systematisk gjennomgang av ti studier om databruk i læringsanalyse i høyere utdanning i ulike land viser at de mest brukte dataene er aktivitetsdata, fulgt av data fra de studieadministrative systemene (for eksempel studentenes bakgrunnsinformasjon) og data fra vurdering (Samuelsen mfl., 2019).

Å kunne behandle data fra flere kilder uten at dataenes integritet går tapt når en sammenstiller ulike datasett, er viktig for å kunne skalere læringsanalysen. For å lykkes godt med dette er man avhengig av at data og datasett finnes i standardiserte formater. På denne måten sikrer man også såkalt *interoperabilitet* mellom de ulike applikasjonene som skal jobbe sammen, slik at de kan utveksle data sømløst.

Vi finner noen eksempler fra de siste årene der læringsanalyse tar i bruk multimodale data (Di Mitri mfl., 2017; Giannakos mfl., 2019; Worsley mfl., 2021). Multimodale data samles typisk inn fra datakilder som inneholder sensorer, for eksempel fysiologiske signalarmbånd og blikksporing, men også lyd og video. Ennå er bruken av sensordata i læringsanalyse på et tidlig stadium og står overfor tekniske utfordringer som blant annet synkronisering og dataintegrasjon (Samuelsen mfl., 2019). Det er i tillegg en rekke uutforskede etiske utfordringer knyttet til å bruke multimodale data, spesielt når det er mange datakilder involvert (Worsley mfl., 2020), eller når data inkluderer helseopplysninger (Martinez-Maldonado mfl., 2020).

Datahåndtering

Før noen kan analysere dataene, må de organiseres og lagres i et strukturert format som gjør at en applikasjon eller en algoritme greier å håndtere dem. De vanligste datalagringsteknologiene som brukes for læringsanalysedata, er relasjonsdatabaser, filer, regneark eller det som kalles «learning record stores», for eksempel den åpne kildekodeløsningen Learning Locker[^17]. I noen former for læringsanalyse er det ønskelig å sammenstille data fra ulike datakilder. Disse kan være lagret i ulike formater og ha ulike nivåer av struktur, eller det kan være sanntidsdata som inngår i analysen uten at de lagres. For å gjøre data med ulike formater tilgjengelige for å kunne håndteres videre, er det utviklet internasjonale standarder for datastrukturer. xAPI[^18] og IMS Caliper Analytics[^19] er eksempler på slike standarder. Dersom noen ønsker å strukturere data fra ulike datakilder til en analyse, trengs det en unik *identifikator* som kan knytte sammen dataene fra de ulike kildene. For eksempel går det an å bruke en students Feide-ID til å koble sammen data fra ulike kilder.

## Dataanalyse

Dataanalyse kan involvere en rekke teknikker og metoder. Noen eksempler er statistisk analyse, maskinlæring, datautvinning og datavisualisering. Dataanalyse kan brukes til å identifisere mønstre, trender og sammenhenger i dataene og til å teste hypoteser. Målet er å avdekke og presentere nyttig informasjon og gi støtte til beslutninger. Utviklerne kan også bruke algoritmer for å automatisere slike dataanalyseprosesser, redusere manuelle inngrep og gjøre analysen raskere.

Utvalgsskjevhet

En feilkilde som er spesielt aktuell for maskinlæring og kunstig intelligens, og som også er relevant for læringsanalyse, er det vi kaller *utvalgsskjevhet* (Kommunal- og moderniseringsdepartementet, 2020). Utvalgsskjevhet kan vi få om datasettene som algoritmene trener på, bare inneholder opplysninger om en del av det relevante datagrunnlaget. Det kan lede til at resultatene viser til assosiasjoner der de ikke finnes, eller ikke viser til assosiasjoner der de faktisk finnes (Larsen, 2020). På denne måten kan algoritmene være mindre effektive, eller de kan bidra til å opprettholde eller forsterke samfunnsmessige skjevheter basert på for eksempel kjønn, bakgrunn eller sosioøkonomisk status.

For læringsanalyse innebærer denne utvalgsskjevheten en fare for at læringsanalysealgoritmene bidrar til å opprettholde og forsterke eksisterende ulikheter og diskriminering i utdanningen (Lester mfl., 2019; Selwyn, 2022). For å redusere skjevheter i læringsanalysealgoritmene er det viktig å nøye vurdere dataene som brukes til å trene algoritmene. Det hører også med å forsikre seg om at algoritmene regelmessig revideres og testes for skjevheter. Ved å i forkant innarbeide etiske prinsipper for hvordan læringsanalyse skal være utformet, og hvordan læringsanalyse skal gjennomføres, bidrar det til å fremme rettferdighet og likeverd i utdanningen.

## Datakvalitet

Hva en analyse faktisk kan fortelle oss om læring og undervisning, er alltid uløselig knyttet til kvaliteten på dataene vi har tilgjengelig. Datakvalitet handler om hvorvidt eller hvor godt dataene stemmer overens med den situasjonen eller aktiviteten de representerer. Datakvalitet dreier seg altså blant annet om å sikre korrekte, komplette og aktuelle data. En må også se til at dataene ikke blir endret eller manipulert, tilsiktet eller utilsiktet, på måter som påvirker sluttresultatet. Dataene må være fullstendige, konsistente, nøyaktige, tidsaktuelle, valide og unike for at vi kan si vi har god datakvalitet (Pipino mfl., 2002). Av disse seks prinsippene er det ofte enklest å vurdere om dataene er fullstendige og valide, dernest om de er tidsaktuelle og unike. Det som oftest er vanskeligst å finne ut av, er om dataene er nøyaktige og konsistente.

Fullstendige data

Et viktig prinsipp for datakvalitet er fullstendige data, som refererer til at ingen data mangler. Det vil si at alle data som man forventet å samle inn faktisk er til stede. Det er ulike årsaker til at man får ufullstendige data, for eksempel manglende verdier eller at det skjer feil når dataene blir lagt inn. Manglende data eller ufullstendige registreringer kan føre til skjeve analyser, feilaktige konklusjoner eller unøyaktige prediksjoner. Framgangsmåten for å sikre seg at dataene er fullstendige, er å ha klare prosedyrer for datainnsamling, å validere dataenes nøyaktighet og konsistens og å rense dataene på en måte som tar for seg manglende verdier og ufullstendige registreringer. I læringsanalyse er det helt avgjørende å sørge for fullstendige data for å få meningsfull innsikt i elevenes og studentenes læring.

Konsistente data

Konsistente data handler om å samle inn de forventede versjonene av dataene og at de ikke inneholder motsetninger eller systematiske ujevnheter. Et enkelt eksempel som kan illustrere dette, er dersom en underviser ønsker å bruke informasjon om når studentene gjorde en læringsaktivitet. Hvis da datoene for når studentene deltok, er registrert i ulike datoformater, fører den inkonsekvente registreringen til ubrukelige data. Det blir vanskelig å skjønne hva dataene egentlig betyr, eller å sammenstille dem på meningsfylte måter.

Nøyaktige data

Nøyaktige data refererer til i hvilken grad dataene representerer det virkelige fenomenet eller informasjonen de er ment å representere (konstruktvaliditet), og hvor nær dataverdiene er de sanne verdiene for det underliggende fenomenet (validitet). Nøyaktige data er dermed data som er korrekte, presise, og de representerer det de er ment å representere. Framgangsmåten for å forbedre nøyaktigheten handler om å kvalitetssikre datakildene, å verifisere integritet og konsistens og om metoder for å rense og validere for å oppdage og korrigere feil. I læringsanalyse er det avgjørende med nøyaktige data for å gi pålitelig og gyldig innsikt i elevenes og studentenes læring.

Tidsaktuelle data

Tidsaktuelle data handler om at dataene må være samlet inn og tilgjengelige på et tidspunkt som gjør at informasjonen kan brukes på en god måte. I pedagogiske sammenhenger dreier dette seg ofte om hvor tett på læringssituasjonen dataene foreligger. Er ikke dataene fra en gitt læringssituasjon tilgjengelige på rett tidspunkt, vil ikke læreren, underviseren eller andre kunne bruke informasjonen til å forbedre elevenes eller studentenes opplæring.

Valide data

Valide data vil si at de må være gyldige – de må si noe om det de faktisk er ment å si noe om. Dersom målet med en læringsapp, for eksempel en kviss med flervalg, er å si noe om hva elevene kan om et gitt faglig tema, og elevene merker seg at det lengste svaret alltid er korrekt, og følgelig alltid velger dette uavhengig av innholdet, vil ikke dataene være valide. Dataene vil da ikke være et gyldig mål på elevens faglige innsikt i temaet.

Unike data

Unike data handler helt enkelt om at dataene ikke må registreres flere ganger enn de skal, altså at duplikater unngås.
