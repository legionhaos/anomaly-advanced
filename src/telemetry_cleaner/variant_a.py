"""Выявление аномалий и очистка ряда забойного давления скважины (Вариант А, 12 часов)."""

from telemetry_cleaner import detectors

Z_THRESHOLD = 2.0  # пороговый коэффициент k для правила k * sigma


def main() -> None:
    print("ПОИСК АНОМАЛИЙ И ОЧИСТКА РЯДА ЗАБОЙНОГО ДАВЛЕНИЯ (ВАРИАНТ А)")
    print("=" * 68)
    raw_n = input("Введите ваш номер по журналу N [по умолчанию 17]: ").strip()
    student_n = int(raw_n) if raw_n.isdigit() and int(raw_n) > 0 else 17
    print(f"Используется номер по журналу: N = {student_n}")

    pressures, tech_min, tech_max = detectors.build_series_12h(student_n)

    # Статистики сырого («грязного») ряда
    raw_mean = detectors.calc_mean(pressures)
    raw_med = detectors.calc_median(pressures)
    raw_std = detectors.calc_std(pressures, raw_mean)
    raw_min, raw_max, raw_rng = detectors.calc_range(pressures)

    # Статистические границы по правилу k * sigma
    stat_low = round(raw_mean - Z_THRESHOLD * raw_std, 2)
    stat_high = round(raw_mean + Z_THRESHOLD * raw_std, 2)

    print(f"\nИсходный ряд (12 ч): {pressures}")
    print(f"Тех. регламент: [{tech_min:.2f}; {tech_max:.2f}] атм")
    print(f"Границы {Z_THRESHOLD:.1f}*sigma: [{stat_low:.2f}; {stat_high:.2f}] атм")

    print("\nДЕТАЛЬНАЯ ТАБЛИЦА КОНТРОЛЯ ИЗМЕРЕНИЙ")
    print("-" * 68)
    print(
        f"{'Час':<5}{'P, атм':>10}{'Откл. от ср.':>14}{'Z-оценка':>11}{'Тех. коридор':>15}{'Статус точки':>13}"
    )
    print("-" * 68)

    for hour, val in enumerate(pressures, start=1):
        diff = val - raw_mean
        z_score = abs(diff) / raw_std if raw_std > 0 else 0.0
        in_tech = "ОК" if tech_min <= val <= tech_max else "НАРУШЕН"
        is_outlier = (val < stat_low or val > stat_high) or (in_tech == "НАРУШЕН")
        status = "ВЫБРОС!" if is_outlier else "Норма"

        print(
            f"{hour:<5}{val:>10.2f}{diff:>+14.2f}{z_score:>11.2f}{in_tech:>15}{status:>13}"
        )

    # Фильтрация ряда по статистическим границам
    cleaned_series = detectors.filter_by_bounds(pressures, stat_low, stat_high)
    found_anomalies = [
        (h, v)
        for h, v in enumerate(pressures, start=1)
        if v < stat_low or v > stat_high or not (tech_min <= v <= tech_max)
    ]

    # Статистики очищенного ряда
    cln_mean = detectors.calc_mean(cleaned_series)
    cln_med = detectors.calc_median(cleaned_series)
    cln_std = detectors.calc_std(cleaned_series, cln_mean)
    _, _, cln_rng = detectors.calc_range(cleaned_series)

    print("\nРЕЗУЛЬТАТ ФИЛЬТРАЦИИ АНОМАЛИЙ")
    print("-" * 68)
    print(f"Обнаружено выбросов: {len(found_anomalies)} шт. -> {found_anomalies}")
    print(f"Очищенный ряд ({len(cleaned_series)} ч): {cleaned_series}")

    print("\nСРАВНЕНИЕ СТАТИСТИК ДО И ПОСЛЕ ОЧИСТКИ")
    print("-" * 68)
    print(
        f"{'Показатель':<28}{'До очистки':>14}{'После очистки':>16}{'Изменение':>10}"
    )
    print("-" * 68)
    print(
        f"{'Среднее арифметическое, атм':<28}{raw_mean:>14.2f}{cln_mean:>16.2f}{cln_mean - raw_mean:>+10.2f}"
    )
    print(
        f"{'Медиана ряда, атм':<28}{raw_med:>14.2f}{cln_med:>16.2f}{cln_med - raw_med:>+10.2f}"
    )
    print(
        f"{'Стандартное отклонение, атм':<28}{raw_std:>14.2f}{cln_std:>16.2f}{cln_std - raw_std:>+10.2f}"
    )
    print(
        f"{'Размах вариации R, атм':<28}{raw_rng:>14.2f}{cln_rng:>16.2f}{cln_rng - raw_rng:>+10.2f}"
    )


if __name__ == "__main__":
    main()
