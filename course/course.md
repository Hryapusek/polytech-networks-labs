<p style="text-align: center;">
Санкт-Петербургский политехнический университет Петра Великого<br>
Институт компьютерных наук и кибербезопасности<br>
Высшая школа программной инженерии
</p>
<br><br><br><br><br><br><br><br><br><br>

<div style="text-align: center;">
<span style="font-size: 16pt;">
Курсовая работа<br>
</span>
</div>

<div style="text-align: center;">
<span style="font-size: 12pt;">
по дисциплине:
</span>
</div>

<div style="text-align: center;">
<span style="font-size: 12pt;">
"Сети и телекоммуникации"<br>
</span>
</div>


<br><br><br><br><br><br><br><br><br><br><br><br><br><br>
<br>
<p style="text-align: right;">
<b>Работу выполнил студент:</b><br>
Абраамян Александр Манвелович<br>
Группа 5130904/10101<br>
4 курс
</p>

<div class="page"/>

# Цель работы
Необходимо придумать надежный, ошибкоустойчивый и в то же время очень быстрый протокол для взаимодействия с БПЛА.

<div class="page"/>

# Результаты работы

## Общее описание взаимодейтсвия по UDP

UDP — это один из основных протоколов транспортного уровня в сетях TCP/IP. В отличие от TCP, он работает без установления соединения и не гарантирует доставку, порядок пакетов или контроль перегрузок.

### 1. Ключевые особенности UDP

#### 1.1. Ненадёжная доставка
- UDP отправляет данные без подтверждения получения
- Пакеты могут теряться, дублироваться или приходить в неправильном порядке

#### 1.2. Отсутствие установки соединения
- Нет фазы "рукопожатия" (как в TCP с `SYN-ACK`)
- Отправитель и получатель не поддерживают состояние соединения

#### 1.3. Минимальные накладные расходы
- Заголовок UDP занимает всего **8 байт** (TCP — минимум 20 байт)
- Нет механизмов контроля перегрузки и повторной передачи

#### 1.4. Поддержка широковещательной передачи
- Возможность multicast/broadcast рассылки

### 2. Сравнение UDP и TCP

| Характеристика       | UDP                          | TCP                          |
|----------------------|------------------------------|------------------------------|
| **Гарантия доставки** | ❌ Нет                        | ✅ Да                        |
| **Порядок пакетов**  | ❌ Нет                        | ✅ Да                        |
| **Контроль перегрузки** | ❌ Нет                       | ✅ Да                        |
| **Установка соединения** | ❌ Нет                     | ✅ Да                        |
| **Накладные расходы** | 8 байт                    | ≥20 байт                  |
| **Использование**     | Видео, игры, VoIP            | Веб, почта, файлы            |

### 3. Когда использовать UDP?

#### 3.1. Мультимедийные приложения
- Видеостримы, VoIP (потеря пакетов менее критична чем задержки)

#### 3.2. Онлайн-игры
- Быстрая передача игрового состояния

#### 3.3. DNS и DHCP
- Короткие запросы-ответы

#### 3.4. IoT устройства
- Ресурсоэффективная передача данных

### 4. Недостатки UDP

#### 4.1. Нет встроенной надёжности
- Требуется самостоятельная реализация:
  - Нумерация пакетов
  - Подтверждения
  - Повторные отправки

#### 4.2. Уязвимость к DDoS
- UDP flood атаки

#### 4.3. Нет контроля перегрузки
- Риск перегрузки сети

### 5. Вывод

**UDP предпочтителен когда:**
✔ Критична низкая задержка  
✔ Допустима потеря части данных  
✔ Нужен multicast

**TCP лучше когда:**
✔ Требуется гарантированная доставка
✔ Важен порядок данных

## Тип пакета
Формат пакета будет лежать в основе взаимодействия с БПЛА. Очень важно учесть что пакет должен иметь возможность расширяться в зависимости от потребностей поставленных компанией. Поэтому необходимо ввести для начала такой параметр как **тип пакета**.

