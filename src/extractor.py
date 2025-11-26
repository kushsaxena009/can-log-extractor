import pandas as pd
import re
import matplotlib.pyplot as plt
import streamlit as st

from .dbc_decoder import DBCDecoder


class CANLogExtractor:
    def __init__(self, file_path, dbc_path=None):
        self.file_path = file_path
        self.dbc_path = dbc_path
        self.data = None
        self.decoder = DBCDecoder(dbc_path)
    
    def load_log(self):
        """
            Reads multiple ASC formats automatically.
            Supports:
            1. Vector ASC Standard
            ts ch id Tx/Rx d dlc bytes...
            2. Vector ASC without Tx/Rx
            ts ch id d dlc bytes...
            3. ETAS ASC
            ts id dlc bytes...
            4. Old CANalyzer
            ts id Tx/Rx dlc bytes...
            5. ASC files with headers (date, base, etc.)
        """

        parsed_lines = []

        # MULTI-FORMAT PATTERNS
        patterns = [
            # 1. Vector Standard ASC
            re.compile(
                r"(?P<ts>\d+\.\d+)\s+\d+\s+(?P<id>[A-Fa-f0-9]+)\s+(Tx|Rx)\s+d\s+(?P<dlc>\d+)\s+(?P<data>(?:[A-Fa-f0-9]{2}\s*)+)"
            ),
            # 2. No Tx/Rx
            re.compile(
                r"(?P<ts>\d+\.\d+)\s+\d+\s+(?P<id>[A-Fa-f0-9]+)\s+d\s+(?P<dlc>\d+)\s+(?P<data>(?:[A-Fa-f0-9]{2}\s*)+)"
            ),
            # 3. ETAS format: ts id dlc bytes
            re.compile(
                r"(?P<ts>\d+\.\d+)\s+(?P<id>[A-Fa-f0-9]+)\s+(?P<dlc>\d+)\s+(?P<data>(?:[A-Fa-f0-9]{2}\s*)+)"
            ),
            # 4. Old CANalyzer: ts id Tx/Rx dlc bytes
            re.compile(
                r"(?P<ts>\d+\.\d+)\s+(?P<id>[A-Fa-f0-9]+)\s+(Tx|Rx)\s+(?P<dlc>\d+)\s+(?P<data>(?:[A-Fa-f0-9]{2}\s*)+)"
            )
        ]

        try:
            with open(self.file_path, "r") as f:
                for line in f:

                    # skip headers
                    if line.startswith(("date", "base", "//", "Begin", "End", "version")):
                        continue

                    line = line.strip()
                    matched = False

                    for pattern in patterns:
                        m = pattern.match(line)
                        if m:
                            matched = True

                            ts = float(m.group("ts"))
                            msg_id = m.group("id")
                            dlc = int(m.group("dlc"))
                            data_bytes = m.group("data").strip().split()

                            # pad to 8 bytes
                            data_bytes = data_bytes + ["00"] * (8 - len(data_bytes))

                            parsed_lines.append([ts, msg_id, dlc] + data_bytes)
                            break

                    # if nothing matched → ignore line silently
                    if not matched:
                        continue

            # final DF
            cols = ["timestamp", "id", "dlc"] + [f"byte_{i}" for i in range(8)]
            self.data = pd.DataFrame(parsed_lines, columns=cols)

            return True

        except Exception as e:
            print("Parsing Error:", e)
            return False


    def get_summary(self):
        if self.data is None:
            print("No data loaded.")
            return None
        return {
            "total_frames": len(self.data),
            "unique_ids": self.data["id"].nunique(),
            "min_time": self.data["timestamp"].min(),
            "max_time": self.data["timestamp"].max()
        }
    
    def filter_by_id(self, msg_id):
        return self.data[self.data["id"] == msg_id]

    def filter_by_time(self, start, end):
        return self.data[(self.data["timestamp"] >= start) & 
                         (self.data["timestamp"] <= end)]
    
    def plot_id_frequency(self):
        freq = self.data["id"].value_counts()
        fig, ax = plt.subplots()
        ax.bar(freq.index.astype(str), freq.values)
        ax.set_title("CAN ID Frequency")
        ax.set_xlabel("Message ID")
        ax.set_ylabel("Count")
        fig.tight_layout()
        st.pyplot(fig)   # <-- This displays the plot in the web UI

    
    def plot_timestamp_vs_id(self):
        fig, ax = plt.subplots()
        ax.scatter(self.data["timestamp"], self.data["id"])
        ax.set_title("Timestamp vs Message ID")
        ax.set_xlabel("Timestamp (s)")
        ax.set_ylabel("Message ID")
        fig.tight_layout()
        st.pyplot(fig)

    def plot_byte(self, byte_index):
        if byte_index < 0 or byte_index > 7:
            print("Invalid byte index (0-7).")
            return
        col = f"byte_{byte_index}"
        # Convert hex string ("5C") to integer (92)
        # Handles missing or malformed bytes safely
        self.data[col] = self.data[col].apply(lambda x: int(x, 16) if isinstance(x, str) else 0)
        fig, ax = plt.subplots()
        plt.figure(figsize=(8, 4))
        ax.plot(self.data["timestamp"], self.data[col])
        ax.set_title(f"Byte {byte_index} vs Time")
        ax.set_xlabel("Timestamp")
        ax.set_ylabel("Value")
        fig.tight_layout()
        st.pyplot(fig)

    def export_csv(self, output_path):
        if self.data is None:
            print("No data loaded.")
            return
        self.data.to_csv(output_path, index=False)
        print(f"Exported CSV to {output_path}")
    
    def decode_all_frames(self):
        if self.data is None:
            return None
        # BONUS SAFETY: Decode only IDs that exist in both ASC & DBC
        id_report = self.compare_asc_dbc_ids()
        safe_ids = set(id_report["matched_ids"]) if id_report else set()

        decoded_output = []

        for _, row in self.data.iterrows():
            # skip IDs that do not match between ASC and DBC
            if safe_ids and row["id"] not in safe_ids:
                continue

            msg_id = row["id"]
            data = [row[f"byte_{i}"] for i in range(8)]

            decoded = self.decoder.decode_frame(msg_id, data)
            
            if decoded:
                decoded_output.append({
                    "timestamp": row["timestamp"],
                    "id": msg_id,
                    **decoded  # expand dict of signals
                })

        return decoded_output
    
    def compare_asc_dbc_ids(self):
        """
        Compare ASC CAN IDs vs DBC Message IDs.
        Returns a dictionary with:
        - matched_ids
        - asc_not_in_dbc
        - dbc_not_in_asc
        """
        if self.data is None or self.decoder.db is None:
            return None

        # Extract IDs from ASC (strings like "2B0")
        asc_ids = set(self.data["id"].unique())

        # Extract IDs from DBC (convert to hex strings)
        dbc_ids = set([format(msg.frame_id, 'X').upper() for msg in self.decoder.db.messages])

        # Compare
        matched = asc_ids.intersection(dbc_ids)
        asc_missing = asc_ids - dbc_ids
        dbc_missing = dbc_ids - asc_ids

        return {
            "matched_ids": sorted(list(matched)),
            "asc_not_in_dbc": sorted(list(asc_missing)),
            "dbc_not_in_asc": sorted(list(dbc_missing)),
        }
