from flask import Flask, request, jsonify, send_file
from PyPDF2 import PdfReader, PdfWriter
import io
import requests

app = Flask(__name__)

# Function to download files from SharePoint URL
def download_file_from_sharepoint(file_url, headers):
    response = requests.get(file_url, headers=headers)
    if response.status_code == 200:
        return io.BytesIO(response.content)
    else:
        raise Exception(f"Failed to download file from SharePoint: {response.status_code}")

@app.route('/merge', methods=['POST'])
def merge_pdfs():
    # Get list of SharePoint file URLs
    file_urls = request.json.get('file_urls')
    sharepoint_token = request.json.get('sharepoint_token')  # Bearer token for authentication
    
    if not file_urls or not sharepoint_token:
        return jsonify({"error": "Missing file URLs or SharePoint token"}), 400

    try:
        writer = PdfWriter()
        headers = {"Authorization": f"Bearer {sharepoint_token}"}

        # Download each file from SharePoint and merge them
        for file_url in file_urls:
            file_content = download_file_from_sharepoint(file_url, headers)
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
