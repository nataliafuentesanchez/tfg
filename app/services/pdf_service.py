# =============================================================================
# AnalisisImagenes - Proyecto para el analisis de imagenes con metodologia SDD.
# Copyright (c) 2026 Natalia Fuentes Sanchez
# Licensed under the MIT License. See LICENSE for details.
# Built with dbv-specs-ops - https://github.com/davidbuenov/dbv-specs-ops
# =============================================================================

from __future__ import annotations

from io import BytesIO
from datetime import datetime
from typing import Dict, Any

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


def generate_clinical_pdf(analysis_data: Dict[str, Any]) -> bytes:
    """
    Genera un informe clinico dermatologico estructurado en PDF a partir
    de los resultados del modelo de vision ResNet-18 y el analisis morfologico ABCDE.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A'),
        alignment=TA_LEFT
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748B'),
        alignment=TA_LEFT
    )

    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#334155')
    )

    badge_style = ParagraphStyle(
        'AlertBadge',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=12,
        alignment=TA_CENTER,
        textColor=colors.white
    )

    story = []

    header_data = [
        [
            Paragraph("<b>OLIVIA AI</b> · Sistema de Orientacion Dermatologica", title_style),
            Paragraph(f"<b>Fecha:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}<br/><b>ID Caso:</b> #{abs(hash(analysis_data.get('filename', '')) % 1000000):06d}", subtitle_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[340, 190])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#6366F1'), spaceBefore=4, spaceAfter=14))

    severity = str(analysis_data.get("severity", "bajo")).lower()
    if severity == "grave":
        alert_bg = colors.HexColor('#DC2626')
        alert_text = "ALERTA: GRAVE (SOSPECHA ALTA)"
    elif severity == "medio":
        alert_bg = colors.HexColor('#D97706')
        alert_text = "ALERTA: MODERADO / PREMALIGNO"
    else:
        alert_bg = colors.HexColor('#059669')
        alert_text = "ALERTA: BAJO RIESGO / BENIGNO"

    badge_data = [[Paragraph(alert_text, badge_style)]]
    badge_table = Table(badge_data, colWidths=[530], rowHeights=[26])
    badge_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), alert_bg),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(badge_table)
    story.append(Spacer(1, 12))

    patology = analysis_data.get("likely_cause", "No especificado")
    risk_score = analysis_data.get("risk_score", 0.0)
    primary_label = "SANO / BENIGNO" if analysis_data.get("primary_label") == "sano" else "ENFERMO / SOSPECHA"
    classification = "Benigna / Normal" if analysis_data.get("benign_malignant") == "benigno_probable" else "Premaligna / Maligna probable"

    metrics_table_data = [
        [
            Paragraph("<b>Patologia mas compatible:</b>", body_style),
            Paragraph(f"<b>{patology}</b>", body_style)
        ],
        [
            Paragraph("<b>Estado visual:</b>", body_style),
            Paragraph(primary_label, body_style)
        ],
        [
            Paragraph("<b>Clasificacion de la lesion:</b>", body_style),
            Paragraph(classification, body_style)
        ],
        [
            Paragraph("<b>Indice de compatibilidad / riesgo:</b>", body_style),
            Paragraph(f"{round(risk_score * 100, 1)}%", body_style)
        ],
        [
            Paragraph("<b>Archivo analizado:</b>", body_style),
            Paragraph(str(analysis_data.get("filename", "imagen.jpg")), body_style)
        ],
    ]
    metrics_table = Table(metrics_table_data, colWidths=[200, 330])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(metrics_table)
    story.append(Spacer(1, 14))

    story.append(Paragraph("EVALUACION VISUAL (CRITERIOS ABCDE)", section_header_style))
    abcde = analysis_data.get("abcde_analysis", {})

    abcde_table_data = [
        [
            Paragraph("<b>Criterio</b>", body_style),
            Paragraph("<b>Hallazgo Morfologico</b>", body_style),
            Paragraph("<b>Puntuacion / Nivel</b>", body_style)
        ],
        [
            Paragraph("<b>A - Asimetria</b>", body_style),
            Paragraph(abcde.get("asymmetry_desc", "Simetrica"), body_style),
            Paragraph(f"{abcde.get('asymmetry_score', 0.0)} / 1.0", body_style)
        ],
        [
            Paragraph("<b>B - Bordes</b>", body_style),
            Paragraph(abcde.get("border_desc", "Bordes definidos"), body_style),
            Paragraph(f"{abcde.get('border_score', 0.0)} / 1.0", body_style)
        ],
        [
            Paragraph("<b>C - Color</b>", body_style),
            Paragraph(abcde.get("color_desc", "Color homogeneo"), body_style),
            Paragraph(f"{abcde.get('color_score', 0.0)} / 1.0", body_style)
        ],
        [
            Paragraph("<b>D - Diametro</b>", body_style),
            Paragraph(abcde.get("diameter_desc", "Diametro focal"), body_style),
            Paragraph(f"{abcde.get('diameter_score', 0.0)} / 1.0", body_style)
        ],
    ]
    abcde_table = Table(abcde_table_data, colWidths=[120, 310, 100])
    abcde_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EEF2FF')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(abcde_table)
    story.append(Spacer(1, 14))

    story.append(Paragraph("RECOMENDACION Y DERIVACION CLINICA", section_header_style))
    rec_text = analysis_data.get("recommendation", "Consulte a su medico especialista.")
    rec_table_data = [[
        Paragraph(f"<b>Recomendacion medica:</b><br/>{rec_text}", body_style)
    ]]
    rec_table = Table(rec_table_data, colWidths=[530])
    rec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F1F5F9')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#94A3B8')),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(rec_table)
    story.append(Spacer(1, 16))

    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#64748B'),
        alignment=TA_CENTER
    )
    disclaimer_text = (
        "<b>AVISO MEDICO LEGAL:</b> Este documento es un informe de orientacion generado mediante un modelo de inteligencia "
        "artificial (ResNet-18) para asistencia en el cribado dermatologico. <b>NO constituye un diagnostico medico definitivo</b> "
        "ni reemplaza la evaluacion presencial de un dermatologo colegiado ni el examen anatomopatologico / biopsia."
    )
    story.append(KeepTogether([
        HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#CBD5E1'), spaceBefore=8, spaceAfter=8),
        Paragraph(disclaimer_text, disclaimer_style)
    ]))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
