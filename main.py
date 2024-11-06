from ae_installation.after_fx import AfterFX
from ae_project.ae_project_file import AEProjectFile
import json


def main():
    ae_project = AEProjectFile(
        r"A:\__ORYGINAL_POST__\VISA\8171_Visa_Payment_IGA_KOT\02_PROJECT\Visa_Iga_Kot_RS_021.aep")
    result = ae_project.get_version_info()
    print(json.dumps(result, indent=2))

    ae_install = AfterFX()
    result = ae_install.get_all_versions()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
