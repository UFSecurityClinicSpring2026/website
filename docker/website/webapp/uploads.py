from werkzeug.utils import secure_filename
import uuid
import magic
import os

upload_folder = "/opt/uploads"
allowed_extensions = {'txt', 'pdf', 'odt', 'ods', 'odp', 'docx', 'rtf', 'doc', 'eml', 'pptx', 'ppt', 'xlsx', 'xls'}
allowed_mime_types = {"application/pdf", "application/rtf", "application/vnd.oasis.opendocument.text", 
                      "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                      "message/rfc822", "text/plain", "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                      "application/vnd.ms-excel", "application/vnd.oasis.opendocument.spreadsheet",
                      "application/vnd.oasis.opendocument.presentation", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                      "application/vnd.ms-powerpoint"}
mime_to_ext = {"application/pdf": "pdf", "application/rtf": "rtf", "application/vnd.oasis.opendocument.text": "odt",
               "application/msword": "doc", "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
               "message/rfc822": "eml", "text/plain": "txt", "application/vnd.openxmlformats-officedocument.presentationml.presentation": "pptx",
               "application/vnd.ms-excel": "xls", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
               "application/vnd.oasis.opendocument.spreadsheet": "ods", "application/vnd.oasis.opendocument.presentation": "odp",
               "application/vnd.ms-powerpoint": "ppt"}

max_filesize = 100 * 1024 * 1024 # 100 MB

os.makedirs(upload_folder, exist_ok=True)

def validate(file):
  parts = file.filename.rsplit('.', 1)
  return '.' in file.filename and parts[1].lower() in allowed_extensions and validate_file_type(file.stream.read(), parts[1].lower())

def validate_file_type(file_content, ext):
  mime = magic.detect_from_content(file_content)
  return mime.mime_type in allowed_mime_types and mime.mime_type in mime_to_ext and mime_to_ext[mime.mime_type] == ext

def save_file(file):
  filename = uuid.uuid4()
  extension = file.filename.rsplit('.', 1)[1].lower()
  original = secure_filename(file.filename)

  unique_filename = f"{filename}.{extension}"
  path = os.path.join(upload_folder, unique_filename)
  file.save(path)
  return original, unique_filename