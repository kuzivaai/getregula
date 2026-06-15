## deepface/deepface/DeepFace.py
```
# common dependencies
import os
import warnings
import logging
from typing import Any, Dict, IO, List, Union, Optional, Sequence, Tuple, cast

# this has to be set before importing tensorflow
os.environ["TF_USE_LEGACY_KERAS"] = "1"

# pylint: disable=wrong-import-position, too-many-positional-arguments

# 3rd party dependencies
from numpy.typing import NDArray
import pandas as pd
import tensorflow as tf
from lightphe import LightPHE
from lightdsa import LightDSA

# package dependencies
from deepface.commons import package_utils, folder_utils
from deepface.commons.logger import Logger
from deepface.modules import (
    modeling,
    representation,
    verification,
    recognition,
    demography,
    detection,
    streaming,
    preprocessing,
    datastore,
)
from deepface import __version__

logger = Logger()

# -----------------------------------
# configurations for dependencies

# users should install tf_keras package if they are using tf 2.16 or later versions
package_utils.validate_for_keras3()

warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
tf_version = package_utils.get_tf_major_version()
if tf_version == 2:
    tf.get_logger().setLevel(logging.ERROR)
# -----------------------------------

# create required folders if necessary to store model weights

```

## deepface/deepface/api/src/app.py
```
# 3rd parth dependencies
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# load environment variables from .env first things first
load_dotenv()


# pylint: disable=wrong-import-position
# project dependencies
from deepface import __version__
from deepface.api.src.modules.core.routes import blueprint
from deepface.api.src.dependencies.variables import Variables
from deepface.api.src.dependencies.container import Container
from deepface import DeepFace
from deepface.commons.logger import Logger

logger = Logger()


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    variables = Variables()
    container = Container(variables=variables)

    # inject variables
    blueprint.variables = variables  # type: ignore[attr-defined]
    blueprint.container = container  # type: ignore[attr-defined]

    load_models_on_startup(variables)

    app.register_blueprint(blueprint)

    logger.info(f"Welcome to DeepFace API v{__version__}!")
    return app


def load_models_on_startup(variables: Variables) -> None:
    """Load models on startup to reduce latency on first request."""
    face_recognition_models = variables.face_recognition_models
    if face_recognition_models is not None:
        for model in face_recognition_models.split(","):
            DeepFace.build_model(task="facial_recognition", model_name=model.strip())
            logger.info(f"Facial Recognition Model {model} loaded on startup.")
    face_detection_models = variables.face_detection_models
    if face_detection_models is not None:
        for model in face_detection_models.split(","):

```

## deepface/deepface/commons/weight_utils.py
```
# built-in dependencies
import os
from typing import Optional
import zipfile
import bz2

# 3rd party dependencies
import gdown

# project dependencies
from deepface.commons import folder_utils, package_utils
from deepface.commons.logger import Logger
from deepface.modules.exceptions import UnimplementedError


tf_version = package_utils.get_tf_major_version()
if tf_version == 1:
    from keras.models import Sequential
else:
    from tensorflow.keras.models import Sequential

logger = Logger()

# pylint: disable=line-too-long, use-maxsplit-arg

ALLOWED_COMPRESS_TYPES = ["zip", "bz2"]


def download_weights_if_necessary(
    file_name: str, source_url: str, compress_type: Optional[str] = None
) -> str:
    """
    Download the weights of a pre-trained model from external source if not downloaded yet.
    Args:
        file_name (str): target file name with extension
        source_url (url): source url to be downloaded
        compress_type (optional str): compress type e.g. zip or bz2
    Returns
        target_file (str): exact path for the target file
    """
    home = folder_utils.get_deepface_home()

    target_file = os.path.normpath(os.path.join(home, ".deepface/weights", file_name))

    if os.path.isfile(target_file):
        logger.debug(f"{file_name} is already available at {target_file}")
        return target_file

    if compress_type is not None and compress_type not in ALLOWED_COMPRESS_TYPES:
        raise UnimplementedError(f"unimplemented compress type - {compress_type}")

```

