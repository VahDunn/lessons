# Совсем небольшое изменение в клиенте, сопровождается некоторым количеством тестов.

@utils.arg('server', metavar='<server>', help=_('Name or ID of server.'))
def do_swap_local_disk(cs, args):
    """Replace the server's local root disk with a volume."""
    _find_server(cs, args.server).swap_local_disk()


def swap_local_disk(self):
    """
    Replace the server's local root disk with a volume.

    :returns: An instance of novaclient.base.TupleWithMeta
    """
    return self.manager.swap_local_disk(self)


def swap_local_disk(self, server):
    """
    Replace the server's local root disk with a volume.

    :param server: The :class:`Server` (or its ID) to swap local disk
    :returns: An instance of novaclient.base.TupleWithMeta
    """
    return self._action('swap_local_disk', server, None)

# По сути это прокидывание команды через слои клиента, больше ничего

def test_swap_local_disk(self):
    s = self.cs.servers.get(1234)
    ret = s.swap_local_disk()
    self.assert_request_id(ret, fakes.FAKE_REQUEST_ID_LIST)
    self.assert_called('POST', '/servers/1234/action',
                       {'swap_local_disk': None})
    ret = self.cs.servers.swap_local_disk(s)
    self.assert_request_id(ret, fakes.FAKE_REQUEST_ID_LIST)
    self.assert_called('POST', '/servers/1234/action',
                       {'swap_local_disk': None})

def test_swap_local_disk(self):
    self.run_command('swap-local-disk sample-server')
    self.assert_called('POST', '/servers/1234/action',
                       {'swap_local_disk': None})

# Соответственно, мы просто проверяем, что команда вызывается
# Это, конечно, важно тестировать во имя стабильности кодовой базы - когда
# поведение находится не только в модальности "действительность" (то есть закреплено в самом коде),
# но и в модальности "необходимость" (закреплено тестами), меньше шансов что-то случайно сломать.
# Здесь все достаточно прозрачно. Однако, я задумался, что, поскольку мы говорим о коде относительно
# тонкого клиента, стоит все же более полноценно проверять его взаимодействие с "основной" системой.
# Поэтому я добавил еще и функциональный тест

import time

from novaclient.tests.functional import base


