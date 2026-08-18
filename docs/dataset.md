You'll likely combine multiple sources.
 
Dataset	Best for	Size
 
SocraticQA	Socratic questioning and guided tutoring	Thousands of examples
OpenTutor	AI tutoring conversations	Large
MathInstruct	Step-by-step math reasoning	~260k examples
NuminaMath	Mathematical reasoning	Millions of examples
OpenThoughts	Chain-of-thought style reasoning (training)	Large
UltraFeedback	Evaluating good vs. bad responses	~60k+
LMSYS Chat-1M	Real tutoring conversations mixed with general chat	~1M chats
WildChat	Real-world educational conversations	Millions
Alpaca / Dolly	Instruction following	Tens of thousands
 
 
Coding-specific
 
CodeContests — Programming contest problems with solutions.
 
APPS — Coding interview and competitive programming questions.
 
HumanEval — Code generation and verification.
 
MBPP — Beginner programming tasks.
 
 
These are excellent if your tutor focuses on DSA, interviews, or programming.
 
For "unlock next step only if correct"
 
This is the tricky part. There isn't a widely used dataset that exactly matches your idea.
 
You'll probably need to generate or collect examples in the form:
 
Question
 
↓
 
Learning Plan
□ Step 1
□ Step 2
□ Step 3
 
↓
 
Student Response
 
↓
 
Verifier
Correct / Incorrect
 
↓
 
Hint
 
↓
 
Retry
 
↓
 
Next Step
 
That interaction format is your unique contribution and could become your proprietary dataset.
 
Educational datasets
 
ASSISTments — Student answers, hints, and knowledge tracing.
 
EdNet — Large-scale student learning interactions.
 
Khan Academy (public research resources) — Exercise and tutoring data.
 
Riiid! Answer Correctness Prediction — Millions of student responses.
 
 
These aren't chat datasets, but they're valuable for modeling mastery and deciding when a learner is ready to move on.
 
A good starting stack
 
If I were building this today, I'd combine:
 
OpenTutor → tutoring dialogue style.
 
SocraticQA → questioning technique.
 
MathInstruct → reasoning decomposition.
 
APPS → programming education.
 
ASSISTments/EdNet → mastery and progression.
 
 
Then I'd fine-tune or preference-train a model to follow rules like:
 
Never reveal the complete solution unless explicitly requested.
 
Break problems into prerequisite checkpoints.
 
Verify each response.
 
Give progressively stronger hints.
 
Don't unlock the next checkpoint until the current one is understood.
 
Encourage the student to explain their reasoning, not just provide the final answer.
 
 
That last interaction pattern is where your idea stands out. Most current tutoring models are optimized to answer well; yours would be optimized to teach well.