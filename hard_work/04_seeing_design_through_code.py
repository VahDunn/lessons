# Предисловие:
# Это набор функций, который создает снапшот инстанса.
# Он относится к подразделю Compute большого монолита из нескольких основных кусков.
# (Compute, Storage, Network, Policies etc.)
# Он забагован, в его рамках существует гонка состояний, а также
# несостыковки между ожидаемыми и реальными состояниями.
# Стоит также отметить, что это легаси код с полным отсутствием типизации.
#
# Цель: создать бэкап
# Границы ответственности: я как разработчик отвечаю только
#  за оркестрацию и Compute-часть. То есть, баги под капотом у вызываемых по api
# функций меня не касаются, о них нужно лишь сообщить.
#
# Результат основной работы: создан полноценный (то есть такой, из которого можно
# сделать восстановление) бэкап в виде тома со снапшотом
#
# В первую очередь я "линейно" изучил высокоуровневую функцию на предмет того, что
# она должна делать, есть ли у основной работы доп. условия,
# какие должны (и не должны) быть сайд эффекты.
#

@check_instance_state(vm_state=[vm_states.ACTIVE, vm_states.STOPPED,
                                    vm_states.SUSPENDED, vm_states.SHELVED,
                                    vm_states.SHELVED_OFFLOADED,
                                    vm_states.STOPPED_OFFLOADED])
    def snapshot_volume_backed(self, context, instance, name,
                               extra_properties=None, backup_image=False):
        """Snapshot the given volume-backed instance.

        :param instance: nova.objects.instance.Instance object
        :param name: name of the backup or snapshot
        :param extra_properties: dict of extra image properties to include

        :returns: the new image metadata
        """
        image_meta = self._initialize_instance_snapshot_metadata(
            instance, name, extra_properties)
        # the new image is simply a bucket of properties (particularly the
        # block device mapping, kernel and ramdisk IDs) with no image data,
        # hence the zero size
        image_meta['size'] = 0
        for attr in ('container_format', 'disk_format'):
            image_meta.pop(attr, None)
        properties = image_meta['properties']
        # clean properties before filling
        for key in ('block_device_mapping', 'bdm_v2', 'root_device_name'):
            properties.pop(key, None)
        if instance.root_device_name:
            properties['root_device_name'] = instance.root_device_name

        bdms = objects.BlockDeviceMappingList.get_by_instance_uuid(
                context, instance.uuid)

        e_prefix = metrics.VOLUME_BACKED_SNAPSHOT_PREFIX + "total."
        quiesce_uuid = uuidutils.generate_uuid()
        event_data = {"quiesce_uuid": quiesce_uuid}
        try:
            result = self._snapshot_volume_backed(context=context,
                                                  instance=instance,
                                                  bdms=bdms,
                                                  image_meta=image_meta,
                                                  quiesce_uuid=quiesce_uuid,
                                                  backup_image=backup_image)
            self._record_action_start(context, instance,
                                      instance_actions.CREATE_IMAGE)
        except Exception as e:
            with common_exc.reraise_original():
                event_data["event_type"] = e_prefix + "error"
                self.camel.send_event(event_data=event_data,
                                      exc=e,
                                      context=context,
                                      instance=instance)

        event_data["event_type"] = e_prefix + "success"
        self.camel.send_event(event_data=event_data,
                              context=context,
                              instance=instance)

        return result

