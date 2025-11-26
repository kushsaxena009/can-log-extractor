import streamlit as st
import sys
import pathlib
import os
import shutil
import time

TEMP_DIR = "temp"

filename = f"log_{int(time.time())}.asc"
asc_path = os.path.join(TEMP_DIR, filename)

if os.path.exists(TEMP_DIR):
    shutil.rmtree(TEMP_DIR)
os.makedirs(TEMP_DIR)


# create folder if not exists
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)


# Allow importing from src/
root = pathlib.Path(__file__).resolve().parent
workspace_root = str(root.parent)
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

from src.extractor import CANLogExtractor
from src.dbc_decoder import DBCDecoder


st.set_page_config(
    page_title="CAN Log Extractor + Visualizer",
    layout="wide"
)

st.markdown("""
# CAN Log Extractor + Visualizer  
Upload a CAN (.asc) file and optionally a DBC to decode signals.
---
""")


# -----------------------------
# Sidebar Inputs
# -----------------------------
st.sidebar.header("Upload Files")

asc_file = st.sidebar.file_uploader("Upload CAN Log (.asc)", type=["asc", "txt"])
dbc_file = st.sidebar.file_uploader("Upload DBC (optional)", type=["dbc"])

asc_path = None
dbc_path = None


# -----------------------------
# Save ASC Temporarily
# -----------------------------
if asc_file:
    asc_path = os.path.join(TEMP_DIR, "uploaded_log.asc")
    with open(asc_path, "wb") as f:
        f.write(asc_file.getbuffer())


# Save DBC
if dbc_file:
    dbc_path = os.path.join(TEMP_DIR, "uploaded.dbc")
    with open(dbc_path, "wb") as f:
        f.write(dbc_file.getbuffer())



# -----------------------------
# Main Parser
# -----------------------------
if asc_path:
    log = CANLogExtractor(asc_path, dbc_path=dbc_path)

    try:
        log.load_log()
        st.success("ASC Log loaded successfully.")
    except Exception as e:
        st.error(f"Error loading file: {e}")
        st.stop()

    st.subheader("Summary")
    st.write(log.get_summary())

    # -----------------------------
    # Visualization Options
    # -----------------------------
    st.subheader("Visualization")

    plot_type = st.selectbox(
        "Choose visualization:",
        ["ID Frequency", "Timestamp vs ID", "Byte Trend"]
    )

    if plot_type == "ID Frequency":
        log.plot_id_frequency()

    elif plot_type == "Timestamp vs ID":
        log.plot_timestamp_vs_id()

    else:
        byte_index = st.number_input("Select Byte (0–7)", min_value=0, max_value=7, value=0)
        log.plot_byte(byte_index)

    # -----------------------------
    # CSV Export
    # -----------------------------
    if st.button("Export CSV"):
        log.export_csv("output.csv")
        st.success("Exported to output.csv")

# -----------------------------
# MATCHING ASC & DBC IDs
# -----------------------------
if asc_path and dbc_path:
    st.subheader("ASC–DBC Consistency Check")

    report = log.compare_asc_dbc_ids()

    if report:
        if report["asc_not_in_dbc"] or report["dbc_not_in_asc"]:
            st.warning("⚠ ASC log and DBC file do NOT fully match.")

            if report["asc_not_in_dbc"]:
                st.error(f"IDs in ASC but NOT in DBC: {report['asc_not_in_dbc']}")

            if report["dbc_not_in_asc"]:
                st.error(f"IDs in DBC but NOT in ASC: {report['dbc_not_in_asc']}")

        else:
            st.success("✔ ASC and DBC fully match!")

        st.write("Matched IDs:", report["matched_ids"])


# -----------------------------
# DBC DECODING
# -----------------------------
if asc_path and dbc_path:

    st.subheader("DBC Decoding Preview (First Frame)")

    try:
        decoder = DBCDecoder(dbc_path)

        row = log.data.iloc[0]
        data_bytes = []

        # Convert hex string bytes to ints
        for i in range(8):
            val = row[f"byte_{i}"]
            try:
                data_bytes.append(int(val, 16))
            except:
                data_bytes.append(0)

        decoded = decoder.decode_frame(row["id"], data_bytes)
        st.write(decoded)

    except Exception as e:
        st.error(f"DBC decode error: {e}")

    # FULL DECODE
    if st.button("Decode Entire Log"):
        decoded = log.decode_all_frames()
        if decoded:
            st.dataframe(decoded)
        else:
            st.warning("No signals decoded.")
