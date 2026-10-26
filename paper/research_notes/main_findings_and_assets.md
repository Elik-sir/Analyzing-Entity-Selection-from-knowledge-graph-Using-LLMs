# Основные выводы и материалы для статьи

**Уточнение состава материалов, 26 октября 2026:** актуальное расположение рисунков и таблиц — в [thesis_asset_plan.md](thesis_asset_plan.md). Motif/size figures сохраняются в основном тексте согласно уточнённой авторской цели; прежняя рекомендация об их переносе в Appendix ниже больше не действует. Числовые выводы и отобранные строки этого документа сохраняются.

## Отправной тезис Tool Selection и основная проблема

Добавлено 26 октября 2026 по уточнению автора. **В Tool Selection качество выбора существенно различается между паттернами зависимостей инструментов; одного числа инструментов недостаточно для описания трудности.** В исходной работе motif-associated differences сохраняются при учёте размера и других измеренных свойств задачи. Это исходный результат Tool Graph Complexity, а не новый вклад нашей статьи. Опора: Section 5.3 и Table 1, PDF p. 8; утверждение не означает одинаковую трудность всех мотивов, универсальный ranking или изолированный причинный эффект topology.

**Основная проблема:** какие из этих структурных различий сохраняются в KG entity selection при явно предъявленных отношениях, какие меняются и что доступность evidence, покрытие маршрутов и соседние distractors позволяют предположить об источниках ошибок выбора инструментов?

**Цель текущей работы:** уточнить границы уже наблюдавшегося Tool-to-KG transfer через существующие evidence/presentation/noise contrasts и парную диагностику остаточных ошибок KG. Appendix O уже содержит первоначальный перенос и Chain/Tree-in наблюдения; собственный дополнительный анализ начинается с более подробного разделения условий и ошибок, а не с повторного заявления самого переноса.

English framing candidate: *Prior work on tool selection reports substantial differences in selection success across dependency patterns, including motif-associated differences after accounting for graph size and other measured task properties. This motivates asking which structural selection difficulties persist when relations are explicitly available, which change, and how evidence availability and observable failure modes constrain explanations of tool-selection errors.*

Из этого исходного тезиса следуют два основных вывода ниже. Структурный паттерн остаётся центральной осью постановки; представление фактов и ошибки используются для исследования границ его объяснения.

25 октября 2026. Первый шаг сокращённого плана: фиксируем формулировки и выбираем уже рассчитанные результаты. Новые эксперименты, пересчёт архива, интервалы и статистические тесты не выполнялись. Таблицы и рисунки ниже — согласуемый состав; финальная LaTeX-вёрстка и новые рисунки ещё не созданы. Текущая рукопись сохранена.

## Основной вывод 1: раскрытие отношений улучшает покрытие, но не гарантирует полноту

**Планируемая формулировка:** раскрытие отношений существенно повышает совпадение выборки с графовым reference. При этом явные связи не устраняют неполное покрытие; величина остаточных ошибок зависит от модели и семейства задания.

Английская формулировка-кандидат: *Providing explicit relations increases graph-reference recovery, but relation visibility alone does not ensure complete route coverage.*

Опора: Raw+E−Raw mean F1 равен +0.674/+0.466/+0.572 для Gemma/Qwen/Ministral при 3,400 парах на модель. Это округлённые существующие оценки. В отдельной контролируемой шестинодовой Tree-in выборке K1 exact составляет 87/100, 15/100 и 54/100. Не объединять эти две панели в одну population или последовательную цепочку одних и тех же условий. Raw/Raw+E добавляет информацию, а не только меняет serialization; низкий Raw score не доказывает ошибку reasoning при отсутствии достаточных фактов.

Claims: `C-final-raw-f1`, `C-raw-overlay-pairing`, `C-nr-groups`. Источники: [paired_contrasts.csv](analyses/final_results/run-01/paired_contrasts.csv), селектор `contrast=raw_explicit, metric=f1`; [signature summary](analyses/novelty_refinement/run-02/summary.json), `groups[condition=K1]`; [reference pairing](reference_pairing_report.md).

Основная поддержка: **рисунок 1A** и **рисунок 2**. Научная роль — разграничить наличие фактов и успешный выбор полного reference, а не заявить новое открытие трудности Tree-in из Appendix O.

## Основной вывод 2: представление одинаковых фактов меняет состав ошибок на тех же задачах

**Планируемая формулировка:** при одинаковых уникальных отношениях размещение фактов и формулировка запроса меняют конкретные итоговые выборки. Улучшение среднего score или уменьшение одной категории ошибок не означает равномерного исправления задач; присутствуют регрессии и другие ошибки, а профиль зависит от модели.

Английская формулировка-кандидат: *Fact-preserving presentation changes alter which incomplete selections become exact, while also introducing regressions and leaving model-specific residual errors.*

