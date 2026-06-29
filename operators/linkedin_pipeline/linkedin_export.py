"""Parser for LinkedIn data export (ZIP file with CSVs)."""

import csv
import zipfile
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


def parse_linkedin_export(zip_path: str | Path) -> Dict[str, Any]:
    """
    Parse LinkedIn data export ZIP file into structured profile data.
    
    Args:
        zip_path: Path to LinkedIn export ZIP file
        
    Returns:
        Dictionary with parsed profile data ready for ProfileVector
    """
    zip_path = Path(zip_path)
    
    if not zip_path.exists():
        raise FileNotFoundError(f"LinkedIn export not found: {zip_path}")
    if zip_path.is_dir():
        raise ValueError(f"Input path is a directory, not a zip file: {zip_path}")
    
    # Check if this is a basic export (only Profile.csv)
    with zipfile.ZipFile(zip_path, 'r') as zf:
        file_list = zf.namelist()
        if len(file_list) == 1 and "Profile.csv" in file_list[0]:
            return _parse_basic_profile_export(zf)
    
    # Full export with multiple CSVs
    data = {
        "positions": [],
        "education": [],
        "skills": [],
        "endorsements_received": [],
        "recommendations_received": [],
        "connections": [],
        "company_follows": [],
        "saved_job_alerts": [],
        "causes": [],
        "inferences": [],
        "articles": [],
    }

    with zipfile.ZipFile(zip_path, 'r') as zf:
        # Parse each relevant CSV
        data["positions"] = _parse_positions(zf)
        data["education"] = _parse_education(zf)
        data["skills"] = _parse_skills(zf)
        data["endorsements_received"] = _parse_endorsements_received(zf)
        data["recommendations_received"] = _parse_recommendations_received(zf)
        data["connections"] = _parse_connections(zf)
        data["company_follows"] = _parse_company_follows(zf)
        data["saved_job_alerts"] = _parse_saved_job_alerts(zf)
        data["causes"] = _parse_causes(zf)
        data["inferences"] = _parse_inferences(zf)
        data["articles"] = _parse_articles(zf)
    
    # Convert to ProfileVector-compatible format
    return _to_profile_vector_data(data)


def _parse_basic_profile_export(zf: zipfile.ZipFile) -> Dict[str, Any]:
    """Parse basic LinkedIn export (only Profile.csv)."""
    csv_data = zf.read("Profile.csv").decode('utf-8')
    reader = csv.DictReader(csv_data.splitlines())
    profile_row = list(reader)[0]  # Only one row
    
    headline = profile_row.get("Headline", "")
    summary = profile_row.get("Summary", "")
    
    # Extract titles from headline (e.g., "Strategy | Go-To-Market | Product")
    titles = [t.strip() for t in headline.split("|") if t.strip()]
    
    # Create synthetic positions
    positions = []
    for title in titles:
        positions.append({
            "company": "",
            "title": title,
            "description": summary[:200],
            "start": "",
            "end": "Present",
            "tenure_years": 2.0,
            "location": profile_row.get("Geo Location", ""),
        })
    
    # Extract skills from summary using keyword matching
    skill_keywords = [
        "agility", "data-driven", "iterative", "collaboration", "stakeholder management",
        "ambiguity", "pivoting", "multi-disciplinary", "measurable results",
        "strategic", "cross-functional", "product", "go-to-market", "GTM"
    ]
    skills = [kw for kw in skill_keywords if kw.lower() in summary.lower()]
    
    # Extract experience years from summary
    import re
    years_match = re.search(r"(\d+)\+?\s*years?", summary, re.IGNORECASE)
    years_exp = int(years_match.group(1)) if years_match else None
    
    # Create synthetic data structure
    data = {
        "positions": positions,
        "education": [],
        "skills": skills,
        "endorsements_received": [],
        "recommendations_received": [],
        "connections": [],
        "company_follows": [],
        "saved_job_alerts": [],
        "causes": [],
    }
    
    # Convert to ProfileVector format
    return _to_profile_vector_data_basic(data, summary, years_exp)


