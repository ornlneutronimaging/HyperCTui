"""
Session management module for HyperCTui.

This module provides constants and default values used across the application
to maintain session state and configuration.
"""


class SessionKeys:
    """
    Constants defining session dictionary keys.

    Attributes
    ----------
    config_version : str
        Key for configuration version
    facility : str
        Key for facility name
    instrument : str
        Key for instrument name
    ipts_selected : str
        Key for selected IPTS
    ipts_index_selected : str
        Key for selected IPTS index
    number_of_obs : str
        Key for number of open beam images
    proton_charge : str
        Key for proton charge value
    top_obs_folder : str
        Key for top-level OB folder location
    list_ob_folders_selected : str
        Key for list of selected OB folders
    ob_tab_selected : str
        Key for selected OB tab
    list_ob_folders_initially_there : str
        Key for initial OB folders list
    name_of_output_ob_folder : str
        Key for output OB folder name
    list_ob_folders_requested : str
        Key for requested OB folders
    list_ob_folders_acquired_so_far : str
        Key for OB folders acquired during experiment
    ob_will_be_saved_as : str
        Key for OB save path
    ob_will_be_moved_to : str
        Key for OB move destination
    run_title : str
        Key for experiment run title
    list_projections : str
        Key for projections list
    list_projections_folders_initially_there : str
        Key for initial projections folders
    list_projections_folders_acquired_so_far : str
        Key for projections folders acquired during experiment
    list_recon_folders_initially_there : str
        Key for initial reconstruction folders
    name_of_output_projection_folder : str
        Key for output projection folder name
    full_path_to_projections : str
        Key for full projection folder path
    image_0_degree : str
        Key for 0-degree reference image
    image_180_degree : str
        Key for 180-degree reference image
    all_tabs_visible : str
        Key for visibility state of all tabs
    main_tab_selected : str
        Key for selected main tab
    window_width : str
        Key for window width
    window_height : str
        Key for window height
    crop_left : str
        Key for left crop position
    crop_right : str
        Key for right crop position
    crop_top : str
        Key for top crop position
    crop_bottom : str
        Key for bottom crop position
    evaluation_regions : str
        Key for evaluation regions dictionary
    evaluation_frequency : str
        Key for evaluation frequency
    tof_roi_region : str
        Key for Time-of-Flight ROI region
    tof_regions : str
        Key for Time-of-Flight region dictionary
    process_in_progress : str
        Key for process status flag
    started_acquisition : str
        Key for acquisition started flag
    obs_have_been_moved_already : str
        Key for OB files moved status flag
    """

    config_version: str = "config version"

    facility: str = "facility"
    instrument: str = "instrument"
    ipts_selected: str = "ipts selected"
    ipts_index_selected: str = "ipts index selected"

    # step ob
    number_of_obs: str = "number of obs"
    proton_charge: str = "proton charge"
    top_obs_folder: str = "top ob folder"
    list_ob_folders_selected: str = "list ob folders selected"
    ob_tab_selected: str = "ob tab selected"
    list_ob_folders_initially_there: str = "list of ob folders initially there"
    name_of_output_ob_folder: str = "name of the output OB folder"
    list_ob_folders_requested: str = "list of ob folders requested"
    list_ob_folders_acquired_so_far: str = "list of ob folders acquired so far for this experiment"
    ob_will_be_saved_as: str = "OB will be saved as"
    ob_will_be_moved_to: str = "OB will be moved to"

    # step projections
    run_title: str = "run title"
    list_projections: str = "list projections"
    list_projections_folders_initially_there: str = "list projections folders initially there"
    list_projections_folders_acquired_so_far: str = "list of projections folders acquired so far for this experiment"
    list_recon_folders_initially_there: str = "list reconstruction folders initially there"
    name_of_output_projection_folder: str = "name of the output projection folder"
    full_path_to_projections: str = "full folder path to projections"
    image_0_degree: str = "image at 0 degree"
    image_180_degree: str = "image at 180 degree"

    # tabs
    all_tabs_visible: str = "all tabs visible"
    main_tab_selected: str = "main tab selected"
    window_width: str = "window width"
    window_height: str = "window height"

    # crop
    crop_left: str = "crop left"
    crop_right: str = "crop right"
    crop_top: str = "crop top"
    crop_bottom: str = "crop bottom"

    # evaluation regions
    evaluation_regions: str = "evaluation regions dict"
    evaluation_frequency: str = "evaluation frequency"

    # tof regions
    tof_roi_region: str = "TOF ROI region of top view dict"
    tof_regions: str = "TOF region dict"

    # general
    process_in_progress: str = "process in progress"
    started_acquisition: str = "started acquisition"
    obs_have_been_moved_already: str = "obs files have already been moved"


class DefaultValues:
    """
    Default values for session parameters.

    Attributes
    ----------
    instrument : str
        Default instrument name
    ipts_index_selected : int
        Default selected IPTS index
    proton_charge : int
        Default proton charge value
    number_of_obs : int
        Default number of open beam images
    ob_tab_selected : int
        Default selected OB tab
    run_title : str
        Default run title
    main_tab_selected : int
        Default selected main tab
    window_width : int
        Default window width
    window_height : int
        Default window height
    process_in_progress : bool
        Default process status flag
    started_acquisition : bool
        Default acquisition started flag
    """

    instrument: str = "VENUS"
    ipts_index_selected: int = 0

    # step ob
    proton_charge: int = 1
    number_of_obs: int = 5
    ob_tab_selected: int = 0

    # step projections
    run_title: str = ""
    main_tab_selected: int = 0

    window_width: int = 800
    window_height: int = 800

    process_in_progress: bool = False

    started_acquisition: bool = False
