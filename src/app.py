import streamlit as st
import re

# Ensure extractor is importable whether running as package or script
import sys
import pathlib
root = pathlib.Path(__file__).resolve().parent
# Add package parent (workspace root) to sys.path so `src` can be imported when needed
workspace_root = str(root.parent)
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

try:
    from src.extractor import CANLogExtractor
except ModuleNotFoundError:
    # Fallback for when running directly from the `src` folder or without package context
    from extractor import CANLogExtractor

st.set_page_config(
    page_title="CAN Log Extractor + Visualizer",
    layout="wide"
)

st.markdown("""
# CAN Log Extractor + Visualizer  
A simple tool to parse, analyze, and visualize CAN network logs.
---
""")

st.sidebar.header("Settings")
log_file = st.sidebar.file_uploader("Upload CAN Log (.asc)", type=["asc", "txt","blf"])
dbc_file = st.sidebar.file_uploader("Upload DBC file (optional)", type=["dbc"])
dbc_path = None

def load_log(self):
    parsed_lines = []
    pattern = r"(\d+\.\d+)\s+([0-9A-Fa-fx]+)\s+(\d+)\s+(.*)"

    try:
        with open(self.file_path, "r") as f:
            for line in f:
                if line.startswith(("//", "date", "base", "version", "Begin", "End")):
                    continue

                match = re.match(pattern, line.strip())
                if match:
                    timestamp = float(match.group(1))
                    msg_id = match.group(2)
                    dlc = int(match.group(3))
                    data = match.group(4).strip().split()

                    parsed_lines.append([timestamp, msg_id, dlc] + data)
    except Exception as e:
            print("Parsing Error:", e)
            return False

if log_file:
    with open("temp.asc", "wb") as f:
        f.write(log_file.read())

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

            
if dbc_file:
    dbc_path = "uploaded.dbc"
    with open(dbc_path, "wb") as f:
        f.write(dbc_file.getbuffer())

    from dbc_decoder import DBCDecoder
    decoder = DBCDecoder(dbc_path)

    st.subheader("Decode Example")
    example_row = log.data.iloc[0]
    data_bytes = [int(x) for x in example_row[3:].tolist()]

    decoded = decoder.decode_message(example_row['id'], data_bytes)
    st.write(decoded)

extractor = CANLogExtractor(dbc_file, dbc_path=dbc_path)

if st.button("Show Decoded Signals"):
    decoded = extractor.decode_all_frames()
    if decoded:
        st.dataframe(decoded)
    else:
        st.warning("No DBC match or nothing decoded.")


#st.write(log.data.head(20))
