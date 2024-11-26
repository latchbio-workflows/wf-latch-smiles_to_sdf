from wf.task import obabel_task, SMILES

from typing import List, Optional

from latch.resources.workflow import workflow
from latch.types.directory import LatchOutputDir
from latch.types.file import LatchFile
from latch.types.metadata import LatchAuthor, LatchMetadata, LatchParameter
from dataclasses import dataclass

from latch.resources.workflow import workflow
from latch.types.directory import LatchDir, LatchOutputDir
from latch.resources.launch_plan import LaunchPlan
from latch.types.file import LatchFile
from latch.types.metadata import (
    Fork,
    ForkBranch,
    LatchAuthor,
    LatchMetadata,
    LatchParameter,
    LatchRule,
    Params,
    Section,
    Spoiler,
    Text
)

metadata = LatchMetadata(
    display_name="Open Babel | SMILES to 3D",
    author=LatchAuthor(
        name="LatchBio",
    ),
    parameters={
        "input_smiles": LatchParameter(
            display_name="Input SMILES",
            batch_table_column=True,  # Show this parameter in batched mode.
            samplesheet=True
        ),
        "output_directory": LatchParameter(
            display_name="Output Directory",
            batch_table_column=True,  # Show this parameter in batched mode.
        ),
        "run_name": LatchParameter(
            display_name="Run Name",
            description="Name for this docking run",
            batch_table_column=True,
            rules=[LatchRule(
                regex=r"^[a-zA-Z0-9_-]+$",
                message="Run name must contain only letters, digits, underscores, and dashes.",
            )],
        ),
    },
)


@workflow(metadata)
def smiles_to_sdf(
    input_smiles: List[SMILES],
    run_name: str,
    output_directory: LatchOutputDir = LatchOutputDir("latch:///OpenBabel SDF")
) -> LatchOutputDir:
    return obabel_task(input_smiles=input_smiles,
                       run_name=run_name,
                       output_directory=output_directory)
