# MentorAI Socratic Tutoring: Dataset, Pipeline, and Evaluation Report

## 1. Dataset
The foundational training dataset for MentorAI's pedagogical modeling originates primarily from the `socrateach` data source, alongside specifically curated domains such as Mathematics (MathDial), Programming, and Data Structures & Algorithms. 

**Dataset Composition (Experiment #2 / Phase 1.5):**
- **Size:** 13,859 rigorously cleaned multi-turn interactions.
- **Format:** The data is structured as multi-turn instructional interactions in JSONL format, mapped into the native ChatML schema (`system`, `user`, `assistant`).
- **Objective:** Unlike traditional instructional datasets optimized for direct question answering, this dataset is formulated to enforce pedagogical constraints, ensuring the AI orchestrates learning via guided Socratic questioning without premature "answer leakage."

## 2. Dataset Processing & Training Pipeline
The raw conversational Q&A data naturally tends toward direct answer generation. Thus, a rigorous processing and formatting pipeline is executed to shape the model’s Socratic behavior.

**Preprocessing Pipeline:**
1. **Cleaning & Quality Filtering:** Raw examples are filtered for safety, quality, and pedagogical relevance.
2. **Socratic Transformation:** The responses are analyzed and reformatted to prevent answer leakage, emphasizing corrections and guided hints over direct solutions.
3. **ChatML Formatting:** Interactions are formatted strictly to Qwen3's native template to prevent catastrophic destruction of pre-trained conversational abilities.
4. **Tokenization & Collation:** The pipeline leverages `DataCollatorForCompletionOnlyLM`. This masks the loss for any tokens preceding the `<|im_start|>assistant` tag. Consequently, the model is strictly penalized based on its generated hints and verifications, not on the user prompts.

**Model Architecture & QLoRA Configuration:**
- **Base Model:** `Qwen/Qwen3-8B`
- **Method:** QLoRA (4-bit precision) utilizing the Unsloth framework to optimize VRAM utilization on a single GPU.
- **LoRA Parameters:** Target modules span across `q, k, v, o, gate, up, down` projections with a Rank of 16 and Alpha of 32. 

## 3. Model/LoRA Metrics - Results and Discussions
The efficacy of the LoRA adapter is gauged via offline behavioral evaluation rather than simple perplexity loss.

- **Primary Metric (Answer Leakage Rate):** The central safety metric evaluates the percentage of responses where the tutor inadvertently leaks the final answer, bypassing the required learning checkpoint.
- **Experiment 01 (Contradictory Socratic Supervision):** The model ran for 2586 steps. The base checks passed successfully.
- **Experiment 02 / Phase 2A:** Trained on the 13,859 datasets for 1 epoch. While the sanity checks passed (the adapter loaded efficiently and maintained coherent text generation), large-scale programmatic behavioral evaluations are still pending. 
- **Behavioral Audits:** Manual audits on subsets like `socrateach_4391` demonstrate that the multi-agent decoupled architecture successfully restricts the LLM from providing straightforward answers. The `Verifier Agent` validates against criteria deterministically, while the `Hint Agent` effectively scales assistance based on failure counts.

## 4. What Went Wrong
During data exploration and processing, a significant structural anomaly was identified in the training conversational schema.

**Consecutive Roles Investigation:**
- **Issue:** The dataset contained sequential utterances from the same speaker, breaking the standard alternating `User -> Assistant -> User` conversational structure.
- **Scale:** In the MathDial subset (1,035 conversations), 140 conversations (13.5%) were corrupted. 
- **Specific Anomaly:** There were exactly 219 instances of **Consecutive Assistant Pairs**. The maximum consecutive run length was 8 assistant messages in a row. 
- **Impact:** This structural flaw injects fragmented `<think>` tokens and duplicate tags (e.g., `(focus)`, `(generic)`), confusing the instruction-tuning process. Standard completion-collators expect discrete conversational turns; consecutive assistant messages corrupt the ChatML parsing, leading to suboptimal attention mechanisms and unexpected generation halting during SFT.

## 5. Alternative Flow and Improvements
To address the current limitations and scale the tutoring efficacy, several alternative pathways and systemic improvements can be implemented:

**1. Advanced Dataset Pruning (Pipeline Fix)**
- **Improvement:** Introduce a strict normalization script during the parsing phase to merge or explicitly discard consecutive assistant messages. This ensures the conversational DAG maintains absolute alternating multi-turn structures.

**2. Direct Preference Optimization (DPO)**
- **Alternative Flow:** Standard Supervised Fine-Tuning (SFT) is somewhat blunt for teaching nuanced pedagogical restraint. Transitioning a secondary phase to DPO will explicitly train the model by presenting it with a "correct Socratic hint" vs. a "rejected leaked answer." This drastically drives down the Answer Leakage Rate.

**3. Semantic RAG Integration (Student Brain Contextualization)**
- **Improvement:** Although the PostgreSQL "Student Brain" currently tracks mastery numerically via Exponential Moving Averages (EMA), the LLM context is largely stateless. Implementing a semantic vector store (e.g., Qdrant) to retrieve past session interactions and inject them directly into the Planner and Hint Agents' prompts will provide deeply personalized, historically grounded scaffolding.

**4. End-to-End Orchestration Optimization**
- **Improvement:** The decoupled architecture (Planner -> Verifier -> Hint) drastically reduces hallucination but inherently increases latency due to sequential LLM inference loops. An alternative flow would involve consolidating the Verifier and Hint generation into a singular structured JSON response, significantly reducing Time-to-First-Token (TTFT) while maintaining strict verification criteria.
