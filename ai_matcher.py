"""
AI-Powered College Matching Engine
Edu Navigator's unique selling point: matches students with colleges based on
qualifications, GPA, preferences, budget, and scholarship needs.
"""

import json
import re
from typing import Optional


def _normalize_location(loc_str: Optional[str]) -> str:
    """Normalize location string for comparison."""
    if not loc_str:
        return ""
    return loc_str.strip().lower().replace(",", " ")


def _location_match_score(pref_location: str, college_city: str, college_district: str) -> float:
    """
    Returns 0-100: 100 if exact match, partial if related, 70 if no preference.
    """
    if not pref_location:
        return 70  # No preference = neutral score
    pref = _normalize_location(pref_location)
    city = _normalize_location(college_city)
    district = _normalize_location(college_district)
    if pref in city or pref in district or city in pref or district in pref:
        return 100
    # Partial word match (e.g., "Kathmandu" vs "Kathmandu Valley")
    pref_words = set(pref.split())
    loc_words = set((city + " " + district).split())
    if pref_words & loc_words:
        return 95
    return 40  # Different location


def _normalize_preferences(prefs) -> list:
    """Normalize preferences to a list of lowercase strings."""
    if not prefs:
        return []
    if isinstance(prefs, str):
        prefs = [p.strip() for p in prefs.split(",") if p.strip()]
    return [str(p).strip().lower() for p in prefs if str(p).strip()]


def safe_float(val, default=0.0):
    try:
        if val is None: return default
        return float(val)
    except (ValueError, TypeError):
        return default

def compute_match_scores(profile: dict, program_dict: dict, college_dict: dict) -> dict:
    """
    Compute individual component scores and total compatibility.
    Returns dict with scores and human-readable match_reasons.
    """
    student_gpa = safe_float(profile.get("gpa", 0))
    preferences = _normalize_preferences(profile.get("preferences"))
    wants_scholarship = profile.get("wants_scholarship", False)
    max_fees = safe_float(profile.get("max_fees", 0))
    pref_location = (profile.get("location") or "").strip()

    req_gpa = safe_float(program_dict.get("gpa_requirement", 0))
    fees = safe_float(program_dict.get("fees", 0))
    name_lower = (program_dict.get("name") or "").lower()
    field_lower = (program_dict.get("field") or "").lower()
    desc_lower = (program_dict.get("description") or "").lower()
    scholarship_available = college_dict.get("scholarship_available", False)
    popularity = college_dict.get("popularity_score", 50) or 50

    location_data = college_dict.get("location", {}) or {}
    college_city = location_data.get("city", "") or ""
    college_district = location_data.get("district", "") or ""

    match_reasons = []
    weights = {"gpa": 0.35, "budget": 0.25, "program": 0.20, "scholarship": 0.10, "location": 0.10}

    # 1. GPA Match (35%)
    if req_gpa == 0:
        gpa_score = 100
        match_reasons.append("No minimum GPA requirement")
    elif student_gpa >= req_gpa:
        gpa_score = 100
        margin = student_gpa - req_gpa
        match_reasons.append(f"Your GPA ({student_gpa}) meets the requirement ({req_gpa})" + (f" with room to spare" if margin >= 0.3 else ""))
    else:
        gap = req_gpa - student_gpa
        gpa_score = max(0, 100 - (gap * 60))
        match_reasons.append(f"GPA gap: you have {student_gpa}, program requires {req_gpa}")

    # 2. Budget vs Fees (25%)
    if fees == 0:
        budget_score = 100
        match_reasons.append("Fee info not available or program is free")
    elif max_fees == 0:
        budget_score = 0
        match_reasons.append(f"Program fee is NPR {fees:,.0f} but your budget is 0")
    elif fees <= max_fees:
        budget_score = 100
        match_reasons.append(f"Within your budget: NPR {fees:,.0f} ≤ NPR {max_fees:,.0f}")
    else:
        excess = fees - max_fees
        budget_penalty = min(80, (excess / max_fees) * 100)
        budget_score = max(0, 100 - budget_penalty)
        match_reasons.append(f"Over budget by NPR {excess:,.0f} — consider scholarship options")

    # 3. Program/Field Match (20%)
    if not preferences:
        program_score = 80  # Slight penalty for no preferences (less targeted)
        match_reasons.append("Add interests in your profile for better program matches")
    else:
        searchable = f"{name_lower} {field_lower} {desc_lower}"
        matches = []
        for p in preferences:
            # Match whole words to avoid partial matches (e.g. 'it' matching 'with')
            pattern = r'\b' + re.escape(p) + r'\b'
            if re.search(pattern, searchable):
                matches.append(p)
                
        if matches:
            program_score = 100
            match_reasons.append(f"Matches your interest: {', '.join(m.title() for m in matches)}")
        else:
            program_score = 0
            match_reasons.append("Does not match your stated interests")

    # 4. Scholarship (10%)
    if wants_scholarship:
        if scholarship_available:
            scholarship_score = 100
            match_reasons.append("This college offers scholarships")
        else:
            scholarship_score = 20
            match_reasons.append("No scholarship — you indicated you need financial aid")
    else:
        scholarship_score = 100
        if scholarship_available:
            match_reasons.append("Scholarship available if you change your mind")

    # 5. Location (10%)
    loc_score = _location_match_score(pref_location, college_city, college_district)
    if pref_location and loc_score >= 95:
        match_reasons.append(f"In your preferred area: {college_city or college_district}")
    elif pref_location and loc_score < 50:
        match_reasons.append(f"Different from preferred location ({pref_location})")

    # Popularity boost (small, folded into scholarship/location)
    pop_boost = min(10, (popularity / 10))
    total_score = (
        gpa_score * weights["gpa"]
        + budget_score * weights["budget"]
        + program_score * weights["program"]
        + scholarship_score * weights["scholarship"]
        + loc_score * weights["location"]
        + pop_boost
    )

    # Heavily penalize programs that completely mismatch stated interests
    if preferences and program_score == 0:
        total_score *= 0.2

    # Hard Requirements
    if req_gpa > 0 and student_gpa < req_gpa:
        total_score = 0
        match_reasons.insert(0, f"Does not meet minimum GPA requirement of {req_gpa}")
    elif field_lower == "engineering" and student_gpa < 2.4:
        total_score = 0
        match_reasons.insert(0, f"Engineering requires a minimum GPA, but you have {student_gpa}")

    total_score = min(100, max(0, round(total_score, 1)))

    return {
        "compatibility_score": total_score,
        "gpa_score": gpa_score,
        "budget_score": budget_score,
        "program_score": program_score,
        "scholarship_score": scholarship_score,
        "location_score": loc_score,
        "match_reasons": match_reasons[:4],  # Top 4 reasons
    }


