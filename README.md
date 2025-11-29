# CAN Log Extractor + Visualizer  
ASC Parser • CSV Export • DBC Decoder • Streamlit UI

A simple and powerful Python tool to parse automotive CAN logs (ASC format), visualize CAN traffic patterns, and decode signals using DBC files.  
Designed for testers, validation engineers, embedded developers, and researchers working with CAN data.

---

## 🚀 Features

### 🔹 Multi-Format ASC Parsing  
Supports:
- Vector ASC (Tx/Rx)
- Vector ASC (no direction)
- ETAS ASC
- CANalyzer legacy ASCII logs
- ASC logs with headers (date, base, comments)

### 🔹 Data Visualization (Streamlit UI)
- CAN ID frequency plot  
- Timestamp vs ID scatter plot  
- Byte value trend plot  
- CSV export  

### 🔹 DBC-Based Signal Decoding
- Load any valid DBC file  
- Decode matched message IDs  
- Skip mismatched IDs safely  
- ASC–DBC mismatch report  

### 🔹 Data Export
- Convert ASC → CSV  
- Clean pandas DataFrame for analysis  

---

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/kushsaxena009/can-log-extractor.git
cd can-log-extractor
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ▶ Running the Streamlit App

```bash
streamlit run app.py
```

This launches the UI where you can:

- Upload ASC log files  
- Upload optional DBC files  
- Visualize message frequency  
- Decode signals  
- Export CSV  

---

## 📁 Project Structure

```
can-log-extractor/
│
├── src/
│   ├── extractor.py        # ASC parser + visualization + decode pipeline
│   ├── dbc_decoder.py      # DBC parsing & decoding
│   └── app.py              # Streamlit web app
│
├── examples/
│   ├── sample.asc
│   └── sample.dbc
│
├── temp/
│   └── .gitkeep            # For uploaded temporary files
│
├── assets/
│   ├── screenshots/        # UI screenshots
│   └── gumroad/            # Gumroad product images
│
├── requirements.txt
└── README.md
```

---

## 📊 Example Visualizations

> *(Screenshots will be added later)*

- ID Frequency Bar Chart  
- Timestamp vs ID Scatter  
- Byte Trend Line  

---

## 🧠 ASC–DBC Consistency Check

The tool automatically detects:

✔ Matched message IDs  
✔ IDs in ASC but **not** in DBC  
✔ IDs in DBC but **not** in ASC  
✔ Only decodes safe matched IDs  

This prevents incorrect signal decoding.

---

## 🧪 Example API Usage

```python
from src.extractor import CANLogExtractor

extractor = CANLogExtractor("sample.asc", dbc_path="sample.dbc")
extractor.load_log()

print(extractor.get_summary())

decoded = extractor.decode_all_frames()
print(decoded)
```

---

## 👤 Author

**Kushagra Saxena**  
Automotive Software Engineer  
Building tools for CAN diagnostics, data visualization, and automation.

---

## ⭐ Contributing

Pull requests and feedback are welcome.  
If you find this tool helpful, please ⭐ star the repo!

---

## 📄 License

MIT License  
