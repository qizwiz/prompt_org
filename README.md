# Collaborative Dynamics - Custom Prompt Generator

![Collaborative Dynamics Logo](image.png)

## 🧠 Overview
The **Custom Prompt Generator** is a web application designed to generate and manage AI prompts. Built with Python, Streamlit, and other essential tools, this project allows users to organize prompts efficiently and interact with AI APIs for streamlined prompt generation.

## 🚀 Features
- **Admin Interface:** Upload and manage prompts.
- **User Interface:** Generate prompts dynamically based on user input.
- **File Support:** Import prompts via CSV/JSON and save them in a structured format.
- **API Integration:** Connect to OpenRouter API for AI-driven prompt generation.
- **Dark Mode Support:** Toggle-friendly UI with light/dark modes.

---

## 📁 Project Structure
```
project-root/
├── main.py             # Streamlit application entry point
├── utils.py            # Helper functions for file processing and validation
├── test_main.py        # Unit tests for key functionalities
├── requirements.txt    # Python dependencies
├── image.png           # Company logo (used in README)
├── prompt_data.parquet # Stored prompts (auto-generated)
└── .gitignore          # Ignored files (e.g., logs, lockfiles)
```

---

## 🔧 Setup Instructions
### 1. **Prerequisites**
Ensure you have the following installed:
- Python 3.8+
- Virtual Environment Manager

### 2. **Clone the Repository**
```bash
git clone https://github.com/qizwiz/prompt_org.git
cd prompt_org
```

### 3. **Setup Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # For Windows use `venv\Scripts\activate`
```

### 4. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 5. **Run the Application**
```bash
streamlit run main.py
```

The application will be available at `http://localhost:8501`.

---

## 🧪 Testing
To run the unit tests:
```bash
pytest test_main.py
```

---

## 🛠️ Key Functionalities
### Admin Interface
- Upload CSV/JSON files to manage prompts.
- Data validation ensures correct schema.

### User Interface
- Select categories, topics, and desired AI models.
- Generate prompts dynamically using OpenRouter AI API.

---

## 📜 Example Prompt Generation Workflow
1. **Select Category:** Choose a category (e.g., Marketing).
2. **Enter Topic:** Define a specific topic (e.g., "Social Media Campaign").
3. **Set Parameters:** Choose model, tokens, and creativity.
4. **Generate Prompts:** Retrieve and preview multiple prompts.

---

## 🖼️ Logo Usage
The **Collaborative Dynamics** logo has been incorporated to align branding across the project. Use the `image.png` file wherever needed.

---

## 🤝 Contributions
We welcome contributions! Follow these steps:
1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature`.
3. Commit your changes: `git commit -m "Add new feature"`.
4. Push to the branch: `git push origin feature/your-feature`.
5. Open a pull request.

---

## 📄 License
This project is licensed under the MIT License.

---

## 📞 Contact
For inquiries or support, reach out to [Collaborative Dynamics](mailto:support@collaborativedynamics.com).
