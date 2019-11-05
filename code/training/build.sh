IMAGE=kfamlacr.azurecr.io/kubeflow/training
docker build -t $IMAGE . && docker run -it $IMAGE
