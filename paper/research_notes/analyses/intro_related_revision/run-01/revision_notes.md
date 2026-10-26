# Уточнение замысла и предложение двух разделов

26 октября 2026. Предложение для обсуждения, не замена активного manuscript/PDF. Уточнение пользователя: вопросы составлялись для полного отбора сущностей; основная задача — проверить перенос Tool Selection на KG Entity Selection. Этот замысел не следует сужать до одного лишь KG error analysis.

## Исправление предыдущей критики

Предыдущий отзыв преувеличивал неопределённость полного selection target и рекомендовал сделать перенос только мотивацией. Требование полного route-entity set явно выражено в сохранённой системной инструкции. Поэтому корректная рекомендация — объяснить его во введении, сохранив перенос центральной целью. Полный target и незаменимость каждой карточки остаются разными свойствами.

Непосредственно прочитан первый сохранённый input `000071451200148392a2dd08214e2974080d469fdc6ec61b6f3f321220fca8c4` в `results/inputs.jsonl.gz`. Selection instruction требует named starting entity, all endpoints, every intermediate и all parallel supporting routes; отдельно исключает утверждение independent card necessity. Вопрос запрашивает endpoint names/supporting links и исключает anchor как дополнительный обязательный ответ. Поэтому предлагаемая формулировка использует «selection protocol», а не утверждает идентичное требование во всех текстах вопросов.

## Научная логика

1. Tool Selection задаёт исходную проблему композиционного отбора.
2. KG предоставляет другую семантику рёбер и возможность предъявить связи явно.
3. Исследуется сохранение/изменение структурных профилей; transfer не означает обучение или перенос весов.
4. Первые Tool-to-KG observations уже есть в Appendix O; нынешние дополнительные свидетельства относятся к matched KG evidence/presentation contrasts и локальным output transitions.
5. Основные RQs: structural correspondence; dependence on evidence conditions; residual errors and paired changes.

Цель исследования шире его дополнительного вклада относительно Appendix O. Это различие сохранено в тексте. Новые условия внутри KG не объявлены новым гармонизированным Tool/KG arm, причинным substrate effect или самостоятельной репликацией.

## Related Work v4

Приложенный текст — полезная расширенная основа. Абзац structural tool selection перенесён первым как ближайший предшественник. Далее идут entity retrieval/QA, structure/representation, residual errors. В коротком варианте сохранены три новые проверенные ссылки: RoG, STaRK, G-Retriever. Их targets различены с exhaustive route coverage. Остальные пять новых leads не признаны ошибочными; их inclusion необязателен и зависит от места.

Новый вариант расположен в `paper/manuscript/proposals/transfer_intro_related_v1/`. Не подключён к `main.tex`. Добавочная bibliography находится рядом и не изменяет действующую.

## Проверки и ограничения

Независимый подагент прочитал оба предложенных раздела: существенных блокеров в ограниченном предложении не нашёл. Исправлены две его рекомендации: attribution exhaustive target именно selection protocol; narrower wording дополнительного вклада как assessment of KG profiles in relation to prior Tool-to-KG findings. Это scoped editorial/claim review, не независимая оценка полной статьи или её originality.

Другой подагент проверил новые literature leads по primary metadata и relevant text. RoG §4.1, STaRK §3.2, G-Retriever §§5.2–5.4 поддерживают только узкие comparison sentences. Даты проверки, версии и URLs — `source_checks.json`. Для старых источников использованы уже выполненные scoped audits; новый полный литературный поиск не заявляется.

Структурная проверка scoped evidence/claims, хешей и citation keys — `validation.json` и `static_checks.json`. Она не сертифицирует научную новизну и не заменяет общий реестр. Предыдущие LF/CRLF mismatches production evidence не исправлялись.

После принятия варианта нужно согласовать Abstract/Discussion и при необходимости порядок Results с transfer-first RQs. Никакие эксперименты, source-code edits, model/judge/database calls или внешняя публикация не выполнялись.
