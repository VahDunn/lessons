# 7 неочевидных проектных ошибок: 2, 3, 4, 5 и 7.


# 1. Функция, отдающая отчет при обращении к ней. Если отчет не находится, функция пытается его создать.
# Все это с кучей фолбеков и бесструктурным "переиспользованием" общей логики.
# Стоит ли говорить, какое количество багов это генерировало. Причем даже после разделения
# на отдельные сквозные сценарии оставалась высокая их связность.
#
# Было

async def get_or_create(report: ReportProtocol, as_pictures=False, clear_cache=False):
    await report.load()  # подгружает отчет в формате json
    storages = []
    return_dictionary = {}
    pdf_storage = ReportStorageDescriptor(report)
    if report.report_xml() is not None:
        xml_storage = ReportStorageDescriptor(report, 'xml')
        storages.append(xml_storage)
    else:
        return_dictionary.update({'xml_hash': None})
    storages.append(pdf_storage)
    if len(storages) < 1:
        return
    for storage in storages:
        if len(storage.signatures) > 0:
            await create_ready_for_sign(storage, report)
        # noinspection PyUnusedLocal
        unsigned_result = None
        file_path = storage.file_path()
        file_exists = False if Config.no_file_cache or clear_cache else os.path.exists(file_path)

        if storage.file_type == 'pdf':
            if not file_exists:
                await report.save(file_path, False)
            else:
                existing_doc = None
                try:
                    existing_doc = Document(file_path)
                    doc_modification_date = string_to_date(existing_doc.metadata['subject'])
                    created_version = existing_doc.metadata['author']
                    if (doc_modification_date < storage.modification_date
                        or doc_modification_date == datetime.min
                        or storage.modification_date == datetime.max
                        or created_version != Config.version
                    ):
                        await report.save(file_path, False)
                finally:
                    if existing_doc:
                        existing_doc.close()

        log(f'should return signed: {storage.should_return_signed}')
        if storage.should_return_signed:
            signed_dict = await get_or_create_signed(storage, report)
            log(f'...created: {signed_dict}')
            if signed_dict:
                return_dictionary.update(signed_dict)
            log(f'updated: {return_dictionary}')
        else:
            doc = Document(file_path) if storage.file_type == 'pdf' else None
            try:
                temp_dict = create_return_dictionary(storage, doc, as_pictures)
                if temp_dict:
                    return_dictionary.update(temp_dict)
            # если подписывать не надо, возвращается словарь с хэшем
            finally:
                if doc is not None:
                    doc.close()
        log(f'...processing storage: {storage.file_type} done')

    return return_dictionary

# В общем, ничего хорошего, как с точки зрения архитектуры, так и с точки зрения стила кодирования.

# Стало - раздельные методы с четким ветвлением, create signed и create unsigned выбираются проверкой в общем
#  методе create.
async def get_report(
    self,
    report: ReportProtocol,
    as_pictures: bool = False,
    refresh: bool = False,
) -> ReportResponse:
    return_dictionary: ReportResponse = {}
    loading_error = await report.load()
    if loading_error:
        raise UpstreamServiceError(
            "report_load_failed", "Failed to load report data"
        )

    pdf_storage = ReportStorageDescriptor(report)
    storages = [pdf_storage]
    signed_pdf_exists = os.path.exists(pdf_storage.signed_file_path())
    if signed_pdf_exists and report.report_xml():
        storages.append(ReportStorageDescriptor(report, "xml"))

    if len(storages) < 1:
        raise ServiceOperationError(
            "storage_descriptor_not_found",
            "No storage descriptors found for this report",
        )

    if len(storages) == 1:
        return_dictionary.update({"xml_hash": None})

    for storage in storages:
        report_is_signed = self.response_builder.check_if_signed(storage)
        if report_is_signed:
            pages_count = await self.file_service.ensure_signed_report(
                storage, as_pictures
            )
            res = self.response_builder.create_return_dictionary(
                storage,
                pages_count,
                signed=True,
            )
        else:
            pages_count = await self.file_service.ensure_unsigned_report(
                report, storage, as_pictures, refresh
            )
            res = self.response_builder.create_return_dictionary(
                storage, pages_count
            )
        return_dictionary.update(res)

    return return_dictionary


