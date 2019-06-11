az ml model deploy -n tacosandburritos -m tacosandburritos:6 --ic inferenceconfig.json --dc deploymentconfig.json --resource-group kubeflow-mlops-rg --workspace-name kfaml --overwrite -v
