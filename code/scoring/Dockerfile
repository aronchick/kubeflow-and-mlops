FROM tensorflow/tensorflow:1.12.0-gpu-py3


# pip install
COPY requirements.txt /scripts/requirements.txt
RUN pip install -r /scripts/requirements.txt

COPY score.py /scripts/score.py

# python score.py -m model/latest.h5
ENTRYPOINT [ "python", \
            "/scripts/score.py", \
            "-m", "model/latest.h5" ]
