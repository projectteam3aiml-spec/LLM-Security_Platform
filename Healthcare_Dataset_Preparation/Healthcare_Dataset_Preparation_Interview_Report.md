# Healthcare Dataset Preparation: Interview-Ready Technical Report

## Evidence Status

- **Verified implementation:** Directly supported by Python scripts, notebooks, saved model files, CSV files, or generated metrics.
- **Generated artifact:** Produced by a notebook or script, but not necessarily reproducible in the current workspace.
- **Historical/design artifact:** Present in the repository but conflicts with later implementation or represents a demonstration.
- **Not verified from the repository:** Required evidence was not available inside `Healthcare_Dataset_Preparation`.

No existing project files were modified while preparing this report.

---

# 1. Folder Inventory

## Raw datasets

| File | Purpose | Pipeline stage |
|---|---|---|
| `data/raw/MedQuAD.csv` | Medical question-answer dataset | Knowledge base and safe classifier examples |
| `data/raw/PubMedQA.csv` | Biomedical question-answer dataset | Knowledge base and safe classifier examples |
| `data/raw/mpib_sample1.csv` | MPIB training data | Security classifier |
| `data/raw/mpib_sample2.csv` | MPIB test data | Security classifier |
| `data/raw/mpib_validation.csv` | MPIB validation data | Security classifier |

## Synthetic datasets

| File | Rows | Class contribution |
|---|---:|---|
| `data/synthetic/general_healthcare_prompts.csv` | 1,005 | Safe |
| `data/synthetic/jailbreak_prompts.csv` | 1,000 | Jailbreak |
| `data/synthetic/phi_prompts.csv` | 1,000 | PHI |

The synthetic generation scripts do not seed Python's `random` module. Exact regeneration is therefore not verified as reproducible.

## Processing scripts

| File | Purpose |
|---|---|
| `scripts/prepare_medquad.py` | Cleans and standardizes MedQuAD |
| `scripts/prepare_pubmedqa.py` | Cleans and standardizes PubMedQA |
| `scripts/prepare_mpib.py` | Converts MPIB fields and severity labels |
| `scripts/create_master_datasets.py` | Combines datasets and creates master splits |
| `scripts/create_security_dataset.py` | Produces security classifier splits |
| `scripts/create_knowledge_base.py` | Creates the knowledge-base CSV |
| `scripts/generate_general_prompts.py` | Generates safe synthetic prompts |
| `scripts/generate_jailbreak_dataset.py` | Generates jailbreak prompts |
| `scripts/generate_phi_dataset.py` | Generates PHI prompts |
| `scripts/inspect_datasets.py` | Dataset inspection |
| `scripts/merge_datasets.py` | Empty historical scaffolding file |

## Notebooks

1. `01_security_dataset_eda.ipynb`: Security dataset EDA.
2. `02_knowledge_base_eda.ipynb`: Knowledge-base EDA.
3. `03_security_preprocessing.ipynb`: Security preprocessing and label creation.
4. `04_tokenization_clean.ipynb`: Tokenization and validation.
5. `05_train_security_classifier.ipynb`: DistilBERT training.
6. `06_model_evaluation.ipynb`: Test evaluation.
7. `07_knowledge_base_inspection.ipynb`: Knowledge-base verification.
8. `08_prepare_knowledge_base.ipynb`: Retrieval document preparation.
9. `09_generate_embeddings.ipynb`: Embedding generation.
10. `10_build_faiss_index.ipynb`: FAISS index creation.
11. `11_retrieval_evaluation.ipynb`: Retrieval evaluation.
12. `12_classifier_retrieval_integration.ipynb`: Classifier and retrieval policy.
13. `13_cross_verify_training_results.ipynb`: Cross-verification.
14. `14_risk_aware_decision_engine.ipynb`: Risk-engine demonstration.
15. `14_rag_llm_integration.ipynb`: Short RAG notebook.
16. `15_output_validation.ipynb`: Output validation.
17. `15_rag_llm_integration.ipynb`: RAG and LLM integration.
18. `16_healthcare_rule_engine.ipynb`: Rule-engine demonstration.
19. `16_shap_explainability.ipynb`: Explainability demonstration.
20. `17_behavioral_anomaly_engine.ipynb`: Anomaly-engine demonstration.
21. `18_explainability_shap.ipynb`: SHAP-oriented integration demonstration.

## Processed data

- `data/processed/medquad_clean.csv`: 14,979 rows.
- `data/processed/pubmedqa_clean.csv`: 1,000 rows.
- `data/processed/mpib_train_clean.csv`: 7,759 rows.
- `data/processed/mpib_validation_clean.csv`: 969 rows.
- `data/processed/mpib_test_clean.csv`: 969 rows.
- `data/processed/master_train.csv`: 22,946 rows.
- `data/processed/master_validation.csv`: 2,867 rows.
- `data/processed/master_test.csv`: 2,868 rows.
- `data/processed/security_train.csv`: 11,463 rows.
- `data/processed/security_validation.csv`: 2,369 rows.
- `data/processed/security_test.csv`: 2,370 rows.
- `data/processed/security_train_processed.csv`: 10,059 rows.
- `data/processed/security_validation_processed.csv`: 2,155 rows.
- `data/processed/security_test_processed.csv`: 2,156 rows.
- `data/processed/knowledge_base.csv`: 15,979 rows.

The referenced file `data/processed/knowledge/knowledge_base_retrieval.csv` is not currently present.

## Important outputs

### EDA

Located under `outputs/eda/`:

- Security summary and class distributions.
- Source distribution.
- Severity distribution.
- PHI distribution.
- Prompt-length plots.
- Missing-value plots.
- Attack/severity heatmap.
- Knowledge-base statistics.
- Duplicate statistics.
- Source distribution.
- Prompt, context, and response histograms.

### Classifier

Located under `outputs/security_classifier/`:

- `best_model/`
- `checkpoint-1258/`
- `checkpoint-2516/`
- Tokenizer files.
- `model.safetensors`.
- `config.json`.
- `training_args.bin`.
- `training_history.csv`.
- Training loss and validation accuracy plots.
- `training_summary.txt`.

### Tokenization

Located under `outputs/tokenized/`:

- `train_encodings.pt`.
- `validation_encodings.pt`.
- `test_encodings.pt`.
- `label_mapping.csv`.
- `label_encoder.pkl`.
- `tokenization_summary.txt`.

### Retrieval

- `outputs/embeddings/knowledge_base_embeddings.npy`.
- `outputs/embeddings/embedding_metadata.csv`.
- `outputs/faiss/knowledge_base.index`.
- Retrieval results and metrics.

### Evaluation

- Classification report.
- Confusion matrix.
- Misclassified samples.
- Per-class precision, recall, and F1 plots.
- Retrieval metrics.
- Risk-engine test results.
- Output-validation results.
- RAG integration results.

No README or dedicated configuration file was found inside `Healthcare_Dataset_Preparation`.

---

# 2. Complete Data Pipeline

The verified classifier pipeline is:

```text
Raw datasets
    |
    v
Dataset-specific cleaning
    |
    v
Common schema conversion
    |
    v
Label and severity standardization
    |
    v
Dataset combination
    |
    v
Train / validation / test creation
    |
    v
Security preprocessing
    |
    v
Tokenization
    |
    v
DistilBERT training
    |
    v
Classifier evaluation
```

