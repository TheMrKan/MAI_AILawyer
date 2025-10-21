import logging


class BlockDebugByMask(logging.Filter):
    def __init__(self, mask):
        super().__init__()
        self.mask = mask

    def filter(self, record):
        # отключает Debug логгеры, начинающиеся с маски
        if record.levelno != logging.DEBUG:
            return True

        return not record.name.startswith(self.mask)


def setup():
    handler = logging.StreamHandler()

    handler.addFilter(BlockDebugByMask("httpcore."))
    handler.addFilter(BlockDebugByMask("cerebras."))
    handler.addFilter(BlockDebugByMask("httpx"))

    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s %(levelname)s][%(name)s]  %(message)s",
        handlers=[handler]
    )
