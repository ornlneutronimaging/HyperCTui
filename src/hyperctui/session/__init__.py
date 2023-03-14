class SessionKeys:

    config_version = 'config version'

    instrument = 'instrument'
    ipts_selected = 'ipts selected'
    ipts_index_selected = 'ipts index selected'

    # step ob
    number_of_obs = 'number of obs'
    proton_charge = "proton charge"
    top_obs_folder = "top ob folder"
    list_ob_folders_selected = "list ob folders selected"
    ob_tab_selected = "ob tab selected"
    list_ob_folders_initially_there = "list of ob folders initially there"
    name_of_output_ob_folder = "name of the output OB folder"
    list_ob_folders_requested = "list of ob folders requested"
    ob_will_be_saved_as = "OB will be saved as"
    ob_will_be_moved_to = "OB will be moved to"

    # step projections
    run_title = 'run title'
    list_projections_folders_initially_there = "list projections folders initially there"
    name_of_output_projection_folder = "name of the output projection folder"

    # tabs
    all_tabs_visible = "all tabs visible"
    main_tab_selected = "main tab selected"
    window_width = "window width"
    window_height = "window height"

    # crop
    crop_left = "crop left"
    crop_right = "crop right"
    crop_top = "crop top"
    crop_bottom = "crop bottom"

    # general
    process_in_progress = "process in progress"
    started_acquisition = "started acquisition"


class DefaultValues:
    instrument = 'SNAP'
    ipts_index_selected = 0

    # step ob
    proton_charge = 1
    number_of_obs = 5
    ob_tab_selected = 0

    # step projections
    run_title = ""
    main_tab_selected = 0

    window_width = 800
    window_height = 800

    process_in_progress = False

    started_acquisition = False