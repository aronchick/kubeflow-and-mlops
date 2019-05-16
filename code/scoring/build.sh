IMAGE=tlaloc.azurecr.io/kubeflow/score
docker build -t $IMAGE . && docker run -it $IMAGE