# ChessRepertoireGenerator

## How to
```bash
cd src/
python main.py example.yaml
```

## Configurazione (.yaml)

```yaml
# Variante di scacchi per cui generare il repertorio (le alternative sono anti-chess ecc...)
variant: standard

# Cadenza di gioco da considerare nel db di lichess
speeds:
  - blitz
  - rapid

# Valori di rating per cui il repertorio è stato generato
ratings:
  - 2000
  - 2200

# Nome del file PGN in cui verranno salvate le partite del repertorio
PgnName: RepertoireExample.pgn

# Nome dell'evento a cui il repertorio è associato
Event: ChessRepertoireGenerator

# Definizione del colore del giocatore per cui viene costruito il repertorio
Color: White

# Mossa iniziale del bianco del repertorio
WhiteStartingMove: b1c3

# Profondità (numero di semi-mosse) massima di ricerca dell'engine di scacchi utilizzato per la generazione del repertorio
MaxDepth: 11

# Numero massimo di linee di analisi dell'engine da considerare
EngineLines: 3

# Soglia di valutazione dell'engine al di sopra della quale le mosse vengono considerate invalide
# es: scarto la mossa ha una valutazione del motore non accettabile (< -1 e tocca la bianco o > 1 e tocca al nero)
EngineThreshold: 0.8

# Sommato totale della frequenza delle mosse avversarie da considera (es: 85 --> considero tutte le mosse che coprono l'85% minimo delle mosse giocate)
FreqThreshold: 85
```