# Type hints и typing

## Type hints основы

### Что такое аннотации типов в Python и зачем они нужны

Аннотации типов — это подсказки для статических анализаторов (mypy, pyright) и IDE о том, какого типа должны быть переменные, аргументы функций и возвращаемые значения. Python не проверяет их во время выполнения — это только статический инструмент.

Зачем нужны: ловят ошибки до запуска кода, улучшают автодополнение в IDE, делают код самодокументируемым.

```python
# без аннотаций
def greet(name):
    return "Hello, " + name

# с аннотациями
def greet(name: str) -> str:
    return "Hello, " + name

# переменные
age: int = 25
items: list[str] = ["a", "b"]
```

### Что такое Optional и когда его использовать

`Optional[X]` означает что значение может быть типа `X` или `None`. Начиная с Python 3.10 можно писать `X | None` — это эквивалентно.

```python
from typing import Optional

# старый синтаксис
def find_user(user_id: int) -> Optional[str]:
    ...

# новый синтаксис (Python 3.10+)
def find_user(user_id: int) -> str | None:
    ...
```

Используй `Optional` когда функция может не найти результат и вернуть `None`.

### Чем отличается Union от нового синтаксиса с вертикальной чертой

`Union[X, Y]` и `X | Y` — одно и то же, но `X | Y` появился в Python 3.10 и считается предпочтительным как более читаемый. `X | None` заменяет `Optional[X]`.

```python
from typing import Union

# старый синтаксис
def process(value: Union[int, str]) -> Union[int, str]:
    return value

# новый синтаксис (Python 3.10+)
def process(value: int | str) -> int | str:
    return value
```

### Что такое TypeVar и для чего он используется

`TypeVar` создаёт переменную типа — позволяет писать обобщённые функции, где тип входящего аргумента связан с типом результата. Это нужно чтобы тайпчекер знал: если передал `int`, получишь `int`, а не просто `Any`.

```python
from typing import TypeVar

T = TypeVar("T")

def first(items: list[T]) -> T:
    return items[0]

result = first([1, 2, 3])   # result: int
result = first(["a", "b"])  # result: str
```

В Python 3.12 появился более лаконичный синтаксис — `TypeVar` можно не импортировать:

```python
# Python 3.12+
def first[T](items: list[T]) -> T:
    return items[0]
```

### Что такое Generic и как создать обобщённый класс

`Generic[T]` используется как базовый класс для создания обобщённых классов. В Python 3.12 появился новый синтаксис без импорта `Generic` и `TypeVar`.

```python
from typing import TypeVar, Generic

T = TypeVar("T")

# старый синтаксис (работает во всех версиях)
class Stack(Generic[T]):
    def __init__(self) -> None:
        self.items: list[T] = []

    def push(self, item: T) -> None:
        self.items.append(item)

    def pop(self) -> T:
        return self.items.pop()

# новый синтаксис (Python 3.12+)
class Stack[T]:
    def __init__(self) -> None:
        self.items: list[T] = []

    def push(self, item: T) -> None:
        self.items.append(item)

    def pop(self) -> T:
        return self.items.pop()

stack = Stack[int]()
stack.push(1)
stack.push(2)
print(stack.pop())  # 2
```

### Что такое Protocol и чем он отличается от ABC

`Protocol` (добавлен в Python 3.8, PEP 544) реализует структурную типизацию — класс считается совместимым с протоколом если у него есть нужные методы и атрибуты, без явного наследования. ABC (Abstract Base Class) требует явного наследования — это номинальная типизация.

```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> str:
        ...

class Circle:  # не наследует Drawable!
    def draw(self) -> str:
        return "circle"

class Square:  # не наследует Drawable!
    def draw(self) -> str:
        return "square"

def render(shape: Drawable) -> None:
    print(shape.draw())

render(Circle())  # OK — есть метод draw()
render(Square())  # OK — есть метод draw()
```

Protocol — это «статический duck typing»: тайпчекер проверяет структуру, не наследование.

### Что такое runtime_checkable и когда это нужно

По умолчанию `Protocol` работает только при статической проверке. Декоратор `@runtime_checkable` позволяет использовать `isinstance()` с протоколом в рантайме, но проверяет только наличие методов — не их сигнатуры.

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Closeable(Protocol):
    def close(self) -> None:
        ...

class File:
    def close(self) -> None:
        pass

f = File()
print(isinstance(f, Closeable))  # True

# Внимание: isinstance с протоколами медленнее обычного
# и не проверяет типы аргументов методов
```

### Что такое type alias и как его объявить

Type alias — это псевдоним для типа, чтобы не повторять длинные аннотации. В Python 3.12 появилось ключевое слово `type` для явного объявления псевдонимов.

```python
# старый способ (работает везде)
from typing import TypeAlias
Vector: TypeAlias = list[float]

# новый способ (Python 3.12+)
type Vector = list[float]
type Matrix = list[Vector]

def scale(v: Vector, factor: float) -> Vector:
    return [x * factor for x in v]
```

### Что такое Callable в аннотациях типов

`Callable[[arg_types], return_type]` описывает тип функции или любого вызываемого объекта.

```python
from collections.abc import Callable

def apply(func: Callable[[int, int], int], a: int, b: int) -> int:
    return func(a, b)