# Первым проходом осмотрел на предмет читаемости и понятности.
# Есть некая фильтрация, в которую при этом зашита неочевидная
#  бизнес-логика. Из кода совсем не ясно, от чего фильтруем и зачем.
# Сразу же кандидат на переделку, вынес в хелпер и добавил константы, превратив их в FrozenSet
# (предположим такая возможность есть).
#
# Теперь непосредственно дизайн.
# Функция
#
# Принимает контекст, инстанс, имя и некие дополнительные необязательные параметры
#
# Состав - контроллер с подготовкой и частичной валидацией
# входных данных, бизнес-логика (приватный метод) и оркестрируемые бизнес-логикой
#  элементы + хелперы для работы с сайд-эффектами и удобства преобразования входных данных.
#
#
# Что делает:
# 1. Проверяет соответствие типа инстанса разрешенным для снапшота --
# 1а - тип соответствует - идем дальше -> 2
# 1б - тип не соответствует - отмена Х
# 2. Фильтрует из метаданных ненужные. -> 3
# 3. Пытается вызвать и провести основную логику. --
# 3а - Основная логика прошла
# 3а1 - создается запись об action -> 4
# 3б - Основная логика не прошла
# 3б1 - Публикация эвента с ошибкой и ее рейз через контекстный менеджер - Х
# 4. Публикация  с success и возврат результата - V
#
# Возвращаемый результат - результат отработки приватного метода. Какой - пока непонятно.
#
# Получается, что у основной функции есть 1 ранний возврат и одно ключевое ветвление.
# В текущем виде она меня устраивает



def _record_action_start(self, context, instance, action):
    objects.InstanceAction.action_start(context, instance,
                                        action, want_result=False)

LEGACY_IMAGE_PROPERTIES = FrozenSet('container_format', 'disk_format')
LEGACY_VOLUME_BACKED_PROPERTIES = FrozenSet(
    'block_device_mapping', 'bdm_v2', 'root_device_name')

def _prepare_volume_backed_snapshot_metadata(self, image_meta,
                                                root_device_name):
    # The new image contains metadata only and has no image data.
    image_meta['size'] = 0
    for attr in LEGACY_IMAGE_PROPERTIES:
        image_meta.pop(attr, None)

    properties = image_meta['properties']
    for key in LEGACY_VOLUME_BACKED_PROPERTIES:
        properties.pop(key, None)
    if root_device_name:
        properties['root_device_name'] = root_device_name

@check_instance_state(vm_state=[vm_states.ACTIVE, vm_states.STOPPED,
                                vm_states.SUSPENDED, vm_states.SHELVED,
                                vm_states.SHELVED_OFFLOADED,
                                vm_states.STOPPED_OFFLOADED])
def snapshot_volume_backed(self, context, instance, name,
                            extra_properties=None, backup_image=False):
    """Snapshot the given volume-backed instance.

    :param instance: nova.objects.instance.Instance object
    :param name: name of the backup or snapshot
    :param extra_properties: dict of extra image properties to include

    :returns: the new image metadata
    """
    image_meta = self._initialize_instance_snapshot_metadata(
        instance, name, extra_properties)
    self._prepare_volume_backed_snapshot_metadata(
        image_meta, instance.root_device_name)

    bdms = objects.BlockDeviceMappingList.get_by_instance_uuid(
            context, instance.uuid)

    event_prefix = metrics.VOLUME_BACKED_SNAPSHOT_PREFIX + "total."
    quiesce_uuid = uuidutils.generate_uuid()
    event_data = {"quiesce_uuid": quiesce_uuid}
    try:
        result = self._snapshot_volume_backed(context=context,
                                                instance=instance,
                                                bdms=bdms,
                                                image_meta=image_meta,
                                                quiesce_uuid=quiesce_uuid,
                                                backup_image=backup_image)
        self._record_action_start(context, instance,
                                    instance_actions.CREATE_IMAGE)
    except Exception as e:
        with common_exc.reraise_original():
            event_data["event_type"] = event_prefix + "error"
            self.camel.send_event(event_data=event_data,
                                    exc=e,
                                    context=context,
                                    instance=instance)

    event_data["event_type"] = event_prefix + "success"
    self.camel.send_event(event_data=event_data,
                            context=context,
                            instance=instance)

    return result


# Далее - переходим к самой бизнес-логике, т.к. на текущем этапе контроллер меня устраивает
# (хотя есть подозрения о недостаточной валидации данных)
#
#
#  Оркестратор основной бизнес-логики. Управляет подготовкой VM,
# созданием и ожиданием снапшотов томов, восстановлением состояния VM,
# компенсацией при ошибке и созданием итогового образа.

