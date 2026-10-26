# Материалы под уточнённую цель: мотив, размер и границы Tool-to-KG transfer

**Последнее уточнение автора, 26 октября 2026:** основная метрика — **Recall**; Precision и Exact — дополнительные. Основная таблица 2 компактная: одна строка на модель, K1/K3/K4/K7 по столбцам, в ячейках mean per-task recall. Данные: [table2_treein_recall.csv](analyses/main_claim_assets/run-06/table2_treein_recall.csv); [изображение](../figures/treein_recall_v1/table2_treein_recall.png). Все три модели включены; N=100 и invalid policy указаны в подписи. Прежняя длинная PR/Exact таблица сохраняется как дополнительный материал. Ранее построенные Precision-графики остаются диагностическими; они не задают основную метрику статьи.

26 октября 2026. Это уточнение набора материалов после авторской формулировки цели: исследовать зависимости от мотива и размера, изменение этих зависимостей при evidence/presentation/noise и сходства/различия с Tool Selection. Используются существующие эксперименты и завершённые анализы. Новые рисунки или manuscript sections в этом шаге не создавались.

**Выбор метрик по указанию автора:** основные графики показывают отдельно recall и precision. Exact остаётся дополнительным показателем полного совпадения; F1 больше не является основной визуальной метрикой. Используются macro means per task из готовых CSV, с исходным failure policy и знаменателями. Данные подготовлены в [run-04](analyses/main_claim_assets/run-04/asset_manifest.json). Старые PDF с F1 сохраняются как исходные renders и требуют перерисовки. Готовые uncertainty exports содержат только F1/exact: для precision/recall новые интервалы не вычисляются и старые не переносятся.

**Изменение прежнего решения:** motif/size figures остаются в основном тексте. Рекомендация перенести их целиком в Appendix из `main_findings_and_assets.md` для этой цели больше не действует. Подробная error-composition figure становится supplementary. Активный набор — три рисунка и две таблицы; исходные материалы сохраняются.

## Рисунок 1. Зависимость качества от графового мотива

**Какой вопрос поддерживает:** различается ли выбор сущностей между семействами при сопоставимом числе узлов; как профиль меняется при adjacent context?

Перерисовать структуру существующего [motif_profiles.pdf](../manuscript/figures/motif_profiles.pdf) из [motif_precision_recall.csv](analyses/main_claim_assets/run-04/motif_precision_recall.csv). Ось X — семейство; ось Y — mean per-task recall и precision в отдельных панелях с согласованной шкалой 0–1. Модели — отдельные панели; K1/K2 показывают disconnected/adjacent context. Пять семейств сравниваются при шести узлах. Rhombus имеет четыре узла, Hourglass — пять; они должны оставаться визуально отделены и не включаться в утверждение об equal-size contrast. По 100 planned tasks в ячейке, invalid сохраняется с нулевым вкладом. Exact сохранить в компактной числовой таблице, не добавляя третью метрику к каждой панели.

**Допустимый вывод:** при одинаковом размере reference наблюдаются разные task-family profiles, причём их величина и noise sensitivity зависят от модели. Это условная связь в frozen tasks: query semantics, relation/type composition и сущности также меняются между семействами. Изолированный причинный эффект topology не измерен.

Источники: [motif_size_metrics.csv](analyses/final_results/run-01/motif_size_metrics.csv), `series_id=core,condition in {K1,K2}`; старый source manifest [asset_sources.json](analyses/manuscript_assets/run-01/asset_sources.json) документирует прежний F1/exact render, новый [manifest](analyses/main_claim_assets/run-04/asset_manifest.json) — выбранные precision/recall. Здесь 42 существующие model/motif/condition cells. Это описательные профили без новых error bars. Recall измеряет долю reference entities, попавших в выборку; precision — долю reference entities среди выбранных. Сохранённые per-task scores усредняются с исходным failure policy, не заменяются pooled micro ratios.

## Рисунок 2. Размерные профили внутри семейств при разных evidence conditions

**Какой вопрос поддерживает:** как качество меняется с числом узлов внутри каждого семейства и как различаются Raw/Raw+E profiles?

