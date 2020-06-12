from kubeflow.fairing.preprocessors.base import BasePreProcessor
from kubeflow.fairing.builders.cluster.minio_context import MinioContextSource
from nbextender.cluster import NBClusterBuilder
import os
from kubernetes import client
import platform
import subprocess
from kubeflow import fairing


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
        fairing.config.set_builder(
            name='cluster',
            registry=self.image_registry,
            context_source=minio_context_source,
            cleanup=True)
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
