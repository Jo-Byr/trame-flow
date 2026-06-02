from pathlib import Path
from typing import Any

from trame.app import TrameApp
from trame.ui.vuetify3 import SinglePageLayout
from trame.widgets import client
from trame.widgets.html import Span
from trame.widgets.vuetify3 import (
    Template,
    VBtn,
    VDivider,
    VIcon,
    VList,
    VListItem,
    VListItemTitle,
    VMenu,
    VNumberInput,
    VRow,
    VSelect,
    VSpacer,
    VTextField,
)
from trame_flow.module.core import create_node
from trame_flow.widgets.flow import (
    Background,
    Controls,
    CustomNode,
    Handle,
    NodeEditor,
)


class Example(TrameApp):
    def __init__(self, server=None):
        super().__init__(server)
        self.next_node_id = 0

        self.state.context_menu_items = [
            {
                "title": "Some",
            },
            {
                "title": "Context menu",
            },
            {
                "title": "Actions",
            },
        ]
        self.state.x = 0
        self.state.y = 0
        self.state.show_menu = False
        self.state.types = ["Text", "Number"]
        self.input_color = "#ef4444"
        self.output_color = "#3b82f6"
        self._handle_counter = 0
        self.ui = self.build_ui()

    @property
    def state(self):
        return self.server.state

    def add_node(self):
        self.vueflow.add_node(
            create_node(
                id=str(self.next_node_id),
                x=0,
                y=0,
                type="dynamic_node",
                label=f"Node {self.next_node_id}",
            )
        )
        self.next_node_id += 1

    def set_node_parameter(self, node_id: str, data_key: str, value: Any):
        self.vueflow.update_node(
            node_id,
            data={
                **self.vueflow.get_node(node_id)["data"],
                data_key: value,
            },
        )

    def add_in_handle(self, node_id: str):
        node = self.vueflow.get_node(node_id)
        in_handles = []
        if "in_handles" in node["data"]:
            in_handles = node["data"]["in_handles"]
        self.set_node_parameter(
            node_id, "in_handles", [*in_handles, f"in-{self._handle_counter}"]
        )
        self._handle_counter += 1

    def add_out_handle(self, node_id: str):
        node = self.vueflow.get_node(node_id)
        out_handles = []
        if "out_handles" in node["data"]:
            out_handles = node["data"]["out_handles"]
        self.set_node_parameter(
            node_id, "out_handles", [*out_handles, f"out-{self._handle_counter}"]
        )
        self._handle_counter += 1

    def middle_click(self, node_id: str, right: bool, handle_index: int):
        # Remove handle
        node = self.vueflow.get_node(node_id)
        in_handle_ids = node["data"].get("in_handles", [])
        out_handle_ids = node["data"].get("out_handles", [])
        if right:
            if len(out_handle_ids) < handle_index:
                return
            handle_id = out_handle_ids[handle_index]
            out_handle_ids.pop(handle_index)
            self.set_node_parameter(node_id, "out_handles", out_handle_ids)
        elif len(in_handle_ids) < handle_index:
            return
        else:
            handle_id = in_handle_ids[handle_index]
            in_handle_ids.pop(handle_index)
            self.set_node_parameter(node_id, "in_handles", in_handle_ids)

        # Remove edges coming in/out of this handle
        to_remove = []
        for edge in self.vueflow.edges:
            if (node_id == edge["source"] and handle_id == edge["sourceHandle"]) or (
                node_id == edge["target"] and handle_id == edge["targetHandle"]
            ):
                to_remove.append(
                    (
                        edge["source"],
                        edge["target"],
                        edge["sourceHandle"],
                        edge["targetHandle"],
                    )
                )
        for edge in to_remove:
            self.vueflow.remove_edge(*edge)

    def right_click(self, node_id: str, right: bool, index: int):
        print(node_id, right, index)  # noqa: T201

    def open_context_menu(self, x: int, y: int):
        self.state.x = x
        self.state.y = y
        self.state.show_menu = True

    def build_ui(self):
        with SinglePageLayout(self.server) as layout:
            layout.title.set_text("trame-flow example")
            with (
                layout.toolbar,
                VBtn(
                    "Add a node",
                    click=self.add_node,
                ),
            ):
                VIcon("mdi-plus")

            with NodeEditor(connection_mode="strict") as self.vueflow:
                with Path(__file__).with_name("style.css").open() as f:
                    client.Style(f.read())
                Background(gap=10, size=1, pattern_color="#81818a")
                Controls()
                with CustomNode(
                    "dynamic_node",
                    var_name="props",
                ):
                    VTextField(
                        model_value=("props.data.label",),
                        update_modelValue=(
                            self.set_node_parameter,
                            "[props.id, 'label', $event]",
                        ),
                        label="Name",
                        hide_details=True,
                        style="width: 200px;",
                        density="comfortable",
                    )
                    VSelect(
                        model_value=("props.data.type",),
                        update_modelValue=(
                            self.set_node_parameter,
                            "[props.id, 'type', $event]",
                        ),
                        label="Type",
                        items=("types",),
                        hide_details=True,
                        style="width: 100%; margin-top: 10px; margin-bottom: 10px;",
                        density="comfortable",
                    )
                    VDivider()
                    with VRow(
                        style="margin: 0; margin-top: 10px; justify-content: center;"
                    ):
                        VTextField(
                            v_if="props.data.type == 'Text'",
                            model_value=("props.data.string",),
                            update_modelValue=(
                                self.set_node_parameter,
                                "[props.id, 'string', $event]",
                            ),
                            label="String",
                            hide_details=True,
                            style="width: 100%; margin-bottom: 10px;",
                            density="comfortable",
                        )
                        VNumberInput(
                            v_if="props.data.type == 'Number'",
                            model_value=("props.data.value",),
                            update_modelValue=(
                                self.set_node_parameter,
                                "[props.id, 'value', $event]",
                            ),
                            label="Value",
                            hide_details=True,
                            style="width: 100%; margin-bottom: 10px;",
                            density="comfortable",
                            precision=2,
                        )
                    VDivider()
                    with VRow(
                        style="margin: 0; margin-top: 10px; justify-content: center;"
                    ):
                        VBtn(
                            icon="mdi-plus",
                            density="compact",
                            click=(self.add_in_handle, "[props.id]"),
                            style="margin-right: 5px;",
                        )
                        VBtn(
                            icon="mdi-plus",
                            density="compact",
                            click=(self.add_out_handle, "[props.id]"),
                            style="margin-left: 5px;",
                        )
                    left_length_str = "props.data.in_handles?.length ?? 0"
                    right_length_str = "props.data.out_handles?.length ?? 0"
                    with VRow(
                        style="margin: 0; position: relative; height: 24px; align-content: center;",
                        v_for=f"(_, i) in Array(Math.max( {left_length_str}, {right_length_str} )).fill()",
                    ):
                        # @contextmenu.prevent="" blocks right click
                        # @auxclick.prevent blocks middle click and calls middle_click with clicked handle properties
                        with Template(v_if=("props.data.in_handles?.length >= i + 1",)):

                            def middle_click_trigger_str(is_right):
                                return f"@auxclick.prevent=\"($event.button===1) ? trigger('{self.server.trigger_name(self.middle_click)}', [props.id, {is_right}, i]) : null\""

                            Span(v_html=("`${props.data.in_handles[i]}`",))
                            Handle(
                                type="target",
                                position="left",
                                connectable=("1",),
                                id=("`${props.data.in_handles[i]}`",),
                                click="console.log($event.target)",
                                raw_attrs=[
                                    f"@contextmenu.prevent=\"trigger('{self.server.trigger_name(self.open_context_menu)}', [$event.x, $event.y]);\"",
                                    middle_click_trigger_str("false"),
                                ],
                                style=f"background: {self.input_color} !important;",
                            )
                        with Template(
                            v_if=("props.data.out_handles?.length >= i + 1",)
                        ):
                            VSpacer()
                            Span(v_html=("`${props.data.out_handles[i]}`",))
                            Handle(
                                type="source",
                                position="right",
                                id=("`${props.data.out_handles[i]}`",),
                                raw_attrs=[
                                    f"@contextmenu.prevent=\"trigger('{self.server.trigger_name(self.open_context_menu)}', [$event.x, $event.y]);\"",
                                    middle_click_trigger_str("true"),
                                ],
                                style=f"background: {self.output_color} !important;",
                            )

                    with (
                        VMenu(
                            v_model=("show_menu",),
                            style=("`position: fixed; left: ${x}px; top: ${y}px;`",),
                        ),
                        VList(),
                        VListItem(
                            v_for="(item, index) in context_menu_items",
                            key=("index",),
                            value=("index",),
                            click="show_menu = false;",
                        ),
                    ):
                        VListItemTitle("{{ item.title }}")

                    def on_graph_change(nodes, edges):
                        with self.state:
                            self.state.nodes = nodes
                            self.state.edges = edges
                        self.state.dirty("nodes")
                        self.state.dirty("edges")

            self.vueflow.graph_change = on_graph_change


if __name__ == "__main__":
    app = Example()
    app.server.start()