def _read_csv_from_zip(zf: zipfile.ZipFile, filename: str) -> List[Dict]:
    """Read CSV file from ZIP and return list of dicts."""
    try:
        # Try multiple possible paths (some exports nest differently)
        possible_names = [
            filename,
            f"Basic_LinkedInDataExport/{filename}",
            f"Linkedin/{filename}",
        ]
        
        csv_data = None
        for name in possible_names:
            try:
                csv_data = zf.read(name).decode('utf-8')
                break
            except KeyError:
                continue
        
        if not csv_data:
            return []
        
        # Parse CSV
        reader = csv.DictReader(csv_data.splitlines())
        return list(reader)
    
    except Exception as e:
        print(f"Warning: Could not read {filename}: {e}")
        return []


def _parse_linkedin_date(value: str) -> "datetime | None":
    """Parse LinkedIn's actual export date formats: bare year ('2025'),
    'Mon YYYY' ('Jan 2020'), or full ISO ('2025-01-15'). Returns None,
    not a swallowed exception, so callers can tell 'unparseable' from
    'never even tried'."""
    value = (value or "").strip()
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%b %Y", "%B %Y", "%Y"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def _parse_positions(zf: zipfile.ZipFile) -> List[Dict]:
    """Parse Positions.csv for tenure patterns and company history."""
    rows = _read_csv_from_zip(zf, "Positions.csv")

    positions = []
    for row in rows:
        # Calculate tenure if dates available
        start_date = row.get("Started On", "")
        end_date = row.get("Finished On", "") or "Present"

        tenure_years = None
        start = _parse_linkedin_date(start_date)
        if start:
            end = datetime.now() if end_date == "Present" else _parse_linkedin_date(end_date)
            if end:
                tenure_years = (end - start).days / 365.25

        positions.append({
            "company": row.get("Company Name", ""),
            "title": row.get("Title", ""),
            "description": row.get("Description", ""),
            "start": start_date,
            "end": end_date,
            "tenure_years": tenure_years,
            "location": row.get("Location", ""),
        })
    
    return positions


def _parse_education(zf: zipfile.ZipFile) -> List[Dict]:
    """Parse Education.csv for school pedigree."""
    rows = _read_csv_from_zip(zf, "Education.csv")
    
    education = []
    for row in rows:
        education.append({
            "school": row.get("School Name", ""),
            "degree": row.get("Degree Name", ""),
            "field": row.get("Notes", ""),  # LinkedIn puts field in Notes
            "start": row.get("Start Date", ""),
            "end": row.get("End Date", ""),
        })
    
    return education


def _parse_skills(zf: zipfile.ZipFile) -> List[str]:
    """Parse Skills.csv."""
    rows = _read_csv_from_zip(zf, "Skills.csv")
    return [row.get("Name", "") for row in rows if row.get("Name")]


def _parse_endorsements_received(zf: zipfile.ZipFile) -> List[Dict]:
    """Parse Endorsement_Received_Info.csv for skill validation."""
    rows = _read_csv_from_zip(zf, "Endorsement_Received_Info.csv")
    
    endorsements = []
    for row in rows:
        endorsements.append({
            "skill": row.get("Skill Name", ""),
            "endorser": row.get("Endorser First Name", "") + " " + row.get("Endorser Last Name", ""),
            "date": row.get("Endorsement Date", ""),
        })
    
    return endorsements


def _parse_recommendations_received(zf: zipfile.ZipFile) -> List[Dict]:
    """Parse Recommendations_Received.csv for zone of genius signals."""
    rows = _read_csv_from_zip(zf, "Recommendations_Received.csv")
    
    recommendations = []
    for row in rows:
        recommendations.append({
            "recommender": row.get("First Name", "") + " " + row.get("Last Name", ""),
            "text": row.get("Text", ""),
            "status": row.get("Status", ""),
            "date": row.get("Created Date", ""),
        })
    
    return recommendations


