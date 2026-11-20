"""Скрипт выполнения всех 7 обязательных исследовательских упражнений (Раздел 8).

Студент: Мусин Тимур Булатович, гр. БЦШ02-26-02, Вариант N = 17
"""

import sys
from pathlib import Path

# Добавляем src в пути поиска модулей
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from telemetry_cleaner import config, detectors


def run_exercise_1(series: list[float], student_n: int) -> None:
    print("\n" + "=" * 76)
    print("УПРАЖНЕНИЕ 1. ЧУВСТВИТЕЛЬНОСТЬ ПОРОГА Z-ОЦЕНКИ (k = 1.5 против k = 3.0)")
    print("=" * 76)
    m = detectors.calc_mean(series)
    s = detectors.calc_std(series, m)
    print(f"Базовый ряд (N = {student_n}, 16 ч): Mean = {m:.2f} атм, Std = {s:.2f} атм\n")
    print(f"{'Коэффициент k':<16}{'Нижняя граница':<18}{'Верхняя граница':<18}{'Найденные часы выбросов':<24}")
    print("-" * 76)
    for k in [1.5, 2.0, 3.0]:
        low, high = round(m - k * s, 2), round(m + k * s, 2)
        outliers = [idx + 1 for idx, x in enumerate(series) if x < low or x > high]
        print(f"{k:<16.1f}{low:<18.2f}{high:<18.2f}{str(outliers):<24}")

    print("\n[ВЫВОД]")
    print(
        "• При жестком k = 1.5 границы сужаются, но на выборке с мощным всплеском Z-score все еще\n"
        "  находит только час 10, так как само СКО раздуто до 21.90 атм.\n"
        "• При мягком k = 3.0 («правило трех сигм») границы раздвигаются до [159.61; 291.01] атм.\n"
        "  Все умеренные сбои (час 5 и час 14) полностью пропускаются."
    )


def run_exercise_2(series: list[float]) -> None:
    print("\n" + "=" * 76)
    print("УПРАЖНЕНИЕ 2. ЭФФЕКТ МАСКИРОВАНИЯ ВЫБРОСОВ (MASKING EFFECT)")
    print("=" * 76)
    masked_series = list(series)
    # Заменяем всплеск на 10-м часу на 1000.0 атм
    masked_series[9] = 1000.0

    m = detectors.calc_mean(masked_series)
    s = detectors.calc_std(masked_series, m)
    low, high = round(m - 2.0 * s, 2), round(m + 2.0 * s, 2)
    outliers_z = [idx + 1 for idx, x in enumerate(masked_series) if x < low or x > high]

    print(f"Ряд со «шпилькой» 1000.0 атм на 10-м часу:")
    print(f"Среднее: {m:.2f} атм (было 225.31 атм)")
    print(f"СКО (sigma): {s:.2f} атм (было 21.90 атм — раздулось почти в 9 раз!)")
    print(f"Границы 2*sigma: [{low:.2f}; {high:.2f}] атм")
    print(f"Найденные выбросы по Z-score: {outliers_z}")

    print("\n[ВЫВОД]")
    print(
        "Экстремальный выброс 1000.0 атм колоссально увеличил сумму квадратов отклонений, из-за чего\n"
        "СКО взлетело до 188.99 атм, а нижняя граница опустилась до отрицательного значения -109.07 атм!\n"
        "В результате реальные сбои датчика (час 5: 200.0 атм и час 14: 195.0 атм) оказались внутри\n"
        "коридора нормы и были полностью замаскированы (Masking Effect)."
    )