# Что делает - основная работа по подготовке к снапшоту, самому снапшоту и созданию образа из него.
#
# Принимает уже подготовленные контроллером контекст, инстанс, список BDM,
# метаданные будущего образа, идентификатор quiesce и признак бэкапа убраза.


def _snapshot_volume_backed(self, context, instance, bdms, image_meta,
                            quiesce_uuid, backup_image=False):
    # NOTE(d.burmistrov): step #1 (preparation "image metadata/load bdms")
    #   is done in the public method: to much work is done in public and
    #   this method, so keep in mind this fact & improve it later during
    #   refactoring/rework

    # 2. preprocess bdms
    mapping, volume_items = self._preprocess_bdms_volume_backed_snapshot(
        context=context,
        bdms=bdms,
    )

    # 3. prepare instance (quiesce/pause/skip)
    snapshot_deadline = time.time() + CONF.vm_snapshot.wait_max_time
    if instance.vm_state not in [vm_states.SHELVED_OFFLOADED,
                                 vm_states.STOPPED_OFFLOADED]:
        restore_vm_state_callback = (
            self._prepare_instance_volume_backed_snapshot(
                context=context,
                instance=instance,
                volume_count=len(volume_items),
                quiesce_uuid=quiesce_uuid,
                backup_image=backup_image
            )
        )

    exc_info = None
    snapshot_ids = []
    track_step = CONF.vm_snapshot.wait_step_period
    try:
        # 4. create volume snapshots
        volume_mapping = self._create_volume_backed_snapshot(
            context=context,
            instance=instance,
            snapshot_name=image_meta['name'],
            volume_items=volume_items,
            snapshot_ids=snapshot_ids,
        )
        mapping.extend(volume_mapping)

        # 5. track volume snapshot states
        self._wait_available_volume_backed_snapshot(
            context=context,
            instance=instance,
            snapshot_ids=snapshot_ids,
            deadline=snapshot_deadline,
            step_period=track_step,
        )
    except Exception:  # temporary skip exception to execute callback
        exc_info = sys.exc_info()
        LOG.exception(_LE('Failed to create snapshot because'
                          ' of %(mod)s.%(cls)s error:'),
                      {'mod': exc_info[0].__module__,
                       'cls': exc_info[0].__name__},
                      instance=instance)

    # 6. restore original instance state
    if instance.vm_state not in [vm_states.SHELVED_OFFLOADED,
                                 vm_states.STOPPED_OFFLOADED]:
        try:
            restore_vm_state_callback(failed=bool(exc_info))
        except Exception as e:  # ignore callback error but send event
            LOG.exception(_LE('Failed to restore instance state because'
                            ' of %(mod)s.%(cls)s error:'),
                        {'mod': e.__class__.__module__,
                        'cls': e.__class__.__name__},
                        instance=instance)
            self.camel.send_event(
                event_data={
                    "event_type": (metrics.VOLUME_BACKED_SNAPSHOT_PREFIX
                                + "vm_state_restore.error")},
                exc=e,
                context=context,
                instance=instance,
            )

    # 7. abort request on error
    if exc_info:
        with common_exc.suppress_any():
            cleanup_step = CONF.vm_snapshot.cleanup_step_period
            cleanup_deadline = (time.time()
                                + CONF.vm_snapshot.cleanup_max_time)

            self._cleanup_volume_backed_snapshot(context=context,
                                                 instance=instance,
                                                 snapshot_ids=snapshot_ids,
                                                 deadline=cleanup_deadline,
                                                 step_period=cleanup_step)
        six.reraise(*exc_info)

    # 8. create image on successful snapshot
    if mapping:
        properties = image_meta['properties']
        properties['block_device_mapping'] = mapping
        properties['bdm_v2'] = True

    LOG.info(_LI('Creating image for instance snapshot.'),
             instance=instance)
    return self.image_api.create(context, image_meta)


# И снова я решил начать с оркестрируемых функций.

