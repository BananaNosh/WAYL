import atexit
import os
import subprocess

from psutil import Process

from helper import current_time_string


def start_pupil_capture():
    pupil_labs_path = os.path.join("eye_tracking", "pupil_labs")
    log_files_path = os.path.join(pupil_labs_path, "pupil_capture", "logs")
    pupil_capture_path = os.path.join(pupil_labs_path, "pupil_capture", "opt", "pupil_capture", "pupil_capture")
    if not os.path.exists(log_files_path):
        os.makedirs(log_files_path)
    with open(os.path.join(log_files_path, "log_{}.txt".format(current_time_string()[1:-2])), "w+") as log_file:
        pupil_capture = subprocess.Popen(pupil_capture_path, stdout=log_file, stderr=log_file)

    def stop_capture():
        process = Process(pupil_capture.pid)
        if process.is_running():
            for proc in process.children(recursive=True):
                proc.kill()
            process.kill()
    atexit.register(stop_capture)

    while True:
        msg = input("Pupil Capture is started ...\n"
                    "Type enter for continuing, when all cameras are calibrated with Pupil Capture:")
        if msg == "":
            return stop_capture
