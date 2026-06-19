# regula-ignore
"""Tests for project_fingerprint module — project import fingerprinting."""
import sys
from pathlib import Path

# Bare import convention: point at scripts/ directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from project_fingerprint import (
    DOMAIN_FINGERPRINTS,
    SUPPRESS_FINGERPRINTS,
    scan_project_imports,
    _extract_imports,
    _get_project_name,
)


# ===================================================================
# 1. DOMAIN_FINGERPRINTS — medical imports activate medical_devices
# ===================================================================


def test_medical_fingerprint_contains_monai():
    """monai should be in medical domain imports."""
    assert "monai" in DOMAIN_FINGERPRINTS["medical"]["imports"]


def test_medical_fingerprint_contains_medkit_lib():
    """medkit_lib should be in medical domain imports."""
    assert "medkit_lib" in DOMAIN_FINGERPRINTS["medical"]["imports"]


def test_medical_fingerprint_contains_dicomweb_client():
    """dicomweb_client should be in medical domain imports."""
    assert "dicomweb_client" in DOMAIN_FINGERPRINTS["medical"]["imports"]


def test_medical_fingerprint_contains_pylidc():
    """pylidc should be in medical domain imports."""
    assert "pylidc" in DOMAIN_FINGERPRINTS["medical"]["imports"]


def test_medical_fingerprint_activates_medical_devices():
    """Medical domain should activate medical_devices."""
    assert "medical_devices" in DOMAIN_FINGERPRINTS["medical"]["activates"]


def test_medical_domain_all_imports():
    """Medical domain should contain all expected medical libraries."""
    expected = {"monai", "nibabel", "pydicom", "simpleitk", "medpy",
                "torchio", "dicom", "hl7", "fhir", "medcat",
                "medkit_lib", "dicomweb_client", "pylidc",
                "radiology", "nifti", "mne"}
    assert DOMAIN_FINGERPRINTS["medical"]["imports"] == expected


# ===================================================================
# 2. SUPPRESS_FINGERPRINTS — medical_imaging suppresses critical_infrastructure
# ===================================================================


def test_medical_imaging_suppresses_critical_infrastructure():
    """medical_imaging fingerprint should suppress critical_infrastructure."""
    assert "critical_infrastructure" in SUPPRESS_FINGERPRINTS["medical_imaging"]["suppresses"]


def test_medical_imaging_contains_monai():
    """monai should be in medical_imaging suppress fingerprint."""
    assert "monai" in SUPPRESS_FINGERPRINTS["medical_imaging"]["imports"]


def test_medical_imaging_contains_expected_imports():
    """medical_imaging suppression should contain the right libraries."""
    expected = {"monai", "nibabel", "simpleitk", "torchio", "medpy", "pydicom"}
    assert SUPPRESS_FINGERPRINTS["medical_imaging"]["imports"] == expected


# ===================================================================
# 3. SUPPRESS_FINGERPRINTS — experiment_tracking suppresses
#    critical_infrastructure and worker_management
# ===================================================================


def test_experiment_tracking_suppresses_critical_infrastructure():
    """experiment_tracking should suppress critical_infrastructure."""
    assert "critical_infrastructure" in SUPPRESS_FINGERPRINTS["experiment_tracking"]["suppresses"]


def test_experiment_tracking_suppresses_worker_management():
    """experiment_tracking should suppress high_risk__worker_management."""
    assert "high_risk__worker_management" in SUPPRESS_FINGERPRINTS["experiment_tracking"]["suppresses"]


def test_experiment_tracking_contains_mlflow():
    """mlflow should be in experiment_tracking imports."""
    assert "mlflow" in SUPPRESS_FINGERPRINTS["experiment_tracking"]["imports"]


def test_experiment_tracking_contains_wandb():
    """wandb should be in experiment_tracking imports."""
    assert "wandb" in SUPPRESS_FINGERPRINTS["experiment_tracking"]["imports"]


def test_experiment_tracking_all_imports():
    """experiment_tracking should contain all expected trackers."""
    expected = {"mlflow", "wandb", "neptune", "comet_ml", "clearml", "tensorboard"}
    assert SUPPRESS_FINGERPRINTS["experiment_tracking"]["imports"] == expected


