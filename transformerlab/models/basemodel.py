import os

import transformerlab.db as db


class BaseModel:
    """
    A basic representation of a Model in TransformerLab.

    To add a new model source, create a subclass.
    The key function to override in your subclass is get_model_path.
    Then in your subclass' constructor call super and then set any additional
    fields you want to store in the model's JSON.

    Properties:
    id:             Unique Transformer Lab model identifier
    name:           Printable name for the model (how it appears in the app)
    architecture:   A string describing the model architecture used to determine
                    support for the model and how to run
    formats:        A array of strings describing the file format used to store model
                    weights. This can be "safetensors", "bin", "gguf", "mlx".
    status:         A text string that is either "OK" or contains and error message

    model_source:   Where the model is stored ("huggingface", "local", etc.)
    source_id_or_path:
                    The id of this model in it source (or path for local files)
    model_filename: With source_id_or_path, a specific filename for this model.
                    For example, GGUF repos have several files representing
                    different versions of teh model.

    json_data:      an unstructured data blob that can contain any data relevant 
                    to the model or its model_source.
    """

    
    def __init__(self, id):
        """
        The constructor takes an ID that is unique to the model source.
        This may be different than the unique ID used in Transformer Lab (self.unique_id).

        That is, model sources (hard drive folders, application caches, web sites, etc.)
        will have subclasses of this BaseModel and may use the same id, but their unique_id
        must be unique to TransformerLab in order to import into the Transfoerm Lab store.
        """

        self.id = id
        self.name = id
        self.architecture = "unknown"
        self.formats = []
        self.status = "OK"

        self.model_source = None
        self.source_id_or_path = id
        self.model_filename = None

        # While json_data is unstructured and flexible
        # These are the fields that the app generally expects to exist
        self.json_data = {
            "uniqueID": self.id,
            "model_filename": "",

            "name": self.id,
            "description": "",
            "architecture": self.architecture,
            "formats": self.formats,
            "source": self.model_source,
            "source_id_or_path": self.source_id_or_path,
            "huggingface_repo": "",

            "parameters": "",
            "context": "",
            "license": "",
            "logo": "",

            # The following are from huggingface_hu.hf_api.ModelInfo
            "private": False, 
            "gated": False, # Literal["auto", "manual", False]
            "model_type": "",
            "library_name": "", 
            "transformers_version": ""
        }


    def __str__(self):
        # For debug output
        return str(self.__class__) + ": " + str(self.__dict__)


    async def is_installed(self):
        '''
        Returns true if this model is saved in Transformer Lab's Local Store.
        '''
        db_model = await db.model_local_get(self.id)
        return db_model is not None


    async def install(self):
        await db.model_local_create(model_id=self.id, name=self.name, json_data=self.json_data)


    def get_model_path(self):
        '''
        Returns ID of model in source OR absolute path to file or directory that contains model.
        Most subclasses will probably want to override this so TransformerLab knows where to
        find the model.
        '''
        if self.model_filename:
            return os.path.join(self.source_id_or_path, self.model_filename)
        else:
            return self.source_id_or_path


# MODEL UTILITY FUNCTIONS


def get_model_file_format(filename: str):
    """
    Helper method available to subclasses to detect format of contained model weight files.
    Returns None if the file doesn't match any of the known types.
    """
    formats = {
        ".safetensors" : "Safetensors",
        ".bin" : "PyTorch",
        ".pt" : "PyTorch",
        ".pth" : "PyTorch",
        ".pkl": "Pickle",
        ".gguf": "GGUF",
        ".ggml": "GGUF",
        ".keras": "Keras",
        ".npz": "NPZ",
        ".llamafile": "Llamafile",
        ".onnx": "ONNX",
        ".ckpt": "TensorFlow CHeckpoint"
    }
    _, file_ext = os.path.splitext(filename)

    # If the extension doesn't exist then return None
    return formats.get(file_ext, None)