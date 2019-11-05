IMAGE=kfamlacr.azurecr.io/kubeflow/preprocess
docker build -t $IMAGE . && docker run -it $IMAGE
