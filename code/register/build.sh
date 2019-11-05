IMAGE=kfamlacr.azurecr.io/kubeflow/register
docker build -t $IMAGE . && docker run -it $IMAGE
