# ChatDB

## Overview

ChatDB is an interactive ChatGPT-like application designed to assist users in learning how to query data in various database systems, including SQL and NoSQL databases. Unlike traditional chatbots, ChatDB can not only suggest sample queries and understand natural language queries but also execute these queries directly in the database systems and display the results to the users.

## Features

- **Natural Language Query Understanding**: ChatDB can understand and process queries written in natural language, making it easier for users to interact with the system.
- **Sample Query Suggestions**: The application can suggest sample queries, including those that use specific language constructs (e.g., `GROUP BY` in SQL).
- **Database Query Execution**: ChatDB can execute queries in both SQL and NoSQL databases and display the results directly to the user.

## File Structures
### Subdirectories:

#### `app/`
- **Files:**
  - `main.py`
  - `config.py`
- **Subdirectories:**
  - `api/`
    - `routes.py`
  - `database/`
    - `mysql_manager.py`
    - `mongo_manager.py`
  - `services/`
    - `data_upload.py`
    - `db_explorer.py`
    - `nlp_processor.py`
    - `query_generator.py`

#### `frontend/`
- **Files:**
  - `.env.local`
  - `components.json`
  - `config.ts`
  - `next-env.d.ts`
  - `next.config.js`
  - `package.json`
  - `postcss.config.js`
  - `tailwind.config.ts`
  - `tsconfig.json`
- **Subdirectories:**
  - `app/`
    - `layout.tsx`
    - `page.tsx`
  - `components/`
    - `database-explorer.tsx`
    - `chat-layout.tsx`
    - `file-upload.tsx`
    - `theme-provider.tsx`
    - `ui/`
  - `contexts/`
    - `database-context.tsx`
  - `public/`
  - `hooks/`
    - `use-toast.ts`
  - `lib/`
    - `utils.ts`


## Setup Instructions

Follow these steps to set up and run the project:

### Env Setting
Rename `.env.example` to `.env` and replace the default env strings with your database connection strings.

### Backend Setup

1. **Install Dependencies**  
   Navigate to the root directory and install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Backend Server**  
   Run the following command to start the backend server:
   ```bash
   python -m app.main
   ```

### Frontend Setup

3. **Navigate to the Frontend Directory**  
   Change to the `frontend/` directory:
   ```bash
   cd frontend
   ```

4. **Install Frontend Dependencies**  
   Use npm to install the necessary packages:
   ```bash
   npm install
   ```

5. **Start the Frontend Development Server**  
   Start the frontend server in development mode:
   ```bash
   npm run dev
   ```

The application should now be running, with the backend accessible via its defined API endpoints and the frontend available on the development server.
