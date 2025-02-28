import struct
import serial
import time

class ModbusProtocol:
    def __init__(self, device_id=1, baudrate=9600, bytesize=8, parity="E", stopbits=1):
        # Atributos de comunicação serial
        self.__device_id = device_id
        self.__baudrate = baudrate
        self.__bytesize = bytesize
        self.__parity = parity
        self.__stopbits = stopbits

        self.received_data = None

    def __calculate_crc(self, data):
        """Calcula o CRC-16 Modbus"""
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1

        return struct.pack('<H', crc)  # Retorna o CRC em formato correto (2 bytes, little-endian)


    def __getHighLowByte(self, data):
        """Converte um valor percentual para bytes Modbus RTU."""
        valor_convertido = data
        byte_alto = (valor_convertido >> 8) & 0xFF
        byte_baixo = valor_convertido & 0xFF
        return [byte_alto, byte_baixo]  # Retorna lista [Hi, Lo]

    def sendRequest(self, port, device_id, function, address, data):
        try:
            # Construção de dados para a comunicação serial
            ser = serial.Serial(
                port=port,
                baudrate=self.__baudrate,
                bytesize=self.__bytesize,
                parity=self.__parity,
                stopbits=self.__stopbits,
                timeout=1
            )

            # Construção do frame Modbus RTU
            frameRTU = bytes([device_id, function, *self.__getHighLowByte(address), *self.__getHighLowByte(data)])

            # Cálculo e adição do CRC ao frame
            frameRTU += self.__calculate_crc(frameRTU)

            # Abertura da porta serial
            if not ser.is_open:
                ser.open()

            # Envio da requisição
            ser.write(frameRTU)

            # Espera Modbus
            time.sleep(0.1)

            # Recebendo a resposta
            self.received_data = ser.read(ser.in_waiting)

            print(f"Requisição Enviada: {frameRTU.hex()}")
            print(f"Resposta do Equipamento: {self.received_data.hex()}\n")

            ser.close()
        except Exception as e:
            print(f"Erro ao enviar dados: {e}")

