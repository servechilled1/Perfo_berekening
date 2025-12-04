import math
from datetime import date

import streamlit as st

# === Constants ===
MM2_PER_M2 = 1_000_000
RAND_MM = 20
MAX_AANZUIG_MS = 2.4
MAX_UITBLAAS_MS = 3.6

st.set_page_config(page_title="Perforatieberekening", layout="wide")
st.title("Perforatieberekening rondom een sparing")

# === Layout met invulvelden links en output rechts ===
left_col, right_col = st.columns([1, 2])

with left_col:
    st.header("🔧 Invoer")

    # Sparing
    sparing_A = st.number_input("Sparing lengte A (mm)", value=1500, min_value=1, step=10)
    sparing_B = st.number_input("Sparing hoogte B (mm)", value=1500, min_value=1, step=10)

    # Perforatiepatroon
    perforatie_A = st.number_input("Gatbreedte perforatie (mm)", value=20, min_value=1, step=1)
    perforatie_B = st.number_input("Gathoogte perforatie (mm)", value=20, min_value=1, step=1)
    tussenmaat = st.number_input("Tussenmaat tussen gaten (mm)", value=5, min_value=0, step=1)

    # Doorlaat en luchtdebiet
    doorlaat_factor = st.number_input(
        "Doorlaatfactor t.o.v. sparingoppervlak (1.0 = 100%)",
        value=1.0,
        min_value=0.1,
        step=0.1,
    )

    lucht_m3h = st.number_input("Luchtdebiet (m³/h)", value=30000.0, min_value=0.0, step=500.0)

# === Basiscontroles en patroon ===
patroon_lengte = perforatie_A + tussenmaat
patroon_hoogte = perforatie_B + tussenmaat

if patroon_lengte <= 0 or patroon_hoogte <= 0:
    st.error("Patroonhoogte/-lengte is 0 of negatief. Controleer perforatie en tussenmaat.")
    st.stop()

gatoppervlak = perforatie_A * perforatie_B
eenheidsoppervlak = patroon_lengte * patroon_hoogte

if eenheidsoppervlak <= 0:
    st.error("Eenheidsoppervlak is 0. Controleer perforatiematen.")
    st.stop()

netto_doorlaat_pct = gatoppervlak / eenheidsoppervlak
if netto_doorlaat_pct <= 0:
    st.error("Netto doorlaat is 0 of negatief. Controleer perforatiematen.")
    st.stop()

# === Sparingoppervlak ===
sparing_oppervlak_mm2 = sparing_A * sparing_B
if sparing_oppervlak_mm2 <= 0:
    st.error("Sparingoppervlak is 0. Lengte en hoogte moeten > 0 zijn.")
    st.stop()

sparing_oppervlak_m2 = sparing_oppervlak_mm2 / MM2_PER_M2
gewenste_netto_doorlaat_mm2 = sparing_oppervlak_mm2 * doorlaat_factor
gewenste_netto_doorlaat_m2 = gewenste_netto_doorlaat_mm2 / MM2_PER_M2

# === Hoofdberekeningen ===
omtrek_mm = 2 * (sparing_A + sparing_B)
if omtrek_mm <= 0:
    st.error("Omtrek is 0. Controleer sparingafmetingen.")
    st.stop()

vereist_perforatie_oppervlak_mm2 = gewenste_netto_doorlaat_mm2 / netto_doorlaat_pct
benodigde_hoogte_mm = vereist_perforatie_oppervlak_mm2 / omtrek_mm

bruikbare_hoogte = max(0, benodigde_hoogte_mm - 2 * RAND_MM)
aantal_rijen = math.ceil(bruikbare_hoogte / patroon_hoogte) if bruikbare_hoogte > 0 else 0
aangepaste_hoogte_mm = aantal_rijen * patroon_hoogte + (2 * RAND_MM if aantal_rijen > 0 else 0)

werkelijke_perforatie_oppervlak_mm2 = omtrek_mm * aangepaste_hoogte_mm
werkelijke_netto_doorlaat_mm2 = werkelijke_perforatie_oppervlak_mm2 * netto_doorlaat_pct
werkelijke_netto_doorlaat_m2 = werkelijke_netto_doorlaat_mm2 / MM2_PER_M2

