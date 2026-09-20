"""Сборка markdown-дайджеста из метрик здоровья."""

from app.services.analyzer import RepoHealth


def build_digest(health: RepoHealth) -> str:
    lines = [
        f"# {health.full_name} — health {health.health_score}/100",
        "",
        f"- Активность (30д): коммитов {health.activity['commits_30d']}, "
        f"смержено PR {health.activity['prs_merged_30d']}, "
        f"звёзд {health.activity['stars']}, форков {health.activity['forks']}",
        f"- Ревью: открытых PR {health.review_load['open_prs']}, "
        f"самый старый открыт {health.review_load['oldest_open_pr_days']} дн.",
        f"- Bus factor: топ {', '.join(health.bus_factor['top_contributors']) or '—'}, "
        f"доля топ-2 {health.bus_factor['top2_share']:.0%}",
    ]
    if health.stale:
        lines.append("- Зависшие:")
        for item in health.stale:
            lines.append(f"  - #{item['number']} {item['title']} ({item['days_open']} дн.)")
    else:
        lines.append("- Зависших issue/PR нет.")
    return "\n".join(lines) + "\n"