def _parse_connections(zf: zipfile.ZipFile) -> List[Dict]:
    """Parse Connections.csv for network analysis."""
    rows = _read_csv_from_zip(zf, "Connections.csv")
    
    connections = []
    for row in rows:
        connections.append({
            "name": row.get("First Name", "") + " " + row.get("Last Name", ""),
            "company": row.get("Company", ""),
            "position": row.get("Position", ""),
            "connected_on": row.get("Connected On", ""),
        })
    
    return connections


def _parse_company_follows(zf: zipfile.ZipFile) -> List[str]:
    """Parse Company Follows.csv for interest signals."""
    rows = _read_csv_from_zip(zf, "Company Follows.csv")
    return [row.get("Organization Name", "") for row in rows if row.get("Organization Name")]


def _parse_saved_job_alerts(zf: zipfile.ZipFile) -> List[Dict]:
    """Parse SavedJobAlerts.csv for job search signals."""
    rows = _read_csv_from_zip(zf, "SavedJobAlerts.csv")
    
    alerts = []
    for row in rows:
        alerts.append({
            "title": row.get("Job Title", ""),
            "location": row.get("Location", ""),
            "created": row.get("Created At", ""),
        })
    
    return alerts


def _parse_causes(zf: zipfile.ZipFile) -> List[str]:
    """Parse Causes You Care About.csv for values signals."""
    rows = _read_csv_from_zip(zf, "Causes You Care About.csv")
    return [row.get("Cause", "") for row in rows if row.get("Cause")]


def _parse_inferences(zf: zipfile.ZipFile) -> List[Dict]:
    """Parse Inferences_about_you.csv — LinkedIn's own ad-targeting/interest
    model of the person. A distinct signal class from biographical data:
    this is the platform's inference about the user, not the user's own
    record of themselves."""
    rows = _read_csv_from_zip(zf, "Inferences_about_you.csv")

    inferences = []
    for row in rows:
        inferences.append({
            "category": row.get("Category", ""),
            "type": row.get("Type of inference", ""),
            "description": row.get("Description", ""),
            "value": row.get("Inference", ""),
        })

    return inferences


def _parse_articles(zf: zipfile.ZipFile) -> List[Dict]:
    """Parse authored articles under Articles/Articles/*.html — a first-person
    long-form corpus, distinct from short recommendation-quote snippets.
    Strips HTML to plain text via BeautifulSoup; falls back to a naive
    tag-strip if bs4 isn't installed in the calling environment."""
    article_paths = [
        n for n in zf.namelist()
        if n.startswith("Articles/Articles/") and n.lower().endswith(".html")
    ]

    try:
        from bs4 import BeautifulSoup
        def extract_text(html: str) -> str:
            return BeautifulSoup(html, "html.parser").get_text(separator=" ", strip=True)
    except ImportError:
        import re as _re
        def extract_text(html: str) -> str:
            return _re.sub(r"<[^>]+>", " ", html)

    articles = []
    for path in article_paths:
        raw_html = zf.read(path).decode("utf-8", errors="replace")
        text = extract_text(raw_html)
        filename = Path(path).stem
        articles.append({
            "filename": filename,
            "text": text,
            "word_count": len(text.split()),
        })

    return articles


