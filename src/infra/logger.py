import os
import logging
from threading import Lock
from collections import deque
import inspect
from types import FrameType
from typing import Optional, List
from .config import CONFIG

class Logger:
    _instance: Optional['Logger'] = None
    _lock: Lock = Lock()
    _initialized: bool = False

    def __new__(cls) -> 'Logger':
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not self._initialized:
            self._initialized: bool = True
            self._log_records: deque[str] = deque(maxlen=100)

        os.makedirs(os.path.dirname(CONFIG.logs_path), exist_ok=True)

        self.logger: logging.Logger = logging.getLogger("simulador")
        self.logger.setLevel(CONFIG.logs_level)

        if not self.logger.handlers:
            # Handler para arquivo com formatação específica para DEBUG
            file_handler = logging.FileHandler(CONFIG.logs_path)
            file_handler.setFormatter(DebugFormatter())

            # Handler para console - apenas INFO
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)  # Apenas INFO no console
            # console_handler.addFilter(InfoOnlyFilter())  # Filtro para apenas INFO
            console_formatter = logging.Formatter("[%(levelname)s] %(message)s")
            console_handler.setFormatter(console_formatter)

            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
            self.clear_log_file()

    def clear_log_file(self) -> None:
        try:
            if os.path.exists(CONFIG.logs_path):
                with open(CONFIG.logs_path, 'w') as file:
                    file.truncate(0)
                self.log_debug("Arquivo de Logs esvaziado")
        except Exception as e:
            self.log_error(f"Falha ao limpar Arquivo de Logs: {e}")

    def log_debug(self, message: str) -> None:
        try:
            frame: Optional[FrameType] = inspect.currentframe()
            caller_frame: Optional[FrameType] = frame.f_back if frame else None

            if caller_frame:
                filename: str = os.path.basename(caller_frame.f_code.co_filename)
                lineno: int = caller_frame.f_lineno

                record: logging.LogRecord = self.logger.makeRecord(
                    self.logger.name, logging.DEBUG, caller_frame.f_code.co_filename,
                    lineno, message, (), None
                )
                record.custom_filename = filename
                self.logger.handle(record)
            else:
                self.logger.debug(message)

            self._log_records.append(f"[DEBUG] {message}")

        except Exception:
            self.logger.debug(message)
            self._log_records.append(f"[DEBUG] {message}")

    def log_info(self, message: str) -> None:
        self.logger.info(message)
        self._log_records.append(f"[INFO] {message}")

    def log_warning(self, message: str) -> None:
        self.logger.warning(message)
        self._log_records.append(f"[WARNING] {message}")

    def log_error(self, message: str) -> None:
        self.logger.error(message)
        self._log_records.append(f"[ERROR] {message}")

    def get_log_records(self, count: Optional[int] = None) -> List[str]:
        try:
            with open(CONFIG.logs_path, "r") as file:
                lines: List[str] = [line.rstrip("\n") for line in file.readlines()]

            if count:
                return lines[-count:]
            return lines
        except Exception:
            if count:
                return list(self._log_records)[-count:]
            return list(self._log_records)

    def close(self) -> None:
        if hasattr(self, 'logger') and self.logger.handlers:
            for handler in self.logger.handlers[:]:  # Create a copy to iterate safely
                handler.close()
                self.logger.removeHandler(handler)

    @classmethod
    def reset_instance(cls) -> None:
        with cls._lock:
            if cls._instance is not None:
                cls._instance.close()
                cls._instance = None
                cls._initialized = False

class DebugFormatter(logging.Formatter):
    def __init__(self) -> None:
        super().__init__()
        self.debug_format: str = "%(asctime)s - %(name)s - [%(levelname)s] - %(custom_filename)s:%(lineno)d - %(message)s"
        self.default_format: str = "%(asctime)s - %(name)s - [%(levelname)s] - %(message)s"

    def format(self, record: logging.LogRecord) -> str:
        if record.levelno == logging.DEBUG and hasattr(record, 'custom_filename'):
            debug_formatter: logging.Formatter = logging.Formatter(self.debug_format)
            return debug_formatter.format(record)
        else:
            default_formatter: logging.Formatter = logging.Formatter(self.default_format)
            return default_formatter.format(record)
