from kubeflow.fairing.preprocessors.base import BasePreProcessor


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

        


