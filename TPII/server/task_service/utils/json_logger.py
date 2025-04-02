import logging
import json
import os
from datetime import datetime

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "nivel": record.levelname,
            "componente": record.name,
            "mensaje": record.getMessage()
        }
        if record.exc_info:
            log_record["excepcion"] = self.formatException(record.exc_info)
        return json.dumps(log_record, ensure_ascii=False)

def get_json_logger(nombre_componente: str, ruta_archivo: str):
    logger = logging.getLogger(nombre_componente)
    logger.setLevel(logging.INFO)

    # Evita agregar múltiples handlers si ya existe
    if not logger.handlers:
        os.makedirs(os.path.dirname(ruta_archivo), exist_ok=True)
        handler = logging.FileHandler(ruta_archivo, encoding='utf-8')
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)

    return logger
