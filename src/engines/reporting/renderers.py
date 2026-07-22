"""Render report content to Markdown and HTML."""

from __future__ import annotations

import html

from src.engines.reporting.models import ReportContent


def render_markdown(content: ReportContent) -> str:
    """Render structured report content as Markdown."""
    lines = [f"# {content.title}", ""]
    if content.summary_line:
        lines.extend([content.summary_line, ""])
    lines.append(
        f"**Period:** {content.period_start.isoformat()} to "
        f"{content.period_end.isoformat()}"
    )
    lines.append("")
    for section in content.sections:
        lines.append(f"## {section.heading}")
        lines.append("")
        lines.extend(section.lines)
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def render_html(content: ReportContent) -> str:
    """Render structured report content as HTML."""
    sections_html: list[str] = []
    for section in content.sections:
        items = "".join(
            f"<li>{html.escape(line)}</li>" for line in section.lines if line
        )
        sections_html.append(
            f"<section><h2>{html.escape(section.heading)}</h2>"
            f"<ul>{items}</ul></section>"
        )
    summary = (
        f"<p><em>{html.escape(content.summary_line)}</em></p>"
        if content.summary_line
        else ""
    )
    return (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<title>{html.escape(content.title)}</title></head><body>"
        f"<h1>{html.escape(content.title)}</h1>"
        f"{summary}"
        f"<p>Period: {content.period_start.isoformat()} to "
        f"{content.period_end.isoformat()}</p>"
        f"{''.join(sections_html)}"
        "</body></html>"
    )
