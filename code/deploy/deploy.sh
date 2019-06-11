<<<<<<< HEAD
az ml model deploy -n tacosandburritos -m tacosandburritos:6 --ic inferenceconfig.json --dc deploymentconfig.json --resource-group kubeflow-mlops-rg --workspace-name kfaml --overwrite -v
=======
az ml model deploy --name tacosandburritos --ic ./inferenceconfig.json --dc ./deploymentconfig.json --model tacosandburritos:6 --overwrite -v
>>>>>>> e2658a9e036a69de526ebff22d46de7157b73fc1
