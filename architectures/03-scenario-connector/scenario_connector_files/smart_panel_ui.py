#!/usr/bin/env python3
import os
import sys
from threading import Thread

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gdk, GLib, Gtk  # noqa: E402

from smart_panel_core.grpc_client import LocalProcessorGrpcClient


APP_ID = "com.smartpanel.control"


CSS = b"""
window {
    background: #101216;
    color: #f3f4f6;
}

.header {
    background: #16191f;
    border-bottom: 1px solid #2a2f39;
    padding: 14px 18px;
}

.app-title {
    font-size: 24px;
    font-weight: 700;
}

.app-subtitle {
    color: #9aa3b2;
    font-size: 13px;
}

.sidebar {
    background: #14171c;
    border-right: 1px solid #2a2f39;
    padding: 14px;
}

.nav-button {
    min-height: 46px;
    border-radius: 12px;
    padding: 0 14px;
}

.nav-button:hover {
    background: #20242c;
}

.nav-button.active {
    background: #2a303a;
    font-weight: 700;
}

.page {
    padding: 22px;
}

.section-title {
    font-size: 22px;
    font-weight: 700;
}

.section-subtitle {
    color: #9aa3b2;
}

.card {
    background: #181c22;
    border: 1px solid #2a2f39;
    border-radius: 16px;
    padding: 18px;
}

.card-title {
    font-size: 17px;
    font-weight: 700;
}

.card-muted {
    color: #9aa3b2;
}

.status-dot {
    min-width: 12px;
    min-height: 12px;
    border-radius: 999px;
    background: #6b7280;
}

.status-dot.online {
    background: #22c55e;
}

.status-dot.offline {
    background: #ef4444;
}

.status-text {
    font-weight: 700;
}

.primary-button {
    min-height: 42px;
    border-radius: 12px;
    padding: 0 18px;
    font-weight: 700;
}

.scenario-row {
    background: #181c22;
    border: 1px solid #2a2f39;
    border-radius: 14px;
    padding: 14px;
}

.run-button {
    min-width: 92px;
    min-height: 38px;
    border-radius: 10px;
}

.empty-state {
    color: #9aa3b2;
    font-size: 15px;
}

.toast {
    background: #242a33;
    border-radius: 12px;
    padding: 10px 14px;
}
"""


