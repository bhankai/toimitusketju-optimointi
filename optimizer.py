"""
optimizer.py — Tuotannon ja kuljetuksen optimointi PuLP:lla.

Ratkaisee lineaarisen ohjelmoinnin ongelman:
- Päätösmuuttujat: x_ij = kuljetetut yksiköt tehtaalta i asiakkaalle j
- Tavoite: minimoi (tuotantokustannus + kuljetuskustannus) yhteensä
- Rajoitteet: kapasiteetti tehtaittain, kysyntä asiakkaittain
"""

import pandas as pd
import pulp

from data import tehtaat, asiakkaat, laske_kuljetuskustannukset


def ratkaise_optimointi(
    tehtaat: pd.DataFrame = tehtaat,
    asiakkaat: pd.DataFrame = asiakkaat,
) -> dict:
    kuljetus = laske_kuljetuskustannukset()
    # kuljetus on DataFrame jossa rivit=tehtaiden nimet, sarakkeet=asiakkaiden nimet

    tehdas_nimet = tehtaat["nimi"].tolist()
    asiakas_nimet = asiakkaat["nimi"].tolist()

  
    kapasiteetit = dict(zip(tehtaat["nimi"], tehtaat["kapasiteetti"]))
    tuotantokustannukset = dict(zip(tehtaat["nimi"], tehtaat["tuotantokustannus"]))
    kysynnat = dict(zip(asiakkaat["nimi"], asiakkaat["kysynta"]))

   
    malli = pulp.LpProblem("PohjolaFood_toimitusketju", pulp.LpMinimize)
    x = pulp.LpVariable.dicts(
        "virta",
        (tehdas_nimet, asiakas_nimet),
        lowBound=0,       # ei-negatiivisuus
        cat="Continuous", # jatkuva muuttuja
    )


    malli += pulp.lpSum(
        (tuotantokustannukset[i] + kuljetus.loc[i, j]) * x[i][j]
        for i in tehdas_nimet
        for j in asiakas_nimet
    ), "Kokonaiskustannus"

    
    for i in tehdas_nimet:
        malli += (
            pulp.lpSum(x[i][j] for j in asiakas_nimet) <= kapasiteetit[i],
            f"Kapasiteetti_{i}",
        )

    
    for j in asiakas_nimet:
        malli += (
            pulp.lpSum(x[i][j] for i in tehdas_nimet) == kysynnat[j],
            f"Kysynta_{j}",
        )

    
    malli.solve(pulp.PULP_CBC_CMD(msg=0))

    status = pulp.LpStatus[malli.status]

    
    virtaukset = pd.DataFrame(
        [[x[i][j].value() for j in asiakas_nimet] for i in tehdas_nimet],
        index=tehdas_nimet,
        columns=asiakas_nimet,
    ).round(1)

   
    tuotanto_per_tehdas = virtaukset.sum(axis=1).round(1)

    kokonaiskustannus = pulp.value(malli.objective)

    return {
        "status": status,
        "kokonaiskustannus": round(kokonaiskustannus, 2),
        "virtaukset": virtaukset,
        "tuotanto_per_tehdas": tuotanto_per_tehdas,
    }



if __name__ == "__main__":
    tulos = ratkaise_optimointi()

    print(f"Ratkaisun tila: {tulos['status']}")
    print(f"Kokonaiskustannus: {tulos['kokonaiskustannus']:.2f} €/vko")

    print("\n=== VIRTAUKSET (yksikköä/vko) ===")
    print(tulos["virtaukset"])

    print("\n=== TUOTANTO TEHTAITTAIN ===")
    print(tulos["tuotanto_per_tehdas"])

    print("\n=== KAPASITEETIN KÄYTTÖASTE ===")
    for tehdas in tehtaat["nimi"]:
        tuotanto = tulos["tuotanto_per_tehdas"][tehdas]
        kapasiteetti = tehtaat.loc[tehtaat["nimi"] == tehdas, "kapasiteetti"].values[0]
        kayttoaste = tuotanto / kapasiteetti * 100
        print(f"  {tehdas:10s}: {tuotanto:6.0f}/{kapasiteetti} = {kayttoaste:5.1f} %")