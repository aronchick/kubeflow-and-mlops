import os
import azureml
import argparse
import tensorflow as tf
from pathlib import Path
from azureml.core import Workspace
from azureml.core.model import Model
from azureml.core.image import ContainerImage, Image
from azureml.core.webservice import Webservice, AciWebservice
from azureml.core.authentication import ServicePrincipalAuthentication 

def info(msg, char = "#", width = 75):
    print("")
    print(char * width)
    print(char + "   %0*s" % ((-1*width)+5, msg) + char)
    print(char * width)

def run(model_path, model_name):
    auth_args = {
        'tenant_id': os.environ['TENANT_ID'],
        'service_principal_id': os.environ['SERVICE_PRINCIPAL_ID'],
        'service_principal_password': os.environ['SERVICE_PRINCIPAL_PASSWORD']
    }

    ws_args = {
        'auth': ServicePrincipalAuthentication(**auth_args),
        'subscription_id': os.environ['SUBSCRIPTION_ID'],
        'resource_group': os.environ['RESOURCE_GROUP']
    }

    ws = Workspace.get(os.environ['WORKSPACE_NAME'], **ws_args)

    print(ws.get_details())

    print('\nSaving model {} to {}'.format(model_path, model_name))
    model = Model.register(ws, model_name=model_name, model_path=model_path)
    print('Done!')

    print('Checking for existing service {}'.format(model_name))
    service_name = 'simplemnist-svc'
    if model_name in ws.webservices:
        print('Found it!\nRemoving Existing service...')
        ws.webservices[model_name].delete()
        print('Done!')
    else:
        print('Not found, creating new one!')

    # image configuration
    image_config = ContainerImage.image_configuration(execution_script="score.py", 
                                    runtime="python", 
                                    conda_file="environment.yml")

    # deployement configuration
    aciconfig = AciWebservice.deploy_configuration(cpu_cores=1, 
                                                memory_gb=1, 
                                                description=model_name)

    # deploy
    service = Webservice.deploy_from_model(workspace=ws,
                                            name=model_name, 
                                            models=[model], 
                                            image_config=image_config, 
                                            deployment_config=aciconfig)

    
    service.wait_for_deployment(show_output=True)

    #print logs
    print(service.get_logs())

    print('Done!')

if __name__ == "__main__":
    # argparse stuff for model path and model name
    parser = argparse.ArgumentParser(description='sanity check on model')
    parser.add_argument('-b', '--base_path', help='directory to base data', default='..')
    parser.add_argument('-m', '--model', help='directory to training and test data', default='model/latest.h5')
    parser.add_argument('-n', '--model_name', help='directory to training and test data', default='dogsandcats')
    args = parser.parse_args()
    
    info('Using TensorFlow v.{}'.format(tf.__version__))
    print('Azure ML SDK Version: {}'.format(azureml.core.VERSION))

    model_path = data_path = str(Path(args.base_path).resolve().joinpath(args.model).resolve())
    rgs = {
        'model_path': model_path,
        'model_name': args.model_name
    }

    # printing out args for posterity
    for i in rgs:
        print('{} => {}'.format(i, rgs[i]))

    run(**rgs)

    # python release.py -b .. -m model/latest.h5 -n dogsandcats
