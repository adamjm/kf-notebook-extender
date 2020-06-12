import logging
import tempfile

from kubeflow.fairing.constants import constants

logger = logging.getLogger('fairing')

# TODO(@karthikv2k): Need to be refractored into a better template
def write_dockerfile(
        docker_command=None,
        destination=None,
        reqs_path="/tmp",
        path_prefix=constants.DEFAULT_DEST_PREFIX,
        base_image=None,
        input_reqs_files=None):
    """Generate dockerfile accoding to the parameters
    :param docker_command: string, CMD of the dockerfile (Default value = None)
    :param destination: string, destination folder for this dockerfile (Default value = None)
    :param path_prefix: string, WORKDIR (Default value = constants.DEFAULT_DEST_PREFIX)
    :param base_image: string, base image, example: gcr.io/kubeflow-image
    :param install_reqs_before_copy: whether to install the prerequisites (Default value = False)
    """
    if not destination:
        _, destination = tempfile.mkstemp(prefix="/tmp/fairing_dockerfile_")
    content_lines = ["FROM {}".format(base_image)]
    copy_context = "COPY {} {}".format(path_prefix, path_prefix)
    if input_reqs_files:
        for file_ in input_reqs_files:
            if file_ == "environment.yml":
                content_lines.append("COPY {}/{} {}".format(reqs_path, file_, path_prefix))
                content_lines.append("RUN conda env update --file {}/{}  --prune && conda clean --all -f -y".format(path_prefix, file_))
            elif file_ == "requirements.txt":
                content_lines.append("COPY {}/{} {}".format(reqs_path, file_, path_prefix))
                content_lines.append("RUN pip install --no-cache -r {}/{}".format(path_prefix, file_))
    content_lines.append(copy_context)

    if docker_command:
        content_lines.append("CMD {}".format(" ".join(docker_command)))

    content = "\n".join(content_lines)
    with open(destination, 'w') as f:
        f.write(content)
    return destination