def get_ai_matches(user, limit: int = 10, include_reasons: bool = True, search_query: Optional[str] = None, programs_data=None):
    """
    Get AI-powered college-program matches for a user.
    user can be a User model instance or None (returns generic matches).
    search_query: optional filter by college name, program name, or field.
    programs_data: list of (program, college) tuples - must be passed from app (avoids db context issues).
    """
    profile = user.get_profile_dict() if user and hasattr(user, "get_profile_dict") else {}
    if not profile and user:
        profile = {}

    if not programs_data:
        return []

    # Return no results if GPA is 2.0 or less, or 0
    gpa = float(profile.get("gpa", 0) or 0)
    if gpa <= 2.0:
        return []

    results = []
    search_lower = (search_query or "").strip().lower()

    for program, college in programs_data:
        if search_lower:
            college_name = (college.name or "").lower()
            prog_name = (program.name or "").lower()
            prog_field = (program.field or "").lower()
            prog_desc = (program.description or "").lower()
            searchable = f"{college_name} {prog_name} {prog_field} {prog_desc}"
            if search_lower not in searchable:
                continue
        if not college:
            continue

        program_dict = program.to_dict()
        college_dict = college.to_dict(include_programs=False, include_hostel=False)
        scores = compute_match_scores(profile, program_dict, college_dict)

        # Hard filter: if relying on profile preferences (no explicit search),
        # completely exclude programs that do not match the stated interests at all.
        prefs = profile.get("preferences", [])
        if prefs and not search_lower and scores["program_score"] == 0:
            continue

        program_dict["compatibility_score"] = scores["compatibility_score"]
        program_dict["college_location"] = ""
        program_dict["logo_url"] = college.logo_url
        if college.location:
            parts = [p for p in [college.location.city, college.location.district] if p]
            program_dict["college_location"] = ", ".join(parts)

        if include_reasons:
            program_dict["match_reasons"] = scores["match_reasons"]

        results.append((scores["compatibility_score"], program_dict))

    results.sort(key=lambda x: (-x[0], x[1]["name"]))
    return [r[1] for r in results[:limit]]


def get_match_summary(profile: dict) -> dict:
    """
    Returns a summary of what the matcher knows about the user for chat context.
    """
    gpa = profile.get("gpa") or 0
    prefs = profile.get("preferences") or []
    max_fees = profile.get("max_fees") or 0
    wants_scholarship = profile.get("wants_scholarship", False)
    location = profile.get("location") or ""

    parts = []
    if gpa:
        parts.append(f"GPA {gpa}")
    if prefs:
        parts.append(f"interests in {', '.join(str(p) for p in prefs)}")
    if max_fees:
        parts.append(f"budget up to NPR {max_fees:,.0f}")
    if wants_scholarship:
        parts.append("needs scholarship")
    if location:
        parts.append(f"preferred location: {location}")

    return {
        "has_data": bool(parts),
        "summary": ", ".join(parts) if parts else "basic profile",
        "missing": [],
    }
