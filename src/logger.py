import logging


ASCII_LOGO = '''

      *****
     *******   CHESS
      *****
       ***@@@@@@@@@@
       *** @@@@@@@@    REPERTOIRE
     .*****.@@@@@@
    ********@@@@@ %%%%
   *********@@@@@%%%%%%%%%%#   GENERATOR
           @@@@@@%%%%%%
          @@@@@@@%%%%%%%%
         @@@@@@@@@%%%%%%%%%
                  %%%%%%%%%
                  %%%%%%%%
                %%%%%%%%%%%%
                 %%%%%%%%%%

'''


class Logger:
    def __init__(self, filename, log_levels=None):
        self.logger = logging.getLogger("custom_logger")
        self.logger.setLevel(logging.DEBUG)

        filepath = filename + '.log'
        file_handler = logging.FileHandler(filepath)
        self.logger.addHandler(file_handler)

        self._print_header(ASCII_LOGO)

        self.logger.handlers[0].setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "[%(asctime)s - %(levelname)s] %(message)s"
        )
        self.logger.handlers[0].setFormatter(formatter)

        if log_levels:
            self._set_log_levels(log_levels)

    def _set_log_levels(self, log_levels):
        if not isinstance(log_levels, list):
            log_levels = [log_levels]

        valid_log_levels = [
            "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
        ]

        for handler in self.logger.handlers:
            handler.setLevel(min([getattr(logging, level)
                             for level in log_levels if level in valid_log_levels]))

    def _print_header(self, ascii_art):
        self.logger.handlers[0].setFormatter(logging.Formatter("%(message)s"))
        self.logger.info(ascii_art)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        print(message)
        self.logger.warning(message)

    def error(self, message):
        print(message)
        self.logger.error(message)

    def critical(self, message):
        print(message)
        self.logger.critical(message)
