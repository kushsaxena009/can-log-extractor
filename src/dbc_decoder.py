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

    def decode_frame(self, message_id, data_bytes):
        """
        Returns decoded signals if message exists in DBC.
        """
        if self.db is None:
            return None

        try:
            message = self.db.get_message_by_frame_id(int(message_id, 16))
            data = bytes(int(b, 16) for b in data_bytes)
            return message.decode(data)
        except:
            return None
