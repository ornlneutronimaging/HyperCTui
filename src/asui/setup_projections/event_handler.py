import os
import logging

from ..parent import Parent


class EventHandler(Parent):

    def run_title_changed(self, run_title=None, checking_if_file_exists=True):
        if (run_title == "") or (run_title == "None"):
            self.parent.ui.projections_title_message.setVisible(True)
            logging.info(f"Please provide a valid title string!")
            self.parent.ui.run_title_formatted_label.setText("None")
            return

        run_title_listed = run_title.split(" ")
        formatted_run_title = "_".join(run_title_listed)

        if checking_if_file_exists:
            formatted_run_title, show_label_ui = self.produce_unused_formatted_run_title(formatted_run_title)
        else:
            show_label_ui = False

        self.parent.ui.run_title_formatted_label.setText(formatted_run_title)
        self.parent.ui.projections_title_message.setVisible(show_label_ui)

    def produce_unused_formatted_run_title(self, run_title):
        """
        this will retrieve the mcp_raw location and look if the run_title exists there.
        if it doesn't, it will return the run_title
        if it does, it will add an increment number

        return:
            new file name, state of label telling if the file name has been changed or not
        """
        o_path = self.parent.folder_path
        mcp_raw = o_path.mcp_raw
        mcp = o_path.mcp

        full_file_name = os.path.join(mcp_raw, run_title)
        if not os.path.exists(full_file_name):
            return run_title, False

        mcp_raw_full_file_name = os.path.join(mcp_raw, run_title)
        autoreduce_full_file_name = os.path.join(mcp, run_title)
        if (not os.path.exists(mcp_raw_full_file_name)) and (not os.path.exists(autoreduce_full_file_name)):
            return run_title, False

        file_increment_index = 1
        while (os.path.exists(os.path.abspath(os.path.join(mcp_raw, f"{run_title}_{file_increment_index:02d}")))) or \
                (os.path.exists(os.path.abspath(os.path.join(mcp, f"{run_title}_{file_increment_index:02d}")))):
            file_increment_index += 1

        return f"{run_title}_{file_increment_index:02d}", True