## deepface/deepface/models/FacialRecognition.py
```
# standard library imports
from abc import ABC
from typing import Any, Union, List, Tuple, cast

# third party imports
import numpy as np
from numpy.typing import NDArray

# project imports
from deepface.commons import package_utils
from deepface.modules.exceptions import InvalidEmbeddingsShapeError

tf_version = package_utils.get_tf_major_version()
if tf_version == 2:
    from tensorflow.keras.models import Model
else:
    from keras.models import Model

# Notice that all facial recognition models must be inherited from this class


# pylint: disable=too-few-public-methods
class FacialRecognition(ABC):
    model: Union[Model, Any]
    model_name: str
    input_shape: Tuple[int, int]
    output_shape: int

    def forward(self, img: NDArray[Any]) -> Union[List[float], List[List[float]]]:
        if not isinstance(self.model, Model):
            raise ValueError(
                "You must overwrite forward method if it is not a keras model,"
                f"but {self.model_name} not overwritten!"
            )

        # predict expexts e.g. (1, 224, 224, 3) shaped inputs
        if img.ndim == 3:
            img = np.expand_dims(img, axis=0)

        if img.ndim == 4 and img.shape[0] == 1:
            # model.predict causes memory issue when it is called in a for loop
            # embedding = model.predict(img, verbose=0)[0].tolist()
            embeddings = self.model(img, training=False).numpy()
        elif img.ndim == 4 and img.shape[0] > 1:
            embeddings = self.model.predict_on_batch(img)
        else:
            raise InvalidEmbeddingsShapeError(
                f"Input image must be (1, X, X, 3) shaped but it is {img.shape}"
            )

        assert isinstance(
            embeddings, np.ndarray
        ), f"Embeddings must be numpy array but it is {type(embeddings)}"

        if embeddings.shape[0] == 1:
            return cast(List[float], embeddings[0].tolist())
        return cast(List[List[float]], embeddings.tolist())

```

## deepface/deepface/models/demography/Age.py
```
# stdlib dependencies
from typing import List, Union, Any, cast

# 3rd party dependencies
import numpy as np
from numpy.typing import NDArray

# project dependencies
from deepface.models.facial_recognition import VGGFace
from deepface.commons import package_utils, weight_utils
from deepface.models.Demography import Demography
from deepface.commons.logger import Logger

logger = Logger()

# dependency configurations

tf_version = package_utils.get_tf_major_version()

if tf_version == 1:
    from keras.models import Model, Sequential
    from keras.layers import Convolution2D, Flatten, Activation
else:
    from tensorflow.keras.models import Model, Sequential
    from tensorflow.keras.layers import Convolution2D, Flatten, Activation

WEIGHTS_URL = (
    "https://github.com/serengil/deepface_models/releases/download/v1.0/age_model_weights.h5"
)


# pylint: disable=too-few-public-methods
class ApparentAgeClient(Demography):
    """
    Age model class
    """

    def __init__(self) -> None:
        self.model = load_model()
        self.model_name = "Age"

    def predict(
        self, img: Union[NDArray[Any], List[NDArray[Any]]]
    ) -> Union[np.float64, NDArray[Any]]:
        """
        Predict apparent age(s) for single or multiple faces
        Args:
            img: Single image as np.ndarray (224, 224, 3) or
                List of images as List[np.ndarray] or
                Batch of images as np.ndarray (n, 224, 224, 3)

```

## deepface/deepface/models/demography/Gender.py
```
# stdlib dependencies

from typing import List, Union, Any

# 3rd party dependencies
from numpy.typing import NDArray

# project dependencies
from deepface.models.facial_recognition import VGGFace
from deepface.commons import package_utils, weight_utils
from deepface.models.Demography import Demography
from deepface.commons.logger import Logger

logger = Logger()

# -------------------------------------
# pylint: disable=line-too-long
# -------------------------------------
# dependency configurations

tf_version = package_utils.get_tf_major_version()
if tf_version == 1:
    from keras.models import Model, Sequential
    from keras.layers import Convolution2D, Flatten, Activation
else:
    from tensorflow.keras.models import Model, Sequential
    from tensorflow.keras.layers import Convolution2D, Flatten, Activation

WEIGHTS_URL = (
    "https://github.com/serengil/deepface_models/releases/download/v1.0/gender_model_weights.h5"
)

# Labels for the genders that can be detected by the model.
labels = ["Woman", "Man"]


# pylint: disable=too-few-public-methods
class GenderClient(Demography):
    """
    Gender model class
    """

    def __init__(self) -> None:
        self.model = load_model()
        self.model_name = "Gender"

    def predict(self, img: Union[NDArray[Any], List[NDArray[Any]]]) -> NDArray[Any]:
        """
        Predict gender probabilities for single or multiple faces
        Args:

```

## deepface/deepface/models/demography/Race.py
```
# stdlib dependencies
from typing import List, Union, Any

# 3rd party dependencies
from numpy.typing import NDArray

# project dependencies
from deepface.models.facial_recognition import VGGFace
from deepface.commons import package_utils, weight_utils
from deepface.models.Demography import Demography
from deepface.commons.logger import Logger

# pylint: disable=line-too-long

# dependency configurations
tf_version = package_utils.get_tf_major_version()

if tf_version == 1:
    from keras.models import Model, Sequential
    from keras.layers import Convolution2D, Flatten, Activation
else:
    from tensorflow.keras.models import Model, Sequential
    from tensorflow.keras.layers import Convolution2D, Flatten, Activation

WEIGHTS_URL = (
    "https://github.com/serengil/deepface_models/releases/download/v1.0/race_model_single_batch.h5"
)
# Labels for the ethnic phenotypes that can be detected by the model.
labels = ["asian", "indian", "black", "white", "middle eastern", "latino hispanic"]

logger = Logger()


# pylint: disable=too-few-public-methods
class RaceClient(Demography):
    """
    Race model class
    """

    def __init__(self) -> None:
        self.model = load_model()
        self.model_name = "Race"

    def predict(self, img: Union[NDArray[Any], List[NDArray[Any]]]) -> NDArray[Any]:
        """
        Predict race probabilities for single or multiple faces
        Args:
            img: Single image as np.ndarray (224, 224, 3) or
                List of images as List[np.ndarray] or
                Batch of images as np.ndarray (n, 224, 224, 3)

```