def add(x: int, y: int) -> int:
    return x + y

result = apply(add, 1, 2)  # result: int

# функция без аргументов возвращающая строку
handler: Callable[[], str]

# любые аргументы — используй ...
callback: Callable[..., None]
```

### Что такое Any и когда его использовать

`Any` совместим с любым типом — тайпчекер не проверяет операции над значением типа `Any`. Используй как последнее средство когда тип действительно неизвестен или при постепенном добавлении типов в большой проект.

```python
from typing import Any

def process(data: Any) -> Any:
    return data  # тайпчекер не проверяет ничего

# лучше использовать object если хочешь принять любой тип
# но не хочешь разрешать произвольные операции
def log(value: object) -> None:
    print(value)
```

Злоупотребление `Any` убивает смысл типизации.

### Что такое Final и как запретить переопределение переменной или метода

`Final` запрещает переприсваивание переменной. `@final` запрещает переопределение метода или наследование от класса.

```python
from typing import Final, final

MAX_SIZE: Final = 100
MAX_SIZE = 200  # ошибка тайпчекера

@final
class Singleton:
    pass

class Child(Singleton):  # ошибка тайпчекера
    pass

class Base:
    @final
    def important(self) -> None:
        pass

class Derived(Base):
    def important(self) -> None:  # ошибка тайпчекера
        pass
```

## Dataclasses

### Что такое dataclasses и зачем они нужны

Модуль `dataclasses` (появился в Python 3.7, PEP 557) позволяет создавать классы для хранения данных с минимальным количеством шаблонного кода. Декоратор `@dataclass` автоматически генерирует методы `__init__`, `__repr__` и `__eq__` на основе аннотированных полей класса. Это избавляет от необходимости вручную писать однотипный boilerplate код, снижает вероятность ошибок и делает структуру класса очевидной с первого взгляда.

```python
from dataclasses import dataclass

@dataclass
class User:
    name: str
    age: int
    email: str = ""

user = User("Alice", 30)
print(user)         # User(name='Alice', age=30, email='')
print(user.name)    # Alice
user2 = User("Alice", 30)
print(user == user2)  # True — __eq__ сравнивает поля
```

### Чем dataclass отличается от NamedTuple

Оба служат для хранения данных, но имеют принципиальные отличия. `NamedTuple` — неизменяемый, является подклассом `tuple`, поддерживает распаковку и индексацию. `dataclass` — по умолчанию изменяемый, является обычным классом, поддерживает наследование, валидацию в `__post_init__` и множество дополнительных опций. Если нужна простая неизменяемая запись без логики — `NamedTuple`, если нужна гибкость и методы — `dataclass`.

```python
from typing import NamedTuple
from dataclasses import dataclass

class PointTuple(NamedTuple):
    x: float
    y: float

@dataclass
class PointData:
    x: float
    y: float

pt = PointTuple(1.0, 2.0)
print(pt[0])        # 1.0 — поддерживает индексацию
x, y = pt           # поддерживает распаковку

pd = PointData(1.0, 2.0)
pd.x = 5.0          # OK — изменяемый
# pd[0]             # TypeError — нет индексации
```

### Что такое field и когда его использовать

Функция `field()` из модуля `dataclasses` даёт тонкий контроль над поведением отдельных полей. Основные причины использовать `field()`: задать фабричную функцию для мутабельных значений по умолчанию (список, словарь нельзя задать напрямую как дефолт), исключить поле из `__repr__` или `__eq__`, пометить поле как не участвующее в `__init__`.

```python
from dataclasses import dataclass, field

@dataclass
class Order:
    items: list[str] = field(default_factory=list)
    _id: int = field(default=0, repr=False)
    tags: set[str] = field(default_factory=set)

    # НЕЛЬЗЯ писать items: list = [] — это ошибка ValueError
    # потому что один и тот же список стал бы дефолтом для всех экземпляров

o1 = Order()
o2 = Order()
o1.items.append("book")
print(o2.items)  # [] — у каждого свой список
```

### Что такое __post_init__ в dataclass

`__post_init__` — специальный метод который вызывается автоматически в конце сгенерированного `__init__`. Используется для валидации данных, вычисления производных полей или любой логики инициализации которую нельзя выразить через дефолтные значения. Это ключевое преимущество `dataclass` над `NamedTuple` — можно добавить логику не теряя декларативности.

```python
from dataclasses import dataclass
from datetime import date

@dataclass
class Person:
    name: str
    birth_year: int
    age: int = 0

    def __post_init__(self):
        if self.birth_year < 1900:
            raise ValueError("Слишком старый год рождения")
        self.age = date.today().year - self.birth_year

p = Person("Alice", 1990)
print(p.age)  # 35 (вычислено автоматически)
```

### Что такое frozen dataclass и чем он полезен

`@dataclass(frozen=True)` делает экземпляр неизменяемым — попытка изменить поле вызовет `FrozenInstanceError`. Побочный эффект: frozen dataclass становится хешируемым и может использоваться как ключ словаря или элемент множества. Это полезно для Value Objects в DDD, конфигурационных объектов и других случаев где важна иммутабельность.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    x: float
    y: float

p = Point(1.0, 2.0)
# p.x = 5.0  # FrozenInstanceError

# можно использовать как ключ словаря
distances = {Point(0, 0): 0, Point(3, 4): 5}
print(distances[Point(0, 0)])  # 0
```

