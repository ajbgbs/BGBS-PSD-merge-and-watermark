from flask import Flask, request, jsonify, send_file
from PyPDF2 import PdfReader, PdfWriter
import io
import base64

app = Flask(__name__)

@app.route('/merge', methods=['POST'])
def merge_pdfs():
    try:
        # Get the list of Base64-encoded files from the request
        files = request.json.get('files')
        if not files or not isinstance(files, list):
            return jsonify({"error": "Missing or invalid 'files' parameter. Must be a list of Base64-encoded PDF content."}), 400

        writer = PdfWriter()

        # Decode each Base64 string and merge the PDFs
        for file_content in files:
            try:
                pdf_data = io.BytesIO(base64.b64decode(file_content))
                reader = PdfReader(pdf_data)
                for page in reader.pages:
                    writer.add_page(page)
            except Exception as e:
                return jsonify({"error": f"Error processing one of the PDFs: {str(e)}"}), 400

        # Create a BytesIO object to store the merged PDF in memory
        merged_pdf = io.BytesIO()
        writer.write(merged_pdf)
        merged_pdf.seek(0)

        # Return the merged PDF as a response
        return send_file(merged_pdf, mimetype='application/pdf', as_attachment=True, download_name="merged_output.pdf")
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/watermark', methods=['POST'])
def add_watermark():
    try:
        # Get the Base64-encoded files from the request
        pdf_file_content = request.json.get('pdf_file_content')
        watermark_file_content = request.json.get('watermark_file_content')

        if not pdf_file_content or not watermark_file_content:
            return jsonify({"error": "Missing 'pdf_file_content' or 'watermark_file_content' parameter."}), 400

        # Decode the Base64 strings
        pdf_data = io.BytesIO(base64.b64decode(pdf_file_content))
        watermark_data = io.BytesIO(base64.b64decode(watermark_file_content))

        # Read the PDF and watermark
        reader = PdfReader(pdf_data)
        watermark_reader = PdfReader(watermark_data)
        watermark_page = watermark_reader.pages[0]

        writer = PdfWriter()
        for page in reader.pages:
            page.merge_page(watermark_page)
            writer.add_page(page)

        # Create a BytesIO object to store the watermarked PDF in memory
        watermarked_pdf = io.BytesIO()
        writer.write(watermarked_pdf)
        watermarked_pdf.seek(0)

        # Return the watermarked PDF as a response
        return send_file(watermarked_pdf, mimetype='application/pdf', as_attachment=True, download_name="watermarked_output.pdf")
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