## deepface/deepface/models/facial_recognition/ArcFace.py
```
# built-in dependencies
from typing import Any

# project dependencies
from deepface.commons import package_utils, weight_utils
from deepface.models.FacialRecognition import FacialRecognition

from deepface.commons.logger import Logger

logger = Logger()

# pylint: disable=unsubscriptable-object

# --------------------------------
# dependency configuration

tf_version = package_utils.get_tf_major_version()

if tf_version == 1:
    from keras.models import Model
    from keras.layers import (
        ZeroPadding2D,
        Input,
        Conv2D,
        BatchNormalization,
        PReLU,
        Add,
        Dropout,
        Flatten,
        Dense,
    )
else:
    from tensorflow.keras.models import Model
    from tensorflow.keras.layers import (
        ZeroPadding2D,
        Input,
        Conv2D,
        BatchNormalization,
        PReLU,
        Add,

```

## deepface/deepface/models/facial_recognition/VGGFace.py
```
# built-in dependencies
from typing import List, cast, Any

# 3rd party dependencies
from numpy.typing import NDArray

# project dependencies
from deepface.commons import package_utils, weight_utils
from deepface.modules import verification
from deepface.models.FacialRecognition import FacialRecognition
from deepface.commons.logger import Logger

logger = Logger()

# ---------------------------------------

tf_version = package_utils.get_tf_major_version()
if tf_version == 1:
    from keras.models import Model, Sequential
    from keras.layers import (
        Convolution2D,
        ZeroPadding2D,
        MaxPooling2D,
        Flatten,
        Dropout,
        Activation,
    )
else:
    from tensorflow.keras.models import Model, Sequential
    from tensorflow.keras.layers import (
        Convolution2D,
        ZeroPadding2D,
        MaxPooling2D,
        Flatten,
        Dropout,
        Activation,
    )

# ---------------------------------------


```

## deepface/deepface/modules/database/milvus.py
```
# built-in dependencies
import os
import json
import hashlib
import struct
from typing import Any, Dict, Optional, List, Union

# project dependencies
from deepface.modules.database.types import Database
from deepface.modules.modeling import build_model
from deepface.commons.logger import Logger

logger = Logger()


class MilvusClient(Database):
    """
    Milvus client for storing and retrieving face embeddings and indices.
    """

    def __init__(
        self,
        connection_details: Optional[Union[str, Dict[str, Any]]] = None,
        connection: Any = None,
    ):
        try:
            from pymilvus import MilvusClient as _MilvusClient, DataType
        except (ModuleNotFoundError, ImportError) as e:
            raise ValueError(
                "pymilvus is an optional dependency. Install with 'pip install pymilvus'"
            ) from e

        self.MilvusClient = _MilvusClient
        self.DataType = DataType

        if connection is not None:
            self.client = connection
        else:
            self.conn_details = connection_details or os.environ.get("DEEPFACE_MILVUS_URI")
            if not self.conn_details or not isinstance(self.conn_details, str):
                raise ValueError(
                    "Milvus URI must be provided as a string in connection_details "
                    "or via DEEPFACE_MILVUS_URI environment variable."
                )

            self.client = self.MilvusClient(uri=self.conn_details)

    def initialize_database(self, **kwargs: Any) -> None:
        """
        Ensure Milvus collection exists.
        """
        model_name = kwargs.get("model_name", "VGG-Face")
        detector_backend = kwargs.get("detector_backend", "opencv")
        aligned = kwargs.get("aligned", True)
        l2_normalized = kwargs.get("l2_normalized", False)

        collection_name = self.__generate_collection_name(
            model_name, detector_backend, aligned, l2_normalized
        )


```