class SmartPanelWindow(Gtk.ApplicationWindow):

    def __init__(self, application):
        super().__init__(application=application)

        self.set_title("PADNA Smart Panel")
        self.set_default_size(1024, 600)

        self.client = LocalProcessorGrpcClient()

        self.nav_buttons = {}
        self.current_page = None

        self.status_dot = None
        self.status_label = None
        self.dashboard_scenario_label = None
        self.scenario_list = None
        self.toast_label = None

        self._build_ui()

        self.connect(
            "close-request",
            self._on_close_request
        )

        GLib.idle_add(
            self.refresh_scenarios
        )

        if os.getenv(
            "SMART_PANEL_FULLSCREEN",
            "0"
        ) == "1":
            self.fullscreen()

    # ========================================================
    # UI construction
    # ========================================================

    def _build_ui(self):

        root = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL
        )

        self.set_child(root)

        root.append(
            self._build_header()
        )

        body = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL
        )

        body.set_vexpand(True)

        root.append(body)

        body.append(
            self._build_sidebar()
        )

        self.stack = Gtk.Stack()

        self.stack.set_hexpand(True)
        self.stack.set_vexpand(True)

        self.stack.set_transition_type(
            Gtk.StackTransitionType.CROSSFADE
        )

        body.append(
            self.stack
        )

        self.stack.add_named(
            self._build_dashboard_page(),
            "dashboard"
        )

        self.stack.add_named(
            self._build_scenarios_page(),
            "scenarios"
        )

        self.stack.add_named(
            self._build_devices_page(),
            "devices"
        )

        self.stack.add_named(
            self._build_settings_page(),
            "settings"
        )

        self._show_page(
            "dashboard"
        )

    def _build_header(self):

        header = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=14
        )

        header.add_css_class(
            "header"
        )

        title_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=2
        )

        title = Gtk.Label(
            label="PADNA Smart Panel",
            xalign=0
        )

        title.add_css_class(
            "app-title"
        )

        subtitle = Gtk.Label(
            label="Local control • ThingsBoard • CAN",
            xalign=0
        )

        subtitle.add_css_class(
            "app-subtitle"
        )

        title_box.append(title)
        title_box.append(subtitle)

        header.append(title_box)

        spacer = Gtk.Box()

        spacer.set_hexpand(True)

        header.append(spacer)

        status_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8
        )

        self.status_dot = Gtk.Box()

        self.status_dot.add_css_class(
            "status-dot"
        )

        self.status_label = Gtk.Label(
            label="Checking..."
        )

        self.status_label.add_css_class(
            "status-text"
        )

        status_box.append(
            self.status_dot
        )

        status_box.append(
            self.status_label
        )

        header.append(
            status_box
        )

        return header

    def _build_sidebar(self):

        sidebar = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=8
        )

        sidebar.set_size_request(
            190,
            -1
        )

        sidebar.add_css_class(
            "sidebar"
        )

        items = (
            ("dashboard", "Dashboard"),
            ("scenarios", "Scenarios"),
            ("devices", "Devices"),
            ("settings", "Settings"),
        )

        for page_name, title in items:

            button = Gtk.Button(
                label=title
            )

            button.add_css_class(
                "nav-button"
            )

            button.connect(
                "clicked",
                self._on_nav_clicked,
                page_name
            )

            sidebar.append(button)

            self.nav_buttons[
                page_name
            ] = button

        spacer = Gtk.Box()

        spacer.set_vexpand(True)

        sidebar.append(spacer)

        version = Gtk.Label(
            label="Smart Panel UI • V1",
            xalign=0
        )

        version.add_css_class(
            "app-subtitle"
        )

        sidebar.append(version)

        return sidebar

    def _page_container(
        self,
        title,
        subtitle
    ):

        page = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=16
        )

        page.add_css_class(
            "page"
        )

        title_label = Gtk.Label(
            label=title,
            xalign=0
        )

        title_label.add_css_class(
            "section-title"
        )

        subtitle_label = Gtk.Label(
            label=subtitle,
            xalign=0
        )

        subtitle_label.set_wrap(True)

        subtitle_label.add_css_class(
            "section-subtitle"
        )

        page.append(
            title_label
        )

        page.append(
            subtitle_label
        )

        return page

    def _build_dashboard_page(self):

        page = self._page_container(
            "Dashboard",
            "Local status and quick access to the Smart Panel."
        )

        status_card = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10
        )

        status_card.add_css_class(
            "card"
        )

        title = Gtk.Label(
            label="Local Processor",
            xalign=0
        )

        title.add_css_class(
            "card-title"
        )

        self.dashboard_connection_label = Gtk.Label(
            label="Checking gRPC connection...",
            xalign=0
        )

        self.dashboard_connection_label.add_css_class(
            "card-muted"
        )

        status_card.append(title)

        status_card.append(
            self.dashboard_connection_label
        )

        page.append(
            status_card
        )

        scenarios_card = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=12
        )

        scenarios_card.add_css_class(
            "card"
        )

        title = Gtk.Label(
            label="Scenarios",
            xalign=0
        )

        title.add_css_class(
            "card-title"
        )

        self.dashboard_scenario_label = Gtk.Label(
            label="Loading...",
            xalign=0
        )

        self.dashboard_scenario_label.add_css_class(
            "card-muted"
        )

        open_button = Gtk.Button(
            label="Open Scenarios"
        )

        open_button.add_css_class(
            "primary-button"
        )

        open_button.connect(
            "clicked",
            lambda _button: self._show_page(
                "scenarios"
            )
        )

        scenarios_card.append(title)

        scenarios_card.append(
            self.dashboard_scenario_label
        )

        scenarios_card.append(
            open_button
        )

        page.append(
            scenarios_card
        )

        self.toast_label = Gtk.Label(
            label="",
            xalign=0
        )

        self.toast_label.set_visible(
            False
        )

        self.toast_label.add_css_class(
            "toast"
        )

        page.append(
            self.toast_label
        )

        return page

    def _build_scenarios_page(self):

        page = self._page_container(
            "Scenarios",
            "Run scenarios stored in the Local Processor."
        )

        toolbar = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=10
        )

        refresh_button = Gtk.Button(
            label="Refresh"
        )

        refresh_button.add_css_class(
            "primary-button"
        )

        refresh_button.connect(
            "clicked",
            lambda _button: self.refresh_scenarios()
        )

        toolbar.append(
            refresh_button
        )

        page.append(
            toolbar
        )

        scroller = Gtk.ScrolledWindow()

        scroller.set_vexpand(True)

        self.scenario_list = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10
        )

        scroller.set_child(
            self.scenario_list
        )

        page.append(
            scroller
        )

        return page

    def _build_devices_page(self):

        page = self._page_container(
            "Devices",
            "Device management will be added in the next UI phase."
        )

        card = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10
        )

        card.add_css_class(
            "card"
        )

        title = Gtk.Label(
            label="CAN Devices",
            xalign=0
        )

        title.add_css_class(
            "card-title"
        )

        text = Gtk.Label(
            label=(
                "The UI will not access CAN directly.\n"
                "Device operations will go through gRPC "
                "to LocalProcessor."
            ),
            xalign=0
        )

        text.set_wrap(True)

        text.add_css_class(
            "card-muted"
        )

        card.append(title)
        card.append(text)

        page.append(card)

        return page

    def _build_settings_page(self):

        page = self._page_container(
            "Settings",
            "Local UI and service information."
        )

        card = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10
        )

        card.add_css_class(
            "card"
        )

        title = Gtk.Label(
            label="Local Processor",
            xalign=0
        )

        title.add_css_class(
            "card-title"
        )

        info = Gtk.Label(
            label="Connected through the local application service.",
            xalign=0
        )

        info.set_wrap(
            True
        )

        info.add_css_class(
            "card-muted"
        )

        card.append(title)
        card.append(info)

        page.append(card)

        return page

    # ========================================================
    # Navigation
    # ========================================================

    def _on_nav_clicked(
        self,
        _button,
        page_name
    ):

        self._show_page(
            page_name
        )

    def _show_page(
        self,
        page_name
    ):

        self.stack.set_visible_child_name(
            page_name
        )

        self.current_page = page_name

        for name, button in self.nav_buttons.items():

            if name == page_name:
                button.add_css_class(
                    "active"
                )

            else:
                button.remove_css_class(
                    "active"
                )

    # ========================================================
    # gRPC async helpers
    # ========================================================

    def _run_async(
        self,
        worker,
        on_success,
        on_error
    ):

        def target():

            try:
                result = worker()

            except Exception as error:

                GLib.idle_add(
                    on_error,
                    error
                )

                return

            GLib.idle_add(
                on_success,
                result
            )

        Thread(
            target=target,
            daemon=True
        ).start()

    # ========================================================
    # Scenarios
    # ========================================================

    def refresh_scenarios(
        self
    ):

        self._set_connection_state(
            None,
            "Checking..."
        )

        self._run_async(
            self.client.get_scenarios,
            self._on_scenarios_loaded,
            self._on_scenarios_failed
        )

        return False

    def _on_scenarios_loaded(
        self,
        result
    ):

        scenarios = self._normalize_scenarios(
            result
        )

        self._set_connection_state(
            True,
            "Local Processor online"
        )

        self.dashboard_connection_label.set_text(
            "Connected to Local Processor"
        )

        self.dashboard_scenario_label.set_text(
            f"{len(scenarios)} scenario(s) available"
        )

        self._render_scenarios(
            scenarios
        )

        return False

    def _on_scenarios_failed(
        self,
        error
    ):

        self._set_connection_state(
            False,
            "Local Processor offline"
        )

        self.dashboard_connection_label.set_text(
            "gRPC connection failed"
        )

        self.dashboard_scenario_label.set_text(
            "Scenarios unavailable"
        )

        self._render_scenarios(
            []
        )

        self._show_toast(
            "Local Processor error: "
            + str(
                error
            )
        )

        return False

    @staticmethod
    def _normalize_scenarios(
        result
    ):

        if isinstance(
            result,
            list
        ):
            return result

        if isinstance(
            result,
            dict
        ):

            for key in (
                "scenarios",
                "result",
                "data"
            ):

                value = result.get(
                    key
                )

                if isinstance(
                    value,
                    list
                ):
                    return value

        return []

    def _render_scenarios(
        self,
        scenarios
    ):

        child = self.scenario_list.get_first_child()

        while child is not None:

            next_child = child.get_next_sibling()

            self.scenario_list.remove(
                child
            )

            child = next_child

        if not scenarios:

            empty = Gtk.Label(
                label="No scenarios available.",
                xalign=0
            )

            empty.add_css_class(
                "empty-state"
            )

            self.scenario_list.append(
                empty
            )

            return

        for scenario in scenarios:

            if isinstance(
                scenario,
                str
            ):

                scenario_name = scenario
                description = ""

            elif isinstance(
                scenario,
                dict
            ):

                scenario_name = (
                    scenario.get(
                        "name"
                    )
                    or
                    scenario.get(
                        "scenarioName"
                    )
                    or
                    "Unnamed scenario"
                )

                description = scenario.get(
                    "description",
                    ""
                )

            else:
                continue

            row = Gtk.Box(
                orientation=Gtk.Orientation.HORIZONTAL,
                spacing=14
            )

            row.add_css_class(
                "scenario-row"
            )

            text_box = Gtk.Box(
                orientation=Gtk.Orientation.VERTICAL,
                spacing=3
            )

            text_box.set_hexpand(
                True
            )

            name_label = Gtk.Label(
                label=str(
                    scenario_name
                ),
                xalign=0
            )

            name_label.add_css_class(
                "card-title"
            )

            text_box.append(
                name_label
            )

            if description:

                description_label = Gtk.Label(
                    label=str(
                        description
                    ),
                    xalign=0
                )

                description_label.set_wrap(
                    True
                )

                description_label.add_css_class(
                    "card-muted"
                )

                text_box.append(
                    description_label
                )

            run_button = Gtk.Button(
                label="Run"
            )

            run_button.add_css_class(
                "run-button"
            )

            run_button.connect(
                "clicked",
                self._on_run_scenario_clicked,
                str(
                    scenario_name
                )
            )

            row.append(
                text_box
            )

            row.append(
                run_button
            )

            self.scenario_list.append(
                row
            )

    def _on_run_scenario_clicked(
        self,
        button,
        scenario_name
    ):

        button.set_sensitive(
            False
        )

        button.set_label(
            "Running..."
        )

        def worker():

            return self.client.run_scenario(
                scenario_name
            )

        def success(result):

            button.set_sensitive(
                True
            )

            button.set_label(
                "Run"
            )

            self._show_toast(
                "Scenario executed: "
                + scenario_name
            )

            print(
                "SCENARIO RESULT:",
                result,
                flush=True
            )

            return False

        def error(exception):

            button.set_sensitive(
                True
            )

            button.set_label(
                "Run"
            )

            self._show_toast(
                "Scenario failed: "
                + str(
                    exception
                )
            )

            return False

        self._run_async(
            worker,
            success,
            error
        )

    # ========================================================
    # Status / toast
    # ========================================================

    def _set_connection_state(
        self,
        online,
        text
    ):

        self.status_dot.remove_css_class(
            "online"
        )

        self.status_dot.remove_css_class(
            "offline"
        )

        if online is True:

            self.status_dot.add_css_class(
                "online"
            )

        elif online is False:

            self.status_dot.add_css_class(
                "offline"
            )

        self.status_label.set_text(
            text
        )

    def _show_toast(
        self,
        text
    ):

        self.toast_label.set_text(
            text
        )

        self.toast_label.set_visible(
            True
        )

        GLib.timeout_add_seconds(
            4,
            self._hide_toast
        )

    def _hide_toast(
        self
    ):

        self.toast_label.set_visible(
            False
        )

        return False

    # ========================================================
    # Shutdown
    # ========================================================

    def _on_close_request(
        self,
        _window
    ):

        try:
            self.client.close()

        except Exception:
            pass

        return False


class SmartPanelApplication(Gtk.Application):

    def __init__(self):
        super().__init__(
            application_id=APP_ID
        )

    def do_startup(self):

        Gtk.Application.do_startup(
            self
        )

        provider = Gtk.CssProvider()

        provider.load_from_data(
            CSS
        )

        display = Gdk.Display.get_default()

        if display is not None:

            Gtk.StyleContext.add_provider_for_display(
                display,
                provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

    def do_activate(self):

        window = self.props.active_window

        if window is None:

            window = SmartPanelWindow(
                self
            )

        window.present()


def main():

    app = SmartPanelApplication()

    return app.run(
        sys.argv
    )


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
