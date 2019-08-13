#!/usr/bin/env bash
pupil_labs_folder="./eye_tracking/pupil_labs"
pupil_capture_deb="pupil_capture_linux_os_x64_v1.12-17-g46c50d3.deb"

pip install -r requirements.txt

dpkg -x $pupil_labs_folder/$pupil_capture_deb $pupil_labs_folder/pupil_capture

cp $pupil_labs_folder/surface_definitions ~/pupil_capture_settings/