# ===================================================================
# 4. SUPPRESS_FINGERPRINTS — database_migration (alembic) suppresses
#    critical_infrastructure
# ===================================================================


def test_database_migration_suppresses_critical_infrastructure():
    """database_migration should suppress critical_infrastructure."""
    assert "critical_infrastructure" in SUPPRESS_FINGERPRINTS["database_migration"]["suppresses"]


def test_database_migration_contains_alembic():
    """alembic should be in database_migration imports."""
    assert "alembic" in SUPPRESS_FINGERPRINTS["database_migration"]["imports"]


def test_database_migration_all_imports():
    """database_migration should contain all expected migration tools."""
    expected = {"alembic", "django", "flask_migrate", "tortoise", "peewee"}
    assert SUPPRESS_FINGERPRINTS["database_migration"]["imports"] == expected


# ===================================================================
# 5. Biometrics fingerprints
# ===================================================================


def test_biometrics_contains_openface():
    """openface should be in biometrics domain imports."""
    assert "openface" in DOMAIN_FINGERPRINTS["biometrics"]["imports"]


def test_biometrics_contains_vggface():
    """vggface should be in biometrics domain imports."""
    assert "vggface" in DOMAIN_FINGERPRINTS["biometrics"]["imports"]


def test_biometrics_contains_facenet():
    """facenet should be in biometrics domain imports."""
    assert "facenet" in DOMAIN_FINGERPRINTS["biometrics"]["imports"]


def test_biometrics_contains_dlib():
    """dlib should be in biometrics domain imports."""
    assert "dlib" in DOMAIN_FINGERPRINTS["biometrics"]["imports"]


def test_biometrics_activates_biometrics():
    """Biometrics domain should activate 'biometrics' subcategory."""
    assert "biometrics" in DOMAIN_FINGERPRINTS["biometrics"]["activates"]


def test_biometrics_all_imports():
    """Biometrics domain should contain all expected face/biometric libs."""
    expected = {"deepface", "face_recognition", "insightface", "arcface",
                "openface", "vggface", "vggface2", "facenet", "dlib"}
    assert DOMAIN_FINGERPRINTS["biometrics"]["imports"] == expected


# ===================================================================
# 6. Finance fingerprints
# ===================================================================


def test_finance_contains_ccxt():
    """ccxt should be in finance domain imports."""
    assert "ccxt" in DOMAIN_FINGERPRINTS["finance"]["imports"]


def test_finance_contains_pandas_datareader():
    """pandas_datareader should be in finance domain imports."""
    assert "pandas_datareader" in DOMAIN_FINGERPRINTS["finance"]["imports"]


def test_finance_contains_alpaca_trade_api():
    """alpaca_trade_api should be in finance domain imports."""
    assert "alpaca_trade_api" in DOMAIN_FINGERPRINTS["finance"]["imports"]


def test_finance_activates_essential_services():
    """Finance domain should activate essential_services."""
    assert "essential_services" in DOMAIN_FINGERPRINTS["finance"]["activates"]


# ===================================================================
# 7. scan_project_imports() with tmp_path projects
# ===================================================================


def test_scan_empty_project(tmp_path):
    """Empty project -> no domains detected, no activations, no suppressions."""
    result = scan_project_imports(str(tmp_path))
    assert result["domains_detected"] == set()
    assert result["activate"] == set()
    assert result["suppress"] == set()
    assert result["imports_found"] == set()


def test_scan_project_with_medical_import(tmp_path):
    """Project with monai import -> medical domain detected, medical_devices activated."""
    py_file = tmp_path / "train.py"
    py_file.write_text("import monai\nimport torch\nmodel = monai.nets.UNet()\n")
    result = scan_project_imports(str(tmp_path))
    assert "medical" in result["domains_detected"]
    assert "medical_devices" in result["activate"]
    assert "monai" in result["imports_found"]


def test_scan_project_with_medkit_lib_import(tmp_path):
    """Project with medkit_lib import -> medical domain detected."""
    py_file = tmp_path / "pipeline.py"
    py_file.write_text("from medkit_lib.core import Document\n")
    result = scan_project_imports(str(tmp_path))
    assert "medical" in result["domains_detected"]
    assert "medical_devices" in result["activate"]


