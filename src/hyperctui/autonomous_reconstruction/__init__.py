class ColumnIndex:

    enabled_state = 0
    name = 1
    from_value = 2
    to_value = 3


class ProjectionsTableColumnIndex:

    folder_name = 0
    log = 1
    err = 2
    meta = 3
    preview = 4
    status = 5


class ReconstructionTableColumnIndex:

    folder_name = 0
    preview = 1
    status = 2


class KeysTofReconstructionConfig:

    tof_reconstruction_folders = "tof reconstruction folders"
    process_id = "process id"