### Что такое slots=True в dataclass и зачем это нужно

Начиная с Python 3.10, `@dataclass(slots=True)` автоматически добавляет `__slots__` к классу. Это запрещает создание произвольных атрибутов и значительно снижает потребление памяти — вместо словаря `__dict__` для каждого экземпляра используется фиксированный набор слотов. Для классов с большим количеством экземпляров это может дать ощутимый выигрыш по памяти и небольшое ускорение доступа к атрибутам.

```python
from dataclasses import dataclass
import sys

@dataclass
class WithoutSlots:
    x: int
    y: int

@dataclass(slots=True)
class WithSlots:
    x: int
    y: int

a = WithoutSlots(1, 2)
b = WithSlots(1, 2)
print(sys.getsizeof(a))  # ~48 bytes + __dict__
print(sys.getsizeof(b))  # меньше — нет __dict__

# a.z = 10   # OK — есть __dict__
# b.z = 10   # AttributeError — нет __dict__
```

## Walrus operator

### Что такое walrus operator и как он работает

Оператор `:=` (walrus operator, «морж», PEP 572, Python 3.8) позволяет присвоить значение переменной прямо внутри выражения. Название «морж» — из-за внешнего сходства с глазами и клыками моржа. Главная цель — избежать двойного вычисления выражения или двойного вызова функции когда результат нужен и для условия и для тела блока.

```python
# без walrus — вычисляем data дважды или нужна отдельная строка
data = get_data()
if data:
    process(data)

# с walrus — одна строка, одно вычисление
if data := get_data():
    process(data)
```

### В каких случаях walrus operator особенно полезен

Наиболее полезен в трёх сценариях: цикл `while` с чтением данных, list comprehension с фильтрацией по результату вычисления, и регулярные выражения где матч нужен и для проверки и для извлечения групп. Злоупотреблять не стоит — если код становится менее читаемым, лучше обойтись обычным присваиванием.

```python
import re

# while с чтением — классический паттерн
while chunk := f.read(8192):
    process(chunk)

# list comprehension — вычисляем expensive_calc один раз
results = [y for x in data if (y := expensive_calc(x)) > 0]

# регулярные выражения
pattern = r"\d+"
if match := re.search(pattern, text):
    print(match.group())  # используем match и для проверки и для результата
```

## match/case

### Что такое структурный паттерн матчинг в Python

`match/case` (Python 3.10+, PEP 634) — это не просто замена цепочки `if/elif`. Это полноценный механизм структурного паттерн матчинга, аналогичный тому что есть в Rust, Haskell, Scala. Он позволяет сопоставлять значение не только с константами но и с его структурой — типом, формой, содержимым коллекции, атрибутами объекта. Питон не просто сравнивает значения, он деструктурирует объект и связывает части с переменными.

```python
command = ("move", 10, 20)

match command:
    case ("move", x, y):
        print(f"Двигаемся в {x}, {y}")
    case ("stop",):
        print("Стоп")
    case _:
        print("Неизвестная команда")
```

### Какие виды паттернов существуют в match/case

Паттерны бывают нескольких видов и могут комбинироваться. Литеральный — сравнение с константой. Capture — связывание с переменной. Wildcard `_` — совпадает со всем но не связывает. OR паттерн через `|`. Паттерн последовательности для списков и кортежей. Паттерн отображения для словарей. Паттерн класса для объектов. Guard — дополнительное условие через `if`.

```python
def process(event):
    match event:
        case {"type": "click", "x": x, "y": y} if x > 0:  # mapping + guard
            print(f"Клик в {x}, {y}")
        case {"type": "scroll", "delta": int(d)}:           # mapping + класс
            print(f"Скролл на {d}")
        case [first, *rest]:                                 # последовательность
            print(f"Список: первый={first}, остальных={len(rest)}")
        case str() as s:                                     # класс + capture
            print(f"Строка: {s}")
        case None | False:                                   # OR паттерн
            print("Пусто")
        case _:
            print("Неизвестно")
```

### Как match/case работает с dataclasses

Паттерн класса позволяет сопоставлять и деструктурировать датаклассы и другие классы с `__match_args__`. `__match_args__` — это кортеж имён атрибутов определяющий порядок позиционных аргументов в паттерне. В датаклассах он генерируется автоматически.

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float

@dataclass
class Circle:
    center: Point
    radius: float

shape = Circle(Point(0, 0), 5.0)

match shape:
    case Circle(center=Point(x=0, y=0), radius=r):
        print(f"Круг в начале координат, радиус {r}")
    case Circle(center=Point(x=x, y=y), radius=r):
        print(f"Круг в ({x}, {y}), радиус {r}")
    case Point(x=x, y=y):
        print(f"Точка в ({x}, {y})")
