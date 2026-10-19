# 2. Призрачное состояние.

# Локальный флаг управляет разморозкой, при этом ни в сигнатуре функции, ни где бы то ни было в спецификации
# он не указан, хотя следовало бы. На мой взгляд, здесь напрашивается расширение интерфейса И документации.

quiesced = False
try:
    self._set_quiesced(context, instance, image_meta, True)
    quiesced = True
except exception.NovaException as err:
    ...

try:
    ...
finally:
    self._host.write_instance_config(xml)
    if quiesced:
        self._set_quiesced(context, instance, image_meta, False)


# Здесь вообще интересно - volume_type_is_supported управляет по сути только изменениями себя, и
# другие опирающиеся на эту переменную проверки убраны. Ранее это был пример, иллюстрирующи описываемую проблему
# с фантомным состоянием. Сейчас, конечно, это просто избыточный код.
#
volume_types = None
  volume_type_is_supported = False
  for bdm in block_device_mappings:
      volume_type = bdm.volume_type
      if volume_type:
          if not volume_type_is_supported:
              # Set the flag to avoid calling
              # _check_compute_supports_volume_type more than once in
              # this for loop.
              volume_type_is_supported = True
          if not volume_types:
              volume_types = self.volume_api.get_all_volume_types(
                  context)
          self._check_requested_volume_type(bdm, volume_type,
                                            volume_types)
    ...


# 3. Слишком узкие предположения.

# iter_default считает, что двоеточие будет одно, и, например, endpoint:https://host:8774 разберется некорректно.
# Решается коррекцией парсинга со сплитом и обращением по индексу. Или спцификацией.
#
def iter_default(attributes):
    """Iterate on attributes with default values."""
    for attribute in attributes:
        if ':' in attribute:
            name, default = attribute.split(':')
        else:
            name = attribute
            default = None
        yield name, default


# read_cached_file - более старый mtime сам по себе не обновляет кэш.
# По сути, мы предполагаем, что любое обновление будет двигать время модификации только вперед.

reloaded = False
mtime = os.path.getmtime(filename)
cache_info = _FILE_CACHE.setdefault(filename, {})
if not cache_info or mtime > cache_info.get('mtime', 0):
    LOG.debug("Reloading cached file %s", filename)
    with open(filename) as fap:
        cache_info['data'] = fap.read()
    cache_info['mtime'] = mtime
    reloaded = True
return (reloaded, cache_info['data'])



def make_dev_path(dev, partition=None, base='/dev'):
    ...
    path = os.path.join(base, dev)
    if partition:
        path += str(partition)
    return path

# А это сгенерировало баг. Потому что приехали устройства, у которых имена заканчиваются на цифру, а раздел
# указывается через p. Ну и соответственно имена обрабатывались неправильно.
# Из-за предположения, что приедет подходящее имя.


# 4. Интерфейсы, которым недостаточно сигнатуры.

# 4.1. Два разных смысла None. Вообще конечно вроде бы из текста понятно как там что, но как-то жутко
# коряво и неконсистентно, потому что у одинакового значения противоположный логический смысл.
#
# :param block_migration: if true, prepare for block migration
#                         if None, calculate it in driver
# :param disk_over_commit: if true, allow disk over commit
#                          if None, ignore disk usage checking



# cast или call в зависимости от версии удалённого сервиса.
#
if not messaging_utils.version_is_compatible(host_version, version):
    ...
    cctxt = client.prepare(server=host, version=version)
    return cctxt.cast(ctxt, 'attach_volume', **kwargs)

cctxt = client.prepare(server=host, version=version)
return cctxt.call(ctxt, 'attach_volume', **kwargs)

# Это вообще говоря сделано для совместимости, но без нормального интерфейса получается условно фантомное
# состояние

# допустимость UUID зависит от source_type - примерно аналогично.
#
elif source_type == 'blank' and device_uuid:
    raise exception.InvalidBDMFormat(
        details=_("Invalid device UUID."))
elif source_type != 'blank':
    if not device_uuid:
        raise exception.InvalidBDMFormat(
            details=_("Missing device UUID."))

# здесь еще и пресловутые elif на частные случаи (и вложенные if :).

# Рефлексия.
# Получилось полезно, но, честно говоря, очень много времени ушло на поиск подобных штук. Как это
# решать эффективно, кроме недопускания подобных ситуаций, не очень понятно, пока что.
# При этом ряд ситуаций, которые я привел в качестве примера, еще и весьма неочевидны без
# достаточно глубоких технических знаний конкретики. А гарантировать, что каждый разработчик,
# пишущий код, обладает таковыми, не получается даже при самых оптимистичных предположениях -
# все частности держать в голове каждого разработчика вряд ли выйдет, если говорить о проектах такой сложности.
# Хотя, конечно, очень хотелось бы.
