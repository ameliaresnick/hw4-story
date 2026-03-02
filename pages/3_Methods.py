import streamlit as st

st.set_page_config(page_title="Methods", layout="wide")

st.title("Methods & Limitations")
st.write("- Data source: `vega_datasets.data.seattle_weather()` (sample dataset packaged with Vega datasets).")
st.write("- Variables used: `date`, `temp_max`, `precipitation`, `weather`")
st.subheader("Limitations")
st.write("- Single city; patterns don’t generalize to other climates.")
st.write("- Since our analysis is based on observational data; the relationships (e.g., precip vs temp) here are not causal.")
st.write("- ‘Weather’ categories are coarse and may hide intra-category variation.")
