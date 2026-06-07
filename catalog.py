from dataclasses import dataclass

from calculators import (
    Calculator,
    calculate_calories,
    calculate_fuel,
    calculate_gaming,
    calculate_reading,
    calculate_steps,
    calculate_water,
)


@dataclass(frozen=True)
class Field:
    key: str
    label_key: str
    unit_key: str
    example: str
    default: str = ""


@dataclass(frozen=True)
class Mode:
    key: str
    label_key: str
    fields: tuple[Field, ...]


@dataclass(frozen=True)
class Tool:
    key: str
    short_key: str
    badge: str
    title_key: str
    subtitle_key: str
    fact_key: str
    modes: tuple[Mode, ...]
    calculator: Calculator


TOOLS = (
    Tool("gaming", "gaming_short", "GT", "gaming_title", "gaming_subtitle", "gaming_fact", (
        Mode("hours_to_days", "mode_hours_days", (Field("amount", "field_hours", "unit_hours", "125"),)),
        Mode("days_to_hours", "mode_days_hours", (Field("amount", "field_days", "unit_days", "7"),)),
    ), calculate_gaming),
    Tool("reading", "reading_short", "RP", "reading_title", "reading_subtitle", "reading_fact", (
        Mode("pages_to_percent", "mode_pages_percent", (
            Field("current", "field_pages_read", "unit_pages", "120"),
            Field("total", "field_book_total", "unit_pages", "350"),
        )),
        Mode("percent_to_pages", "mode_percent_pages", (
            Field("percent", "field_progress", "unit_percent", "35"),
            Field("total", "field_book_total", "unit_pages", "350"),
        )),
    ), calculate_reading),
    Tool("calories", "calories_short", "CB", "calories_title", "calories_subtitle", "calories_fact", (
        Mode("walking", "mode_walking", (Field("weight", "field_weight", "unit_kg", "70"), Field("minutes", "field_duration", "unit_minutes", "45"))),
        Mode("running", "mode_running", (Field("weight", "field_weight", "unit_kg", "70"), Field("minutes", "field_duration", "unit_minutes", "30"))),
        Mode("cycling", "mode_cycling", (Field("weight", "field_weight", "unit_kg", "70"), Field("minutes", "field_duration", "unit_minutes", "60"))),
    ), calculate_calories),
    Tool("fuel", "fuel_short", "FC", "fuel_title", "fuel_subtitle", "fuel_fact", (
        Mode("trip_cost", "mode_trip_cost", (
            Field("distance", "field_distance", "unit_km", "420"),
            Field("consumption", "field_consumption", "unit_l100", "7.2"),
            Field("price", "field_fuel_price", "unit_currency_l", "7.45"),
        )),
        Mode("budget_distance", "mode_budget_distance", (
            Field("budget", "field_budget", "unit_currency", "250"),
            Field("consumption", "field_consumption", "unit_l100", "7.2"),
            Field("price", "field_fuel_price", "unit_currency_l", "7.45"),
        )),
    ), calculate_fuel),
    Tool("steps", "steps_short", "SD", "steps_title", "steps_subtitle", "steps_fact", (
        Mode("steps_to_distance", "mode_steps_distance", (
            Field("steps", "field_steps", "unit_steps", "10000"),
            Field("stride", "field_stride", "unit_cm", "75", "75"),
        )),
        Mode("distance_to_steps", "mode_distance_steps", (
            Field("distance", "field_distance", "unit_km", "5"),
            Field("stride", "field_stride", "unit_cm", "75", "75"),
        )),
    ), calculate_steps),
    Tool("water", "water_short", "WI", "water_title", "water_subtitle", "water_fact", (
        Mode("daily_goal", "mode_daily_goal", (
            Field("weight", "field_weight", "unit_kg", "70"),
            Field("activity", "field_activity", "unit_minutes", "45", "0"),
        )),
        Mode("glasses_to_liters", "mode_glasses_liters", (
            Field("glasses", "field_glasses", "unit_glasses", "8"),
            Field("glass_size", "field_glass_size", "unit_ml", "250", "250"),
        )),
    ), calculate_water),
)

TOOLS_BY_KEY = {tool.key: tool for tool in TOOLS}
