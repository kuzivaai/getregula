# Targeted Corpus — Human Labelling Workbench

**Total findings:** 39
**Distribution:** biometrics 33, credit_scoring 5, employment 1

**Instructions:** For each finding, set `label` to `tp` or `fp` in `candidates.json`. Add `notes`. See LABELLING_CRITERIA.md for full definitions.

**Key decision criteria for this corpus:**
- TP if the code **performs or enables** the described Annex III activity in its production context
- FP if the pattern matched syntactically but the file is **infrastructure/utility** that does not itself perform the regulated activity
- For deepface: the project IS a biometric identification library. Core modules (recognition, verification, representation, demography models) are clearly TP. Infrastructure (database adapters, weight downloaders, setup.py) are the borderline cases — apply the 'does this file perform or enable biometric identification' test.

---

## T-deepface-001

- **Repo:** deepface (https://github.com/serengil/deepface.git)
- **File:** `deepface/DeepFace.py`
- **Tier:** high_risk
- **Category:** Annex III, Category 1
- **Domain:** biometrics
- **Confidence:** 93
- **Description:** Biometric identification and categorisation

**Legal test:** Biometric identification and categorisation of natural persons. Legal test (Art 6(2) + Annex III §1): Does this AI system perform remote biometric identification, biometric categorisation based on sensitive attributes, or emotion recognition? Key distinction: the system must IDENTIFY or CATEGORISE natural persons using biometric data, not merely process images/audio for other purposes.

**Code context:**
```
   1 >> # common dependencies
   2    import os
   3    import warnings
   4    import logging
   5    from typing import Any, Dict, IO, List, Union, Optional, Sequence, Tuple, cast
   6    
   7    # this has to be set before importing tensorflow
   8    os.environ["TF_USE_LEGACY_KERAS"] = "1"
   9    
  10    # pylint: disable=wrong-import-position, too-many-positional-arguments
  11    
```

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## T-deepface-002

- **Repo:** deepface (https://github.com/serengil/deepface.git)
- **File:** `deepface/api/src/app.py`
- **Tier:** high_risk
- **Category:** Annex III, Category 1
- **Domain:** biometrics
- **Confidence:** 88
- **Description:** Biometric identification and categorisation

**Legal test:** Biometric identification and categorisation of natural persons. Legal test (Art 6(2) + Annex III §1): Does this AI system perform remote biometric identification, biometric categorisation based on sensitive attributes, or emotion recognition? Key distinction: the system must IDENTIFY or CATEGORISE natural persons using biometric data, not merely process images/audio for other purposes.

**Code context:**
```
   1 >> # 3rd parth dependencies
   2    from flask import Flask
   3    from flask_cors import CORS
   4    from dotenv import load_dotenv
   5    
   6    # load environment variables from .env first things first
   7    load_dotenv()
   8    
   9    
  10    # pylint: disable=wrong-import-position
  11    # project dependencies
```

**Workbench hint:** NOTE: This appears to be an API/application entry point.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## T-deepface-003

- **Repo:** deepface (https://github.com/serengil/deepface.git)
- **File:** `deepface/commons/weight_utils.py`
- **Tier:** high_risk
- **Category:** Annex III, Category 1
- **Domain:** biometrics
- **Confidence:** 88
- **Description:** Biometric identification and categorisation

**Legal test:** Biometric identification and categorisation of natural persons. Legal test (Art 6(2) + Annex III §1): Does this AI system perform remote biometric identification, biometric categorisation based on sensitive attributes, or emotion recognition? Key distinction: the system must IDENTIFY or CATEGORISE natural persons using biometric data, not merely process images/audio for other purposes.

**Code context:**
```
   1 >> # built-in dependencies
   2    import os
   3    from typing import Optional
   4    import zipfile
   5    import bz2
   6    
   7    # 3rd party dependencies
   8    import gdown
   9    
  10    # project dependencies
  11    from deepface.commons import folder_utils, package_utils
```

**Workbench hint:** NOTE: This appears to be infrastructure/utility code within the project.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## T-deepface-004

- **Repo:** deepface (https://github.com/serengil/deepface.git)
- **File:** `deepface/models/FacialRecognition.py`
- **Tier:** high_risk
- **Category:** Annex III, Category 1
- **Domain:** biometrics
- **Confidence:** 88
- **Description:** Biometric identification and categorisation

**Legal test:** Biometric identification and categorisation of natural persons. Legal test (Art 6(2) + Annex III §1): Does this AI system perform remote biometric identification, biometric categorisation based on sensitive attributes, or emotion recognition? Key distinction: the system must IDENTIFY or CATEGORISE natural persons using biometric data, not merely process images/audio for other purposes.

**Code context:**
```
   1 >> # standard library imports
   2    from abc import ABC
   3    from typing import Any, Union, List, Tuple, cast
   4    
   5    # third party imports
   6    import numpy as np
   7    from numpy.typing import NDArray
   8    
   9    # project imports
  10    from deepface.commons import package_utils
  11    from deepface.modules.exceptions import InvalidEmbeddingsShapeError
```

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## T-deepface-005

- **Repo:** deepface (https://github.com/serengil/deepface.git)
- **File:** `deepface/models/demography/Age.py`
- **Tier:** high_risk
- **Category:** Annex III, Category 1
- **Domain:** biometrics
- **Confidence:** 93
- **Description:** Biometric identification and categorisation

**Legal test:** Biometric identification and categorisation of natural persons. Legal test (Art 6(2) + Annex III §1): Does this AI system perform remote biometric identification, biometric categorisation based on sensitive attributes, or emotion recognition? Key distinction: the system must IDENTIFY or CATEGORISE natural persons using biometric data, not merely process images/audio for other purposes.

**Code context:**
```
   1 >> # stdlib dependencies
   2    from typing import List, Union, Any, cast
   3    
   4    # 3rd party dependencies
   5    import numpy as np
   6    from numpy.typing import NDArray
   7    
   8    # project dependencies
   9    from deepface.models.facial_recognition import VGGFace
  10    from deepface.commons import package_utils, weight_utils
  11    from deepface.models.Demography import Demography
```

**Workbench hint:** NOTE: This appears to be core functional code — likely performs the regulated activity directly.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## T-deepface-006

- **Repo:** deepface (https://github.com/serengil/deepface.git)
- **File:** `deepface/models/demography/Gender.py`
- **Tier:** high_risk
- **Category:** Annex III, Category 1
- **Domain:** biometrics
- **Confidence:** 88
- **Description:** Biometric identification and categorisation

**Legal test:** Biometric identification and categorisation of natural persons. Legal test (Art 6(2) + Annex III §1): Does this AI system perform remote biometric identification, biometric categorisation based on sensitive attributes, or emotion recognition? Key distinction: the system must IDENTIFY or CATEGORISE natural persons using biometric data, not merely process images/audio for other purposes.

**Code context:**
```
   1 >> # stdlib dependencies
   2    
   3    from typing import List, Union, Any
   4    
   5    # 3rd party dependencies
   6    from numpy.typing import NDArray
   7    
   8    # project dependencies
   9    from deepface.models.facial_recognition import VGGFace
  10    from deepface.commons import package_utils, weight_utils
  11    from deepface.models.Demography import Demography
```

**Workbench hint:** NOTE: This appears to be core functional code — likely performs the regulated activity directly.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## T-deepface-007

- **Repo:** deepface (https://github.com/serengil/deepface.git)
- **File:** `deepface/models/demography/Race.py`
- **Tier:** high_risk
- **Category:** Annex III, Category 1
- **Domain:** biometrics
- **Confidence:** 88
- **Description:** Biometric identification and categorisation

**Legal test:** Biometric identification and categorisation of natural persons. Legal test (Art 6(2) + Annex III §1): Does this AI system perform remote biometric identification, biometric categorisation based on sensitive attributes, or emotion recognition? Key distinction: the system must IDENTIFY or CATEGORISE natural persons using biometric data, not merely process images/audio for other purposes.

**Code context:**
```
   1 >> # stdlib dependencies
   2    from typing import List, Union, Any
   3    
   4    # 3rd party dependencies
   5    from numpy.typing import NDArray
   6    
   7    # project dependencies
   8    from deepface.models.facial_recognition import VGGFace
   9    from deepface.commons import package_utils, weight_utils
  10    from deepface.models.Demography import Demography
  11    from deepface.commons.logger import Logger
```

**Workbench hint:** NOTE: This appears to be core functional code — likely performs the regulated activity directly.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## T-deepface-008

- **Repo:** deepface (https://github.com/serengil/deepface.git)
- **File:** `deepface/models/facial_recognition/ArcFace.py`
- **Tier:** high_risk
- **Category:** Annex III, Category 1
- **Domain:** biometrics
- **Confidence:** 88
- **Description:** Biometric identification and categorisation

**Legal test:** Biometric identification and categorisation of natural persons. Legal test (Art 6(2) + Annex III §1): Does this AI system perform remote biometric identification, biometric categorisation based on sensitive attributes, or emotion recognition? Key distinction: the system must IDENTIFY or CATEGORISE natural persons using biometric data, not merely process images/audio for other purposes.

**Code context:**
```
   1 >> # built-in dependencies
   2    from typing import Any
   3    
   4    # project dependencies
   5    from deepface.commons import package_utils, weight_utils
   6    from deepface.models.FacialRecognition import FacialRecognition
   7    
   8    from deepface.commons.logger import Logger
   9    
  10    logger = Logger()
  11    
```

**Workbench hint:** NOTE: This appears to be core functional code — likely performs the regulated activity directly.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## T-deepface-009

- **Repo:** deepface (https://github.com/serengil/deepface.git)
- **File:** `deepface/models/facial_recognition/Buffalo_L.py`
- **Tier:** high_risk
- **Category:** Annex III, Category 1
- **Domain:** biometrics
- **Confidence:** 88
- **Description:** Biometric identification and categorisation

**Legal test:** Biometric identification and categorisation of natural persons. Legal test (Art 6(2) + Annex III §1): Does this AI system perform remote biometric identification, biometric categorisation based on sensitive attributes, or emotion recognition? Key distinction: the system must IDENTIFY or CATEGORISE natural persons using biometric data, not merely process images/audio for other purposes.

**Code context:**
```
   1 >> # built-in dependencies
   2    import os
   3    from typing import List, Union, Any
   4    
   5    # third-party dependencies
   6    import numpy as np
   7    from numpy.typing import NDArray
   8    
   9    # project dependencies
  10    from deepface.commons import weight_utils, folder_utils
  11    from deepface.commons.logger import Logger
```

**Workbench hint:** NOTE: This appears to be core functional code — likely performs the regulated activity directly.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## T-deepface-010

- **Repo:** deepface (https://github.com/serengil/deepface.git)
- **File:** `deepface/models/facial_recognition/DeepID.py`
- **Tier:** high_risk
- **Category:** Annex III, Category 1
- **Domain:** biometrics
- **Confidence:** 88
- **Description:** Biometric identification and categorisation

**Legal test:** Biometric identification and categorisation of natural persons. Legal test (Art 6(2) + Annex III §1): Does this AI system perform remote biometric identification, biometric categorisation based on sensitive attributes, or emotion recognition? Key distinction: the system must IDENTIFY or CATEGORISE natural persons using biometric data, not merely process images/audio for other purposes.

**Code context:**
```
   1 >> # project dependencies
   2    from deepface.commons import package_utils, weight_utils
   3    from deepface.models.FacialRecognition import FacialRecognition
   4    from deepface.commons.logger import Logger
   5    
   6    logger = Logger()
   7    
   8    tf_version = package_utils.get_tf_major_version()
   9    
  10    if tf_version == 1:
  11        from keras.models import Model
```

**Workbench hint:** NOTE: This appears to be core functional code — likely performs the regulated activity directly.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## T-deepface-011

- **Repo:** deepface (https://github.com/serengil/deepface.git)
- **File:** `deepface/models/facial_recognition/Dlib.py`
- **Tier:** high_risk
- **Category:** Annex III, Category 1
- **Domain:** biometrics
- **Confidence:** 88
- **Description:** Biometric identification and categorisation

**Legal test:** Biometric identification and categorisation of natural persons. Legal test (Art 6(2) + Annex III §1): Does this AI system perform remote biometric identification, biometric categorisation based on sensitive attributes, or emotion recognition? Key distinction: the system must IDENTIFY or CATEGORISE natural persons using biometric data, not merely process images/audio for other purposes.

**Code context:**
```
   1 >> # built-in dependencies
   2    from typing import List, Union, Any, cast
   3    
   4    # 3rd party dependencies
   5    import numpy as np
   6    from numpy.typing import NDArray
   7    
   8    # project dependencies
   9    from deepface.commons import weight_utils
  10    from deepface.models.FacialRecognition import FacialRecognition
  11    from deepface.commons.logger import Logger
```

**Workbench hint:** NOTE: This appears to be core functional code — likely performs the regulated activity directly.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## T-deepface-012

- **Repo:** deepface (https://github.com/serengil/deepface.git)
- **File:** `deepface/models/facial_recognition/Facenet.py`
- **Tier:** high_risk
- **Category:** Annex III, Category 1
- **Domain:** biometrics
- **Confidence:** 88
- **Description:** Biometric identification and categorisation

**Legal test:** Biometric identification and categorisation of natural persons. Legal test (Art 6(2) + Annex III §1): Does this AI system perform remote biometric identification, biometric categorisation based on sensitive attributes, or emotion recognition? Key distinction: the system must IDENTIFY or CATEGORISE natural persons using biometric data, not merely process images/audio for other purposes.

**Code context:**
```
   1 >> # built-in dependencies
   2    from typing import Any
   3    
   4    # 3rd party dependencies
   5    from numpy.typing import NDArray
   6    
   7    # project dependencies
   8    from deepface.commons import package_utils, weight_utils
   9    from deepface.models.FacialRecognition import FacialRecognition
  10    from deepface.commons.logger import Logger
  11    
```

**Workbench hint:** NOTE: This appears to be core functional code — likely performs the regulated activity directly.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## T-deepface-013

- **Repo:** deepface (https://github.com/serengil/deepface.git)
- **File:** `deepface/models/facial_recognition/FbDeepFace.py`
- **Tier:** high_risk
- **Category:** Annex III, Category 1
- **Domain:** biometrics
- **Confidence:** 88
- **Description:** Biometric identification and categorisation

**Legal test:** Biometric identification and categorisation of natural persons. Legal test (Art 6(2) + Annex III §1): Does this AI system perform remote biometric identification, biometric categorisation based on sensitive attributes, or emotion recognition? Key distinction: the system must IDENTIFY or CATEGORISE natural persons using biometric data, not merely process images/audio for other purposes.

**Code context:**
```
   1 >> # project dependencies
   2    from deepface.commons import package_utils, weight_utils
   3    from deepface.models.FacialRecognition import FacialRecognition
   4    from deepface.commons.logger import Logger
   5    
   6    logger = Logger()
   7    
   8    # --------------------------------
   9    # dependency configuration
  10    
  11    tf_major = package_utils.get_tf_major_version()
```

**Workbench hint:** NOTE: This appears to be core functional code — likely performs the regulated activity directly.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## T-deepface-014

- **Repo:** deepface (https://github.com/serengil/deepface.git)
- **File:** `deepface/models/facial_recognition/GhostFaceNet.py`
- **Tier:** high_risk
- **Category:** Annex III, Category 1
- **Domain:** biometrics
- **Confidence:** 88
- **Description:** Biometric identification and categorisation

**Legal test:** Biometric identification and categorisation of natural persons. Legal test (Art 6(2) + Annex III §1): Does this AI system perform remote biometric identification, biometric categorisation based on sensitive attributes, or emotion recognition? Key distinction: the system must IDENTIFY or CATEGORISE natural persons using biometric data, not merely process images/audio for other purposes.

**Code context:**
```
   1 >> # built-in dependencies
   2    from typing import Any
   3    
   4    # 3rd party dependencies
   5    import tensorflow as tf
   6    
   7    # project dependencies
   8    from deepface.commons import package_utils, weight_utils
   9    from deepface.models.FacialRecognition import FacialRecognition
  10    from deepface.commons.logger import Logger
  11    
```

**Workbench hint:** NOTE: This appears to be core functional code — likely performs the regulated activity directly.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## T-deepface-015

- **Repo:** deepface (https://github.com/serengil/deepface.git)
- **File:** `deepface/models/facial_recognition/OpenFace.py`
- **Tier:** high_risk
- **Category:** Annex III, Category 1
- **Domain:** biometrics
- **Confidence:** 88
- **Description:** Biometric identification and categorisation

**Legal test:** Biometric identification and categorisation of natural persons. Legal test (Art 6(2) + Annex III §1): Does this AI system perform remote biometric identification, biometric categorisation based on sensitive attributes, or emotion recognition? Key distinction: the system must IDENTIFY or CATEGORISE natural persons using biometric data, not merely process images/audio for other purposes.

**Code context:**
```
   1 >> # 3rd party dependencies
   2    import tensorflow as tf
   3    
   4    # project dependencies
   5    from deepface.commons import package_utils, weight_utils
   6    from deepface.models.FacialRecognition import FacialRecognition
   7    from deepface.commons.logger import Logger
   8    
   9    logger = Logger()
  10    
  11    tf_version = package_utils.get_tf_major_version()
```

**Workbench hint:** NOTE: This appears to be core functional code — likely performs the regulated activity directly.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## T-deepface-016

- **Repo:** deepface (https://github.com/serengil/deepface.git)
- **File:** `deepface/models/facial_recognition/SFace.py`
- **Tier:** high_risk
- **Category:** Annex III, Category 1
- **Domain:** biometrics
- **Confidence:** 88
- **Description:** Biometric identification and categorisation

**Legal test:** Biometric identification and categorisation of natural persons. Legal test (Art 6(2) + Annex III §1): Does this AI system perform remote biometric identification, biometric categorisation based on sensitive attributes, or emotion recognition? Key distinction: the system must IDENTIFY or CATEGORISE natural persons using biometric data, not merely process images/audio for other purposes.

**Code context:**
```
   1 >> # built-in dependencies
   2    from typing import Any, List, Union, cast
   3    
   4    # 3rd party dependencies
   5    import numpy as np
   6    from numpy.typing import NDArray
   7    import cv2 as cv
   8    
   9    # project dependencies
  10    from deepface.commons import weight_utils
  11    from deepface.models.FacialRecognition import FacialRecognition
```

**Workbench hint:** NOTE: This appears to be core functional code — likely performs the regulated activity directly.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## T-deepface-017

- **Repo:** deepface (https://github.com/serengil/deepface.git)
- **File:** `deepface/models/facial_recognition/VGGFace.py`
- **Tier:** high_risk
- **Category:** Annex III, Category 1
- **Domain:** biometrics
- **Confidence:** 88
- **Description:** Biometric identification and categorisation

**Legal test:** Biometric identification and categorisation of natural persons. Legal test (Art 6(2) + Annex III §1): Does this AI system perform remote biometric identification, biometric categorisation based on sensitive attributes, or emotion recognition? Key distinction: the system must IDENTIFY or CATEGORISE natural persons using biometric data, not merely process images/audio for other purposes.

**Code context:**
```
   1 >> # built-in dependencies
   2    from typing import List, cast, Any
   3    
   4    # 3rd party dependencies
   5    from numpy.typing import NDArray
   6    
   7    # project dependencies
   8    from deepface.commons import package_utils, weight_utils
   9    from deepface.modules import verification
  10    from deepface.models.FacialRecognition import FacialRecognition
  11    from deepface.commons.logger import Logger
```

**Workbench hint:** NOTE: This appears to be core functional code — likely performs the regulated activity directly.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## T-deepface-018

- **Repo:** deepface (https://github.com/serengil/deepface.git)
- **File:** `deepface/modules/database/milvus.py`
- **Tier:** high_risk
- **Category:** Annex III, Category 1
- **Domain:** biometrics
- **Confidence:** 88
- **Description:** Biometric identification and categorisation

**Legal test:** Biometric identification and categorisation of natural persons. Legal test (Art 6(2) + Annex III §1): Does this AI system perform remote biometric identification, biometric categorisation based on sensitive attributes, or emotion recognition? Key distinction: the system must IDENTIFY or CATEGORISE natural persons using biometric data, not merely process images/audio for other purposes.

**Code context:**
```
   1 >> # built-in dependencies
   2    import os
   3    import json
   4    import hashlib
   5    import struct
   6    from typing import Any, Dict, Optional, List, Union
   7    
   8    # project dependencies
   9    from deepface.modules.database.types import Database
  10    from deepface.modules.modeling import build_model
  11    from deepface.commons.logger import Logger
```

**Workbench hint:** NOTE: This appears to be infrastructure/utility code within the project.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## T-deepface-019

- **Repo:** deepface (https://github.com/serengil/deepface.git)
- **File:** `deepface/modules/database/neo4j.py`
- **Tier:** high_risk
- **Category:** Annex III, Category 1
- **Domain:** biometrics
- **Confidence:** 88
- **Description:** Biometric identification and categorisation

**Legal test:** Biometric identification and categorisation of natural persons. Legal test (Art 6(2) + Annex III §1): Does this AI system perform remote biometric identification, biometric categorisation based on sensitive attributes, or emotion recognition? Key distinction: the system must IDENTIFY or CATEGORISE natural persons using biometric data, not merely process images/audio for other purposes.

**Code context:**
```
   1 >> # built-in dependencies
   2    import os
   3    import json
   4    import hashlib
   5    import struct
   6    from typing import Any, Dict, Optional, List, Union
   7    from urllib.parse import urlparse
   8    
   9    
  10    # project dependencies
  11    from deepface.modules.database.types import Database
```

**Workbench hint:** NOTE: This appears to be infrastructure/utility code within the project.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## T-deepface-020

- **Repo:** deepface (https://github.com/serengil/deepface.git)
- **File:** `deepface/modules/database/pgvector.py`
- **Tier:** high_risk
- **Category:** Annex III, Category 1
- **Domain:** biometrics
- **Confidence:** 88
- **Description:** Biometric identification and categorisation

**Legal test:** Biometric identification and categorisation of natural persons. Legal test (Art 6(2) + Annex III §1): Does this AI system perform remote biometric identification, biometric categorisation based on sensitive attributes, or emotion recognition? Key distinction: the system must IDENTIFY or CATEGORISE natural persons using biometric data, not merely process images/audio for other purposes.

**Code context:**
```
   1 >> # built-in dependencies
   2    import os
   3    import json
   4    import struct
   5    import hashlib
   6    from typing import Any, Dict, Optional, List, Union
   7    
   8    # 3rd party dependencies
   9    import numpy as np
  10    
  11    # project dependencies
```

**Workbench hint:** NOTE: This appears to be infrastructure/utility code within the project.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## T-deepface-021

- **Repo:** deepface (https://github.com/serengil/deepface.git)
- **File:** `deepface/modules/database/pinecone.py`
- **Tier:** high_risk
- **Category:** Annex III, Category 1
- **Domain:** biometrics
- **Confidence:** 88
- **Description:** Biometric identification and categorisation

**Legal test:** Biometric identification and categorisation of natural persons. Legal test (Art 6(2) + Annex III §1): Does this AI system perform remote biometric identification, biometric categorisation based on sensitive attributes, or emotion recognition? Key distinction: the system must IDENTIFY or CATEGORISE natural persons using biometric data, not merely process images/audio for other purposes.

**Code context:**
```
   1 >> # built-in dependencies
   2    import os
   3    import json
   4    import hashlib
   5    import struct
   6    import math
   7    from typing import Any, Dict, Optional, List, Union
   8    
   9    # project dependencies
  10    from deepface.modules.database.types import Database
  11    from deepface.modules.modeling import build_model
```

**Workbench hint:** NOTE: This appears to be infrastructure/utility code within the project.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## T-deepface-022

- **Repo:** deepface (https://github.com/serengil/deepface.git)
- **File:** `deepface/modules/database/weaviate.py`
- **Tier:** high_risk
- **Category:** Annex III, Category 1
- **Domain:** biometrics
- **Confidence:** 73
- **Description:** Biometric identification and categorisation

**Legal test:** Biometric identification and categorisation of natural persons. Legal test (Art 6(2) + Annex III §1): Does this AI system perform remote biometric identification, biometric categorisation based on sensitive attributes, or emotion recognition? Key distinction: the system must IDENTIFY or CATEGORISE natural persons using biometric data, not merely process images/audio for other purposes.

**Code context:**
```
   1 >> # built-in dependencies
   2    import os
   3    import json
   4    import hashlib
   5    import struct
   6    import base64
   7    import uuid
   8    import math
   9    from typing import Any, Dict, Optional, List, Union
  10    
  11    # project dependencies
```

**Workbench hint:** NOTE: This appears to be infrastructure/utility code within the project.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## T-deepface-023

- **Repo:** deepface (https://github.com/serengil/deepface.git)
- **File:** `deepface/modules/datastore.py`
- **Tier:** high_risk
- **Category:** Annex III, Category 1
- **Domain:** biometrics
- **Confidence:** 93
- **Description:** Biometric identification and categorisation

**Legal test:** Biometric identification and categorisation of natural persons. Legal test (Art 6(2) + Annex III §1): Does this AI system perform remote biometric identification, biometric categorisation based on sensitive attributes, or emotion recognition? Key distinction: the system must IDENTIFY or CATEGORISE natural persons using biometric data, not merely process images/audio for other purposes.

**Code context:**
```
   1 >> # built-in dependencies
   2    import os
   3    from typing import Any, Dict, IO, List, Union, Optional, cast
   4    import uuid
   5    import time
   6    import math
   7    import tempfile
   8    
   9    # 3rd party dependencies
  10    import pandas as pd
  11    import numpy as np
```

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## T-deepface-024

- **Repo:** deepface (https://github.com/serengil/deepface.git)
- **File:** `deepface/modules/modeling.py`
- **Tier:** high_risk
- **Category:** Annex III, Category 1
- **Domain:** biometrics
- **Confidence:** 88
- **Description:** Biometric identification and categorisation

**Legal test:** Biometric identification and categorisation of natural persons. Legal test (Art 6(2) + Annex III §1): Does this AI system perform remote biometric identification, biometric categorisation based on sensitive attributes, or emotion recognition? Key distinction: the system must IDENTIFY or CATEGORISE natural persons using biometric data, not merely process images/audio for other purposes.

**Code context:**
```
   1 >> from __future__ import annotations
   2    
   3    # built-in dependencies
   4    from typing import TYPE_CHECKING, Any, Final, TypedDict, Dict
   5    
   6    # project dependencies
   7    from deepface.models.facial_recognition import (
   8        VGGFace,
   9        OpenFace,
  10        FbDeepFace,
  11        DeepID,
```

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## T-deepface-025

- **Repo:** deepface (https://github.com/serengil/deepface.git)
- **File:** `deepface/modules/recognition.py`
- **Tier:** high_risk
- **Category:** Annex III, Category 1
- **Domain:** biometrics
- **Confidence:** 93
- **Description:** Biometric identification and categorisation

**Legal test:** Biometric identification and categorisation of natural persons. Legal test (Art 6(2) + Annex III §1): Does this AI system perform remote biometric identification, biometric categorisation based on sensitive attributes, or emotion recognition? Key distinction: the system must IDENTIFY or CATEGORISE natural persons using biometric data, not merely process images/audio for other purposes.

**Code context:**
```
   1 >> # built-in dependencies
   2    import os
   3    import pickle
   4    from typing import List, Union, Optional, Dict, Any, Set, IO, cast, Tuple
   5    import time
   6    import ast
   7    
   8    # 3rd party dependencies
   9    import numpy as np
  10    from numpy.typing import NDArray
  11    import pandas as pd
```

**Workbench hint:** NOTE: This appears to be core functional code — likely performs the regulated activity directly.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## T-deepface-026

- **Repo:** deepface (https://github.com/serengil/deepface.git)
- **File:** `deepface/modules/representation.py`
- **Tier:** high_risk
- **Category:** Annex III, Category 1
- **Domain:** biometrics
- **Confidence:** 88
- **Description:** Biometric identification and categorisation

**Legal test:** Biometric identification and categorisation of natural persons. Legal test (Art 6(2) + Annex III §1): Does this AI system perform remote biometric identification, biometric categorisation based on sensitive attributes, or emotion recognition? Key distinction: the system must IDENTIFY or CATEGORISE natural persons using biometric data, not merely process images/audio for other purposes.

**Code context:**
```
   1 >> # built-in dependencies
   2    from typing import Any, Dict, List, Union, Optional, Sequence, IO, cast
   3    from collections import defaultdict
   4    
   5    # 3rd party dependencies
   6    import numpy as np
   7    from numpy.typing import NDArray
   8    from lightphe import LightPHE
   9    
  10    # project dependencies
  11    from deepface.commons import image_utils
```

**Workbench hint:** NOTE: This appears to be core functional code — likely performs the regulated activity directly.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## T-deepface-027

- **Repo:** deepface (https://github.com/serengil/deepface.git)
- **File:** `deepface/modules/streaming.py`
- **Tier:** high_risk
- **Category:** Annex III, Category 1
- **Domain:** biometrics
- **Confidence:** 93
- **Description:** Biometric identification and categorisation

**Legal test:** Biometric identification and categorisation of natural persons. Legal test (Art 6(2) + Annex III §1): Does this AI system perform remote biometric identification, biometric categorisation based on sensitive attributes, or emotion recognition? Key distinction: the system must IDENTIFY or CATEGORISE natural persons using biometric data, not merely process images/audio for other purposes.

**Code context:**
```
   1 >> # built-in dependencies
   2    import os
   3    import time
   4    from typing import List, Tuple, Optional, cast, Dict, Any
   5    import traceback
   6    
   7    # 3rd party dependencies
   8    import numpy as np
   9    from numpy.typing import NDArray
  10    import pandas as pd
  11    import cv2
```

**Workbench hint:** NOTE: This appears to be core functional code — likely performs the regulated activity directly.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## T-deepface-028

- **Repo:** deepface (https://github.com/serengil/deepface.git)
- **File:** `deepface/modules/verification.py`
- **Tier:** high_risk
- **Category:** Annex III, Category 1
- **Domain:** biometrics
- **Confidence:** 93
- **Description:** Biometric identification and categorisation

**Legal test:** Biometric identification and categorisation of natural persons. Legal test (Art 6(2) + Annex III §1): Does this AI system perform remote biometric identification, biometric categorisation based on sensitive attributes, or emotion recognition? Key distinction: the system must IDENTIFY or CATEGORISE natural persons using biometric data, not merely process images/audio for other purposes.

**Code context:**
```
   1 >> # built-in dependencies
   2    import time
   3    from typing import Any, Dict, Optional, Union, List, Tuple, IO, cast
   4    import math
   5    
   6    # 3rd party dependencies
   7    import numpy as np
   8    from numpy.typing import NDArray
   9    
  10    # project dependencies
  11    from deepface.modules import representation, detection, modeling
```

**Workbench hint:** NOTE: This appears to be core functional code — likely performs the regulated activity directly.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## T-deepface-029

- **Repo:** deepface (https://github.com/serengil/deepface.git)
- **File:** `setup.py`
- **Tier:** high_risk
- **Category:** Annex III, Category 1
- **Domain:** biometrics
- **Confidence:** 88
- **Description:** Biometric identification and categorisation

**Legal test:** Biometric identification and categorisation of natural persons. Legal test (Art 6(2) + Annex III §1): Does this AI system perform remote biometric identification, biometric categorisation based on sensitive attributes, or emotion recognition? Key distinction: the system must IDENTIFY or CATEGORISE natural persons using biometric data, not merely process images/audio for other purposes.

**Code context:**
```
   1 >> import json
   2    import setuptools
   3    
   4    with open("README.md", "r", encoding="utf-8") as fh:
   5        long_description = fh.read()
   6    
   7    with open("requirements.txt", "r", encoding="utf-8") as f:
   8        requirements = f.read().split("
")
   9    
  10    with open("package_info.json", "r", encoding="utf-8") as f:
  11        package_info = json.load(f)
```

**Workbench hint:** ATTENTION: This is a packaging/setup file, not application code.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## T-face_recognition-001

- **Repo:** face_recognition (https://github.com/ageitgey/face_recognition.git)
- **File:** `docs/conf.py`
- **Tier:** high_risk
- **Category:** Annex III, Category 1
- **Domain:** biometrics
- **Confidence:** 63
- **Description:** Biometric identification and categorisation

**Legal test:** Biometric identification and categorisation of natural persons. Legal test (Art 6(2) + Annex III §1): Does this AI system perform remote biometric identification, biometric categorisation based on sensitive attributes, or emotion recognition? Key distinction: the system must IDENTIFY or CATEGORISE natural persons using biometric data, not merely process images/audio for other purposes.

**Code context:**
```
   1 >> #!/usr/bin/env python
   2    # -*- coding: utf-8 -*-
   3    #
   4    # face_recognition documentation build configuration file, created by
   5    # sphinx-quickstart on Tue Jul  9 22:26:36 2013.
   6    #
   7    # This file is execfile()d with the current directory set to its
   8    # containing dir.
   9    #
  10    # Note that not all possible configuration values are present in this
  11    # autogenerated file.
```

**Workbench hint:** ATTENTION: This is a Sphinx documentation config, not application code.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## T-face_recognition-002

- **Repo:** face_recognition (https://github.com/ageitgey/face_recognition.git)
- **File:** `face_recognition/api.py`
- **Tier:** high_risk
- **Category:** Annex III, Category 1
- **Domain:** biometrics
- **Confidence:** 88
- **Description:** Biometric identification and categorisation

**Legal test:** Biometric identification and categorisation of natural persons. Legal test (Art 6(2) + Annex III §1): Does this AI system perform remote biometric identification, biometric categorisation based on sensitive attributes, or emotion recognition? Key distinction: the system must IDENTIFY or CATEGORISE natural persons using biometric data, not merely process images/audio for other purposes.

**Code context:**
```
   1 >> # -*- coding: utf-8 -*-
   2    
   3    import PIL.Image
   4    import dlib
   5    import numpy as np
   6    from PIL import ImageFile
   7    
   8    try:
   9        import face_recognition_models
  10    except Exception:
  11        print("Please install `face_recognition_models` with this command before using `face_recognition`:
")
```

**Workbench hint:** NOTE: This appears to be core functional code — likely performs the regulated activity directly.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## T-face_recognition-003

- **Repo:** face_recognition (https://github.com/ageitgey/face_recognition.git)
- **File:** `face_recognition/face_detection_cli.py`
- **Tier:** high_risk
- **Category:** Annex III, Category 1
- **Domain:** biometrics
- **Confidence:** 88
- **Description:** Biometric identification and categorisation

**Legal test:** Biometric identification and categorisation of natural persons. Legal test (Art 6(2) + Annex III §1): Does this AI system perform remote biometric identification, biometric categorisation based on sensitive attributes, or emotion recognition? Key distinction: the system must IDENTIFY or CATEGORISE natural persons using biometric data, not merely process images/audio for other purposes.

**Code context:**
```
   1 >> # -*- coding: utf-8 -*-
   2    from __future__ import print_function
   3    import click
   4    import os
   5    import re
   6    import face_recognition.api as face_recognition
   7    import multiprocessing
   8    import sys
   9    import itertools
  10    
  11    
```

**Workbench hint:** NOTE: This appears to be core functional code — likely performs the regulated activity directly.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## T-AI-Resume-Analyzer-001

- **Repo:** AI-Resume-Analyzer (https://github.com/deepakpadhi986/AI-Resume-Analyzer.git)
- **File:** `App/App.py`
- **Tier:** high_risk
- **Category:** Annex III, Category 4
- **Domain:** employment
- **Confidence:** 88
- **Description:** Employment and workers management

**Legal test:** Employment, workers management, and access to self-employment. Legal test (Annex III §4): Is this AI system used for recruitment, selection, placing job advertisements, screening/filtering applications, evaluating candidates, making decisions affecting employment relationships, or task allocation/monitoring of workers?

**Code context:**
```
   1 >> # Developed by dnoobnerd [https://dnoobnerd.netlify.app]    Made with Streamlit
   2    
   3    
   4    ###### Packages Used ######
   5    import streamlit as st # core package used in this project
   6    import pandas as pd
   7    import base64, random
   8    import time,datetime
   9    import pymysql
  10    import os
  11    import socket
```

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## T-Lending-Club-Credit-Scoring-001

- **Repo:** Lending-Club-Credit-Scoring (https://github.com/allmeidaapedro/Lending-Club-Credit-Scoring.git)
- **File:** `notebooks/3_pd_modeling.ipynb`
- **Tier:** high_risk
- **Category:** Annex III, Category 5
- **Domain:** credit_scoring
- **Confidence:** 95
- **Description:** Access to essential services

**Legal test:** Access to and enjoyment of essential private services and essential public services and benefits. Legal test (Annex III §5): Is this AI system used to evaluate creditworthiness, establish credit scores, or assess eligibility for essential services (insurance, public benefits, emergency services)?

**Code context:**
```
   1 >> {
   2     "cells": [
   3      {
   4       "cell_type": "markdown",
   5       "metadata": {},
   6       "source": [
   7        "## Lending Club Credit Risk Modeling
",
   8        "- In this project, I will build three **machine learning** models to predict the three components of expected loss in the context of **credit risk modeling** at the **Lending Club** (a peer-to-peer credit company): **Probability of Default (PD), Exposure at Default (EAD) and Loss Given Default (LGD)**. The expected loss will be the product of these elements: **Expected Loss (EL) = PD * EAD * LGD**. These models will be used to stablish a credit policy, deciding wheter to grant a loan or not for new applicants (application model) based on their credit scores and expected losses on loans. By estimating the Expected Loss (EL) from each loan, the Lending Club can also assess the required capital to hold to protect itself against defaults.
",
   9        "- The PD modelling encompasses an imbalanced binary classification problem with target being 1 in case of non-default and 0 in case of default (minority class). A Logistic Regression model will be built. 
",
  10        "- The LGD and EAD modelling encompasses a beta regression problem, that is, a regression task in which the dependent variables are beta distributed, the recovery rate and credit conversion factor, respectively.
",
  11        "- The **solution pipeline** is based on the **crisp-dm** framework:
",
```

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## T-Lending-Club-Credit-Scoring-002

- **Repo:** Lending-Club-Credit-Scoring (https://github.com/allmeidaapedro/Lending-Club-Credit-Scoring.git)
- **File:** `notebooks/4_lgd_ead_modeling.ipynb`
- **Tier:** high_risk
- **Category:** Annex III, Category 5
- **Domain:** credit_scoring
- **Confidence:** 88
- **Description:** Access to essential services

**Legal test:** Access to and enjoyment of essential private services and essential public services and benefits. Legal test (Annex III §5): Is this AI system used to evaluate creditworthiness, establish credit scores, or assess eligibility for essential services (insurance, public benefits, emergency services)?

**Code context:**
```
   1 >> {
   2     "cells": [
   3      {
   4       "cell_type": "markdown",
   5       "metadata": {},
   6       "source": [
   7        "## Lending Club Credit Risk Modeling
",
   8        "- In this project, I will build three **machine learning** models to predict the three components of expected loss in the context of **credit risk modeling** at the **Lending Club** (a peer-to-peer credit company): **Probability of Default (PD), Exposure at Default (EAD) and Loss Given Default (LGD)**. The expected loss will be the product of these elements: **Expected Loss (EL) = PD * EAD * LGD**. These models will be used to stablish a credit policy, deciding wheter to grant a loan or not for new applicants (application model) based on their credit scores and expected losses on loans. By estimating the Expected Loss (EL) from each loan, the Lending Club can also assess the required capital to hold to protect itself against defaults.
",
   9        "- The PD modelling encompasses an imbalanced binary classification problem with target being 1 in case of non-default and 0 in case of default (minority class). A Logistic Regression model will be built. 
",
  10        "- The LGD and EAD modelling encompasses a beta regression problem, that is, a regression task in which the dependent variables are beta distributed, the recovery rate and credit conversion factor, respectively.
",
  11        "- The **solution pipeline** is based on the **crisp-dm** framework:
",
```

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## T-Lending-Club-Credit-Scoring-003

- **Repo:** Lending-Club-Credit-Scoring (https://github.com/allmeidaapedro/Lending-Club-Credit-Scoring.git)
- **File:** `notebooks/5_pd_model_monitoring.ipynb`
- **Tier:** high_risk
- **Category:** Annex III, Category 5
- **Domain:** credit_scoring
- **Confidence:** 95
- **Description:** Access to essential services

**Legal test:** Access to and enjoyment of essential private services and essential public services and benefits. Legal test (Annex III §5): Is this AI system used to evaluate creditworthiness, establish credit scores, or assess eligibility for essential services (insurance, public benefits, emergency services)?

**Code context:**
```
   1 >> {
   2     "cells": [
   3      {
   4       "cell_type": "markdown",
   5       "metadata": {},
   6       "source": [
   7        "#### PD Model Monitoring
",
   8        "- A year has passed since I built the Probability of Default (PD), Loss Given Default (LGD) and Exposure at Default (EAD) models, estimated the Expected Loss (EL) of the loans and designed the credit policy. Thus, it is necessary to apply model monitoring.
",
   9        "
",
  10        "- **PD Model Monitoring:**
",
  11        "    - Imagine a year has passed since we built our PD model. Although it is very unlikely, the people applying for loans now might be very different from those we used to train our PD model. We need to reassess if our PD model is working well.
",
```

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## T-Lending-Club-Credit-Scoring-004

- **Repo:** Lending-Club-Credit-Scoring (https://github.com/allmeidaapedro/Lending-Club-Credit-Scoring.git)
- **File:** `setup.py`
- **Tier:** high_risk
- **Category:** Annex III, Category 5
- **Domain:** credit_scoring
- **Confidence:** 95
- **Description:** Access to essential services

**Legal test:** Access to and enjoyment of essential private services and essential public services and benefits. Legal test (Annex III §5): Is this AI system used to evaluate creditworthiness, establish credit scores, or assess eligibility for essential services (insurance, public benefits, emergency services)?

**Code context:**
```
   1 >> '''
   2    This script aims to build my entire project as a package.
   3    '''
   4    
   5    from setuptools import find_packages, setup
   6    from typing import List
   7    
   8    
   9    HYPHEN_E_DOT = '-e .'
  10    def get_requirements(file_path:str)->List[str]:
  11        '''
```

**Workbench hint:** ATTENTION: This is a packaging/setup file, not application code.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## T-Lending-Club-Credit-Scoring-005

- **Repo:** Lending-Club-Credit-Scoring (https://github.com/allmeidaapedro/Lending-Club-Credit-Scoring.git)
- **File:** `src/modelling_utils.py`
- **Tier:** high_risk
- **Category:** Annex III, Category 5
- **Domain:** credit_scoring
- **Confidence:** 100
- **Description:** Access to essential services

**Legal test:** Access to and enjoyment of essential private services and essential public services and benefits. Legal test (Annex III §5): Is this AI system used to evaluate creditworthiness, establish credit scores, or assess eligibility for essential services (insurance, public benefits, emergency services)?

**Code context:**
```
   1 >> 
   2    '''
   3    This script aims to provide functions that will turn the modelling process easier
   4    '''
   5    
   6    '''
   7    Importing libraries
   8    '''
   9    
  10    # Data manipulation and visualization.
  11    import pandas as pd
```

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## T-Face-Biometry-001

- **Repo:** Face-Biometry (https://github.com/prathameshparit/Face-Biometry.git)
- **File:** `app.py`
- **Tier:** high_risk
- **Category:** Annex III, Category 1
- **Domain:** biometrics
- **Confidence:** 88
- **Description:** Biometric identification and categorisation

**Legal test:** Biometric identification and categorisation of natural persons. Legal test (Art 6(2) + Annex III §1): Does this AI system perform remote biometric identification, biometric categorisation based on sensitive attributes, or emotion recognition? Key distinction: the system must IDENTIFY or CATEGORISE natural persons using biometric data, not merely process images/audio for other purposes.

**Code context:**
```
   1 >> import webbrowser
   2    from flask import Flask, render_template, Response
   3    import cv2
   4    import face_recognition
   5    import numpy as np
   6    import os
   7    from datetime import datetime
   8    import pandas as pd
   9    from flask import Flask, render_template
  10    from flask_wtf import FlaskForm
  11    from wtforms import StringField, PasswordField
```

**Workbench hint:** NOTE: This appears to be an API/application entry point.

**Your label:** `____` (tp / fp)
**Your notes:** 

---