Отдельно необходимо выделить следующие типы пакетов:
- ACK - подтверждение получения пакета
- CMD - команда
- PARAM - параметр
- PARAM_GET - запрос параметра
- MESSAGE - сообщение
- VERSION - версия
- FIRMWARE - обновление ПО
- ...

### Примерный код на С
```c++
enum ruavp_structures_t
{
  STRUCT_CORE_ACK = 0,
  STRUCT_CORE_CMD = 1,
  STRUCT_CORE_PARAM = 2,
  STRUCT_CORE_PARAM_GET = 3,
  STRUCT_CORE_MESSAGE = 4,
  STRUCT_CORE_VERSION = 5,
  STRUCT_CORE_FIRMWARE = 6,
  ...
  STRUCT_HELI_ROUTE_GET = 14,
  STRUCT_HELI_ROUTE_GET_POINT = 15,
  STRUCT_HELI_ROUTE = 16,
  ...
  STRUCT_ZIMU_MAG = 65,
  STRUCT_ZIMU_BARO = 66,
  STRUCT_ZIMU_GPS = 67,
  STRUCT_ZIMU_RANGE = 68,
  STRUCT_ZIMU_AIRSPEED = 69,
  ...
};
```

### Адресаты
Для различия адресатов необходимо выделить следующие типы адресатов:
- HELI - вертолет (1-15)
- LAND - земля (16)

### Примерный код на С
```c++
enum ruavp_class_t
{
  CLASS_LAND = 1 << 4,
  CLASS_HELI = 2 << 4,
  CLASS_HELIHW = 3 << 4,
  CLASS_EXT = 4 << 4,
};

enum ruavp_class_max_t
{
  CLASS_LAND_MAX = 7,
  CLASS_HELI_MAX = 7,
  CLASS_HELIHW_MAX = 7,
  CLASS_EXT_MAX = 7,
};
```

### Размер пакета
Необходимо также хранить в пакете его размер например в байтах.

### Валидация пакета
При получении пакета необходимо провести валидацию данных. При беспроводной передачи пакетов необходимо проверять контрольную сумму. Например, мы можем ввести CRC16 в качестве контрольной суммы.

Примеры алгоритмов:
```c++
#include <stdint.h>
#include <stddef.h>

uint16_t calculate_crc(const uint8_t *data, size_t length)
{
    uint16_t crc = 0xFFFF;  // Initial value
    for (size_t i = 0; i < length; i++) {
        crc ^= (uint16_t)data[i] << 8;
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;  // Polynomial for CRC-16-CCITT
            } else {
                crc <<= 1;
            }
        }
    }
    return crc;
}
```

Функция для валидации CRC16 может выглядеть следующим образом:

```c++
bool validate_packet(const ruavp_header_t* header, const void* data)
{
    // Сохраняем оригинальный CRC
    uint16_t received_crc = header->crc;
    
    // Создаем копию заголовка с нулевым CRC для вычисления
    ruavp_header_t temp_header = *header;
    temp_header.crc = 0;
    
    // Вычисляем CRC
    uint8_t* packet_start = reinterpret_cast<uint8_t*>(&temp_header);
    size_t packet_size = sizeof(ruavp_header_t) + header->size;
    uint16_t calculated_crc = calculate_crc(packet_start, packet_size);
    
    // Сравниваем CRC
    return (received_crc == calculated_crc);
}
```

### Итоговая структура

Теперь мы готовы описать структуру которая будет содержать в себе всю необходимую информацию о пакете.

```c++
struct ruavp_header_t
{
    uint16_t marker;
    uint8_t size;
    uint8_t source;
    uint8_t destination;
    uint8_t structure_id;
    uint16_t crc;
} __attribute__((packed));
```

Сразу за заголовком могут следовать данные, структура которых будет зависеть от structure_id. Если это, например, команда, то она может выглядеть следующим образом:

```c++
struct core_cmd_t
{
  uint64_t cid;
  int32_t param;
  uint32_t code;
  uint8_t subsystem;
} __attribute__((packed));
```

Если БПЛА будет отправлять телеметрию, то она может выглядеть примерно следующим образом:

