# from flask import Flask, request, jsonify
# import os
# import re
# import PyPDF2
# import logging
# import http.client
# import urllib.parse
# from whoosh.index import create_in, open_dir, EmptyIndexError
# from whoosh.fields import Schema, TEXT, ID
# from whoosh.qparser import QueryParser
# from whoosh.analysis import StemmingAnalyzer
# connection_string = 'DefaultEndpointsProtocol=https;AccountName=kbhdocumentstorage;AccountKey=doSuaslyxCWTQRhiKeyTQEIaT+wVsx4upRJmmNOicvGcb5vJCb1S5d+0bsNQitQxI4uVbYtTwcT1+AStUfrp0Q==;EndpointSuffix=core.windows.net'
# container_name = 'kbhdocumentcontainer'
# app = Flask(__name__)

# @app.route('/')
# def index():
#     return "Hello, world!"

# @app.route('/hello')
# def hello():
#     name = request.args.get('name', 'World')
#     return f"Hello, {name}!"

# def download_blob(blob_url):
#     parsed_url = urllib.parse.urlparse(blob_url)
#     conn = http.client.HTTPSConnection(parsed_url.netloc)
#     conn.request("GET", parsed_url.path + '?' + parsed_url.query)
#     response = conn.getresponse()
#     if response.status == 200:
#         return response.read()
#     else:
#         logging.error(f"Failed to download blob: {response.status} - {response.read().decode('utf-8')}")
#         return None

# # def process_docx(file_content):
# #     with open('temp.docx', 'wb') as temp_file:
# #         temp_file.write(file_content)
# #     text = pypandoc.convert_file('temp.docx', 'plain')
# #     os.remove('temp.docx')
# #     return text

# def process_pdf(file_content):
#     pdf_reader = PyPDF2.PdfReader(file_content)
#     text = ""
#     for page in pdf_reader.pages:
#         text += page.extract_text()
#     return text

# def create_index_and_upload(connection_string, container_name):
#     list_blobs_url = f"https://{connection_string.split(';')[1].split('=')[1]}.blob.core.windows.net/{container_name}?restype=container&comp=list"
#     parsed_url = urllib.parse.urlparse(list_blobs_url)
#     conn = http.client.HTTPSConnection(parsed_url.netloc)
#     conn.request("GET", parsed_url.path + '?' + parsed_url.query, headers={"x-ms-version": "2020-08-04"})
#     response = conn.getresponse()

#     if response.status != 200:
#         logging.error(f"Failed to list blobs: {response.status} - {response.read().decode('utf-8')}")
#         return

#     blob_names = re.findall(r'<Name>(.*?)</Name>', response.read().decode('utf-8'))
#     schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT(stored=True, analyzer=StemmingAnalyzer()))
#     index_dir = os.path.join(os.getcwd(), 'indexdir')
#     if not os.path.exists(index_dir):
#         os.makedirs(index_dir)
#     ix = create_in(index_dir, schema)
#     writer = ix.writer()

#     for blob_name in blob_names:
#         if blob_name.startswith('~$') or not (blob_name.lower().endswith(".docx") or blob_name.lower().endswith(".pdf")):
#             continue

#         blob_url = f"https://{connection_string.split(';')[1].split('=')[1]}.blob.core.windows.net/{container_name}/{blob_name}"
#         file_content = download_blob(blob_url)

#         if not file_content:
#             continue

#         try:
          
#             if blob_name.lower().endswith(".pdf"):
#                 text = process_pdf(file_content)

#             writer.add_document(title=blob_name, path=blob_name, content=text)

#         except Exception as e:
#             logging.error(f"Failed to process {blob_name}: {e}")

#     writer.commit()

# def download_index_from_blob(connection_string, container_name):
#     list_blobs_url = f"https://{connection_string.split(';')[1].split('=')[1]}.blob.core.windows.net/{container_name}?restype=container&comp=list"
#     parsed_url = urllib.parse.urlparse(list_blobs_url)
#     conn = http.client.HTTPSConnection(parsed_url.netloc)
#     conn.request("GET", parsed_url.path + '?' + parsed_url.query, headers={"x-ms-version": "2020-08-04"})
#     response = conn.getresponse()

#     if response.status != 200:
#         logging.error(f"Failed to list blobs: {response.status} - {response.read().decode('utf-8')}")
#         return

#     blobs = re.findall(r'<Name>(.*?)</Name>', response.read().decode('utf-8'))
#     index_dir = os.path.join(os.getcwd(), 'indexdir')
#     if not os.path.exists(index_dir):
#         os.makedirs(index_dir)

#     for blob_name in blobs:
#         blob_url = f"https://{connection_string.split(';')[1].split('=')[1]}.blob.core.windows.net/{container_name}/{urllib.parse.quote(blob_name)}"
#         file_content = download_blob(blob_url)

#         if not file_content:
#             continue

#         download_file_path = os.path.join(index_dir, blob_name)
#         os.makedirs(os.path.dirname(download_file_path), exist_ok=True)

#         with open(download_file_path, "wb") as download_file:
#             download_file.write(file_content)


# def search_index(query_str, connection_string, container_name):
#     try:
#         download_index_from_blob(connection_string, container_name)
#         index_dir = os.path.join(os.getcwd(), 'indexdir')
#         ix = open_dir(index_dir)
#         searcher = ix.searcher()
#         query = QueryParser("content", schema=ix.schema).parse(query_str)

#         results = searcher.search(query, limit=None)
#         hits = []
#         for hit in results:
#             matched_para = re.sub('<.*?>', '', hit.highlights("content", top=4))
#             hits.append({"path": hit['path'], "paragraphs": matched_para.replace('\n', '').replace('\t', '')})

#         searcher.close()
#         ix.close()