def _preprocess_bdms_volume_backed_snapshot(self, context, bdms):
    volume_items = []
    mapping = []

    for bdm in bdms:
        if bdm.no_device:
            continue

        if bdm.is_volume:
            volume = self.volume_api.get(context, bdm.volume_id)
            volume_items.append((volume, bdm))
        else:
            mapping.append(bdm.get_image_mapping())

    return mapping, volume_items

def _initialize_instance_snapshot_metadata(self, instance, name,
                                            extra_properties=None):
    """Initialize new metadata for a snapshot of the given instance.

    :param instance: nova.objects.instance.Instance object
    :param name: string for name of the snapshot
    :param extra_properties: dict of extra metadata properties to include

    :returns: the new instance snapshot metadata
    """
    image_meta = utils.get_image_from_system_metadata(
        instance.system_metadata)
    image_meta.update({'name': name,
                        'is_public': False})

    # Delete properties that are non-inheritable
    properties = image_meta['properties']
    for key in CONF.non_inheritable_image_properties:
        properties.pop(key, None)

    # The properties in extra_properties have precedence
    properties.update(extra_properties or {})

    return image_meta


def _create_volume_backed_snapshot(self, context, instance, snapshot_name,
                                    volume_items, snapshot_ids):
    mapping = []
    for volume, bdm in volume_items:
        LOG.debug('Creating snapshot from volume %s.',
                    volume['id'],
                    instance=instance)
        snapshot = self.volume_api.create_snapshot_force(
            context,
            volume['id'],
            _('snapshot for %s') % snapshot_name,
            volume['display_description'],
        )

        snapshot_ids.append(snapshot['id'])

        mapping_dict = block_device.snapshot_from_bdm(snapshot['id'], bdm)
        mapping_dict = mapping_dict.get_image_mapping()
        mapping.append(mapping_dict)

    LOG.info(_LI('Created %d snapshots for instance volumes.'),
                len(snapshot_ids),
                instance=instance)
    return mapping

def _wait_available_volume_backed_snapshot(
        self, context, instance, snapshot_ids, deadline, step_period):
    not_available = collections.OrderedDict.fromkeys(snapshot_ids)

    def check_snapshots_for_available():
        for snap_id in list(not_available.keys()):
            LOG.debug('Checking snapshot status for %s.',
                        snap_id,
                        instance=instance)
            snapshot = self.volume_api.get_snapshot(context, snap_id)
            snap_status = snapshot.get('status')
            if snap_status == 'available':
                del not_available[snap_id]
            elif snap_status == 'error':
                reason = ("snapshot %s transitioned into %s state"
                            % (snap_id, snap_status))
                raise exception.CinderVolumeSnapshotFailed(reason=reason)

    c = 0
    while not_available and time.time() < deadline:
        c += 1
        check_snapshots_for_available()
        time.sleep(step_period)
    if not c:  # check snapshots at least once
        check_snapshots_for_available()

    if not_available:
        reason = ("snapshots [%s] are still not in final states within %ss"
                    % (", ".join(not_available), deadline))
        raise exception.CinderVolumeSnapshotsNotInFinalState(reason=reason)

    LOG.info(_LI('%d snapshots became available.'),
                len(snapshot_ids),
                instance=instance)

