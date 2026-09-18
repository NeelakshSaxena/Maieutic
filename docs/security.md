# MentorAI — Security

## 1. Student Data
Student learning data is sensitive.
Protect:
- Conversations
- Performance
- Mistakes
- Notes
- Projects
- Personal information

## 2. Authentication
Use secure authentication (to be implemented).
Passwords must never be stored directly. 

*MVP Note: Currently, the system relies on mocked IDs. A robust identity provider (e.g., Auth0 or NextAuth) must be implemented before public exposure.*

## 3. Authorization
Every Student Brain query must verify student ownership. A student must never be able to request another student's data.

## 4. LLM Security
Treat model output as untrusted. Never allow model output to:
- Execute arbitrary commands
- Modify database schema
- Access secrets
- Execute SQL
- Modify authorization

*Implementation: The `LLMClient` uses strict Pydantic schemas. Invalid outputs are rejected. The model is strictly isolated from the database connection layer.*

## 5. Prompt Injection
User content must be considered untrusted.
Separate:
- System instructions
- Developer instructions
- Student content
- Retrieved memory

## 6. Secrets & Networking
Never commit:
- API keys (e.g., `LLM_API_KEY`)
- Database passwords
- RunPod tokens
- JWT secrets

Use environment variables via `.env`.

*Docker Note: In the local MVP, the API binds to port 8000 and PostgreSQL to 5432. Do not expose these ports to the public internet on a VPS without proper firewalling (e.g., UFW) and TLS termination.*

## 7. Training Data
User conversations must not enter model training automatically.
Require appropriate consent. Anonymize personal information before training.

## 8. Logging
Never log:
- Passwords
- Authentication tokens
- API keys
- Private student notes unnecessarily

## 9. Data Deletion
Students should eventually be able to delete:
- Sessions
- Brain data
- Account
- Training contribution

## 10. Principle
The model is not the security boundary. The backend is.