def test_scan_project_with_dicomweb_client(tmp_path):
    """Project with dicomweb_client import -> medical domain detected."""
    py_file = tmp_path / "fetch_images.py"
    py_file.write_text("from dicomweb_client import DICOMwebClient\nclient = DICOMwebClient(url)\n")
    result = scan_project_imports(str(tmp_path))
    assert "medical" in result["domains_detected"]
    assert "medical_devices" in result["activate"]


def test_scan_project_with_pylidc(tmp_path):
    """Project with pylidc import -> medical domain detected."""
    py_file = tmp_path / "lung_scan.py"
    py_file.write_text("import pylidc\nscans = pylidc.query(pylidc.Scan)\n")
    result = scan_project_imports(str(tmp_path))
    assert "medical" in result["domains_detected"]
    assert "medical_devices" in result["activate"]


def test_scan_project_with_biometrics_import(tmp_path):
    """Project with deepface import -> biometrics domain detected."""
    py_file = tmp_path / "verify.py"
    py_file.write_text("from deepface import DeepFace\nresult = DeepFace.verify(img1, img2)\n")
    result = scan_project_imports(str(tmp_path))
    assert "biometrics" in result["domains_detected"]
    assert "biometrics" in result["activate"]


def test_scan_project_with_facenet_import(tmp_path):
    """Project with facenet import -> biometrics domain detected."""
    py_file = tmp_path / "embeddings.py"
    py_file.write_text("import facenet\nembedding = facenet.get_embedding(face_img)\n")
    result = scan_project_imports(str(tmp_path))
    assert "biometrics" in result["domains_detected"]
    assert "biometrics" in result["activate"]


def test_scan_project_with_dlib_import(tmp_path):
    """Project with dlib import -> biometrics domain detected."""
    py_file = tmp_path / "detect.py"
    py_file.write_text("import dlib\ndetector = dlib.get_frontal_face_detector()\n")
    result = scan_project_imports(str(tmp_path))
    assert "biometrics" in result["domains_detected"]
    assert "biometrics" in result["activate"]


def test_scan_project_with_finance_import(tmp_path):
    """Project with ccxt import -> finance domain detected."""
    py_file = tmp_path / "trading.py"
    py_file.write_text("import ccxt\nexchange = ccxt.binance()\n")
    result = scan_project_imports(str(tmp_path))
    assert "finance" in result["domains_detected"]
    assert "essential_services" in result["activate"]


def test_scan_project_with_alpaca_trade_api(tmp_path):
    """Project with alpaca_trade_api import -> finance domain detected."""
    py_file = tmp_path / "broker.py"
    py_file.write_text("import alpaca_trade_api\napi = alpaca_trade_api.REST()\n")
    result = scan_project_imports(str(tmp_path))
    assert "finance" in result["domains_detected"]
    assert "essential_services" in result["activate"]


def test_scan_project_with_pandas_datareader(tmp_path):
    """Project with pandas_datareader import -> finance domain detected."""
    py_file = tmp_path / "data.py"
    py_file.write_text("from pandas_datareader import data as pdr\ndf = pdr.get_data_yahoo('AAPL')\n")
    result = scan_project_imports(str(tmp_path))
    assert "finance" in result["domains_detected"]
    assert "essential_services" in result["activate"]


def test_scan_project_suppress_medical_imaging(tmp_path):
    """monai import -> suppresses critical_infrastructure AND activates medical_devices."""
    py_file = tmp_path / "segment.py"
    py_file.write_text("import monai\nimport torch\nmodel = monai.networks.nets.UNet()\n")
    result = scan_project_imports(str(tmp_path))
    # monai is in BOTH domain fingerprints (medical) and suppress fingerprints (medical_imaging)
    assert "medical" in result["domains_detected"]
    assert "medical_devices" in result["activate"]
    # medical_imaging suppresses critical_infrastructure
    # But since medical_devices is activated (not critical_infrastructure), no conflict
    # critical_infrastructure should be suppressed
    assert "critical_infrastructure" in result["suppress"]