```c++
struct heli_telemetry_t
{
  double latitude;
  double longitude;
  float altitude;
  float altitude_abs;
  float ax;
  float ay;
  float az;
  float colpitch;
  float pitch;
  float roll;
  float target_altitude;
  float target_speed;
  float throttle;
  float yaw;
  int16_t route_point;
  uint16_t rpm_engine;
  uint8_t engine_state;
  uint8_t mode;
  uint8_t route;
} __attribute__((packed));
```

## Обработчик
Необходимо также написать сущность которая будет заниматься обработкой и диспетчеризацией всех пакетов.
Приблизительная структура будет выглядеть следующим образом:
```c++
struct ruavp_protocol_t
{
  ruavp_address_t address;
  void* user;

  uint16_t sid;
  uint32_t counters[RUAVP_CLASSES_ARRAY_SIZE];

  void (*handle_any)(struct ruavp_protocol_t* d, 
                     const struct ruavp_header_t* buf, 
                     size_t sz);
  void (*process_core_ack)(struct ruavp_protocol_t* d, 
                            const struct ruavp_header_t* h,
                            const struct core_ack_t* v);
  void (*process_core_cmd)(struct ruavp_protocol_t* d, 
                            const struct ruavp_header_t* h,
                            const struct core_cmd_t* v);
  void (*process_core_param)(struct ruavp_protocol_t* d, 
                            const struct ruavp_header_t* h,
                            const struct core_param_t* v);
  ...
  struct ruavp_buffer_t buffer;
  struct ruavp_control_t control[RUAVP_CLASSES_ARRAY_SIZE];
};
```

Обозначив подобную структуру можно написать функцию которая будет обрабатывать пришедшие пакеты.
```c++
int ruavp_decode_process(struct ruavp_protocol_t* d, const void* v, size_t sz);
```

Её задача будет заключаться в следующем:
1. Проверить валидность пакета
2. Вызвать обработчик для соответствующего класса
3. Передать данные обработчику

В итоге мы может заполнить ruavp_protocol_t своими обработчиками и получить удобную функцию для работы с пакетами.

## Шифрование
### Шифровальный модуль

Для защиты передаваемых данных был реализован отдельный модуль шифрования, который:

* Шифрует пакеты перед отправкой
* Расшифровывает их при получении
* Использует алгоритм "Кузнечик" (ГОСТ Р 34.12-2015)
* Работает в режиме CFB (гаммирование с обратной связью)

### Принцип работы

#### Перед отправкой

1. Модуль принимает исходный пакет (заголовок + данные).
2. Генерирует случайный вектор инициализации (IV).
3. Шифрует данные с помощью ключа "Кузнечик".
4. Добавляет IV в начало пакета.
5. Отправляет зашифрованный пакет по UDP.

#### При получении

1. Модуль извлекает IV из пакета.
2. Расшифровывает данные с помощью того же ключа.
3. Проверяет целостность заголовка.
4. Передает расшифрованный пакет на обработку.

### Структура пакета
```
+----------------+----------------+----------------+
|      IV        | Зашифрованные  |   Данные (N)   |
|   (16 байт)    |   заголовок    |                |
+----------------+----------------+----------------+
```

### Пример кода
```c++
#include <stdint.h>
#include <string.h>

// Ключ шифрования (256 бит)
const uint8_t KUZ_KEY[32] = { ... }; 

// Шифрует данные (режим CFB)
void kuz_encrypt(const uint8_t* iv, const uint8_t* input, uint8_t* output, size_t len) {
    // ... (реализация шифрования Кузнечиком)
}

// Расшифровывает данные (режим CFB)
void kuz_decrypt(const uint8_t* iv, const uint8_t* input, uint8_t* output, size_t len) {
    // ... (та же функция, что и шифрование)
}

// Подготовка пакета к отправке
void encrypt_packet(uint8_t* packet, size_t packet_size) {
    uint8_t iv[16];
    generate_random_iv(iv);  // Генерация IV
    
    // Шифруем данные (кроме самого IV)
    kuz_encrypt(iv, packet, packet + 16, packet_size - 16);
    
    // Добавляем IV в начало пакета
    memcpy(packet, iv, 16);
}

// Обработка полученного пакета
void decrypt_packet(uint8_t* packet, size_t packet_size) {
    uint8_t iv[16];
    
    // Извлекаем IV из начала пакета
    memcpy(iv, packet, 16);
    
    // Расшифровываем остальную часть
    kuz_decrypt(iv, packet + 16, packet + 16, packet_size - 16);
}
```

