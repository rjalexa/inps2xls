"""
Legge un file JSON derivato dal file XML dei contributi INPS (inserire nome nel codice)
Genera un file excel con la somma dei contributi e delle relative settimane anno per anno

Per generare il file JSON:
* Accedere con opportuna autenticazione al servizio MyINPS
* Dalla barra verticale di sinistra:
*   Fascicolo previdenziale
*   Consultazione estratto conto unificato
* Scorrere in fondo alla pagina e cliccare sul bottone XML
* Salvato l'XML potete andare as es. su https://codebeautify.org/xmltojson
* Caricare l'XML e scaricare il JSON

Prerequisiti:
Librerie python json, pandas ed openpyxl
"""
from datetime import datetime
import json
import pandas as pd

FILE_JSON_DA_LEGGERE = "CODICEFISCALE.json"

with open(FILE_JSON_DA_LEGGERE, "r", encoding="utf8") as f:
    data = json.load(f)

df = pd.DataFrame(
    {
        "dal": pd.Series(dtype="str"),
        "al": pd.Series(dtype="str"),
        "retribeuro": pd.Series(dtype="float"),
        "tipocontr": pd.Series(dtype="str"),
        "unitacontr": pd.Series(dtype="str"),
        "qtacontrcalcolo": pd.Series(dtype="float"),
    }
)

i = 0
for contributo in data["EstrattoConto"]["RegimeGenerale"]["Contributi"][
    "RigaContributi"
]:
    dal = datetime(
        year=int(contributo["Dal"]["Anno"]),
        month=int(contributo["Dal"]["Mese"]),
        day=int(contributo["Dal"]["Giorno"]),
    )
    al = datetime(
        year=int(contributo["Al"]["Anno"]),
        month=int(contributo["Al"]["Mese"]),
        day=int(contributo["Al"]["Giorno"]),
    )
    retribeuro = float(contributo["RetribuzioneEuro"])
    tipocontr = contributo["TipoContribuzione"]
    unitacontr = contributo["TipoContributo"]
    qtacontrcalcolo = float(contributo["ContributiUtiliCalcolo"])
    # normalizzare un paio di casi strani in settimane
    if unitacontr == "Anni":
        qtacontrcalcolo = float(qtacontrcalcolo) * 52
        unitacontr = "Settimane"
    elif unitacontr == "Mesi":
        if qtacontrcalcolo == float("6.0"):
            qtacontrcalcolo = float("26.0")
            unitacontr = "Settimane"
    df.loc[i] = [dal, al, retribeuro, tipocontr, unitacontr, qtacontrcalcolo]
    i += 1

df.groupby(pd.to_datetime(df["dal"]).dt.year).sum(numeric_only=True).to_excel(
    "contributi.xlsx"
)
