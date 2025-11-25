import pandas as pd
import re
import matplotlib.pyplot as plt

class CANLogExtractor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None

    def load_log(self):
        """
        Reads ASC-like CAN logs.
        Expected format:
        <timestamp> <ID> <DLC> <data-bytes...>
        """
        parsed_lines = []

        pattern = r"(\d+\.\d+)\s+([0-9A-Fa-fx]+)\s+(\d+)\s+(.*)"
        try:
            with open(self.file_path, "r") as f:
                for line in f:
                    match = re.match(pattern, line.strip())
                    if match:
                        timestamp = float(match.group(1))
                        msg_id = match.group(2)
                        dlc = int(match.group(3))
                        data = match.group(4).strip().split()
                        parsed_lines.append([timestamp, msg_id, dlc] + data)

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
        freq.plot(kind="bar")
        plt.title("CAN ID Frequency")
        plt.xlabel("Message ID")
        plt.ylabel("Count")
        plt.tight_layout()
        plt.show()
    
    def plot_timestamp_vs_id(self):
        plt.scatter(self.data["timestamp"], self.data["id"])
        plt.title("Timestamp vs Message ID")
        plt.xlabel("Timestamp (s)")
        plt.ylabel("Message ID")
        plt.tight_layout()
        plt.show()
    
    def plot_byte(self, byte_index):
        if byte_index < 0 or byte_index > 7:
            print("Invalid byte index (0-7).")
            return
        col = f"byte_{byte_index}"
        self.data[col] = self.data[col].astype(int)
        plt.plot(self.data["timestamp"], self.data[col])
        plt.title(f"Byte {byte_index} vs Time")
        plt.xlabel("Timestamp")
        plt.ylabel("Value")
        plt.tight_layout()
        plt.show()

    def export_csv(self, output_path):
        if self.data is None:
            print("No data loaded.")
            return
        self.data.to_csv(output_path, index=False)
        print(f"Exported CSV to {output_path}")



