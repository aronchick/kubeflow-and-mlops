echo "test the deployment with a burrito image"
<<<<<<< HEAD
az ml service run -n fooddeployaci -d '{ "image": "https://www.exploreveg.org/files/2015/05/sofritas-burrito.jpeg" }' -w kfaml -g kubeflow-mlops-rg
echo "test the deployment with a taco image"
az ml service run -n fooddeployaci -d '{ "image": "https://c1.staticflickr.com/5/4022/4401140214_f489c708f0_b.jpg" }' -w kfaml -g kubeflow-mlops-rg
=======
az ml service run -n tacosandburritos -d '{ "image": "https://www.exploreveg.org/files/2015/05/sofritas-burrito.jpeg" }'
echo "test the deployment with a taco image"
az ml service run -n tacosandburritos -d '{ "image": "https://c1.staticflickr.com/5/4022/4401140214_f489c708f0_b.jpg" }'
>>>>>>> e2658a9e036a69de526ebff22d46de7157b73fc1