def _cleanup_volume_backed_snapshot(self, context, instance, snapshot_ids,
                                    deadline, step_period):
    if not snapshot_ids:
        LOG.info(_LI("No snapshots to cleanup."), instance=instance)
        return

    LOG.info(_LI("Cleaning up %(snap_count)d snapshots: %(snap_ids)s"),
                {'snap_count': len(snapshot_ids),
                'snap_ids': snapshot_ids},
                instance=instance)
    to_cleanup = collections.OrderedDict.fromkeys(snapshot_ids, 0)
    attempt_msg = ('Snapshot %(snap_id)s cleanup attempt #%(attempt)d'
                    ' failed by reason: %(reason)r')

    def cleanup():
        for snap_id in list(to_cleanup.keys()):
            try:
                snapshot = self.volume_api.get_snapshot(context, snap_id)
                if snapshot.get('status') == 'creating':
                    LOG.debug(("Snapshot %s is in 'creating' status"
                                " - cleanup attempt skipped"),
                                snap_id,
                                instance=instance)
                    continue

                LOG.debug('Trying to cleanup snapshot %s.',
                            snap_id,
                            instance=instance)
                to_cleanup[snap_id] += 1
                self.volume_api.delete_snapshot(context, snap_id)
                del to_cleanup[snap_id]
            except Exception as e:
                LOG.debug(attempt_msg,
                            {'snap_id': snap_id,
                            'attempt': to_cleanup[snap_id],
                            'reason': e},
                            instance=instance)

    c = 0
    while to_cleanup and time.time() < deadline:
        c += 1
        cleanup()
        time.sleep(step_period)
    if not c:  # cleanup snapshots at least once
        cleanup()

    cleaned = set(snapshot_ids) - set(to_cleanup)
    LOG.info(_LI("Successfully cleaned up %(cleaned_count)d snapshots:"
                    " %(cleaned)s"),
                {'cleaned_count': len(cleaned), 'cleaned': list(cleaned)},
                instance=instance)
    if to_cleanup:
        LOG.warning(_LW("Failed to clean up %(failed_count)d snapshots:"
                        " %(failed)s"),
                    {'failed_count': len(to_cleanup),
                        'failed': list(to_cleanup)},
                    instance=instance)
    return list(to_cleanup)


# Здесь получается , что вариант отработки всего один - оба списка возвращаются всегда
# Могут быть пустыми или непустыми. Пока что менять ничего не стал.


def _prepare_instance_volume_backed_snapshot(self,
                                                context,
                                                instance,
                                                volume_count,
                                                quiesce_uuid,
                                                backup_image=False):

    qlog = logs.KVsPrefixAdapter(logger=LOG,
                                    kvs={"quiesce_uuid": quiesce_uuid})

    def empty_callback(failed):
        pass

    def unquiesce_callback(failed):
        LOG.info(_LI("Unquiescing instance after volume snapshot %s."),
                    "failure" if failed else "created",
                    instance=instance)
        self.compute_rpcapi.unquiesce_instance(ctxt=context,
                                                instance=instance,
                                                mapping=None)

    def unpause_callback(failed):
        LOG.info(_LI("Unpausing instance after volume snapshot %s."),
                    "failure" if failed else "created",
                    instance=instance)
        self.compute_rpcapi.unpause_instance(ctxt=context,
                                                instance=instance)

    if instance.vm_state != vm_states.ACTIVE:
        return empty_callback

    if self._quiesce_instance_volume_backed(context=context,
                                            instance=instance,
                                            quiesce_uuid=quiesce_uuid,
                                            log=qlog,
                                            backup_image=backup_image):
        return unquiesce_callback
    elif volume_count < 2:  # single volume
        LOG.warning(_LW("Instance has %d < 2 volumes - ignoring quiesce"
                        " error"),
                    volume_count,
                    instance=instance)
        return empty_callback

    # multiple volumes
    LOG.info(_LI("Attempting to pause multi-volume instance before "
                    "snapshot as quiesce failed."),
                instance=instance)
    try:
        self.compute_rpcapi.pause_instance(ctxt=context, instance=instance)
        LOG.info(_LI("Instance has been paused for volume snapshot."),
                    instance=instance)
    except Exception as e:
        LOG.warning(
            _LW("Failed to pause instance with %(err_type)s: %(err)s"),
            {"err_type": type(e), "err": e},
            instance=instance,
        )
        with common_exc.reraise_original():
            LOG.debug("Trying to unpause as pause has failed")
            self.compute_rpcapi.unpause_instance(ctxt=context,
                                                    instance=instance)

    return unpause_callback

