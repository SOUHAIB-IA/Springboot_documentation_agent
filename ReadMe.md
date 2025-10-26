# Autonomous Spring Boot Documentation Agent

<div align="center">
  <img src="https://path-to-your-logo-or-banner-image.png" alt="Project Banner" width="600"/>
  <br/><br/>
  <p>
    <b>An AI-powered multi-agent system that autonomously generates comprehensive technical documentation for Spring Boot projects.</b>
  </p>
  <p>
    Built with a real-time "Mission Control" desktop interface using Tauri and Next.js.
  </p>
  <br/>
    <img alt="License" src="https://img.shields.io/github/license/your-username/your-repo-name?style=for-the-badge">
    <img alt="Last Commit" src="https://img.shields.io/github/last-commit/your-username/your-repo-name?style=for-the-badge">
    <img alt="Repo Stars" src="https://img.shields.io/github/stars/your-username/your-repo-name?style=social">
</div>

---

## 🚀 Overview

This project is an advanced AI agent designed to automate the tedious process of writing and maintaining technical documentation for Java Spring Boot applications. It leverages a multi-agent architecture where AI agents collaborate to analyze a codebase, write documentation, review the output for accuracy, and assemble a final, polished Markdown document.

The entire process can be monitored in real-time through a sleek "Mission Control" desktop application, which provides a live feed of the agents' thoughts, actions, and the documentation as it's being built.

### ✨ Key Features

*   **🧠 Multi-Agent Collaboration:** A **Writer Agent** generates content, and a **Reviewer Agent** critiques it by comparing it against the source code, ensuring high accuracy.
*   **🖥️ Real-Time Mission Control UI:** A native desktop application built with **Tauri** and **Next.js** provides a live feed of the agent's reasoning process and the generated documentation.
*   **🔐 Local-First & Secure:** The application runs locally on your machine. Using Tauri, it can securely access local project folders without exposing them to the web.
*   **🤖 Autonomous Operation:** Simply point the agent at a project, and it handles the entire workflow: file discovery, analysis, generation, review, and final publishing.
*   **📝 Comprehensive Markdown Output:** Generates a single, well-organized document with a table of contents, code snippets, and logical sections for Entities, Services, Controllers, and more.
*   **🔄 Stateful & Resilient:** Uses a vector store for long-term memory and includes robust error handling for network issues, allowing it to continue its work on long-running tasks.

<br/>
<p align="center">
  <img src="https-your-screenshot-link-here.png" alt="Mission Control Screenshot" width="800"/>
  <br/>
  <em>The Mission Control dashboard in action.</em>
</p>
<br/>

---

## 🛠️ Tech Stack & Architecture

This project is a monorepo combining a Python back end with a TypeScript/React front end.

| Component      | Technology                                                                          |
| -------------- | ----------------------------------------------------------------------------------- |
| **Back End**   | **Python**, **FastAPI**, **LangChain** (with **LangGraph**), **Socket.IO**           |
| **LLM**        | **Google Gemini 1.5 Pro** (easily swappable for Groq, OpenAI, etc.)                 |
| **Front End**  | **Next.js**, **React**, **TypeScript**, **Tailwind CSS**, **Shadcn/ui**             |
| **Desktop App**| **Tauri** (Rust-based)                                                              |
| **Real-Time**  | **WebSockets** (via `python-socketio` and `socket.io-client`)                       |
| **Memory**     | **ChromaDB** (Vector Store) with **Sentence Transformers** (Local Embeddings)       |

### 🏛️ Architectural Flow

The system operates as a stateful graph where a manager orchestrates tasks, one file at a time.

