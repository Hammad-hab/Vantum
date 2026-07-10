import os
import re
import argparse
import configparser
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

OUTPUT_PATH = "menu.xml"

FIELD_CODE_RE = re.compile(r"%[fFuUdDnNickvm]")


def clean_exec(exec_str):
    """Strip .desktop field codes (%f, %U, etc.) — they're meant to be
    substituted with file paths/URIs at launch time, not passed through
    literally to subprocess/shlex."""
    if not exec_str:
        return None
    return FIELD_CODE_RE.sub("", exec_str).strip()


def collect_apps(applications_dir):
    apps = []

    for item in sorted(os.listdir(applications_dir)):
        if not item.endswith(".desktop"):
            continue

        path = os.path.join(applications_dir, item)
        config = configparser.ConfigParser(interpolation=None)

        try:
            config.read(path)
        except configparser.Error as exc:
            print(f"Skipping '{item}': {exc}")
            continue

        if "Desktop Entry" not in config:
            continue

        entry = config["Desktop Entry"]

        if entry.getboolean("NoDisplay", fallback=False):
            continue
        if entry.getboolean("Hidden", fallback=False):
            continue
        if entry.get("Type", "Application") != "Application":
            continue

        name = entry.get("Name")
        exec_cmd = clean_exec(entry.get("Exec"))
        icon = entry.get("Icon")

        if not name or not exec_cmd:
            continue

        apps.append({"name": name, "icon": icon, "exec": exec_cmd})

    return apps


def build_menu_xml(apps):
    root = ET.Element("menu")

    for app in apps:
        attrs = {"name": app["name"], "exec": app["exec"]}
        if app["icon"]:
            attrs["icon"] = app["icon"]
        ET.SubElement(root, "item", attrs)

    rough = ET.tostring(root, encoding="unicode")
    return minidom.parseString(rough).toprettyxml(indent="    ")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate a Vantum menu.xml from installed .desktop files"
    )
    parser.add_argument(
        "applications_dir",
        nargs="?",
        default="/usr/share/applications",
        help="Directory containing .desktop files (default: /usr/share/applications)",
    )
    parser.add_argument(
        "-o", "--output",
        default=OUTPUT_PATH,
        help=f"Path to write the generated menu XML (default: {OUTPUT_PATH})",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if not os.path.isdir(args.applications_dir):
        raise SystemExit(f"'{args.applications_dir}' is not a directory")

    apps = collect_apps(args.applications_dir)
    xml_text = build_menu_xml(apps)

    xml_text = "\n".join(
        line for line in xml_text.splitlines() if line.strip()
    )

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(xml_text + "\n")

    print(f"Wrote {len(apps)} apps to {args.output}")


if __name__ == "__main__":
    main()