class TestSwapLocalDiskNovaClient(base.ClientTestBase):
    """Functional tests for swap local disk"""

    # The server-side action carries no microversion gate (it behaves like
    # 'shelve'), so the minimum client version is enough to exercise it.
    COMPUTE_API_VERSION = "2.1"

    def _assert_swap_local_disk(self, server_id, timeout=60, poll_interval=1):
        start_time = time.time()
        while time.time() - start_time < timeout:
            if 'swap_local_disk' in self.nova('instance-action-list %s ' %
                                              server_id):
                break
            time.sleep(poll_interval)
        else:
            self.fail("Swap local disk hasn't been executed for server %s"
                      % server_id)

    def wait_for_swapped_root_disk(self, server_id, timeout=300,
                                   poll_interval=3):
        """Wait until the server's local root disk is replaced by a volume.

        Swap is a boot-from-volume conversion: nova creates a volume, copies
        the root disk into it and re-attaches it. The final signal is that
        server ends up with exactly one attached volume that cinder
        reports as ``in-use``. Polling that state keeps the test fast when
        swap is quick and bounded when it is slow; the timeout turns a
        genuinely stuck swap into a failure instead of a hang.

        :param server_id: uuid of the instance being swapped
        :param timeout: timeout in seconds
        :param poll_interval: poll interval in seconds
        :returns: the attached root volume id
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            attachments = self.client.volumes.get_server_volumes(server_id)
            if len(attachments) == 1:
                volume = self.cinder.volumes.get(attachments[0].id)
                if volume.status == 'in-use':
                    return volume.id
            time.sleep(poll_interval)
        else:
            self.fail("Root disk of server %s was not replaced by a volume "
                      "after %d s" % (server_id, timeout))

    def test_swap_local_disk_in_active_state(self):
        server = self._create_server()
        self.wait_for_server_os_boot(server.id)
        self.nova('swap-local-disk %s ' % server.id)
        self._assert_swap_local_disk(server.id)



# Этот тест я намеренно сделал достаточно щадащим. Причем, за это еще и пришлось с ревьюером повоевать.
# Он настаивал, что нужно в тесте проверять сайд-эффекты и вариант отработки "большого функционала".
# Хотя вообще-то это должно покрываться (и покрывается) тестами, находящимися рядом с этим самым
# основным функционалом.
# Такой тест все равно может падать иногда "сам по себе" (из-за общей склонности системы к гонкам состояний :),
# но вероятность сильно ниже. Была индуцированная ревьюером мысль добавить вот это,

    def test_swap_local_disk_replaces_root_with_volume(self):
        server = self._create_server()
        self.wait_for_server_os_boot(server.id)

        # An image-booted server starts with no volume attachments; the swap
        # is what introduces one, so this is the baseline we compare against.
        self.assertEqual(
            [], self.client.volumes.get_server_volumes(server.id))

        self.nova('swap-local-disk %s ' % server.id)
        self._assert_swap_local_disk(server.id)

        volume_id = self.wait_for_swapped_root_disk(server.id)

        # The instance is now backed by that volume, so nova reports an empty
        # image reference (boot-from-volume) instead of the original image.
        server = self.client.servers.get(server.id)
        self.assertEqual('', server.image)
        self.addCleanup(self.cinder.volumes.delete, volume_id)

# но я от нее отказался по вышеописанным причинам (проверяет не относящийся к изменениям блок).

# Еще одо изменение - к существовавшим ранее пользовательским хинтам добавились
# хинты системные.

system_hints = {'nova:operations': ['live-migrate']}
if not CONF.workarounds.skip_hypervisor_version_check_on_lm:
    source_info = self._get_compute_info(self.source)
    hypervisor_version = versionutils.convert_version_to_str(
        source_info.hypervisor_version)
    system_hints['hypervisor_version'] = [
        '>=%s' % hypervisor_version]
request_spec.system_scheduler_hints = system_hints

# Как следствие, необходима логика взаимодействия их друг с другом.

def _parse_hint(self, hint):
    ops = [
        # First check operations with len=2, so that ">=1.2.3"
        # doesn't match op ">"
        ("!=", lambda a, b: a != b),
        ("<=", lambda a, b: a <= b),
        (">=", lambda a, b: a >= b),
        ("=", lambda a, b: a == b),
        ("<", lambda a, b: a < b),
        (">", lambda a, b: a > b),
    ]

    for op_str, op in ops:
        if hint.startswith(op_str):
            version_str = hint[len(op_str):]
            break
    else:
        raise exception.InvalidInput(reason=_("hypervisor_version "
                                              "schedule hint must start with an operation: %s") %
                                            ", ".join([x[0] for x in ops]))

    try:
        version = versionutils.convert_version_to_int(version_str)
    except Exception as e:
        raise exception.InvalidInput(reason=_("hypervisor_version "
                                              "schedule hint has invalid version format: %s") % e)

    return op, version


def _get_version_constraint(self, spec_obj):
    hints = (
        spec_obj.get_system_scheduler_hint('hypervisor_version'),
        spec_obj.get_scheduler_hint('hypervisor_version'),
    )
    parsed_hints = [self._parse_hint(hint) for hint in hints if hint]
    if not parsed_hints:
        return None

    # max() returns the first matching item, so the system hint wins when
    # both versions are equal.
    return max(parsed_hints, key=lambda parsed: parsed[1])


def host_passes(self, host_state, spec_obj):
    constraint = self._get_version_constraint(spec_obj)
    if not constraint:
        return True

    op, version = constraint
    return op(host_state.hypervisor_version, version)

# Соответственно, тесты - три варианта входных данных

def test_hv_filter_uses_system_hint_when_user_version_is_lower(self):
    spec_obj = objects.RequestSpec(
        scheduler_hints={"hypervisor_version": [">=2.9.0"]},
        system_scheduler_hints={"hypervisor_version": [">=2.11.0"]})

    self.assertFalse(self.filt_cls.host_passes(self.host, spec_obj))


def test_hv_filter_uses_user_hint_when_user_version_is_higher(self):
    spec_obj = objects.RequestSpec(
        scheduler_hints={"hypervisor_version": [">=2.11.0"]},
        system_scheduler_hints={"hypervisor_version": [">=2.9.0"]})

    self.assertFalse(self.filt_cls.host_passes(self.host, spec_obj))


def test_hv_filter_uses_system_hint_when_versions_are_equal(self):
    spec_obj = objects.RequestSpec(
        scheduler_hints={"hypervisor_version": [">2.10.0"]},
        system_scheduler_hints={"hypervisor_version": [">=2.10.0"]})

    self.assertTrue(self.filt_cls.host_passes(self.host, spec_obj))

# И еще случаи, когда чего-то нет

def test_hv_filter_uses_system_hint_when_no_user_hint(self):
    spec_obj = objects.RequestSpec(
        system_scheduler_hints={"hypervisor_version": [">=2.10.0"]})

    self.assertTrue(self.filt_cls.host_passes(self.host, spec_obj))

def test_hv_filter_uses_system_hint_when_no_user_hint_false(self):
    spec_obj = objects.RequestSpec(
        system_scheduler_hints={"hypervisor_version": [">2.10.0"]})

    self.assertFalse(self.filt_cls.host_passes(self.host, spec_obj))

# Для ситуаций, когда есть только пользовательский хинт, тесты уже были написаны не мной.


# Рефлексия.
# Полезное упражнение. Нравится в первую очередь тем, что учит смотреть "обратную сторону". То есть,
# ранее я писал тесты отталкиваясь от дизайна, и это правильно и важно. Но когда дело касается
# подготовки и стабилизации кодовой базы, а также фиксации поведения, необходимо идти немного в другом направлении
# то есть, задавать себе вопросы "а подчиняется ли конкретное маленькое ветвление общей логике?"
# "не вступает ли результат отработки этого куска кода в противоречие с общим дизайном?"
# и соответственно ответам на эти вопросы писать мелкие тесты. Разумеется, это касается в первую очередь бизнес-логики.
# И, разумеется, это чревато негибкостью. Но, на мой взгляд, второй случай как раз иллюстрирует полезные
# тесты для точного и конкретного, но все же жесткого бизнес-правила. И в первые итерации было действительно
# сильно проще проверять и писать тесты на моках. И это гораздо удобнее, чем писать все сразу, потому что
# написанный и сохраненный код это безусловно надежнее, чем человеческая "оперативная память".