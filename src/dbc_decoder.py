import cantools

class DBCDecoder:
    def __init__(self, dbc_path):
        self.db = None
        if dbc_path:
            try:
                self.db = cantools.database.load_file(dbc_path)
                print("DBC loaded successfully.")
            except Exception as e:
                print("DBC load error:", e)
                self.db = None

    def decode_frame(self, message_id, data_bytes):
        """
        message_id: hex string like "2B0"
        data_bytes: list of integers like [12, 34, 56, 78, 0, 0, 0, 0]
        """

        if self.db is None:
            return None

        try:
            # Convert hex ID string to decimal
            frame_id = int(message_id, 16)

            # Find the message definition in DBC
            message = self.db.get_message_by_frame_id(frame_id)
            if message is None:
                return None

            # Ensure byte array is valid
            payload = bytes(int(b) for b in data_bytes)

            # Decode using cantools
            return message.decode(payload)

        except Exception as e:
            print("Decode error:", e)
            return None