def test_scan_project_suppress_experiment_tracking(tmp_path):
    """mlflow import -> suppresses critical_infrastructure and worker_management."""
    py_file = tmp_path / "train.py"
    py_file.write_text("import mlflow\nmlflow.log_metric('loss', 0.5)\n")
    result = scan_project_imports(str(tmp_path))
    assert "critical_infrastructure" in result["suppress"]
    assert "high_risk__worker_management" in result["suppress"]


def test_scan_project_suppress_wandb(tmp_path):
    """wandb import -> same suppressions as mlflow."""
    py_file = tmp_path / "experiment.py"
    py_file.write_text("import wandb\nwandb.init(project='test')\n")
    result = scan_project_imports(str(tmp_path))
    assert "critical_infrastructure" in result["suppress"]
    assert "high_risk__worker_management" in result["suppress"]


def test_scan_project_suppress_database_migration(tmp_path):
    """alembic import -> suppresses critical_infrastructure."""
    py_file = tmp_path / "migrations.py"
    py_file.write_text("from alembic import op\nop.add_column('users', sa.Column('name'))\n")
    result = scan_project_imports(str(tmp_path))
    assert "critical_infrastructure" in result["suppress"]


def test_scan_project_suppress_django(tmp_path):
    """django import -> suppresses critical_infrastructure."""
    py_file = tmp_path / "models.py"
    py_file.write_text("from django.db import models\nclass User(models.Model):\n    pass\n")
    result = scan_project_imports(str(tmp_path))
    assert "critical_infrastructure" in result["suppress"]


def test_scan_project_suppress_compute_infra(tmp_path):
    """celery import -> suppresses worker_management."""
    py_file = tmp_path / "tasks.py"
    py_file.write_text("from celery import Celery\napp = Celery('tasks')\n")
    result = scan_project_imports(str(tmp_path))
    assert "high_risk__worker_management" in result["suppress"]


def test_scan_project_suppress_speech_audio(tmp_path):
    """lhotse import -> suppresses biometrics."""
    py_file = tmp_path / "asr.py"
    py_file.write_text("import lhotse\ncuts = lhotse.CutSet.from_manifests()\n")
    result = scan_project_imports(str(tmp_path))
    assert "biometrics" in result["suppress"]


def test_scan_project_suppress_physics_simulation(tmp_path):
    """deepmd import -> suppresses safety_components, critical_infrastructure, worker_management, employment."""
    py_file = tmp_path / "simulate.py"
    py_file.write_text("import deepmd\nmodel = deepmd.DeepPot('model.pb')\n")
    result = scan_project_imports(str(tmp_path))
    assert "safety_components" in result["suppress"]
    assert "critical_infrastructure" in result["suppress"]
    assert "high_risk__worker_management" in result["suppress"]
    assert "employment" in result["suppress"]


# ===================================================================
# 8. Activation overrides suppression
# ===================================================================


def test_activation_overrides_suppression(tmp_path):
    """When a domain activates a category AND a suppress fingerprint
    suppresses it, activation wins."""
    # pymodbus activates critical_infrastructure (infrastructure domain)
    # alembic suppresses critical_infrastructure (database_migration)
    # But activation overrides suppression
    py_file1 = tmp_path / "scada.py"
    py_file1.write_text("import pymodbus\nfrom pymodbus.client import ModbusTcpClient\n")
    py_file2 = tmp_path / "migrate.py"
    py_file2.write_text("import alembic\nfrom alembic import op\n")
    result = scan_project_imports(str(tmp_path))
    assert "infrastructure" in result["domains_detected"]
    assert "critical_infrastructure" in result["activate"]
    # Activation should have removed it from suppress
    assert "critical_infrastructure" not in result["suppress"]


# ===================================================================
# 9. scan_project_imports skips non-.py files
# ===================================================================


def test_scan_ignores_non_python_files(tmp_path):
    """Non-.py files should not contribute to fingerprint."""
    js_file = tmp_path / "app.js"
    js_file.write_text("import monai from 'monai';\n")
    result = scan_project_imports(str(tmp_path))
    assert "medical" not in result["domains_detected"]
    assert result["imports_found"] == set()


def test_scan_ignores_txt_files(tmp_path):
    """Text files that happen to contain import statements are ignored."""
    txt_file = tmp_path / "requirements.txt"
    txt_file.write_text("monai==1.3.0\ndeepface==0.0.79\n")
    result = scan_project_imports(str(tmp_path))
    assert result["domains_detected"] == set()


