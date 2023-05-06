# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 09:14:38 2020

@author: ktngl
"""
from math import log, log2
from random import randint, randrange
from math import log2, ceil

# Константы, применяемые для обозначения режима отображения элемента блока данных
RM_DATABLOCK = 0    # Как подблока данных
RM_INT = 1          # Как целого числа
RM_TEXT = 2         # Как текстовой строки
RM_BYTES = 3       # Как двоичной последовательности

elemSize = 8        # Размер элемента в битах, по умолчанию 8
retMode = RM_DATABLOCK # Режим отображения элемента, по умолчанию - в виде подблока данных

    
# Класс Datablock описывает объект, способный вести себя одновременно как:
#     - натуральное число;
#     - двоичная последовательность элементов.
# Инкапсулирует два "личных" поля:
#     - __value - значение блока данных, целое число (фактически - неотрицательное);
#     - __bitSize - установленный размер блока данных в битах.
# Примечание: значение __bitSize может быть не равным реальному размеру поля __value
class Datablock:
    # Конструктор по умолчанию устанавливает нулевое значение блока данных и нулевой размер
    def __init__(self):
        self.__value = 0
        self.__bitSize = 0
        
    # Метод asBytes() возвращает содержимое блока данных в виде двоичной последовательности
    def asBytes(self):
        barr = bytearray()
        v = self.__value
        while v != 0:
            barr.append(v % 256)
            v >>= 8
        return bytes(barr)
        
    # Метод asInt() возвращает содержимое блока данных в виде большого целого числа
    def asInt(self, base = 10):
        if base == 2:
            return bin(self.__value)
        elif base == 8:
            return oct(self.__value)
        elif base == 16:
            return hex(self.__value)
        else:
            return self.__value
    
    # Метод asText() возвращает содержимое блока данных в виде текста.
    # Иначе говоря, возвращает строку, закодированную значением self.__value.
    # Параметр encoding - кодировка
    def asText(self, encoding = "cp1251"):
        bts = self.asBytes()
        try:
            s = str(bts, encoding)
        except UnicodeDecodeError:
            s = "<Не удалось декодировать содержимое блока данных>"
        return s

    # Метод asBitArray() представляет значение блока данных в виде двоичного массива
    def asBitArray(self):
        if self.__bitSize == 0:
            return []
        
        res = []
        val = self.__value
        for i in range(0, self.__bitSize):
            res.append(val % 2)
            val >>= 1
        return res
    
    # Метод getBitSize() возвращает установленный размер блока в битах
    def getBitSize(self):
        return self.__bitSize
    
    # Метод wt возвращает вес Хемминга для блока данных
    def wt(self):
        v = self.__value
        res = 0
    
        while v != 0:
            res += v % 2
            v >>= 1
    
        return res
    
    # Метод fromDatablock() инициализирует значение блока данных на основе блока данных other
    # Возвращает ссылку на самого себя
    def fromDatablock(self, other):
        self.__value = other.asInt()
        self.__bitSize = other.getBitSize()
        return self
    
    # Метод fromBytes() инициализирует значение блока данных на основе последовательности двоичных данных bts
    # Возвращает ссылку на самого себя
    def fromBytes(self, bts):
        res = 0
        for i in range(len(bts), 0, -1):
            res += bts[i - 1]
            if i != 1:
                res <<= 8
        self.__value = res
        self.__bitSize = ceil(log2(res + 1))
        return self

    
    # Метод fromInt() инициализирует значение блока данных на основе целого числа val
    # Возвращает ссылку на самого себя
    def fromInt(self, val):
        if val < 0:
            raise Exception("Отрицательные числа в блок данных не переводятся")
        self.__value = val
        self.__bitSize = ceil(log2(val + 1))
        return self
    
    # Метод fromText() инициализирует значение блока данных на основе строки s, используя кодировку encoding
    # Возвращает ссылку на самого себя
    def fromText(self, s, encoding = "cp1251"):
        bts = bytes(s, encoding)
        return self.fromBytes(bts)
    
    # Метод fromBitArray() инициализирует значение блока данных на основе строки двоичного массива
    # Возвращает ссылку на самого себя
    def fromBitArray(self, arr):
        self.__value = 0
        for i in range(0, len(arr)):
            self.__value += arr[i] * 2 ** i
        self.__bitSize = len(arr)
        return self
    
    # Метод clone() возвращает точную копию блока данных self ("клонирует" текущий объект)
    def clone(self):
        dblock = Datablock().fromDatablock(self)
        return dblock
    
    # Вспомогательный метод __subb() возвращает подблок на основе битовой подпоследовательности,
    # начиная с бита wherefrom и заканчивая битом wherefrom + howmany - 1 блока данных self
    def __subb(self, wherefrom, howmany):
        if wherefrom + howmany > self.__bitSize:
            raise Exception("Размер извлекаемой подпоследовательности битов слишком велик")
        if howmany <= 0:
            raise Exception("Размер битовой подпоследовательности должен быть положительным")
        if wherefrom < 0:
            raise Exception("Индекс должен быть неортицательной величиной")
        
        val = self.__value
        val >>= wherefrom
        val %= 2 ** howmany
        dblock = Datablock().fromInt(val)
        dblock.setBitSize(howmany)
        return dblock
    
    # Метод setBitSize() устанавливает размер блока данных в битах
    # Параметры:
        # howmany - устанавливаемый размер;
        # cutIfNotZeros - принудительное "урезание" блока, если его размер уменьшается, а "отбрасываемые" старшие разряды (хотя бы некоторые) не нулевые
        #     если True, то уменьшение размер меняется в любом случае, даже в сторону уменьшения, с возможной потерей ненулевых битов
    def setBitSize(self, howmany, cutIfNotZeros = False):
        if howmany > 0:
            if self.__value > 2 ** howmany and cutIfNotZeros:
                self.__value %= 2 ** howmany
            self.__bitSize = howmany
        return self

    # Перегружаемый метод __str__ отвечает за строковое представление блока данных, в том числе при его выводе с помощью функции print()
    # Способ представления зависит от установленного режима отображения (retMode)
    def __str__(self):
        global retMode
        if retMode == RM_BYTES:
            return str(self.asBytes())
        if retMode == RM_INT:
            return str(self.__value)
        if retMode == RM_TEXT:
            return self.asText()
        return "В строковом виде: " + self.asText() + "; в числовом виде: " + str(hex(self.__value)) + "; размер в битах: " + str(self.getBitSize())

    def __len__(self):
        res = self.__bitSize // elemSize
        if self.__bitSize % elemSize > 0:
            res += 1
        return res

    # Перегрузка операции индексирования
    # Общая идея: по индексу можно обратиться к элементу двоичной последовательности размером elemSize битов
    # При этом элемент представляется в виде, задаваемом режимом отображения
    def __getitem__(self, key):
        firstBitIndex = key * elemSize
        if firstBitIndex > self.__bitSize:
            raise Exception("Индекс вне границ блока данных")
        lastBitIndex = firstBitIndex + elemSize
        if lastBitIndex > self.__bitSize:
            lastBitIndex = self.__bitSize
        dblock = self.__subb(firstBitIndex, lastBitIndex - firstBitIndex)
        if retMode == RM_BYTES:
            return dblock.asBytes()
        elif retMode == RM_DATABLOCK:
            return dblock
        elif retMode == RM_INT:
            return dblock.asInt()
        elif retMode == RM_TEXT:
            return dblock.asText()
        else:
            raise Exception("Странный режим отображения элементов тут у вас")
            
    
    def __setitem__(self, key, value):
        if key >= len(self):
            raise Exception("Индекс превышает длину блока данных")
        if str(type(value)) == "<class 'datablocks.Datablock'>" or str(type(value)) == "<class 'Datablock'>":
            val = value.asInt()
        elif str(type(value)) == "<class 'bytes'>":
            val = Datablock().fromBytes(value).asInt()
        elif str(type(value)) == "<class 'str'>":
            val = Datablock().fromText(value).asInt()
        elif str(type(value)) == "<class 'int'>":
            val = value
        else:
            raise Exception("Недопустимое присваивание: попытка присвоить значение типа " + str(type(value)) + " подблоку данных")
        
        if val < 0:
            raise Exception("Отрицательные значения не допускаются")
        if val >= 2 ** elemSize:
            raise Exception("Размер указанного значения превышает установленный размер элемента")
        
        firstBitIndex = key * elemSize
        lastBitIndex = (key + 1) * elemSize
        
        if lastBitIndex > self.__bitSize:
            self.setBitSize(lastBitIndex)
        
        bsz = self.getBitSize()
        
        res = self.__value >> lastBitIndex
        res <<= lastBitIndex
        res += val << firstBitIndex
        res += self.__value % 2 ** firstBitIndex
        
        self.fromInt(res).setBitSize(bsz)

    # Метод random() устанавливает случайное значение блока данных, имеющие размер size битов
    def random(self, size):
        self.fromInt(randint(2, 2 ** size))
        self.setBitSize(size)
        return self

    # не работает!
    def probablePrime(self, size):
        while True:
            self.random(size)
            
            if self.__value % 2 == 0:
                self.__value += 1
                self.__value %= 2 ** size
            
            isPrime = True
            
            for i in range(0, 64):
                a = randint(2, self.__value)
                qwe = pow(a, self.__value - 1, self.__value)
                if qwe != 1:
                    isPrime = False
                    print("is not prime; ", pow(a, self.__value - 1, self.__value))
                    break
            
            if isPrime:
                break
            
        return self

    def generatePrime(self, bitlen: int):
        """
        - Генерирует простое число (проверка на простоту происходит с помощью алгоритма Миллера-Рабина)
        - Вероятность того, что число окажется составным оценивается как величина, не превышающая 4**(-k),\\
        где k - количество раундов проверки: k = log2(2**bitlen) = bitlen
        - Возвращает значение типа int
        """
        
        def isPrime(n, k):
            """
            Проверка на простоту случайного числа алгоритмом Миллера-Рабина
            n - случайное число, k - количество раундов
            """
            def isStrongPseudoprime(n, a):
                d, s = n - 1, 0
                while d % 2 == 0:
                    d, s = d//2, s+1
                t = pow(a, d, n)
                if t == 1:
                    return True
                while s > 0:
                    if t == n - 1:
                        return True
                    t, s = pow(t, 2, n), s - 1
                return False

            if n % 2 == 0:
                return n == 2
            for i in range(1, k):
                a = randrange(2, n)
                if not isStrongPseudoprime(n, a):
                    return False
            return True

        while True:
            genrand = randrange(0, int(2**bitlen))

            k = int(log2(genrand))
            if isPrime(genrand, k) == True:
                break
        return genrand


    # Два метода, позволяющие сравнить блок данных с нулём
    def isZero(self):
        return self.__value == 0
    
    def isNotZero(self):
        return self.__value != 0

    def __otherToInt(self, other):
        typeother = str(type(other))
        if typeother == "<class '__main__.Datablock'>" or typeother == "<class 'datablocks.Datablock'>":
            return other.asInt()
        if typeother == "<class 'int'>":
            return other
        else:
            raise Exception("Недопустимый тип второго оператора ", typeother)
            
    # Оператор +
    # Все арифметические операторы, поразрядные логические операторы и операторы отношения
    # принимают в качестве второго операнда как блок данных, так и целое число
    def __add__(self, other):
        return Datablock().fromInt(self.asInt() + self.__otherToInt(other))

    # Оператор +=
    def __iadd__(self, other):
        return self.fromInt(self.asInt() + self.__otherToInt(other))
    
    # Оператор -
    def __sub__(self, other):
        return Datablock().fromInt(self.asInt() - self.__otherToInt(other))

    # Оператор -=
    def __isub__(self, other):
        return self.fromInt(self.asInt() - self.__otherToInt(other))

    # Оператор *
    def __mul__(self, other):
        return Datablock().fromInt(self.asInt() * self.__otherToInt(other))
    
    # Оператор *=
    def __imul__(self, other):
        return self.fromInt(self.asInt() * self.__otherToInt(other))
    
    # Оператор //
    def __floordiv__(self, other):
        return Datablock().fromInt(self.asInt() // self.__otherToInt(other))

    # Оператор //=
    def __ifloordiv__(self, other):
        return self.fromInt(self.asInt() // self.__otherToInt(other))
    
    # Оператор %
    def __mod__(self, other):
        return Datablock().fromInt(self.asInt() % self.__otherToInt(other))

    # Оператор %=
    def __imod__(self, other):
        return self.fromInt(self.asInt() % self.__otherToInt(other))
    
    # Оператор **
    def __pow__(self, other):
        return Datablock().fromInt(self.asInt() ** self.__otherToInt(other))
    
    # Оператор **=
    def __ipow__(self, other):
        return self.fromInt(self.asInt() ** self.__otherToInt(other))
    
    # Метод modPow() выполняет возведение блока данных в степень other по модулю modulo
    def modPow(self, other, modulo):
        return Datablock().fromInt(pow(self.asInt(), self.__otherToInt(other), self.__otherToInt(modulo)))
        
    # Метод setToModPow() аналогичен предыдущему, при этом результат сохраняется в текущем блоке
    def setToModPow(self, other, modulo):
        return self.fromInt(pow(self.asInt(), self.__otherToInt(other), self.__otherToInt(modulo)))
    
    # Оператор <<
    def __lshift__(self, other):
        return Datablock().fromInt(self.asInt() << self.__otherToInt(other))

    # Оператор <<=
    def __ilshift__(self, other):
        return self.fromInt(self.asInt() << self.__otherToInt(other))
    
    # Оператор >>
    def __rshift__(self, other):
        return Datablock().fromInt(self.asInt() >> self.__otherToInt(other))
    
    # Оператор >>=
    def __irshift__(self, other):
        return self.fromInt(self.asInt() >> self.__otherToInt(other))

    # Оператор &
    def __and__(self, other):
        return Datablock().fromInt(self.asInt() & self.__otherToInt(other))

    # Оператор &=
    def __iand__(self, other):
        return self.fromInt(self.asInt() & self.__otherToInt(other))
    
    # Оператор ^
    def __xor__(self, other):
        return Datablock().fromInt(self.asInt() ^ self.__otherToInt(other))

    # Оператор ^=
    def __ixor__(self, other):
        return self.fromInt(self.asInt() ^ self.__otherToInt(other))

    # Оператор |
    def __or__(self, other):
        return Datablock().fromInt(self.asInt() | self.__otherToInt(other))

    # Оператор |=
    def __ior__(self, other):
        return self.fromInt(self.asInt() | self.__otherToInt(other))

    # Оператор ~
    def __invert__(self):
        ones = 2 ** self.__bitSize - 1
        return Datablock().fromInt(self.__value ^ ones)

    # Оператор ==
    def __eq__(self, other):
        return self.__value == self.__otherToInt(other)
    
    # Оператор !=
    def __ne__(self, other):
        return self.__value != self.__otherToInt(other)
    
    # Оператор <
    def __lt__(self, other):
        return self.__value < self.__otherToInt(other)
    
    # Оператор >
    def __gt__(self, other):
        return self.__value > self.__otherToInt(other)
    
    # Оператор <=
    def __le__(self, other):
        return self.__value <= self.__otherToInt(other)
    
    # Оператор >=
    def __ge__(self, other):
        return self.__value >= self.__otherToInt(other)
    
    # Метод bitConcat() присоединяет к текущему блоку блок other. Оба блока представляются как битовые последовательности.
    # При этом от каждого блока берётся ровно __bitSIze битов.
    # Результат этого метода не всегда совпадает с результатом метода concat()!
    # Результат конкатенации сохраняется в текущем 
    def bitConcat(self, other):
        slf = self.__value
        oth = other.asInt()
        cnc = (oth << self.__bitSize) + slf
        return Datablock().fromInt(cnc).setBitSize(other.getBitSize() + self.__bitSize)
    
    # Метод cshl() возвращает результат циклического сдвига текущего блока влево на other позиций
    def cshl(self, other):
        howmany = self.__otherToInt(other) % self.__bitSize
        if howmany == 0:
            return self.clone()
        
        last = self.__subb(0, self.__bitSize - howmany)
        most = self.__subb(self.__bitSize - howmany, howmany)

        return most.bitConcat(last)
    
    # Метод cshr() возвращает результат циклического сдвига текущего блока вправо на other позиций
    def cshr(self, other):
        howmany = self.__otherToInt(other) % self.__bitSize
        if howmany == 0:
            return self.clone()
        
        last = self.__subb(0, howmany)
        most = self.__subb(howmany, self.__bitSize - howmany)
        
        return most.bitConcat(last)
    
    def setToCshl(self, other):
        self.fromDatablock(self.cshl(other))
        return self
    
    def setToCshr(self, other):
        self.fromDatablock(self.cshr(other))
        return self
    
    # Метод extEuc реализует расширенный алгоритм Евклида
    # Используется в методе modInverse() - см. далее.
    def extEuc(self, other):
        a0 = self.asInt()
        a1 = self.__otherToInt(other)
        if a0 == 0 or a1 == 0:
            return None
        x0 = 1
        x1 = 0
        y0 = 0
        y1 = 1
        
        while a1 != 0:
            q = a0 // a1
            (a0, a1) = (a1, a0 - a1 * q)
            (x0, x1) = (x1, x0 - x1 * q)
            (y0, y1) = (y1, y0 - y1 * q)
        out = []
        out.append(a0)
        out.append(x0)
        out.append(y0)
        return out
    
    # Метод modInverse() возвращает число (в виде блока данных), обратное self по модулю other
    def modInverse(self, other):
        dxy = self.extEuc(other)
        if dxy[0] == 1:
            if dxy[1] > 0:
                return Datablock().fromInt(dxy[1])
            return Datablock().fromInt(self.__otherToInt(other) - abs(dxy[1]))
        return None
    
    # Метод gcd() возвращает наибольший общий делитель self и other
    def gcd(self, other):
        slf = self.__value
        oth = self.__otherToInt(other)
        
        if slf == oth:
            return self.clone()
        
        if slf > oth:
            a, b = slf, oth
        else:
            a, b = oth, slf
        
        while True:
            r = a % b
            q = a // b
            
            if r == 0:
                break
            
            a = b
            b = r
        
        return dbi(b)
    
    # Метод subblock() возвращает подблок текущего блока.
    # Параметры:
         # wherefrom - первый элемент блока (бит, байт, слово и т. п. - размер определяется на основе elemSize);
         # howmany - количество элементов в подблоке.
         # Если howmany = 0 или wherefrom превышает количество элементов в текущем блоке, возвращается пустой (нулевой) блок данных.
         # Если howmany < -1 (значение по умолчанию), то в подблок включаются элементы, начиная с позиции wherefrom и заканчивая последним элементом текущего блока
    def subblock(self, wherefrom, howmany = -1):
        if wherefrom >= len(self):
            return Datablock()
        if howmany == 0:
            return Datablock()
        if howmany < 0:
            howmany = len(self) - wherefrom
        
        firstBitIndex = wherefrom * elemSize
        lastBitIndex = (wherefrom + howmany) * elemSize
        
        if lastBitIndex > self.__bitSize:
            lastBitIndex = self.__bitSize
            
        dblock = self.__subb(firstBitIndex, lastBitIndex - firstBitIndex)
        dblock.setBitSize(howmany * elemSize)
        
        return dblock
    
    # Метод concat() объединяет блоки self и other.
    # В отличие от битовой конкатенации, здесь объединяются две последовательности элементов размера elemSize.
    
    #     Пусть имеются два блока: 01011 и 101101. Размеры в битах 5 и 6 соответственно, при этом elemSize = 4.
    #     Предположим, второй блок присоединяется к первому.
    #     Метод bitConcat() просто сливает две битовые последовательности (первая справа, вторая слева): 10110101011
    #     Метод concat() представляет первый блок как: 0000 1011. Второй блок: 0010 1101.
    #     При объединении получается 0010 1101 0000 1011.
    def concat(self, other):
        self.setBitSize(len(self) * elemSize)
        other.setBitSize(len(other) * elemSize)
        self.fromDatablock(self.bitConcat(other))
        return self
    
    # Метод replace() выполняет замену подблока текущего блока, расположенного в позиции wherefrom, на подблок subblock
    def replace(self, wherefrom, subblock):
        if wherefrom + len(subblock) > len(self):
            raise Exception("Размер предлагаемого подблока слишком велик: " + str(wherefrom + len(subblock)) + " " + str(self.len()))
            
        last = self.subblock(0, wherefrom)
        most = self.subblock(wherefrom + len(subblock))
        self.fromDatablock(last.concat(subblock).concat(most))
        return self
        
    # Метод subblockIndex() возвращает индекс первого вхождения подблока в блок
    def subblockIndex(self, other):
        selflen = len(self)
        otherlen = len(other)
        
        if selflen < otherlen:
            raise Exception("Искомый подблок имеет слишком большой размер")
        m = 2 ** (elemSize * otherlen)
        slf = self.asInt()
        oth = other.asInt()

        for i in range(0, selflen - otherlen + 1):
            if (slf >> i * elemSize) % m == oth:
                return i
            
        return None
    
    # Метод index() возвращает индекс первого вхождения элемента elem в текущий блок данных
    def index(self, elem):
        for i in range(0, len(self)):
            if self[i] == elem:
                return i
        return None
    
    # Метод insert() осуществляет вставку подблока other в текущий блок по позиции index
    def insert(self, other, index):
        last = self.subblock(0, index)
        most = self.subblock(index)
        self.fromDatablock(last.concat(other).concat(most))
        return self
    
    # Метод substMonoShiftedAbc() выполняет простое подстановочное преобразование блока данных
    # key - ключ подстановки;
    # direction - прямая (True) или обратная (False) подстановка
    def substMonoShiftedAbc(self, key, direction):
        global retMode
        m = 2 ** elemSize
        
        if key >= m:
            raise Exception("Ключ при текущем размере элемента не должен превышать " + str(m - 1))
        
        curRetMode = retMode
        retMode = RM_INT
        for i in range(0, len(self)):
            if direction:
                self[i] = (self[i] + key) % m
            else:
                self[i] = (self[i] + m - key) % m
                
        retMode = curRetMode
        return self

    # Метод substMonoMixedAbc() выполняет простое подстановочное преобразование блока данных с использованием одного перемешанного алфавита
    # abc - алфавит замены;
    # direction - прямая (True) или обратная (False) подстановка
    def substMonoMixedAbc(self, abc, direction):
        global retMode
        
        curRetMode = retMode
        retMode = RM_INT
        
        for i in range(0, len(self)):
            if direction:
                self[i] = abc[self[i]]
            else:
                self[i] = abc.index(self[i])
        
        retMode = curRetMode
        
        return self
    
    # Метод substPolyShiftedAbc() выполняет полиалфавитное подстановочное преобразование блока данных с использованием нескольких смещённых алфавитов
    # key - ключ подстановки;
    # direction - прямая (True) или обратная (False) подстановка
    def substPolyShiftedAbc(self, key, direction):
        global retMode
        
        keylen = len(key)
        if keylen == 0:
            raise Exception("Ключ подстановки пуст")
        m = 2 ** elemSize
        
        curRetMode = retMode
        retMode = RM_INT
        
        for i in range(0, len(self)):
            if direction:
                self[i] = (self[i] + key[i % keylen]) % m
            else:
                self[i] = (self[i] + m - key[i % keylen]) % m
        
        retMode = curRetMode
        
        return self
    
    # Метод substPolyMixedAbc() выполняет полиалфавитное подстановочное преобразование блока данных с использованием нескольких перемешанных алфавитов
    # abcs - перемешанные алфавиты;
    # direction - прямая (True) или обратная (False) подстановка
    def substPolyMixedAbc(self, abcs, direction):
        global retMode
        
        keylen = len(abcs)
        if keylen == 0:
            raise Exception("Ключ подстановки пуст")
            
        curRetMode = retMode
        retMode = RM_INT
        
        for i in range(0, len(self)):
            if direction:
                self[i] = abcs[i % keylen][self[i]]
            else:
                self[i] = abcs[i % keylen].index(self[i])
        
        retMode = curRetMode
        
        return self        
    
    # Метод transposSimple() выполняет простую перестановку элементов блока данных.
    # key - ключ подстановки;
    # direction - прямая (True) или обратная (False) перестановка
    def transposSimple(self, key, direction):
        global retMode
        
        keylen = len(key)

        if len(self) % keylen != 0:
            raise Exception("Размер блока не кратен размеру ключа")

        curRetMode = retMode
        retMode = RM_INT
        
        tmp = self.clone()
        
        for i in range(0, len(self), keylen):
            for j in range(0, keylen):
                if direction:
                    self[i + j] = tmp[i + key.index(j)]
                else:
                    self[i + key.index(j)] = tmp[i + j]
                   
        retMode = curRetMode
        
        return self

    # Метод transposTbl() выполняет  перестановку элементов блока данных с усложнением по таблице.
    # key - ключ подстановки;
    # direction - прямая (True) или обратная (False) перестановка
    def transposTbl(self, key1, key2, direction):
        global retMode
        
        l = len(self)
        l1 = len(key1)

        if l % l1 != 0:
            raise Exception("Блок данных не может быть равномерно разбит на " + str(l1) + " подблоков " + str(l))        
        
        l2 = len(key2)
        sbSize = l // l1
            
        if l2 != sbSize:
            raise Exception("Размер второго ключа не равен размеру подблока")
        
        curRetMode = retMode
        retMode = RM_INT
        
        tbl = []
          
        if direction:
            for i in range(0, l1):
                tbl.append(self.subblock(key1.index(i) * sbSize, sbSize))
                
            j = 0
            
            for i in range(0, l2):
                for db in tbl:
                    self[j] = db[key2.index(i)]
                    j += 1
        else:
            for i in range(0, l1):
                tbl.append(Datablock().fromInt(2 ** (elemSize * l2) - 1))
            
            for j in range(0, l):
                tbl[j % l1][key2.index(j // l1)] = self[j]
                
            for i in range(0, l1):
                self.replace(key1.index(i) * sbSize, tbl[i])
        
        retMode = curRetMode
        
        return self

    # Метод transposSimple() выполняет  перестановку элементов блока данных с усложнением по маршруту.
    # key - ключ подстановки;
    # direction - прямая (True) или обратная (False) перестановка
    def transposRoute(self, key, direction):
        global retMode
        
        curRetMode = retMode
        retMode = RM_INT
        
        keylen = len(key)
        dblen = len(self)
        db = self.clone()
        if(direction):
            db.transposSimple(key, True)
            k = 0
            for i in range(0, keylen):
                for j in range(0, dblen, keylen):
                    self[k] = db[j + i]
                    k += 1
        else:
            k = 0
            for i in range(0, keylen):
                for j in range(0, dblen, keylen):
                    self[i + j] = db[k]
                    k += 1
            self.transposSimple(key, False)
        
        retMode = curRetMode
        
        return self
    
    # Метод getProbabilityTable() возвращает таблицу частот элементов текущего блока
    def getProbabilityTable(self):
        global retMode
        curRetMode = retMode
        
        t = {}
        
        retMode = RM_INT
        
        for i in range(0, len(self)):
            if self[i] in t:
                t[self[i]] += 1 / len(self)
            else:
                t[self[i]] = 1 / len(self)
        
        retMode = curRetMode
        
        return t

# Следующие функции созданы для удобства,
# Чтобы при создании блоков данных не писать каждый раз Datablock().fromInt(...), Datablock().fromText(...) и т. п.
# Для создания блока с одновременным присванием ему значения достаточно написать dbi(5), dbt("Секретное сообщение") и т. п.
def dbi(value):
    dblock = Datablock().fromInt(value)
    return dblock

def dbt(txt):
    dblock = Datablock().fromText(txt)
    return dblock

def dbb(block):
    dblock = Datablock().fromDatablock(block)
    return dblock

def dbbs(bts):
    dblock = Datablock().fromBytes(bts)
    return dblock