Опора: у Qwen Tree-in K1 исходно 71/100 точных одношаговых множеств. K1→K4 исправляет до exact 38 из этих 71, но шесть из пятнадцати исходно exact выборок перестают быть exact. K1→K3 и K1→K7 исправляют соответственно 13/71 и 10/71; итоговая exact в обоих случаях 16/100 против 15/100 исходно. В K7 одношаговых множеств становится 52/100, поэтому сокращение этого паттерна нельзя целиком назвать исправлением: часть задач переходит в другие ошибки. У Ministral иной исходный профиль — 15/100 одношаговых множеств и 54/100 exact; условия и ухудшения показываем также для него.

Claims: `C-nr-groups`, `C-nr-transitions`, `C-final-placement-f1`, `C-final-representation-f1`. Источники: [signature summary](analyses/novelty_refinement/run-02/summary.json), `groups` и `transitions[before=K1,after=K3/K4/K7]`; `paired_contrasts.csv`, селекторы `format_slots/format_goal/placement_object/placement_both/question_triples,metric=f1`.

Основная поддержка: **таблица 2** и **рисунок 1B**. Это наиболее конкретный дополнительный анализ относительно прежнего описательного текста. K4 также меняет повторение, заметность и длину; внутренний механизм поиска не установлен. Gemma имеет aggregate/cached показатели, но не identity-level одношаговые подписи; в таблице 2 его не восстанавливаем из F1.

## Поддерживающий вывод: связанные distractors меняют не только score, но и профиль ошибок

В существующих парных данных соседний контекст снижает F1 у всех трёх моделей в triples и templated text. В конкретных семействах меняется сочетание пропусков и лишних включений. Например, Ministral Tree-in K2 имеет 27 omission-only, 19 inclusion-only, 41 mixed и 13 exact исходов на 100 задач; в K1 — 39/1/6/54 соответственно. Такой профиль не следует описывать как единый для всех моделей переход от omission к inclusion.

Claims: `C-final-noise-f1`, `C-assessment-error-profiles`; для выбранных cached категорий см. [transfer summary](analyses/transfer_positioning/run-04/summary.json), `groups[series_id=core,condition=K1/K2,motif=tree_in,size=6]`. Основная поддержка: **рисунок 1C** и **рисунок 2**. Adjacent effects и omission/inclusion уже изучались в Appendix O; здесь это диагностическая поддержка двух выводов, а не самостоятельное заявление о впервые обнаруженном явлении.

## Таблица 1 — что уже установлено и что добавляет эта работа

Предварительное название: *Prior Tool-to-KG Evidence and the Scope of the Present Analysis*.

Компактная качественная таблица перед Results, примерно пять строк, три содержательных столбца: «Вопрос», «Tool Graph / Appendix O», «Дополнительный анализ здесь».

- Перенос профилей Chain/Tree-in: исходное наблюдение уже в Appendix O; здесь — предпосылка и граница интерпретации, не новый transfer test.
- Доступность отношений: в Appendix O explicit KG; здесь — архивный paired Raw/Raw+E contrast с проверкой того, что добавлено.
- Представление одинаковых фактов: controlled triples/text, hosting и wording contrasts в текущем архиве.
- Ошибки: omission/inclusion уже обсуждались; здесь — точные одношаговые подписи и реальные same-task transitions.
- Источники и reference: обозначить reuse/неустановленное row overlap, различие tool reference и KG route union; не утверждать независимую репликацию.

Без новых чисел Tool/KG, вычитания разных papers и фиктивного Tool control arm. Опора: `C-transfer-prior-overlap`, `C-nr-prior-overlap`, [contribution comparison](contribution_comparison.md), [transfer positioning](transfer_positioning.md). Эта таблица показывает границу вклада; не заменяет эмпирические доказательства.

## Рисунок 1 — эффекты evidence, presentation и noise

Предварительное название: *Relational Evidence, Presentation, and Adjacent-Context Effects on Selection F1*.

Один составной forest plot из существующих парных оценок, три отдельные панели:

- **A — добавление информации:** Raw+E−Raw для трёх моделей, по 3,400 пар.
- **B — представление выделенных фактов:** Text−triples для procedural/direct queries; destination−source; both−source; direct−procedural wording, по 700 пар.
- **C — соседний контекст:** adjacent−disconnected для triples и text, по 700 пар.

Ось X — изменение mean per-task set-F1 в score units; нулевая линия; модели обозначены единообразно. Интервалы — только уже рассчитанные exploratory simultaneous bands из исходного семейства 78 F1/exact effects. Масштабы панелей можно различать, но их пределы должны быть явно подписаны. Не трактовать разницу двух оценок из разных панелей как проверенный interaction или difference-in-differences. Не переносить эти bands на выбранную после анализа Tree-in диагностику.

