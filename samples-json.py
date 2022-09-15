import os
import argparse
import json

SCENE_EXT = ".casc"
PREVIEW_EXT = ".png"


def create_entry(dir_entry, lookup_set):
    base_name = os.path.splitext(dir_entry.name)[0]

    preview_name = base_name + PREVIEW_EXT
    if preview_name.lower() not in lookup_set:
        print("WARNING: preview not found for '{}'".format(dir_entry.name))
        return None
    else:
        print("created entry for '{}'".format(dir_entry.name))
        return {"name": base_name, "file": dir_entry.name, "preview": preview_name}


def get_content(dir_path):
    files = [f for f in os.scandir(dir_path) if f.is_file()]

    return [
        d
        for d in [
            create_entry(f, {f.name.lower() for f in files})
            for f in files
            if os.path.splitext(f.name)[1] == SCENE_EXT
        ]
        if d is not None
    ]


def generate(dir_path, output):
    content = get_content(dir_path)

    with open(output, "w") as output:
        json.dump(content, output, indent=2)


def check(dir_path, file_path):
    with open(file_path, "r") as file:
        content = json.load(file)
        is_valid = True

        files = {f.name for f in os.scandir(dir_path) if f.is_file()}

        def check_file(name):
            nonlocal files
            nonlocal is_valid

            if name not in files:
                print("ERROR: file '{}' was not found in directory".format(name))
                is_valid = False

        for entry in content:
            check_file(entry.get("file"))
            check_file(entry.get("preview"))

        if is_valid:
            print("File '{}' is valid".format(file_path))
        else:
            print("\nFile '{}' is not valid".format(file_path))


def main():
    parser = argparse.ArgumentParser(description="Create 'samples.json'")

    parser.add_argument(
        "--path",
        dest="path",
        default=".",
        help="path to the samples",
    )

    parser.add_argument(
        "--file",
        dest="file",
        default="samples.json",
        help="path to json file",
    )

    parser.add_argument(
        "--check",
        dest="check",
        action="store_const",
        const=True,
        default=False,
        help="check if 'samples.json' is valid",
    )

    args = parser.parse_args()

    if not os.path.exists(args.path):
        raise Exception("provided directory does not exists: {}".format(args.path))

    if args.check and not os.path.exists(args.file):
        raise Exception("provided file does not exists: {}".format(args.path))

    if args.check:
        check(args.path, args.file)
    else:
        generate(args.path, args.file)


if __name__ == "__main__":
    main()