## deepface/deepface/modules/database/neo4j.py
```
# built-in dependencies
import os
import json
import hashlib
import struct
from typing import Any, Dict, Optional, List, Union
from urllib.parse import urlparse


# project dependencies
from deepface.modules.database.types import Database
from deepface.modules.modeling import build_model
from deepface.modules.verification import find_cosine_distance, find_euclidean_distance
from deepface.commons.logger import Logger

logger = Logger()

_SCHEMA_CHECKED: Dict[str, bool] = {}


# pylint: disable=too-many-positional-arguments
class Neo4jClient(Database):
    def __init__(
        self,
        connection_details: Optional[Union[Dict[str, Any], str]] = None,
        connection: Any = None,
    ) -> None:
        # Import here to avoid mandatory dependency
        try:
            from neo4j import GraphDatabase
        except (ModuleNotFoundError, ImportError) as e:
            raise ValueError(
                "neo4j is an optional dependency, ensure the library is installed."
                "Please install using 'pip install neo4j' "
            ) from e

        self.GraphDatabase = GraphDatabase
        if connection is not None:
            self.conn = connection
        else:
            self.conn_details = connection_details or os.environ.get("DEEPFACE_NEO4J_URI")
            if not self.conn_details:
                raise ValueError(
                    "Neo4j connection information not found. "
                    "Please provide connection_details or set the DEEPFACE_NEO4J_URI"
                    " environment variable."
                )

            if isinstance(self.conn_details, str):
                parsed = urlparse(self.conn_details)
                uri = f"{parsed.scheme}://{parsed.hostname}:{parsed.port}"
                self.conn = self.GraphDatabase.driver(uri, auth=(parsed.username, parsed.password))
            else:
                raise ValueError("connection_details must be a string.")

        if not self.__is_gds_installed():
            raise ValueError(
                "Neo4j Graph Data Science (GDS) plugin is not installed. "
                "Please install the GDS plugin to use Neo4j as a database backend."
            )

```

## deepface/deepface/modules/database/pgvector.py
```
# built-in dependencies
import os
import json
import struct
import hashlib
from typing import Any, Dict, Optional, List, Union

# 3rd party dependencies
import numpy as np

# project dependencies
from deepface.modules.modeling import build_model
from deepface.modules.database.types import Database
from deepface.modules.exceptions import DuplicateEntryError
from deepface.commons.logger import Logger

logger = Logger()


_SCHEMA_CHECKED: Dict[str, bool] = {}


# pylint: disable=too-many-positional-arguments
class PGVectorClient(Database):
    def __init__(
        self,
        connection_details: Optional[Union[Dict[str, Any], str]] = None,
        connection: Any = None,
    ) -> None:
        # Import here to avoid mandatory dependency
        try:
            import psycopg
            from psycopg import errors
        except (ModuleNotFoundError, ImportError) as e:
            raise ValueError(
                "psycopg is an optional dependency, ensure the library is installed."
                "Please install using 'pip install \"psycopg[binary]\"' "
            ) from e

        try:
            from pgvector.psycopg import register_vector
        except (ModuleNotFoundError, ImportError) as e:
            raise ValueError(
                "pgvector is an optional dependency, ensure the library is installed."
                "Please install using 'pip install pgvector' "
            ) from e

        self.psycopg = psycopg
        self.errors = errors

        if connection is not None:
            self.conn = connection
        else:
            # Retrieve connection details from parameter or environment variable
            self.conn_details = connection_details or os.environ.get("DEEPFACE_POSTGRES_URI")
            if not self.conn_details:
                raise ValueError(
                    "PostgreSQL connection information not found. "
                    "Please provide connection_details or set the DEEPFACE_POSTGRES_URI"
                    " environment variable."

```

## deepface/deepface/modules/database/pinecone.py
```
# built-in dependencies
import os
import json
import hashlib
import struct
import math
from typing import Any, Dict, Optional, List, Union

# project dependencies
from deepface.modules.database.types import Database
from deepface.modules.modeling import build_model
from deepface.commons.logger import Logger

logger = Logger()


class PineconeClient(Database):
    """
    Pinecone client for storing and retrieving face embeddings and indices.
    """

    def __init__(
        self,
        connection_details: Optional[Union[str, Dict[str, Any]]] = None,
        connection: Any = None,
    ):
        try:
            from pinecone import Pinecone, ServerlessSpec
        except (ModuleNotFoundError, ImportError) as e:
            raise ValueError(
                "pinecone is an optional dependency. Install with 'pip install pinecone'"
            ) from e

        self.pinecone = Pinecone
        self.serverless_spec = ServerlessSpec

        if connection is not None:
            self.client = connection
        else:
            self.conn_details = connection_details or os.environ.get("DEEPFACE_PINECONE_API_KEY")
            if not isinstance(self.conn_details, str):
                raise ValueError(
                    "Pinecone api key must be provided as a string in connection_details "
                    "or via DEEPFACE_PINECONE_API_KEY environment variable."
                )

            self.client = self.pinecone(api_key=self.conn_details)

    def initialize_database(self, **kwargs: Any) -> None:
        """
        Ensure Pinecone index exists.
        """
        model_name = kwargs.get("model_name", "VGG-Face")
        detector_backend = kwargs.get("detector_backend", "opencv")
        aligned = kwargs.get("aligned", True)
        l2_normalized = kwargs.get("l2_normalized", False)

        index_name = self.__generate_index_name(
            model_name, detector_backend, aligned, l2_normalized
        )

```