# Я переписывал эту функцию несколько раз. Поначалу мне показалось, что лучше
# разнести ее на две, отделив действие над инстансом от выбора колбека.
# Но в итоге я пришел к выводу, что всей этой логике, специфичной для работающего инстанса
#  совсем не место в этом слое, и я унес ее в слой вычислений.
# Слишком много специфичной логики находится в, вообще-то,
# оркестрирующем/контроллерном слое.
# А вот offloaded ветку я оставил на месте, но выделил в отдельный сценарий.
#
# В итоге получается вот такое
#
def _snapshot_volume_backed(self, context, instance, bdms, image_meta,
                             quiesce_uuid, backup_image=False):
     mapping, volume_items = self._preprocess_bdms_volume_backed_snapshot(
         context=context,
         bdms=bdms,
     )
     is_offloaded = instance.vm_state in (
         vm_states.SHELVED_OFFLOADED,
         vm_states.STOPPED_OFFLOADED,
     )

     try:
         if is_offloaded:
             volume_mapping = self._create_offloaded_volume_backed_snapshot(
                 context=context,
                 instance=instance,
                 snapshot_name=image_meta['name'],
                 volume_items=volume_items,
             )

         if not is_offloaded:
             volume_mapping = self.compute_rpcapi.create_volume_backed_snapshot(
                 ctxt=context,
                 instance=instance,
                 volume_items=volume_items,
                 snapshot_name=image_meta['name'],
                 quiesce_uuid=quiesce_uuid,
                 backup_image=backup_image,
             )
     except Exception as error:
         LOG.exception(_LE('Failed to create snapshot because'
                           ' of %(mod)s.%(cls)s error:'),
                       {'mod': error.__class__.__module__,
                        'cls': error.__class__.__name__},
                       instance=instance)
         raise

     mapping.extend(volume_mapping)

     if mapping:
         properties = image_meta['properties']
         properties['block_device_mapping'] = mapping
         properties['bdm_v2'] = True

     LOG.info(_LI('Creating image for instance snapshot.'), instance=instance)
     return self.image_api.create(context, image_meta)

# Здесь варианта всего два - либо инстанс активен, либо на полочке.
# И тогда на уровне api это разводится на два варианта - снапшот или создан или нет.
#
# И нижележащие методы в api становятся проще, поскольку специфичны для offload.


