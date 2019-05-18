IMAGE=kubeflowregistry.azurecr.io/kubeflow/evaluate
docker build -t $IMAGE . && docker run -it $IMAGE