## deepface/deepface/modules/database/weaviate.py
```
# built-in dependencies
import os
import json
import hashlib
import struct
import base64
import uuid
import math
from typing import Any, Dict, Optional, List, Union

# project dependencies
from deepface.modules.database.types import Database
from deepface.commons.logger import Logger

logger = Logger()


_SCHEMA_CHECKED: Dict[str, bool] = {}


# pylint: disable=too-many-positional-arguments
class WeaviateClient(Database):
    """
    Weaviate client for storing and retrieving face embeddings and indices.
    """

    def __init__(
        self,
        connection_details: Optional[Union[str, Dict[str, Any]]] = None,
        connection: Any = None,
    ):
        try:
            import weaviate
        except (ModuleNotFoundError, ImportError) as e:
            raise ValueError(
                "weaviate-client is an optional dependency. "
                "Install with 'pip install weaviate-client'"
            ) from e

        self.weaviate = weaviate

        if connection is not None:
            self.client = connection
            # URL key for _WEAVIATE_CHECKED; fallback if client has no URL
            self.url = getattr(connection, "url", str(id(connection)))
        else:
            self.conn_details = connection_details or os.environ.get("DEEPFACE_WEAVIATE_URL")
            if isinstance(self.conn_details, str):
                self.url = self.conn_details
                self.api_key = os.getenv("WEAVIATE_API_KEY")
            elif isinstance(self.conn_details, dict):
                self.url = self.conn_details.get("url")
                self.api_key = self.conn_details.get("api_key") or os.getenv("WEAVIATE_API_KEY")
            else:
                raise ValueError("connection_details must be a string or dict with 'url'.")

            if not self.url:
                raise ValueError("Weaviate URL not provided in connection_details.")

            client_config = {"url": self.url}

```

## deepface/deepface/modules/datastore.py
```
# built-in dependencies
import os
from typing import Any, Dict, IO, List, Union, Optional, cast
import uuid
import time
import math
import tempfile

# 3rd party dependencies
import pandas as pd
import numpy as np
from numpy.typing import NDArray

# project dependencies
from deepface.modules.database.types import Database
from deepface.modules.database.inventory import database_inventory

from deepface.modules.representation import represent
from deepface.modules.verification import (
    find_angular_distance,
    find_cosine_distance,
    find_euclidean_distance,
    l2_normalize as find_l2_normalize,
    find_threshold,
    find_confidence,
)
from deepface.commons.logger import Logger


logger = Logger()


# pylint: disable=too-many-positional-arguments, no-else-return
def register(
    img: Union[str, NDArray[Any], IO[bytes], List[str], List[NDArray[Any]], List[IO[bytes]]],
    img_name: Optional[str] = None,
    model_name: str = "VGG-Face",
    detector_backend: str = "opencv",
    enforce_detection: bool = True,
    align: bool = True,
    l2_normalize: bool = False,
    expand_percentage: int = 0,
    normalization: str = "base",
    anti_spoofing: bool = False,
    database_type: str = "postgres",
    connection_details: Optional[Union[Dict[str, Any], str]] = None,
    connection: Any = None,
) -> Dict[str, Any]:
    """
    Register identities to database for face recognition
    Args:
        img (str or np.ndarray or IO[bytes] or list): The exact path to the image, a numpy array
            in BGR format, a file object that supports at least `.read` and is opened in binary
            mode, or a base64 encoded image. If a list is provided, each element should be a string
            or numpy array representing an image, and the function will process images in batch.
        img_name (optional str): image name to store in db, if not provided then we will try to
            extract it from given img.
        model_name (str): Model for face recognition. Options: VGG-Face, Facenet, Facenet512,
            OpenFace, DeepFace, DeepID, Dlib, ArcFace, SFace and GhostFaceNet (default is VGG-Face).
        detector_backend (string): face detector backend. Options: 'opencv', 'retinaface',

```

## deepface/deepface/modules/recognition.py
```
# built-in dependencies
import os
import pickle
from typing import List, Union, Optional, Dict, Any, Set, IO, cast, Tuple
import time
import ast

# 3rd party dependencies
import numpy as np
from numpy.typing import NDArray
import pandas as pd
from tqdm import tqdm
from lightdsa import LightDSA

# project dependencies
from deepface.commons import image_utils
from deepface.modules import representation, detection, verification
from deepface.modules.exceptions import (
    ImgNotFound,
    PathNotFound,
    EmptyDatasource,
    SpoofDetected,
    DimensionMismatchError,
)
from deepface.commons.logger import Logger

logger = Logger()


# pylint: disable=too-many-arguments, too-many-positional-arguments
def find(
    img_path: Union[str, NDArray[Any], IO[bytes]],
    db_path: str,
    model_name: str = "VGG-Face",
    distance_metric: str = "cosine",
    enforce_detection: bool = True,
    detector_backend: str = "opencv",
    align: bool = True,
    similarity_search: bool = False,
    k: Optional[int] = None,
    expand_percentage: int = 0,
    threshold: Optional[float] = None,
    normalization: str = "base",
    silent: bool = False,
    refresh_database: bool = True,
    anti_spoofing: bool = False,
    batched: bool = False,
    credentials: Optional[Union[LightDSA, Dict[str, Any]]] = None,
) -> Union[List[pd.DataFrame], List[List[Dict[str, Any]]]]:
    """
    Identify individuals in a database

    Args:
        img_path (str or np.ndarray): The exact path to the image, a numpy array in BGR format,
            or a base64 encoded image. If the source image contains multiple faces, the result will
            include information for each detected face.

        db_path (string): Path to the folder containing image files. All detected faces
            in the database will be considered in the decision-making process.


```

