from extractor import CANLogExtractor

log = CANLogExtractor("../examples/sample_can_log.asc")
if log.load_log():
    print("Summary:", log.get_summary())
    log.plot_id_frequency()