```mermaid
graph TD
    subgraph Mission Control UI (Tauri/Next.js)
        A[1. User clicks 'Browse'] --> B{Selects Project Folder};
        B --> C[2. User clicks 'Launch Agent'];
        C --> D[3. UI emits 'start_agent' via WebSocket];
        D --> E{Listens for 'log' events};
        E --> F[4. Agent Feed is populated];
        G{Listens for 'final_result'} --> H[5. Documentation Panel is populated];
    end

    subgraph Back End (FastAPI & LangGraph)
        I[3. Socket.IO server receives 'start_agent'];
        I --> J[4. run_agent() orchestrator starts];
        J --> K[Discovers files];
        K --> L{Loop for each file};
        L --> M[5. Invoke LangGraph App];
        M --> N[6. Writer Agent];
        N --> O[7. Reviewer Agent];
        O --> P{Approved?};
        P -- No --> N;
        P -- Yes --> L;
        J --> Q[8. Publisher Agent assembles final doc];
    end
    
    subgraph Services
      R[LLM API (Gemini)];
      S[Local Vector Store];
    end

    subgraph Agent Tools
      T[File System Tools];
      U[Memory Tools];
    end

    N --> T;
    O --> T;
    N <--> R;
    O <--> R;
    N <--> U;
    U <--> S;
    
    style Mission Control UI fill:#222,stroke:#39c,stroke-width:2px
    style Back End fill:#222,stroke:#5c5,stroke-width:2px
```

---

## 🏁 Getting Started

Follow these instructions to set up and run the project locally.

### Prerequisites

*   **Node.js** (v18 or later)
*   **Python** (v3.11 or later)
*   **Rust & System Dependencies** for Tauri. Follow the [official Tauri guide](https://tauri.app/v1/guides/getting-started/prerequisites) for your operating system.
*   A **Google Gemini API Key**.

### 1. Back-End Setup

```bash
# Clone the repository
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

# Set up a Python virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`

# Install Python dependencies
pip install -r requirements.txt

# Create the environment file
cp .env.example .env
```

Now, open the `.env` file and add your Google Gemini API key:

```env
# .env
GOOGLE_API_KEY="your-google-api-key-goes-here..."
```

### 2. Front-End Setup

```bash
# Navigate to the front-end directory
cd springboot-doc-agent-frontend  # Or your front-end folder name

# Install Node.js dependencies
npm install
```

### 3. Running the Application

This application requires **two separate terminal sessions** to run concurrently.

**Terminal 1: Start the Back-End Server**

```bash
# From the project root directory
source .venv/bin/activate
python main.py
```
You should see Uvicorn start the server on `http://0.0.0.0:8000`.

**Terminal 2: Launch the Front-End Desktop App**

```bash
# From the front-end directory (e.g., springboot-doc-agent-frontend)
npm run tauri dev
```
After the initial compilation, the native desktop "Mission Control" window will appear.

---

## 📖 How to Use

1.  **Launch the application** using the two-terminal setup described above.
2.  In the Mission Control window, click **"Browse for Project..."**.
3.  A native file dialog will open. Select the **root folder** of the Spring Boot project you want to document.
4.  Click **"Launch Agent"**.
5.  **Watch the magic!** The "Agent Feed" will populate with the real-time thoughts and actions of the agents.
6.  Once the process is complete, the final documentation will appear in the "Documentation Preview" panel. You can then **copy** it or **download** it as a `.md` file.

---

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

Please see the `CONTRIBUTING.md` file for our code of conduct and the process for submitting pull requests.

### Areas for Contribution

*   **➕ More Tools:** Add new tools for the agents, such as a `dependency_analysis_tool` (reads `pom.xml`/`build.gradle`) or a `database_schema_tool`.
*   **🧠 Smarter Agents:** Improve the prompts to handle more complex code structures or edge cases.
*   **🎨 UI/UX Enhancements:** Add features to the Mission Control dashboard, like a "Diff Viewer" for re-runs or a project history panel.
*   **🧪 Better Testing:** Expand the test suite for both the front-end and back-end components.
*   **🌐 Broader Language Support:** Adapt the agent to document projects in other languages (e.g., Python/Django, Node.js/Express).

---

## 🗺️ Roadmap

*   [ ] **Project History & Diff Viewer:** Allow users to view past documentation runs and compare versions.
*   [ ] **Configuration Editor:** A UI to edit agent prompts and parameters directly from the Mission Control dashboard.
*   [ ] **Support for Other LLMs:** Add a settings panel to easily switch between Gemini, Groq, and local models.
*   [ ] **Automated Diagram Generation:** Integrate a tool that generates Mermaid.js diagrams (e.g., class or sequence diagrams) from the code.

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## Acknowledgment

This project stands on the shoulders of giants. A big thank you to the teams behind LangChain, Tauri, FastAPI, and all the other open-source libraries that made this possible.