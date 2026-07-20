# 1 - было. ЦС 16

def execute_step(self) -> None:
    """Start execution of the step."""
    if (
        not self.mediator.config.email.mail_send_enabled
        or not self.context.kwargs.get('client_emails')
        or self._no_letter_id_migrate_before()
    ):
        self.context.set(
            key='instances_to_notify_about',
            value={},
        )
        return

    notify_after = True
    if (
        not self.mediator.config.email.mail_send_enabled
        or self._no_letter_id_migrate_after()
    ):
        notify_after = False

    letter_id = self.mediator.config.email.letter_id_migrate_before
    migrations = self.context.get(
        expected_type=list[domain.MigrationTracker],
        key='migrations',
    )

    only_started = [
        tracker for tracker in migrations if not tracker.migration_info.error
    ]

    instances_to_notify_about: dict[
        interfaces.OwnerHint, dict[interfaces.NovaInstance, bool | None]
    ] = {}
    for tracker in only_started:
        if (
            not tracker.instance_info.owner.email
            or not tracker.instance_info.owner.vk_cs_project_id
        ):
            continue

        if (
            tracker.instance_info.owner.is_partner
            and self.mediator.config.email.filter_partner_projects_enabled
        ):
            continue

        if tracker.instance_info.owner in instances_to_notify_about:
            instances_to_notify_about[tracker.instance_info.owner][
                tracker.instance_info.instance
            ] = None
        else:
            instances_to_notify_about[tracker.instance_info.owner] = {
                tracker.instance_info.instance: None
            }

    for owner, instances in instances_to_notify_about.items():
        template_data = self._prepare_email_before(
            instances=sorted(instances.keys(), key=lambda x: x.name),
            target_availability_zone=self.var.report.get(
                'target_availability_zone'
            ),
        )

        self.mediator.watchdog.generate_heartbeat()
        self._send_email_with_debug(
            email_address=str(owner.email),
            letter_template_id=letter_id,
            template_label=str(owner.vk_cs_project_id),
            template_data=template_data,
        )

    if not notify_after:
        instances_to_notify_about.clear()

    self.context.set(
        key='instances_to_notify_about',
        value=instances_to_notify_about,
    )

# 1 - стало. ЦС 3

def execute_step() -> None:
    """Notify owners before migration and remember follow-up recipients."""
    if not _can_send_before_migration_notification():
        _save_instances_to_notify({})
        return

    notify_after = _can_send_after_migration_notification()
    letter_id = mediator.config.email.letter_id_migrate_before
    migrations = context.get(
        expected_type=list[domain.MigrationTracker],
        key='migrations',
    )

    instances_by_owner = _group_instances_for_notification(
        migrations,
    )
    _send_before_migration_notifications(
        instances_by_owner=instances_by_owner,
        letter_id=letter_id,
    )
    if not notify_after:
        instances_by_owner.clear()
    _save_instances_to_notify(instances_by_owner)


def _can_send_before_migration_notification() -> bool:
    # The order preserves the original short-circuit behavior: the helper
    # checking the letter id is not called when mail or recipients are off.
    return (
        mediator.config.email.mail_send_enabled
        and bool(context.kwargs.get('client_emails'))
        and not _no_letter_id_migrate_before()
    )

def _can_send_after_migration_notification() -> bool:
    return (
        mediator.config.email.mail_send_enabled
        and not _no_letter_id_migrate_after()
    )

def _is_owner_notifiable_before_migration(
    owner: interfaces.OwnerHint,
) -> bool:
    return (
        bool(owner.email)
        and bool(owner.vk_cs_project_id)
        and not (
            owner.is_partner
            and mediator.config.email.filter_partner_projects_enabled
        )
    )

