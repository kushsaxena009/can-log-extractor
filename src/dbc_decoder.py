import cantools

class DBCDecoder:
    def __init__(self, dbc_path):
        self.db = cantools.database.load_file(dbc_path)

    def decode_message(self, can_id, data):
        try:
            msg = self.db.get_message_by_frame_id(int(can_id, 16))
            decoded = msg.decode(bytes(data))
            return decoded
        except:
            return None
