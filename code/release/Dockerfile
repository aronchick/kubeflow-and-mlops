FROM tensorflow/tensorflow:1.12.0-py3

# pip install
COPY requirements.txt /scripts/requirements.txt
RUN pip install -r /scripts/requirements.txt

COPY release.py release.py
COPY latest.h5 latest.h5
COPY score.py score.py
COPY environment.yml environment.yml

# #python release.py -d model/latest_model.h5 -n dogsandcats
#ENTRYPOINT [ "bash" ]
ENTRYPOINT [ "python", "release.py", \
             "--base_path", ".", \
             "--model", "latest.h5", \
             "--model_name", "dogsandcats" ]
