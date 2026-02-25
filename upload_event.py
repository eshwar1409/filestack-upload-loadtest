from locust import HttpUser, task, events
import os
import random
import mimetypes
from threading import Lock

FILE_FOLDER = os.getenv("FILE_FOLDER", "testdata")
API_KEY = os.getenv("API_KEY")
TARGET_REQUESTS = int(os.getenv("TARGET_REQUESTS", "10"))

request_count = 0
lock = Lock()

FILE_DATA = []

for f in os.listdir(FILE_FOLDER):
    full_path = os.path.join(FILE_FOLDER, f)
    if os.path.isfile(full_path):
        with open(full_path, "rb") as file:
            FILE_DATA.append((f, file.read()))

@events.request.add_listener
def count_requests(request_type, name, response_time,
                   response_length, response, context,
                   exception, **kwargs):
    global request_count
    with lock:
        request_count += 1
        if request_count >= TARGET_REQUESTS:
            events.runner.quit()

class UploadEventUser(HttpUser):
    wait_time = lambda self: 0

    @task
    def upload_event(self):
        file_name, file_content = random.choice(FILE_DATA)
        mime_type, _ = mimetypes.guess_type(file_name)
        mime_type = mime_type or "application/octet-stream"

        files = {"fileUpload": (file_name, file_content, mime_type)}

        self.client.post(
            f"/api/store/S3?key={API_KEY}",
            files=files,
            name="upload_event"
        )