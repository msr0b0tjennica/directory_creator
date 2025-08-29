import os

# Define the common folder structure for every service
FRAMEWORK = {
    "app": {
        "database": ["__init__.py", "{service}_db_manager.py"],
        "managers": ["__init__.py", "{service}_manager.py"],
        "models": ["__init__.py", "{service}_model.py"],
        "parsers": [
            "__init__.py",
            "{service}_parser.py",
            "{service}_processor_factory.py",
        ],
        "routes": ["__init__.py", "{service}_routes.py"],
    },
    "": [  # root-level files
        "run.py",
        "requirements.txt",
        "README.md",
        "test_{service}_service.py"
    ]
}


def create_structure(service_name: str, base_dir="."): # Creates a file/directory framework for a given service.

    # Normalize service name (remove spaces, lowercase for filenames)
    clean_service = service_name.strip().replace(" ", "_").lower()

    # Create root directory
    service_root = os.path.join(base_dir, service_name)
    os.makedirs(service_root, exist_ok=True)

    for folder, contents in FRAMEWORK.items():
        if folder:  # subfolders under "app"
            folder_path = os.path.join(service_root, folder)
            os.makedirs(folder_path, exist_ok=True)

            for subfolder, files in contents.items():
                subfolder_path = os.path.join(folder_path, subfolder)
                os.makedirs(subfolder_path, exist_ok=True)

                for file in files:
                    filename = file.replace("{service}", clean_service)
                    filepath = os.path.join(subfolder_path, filename)

                    if not os.path.exists(filepath):
                        with open(filepath, "w") as f:
                            if filename.endswith(".py"):
                                f.write(f'""" {filename} for {service_name} """\n')
                            else:
                                f.write("")
        else:  # root-level files
            for file in contents:
                filepath = os.path.join(service_root, file)
                if not os.path.exists(filepath):
                    with open(filepath, "w") as f:
                        if file.endswith(".py"):
                            f.write(f'""" {file} for {service_name} """\n')
                        else:
                            f.write("")


if __name__ == "__main__":
    service_input = input("Enter the service name (e.g., Record Service): ").strip()
    create_structure(service_input)
    print(f"✅ Framework for '{service_input}' created successfully!")
