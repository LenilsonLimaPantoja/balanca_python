import RPi.GPIO as GPIO
import time
import threading

# Classe para controlar o sensor HX711 (célula de carga)
class HX711:

    # Inicialização da classe
    def __init__(self, dout, pd_sck, gain=128):
        self.PD_SCK = pd_sck  # Pino de clock do HX711
        self.DOUT = dout      # Pino de dados do HX711

        # Mutex para leitura do sensor, evita que múltiplas threads acessem ao mesmo tempo
        self.readLock = threading.Lock()
        
        # Configuração dos pinos GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.PD_SCK, GPIO.OUT)
        GPIO.setup(self.DOUT, GPIO.IN)

        self.GAIN = 0  # Ganho inicial

        # Unidade de referência usada para calibrar o peso
        self.REFERENCE_UNIT = 1
        self.REFERENCE_UNIT_B = 1

        # Valores de offset para zerar o sensor
        self.OFFSET = 1
        self.OFFSET_B = 1
        self.lastVal = int(0)

        self.DEBUG_PRINTING = False  # Ativa logs de debug

        self.byte_format = 'MSB'  # Formato de byte
        self.bit_format = 'MSB'   # Formato de bit

        self.set_gain(gain)  # Configura o ganho inicial
        
        # Espera 1 segundo para estabilizar o sensor
        time.sleep(1)


    # Converte valor de 24 bits em complemento de dois
    def convertFromTwosComplement24bit(self, inputValue):
        return -(inputValue & 0x800000) + (inputValue & 0x7fffff)

    
    # Verifica se o HX711 está pronto para leitura
    def is_ready(self):
        return GPIO.input(self.DOUT) == 0

    
    # Configura o ganho do sensor
    def set_gain(self, gain):
        if gain == 128:
            self.GAIN = 1
        elif gain == 64:
            self.GAIN = 3
        elif gain == 32:
            self.GAIN = 2

        GPIO.output(self.PD_SCK, False)
        # Descarta uma leitura inicial
        self.readRawBytes()

        
    def get_gain(self):
        # Retorna o ganho atual em valor numérico
        if self.GAIN == 1:
            return 128
        if self.GAIN == 3:
            return 64
        if self.GAIN == 2:
            return 32
        return 0  # Nunca deve chegar aqui
        

    # Lê um bit do HX711
    def readNextBit(self):
       GPIO.output(self.PD_SCK, True)   # Sobe o clock
       GPIO.output(self.PD_SCK, False)  # Desce o clock
       value = GPIO.input(self.DOUT)
       return int(value)  # Converte boolean para int


    # Lê um byte do HX711
    def readNextByte(self):
       byteValue = 0
       for x in range(8):
          if self.bit_format == 'MSB':
             byteValue <<= 1
             byteValue |= self.readNextBit()
          else:
             byteValue >>= 1              
             byteValue |= self.readNextBit() * 0x80
       return byteValue  # Retorna o byte lido
        

    # Lê três bytes brutos do HX711
    def readRawBytes(self):
        self.readLock.acquire()  # Bloqueia leitura

        # Espera sensor ficar pronto
        while not self.is_ready():
           pass

        # Lê os 3 bytes
        firstByte  = self.readNextByte()
        secondByte = self.readNextByte()
        thirdByte  = self.readNextByte()

        # Ajusta ganho conforme configuração
        for i in range(self.GAIN):
           self.readNextBit()

        self.readLock.release()  # Libera leitura

        # Retorna os bytes lidos no formato correto
        if self.byte_format == 'LSB':
           return [thirdByte, secondByte, firstByte]
        else:
           return [firstByte, secondByte, thirdByte]


    # Lê valor de 24 bits como inteiro com sinal
    def read_long(self):
        dataBytes = self.readRawBytes()

        if self.DEBUG_PRINTING:
            print(dataBytes,)
        
        # Junta os bytes em um valor de 24 bits
        twosComplementValue = ((dataBytes[0] << 16) |
                               (dataBytes[1] << 8)  |
                               dataBytes[2])

        if self.DEBUG_PRINTING:
            print("Twos: 0x%06x" % twosComplementValue)
        
        # Converte para inteiro com sinal
        signedIntValue = self.convertFromTwosComplement24bit(twosComplementValue)
        self.lastVal = signedIntValue
        return int(signedIntValue)

    
    # Lê média de múltiplas amostras para reduzir ruído
    def read_average(self, times=3):
        if times <= 0:
            raise ValueError("times deve ser >= 1")

        if times == 1:
            return self.read_long()

        if times < 5:
            return self.read_median(times)

        valueList = [self.read_long() for _ in range(times)]
        valueList.sort()

        # Remove 20% de outliers
        trimAmount = int(len(valueList) * 0.2)
        valueList = valueList[trimAmount:-trimAmount]

        return sum(valueList) / len(valueList)


    # Leitura baseada na mediana
    def read_median(self, times=3):
       if times <= 0:
          raise ValueError("times deve ser > 0")
      
       if times == 1:
          return self.read_long()

       valueList = [self.read_long() for _ in range(times)]
       valueList.sort()

       if (times & 0x1) == 0x1:
          return valueList[len(valueList) // 2]
       else:
          midpoint = len(valueList) // 2
          return sum(valueList[midpoint:midpoint+2]) / 2.0


    # Pega valor do canal A
    def get_value_A(self, times=3):
        return self.read_median(times) - self.get_offset_A()

    # Pega valor do canal B
    def get_value_B(self, times=3):
        g = self.get_gain()
        self.set_gain(32)
        value = self.read_median(times) - self.get_offset_B()
        self.set_gain(g)
        return value

    # Pega peso em gramas no canal A
    def get_weight_A(self, times=3):
        value = self.get_value_A(times)
        return value / self.REFERENCE_UNIT

    # Pega peso em gramas no canal B
    def get_weight_B(self, times=3):
        value = self.get_value_B(times)
        return value / self.REFERENCE_UNIT_B
    

    # Faz tare (zera o peso) no canal A
    def tare_A(self, times=15):
        backupReferenceUnit = self.get_reference_unit_A()
        self.set_reference_unit_A(1)
        value = self.read_average(times)
        if self.DEBUG_PRINTING:
            print("Tare A value:", value)
        self.set_offset_A(value)
        self.set_reference_unit_A(backupReferenceUnit)
        return value

    # Faz tare no canal B
    def tare_B(self, times=15):
        backupReferenceUnit = self.get_reference_unit_B()
        self.set_reference_unit_B(1)
        backupGain = self.get_gain()
        self.set_gain(32)
        value = self.read_average(times)
        if self.DEBUG_PRINTING:
            print("Tare B value:", value)
        self.set_offset_B(value)
        self.set_gain(backupGain)
        self.set_reference_unit_B(backupReferenceUnit)
        return value


    # Configura formato de leitura de bytes e bits
    def set_reading_format(self, byte_format="LSB", bit_format="MSB"):
        if byte_format in ["LSB", "MSB"]:
            self.byte_format = byte_format
        else:
            raise ValueError(f"byte_format inválido: {byte_format}")

        if bit_format in ["LSB", "MSB"]:
            self.bit_format = bit_format
        else:
            raise ValueError(f"bit_format inválido: {bit_format}")


    # Define offset para canal A ou B
    def set_offset_A(self, offset):
        self.OFFSET = offset

    def set_offset_B(self, offset):
        self.OFFSET_B = offset

    def get_offset_A(self):
        return self.OFFSET

    def get_offset_B(self):
        return self.OFFSET_B


    # Define unidade de referência para canal A ou B
    def set_reference_unit_A(self, reference_unit):
        if reference_unit == 0:
            raise ValueError("Reference unit não pode ser 0!")
        self.REFERENCE_UNIT = reference_unit

    def set_reference_unit_B(self, reference_unit):
        if reference_unit == 0:
            raise ValueError("Reference unit não pode ser 0!")
        self.REFERENCE_UNIT_B = reference_unit

    def get_reference_unit_A(self):
        return self.REFERENCE_UNIT

    def get_reference_unit_B(self):
        return self.REFERENCE_UNIT_B


    # Desliga o sensor (power down)
    def power_down(self):
        self.readLock.acquire()
        GPIO.output(self.PD_SCK, False)
        GPIO.output(self.PD_SCK, True)
        time.sleep(0.0001)
        self.readLock.release()           


    # Liga o sensor (power up)
    def power_up(self):
        self.readLock.acquire()
        GPIO.output(self.PD_SCK, False)
        time.sleep(0.0001)
        self.readLock.release()
        if self.get_gain() != 128:
            self.readRawBytes()


    # Reinicia o sensor
    def reset(self):
        self.power_down()
        self.power_up()