import kfp.dsl as dsl
from kubernetes import client as k8s_client


@dsl.pipeline(
    name='Tacos vs. Burritos',
    description='Simple TF CNN for binary classifier between burritos and tacos'
)
def tacosandburritos_train(
    tenant_id,
    service_principal_id,
    service_principal_password,
    subscription_id,
    resource_group,
    workspace,
    persistent_volume_name='azure',
    persistent_volume_path='/mnt/azure',
    data_download='https://centeotl.blob.core.windows.net/public/tacodata.zip',
    epochs=5,
    batch=32,
    learning_rate=0.0001,
    imagetag='latest',
    model_name='tacosandburritos',
):

    operations = {}
    image_size = 160
    training_folder = 'train'
    training_dataset = 'train.txt'
    model_folder = 'model'

    # preprocess data
    operations['preprocess'] = dsl.ContainerOp(
        name='preprocess',
        image='kubeflowregistry.azurecr.io/kubeflow/preprocess:' + str(imagetag),
        command=['python'],
        arguments=[
            '/scripts/data.py',
            '--base_path', persistent_volume_path,
            '--data', training_folder,
            '--target', training_dataset,
            '--img_size', image_size,
            '--zipfile', data_download
        ]
    )

    # train
    operations['training'] = dsl.ContainerOp(
        name='training',
        image='kubeflowregistry.azurecr.io/kubeflow/training:' + str(imagetag),
        command=['python'],
        arguments=[
            '/scripts/train.py',
            '--base_path', persistent_volume_path,
            '--data', training_folder, 
            '--epochs', epochs, 
            '--batch', batch, 
            '--image_size', image_size, 
            '--lr', learning_rate, 
            '--outputs', model_folder, 
            '--dataset', training_dataset
        ]
    )
    operations['training'].after(operations['preprocess'])

    # register model
    operations['register'] = dsl.ContainerOp(
        name='register',
        image='kubeflowregistry.azurecr.io/kubeflow/register:' + str(imagetag),
        command=['python'],
        arguments=[
            '/scripts/register.py',
            '--base_path', persistent_volume_path,
            '--model', 'latest.h5',
            '--model_name', model_name,
            '--tenant_id', tenant_id,
            '--service_principal_id', service_principal_id,
            '--service_principal_password', service_principal_password,
            '--subscription_id', subscription_id,
            '--resource_group', resource_group,
            '--workspace', workspace
        ]
    )
    operations['register'].after(operations['training'])

    for _, op in operations.items():
        op.container.set_image_pull_policy("Always")
        op.add_volume(
            k8s_client.V1Volume(
                name=persistent_volume_name,
                persistent_volume_claim=k8s_client.V1PersistentVolumeClaimVolumeSource(
                    claim_name='azure-managed-disk')
                )
            ).add_volume_mount(k8s_client.V1VolumeMount(
                mount_path=persistent_volume_path, 
                name=persistent_volume_name)
            )


if __name__ == '__main__':
   import kfp.compiler as compiler
   compiler.Compiler().compile(tacosandburritos_train, __file__ + '.tar.gz')
