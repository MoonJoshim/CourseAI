"""엑셀에서 소프트웨어학과 과목을 추출해 JSON으로 저장하는 스크립트."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = PROJECT_ROOT / "course" / "2025-2.xlsx"
OUTPUT_PATH = PROJECT_ROOT / "frontend" / "react-app" / "src" / "data" / "softwareCourses.json"


def clean_string(value) -> str:
    if pd.isna(value):
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return str(value).strip()
    return str(value).strip()


def clean_number(value, default: int = 0):
    if pd.isna(value):
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        try:
            return float(value)
        except (ValueError, TypeError):
            return default


def load_courses() -> list[dict]:
    if not SOURCE_PATH.exists():
        raise FileNotFoundError(f"엑셀 파일이 존재하지 않습니다: {SOURCE_PATH}")

    df = pd.read_excel(SOURCE_PATH, header=2)
    df = df[df["과목명"].notna()].copy()
    df.fillna("", inplace=True)

    if "소속" in df.columns:
        df = df[df["소속"] == "소프트웨어학과"]
    else:
        df = df[df["개설\n전공"].fillna("").str.contains("소프트웨어", na=False)]

    courses: list[dict] = []
    for _, row in df.iterrows():
        course = {
            "course_id": clean_string(row.get("과목\nID") or row.get("수강\n번호")),
            "course_name": clean_string(row.get("과목명")),
            "professor": clean_string(row.get("담당\n교수")),
            "department": clean_string(row.get("소속") or row.get("개설\n전공")),
            "major": clean_string(row.get("개설\n전공")),
            "semester": "2025-2",
            "credits": clean_number(row.get("학점")),
            "hours": clean_number(row.get("시간")),
            "course_code": clean_string(row.get("교과목\n코드")),
            "lecture_time": clean_string(row.get("강의\n시간명")),
            "lecture_method": clean_string(row.get("분반별\n수업\n방식") or row.get("수업\n방식")),
            "class_type": clean_string(row.get("분반별\n수업\n방법") or row.get("과목\n특성")),
            "course_english_name": clean_string(row.get("과목\n영문명")),
            "target_grade": clean_string(row.get("수강\n대상\n학년")),
            "subject_id": clean_string(row.get("과목\nID")),
            "course_type": clean_string(row.get("학수\n구분")),
            "subject_type": clean_string(row.get("교과\n구분")),
            "details": {
                "lecture_method": clean_string(row.get("분반별\n수업\n방식") or row.get("수업\n방식")),
                "room": "",
                "time_slot": clean_string(row.get("강의\n시간명")),
                "assignment": "정보 없음",
                "attendance": "정보 없음",
                "exam": "정보 없음",
                "team_project": "정보 없음",
            },
            "average_rating": 0.0,
            "total_reviews": 0,
            "rating": 0.0,
            "tags": ["소프트웨어학과", "2025-2학기"],
        }

        if not course["course_id"]:
            course["course_id"] = course["course_code"] or course["course_name"]

        courses.append(course)

    return courses


def main() -> None:
    courses = load_courses()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(courses, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ 총 {len(courses)}개의 소프트웨어학과 과목을 {OUTPUT_PATH} 에 저장했습니다.")


if __name__ == "__main__":
    main()


