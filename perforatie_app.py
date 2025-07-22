import streamlit as st
import math
from datetime import date

st.set_page_config(page_title="Perforatieberekening", layout="wide")
st.title("Perforatieberekening rondom een sparing")

# === Layout met invulvelden links en output rechts ===
left_col, right_col = st.columns([1, 2])

with left_col:
    st.header("🔧 Invoer")
    sparing_A = st.number_input("Sparing lengte A (mm)", value=1500)
    sparing_B = st.number_input("Sparing hoogte B (mm)", value=1500)
    perforatie_A = st.number_input("Gatbreedte perforatie (mm)", value=20)
    perforatie_B = st.number_input("Gathoogte perforatie (mm)", value=20)
    tussenmaat = st.number_input("Tussenmaat tussen gaten (mm)", value=5)
    doorlaat_factor = st.number_input("Doorlaatfactor t.o.v. sparingoppervlak (1.0 = 100%)", value=1.0, step=0.1)
    lucht_m3h = st.number_input("Luchtdebiet (m³/h)", value=30000)

# === Berekeningen ===
rand = 20
patroon_lengte = perforatie_A + tussenmaat
patroon_hoogte = perforatie_B + tussenmaat
gatoppervlak = perforatie_A * perforatie_B
eenheidsoppervlak = patroon_lengte * patroon_hoogte
netto_doorlaat_pct = gatoppervlak / eenheidsoppervlak

sparing_oppervlak_mm2 = sparing_A * sparing_B
sparing_oppervlak_m2 = sparing_oppervlak_mm2 / 1_000_000
gewenste_netto_doorlaat_mm2 = sparing_oppervlak_mm2 * doorlaat_factor
gewenste_netto_doorlaat_m2 = gewenste_netto_doorlaat_mm2 / 1_000_000

vereist_perforatie_oppervlak_mm2 = gewenste_netto_doorlaat_mm2 / netto_doorlaat_pct
omtrek_mm = 2 * (sparing_A + sparing_B)
benodigde_hoogte_mm = vereist_perforatie_oppervlak_mm2 / omtrek_mm

bruikbare_hoogte = max(0, benodigde_hoogte_mm - 2 * rand)
aantal_rijen = math.ceil(bruikbare_hoogte / patroon_hoogte)
aangepaste_hoogte_mm = aantal_rijen * patroon_hoogte + 2 * rand

werkelijke_perforatie_oppervlak_mm2 = omtrek_mm * aangepaste_hoogte_mm
werkelijke_netto_doorlaat_mm2 = werkelijke_perforatie_oppervlak_mm2 * netto_doorlaat_pct
werkelijke_netto_doorlaat_m2 = werkelijke_netto_doorlaat_mm2 / 1_000_000

lucht_m3s = lucht_m3h / 3600
snelheid_sparing = lucht_m3s / sparing_oppervlak_m2 if sparing_oppervlak_m2 else 0
snelheid_perforatie = lucht_m3s / werkelijke_netto_doorlaat_m2 if werkelijke_netto_doorlaat_m2 else 0

# === Aanbevolen perforatiehoogte bij max 2.4 m/s ===
benodigde_doorlaat_m2_bij_2_4 = lucht_m3s / 2.4
benodigde_doorlaat_mm2_bij_2_4 = benodigde_doorlaat_m2_bij_2_4 * 1_000_000
benodigde_perforatie_oppervlak_mm2_bij_2_4 = benodigde_doorlaat_mm2_bij_2_4 / netto_doorlaat_pct
aanbevolen_hoogte_mm = benodigde_perforatie_oppervlak_mm2_bij_2_4 / omtrek_mm
aantal_rijen_aanbevolen = math.ceil((aanbevolen_hoogte_mm - 2 * rand) / patroon_hoogte)
aangepaste_aanbevolen_hoogte = aantal_rijen_aanbevolen * patroon_hoogte + 2 * rand
aanbevolen_doorlaatfactor = benodigde_doorlaat_m2_bij_2_4 / sparing_oppervlak_m2 if sparing_oppervlak_m2 else 0

# === Output rechts ===
with right_col:
    if snelheid_perforatie > 3.6:
        st.error("⚠️ Luchtsnelheid door perforatie is hoger dan 3.6 m/s (uitblaas).")
    elif snelheid_perforatie > 2.4:
        st.warning("⚠️ Luchtsnelheid door perforatie is hoger dan 2.4 m/s (aanzuig).")

    vandaag = date.today().strftime("%d-%m-%Y")
    klant_tekst = f"""Perforatieberekening – overzicht ({vandaag})

Gegevens sparing:
- Lengte: {sparing_A:.0f} mm
- Hoogte: {sparing_B:.0f} mm
- Oppervlakte sparing: {sparing_oppervlak_m2:.2f} m²

Gegevens perforatiepatroon:
- Gatbreedte: {perforatie_A:.0f} mm
- Gathoogte: {perforatie_B:.0f} mm
- Tussenmaat tussen gaten: {tussenmaat:.0f} mm
- Netto doorlaat per patroon: {netto_doorlaat_pct * 100:.2f}%

Benodigd resultaat:
- Gewenste netto doorlaat (factor {doorlaat_factor:.2f}): {gewenste_netto_doorlaat_mm2:,.0f} mm²
- Benodigde perforatiehoogte (afgerond): {aangepaste_hoogte_mm:.1f} mm

Werkelijke perforatie:
- Werkelijke netto doorlaat: {werkelijke_netto_doorlaat_m2:.2f} m²
- Werkelijke perforatie-oppervlakte: {werkelijke_perforatie_oppervlak_mm2 / 1_000_000:.2f} m²
- Randvrijheid toegepast: 20 mm rondom

Aanbevolen perforatiehoogte (bij 2.4 m/s luchtsnelheid):
- Hoogte: {aangepaste_aanbevolen_hoogte:.1f} mm
- Benodigde netto doorlaat: {benodigde_doorlaat_mm2_bij_2_4:,.0f} mm²
- Overeenkomende doorlaatfactor: {aanbevolen_doorlaatfactor:.2f}

Luchttechnisch:
- Luchtdebiet: {lucht_m3h:,.0f} m³/h
- Snelheid in sparing: {snelheid_sparing:.2f} m/s
- Snelheid door perforatie: {snelheid_perforatie:.2f} m/s"""

    st.subheader("Klantoverzicht (kopieer en plak)")
    st.code(klant_tekst, language="markdown")
