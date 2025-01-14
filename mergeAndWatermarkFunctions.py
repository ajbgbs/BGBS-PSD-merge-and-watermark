from flask import Flask, request, jsonify
from PyPDF2 import PdfReader, PdfWriter
import os

app = Flask(__name__)

@app.route('/merge', methods=['POST'])
def merge_pdfs():
    files = request.files.getlist('files')
    output_path = request.form.get('output_path')

    if not files or not output_path:
        return jsonify({"error": "Missing files or output path"}), 400

    writer = PdfWriter()
    try:
        for file in files:
            reader = PdfReader(file)
            for page in reader.pages:
                writer.add_page(page)

        with open(output_path, 'wb') as output_file:
            writer.write(output_file)

        return jsonify({"message": "PDFs merged successfully", "output": output_path})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/watermark', methods=['POST'])
def add_watermark():
    pdf_file = request.files.get('pdf_file')
    watermark_file = request.files.get('watermark_file')
    output_path = request.form.get('output_path')

    if not pdf_file or not watermark_file or not output_path:
        return jsonify({"error": "Missing PDF file, watermark file, or output path"}), 400

    try:
        reader = PdfReader(pdf_file)
        watermark_reader = PdfReader(watermark_file)
        watermark_page = watermark_reader.pages[0]

        writer = PdfWriter()
        for page in reader.pages:
            page.merge_page(watermark_page)
            writer.add_page(page)

        with open(output_path, 'wb') as output_file:
            writer.write(output_file)

        return jsonify({"message": "Watermark added successfully", "output": output_path})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
