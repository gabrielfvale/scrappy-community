#!/usr/bin/env python3
import os
import json
import zipfile
from collections import defaultdict

def find_templates():
    templates_by_res = defaultdict(list)
    resolutions = ["640x480", "720x480", "720x720", "1024x768", "nores"]

    for resolution in resolutions:
        if not os.path.isdir(resolution):
            continue

        for template_dir in os.listdir(resolution):
            template_path = os.path.join(resolution, template_dir)
            manifest_path = os.path.join(template_path, "manifest.json")

            print(f"Processing template: {template_dir}")

            # Skip if no manifest exists
            if not os.path.exists(manifest_path):
                print(f"No manifest found for template: {template_dir}")
                continue

            try:
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)

                if all(field in manifest for field in ["name", "author", "submission", "outputs"]):
                    templates_by_res[resolution].append({
                        "id": template_dir,
                        "name": manifest["name"],
                        "author": manifest["author"],
                        "submission": manifest["submission"],
                        "outputs": manifest["outputs"],
                        "preview": f"previews/{resolution}/{template_dir}.png"
                    })

            except (json.JSONDecodeError, OSError):
                continue

    return dict(templates_by_res)

def create_templates_zip(templates_dict):
    with zipfile.ZipFile('templates.zip', 'w') as zipf:
        # Add templates.json
        with zipf.open('templates.json', 'w') as json_file:
            json_file.write(json.dumps(templates_dict, indent=2).encode('utf-8'))

        # Add all preview images
        for resolution, templates in templates_dict.items():
            for template in templates:
                src_path = os.path.join(resolution, template['id'], "preview.png")
                if os.path.exists(src_path):
                    zipf.write(src_path, f"previews/{resolution}/{template['id']}.png")

def main():
    templates_dict = find_templates()

    # Create the combined zip file
    create_templates_zip(templates_dict)

    print(f"Created templates.zip with {sum(len(v) for v in templates_dict.values())} templates")

if __name__ == "__main__":
    main()