## deepface/deepface/modules/representation.py
```
# built-in dependencies
from typing import Any, Dict, List, Union, Optional, Sequence, IO, cast
from collections import defaultdict

# 3rd party dependencies
import numpy as np
from numpy.typing import NDArray
from lightphe import LightPHE

# project dependencies
from deepface.commons import image_utils
from deepface.modules import modeling, detection, preprocessing
from deepface.models.FacialRecognition import FacialRecognition
from deepface.modules.normalization import normalize_embedding_l2, normalize_embedding_minmax
from deepface.modules.encryption import encrypt_embeddings
from deepface.modules.exceptions import SpoofDetected
from deepface.commons.logger import Logger

logger = Logger()


# pylint: disable=too-many-positional-arguments
def represent(
    img_path: Union[str, IO[bytes], NDArray[Any], Sequence[Union[str, NDArray[Any], IO[bytes]]]],
    model_name: str = "VGG-Face",
    enforce_detection: bool = True,
    detector_backend: str = "opencv",
    align: bool = True,
    expand_percentage: int = 0,
    normalization: str = "base",
    anti_spoofing: bool = False,
    max_faces: Optional[int] = None,
    l2_normalize: bool = False,
    minmax_normalize: bool = False,
    return_face: bool = False,
    cryptosystem: Optional[LightPHE] = None,
) -> Union[List[Dict[str, Any]], List[List[Dict[str, Any]]]]:
    """
    Represent facial images as multi-dimensional vector embeddings.

    Args:
        img_path (str, np.ndarray, or Sequence[Union[str, np.ndarray]]):
            The exact path to the image, a numpy array in BGR format,
            a base64 encoded image, or a sequence of these.
            If the source image contains multiple faces,
            the result will include information for each detected face.

        model_name (str): Model for face recognition. Options: VGG-Face, Facenet, Facenet512,
            OpenFace, DeepFace, DeepID, Dlib, ArcFace, SFace and GhostFaceNet

        enforce_detection (boolean): If no face is detected in an image, raise an exception.
            Default is True. Set to False to avoid the exception for low-resolution images.

        detector_backend (string): face detector backend. Options: 'opencv', 'retinaface',
            'mtcnn', 'ssd', 'dlib', 'mediapipe', 'yolov8n', 'yolov8m', 'yolov8l', 'yolov11n',
            'yolov11s', 'yolov11m', 'yolov11l', 'yolov12n', 'yolov12s', 'yolov12m', 'yolov12l'
            'centerface' or 'skip'.

        align (boolean): Perform alignment based on the eye positions.


```

## deepface/deepface/modules/streaming.py
```
# built-in dependencies
import os
import time
from typing import List, Tuple, Optional, cast, Dict, Any
import traceback

# 3rd party dependencies
import numpy as np
from numpy.typing import NDArray
import pandas as pd
import cv2

# project dependencies
from deepface import DeepFace
from deepface.commons.logger import Logger

logger = Logger()

# dependency configuration
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"


IDENTIFIED_IMG_SIZE = 112
TEXT_COLOR = (255, 255, 255)


# pylint: disable=unused-variable, too-many-positional-arguments
def analysis(
    db_path: str,
    model_name: str = "VGG-Face",
    detector_backend: str = "opencv",
    distance_metric: str = "cosine",
    enable_face_analysis: bool = True,
    source: int = 0,
    time_threshold: int = 5,
    frame_threshold: int = 5,
    anti_spoofing: bool = False,
    output_path: Optional[str] = None,
    debug: bool = False,
) -> None:
    """
    Run real time face recognition and facial attribute analysis

    Args:
        db_path (string): Path to the folder containing image files. All detected faces
            in the database will be considered in the decision-making process.

        model_name (str): Model for face recognition. Options: VGG-Face, Facenet, Facenet512,
            OpenFace, DeepFace, DeepID, Dlib, ArcFace, SFace and GhostFaceNet (default is VGG-Face)

        detector_backend (string): face detector backend. Options: 'opencv', 'retinaface',
            'mtcnn', 'ssd', 'dlib', 'mediapipe', 'yolov8n', 'yolov8m', 'yolov8l', 'yolov11n',
            'yolov11s', 'yolov11m', 'yolov11l', 'yolov12n', 'yolov12s', 'yolov12m', 'yolov12l'
            'centerface' or 'skip' (default is opencv).

        distance_metric (string): Metric for measuring similarity. Options: 'cosine',
            'euclidean', 'euclidean_l2', 'angular' (default is cosine).

        enable_face_analysis (bool): Flag to enable face analysis (default is True).


```

