from src.config import settings

if settings.debug:
    from devtools import debug
else:

    def debug(*_args, **_kwargs):
        pass

# Assigning the same variable 'debug' to itself (self-assigning-variable)
# It is because otherwise import of debug from devtools will be unused
debug = debug  # pylint: disable=W0127
