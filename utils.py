import json
import random
import re
from typing import Any, Dict, List

import pandas as pd


def process_csv(
    df: pd.DataFrame, has_image_url: bool, upload_option: str
) -> List[Dict[str, Any]]:
    if "Option 1" in upload_option:  # Allow partial matching
        column_mapping = {
            "Letter": "Letter",
            "Prompt Name": "PromptName",
            "Category": "Categories",
            "Prompt Text": "PromptText",
        }
        required_columns = ["Letter", "PromptName", "Categories", "PromptText"]
    else:
        column_mapping = {
            "Letter": "Letter",
            "Persona Name": "PersonaName",
            "Category": "Categories",
            "ImageURL": "ImageURL",
            "Prompt Text": "PromptText",
        }
        required_columns = [
            "Letter",
            "PersonaName",
            "Categories",
            "ImageURL",
            "PromptText",
        ]

    df = df.rename(columns=column_mapping)

    # Validate renaming
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns after renaming: {missing_columns}")

    return df.to_dict(orient="records")


def process_json(
    data: List[Dict[str, Any]], has_image_url: bool, upload_option: str
) -> List[Dict[str, Any]]:
    if upload_option == "Option 1: [Letter, Prompt Name, Category, Prompt Text]":
        required_keys = ["Letter", "PromptName", "Categories", "PromptText"]
    else:
        required_keys = [
            "Letter",
            "PersonaName",
            "Categories",
            "ImageURL",
            "PromptText",
        ]

    processed_data = []
    for item in data:
        processed_item = {}
        for key in required_keys:
            processed_item[key] = item.get(key, "")

        for key in required_keys:
            if processed_item.get(key, "") == "":
                raise ValueError(
                    f"Missing value for key '{key}' in item: {processed_item}"
                )

        processed_data.append(processed_item)

    return processed_data


def generate_html_content(
    data: List[Dict[str, Any]], has_image_url: bool, theme: str, header_title: str
) -> str:
    css_styles = get_css_styles()
    search_column_0 = "Persona Name" if has_image_url else "Letter"
    search_column_2 = 2
    search_column_3 = 3

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{header_title}</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:400,700&display=swap">
<style>
{css_styles}
</style>
</head>
<body>
<button id="darkModeToggle" class="btn btn-secondary">Toggle Dark Mode</button>
<h1 class="main-heading">{header_title}</h1>
<div class="search-bar">
<input type="text" id="searchInput" onkeyup="searchTable()" placeholder="Search..." class="form-control">
<select id="searchColumn" class="form-control">
<option value="all">All Columns</option>
<option value="0">{search_column_0}</option>
<option value="{search_column_2}">Categories/Tags</option>
<option value="{search_column_3}">Prompt Text</option>
</select>
</div>
<nav id="navigation">
"""
    letters = sorted(set(item["Letter"].upper() for item in data if item["Letter"]))
    for letter in letters:
        html_content += f'<a href="#section-{letter}">{letter}</a> '

    html_content += """
<button type="button" data-toggle="modal" data-target="#categoriesModal">Categories</button>
</nav>
<div id="content">
"""
    data_by_letter = {}
    for item in data:
        letter = item["Letter"].upper()
        if letter not in data_by_letter:
            data_by_letter[letter] = []
        data_by_letter[letter].append(item)

    entry_id = 1
    categories_dict = {}

    for letter in letters:
        html_content += (
            f'<div class="letter-section" id="section-{letter}"><h2>{letter}</h2>\n'
        )
        html_content += """
<table class="table table-bordered table-hover">
<thead>
<tr>
"""
        if has_image_url:
            headers = [
                "Persona Name",
                "Image",
                "Categories/Tags",
                "Prompt Text",
                "Copy Prompt",
            ]
        else:
            headers = [
                "Letter",
                "Prompt Name",
                "Categories/Tags",
                "Prompt Text",
                "Copy Prompt",
            ]
        for idx, column in enumerate(headers):
            if column in ["Persona Name", "Prompt Name", "Prompt Text"]:
                html_content += f'<th class="sortable" onclick="sortTable(this, {idx})">{column}</th>\n'
            else:
                html_content += f"<th>{column}</th>\n"
        html_content += """
</tr>
</thead>
<tbody>
"""

        for item in data_by_letter[letter]:
            if has_image_url:
                name_field = item.get("PersonaName", "")
                letter_field = item.get("Letter", "")
            else:
                name_field = item.get("PromptName", "")
                letter_field = item.get("Letter", "")

            image_url = item.get("ImageURL", "") if has_image_url else ""
            categories = item.get("Categories", "")
            prompt_text = item.get("PromptText", "").replace("\n", "<br>")
            categories_list = [
                cat.strip() for cat in categories.split(",") if cat.strip()
            ]
            for category in categories_list:
                if category not in categories_dict:
                    categories_dict[category] = []
                categories_dict[category].append(
                    {"id": f"entry-{entry_id}", "name": name_field}
                )

            html_content += f"""
