import logging

logger = logging.getLogger(__name__)


class ModelLoader:
    """Singleton registry for the injection classifier, PHI NER pipeline, and
    embedding model. Nothing downloads or loads until a given model is actually
    accessed, so importing/instantiating this class is cheap and never crashes
    a container at startup for lack of network access or weights."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
            cls._instance._device = None
            cls._instance._injection_tokenizer = None
            cls._instance._injection_model = None
            cls._instance._phi_pipeline = None
            cls._instance._embedding_model = None
        return cls._instance

    @property
    def device(self):
        if self._device is None:
            import torch

            self._device = 0 if torch.cuda.is_available() else -1
            logger.info(f"AI models will load onto device: {'GPU (CUDA)' if self._device == 0 else 'CPU'}")
        return self._device

    def _load_injection_model(self):
        if self._injection_model is not None:
            return
        from pathlib import Path

        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        # The project's own fine-tuned 5-class classifier, not an off-the-shelf
        # model. Same relative-path convention as analysis_service.py's
        # SecureRAGPipeline root resolution (this file sits at the same
        # backend/app/ai_engine/ depth), so it resolves correctly both in dev
        # (repo root) and in the container, where docker-compose.yml mounts
        # Healthcare_Dataset_Preparation/ at /app/Healthcare_Dataset_Preparation
        # specifically so these weights aren't baked into the image.
        model_dir = Path(__file__).resolve().parents[3] / "Healthcare_Dataset_Preparation" / "outputs" / "security_classifier" / "best_model"
        self._injection_tokenizer = AutoTokenizer.from_pretrained(model_dir)
        self._injection_model = AutoModelForSequenceClassification.from_pretrained(model_dir)
        if self.device == 0:
            self._injection_model = self._injection_model.cuda()
        logger.info(f"Security classifier loaded from {model_dir}.")

    @property
    def injection_tokenizer(self):
        self._load_injection_model()
        return self._injection_tokenizer

    @property
    def injection_model(self):
        self._load_injection_model()
        return self._injection_model

    @property
    def phi_pipeline(self):
        if self._phi_pipeline is None:
            from transformers import pipeline

            ner_model_name = "dslim/bert-base-NER"
            pipeline_kwargs = dict(
                task="token-classification",
                model=ner_model_name,
                tokenizer=ner_model_name,
                aggregation_strategy="simple",  # Groups split sub-words into single entities
                device=self.device,
            )
            try:
                # AutoTokenizer.from_pretrained() makes a Hub metadata call
                # (chat-template lookup) even when the weights are already
                # fully cached locally -- local_files_only skips that, so a
                # flaky connection can't crash a cold singleton construction
                # for a model that's already on disk. Falls back to a normal
                # networked load on an actual first-ever run (nothing cached
                # yet), which is the scenario local_files_only would break.
                self._phi_pipeline = pipeline(local_files_only=True, **pipeline_kwargs)
            except Exception:
                logger.info(f"{ner_model_name} not cached locally yet; downloading.")
                self._phi_pipeline = pipeline(**pipeline_kwargs)
            logger.info("PHI/PII NER pipeline loaded.")
        return self._phi_pipeline

    @property
    def embedding_model(self):
        if self._embedding_model is None:
            from sentence_transformers import SentenceTransformer

            model_name = "BAAI/bge-small-en-v1.5"
            try:
                # Same rationale as phi_pipeline above: skip the Hub
                # metadata round-trip once the model is already cached.
                self._embedding_model = SentenceTransformer(model_name, local_files_only=True)
            except Exception:
                logger.info(f"{model_name} not cached locally yet; downloading.")
                self._embedding_model = SentenceTransformer(model_name)
            logger.info("Embedding model loaded.")
        return self._embedding_model


# Cheap to instantiate: __new__ only sets None placeholders, no model loads here.
model_registry = ModelLoader()