#         return hits

#     except EmptyIndexError as e:
#         logging.error(f"EmptyIndexError: {e}")
#         return []

# @app.route('/search', methods=['GET'])
# def search():
#     query_str = request.args.get('q', '')
#     results = search_index(query_str, connection_string, container_name)
#     return jsonify(results)

# if __name__ == '__main__':
#     app.run()
from flask import Flask, request, jsonify
import os
import re
import logging
import http.client
import urllib.parse
from whoosh.index import create_in, open_dir, EmptyIndexError
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser
from whoosh.analysis import StemmingAnalyzer

connection_string = 'DefaultEndpointsProtocol=https;AccountName=kbhdocumentstorage;AccountKey=doSuaslyxCWTQRhiKeyTQEIaT+wVsx4upRJmmNOicvGcb5vJCb1S5d+0bsNQitQxI4uVbYtTwcT1+AStUfrp0Q==;EndpointSuffix=core.windows.net'
container_name = 'kbhdocumentcontainer'
app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, world!"

@app.route('/hello')
def hello():
    name = request.args.get('name', 'World')
    return f"Hello, {name}!"

def download_blob(blob_url):
    parsed_url = urllib.parse.urlparse(blob_url)
    conn = http.client.HTTPSConnection(parsed_url.netloc)
    conn.request("GET", parsed_url.path + '?' + parsed_url.query)
    response = conn.getresponse()
    if response.status == 200:
        return response.read()
    else:
        logging.error(f"Failed to download blob: {response.status} - {response.read().decode('utf-8')}")
        return None

def create_index_and_upload(connection_string, container_name):
    list_blobs_url = f"https://{connection_string.split(';')[1].split('=')[1]}.blob.core.windows.net/{container_name}?restype=container&comp=list"
    parsed_url = urllib.parse.urlparse(list_blobs_url)
    conn = http.client.HTTPSConnection(parsed_url.netloc)
    conn.request("GET", parsed_url.path + '?' + parsed_url.query, headers={"x-ms-version": "2020-08-04"})
    response = conn.getresponse()

    if response.status != 200:
        logging.error(f"Failed to list blobs: {response.status} - {response.read().decode('utf-8')}")
        return

    blob_names = re.findall(r'<Name>(.*?)</Name>', response.read().decode('utf-8'))
    schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT(stored=True, analyzer=StemmingAnalyzer()))
    index_dir = os.path.join(os.getcwd(), 'indexdir')
    if not os.path.exists(index_dir):
        os.makedirs(index_dir)
    ix = create_in(index_dir, schema)
    writer = ix.writer()

    for blob_name in blob_names:
        if blob_name.startswith('~$') or not (blob_name.lower().endswith(".docx") or blob_name.lower().endswith(".pdf")):
            continue

        blob_url = f"https://{connection_string.split(';')[1].split('=')[1]}.blob.core.windows.net/{container_name}/{blob_name}"
        file_content = download_blob(blob_url)

        if not file_content:
            continue

        try:
            # Process document content (assuming you handle DOCX or PDF here)
            # For example:
            # if blob_name.lower().endswith(".pdf"):
            #     text = process_pdf(file_content)
            # else:
            #     text = process_docx(file_content)

            text = "Sample document content for indexing"  # Placeholder for document content processing

            writer.add_document(title=blob_name, path=blob_name, content=text)

        except Exception as e:
            logging.error(f"Failed to process {blob_name}: {e}")

    writer.commit()

def download_index_from_blob(connection_string, container_name):
    list_blobs_url = f"https://{connection_string.split(';')[1].split('=')[1]}.blob.core.windows.net/{container_name}?restype=container&comp=list"
    parsed_url = urllib.parse.urlparse(list_blobs_url)
    conn = http.client.HTTPSConnection(parsed_url.netloc)
    conn.request("GET", parsed_url.path + '?' + parsed_url.query, headers={"x-ms-version": "2020-08-04"})
    response = conn.getresponse()

    if response.status != 200:
        logging.error(f"Failed to list blobs: {response.status} - {response.read().decode('utf-8')}")
        return

    blobs = re.findall(r'<Name>(.*?)</Name>', response.read().decode('utf-8'))
    index_dir = os.path.join(os.getcwd(), 'indexdir')
    if not os.path.exists(index_dir):
        os.makedirs(index_dir)

    for blob_name in blobs:
        blob_url = f"https://{connection_string.split(';')[1].split('=')[1]}.blob.core.windows.net/{container_name}/{urllib.parse.quote(blob_name)}"
        file_content = download_blob(blob_url)

        if not file_content:
            continue

        download_file_path = os.path.join(index_dir, blob_name)
        os.makedirs(os.path.dirname(download_file_path), exist_ok=True)

        with open(download_file_path, "wb") as download_file:
            download_file.write(file_content)

def search_index(query_str, connection_string, container_name):
    try:
        download_index_from_blob(connection_string, container_name)
        index_dir = os.path.join(os.getcwd(), 'indexdir')
        ix = open_dir(index_dir)
        searcher = ix.searcher()
        query = QueryParser("content", schema=ix.schema).parse(query_str)

        results = searcher.search(query, limit=None)
        hits = []
        for hit in results:
            matched_para = re.sub('<.*?>', '', hit.highlights("content", top=4))
            hits.append({"path": hit['path'], "paragraphs": matched_para.replace('\n', '').replace('\t', '')})

        searcher.close()
        ix.close()

        return hits

    except EmptyIndexError as e:
        logging.error(f"EmptyIndexError: {e}")
        return []

@app.route('/search', methods=['GET'])
def search():
    query_str = request.args.get('q', '')
    results = search_index(query_str, connection_string, container_name)
    return jsonify(results)

if __name__ == '__main__':
    app.run()
