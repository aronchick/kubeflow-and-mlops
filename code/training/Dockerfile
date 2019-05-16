FROM tensorflow/tensorflow:1.12.0-gpu-py3

# pip install
COPY requirements.txt /scripts/requirements.txt
RUN pip install -r /scripts/requirements.txt

COPY train.py /scripts/train.py

# python train.py -d data/PetImages -e 1 -b 32 -l 0.0001 -o model -f dataset.txt
ENTRYPOINT [ "python", \
            "/scripts/train.py", \
            "-d", "data/PetImages", \
            "-e", "10", \
            "-b", "32", \
            "-l", "0.0001", \
            "-o", "model", \
            "-f", "dataset.txt" ]
