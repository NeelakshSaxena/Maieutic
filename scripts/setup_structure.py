import os
import re

def create_structure_from_markdown(md_path, root_dir):
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    stack = []
    
    for line in lines:
        line_stripped = line.rstrip()
        if not line_stripped or line_stripped.strip() == "│" or "..." in line_stripped:
            continue
            
        # Find how many level indents.
        # "├── " or "└── " or "│   " are the prefixes. Each level is 4 spaces or a pipe and 3 spaces.
        # Let's count characters before the tree branch symbols.
        match = re.search(r'([│\s]*)[├└]──\s*(.+)', line_stripped)
        if match:
            indent_str = match.group(1)
            name = match.group(2).strip()
            # Calculate depth: each level in tree is usually 4 characters: "│   " or "    "
            # It's safer to just calculate the exact length of the prefix to determine depth
            depth = len(indent_str) // 4
            
            # Pop from stack until we are at the parent depth
            while len(stack) > depth:
                stack.pop()
                
            current_path = os.path.join(root_dir, *stack, name)
            
            if name.endswith('/'):
                # It's a directory
                os.makedirs(current_path, exist_ok=True)
                stack.append(name.strip('/'))
            else:
                # It's a file
                os.makedirs(os.path.dirname(current_path), exist_ok=True)
                if not os.path.exists(current_path):
                    with open(current_path, 'w', encoding='utf-8') as f:
                        pass # Touch file
        elif re.match(r'^[\w\-]+/$', line_stripped):
            # Root directory like mentorai/
            name = line_stripped.strip('/')
            # We treat root_dir as the base, so we don't need to append this to stack if we want
            # to create everything inside root_dir. Actually, let's just make sure we are in root_dir.
            pass

if __name__ == "__main__":
    md_path = "docs/folder-structure.md"
    root_dir = "."
    create_structure_from_markdown(md_path, root_dir)
    print("Folder structure created successfully.")
