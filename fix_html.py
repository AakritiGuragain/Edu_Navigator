import os

TEMPLATES_DIR = 'templates'

for filename in os.listdir(TEMPLATES_DIR):
    if filename.endswith('.html'):
        path = os.path.join(TEMPLATES_DIR, filename)
        with open(path, 'r') as f:
            content = f.read()
            
        # We want to replace the <nav> structure
        # Find: 
        #             <nav>
        #                 <a href="{{ url_for('index') }}">Home</a>
        # ...
        #                 <div class="dropdown">
        #                     ...
        #                 </div>
        # And convert it to:
        #             <nav class="nav-center">
        #                 <a href="{{ url_for('index') }}">Home</a>
        # ...
        #             </nav>
        #             <div class="nav-right">
        #                 ...
        #             </div>
        
        # Actually, let's just make the changes safely using a generic replace block.
        old_nav_start = """            <nav>
                <a href="{{ url_for('index') }}">Home</a>"""
                
        new_nav_start = """            <nav class="nav-center">
                <a href="{{ url_for('index') }}">Home</a>"""
                
        # To handle the split: we need to find the end of the dropdown.
        # It's better to just use python's re module.
        import re
        
        # Replace `<nav>` with `<div class="navbar-links"> \n <nav class="nav-main">`
        # and end of nav with `</nav> ... </div>`
        content = content.replace("<nav>", '<nav class="nav-main">')
        
        # After dropdown closes, we want to split right align stuff
        # We can look for `</a>\n                    </div>\n                </div>\n`
        # and insert `</nav><div class="nav-right">`
        pattern = r'(<div class="dropdown">.*?</div>\s*</div>)'
        
        # Be careful, dropdown doesn't have an inner div in the same way?
        # Let's read index.html first to make sure.
