from logging.handlers import RotatingFileHandler
import gzip
import itertools
import os
import shutil


class RollingGzipFileHandler(RotatingFileHandler):
    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None

        for i in itertools.count(1):
            name, extension = os.path.splitext(self.baseFilename)
            nextName = f"{name}.{i}{extension}.gz"
            if not os.path.exists(nextName):
                with open(self.baseFilename, "rb") as original_log:
                    with gzip.open(nextName, 'wb') as gzipped_log:
                        shutil.copyfileobj(original_log, gzipped_log)
                os.remove(self.baseFilename)
                break

        if not self.delay:
            self.stream = self._open()
