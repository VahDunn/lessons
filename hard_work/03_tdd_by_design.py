# Задача - ручка drop task по id
# Идея в том, чтобы свести выполнение юзкейса к некой линейной работе
# в ходе которой путем ряда проверок будут отсекаться все ситуации,
# кроме штатных. Штатная ситуация в итоге сводится к бинарному "получилось/не получилось".
# Параллельно с кодом небольшие комментарии о ходе рассуждения.

# Контроллер - написал его первым, поскольку он типовой и отражает требования к
# дизайну со стороны уже существующего сервиса + дает представления о верхнеслойном устройстве.
@router.delete(
    '/tasks/{task_id}',
    response_model=api_models.DropTaskResponse,
    responses={
        status.HTTP_200_OK: {'description': 'OK'},
        status.HTTP_404_NOT_FOUND: {'description': 'Task not found'},
    },
)
def drop_task(
    context: Annotated[PolicyContext, Depends(dep.get_context)],
    task_id: int,
    use_case: Annotated[
        use_cases.DropTaskUseCase,
        Depends(dep.drop_task_use_case),
    ],
    event_listener: Annotated[
        interfaces.EventListener,
        Depends(dep.get_event_listener),
    ],
) -> api_models.DropTaskResponse | JSONResponse:
    """Drop a single task by id."""
    try:
        result = use_case.execute(context, task_id)
    except exceptions.NotFoundError:
        return JSONResponse(
            {'error': f'Task with id {task_id} not found'},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    event_listener.trigger(
        events.API.DROP_TASK,
        {
            'task_id': task_id,
            'description': f'Dropped task {task_id}',
            'event_set': events.make_event_set_id(),
            'user': context.user_name,
        },
    )
    return api_models.DropTaskResponse.from_domain(result)
# после этого написал высокоуровневый тест
def test_api_drop_task(ec_api_client, headers):
    # arrange
    client = ec_api_client

    task_id = client.post('/evacuate/host1', headers=headers).json()['id']
    client.post('/evacuate/host2', headers=headers)

    # act
    with mock.patch.object(
        PolicyEnforce,
        'can_sync',
        autospec=True,
        side_effect=PolicyEnforce.can_sync,
    ) as can_sync:
        response = client.delete(f'/tasks/{task_id}', headers=headers)

    # assert
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {
        'id': task_id,
        'command': 'evacuate',
        'hostname': 'host1',
        'created_by': mock.ANY,
        'created_at': mock.ANY,
    }
    assert mock.call(mock.ANY, 'drop_task', mock.ANY) in can_sync.call_args_list

    assert client.event_listener.get_names() == [
        'MANUAL_EVACUATE',
        'MANUAL_EVACUATE',
        'DROP_TASK',
    ]

    response = client.get(f'/tasks/{task_id}/', headers=headers)
    assert response.status_code == http.HTTPStatus.NOT_FOUND

    response = client.get('/tasks', headers=headers)
    assert response.status_code == http.HTTPStatus.OK
    assert [task['hostname'] for task in response.json()] == ['host2']

# Идея в том, что в тесте закреплена основная работа ручки, и он тестирует ее целиком.
# Таким образом мы получаем "широкими мазками" рисунок планируемой функции в модальности "необходимость".
# Далее будем уточнять ее дизайн прицельно.
# Был соблазн начать с бизнес-логики, но я решил, что для корректного ответа на вопрос
# "как должна работать бизнес-логика" нужно ответить на вопрос "какие данные она может получить".

# Первый прицельный тест - проверка входных данных, а именно, task id. То есть фаззинг.
# На этом этапе выяснилось, что при пустом task_id происхходит редирект на общую ручку
# которая удаляет все таски. Принял решение оставить эту логику после обсуждения с лидом.
# Получается высокоуровневый переход в соседний сценарий (удалить все таски).
# Реализовал просто через pytest.

@pytest.mark.parametrize(
    ('raw_task_id', 'expected_status'),
    [
        pytest.param('abc', http.HTTPStatus.UNPROCESSABLE_ENTITY, id='non-numeric'),
        pytest.param('1.5', http.HTTPStatus.UNPROCESSABLE_ENTITY, id='float'),
        pytest.param(
            '1e10',
            http.HTTPStatus.UNPROCESSABLE_ENTITY,
            id='scientific-notation',
        ),
        pytest.param('true', http.HTTPStatus.UNPROCESSABLE_ENTITY, id='boolean-word'),
        pytest.param(
            '1;drop table tasks',
            http.HTTPStatus.UNPROCESSABLE_ENTITY,
            id='sql-injection-attempt',
        ),
        pytest.param('-1', http.HTTPStatus.NOT_FOUND, id='negative'),
        pytest.param('0', http.HTTPStatus.NOT_FOUND, id='zero'),
        pytest.param(
            '99999999999999999999999999999999',
            http.HTTPStatus.NOT_FOUND,
            id='huge-int',
        ),
        pytest.param(
            '../../etc/passwd',
            http.HTTPStatus.NOT_FOUND,
            id='path-traversal',
        ),
        pytest.param(
            '<script>alert(1)</script>',
            http.HTTPStatus.NOT_FOUND,
            id='xss-payload',
        ),
    ],
)
def test_api_drop_task_fuzz_garbage_ids(
    ec_api_client,
    headers,
    raw_task_id,
    expected_status,
):
    """Garbage task_id values must never crash or delete unrelated tasks."""
    # arrange
    client = ec_api_client
    survivor_id = client.post('/evacuate/host1', headers=headers).json()['id']

    # act
    response = client.delete(f'/tasks/{raw_task_id}', headers=headers)

    # assert
    assert response.status_code == expected_status

    survivor = client.get(f'/tasks/{survivor_id}/', headers=headers)
    assert survivor.status_code == http.HTTPStatus.OK


# После того, как данные, приходящие в контроллер и
# передаваемые в еще не реализованную бизнес логику
# проверены (педантик защищает :), можно закреплять поведение репозитория и политики

# Репозиторий
# Если бы не нжно было возвращать некоторые значения, можно было бы обойтись
# только методом drop task.
# Но наша версия БД не умеет DELETE RETURNING,  поэтому
# метод только удаляет, а значения полей и проверка на существование будет
# вынесена на уровень выше - в юзкейс.

# Метод get репозитория тестами покрыт. Тестирую drop.


def test_repo_drop_task_deletes_existing_task(
    ec_api_database,
    ec_api_client,
    api_reference_time,
):
    """Repository deletes the row by id and reports one row dropped."""
    # arrange
    with ec_api_database.get_engine().begin() as conn:
        conn.execute(
            sqlalchemy.insert(models.DbTask).values(
                event_id='event-1',
                hostname='host1',
                command='evacuate',
                status='created',
                created_by='admin',
                created_at=api_reference_time,
            ),
        )
        task_id = conn.execute(
            sqlalchemy.select(models.DbTask.id).where(
                models.DbTask.hostname == 'host1',
            ),
        ).scalar_one()

    # act
    with ec_api_database.get_engine().begin() as conn:
        result = ec_api_database.drop_task(conn, task_id)

    # assert
    assert result == 1

    with ec_api_database.get_engine().begin() as conn:
        remaining = conn.execute(
            sqlalchemy.select(models.DbTask).where(
                models.DbTask.id == task_id,
            ),
        ).fetchone()
    assert remaining is None


def test_repo_drop_task_noop_when_missing(
    ec_api_database,
    ec_api_client,
    api_reference_time,
):
    """Repository still reports success for an already-absent id."""
    # arrange
    with ec_api_database.get_engine().begin() as conn:
        conn.execute(
            sqlalchemy.insert(models.DbTask).values(
                event_id='event-1',
                hostname='host1',
                command='evacuate',
                status='created',
                created_by='admin',
                created_at=api_reference_time,
            ),
        )

    # act
    with ec_api_database.get_engine().begin() as conn:
        result = ec_api_database.drop_task(conn, 999999)

    # assert
    assert result == 1

    with ec_api_database.get_engine().begin() as conn:
        remaining = (
            conn.execute(sqlalchemy.select(models.DbTask.hostname))
            .scalars()
            .all()
        )
    assert remaining == ['host1']


def test_repo_drop_task_propagates_unexpected_errors():
    """Errors from the delete statement are not swallowed."""
    # arrange
    conn = mock.MagicMock()
    conn.execute.side_effect = sqlalchemy.exc.OperationalError(
        'DELETE FROM tasks WHERE id = ?',
        (1,),
        Exception('connection lost'),
    )

    # act / assert
    with pytest.raises(sqlalchemy.exc.OperationalError):
        APIDatabaseHelper.drop_task(conn, 1)

# Сам метод.
@staticmethod
def drop_task(
        conn: Connection,
        task_id: int,
) -> bool:
    """Delete task by id.

    Returns 1 whether or not a matching row existed, since the desired
    end state (no such row) is reached either way. Unexpected DB errors
    are not caught here and propagate to the caller.
    """
    conn.execute(
        sqlalchemy.delete(models.DbTask).where(
            models.DbTask.id == task_id
        )
    )
    return True

# Таким образом закреплено поведение - удаляем, если есть, если нет - ничего не делаем.
# В обоих случаях считаем отработку успевшной, ошибки прокидываются.
# 2 варианта отработки - успех и ошибка (если база данных ругнулась).

# Тестирование сервиса политики (а точнее, библиотеки) также было проведено ранее.
# У него зафиксировано 2 исхода отрабатывания - can/can not.

# Можно переходить к написанию тестов для бизнес-логики.
# Сначала 2 ранних выхода. 1 - политика не позволяет.
def test_drop_task_use_case_policy_denied(use_case, policy, database):
    """Policy rejects the action: task is not touched."""
    # arrange
    context = mock.Mock()
    policy.can_sync.side_effect = policy_exceptions.PolicyNotAuthorizedError(
        action='drop_task',
    )

    # act / assert
    with pytest.raises(policy_exceptions.PolicyNotAuthorizedError):
        use_case.execute(context, task_id=1)

    policy.can_sync.assert_called_once_with('drop_task', context)
    database.get_task_status.assert_not_called()
    database.drop_task.assert_not_called()

# 2 - таски с данным id нет в базе.
def test_drop_task_use_case_task_not_found(use_case, policy, database):
    """Task does not exist: repository error is propagated, nothing dropped."""
    # arrange
    context = mock.Mock()
    database.get_task_status.side_effect = exceptions.NotFoundError(
        'Not found task with id 1.',
    )

    # act / assert
    with pytest.raises(exceptions.NotFoundError):
        use_case.execute(context, task_id=1)

    policy.can_sync.assert_called_once_with('drop_task', context)
    database.drop_task.assert_not_called()

# Если в самом конце репозиторий вернул ошибку, это не ранний выход и не штатная ситуация.
def test_drop_task_use_case_repository_error_propagates(
    use_case,
    policy,
    database,
):
    """Unexpected repository errors are not swallowed by the use case."""
    # arrange
    context = mock.Mock()
    task = TaskDomainModel(
        id=1,
        status='created',
        hostname='host1',
        command='evacuate',
        created_at='2026-01-01 00:00:00+00:00',
        created_by='admin',
        event_id='event-1',
    )
    database.get_task_status.return_value = task
    database.drop_task.side_effect = sqlalchemy.exc.OperationalError(
        'DELETE FROM tasks WHERE id = ?',
        (1,),
        Exception('connection lost'),
    )
    with pytest.raises(sqlalchemy.exc.OperationalError):
        use_case.execute(context, task_id=1)

    policy.can_sync.assert_called_once_with('drop_task', context)
    database.get_task_status.assert_called_once()
    database.drop_task.assert_called_once()

# Остальное тестирование сводится к варианту, когда все ок, то есть, вызов репо и корректная отработка
def test_drop_task_use_case_ok(use_case, policy, database):
    """Task exists and policy allows the action: task is dropped."""
    # arrange
    context = mock.Mock()
    task = TaskDomainModel(
        id=1,
        status='created',
        hostname='host1',
        command='evacuate',
        created_at='2026-01-01 00:00:00+00:00',
        created_by='admin',
        event_id='event-1',
    )
    conn = database.get_engine.return_value.begin.return_value.__enter__.return_value
    database.get_task_status.return_value = task
    database.drop_task.return_value = 1

    # act
    result = use_case.execute(context, task_id=1)

    # assert
    assert result == task
    policy.can_sync.assert_called_once_with('drop_task', context)
    database.get_task_status.assert_called_once_with(conn, 1)
    database.drop_task.assert_called_once_with(conn, 1)

# В конце написал высокоуровневый параметризованный тест с проверкой статусов и
# эвентов в случаях ошибок. Круг замкнулся :)

@pytest.mark.parametrize(
    ('side_effect', 'expected_status', 'expected_events'),
    [
        pytest.param(
            policy_exceptions.PolicyNotAuthorizedError(action='drop_task'),
            http.HTTPStatus.INTERNAL_SERVER_ERROR,
            ['API_EXCEPTION'],
            id='policy-denied',
        ),
        pytest.param(
            exceptions.NotFoundError('Not found task with id 1.'),
            http.HTTPStatus.NOT_FOUND,
            [],
            id='task-not-found',
        ),
        pytest.param(
            sqlalchemy.exc.OperationalError(
                'DELETE FROM tasks WHERE id = ?',
                (1,),
                Exception('connection lost'),
            ),
            http.HTTPStatus.INTERNAL_SERVER_ERROR,
            ['API_EXCEPTION'],
            id='repository-error',
        ),
    ],
)
def test_api_drop_task_controller_use_case_failures(
    ec_api_silent_client,
    event_listener,
    headers,
    side_effect,
    expected_status,
    expected_events,
):
    """Controller reacts correctly no matter why the use case failed.

    A denied policy and an unexpected repository error both fall through
    to the generic exception handler (API_EXCEPTION, 500); only a missing
    task is handled locally by the controller (404, no event at all).
    """
    # arrange
    client = ec_api_silent_client
    fake_use_case = mock.Mock()
    fake_use_case.execute.side_effect = side_effect
    client.app.dependency_overrides[dep.drop_task_use_case] = (
        lambda: fake_use_case
    )

    # act
    with mock.patch('evacuation_controller.api.app.dep') as fake_dep:
        fake_dep.get_config.return_value = mock.Mock()
        fake_dep.get_event_listener.return_value = event_listener
        response = client.delete('/tasks/1', headers=headers)

    # assert
    assert response.status_code == expected_status
    assert event_listener.get_names() == expected_events


# Таким образом, получаем один счастливый тест, когда все компоненты выполняют то, что должны,
# он носит скорее общеописательный характер.
# Ряд тестов, закрепляющих варианты работы отдельных компонентов и бизнес-логики.
# И итоговый тест, проверяющий собранные и закрепленные ранее варианты с ошибками.


# Рефлексия
# Очень сильно впечатлило это задание. Нравится так работать. Да, это дольше (пока что), но зато я
# почти с полной уверенностью могу говорить, что код, который я отдаю, работает как надо, и
# я готов за него отвечать.