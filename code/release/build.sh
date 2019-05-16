IMAGE=tlaloc.azurecr.io/kubeflow/release
docker build -t $IMAGE . && docker run -it --privileged --env-file aml.env $IMAGE