async def create_unsigned_report(
    self,
    report: ReportProtocol,
    storage: ReportStorageDescriptor,
    as_pictures: bool = False,
) -> int | None:
    try:
        await report.save(storage.file_path(), False, storage.file_type)
    except XmlReportGenerationError as e:
        error_message = str(e)
        raise ReportFileGenerationError(error_message)
    except Exception:
        raise
    pages_count = None
    if storage.file_type == "pdf":
        pages_count = await self.count_pages_and_create_pictures_if_required(
            storage, as_pictures
        )
    return pages_count

async def create_signed_report(
    self,
    storage: ReportStorageDescriptor,
    report: ReportProtocol,
    as_pictures: bool = False,
) -> None:
    any_sig_exist = any(
        [signature.exists(storage.file_type) for signature in storage.signatures]
    )
    signed_report_exist = os.path.exists(storage.signed_file_path())
    if any_sig_exist and signed_report_exist:
        return
    try:
        report_error = await report.save(
            storage.signed_file_path(), True, storage.file_type
        )
    except XmlReportGenerationError as e:
        error_message = str(e)
        raise ReportFileGenerationError(error_message)
    except Exception:
        raise

    if report_error:
        raise ReportFileGenerationError(str(report_error))

    if storage.file_type == "pdf":
        await self.count_pages_and_create_pictures_if_required(
            storage, as_pictures, signed=True
        )


# 2. Большая функция отправки разделена на классы с разными обязанностями.
#
# Назначение: взять готовое сообщение из очереди, получить исходные данные
# и подписанный документ, сформировать запрос регистрации, отправить его
# и сохранить состояние для последующего callback.
#
# Было
async def run(report_type: str = 'egisz.permit', code: str = ''):
    app_name = 'egisz.' + report_type
    logger = logging.getLogger(app_name)

    try:
        with pidfile.PIDFile(f"/var/run/{app_name}.service.pid"):
            for connection in Config.connection_strings:
                client = MongoClient(connection)
                database = client['exchange']
                outbox = database[f'{app_name}.outbox']
                sent = database[f'{app_name}.sent']
                callback = database['egisz.callback.status']
                with_error = database[f'{app_name}.errors']

                data = list(outbox.find({
                    "ready_to_send": {"$ne": False},
                }).sort([("_id", -1)]))
                host = client.address[0] if client.address and len(client.address) > 0 else 'unknown'

                sleep_time = 0

                for message in data:
                    message_id = message.get('uuid', 'unknown')
                    try:
                        signed_id = str(message.get('signed_id', ''))
                        ht_protocol = 'https' if host in https_hosts else 'http'
                        json_url = f'{ht_protocol}://{host}/reports/umo/{report_type}-json/{signed_id}'
                        permit_json = await download_json(json_url, host, ht_protocol)

# Ещё один участок той же функции сборщик XML получает в числе аргументов
# коллекцию outbox. Формирование внешнего документа связано с очередью БД.
# Между этими выдержками находятся проверки пациента, подписи и типа документа.
                        xml_body, body_error = create_register_request_body(
                            document_type, document_type_oid, permit_json,
                            message_id, signed_id, host, ht_protocol, outbox, logger
                        )
                        if not xml_body:
                            save_error(message, f'failed to create body: {body_error}', outbox)
                            continue
                        xml_envelope = create_envelope_as_string(xml_body, message_id, 'registerDocument', False)
                        request_response = await send_request(xml_envelope, logger, sleep_time, message, outbox, message_id)

                        time.sleep(sleep_time)

# Стало

async def _handle_instance(self, mias_instance, logger) -> None:
    mias_api: MiasApi = mias_instance.get_api()
    if not mias_api:
        return

    exchange: MiasExchangeApp = mias_instance.get_exchange().for_app_and_type(
        self.app_prefix, self.report_type
    )
    messages: List[MiasMessage] = exchange.list_ready_to_send()

    for message in messages:
        try:
            await self._process_message(message, mias_api, exchange, logger)
        except NotSendingError as e:
            exchange.remove_from_outbox(message, str(e))
        except Exception as e:
            pass  # В исходнике здесь был только лог.

