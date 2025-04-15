#!/usr/bin/env python3
import os
import json
import zipfile
from collections import defaultdict

REPO_RAW_BASE = "https://github.com/gabrielfvale/scrappy-community/raw/main"

def find_templates():
    templates_by_res = defaultdict(list)
    resolutions = ["640x480", "720x480", "720x720", "1024x768", "nores"]

    for resolution in resolutions:
        # Skip non-directories and special directories
        if not os.path.isdir(resolution) or resolution in ['scripts', '.github']:
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

                # Validate required fields and files
                required_fields = ["name", "author", "submission", "outputs"]
                required_files = [
                    os.path.join(template_path, "template.zip"),
                    os.path.join(template_path, "preview.png")
                ]

                if (all(field in manifest for field in required_fields) and
                    all(os.path.exists(f) for f in required_files)):

                    template_data = {
                        "id": template_dir,
                        **{k: v for k, v in manifest.items() if k != "outputs"},
                        "outputs": manifest["outputs"],
                        # "assets": {
                        #     "template": f"{REPO_RAW_BASE}/{resolution}/{template_dir}/template.zip",
                        #     "preview": f"{resolution}/{template_dir}/preview.png"
                        # }
                    }
                    templates_by_res[resolution].append(template_data)

            except (json.JSONDecodeError, OSError):
                continue

    return dict(templates_by_res)

def create_previews_zip(templates_dict, output_file="previews.zip"):
    with zipfile.ZipFile(output_file, 'w') as zipf:
        for resolution, templates in templates_dict.items():
            for template in templates:
                preview_path = f"{resolution}/{template['id']}/preview.png"
                if os.path.exists(preview_path):
                    zipf.write(preview_path, preview_path)

def main():
    templates_dict = find_templates()

    # Save templates.json
    with open('templates.json', 'w') as f:
        json.dump(templates_dict, f, indent=2)

    # Create previews zip
    create_previews_zip(templates_dict)

    print(f"Processed {sum(len(v) for v in templates_dict.values())} templates across {len(templates_dict)} resolutions")

if __name__ == "__main__":
    main()