```

## asyncio

### Что такое asyncio и как он работает

`asyncio` — стандартная библиотека Python для написания конкурентного кода с помощью синтаксиса `async/await`. В основе лежит цикл событий (event loop) — бесконечный цикл который управляет корутинами и переключается между ними когда одна из них ожидает I/O операцию. В отличие от потоков asyncio работает в одном потоке и не имеет проблем с гонками данных. Это делает его идеальным для I/O-bound задач: сетевые запросы, работа с базами данных, файловый I/O. Для CPU-bound задач asyncio не даёт преимуществ — там нужен multiprocessing.

```python
import asyncio

async def fetch(url: str) -> str:
    await asyncio.sleep(1)  # имитация сетевого запроса
    return f"data from {url}"

async def main():
    result = await fetch("https://example.com")
    print(result)

asyncio.run(main())  # запускает event loop
```

### Чем корутина отличается от обычной функции и от Task

Корутина — это функция объявленная через `async def`. Сама по себе при вызове она не выполняется, а возвращает объект корутины. Чтобы выполнить корутину нужно `await` её или обернуть в `Task`. `Task` — это обёртка над корутиной которая планирует её выполнение в event loop и позволяет запускать несколько корутин конкурентно без явного `await` каждой. Корутина с `await` выполняется последовательно, `Task` — конкурентно с другими задачами.

```python
import asyncio

async def work(n: int) -> int:
    await asyncio.sleep(1)
    return n * 2

async def main():
    # последовательно — займёт 2 секунды
    r1 = await work(1)
    r2 = await work(2)

    # конкурентно через Task — займёт 1 секунду
    t1 = asyncio.create_task(work(1))
    t2 = asyncio.create_task(work(2))
    r1, r2 = await t1, await t2
```

### Что такое asyncio.gather и когда его использовать

`asyncio.gather()` запускает несколько корутин или задач конкурентно и ждёт завершения всех. Результаты возвращаются в том же порядке что и входные аргументы — независимо от порядка завершения. Параметр `return_exceptions=True` позволяет не прерываться при исключении в одной из задач — вместо этого исключение попадает в результат как обычное значение. Начиная с Python 3.11 для большинства случаев предпочтительнее `TaskGroup` — он безопаснее.

```python
import asyncio

async def fetch(url: str) -> str:
    await asyncio.sleep(0.5)
    return f"data from {url}"

async def main():
    # все три запроса идут параллельно
    results = await asyncio.gather(
        fetch("site-a.com"),
        fetch("site-b.com"),
        fetch("site-c.com"),
    )
    print(results)  # ['data from site-a.com', ...]

    # не падаем если одна задача упала
    results = await asyncio.gather(
        fetch("good.com"),
        asyncio.sleep(-1),  # упадёт
        return_exceptions=True,
    )
    for r in results:
        if isinstance(r, Exception):
            print(f"Ошибка: {r}")
```

### Что такое asyncio.TaskGroup и чем он лучше gather

`asyncio.TaskGroup` (Python 3.11+, PEP 654) — это контекстный менеджер для структурированного запуска группы задач. При выходе из блока `async with` автоматически ожидает завершения всех задач. Ключевое преимущество перед `gather`: если одна из задач падает с исключением — все остальные задачи немедленно отменяются, а исключения собираются в `ExceptionGroup`. Это устраняет проблему «осиротевших» задач которые продолжают работать в фоне после ошибки. Для обработки `ExceptionGroup` используется синтаксис `except*`.

```python
import asyncio

async def fetch(url: str) -> str:
    await asyncio.sleep(0.5)
    if "bad" in url:
        raise ValueError(f"Не могу загрузить {url}")
    return f"data from {url}"

async def main():
    try:
        async with asyncio.TaskGroup() as tg:
            t1 = tg.create_task(fetch("site-a.com"))
            t2 = tg.create_task(fetch("bad-site.com"))  # упадёт
            t3 = tg.create_task(fetch("site-c.com"))
        # если всё ок — берём результаты здесь
        print(t1.result(), t3.result())
    except* ValueError as eg:
        for exc in eg.exceptions:
            print(f"Ошибка: {exc}")
```

### Что такое asyncio.timeout и как им пользоваться

`asyncio.timeout()` (Python 3.11+) — контекстный менеджер для ограничения времени выполнения блока кода. Это современная замена `asyncio.wait_for()`. При превышении времени поднимается `asyncio.TimeoutError`. Удобство `asyncio.timeout` в том что он работает с любым кодом внутри блока, а не только с одной корутиной. Хорошо комбинируется с `TaskGroup`.

```python
import asyncio

async def slow_operation() -> str:
    await asyncio.sleep(10)
    return "done"

async def main():
    # простой таймаут
    try:
        async with asyncio.timeout(2.0):
            result = await slow_operation()
    except TimeoutError:
        print("Превышено время ожидания")

    # таймаут на всю группу задач
    try:
        async with asyncio.timeout(3.0):
            async with asyncio.TaskGroup() as tg:
                t1 = tg.create_task(slow_operation())
                t2 = tg.create_task(slow_operation())
    except TimeoutError:
        print("Вся группа отменена по таймауту")
```

### Что такое asyncio.to_thread и зачем он нужен

`asyncio.to_thread()` (Python 3.9+) запускает синхронную блокирующую функцию в отдельном потоке не блокируя event loop. Это правильный способ интегрировать синхронный код (например синхронные библиотеки, `time.sleep`, тяжёлые вычисления) в асинхронное приложение. Под капотом использует `ThreadPoolExecutor`.

```python
import asyncio
import time