Данные уже отобраны: [figure1_condition_effects.csv](analyses/main_claim_assets/run-02/figure1_condition_effects.csv), 24 существующие F1-оценки. Поля `left/right/direction`, `N_pairs`, `left_valid/right_valid`, `delta`, `simultaneous_low/high` сохранены. По сути это компактное объединение нынешней таблицы condition effects и части supplementary presentation estimates; не добавлять их дубли в основной текст. Готовые Raw/controlled рисунки остаются референсами оформления, но новый composite ещё не нарисован.

## Рисунок 2 — какие ошибки остаются при явных связях

Предварительное название: *Exact Recovery, Omissions, and Excess Selection under Explicit Relations*.

Три панели по моделям; в каждой пять семейств с размером шесть: Chain, Star-in, Star-out, Tree-in, Tree-out. Для каждого — две горизонтальные stacked bars K1/K2. Сегменты: exact, omission-only, inclusion-only, mixed, invalid. Ось X — число задач из 100 запланированных; исходные cached fp/fn и validity задают категории. Сумма каждого столбика/полосы — 100, invalid не исключается. Это описательная композиция без новых error bars или interaction tests.

Данные уже отобраны: [figure2_error_composition.csv](analyses/main_claim_assets/run-02/figure2_error_composition.csv), 30 model/family/condition cells. Источник — уже рассчитанный transfer summary, не новый пересчёт ответов. Gemma участвует по cached coarse categories; это не предоставляет identities для его one-hop диагностики. Rhombus/hourglass сюда не включать: их доступные размеры другие. Рисунок заменяет роль нынешнего большого motif-profile plot в основном тексте, добавляя явное разложение ошибок вместо повторения двух метрик.

## Таблица 2 — что происходит с теми же ошибочными выборками

Предварительное название: *Paired Changes in Six-Node Tree-in Selection Signatures*.

Шесть строк: Qwen и Ministral × K1→K3/K4/K7. Столбцы: model/contrast; exact до→после из 100; one-hop до→после из 100; one-hop→exact с условным исходным знаменателем; утраченные exact с исходным exact-знаменателем; invalid после из 100. Подпись расшифровывает K1/K3/K4/K7 словами и указывает одношаговую подпись как конечное множество, а не внутреннюю траекторию.

Готовые значения (каждое сравнение имеет 100 запланированных пар):

- Qwen K1→K3: exact 15→16; one-hop 71→76; исправлено 13/71; утрачено exact 12/15; invalid 0.
- Qwen K1→K4: exact 15→51; one-hop 71→31; исправлено 38/71; утрачено exact 6/15; invalid 0.
- Qwen K1→K7: exact 15→16; one-hop 71→52; исправлено 10/71; утрачено exact 11/15; invalid 0.
- Ministral K1→K3: exact 54→38; one-hop 15→24; исправлено 6/15; утрачено exact 29/54; invalid 1.
- Ministral K1→K4: exact 54→62; one-hop 15→6; исправлено 8/15; утрачено exact 9/54; invalid 0.
- Ministral K1→K7: exact 54→62; one-hop 15→5; исправлено 8/15; утрачено exact 11/54; invalid 9.

Эти контрасты используют повторно одни исходные задачи; не суммировать их в независимую выборку. Условные fractions не имеют новых интервалов. Отсутствие Gemma объяснить недоступными selected identities, а не скрытым отбором слабых моделей.

Данные: [table2_signature_transitions.csv](analyses/main_claim_assets/run-02/table2_signature_transitions.csv). Это центральный новый материал относительно текущего PDF; LaTeX-фрагмент ещё не создан.

## Что оставить в приложении

Полные motif/size curves и endpoint tables, все условия/naming/incremental, analytical baseline values, подробные validity/coverage сведения. Не дублировать таблицу 2 Sankey-графиком с теми же шестью строками. Ограничение о неразличимости правильного и ненаправленного обхода в проверенном Tree-in срезе обозначить в основном Discussion; неизвестный результат полной component heuristic не превращать в отдельный вывод или рисунок. Исходные figures не удалять.

## Итог зафиксированного набора

**Два основных вывода, один поддерживающий; две таблицы и два рисунка.** Таблица 1 отделяет prior от increment; рисунок 1 показывает общие эффекты; рисунок 2 локализует типы остаточных ошибок; таблица 2 показывает реальные изменения на одних заданиях. Связь с Tool Selection обсуждается через границы возможных объяснений. Новый алгоритм, causal mechanism, самостоятельная новая transfer-демонстрация и QA gain не заявляются.

Машиночитаемые селекторы, hashes, проверка знаменателей и связи с claim IDs: [asset_manifest.json](analyses/main_claim_assets/run-02/asset_manifest.json). Скрипт только выбирает готовые строки; новые результаты модельных экспериментов или inference не создаёт. `run-01` содержит промежуточные CSV до остановки на проверке ошибочно указанного claim ID; финальным является `run-02`. Это не независимые анализы. Проверки выбранных чисел не означают полного scientific review или доказанной публикационной оригинальности.
