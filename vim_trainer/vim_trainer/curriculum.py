from __future__ import annotations

from textwrap import dedent

from vim_trainer.domain.course import Course
from vim_trainer.domain.entities import (
    Cursor,
    Lesson,
    PracticeFile,
    RegisterExpectation,
)


def _text(source: str) -> str:
    """Normalize embedded practice files and keep their final newline."""
    value = dedent(source).lstrip("\n")
    return value if value.endswith("\n") else f"{value}\n"


def _file(path: str, initial: str, expected: str) -> PracticeFile:
    return PracticeFile(
        path=path,
        initial=_text(initial),
        expected=_text(expected),
    )


DEFAULT_COURSE = Course(
    lessons=(
        Lesson(
            id="00-navigation-warmup",
            chapter="Основы",
            title="Разминка: навигация",
            goal="Двигать курсор по тексту, не меняя его.",
            task=(
                "Vim уже открыт в Normal mode; ничего не печатай.",
                "От S нажми l четыре раза, j два раза, h два раза и k один раз.",
                "Остановись на X и заверши упражнение через :wqa.",
            ),
            commands=("h — влево", "j — вниз", "k — вверх", "l — вправо"),
            hint="Если сбился, найди S и начни маршрут заново.",
            files=(
                _file(
                    "navigation.txt",
                    """
                    ..........
                    .S........
                    ...X......
                    ..........
                    """,
                    """
                    ..........
                    .S........
                    ...X......
                    ..........
                    """,
                ),
            ),
            entrypoint="navigation.txt",
            start_cursor=Cursor(2, 2),
            expected_cursor=Cursor(3, 4),
        ),
        Lesson(
            id="01-modes",
            chapter="Основы",
            title="Normal и Insert",
            goal="Переключаться между вводом и командами без мыши.",
            task=(
                "Вставь ready между кавычками первой строки.",
                "Вернись в Normal, перейди ниже и допиши 3 после пробела.",
            ),
            commands=("i — ввод перед курсором", "A — ввод в конце строки", "Esc — Normal"),
            hint="После каждого фрагмента текста нажимай Esc.",
            files=(
                _file(
                    "modes.txt",
                    """
                    status = ""
                    count =
                    """,
                    """
                    status = "ready"
                    count = 3
                    """,
                ),
            ),
            entrypoint="modes.txt",
            start_cursor=Cursor(1, 11),
        ),
        Lesson(
            id="02-command-line",
            chapter="Основы",
            title="Ex-команды и справка",
            goal="Вызывать справку, сохранять файл и закрывать окна.",
            task=(
                "Открой :help :write и закрой окно справки через :q.",
                "Вставь ready между кавычками и сохрани отдельной командой :w.",
                "Заверши урок обычной для тренажёра командой :wqa.",
            ),
            commands=(":help {topic} — справка", ":w — записать", ":q/:q! — выйти"),
            hint="Двоеточие открывает командную строку; Enter выполняет команду.",
            files=(
                _file(
                    "commands.txt",
                    'status = ""',
                    'status = "ready"',
                ),
            ),
            entrypoint="commands.txt",
            start_cursor=Cursor(1, 11),
        ),
        Lesson(
            id="03-hjkl",
            chapter="Основы",
            title="Навигация hjkl",
            goal="Двигаться по тексту клавишами домашнего ряда.",
            task=("Не меняя файл, поставь курсор на c в слове center.",),
            commands=("h ←", "j ↓", "k ↑", "l →"),
            hint="Цель: строка 4, колонка 7.",
            files=(
                _file(
                    "grid.txt",
                    """
                    one two three
                    alpha beta gamma
                    red green blue
                    north center south
                    """,
                    """
                    one two three
                    alpha beta gamma
                    red green blue
                    north center south
                    """,
                ),
            ),
            entrypoint="grid.txt",
            expected_cursor=Cursor(4, 7),
        ),
        Lesson(
            id="04-words",
            chapter="Основы",
            title="Переходы по словам",
            goal="Перемещаться по словам крупными шагами.",
            task=("Не меняя файл, остановись на последней букве слова finish.",),
            commands=("w — следующее слово", "b — предыдущее слово", "e — конец слова"),
            hint="Сначала спустись на третью строку, затем используй w и e.",
            files=(
                _file(
                    "words.txt",
                    """
                    alpha beta gamma
                    delta epsilon zeta
                    target finish here
                    """,
                    """
                    alpha beta gamma
                    delta epsilon zeta
                    target finish here
                    """,
                ),
            ),
            entrypoint="words.txt",
            expected_cursor=Cursor(3, 13),
        ),
        Lesson(
            id="05-lines",
            chapter="Основы",
            title="Начало и конец строки",
            goal="Быстро выбирать опорные позиции строки.",
            task=(
                "Проверь разницу между 0 и ^ на строках с отступом.",
                "Остановись на последнем символе третьей строки.",
            ),
            commands=("0 — колонка 1", "^ — первый непробельный символ", "$ — конец строки"),
            hint="На третьей строке достаточно нажать $.",
            files=(
                _file(
                    "lines.py",
                    """
                        first = 1
                          second = 2
                    final_value = first + second
                    """,
                    """
                        first = 1
                          second = 2
                    final_value = first + second
                    """,
                ),
            ),
            entrypoint="lines.py",
            expected_cursor=Cursor(3, 28),
        ),
        Lesson(
            id="06-find-char",
            chapter="Основы",
            title="Поиск символа в строке",
            goal="Прыгать к нужному символу без серии l.",
            task=("Не меняя строку, остановись на третьем символе |.",),
            commands=("f{char} — на символ", "t{char} — перед символом", "; — повтор", ", — назад"),
            hint="Нажми f|, затем дважды ;.",
            files=(
                _file(
                    "pipeline.txt",
                    "request | parse | validate | persist | done",
                    "request | parse | validate | persist | done",
                ),
            ),
            entrypoint="pipeline.txt",
            expected_cursor=Cursor(1, 28),
        ),
        Lesson(
            id="07-file-jumps",
            chapter="Основы",
            title="Прыжки по файлу",
            goal="Переходить к краям и заданной строке.",
            task=(
                "Перейди в конец через G и вернись через gg.",
                "Остановись в начале строки 9.",
            ),
            commands=("gg — первая строка", "G — последняя строка", "{n}G — строка n"),
            hint="Финальная команда: 9G.",
            files=(
                _file(
                    "long.txt",
                    """
                    line 01
                    line 02
                    line 03
                    line 04
                    line 05
                    line 06
                    line 07
                    line 08
                    line 09
                    line 10
                    line 11
                    line 12
                    """,
                    """
                    line 01
                    line 02
                    line 03
                    line 04
                    line 05
                    line 06
                    line 07
                    line 08
                    line 09
                    line 10
                    line 11
                    line 12
                    """,
                ),
            ),
            entrypoint="long.txt",
            expected_cursor=Cursor(9, 1),
        ),
        Lesson(
            id="08-advanced-motion",
            chapter="Основы",
            title="Парные скобки и возврат",
            goal="Прыгать к парному ограничителю и возвращаться по истории позиций.",
            task=(
                "На открывающей скобке нажми %, чтобы перейти к закрывающей.",
                "Вернись к открывающей через Ctrl-o и снова вперёд через Ctrl-i.",
                "Заверши на закрывающей скобке в начале четвёртой строки.",
            ),
            commands=(
                "% — парная скобка",
                "Ctrl-o — предыдущая позиция",
                "Ctrl-i — следующая позиция",
            ),
            hint="Межстрочный переход через % попадает в список прыжков.",
            files=(
                _file(
                    "jumps.txt",
                    """
                    start = (
                        "alpha",
                        "beta",
                    )
                    tail = "keep"
                    """,
                    """
                    start = (
                        "alpha",
                        "beta",
                    )
                    tail = "keep"
                    """,
                ),
            ),
            entrypoint="jumps.txt",
            start_cursor=Cursor(1, 9),
            expected_cursor=Cursor(4, 1),
        ),
        Lesson(
            id="09-insert-variants",
            chapter="Основы",
            title="Точки входа в Insert",
            goal="Начинать ввод ровно там, где он нужен.",
            task=(
                "Добавь сверху комментарий # totals.",
                "Дополни выражение на + 1 и вставь print(value) перед return.",
            ),
            commands=(
                "i/a — до/после курсора",
                "I/A — начало/конец строки",
                "o/O — строка ниже/выше",
            ),
            hint="Для трёх правок удобны O, A и o.",
            files=(
                _file(
                    "total.py",
                    """
                    def total(items):
                        value = sum(items)
                        return value
                    """,
                    """
                    # totals
                    def total(items):
                        value = sum(items) + 1
                        print(value)
                        return value
                    """,
                ),
            ),
            entrypoint="total.py",
            start_cursor=Cursor(2, 5),
        ),
        Lesson(
            id="10-small-edits",
            chapter="Редактирование",
            title="Мелкие правки и undo",
            goal="Исправлять символы и уверенно откатывать изменения.",
            task=(
                "Удали символ под курсором через x, нажми u, Ctrl-r и снова u.",
                "Преврати debaag в debug с помощью r и x.",
                "Удали пустую строку и собери print(message) через gJ.",
            ),
            commands=(
                "x — удалить символ",
                "r{char} — заменить символ",
                "u / Ctrl-r — undo / redo",
                "J/gJ — соединить строки",
            ),
            hint="gJ соединяет без добавочного пробела; u откатывает одну правку.",
            files=(
                _file(
                    "small_edits.py",
                    """
                    level = "debaag"
                    message = "ready"

                    print(
                    message)
                    """,
                    """
                    level = "debug"
                    message = "ready"
                    print(message)
                    """,
                ),
            ),
            entrypoint="small_edits.py",
            start_cursor=Cursor(1, 10),
        ),
        Lesson(
            id="11-delete-operator",
            chapter="Редактирование",
            title="Оператор удаления",
            goal="Комбинировать d с движением.",
            task=(
                "Удали DEBUG и хвост trailing из первой строки.",
                "Удали beta, всю третью строку и old_value в последней.",
            ),
            commands=(
                "dw — слово",
                "d$ — до конца",
                "dd — строка",
                "d{motion} — диапазон движения",
            ),
            hint="Для trailing и old_value начни d$ на пробеле слева.",
            files=(
                _file(
                    "delete.txt",
                    """
                    DEBUG request accepted trailing
                    keep: alpha beta gamma
                    remove this entire line
                    result = old_value
                    """,
                    """
                    request accepted
                    keep: alpha gamma
                    result =
                    """,
                ),
            ),
            entrypoint="delete.txt",
        ),
        Lesson(
            id="12-counts",
            chapter="Редактирование",
            title="Счётчики команд",
            goal="Сворачивать повторения в одну команду.",
            task=(
                "Удали три noise одной командой.",
                "Оставь во второй строке zero one five и удали три drop-строки.",
            ),
            commands=("3dw — три слова", "3dd — три строки", "{count}{operator}{motion}"),
            hint="Счётчик можно ставить перед оператором или движением.",
            files=(
                _file(
                    "counts.txt",
                    """
                    noise noise noise payload
                    zero one two three four five
                    drop-a
                    drop-b
                    drop-c
                    keep
                    """,
                    """
                    payload
                    zero one five
                    keep
                    """,
                ),
            ),
            entrypoint="counts.txt",
        ),
        Lesson(
            id="13-yank-put",
            chapter="Редактирование",
            title="Yank и put",
            goal="Копировать строки и объекты без системного буфера обмена.",
            task=(
                "Скопируй template() через yy и вставь перед destination: через P.",
                "Скопируй beta через yiw и вставь после selected = через p.",
            ),
            commands=("yy — строка", "yiw — слово", "p/P — после/до курсора"),
            hint="Перед вторым p добавь после знака = один пробел.",
            files=(
                _file(
                    "yank.txt",
                    """
                    template()
                    alpha
                    beta
                    destination:
                    selected =
                    """,
                    """
                    template()
                    alpha
                    beta
                    template()
                    destination:
                    selected = beta
                    """,
                ),
            ),
            entrypoint="yank.txt",
        ),
        Lesson(
            id="14-change-operator",
            chapter="Редактирование",
            title="Оператор изменения",
            goal="Удалять диапазон и сразу вводить замену.",
            task=(
                "Замени слово temporary на mira.",
                "Замени 999 на 30 и development на production.",
            ),
            commands=("cw — изменить слово", "c$ — изменить до конца", 'ci" — внутри кавычек'),
            hint="После ввода каждой замены возвращайся через Esc.",
            files=(
                _file(
                    "settings.py",
                    """
                    user_name = "temporary"
                    timeout_seconds = 999
                    mode = development
                    """,
                    """
                    user_name = "mira"
                    timeout_seconds = 30
                    mode = production
                    """,
                ),
            ),
            entrypoint="settings.py",
            start_cursor=Cursor(1, 14),
        ),
        Lesson(
            id="15-inner-objects",
            chapter="Редактирование",
            title="Внутренние text objects",
            goal="Править содержимое структур без ручного выделения.",
            task=(
                "Замени текст в кавычках на compact.",
                "Замени кортеж повторов на (5, 8), а список — на [ready].",
            ),
            commands=('ci" — внутри кавычек', "ci( — внутри скобок", "ci[ — внутри списка"),
            hint="Поставь курсор внутрь нужной пары ограничителей.",
            files=(
                _file(
                    "objects.py",
                    """
                    send("obsolete payload", retries=(1, 2, 3))
                    config = [alpha, beta, gamma]
                    """,
                    """
                    send("compact", retries=(5, 8))
                    config = [ready]
                    """,
                ),
            ),
            entrypoint="objects.py",
        ),
        Lesson(
            id="16-around-objects",
            chapter="Редактирование",
            title="Внутри и вокруг объекта",
            goal="Осознанно включать границы объекта в действие.",
            task=(
                "Удали [debug_value] вместе со скобками.",
                "Замени аргумент wrap с old_value на new_value.",
                "Удали слово beta вместе с соседним пробелом.",
            ),
            commands=("diw/daw — слово", "ci( — внутри скобок", "da[ — вместе со скобками"),
            hint="i оставляет границы, a включает их.",
            files=(
                _file(
                    "around.py",
                    """
                    log([debug_value])
                    result = wrap(old_value)
                    words = alpha beta gamma
                    """,
                    """
                    log()
                    result = wrap(new_value)
                    words = alpha gamma
                    """,
                ),
            ),
            entrypoint="around.py",
        ),
        Lesson(
            id="17-formatting",
            chapter="Редактирование",
            title="Отступы и форматирование",
            goal="Сдвигать строки операторами и выравнивать блоки.",
            task=(
                "На строке value выполни >> и отмени через u.",
                "На строке return выполни << и тоже отмени.",
                "Отформатируй весь файл командой gg=G.",
            ),
            commands=(">>/<< — сдвиг строки", "u — отмена", "=ip/gg=G — автоотступ"),
            hint="Оператор = использует правила отступов для типа файла.",
            files=(
                _file(
                    "formatting.c",
                    """
                    int build(void) {
                    int value = 1;
                    if (value) {
                                return value;
                    }
                    }
                    """,
                    """
                    int build(void) {
                        int value = 1;
                        if (value) {
                            return value;
                        }
                    }
                    """,
                ),
            ),
            entrypoint="formatting.c",
        ),
        Lesson(
            id="18-dot",
            chapter="Редактирование",
            title="Повтор через точку",
            goal="Повторять последнее изменение без записи команды заново.",
            task=(
                "На первой строке замени red на ripe через cw.",
                "Повтори изменение на трёх строках клавишей .",
            ),
            commands=(". — повтор последнего изменения", "j0 — следующая строка"),
            hint="После первой правки используй j0. ещё три раза.",
            files=(
                _file(
                    "repeat.txt",
                    """
                    red apple
                    red berry
                    red cherry
                    red date
                    """,
                    """
                    ripe apple
                    ripe berry
                    ripe cherry
                    ripe date
                    """,
                ),
            ),
            entrypoint="repeat.txt",
        ),
        Lesson(
            id="19-search",
            chapter="Поиск и замены",
            title="Поиск по файлу",
            goal="Искать и обходить совпадения в обе стороны.",
            task=(
                "Найди state и пройди его совпадения через n и N.",
                "Затем найди target и оставь курсор на нём.",
            ),
            commands=(
                "/pattern Enter — поиск",
                "n — дальше",
                "N — назад",
                "* — слово под курсором",
            ),
            hint="Последний запрос должен быть /target.",
            files=(
                _file(
                    "search.py",
                    """
                    state = "idle"
                    cache = {}
                    state = "warming"
                    cache["key"] = 1
                    state = "ready"
                    target = cache["key"]
                    """,
                    """
                    state = "idle"
                    cache = {}
                    state = "warming"
                    cache["key"] = 1
                    state = "ready"
                    target = cache["key"]
                    """,
                ),
            ),
            entrypoint="search.py",
            expected_cursor=Cursor(6, 1),
        ),
        Lesson(
            id="20-substitute",
            chapter="Поиск и замены",
            title="Точная замена",
            goal="Заменять только полные слова во всём файле.",
            task=("Замени слово colour на color везде, не меняя colour_count.",),
            commands=(":%s/old/new/g — весь файл", "\\< и \\> — границы слова", "c — подтверждать"),
            hint=r"Команда: :%s/\<colour\>/color/g",
            files=(
                _file(
                    "spelling.py",
                    """
                    colour = "blue"
                    print(colour)
                    colour_count = 2
                    # colour colour
                    """,
                    """
                    color = "blue"
                    print(color)
                    colour_count = 2
                    # color color
                    """,
                ),
            ),
            entrypoint="spelling.py",
        ),
        Lesson(
            id="21-substitute-groups",
            chapter="Поиск и замены",
            title="Группы в замене",
            goal="Перестраивать строки одним шаблоном.",
            task=("Преобразуй каждое Имя Фамилия в Фамилия, Имя.",),
            commands=(r"\v — very magic", "(...) — группа", r"\1, \2 — подстановки"),
            hint=r"Используй :%s/\v(\w+) (\w+)/\2, \1/",
            files=(
                _file(
                    "people.txt",
                    """
                    Ada Lovelace
                    Grace Hopper
                    Edsger Dijkstra
                    """,
                    """
                    Lovelace, Ada
                    Hopper, Grace
                    Dijkstra, Edsger
                    """,
                ),
            ),
            entrypoint="people.txt",
        ),
        Lesson(
            id="22-global",
            chapter="Поиск и замены",
            title="Команда global",
            goal="Применять Ex-команду к выбранным строкам.",
            task=(
                "Удали все строки DEBUG.",
                "На оставшихся строках INFO замени префикс на OK.",
            ),
            commands=(
                ":g/pattern/d — удалить совпавшие строки",
                ":g/pattern/s/old/new/",
                ":v — инверсия",
            ),
            hint="Сначала :g/^DEBUG/d, затем отдельная :g для INFO.",
            files=(
                _file(
                    "service.log",
                    """
                    INFO boot
                    DEBUG token=abc
                    INFO ready
                    DEBUG cache=miss
                    WARN slow
                    """,
                    """
                    OK boot
                    OK ready
                    WARN slow
                    """,
                ),
            ),
            entrypoint="service.log",
        ),
        Lesson(
            id="23-visual-char",
            chapter="Выделение и диапазоны",
            title="Visual по символам",
            goal="Выделять произвольный диапазон и заменять его.",
            task=("Выдели SECRET и замени его на public.",),
            commands=(
                "v — начать выделение",
                "o — сменить активный край",
                "c — заменить выделение",
            ),
            hint="Найди S через fS, затем v, движение и c.",
            files=(
                _file(
                    "visual.txt",
                    "token = prefix_SECRET_suffix",
                    "token = prefix_public_suffix",
                ),
            ),
            entrypoint="visual.txt",
        ),
        Lesson(
            id="24-visual-line",
            chapter="Выделение и диапазоны",
            title="Visual по строкам",
            goal="Перемещать блоки целыми строками.",
            task=("Перенеси первые две строки в конец, сохранив их порядок.",),
            commands=("V — строковый Visual", "d — вырезать", "p — вставить после строки"),
            hint="Выдели Vj, вырежи, перейди в конец и вставь.",
            files=(
                _file(
                    "order.txt",
                    """
                    gamma
                    delta
                    alpha
                    beta
                    """,
                    """
                    alpha
                    beta
                    gamma
                    delta
                    """,
                ),
            ),
            entrypoint="order.txt",
        ),
        Lesson(
            id="25-ex-ranges",
            chapter="Выделение и диапазоны",
            title="Диапазоны и normal",
            goal="Применять Normal-команды к диапазону строк.",
            task=(
                "Замени todo на DONE командой :2,5s/todo/DONE/.",
                "Выдели строки 2–5 через V и добавь '- ' через :normal! I-<пробел>.",
                "Добавь ; в конец тех же строк через :2,5normal! A;.",
            ),
            commands=(":2,5 — номера строк", ":'<,'> — Visual-диапазон", ":normal! {keys}"),
            hint="После V и : диапазон '<,'> появится сам; <пробел> — клавиша Space.",
            files=(
                _file(
                    "ranges.txt",
                    """
                    header
                    todo alpha
                    todo beta
                    todo gamma
                    todo delta
                    footer
                    """,
                    """
                    header
                    - DONE alpha;
                    - DONE beta;
                    - DONE gamma;
                    - DONE delta;
                    footer
                    """,
                ),
            ),
            entrypoint="ranges.txt",
        ),
        Lesson(
            id="26-visual-block",
            chapter="Выделение и диапазоны",
            title="Visual Block",
            goal="Править одинаковые колонки нескольких строк.",
            task=(
                "Добавь item_ в начало каждой строки одним блоком.",
                "Добавь ; в конец каждой строки блоковым выделением.",
            ),
            commands=(
                "Ctrl-v — блочный Visual",
                "I — вставка слева",
                "A — вставка справа",
                "Esc — применить",
            ),
            hint="Для правого края выдели строки, затем нажми $ и A.",
            files=(
                _file(
                    "block.txt",
                    """
                    alpha = 1
                    beta = 2
                    gamma = 3
                    """,
                    """
                    item_alpha = 1;
                    item_beta = 2;
                    item_gamma = 3;
                    """,
                ),
            ),
            entrypoint="block.txt",
        ),
        Lesson(
            id="27-named-register",
            chapter="Состояние Vim",
            title="Именованный регистр",
            goal="Хранить и вставлять текст явно выбранным регистром.",
            task=(
                'С пробела перед stable_value скопируй хвост строки в a через "ay$.',
                'Вставь его после = в трёх строках через "ap.',
            ),
            commands=('"ay$ — yank до конца в a', '"ap — put из a', ":reg a — показать a"),
            hint="Имя регистра указывается перед оператором.",
            files=(
                _file(
                    "registers.txt",
                    """
                    SOURCE: stable_value
                    first =
                    second =
                    third =
                    """,
                    """
                    SOURCE: stable_value
                    first = stable_value
                    second = stable_value
                    third = stable_value
                    """,
                ),
            ),
            entrypoint="registers.txt",
            expected_registers=(RegisterExpectation("a", " stable_value"),),
        ),
        Lesson(
            id="28-black-hole",
            chapter="Состояние Vim",
            title="Нулевой и чёрная дыра",
            goal="Не терять скопированный текст при удалении.",
            task=(
                "Скопируй строку template через yy.",
                'Удали trash one обычным dd, а trash two — через "_dd.',
                'Восстанови template после copy: через "0p.',
            ),
            commands=(
                "dd — удаляет и меняет безымянный регистр",
                '"_dd — чёрная дыра',
                '"0p — последняя копия',
            ),
            hint='Последовательность: yy, jdd, "_dd, "0p.',
            files=(
                _file(
                    "safe_delete.txt",
                    """
                    template
                    trash one
                    trash two
                    copy:
                    """,
                    """
                    template
                    copy:
                    template
                    """,
                ),
            ),
            entrypoint="safe_delete.txt",
            expected_registers=(
                RegisterExpectation("0", "template\n"),
                RegisterExpectation('"', "trash one\n"),
            ),
        ),
        Lesson(
            id="29-marks",
            chapter="Состояние Vim",
            title="Метки",
            goal="Возвращаться к точному месту после дальней правки.",
            task=(
                "Поставь локальную метку a внутри old первой строки.",
                "Замени нижний summary на ready.",
                "Вернись через `a и замени anchor на ready.",
            ),
            commands=(
                "ma — поставить метку",
                "`a — точная позиция",
                "'a — строка метки",
                ":marks — список",
            ),
            hint="Обе строки должны получить ready.",
            files=(
                _file(
                    "marks.txt",
                    """
                    anchor = "old"
                    line 2
                    line 3
                    line 4
                    line 5
                    line 6
                    line 7
                    line 8
                    summary = "old"
                    """,
                    """
                    anchor = "ready"
                    line 2
                    line 3
                    line 4
                    line 5
                    line 6
                    line 7
                    line 8
                    summary = "ready"
                    """,
                ),
            ),
            entrypoint="marks.txt",
            start_cursor=Cursor(1, 11),
        ),
        Lesson(
            id="30-macros",
            chapter="Состояние Vim",
            title="Макросы",
            goal="Записывать составное повторяемое действие.",
            task=(
                "На первой строке запиши в q добавление '- ' слева и ';' справа.",
                "Примени макрос к четырём следующим строкам через 4@q.",
            ),
            commands=(
                "qq ... q — запись в q",
                "@q — выполнить",
                "@@ — повторить",
                "4@q — четыре раза",
            ),
            hint="Заверши тело макроса переходом на начало следующей строки.",
            files=(
                _file(
                    "macro.txt",
                    """
                    alpha
                    beta
                    gamma
                    delta
                    epsilon
                    """,
                    """
                    - alpha;
                    - beta;
                    - gamma;
                    - delta;
                    - epsilon;
                    """,
                ),
            ),
            entrypoint="macro.txt",
        ),
        Lesson(
            id="31-buffers",
            chapter="Несколько файлов",
            title="Буферы",
            goal="Переключаться между открытыми файлами без потери правок.",
            task=(
                "В app.py замени dev на prod.",
                "Через :edit config.py выставь DEBUG = False.",
                "Через :edit notes.txt замени TODO на DONE.",
                "Посмотри :ls и вернись в app.py через :buffer app.py.",
            ),
            commands=(
                ":edit file — открыть",
                ":ls — список",
                ":buffer name — перейти",
                ":bnext/:bprevious",
            ),
            hint="Опция hidden уже включена; сохранять между переходами не обязательно.",
            files=(
                _file("app.py", 'MODE = "dev"', 'MODE = "prod"'),
                _file("config.py", "DEBUG = True", "DEBUG = False"),
                _file("notes.txt", "TODO release", "DONE release"),
            ),
            entrypoint="app.py",
        ),
        Lesson(
            id="32-windows",
            chapter="Несколько файлов",
            title="Окна и split",
            goal="Редактировать два буфера рядом и управлять фокусом.",
            task=(
                "Открой config.py справа через :vsplit и выставь TIMEOUT = 30.",
                "Вернись в левое окно через Ctrl-w h и выставь retries = 3.",
            ),
            commands=(":split/:vsplit file", "Ctrl-w h/j/k/l — фокус", "Ctrl-w = — выровнять"),
            hint="Панель задания — отдельное окно; ориентируйся по имени файла.",
            files=(
                _file("client.py", "retries = 1", "retries = 3"),
                _file("config.py", "TIMEOUT = 10", "TIMEOUT = 30"),
            ),
            entrypoint="client.py",
        ),
        Lesson(
            id="33-argdo",
            chapter="Несколько файлов",
            title="Список аргументов и argdo",
            goal="Выполнять одну Ex-команду по набору файлов.",
            task=(
                "Задай список :args src/a.py src/b.py src/c.py.",
                "Замени TODO на DONE во всех аргументах и сохрани их.",
            ),
            commands=(":args files — задать список", ":args — показать", ":argdo {cmd} | update"),
            hint="Подойдёт :argdo %s/TODO/DONE/g | update",
            files=(
                _file("src/a.py", "# TODO validate\nA = 1", "# DONE validate\nA = 1"),
                _file("src/b.py", "# TODO parse\nB = 2", "# DONE parse\nB = 2"),
                _file("src/c.py", "# TODO store\nC = 3", "# DONE store\nC = 3"),
            ),
            entrypoint="src/a.py",
        ),
        Lesson(
            id="34-quickfix",
            chapter="Несколько файлов",
            title="Quickfix",
            goal="Собрать совпадения проекта и пройти их как список задач.",
            task=(
                "Собери BROKEN через :vimgrep по src/*.py и открой :copen.",
                "Пройди совпадения и замени каждое BROKEN на FIXED.",
            ),
            commands=(
                ":vimgrep /pattern/ files",
                ":copen",
                ":cnext/:cprevious",
                ":cfdo {cmd} | update",
            ),
            hint="Можно править по одному через :cnext или применить :cfdo.",
            files=(
                _file(
                    "src/parser.py",
                    """
                    PARSER = "BROKEN"
                    fallback = "ok"
                    """,
                    """
                    PARSER = "FIXED"
                    fallback = "ok"
                    """,
                ),
                _file(
                    "src/store.py",
                    """
                    primary = "BROKEN"
                    replica = "BROKEN"
                    """,
                    """
                    primary = "FIXED"
                    replica = "FIXED"
                    """,
                ),
                _file("src/api.py", 'status = "BROKEN"', 'status = "FIXED"'),
            ),
            entrypoint="src/parser.py",
        ),
        Lesson(
            id="35-final-python",
            chapter="Проектная практика",
            title="Python-проект: сборка",
            goal="Закрепить точные правки и проектную навигацию в одном упражнении.",
            task=(
                'report.py: оставь return sum(values); value → total_value; замени print на print(f"total={total_value}").',
                "Через :args открой config.py и tests/test_report.py; MODE: debug → prod.",
                "Через :vimgrep и quickfix замени old_total на total во всём проекте.",
            ),
            commands=(":args/:buffer", ":vimgrep/:cfdo", "text objects · Visual · ."),
            hint="Ожидаемый стиль: две пустые строки между верхнеуровневыми блоками.",
            files=(
                _file(
                    "report.py",
                    """
                    def total(values):
                        result = 0
                        for item in values:
                            result += item
                        return result

                    def report(values):
                        value = total(values)
                        print("total:", value)

                    numbers = [1, 2, 3]
                    report(numbers)
                    """,
                    """
                    def total(values):
                        return sum(values)


                    def report(values):
                        total_value = total(values)
                        print(f"total={total_value}")


                    numbers = [1, 2, 3]
                    report(numbers)
                    """,
                ),
                _file(
                    "config.py",
                    """
                    MODE = "debug"
                    REPORT_KEY = "old_total"
                    """,
                    """
                    MODE = "prod"
                    REPORT_KEY = "total"
                    """,
                ),
                _file(
                    "tests/test_report.py",
                    """
                    from report import total


                    def test_old_total():
                        assert total([1, 2, 3]) == 6
                    """,
                    """
                    from report import total


                    def test_total():
                        assert total([1, 2, 3]) == 6
                    """,
                ),
            ),
            entrypoint="report.py",
        ),
        Lesson(
            id="36-nested-text-object",
            chapter="Объекты текста и поиск",
            title="Внешний уровень скобок",
            goal="Выбирать нужный уровень во вложенных конструкциях.",
            task=(
                "Поставь курсор на old_value внутри format(...).",
                "Командой c2i( замени всё содержимое внешнего wrap(...) на prepared, retries=3.",
            ),
            commands=("ci( — ближайшие скобки", "c2i( — второй внешний уровень"),
            hint="Счётчик перед text object расширяет его до следующей пары скобок.",
            files=(
                _file(
                    "nested.py",
                    "result = wrap(format(old_value, width=10), retries=2)",
                    "result = wrap(prepared, retries=3)",
                ),
            ),
            entrypoint="nested.py",
            start_cursor=Cursor(1, 22),
        ),
        Lesson(
            id="37-tag-text-objects",
            chapter="Объекты текста и поиск",
            title="Text objects для тегов",
            goal="Менять содержимое и удалять HTML-узлы вместе с границами.",
            task=(
                "Внутри h2 замени текст на Release status через cit.",
                "Поставь курсор на имя aside в открывающем теге и удали весь узел через dat.",
                "Удали оставшуюся пустую строку через dd.",
            ),
            commands=("cit — изменить внутри тега", "dat — удалить тег целиком"),
            hint="t работает с ближайшей парой открывающего и закрывающего тегов.",
            files=(
                _file(
                    "status.html",
                    """
                    <section>
                    <h2>Legacy title</h2>
                    <p>keep this paragraph</p>
                    <aside><span>remove me</span></aside>
                    </section>
                    """,
                    """
                    <section>
                    <h2>Release status</h2>
                    <p>keep this paragraph</p>
                    </section>
                    """,
                ),
            ),
            entrypoint="status.html",
            start_cursor=Cursor(2, 5),
        ),
        Lesson(
            id="38-search-boundaries",
            chapter="Объекты текста и поиск",
            title="Границы совпадения",
            goal="Ограничивать заменяемую часть сложного шаблона.",
            task=(
                "Одной заменой выставь 42 только числам после точного ключа key=.",
                "Не меняй backup_key и key_count.",
            ),
            commands=(r"\zs — начало результата", r"\ze — конец результата", r"\v — very magic"),
            hint=r"Подойдёт :%s/\v<key\=\zs\d+\ze;/42/g",
            files=(
                _file(
                    "limits.conf",
                    """
                    key=7;
                    backup_key=9;
                    key_count=3;
                    key=11;
                    """,
                    """
                    key=42;
                    backup_key=9;
                    key_count=3;
                    key=42;
                    """,
                ),
            ),
            entrypoint="limits.conf",
        ),
        Lesson(
            id="39-cgn-rename",
            chapter="Рефакторинг кода",
            title="Повторяемое переименование",
            goal="Переименовывать точный идентификатор через поиск и точку.",
            task=(
                "На total_value нажми *, затем N, чтобы задать поиск и вернуться.",
                "Замени совпадение через cgn на sum_value и повтори правку точкой.",
                "Не меняй total_value_count.",
            ),
            commands=("* — искать слово", "cgn — изменить следующее совпадение", ". — повторить"),
            hint="После первого cgn две точки обработают ещё два точных совпадения.",
            files=(
                _file(
                    "rename.py",
                    """
                    total_value = calculate()
                    total_value_count = 1
                    print(total_value)
                    return_value = total_value
                    """,
                    """
                    sum_value = calculate()
                    total_value_count = 1
                    print(sum_value)
                    return_value = sum_value
                    """,
                ),
            ),
            entrypoint="rename.py",
            start_cursor=Cursor(1, 1),
        ),
        Lesson(
            id="40-ex-move",
            chapter="Рефакторинг кода",
            title="Перестановка через :move",
            goal="Перемещать строки к адресу без вырезания и вставки.",
            task=(
                "Перенеси строку parse сразу после открывающей скобки PIPELINE.",
                "Используй :move с номером строки или адресом поиска.",
            ),
            commands=(":{range}move {address}", ":m — короткая форма", ":t — копировать"),
            hint="В исходном файле достаточно команды :4move 1.",
            files=(
                _file(
                    "pipeline.py",
                    """
                    PIPELINE = [
                        validate,
                        persist,
                        parse,
                    ]
                    """,
                    """
                    PIPELINE = [
                        parse,
                        validate,
                        persist,
                    ]
                    """,
                ),
            ),
            entrypoint="pipeline.py",
        ),
        Lesson(
            id="41-sequential-numbers",
            chapter="Рефакторинг кода",
            title="Последовательности чисел",
            goal="Нумеровать однотипные строки одной Visual-командой.",
            task=(
                "Выдели четыре строки через Visual Line.",
                "Нажми g Ctrl-a, чтобы получить значения от 1 до 4.",
            ),
            commands=("V — построчное выделение", "g Ctrl-a — возрастающая прибавка"),
            hint="На первой строке нажми V3j, затем g Ctrl-a.",
            files=(
                _file(
                    "codes.py",
                    """
                    OK = 0
                    PARSE_ERROR = 0
                    STORE_ERROR = 0
                    SEND_ERROR = 0
                    """,
                    """
                    OK = 1
                    PARSE_ERROR = 2
                    STORE_ERROR = 3
                    SEND_ERROR = 4
                    """,
                ),
            ),
            entrypoint="codes.py",
            start_cursor=Cursor(1, 6),
        ),
        Lesson(
            id="42-expression-register",
            chapter="Состояние и автоматизация",
            title="Регистр выражений",
            goal="Вставлять вычисленные значения без выхода из Insert mode.",
            task=(
                "После answer = вставь результат 7 * 6 через Ctrl-r =.",
                "После slug = вычисли tolower(substitute('Release Candidate', ' ', '-', 'g')).",
            ),
            commands=("Ctrl-r = — выражение в Insert", "Enter — вычислить и вставить"),
            hint="Кавычки вокруг результата уже есть только в строке slug.",
            files=(
                _file(
                    "computed.vim",
                    """
                    answer =
                    slug = ''
                    """,
                    """
                    answer = 42
                    slug = 'release-candidate'
                    """,
                ),
            ),
            entrypoint="computed.vim",
            start_cursor=Cursor(1, 8),
        ),
        Lesson(
            id="43-append-macro",
            chapter="Состояние и автоматизация",
            title="Дополнение макроса",
            goal="Собирать макрос по частям и повторять итоговое действие.",
            task=(
                "На alpha запиши в a добавление кавычки слева и останови запись.",
                "Через qA допиши в тот же макрос кавычку и запятую справа, затем переход j.",
                "Примени готовый макрос к двум оставшимся строкам через 2@a.",
            ),
            commands=("qa ... q — новая запись", "qA ... q — дописать в a", "2@a — повторить"),
            hint='Первая часть: qa I" Esc q. Вторая: qA A", Esc j q.',
            files=(
                _file(
                    "macro_append.txt",
                    """
                    alpha
                    beta
                    gamma
                    """,
                    """
                    "alpha",
                    "beta",
                    "gamma",
                    """,
                ),
            ),
            entrypoint="macro_append.txt",
        ),
        Lesson(
            id="44-change-list",
            chapter="Состояние и автоматизация",
            title="История изменений",
            goal="Возвращаться к местам последних правок без меток.",
            task=(
                "Сверху вниз замени old на ready во всех трёх строках с настройками.",
                "Открой :changes и повторяй g;, пока не вернёшься к первой правке.",
            ),
            commands=("g; — предыдущее изменение", "g, — следующее изменение", ":changes — список"),
            hint="g; ходит по change list, отдельно от списка прыжков Ctrl-o.",
            files=(
                _file(
                    "changes.py",
                    """
                    primary = "old"
                    line_2 = "keep"
                    line_3 = "keep"
                    secondary = "old"
                    line_5 = "keep"
                    line_6 = "keep"
                    fallback = "old"
                    """,
                    """
                    primary = "ready"
                    line_2 = "keep"
                    line_3 = "keep"
                    secondary = "ready"
                    line_5 = "keep"
                    line_6 = "keep"
                    fallback = "ready"
                    """,
                ),
            ),
            entrypoint="changes.py",
            start_cursor=Cursor(1, 12),
        ),
        Lesson(
            id="45-find-path",
            chapter="Работа с проектом",
            title="Поиск файла через path",
            goal="Открывать модуль по имени без ручного ввода полного пути.",
            task=(
                "Добавь src/** в опцию path и открой formatter.py через :find.",
                "В format_name() замени return value на return value.strip().title().",
            ),
            commands=(":set path+=src/**", ":find {name}", ":set path? — проверить"),
            hint="После :set path+=src/** выполни :find formatter.py.",
            files=(
                _file(
                    "app.py",
                    """
                    from core.formatter import format_name

                    print(format_name("  ada "))
                    """,
                    """
                    from core.formatter import format_name

                    print(format_name("  ada "))
                    """,
                ),
                _file(
                    "src/core/formatter.py",
                    """
                    def format_name(value):
                        return value
                    """,
                    """
                    def format_name(value):
                        return value.strip().title()
                    """,
                ),
            ),
            entrypoint="app.py",
        ),
        Lesson(
            id="46-location-list",
            chapter="Работа с проектом",
            title="Локальный список ошибок",
            goal="Собирать и обрабатывать совпадения в location list текущего окна.",
            task=(
                "Собери DEPRECATED через :lvimgrep по src/*.py и открой :lopen.",
                "Замени совпадения на SUPPORTED через :ldo и сохрани файлы.",
            ),
            commands=(":lvimgrep /pattern/ files", ":lopen/:lnext", ":ldo {cmd} | update"),
            hint="Подойдёт :ldo s/DEPRECATED/SUPPORTED/ | update.",
            files=(
                _file("src/api.py", 'API = "DEPRECATED"', 'API = "SUPPORTED"'),
                _file("src/cache.py", 'CACHE = "DEPRECATED"', 'CACHE = "SUPPORTED"'),
                _file("src/store.py", 'STORE = "DEPRECATED"', 'STORE = "SUPPORTED"'),
            ),
            entrypoint="src/api.py",
        ),
        Lesson(
            id="47-quickfix-items",
            chapter="Работа с проектом",
            title="Операция на каждый match",
            goal="Применять команду к каждой позиции quickfix, а не к каждому файлу.",
            task=(
                "Собери все TODO через :vimgrep /TODO/ **/*.py.",
                "На каждой найденной строке замени TODO на DONE через :cdo и сохрани.",
            ),
            commands=(":vimgrep /pattern/ **/*.py", ":copen/:cnext", ":cdo {cmd} | update"),
            hint="Подойдёт :cdo s/TODO/DONE/ | update; один файл содержит два совпадения.",
            files=(
                _file(
                    "src/jobs.py",
                    """
                    # TODO retry policy
                    def run():
                        pass  # TODO metrics
                    """,
                    """
                    # DONE retry policy
                    def run():
                        pass  # DONE metrics
                    """,
                ),
                _file(
                    "tests/test_jobs.py",
                    """
                    # TODO add timeout case
                    def test_run():
                        assert True
                    """,
                    """
                    # DONE add timeout case
                    def test_run():
                        assert True
                    """,
                ),
            ),
            entrypoint="src/jobs.py",
        ),
        Lesson(
            id="48-code-navigation",
            chapter="Работа с проектом",
            title="Навигация по коду",
            goal="Открывать файл под курсором и переходить к определению по tags.",
            task=(
                "На пути src/pricing.py нажми gf и замени DEFAULT_TAX = 0.10 на 0.20.",
                "Вернись в app.py через Ctrl-o, поставь курсор на calculate_total и нажми Ctrl-].",
                "В определении измени return на subtotal * (1 + DEFAULT_TAX).",
            ),
            commands=(
                "gf — открыть путь под курсором",
                "Ctrl-] — перейти по tag",
                "Ctrl-o — вернуться",
            ),
            hint="Готовый файл tags лежит в корне упражнения; создавать его не нужно.",
            files=(
                _file(
                    "app.py",
                    """
                    # file: src/pricing.py
                    from src.pricing import calculate_total

                    print(calculate_total([10, 20]))
                    """,
                    """
                    # file: src/pricing.py
                    from src.pricing import calculate_total

                    print(calculate_total([10, 20]))
                    """,
                ),
                _file(
                    "src/pricing.py",
                    """
                    DEFAULT_TAX = 0.10


                    def calculate_total(values):
                        subtotal = sum(values)
                        return subtotal
                    """,
                    """
                    DEFAULT_TAX = 0.20


                    def calculate_total(values):
                        subtotal = sum(values)
                        return subtotal * (1 + DEFAULT_TAX)
                    """,
                ),
                _file(
                    "tags",
                    "!_TAG_FILE_FORMAT\t2\t/extended format/\n"
                    'calculate_total\tsrc/pricing.py\t/^def calculate_total(values):$/;"\tf',
                    "!_TAG_FILE_FORMAT\t2\t/extended format/\n"
                    'calculate_total\tsrc/pricing.py\t/^def calculate_total(values):$/;"\tf',
                ),
            ),
            entrypoint="app.py",
            start_cursor=Cursor(1, 9),
        ),
        Lesson(
            id="49-make-quickfix",
            chapter="Работа с проектом",
            title="Проверка через :make",
            goal="Запускать проектную проверку и исправлять ошибку через quickfix.",
            task=(
                r"Задай :set makeprg=python3\ check_project.py и :set errorformat=%f:%l:%m.",
                "Запусти :make, открой :copen и перейди к первой ошибке.",
                "Исправь MODE на prod, сохрани, вернись в README.txt и повтори :make без ошибок.",
            ),
            commands=(":make — запустить makeprg", ":copen/:cfirst", ":update — сохранить"),
            hint="Проверяющий Python-скрипт уже входит в упражнение.",
            files=(
                _file(
                    "README.txt",
                    "Run the project check from Vim.",
                    "Run the project check from Vim.",
                ),
                _file(
                    "src/config.py",
                    """
                    MODE = "debug"
                    TIMEOUT = 10
                    """,
                    """
                    MODE = "prod"
                    TIMEOUT = 10
                    """,
                ),
                _file(
                    "check_project.py",
                    """
                    from pathlib import Path


                    path = Path("src/config.py")
                    if 'MODE = "prod"' not in path.read_text(encoding="utf-8"):
                        print("src/config.py:1:MODE must be prod")
                        raise SystemExit(1)
                    """,
                    """
                    from pathlib import Path


                    path = Path("src/config.py")
                    if 'MODE = "prod"' not in path.read_text(encoding="utf-8"):
                        print("src/config.py:1:MODE must be prod")
                        raise SystemExit(1)
                    """,
                ),
            ),
            entrypoint="README.txt",
        ),
        Lesson(
            id="50-final-project",
            chapter="Итог",
            title="Итоговый проект",
            goal="Собрать продвинутую навигацию, рефакторинг и проверку проекта.",
            task=(
                "gf: открой report.py; total_value → sum_value через cgn, внешний wrap — через c2i(.",
                "Через :find открой config.py: mode → prod, retries → 3; TODO замени через :cdo.",
                r"В main.py: makeprg=python3\ check_project.py, errorformat=%f:%l:%m; затем :make.",
            ),
            commands=(
                "gf/:find",
                "cgn · c2i(",
                ":vimgrep/:cdo",
                ":make/quickfix",
            ),
            hint='Финал report.py: return wrap(sum_value, retries=SETTINGS["retries"]).',
            files=(
                _file(
                    "main.py",
                    """
                    # file: src/report.py
                    from src.report import build_report

                    print(build_report([1, 2, 3]))
                    """,
                    """
                    # file: src/report.py
                    from src.report import build_report

                    print(build_report([1, 2, 3]))
                    """,
                ),
                _file(
                    "src/report.py",
                    """
                    from src.config import SETTINGS


                    def format_value(value):
                        return str(value)


                    def wrap(value, retries):
                        return f"{value}:{retries}"


                    def build_report(values):
                        total_value = sum(values)
                        return wrap(format_value(total_value), retries=1)
                    """,
                    """
                    from src.config import SETTINGS


                    def format_value(value):
                        return str(value)


                    def wrap(value, retries):
                        return f"{value}:{retries}"


                    def build_report(values):
                        sum_value = sum(values)
                        return wrap(sum_value, retries=SETTINGS["retries"])
                    """,
                ),
                _file(
                    "src/config.py",
                    'SETTINGS = {"mode": "debug", "retries": 1}',
                    'SETTINGS = {"mode": "prod", "retries": 3}',
                ),
                _file(
                    "tests/test_report.py",
                    """
                    # TODO cover production mode
                    from src.report import build_report


                    def test_report():
                        assert build_report([1, 2])
                    """,
                    """
                    # DONE cover production mode
                    from src.report import build_report


                    def test_report():
                        assert build_report([1, 2])
                    """,
                ),
                _file(
                    "check_project.py",
                    """
                    from pathlib import Path


                    CHECKS = (
                        ("src/report.py", 13, "sum_value = sum(values)"),
                        (
                            "src/report.py",
                            14,
                            'return wrap(sum_value, retries=SETTINGS["retries"])',
                        ),
                        (
                            "src/config.py",
                            1,
                            'SETTINGS = {"mode": "prod", "retries": 3}',
                        ),
                        ("tests/test_report.py", 1, "# DONE cover production mode"),
                    )

                    failed = False
                    for path, line, expected in CHECKS:
                        if expected not in Path(path).read_text(encoding="utf-8"):
                            print(f"{path}:{line}:missing required change")
                            failed = True
                    raise SystemExit(1 if failed else 0)
                    """,
                    """
                    from pathlib import Path


                    CHECKS = (
                        ("src/report.py", 13, "sum_value = sum(values)"),
                        (
                            "src/report.py",
                            14,
                            'return wrap(sum_value, retries=SETTINGS["retries"])',
                        ),
                        (
                            "src/config.py",
                            1,
                            'SETTINGS = {"mode": "prod", "retries": 3}',
                        ),
                        ("tests/test_report.py", 1, "# DONE cover production mode"),
                    )

                    failed = False
                    for path, line, expected in CHECKS:
                        if expected not in Path(path).read_text(encoding="utf-8"):
                            print(f"{path}:{line}:missing required change")
                            failed = True
                    raise SystemExit(1 if failed else 0)
                    """,
                ),
            ),
            entrypoint="main.py",
            start_cursor=Cursor(1, 11),
        ),
    )
)
