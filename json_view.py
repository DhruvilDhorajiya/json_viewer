import streamlit as st
import streamlit.components.v1 as components
import json
import jsonlines

def create_tree_node(key, value, node_id):
    """Create a tree node based on the type of value"""
    if isinstance(value, dict):
        return {
            "id": f"{node_id}_{key}",
            "text": key,
            "icon": "📂",
            "children": [create_tree_node(k, v, f"{node_id}_{key}") for k, v in value.items()],
            "state": {"checkbox_disabled": False}
        }
    elif isinstance(value, list):
        if len(value) > 0:
            if isinstance(value[0], dict):
                return {
                    "id": f"{node_id}_{key}",
                    "text": key,
                    "icon": "📂",
                    "children": [create_tree_node(k, v, f"{node_id}_{key}") for k, v in value[0].items()],
                    "state": {"checkbox_disabled": False}
                }
            else:
                return {
                    "id": f"{node_id}_{key}",
                    "text": key,
                    "icon": "📄",
                    "state": {"checkbox_disabled": False}
                }
        else:
            return {
                "id": f"{node_id}_{key}",
                "text": key,
                "icon": "📄",
                "state": {"checkbox_disabled": False}
            }
    else:
        return {
            "id": f"{node_id}_{key}",
            "text": key,
            "icon": "📄",
            "state": {"checkbox_disabled": False}
        }

def create_tree_data(json_obj):
    """Convert JSON data to jsTree format"""
    tree_data = []
    if isinstance(json_obj, list):
        tree_data.append({
            "id": "root_list",
            "text": "root",
            "icon": "📂",
            "children": [create_tree_node(k, v, "root") for k, v in json_obj[0].items()],
            "state": {"checkbox_disabled": False}
        })
    else:
        for key, value in json_obj.items():
            tree_data.append(create_tree_node(key, value, "root"))
    return tree_data

def load_json_data(uploaded_file):
    """Load data from either JSON or JSONL file"""
    file_extension = uploaded_file.name.split('.')[-1].lower()
    
    if file_extension == 'jsonl':
        content = uploaded_file.getvalue().decode('utf-8')
        lines = content.strip().split('\n')
        first_line = json.loads(lines[0].replace("'", '"'))
        return first_line
    else:
        return json.load(uploaded_file)

# HTML template for jsTree with checkbox plugin
JSTREE_HTML = """
<html>
<head>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/jstree/3.3.12/themes/default/style.min.css" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jstree/3.3.12/jstree.min.js"></script>
    <style>
        #tree { margin: 20px; }
        .jstree-default .jstree-anchor { height: auto; }
    </style>
</head>
<body>
    <div id="tree"></div>
    <div id="selected_nodes"></div>
    <script>
        var treeData = %s;
        $(function() {
            $('#tree').jstree({
                'core': {
                    'data': treeData,
                    'themes': {
                        'name': 'default',
                        'dots': true,
                        'icons': true
                    }
                },
                'plugins': ['checkbox'],
                'checkbox': {
                    'three_state': true,
                    'whole_node': false,
                    'tie_selection': false
                }
            });

            // Event handler for checkbox changes
            $('#tree').on('check_node.jstree uncheck_node.jstree', function(e, data) {
                var selected = $('#tree').jstree('get_checked', true);
                var selectedPaths = selected.map(function(node) {
                    return node.text;
                });
                $('#selected_nodes').text('Selected: ' + selectedPaths.join(', '));
            });
        });
    </script>
</body>
</html>
"""

st.title("JSON Explorer")

uploaded_file = st.file_uploader("Upload your JSON file", type=["json", "jsonl"])
if uploaded_file:
    try:
        json_data = load_json_data(uploaded_file)
        tree_data = create_tree_data(json_data)
        
        # Render the jsTree
        html_content = JSTREE_HTML % json.dumps(tree_data)
        components.html(html_content, height=600)
        
    except json.JSONDecodeError:
        st.error("Invalid JSON/JSONL file uploaded.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
