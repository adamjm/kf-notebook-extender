from kubeflow.fairing.preprocessors.base import BasePreProcessor
from kubeflow.fairing.builders.cluster.minio_context import MinioContextSource

class NBExtender(object):
	def __init__(self, new_image, base_image, context_source_type=None):
		self.image_name = new_image
		self.base_image = base_image
		
	  if context_source_type is None:
	  	raise RuntimeError("context_source_type is not specified")
    self.context_source_type = context_source_type
        
	def get_global_state(self):
		# get current image
		# self.base_image 
		# get minio config
		# get arch
		
	def set_context_source(self):
		if self.context_source_type == "minio":
		  endpoint_url = os.environ.get("MINIO_URL")
		  minio_secret=os.environ.get("ACCESSKEY")
		  minio_secret_key=os.environ.get("SECRETKEY")
      region_name=os.environ.get("REGION")
			self.context_source =	MinioContextSource( endpoint_url, minio_secret, minio_secret_key,
                 region_name)
      
		
	
		
		
	def save(self):
		# get current state
		## python installs ubuntu installs
		# send current state to builder
		




class NotebookExtenderPreProcessor(BasePreProcessor):
    """ The notebook externder preprocess for the context that comes from BasePreProcessor.
    : param BasePreProcessor: a context that gets sent to the builder for the docker build and 
    sets the entrypoint """

    def __init__(self, 
                path_prefix=constants.DEFAULT_DEST_PREFIX,
                input_files=None):
        """Init the function preprocess class
          :param input_files: the source files to be processed.
        """
        super().__init__(
            path_prefix=path_prefix,
            input_files=input_files)

        


