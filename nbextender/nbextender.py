from kubeflow.fairing.preprocessors.base import BasePreProcessor
from kubeflow.fairing.builders.cluster.minio_context import MinioContextSource
from nbextender.cluster import NBClusterBuilder
import os
from kubernetes import client
import platform
import subprocess
from kubeflow import fairing
from kubernetes import client
from kubernetes.client.models.v1_resource_requirements import V1ResourceRequirements
from kubeflow.fairing.constants import constants



class NBExtender(object):
    def __init__(self, image_registry, new_image, context_source_type=None):
        self.image_name = new_image
        if context_source_type is None:
            raise RuntimeError("context_source_type is not specified")
        self.context_source_type = context_source_type
        self.get_global_state()
        self.set_context_source()
        self.image_registry = image_registry

    def get_global_state(self):
        pod_name = platform.node()
        self.arch = platform.machine()
        self.current_image_name = self.get_current_image(pod_name)
    
    def get_local_state(self):
        subprocess.run(["conda", "envs", "export", ">", "/tmp/environment.yml"])


    def get_host_alias_mutator(self, hosts_dict):
        """
        The mutator adds environment variables to the kaniko deployment and
        adds the environment variables as build args for the kaniko build. 
        :param env_dict: Dict of all environment variabels to be added
        returns: object: The mutator function for setting environment variables
        """
        def _hosts_mutator(kube_manager, pod_spec, namespace): #pylint:disable=unused-argument
            if env_dict is None:
                return
            if pod_spec.containers and len(pod_spec.containers) >= 1:
                # All cloud providers specify their instace memory in GB
                # so it is peferable for user to specify memory in GB
                # and we convert it to Gi that K8s needs
                if pod_spec.containers[0].args:
                    current_args = pod_spec.containers[0].args
                    for k,v in env_dict:
                        barg = "--build-arg {0}={1}".format(k,v)
                        current_args.append(barg)
                    pod_spec.containers[0].args = current_args
                if pod_spec.containers[0].env:
                    current_env = pod_spec.containers[0].env
                    for k,v in env_dict:
                        nenv = client.v1envvar(name=k, value=v)
                        current_env.append(nenv)
                    pod_spec.containers[0].env = current_env
                else:
                    current_env = []
                    for k,v in env_dict:
                        nenv = client.v1envvar(name=k, value=v)
                        current_env.append(nenv)
                    pod_spec.containers[0].env = current_env
        return _hosts_mutator

    def get_environment_mutator(self, env_dict):
        """
        The mutator adds environment variables to the kaniko deployment and
        adds the environment variables as build args for the kaniko build. 
        :param env_dict: Dict of all environment variabels to be added
        returns: object: The mutator function for setting environment variables
        """
        def _env_mutator(kube_manager, pod_spec, namespace): #pylint:disable=unused-argument
            if env_dict is None:
                return
            if pod_spec.containers and len(pod_spec.containers) >= 1:
                # All cloud providers specify their instace memory in GB
                # so it is peferable for user to specify memory in GB
                # and we convert it to Gi that K8s needs
                if pod_spec.containers[0].args:
                    current_args = pod_spec.containers[0].args
                    for k,v in env_dict:
                        barg = "--build-arg {0}={1}".format(k,v)
                        current_args.append(barg)
                    pod_spec.containers[0].args = current_args
                if pod_spec.containers[0].env:
                    current_env = pod_spec.containers[0].env
                    for k,v in env_dict:
                        nenv = client.v1envvar(name=k, value=v)
                        current_env.append(nenv)
                    pod_spec.containers[0].env = current_env
                else:
                    current_env = []
                    for k,v in env_dict:
                        nenv = client.v1envvar(name=k, value=v)
                        current_env.append(nenv)
                    pod_spec.containers[0].env = current_env
        return _env_mutator

def get_resource_mutator(cpu=None, memory=None, gpu=None):
    """The mutator for getting the resource setting for pod spec.
    The useful example:
    https://github.com/kubeflow/fairing/blob/master/examples/train_job_api/main.ipynb
    :param cpu: Limits and requests for CPU resources (Default value = None)
    :param memory: Limits and requests for memory (Default value = None)
    :returns: object: The mutator function for setting cpu and memory in pod spec.
    """
    def _resource_mutator(kube_manager, pod_spec, namespace): #pylint:disable=unused-argument
        if cpu is None and memory is None and gpu is None:
            return
        if pod_spec.containers and len(pod_spec.containers) >= 1:
            # All cloud providers specify their instace memory in GB
            # so it is peferable for user to specify memory in GB
            # and we convert it to Gi that K8s needs
            limits = {}
            if cpu:
                limits['cpu'] = cpu
            if memory:
                memory_gib = "{}Gi".format(round(memory/1.073741824, 2))
                limits['memory'] = memory_gib
            if gpu:
                limits['nvidia.com/gpu'] = gpu
            if pod_spec.containers[0].resources:
                if pod_spec.containers[0].resources.limits:
                    pod_spec.containers[0].resources.limits = {}
                for k, v in limits.items():
                    pod_spec.containers[0].resources.limits[k] = v
            else:
                pod_spec.containers[0].resources = V1ResourceRequirements(limits=limits)
    return _resource_mutator
        
    def get_current_image(self, pod_name):
      v1 = client.CoreV1Api()
      print("Listing pods")
      ret = v1.list_pod_for_all_namespaces(watch=False)
      for i in ret.items:
          if i.metadata.name == pod_name:
              current_images = i.spec.containers
              for j in current_images:
                  if j.name == pod_name:
                      current_image = j.image
                  else:
                      raise RuntimeError("Can not get current image name")
          else:
              raise RuntimeError("Can not get current image name")
      return current_image
          
    def set_context_source(self):
        if self.context_source_type == "minio":
            endpoint_url = os.environ.get("MINIO_URL")
            minio_secret=os.environ.get("ACCESSKEY")
            minio_secret_key=os.environ.get("SECRETKEY")
            region_name=os.environ.get("REGION")
            if region_name is None:
                region_name = "us-east-1"
            if endpoint_url is None or minio_secret is None or minio_secret_key is None:
                raise RuntimeError("Minio configuration not specified in Environment variables")
            self.context_source = MinioContextSource( endpoint_url, minio_secret, minio_secret_key, region_name)

    def save(self):
        self.get_local_state()
        preprocessor = NotebookExtenderPreProcessor(input_files=['/tmp/environment.yml'])
        builder = NBClusterBuilder(context_source=self.context_source, preprocessor=preprocessor, ) 
       
        fairing.config.run()
          
        # get current state
        ## python installs ubuntu installs
        # send current state to builder
        pass





class NotebookExtenderPreProcessor(BasePreProcessor):
    """ The notebook externder preprocess for the context that comes from BasePreProcessor.
    : param BasePreProcessor: a context that gets sent to the builder for the docker build and
    sets the entrypoint """

    def __init__(self, path_prefix=constants.DEFAULT_DEST_PREFIX,
                input_files=None):
        """Init the function preprocess class
          :param input_files: the source files to be processed.
        """
        super().__init__(
            path_prefix=path_prefix,
            input_files=input_files)
            
            
    
    def is_update_file_present(self):
        """ Verfiy the environment txt file if it is present.
        :returns: res: get the present required files
        """
        dst_files = self.context_map().keys()
        env_file = posixpath.join(self.path_prefix, "environment.yml")
        reqs_file = posixpath.join(self.path_prefix, "requirements.txt")
        res = reqs_file in dst_files
        envs = env_file in dst_files
        return res or envs 
