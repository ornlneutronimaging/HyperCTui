from ..parent import Parent


class EventHandler(Parent):

	def run_title_changed(self, run_title=None):
		run_title_listed = run_title.split(" ")
		formatted_run_title = "_".join(run_title_listed)
		self.parent.ui.run_title_formatted_label.setText(formatted_run_title)
