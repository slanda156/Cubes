# Import needed modules
import socket

from classes.constants import logger, traceback

class indexServer:
    def __init__(self, ip, port, timeout):
        self.ip = ip
        self.port = int(port)
        self.timeout = int(timeout)
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.settimeout(self.timeout)

    def connect(self):
        logger.debug(f"Connecting to {self.ip}")
        try:
            self.connection.connect((self.ip, self.port))
            self.connection.send(b"client")
            logger.info(self.connection.recv(4096).decode())
        except ConnectionRefusedError:
            logger.debug("Connection refused")
        except ConnectionAbortedError:
            logger.debug("Connection timeout")
        except:
            logger.debug(traceback.format_exc())

class gameServer:
    def __init__(self, ip, port, timeout):
        self.ip = ip
        self.port = port
        self.timeout = int(timeout)
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        logger.debug(f"Connecting to {self.ip}")
        try:
            self.connection.connect((self.ip, self.port))
        except ConnectionRefusedError:
            logger.debug("Connection refused")
        except:
            logger.debug(traceback.format_exc())
