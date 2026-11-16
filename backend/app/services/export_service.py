import io
import json
from datetime import datetime, timezone
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Task 09: export labels follow the REQUESTED UI locale ("id" | "en"), not the
# story language. User-authored text and backend analysis content are never
# translated — only section headings, labels and empty-state boilerplate.
EXPORT_LABELS: Dict[str, Dict[str, str]] = {
    "id": {
        "report_title": "Laporan Audit Kebutuhan",
        "audit_id": "ID Audit",
        "audit_date": "Tanggal Audit",
        "audit_status": "Status Audit",
        "revision_status": "Status Revisi",
        "initial_score": "Skor Awal",
        "current_score": "Skor Terkini",
        "quality_score": "Skor Kualitas Terkini",
        "findings_summary": "Ringkasan Temuan",
        "incomplete": "Tidak Lengkap",
        "total_findings": "Total Temuan",
        "findings_list": "Daftar Temuan Cacat",
        "col_no": "No",
        "col_category": "Kategori",
        "col_severity": "Severity",
        "col_text": "Potongan Teks",
        "col_fix": "Saran Perbaikan",
        "no_defects": "Tidak ada cacat terdeteksi",
        "no_findings_pdf": "Tidak ada temuan cacat",
        "req_text_comparison": "Perbandingan Teks Kebutuhan",
        "original_label": "Teks Orisinal:",
        "revised_label": "Teks Revisi:",
        "no_revision": "(Belum ada revisi)",
    },
    "en": {
        "report_title": "Requirements Audit Report",
        "audit_id": "Audit ID",
        "audit_date": "Audit Date",
        "audit_status": "Audit Status",
        "revision_status": "Revision Status",
        "initial_score": "Initial Score",
        "current_score": "Current Score",
        "quality_score": "Current Quality Score",
        "findings_summary": "Findings Summary",
        "incomplete": "Incomplete",
        "total_findings": "Total Findings",
        "findings_list": "Defect Findings",
        "col_no": "No",
        "col_category": "Category",
        "col_severity": "Severity",
        "col_text": "Text Excerpt",
        "col_fix": "Suggested Fix",
        "no_defects": "No defects detected",
        "no_findings_pdf": "No defect findings",
        "req_text_comparison": "Requirements Text Comparison",
        "original_label": "Original Text:",
        "revised_label": "Revised Text:",
        "no_revision": "(No revision yet)",
    },
}


def _labels(lang: str) -> Dict[str, str]:
    return EXPORT_LABELS["en"] if (lang or "").lower() == "en" else EXPORT_LABELS["id"]


