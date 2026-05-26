import logging
import sys
import structlog
import os

log_level = os.getenv("LOG_LEVEL", "INFO").upper()

def setup_logging():
    """Configures structlog to emit structured JSON logs."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,           # Adds 'level': 'info', etc.
            structlog.stdlib.add_logger_name,         # Adds the logger name
            structlog.processors.TimeStamper(fmt="iso"), # Adds 'timestamp' in ISO format
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,     # Formats tracebacks as JSON-safe strings if exc_info=True
            structlog.processors.JSONRenderer()       # Outputs the final log as a JSON string
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Intercept standard library logging and route it to stdout as INFO
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=log_level)