from urllib.error import URLError

import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="DataFrame Demo", page_icon="📊")

st.markdown("# DataFrame Demo")
st.sidebar.header("DataFrame Demo")
st.write(
    """This demo shows how to use `st.write` to visualize Pandas DataFrames.
(Data courtesy of the [UN Data Explorer](http://data.un.org/Explorer.aspx).)"""
)


@st.cache
def get_UN_data():
    AWS_BUCKET_URL = "http://streamlit-demo-data.s3-us-west-2.amazonaws.com"
    df = pd.read_csv(f"{AWS_BUCKET_URL}/agri.csv.gz")
    return df.set_index("Region")


try:
    df = get_UN_data()
    if countries := st.multiselect(
        "Choose countries",
        list(df.index),
        ["China", "United States of America"]
    ):
        data = df.loc[countries]
        data /= 1000000.0
        st.write("### Gross Agricultural Production ($B)", data.sort_index())

        data = data.T.reset_index()
        data = pd.melt(data, id_vars=["index"]).rename(
            columns={"index": "year",
                     "value": "Gross Agricultural Product ($B)"}
        )
        chart = (
            alt.Chart(data)  # type: ignore
            .mark_area(opacity=0.3)  # type: ignore
            .encode(
                x="year:T",
                y=alt.Y("Gross Agricultural Product ($B):Q",  # type: ignore
                        stack=None),  # type: ignore
                color="Region:N",
            )
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.error("Please select at least one country.")
except URLError as e:
    st.error(
        f"""
        **This demo requires internet access.**
        Connection error: {e.reason}
        """
    )