## deepface/deepface/modules/verification.py
```
# built-in dependencies
import time
from typing import Any, Dict, Optional, Union, List, Tuple, IO, cast
import math

# 3rd party dependencies
import numpy as np
from numpy.typing import NDArray

# project dependencies
from deepface.modules import representation, detection, modeling
from deepface.models.FacialRecognition import FacialRecognition
from deepface.commons.logger import Logger
from deepface.config.confidence import confidences
from deepface.config.threshold import thresholds
from deepface.modules.exceptions import (
    SpoofDetected,
    DimensionMismatchError,
    DataTypeError,
    InvalidEmbeddingsShapeError,
)

logger = Logger()


# pylint: disable=too-many-positional-arguments, no-else-return
def verify(
    img1_path: Union[str, NDArray[Any], List[float], IO[bytes]],
    img2_path: Union[str, NDArray[Any], List[float], IO[bytes]],
    model_name: str = "VGG-Face",
    detector_backend: str = "opencv",
    distance_metric: str = "cosine",
    enforce_detection: bool = True,
    align: bool = True,
    expand_percentage: int = 0,
    normalization: str = "base",
    silent: bool = False,
    threshold: Optional[float] = None,
    anti_spoofing: bool = False,
) -> Dict[str, Any]:
    """
    Verify if an image pair represents the same person or different persons.

    The verification function converts facial images to vectors and calculates the similarity
    between those vectors. Vectors of images of the same person should exhibit higher similarity
    (or lower distance) than vectors of images of different persons.

    Args:
        img1_path (str or np.ndarray or List[float]): Path to the first image.
            Accepts exact image path as a string, numpy array (BGR), base64 encoded images
            or pre-calculated embeddings.

        img2_path (str or np.ndarray or  or List[float]): Path to the second image.
            Accepts exact image path as a string, numpy array (BGR), base64 encoded images
            or pre-calculated embeddings.

        model_name (str): Model for face recognition. Options: VGG-Face, Facenet, Facenet512,
            OpenFace, DeepFace, DeepID, Dlib, ArcFace, SFace and GhostFaceNet (default is VGG-Face).

        detector_backend (string): face detector backend. Options: 'opencv', 'retinaface',

```

## deepface/deepface/modules/modeling.py
```
from __future__ import annotations

# built-in dependencies
from typing import TYPE_CHECKING, Any, Final, TypedDict, Dict

# project dependencies
from deepface.models.facial_recognition import (
    VGGFace,
    OpenFace,
    FbDeepFace,
    DeepID,
    ArcFace,
    SFace,
    Dlib,
    Facenet,
    GhostFaceNet,
    Buffalo_L,
)
from deepface.models.face_detection import (
    FastMtCnn,
    MediaPipe,
    MtCnn,
    OpenCv,
    Dlib as DlibDetector,
    RetinaFace,
    Ssd,
    Yolo as YoloFaceDetector,
    YuNet,
    CenterFace,
)
from deepface.models.demography import Age, Gender, Race, Emotion
from deepface.models.spoofing import FasNet
from deepface.modules.exceptions import UnimplementedError

if TYPE_CHECKING:
    from deepface.models.Demography import Demography
    from deepface.models.Detector import Detector
    from deepface.models.FacialRecognition import FacialRecognition

    cached_models: Dict[str, Dict[str, Any]] = {}


class AvailableModels(TypedDict):
    facial_recognition: dict[str, type[FacialRecognition]]
    spoofing: dict[str, type[FasNet.Fasnet]]
    facial_attribute: dict[str, type[Demography]]
    face_detector: dict[str, type[Detector]]


AVAILABLE_MODELS: Final[AvailableModels] = {
    "facial_recognition": {
        "VGG-Face": VGGFace.VggFaceClient,
        "OpenFace": OpenFace.OpenFaceClient,
        "Facenet": Facenet.FaceNet128dClient,
        "Facenet512": Facenet.FaceNet512dClient,
        "DeepFace": FbDeepFace.DeepFaceClient,
        "DeepID": DeepID.DeepIdClient,
        "Dlib": Dlib.DlibClient,
        "ArcFace": ArcFace.ArcFaceClient,
        "SFace": SFace.SFaceClient,

```

## deepface/setup.py
```
import json
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().split("\n")

with open("package_info.json", "r", encoding="utf-8") as f:
    package_info = json.load(f)

setuptools.setup(
    name="deepface",
    version=package_info["version"],
    author="Sefik Ilkin Serengil",
    author_email="serengil@gmail.com",
    description=(
        "A Lightweight Face Recognition and Facial Attribute Analysis Framework"
        " (Age, Gender, Emotion, Race) for Python"
    ),
    data_files=[("", ["README.md", "requirements.txt", "package_info.json"])],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/serengil/deepface",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": ["deepface = deepface.DeepFace:cli"],
    },
    python_requires=">=3.7",
    license="MIT",
    install_requires=requirements,
)

```

