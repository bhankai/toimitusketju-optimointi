import plotly.graph_objects as go
import pandas as pd


def piirra_kartta(
    tehtaat: pd.DataFrame,
    asiakkaat: pd.DataFrame,
) -> go.Figure:
    fig = go.Figure()

    fig.add_trace(go.Scattermapbox(
        lat=tehtaat["lat"],
        lon=tehtaat["lon"],
        mode="markers+text",
        marker=dict(size=tehtaat["kapasiteetti"] / 100, color="royalblue", opacity=0.85),
        text=tehtaat["nimi"],
        textposition="top right",
        textfont=dict(size=14, color="black"),
        name="Tehtaat",
        hovertemplate=(
            "<b>%{text}</b><br>"
            "Kapasiteetti: %{customdata[0]} yks/vko<br>"
            "Tuotantokust.: %{customdata[1]:.2f} €/yks"
            "<extra></extra>"
        ),
        customdata=tehtaat[["kapasiteetti", "tuotantokustannus"]].values,
    ))

    fig.add_trace(go.Scattermapbox(
        lat=asiakkaat["lat"],
        lon=asiakkaat["lon"],
        mode="markers+text",
        marker=dict(size=asiakkaat["kysynta"] / 100, color="darkorange", opacity=0.85),
        text=asiakkaat["nimi"],
        textposition="bottom right",
        textfont=dict(size=12, color="black"),
        name="Asiakkaat",
        hovertemplate=(
            "<b>%{text}</b><br>"
            "Kysyntä: %{customdata[0]} yks/vko"
            "<extra></extra>"
        ),
        customdata=asiakkaat[["kysynta"]].values,
    ))

    fig.update_layout(
        mapbox=dict(style="open-street-map", center=dict(lat=63.5, lon=25.5), zoom=4.3),
        margin=dict(l=0, r=0, t=40, b=0),
        title=dict(text="PohjolaFood Oy — toimitusketjun verkosto", x=0.5, xanchor="center"),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(255,255,255,0.8)"),
        height=650,
    )
    return fig


def piirra_kartta_ratkaisulla(
    tehtaat: pd.DataFrame,
    asiakkaat: pd.DataFrame,
    virtaukset: pd.DataFrame,
) -> go.Figure:
   
    fig = go.Figure()

    max_virtaus = virtaukset.values.max() if virtaukset.values.max() > 0 else 1

    for tehdas_nimi in virtaukset.index:
        for asiakas_nimi in virtaukset.columns:
            maara = virtaukset.loc[tehdas_nimi, asiakas_nimi]

            # Piirretään viiva vain jos virtausta on (yli 0)
            if maara <= 0:
                continue

            # Haetaan koordinaatit
            tehdas_rivi = tehtaat[tehtaat["nimi"] == tehdas_nimi].iloc[0]
            asiakas_rivi = asiakkaat[asiakkaat["nimi"] == asiakas_nimi].iloc[0]

            # Viivan paksuus skaalautuu virtauksen mukaan (1-8 pikseliä)
            paksuus = 1 + 7 * (maara / max_virtaus)

            fig.add_trace(go.Scattermapbox(
                lat=[tehdas_rivi["lat"], asiakas_rivi["lat"]],
                lon=[tehdas_rivi["lon"], asiakas_rivi["lon"]],
                mode="lines",
                line=dict(width=paksuus, color="rgba(70, 130, 180, 0.6)"),
                hovertemplate=(
                    f"<b>{tehdas_nimi} → {asiakas_nimi}</b><br>"
                    f"Määrä: {maara:.0f} yks/vko"
                    "<extra></extra>"
                ),
                showlegend=False,
            ))

    # Lasketaan käyttöaste hovertemplatea varten
    tuotanto_per_tehdas = virtaukset.sum(axis=1)
    kayttoasteet = []
    for nimi in tehtaat["nimi"]:
        tuotanto = tuotanto_per_tehdas.get(nimi, 0)
        kapasiteetti = tehtaat.loc[tehtaat["nimi"] == nimi, "kapasiteetti"].values[0]
        kayttoasteet.append(tuotanto / kapasiteetti * 100)

    fig.add_trace(go.Scattermapbox(
        lat=tehtaat["lat"],
        lon=tehtaat["lon"],
        mode="markers+text",
        marker=dict(size=tehtaat["kapasiteetti"] / 100, color="royalblue", opacity=0.9),
        text=tehtaat["nimi"],
        textposition="top right",
        textfont=dict(size=14, color="black"),
        name="Tehtaat",
        hovertemplate=(
            "<b>%{text}</b><br>"
            "Kapasiteetti: %{customdata[0]} yks/vko<br>"
            "Tuotanto: %{customdata[1]:.0f} yks/vko<br>"
            "Käyttöaste: %{customdata[2]:.1f} %"
            "<extra></extra>"
        ),
        customdata=list(zip(
            tehtaat["kapasiteetti"],
            tuotanto_per_tehdas.reindex(tehtaat["nimi"]).fillna(0),
            kayttoasteet,
        )),
    ))
    fig.add_trace(go.Scattermapbox(
        lat=asiakkaat["lat"],
        lon=asiakkaat["lon"],
        mode="markers+text",
        marker=dict(size=asiakkaat["kysynta"] / 100, color="darkorange", opacity=0.9),
        text=asiakkaat["nimi"],
        textposition="bottom right",
        textfont=dict(size=12, color="black"),
        name="Asiakkaat",
        hovertemplate=(
            "<b>%{text}</b><br>"
            "Kysyntä: %{customdata[0]} yks/vko"
            "<extra></extra>"
        ),
        customdata=asiakkaat[["kysynta"]].values,
    ))

    fig.update_layout(
        mapbox=dict(style="open-street-map", center=dict(lat=63.5, lon=25.5), zoom=4.3),
        margin=dict(l=0, r=0, t=40, b=0),
        title=dict(
            text="PohjolaFood Oy — optimoidut kuljetusvirrat",
            x=0.5,
            xanchor="center",
        ),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(255,255,255,0.8)"),
        height=650,
    )
    return fig

if __name__ == "__main__":
    from data import tehtaat, asiakkaat
    from optimizer import ratkaise_optimointi

    tulos = ratkaise_optimointi()
    fig = piirra_kartta_ratkaisulla(tehtaat, asiakkaat, tulos["virtaukset"])
    fig.show()