# ===================================================================
# 10. SKIP_DIRS respected
# ===================================================================


def test_scan_skips_venv_directory(tmp_path):
    """Files in venv/ should be skipped."""
    venv_dir = tmp_path / "venv" / "lib"
    venv_dir.mkdir(parents=True)
    py_file = venv_dir / "monai_wrapper.py"
    py_file.write_text("import monai\n")
    result = scan_project_imports(str(tmp_path))
    assert "medical" not in result["domains_detected"]


def test_scan_skips_node_modules(tmp_path):
    """Files in node_modules/ should be skipped."""
    nm_dir = tmp_path / "node_modules" / "some_package"
    nm_dir.mkdir(parents=True)
    py_file = nm_dir / "wrapper.py"
    py_file.write_text("import deepface\n")
    result = scan_project_imports(str(tmp_path))
    assert "biometrics" not in result["domains_detected"]


def test_scan_skips_pycache(tmp_path):
    """Files in __pycache__/ should be skipped."""
    cache_dir = tmp_path / "__pycache__"
    cache_dir.mkdir()
    py_file = cache_dir / "cached.py"
    py_file.write_text("import ccxt\n")
    result = scan_project_imports(str(tmp_path))
    assert "finance" not in result["domains_detected"]


# ===================================================================
# 11. _extract_imports helper
# ===================================================================


def test_extract_imports_simple(tmp_path):
    """Simple import statements are extracted correctly."""
    py_file = tmp_path / "test.py"
    py_file.write_text("import os\nimport sys\nfrom pathlib import Path\n")
    imports = _extract_imports(py_file)
    assert "os" in imports
    assert "sys" in imports
    assert "pathlib" in imports


def test_extract_imports_dotted(tmp_path):
    """Dotted imports extract top-level module only."""
    py_file = tmp_path / "test.py"
    py_file.write_text("from torch.nn import Linear\nimport torch.optim\n")
    imports = _extract_imports(py_file)
    assert "torch" in imports
    # Should NOT have torch.nn or torch.optim as separate entries
    assert "torch.nn" not in imports


def test_extract_imports_from_style(tmp_path):
    """from X import Y extracts X."""
    py_file = tmp_path / "test.py"
    py_file.write_text("from monai.networks import nets\nfrom deepface import DeepFace\n")
    imports = _extract_imports(py_file)
    assert "monai" in imports
    assert "deepface" in imports


def test_extract_imports_nonexistent_file():
    """Non-existent file returns empty set."""
    result = _extract_imports(Path("/nonexistent/file.py"))
    assert result == set()


def test_extract_imports_case_lowered(tmp_path):
    """Import module names are lowercased."""
    py_file = tmp_path / "test.py"
    py_file.write_text("import TensorFlow\nfrom PyTorch import nn\n")
    imports = _extract_imports(py_file)
    assert "tensorflow" in imports
    assert "pytorch" in imports


# ===================================================================
# 12. _get_project_name helper
# ===================================================================


def test_get_project_name_pyproject_toml(tmp_path):
    """Reads project name from pyproject.toml."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "my-cool-lib"\nversion = "1.0.0"\n')
    name = _get_project_name(str(tmp_path))
    assert name == "my_cool_lib"


def test_get_project_name_normalises_dashes(tmp_path):
    """Dashes in project name are converted to underscores."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "lhotse-speech"\n')
    name = _get_project_name(str(tmp_path))
    assert name == "lhotse_speech"


def test_get_project_name_no_pyproject(tmp_path):
    """No pyproject.toml -> None."""
    name = _get_project_name(str(tmp_path))
    assert name is None


def test_get_project_name_empty_pyproject(tmp_path):
    """pyproject.toml without name field -> None."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[tool.pytest]\naddopts = '-q'\n")
    name = _get_project_name(str(tmp_path))
    assert name is None


# ===================================================================
# 13. Library self-detection via pyproject.toml
# ===================================================================


def test_self_detection_lhotse_suppresses_biometrics(tmp_path):
    """A project named 'lhotse' scanning itself should trigger speech_audio suppression."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "lhotse"\nversion = "1.0.0"\n')
    # lhotse's own source files use relative imports, not 'import lhotse'
    py_file = tmp_path / "core.py"
    py_file.write_text("from .cuts import CutSet\nimport torch\n")
    result = scan_project_imports(str(tmp_path))
    # Self-detection reads pyproject.toml name="lhotse" -> speech_audio suppression
    assert "biometrics" in result["suppress"]


