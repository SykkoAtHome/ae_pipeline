import argparse
import sys
from src.analyzer.ae_analyzer import AEAnalyzer


def parse_arguments():
    parser = argparse.ArgumentParser(description='After Effects Project Analyzer')
    parser.add_argument('project_path', type=str, help='Path to After Effects project file (.aep)')
    return parser.parse_args()


def main():
    args = parse_arguments()

    analyzer = AEAnalyzer()
    project = analyzer.analyze_project(args.project_path)

    if project:
        print("\nAnalysis completed successfully!")
        print(f"\nProject information:")
        print(f"Name: {project.name}")
        print(f"AE Version: {project.version}")

        print(f"\nFound items:")
        print(f"- Compositions: {len(project.compositions)}")
        print(f"- Footage: {len(project.footage)}")
        print(f"- Folders: {len(project.folders)}")

        # Print details
        project.print_summary()
    else:
        print("\nAnalysis failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()