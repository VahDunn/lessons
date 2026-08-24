# Ясный код 2


# 1.1. Метод, который используется только в тестах
# Продовый класс содержит отдельный метод ради одного теста :)

# Было

def _test_remove_vm(self, instance_uuid):
    """Removes the named VM, as if it crashed. For testing."""
    self.instances.pop(instance_uuid)


instance_uuid = instances[0]["uuid"]
self.compute.driver._test_remove_vm(instance_uuid)


# Стало

instance_uuid = instances[0]["uuid"]
instance_not_found = exception.InstanceNotFound(
    instance_id=instance_uuid)

with mock.patch.object(
        self.compute.driver,
        "get_info",
        side_effect=instance_not_found):
    self.compute._sync_power_states(ctxt)

# Инкапсулировал логику, нужную только для тестов, рядом с самими тестами.


# 1.2. Длинная цепочка методов
# Поиск root VHD проходит через цепочку прокси-методов и колбек.

# Было

def get_instance_dir(self, instance_name, remote_server=None,
                     create_dir=True, remove_dir=False):
    return self._get_instances_sub_dir(
        instance_name, remote_server, create_dir, remove_dir)


def _lookup_vhd_path(self, instance_name, vhd_path_func,
                     *args, **kwargs):
    vhd_path = None
    for format_ext in ["vhd", "vhdx"]:
        test_path = vhd_path_func(
            instance_name, format_ext, *args, **kwargs)
        if self.exists(test_path):
            vhd_path = test_path
            break
    return vhd_path


def lookup_root_vhd_path(self, instance_name, rescue=False):
    return self._lookup_vhd_path(
        instance_name, self.get_root_vhd_path, rescue)


def get_root_vhd_path(self, instance_name, format_ext, rescue=False):
    instance_path = self.get_instance_dir(instance_name)
    image_name = "root"
    if rescue:
        image_name += "-rescue"
    return os.path.join(
        instance_path, image_name + "." + format_ext.lower())


# Стало

def _find_vhd_path(self, directory, image_name):
    for format_ext in ("vhd", "vhdx"):
        path = os.path.join(
            directory, "%s.%s" % (image_name, format_ext))
        if self.exists(path):
            return path
    return None


def lookup_root_vhd_path(self, instance_name, rescue=False):
    instance_dir = self.get_instance_dir(instance_name)
    image_name = "root-rescue" if rescue else "root"
    return self._find_vhd_path(instance_dir, image_name)


def get_root_vhd_path(self, instance_name, format_ext, rescue=False):
    instance_path = self.get_instance_dir(instance_name)
    image_name = "root-rescue" if rescue else "root"
    return os.path.join(
        instance_path, "%s.%s" % (image_name, format_ext.lower()))

# Убрал один метод из цепочки, который по сути просто проксировал следующий. Судя по истории в гите,
# это просто недоработка коллег - раньше он делал больше. Ну и в целом поправил код немножко.


# 1.3. Слишком большой список параметров
# Метод принимает 20 несгруппированных параметров, один из которых не используется :)

# Было

def _validate_and_build_base_options(
    self, context, instance_type, boot_meta, image_href, image_id,
    kernel_id, ramdisk_id, display_name, display_description, key_name,
    key_data, availability_zone, user_data, metadata, access_ip_v4,
    access_ip_v6, requested_networks, config_drive, auto_disk_config,
    reservation_id
):
    ...


base_options, key_pair = self._validate_and_build_base_options(
    context, instance_type, boot_meta, image_href, image_id,
    kernel_id, ramdisk_id, display_name, display_description,
    key_name, key_data, availability_zone, user_data, metadata,
    access_ip_v4, access_ip_v6, requested_networks, config_drive,
    auto_disk_config, reservation_id)


# Стало

_BootOptions = collections.namedtuple(
    "_BootOptions",
    ["image_href", "image_meta", "kernel_id", "ramdisk_id",
     "config_drive", "auto_disk_config"])

_InstanceOptions = collections.namedtuple(
    "_InstanceOptions",
    ["display_name", "display_description", "key_name", "key_data",
     "user_data", "metadata"])

_NetworkOptions = collections.namedtuple(
    "_NetworkOptions",
    ["availability_zone", "access_ip_v4", "access_ip_v6",
     "requested_networks"])


def _validate_and_build_base_options(
        self, context, instance_type, boot, instance_options,
        network, reservation_id):
    if instance_options.user_data:
        ...

    kernel_id, ramdisk_id = self._handle_kernel_and_ramdisk(
        context,
        boot.kernel_id,
        boot.ramdisk_id,
        boot.image_meta)

    config_drive = self._check_config_drive(boot.config_drive)

    self.network_api.create_pci_requests_for_sriov_ports(
        context, pci_request_info, network.requested_networks)

    base_options = {
        "reservation_id": reservation_id,
        "image_ref": boot.image_href,
        "kernel_id": kernel_id or "",
        "ramdisk_id": ramdisk_id or "",
        "display_name": instance_options.display_name,
        "display_description": instance_options.display_description,
        "user_data": instance_options.user_data,
        "metadata": instance_options.metadata or {},
        "access_ip_v4": network.access_ip_v4,
        "access_ip_v6": network.access_ip_v6,
        "availability_zone": network.availability_zone,
        "config_drive": config_drive,
        ...
    }
    ...