# Обработка одного сообщения связывает готовые части:
# MiasApi получает JSON и файлы, ReportJsonData разбирает данные,
# XmlMessageBuilder строит запрос, сендер делает, собственно, отправку.
async def _process_message(
    self,
    message: MiasMessage,
    mias_api: MiasApi,
    exchange: MiasExchangeApp,
    logger,
    type_data
):
    report_path = self._resolve_report_path(message.signed_id)
    report_json = await mias_api.download_json(report_path, logger)
    parsed: ReportJsonData = ReportJsonData.parse(report_json, self.report_type)
    if isinstance(parsed, ParseFail):
        raise NotSendingError(parsed.message)
    json_data = parsed
    fetched_report_info: PdfXmlInfo = await mias_api.fetch_report(message.signed_id, self.report_type, logger)
    sig_file_path = self._validate_fetched_and_get_sig_path(fetched_report_info)
    xml_body = self.xml_builder.create_register_request_body(
        type_data=type_data,
        message=message,
        json_data=json_data,
        sig_file_path=sig_file_path,
    )
    xml_envelope = self.xml_builder.create_envelope_as_string(xml_body, message.uuid, 'registerDocument', False)
    message.clinic = json_data.clinic # TODO переделать так, чтобы не было этой зависимости (используется в save_callback)
    response = requests.post(
        self.config.remd_proxy_url, xml_envelope.encode('utf-8'),
        headers={'Content-Type': 'text/xml; charset=utf-8'}
    )
    await self._process_response(response, message, exchange, message.uuid)
    time.sleep(self.sleep_time)

# Данные между этапами представлены отдельной структурой ReportJsonData.
@dataclass(frozen=True)
class ReportJsonData:
    report_json: Dict[str, Any]
    person: Dict[str, Any]
    person_id: str
    snils: Optional[str]
    clinic: Dict[str, Any]
    sig: Dict[str, Any]
    signed_at: str
    doctor_id: str
    meta: Dict[str, Any]

# На границе XmlMessageBuilder уже нет никаких внешних обращений, передаются уже собранные данные.
    def create_register_request_body(
        self,
        type_data: ReportType,
        message: MiasMessage,
        json_data: ReportJsonData,
        sig_file_path: str,
    ):
        report_type_oid = type_data['oid']

# Детали переноса сообщения между Mongo-коллекциями находятся в MiasExchangeApp.
    def mark_as_sent(self, message: MiasMessage):
        self._get_outbox().delete_one({'_id': message.data.get('_id')})
        message.data['error'] = None
        message.data['uuid'] = message.uuid
        self._get_sent().insert_one(message.data)


# 3. Общий каталог вместо трёх независимых таблиц соответствий типов отчета.
# Было — три записи одного и того же типа отчёта.
    RouteDescriptor('/team-umo', ConsolidatedReportTeam),

    '102': ConsolidatedReportTeam,

    'team': ConsolidatedReportTeam,

# Стало — запись ReportCatalogItem связывает все обозначения с фабрикой отчёта.
@dataclass(frozen=True)
class ReportCatalogItem:
    route: str
    report: ReportFactory
    is_lab_special: bool = False
    detect_codes: tuple[str, ...] = ()
    group_sign_key: str | None = None

    ReportCatalogItem(
        "/team-umo",
        ConsolidatedReportTeam,
        detect_codes=("102",),
        group_sign_key="team",
    ),

# Маршруты и индексы вычисляются из каталога, а не поддерживаются независимо.
REPORT_ROUTES = list(REPORT_CATALOG)
DETECT_LOSS_REPORTS_BY_CODE: dict[str, ReportFactory] = {
    code: item.report for item in REPORT_CATALOG for code in item.detect_codes
}
GROUP_SIGN_REPORTS_BY_KEY: dict[str, ReportFactory] = {
    item.group_sign_key: item.report
    for item in REPORT_CATALOG
    if item.group_sign_key is not None
}


def get_report_by_detect_code(code: str) -> ReportFactory | None:
    return DETECT_LOSS_REPORTS_BY_CODE.get(code)


def get_group_sign_report_loaders() -> dict[str, ReportFactory]:
    return GROUP_SIGN_REPORTS_BY_KEY.copy()


# Рефлексия.
#
# Получился отличный повод посмотреть на собственный рефакторинг более формально. Теперь
# замечаю некоторые очевидные недочеты, например, протекания слоев или дублирование кода.
# Все же без формальной подготовки такое замечаешь хуже и скорее интуитивно, что, на мой взгляд, скорее
# плохо, чем хорошо. В первую очередь из-за низкой эффективности и периодическим упусканием деталей
# из-за того, что знания о том, как и почему надо делать определенным образом, не структурированы.
# С сформированными навыками и теоретической базой работается и быстрее, и приятнее, и эффективнее
# по энергозатратам. Требуется дальнейшая практика, как раз рефакторинг намечается.
