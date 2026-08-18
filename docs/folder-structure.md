mentorai/
│
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── docker-compose.yml
├── Makefile
│
├── docs/
│   ├── PRD.md
│   ├── SYSTEM_ARCHITECTURE.md
│   ├── AI_ARCHITECTURE.md
│   ├── STUDENT_BRAIN.md
│   ├── KNOWLEDGE_GRAPH.md
│   ├── MISCONCEPTION_SYSTEM.md
│   ├── TUTORING_PROTOCOL.md
│   ├── MODEL_TRAINING.md
│   ├── MODEL_EVALUATION.md
│   ├── DATA_PIPELINE.md
│   ├── API.md
│   ├── DATABASE.md
│   ├── SECURITY.md
│   ├── DEPLOYMENT.md
│   └── ROADMAP.md
│
├── apps/
│   │
│   ├── web/
│   │   ├── app/
│   │   │   ├── (auth)/
│   │   │   ├── dashboard/
│   │   │   ├── tutor/
│   │   │   ├── brain/
│   │   │   ├── progress/
│   │   │   ├── concepts/
│   │   │   ├── settings/
│   │   │   └── api/
│   │   │
│   │   ├── components/
│   │   │   ├── tutor/
│   │   │   ├── checklist/
│   │   │   ├── brain/
│   │   │   ├── mastery/
│   │   │   └── ui/
│   │   │
│   │   ├── hooks/
│   │   ├── lib/
│   │   ├── types/
│   │   ├── public/
│   │   └── package.json
│   │
│   └── api/
│       ├── app/
│       │   ├── main.py
│       │   │
│       │   ├── api/
│       │   │   ├── auth.py
│       │   │   ├── sessions.py
│       │   │   ├── tutoring.py
│       │   │   ├── students.py
│       │   │   ├── concepts.py
│       │   │   ├── brain.py
│       │   │   ├── mastery.py
│       │   │   ├── misconceptions.py
│       │   │   └── analytics.py
│       │   │
│       │   ├── agents/
│       │   │   ├── planner.py
│       │   │   ├── checkpoint.py
│       │   │   ├── verifier.py
│       │   │   ├── hint.py
│       │   │   ├── misconception.py
│       │   │   ├── mastery.py
│       │   │   └── orchestrator.py
│       │   │
│       │   ├── models/
│       │   │   ├── user.py
│       │   │   ├── session.py
│       │   │   ├── checkpoint.py
│       │   │   ├── concept.py
│       │   │   ├── mastery.py
│       │   │   ├── misconception.py
│       │   │   └── interaction.py
│       │   │
│       │   ├── schemas/
│       │   ├── services/
│       │   │   ├── tutoring_service.py
│       │   │   ├── brain_service.py
│       │   │   ├── mastery_service.py
│       │   │   ├── misconception_service.py
│       │   │   └── memory_service.py
│       │   │
│       │   ├── repositories/
│       │   ├── prompts/
│       │   │   ├── planner/
│       │   │   ├── verifier/
│       │   │   ├── hints/
│       │   │   ├── misconceptions/
│       │   │   └── brain/
│       │   │
│       │   ├── core/
│       │   ├── db/
│       │   └── workers/
│       │
│       ├── tests/
│       ├── alembic/
│       ├── pyproject.toml
│       └── Dockerfile
│
├── packages/
│   │
│   ├── shared-types/
│   │   ├── schemas/
│   │   └── README.md
│   │
│   ├── tutoring-protocol/
│   │   ├── checkpoint_schema.json
│   │   ├── verification_schema.json
│   │   ├── hint_schema.json
│   │   ├── mastery_schema.json
│   │   └── README.md
│   │
│   └── ui/
│       └── ...
│
├── ai/
│   │
│   ├── prompts/
│   │   ├── planner/
│   │   ├── checkpoint/
│   │   ├── verifier/
│   │   ├── hint/
│   │   ├── misconception/
│   │   └── mastery/
│   │
│   ├── agents/
│   │   ├── planner/
│   │   ├── verifier/
│   │   ├── tutor/
│   │   ├── hint_generator/
│   │   └── brain/
│   │
│   ├── evaluation/
│   │   ├── datasets/
│   │   ├── benchmarks/
│   │   ├── evaluators/
│   │   ├── regression/
│   │   └── reports/
│   │
│   └── configs/
│       ├── development.yaml
│       ├── staging.yaml
│       └── production.yaml
│
├── training/
│   │
│   ├── datasets/
│   │   ├── raw/
│   │   │   ├── mathinstruct/
│   │   │   ├── numinamath/
│   │   │   ├── gsm8k/
│   │   │   ├── math/
│   │   │   ├── apps/
│   │   │   ├── mbpp/
│   │   │   ├── codecontests/
│   │   │   ├── socraticqa/
│   │   │   ├── opentutor/
│   │   │   ├── ednet/
│   │   │   └── assistments/
│   │   │
│   │   ├── processed/
│   │   ├── normalized/
│   │   ├── filtered/
│   │   ├── deduplicated/
│   │   └── final/
│   │
│   ├── preprocessing/
│   │   ├── download.py
│   │   ├── normalize.py
│   │   ├── clean.py
│   │   ├── deduplicate.py
│   │   ├── quality_filter.py
│   │   ├── concept_extract.py
│   │   └── build_training_set.py
│   │
│   ├── sft/
│   │   ├── train.py
│   │   ├── config.yaml
│   │   └── dataset.py
│   │
│   ├── preference/
│   │   ├── prepare_dpo.py
│   │   ├── train_dpo.py
│   │   └── config.yaml
│   │
│   ├── evaluation/
│   │   ├── tutoring_eval.py
│   │   ├── verifier_eval.py
│   │   ├── hint_eval.py
│   │   ├── misconception_eval.py
│   │   └── benchmark.py
│   │
│   ├── configs/
│   │   ├── qlora_14b.yaml
│   │   ├── lora_14b.yaml
│   │   └── dpo_14b.yaml
│   │
│   └── README.md
│
├── student-data/
│   │
│   ├── schemas/
│   │   ├── student.json
│   │   ├── concept.json
│   │   ├── mastery.json
│   │   ├── misconception.json
│   │   ├── interaction.json
│   │   └── session.json
│   │
│   ├── knowledge-graph/
│   │   ├── concepts/
│   │   ├── relationships/
│   │   └── curriculum/
│   │
│   └── anonymization/
│       └── sanitize.py
│
├── infrastructure/
│   │
│   ├── docker/
│   ├── postgres/
│   ├── redis/
│   ├── qdrant/
│   ├── minio/
│   ├── monitoring/
│   │   ├── prometheus/
│   │   └── grafana/
│   └── runpod/
│       ├── training/
│       ├── inference/
│       └── README.md
│
├── scripts/
│   ├── setup.sh
│   ├── dev.sh
│   ├── test.sh
│   ├── seed_db.py
│   └── evaluate.py
│
├── tests/
│   │
│   ├── integration/
│   ├── e2e/
│   ├── agents/
│   ├── tutoring/
│   ├── student_brain/
│   └── model/
│
└── .github/
    └── workflows/
        ├── test.yml
        ├── lint.yml
        ├── build.yml
        └── deploy.yml