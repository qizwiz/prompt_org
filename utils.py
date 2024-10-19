import logging
import json
from typing import List, Dict

def generate_html_content(data: List[Dict], has_image_url: bool, theme: str, header_title: str) -> str:
    """Generate HTML content from the processed data."""
    logging.info(f"Starting HTML generation with {len(data)} items")
    
    # Precompute variables for the HTML content
    css_styles = get_css_styles()
    search_column_0 = 'Persona Name' if has_image_url else 'Letter'
    search_column_2 = 2  # Categories/Tags column
    search_column_3 = 3  # Prompt Text column

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
            <option value="0">{search_column_0}</option>
            <option value="{search_column_2}">Categories/Tags</option>
            <option value="{search_column_3}">Prompt Text</option>
        </select>
    </div>
    <!-- Navigation -->
    <nav id="navigation">
        <!-- Alphabet Navigation -->
"""
    # Generate alphabetical navigation with letters that have entries
    letters = sorted(set(item['Letter'].upper() for item in data if item['Letter']))
    for letter in letters:
        html_content += f'<a href="#section-{letter}">{letter}</a> '

    # Categories Button
    html_content += '<button type="button" data-toggle="modal" data-target="#categoriesModal">Categories</button>\n'
    html_content += '</nav>\n'

    # Start Content Sections
    html_content += '<!-- Content Sections -->\n<div id="content">\n'

    # Group data by letters
    data_by_letter = {}
    for item in data:
        letter = item['Letter'].upper()
        if letter not in data_by_letter:
            data_by_letter[letter] = []
        data_by_letter[letter].append(item)

    # Generate content for each letter with entries
    entry_id = 1  # For unique IDs
    categories_dict = {}  # For categories modal

    for letter in letters:
        html_content += f'<div class="letter-section" id="section-{letter}"><h2>{letter}</h2>\n'
        html_content += '''
    <table class="table table-bordered table-hover">
        <thead>
            <tr>
    '''
        # Determine headers based on the upload option
        if has_image_url:
            headers = ['Persona Name', 'Image', 'Categories/Tags', 'Prompt Text', 'Copy Prompt']
        else:
            headers = ['Letter', 'Prompt Name', 'Categories/Tags', 'Prompt Text', 'Copy Prompt']
        for idx, column in enumerate(headers):
            if column in ['Persona Name', 'Prompt Name', 'Prompt Text']:
                html_content += f'<th class="sortable" onclick="sortTable(this, {idx})">{column}</th>\n'
            else:
                html_content += f'<th>{column}</th>\n'
        html_content += '''
            </tr>
        </thead>
        <tbody>
    '''

        for item in data_by_letter[letter]:
            if has_image_url:
                name_field = item.get('PersonaName', '')
                letter_field = item.get('Letter', '')
            else:
                name_field = item.get('PromptName', '')
                letter_field = item.get('Letter', '')

            image_url = item.get('ImageURL', '') if has_image_url else ''
            categories = item.get('Categories', '')
            prompt_text = item.get('PromptText', '').replace('\n', '<br>')
            categories_list = [cat.strip() for cat in categories.split(',') if cat.strip()]
            # Update categories_dict
            for category in categories_list:
                if category not in categories_dict:
                    categories_dict[category] = []
                categories_dict[category].append({'id': f'entry-{entry_id}', 'name': name_field})

            # Sanitize prompt_text
            prompt_text = prompt_text.replace("fucked", "****")

            html_content += f'''
            <tr id="entry-{entry_id}">
            '''
            if not has_image_url:
                html_content += f'    <td>{letter_field}</td>\n'
            html_content += f'    <td>{name_field}</td>\n'
            if has_image_url:
                if image_url:
                    html_content += f'    <td><img src="{image_url}" alt="{name_field}"></td>\n'
                else:
                    html_content += '    <td></td>\n'
            html_content += '    <td class="category-tags">'
            for category in categories_list:
                html_content += f'<a href="#" onclick="showEntriesByCategory(`{category}`);">{category}</a>'
                if category != categories_list[-1]:
                    html_content += ', '
            html_content += '</td>\n'
            html_content += f'    <td>{prompt_text}</td>\n'
            # Adjusted copyText function call to handle special characters
            sanitized_prompt_text = item.get("PromptText", "").replace("`", "\\`").replace("\\", "\\\\").replace("\n", "\\n").replace("fucked", "****")
            html_content += f'    <td><button class="btn btn-primary copy-button" onclick="copyText(`{sanitized_prompt_text}`)">Copy</button></td>\n'
            html_content += '</tr>\n'

            entry_id += 1

        html_content += '''
        </tbody>
    </table>
    '''
        html_content += '</div>'

    # Categories Modal
    html_content += '''
    <!-- Categories Modal -->
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
    '''
    # List of Categories
    for category in sorted(categories_dict.keys()):
        html_content += f'<li><a href="#" onclick="showEntriesByCategory(`{category}`);">{category}</a></li>'
    html_content += '''
            </ul>
            <!-- Entries by Category -->
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
    <!-- End of Categories Modal -->
    '''

    # Include scripts
    html_content += '''
</div>
<!-- Include jQuery and Bootstrap JS -->
<script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@4.5.2/dist/js/bootstrap.min.js"></script>
<script>
    // Data structures for categories and entries
    var categories = {};
'''
    # Generate JavaScript categories object
    categories_js = 'categories = {\n'
    for category, entries in categories_dict.items():
        categories_js += f'    "{category}": [\n'
        for idx, entry in enumerate(entries):
            entry_id = entry['id']
            entry_name = entry['name'].replace('"', '\\"')
            categories_js += f'        {{"id": "{entry_id}", "name": "{entry_name}"}},\n'
        categories_js += '    ],\n'
    categories_js += '};\n'
    html_content += categories_js

    # Add JavaScript functions
    html_content += '''
    function copyText(text) {
        navigator.clipboard.writeText(text)
            .then(() => alert('Text copied!'))
            .catch(err => console.error('Error copying text: ', err));
    }

    function searchTable() {
        var input, filter, tableContainers, tables, tr, td, i, txtValue;
        input = document.getElementById("searchInput");
        filter = input.value.toUpperCase();
        var columnSelect = document.getElementById("searchColumn");
        var columnIndex = columnSelect.value;

        tableContainers = document.querySelectorAll(".letter-section");
        tableContainers.forEach(function(container) {
            var tables = container.getElementsByTagName("table");
            if (tables.length > 0) {
                var tr = tables[0].getElementsByTagName("tr");
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
                        td = tdArray[columnIndex];
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
        // Toggle sort direction
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
                // Wait for the modal to fully hide, then scroll
                $('#categoriesModal').on('hidden.bs.modal', function () {
                    var target = document.getElementById(entry.id);
                    if (target) {
                        target.scrollIntoView({ behavior: 'smooth' });
                    }
                    // Remove the event listener to prevent it from firing multiple times
                    $('#categoriesModal').off('hidden.bs.modal');
                });
            });
            li.appendChild(a);
            entryList.appendChild(li);
        });
        document.getElementById('categoryList').style.display = 'none';
        document.getElementById('modalTitle').innerText = 'Entries in ' + category;
        $('#categoriesModal').modal('show'); // Ensure the modal is shown
    }

    function backToCategories() {
        document.getElementById('entriesByCategory').style.display = 'none';
        document.getElementById('categoryList').style.display = 'block';
        document.getElementById('modalTitle').innerText = 'Categories';
    }
</script>
</body>
</html>
'''
    logging.info("HTML content generation completed")
    return html_content

def get_css_styles() -> str:
    """Return CSS styles as per the provided HTML."""
    css_styles = '''
    body {
        font-family: 'Roboto', sans-serif;
        padding: 20px;
        background-color: #f0f2f5;
        color: #333;
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
    #navigation a:hover:not(.disabled), #navigation button:hover {
        background-color: #0056b3;
        text-decoration: none;
    }
    .letter-section {
        margin-bottom: 40px;
    }
    .copy-button {
        margin-top: 5px;
    }
    table {
        table-layout: fixed;
        word-wrap: break-word;
        background-color: #ffffff;
    }
    th, td {
        vertical-align: middle !important;
    }
    th {
        background-color: #007bff;
        color: #ffffff;
        cursor: pointer;
    }
    th.sortable:hover {
        background-color: #0056b3;
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
    .main-heading {
        text-align: center;
        margin-bottom: 30px;
        color: #007bff;
    }
    /* Additional Styling */
    .category-tags {
        font-size: 0.9em;
        color: #007bff;
        cursor: pointer;
    }
    .category-tags a {
        color: #007bff;
        text-decoration: none;
    }
    .category-tags a:hover {
        text-decoration: underline;
    }
    /* Highlight for Search */
    .highlight {
        background-color: yellow;
    }
    /* Smooth Scrolling */
    html {
        scroll-behavior: smooth;
    }
    /* Modal Styling */
    .modal-content {
        color: #333;
    }
    .category-list, .entry-list {
        list-style-type: none;
        padding-left: 0;
    }
    .category-list li, .entry-list li {
        margin-bottom: 10px;
    }
    .category-list a, .entry-list a {
        color: #007bff;
        text-decoration: none;
    }
    .category-list a:hover, .entry-list a:hover {
        text-decoration: underline;
    }
    '''
    return css_styles