class ExportService:
    @staticmethod
    def render_json(audit_detail: Dict[str, Any], konten_asli: str, konten_revisi: str) -> bytes:
        data = {
            "report_version": "1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "audit": {
                "id_audit": audit_detail["id_audit"],
                "judul_klausul": audit_detail["judul_klausul"],
                "tanggal_audit": audit_detail["tanggal_audit"],
                "status_audit": audit_detail["status_audit"]
            },
            "scorecard": audit_detail["scorecard"],
            "ringkasan": audit_detail["ringkasan"],
            "temuan": audit_detail["temuan"],
            "konten_asli": konten_asli,
            "konten_revisi": konten_revisi,
            "acceptance_criteria": audit_detail.get("rekomendasi_ai", {}).get("acceptance_criteria") if audit_detail.get("rekomendasi_ai") else []
        }
        return json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")

    @staticmethod
    def render_markdown(audit_detail: Dict[str, Any], konten_asli: str, konten_revisi: str, lang: str = "id") -> bytes:
        L = _labels(lang)
        scorecard = audit_detail.get("scorecard") or {}
        skor_awal = scorecard.get("skor_awal", "-")
        skor_kualitas = scorecard.get("skor_kualitas", "-")
        ringkasan = audit_detail.get("ringkasan") or {}

        lines = [
            f"# {L['report_title']}: {audit_detail['judul_klausul']}",
            "",
            f"- **{L['audit_id']}**: {audit_detail['id_audit']}",
            f"- **{L['audit_date']}**: {audit_detail.get('tanggal_audit', '-')}",
            f"- **{L['audit_status']}**: {audit_detail.get('status_audit', '-')}",
            f"- **{L['initial_score']}**: {skor_awal}",
            f"- **{L['current_score']}**: {skor_kualitas}",
            "",
            f"## {L['findings_summary']}",
            f"- Ambiguity: {ringkasan.get('ambiguity', 0)}",
            f"- {L['incomplete']}: {ringkasan.get('tidak_lengkap', 0)}",
            f"- Weak Directive: {ringkasan.get('weak_directive', 0)}",
            f"- Passive Voice: {ringkasan.get('passive_voice', 0)}",
            f"- **{L['total_findings']}**: {ringkasan.get('total', 0)}",
            "",
            f"## {L['findings_list']}",
            f"| {L['col_no']} | {L['col_category']} | {L['col_severity']} | {L['col_text']} | {L['col_fix']} |",
            "|---|---|---|---|---|"
        ]

        temuan = audit_detail.get("temuan") or []
        if not temuan:
            lines.append(f"| - | {L['no_defects']} | - | - | - |")
        else:
            for i, t in enumerate(temuan, 1):
                clean_saran = t.get('saran_perbaikan', '').replace("|", "\\|")
                lines.append(f"| {i} | {t.get('kategori_cacat')} | {t.get('severity')} | `{t.get('potongan_teks_asli')}` | {clean_saran} |")

        lines.extend([
            "",
            f"## {L['req_text_comparison']}",
            f"### {L['original_label'].rstrip(':')}",
            f"> {konten_asli}",
            "",
            f"### {L['revised_label'].rstrip(':')}",
            f"> {konten_revisi if konten_revisi else L['no_revision']}",
            ""
        ])

        rekomendasi = audit_detail.get("rekomendasi_ai")
        if rekomendasi and rekomendasi.get("acceptance_criteria"):
            lines.append("## Acceptance Criteria (Gherkin)")
            for ac in rekomendasi["acceptance_criteria"]:
                lines.append(f"- **Given** {ac.get('given')}")
                lines.append(f"  **When** {ac.get('when')}")
                lines.append(f"  **Then** {ac.get('then')}")
                lines.append("")

        return "\n".join(lines).encode("utf-8")

    @staticmethod
    def render_pdf(audit_detail: Dict[str, Any], konten_asli: str, konten_revisi: str, lang: str = "id") -> bytes:
        L = _labels(lang)
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            name="TitleStyle",
            parent=styles["Heading1"],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#1e293b")
        )
        h2_style = ParagraphStyle(
            name="H2Style",
            parent=styles["Heading2"],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#334155"),
            spaceBefore=10,
            spaceAfter=6
        )
        normal_style = styles["Normal"]

        story = []

        # Title & Meta
        story.append(Paragraph(f"ReqLint Audit Report: {audit_detail['judul_klausul']}", title_style))
        story.append(Spacer(1, 10))

        scorecard = audit_detail.get("scorecard") or {}
        skor_awal = scorecard.get("skor_awal", "-")
        skor_kualitas = scorecard.get("skor_kualitas", "-")

        meta_data = [
            [L["audit_id"], str(audit_detail["id_audit"]), L["audit_date"], str(audit_detail.get("tanggal_audit", "-"))[:19]],
            [L["audit_status"], audit_detail.get("status_audit", "-"), L["revision_status"], audit_detail.get("status_revisi", "-")],
            [L["initial_score"], str(skor_awal), L["quality_score"], str(skor_kualitas)]
        ]
        meta_table = Table(meta_data, colWidths=[110, 150, 130, 150])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor("#0f172a")),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 12))

        # Findings Table
        story.append(Paragraph(L["findings_list"], h2_style))
        findings = audit_detail.get("temuan") or []
        findings_data = [[L["col_category"], L["col_severity"], L["col_text"], L["col_fix"]]]
        if not findings:
            findings_data.append(["-", "-", L["no_findings_pdf"], "-"])
        else:
            for f in findings:
                findings_data.append([
                    Paragraph(f.get("kategori_cacat", ""), normal_style),
                    Paragraph(f.get("severity", ""), normal_style),
                    Paragraph(f.get("potongan_teks_asli", ""), normal_style),
                    Paragraph(f.get("saran_perbaikan", ""), normal_style)
                ])

        findings_table = Table(findings_data, colWidths=[90, 60, 140, 250])
        findings_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(findings_table)
        story.append(Spacer(1, 12))

        # Original vs Revised
        story.append(Paragraph(L["req_text_comparison"], h2_style))
        story.append(Paragraph(f"<b>{L['original_label']}</b>", normal_style))
        story.append(Paragraph(konten_asli, normal_style))
        story.append(Spacer(1, 8))
        story.append(Paragraph(f"<b>{L['revised_label']}</b>", normal_style))
        story.append(Paragraph(konten_revisi if konten_revisi else L["no_revision"], normal_style))
        story.append(Spacer(1, 12))

        # Acceptance Criteria
        rekomendasi = audit_detail.get("rekomendasi_ai")
        if rekomendasi and rekomendasi.get("acceptance_criteria"):
            story.append(Paragraph("Acceptance Criteria (Gherkin)", h2_style))
            for ac in rekomendasi["acceptance_criteria"]:
                ac_text = f"<b>Given</b> {ac.get('given')}<br/><b>When</b> {ac.get('when')}<br/><b>Then</b> {ac.get('then')}"
                story.append(Paragraph(ac_text, normal_style))
                story.append(Spacer(1, 6))

        doc.build(story)
        buf.seek(0)
        return buf.getvalue()