def _group_instances_for_notification(
    migrations: list[domain.MigrationTracker],
) -> dict[
    interfaces.OwnerHint,
    dict[interfaces.NovaInstance, bool | None],
]:
    instances_by_owner: dict[
        interfaces.OwnerHint,
        dict[interfaces.NovaInstance, bool | None],
    ] = {}

    only_started = [
        tracker
        for tracker in migrations
        if not tracker.migration_info.error
    ]
    for tracker in only_started:
        owner = tracker.instance_info.owner
        if not _is_owner_notifiable_before_migration(owner):
            continue

        instances_by_owner.setdefault(owner, {})[
            tracker.instance_info.instance
        ] = None

    return instances_by_owner

def _send_before_migration_notifications(
    instances_by_owner: dict[
        interfaces.OwnerHint,
        dict[interfaces.NovaInstance, bool | None],
    ],
    letter_id: str,
) -> None:
    for owner, instances in instances_by_owner.items():
        template_data = _prepare_email_before(
            instances=sorted(instances, key=lambda instance: instance.name),
            target_availability_zone=var.report.get(
                'target_availability_zone'
            ),
        )

        mediator.watchdog.generate_heartbeat()
        _send_email_with_debug(
            email_address=str(owner.email),
            letter_template_id=letter_id,
            template_label=str(owner.vk_cs_project_id),
            template_data=template_data,
        )

def _save_instances_to_notify(
    instances_by_owner: dict[
        interfaces.OwnerHint,
        dict[interfaces.NovaInstance, bool | None],
    ],
) -> None:
    context.set(
        key='instances_to_notify_about',
        value=instances_by_owner,
    )

# 2 - было. ЦС 14

def _maybe_notify_owner(self, instance: interfaces.NovaInstance) -> None:
    """Use it as callback, alert owner when all instances are migrated."""
    hypervisor_state = self.context.get(
        expected_type=HypervisorState,
        key='hypervisor_state',
    )

    data = hypervisor_state.get_all_instances_of_the_owner(instance.uuid)
    owner, instances_before, instances_after = data

    if owner is None:
        return

    hypervisor_state.mark_instance_as_evacuated(owner, instance)

    if not hypervisor_state.all_instances_are_ready(owner):
        return

    self.mediator.event_listener.trigger(
        events.Evacuate.EVACUATED_GROUP,
        {
            'hostname': self.var.hostname,
            'event_set': self.var.event_set,
            'total': len(instances_before),
            'project_id': f'{owner.project_id} ({owner.vk_cs_project_id})',
            'targets_uuids': sorted(x.uuid for x in instances_before),
        },
    )

    if (
        not self.mediator.config.email.mail_send_enabled
        or self._no_letter_id_evacuate_after()
    ):
        return

    letter_id = self.mediator.config.email.letter_id_evacuate_after

    if not owner.email or not owner.vk_cs_project_id:
        return

    if not self._validate_owner(owner):
        return

    notifiable = [
        (before, after)
        for before, after in zip(
            instances_before,
            instances_after,
            strict=True,
        )
        if not _is_powered_off(before)
    ]
    if not notifiable:
        return

    notifiable_before = [before for before, _ in notifiable]
    notifiable_after = [after for _, after in notifiable]

    template_data = self._prepare_email_after(
        instances_before=notifiable_before,
        instances_after=notifiable_after,
    )

    self._send_email_with_debug(
        email_address=owner.email,
        letter_template_id=letter_id,
        template_label=owner.vk_cs_project_id,
        template_data=template_data,
    )

# 2 - стало. ЦС 5


def _maybe_notify_owner(,
    instance: interfaces.NovaInstance,
) -> None:
    ready_group = _mark_and_get_ready_owner_group(instance)
    if ready_group is None:
        return

    owner, instances_before, instances_after = ready_group
    _emit_evacuated_group(owner, instances_before)

    if not _is_after_evacuation_email_configured():
        return

    letter_id = mediator.config.email.letter_id_evacuate_after
    if not _is_valid_notification_owner(owner):
        return

    notifiable = _notifiable_instance_pairs(
        instances_before,
        instances_after,
    )
    if not notifiable:
        return

    _send_after_evacuation_notification(
        owner=owner,
        letter_id=letter_id,
        notifiable=notifiable,
    )

