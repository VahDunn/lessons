# 1. Временно изменить состояние -> выполнить действие -> восстановить состояние
#
#
# При создании файла функция временно меняет umask процесса. Потом она обязана
# вернуть прежнее значение, в том числе при ошибке открытия или записи файла.
# Не очень надежно.


# Было

def write_to_file(path, contents, umask=None):
    if umask:
        saved_umask = os.umask(umask)

    try:
        with open(path, 'w') as f:
            f.write(contents)
    finally:
        if umask:
            os.umask(saved_umask)


# Стало
#
# Контекстный менеджер temporary_umask инкапсулирует временную смену маски.
# Вызывающий код больше не хранит saved_umask и не организует finally.

@contextlib.contextmanager
def temporary_umask(mask):
    if not mask:
        yield
        return

    previous = os.umask(mask)
    try:
        yield
    finally:
        os.umask(previous)


def write_to_file(path, contents, umask=None):
    with temporary_umask(umask), open(path, 'w') as stream:
        stream.write(contents)



# 2. Обойти коллекцию -> обработать каждый элемент независимо от ошибок остальных
#
# Источник: compute-api/compute_api/database/implementations/database_sqlalchemy.py,
# SqlalchemyDatabase.disconnect.
#
# При остановке сервиса нужно освободить пулы соединений со всеми базами.
# Ошибка одного dispose не должна помешать попытке закрыть остальные пулы.
# В исходнике этот порядок действий повторяется для master, replica и cells.


# Было

class SqlalchemyDatabase:

    async def disconnect(self):
        try:
            await self._master_engine.dispose()
        except Exception:
            LOG.exception('Exception while disposing master engine')

        if self._replica_engine is not None:
            try:
                await self._replica_engine.dispose()
            except Exception:
                LOG.exception('Exception while disposing replica engine')

        try:
            await self._default_cell_engine.dispose()
        except Exception:
            LOG.exception('Exception while disposing default cell engine')

        for engine in self._cell_engines:
            try:
                await engine.dispose()
            except Exception:
                LOG.exception(
                    'Exception while disposing cell engine %s',
                    engine.url.database,
                )


# Стало.
#
# Выделена последовательность движков и операция dispose_all.
# В dispose_all находится управляющий шаблон: обработать элемент, записать
# его ошибку и продолжить обход. try/except расположен внутри цикла,
# поэтому ошибка одного элемента не прерывает обработку всей коллекции.

async def dispose_all(engines):
    for name, engine in engines:
        try:
            await engine.dispose()
        except Exception:
            LOG.exception('Exception while disposing %s', name)


class SqlalchemyDatabase:

    def _engines(self):
        yield 'master engine', self._master_engine
        if self._replica_engine is not None:
            yield 'replica engine', self._replica_engine
        yield 'default cell engine', self._default_cell_engine
        for engine in self._cell_engines:
            yield 'cell engine %s' % engine.url.database, engine

    async def disconnect(self):
        await dispose_all(self._engines())


# Прикладная операция отключения теперь занимает одну строку. Чтобы добавить
# ещё один движок, достаточно включить его в последовательность, не копируя
# обработку исключений. Лог сохраняет имя движка и трейс его ошибки.
#

# 3. Попытаться получить результат -> подождать -> повторить до истечения срока
#
# Этот метод используется NbdMount при получении блочного устройства.
#
# Если свободное устройство не удалось получить, код ждёт две секунды
# и пробует снова, пока не истечёт MAX_DEVICE_WAIT. Повторяется именно вызов
# _inner_get_dev, который сообщает об успехе своим возвращаемым значением.
# В обоих фрагментах этого примера опущено только логирование повторов и таймаута.


# Было

class Mount:

    def _get_dev_retry_helper(self):
        start_time = time.time()
        device = self._inner_get_dev()
        while not device:
            time.sleep(2)
            if time.time() - start_time > MAX_DEVICE_WAIT:
                return False
            device = self._inner_get_dev()
        return True


# Стало
#
# wait_until — функция-хелпер высшего порядка. Она принимает действие, которое
# возвращает признак успеха, и управляет временем и повторными вызовами.
# Такой интерфейс подходит и для получения устройства, и для опроса состояния
# виртуальной машины: меняется переданная функция, а не сам управляющий цикл.

def wait_until(operation, timeout, interval):
    started = time.time()
    while not operation():
        time.sleep(interval)
        if time.time() - started > timeout:
            return False
    return True


class Mount:

    def _get_dev_retry_helper(self):
        return wait_until(
            self._inner_get_dev, timeout=MAX_DEVICE_WAIT, interval=2,
        )


# В исходном варианте переиспользование цикла завязано на наследование от Mount
# и переопределение _inner_get_dev. Теперь достаточно передать обычную функцию
# или связанный метод, поэтому этот протокол доступен и другим частям проекта.



# Рефлексия
#
# Вот вроде не очень большая концепция, а как полезно!
# Удобно, активно пользовался контекстными менеджерами сам, но только ими, хотя можно больше.
# Сильно редуцирует количество багов (а значит и время дебага), что определенно приятно.
# И читаемость растет, и компактность. Причем, без снижения выразительности, а еще позволяет
# стандартизировать такие абстракции и переиспользовать по проекту.
# В контексте нашего славного легаси-монолита особенно нравится.
