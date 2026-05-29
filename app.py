"""
BrainyNotes AI — PDF Microservice
===================================
Flask API that receives structured JSON from Lovable/Supabase
and returns a branded PDF as binary.

Endpoints:
  POST /generate   → returns PDF binary
  GET  /health     → returns {"status": "ok"}
"""

import os, json, logging
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import io

from pdf_generator import generate_pdf

# ─────────────────────────────────────────────
app = Flask(__name__)
CORS(app)  # allow all origins (Supabase edge functions need this)
logging.basicConfig(level=logging.INFO)
# ─────────────────────────────────────────────


@app.route("/health", methods=["GET"])
def health():
    """Railway health check endpoint."""
    return jsonify({"status": "ok", "service": "BrainyNotes AI PDF Service"})


@app.route("/generate", methods=["POST"])
def generate():
    """
    Expects JSON body:
    {
      "course": {
        "code":      "KU4VACCOM101",
        "semester":  "Semester 4",
        "note_type": "SHORT NOTES",
        "subject":   "Consumer Rights and Protection",
        "module":    "Module 1",
        "title1":    "Fundamentals of",
        "title2":    "Consumer Rights",
        "program":   "BCom",
        "credits":   "3 Credits"
      },
      "sections": [
        {
          "h1": "Main Heading",
          "body": "Paragraph text",
          "definition": "Quote/definition text",
          "numbered_list": [
            {"title": "Point Title", "desc": "Description"}
          ],
          "recall_items": [
            {"keyword": "Term", "definition": "One-liner"}
          ],
          "subsections": [
            {
              "h2": "Subheading",
              "body": "Text",
              "numbered_list": []
            }
          ]
        }
      ]
    }

    Returns: PDF binary (application/pdf)
    """
    try:
        data = request.get_json(force=True)

        if not data:
            return jsonify({"error": "No JSON body provided"}), 400

        course   = data.get("course", {})
        sections = data.get("sections", [])

        if not course:
            return jsonify({"error": "Missing 'course' field"}), 400
        if not sections:
            return jsonify({"error": "Missing 'sections' field"}), 400

        app.logger.info(f"Generating PDF for: {course.get('subject','unknown')}")

        pdf_bytes = generate_pdf(course, sections)

        filename = (
            f"{course.get('subject','notes').replace(' ','_')}_"
            f"{course.get('module','Module1').replace(' ','')}.pdf"
        )

        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=filename,
        )

    except Exception as e:
        app.logger.error(f"PDF generation error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False)