def _mark_and_get_ready_owner_group(
    instance: interfaces.NovaInstance,
) -> tuple[
    interfaces.OwnerHint,
    list[interfaces.NovaInstance],
    list[interfaces.NovaInstance],
] | None:
    hypervisor_state = context.get(
        expected_type=HypervisorState,
        key='hypervisor_state',
    )
    owner, instances_before, instances_after = (
        hypervisor_state.get_all_instances_of_the_owner(instance.uuid)
    )

    if owner is None:
        return None

    hypervisor_state.mark_instance_as_evacuated(owner, instance)
    if not hypervisor_state.all_instances_are_ready(owner):
        return None

    return owner, instances_before, instances_after

def _emit_evacuated_group(
    owner: interfaces.OwnerHint,
    instances_before: list[interfaces.NovaInstance],
) -> None:
    mediator.event_listener.trigger(
        events.Evacuate.EVACUATED_GROUP,
        {
            'hostname': var.hostname,
            'event_set': var.event_set,
            'total': len(instances_before),
            'project_id': (
                f'{owner.project_id} ({owner.vk_cs_project_id})'
            ),
            'targets_uuids': sorted(
                instance.uuid for instance in instances_before
            ),
        },
    )

def _is_after_evacuation_email_configured() -> bool:
    return (
        mediator.config.email.mail_send_enabled
        and not _no_letter_id_evacuate_after()
    )

def _is_valid_notification_owner(
    owner: interfaces.OwnerHint,
) -> bool:
    return (
        bool(owner.email)
        and bool(owner.vk_cs_project_id)
        and _validate_owner(owner)
    )

def _notifiable_instance_pairs(
    instances_before: list[interfaces.NovaInstance],
    instances_after: list[interfaces.NovaInstance],
) -> list[tuple[interfaces.NovaInstance, interfaces.NovaInstance]]:
    return [
        (before, after)
        for before, after in zip(
            instances_before,
            instances_after,
            strict=True,
        )
        if not _is_powered_off(before)
    ]

def _send_after_evacuation_notification(
    self,
    owner: interfaces.OwnerHint,
    letter_id: str,
    notifiable: list[
        tuple[interfaces.NovaInstance, interfaces.NovaInstance]
    ],
) -> None:
    notifiable_before = [before for before, _ in notifiable]
    notifiable_after = [after for _, after in notifiable]
    template_data = self._prepare_email_after(
        instances_before=notifiable_before,
        instances_after=notifiable_after,
    )

    self._send_email_with_debug(
        email_address=owner.email,
        letter_template_id=letter_id,
        template_label=owner.vk_cs_project_id,
        template_data=template_data,
    )

# 3 - было. ЦС 11

def execute_step(self) -> None:
    """Start execution of the step."""
    if (
        not self.mediator.config.email.mail_send_enabled
        or self._no_letter_id_evacuate_before()
    ):
        return

    hypervisor_state = self.context.get(
        expected_type=HypervisorState,
        key='hypervisor_state',
    )

    letter_id = self.mediator.config.email.letter_id_evacuate_before

    for owner, instances in self._iterate_on_projects():
        if not owner.email or not owner.vk_cs_project_id:
            continue

        if (
            owner.is_partner
            and self.mediator.config.email.filter_partner_projects_enabled
        ):
            continue

        active_instances = [
            instance for instance in instances if not _is_powered_off(instance)
        ]
        if not active_instances:
            self.mediator.event_listener.trigger(
                events.Email.NOT_SENDING_EMAIL,
                {
                    'hostname': self.var.hostname,
                    'event_set': self.var.event_set,
                    'project_id': (
                        f'{owner.project_id} ({owner.vk_cs_project_id})'
                    ),
                    'reason': 'all instances are powered off',
                },
            )
            continue

        template_data = self._prepare_email_before(
            instances=active_instances,
        )

        self._send_email_with_debug(
            email_address=owner.email,
            letter_template_id=letter_id,
            template_label=owner.vk_cs_project_id,
            template_data=template_data,
        )

        hypervisor_state.remember_instances_to_notify_about(
            owner=owner,
            instances=active_instances,
        )

