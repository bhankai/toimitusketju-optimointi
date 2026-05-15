import pandas as pd
from math import radians, sin, cos, sqrt, atan2

tehtaat = pd.DataFrame([
    { 
        "nimi": "Helsinki",
        "lat": 60.1699,
        "lon": 24.9384,
        "kapasiteetti": 5000,
        "tuotantokustannus": 12.50,
    },
    {
        "nimi": "Tampere",
        "lat": 61.4978,
        "lon": 23.7610,
        "kapasiteetti": 4000,
        "tuotantokustannus": 11.00,
    },
    {
        "nimi": "Oulu",
        "lat": 65.0121,
        "lon": 25.4651,
        "kapasiteetti": 3500,
        "tuotantokustannus": 10.00,
    },
])   

asiakkaat = pd.DataFrame([
    {"nimi": "Helsinki-keskus", "lat": 60.1699, "lon": 24.9384, "kysynta": 2500},
    {"nimi": "Turku",           "lat": 60.4518, "lon": 22.2666, "kysynta": 1800},
    {"nimi": "Tampere-keskus",  "lat": 61.4978, "lon": 23.7610, "kysynta": 1500},
    {"nimi": "Kuopio",          "lat": 62.8924, "lon": 27.6770, "kysynta": 1200},
    {"nimi": "Oulu-keskus",     "lat": 65.0121, "lon": 25.4651, "kysynta": 2000},
])
KULJETUS_EUR_PER_YKSIKKO_PER_KM = 0.5

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    # Laskee kahden pisteen välisen etäisyyden kilometreinä
    #pallopinnalla (Haversine-kaava).
    #Tämä on standardi tapa laskea etäisyyksiä leveys- ja pituusasteista,
    #kun ei haluta käyttää erillistä karttapalvelua
    R = 6371.0
    # Muutetaan asteet radiaaneiksi
    lat1_r, lon1_r = radians(lat1), radians(lon1)
    lat2_r, lon2_r = radians(lat2), radians(lon2)

    # Erotukset
    dlat = lat2_r - lat1_r
    dlon = lon2_r - lon1_r

    # Haversine-kaava
    a = sin(dlat / 2) ** 2 + cos(lat1_r) * cos(lat2_r) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c

def laske_etaisyysmatriisi() -> pd.DataFrame:
    """
    Palauttaa DataFrame-taulukon jossa rivit ovat tehtaita,
    sarakkeet asiakkaita, ja arvot etäisyyksiä kilometreinä.
    """
    rivit = []
    for _, tehdas in tehtaat.iterrows():
        rivi = {"tehdas": tehdas["nimi"]}
        for _, asiakas in asiakkaat.iterrows():
            km = haversine_km(
                tehdas["lat"], tehdas["lon"],
                asiakas["lat"], asiakas["lon"],
            )
            rivi[asiakas["nimi"]] = round(km, 1)
        rivit.append(rivi)
    return pd.DataFrame(rivit).set_index("tehdas")

def laske_kuljetuskustannukset() -> pd.DataFrame:
    """
    Palauttaa DataFrame-taulukon, jossa arvot ovat kuljetuskustannus
    euroa per yksikkö tehtaalta asiakkaalle.
    """
    etaisyydet = laske_etaisyysmatriisi()
    return (etaisyydet * KULJETUS_EUR_PER_YKSIKKO_PER_KM).round(3)

if __name__ == "__main__":
    print("=== TEHTAAT ===")
    print(tehtaat)
    print(f"\nKokonaiskapasiteetti: {tehtaat['kapasiteetti'].sum()} yksikköä/vko")

    print("\n=== ASIAKKAAT ===")
    print(asiakkaat)
    print(f"\nKokonaiskysyntä: {asiakkaat['kysynta'].sum()} yksikköä/vko")

    print("\n=== ETÄISYYDET (km) ===")
    print(laske_etaisyysmatriisi())

    print("\n=== KULJETUSKUSTANNUKSET (€/yksikkö) ===")
    print(laske_kuljetuskustannukset())