from flask import Flask, request, jsonify, send_file
from PyPDF2 import PdfReader, PdfWriter
import io
import requests

app = Flask(__name__)

# Function to download files from SharePoint URL
def download_file_from_sharepoint(file_url, token=None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = requests.get(file_url, headers=headers)
    if response.status_code == 200:
        return io.BytesIO(response.content)
    else:
        raise Exception(f"Failed to download file from SharePoint: {response.status_code}")

@app.route('/merge', methods=['POST'])
def merge_pdfs():
    # Get list of SharePoint file URLs
    file_urls = request.json.get('file_urls')
    token = request.json.get('token')  # Optional authentication token
    
    if not file_urls:
        return jsonify({"error": "Missing file URLs"}), 400

    try:
        writer = PdfWriter()

        # Download each file from SharePoint and merge them
        for file_url in file_urls:
             file_content = download_file_from_sharepoint(file_url, token=token)
            reader = PdfReader(file_content)
            for page in reader.pages:
                writer.add_page(page)

        # Create a BytesIO object to store the merged PDF in memory
        merged_pdf = io.BytesIO()
        writer.write(merged_pdf)
        merged_pdf.seek(0)  # Move the pointer to the start of the in-memory file

        # Return the merged PDF as content to Power Automate
        return send_file(merged_pdf, mimetype='application/pdf', as_attachment=True, download_name="merged_output.pdf")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/watermark', methods=['POST'])
def add_watermark():
    pdf_file = request.files.get('pdf_file')
    watermark_file = request.files.get('watermark_file')

    if not pdf_file or not watermark_file:
        return jsonify({"error": "Missing PDF file or watermark file"}), 400

    try:
        reader = PdfReader(pdf_file)
        watermark_reader = PdfReader(watermark_file)
        watermark_page = watermark_reader.pages[0]

        writer = PdfWriter()
        for page in reader.pages:
            page.merge_page(watermark_page)
            writer.add_page(page)

        # Create a BytesIO object to store the watermarked PDF in memory
        watermarked_pdf = io.BytesIO()
        writer.write(watermarked_pdf)
        watermarked_pdf.seek(0)  # Move the pointer to the start of the in-memory file

        # Return the watermarked PDF as content to Power Automate
        return send_file(watermarked_pdf, mimetype='application/pdf', as_attachment=True, download_name="watermarked_output.pdf")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
