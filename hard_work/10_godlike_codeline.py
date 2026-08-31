# Godlike codeline


# 1.1. Удаление дубликатов1
# Строка одновременно фильтрует элементы и изменяет множество внутри условия.

# Было

def uniq(lst):
    s = set()
    return [el for el in lst if el not in s and not s.add(el)]


# Стало

def uniq(elements):
    seen = set()
    unique_elements = []

    for element in elements:
        if element in seen:
            continue
        seen.add(element)
        unique_elements.append(element)

    return unique_elements


# 1.2. Выполнение скрипта
# Строка открывает файл, читает, компилирует и выполняет код.

# Было

exec(compile(open(path).read(), path, 'exec'), locals(), globals())


# Стало

with open(path) as script_file:
    script_source = script_file.read()

compiled_script = compile(script_source, path, 'exec')
exec(compiled_script, locals(), globals())


# 1.3. Сопоставление аргументов
# Строка получает имена аргументов, объединяет их со значениями и обновляет kwargs.

# Было

kwargs.update(dict(zip(function.__code__.co_varnames[2:], args)))


# Стало

argument_names = function.__code__.co_varnames[2:]
positional_arguments = zip(argument_names, args)
arguments_by_name = dict(positional_arguments)
kwargs.update(arguments_by_name)


# 1.4. Разбор PCI-адреса
# Выражение повторно разделяет адрес для заполнения четырёх полей.

# Было

dev.domain, dev.bus, dev.slot, dev.function = \
    pci_addr.split(":")[0], \
    pci_addr.split(":")[1], \
    pci_addr.split(":")[2].split(".")[0], \
    pci_addr.split(":")[2].split(".")[1]


# Стало

domain, bus, device = pci_addr.split(":")
slot, function = device.split(".")

dev.domain = domain
dev.bus = bus
dev.slot = slot
dev.function = function


# 1.5. Расчёт размера образа
# Строка выбирает значение, преобразует тип, переводит единицы и округляет.

# Было

image_size = int(
    int(math.ceil(float(image_meta.size or 0.0) / units.Gi))
)


# Стало

image_size_bytes = float(image_meta.size or 0.0)
image_size_gib = image_size_bytes / units.Gi
image_size = int(math.ceil(image_size_gib))


# 1.6. Сбор тегов проекта
# Строка разделяет строку, дважды очищает значения, фильтрует и удаляет дубликаты.

# Было

def get_project_tags_from_aggregate(aggregate):
    tags_csv = (aggregate.metadata or {}).get(PROJECT_TAGS_METADATA_KEY, '')
    return set(tag.strip() for tag in tags_csv.split(',') if tag.strip())


# Стало

def get_project_tags_from_aggregate(aggregate):
    tags_csv = (aggregate.metadata or {}).get(PROJECT_TAGS_METADATA_KEY, '')
    raw_tags = tags_csv.split(',')
    tags = set()

    for raw_tag in raw_tags:
        tag = raw_tag.strip()
        if tag:
            tags.add(tag)

    return tags


# 1.7. Загрузка портов
# Строка вызывает API, извлекает данные из ответа и изменяет список портов.

# Было

ports.extend(neutron.list_ports(**search_opts).get('ports'))


# Стало

response = neutron.list_ports(**search_opts)
new_ports = response.get('ports')
ports.extend(new_ports)


# Рефлексия
# На самом деле, подобных мест в коде еще много. Очень много.
# И это, разумеется, сильно затрудняет его чтение и понимание, особенно на ранних этапах.
# Более того, судя по общению коллег, такие проблемы возникают и у людей с большим стажем в команде.
# Вообще, я не считаю, что писать однострочники это безусловно плохо, но здесь прямо вот чувствовал боль,
# когда их распутывал. И не очень понятно, зачем было так писать, дело ведь даже не только в сложности
# восприятия (которая субъективна) - это как минимум сложнее поддерживать и вносить изменения.
# Но вопрос "зачем было так делать" у меня при чтении этого репозитория возникает достаточно часто :)