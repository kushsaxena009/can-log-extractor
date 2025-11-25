import streamlit as st
from extractor import CANLogExtractor

st.title("CAN Log Extractor + Visualizer")

uploaded = st.file_uploader("Upload CAN Log (.asc or .txt)")

if uploaded:
    with open("temp.asc", "wb") as f:
        f.write(uploaded.read())

    log = CANLogExtractor("temp.asc")

    if log.load_log():
        st.subheader("Summary")
        st.write(log.get_summary())

        st.subheader("Select Visualization")
        plot_type = st.selectbox(
            "Choose:",
            ["ID Frequency", "Timestamp vs ID", "Byte Trend"]
        )

        if plot_type == "ID Frequency":
            log.plot_id_frequency()

        elif plot_type == "Timestamp vs ID":
            log.plot_timestamp_vs_id()

        else:
            byte = st.number_input("Byte index (0-7)", min_value=0, max_value=7)
            log.plot_byte(byte)

        if st.button("Export CSV"):
            log.export_csv("output.csv")
            st.success("CSV exported as output.csv")
