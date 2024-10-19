import pandas as pd
import json
from typing import List, Dict
import logging

# Add the AVAILABLE_MODELS dictionary
AVAILABLE_MODELS = {
    "Ministral 8B": "mistralai/ministral-8b",
    "Ministral 3B": "mistralai/ministral-3b",
    "Qwen2.5 7B Instruct": "qwen/qwen-2.5-7b-instruct",
    "Nvidia: Llama 3.1 Nemotron 70B Instruct": "nvidia/llama-3.1-nemotron-70b-instruct",
    "Google: Gemini 1.5 Flash-8B": "google/gemini-flash-1.5-8b",
    "Mistral Large": "mistralai/mistral-large",
    "OpenAI: GPT-4 Turbo Preview": "openai/gpt-4-turbo-preview",
    "Anthropic: Claude 3 Opus": "anthropic/claude-3-opus",
    "Anthropic: Claude 3 Sonnet": "anthropic/claude-3-sonnet",
    "Anthropic: Claude 3 Haiku": "anthropic/claude-3-haiku",
}

def generate_html_content(data: List[Dict], has_image_url: bool, theme: str, header_title: str) -> str:
    """Generate HTML content from the processed data."""
    # Precompute variables for the HTML content
    css_styles = get_css_styles()

    # Start building the HTML content using f-strings
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{header_title}</title>
    <!-- Responsive Design -->
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Include Bootstrap CSS for Responsive Design -->
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <!-- Include Google Fonts -->
    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:400,700&display=swap">
    <style>
        {css_styles}
    </style>
</head>
<body>
    <!-- Main Heading -->
    <h1 class="main-heading">{header_title}</h1>
    <!-- Search and Filters -->
    <div class="search-bar">
        <input type="text" id="searchInput" onkeyup="searchTable()" placeholder="Search..." class="form-control">
        <!-- Advanced Search -->
        <select id="searchColumn" class="form-control">
            <option value="all">All Columns</option>
            <option value="0">Letter</option>
            <option value="1">Prompt Name</option>
            <option value="2">Category</option>
            <option value="3">Prompt Text</option>
        </select>
    </div>
    <!-- Content Section -->
    <div id="content">
        <table class="table table-bordered table-hover">
            <thead>
                <tr>
                    <th class="sortable" onclick="sortTable(this, 0)">Letter</th>
                    <th class="sortable" onclick="sortTable(this, 1)">Prompt Name</th>
                    <th class="sortable" onclick="sortTable(this, 2)">Category</th>
                    <th class="sortable" onclick="sortTable(this, 3)">Prompt Text</th>
                    <th>Copy Prompt</th>
                </tr>
            </thead>
            <tbody>
    """

    # Generate content for each entry
    for item in data:
        letter = item.get('Letter', '')
        prompt_name = item.get('PromptName', '')
        category = item.get('Categories', '')
        prompt_text = item.get('PromptText', '').replace('\n', '<br>')

        # Sanitize prompt_text
        prompt_text = prompt_text.replace("fucked", "****")

        # Adjusted copyText function call to handle special characters
        sanitized_prompt_text = prompt_text.replace("`", "\\`").replace("\\", "\\\\").replace("\n", "\\n")

        html_content += f"""
                <tr>
                    <td>{letter}</td>
                    <td>{prompt_name}</td>
                    <td>{category}</td>
                    <td>{prompt_text}</td>
                    <td><button class="btn btn-primary copy-button" onclick="copyText(`{sanitized_prompt_text}`)">Copy</button></td>
                </tr>
        """

    # Close the table and add scripts
    html_content += """
            </tbody>
        </table>
    </div>
    <!-- Include jQuery and Bootstrap JS -->
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.5.2/dist/js/bootstrap.min.js"></script>
    <script>
        function copyText(text) {
            navigator.clipboard.writeText(text)
                .then(() => alert('Text copied!'))
                .catch(err => console.error('Error copying text: ', err));
        }

        function searchTable() {
            var input, filter, table, tr, td, i, txtValue;
            input = document.getElementById("searchInput");
            filter = input.value.toUpperCase();
            var columnSelect = document.getElementById("searchColumn");
            var columnIndex = columnSelect.value === "all" ? -1 : parseInt(columnSelect.value);

            table = document.querySelector("table");
            tr = table.getElementsByTagName("tr");

            for (i = 1; i < tr.length; i++) {
                tr[i].style.display = "none";
                if (columnIndex === -1) {
                    // Search all columns
                    var found = false;
                    td = tr[i].getElementsByTagName("td");
                    for (var j = 0; j < td.length - 1; j++) { // Exclude the Copy button column
                        if (td[j]) {
                            txtValue = td[j].textContent || td[j].innerText;
                            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                                found = true;
                                break;
                            }
                        }
                    }
                    if (found) tr[i].style.display = "";
                } else {
                    // Search specific column
                    td = tr[i].getElementsByTagName("td")[columnIndex];
                    if (td) {
                        txtValue = td.textContent || td.innerText;
                        if (txtValue.toUpperCase().indexOf(filter) > -1) {
                            tr[i].style.display = "";
                        }
                    }
                }
            }
        }

        function sortTable(header, columnIndex) {
            var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
            table = document.querySelector("table");
            switching = true;
            dir = "asc";

            while (switching) {
                switching = false;
                rows = table.rows;

                for (i = 1; i < (rows.length - 1); i++) {
                    shouldSwitch = false;
                    x = rows[i].getElementsByTagName("TD")[columnIndex];
                    y = rows[i + 1].getElementsByTagName("TD")[columnIndex];

                    if (dir == "asc") {
                        if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                            shouldSwitch = true;
                            break;
                        }
                    } else if (dir == "desc") {
                        if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                            shouldSwitch = true;
                            break;
                        }
                    }
                }

                if (shouldSwitch) {
                    rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                    switching = true;
                    switchcount++;
                } else {
                    if (switchcount == 0 && dir == "asc") {
                        dir = "desc";
                        switching = true;
                    }
                }
            }

            // Update sort direction indicators
            var headers = table.querySelectorAll('th');
            headers.forEach(h => h.classList.remove('asc', 'desc'));
            header.classList.add(dir);
        }
    </script>
</body>
</html>
    """
    return html_content

def get_css_styles() -> str:
    """Return CSS styles for the HTML content."""
    return """
    body {
        font-family: 'Roboto', sans-serif;
        padding: 20px;
        background-color: #f0f2f5;
        color: #333;
    }
    .main-heading {
        text-align: center;
        margin-bottom: 30px;
        color: #007bff;
    }
    .search-bar {
        margin-bottom: 20px;
        display: flex;
        gap: 10px;
    }
    .search-bar input {
        flex: 1;
    }
    .search-bar select {
        width: 200px;
    }
    table {
        background-color: #ffffff;
        border-collapse: collapse;
        width: 100%;
    }
    th, td {
        border: 1px solid #ddd;
        padding: 12px;
        text-align: left;
    }
    th {
        background-color: #007bff;
        color: white;
        cursor: pointer;
    }
    th:hover {
        background-color: #0056b3;
    }
    th.asc:after {
        content: ' ▲';
    }
    th.desc:after {
        content: ' ▼';
    }
    tr:nth-child(even) {
        background-color: #f2f2f2;
    }
    tr:hover {
        background-color: #ddd;
    }
    .copy-button {
        padding: 5px 10px;
        background-color: #28a745;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
    }
    .copy-button:hover {
        background-color: #218838;
    }
    """