def _to_profile_vector_data(data: Dict) -> Dict[str, Any]:
    """
    Convert parsed LinkedIn data to ProfileVector-compatible format.
    
    Enriches with semantic analysis from recommendations, positions, etc.
    """
    # Calculate tenure patterns
    tenure_patterns = [
        pos["tenure_years"] 
        for pos in data["positions"] 
        if pos.get("tenure_years")
    ]
    
    # Extract energy signals from recommendations
    energy_signals = _extract_energy_signals(data["recommendations_received"], data["positions"])
    
    # Identify zone of genius from recommendations + role descriptions
    zone_of_genius = _extract_zone_of_genius(data["recommendations_received"], data["positions"])
    
    # Aggregate skill clusters (skills + endorsements) — top 15, for the
    # existing SmartGrid-style consumers that expect a short list
    skill_clusters = _aggregate_skill_clusters(data["skills"], data["endorsements_received"])

    # Full skill inventory with endorsement counts, uncapped — the
    # top-15 cut above was silently dropping 85 of 100 real skills
    endorsement_counts: Dict[str, int] = {}
    for endorsement in data["endorsements_received"]:
        skill = endorsement.get("skill", "")
        if skill:
            endorsement_counts[skill] = endorsement_counts.get(skill, 0) + 1
    skills_full = sorted(
        (
            {"skill": skill, "endorsement_count": endorsement_counts.get(skill, 0)}
            for skill in data["skills"]
        ),
        key=lambda s: s["endorsement_count"],
        reverse=True,
    )
    
    # Prior companies
    prior_companies = list(set([
        pos["company"] 
        for pos in data["positions"] 
        if pos.get("company")
    ]))
    
    # Calculate total years of experience
    years_experience = sum(tenure_patterns) if tenure_patterns else None
    
    # Detect drainer flags (short tenures, frequent changes)
    drainer_flags = _detect_drainer_flags(tenure_patterns, data["positions"])
    
    # Infer communication style from recommendations/descriptions
    communication_style = _infer_communication_style(
        data["recommendations_received"], 
        data["positions"]
    )
    
    return {
        "tenure_patterns": tenure_patterns,
        "energy_signals": energy_signals,
        "zone_of_genius": zone_of_genius,
        "skill_clusters": skill_clusters,
        "skills_full": skills_full,
        "endorsements_total": len(data["endorsements_received"]),
        "education": [
            {
                "school": edu["school"],
                "degree": edu["degree"],
                "field": edu["field"],
            }
            for edu in data["education"]
        ],
        "prior_companies": prior_companies,
        "drainer_flags": drainer_flags,
        "communication_style": communication_style,
        "years_experience": years_experience,
        # Extra metadata for analysis
        "network_size": len(data["connections"]),
        "company_follows": data["company_follows"],
        "saved_job_alerts": data["saved_job_alerts"],
        "causes": data["causes"],
        # Platform inference layer — LinkedIn's own model of the user,
        # not the user's own record of themselves
        "platform_inferences": data["inferences"],
        # Authored long-form corpus — primary input for the Rhetorical
        # Resonance Engine (PRD-B); not consumed by anything in this
        # module, passed through as-is
        "articles": data["articles"],
    }


def _extract_energy_signals(recommendations: List[Dict], positions: List[Dict]) -> Dict[str, List[str]]:
    """Extract energizers and drainers from recommendations and role descriptions."""
    energizers = []
    drainers = []
    
    # Energizer keywords (what excites people)
    energizer_keywords = [
        "passionate", "excels", "thrives", "loves", "energized", "innovative",
        "creative", "strategic", "leadership", "mentoring", "collaborative",
        "inspiring", "driven", "enjoys", "natural", "exceptional"
    ]
    
    # Drainer keywords (what depletes)
    drainer_keywords = [
        "struggled", "challenging", "difficult", "frustrated", "burnout",
        "micromanage", "repetitive", "monotonous", "tedious"
    ]
    
    # Scan recommendations
    for rec in recommendations:
        text = rec.get("text", "").lower()
        
        for keyword in energizer_keywords:
            if keyword in text:
                # Extract sentence containing keyword
                sentences = text.split('.')
                for sent in sentences:
                    if keyword in sent:
                        energizers.append(sent.strip()[:100])
                        break
        
        for keyword in drainer_keywords:
            if keyword in text:
                sentences = text.split('.')
                for sent in sentences:
                    if keyword in sent:
                        drainers.append(sent.strip()[:100])
                        break
    
    return {
        "energizers": list(set(energizers))[:5],  # Top 5
        "drainers": list(set(drainers))[:5],
    }


def _extract_zone_of_genius(recommendations: List[Dict], positions: List[Dict]) -> List[str]:
    """Identify recurring excellence themes from recommendations."""
    themes = []
    
    # Common zone of genius phrases
    genius_patterns = [
        "excels at", "exceptional at", "masterful", "natural talent",
        "consistently delivers", "go-to person", "expert in", "deep expertise",
        "uniquely skilled", "standout", "best at"
    ]
    
    for rec in recommendations:
        text = rec.get("text", "").lower()
        
        for pattern in genius_patterns:
            if pattern in text:
                # Extract the skill/theme mentioned
                idx = text.find(pattern)
                snippet = text[idx:idx+150]
                themes.append(snippet.strip())
    
    return list(set(themes))[:5]