## face_recognition/docs/conf.py
```
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# face_recognition documentation build configuration file, created by
# sphinx-quickstart on Tue Jul  9 22:26:36 2013.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

import sys
import os
from unittest.mock import MagicMock

class Mock(MagicMock):
    @classmethod
    def __getattr__(cls, name):
            return MagicMock()

MOCK_MODULES = ['face_recognition_models', 'Click', 'dlib', 'numpy', 'PIL']
sys.modules.update((mod_name, Mock()) for mod_name in MOCK_MODULES)

# If extensions (or modules to document with autodoc) are in another
# directory, add these directories to sys.path here. If the directory is
# relative to the documentation root, use os.path.abspath to make it

```

## face_recognition/face_recognition/api.py
```
# -*- coding: utf-8 -*-

import PIL.Image
import dlib
import numpy as np
from PIL import ImageFile

try:
    import face_recognition_models
except Exception:
    print("Please install `face_recognition_models` with this command before using `face_recognition`:\n")
    print("pip install git+https://github.com/ageitgey/face_recognition_models")
    quit()

ImageFile.LOAD_TRUNCATED_IMAGES = True

face_detector = dlib.get_frontal_face_detector()

predictor_68_point_model = face_recognition_models.pose_predictor_model_location()
pose_predictor_68_point = dlib.shape_predictor(predictor_68_point_model)

predictor_5_point_model = face_recognition_models.pose_predictor_five_point_model_location()
pose_predictor_5_point = dlib.shape_predictor(predictor_5_point_model)

cnn_face_detection_model = face_recognition_models.cnn_face_detector_model_location()
cnn_face_detector = dlib.cnn_face_detection_model_v1(cnn_face_detection_model)

face_recognition_model = face_recognition_models.face_recognition_model_location()
face_encoder = dlib.face_recognition_model_v1(face_recognition_model)


def _rect_to_css(rect):
    """
    Convert a dlib 'rect' object to a plain tuple in (top, right, bottom, left) order

    :param rect: a dlib 'rect' object
    :return: a plain tuple representation of the rect in (top, right, bottom, left) order
    """
    return rect.top(), rect.right(), rect.bottom(), rect.left()


def _css_to_rect(css):
    """
    Convert a tuple in (top, right, bottom, left) order to a dlib `rect` object

    :param css:  plain tuple representation of the rect in (top, right, bottom, left) order
    :return: a dlib `rect` object
    """
    return dlib.rectangle(css[3], css[0], css[1], css[2])


def _trim_css_to_bounds(css, image_shape):
    """
    Make sure a tuple in (top, right, bottom, left) order is within the bounds of the image.

    :param css:  plain tuple representation of the rect in (top, right, bottom, left) order
    :param image_shape: numpy shape of the image array
    :return: a trimmed plain tuple representation of the rect in (top, right, bottom, left) order
    """
    return max(css[0], 0), min(css[1], image_shape[1]), min(css[2], image_shape[0]), max(css[3], 0)


def face_distance(face_encodings, face_to_compare):
    """
    Given a list of face encodings, compare them to a known face encoding and get a euclidean distance
    for each comparison face. The distance tells you how similar the faces are.

    :param face_encodings: List of face encodings to compare
    :param face_to_compare: A face encoding to compare against
    :return: A numpy ndarray with the distance for each face in the same order as the 'faces' array
    """
    if len(face_encodings) == 0:
        return np.empty((0))

    return np.linalg.norm(face_encodings - face_to_compare, axis=1)


def load_image_file(file, mode='RGB'):
    """
    Loads an image file (.jpg, .png, etc) into a numpy array

```

## face_recognition/face_recognition/face_detection_cli.py
```
# -*- coding: utf-8 -*-
from __future__ import print_function
import click
import os
import re
import face_recognition.api as face_recognition
import multiprocessing
import sys
import itertools


def print_result(filename, location):
    top, right, bottom, left = location
    print("{},{},{},{},{}".format(filename, top, right, bottom, left))


def test_image(image_to_check, model, upsample):
    unknown_image = face_recognition.load_image_file(image_to_check)
    face_locations = face_recognition.face_locations(unknown_image, number_of_times_to_upsample=upsample, model=model)

    for face_location in face_locations:
        print_result(image_to_check, face_location)


def image_files_in_folder(folder):
    return [os.path.join(folder, f) for f in os.listdir(folder) if re.match(r'.*\.(jpg|jpeg|png)', f, flags=re.I)]


def process_images_in_process_pool(images_to_check, number_of_cpus, model, upsample):
    if number_of_cpus == -1:
        processes = None
    else:
        processes = number_of_cpus

    # macOS will crash due to a bug in libdispatch if you don't use 'forkserver'
    context = multiprocessing
    if "forkserver" in multiprocessing.get_all_start_methods():
        context = multiprocessing.get_context("forkserver")

    pool = context.Pool(processes=processes)

    function_parameters = zip(
        images_to_check,
        itertools.repeat(model),
        itertools.repeat(upsample),
    )

    pool.starmap(test_image, function_parameters)



```