def blocking_io(filename: str) -> str:
    time.sleep(2)  # имитация долгой синхронной операции
    return f"content of {filename}"

async def main():
    # НЕ делай так — блокирует весь event loop
    # content = blocking_io("file.txt")

    # Делай так — выполняется в потоке
    content = await asyncio.to_thread(blocking_io, "file.txt")
    print(content)

    # несколько блокирующих операций конкурентно
    results = await asyncio.gather(
        asyncio.to_thread(blocking_io, "file1.txt"),
        asyncio.to_thread(blocking_io, "file2.txt"),
    )
```

### Что такое ExceptionGroup и синтаксис except*

`ExceptionGroup` (Python 3.11+, PEP 654) — это контейнер для нескольких исключений одновременно. Появился вместе с `TaskGroup` для обработки случаев когда несколько задач падают одновременно. `except*` — новый синтаксис который фильтрует исключения из группы по типу и позволяет обработать каждый тип отдельно. Обычный `except` с `ExceptionGroup` тоже работает — поймает всю группу целиком.

```python
import asyncio

async def fail(msg: str, exc_type: type) -> None:
    raise exc_type(msg)

async def main():
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(fail("сеть", ConnectionError))
            tg.create_task(fail("данные", ValueError))
    except* ConnectionError as eg:
        print(f"Сетевые ошибки: {eg.exceptions}")
    except* ValueError as eg:
        print(f"Ошибки данных: {eg.exceptions}")

asyncio.run(main())
# Сетевые ошибки: (ConnectionError('сеть'),)
# Ошибки данных: (ValueError('данные'),)
```

## Инструменты разработки

### Что такое ruff и зачем он нужен

`ruff` — линтер и форматтер для Python написанный на Rust, разработанный компанией Astral (авторы `uv`). Главная идея: заменить целый стек инструментов — Flake8, Black, isort, pyupgrade, pydocstyle — одним быстрым бинарником. Скорость — ключевое преимущество: на больших проектах ruff работает в 10-100 раз быстрее чем Flake8 или Black по отдельности. Реализует более 900 правил. Используется в таких проектах как FastAPI, pandas, pydantic, Apache Airflow. Важно понимать: ruff — это линтер и форматтер, но не тайпчекер. Для проверки типов по-прежнему нужен mypy или pyright.

```bash
# установка
uv add --dev ruff

# проверка кода
ruff check .

# автоматическое исправление
ruff check --fix .

# форматирование (аналог Black)
ruff format .
```

### Как настроить ruff в pyproject.toml

Вся конфигурация ruff живёт в `pyproject.toml` в секции `[tool.ruff]`. Это заменяет отдельные файлы `.flake8`, `pyproject.toml` для black и `.isort.cfg`. Правила выбираются через `select` по категориям: `E/W` — pycodestyle, `F` — Pyflakes, `I` — isort, `B` — flake8-bugbear, `UP` — pyupgrade (модернизация синтаксиса).

```toml
[tool.ruff]
line-length = 88

[tool.ruff.lint]
select = [
    "E",   # pycodestyle ошибки
    "F",   # Pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "UP",  # pyupgrade — предлагает современный синтаксис
]
ignore = ["E501"]  # игнорировать длину строки если нужно

[tool.ruff.lint.isort]
known-first-party = ["app", "bot"]
```

### Что такое mypy и чем отличается от ruff

`mypy` — статический тайпчекер для Python. В отличие от ruff который проверяет стиль и типичные ошибки, mypy проверяет корректность типов на основе аннотаций. Это разные уровни проверки: ruff найдёт неиспользуемый импорт или неправильный отступ, mypy найдёт что ты передал `str` туда где ожидается `int`. Mypy не запускает код — это статический анализ. Стандартная рекомендация: использовать ruff + mypy вместе. Mypy поддерживает постепенное добавление типов — можно начать с нетипизированного кода и аннотировать файл за файлом.

```bash
uv add --dev mypy

# проверить проект
mypy .

# строгий режим — требует аннотации везде
mypy --strict .
```

### Что такое строгий режим mypy и что он включает

`--strict` включает набор самых строгих проверок. В строгом режиме mypy требует аннотации у всех функций, запрещает неявный `Any`, предупреждает если вызываешь функцию без аннотаций из сторонней библиотеки. Для новых проектов рекомендуется сразу включать строгий режим. Для существующих больших кодовых баз лучше включать проверки постепенно — добавлять флаги по одному.

```toml
# pyproject.toml — настройка через файл
[tool.mypy]
strict = true
ignore_missing_imports = true  # игнорировать либы без стабов

# исключить конкретные библиотеки без типов
[[tool.mypy.overrides]]
module = "some_untyped_lib.*"
ignore_errors = true
```

```python
# type: ignore — заглушить ошибку в конкретной строке
result = some_dynamic_function()  # type: ignore[no-any-return]
```

### Что такое uv и чем он лучше pip

`uv` — менеджер пакетов и окружений Python написанный на Rust, разработан компанией Astral. Устанавливает пакеты в 10-100 раз быстрее чем pip за счёт параллельной загрузки и агрессивного кэширования. Полностью совместим с `pyproject.toml` и стандартом PEP 517/518. Заменяет сразу несколько инструментов: pip, pip-tools, virtualenv, pyenv (частично). Поддерживает lock-файлы (`uv.lock`) для воспроизводимых сборок. Активно принят сообществом — используется в крупных проектах как стандарт.

```bash
# создать проект
uv init my-project