The separate knowledge-base pipeline is:

```text
MedQuAD + PubMedQA
    |
    v
Knowledge-base CSV
    |
    v
Retrieval text construction
    |
    v
Normalized 768-dimensional embeddings
    |
    v
FAISS IndexFlatIP
    |
    v
Top-K retrieval
```

---

# 3. Datasets

## MedQuAD

Raw file: `data/raw/MedQuAD.csv`

- Raw rows: **48,480**.
- Columns: `Disease`, `Question`, `Answer`, `Question_Type`, `Source`, `URL`.
- Cleaned rows: **14,979**.
- Processed columns include `id`, `prompt`, `context`, `response`, `attack_type`, `is_safe`, `severity`, `phi_present`, `disease`, `question_type`, `source_name`, `url`, and `source_dataset`.

Cleaning includes:

- Full duplicate removal.
- Missing or blank question removal.
- Missing or blank answer removal.
- Duplicate-question removal.
- Conversion to the common schema.
- Assignment of `safe`.
- Severity `0`.
- `phi_present = 0`.

It contributes safe examples and knowledge-base documents.

## PubMedQA

Raw file: `data/raw/PubMedQA.csv`

- Rows: **1,000**.
- Columns: `PMID`, `Question`, `Context`, `Labels`, `Meshes`, `Year`, `Reasoning_Required`, `Reasoning_Free`, `Final_Decision`, and `Long_Answer`.

Processing includes:

- Full duplicate removal.
- Missing or blank question removal.
- Missing or blank long-answer removal.
- Duplicate question-answer pair removal.
- Renaming to the common schema.
- Assignment of `safe`.
- Severity `0`.
- `phi_present = 0`.

It contributes safe examples and knowledge-base documents.

## MPIB

Raw files:

- `mpib_sample1.csv`: **7,759** rows.
- `mpib_sample2.csv`: **969** rows.
- `mpib_validation.csv`: **969** rows.

Raw columns:

- `vector`
- `user_query`
- `contexts`
- `metadata`
- `rule`
- `scenario`
- `parent_sample_id`
- `sample_id`
- `labels`

The processing script:

- Parses `labels` using `ast.literal_eval`.
- Converts `user_query` to `prompt`.
- Converts `contexts` to `context`.
- Extracts severity.
- Maps severity to security classes.
- Detects PHI from `harm_types` containing `H3`.
- Preserves scenario, rule, metadata, parent ID, and sample ID.

Severity mapping:

| Severity | Class |
|---:|---|
| 0 | `safe` |
| 1-2 | `suspicious` |
| Greater than 2 | `malicious` |

MPIB contributes safe, suspicious, and malicious examples.

## Synthetic-General

- Rows: **1,005**.
- Intended class: `safe`.
- Columns: `prompt`, `response`, `attack_type`, `is_safe`, `severity`, `phi_present`, and `source_dataset`.

## Synthetic-Jailbreak

- Rows: **1,000**.
- Intended class: `jailbreak`.
- Same seven-column synthetic schema.

## Synthetic-PHI

- Rows: **1,000**.
- Intended class: `phi`.
- Same seven-column synthetic schema.

Synthetic data was used to increase coverage of security behaviors that were not sufficiently represented in ordinary medical datasets.

---

# 4. Preprocessing

## Missing-value handling

- Missing question or answer values are removed from MedQuAD and PubMedQA.
- Missing fields in the common combined schema receive defaults.
- Knowledge-base text fields use empty strings for missing values.
- `source_dataset` uses `unknown` when missing during retrieval preparation.

## Blank-text removal

Blank questions and answers are removed from the medical datasets.

## Duplicate removal

Implemented locally within several preprocessing stages:

- Full-row duplicate removal.
- Duplicate-question removal in MedQuAD.
- Duplicate question-answer pair removal in PubMedQA.
- Duplicate prompt removal in later security preprocessing.

However, original cross-source and cross-split duplicate removal is not fully verified.

## Label conversion

MPIB severity is converted to `safe`, `suspicious`, or `malicious`.

Synthetic datasets already contain security labels.

Medical datasets are assigned `safe`.

## Column standardization

Different source schemas are converted to a common schema containing fields such as:

- `prompt`
- `context`
- `response`
- `attack_type`
- `severity`
- `is_safe`
- `phi_present`
- `source_dataset`

## Severity processing

Severity is preserved as a numeric feature.

```text
0       -> safe
1 or 2  -> suspicious
> 2     -> malicious
```

## PHI processing

The MPIB processor sets `phi_present = 1` when the harm-type field contains `H3`.

Synthetic PHI data is explicitly labelled with `phi_present`.

## Source tracking

`source_dataset` is retained throughout processing, allowing the project to distinguish MPIB, MedQuAD, PubMedQA, Synthetic-General, Synthetic-Jailbreak, and Synthetic-PHI.

## Feature creation

The processed classifier files include:

- `characters`
- `words`
- `label`
- `label_id`
- `label_name`

The retrieval preparation creates:

- `document_id`
- `retrieval_text`
- `text_length`

URL removal and HTML removal are not verified as implemented.

---

# 5. EDA Results

## Security training data

From `outputs/eda/security/summary.txt`:

- Rows: **11,463**.
- Reported columns: **8**.
- Missing values: **0**.
- Average prompt length: **541.93 characters**.
- Average prompt length: **84.61 words**.
- Duplicate prompts: **1,404**.

### Class distribution

| Class | Count | Approx. percentage |
|---|---:|---:|
| Safe | 6,313 | 55.07% |
| Malicious | 2,874 | 25.07% |
| Jailbreak | 815 | 7.11% |
| PHI | 800 | 6.98% |
| Suspicious | 661 | 5.77% |

### Severity distribution

| Severity | Count |
|---:|---:|
| 0 | 6,313 |
| 1 | 107 |
| 2 | 554 |
| 3 | 3,774 |
| 4 | 715 |

### Source distribution

| Source | Count |
|---|---:|
| MPIB | 7,759 |
| MedQuAD | 1,000 |
| Synthetic-Jailbreak | 815 |
| Synthetic-PHI | 800 |
| Synthetic-General | 789 |
| PubMedQA | 300 |

The security EDA includes class-distribution, safe-versus-unsafe, source-distribution, severity-distribution, PHI-distribution, prompt-length, prompt-length-by-attack, attack/severity heatmap, missing-value, and top-word plots.

## Knowledge-base EDA

The knowledge base contains:

- Rows: **15,979**.
- Columns: **4**.
- MedQuAD: **14,979**.
- PubMedQA: **1,000**.
- Missing values: **0**.
- Full duplicate rows: **0**.
- Duplicate prompts: **0**.
- Duplicate responses: **518**.
- Unique responses: **15,461**.
- Average prompt length: **54.30 characters**.
- Average prompt length: **8.58 words**.
- Average response length: **1,223.25 characters**.
- Average response length: **188.73 words**.
- Maximum response length: **29,046 characters**.
- Maximum response length: **4,281 words**.
- Context populated: **1,000**.
- Context empty: **14,979**.

These results indicate that the knowledge base is dominated by MedQuAD and contains highly variable response lengths.