# Отдельная ветка для offloaded
    def _create_offloaded_volume_backed_snapshot(
            self, context, instance, snapshot_name, volume_items):
        created_snapshot_ids = []
        snapshot_deadline = time.time() + CONF.vm_snapshot.wait_max_time

        try:
            mapping = self._create_offloaded_volume_snapshots(
                context=context,
                instance=instance,
                snapshot_name=snapshot_name,
                volume_items=volume_items,
                created_snapshot_ids=created_snapshot_ids,
            )
            self._wait_available_offloaded_volume_snapshots(
                context=context,
                instance=instance,
                created_snapshot_ids=created_snapshot_ids,
                deadline=snapshot_deadline,
                step_period=CONF.vm_snapshot.wait_step_period,
            )
        except Exception:
            with common_exc.suppress_any():
                cleanup_deadline = (time.time()
                                    + CONF.vm_snapshot.cleanup_max_time)
                self._cleanup_volume_snapshots(
                    context=context,
                    instance=instance,
                    created_snapshot_ids=created_snapshot_ids,
                    deadline=cleanup_deadline,
                    step_period=CONF.vm_snapshot.cleanup_step_period,
                )
            raise

        return mapping




    def _create_offloaded_volume_snapshots(
            self, context, instance, snapshot_name, volume_items,
            created_snapshot_ids):
        mapping = []
        for volume, bdm in volume_items:
            LOG.debug('Creating snapshot from volume %s.',
                      volume['id'],
                      instance=instance)
            snapshot = self.volume_api.create_snapshot_force(
                context,
                volume['id'],
                _('snapshot for %s') % snapshot_name,
                volume['display_description'],
            )

            created_snapshot_ids.append(snapshot['id'])

            mapping_dict = block_device.snapshot_from_bdm(snapshot['id'], bdm)
            mapping_dict = mapping_dict.get_image_mapping()
            mapping.append(mapping_dict)

        LOG.info(_LI('Created %d snapshots for instance volumes.'),
                 len(created_snapshot_ids),
                 instance=instance)
        return mapping

    def _wait_available_offloaded_volume_snapshots(
            self, context, instance, created_snapshot_ids, deadline,
            step_period):
        not_available = collections.OrderedDict.fromkeys(created_snapshot_ids)

        def check_snapshots_for_available():
            for snap_id in list(not_available.keys()):
                LOG.debug('Checking snapshot status for %s.',
                          snap_id,
                          instance=instance)
                snapshot = self.volume_api.get_snapshot(context, snap_id)
                snap_status = snapshot.get('status')
                if snap_status == 'available':
                    del not_available[snap_id]
                elif snap_status == 'error':
                    reason = ("snapshot %s transitioned into %s state"
                              % (snap_id, snap_status))
                    raise exception.CinderVolumeSnapshotFailed(reason=reason)

        c = 0
        while not_available and time.time() < deadline:
            c += 1
            check_snapshots_for_available()
            time.sleep(step_period)
        if not c:  # check snapshots at least once
            check_snapshots_for_available()

        if not_available:
            reason = ("snapshots [%s] are still not in final states within %ss"
                      % (", ".join(not_available), deadline))
            raise exception.CinderVolumeSnapshotsNotInFinalState(reason=reason)

        LOG.info(_LI('%d snapshots became available.'),
                 len(created_snapshot_ids),
                 instance=instance)

    def _cleanup_volume_snapshots(
            self, context, instance, created_snapshot_ids, deadline,
            step_period):
        if not created_snapshot_ids:
            LOG.info(_LI("No snapshots to cleanup."), instance=instance)
            return

        LOG.info(_LI("Cleaning up %(snap_count)d snapshots: %(snap_ids)s"),
                 {'snap_count': len(created_snapshot_ids),
                  'snap_ids': created_snapshot_ids},
                 instance=instance)
        to_cleanup = collections.OrderedDict.fromkeys(created_snapshot_ids, 0)
        attempt_msg = ('Snapshot %(snap_id)s cleanup attempt #%(attempt)d'
                       ' failed by reason: %(reason)r')

        def cleanup():
            for snap_id in list(to_cleanup.keys()):
                try:
                    snapshot = self.volume_api.get_snapshot(context, snap_id)
                    if snapshot.get('status') == 'creating':
                        LOG.debug(("Snapshot %s is in 'creating' status"
                                   " - cleanup attempt skipped"),
                                  snap_id,
                                  instance=instance)
                        continue

                    LOG.debug('Trying to cleanup snapshot %s.',
                              snap_id,
                              instance=instance)
                    to_cleanup[snap_id] += 1
                    self.volume_api.delete_snapshot(context, snap_id)
                    del to_cleanup[snap_id]
                except Exception as e:
                    LOG.debug(attempt_msg,
                              {'snap_id': snap_id,
                               'attempt': to_cleanup[snap_id],
                               'reason': e},
                              instance=instance)

        counter = 0
        while to_cleanup and time.time() < deadline:
            counter += 1
            cleanup()
            time.sleep(step_period)
        if not counter:  # cleanup snapshots at least once
            cleanup()

        cleaned = set(created_snapshot_ids) - set(to_cleanup)
        LOG.info(_LI("Successfully cleaned up %(cleaned_count)d snapshots:"
                     " %(cleaned)s"),
                 {'cleaned_count': len(cleaned), 'cleaned': list(cleaned)},
                 instance=instance)
        if to_cleanup:
            LOG.warning(_LW("Failed to clean up %(failed_count)d snapshots:"
                            " %(failed)s"),
                        {'failed_count': len(to_cleanup),
                         'failed': list(to_cleanup)},
                        instance=instance)
        return list(to_cleanup)


# Следовательно мы получаем вместо сложного ветвления с пробросом условий между ними
# достаточно простую линейную структуру, где по сути ветвления всего два
# 1. offload/ не offload, которое при этом сводится к одному исходу - созданию снапшота
# 2. Удалось создать снапшот или нет (соответственно во втором случае cleanup)
# Каждая ветка вызывает общий cleanup для созданных ею снапшотов.
# Функцию cleanup я сделал общей и поместил в общий для двух модулей код.