# создать виртуальное окружение
uv venv

# добавить зависимость
uv add fastapi

# добавить dev-зависимость
uv add --dev pytest ruff mypy

# установить все зависимости из lock-файла
uv sync

# запустить команду в окружении проекта
uv run python main.py
uv run pytest
```

### Чем uv.lock отличается от requirements.txt

`uv.lock` — это lock-файл который фиксирует точные версии всех зависимостей включая транзитивные (зависимости зависимостей), с хешами для верификации целостности. Это гарантирует что на любой машине и в CI будет установлено ровно то же самое. `requirements.txt` фиксирует только прямые зависимости и не содержит хешей по умолчанию. `uv.lock` нужно коммитить в git. `pyproject.toml` содержит требования к версиям (например `fastapi>=0.100`), `uv.lock` — точные разрешённые версии.

```bash
# uv.lock создаётся автоматически при uv add
uv add requests

# обновить все зависимости до последних совместимых версий
uv lock --upgrade

# обновить конкретный пакет
uv lock --upgrade-package requests

# установить строго по lock-файлу (для CI)
uv sync --frozen
```

## SQLAlchemy 2.0

### Чем SQLAlchemy 2.0 отличается от 1.x

SQLAlchemy 2.0 (вышел в январе 2023) — это мажорная версия с рядом принципиальных изменений. Главные отличия: новый стиль объявления моделей через `DeclarativeBase` и `Mapped[]` с полной поддержкой типизации; новый способ запросов через `select()` вместо устаревшего `session.query()`; `Session.execute()` вместо `Session.query()`; обязательный `session.commit()` или контекстный менеджер вместо автокоммита. Старый стиль 1.x по большей части всё ещё работает в 2.0 в режиме совместимости, но считается устаревшим.

```python
# Старый стиль (1.x, устарел)
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)

users = session.query(User).filter(User.name == "Alice").all()

# Новый стиль (2.0)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import select

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

stmt = select(User).where(User.name == "Alice")
users = session.execute(stmt).scalars().all()
```

### Что такое Mapped и mapped_column в SQLAlchemy 2.0

`Mapped[T]` — это дженерик-аннотация которая говорит SQLAlchemy что атрибут является колонкой с конкретным Python-типом. `mapped_column()` — функция для уточнения параметров колонки (индекс, уникальность, nullable и т.д.). Если дополнительных параметров нет, `mapped_column()` можно опустить — тип будет выведен из `Mapped[T]`. `Mapped[Optional[str]]` или `Mapped[str | None]` автоматически делает колонку nullable. Это ключевое улучшение 2.0: модели теперь полностью совместимы с mypy и IDE.

```python
from typing import Optional
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text

class Base(DeclarativeBase):
    pass

class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), index=True)
    body: Mapped[str] = mapped_column(Text)
    summary: Mapped[str | None]           # nullable, mapped_column не нужен
    views: Mapped[int] = mapped_column(default=0)
```

### Как выполнять запросы в SQLAlchemy 2.0

В 2.0 все запросы строятся через `select()` и выполняются через `session.execute()`. Результат — объект `Result`, из которого данные извлекаются методами: `scalars().all()` для списка ORM-объектов, `scalar_one()` для одного объекта (бросает исключение если не один), `scalar_one_or_none()` если может не быть результата, `all()` для списка `Row` кортежей. Метод `session.query()` считается устаревшим.

```python
from sqlalchemy import select

# получить всех пользователей
stmt = select(User).order_by(User.name)
users = session.execute(stmt).scalars().all()

# с фильтрацией
stmt = select(User).where(User.age > 18, User.is_active == True)
users = session.execute(stmt).scalars().all()

# один объект или None
stmt = select(User).where(User.id == user_id)
user = session.execute(stmt).scalar_one_or_none()

# join
stmt = select(User).join(User.posts).where(Post.published == True)
users = session.execute(stmt).scalars().all()
```

### Как добавлять, обновлять и удалять объекты в SQLAlchemy 2.0

Операции записи не изменились принципиально, но в 2.0 рекомендуется использовать контекстный менеджер `with Session(engine) as session` для гарантированного закрытия сессии. `session.add()` добавляет или обновляет объект, `session.delete()` помечает на удаление, `session.commit()` фиксирует транзакцию. Важно: в 2.0 нет автокоммита — нужно явно вызывать `commit()`.

```python
from sqlalchemy.orm import Session

with Session(engine) as session:
    # создать
    user = User(name="Alice", age=30)
    session.add(user)
    session.commit()
    session.refresh(user)  # обновить из БД (например чтобы получить id)
    print(user.id)

    # обновить
    user.age = 31
    session.commit()

    # удалить
    session.delete(user)
    session.commit()

    # bulk insert (эффективнее чем add() в цикле)
    session.execute(
        insert(User),
        [{"name": "Bob", "age": 25}, {"name": "Carol", "age": 28}]
    )
    session.commit()
