# Scientific and presentation review of the recall revision

26 октября 2026. Проверена текущая версия `paper/manuscript/main.tex`, восемь активных `*_recall_*` sections, пять графиков, две основные и две включённые supplementary таблицы, bibliography и все десять страниц PDF. Это проверка тем же агентом, а не независимое рецензирование.

## Что изменено и проверено

- Исходный тезис о pattern dependence в Tool Selection вынесен в Introduction. Section 5.3/Table 1 и Appendix O исходной статьи различаются: adjusted Tree-in не приравнивается к raw difficulty или KG incoming-tree errors.
- Первый Tool-to-KG перенос, Chain inversion и adjacent effects обозначены как antecedent findings. Вклад сформулирован как дополнительный evidence/presentation анализ и локализация остаточных ошибок, а не первое открытие, новый dataset или алгоритм.
- Recall — основная метрика; precision отдельно в приложении. Переноса F1/exact intervals на recall нет. Таблицы 1 и 2 имеют модели по строкам; таблица 2 включает Gemma и сохраняет planned N и invalid outcomes.
- Все отображаемые source rows графиков сопоставлены с исходными aggregate CSV; значения таблиц и направления разностей проверены. Числа Abstract/Results относятся к разным явно различённым панелям. Модельные ответы заново не генерировались и не пересчитывались.
- Current code symbols, frozen-reference audit и историческое выполнение разведены. Определение W, endpoint answer, минимальный evidence и card necessity не смешиваются. Ограничения Raw sufficiency и отдельного graph-component baseline указаны.
- One-hop outputs описаны как наблюдаемые конечные множества; коррекции и регрессии сохранены. Неполные Gemma identities не мешают aggregate метрикам, но не восстанавливаются из них. Разбор не выдаётся за внутреннюю траекторию.
- Web relevance дана на первой странице через reliability of connected evidence selection для корпоративных Web knowledge graphs, без заявления измеренных downstream QA gains.
- Новая ссылка GraphWalk проверена по primary arXiv v1: metadata и утверждение о неполном exploration. Остальные записи сохранены из ранее проверенной библиографии. Не придуманы DOI, авторы или publication acceptance для анонимного Tool Graph источника.
- Все десять страниц просмотрены; фигуры читаемы, нет обрезанных подписей, overfull boxes, unresolved references или citation keys. Шрифты embedded; PDF metadata не содержит авторских имён. Стандартная опция acmart `balance=false` отключает только балансировку последней страницы; class, margins и fonts не изменены.

## Оставшиеся существенные ограничения

**Высокая важность: точное пересечение с Appendix O и eligibility подачи.** Текст честно исключает независимую репликацию и новый transfer experiment; row-level overlap не установлен. Авторам перед подачей требуется оценить самостоятельность вклада и применимость originality/concurrent-submission правил к реальному статусу связанной работы. Эта сборка не подтверждает её текущий статус и не заменяет авторское решение.

**Умеренная важность: ограниченная интерпретация.** Мотивы меняют query semantics и typed entities, size cohorts различаются, K4 меняет повторение/заметность/длину. Независимый причинный topology/evidence mechanism и statistical interactions не установлены. Эти ограничения отражены в основном тексте.

**Умеренная важность: историческая воспроизводимость.** Native sufficiency, полный source graph, часть raw replies/settings и incremental histories недоступны в проверенном объёме. Воспроизводимы сохранённые summaries и frozen checks; это не сертификат полного повторения исходного эксперимента.

**Техническая область проверки.** `manuscript_claim_map.json` даёт 70 paragraph/asset bindings, а не автоматическое доказательство каждого предложения. Scoped structural validation проходит; общий реестр сохраняет 39 старых LF/CRLF hash mismatches с ранее записанным доказательством. Хеши не обновлялись массово ради зелёной проверки.

## Решение

Готов обновлённый ограниченный английский черновик и проверенный PDF. Дальнейшее независимое scientific review и решение о подаче остаются за авторами. Публикационная новизна, соответствие originality по отношению к другой заявке и acceptance не сертифицированы. Никакая внешняя загрузка, отправка, сообщение соавторам или новый эксперимент не выполнялись.