lucht_m3s = lucht_m3h / 3600 if lucht_m3h else 0
snelheid_sparing = lucht_m3s / sparing_oppervlak_m2 if sparing_oppervlak_m2 else 0
snelheid_perforatie = lucht_m3s / werkelijke_netto_doorlaat_m2 if werkelijke_netto_doorlaat_m2 else 0

# === Aanbevolen perforatiehoogte bij max 2.4 m/s ===
benodigde_doorlaat_m2_bij_2_4 = lucht_m3s / MAX_AANZUIG_MS if MAX_AANZUIG_MS else 0
benodigde_doorlaat_mm2_bij_2_4 = benodigde_doorlaat_m2_bij_2_4 * MM2_PER_M2
benodigde_perforatie_oppervlak_mm2_bij_2_4 = (
    benodigde_doorlaat_mm2_bij_2_4 / netto_doorlaat_pct if netto_doorlaat_pct else 0
)
aanbevolen_hoogte_mm = (
    benodigde_perforatie_oppervlak_mm2_bij_2_4 / omtrek_mm if omtrek_mm else 0
)

bruikbare_hoogte_aanbevolen = max(0, aanbevolen_hoogte_mm - 2 * RAND_MM)
aantal_rijen_aanbevolen = (
    math.ceil(bruikbare_hoogte_aanbevolen / patroon_hoogte)
    if bruikbare_hoogte_aanbevolen > 0
    else 0
)
aangepaste_aanbevolen_hoogte = (
    aantal_rijen_aanbevolen * patroon_hoogte + (2 * RAND_MM if aantal_rijen_aanbevolen > 0 else 0)
)

aanbevolen_doorlaatfactor = (
    benodigde_doorlaat_m2_bij_2_4 / sparing_oppervlak_m2 if sparing_oppervlak_m2 else 0
)

# === Output rechts ===
with right_col:
    st.header("📊 Resultaten")

    # Korte visuele samenvatting
    c1, c2, c3 = st.columns(3)
    c1.metric("Sparingoppervlak [m²]", f"{sparing_oppervlak_m2:.2f}")
    c2.metric("Netto doorlaat patroon [%]", f"{netto_doorlaat_pct * 100:.1f}")
    c3.metric("Perforatiehoogte [mm]", f"{aangepaste_hoogte_mm:.1f}")

    c4, c5 = st.columns(2)
    c4.metric("Snelheid in sparing [m/s]", f"{snelheid_sparing:.2f}")
    c5.metric("Snelheid door perforatie [m/s]", f"{snelheid_perforatie:.2f}")

    # Waarschuwingen
    if snelheid_perforatie > MAX_UITBLAAS_MS:
        st.error(f"⚠️ Luchtsnelheid door perforatie is hoger dan {MAX_UITBLAAS_MS} m/s (uitblaas).")
    elif snelheid_perforatie > MAX_AANZUIG_MS:
        st.warning(f"⚠️ Luchtsnelheid door perforatie is hoger dan {MAX_AANZUIG_MS} m/s (aanzuig).")

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
- Aantal rijen perforatie: {aantal_rijen:d}

Werkelijke perforatie:
- Werkelijke netto doorlaat: {werkelijke_netto_doorlaat_m2:.2f} m²
- Werkelijke perforatie-oppervlakte: {werkelijke_perforatie_oppervlak_mm2 / MM2_PER_M2:.2f} m²
- Randvrijheid toegepast: {RAND_MM} mm rondom

Aanbevolen perforatiehoogte (bij {MAX_AANZUIG_MS} m/s luchtsnelheid):
- Hoogte: {aangepaste_aanbevolen_hoogte:.1f} mm
- Benodigde netto doorlaat: {benodigde_doorlaat_mm2_bij_2_4:,.0f} mm²
- Overeenkomende doorlaatfactor: {aanbevolen_doorlaatfactor:.2f}

Luchttechnisch:
- Luchtdebiet: {lucht_m3h:,.0f} m³/h
- Snelheid in sparing: {snelheid_sparing:.2f} m/s
- Snelheid door perforatie: {snelheid_perforatie:.2f} m/s"""

    st.subheader("Klantoverzicht (kopieer en plak)")
    st.code(klant_tekst, language="markdown")