```

## Alembic

### Что такое Alembic и зачем он нужен

Alembic — инструмент для управления миграциями базы данных, разработанный автором SQLAlchemy. Миграция — это файл с Python-кодом который описывает как изменить схему БД (добавить таблицу, колонку, индекс) и как откатить это изменение. Alembic хранит историю миграций аналогично тому как git хранит историю коммитов — каждая ревизия ссылается на предыдущую через `down_revision`. Это позволяет применять изменения последовательно (`upgrade`) и откатывать их (`downgrade`). Без миграций при изменении модели нужно вручную менять схему БД на каждом сервере.

```bash
# инициализация (создаёт папку alembic/ и alembic.ini)
alembic init alembic

# создать пустую ревизию
alembic revision -m "add users table"

# применить все миграции
alembic upgrade head

# откатить последнюю миграцию
alembic downgrade -1

# посмотреть историю
alembic history

# текущая версия БД
alembic current
```

### Что такое autogenerate в Alembic и как он работает

`--autogenerate` — флаг который заставляет Alembic сравнить текущую схему БД с метаданными SQLAlchemy моделей и автоматически сгенерировать код миграции. Это огромная экономия времени: не нужно вручную писать `op.create_table()`, `op.add_column()` и т.д. Важно понимать ограничения: autogenerate обнаруживает добавление/удаление таблиц и колонок, изменение nullable, индексы и ограничения. Но не обнаруживает переименования таблиц и колонок (показывает как удаление + добавление), изменения хранимых процедур, данные. Сгенерированные миграции всегда нужно проверять перед применением.

```bash
# сгенерировать миграцию автоматически
alembic revision --autogenerate -m "add email to users"
```

```python
# пример сгенерированного файла миграции
"""add email to users

Revision ID: a1b2c3d4e5f6
Revises: 9z8y7x6w5v4u
Create Date: 2024-01-15 10:30:00
"""
from alembic import op
import sqlalchemy as sa

revision = 'a1b2c3d4e5f6'
down_revision = '9z8y7x6w5v4u'

def upgrade() -> None:
    op.add_column('users', sa.Column('email', sa.String(120), nullable=True))
    op.create_index('ix_users_email', 'users', ['email'])

def downgrade() -> None:
    op.drop_index('ix_users_email', table_name='users')
    op.drop_column('users', 'email')
```

### Как настроить Alembic для работы с моделями SQLAlchemy

После `alembic init alembic` нужно настроить два файла: `alembic.ini` — строка подключения к БД, и `alembic/env.py` — импорт метаданных моделей. Без указания `target_metadata` autogenerate не будет работать — Alembic не знает о существовании моделей.

```python
# alembic/env.py — ключевые изменения
from app.database import Base          # импорт Base с метаданными
from app import models                 # импорт всех моделей чтобы они зарегистрировались

target_metadata = Base.metadata        # указываем метаданные для autogenerate
```

```ini
# alembic.ini
sqlalchemy.url = sqlite:///./data/cards.db
# или через переменную окружения:
# sqlalchemy.url = %(DATABASE_URL)s
```

## Безопасность и JWT

### Что такое JWT и из чего он состоит

JWT (JSON Web Token) — это стандарт (RFC 7519) для передачи данных между сторонами в виде компактного самодостаточного токена. Называется самодостаточным потому что сервер не хранит сессии — вся нужная информация о пользователе находится внутри самого токена. Токен состоит из трёх частей разделённых точками: `header.payload.signature`. Каждая часть закодирована в Base64URL — это не шифрование, данные можно декодировать без ключа. Шифрование заменяет подпись: без знания секретного ключа нельзя создать валидную подпись, поэтому сервер проверяет что токен не был изменён.

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9       # header
.eyJ1c2VyX2lkIjoxLCJleHAiOjE3MDAwMDAwMDB9  # payload
.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c  # signature
```

```python
import base64, json

# декодируем payload (добавляем padding если нужно)
payload = "eyJ1c2VyX2lkIjoxLCJleHAiOjE3MDAwMDAwMDB9"
decoded = base64.urlsafe_b64decode(payload + "==")
print(json.loads(decoded))  # {'user_id': 1, 'exp': 1700000000}
# данные видны без ключа — не храни секреты в payload!
```

### Что находится в header, payload и signature JWT

**Header** — JSON объект с типом токена и алгоритмом подписи. Поле `alg` определяет как вычисляется подпись: `HS256` — симметричный HMAC-SHA256 (один секретный ключ), `RS256` — асимметричный RSA (приватный ключ для подписи, публичный для проверки).

**Payload** — JSON объект с утверждениями (claims). Стандартные: `sub` — субъект (обычно user_id), `exp` — время истечения, `iat` — время выдачи, `nbf` — не раньше чем. Плюс любые кастомные поля. Payload не зашифрован — не клади туда пароли или секреты.

**Signature** — результат подписи `base64url(header) + "." + base64url(payload)` секретным ключом. Если изменить хоть один символ в header или payload, подпись станет невалидной.

```python
import jwt  # PyJWT

# создать токен
token = jwt.encode(
    {"user_id": 1, "exp": datetime.utcnow() + timedelta(hours=24)},
    key="secret",
    algorithm="HS256",
)

# проверить и декодировать
payload = jwt.decode(token, key="secret", algorithms=["HS256"])
print(payload)  # {"user_id": 1, "exp": ...}
```

