#!/usr/bin/env python
"""
serial_logger
Simple utility for logging data sent via serial port
"""

import logging
import os
from datetime import datetime
from dataclasses import dataclass, field

import serial

__author__ = "N. Dornseif"
__copyright__ = "Copyright 2023, N. Dornseif"
__license__ = "GNU General Public License v3.0"
__version__ = "1.0.0"


@dataclass
class SerialConfiguration():
    """
    A collection of variables used to configure a serial port
    """
    port: str = '/dev/ttyUSB0'
    baudrate: int = 115200
    timeout: float = 90.0
    # Received bytes are seperated into data points at this seperator
    data_seperator: bytes = b'\n'
    # Bytes listed in the remove list will be removed from received data
    remove_byte_list: list[bytes] = field(default_factory=list)
    # A file path that the recorded data will be written at
    data_file_path: str = None
    data_encoding: str = 'utf-8'
    data_bits = serial.EIGHTBITS
    stop_bits = serial.STOPBITS_ONE
    parity = serial.PARITY_NONE

    def __post_init__(self):
        """
        Initialize the default parameters
        """
        if not self.remove_byte_list:
            self.remove_byte_list = [b'\n', b'\r']

        if self.data_file_path is None:
            root_path = os.path.dirname(os.path.realpath(__file__))
            filename = datetime.now().isoformat() + '.csv'
            self.data_file_path = os.path.join(root_path, filename)


def configure_logger() -> None:
    """
    Configures a logger accessible using __name__ as its identifier
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


def cleanup_port() -> None:
    """
    Close serial port during exit
    """
    main_logger = logging.getLogger(__name__)
    serial_port.close()
    main_logger.info('Serial port %s closed.', serial_port.port)


def write_data_point(
        data_file_path: str,
        data_point: str,
        add_timestamp: bool = True,
        suffix: str = '\n',
        time_seperator: str = ',',
        file_encoding: str = 'utf-8') -> None:
    """
    Attaches a timestamp to a datapoint and writes it to the specified file
    The time seperator is placed between the timestamp and the data
    """
    with open(data_file_path, mode='a', encoding=file_encoding) as file:
        write_string = data_point + suffix
        if add_timestamp:
            timestamp = datetime.now().isoformat()
            write_string = timestamp + time_seperator + write_string
        file.write(write_string)


def main() -> None:
    """
    The Serial loggers main function
    """
    global serial_port
    configure_logger()
    main_logger = logging.getLogger(__name__)
    serial_config = SerialConfiguration()
    serial_port = serial.Serial(
        port=serial_config.port,
        baudrate=serial_config.baudrate,
        bytesize=serial_config.data_bits,
        parity=serial_config.parity,
        stopbits=serial_config.stop_bits,
        timeout=serial_config.timeout)
    try:
        serial_port.open()
    except serial.serialutil.SerialException as exc:
        if str(exc) == "Port is already open.":
            main_logger.warning(
                'Serial port %s is already open.', serial_port.port)
        else:
            raise

    main_logger.info('Saving data to file: %s', serial_config.data_file_path)
    current_data_point = b''
    while True:
        read_byte = serial_port.read()
        if read_byte not in serial_config.remove_byte_list:
            current_data_point += read_byte

        if read_byte == serial_config.data_seperator:
            current_data_point = current_data_point.decode(
                serial_config.data_encoding)

            main_logger.info('Read data point: %s', current_data_point)
            write_data_point(
                serial_config.data_file_path, current_data_point,
                file_encoding=serial_config.data_encoding)
            current_data_point = b''


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        cleanup_port()
