IMAGE=tlaloc.azurecr.io/kubeflow/train
docker build -t $IMAGE . && docker run -it --privileged --env-file blob.env $IMAGE