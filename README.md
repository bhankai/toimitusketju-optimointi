# 🚚 Supply Chain Optimization Tool

Optimoi suomalaisen elintarviketuottajan tuotanto- ja kuljetuspäätökset
lineaarisen ohjelmoinnin avulla. Interaktiivinen Streamlit-sovellus jossa
käyttäjä säätää parametreja ja näkee ratkaisun reaaliajassa Suomen kartalla.

🔗 **[Live-demo →](STREAMLIT_URL)**

## Stack
- **PuLP** — lineaarinen ohjelmointi (LP), CBC-solveri
- **Pandas** — datan käsittely
- **Plotly** — interaktiivinen karttavisualisointi
- **Streamlit** — web-käyttöliittymä

## Optimointiongelma

3 tehdasta → 5 asiakasta. Minimoi tuotanto- ja kuljetuskustannukset
kapasiteetti- ja kysyntärajoitteiden puitteissa.

**Tulos oletusparametreilla: 381 825 €/vko**
Tampere 100 % käyttöasteella (pullonkaula), Helsinki 50 %, Oulu 71 %.

## Käynnistys

git clone https://github.com/bhankai/toimitusketju-optimointi.git
cd toimitusketju-optimointi
pip install -r requirements.txt
streamlit run app.py

## Tekijä
Kailash Bhandari 
[LinkedIn]([URL](https://www.linkedin.com/in/kailash-bhandari/) · [GitHub](https://github.com/bhankai)