<tr id="entry-{entry_id}">
"""
            if not has_image_url:
                html_content += f"    <td>{letter_field}</td>\n"
            html_content += f"    <td>{name_field}</td>\n"
            if has_image_url:
                if image_url:
                    html_content += (
                        f'    <td><img src="{image_url}" alt="{name_field}"></td>\n'
                    )
                else:
                    html_content += "    <td></td>\n"
            html_content += '    <td class="category-tags">'
            for idx_, category in enumerate(categories_list):
                html_content += f'<a href="#" onclick="showEntriesByCategory(`{category}`);">{category}</a>'
                if idx_ != len(categories_list) - 1:
                    html_content += ", "
            html_content += "</td>\n"
            html_content += f'    <td class="prompt-text">{prompt_text}</td>\n'
            html_content += f'    <td><button class="btn btn-primary copy-button" onclick="copyText(this)" data-prompt="{entry_id}">Copy</button></td>\n'
            html_content += "</tr>\n"

            entry_id += 1

        html_content += """
</tbody>
</table>
</div>
"""

    html_content += """
<div class="modal fade" id="categoriesModal" tabindex="-1" role="dialog" aria-labelledby="categoriesModalLabel" aria-hidden="true">
  <div class="modal-dialog modal-dialog-scrollable" role="document">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title"><span id="modalTitle">Categories</span></h5>
        <button type="button" class="close" data-dismiss="modal" aria-label="Close" onclick="backToCategories()">
          <span aria-hidden="true">&times;</span>
        </button>
      </div>
      <div class="modal-body">
        <ul class="category-list" id="categoryList">
"""
    for category in sorted(categories_dict.keys()):
        html_content += f'<li><a href="#" onclick="showEntriesByCategory(`{category}`);">{category}</a></li>\n'
    html_content += """
        </ul>
        <div id="entriesByCategory" style="display:none;">
          <h5 id="selectedCategory"></h5>
          <ul class="entry-list" id="entryList">
          </ul>
        </div>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" onclick="backToCategories()">Back</button>
        <button type="button" class="btn btn-secondary" data-dismiss="modal" onclick="backToCategories()">Close</button>
      </div>
    </div>
  </div>
</div>
</div>
"""

    html_content += """
<script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@4.5.2/dist/js/bootstrap.min.js"></script>
<script>
var categories = {};
"""

    categories_json = json.dumps(categories_dict)
    html_content += f"categories = {categories_json};\n"

    html_content += """
function copyText(button) {
    var row = button.closest('tr');
    var promptText = row.querySelector('.prompt-text').innerText;
    navigator.clipboard.writeText(promptText)
        .then(() => {
            button.textContent = 'Copied!';
            setTimeout(() => {
                button.textContent = 'Copy';
            }, 2000);
        })
        .catch(err => console.error('Error copying text: ', err));
}

function searchTable() {
    var input, filter, tableContainers, tr, td, i, txtValue;
    input = document.getElementById("searchInput");
    filter = input.value.toUpperCase();
    var columnSelect = document.getElementById("searchColumn");
    var columnIndex = columnSelect.value;

    tableContainers = document.querySelectorAll(".letter-section");
    tableContainers.forEach(function(container) {
        var tables = container.getElementsByTagName("table");
        if (tables.length > 0) {
            tr = tables[0].getElementsByTagName("tr");
            for (i = 1; i < tr.length; i++) {
                tr[i].style.display = "none";
                var tdArray = tr[i].getElementsByTagName("td");
                if (columnIndex === "all") {
                    for (var j = 0; j < tdArray.length; j++) {
                        td = tdArray[j];
                        if (td) {
                            txtValue = td.textContent || td.innerText;
                            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                                tr[i].style.display = "";
                                break;
                            }
                        }
                    }
                } else {
                    var idx = parseInt(columnIndex);
                    td = tdArray[idx];
                    if (td) {
                        txtValue = td.textContent || td.innerText;
                        if (txtValue.toUpperCase().indexOf(filter) > -1) {
                            tr[i].style.display = "";
                        }
                    }
                }
            }
        }
    });
}

function sortTable(header, columnIndex) {
    var table = header.closest('table');
    var tbody = table.querySelector('tbody');
    var rows = Array.from(tbody.rows);
    var ascending = header.classList.contains('asc');
    rows.sort(function(a, b) {
        var aText = a.cells[columnIndex].innerText.trim().toUpperCase();
        var bText = b.cells[columnIndex].innerText.trim().toUpperCase();
        if (aText < bText) return ascending ? -1 : 1;
        if (aText > bText) return ascending ? 1 : -1;
        return 0;
    });
    rows.forEach(function(row) {
        tbody.appendChild(row);
    });
    header.classList.toggle('asc', !ascending);
    header.classList.toggle('desc', ascending);
}