# 3 - стало. ЦС 3

def execute_step() -> None:
    """Notify eligible owners before evacuation."""
    if not _is_before_evacuation_email_configured():
        return

    hypervisor_state = context.get(
        expected_type=HypervisorState,
        key='hypervisor_state',
    )
    letter_id = mediator.config.email.letter_id_evacuate_before

    for owner, instances in _iterate_on_projects():
        _maybe_notify_owner_before_evacuation(
            owner=owner,
            instances=instances,
            letter_id=letter_id,
            hypervisor_state=hypervisor_state,
        )

def _maybe_notify_owner_before_evacuation(
    owner: interfaces.OwnerHint,
    instances: list[interfaces.NovaInstance],
    letter_id: str,
    hypervisor_state: HypervisorState,
) -> None:
    if not _is_owner_notifiable_before_evacuation(owner):
        return

    active_instances = _active_instances(instances)
    if not active_instances:
        _emit_all_instances_powered_off(owner)
        return

    _send_before_evacuation_notification(
        owner=owner,
        instances=active_instances,
        letter_id=letter_id,
    )
    hypervisor_state.remember_instances_to_notify_about(
        owner=owner,
        instances=active_instances,
    )

def _is_before_evacuation_email_configured() -> bool:
    return (
        mediator.config.email.mail_send_enabled
        and not _no_letter_id_evacuate_before()
    )

def _is_owner_notifiable_before_evacuation(
    owner: interfaces.OwnerHint,
) -> bool:
    return (
        bool(owner.email)
        and bool(owner.vk_cs_project_id)
        and not (
            owner.is_partner
            and mediator.config.email.filter_partner_projects_enabled
        )
    )

@staticmethod
def _active_instances(
    instances: list[interfaces.NovaInstance],
) -> list[interfaces.NovaInstance]:
    return [
        instance
        for instance in instances
        if not _is_powered_off(instance)
    ]

def _emit_all_instances_powered_off(
    owner: interfaces.OwnerHint,
) -> None:
    mediator.event_listener.trigger(
        events.Email.NOT_SENDING_EMAIL,
        {
            'hostname': var.hostname,
            'event_set': var.event_set,
            'project_id': (
                f'{owner.project_id} ({owner.vk_cs_project_id})'
            ),
            'reason': 'all instances are powered off',
        },
    )

def _send_before_evacuation_notification(
    owner: interfaces.OwnerHint,
    instances: list[interfaces.NovaInstance],
    letter_id: str,
) -> None:
    template_data = _prepare_email_before(instances=instances)
    _send_email_with_debug(
        email_address=owner.email,
        letter_template_id=letter_id,
        template_label=owner.vk_cs_project_id,
        template_data=template_data,
        )



# Не стал тащить весь код (в тч некоторые фигурирующие методы), тк к сути задания это не имеет прямого отношения.
# Очень интересная метрика. И полезная - помогает быстро понять, где запутанно, ну и быстро распутать.
# Особенно нравится, что ее можно использовать в чужом коде, и она будет работать так же эффективно.
# А еще это формальный критерий запутанности кода, и на него можно ссылаться во время код ревью, когда коллега
# задает классический вопрос "а с чего ты взял, что это плохо?", на который трудно отвечать без формального
# чего-либо. В текущем коде не делал (специально, по крайней мере) ad-hoc полиморфизм, но идея интересная хотя бы потому,
# что позволяет удобно думать о проекте на высоком уровне абстракции, хоть и требует более тщательного
# подхода к проектированию с точки зрения состояний (или объектов в ООП) и того, что с ними можно и нельзя делать.
# Вероятно, эти состояния и правила перехода между ними как-то можно формально описать. Вероятно, с помощью функциональных
# штук и/или DSL. Впрочем, могу и ошибаться.