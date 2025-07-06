![image](https://github.com/user-attachments/assets/70b03ea4-743f-484f-9560-5930d4e66ab3)

# 🤖 PR Code Reviewer with LangChain + GitHub + VectorDB

A  project that automates pull request (PR) code reviews using Large Language Models (LLMs), code embeddings, and GitHub integration. This app fetches PRs from GitHub, retrieves relevant context using a vector database of code embeddings, and generates insightful code review feedback using an LLM.

---

## 🚀 Features
* 🔍 **Automatic PR Fetching** from GitHub repositories
* 🧠 **Context-aware Code Reviews** using LLMs
* 🦮 **Code Embeddings with Vector Search** to retrieve relevant code chunks
* 📚 **LangChain Integration** for prompt orchestration
* ⚡ **Top-k Semantic Search** from a vector store to enrich PR diff analysis
* 📘 **Review Summaries** and **inline suggestions**

---

## 🧱 Architecture

```
          GitHub PR API
                ↓
         PR Metadata + Diff
                ↓
          Vector Store Query
     (Top-k most relevant code chunks)
                ↓
         ┌────────────────────────┐
         │   LangChain LLM        │
         │  Prompt Template       │
         └────────────────────────┘
                ↓
        Structured Review Feedback
                ↓
           Markdown Output / PR Comment
```

---

## 🛠️ Tech Stack

* **GitHub API** – Pull Request integration
* **LangChain** – Prompting and LLM chain management
* **OpenAI / Anthropic / LLM of choice** – For generating the review
* **FAISS & Pinecone** – Vector DB backend
* **Python** – Primary language

---

## 🏦 Project Structure

```
.
├── .env                          # Environment variables
├── main.py                       # Entry point
├── openai_wrapperpy              # OPEN API wrapper
├── vector_store.py               # Code embedding and retrieval logic
├── utils.py                      # Helper functions
├── README.md
└── requirements.txt
```
---

## ⚙️ Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/anmolnehru/IntelliReview.git
cd IntelliReview
```

### 2. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `secrets.yml` file with the following:

```env
GITHUB_TOKEN=ghp_XXXXXXXXXXXXXXXXXX
OPENAI_API_KEY=sk-XXXXXXXXXXXXXXXXXX
VECTOR_DB_PATH=./vectorstore/index.faiss
REPO_URL=https://github.com/anmolnehru/IntelliReview
```

### 4. Run the Application

```bash
python main.py pull $pr_number
```

You can also provide multiple PRs:

```bash
python main.py pull $pr_numbers 123 124 125
```

---

## 🧠 How It Works

1. **Embeddings Preprocessing**: Parses and embeds the codebase into a vector DB (FAISS/Chroma).
2. **PR Diff Fetching**: Fetches the latest PR diff and metadata.
3. **Top-k Retrieval**: Computes vector similarity between PR diff and stored embeddings to retrieve related context.
4. **LLM Prompting**: Passes the PR diff + top 5 chunks + file metadata into a LangChain prompt.
5. **Feedback Generation**: Outputs a markdown-formatted code review summary, which can optionally be posted back to the GitHub PR.

---

## 🔍 Example Prompt to the LLM

```text
You are a senior software engineer reviewing a pull request.

Here is the diff:
<DIFF_SNIPPET>

Here are 5 relevant code snippets from the codebase for context:
<RELEVANT_SNIPPETS>

Please provide:
- Summary of what this PR is doing
- High-level feedback
- Suggestions for improvement
- Any security/performance issues

Respond in markdown.
```

---

## 🧚️ Testing

```bash
pytest tests/
```

---

## 🧰 Embedding the Codebase

To embed your codebase initially:

```bash
python vector_store.py --index ./your_repo_path
```

Supports recursive file walking and language-specific tokenization (Python, JS, etc.).

---

## 📝 Output Format

Output is a Markdown summary that can be:

* Posted to the PR using the GitHub API
* Saved locally in a `.md` file
* Logged to console

---

## 🤝 Contributing

Pull requests are welcome! Please:

* Follow the project structure and naming conventions
* Include relevant tests
* Follow PEP8

---

## 💡 Ideas for Future Work

* Inline code comments via GitHub suggestions API
* Multi-agent review (style, logic, security reviewers)
* Web dashboard for reviewing and approving LLM responses
* Support for multiple repos and monorepos
* Streaming LLM responses

---

## 📄 License

MIT License – see `LICENSE` file for details.

---

## ✨ Acknowledgments

Built with ❤️ at Midnight BiriyaniLLM. Powered by LangChain, GitHub, and your favorite LLM.