---

# 6. Security Classes and Label Mapping

The final classifier classes are:

| Class | ID | Meaning |
|---|---:|---|
| `safe` | 0 | Normal healthcare-related request |
| `malicious` | 1 | Harmful or clearly unsafe request |
| `phi` | 2 | Request involving protected health information |
| `jailbreak` | 3 | Attempt to bypass model safety controls |
| `suspicious` | 4 | Ambiguous or potentially risky request |

This mapping is confirmed by notebooks 03 and 04, `outputs/tokenized/label_mapping.csv`, and the saved model `config.json`.

Raw datasets do not all use this mapping. MPIB initially uses severity and harm-type fields. Medical datasets do not begin with the five-class security labels. Synthetic datasets contain source-specific label fields. The mapping is standardized before tokenization.

---

# 7. Dataset Combination

The master combination script combines:

- MPIB.
- MedQuAD.
- PubMedQA.
- Synthetic-General.
- Synthetic-Jailbreak.
- Synthetic-PHI.

The master data uses a broad common schema with fields including `prompt`, `context`, `response`, `attack_type`, `severity`, `is_safe`, `phi_present`, `source_dataset`, `source_name`, `url`, `disease`, `question_type`, `scenario`, `rule_name`, `metadata`, and identifiers and biomedical metadata.

Defaults are used when a source does not contain a particular field.

Important limitation: IDs are created independently in different sources and splits, so they are not necessarily globally unique.

---

# 8. Train, Validation, and Test Split

The master-dataset script uses:

- `test_size=0.20`.
- `random_state=42`.
- A second 50/50 split of the temporary 20% portion.

This nominally produces 80% training, 10% validation, and 10% test.

MPIB's existing train, validation, and test files are reused instead of being repartitioned.

The security dataset reports:

| Dataset | Rows |
|---|---:|
| Security train | 11,463 |
| Security validation | 2,369 |
| Security test | 2,370 |

Later processed artifacts report:

| Dataset | Rows |
|---|---:|
| Processed train | 10,059 |
| Processed validation | 2,306 |
| Processed test | 2,306 |

Notebook 13 verifies the later processed CSV counts.

A historical tokenization output reports validation **2,155** and test **2,156**. This conflicts with the later **2,306 / 2,306** artifacts. The later cross-verification should be treated as the current result, while the earlier result is historical or stale.

Stratification is not established for every split. Group-based splitting is not verified.

---

# 9. Leakage and Duplicate Analysis

Verified findings:

- Knowledge-base duplicate prompts: **0**.
- Knowledge-base full duplicate rows: **0**.
- Knowledge-base duplicate responses: **518**.
- Security training duplicate prompts in the EDA artifact: **1,404**.
- Later within-split duplicate prompts were removed.
- Notebook 04 checks normalized prompt overlap between final train, validation, and test sets.
- Notebook 04 reports no normalized prompt intersection between final splits.

Limitations:

- The final checks operate on already-created split files.
- They do not prove that the original master construction was leakage-free.
- Cross-source duplicate checks are not verified.
- Cross-split duplicate checks before preprocessing are not verified.
- Conflicting labels for duplicate prompts are not comprehensively reported.

Data leakage means information from validation or test data influences training. It can make evaluation appear better than real-world performance.

The repository provides useful final-split checks, but zero leakage across the complete original pipeline is **not verified**.

---

# 10. Tokenization

The verified tokenizer is:

```text
distilbert-base-uncased
```

Configuration:

- Maximum length: **256**.
- Truncation: enabled.
- Padding: enabled.
- Return type: PyTorch tensors.
- Labels: `torch.long`.
- Inputs: `input_ids`, `attention_mask`, and `labels`.

Meaning of the tensors:

- `input_ids`: Integer vocabulary IDs for each token.
- `attention_mask`: Indicates which positions contain real tokens rather than padding.
- `labels`: Numeric target class IDs used by the loss function.

Tokenizer artifacts are saved under `outputs/security_classifier/best_model/`. Tokenized tensors are saved under `outputs/tokenized/`.

### Conflict

`tokenization_summary.txt` reports maximum sequence length **128**.

The actual tokenization notebook and training notebook use **256**. The model training artifacts also support **256**. Therefore, **256 is the verified implementation setting**, while 128 is a historical or stale summary value.

---

# 11. Transformer Fundamentals

A Transformer converts tokenized text into contextual representations.

1. The tokenizer converts text into token IDs.
2. Token IDs are converted into embeddings.
3. Self-attention allows each token to use information from other tokens.
4. The encoder produces contextual representations.
5. A classification head produces logits.
6. Softmax converts logits into probabilities.

For attention:

$$
Q = XW_Q,\qquad K = XW_K,\qquad V = XW_V
$$

The scaled attention calculation is:

$$
\operatorname{Attention}(Q,K,V)
=\operatorname{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V
$$

Where $Q$ is the Query, $K$ is the Key, $V$ is the Value, and $d_k$ is the key-vector dimension. $QK^T$ produces similarity scores and softmax converts them into attention weights.

Multi-head attention performs this process in multiple representation subspaces and combines the results.

The repository uses a pretrained Transformer classifier, but does not implement the Transformer architecture from scratch.

---

# 12. DistilBERT

Verified model:

```text
distilbert-base-uncased
```

Architecture details from the saved model configuration:

- Transformer layers: **6**.
- Hidden size: **768**.
- Attention heads: **12**.
- Vocabulary size: **30,522**.
- Output classes: **5**.

The classification flow is:

```text
Prompt
  -> DistilBERT tokenizer
  -> input_ids and attention_mask
  -> DistilBERT encoder
  -> classification head
  -> logits
  -> softmax probabilities
  -> predicted security class
```

The repository does not document a formal model-selection experiment comparing DistilBERT with other models. Reasons such as speed, lower memory usage, and practical deployment are interview-level engineering reasoning, not repository-proven selection evidence.

---

# 13. Model Training

Verified configuration from notebook 05:

| Parameter | Value |
|---|---|
| Model | `distilbert-base-uncased` |
| Epochs | 4 |
| Learning rate | `2e-5` |
| Training batch size | 16 |
| Evaluation batch size | 32 |
| Weight decay | 0.01 |
| Evaluation strategy | Every epoch |
| Checkpoint strategy | Every epoch |
| Best-model metric | Macro F1 |
| Best model loading | Enabled |
| Maximum checkpoints retained | 2 |
| Seed | 42 |
| FP16 | Enabled when CUDA is available |
| Loss | Weighted cross entropy |

The optimizer is managed by Hugging Face `Trainer`. The exact optimizer and scheduler class are not explicitly documented in the project report artifacts.

Best checkpoint:

- Checkpoint: **1258**.
- Best epoch: **2**.
- Validation macro F1: **0.8621**.
- Validation accuracy: **0.9328**.

Training history:

| Epoch | Accuracy | Macro F1 |
|---:|---:|---:|
| 1 | 0.9042 | 0.8401 |
| 2 | 0.9328 | 0.8621 |
| 3 | 0.9245 | 0.8509 |
| 4 | 0.9315 | 0.8465 |

The best model was selected from epoch 2 rather than the final epoch.

---

# 14. Class Imbalance

The majority class is `safe` with **6,313** training examples.

The minority class is `suspicious` with **661** examples.

Class imbalance can cause a model to favour the majority class. Accuracy may remain high while rare attack classes receive poor recall.

The project addresses imbalance using weighted cross entropy.

---

# 15. Weighted Cross Entropy

Normal cross entropy for one example is:

$$
L = -\log(p_y)
$$

Weighted cross entropy is:

$$
L = -w_y\log(p_y)
$$

The repository implements:

$$
w_c = \frac{N}{K n_c}
$$

Where $N$ is the total number of training samples, $K$ is the number of classes, $n_c$ is the number of samples in class $c$, and $w_c$ is the class weight.

Rare classes receive larger weights, making mistakes on those classes more influential during training. The loss is implemented using PyTorch `CrossEntropyLoss(weight=class_weights)`.

---

# 16. Model Evaluation

Test set size: **2,306**.

| Metric | Value |
|---|---:|
| Accuracy | 0.9389 |
| Macro precision | 0.8640 |
| Macro recall | 0.8720 |
| Macro F1 | 0.8673 |
| Weighted F1 | 0.9401 |

## Per-class results

| Class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| Safe | 0.9759 | 0.9765 | 0.9762 | 1,660 |
| Malicious | 0.8852 | 0.8460 | 0.8652 | 383 |
| PHI | 1.0000 | 1.0000 | 1.0000 | 98 |
| Jailbreak | 1.0000 | 1.0000 | 1.0000 | 72 |
| Suspicious | 0.4587 | 0.5376 | 0.4950 | 93 |

The main weakness is `suspicious`.

The perfect PHI and jailbreak scores should be interpreted cautiously because their supports are small and synthetic-heavy.

---

# 17. Macro F1 Versus Weighted F1

Macro F1 gives every class equal importance:

$$
F1_{\text{macro}}=\frac{1}{K}\sum_{c=1}^{K}F1_c
$$

Weighted F1 weights each class according to its support:

$$
F1_{\text{weighted}}=\sum_{c=1}^{K}\frac{n_c}{N}F1_c
$$

In this project:

- Macro F1: **0.8673**.
- Weighted F1: **0.9401**.

Weighted F1 is high because safe examples dominate the test set. Macro F1 exposes weaknesses in rare classes, especially suspicious prompts. Therefore, macro F1 is the more informative model-selection metric for this security problem.

---

# 18. Confusion Matrix

A confusion matrix contains:

- Rows: actual classes.
- Columns: predicted classes.
- Diagonal: correct predictions.
- Off-diagonal: misclassifications.

Observed error patterns include:

- Safe predicted as malicious.
- Suspicious predicted as safe.
- Suspicious predicted as malicious.

These errors matter because safe-to-malicious errors can unnecessarily block legitimate healthcare questions, suspicious-to-safe errors can permit risky requests to proceed, and suspicious-to-malicious errors can cause unnecessary blocking.

The available misclassification artifact is `outputs/evaluation/misclassified_samples.csv`.

Exact complete confusion-matrix cell counts were not available in the textual report artifacts.

---

# 19. Error Analysis

Verified observations:

- `suspicious` has the weakest F1: **0.4950**.
- Suspicious recall is **0.5376**.
- The misclassification file includes safe prompts predicted as malicious.
- Suspicious examples are predicted as safe or malicious.

Reasonable interpretation:

- Suspicious prompts likely lie between ordinary medical questions and clear attacks.
- Ambiguous language is harder to distinguish than strongly templated jailbreak or PHI examples.
- Synthetic examples may be easier than naturally occurring attacks.

The last two points are interpretations, not directly measured causal findings.

---

# 20. Inference Pipeline

For a new prompt:

```text
New prompt
  -> Tokenizer
  -> input_ids and attention_mask
  -> DistilBERT
  -> logits
  -> softmax
  -> class probabilities
  -> highest-probability class
  -> confidence
```

The predicted class is:

$$
\hat{y}=\arg\max_c p(y=c\mid x)
$$

Confidence is generally the highest softmax probability. The repository demonstrates classifier decisions and confidence values in integration and risk-engine artifacts. It does not establish that the confidence values are calibrated probabilities.

---

# 21. Security Engine Connection and Individual Role

The broader conceptual architecture is:

```text
User
  -> React frontend
  -> FastAPI API gateway
  -> Security engine
  -> Risk aggregation
  -> Decision engine
  -> Allow / Flag / Block
```

The classifier provides one security signal: the predicted input category and confidence.

Other components represented in the preparation folder include semantic retrieval, the healthcare rule engine, PHI detection, behavioural anomaly detection, and explainability. The authoritative backend implementations are outside this folder or represented by demonstrations.

## My individual role

The repository supports my contribution around:

- Dataset collection and organization.
- Source-specific preprocessing.
- Common-schema conversion.
- Security label creation.
- Exploratory data analysis.
- Train/validation/test preparation.
- Tokenization.
- DistilBERT training.
- Classifier evaluation.
- Cross-verification of saved results.
- Preparation and evaluation of the knowledge-base retrieval artifacts.

## Work not attributable to my role from this folder

The folder does not establish individual ownership of the React frontend, FastAPI gateway, authoritative backend risk engine, production rule engine, production PHI module, production anomaly engine, or complete continuous-learning system. Those components should be described as team or broader-system work unless separate evidence establishes ownership.

---

# 22. Risk Aggregator

The architecture diagram describes a conceptual formula:

$$
R=\alpha P_1+\beta P_2+\gamma S+\delta R+\epsilon\Phi+\zeta A
$$

Possible meanings are described architecturally as classifier, similarity, severity, rules, PHI, and anomaly signals. The exact symbol definitions are not fully verified inside this folder.

The exact six-term formula is **not verified as implemented**.

The risk notebook delegates risk calculation and thresholds to the backend `RiskEngine`, which is outside the audited folder. Therefore, the actually implemented formula, class-risk constants, and exact thresholds are **not verified from this folder**.

Observed results include:

- Safe confidence around `0.990`: risk approximately **0.238**, level `LOW`, decision `ALLOW`.
- Jailbreak confidence around `0.998`: risk approximately **0.9595**, level `HIGH`, decision `BLOCK`.

These observations must not be presented as proof of a specific six-term formula or of a formula such as `risk_score = 0.80 * class_risk + 0.20 * confidence`.

---

# 23. Knowledge Base and RAG

The verified Knowledge Base uses **MedQuAD** and **PubMedQA**:

- MedQuAD: **14,979 documents**.
- PubMedQA: **1,000 documents**.
- Total: **15,979 documents**.

The source knowledge-base schema is:

- `prompt`
- `context`
- `response`
- `source_dataset`

Notebook 08 normalizes prompt, context, and response strings and constructs retrieval text as:

```text
Question: <prompt>

Context: <context>

Answer: <response>
```

The context section is included only when non-empty.

The verified RAG flow is:

```text
User query
  -> Query embedding
  -> FAISS similarity search
  -> Top-K documents
  -> Retrieved context
  -> Healthcare LLM
  -> Output validation
  -> Response
```

## Embeddings

The verified embedding artifact has shape **15,979 x 768**.

The embedding model used by notebook 09 and the FAISS-building notebook is:

```text
pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb
```

This is a BioBERT-based biomedical sentence-embedding model.

Embeddings are normalized before indexing. NaN and infinite-value checks are implemented, and metadata count and unique document IDs are checked against the embedding matrix.

## FAISS

The repository explicitly uses:

```text
FAISS IndexFlatIP
```

The index contains **15,979** vectors of dimension **768**.

`IndexFlatIP` performs exact inner-product search. Since the embeddings are normalized, inner product is equivalent to cosine similarity:

$$
u\cdot v=\cos(\theta)$$

for normalized vectors.

## Top-K retrieval

The query is embedded using the embedding model, normalized, and searched against the FAISS index. FAISS returns the nearest document positions, which are mapped to document metadata. Top-1, Top-3, and Top-5 retrieval are evaluated.

## RAG model conflict

Notebook `14_rag_llm_integration.ipynb` references a different embedding model:

```text
pritamdeka/S-BioBert-snli-multinli-stsb
```

A FAISS index should be queried using the same embedding model used to construct it. The alternate-model RAG path is therefore **not verified and potentially incompatible** with the saved index. This contradiction is retained rather than silently resolved.

---

# 24. FAISS Explanation

FAISS is a library for similarity search over vectors.

`IndexFlatIP` means:

- `IndexFlat`: exact flat index, without an approximate partitioning structure.
- `IP`: inner product.

The project normalizes document and query vectors. For normalized vectors, inner product equals cosine similarity. The index stores one vector per knowledge-base document and returns the highest-scoring candidates for each query.

---

# 25. RAG Evaluation

Verified retrieval results:

- Evaluation queries: **100**.
- Top-1 accuracy: **0.6100**.
- Top-3 accuracy: **0.8500**.
- Top-5 accuracy: **0.9300**.

The evaluation measures whether the expected source document is retrieved for sampled in-dataset queries. It does not measure clinical correctness, factuality of generated answers, or quality on an independently collected external query set.

The repository must not describe these scores as clinical accuracy.

---

# 26. Output Validation

Input security is insufficient because a safe-looking prompt can still produce PHI leakage, unsafe medical advice, unsupported claims, or poorly grounded responses.

Controlled validation results:

| Check | Result |
|---|---:|
| PHI detection rate | 1.0 |
| Unsafe-output detection rate | 1.0 |
| False-positive rate | 0.0 |
| Unsupported-answer detection rate | 1.0 |
| Valid-answer rate | 1.0 |
| Abstention rate | 0.286 |

These results come from seven controlled cases. They are not population-level clinical validation.

---

# 27. Logging and Continuous Learning

The folder contains evidence of evaluation outputs, risk-engine test results, integration result files, audit-style CSV outputs, and training and retrieval artifacts.

However:

- Production logging is not fully verified.
- Monitoring is not fully verified.
- Drift detection is not verified.
- Automated feedback-to-retraining is not verified.
- A complete continuous-learning loop is not verified.

These should be described as architectural goals or partial demonstrations rather than complete production features.

---

# 28. End-to-End Scenarios

Exact confidence and risk values are available only for selected demonstrated cases.

## Safe medical question

```text
Prompt
  -> safe
  -> retrieval permitted
  -> knowledge-base search
  -> RAG response
  -> output validation
  -> allow
```

Observed safe case: confidence approximately `0.990`, risk approximately `0.238`, level `LOW`, decision `ALLOW`.

## Malicious prompt

```text
Prompt
  -> malicious
  -> retrieval blocked
  -> decision engine blocks
  -> event logged
```

Exact confidence and risk for a representative malicious case are not verified in the folder.

## Jailbreak attempt

```text
Prompt
  -> jailbreak
  -> retrieval blocked
  -> decision: BLOCK
  -> event logged
```

Observed confidence is approximately `0.998`, risk approximately `0.9595`, level `HIGH`, decision `BLOCK`.

## PHI-related request

```text
Prompt
  -> phi
  -> retrieval blocked
  -> decision: BLOCK
  -> event logged
```

This follows the verified integration policy. Exact confidence and risk are not verified.

## Suspicious or ambiguous prompt

```text
Prompt
  -> suspicious
  -> retrieval permitted by current policy
  -> retrieved context
  -> output validation
```

This creates residual risk because suspicious classification has only **0.4950 F1**. Exact risk thresholds are not verified.

---

# 29. Interview Questions

## Basic

**What problem does the project solve?**

It detects security-sensitive healthcare LLM inputs and combines classifier, retrieval, rules, PHI, and anomaly signals before deciding whether to allow, flag, or block a request.

**What are the five classes?**

Safe, malicious, PHI, jailbreak, and suspicious.

## Intermediate

**Why combine real and synthetic data?**

Medical datasets provide realistic safe healthcare language, while synthetic data provides explicit PHI and jailbreak examples. Synthetic examples may be more templated than real attacks.

**How was MPIB converted?**

MPIB severity 0 became safe, severity 1-2 became suspicious, and severity above 2 became malicious.

## Advanced

**How did you verify leakage?**

Final preprocessing checked duplicate prompts and normalized prompt intersections between final splits. Complete cross-source and pre-split leakage absence is not verified.

**What would you improve?**

Deduplicate globally before splitting, check normalized prompts and semantic near-duplicates, and use grouped splitting where parent IDs exist.

## ML fundamentals

**Why is accuracy insufficient?**

Safe is the majority class. A model can achieve high accuracy while performing poorly on suspicious or other rare security classes.

**Which metric was selected for the best model?**

Validation macro F1.

## NLP and Transformer

**What does self-attention do?**

It lets each token assign importance to other tokens so the model can build context-sensitive representations.

**What are Query, Key, and Value?**

Query represents what a token is looking for, Key represents what each token offers for matching, and Value contains the information aggregated after attention.

## Dataset

**Why is MedQuAD useful?**

It provides medical question-answer language and safe healthcare prompts for both the knowledge base and classifier.

**Why is MPIB useful?**

It supplies security-oriented examples with severity, scenarios, rules, and harm metadata.

## DistilBERT

**What model was used?**

`distilbert-base-uncased`, with six Transformer layers, hidden size 768, twelve attention heads, and five classifier outputs.

**Why DistilBERT?**

The repository confirms its use but does not record a formal comparison study. A reasonable engineering explanation is that it provides a smaller, faster Transformer suitable for classification.

## Evaluation

**What was the test macro F1?**

0.8673.

**Which class was weakest?**

Suspicious, with F1 0.4950.

## Risk engine

**Is the six-term architecture formula implemented?**

It is not verified in this folder. The notebook delegates authoritative risk calculation to a backend engine outside this folder.

## RAG and FAISS

**What FAISS index was used?**

`FAISS IndexFlatIP`.

**Why normalize vectors?**

With normalized vectors, inner product becomes equivalent to cosine similarity.

**What were retrieval results?**

Top-1 0.61, Top-3 0.85, and Top-5 0.93 over 100 evaluation queries.

## Scenario-based

**What happens to a jailbreak prompt?**

It is classified as jailbreak, blocked by the demonstrated integration policy, and does not proceed to retrieval.

**What happens to a safe prompt?**

It can proceed to retrieval, generation, and output validation.

## Project defense

**What was the biggest technical weakness?**

The suspicious class performed poorly, and the repository contains split-size, token-length, path, and embedding-model inconsistencies.

**What would you improve first?**

Establish one reproducible pipeline, deduplicate before splitting, resolve configuration conflicts, recalibrate suspicious-class handling, and evaluate on independently collected data.

---

# 30. Why Did You Choose These Approaches?

| Question | Evidence-based answer |
|---|---|
| Why this project? | It addresses security risks specific to healthcare LLM systems, including malicious prompts, jailbreaks, PHI, and unsafe outputs. |
| Why these datasets? | MedQuAD and PubMedQA provide medical language; MPIB provides security examples; synthetic data provides targeted PHI and jailbreak coverage. |
| Why MPIB? | It contains security metadata such as severity, scenarios, rules, and harm types. |
| Why MedQuAD? | It supplies medical question-answer content and safe examples. |
| Why PubMedQA? | It adds biomedical questions and evidence-oriented answers. |
| Why synthetic data? | Explicit security classes were needed for PHI and jailbreak examples. |
| Why five classes? | The repository standardizes safe, malicious, PHI, jailbreak, and suspicious behavior. |
| Why DistilBERT? | It is the verified selected model; performance-versus-speed motivation is reasonable but not formally documented. |
| Why Transformer? | Security classification requires contextual understanding of prompts. |
| Why weighted cross entropy? | The classes are imbalanced, especially suspicious versus safe. |
| Why Macro F1? | It gives equal importance to rare security classes. |
| Why not accuracy? | Accuracy can hide poor rare-class performance. |
| Why RAG? | It retrieves healthcare context instead of relying only on model memory. |
| Why embeddings? | They represent semantic meaning for similarity search. |
| Why BioBERT? | The repository uses a biomedical sentence-embedding model for healthcare retrieval. |
| Why FAISS? | It provides efficient vector similarity search. |
| Why IndexFlatIP? | Normalized embeddings make inner product equivalent to cosine similarity. |
| Why cosine similarity? | It compares semantic direction while reducing sensitivity to vector magnitude. |
| Why separate classifier and risk engine? | Classification provides one signal; policy decisions can combine multiple signals. |
| Why output validation? | Safe input does not guarantee safe, supported, or non-leaking output. |
| Why multiple security layers? | A single classifier cannot detect every security, clinical, privacy, and behavioural risk. |

---

# 31. My Role Defense

## What exactly did you do?

I worked on the dataset and machine-learning preparation pipeline: collecting and organizing datasets, cleaning source-specific data, converting sources to a common schema, creating security labels, performing EDA, preparing train/validation/test data, tokenizing prompts, training the DistilBERT classifier, evaluating it, and cross-verifying the saved results.

## What was your biggest contribution?

The strongest repository-supported contribution is the security classification dataset and training pipeline, including preprocessing, label mapping, weighted loss, evaluation, and validation.

## What was hardest?

The hardest technical issues were combining heterogeneous schemas, handling class imbalance, preserving source metadata, and distinguishing suspicious requests from clearly safe or malicious requests.

## How did you solve it?

I used source-specific preprocessing, a common schema, explicit label mapping, class-weighted cross entropy, macro F1 model selection, and saved validation artifacts.

## What would you improve?

I would make the pipeline fully reproducible, resolve configuration conflicts, perform global deduplication before splitting, recalibrate confidence, improve suspicious-class coverage, and evaluate on independently collected data.

## Did you build the entire system?

No. This folder verifies the dataset, classifier, knowledge-base, retrieval, and several demonstrations. The authoritative backend risk engine and broader production components are outside this folder.

---

# 32. Limitations

Verified or strongly indicated limitations include:

1. Suspicious-class F1 is only **0.4950**.
2. Security training data contains **1,404 duplicate prompts** in the EDA artifact.
3. Synthetic generation is unseeded.
4. Cross-source leakage is not fully verified.
5. Historical and current split sizes conflict.
6. Tokenization summaries conflict over maximum length.
7. Several notebooks use hardcoded paths from `Desktop\\major`.
8. The retrieval CSV referenced by notebooks is absent.
9. RAG notebooks reference different embedding models.
10. Perfect PHI and jailbreak metrics rely on small supports.
11. Confidence calibration is not verified.
12. RAG evaluation measures document retrieval, not clinical correctness.
13. Output validation uses only seven controlled cases.
14. Behavioural anomaly evaluation has no population-level precision or recall.
15. Model-level SHAP attribution is not verified.
16. Long prompts may be truncated at 256 tokens.
17. Real-world evolving attacks are not comprehensively represented.

---

# 33. Future Work

These are proposed improvements, not implemented features.

| Problem | Improvement | Benefit |
|---|---|---|
| Duplicate leakage risk | Globally deduplicate before splitting | More reliable evaluation |
| Suspicious-class weakness | Collect hard ambiguous examples | Better boundary detection |
| Synthetic bias | Add naturally occurring attack data | Better generalization |
| Confidence uncertainty | Calibrate probabilities | Better risk decisions |
| Fixed policy | Tune thresholds on validation data | Fewer false blocks and misses |
| Parent relationships | Use grouped splits by parent ID | Reduce related-example leakage |
| Token truncation | Add longer-context handling | Preserve more prompt information |
| RAG mismatch | Use one embedding model for indexing and querying | Correct vector-space compatibility |
| Retrieval limitations | Add reranking | Improve Top-K relevance |
| Limited evaluation | Add independent external test sets | Better generalization evidence |
| Evolving attacks | Add adversarial augmentation | Improve robustness |
| Monitoring | Add drift detection | Detect changing traffic patterns |
| Multilingual risk | Add multilingual security examples | Broader deployment coverage |

---

# 34. Complete End-to-End Flow

```text
User
  |
  v
React frontend
  |
  v
FastAPI API gateway
  |
  v
Security engine
  |
  v
DistilBERT classifier
  |
  v
Semantic, PHI, rule, and anomaly signals
  |
  v
Risk aggregator
  |
  v
Risk score
  |
  v
Decision engine
  |
  v
ALLOW / FLAG / BLOCK
  |
  v
If ALLOW:
Knowledge base
  |
  v
BioBERT-based embedding
  |
  v
FAISS IndexFlatIP
  |
  v
Top-K documents
  |
  v
Healthcare LLM
  |
  v
Output validator
  |
  v
User response

Logging
  |
  v
Feedback
  |
  v
Retraining
  |
  v
Drift detection
```

The final logging, feedback, retraining, and drift-detection loop is only partially verified in this folder.

---

# 35. Handwritten Interview Notes

## Page 1: Project Overview

- **Definition:** Healthcare LLM security platform.
- **What we did:** Built a security dataset and classifier pipeline.
- **Why:** Protect healthcare LLMs from unsafe inputs and outputs.
- **Details:** Five classes, DistilBERT, FAISS, RAG.
- **Interview line:** “My main contribution was the dataset-to-classifier pipeline.”
- **Follow-up:** What was your metric?
- **Answer:** Test macro F1 was 0.8673.

## Page 2: Problem Statement

- **Definition:** Healthcare LLMs face prompt, privacy, and safety risks.
- **What we did:** Classified prompts before generation.
- **Why:** Input filtering reduces unsafe downstream behavior.
- **Detail:** Safe, malicious, PHI, jailbreak, suspicious.
- **Follow-up:** Is classification enough?
- **Answer:** No, output validation and additional signals are also needed.

## Page 3: Architecture

- **Definition:** Multi-layer security architecture.
- **Flow:** React -> FastAPI -> Security engine -> risk decision.
- **Why:** Multiple signals are stronger than one classifier.
- **Follow-up:** Is every component implemented here?
- **Answer:** No, some are outside this folder or demonstrations.

## Page 4: My Role

- **Definition:** Dataset and ML preparation.
- **Work:** Cleaning, standardization, EDA, labels, tokenization, training, evaluation.
- **Why:** These determine model reliability.
- **Follow-up:** Did you build the complete product?
- **Answer:** No, the folder covers my ML preparation scope.

## Page 5: Datasets

- **Definition:** Raw and synthetic sources.
- **Details:** MedQuAD, PubMedQA, MPIB, three synthetic datasets.
- **Why:** Medical language plus security coverage.
- **Follow-up:** Which source supports RAG?
- **Answer:** MedQuAD and PubMedQA.

## Page 6: MPIB

- **Definition:** Security-oriented dataset.
- **Rows:** 7,759 train, 969 validation, 969 test.
- **Processing:** Severity-to-class mapping.
- **Follow-up:** What is severity 1-2?
- **Answer:** Suspicious.

## Page 7: MedQuAD

- **Definition:** Medical question-answer dataset.
- **Raw rows:** 48,480.
- **Clean rows:** 14,979.
- **Use:** Safe classifier data and knowledge base.
- **Follow-up:** Why fewer rows after cleaning?
- **Answer:** Duplicate and invalid question-answer filtering.

## Page 8: PubMedQA

- **Definition:** Biomedical QA dataset.
- **Rows:** 1,000.
- **Use:** Safe classifier data and knowledge base.
- **Follow-up:** What is special about it?
- **Answer:** It contains biomedical context and long answers.

## Page 9: Synthetic Data

- **Definition:** Programmatically generated examples.
- **Rows:** 1,005 general, 1,000 jailbreak, 1,000 PHI.
- **Why:** Targeted security coverage.
- **Limitation:** Random generation is not seeded.

## Page 10: Preprocessing

- **Operations:** Missing-value removal, duplicate removal, schema conversion.
- **Why:** Consistent model inputs.
- **Follow-up:** Was HTML removal verified?
- **Answer:** No.

## Page 11: EDA

- **Results:** Class, source, severity, PHI, length, missingness, duplicates.
- **Why:** Understand data quality and imbalance.
- **Follow-up:** Largest class?
- **Answer:** Safe.

## Page 12: Security Labels

- **Mapping:** safe 0, malicious 1, phi 2, jailbreak 3, suspicious 4.
- **Why:** Consistent model targets.
- **Follow-up:** Is this mapping in the saved model?
- **Answer:** Yes.

## Page 13: Dataset Combination

- **Definition:** Convert heterogeneous sources to a common schema.
- **Fields:** Prompt, context, response, labels, severity, source.
- **Risk:** IDs are not globally unique.
- **Follow-up:** Is `merge_datasets.py` active?
- **Answer:** No, it is empty.

## Page 14: Train/Validation/Test

- **Configuration:** `random_state=42`, nominal 80/10/10.
- **MPIB:** Existing splits reused.
- **Conflict:** Later processed counts differ from earlier artifacts.
- **Follow-up:** Is stratification verified?
- **Answer:** Not for all splits.

## Page 15: Data Leakage

- **Checks:** Duplicate and normalized prompt overlap checks.
- **Result:** No final normalized prompt intersections reported.
- **Limitation:** Original global leakage absence is not verified.
- **Follow-up:** Improvement?
- **Answer:** Global deduplication before splitting.

## Page 16: Tokenization

- **Model:** `distilbert-base-uncased`.
- **Max length:** 256 in implementation.
- **Inputs:** `input_ids`, `attention_mask`, `labels`.
- **Conflict:** Summary says 128.
- **Follow-up:** What happens to long prompts?
- **Answer:** They are truncated.

## Page 17: Transformer

- **Definition:** Contextual sequence model.
- **Flow:** Embeddings -> attention -> contextual representation.
- **Why:** Security meaning depends on context.
- **Follow-up:** What is an embedding?
- **Answer:** A learned vector representation.

## Page 18: Self-Attention

- **Formula:** $\operatorname{softmax}(QK^T/\sqrt{d_k})V$.
- **Meaning:** Tokens attend to relevant tokens.
- **Follow-up:** Why multiple heads?
- **Answer:** Different heads can capture different relationships.

## Page 19: DistilBERT

- **Details:** 6 layers, 768 hidden size, 12 heads, 30,522 vocabulary.
- **Output:** 5 classes.
- **Follow-up:** Why not claim formal model comparison?
- **Answer:** No comparison experiment is present.

## Page 20: Training

- **Epochs:** 4.
- **Learning rate:** `2e-5`.
- **Batch sizes:** 16 train, 32 evaluation.
- **Best checkpoint:** 1258.
- **Follow-up:** Why checkpoint 1258?
- **Answer:** It had the best validation macro F1.

## Page 21: Class Imbalance

- **Majority:** Safe.
- **Minority:** Suspicious.
- **Risk:** Accuracy hides rare-class errors.
- **Solution:** Weighted loss and macro F1.
- **Follow-up:** Weakest class?
- **Answer:** Suspicious.

## Page 22: Weighted Cross Entropy

- **Formula:** $w_c=N/(Kn_c)$.
- **Purpose:** Increase rare-class influence.
- **Follow-up:** What happens without weighting?
- **Answer:** The model may favour safe examples.

## Page 23: Evaluation Metrics

- **Accuracy:** 0.9389.
- **Macro F1:** 0.8673.
- **Weighted F1:** 0.9401.
- **Follow-up:** Which is more informative?
- **Answer:** Macro F1 for class-balanced security assessment.

## Page 24: Macro F1

- **Definition:** Average of per-class F1 values.
- **Why:** Equal class importance.
- **Weakness exposed:** Suspicious F1 0.4950.
- **Follow-up:** Why not weighted F1?
- **Answer:** Weighted F1 is dominated by safe support.

## Page 25: Confusion Matrix

- **Rows:** Actual.
- **Columns:** Predicted.
- **Diagonal:** Correct.
- **Off-diagonal:** Errors.
- **Follow-up:** Security concern?
- **Answer:** Suspicious-to-safe can allow risky prompts.

## Page 26: Error Analysis

- **Observed:** Safe-to-malicious and suspicious boundary errors.
- **Main weakness:** Suspicious class.
- **Interpretation:** Ambiguous prompts are difficult.
- **Follow-up:** How improve?
- **Answer:** Add hard negatives and real traffic examples.

## Page 27: Inference

- **Flow:** Prompt -> tokenizer -> model -> logits -> softmax -> class.
- **Confidence:** Highest class probability.
- **Limitation:** Calibration not verified.
- **Follow-up:** What is a logit?
- **Answer:** An unnormalized class score.

## Page 28: Security Engine

- **Role:** Combine classifier with other controls.
- **Classifier output:** Class and confidence.
- **Follow-up:** Is it the only signal?
- **Answer:** No.

## Page 29: Semantic Similarity

- **Definition:** Compare query and document meaning.
- **Use:** Retrieval.
- **Implementation:** Embeddings and FAISS.
- **Follow-up:** Is similarity clinical correctness?
- **Answer:** No.

## Page 30: PHI Detection

- **Definition:** Detect protected health information.
- **Evidence:** PHI class and output-validation checks.
- **Follow-up:** Is population-level PHI recall verified?
- **Answer:** No.

## Page 31: Rule Engine

- **Examples:** Chest pain block, prescription warn, hydration allow.
- **Status:** Notebook demonstration.
- **Follow-up:** Are these production thresholds verified here?
- **Answer:** No.

## Page 32: Behavioral Anomaly

- **Demo:** Three events, anomaly score 0.65, anomalous true.
- **Limitation:** No population precision or recall.
- **Follow-up:** Improvement?
- **Answer:** Evaluate against labelled user-session data.

## Page 33: SHAP

- **Definition:** Feature or factor attribution.
- **Status:** Decision-factor interface verified.
- **Limitation:** Model-level SHAP not verified.
- **Follow-up:** Why use explanations?
- **Answer:** To help analysts understand security decisions.

## Page 34: Risk Aggregator

- **Role:** Combine security signals.
- **Observed:** Safe low risk and jailbreak high risk.
- **Limitation:** Exact formula outside folder.
- **Follow-up:** Is the six-term formula verified?
- **Answer:** No.

## Page 35: Decision Engine

- **Outputs:** Allow, flag/review, block.
- **Verified policy:** Malicious, PHI, jailbreak block; safe and suspicious retrieve.
- **Risk:** Suspicious retrieval may be too permissive.
- **Follow-up:** Why?
- **Answer:** Suspicious F1 is only 0.4950.

## Page 36: Knowledge Base

- **Documents:** 15,979.
- **Sources:** MedQuAD and PubMedQA.
- **Schema:** Prompt, context, response, source.
- **Follow-up:** Are duplicates present?
- **Answer:** No duplicate prompts or full rows.

## Page 37: RAG

- **Flow:** Query -> embedding -> FAISS -> context -> LLM.
- **Why:** Ground generation in healthcare documents.
- **Follow-up:** Does retrieval guarantee correct answers?
- **Answer:** No.

## Page 38: Embeddings

- **Model:** `pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb`.
- **Shape:** 15,979 x 768.
- **Normalization:** Applied.
- **Follow-up:** Why normalize?
- **Answer:** To make inner product equivalent to cosine similarity.

## Page 39: FAISS

- **Index:** `IndexFlatIP`.
- **Vectors:** 15,979.
- **Dimension:** 768.
- **Follow-up:** What does IP mean?
- **Answer:** Inner product.

## Page 40: Cosine Similarity

- **Formula:** $\cos(\theta)=u\cdot v$ for normalized vectors.
- **Purpose:** Compare semantic direction.
- **Follow-up:** What if vectors are not normalized?
- **Answer:** Inner product is no longer equivalent to cosine similarity.

## Page 41: Top-K Retrieval

- **Top-1:** Best document.
- **Top-3:** Three candidates.
- **Top-5:** Five candidates.
- **Why:** More candidates can improve recall.
- **Follow-up:** Tradeoff?
- **Answer:** More irrelevant context may affect generation quality.

## Page 42: RAG Evaluation

- **Queries:** 100.
- **Top-1:** 0.6100.
- **Top-3:** 0.8500.
- **Top-5:** 0.9300.
- **Follow-up:** What does it measure?
- **Answer:** Expected-document retrieval, not clinical accuracy.

## Page 43: Output Validator

- **Checks:** PHI, unsafe output, unsupported answer.
- **Controlled results:** All listed detection rates were 1.0.
- **Limitation:** Seven test cases.
- **Follow-up:** Why validate output?
- **Answer:** Safe input can still produce unsafe output.

## Page 44: Logging

- **Evidence:** Saved evaluation and integration CSV artifacts.
- **Status:** Audit-style evidence exists.
- **Limitation:** Complete production logging not verified.
- **Follow-up:** What should be logged?
- **Answer:** Prompt ID, model decision, confidence, risk, action, and validator result.

## Page 45: Continuous Learning

- **Architecture:** Feedback -> retraining -> monitoring.
- **Status:** Full automated loop not verified.
- **Follow-up:** What is drift?
- **Answer:** A change in input or label distribution over time.

## Page 46: Safe Scenario

- **Flow:** Safe -> low risk -> retrieve -> validate -> answer.
- **Observed:** Approximately 0.990 confidence and 0.238 risk.
- **Follow-up:** Is retrieval always correct?
- **Answer:** No.

## Page 47: Attack Scenario

- **Flow:** Jailbreak -> high risk -> block.
- **Observed:** Approximately 0.998 confidence and 0.9595 risk.
- **Follow-up:** Does it reach FAISS?
- **Answer:** The demonstrated integration blocks it before retrieval.

## Page 48: Challenges

- **Challenges:** Heterogeneous schemas, class imbalance, ambiguous suspicious prompts, configuration conflicts.
- **Solution:** Common schema, weighted loss, macro F1, cross-verification.
- **Follow-up:** Biggest remaining issue?
- **Answer:** Suspicious-class performance and reproducibility inconsistencies.

## Page 49: Limitations

- **Main limitations:** Duplicate history, synthetic data, path conflicts, token-length conflict, RAG model conflict.
- **Interview line:** “I report these limitations rather than treating generated artifacts as proof.”
- **Follow-up:** Which metric exposes one limitation?
- **Answer:** Suspicious F1 of 0.4950.

## Page 50: Future Improvements

- **Priorities:** Global deduplication, reproducibility, calibration, hard negatives, external testing.
- **Benefit:** More reliable deployment decisions.
- **Follow-up:** First implementation?
- **Answer:** Consolidate the pipeline and remove configuration conflicts.

## Page 51: Interview Questions

- **Core questions:** Dataset sources, label mapping, leakage, DistilBERT, weighted loss, macro F1, FAISS, risk limitations.
- **Interview strategy:** State verified facts first, then clearly label interpretation.
- **Follow-up:** What should never be claimed?
- **Answer:** Unverified risk formulas, clinical RAG accuracy, or complete leakage-free training.

## Page 52: Final Revision Sheet

```text
Five classes:
safe, malicious, phi, jailbreak, suspicious

Model:
distilbert-base-uncased

Max length:
256 in implementation

Best checkpoint:
1258

Test accuracy:
0.9389

Test macro F1:
0.8673

Weakest class:
suspicious, F1 0.4950

Knowledge base:
15,979 documents

Embeddings:
15,979 x 768

FAISS:
IndexFlatIP

Retrieval:
Top-1 0.6100
Top-3 0.8500
Top-5 0.9300
```

The strongest interview answer is:

> I built and validated the healthcare security dataset and classifier pipeline. I standardized heterogeneous datasets, created five security classes, handled imbalance with weighted cross entropy, trained a DistilBERT classifier, evaluated it using macro F1, and connected the resulting security decision to retrieval and output-validation demonstrations. I also identified reproducibility, leakage, split, and configuration limitations that should be resolved before production deployment.