boot = _BootOptions(
    image_href=image_href,
    image_meta=boot_meta,
    kernel_id=kernel_id,
    ramdisk_id=ramdisk_id,
    config_drive=config_drive,
    auto_disk_config=auto_disk_config)

instance_options = _InstanceOptions(
    display_name=display_name,
    display_description=display_description,
    key_name=key_name,
    key_data=key_data,
    user_data=user_data,
    metadata=metadata)

network = _NetworkOptions(
    availability_zone=availability_zone,
    access_ip_v4=access_ip_v4,
    access_ip_v6=access_ip_v6,
    requested_networks=requested_networks)

base_options, key_pair = self._validate_and_build_base_options(
    context,
    instance_type,
    boot,
    instance_options,
    network,
    reservation_id)

# Это даже комментировать не хочу, как в этом месиве что-то можно было понять - неизвестно.


# 1.4. Разные решения одной проблемы
# Разбор и валидация JSON реализованы двумя одинаковыми функциями.

# Было

def _extract_allocations(body, schema):
    try:
        data = jsonutils.loads(body)
    except ValueError as exc:
        raise webob.exc.HTTPBadRequest(
            _("Malformed JSON: %(error)s") % {"error": exc},
            json_formatter=util.json_error_formatter)
    try:
        jsonschema.validate(
            data,
            schema,
            format_checker=jsonschema.FormatChecker())
    except jsonschema.ValidationError as exc:
        raise webob.exc.HTTPBadRequest(
            _("JSON does not validate: %(error)s") % {"error": exc},
            json_formatter=util.json_error_formatter)
    return data


def extract_json(body, schema):
    try:
        data = jsonutils.loads(body)
    except ValueError as exc:
        raise webob.exc.HTTPBadRequest(
            _("Malformed JSON: %(error)s") % {"error": exc},
            json_formatter=json_error_formatter)
    try:
        jsonschema.validate(
            data,
            schema,
            format_checker=jsonschema.FormatChecker())
    except jsonschema.ValidationError as exc:
        raise webob.exc.HTTPBadRequest(
            _("JSON does not validate: %(error)s") % {"error": exc},
            json_formatter=json_error_formatter)
    return data


# Стало

def _set_allocations_for_consumer(req, schema):
    context = req.environ["placement.context"]
    consumer_uuid = util.wsgi_path_item(
        req.environ, "consumer_uuid")
    data = util.extract_json(req.body, schema)
    allocation_data = data["allocations"]
    ...


# 1.5. Чрезмерный результат
# Метод возвращает detailed вместе с диапазоном дат, хотя он нужен не всем вызываюим.

# Было

def _get_datetime_range(self, req):
    qs = req.environ.get("QUERY_STRING", "")
    env = urlparse.parse_qs(qs)
    period_start = self._parse_datetime(
        env.get("start", [None])[0])
    period_stop = self._parse_datetime(
        env.get("end", [None])[0])

    if not period_start < period_stop:
        msg = _(
            "Invalid start time. The start time cannot occur after "
            "the end time.")
        raise exc.HTTPBadRequest(explanation=msg)

    detailed = env.get("detailed", ["0"])[0] == "1"
    return period_start, period_stop, detailed


period_start, period_stop, detailed = self._get_datetime_range(req)
period_start, period_stop, ignore = self._get_datetime_range(req)


# Стало

def _get_datetime_range(self, req):
    qs = req.environ.get("QUERY_STRING", "")
    env = urlparse.parse_qs(qs)
    period_start = self._parse_datetime(
        env.get("start", [None])[0])
    period_stop = self._parse_datetime(
        env.get("end", [None])[0])

    if not period_start < period_stop:
        msg = _(
            "Invalid start time. The start time cannot occur after "
            "the end time.")
        raise exc.HTTPBadRequest(explanation=msg)

    return period_start, period_stop


def _is_detailed(self, req):
    qs = req.environ.get("QUERY_STRING", "")
    env = urlparse.parse_qs(qs)
    return env.get("detailed", ["0"])[0] == "1"


period_start, period_stop = self._get_datetime_range(req)
detailed = self._is_detailed(req)
period_start, period_stop = self._get_datetime_range(req)


# По сути вынес логику получения деталей в отдельный метод.
# Честно говоря, мне этот фикс кажется сомнительным, но я ничего лучше на улучшение не нашел.
# В плане возврата ответов в репо все неожиданно неплохо.


# Рефлексия
# Люблю такой рефакторинг, поэтому задание понравилось :)
# У нас еще есть contol plane, там такого было больше, а питон было поновее + FastAPI.
# Поэтому там большую часть аналогичной работы я уже сделал. Но было полезно покопаться прицельно в
# "большом" легаси, особенно в свете прохождения курса "Ясное легаси".
# Очень нравится, как голова разгружается после таких задач - то, что было запутанно и нечетко,
# обретает понятную форму.