def run_exercise_3(series: list[float]) -> None:
    print("\n" + "=" * 76)
    print("УПРАЖНЕНИЕ 3. ДВУХПРОХОДНАЯ (ИТЕРАТИВНАЯ) ОЧИСТКА РЯДА")
    print("=" * 76)
    masked_series = list(series)
    masked_series[9] = 1000.0  # Экстремальный выброс

    # Первый проход
    m1 = detectors.calc_mean(masked_series)
    s1 = detectors.calc_std(masked_series, m1)
    low1, high1 = round(m1 - 2.0 * s1, 2), round(m1 + 2.0 * s1, 2)
    pass1_cleaned = [x for x in masked_series if low1 <= x <= high1]
    pass1_outliers = [idx + 1 for idx, x in enumerate(masked_series) if x < low1 or x > high1]

    print(f"ПРОХОД 1: Mean = {m1:.2f}, Std = {s1:.2f}, Границы = [{low1:.2f}; {high1:.2f}]")
    print(f"Выбросы 1-го прохода (часы): {pass1_outliers}")

    # Второй проход по оставшимся точкам
    m2 = detectors.calc_mean(pass1_cleaned)
    s2 = detectors.calc_std(pass1_cleaned, m2)
    low2, high2 = round(m2 - 2.0 * s2, 2), round(m2 + 2.0 * s2, 2)
    final_outliers = [idx + 1 for idx, x in enumerate(masked_series) if x < low2 or x > high2]

    print(f"\nПРОХОД 2: Mean = {m2:.2f}, Std = {s2:.2f}, Скорректированные границы = [{low2:.2f}; {high2:.2f}]")
    print(f"Итоговые выбросы после 2-го прохода (часы): {final_outliers}")

    print("\n[ВЫВОД]")
    print(
        "Двухпроходная очистка успешно устранила эффект маскирования:\n"
        "После исключения «шпильки» 1000.0 атм на 1-м шаге, на 2-м шаге СКО вернулось к реальному уровню\n"
        f"(9.37 атм), границы сузились до [{low2}; {high2}], и алгоритм безошибочно выявил замаскированные\n"
        "провалы на 5-м (200.0 атм) и 14-м (195.0 атм) часах!"
    )


def run_exercise_4() -> None:
    print("\n" + "=" * 76)
    print("УПРАЖНЕНИЕ 4. ОПАСНОСТЬ УДАЛЕНИЯ ЭЛЕМЕНТОВ ВО ВРЕМЯ ИТЕРАЦИИ (.remove / .pop)")
    print("=" * 76)
    # Создаем ряд с двумя выбросами подряд (часы 4 и 5 со значениями 110.0 атм)
    test_list = [222.5, 225.0, 220.0, 110.0, 110.0, 222.5]
    stat_low = 181.51
    print(f"Исходный тестовый список: {test_list}")
    print(f"Порог отсечения снизу: {stat_low} атм")

    # Ошибочный алгоритм: удаление прямо в цикле
    faulty_list = list(test_list)
    for val in faulty_list:
        if val < stat_low:
            faulty_list.remove(val)

    print(f"Результат после ошибочного цикла for + .remove(): {faulty_list}")

    # Корректный алгоритм: сборка нового списка
    correct_list = [x for x in test_list if x >= stat_low]
    print(f"Результат правильной фильтрации (новый список):     {correct_list}")

    print("\n[ВЫВОД]")
    print(
        "При вызове .remove(val) элементы списка сдвигаются влево на один индекс. Внутренний итератор\n"
        "цикла for при этом увеличивает индекс на 1, перескакивая через следующий элемент.\n"
        "В итоге второй подряд выброс (110.0) остался в списке! Правильный подход — генерация нового\n"
        "списка через списковое включение [x for x in series if low <= x <= high]."
    )


def run_exercise_5(series: list[float]) -> None:
    print("\n" + "=" * 76)
    print("УПРАЖНЕНИЕ 5. ИМПУТАЦИЯ (ЗАМЕЩЕНИЕ) АНОМАЛИЙ СРЕДНИМ СОСЕДЕЙ")
    print("=" * 76)
    q1, q3, iqr = detectors.calc_quartiles_iqr(series)
    low_iqr, high_iqr = detectors.get_iqr_bounds(series)

    imputed_neighbors = detectors.replace_outliers_with_neighbor_avg(series, low_iqr, high_iqr)

    print(f"Исходный ряд (16 ч):                 {series}")
    print(f"Ряд после импутации средним соседей: {imputed_neighbors}")
    print(f"Выбросы на часах 5 (200.0) -> {imputed_neighbors[4]:.2f} атм (соседи 227.5 и 222.5)")
    print(f"Выброс  на часе 10 (302.5) -> {imputed_neighbors[9]:.2f} атм (соседи 227.5 и 217.5)")
    print(f"Выброс  на часе 14 (195.0) -> {imputed_neighbors[13]:.2f} атм (соседи 222.5 и 225.0)")

    print("\n[ВЫВОД]")
    print(
        "Импутация необходима в задачах анализа временных рядов с непрерывной сеткой (расчет скользящей\n"
        "средней, FFT-спектральный анализ, обучение ARIMA/LSTM моделей, прогнозирование), где удаление\n"
        "точек приводит к разрыву хронологии и искажению динамики процесса."
    )


