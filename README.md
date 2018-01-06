# Setup
- `cd` to the directory where `requirements.txt` is located.
- Create virtual env: `python3 -m venv ./env`
- Activate your virtualenv: `source env/bin/activate`
- Run: `pip install -r requirements.txt` in your shell.

# Run

Set environment variables
```
export AWS_KEY=xxxxxxxxxx
export AWS_SECRET=xxxxxxxxxxxxxxxxxxx
export AWS_REGION=xxxxxxxx
export KINESIS_STREAM_NAME=your-kinesis-data-stream-name
```

Run:
```
python ipcam_video_capture.py http://your-ipcam-url/vid
```