### Какие алгоритмы подписи JWT бывают и чем они отличаются

Алгоритмы делятся на симметричные и асимметричные. **Симметричные** (HS256, HS384, HS512) используют один общий секретный ключ для создания и проверки подписи — подходят когда подписывает и проверяет одна система. **Асимметричные** (RS256, ES256, EdDSA) используют пару ключей: приватный для подписи, публичный для проверки. Публичный ключ можно раздавать всем — это позволяет нескольким сервисам проверять токены не зная приватного ключа. По скорости и безопасности: EdDSA > ES256 > RS256 > HS256, но HS256 самый распространённый из-за простоты.

```python
# HS256 — один ключ, простой вариант
token = jwt.encode(payload, key="shared_secret", algorithm="HS256")
jwt.decode(token, key="shared_secret", algorithms=["HS256"])

# RS256 — пара ключей
from cryptography.hazmat.primitives.asymmetric import rsa
# подпись приватным ключом
token = jwt.encode(payload, private_key, algorithm="RS256")
# проверка публичным ключом
jwt.decode(token, public_key, algorithms=["RS256"])
```

### Что такое уязвимость alg:none в JWT

Спецификация JWT включает алгоритм `none` — токен без подписи. Уязвимость возникает когда сервер принимает алгоритм подписи из самого токена не проверяя что это ожидаемый алгоритм. Атакующий берёт любой валидный токен, меняет в header `"alg": "HS256"` на `"alg": "none"`, редактирует payload (например меняет `"role": "user"` на `"role": "admin"`), убирает подпись — и сервер принимает такой токен как валидный. Варианты обхода фильтров: `None`, `NONE`, `nOnE` — если сервер делает простое строковое сравнение.

**Защита:** всегда жёстко указывай список допустимых алгоритмов при верификации. PyJWT требует это явно.

```python
# НЕПРАВИЛЬНО — берём алгоритм из самого токена
payload = jwt.decode(token, key=secret, algorithms=jwt.get_unverified_header(token)["alg"])

# ПРАВИЛЬНО — жёстко указываем ожидаемый алгоритм
payload = jwt.decode(token, key=secret, algorithms=["HS256"])
# PyJWT откажет если в токене будет alg: none или любой другой алгоритм
```

### Почему слабый секретный ключ JWT опасен и как его выбрать

При алгоритме HS256 безопасность целиком зависит от сложности секретного ключа. Зная подписанный токен, атакующий может попробовать перебрать ключ офлайн с помощью hashcat или John the Ripper — никаких запросов к серверу не нужно. Короткие и предсказуемые ключи (`secret`, `password`, `changeme`) ломаются за секунды. Ключи взятые из примеров документации или скопированные из Stack Overflow часто есть в словарях для брутфорса.

**Правило:** секретный ключ должен быть минимум 32 байта случайных данных, никогда не хранится в коде, передаётся только через переменные окружения.

```python
import secrets

# генерация сильного ключа
key = secrets.token_hex(32)  # 64 символа hex = 32 байта
print(key)  # например: a3f8c2d1e4b7...

# в .env
# SECRET_KEY=a3f8c2d1e4b7...

# в коде — только из переменной окружения
import os
SECRET_KEY = os.environ["SECRET_KEY"]
```

### Где хранить JWT на клиенте и какие риски это несёт

Есть два основных варианта хранения в браузере, каждый со своими рисками. **localStorage** — простой доступ из JavaScript, но уязвим к XSS: если на сайте выполнится чужой скрипт, он прочитает токен и отправит атакующему. **HttpOnly cookie** — недоступна из JavaScript, защищает от XSS, но уязвима к CSRF: браузер автоматически отправляет cookie с каждым запросом, что можно использовать для атаки с другого сайта. CSRF решается через `SameSite=Strict` или CSRF-токены. Для большинства современных SPA рекомендуется HttpOnly cookie + `SameSite=Strict`.

```python
# FastAPI — установка JWT в HttpOnly cookie
from fastapi import Response

@app.post("/login")
async def login(response: Response):
    token = create_token(user_id=1)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,      # недоступна из JS
        samesite="strict",  # защита от CSRF
        secure=True,        # только HTTPS
        max_age=86400,      # 24 часа
    )
    return {"status": "ok"}
```

### Как правильно верифицировать JWT в Python

При верификации важно явно проверять все критичные параметры: алгоритм, время истечения, аудиторию. PyJWT делает это автоматически если правильно настроен — автоматически проверяет `exp`, `nbf`, `iat`. Главное не отключать проверки ради удобства.

```python
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

SECRET_KEY = "your-secret-key"

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            key=SECRET_KEY,
            algorithms=["HS256"],   # жёсткий список алгоритмов
            options={
                "require": ["exp", "sub"],  # обязательные поля
            }
        )
        return payload
    except ExpiredSignatureError:
        raise ValueError("Токен истёк")
    except InvalidTokenError:
        raise ValueError("Невалидный токен")

# НИКОГДА не делай так — отключает проверку подписи
jwt.decode(token, options={"verify_signature": False})
```
