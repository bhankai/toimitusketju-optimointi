import streamlit as st
import pandas as pd

from data import tehtaat as oletustehtaat, asiakkaat as oletusasiakkaat
from optimizer import ratkaise_optimointi
from visualization import piirra_kartta_ratkaisulla

st.set_page_config(
    page_title="PohjolaFood — toimitusketjun optimointi",
    page_icon="🚚",
    layout="wide",
)

st.title("🚚 PohjolaFood Oy — toimitusketjun optimointi")

st.markdown(
    """
    Tämä työkalu optimoi suomalaisen elintarviketuottajan tuotanto- ja
    kuljetuspäätökset lineaarisen ohjelmoinnin avulla. Säädä parametreja
    sivupalkista ja näe miten optimaalinen ratkaisu muuttuu reaaliajassa.
    """
)

st.sidebar.header("⚙️ Parametrit")

st.sidebar.subheader("Tehtaiden kapasiteetit (yks/vko)")

# Kopioidaan oletustehtaat jotta emme muokkaa alkuperäistä
tehtaat = oletustehtaat.copy()

# Slider jokaiselle tehtaalle
for i, rivi in tehtaat.iterrows():
    uusi_kapasiteetti = st.sidebar.slider(
        label=f"{rivi['nimi']}",
        min_value=1000,
        max_value=8000,
        value=int(rivi["kapasiteetti"]),
        step=100,
        key=f"kap_{rivi['nimi']}",
    )
    tehtaat.at[i, "kapasiteetti"] = uusi_kapasiteetti

st.sidebar.subheader("Asiakkaiden kysyntä (yks/vko)")

asiakkaat = oletusasiakkaat.copy()

for i, rivi in asiakkaat.iterrows():
    uusi_kysynta = st.sidebar.slider(
        label=f"{rivi['nimi']}",
        min_value=0,
        max_value=4000,
        value=int(rivi["kysynta"]),
        step=100,
        key=f"kys_{rivi['nimi']}",
    )
    asiakkaat.at[i, "kysynta"] = uusi_kysynta


kokonaiskapasiteetti = tehtaat["kapasiteetti"].sum()
kokonaiskysynta = asiakkaat["kysynta"].sum()

if kokonaiskysynta > kokonaiskapasiteetti:
    st.error(
        f"❌ Kokonaiskysyntä ({kokonaiskysynta:,} yks) ylittää "
        f"kokonaiskapasiteetin ({kokonaiskapasiteetti:,} yks). "
        f"Optimointiongelmalla ei ole ratkaisua. Säädä parametreja."
    )
    st.stop()  # Pysäytetään skriptin suoritus tähän

tulos = ratkaise_optimointi(tehtaat, asiakkaat)

if tulos["status"] != "Optimal":
    st.error(f"Optimointi epäonnistui. Status: {tulos['status']}")
    st.stop()

st.subheader("📊 Optimointitulos")

col1, col2, col3 = st.columns(3)

col1.metric(
    label="Kokonaiskustannus",
    value=f"{tulos['kokonaiskustannus']:,.0f} €/vko",
)

col2.metric(
    label="Kokonaistuotanto",
    value=f"{int(tulos['tuotanto_per_tehdas'].sum()):,} yks/vko",
)

col3.metric(
    label="Yksikkökustannus",
    value=f"{tulos['kokonaiskustannus'] / kokonaiskysynta:.2f} €/yks",
)

st.subheader("🗺️ Optimoidut kuljetusvirrat")

kartta = piirra_kartta_ratkaisulla(tehtaat, asiakkaat, tulos["virtaukset"])
st.plotly_chart(kartta, use_container_width=True)


col_vasen, col_oikea = st.columns(2)

with col_vasen:
    st.subheader("🏭 Tuotanto tehtaittain")

    # Lasketaan käyttöaste
    tuotanto_taulu = pd.DataFrame({
        "Tehdas": tehtaat["nimi"].values,
        "Kapasiteetti": tehtaat["kapasiteetti"].values,
        "Tuotanto": tulos["tuotanto_per_tehdas"].reindex(tehtaat["nimi"]).values,
    })
    tuotanto_taulu["Käyttöaste"] = (
        tuotanto_taulu["Tuotanto"] / tuotanto_taulu["Kapasiteetti"] * 100
    ).round(1).astype(str) + " %"

    st.dataframe(tuotanto_taulu, hide_index=True, use_container_width=True)

with col_oikea:
    st.subheader("📦 Kysynnän täyttyminen")

    toimitukset_taulu = pd.DataFrame({
        "Asiakas": asiakkaat["nimi"].values,
        "Kysyntä": asiakkaat["kysynta"].values,
        "Toimitettu": tulos["virtaukset"].sum(axis=0).reindex(asiakkaat["nimi"]).values,
    })

    st.dataframe(toimitukset_taulu, hide_index=True, use_container_width=True)

st.subheader("🔀 Kuljetusvirrat (yksikköä/vko)")
st.dataframe(tulos["virtaukset"], use_container_width=True)

st.markdown("---")
st.caption(
    "Rakennettu osana portfolioprojektia. "
    "Optimointi: PuLP (CBC-solveri). "
    "Visualisointi: Plotly. "
    "Käyttöliittymä: Streamlit."
)