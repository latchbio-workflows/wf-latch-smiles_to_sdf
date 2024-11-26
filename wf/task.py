from latch.resources.tasks import small_task
from latch.types.directory import LatchOutputDir
from latch.types.file import LatchFile
from typing import List, Optional
from latch.executions import rename_current_execution
import subprocess
from dataclasses import dataclass
from latch.account import Account
from latch.ldata.path import LPath

import sys
import time
import yaml
from pathlib import Path
from typing import Optional
import time

@dataclass
class SMILES:
    ID: str
    SMILES: str

sys.stdout.reconfigure(line_buffering=True)


@small_task
def obabel_task(input_smiles: List[SMILES],
    run_name: str,
    output_directory: LatchOutputDir = LatchOutputDir("latch:///OpenBabel SDF")) -> LatchOutputDir:

    import subprocess

    rename_current_execution(str(run_name))

    print("-" * 60)
    print("Creating local directories")
    local_output_dir = Path(f"/root/outputs/{run_name}")
    local_output_dir.mkdir(parents=True, exist_ok=True)


    for s in input_smiles:
        smiles = s.SMILES
        command = ['obabel', f'-:{smiles}', f'-O{s.ID}.sdf', '--gen3D']

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                cwd=local_output_dir
            )
            print("Output:", result.stdout)
            if result.stderr:
                print("Errors:", result.stderr)
        except subprocess.CalledProcessError as e:
            print("Error running OpenBabel:", e)
            if e.stderr:
                print("Error details:", e.stderr)


    columns = ["smiles", "sdf_file"]
    dtypes = [str, LatchFile]

    target_project_name = "SDF Files"
    target_table_name = f"{run_name}"
    account = Account.current()
    target_project = next(
        (
            project
            for project in account.list_registry_projects()
            if project.get_display_name() == target_project_name
        ),
        None,
    )

    target_project = next(
        (
            project
            for project in account.list_registry_projects()
            if project.get_display_name() == target_project_name
        ),
        None,
    )

    if target_project is None:
        with account.update() as account_updater:
            account_updater.upsert_registry_project(target_project_name)
        target_project = next(
            project
            for project in account.list_registry_projects()
            if project.get_display_name() == target_project_name
        )
        print("Upserted project")

    target_table = next(
        (
            table
            for table in target_project.list_tables()
            if table.get_display_name() == target_table_name
        ),
        None,
    )

    print(len(columns))
    print(len(dtypes))

    if target_table == None:
        ### Upsert_Table
        with target_project.update() as project_updater:
            project_updater.upsert_table(target_table_name)
        target_table = next(
            table
            for table in target_project.list_tables()
            if table.get_display_name() == target_table_name
        )
        print("Upserted table")

        with target_table.update() as updater:
            for i in range(0, len(columns)):
                updater.upsert_column(columns[i], type=dtypes[i])
        print("Upserted columns")

    LPath(f"{output_directory.remote_directory}/{run_name}").mkdirp()

    with target_table.update() as updater:
        for s in input_smiles:

            latch_path = LPath(f"{output_directory.remote_directory}/{run_name}/{s.ID}.sdf")
            latch_path.upload_from(f"{local_output_dir}/{s.ID}.sdf")
            sdf_latchfile = LatchFile(f"{local_output_dir}/{s.ID}.sdf", f"{output_directory.remote_directory}/{run_name}/{s.ID}.sdf")

            try:
                updater.upsert_record(name=str(s.ID), smiles=str(s.SMILES), sdf_file=sdf_latchfile)
                print("Inserted Record....")
            except Exception:
                print("Failed to insert record")

    return LatchOutputDir(str("/root/outputs"), output_directory.remote_path)
