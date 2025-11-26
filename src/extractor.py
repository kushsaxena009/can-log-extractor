import pandas as pd
import re
import matplotlib.pyplot as plt
import streamlit as st

class CANLogExtractor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None
    
    def load_log(self):
        """
        Reads Vector ASC CAN logs.
        Format example:
        <timestamp> <channel> <ID> Tx d <DLC> <data bytes...>
        """
        parsed_lines = []

        # Correct ASC regex
        pattern = re.compile(
            r"(?P<ts>\d+\.\d+)\s+"                  # timestamp
            r"(?P<channel>\d+)\s+"                  # channel number
            r"(?P<id>[0-9A-Fa-f]+)\s+"              # CAN ID
            r"(Tx|Rx)\s+"                           # direction
            r"d\s+(?P<dlc>\d+)\s+"                  # 'd' + DLC
            r"(?P<data>(?:[0-9A-Fa-f]{2}\s+){0,8})" # up to 8 bytes
        )
        

        #pattern = r"(\d+\.\d+)\s+\d+\s+([A-Fa-f0-9]+)\s+Tx\s+d\s+(\d+)\s+((?:[A-Fa-f0-9]{2}\s+)*[A-Fa-f0-9]{2})"
        #pattern = r"(\d+\.\d+)\s+\d+\s+([A-Fa-f0-9]+)\s+(?:Tx\s+)?d\s+(\d+)\s+((?:[A-Fa-f0-9]{2}\s*)+)"


        try:
            with open(self.file_path, "r") as f:
                for line in f:
                    m = pattern.search(line)
                    if m:
                        data_bytes = m.group("data").strip().split()

                        # Ensure exactly 8 columns (pad missing bytes)
                        padded = data_bytes + ["00"]*(8 - len(data_bytes))

                        parsed_lines.append([
                            float(m.group("ts")),
                            m.group("id"),
                            int(m.group("dlc")),
                            *padded
                        ])

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
        # freq = self.data["id"].value_counts()
        # fig, ax = plt.subplots()
        # freq.plot(kind="bar")
        # plt.title("CAN ID Frequency")
        # plt.xlabel("Message ID")
        # plt.ylabel("Count")
        # plt.tight_layout()
        # plt.show()
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



