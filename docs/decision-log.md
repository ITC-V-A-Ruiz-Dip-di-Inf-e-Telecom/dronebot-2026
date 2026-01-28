# Decision Log (Registro decisioni)

Questo documento raccoglie le decisioni tecniche principali, con motivazioni e impatti, per garantire tracciabilità e supportare la valutazione della giuria.

## DR-001 — Repository e processo di sviluppo
**Decisione**: usare una repository GitHub pubblica, con versionamento per milestone (tag/release), documentazione e changelog.  
**Motivazione**: tracciabilità del percorso, collaborazione del team, evidenza dell’evoluzione del progetto.  
**Impatto**: richiede disciplina minima su commit/tag, ma aumenta qualità e valutabilità.

## DR-002 — Separazione alimentazioni (stabilità real-time)
**Decisione**: alimentazioni separate per:
- motori (batteria dedicata),
- Arduino (batteria dedicata),
- Raspberry Pi + LiDAR (5V stabile dedicato, preferibilmente powerbank o buck 5V ad alta corrente).  
**Motivazione**: evitare brownout, reset intermittenti e disturbi sul regolatore Arduino in presenza di carichi elevati (motori, USB, LiDAR).  
**Impatto**: più complessità di cablaggio, ma maggiore affidabilità in gara.

**Regola d’oro**: “Un microcontrollore non è un alimentatore. Se un dispositivo consuma più di 100–150 mA, va alimentato a parte.”

## DR-003 — Architettura di controllo (divisione responsabilità)
**Decisione**: Raspberry Pi gestisce percezione e decisione (camera + LiDAR), Arduino gestisce attuazione e safety (motori + watchdog + stop emergenza).  
**Motivazione**: Arduino è più adatto al controllo real-time dei motori e alle funzioni di sicurezza; Raspberry è più adatto a vision e LiDAR.  
**Impatto**: interfaccia Raspberry→Arduino via USB seriale; firmware Arduino semplice e robusto.
