from flask import Flask, request, jsonify, send_file
from PyPDF2 import PdfReader, PdfWriter
import io
import base64

app = Flask(__name__)

@app.route('/merge', methods=['POST'])
def merge_pdfs():
    files = request.json.get('files')  # Expecting a list of file objects with fileContent and fileName

    if not files:
        return jsonify({"error": "Missing files"}), 400

    try:
        writer = PdfWriter()

        # Decode each file and add its pages to the PDF writer
        for file in files:
            file_content = base64.b64decode(file['fileContent'])
            file_stream = io.BytesIO(file_content)
            reader = PdfReader(file_stream)
            for page in reader.pages:
                writer.add_page(page)

        # Create a BytesIO object to store the merged PDF in memory
        merged_pdf = io.BytesIO()
        writer.write(merged_pdf)
        merged_pdf.seek(0)

        # Return the merged PDF as binary content
        return send_file(merged_pdf, mimetype='application/pdf', as_attachment=True, download_name="merged_output.pdf")

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/watermark', methods=['POST'])
def add_watermark():
    # Get Base64-encoded PDF and watermark file content from the request
    pdf_file_content = request.json.get('pdf_file_content')  # Base64-encoded PDF file
    watermark_file_content = request.json.get('watermark_file_content')  # Base64-encoded watermark file

    if not pdf_file_content or not watermark_file_content:
        return jsonify({"error": "Missing PDF file or watermark file"}), 400

    try:
        # Decode the Base64-encoded files
        pdf_file_binary = base64.b64decode(pdf_file_content)
        watermark_file_binary = base64.b64decode(watermark_file_content)

        # Create file streams from the binary content
        pdf_stream = io.BytesIO(pdf_file_binary)
        watermark_stream = io.BytesIO(watermark_file_binary)

        # Read the PDF and the watermark
        pdf_reader = PdfReader(pdf_stream)
        watermark_reader = PdfReader(watermark_stream)
        watermark_page = watermark_reader.pages[0]

        # Apply watermark to each page
        writer = PdfWriter()
        for page in pdf_reader.pages:
            page.merge_page(watermark_page)
            writer.add_page(page)

        # Create a BytesIO object to store the watermarked PDF in memory
        watermarked_pdf = io.BytesIO()
        writer.write(watermarked_pdf)
        watermarked_pdf.seek(0)

        # Return the watermarked PDF as binary content
        return send_file(watermarked_pdf, mimetype='application/pdf', as_attachment=True, download_name="watermarked_output.pdf")

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