def _aggregate_skill_clusters(skills: List[str], endorsements: List[Dict]) -> List[str]:
    """Aggregate and prioritize skills based on endorsements."""
    # Count endorsements per skill
    skill_counts = {}
    for skill in skills:
        skill_counts[skill] = 0
    
    for endorsement in endorsements:
        skill = endorsement.get("skill", "")
        if skill in skill_counts:
            skill_counts[skill] += 1
    
    # Sort by endorsement count
    sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)
    
    return [skill for skill, count in sorted_skills[:15]]  # Top 15


def _detect_drainer_flags(tenure_patterns: List[float], positions: List[Dict]) -> List[str]:
    """Detect burnout/misalignment signals from tenure patterns."""
    flags = []
    
    if tenure_patterns:
        avg_tenure = sum(tenure_patterns) / len(tenure_patterns)
        
        if avg_tenure < 1.5:
            flags.append("Short average tenure (<1.5 years)")
        
        short_stints = sum(1 for t in tenure_patterns if t < 1.0)
        if short_stints >= 2:
            flags.append(f"Multiple short stints ({short_stints} roles <1 year)")
    
    # Check for gaps or frequent role changes at same company
    if len(positions) > 5:
        flags.append("Frequent role changes (5+ positions)")
    
    return flags


def _to_profile_vector_data_basic(data: Dict, summary: str, years_exp: int | None) -> Dict[str, Any]:
    """Convert basic profile data to ProfileVector format."""
    positions = data.get("positions", [])
    skills = data.get("skills", [])
    
    # Extract energy signals from summary
    energizers = []
    if "passionate" in summary.lower():
        energizers.append("technology disruption")
    if "collaboration" in summary.lower() or "collaborative" in summary.lower():
        energizers.append("cross-functional collaboration")
    if "strategic" in summary.lower():
        energizers.append("strategic thinking")
    
    # Extract zone of genius
    zone_of_genius = []
    if "navigating ambiguity" in summary.lower():
        zone_of_genius.append("navigating ambiguity")
    if "stakeholder management" in summary.lower():
        zone_of_genius.append("stakeholder management")
    if "measurable results" in summary.lower():
        zone_of_genius.append("driving measurable results")
    
    return {
        "tenure_patterns": [2.0] * len(positions) if positions else [],
        "energy_signals": {
            "energizers": energizers,
            "drainers": [],
        },
        "zone_of_genius": zone_of_genius,
        "skill_clusters": skills[:15],
        "education": [],
        "prior_companies": [],
        "drainer_flags": [],
        "communication_style": "balanced",
        "years_experience": years_exp,
        "network_size": 0,
        "company_follows": [],
        "saved_job_alerts": [],
        "causes": [],
        "positions": positions,  # Add this for role discovery
    }


def _infer_communication_style(recommendations: List[Dict], positions: List[Dict]) -> str:
    """Infer communication style from language patterns."""
    async_keywords = [
        "thoughtful", "detailed", "documentation", "written", "asynchronous",
        "thorough", "comprehensive", "well-documented"
    ]
    
    sync_keywords = [
        "collaborative", "real-time", "meetings", "quick", "responsive",
        "agile", "fast-paced", "in-person"
    ]
    
    async_score = 0
    sync_score = 0
    
    for rec in recommendations:
        text = rec.get("text", "").lower()
        async_score += sum(1 for kw in async_keywords if kw in text)
        sync_score += sum(1 for kw in sync_keywords if kw in text)
    
    for pos in positions:
        desc = pos.get("description", "").lower()
        async_score += sum(1 for kw in async_keywords if kw in desc)
        sync_score += sum(1 for kw in sync_keywords if kw in desc)
    
    if async_score > sync_score * 1.5:
        return "prep-to-sync"
    elif sync_score > async_score * 1.5:
        return "sync-first"
    else:
        return "balanced"