def test_self_detection_deepmd_suppresses_multiple(tmp_path):
    """A project named 'deepmd' scanning itself should trigger physics_simulation suppression."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "deepmd"\nversion = "2.0.0"\n')
    py_file = tmp_path / "potential.py"
    py_file.write_text("from .model import DeepPot\nimport numpy\n")
    result = scan_project_imports(str(tmp_path))
    # physics_simulation suppresses: safety_components, critical_infrastructure,
    # high_risk__worker_management, employment
    assert "safety_components" in result["suppress"]
    assert "critical_infrastructure" in result["suppress"]


# ===================================================================
# 14. Multi-file project scanning
# ===================================================================


def test_scan_multiple_files_aggregates_imports(tmp_path):
    """Imports from multiple .py files are aggregated."""
    f1 = tmp_path / "model.py"
    f1.write_text("import torch\nimport monai\n")
    f2 = tmp_path / "data.py"
    f2.write_text("import numpy\nimport pandas\n")
    f3 = tmp_path / "eval.py"
    f3.write_text("import mlflow\n")
    result = scan_project_imports(str(tmp_path))
    assert "torch" in result["imports_found"]
    assert "monai" in result["imports_found"]
    assert "numpy" in result["imports_found"]
    assert "pandas" in result["imports_found"]
    assert "mlflow" in result["imports_found"]
    # monai -> medical domain + medical_imaging suppression
    assert "medical" in result["domains_detected"]
    # mlflow -> experiment_tracking suppression
    assert "critical_infrastructure" in result["suppress"]


def test_scan_nested_directory_structure(tmp_path):
    """Files in subdirectories are found and scanned."""
    sub = tmp_path / "src" / "models"
    sub.mkdir(parents=True)
    py_file = sub / "classifier.py"
    py_file.write_text("import deepface\nfrom deepface import DeepFace\n")
    result = scan_project_imports(str(tmp_path))
    assert "biometrics" in result["domains_detected"]
    assert "deepface" in result["imports_found"]


# ===================================================================
# 15. SUPPRESS_FINGERPRINTS structural validation
# ===================================================================


def test_all_suppress_fingerprints_have_required_keys():
    """Every suppress fingerprint must have 'imports' and 'suppresses' keys."""
    for name, cfg in SUPPRESS_FINGERPRINTS.items():
        assert "imports" in cfg, f"{name} missing 'imports'"
        assert "suppresses" in cfg, f"{name} missing 'suppresses'"
        assert isinstance(cfg["imports"], set), f"{name} imports is not a set"
        assert isinstance(cfg["suppresses"], set), f"{name} suppresses is not a set"
        assert len(cfg["imports"]) > 0, f"{name} has empty imports"
        assert len(cfg["suppresses"]) > 0, f"{name} has empty suppresses"


def test_all_domain_fingerprints_have_required_keys():
    """Every domain fingerprint must have 'imports' and 'activates' keys."""
    for name, cfg in DOMAIN_FINGERPRINTS.items():
        assert "imports" in cfg, f"{name} missing 'imports'"
        assert "activates" in cfg, f"{name} missing 'activates'"
        assert isinstance(cfg["imports"], set), f"{name} imports is not a set"
        assert isinstance(cfg["activates"], set), f"{name} activates is not a set"
        assert len(cfg["imports"]) > 0, f"{name} has empty imports"
        assert len(cfg["activates"]) > 0, f"{name} has empty activates"


# ===================================================================
# 16. Return structure validation
# ===================================================================


def test_return_structure_keys(tmp_path):
    """scan_project_imports returns dict with exactly the right keys."""
    result = scan_project_imports(str(tmp_path))
    expected_keys = {"domains_detected", "activate", "suppress", "imports_found"}
    assert set(result.keys()) == expected_keys


def test_return_types(tmp_path):
    """All return values are sets."""
    result = scan_project_imports(str(tmp_path))
    assert isinstance(result["domains_detected"], set)
    assert isinstance(result["activate"], set)
    assert isinstance(result["suppress"], set)
    assert isinstance(result["imports_found"], set)


# ===================================================================
# 17. ML framework suppression
# ===================================================================


def test_ml_framework_suppresses_critical_infrastructure(tmp_path):
    """diffusers import -> suppresses critical_infrastructure and safety_components."""
    py_file = tmp_path / "generate.py"
    py_file.write_text("from diffusers import StableDiffusionPipeline\n")
    result = scan_project_imports(str(tmp_path))
    assert "critical_infrastructure" in result["suppress"]
    assert "safety_components" in result["suppress"]


# ===================================================================
# 18. JS/TS package.json fingerprinting
# ===================================================================


def test_package_json_plain_dep_added_to_imports(tmp_path):
    """A plain (non-scoped) package.json dependency is added to imports_found."""
    pkg = tmp_path / "package.json"
    pkg.write_text('{"dependencies": {"openai": "^4.0.0"}}')
    result = scan_project_imports(str(tmp_path))
    assert "openai" in result["imports_found"]


def test_package_json_scoped_dep_cleaned(tmp_path):
    """Scoped packages like @tensorflow/tfjs are cleaned to 'tfjs'."""
    pkg = tmp_path / "package.json"
    pkg.write_text('{"dependencies": {"@tensorflow/tfjs": "^4.0.0"}}')
    result = scan_project_imports(str(tmp_path))
    assert "tfjs" in result["imports_found"]


def test_package_json_openai_triggers_js_ai_sdk_suppression(tmp_path):
    """openai in package.json -> js_ai_sdk suppression applied."""
    pkg = tmp_path / "package.json"
    pkg.write_text('{"dependencies": {"openai": "^4.0.0"}}')
    result = scan_project_imports(str(tmp_path))
    assert "critical_infrastructure" in result["suppress"]
    assert "safety_components" in result["suppress"]
    assert "high_risk__worker_management" in result["suppress"]


def test_package_json_tfjs_triggers_suppression(tmp_path):
    """@tensorflow/tfjs (cleaned to tfjs) -> js_ai_sdk suppression."""
    pkg = tmp_path / "package.json"
    pkg.write_text('{"devDependencies": {"@tensorflow/tfjs": "^4.0.0"}}')
    result = scan_project_imports(str(tmp_path))
    assert "critical_infrastructure" in result["suppress"]


def test_package_json_dev_and_peer_deps_read(tmp_path):
    """devDependencies and peerDependencies are also scanned."""
    pkg = tmp_path / "package.json"
    pkg.write_text(
        '{"devDependencies": {"langchain": "^0.2.0"},'
        ' "peerDependencies": {"react": "^18.0.0"}}'
    )
    result = scan_project_imports(str(tmp_path))
    assert "langchain" in result["imports_found"]
    assert "react" in result["imports_found"]


def test_package_json_missing_does_not_error(tmp_path):
    """No package.json -> no error, empty imports from JS path."""
    # No package.json created
    result = scan_project_imports(str(tmp_path))
    assert isinstance(result["imports_found"], set)


def test_package_json_invalid_json_does_not_error(tmp_path):
    """Malformed package.json is silently ignored."""
    pkg = tmp_path / "package.json"
    pkg.write_text("{not valid json")
    result = scan_project_imports(str(tmp_path))
    assert isinstance(result["imports_found"], set)


def test_package_json_empty_deps_keys(tmp_path):
    """package.json with no dependencies keys does not error."""
    pkg = tmp_path / "package.json"
    pkg.write_text('{"name": "my-app", "version": "1.0.0"}')
    result = scan_project_imports(str(tmp_path))
    assert isinstance(result["imports_found"], set)


def test_package_json_combined_with_python_imports(tmp_path):
    """package.json deps and Python imports are both in imports_found."""
    pkg = tmp_path / "package.json"
    pkg.write_text('{"dependencies": {"openai": "^4.0.0"}}')
    py_file = tmp_path / "server.py"
    py_file.write_text("import flask\n")
    result = scan_project_imports(str(tmp_path))
    assert "openai" in result["imports_found"]
    assert "flask" in result["imports_found"]
