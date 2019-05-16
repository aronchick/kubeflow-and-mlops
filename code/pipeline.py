import kfp.dsl as dsl
from kubernetes import client as k8s_client

@dsl.pipeline(
    name='DogsVCats',
    description='Simple TF CNN for binary classifier between dogs and cats'
)
def dogsandcats_train(
    persistent_volume_name='azure',
    persistent_volume_path='/mnt/azure'
    base_path='/mnt/azure',
    epochs=5,
    batch=32,
    learning_rate=0.0001
):


    operations = {}

    # preprocess data
    operations['preprocess'] = dsl.ContainerOp(
        name='preprocess',
        image='kubeflowregistry.azurecr.io/kubeflow/preprocess',
        command=['python'],
        arguments=[
            '/scripts/data.py',
            '--base_path', persistent_volume_path,
            '--data', 'train',
            '--target', 'train.txt',
            '--img_size', '160',
            '--zipfile', 'https://location_to_data'
        ]
    )

    # train
    operations['train'] = dsl.ContainerOp(
        name='train',
        image='kubeflowregistry.azurecr.io/kubeflow/train',
        command=['python'],
        arguments=[
            '/scripts/train.py',
            '--base_path', persistent_volume_path,
            '--data', 'train', 
            '--epochs', epochs, 
            '--batch', batch, 
            '--image_size', '160', 
            '--lr', learning_rate, 
            '--outputs', 'model', 
            '--dataset', 'train.txt'
        ]
    )
    operations['train'].after(operations['preprocess'])

    # score
    operations['score'] = dsl.ContainerOp(
        name='score',
        image='kubeflowregistry.azurecr.io/kubeflow/score',
        command=['python'],
        arguments=[
            '/scripts/score.py',
            '--base_path', persistent_volume_path,
            '--model', 'model/latest.h5'
        ]
    )
    operations['score'].after(operations['train'])

    #release
    operations['release'] = dsl.ContainerOp(
        name='release',
        image='kubeflowregistry.azurecr.io/kubeflow/release',
        command=['python'],
        arguments=[
            '/scripts/release.py',
            '--base_path', persistent_volume_path,
            '--model', 'model/latest.h5',
            '--model_name', 'model/latest.h5'
        ]
    )
    operations['release'].after(operations['score'])

    for _, op in operations.items():
        op.add_volume(
                k8s_client.V1Volume(
                    host_path=k8s_client.V1HostPathVolumeSource(
                        path=persistent_volume_path),
                        name=persistent_volume_name)
                ) \
            .add_volume_mount(k8s_client.V1VolumeMount(
                mount_path=persistent_volume_path, 
                name=persistent_volume_name))

if __name__ == '__main__':
   import kfp.compiler as compiler
   compiler.Compiler().compile(dogsandcats_train, __file__ + '.tar.gz')
