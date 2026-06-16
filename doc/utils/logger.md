 ---                                                                                                                           
  What logger.py does                                                                                                           
                                                                                                                                
  It's a factory function — you call get_logger(name) and it hands you back a configured logging.Logger object.                 
                  
  Python's logging system (the mental model)

  Think of it as three layers:

  Logger  →  Handler  →  Formatter
    (what)     (where)      (how it looks)

  - Logger: the object you call .info(), .debug(), .error() on
  - Handler: decides where output goes — console, file, etc.
  - Formatter: decides how each line looks — timestamp, name, level, message

  ---
  Line-by-line breakdown

  logger = logging.getLogger(name)
  Python keeps a global registry of loggers by name. If "data_cleaner" already exists, you get the same object back. This is
  intentional — it prevents duplicate loggers.

  logger.setLevel(getattr(logging, LOG_LEVEL))
  LOG_LEVEL = "DEBUG" (from settings.py) is a string. getattr(logging, "DEBUG") converts it to the integer constant
  logging.DEBUG (= 10). This sets the minimum severity to log.

  if logger.handlers:
      return logger
  Critical guard. If you call get_logger("data_cleaner") twice, Python returns the same logger object — but without this check
  you'd add a second handler, and every log message would print twice.

  formatter = logging.Formatter(
      '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
      datefmt='%Y-%m-%d %H:%M:%S'
  )
  Defines the output format. The %()s tokens are filled in at log time:

  ┌───────────────┬─────────────────────┐
  │     Token     │   Example output    │
  ├───────────────┼─────────────────────┤
  │ %(asctime)s   │ 2026-03-12 14:30:05 │
  ├───────────────┼─────────────────────┤
  │ %(name)s      │ data_cleaner        │
  ├───────────────┼─────────────────────┤
  │ %(levelname)s │ DEBUG               │
  ├───────────────┼─────────────────────┤
  │ %(message)s   │ Cleaned 200 rows    │
  └───────────────┴─────────────────────┘

  So a full line looks like:
  2026-03-12 14:30:05 - data_cleaner - DEBUG - Cleaned 200 rows

  ---
  The function is incomplete

  The file cuts off — it's missing the handler creation and return logger. A complete version would look like:

  handler = logging.StreamHandler()   # send to console
  handler.setFormatter(formatter)
  logger.addHandler(handler)
  return logger

  ---
  How it's used in practice

  In any module (e.g., data_cleaner.py):

  from utils.logger import get_logger

  logger = get_logger("data_cleaner")

  logger.debug("Starting unicode clean")   # only shows if LOG_LEVEL=DEBUG
  logger.info("Cleaned 200 rows")          # shows for INFO and above
  logger.warning("Empty value in row 42")  # shows for WARNING and above
  logger.error("Failed to parse date")     # always shows

  The name you pass ("data_cleaner") appears in every log line, so when you have 5 modules all logging, you can instantly see
  which module produced each message.

  ---
  Bottom line: get_logger(name) is a thin wrapper around Python's built-in logging module. It ensures every module gets a
  consistently formatted logger, and the duplicate-handler guard makes it safe to call multiple times.


Level  Value  When to use 
DEBUG   10    Everything — detailed tracing
INFO    20    Normal operation — "loaded 200 rows"
WARNING 30    Something unexpected but not broken
ERROR   40    Something failed