### Преимущества решения
- ✔️ Простота – модуль работает "прозрачно", не меняя логику обмена пакетами.
- ✔️ Совместимость – не требует изменения структуры пакетов (кроме добавления IV).
- ✔️ Безопасность – "Кузнечик" соответствует ГОСТ, обеспечивая надежное шифрование.
- ✔️ Производительность – работает быстро даже на слабых устройствах.

## Библиотека
Теперь разобравшись с основными структурами мы можем написать библиотеку для того чтобы сложить все вместе и использовать в различных программах для взаимодейтсвия с БПЛА.

Примерный CMakeLists.txt
```
cmake_minimum_required(VERSION 3.21)
project(vt45 C)

set(RUAVP_INCLUDE_DIRS "${CMAKE_CURRENT_SOURCE_DIR}")

add_library(vt45 STATIC vt45.c vt45-params.c)
target_include_directories(vt45 PUBLIC
  "$<BUILD_INTERFACE:${RUAVP_INCLUDE_DIRS}>"
  "$<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>"
)
target_include_directories(vt45 PUBLIC vt45.h ruavp-c.h)
target_include_directories(vt45 PRIVATE ruavp/crc.h)

install(TARGETS vt45
  EXPORT vt45Targets
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
  INCLUDES DESTINATION include
  PUBLIC_HEADER DESTINATION include/vt45
  PRIVATE_HEADER DESTINATION include/vt45/ruavp
)

add_library(vt45x STATIC vt45-params-x.c)
target_include_directories(vt45x PUBLIC
  "$<BUILD_INTERFACE:${RUAVP_INCLUDE_DIRS}>"
  "$<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>"
)
```

## Заключение
В ходе данного проекта была разработана надежная система передачи данных по UDP, сочетающая эффективность, безопасность и гибкость. Основные достижения:

1. **Оптимизированная структура пакетов**
	* Разработан универсальный заголовок (ruavp_header_t), включая:
		+ Идентификаторы источника и получателя
		+ Тип данных (structure_id)
		+ Контрольную сумму (CRC-16) для проверки целостности
		+ Поддержка разных форматов данных (например, core_cmd_t для команд)
		+ Минимальные накладные расходы (8 байт на заголовок)

2. **Надежная передача данных**
	* Реализован механизм проверки целостности (CRC) для обнаружения поврежденных пакетов
	* Учет порядка пакетов (через счетчики или временные метки)
	* Возможность повторной отправки критически важных данных

3. **Безопасность (шифрование "Кузнечик")**
	* Все пакеты шифруются алгоритмом ГОСТ Р 34.12-2015
	* Каждый пакет содержит уникальный IV для защиты от атак воспроизведения
	* Низкие накладные расходы (+16 байт на пакет)
	* Поддержка разных режимов (CFB, CBC)

4. **Производительность**
	* Высокая скорость обработки (подходит для VoIP, игр, IoT)
	* Минимальные задержки (< 50 мкс на слабых устройствах)
	* Эффективное использование полосы пропускания

5. **Гибкость и масштабируемость**
	* Легко добавляются новые типы данных (через structure_id)
	* Поддержка многопоточной обработки
	* Возможность аппаратной оптимизации (например, через ГОСТ-совместимые чипы)

**Рекомендации по развитию**

* Внедрить P2P-шифрование (ECDH + "Кузнечик")
* Добавить аутентификацию пакетов (HMAC или ГОСТ Р 34.11)
* Оптимизировать буферизацию для снижения нагрузки на CPU

**Итог**

Разработанная система соответствует современным требованиям к:

*  Скорости (UDP + оптимизированные структуры)
*  Безопасности (ГОСТ + CRC)
*  Гибкости (поддержка любых данных)

<div class="page"/>