Перерисовать существующий [size_profiles.pdf](../manuscript/figures/size_profiles.pdf) из [size_precision_recall.csv](analyses/main_claim_assets/run-04/size_precision_recall.csv). Ось X — размер target/reference subgraph; recall и precision показать в раздельных согласованных блоках, сохранив Raw/Raw+E, все три модели и пять variable-size families. При нехватке места разделить блоки на две согласованные части рисунка вместо наложения метрик на двойную ось. Rhombus/Hourglass с единственным размером не образуют кривых. Все семейства сохраняются, включая near-ceiling и немонотонные профили; exact endpoint values остаются supplementary.

**Проверяемый по готовым данным вопрос:** связано ли изменение размера преимущественно с пропусками, лишними включениями или обоими типами ошибок, и как выглядят эти профили по task families, моделям и условиям? Направления старых F1-кривых не подставлять вместо отдельно показанных precision/recall. Выводы о монотонности каждой метрики формулировать по её фактическим значениям.

Размеры представлены разными frozen samples, а не последовательным расширением одной задачи. При фиксированных 25 candidates меняются reference prevalence и число distractors. Сравнение наклонов не является протестированным interaction или causal size effect. Raw/Raw+E добавляет информацию; это не одинаковые факты в разном формате.

Источники: `motif_size_metrics.csv`, `series_id=full_braw,condition in {Braw,Braw+E}`; существующий source manifest. Полный набор содержит 204 сохранённые model/motif/size/condition cells, включая single-size families; линии используют только пять variable-size families. Никакой новый fit или uncertainty calculation не нужен.

## Рисунок 3. Парные эффекты evidence, presentation и noise

**Какой вопрос поддерживает:** что именно меняется при раскрытии отношений, представлении одинаковых выделенных фактов и добавлении adjacent distractors?

Запланированный составной описательный difference plot из [condition_precision_recall.csv](analyses/main_claim_assets/run-04/condition_precision_recall.csv): A — Raw+E−Raw; B — triples/text, source/destination/both hosting и question wording; C — adjacent−disconnected для triples/text. Для каждого сравнения показать отдельно delta recall и delta precision, три модели и нулевую линию. Это разности готовых средних по полным парным populations; отображение условий и знаменателей проверено по прежнему paired export. Новый composite ещё не отрисован. Прежний [F1 export](analyses/main_claim_assets/run-02/figure1_condition_effects.csv) сохраняется только как история.

**Допустимая интерпретация:** отдельно описывать, как меняются полнота и доля релевантных выборов, а не скрывать их разное поведение в F1. В этом PR-рисунке нет uncertainty bars: их готовые значения отсутствуют. Не заявлять статистическую значимость PR-изменений или подтверждённый interaction на основании старых F1 bands либо одних point estimates.

Ограничение: aggregate condition plot показывает общий эффект в соответствующей population, но сам по себе не доказывает, что формат одинаково действует на каждый мотив или размер. Часть зависимости по семействам видна в рисунках 1–2; отдельный статистический motif×presentation тест не выполнен. Caption должен обозначать разные N (3,400 Raw pairs; 700 Core pairs), описательный характер PR-разностей и отсутствие новых интервалов.

## Таблица 1. Сопоставление структурных результатов Tool Selection и KG

**Какой вопрос поддерживает:** какие наблюдения служат исходной мотивацией, где видны сходства/различия и какие выводы о переносе допустимы?

Планируемая компактная таблица: «Свойство/семейство», «Tool Selection: результат и источник», «KG: условие, метрика и наблюдение», «Граница интерпретации».

Содержательное ядро строк:

- Pattern dependence beyond node count: исходный Tool result Section 5.3/Table 1; KG equal-size profiles рисунка 1. У Tool учёт измеренных covariates не делает KG family contrast causal.
- Chain: Tool-side sequential penalty и облегчение explicit-KG chains, уже рассмотренное в Appendix O; различия моделей/conditions в нашем архиве не превращать в единое универсальное inversion утверждение.
- Tree-in: различать raw tool difficulty и null-compatible adjusted Tree-in coefficient; KG residual incompleteness не считать автоматически тем же механизмом.
- Size: передавать условные профили и исключения, не постулировать общий монотонный закон или одинаковые размерные диапазоны.
- Adjacent context и reference: сообщить известные omission/inclusion различия и разделить tool reference recovery, execution, KG route union и endpoint answer.

