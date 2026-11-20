"""Математическое ядро: расчёт квартилей, границ Z-score / IQR, фильтрация и импутация."""

from telemetry_cleaner import config


def build_series_16h(student_n: int) -> list[float]:
    """Генерирует 16-часовой ряд забойного давления по номеру студента N."""
    base = 180.0 + 2.5 * student_n
    step = float(student_n % 4) + 1.5
    return [round(base + k * step, 2) for k in config.OFFSETS_16H]


def build_series_12h(student_n: int) -> tuple[list[float], float, float]:
    """Генерирует 12-часовой ряд давления (Вариант А) и возвращает (ряд, p_min, p_max)."""
    p_base = 160.0 + 2.0 * student_n
    step = float((student_n % 4) + 1)
    series = [round(p_base + k * step, 2) for k in config.OFFSETS_12H]
    p_min = round(p_base - 10.0 * step, 2)
    p_max = round(p_base + 10.0 * step, 2)
    return series, p_min, p_max


def calc_mean(series: list[float]) -> float:
    """Среднее арифметическое ряда."""
    if not series:
        raise ValueError("Пустой числовой ряд")
    total = 0.0
    for x in series:
        total += x
    return total / len(series)


def calc_median(series: list[float]) -> float:
    """Медиана числового ряда."""
    n = len(series)
    if n == 0:
        raise ValueError("Пустой числовой ряд")
    ordered = sorted(series)
    mid = n // 2
    if n % 2 == 1:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2.0


def calc_std(series: list[float], mean_val: float) -> float:
    """Выборочное стандартное отклонение ряда."""
    if not series:
        raise ValueError("Пустой числовой ряд")
    sq_sum = 0.0
    for x in series:
        sq_sum += (x - mean_val) ** 2
    return (sq_sum / len(series)) ** 0.5


def calc_range(series: list[float]) -> tuple[float, float, float]:
    """Возвращает (минимум, максимум, размах вариации) за один проход."""
    if not series:
        raise ValueError("Пустой числовой ряд")
    lo = hi = series[0]
    for val in series[1:]:
        if val < lo:
            lo = val
        if val > hi:
            hi = val
    return lo, hi, round(hi - lo, 2)


def calc_quartiles_iqr(series: list[float]) -> tuple[float, float, float]:
    """Вычисляет первый квартиль Q1, третий квартиль Q3 и межквартильный размах IQR.

    Используется метод Тьюки (медианы младшей и старшей половин отсортированного ряда).
    """
    n = len(series)
    if n < 4:
        raise ValueError("Для расчёта квартилей нужно минимум 4 элемента")
    ordered = sorted(series)
    mid = n // 2
    lower_half = ordered[:mid]
    upper_half = ordered[mid:] if n % 2 == 0 else ordered[mid + 1 :]
    q1 = calc_median(lower_half)
    q3 = calc_median(upper_half)
    return q1, q3, round(q3 - q1, 2)


def get_zscore_bounds(series: list[float], k: float = config.Z_K) -> tuple[float, float]:
    """Возвращает границы нормального коридора [mean - k*std; mean + k*std]."""
    m = calc_mean(series)
    s = calc_std(series, m)
    return round(m - k * s, 2), round(m + k * s, 2)


def get_iqr_bounds(
    series: list[float], factor: float = config.IQR_FACTOR
) -> tuple[float, float]:
    """Возвращает робастные границы Тьюки [Q1 - factor*IQR; Q3 + factor*IQR]."""
    q1, q3, iqr = calc_quartiles_iqr(series)
    return round(q1 - factor * iqr, 2), round(q3 + factor * iqr, 2)


def filter_by_bounds(series: list[float], low: float, high: float) -> list[float]:
    """Возвращает новый список только из нормальных значений в пределах [low; high]."""
    return [x for x in series if low <= x <= high]


def impute_with_median(series: list[float], low: float, high: float) -> list[float]:
    """Возвращает ряд исходной длины, где выбросы заменены на медиану ряда."""
    med = round(calc_median(series), 2)
    return [x if low <= x <= high else med for x in series]


def replace_outliers_with_neighbor_avg(
    series: list[float], low: float, high: float
) -> list[float]:
    """Заменяет выброс полусуммой двух соседних точек (для крайних - на медиану)."""
    n = len(series)
    med = round(calc_median(series), 2)
    result: list[float] = []
    for i, x in enumerate(series):
        if low <= x <= high:
            result.append(x)
        else:
            if i == 0:
                result.append(series[1] if n > 1 else med)
            elif i == n - 1:
                result.append(series[n - 2] if n > 1 else med)
            else:
                result.append(round((series[i - 1] + series[i + 1]) / 2.0, 2))
    return result
