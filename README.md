# Enron Graph: Communities & Roles

Анализ графа переписки **Enron**: поиск сообществ (Louvain/Leiden) и выявление **ролей узлов** через центральности + кластеризацию.

---

## Возможности

* Загрузка графа из **edge list** (текстовый файл `u v` на строку).
* Предобработка: симметризация (неориентированный граф), выбор **наибольшей компоненты связности**, удаление изолятов.
* Поиск сообществ: **Louvain** (по умолчанию) и **Leiden** (опционально).
* Роли узлов: вычисление метрик (degree, betweenness, closeness, PageRank, clustering coeff) → **k-means** (автовыбор k по silhouette) или фиксированный `--k`.
* Метрики: **modularity Q** (для сообществ), **silhouette** (для ролей — в логах при автоподборе).
* Визуализация: цвет = сообщество, размер = степень (можно поменять), подписи топ-хабов.
* Результаты сохраняются в `results/` (таблица ролей + PNG с визуализацией).

---

## Структура проекта

```
graph_roles_enron/
  data/
    email-enron.txt        # edge list (u v) — твой найденный файл
  results/
  src/
    __init__.py
    datasets.py
    preprocess.py          # (не обязателен — логика сейчас в datasets.py)
    communities.py
    roles.py
    viz.py
    run.py
  requirements.txt
  README.md                # этот файл
```

> **Примечание:** если файла `preprocess.py` нет — значит предобработка идёт прямо в `datasets.py`.

---

## Требования

* **Python 3.10+** (рекомендуется; Louvain работает и на 3.8, но стек обновлён под 3.10).
* Библиотеки: `networkx`, `pandas`, `numpy`, `scikit-learn`, `matplotlib`, `cdlib`. Для **Leiden** потребуется `python-igraph` и `leidenalg`.

`requirements.txt` (минимум):

```
networkx>=3.2
pandas>=2.2
numpy>=1.26
scikit-learn>=1.4
matplotlib>=3.8
cdlib>=0.3.0
python-igraph>=0.11
leidenalg>=0.10
```

Если установка `python-igraph`/`leidenalg` сложная — убери их из `requirements.txt` и используй `--algo louvain`.

---

## Быстрый старт

### 1) Создать окружение на Python 3.10

```bash
python3.10 --version         # убедись, что установлен
python3.10 -m venv .venv
source .venv/bin/activate
python --version             # должно быть Python 3.10.x
```

### 2) Установка зависимостей

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> Если `python-igraph`/`leidenalg` не ставятся: временно удали их из `requirements.txt` и работай с Louvain.

### 3) Данные

Положи **edge list** в `data/email-enron.txt`. Формат строк:

```
sender@example.com recipient@example.com
another@enron.com someone@enron.com
```

Без заголовков; комментарии с `#` допускаются и игнорируются.

### 4) Запуск

```bash
# Louvain (по умолчанию)
python -m src.run --data data/email-enron.txt --algo louvain

# Leiden (если установлен python-igraph + leidenalg)
python -m src.run --data data/email-enron.txt --algo leiden

# Зафиксировать число ролей (k-means)
python -m src.run --data data/email-enron.txt --algo louvain --k 4
```

После запуска в консоли появится, например:

```
[INFO] communities: 42 | modularity Q=0.6841
[INFO] roles: k=4
[INFO] saved plot -> results/enron_louvain_roles.png
```

Файлы:

* `results/node_roles.csv` — таблица признаков + метки ролей для каждого узла.
* `results/enron_<algo>_roles.png` — визуализация.

---

## Детали алгоритмов

* **Louvain** — двухфазная жадная оптимизация модульности (локальные перемещения узлов → агрегация сообществ в суперузлы → повторение). Быстрый, но может давать несвязные сообщества и нестабильные разбиения.
* **Leiden** — улучшение Louvain (добавляет фазу улучшения кластеров, гарантирует связность сообществ, стабильнее; обычно даёт выше Q). Требует `igraph + leidenalg`.

Метрика:

* **Modularity (Q)**: чем выше, тем «чётче» сообщества. Сравни Louvain vs Leiden на твоём графе.
* **Silhouette** для ролей: выводится в логах при автоподборе `k` (если включён).

---

## Роли узлов (baseline)

Фичи по каждому узлу:

* `degree`, `betweenness`, `closeness`, `pagerank`, `clustcoef`.

Кластеризация:

* **k-means** по стандартизированным фичам.
* `--k` — зафиксировать число ролей. Если не задан, подбирается по **silhouette** в диапазоне `2..6` (можно поменять в `roles.py`).

Интерпретация (пример):

* **Хабы** (высокий degree/PageRank).
* **Мосты** (высокая betweenness, средняя степень).
* **Периферия** (низкие степени, высокие clustcoef внутри сообществ).

---

## Визуализация

* Лэйаут: `spring_layout(seed=42)` по умолчанию.
* **Цвет** узла — номер сообщества.
* **Размер** узла — степень (`degree * 2`, но не меньше 50). Можно изменить в `viz.py`.
* Подписи: топ-20 узлов по степени (чтобы не захламлять граф).

Если граф слишком большой:

* Визуализируй **индуцированный подграф** топ-узлов по степени/центральности.
* Или отрисуй **метаграф сообществ** (каждое сообщество как один узел; опционально, не включено в MVP).

---

## Повторяемость

* Во многих шагах задан `random_state=42`. Для полной детерминированности:

  * фиксируй сиды в `numpy`, `random` и, при необходимости, в `networkx` лэйаутах.

---

## Производительность и память

* Email-Enron (SNAP) \~36k узлов / \~184k рёбер → помещается в память без проблем.
* Если у тебя полные сырые письма (CMU), сначала конвертируй в edge list (см. ниже), затем можно фильтровать домены или редкие адреса.

---