Это описательное межстатейное сопоставление с пометками источника/условия/метрики, без механического вычитания score и без нового harmonized transfer estimate. Appendix O непосредственно обозначается как предшествующий KG эксперимент; точное row overlap остаётся неустановленным. Полную семимотивную матрицу переносить в Appendix, если компактная таблица перегружает основной текст. Исходный Tool тезис подкрепляется цитатой на его таблицу, а не выдаётся за новое измерение этой работы.

Источники: [contribution_comparison.md](contribution_comparison.md), [transfer_positioning.md](transfer_positioning.md), supplied Tool PDF Section 5.3/Table 1 and Appendix O, текущие saved KG summaries. Ближайшая роль прежней таблицы «prior/increment» сохраняется внутри этой сопоставительной таблицы; отдельный её дубль не нужен.

## Таблица 2. Диагностика ошибок на одних и тех же заданиях

**Обновление по указанию автора:** основной вариант таблицы 2 теперь показывает только Precision, Recall и Exact для **всех трёх моделей**, включая Gemma, в шестинодовых Tree-in K1/K3/K4/K7. Плановые и valid counts сохраняются для прозрачности failure policy. Готовые значения: [table2_treein_metrics_all_models.csv](analyses/main_claim_assets/run-05/table2_treein_metrics_all_models.csv); [просмотр](../figures/treein_metrics_v1/table2_treein_metrics_all_models.png). Таблица не требует selected identities. Gemma полностью представлен метриками; ниже сохранена прежняя идея identity-level переходов как supplementary analysis, а не основание исключать Gemma из основной таблицы.

**Какой вопрос поддерживает:** какие наблюдения позволяют формулировать гипотезы о причинах неполной выборки после предъявления связей?

Использовать уже отобранный [table2_signature_transitions.csv](analyses/main_claim_assets/run-02/table2_signature_transitions.csv). Шесть строк: Qwen/Ministral × K1→K3/K4/K7. Показать exact до→после, one-hop до→после, one-hop→exact с условным знаменателем, утраченные exact и invalid. Это отдельная six-node Tree-in диагностика, а не описание всех мотивов.

**Допустимый вывод:** при фактически одинаковых unique facts меняются конкретные ошибки и их переходы; исправления сосуществуют с регрессиями. Это совместимо с несколькими объяснениями, включая распределение/повторение evidence, но не идентифицирует внутренний алгоритм. Gemma имеет cached coarse metrics, но не selected identities для такой таблицы. Прежнее назначение таблицы 2 сохраняется; новый расчёт не требуется.

## Что уходит в приложение и что не требуется

Подробная stacked error-composition figure из `figure2_error_composition.csv`, полный каталог условий, дополнительные Exact/F1 values, naming/incremental материалы, analytical baselines и coverage details. Precision/recall теперь основные метрики, а не только supplementary. Исходные size endpoint tables остаются рядом с полными size curves/values по мере места. Не нужен дополнительный Sankey с теми же transition counts. Полная component heuristic не измерена и не включается как результат. Простые ограничивающие примеры диагностической неразличимости обсуждаются текстом.

## Соответствие цели

Тип мотива → рисунок 1. Количество узлов → рисунок 2. Доступность отношений → рисунки 2–3. Представление отношений → рисунок 3 и таблица 2. Структурные distractors → рисунки 1 и 3. Сходства/различия с Tool Selection → таблица 1. Гипотезы об ошибках → таблица 2 и Discussion.

Такой набор сохраняет структурный тезис центральным и использует диагностику для объяснения его границ. Он не обещает статистические взаимодействия, причинный механизм или полностью сопоставимый Tool/KG эксперимент, которых нет среди завершённых анализов.