def run_exercise_6(series: list[float]) -> None:
    print("\n" + "=" * 76)
    print("УПРАЖНЕНИЕ 6. ДОЛЯ БРАКОВАННОЙ ТЕЛЕМЕТРИИ (ПРОЦЕНТ ПОТЕРЬ ДАННЫХ)")
    print("=" * 76)
    low_iqr, high_iqr = detectors.get_iqr_bounds(series)
    anomalies = [(idx + 1, val) for idx, val in enumerate(series) if val < low_iqr or val > high_iqr]

    total_count = len(series)
    bad_count = len(anomalies)
    anomaly_rate = (bad_count / total_count) * 100.0

    if anomaly_rate <= 10.0:
        verdict = "Канал исправен"
    elif anomaly_rate <= 25.0:
        verdict = "Требуется калибровка датчика"
    else:
        verdict = "Авария телеметрии"

    print(f"Всего измерений в ряду:       {total_count} шт.")
    print(f"Обнаружено аномальных точек:  {bad_count} шт. (часы {[a[0] for a in anomalies]})")
    print(f"Доля брака (anomaly_rate):    {bad_count} / {total_count} * 100% = {anomaly_rate:.2f}%")
    print(f"Автоматический вердикт:       «{verdict}»")

    print("\n[ВЫВОД]")
    print(
        f"Для варианта N = 17 доля отбракованных данных составляет 18.75% (3 точки из 16).\n"
        "Это укладывается в нормативный диапазон 10%–25%, что соответствует статусу «Требуется калибровка датчика»."
    )


def run_exercise_7() -> None:
    print("\n" + "=" * 76)
    print("УПРАЖНЕНИЕ 7. ЗАЩИТА ОТ ВЫРОЖДЕННОГО РЯДА (ЗАЛИПАНИЕ ДАТЧИКА)")
    print("=" * 76)
    const_series = [222.5] * 16
    m = detectors.calc_mean(const_series)
    s = detectors.calc_std(const_series, m)
    q1, q3, iqr = detectors.calc_quartiles_iqr(const_series)

    print(f"Константный ряд (16 замеров по 222.5 атм): {const_series}")
    print(f"Среднее арифметическое: {m:.2f} атм")
    print(f"Стандартное отклонение σ: {s:.2f} атм")
    print(f"Первый квартиль Q1: {q1:.2f} атм, Третий квартиль Q3: {q3:.2f} атм, Размах IQR: {iqr:.2f} атм")

    # Проверка деления на 0
    test_val = const_series[0]
    z_score_safe = abs(test_val - m) / s if s > 0 else 0.0
    print(f"Безопасная Z-оценка: z = abs(val - mean) / std if std > 0 else 0.0 -> {z_score_safe}")

    print("\n[ВЫВОД]")
    print(
        "При эффекте «залипания» датчика все значения одинаковы, поэтому СКО σ = 0.0 и IQR = 0.0.\n"
        "Если в коде отсутствует проверка (std > 0), классическая формула z = abs(x - mean) / std\n"
        "приведет к критическому сбою программы ZeroDivisionError: float division by zero.\n"
        "Защита 'if std > 0 else 0.0' является обязательной практикой надежного промышленного кода."
    )


def main() -> None:
    student_n = 17
    series = detectors.build_series_16h(student_n)
    print(f"ЗАПУСК ВСЕХ 7 ОБЯЗАТЕЛЬНЫХ УПРАЖНЕНИЙ ДЛЯ N = {student_n}")
    print(f"Студент: Мусин Тимур Булатович | Группа: БЦШ02-26-02")
    run_exercise_1(series, student_n)
    run_exercise_2(series)
    run_exercise_3(series)
    run_exercise_4()
    run_exercise_5(series)
    run_exercise_6(series)
    run_exercise_7()
    print("\n" + "=" * 76)
    print("ВСЕ 7 УПРАЖНЕНИЙ УСПЕШНО ВЫПОЛНЕНЫ!")
    print("=" * 76)


if __name__ == "__main__":
    main()