function showEntriesByCategory(category) {
    document.getElementById('entriesByCategory').style.display = 'block';
    document.getElementById('selectedCategory').innerText = category;
    var entryList = document.getElementById('entryList');
    entryList.innerHTML = '';
    var entries = categories[category];
    entries.forEach(function(entry) {
        var li = document.createElement('li');
        var a = document.createElement('a');
        a.href = "#";
        a.innerText = entry.name;
        a.addEventListener('click', function(e) {
            e.preventDefault();
            $('#categoriesModal').modal('hide');
            $('#categoriesModal').on('hidden.bs.modal', function () {
                var target = document.getElementById(entry.id);
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
                $('#categoriesModal').off('hidden.bs.modal');
            });
        });
        li.appendChild(a);
        entryList.appendChild(li);
    });
    document.getElementById('categoryList').style.display = 'none';
    document.getElementById('modalTitle').innerText = 'Entries in ' + category;
    $('#categoriesModal').modal('show');
}

function backToCategories() {
    document.getElementById('entriesByCategory').style.display = 'none';
    document.getElementById('categoryList').style.display = 'block';
    document.getElementById('modalTitle').innerText = 'Categories';
}

document.getElementById('darkModeToggle').addEventListener('click', function() {
    document.body.classList.toggle('dark-mode');
});
</script>
</body>
</html>
"""
    return html_content


def get_css_styles() -> str:
    css_styles = """
body {
    font-family: 'Roboto', sans-serif;
    padding: 20px;
    background-color: #f0f2f5;
    color: #333;
    font-size: 16px;
}
body.dark-mode {
    background-color: #121212;
    color: #e0e0e0;
}
.main-heading {
    text-align: center;
    margin-bottom: 30px;
    color: #007bff;
}
body.dark-mode .main-heading {
    color: #00ffff;
}
#navigation {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    margin-bottom: 20px;
}
#navigation a, #navigation button {
    margin: 5px;
    text-decoration: none;
    font-weight: bold;
    color: #ffffff;
    background-color: #007bff;
    padding: 10px 15px;
    border: none;
    border-radius: 5px;
    display: inline-block;
    transition: background-color 0.3s;
}
body.dark-mode #navigation a, body.dark-mode #navigation button {
    background-color: #00bcd4;
    color: #ffffff;
}
#navigation a:hover:not(.disabled), #navigation button:hover {
    background-color: #0056b3;
    text-decoration: none;
}
body.dark-mode #navigation a:hover:not(.disabled), body.dark-mode #navigation button:hover {
    background-color: #0097a7;
}
.letter-section {
    margin-bottom: 40px;
}
.letter-section h2 {
    color: #007bff;
}
body.dark-mode .letter-section h2 {
    color: #00bcd4;
}
.copy-button {
    margin-top: 5px;
}
table {
    table-layout: fixed;
    word-wrap: break-word;
    background-color: #ffffff;
}
body.dark-mode table {
    background-color: #1e1e1e;
}
th, td {
    vertical-align: middle !important;
    font-size: 16px;
    color: #333;
}
body.dark-mode th, body.dark-mode td {
    color: #e0e0e0;
}
th {
    background-color: #007bff;
    color: #ffffff;
    cursor: pointer;
}
body.dark-mode th {
    background-color: #00bcd4;
    color: #ffffff;
}
th.sortable:hover {
    background-color: #0056b3;
}
body.dark-mode th.sortable:hover {
    background-color: #0097a7;
}
img {
    max-width: 100%;
    height: auto;
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
.search-bar input, .search-bar select {
    background-color: #ffffff;
    color: #333;
}
body.dark-mode .search-bar input, body.dark-mode .search-bar select {
    background-color: #1e1e1e;
    color: #e0e0e0;
    border-color: #00bcd4;
}
.category-tags {
    font-size: 0.9em;
    color: #007bff;
    cursor: pointer;
}
body.dark-mode .category-tags {
    color: #00bcd4;
}
.category-tags a {
    color: inherit;
    text-decoration: none;
}
.category-tags a:hover {
    text-decoration: underline;
}
.modal-content {
    color: #333;
}
body.dark-mode .modal-content {
    background-color: #1e1e1e;
    color: #e0e0e0;
}
.modal-header, .modal-footer {
    border-color: #007bff;
}
body.dark-mode .modal-header, body.dark-mode .modal-footer {
    border-color: #00bcd4;
}
.prompt-text {
    font-size: 16px;
}
"""
    return css_styles


AVAILABLE_MODELS = {
    "Ministral 8B": {"id": "mistralai/ministral-8b", "context_tokens": 128000},
    "Ministral 3B": {"id": "mistralai/ministral-3b", "context_tokens": 128000},
}


def parse_ai_response(response_text):
    """
    Parse the AI response from JSON or extract JSON objects from text.
    """
    try:
        parsed_data = json.loads(response_text)
        if isinstance(parsed_data, list):
            return parsed_data
    except json.JSONDecodeError:
        # Find all JSON objects in the response text
        json_objects = re.findall(r"\{.*?\}", response_text, re.DOTALL)
        parsed_data = []
        for obj in json_objects:
            try:
                parsed_obj = json.loads(obj)
                # Check for required keys
                if all(
                    key in parsed_obj
                    for key in ["Letter", "PromptName", "Categories", "PromptText"]
                ):
                    parsed_data.append(parsed_obj)
            except json.JSONDecodeError:
                continue
    return parsed_data
