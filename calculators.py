from dataclasses import dataclass
from math import isfinite
from typing import Callable


Translator = Callable[..., str]


@dataclass(frozen=True)
class CalculationResult:
    value: float
    unit_key: str
    detail: str
    stats: tuple[tuple[str, str], tuple[str, str]]


def format_number(value: float, decimals: int = 2) -> str:
    text = f"{value:,.{decimals}f}"
    return text.rstrip("0").rstrip(".")


def duration_text(total_hours: float, tr: Translator) -> str:
    total_minutes = round(total_hours * 60)
    days, remaining = divmod(total_minutes, 24 * 60)
    hours, minutes = divmod(remaining, 60)
    parts = []
    if days:
        parts.append(f"{days} {tr('day_one' if days == 1 else 'day_many')}")
    if hours:
        parts.append(f"{hours} {tr('hour_one' if hours == 1 else 'hour_many')}")
    if minutes or not parts:
        parts.append(
            f"{minutes} {tr('minute_one' if minutes == 1 else 'minute_many')}"
        )
    return ", ".join(parts)


def parse_number(raw_value: str, tr: Translator) -> float:
    value = raw_value.strip().replace(" ", "")
    if not value:
        raise ValueError(tr("error_required"))

    if "," in value and "." in value:
        if value.rfind(",") > value.rfind("."):
            value = value.replace(".", "").replace(",", ".")
        else:
            value = value.replace(",", "")
    else:
        value = value.replace(",", ".")

    try:
        number = float(value)
    except ValueError as error:
        raise ValueError(tr("error_number")) from error

    if not isfinite(number):
        raise ValueError(tr("error_finite"))
    if number < 0:
        raise ValueError(tr("error_negative"))
    if number > 100_000_000:
        raise ValueError(tr("error_too_large"))
    return number


def calculate_gaming(
    values: dict[str, float], mode: str, tr: Translator
) -> CalculationResult:
    amount = values["amount"]
    hours = amount if mode == "hours_to_days" else amount * 24
    result = hours / 24 if mode == "hours_to_days" else hours
    unit_key = "unit_days" if mode == "hours_to_days" else "unit_hours"
    return CalculationResult(
        result,
        unit_key,
        duration_text(hours, tr),
        (
            (tr("stat_weeks"), format_number(hours / 168)),
            (tr("stat_sessions"), format_number(hours / 4, 1)),
        ),
    )


def calculate_reading(
    values: dict[str, float], mode: str, tr: Translator
) -> CalculationResult:
    total = values["total"]
    if total <= 0:
        raise ValueError(tr("error_total_positive"))

    if mode == "pages_to_percent":
        current = values["current"]
        if current > total:
            raise ValueError(tr("error_pages_over_total"))
        percent = current / total * 100
        detail = tr(
            "detail_read_pages",
            current=format_number(current),
            total=format_number(total),
        )
        result = percent
        unit_key = "unit_percent"
    else:
        percent = values["percent"]
        if percent > 100:
            raise ValueError(tr("error_percent"))
        result = total * percent / 100
        detail = tr(
            "detail_read_percent",
            percent=format_number(percent),
            total=format_number(total),
        )
        unit_key = "unit_pages"

    return CalculationResult(
        result,
        unit_key,
        detail,
        (
            (tr("stat_pages_left"), format_number(total - total * percent / 100)),
            (tr("stat_progress"), f"{format_number(percent, 1)}%"),
        ),
    )


ACTIVITY_MET = {"walking": 4.3, "running": 8.3, "cycling": 7.5}


def calculate_calories(
    values: dict[str, float], mode: str, tr: Translator
) -> CalculationResult:
    weight = values["weight"]
    minutes = values["minutes"]
    if weight == 0 or minutes == 0:
        raise ValueError(tr("error_weight_duration"))

    calories = ACTIVITY_MET[mode] * 3.5 * weight / 200 * minutes
    return CalculationResult(
        calories,
        "unit_kcal",
        tr(
            "detail_calories",
            activity=tr(f"activity_{mode}"),
            minutes=format_number(minutes),
        ),
        (
            (tr("stat_kcal_hour"), format_number(calories / minutes * 60)),
            (tr("stat_meals"), format_number(calories / 600, 1)),
        ),
    )


def calculate_fuel(
    values: dict[str, float], mode: str, tr: Translator
) -> CalculationResult:
    consumption = values["consumption"]
    price = values["price"]
    if consumption == 0 or price == 0:
        raise ValueError(tr("error_consumption_price"))

    if mode == "trip_cost":
        distance = values["distance"]
        liters = distance * consumption / 100
        result = liters * price
        unit_key = "unit_currency"
        detail = tr(
            "detail_trip",
            distance=format_number(distance),
            liters=format_number(liters),
        )
        second_stat = ("stat_cost_100", consumption * price)
    else:
        budget = values["budget"]
        liters = budget / price
        result = liters / consumption * 100
        unit_key = "unit_km"
        detail = tr(
            "detail_budget",
            budget=format_number(budget),
            liters=format_number(liters),
        )
        second_stat = ("stat_cost_km", consumption * price / 100)

    return CalculationResult(
        result,
        unit_key,
        detail,
        (
            (tr("stat_liters"), format_number(liters)),
            (tr(second_stat[0]), format_number(second_stat[1])),
        ),
    )


def calculate_steps(
    values: dict[str, float], mode: str, tr: Translator
) -> CalculationResult:
    stride_cm = values["stride"]
    if stride_cm == 0:
        raise ValueError(tr("error_stride"))

    if mode == "steps_to_distance":
        steps = values["steps"]
        distance = steps * stride_cm / 100_000
        result = distance
        unit_key = "unit_km"
    else:
        distance = values["distance"]
        steps = distance * 100_000 / stride_cm
        result = steps
        unit_key = "unit_steps"

    calories = steps * 0.04
    walking_minutes = distance / 5 * 60
    return CalculationResult(
        result,
        unit_key,
        tr(
            "detail_steps",
            steps=format_number(steps, 0),
            distance=format_number(distance),
        ),
        (
            (tr("stat_walk_time"), f"{format_number(walking_minutes, 0)} min"),
            (tr("stat_kcal_est"), format_number(calories, 0)),
        ),
    )


def calculate_water(
    values: dict[str, float], mode: str, tr: Translator
) -> CalculationResult:
    if mode == "daily_goal":
        liters = values["weight"] * 0.033 + values["activity"] / 30 * 0.35
        detail = tr("detail_water_goal")
    else:
        liters = values["glasses"] * values["glass_size"] / 1000
        detail = tr(
            "detail_water_glasses",
            glasses=format_number(values["glasses"]),
            size=format_number(values["glass_size"]),
        )

    return CalculationResult(
        liters,
        "unit_liters_day" if mode == "daily_goal" else "unit_liters",
        detail,
        (
            (
                tr("stat_glasses_250" if mode == "daily_goal" else "stat_milliliters"),
                format_number(liters * 4, 1)
                if mode == "daily_goal"
                else format_number(liters * 1000, 0),
            ),
            (tr("stat_bottles_500"), format_number(liters * 2, 1)),
        ),
    )


Calculator = Callable[[dict[str, float], str, Translator], CalculationResult]
