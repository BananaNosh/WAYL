# WAYL
In this program the user is shown an image and their gaze is tracked with the [Pupils Lab](https://pupil-labs.com/) Eye Tracker.
The tracked gaze is then send to other running instances of the program within the local network.
The shown image then is adapted to show where the users are looking at.

## Install
Clone the repository and change to the new directory with 
```bash
git clone git@github.com:BananaNosh/WAYL.git <Your Project Folder Name>
cd <Your Project Folder Name>
``` 
Then create a new Python environment, unless you want to use an existing one, with
```bash
python3 -m env <Path to Your Environment>
```
and activate it:
```bash
source <Path to Your Environment>/bin/activate
```
Of course you can also use virtualenv or something similar instead.

Afterwards you can call the `install.sh`, which will install the needed Python packages and [Pupil Capture](https://github.com/pupil-labs/pupil/releases/tag/v1.12).

## Run
To run the program just call
```bash
python wayl.py
```
and follow the instructions given in the terminal.

Pupil Capture will be started. Wait until you see the images of all three cameras and then adjust them (The participant should wear the Pupils Lab Eye Tracker already), so that they are focused and the pupils can be easily detected.
You find more information for that here https://docs.pupil-labs.com/#3-check-pupil-detection.

Then press enter and start the actual main loop.